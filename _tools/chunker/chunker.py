#!/usr/bin/env python3
r"""
chunker.py - the universal, token-aware document chunker.

Goal: let ANY instance READ a document FULLY, no matter how large, by splitting
it into context-sized chunks at the best available semantic boundary, with real
token budgeting and orientation metadata so the reader never loses its place.

  python chunker.py FILE [FILE ...] [options]

Key options:
  --budget N     target tokens of CONTENT per chunk (default 100000).
                 Set this to ~half your available context window for safety.
  --overlap N    tokens of recap carried from the previous chunk (default 600).
  --out DIR      output dir (default: <file>.chunks next to the source).
  --plan         don't write anything; just print the chunk plan + token totals.
  --stdout N     print chunk N (1-based) to stdout and exit (for agent reads).
  --encoding ENC tiktoken encoding (default o200k_base; falls back to heuristic).

Formats: .md .txt .rst .org code(.py/.js/.ts/.rs/.go/.java/.c/.cpp/.cs/...)
         .pdf (PyMuPDF or pypdf/pdfplumber) .docx (python-docx)
         .html/.htm (stdlib) .json .jsonl
Everything normalizes to text first; PDFs get "## Page N" markers that the
splitter treats as section boundaries.

Boundary hierarchy (split at the highest that fits, never mid-word, never drop
content): heading > page-marker > paragraph (blank line) > sentence > line > word.
Source code (.py/.js/.ts/.rs/.go/.java/.c/.cpp/.cs/...) instead splits between
definitions (function/class), so a chunk never cuts a body in half and each
chunk's `section:` names the enclosing def; an oversized single def falls back to
the text hierarchy above.

Dependencies are all OPTIONAL and lazy. With nothing installed it still chunks
text/markdown/code/json(l) using a smart char-density heuristic. With `tiktoken`
it counts tokens exactly; with `fitz`/`pypdf`/`python-docx` it reads those formats.
"""
import sys, os, re, json, glob, argparse

# ----------------------------------------------------------------------------- token counting

class TokenCounter:
    """tiktoken if available (exact), else a density-aware char heuristic."""
    def __init__(self, encoding="o200k_base"):
        self.enc = None
        self.name = "heuristic"
        try:
            import tiktoken
            for cand in (encoding, "o200k_base", "cl100k_base"):
                try:
                    self.enc = tiktoken.get_encoding(cand)
                    self.name = f"tiktoken:{cand}"
                    break
                except Exception:
                    continue
        except ImportError:
            pass

    # Cap on chars per tiktoken.encode() call. A single multi-100k-char pretoken
    # (a long run of one character, an unwrapped base sequence, etc.) makes
    # tiktoken's BPE blow up super-linearly - one 300k-char run takes ~60s. We
    # encode in bounded windows split right before whitespace, so counts stay
    # exact for normal text but pathological input can't make counting hang.
    MAX_ENCODE_CHARS = 20000

    def count(self, text):
        if not text:
            return 0
        if self.enc is None:
            # heuristic: denser text (high chars/word) tokenizes into more pieces
            chars = len(text)
            words = len(re.findall(r"\S+", text)) or 1
            cpw = chars / words
            divisor = 4.0 if cpw <= 6 else (3.6 if cpw <= 8 else 3.3)
            return int(round(chars / divisor))
        if len(text) <= self.MAX_ENCODE_CHARS:
            return len(self.enc.encode(text, disallowed_special=()))
        total, i, n = 0, 0, len(text)
        while i < n:
            end = min(n, i + self.MAX_ENCODE_CHARS)
            if end < n:                        # back up to a whitespace boundary
                cut = text.rfind("\n", i, end)
                if cut <= i:
                    cut = text.rfind(" ", i, end)
                if cut > i:
                    end = cut
            total += len(self.enc.encode(text[i:end], disallowed_special=()))
            i = end
        return total


# ----------------------------------------------------------------------------- format extraction

TEXT_EXTS = {
    ".md", ".markdown", ".txt", ".rst", ".org", ".text", ".log",
    ".py", ".js", ".ts", ".tsx", ".jsx", ".rs", ".go", ".java", ".c", ".h",
    ".cpp", ".hpp", ".cc", ".cs", ".rb", ".php", ".swift", ".kt", ".scala",
    ".sh", ".ps1", ".bat", ".sql", ".r", ".lua", ".pl", ".html", ".htm",
    ".css", ".xml", ".yaml", ".yml", ".toml", ".ini", ".cfg", ".env", ".tex",
}

# Code files get definition-aware splitting (split between defs, never mid-body).
# Limited to languages the def-matchers below cover well; others fall back to the
# plain text path (paragraph/blank-line splitting), which is fine for them.
CODE_EXTS = {
    ".py", ".js", ".ts", ".tsx", ".jsx", ".rs", ".go", ".java",
    ".c", ".h", ".cpp", ".hpp", ".cc", ".cs", ".rb", ".php",
    ".swift", ".kt", ".scala", ".lua",
}

def read_text_file(path):
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        return f.read()

def extract_pdf(path):
    # try PyMuPDF (fitz) first - best text fidelity - then pypdf, then pdfplumber
    try:
        import fitz  # PyMuPDF
        doc = fitz.open(path)
        out = []
        for i, page in enumerate(doc, 1):
            out.append(f"## Page {i}\n\n{page.get_text('text')}")
        return "\n\n".join(out)
    except Exception:
        pass
    try:
        from pypdf import PdfReader
        r = PdfReader(path)
        return "\n\n".join(f"## Page {i}\n\n{(pg.extract_text() or '')}"
                           for i, pg in enumerate(r.pages, 1))
    except Exception:
        pass
    try:
        import pdfplumber
        with pdfplumber.open(path) as pdf:
            return "\n\n".join(f"## Page {i}\n\n{(pg.extract_text() or '')}"
                               for i, pg in enumerate(pdf.pages, 1))
    except Exception as e:
        raise RuntimeError(f"PDF needs one of: PyMuPDF / pypdf / pdfplumber  ({e})")

def extract_docx(path):
    try:
        import docx
        d = docx.Document(path)
        return "\n\n".join(p.text for p in d.paragraphs)
    except Exception as e:
        raise RuntimeError(f"DOCX needs python-docx  ({e})")

def extract_html(text):
    from html.parser import HTMLParser
    class Strip(HTMLParser):
        def __init__(self):
            super().__init__()
            self.out = []
            self.skip = 0
        def handle_starttag(self, tag, attrs):
            if tag in ("script", "style"):
                self.skip += 1
            if tag in ("p", "br", "div", "li", "tr", "h1", "h2", "h3", "h4"):
                self.out.append("\n")
        def handle_endtag(self, tag):
            if tag in ("script", "style") and self.skip:
                self.skip -= 1
        def handle_data(self, data):
            if not self.skip:
                self.out.append(data)
    s = Strip()
    s.feed(text)
    return re.sub(r"\n{3,}", "\n\n", "".join(s.out))

def extract(path):
    """Return (normalized_text, format_label)."""
    ext = os.path.splitext(path)[1].lower()
    if ext == ".pdf":
        return extract_pdf(path), "pdf"
    if ext == ".docx":
        return extract_docx(path), "docx"
    raw = read_text_file(path)
    if ext in (".html", ".htm"):
        return extract_html(raw), "html"
    if ext == ".jsonl":
        return raw, "jsonl"
    if ext == ".json":
        try:
            return json.dumps(json.loads(raw), indent=2, ensure_ascii=False), "json"
        except Exception:
            return raw, "json"
    return raw, ("markdown" if ext in (".md", ".markdown")
                 else ("code" if ext in CODE_EXTS else "text"))


# ----------------------------------------------------------------------------- block splitting

class Block:
    __slots__ = ("text", "crumb", "tokens")
    def __init__(self, text, crumb, tokens):
        self.text = text
        self.crumb = crumb
        self.tokens = tokens

HEADING_RE = re.compile(r"^(#{1,6})\s+(.*)$")

# --- code-aware splitting: recognize where a definition STARTS, so chunk seams
# fall between defs (never mid-function). Language-agnostic; conservative on the
# C-family (requires a trailing "{") so a call/control statement isn't mistaken
# for a definition. False negatives just mean fewer seams (safe); the kw guard
# below blocks the common false positives (if/for/while (...) { ).
_CODE_DEF_RES = (
    re.compile(r"(?:async\s+)?def\s+(\w+)"),                          # python
    re.compile(r"class\s+(\w+)"),                                     # py/js/ts/java/...
    re.compile(r"(?:pub\s+)?(?:async\s+)?(?:unsafe\s+)?fn\s+(\w+)"),  # rust
    re.compile(r"(?:pub\s+)?(?:unsafe\s+)?(?:struct|enum|trait|impl|mod)\s+(\w+)"),  # rust
    re.compile(r"func\s+(?:\([^)]*\)\s*)?(\w+)"),                     # go
    re.compile(r"(?:export\s+)?(?:default\s+)?(?:async\s+)?function\s*\*?\s*(\w*)"), # js
    re.compile(r"(?:export\s+)?(?:abstract\s+)?(?:interface|enum)\s+(\w+)"),         # ts/java
    re.compile(r"(?:export\s+)?(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s*)?(?:\([^)]*\)|\w+)\s*=>"),  # js arrow fn
    re.compile(r"(?:[\w<>\[\],:*&~\s]+?\s+)?(\w+)\s*\([^;{]*\)\s*(?:->\s*[^{;]+)?\{\s*$"),  # C/C++/Java/C#
)
_CTRL_KW = {"if", "for", "while", "switch", "catch", "else", "elif", "do",
            "return", "with", "except", "finally", "try", "case", "default",
            "when", "match", "using", "namespace", "synchronized", "lock"}

def _match_code_def(raw_line):
    """If a line starts a definition, return (indent_cols, name); else None."""
    line = raw_line.expandtabs(4)
    stripped = line.strip()
    if not stripped or stripped[0] in "}])":
        return None
    indent = len(line) - len(line.lstrip(" "))
    for rx in _CODE_DEF_RES:
        m = rx.match(stripped)
        if m:
            name = (m.group(1) or "").strip() or "—"   # em-dash for anon fn
            if name in _CTRL_KW:
                return None
            return indent, name
    return None

def _attached_to_next_def(line):
    """Decorators / comments / blank lines directly above a def belong WITH it."""
    s = line.strip()
    if s == "":
        return True
    return s[0] in "@#" or s.startswith(("//", "/*", "*", "///", '"""', "'''", "<!--"))

def split_code_blocks(text, counter, budget):
    """Code -> [Block]: each definition (with its body and any leading
    decorators/comments) is one atom, so packing never splits a function or class
    across a chunk seam. Breadcrumbs track the enclosing-definition nesting, and
    a single definition larger than budget still falls back to split_oversized."""
    lines = text.split("\n")
    stack = []          # [(indent, name)] enclosing-definition breadcrumb
    blocks = []
    buf = []

    def crumb():
        return " > ".join(nm for _, nm in stack) if stack else ""

    def flush():
        if not buf:
            return
        chunk_text = "\n".join(buf).strip("\n")
        buf.clear()
        if not chunk_text.strip():
            return
        toks = counter.count(chunk_text)
        if toks <= budget:
            blocks.append(Block(chunk_text, crumb(), toks))
        else:
            cr = crumb()
            for sub in split_oversized(chunk_text, counter, budget):
                blocks.append(Block(sub, cr, counter.count(sub)))

    for ln in lines:
        m = _match_code_def(ln)
        if m:
            indent, name = m
            carry = []                       # pull leading decorators/comments
            while buf and _attached_to_next_def(buf[-1]) and len(carry) < 25:
                carry.insert(0, buf.pop())
            flush()
            while stack and stack[-1][0] >= indent:
                stack.pop()
            stack.append((indent, name))
            buf.extend(carry)
            buf.append(ln)
        else:
            buf.append(ln)
    flush()
    return blocks

def split_blocks(text, fmt, counter, budget):
    """Text -> [Block], heading/page/paragraph aware, oversized blocks recursed."""
    # jsonl: each non-empty line is a record = an atom (group during packing)
    if fmt == "jsonl":
        blocks = []
        for ln in text.split("\n"):
            if ln.strip():
                blocks.append(Block(ln, "record", counter.count(ln)))
        return blocks

    # code: split between definitions (functions/classes), never mid-body
    if fmt == "code":
        return split_code_blocks(text, counter, budget)

    lines = text.split("\n")
    stack = []          # [(level, title)] for markdown / "## Page N" headings
    blocks = []
    para = []

    def crumb():
        return " > ".join(t for _, t in stack) if stack else ""

    def flush_para():
        if not para:
            return
        chunk_text = "\n".join(para).strip("\n")
        para.clear()
        if not chunk_text.strip():
            return
        toks = counter.count(chunk_text)
        if toks <= budget:
            blocks.append(Block(chunk_text, crumb(), toks))
        else:
            for sub in split_oversized(chunk_text, counter, budget):
                blocks.append(Block(sub, crumb(), counter.count(sub)))

    for ln in lines:
        m = HEADING_RE.match(ln)
        if m:
            flush_para()
            level = len(m.group(1))
            title = m.group(2).strip()
            while stack and stack[-1][0] >= level:
                stack.pop()
            stack.append((level, title))
            # the heading line itself rides with the next paragraph as context
            para.append(ln)
        elif ln.strip() == "":
            flush_para()
        else:
            para.append(ln)
    flush_para()
    return blocks

SENT_RE = re.compile(r"(?<=[.!?])\s+")

def split_oversized(text, counter, budget):
    """Recursively split a too-big block: paragraph->sentence->line->word->chars."""
    if counter.count(text) <= budget:
        return [text]
    # try paragraphs (double newline)
    parts = [p for p in re.split(r"\n\s*\n", text) if p.strip()]
    if len(parts) > 1:
        return _greedy_join(parts, counter, budget, sep="\n\n")
    # try sentences
    sents = [s for s in SENT_RE.split(text) if s.strip()]
    if len(sents) > 1:
        return _greedy_join(sents, counter, budget, sep=" ")
    # try lines
    ls = [l for l in text.split("\n") if l != ""]
    if len(ls) > 1:
        return _greedy_join(ls, counter, budget, sep="\n")
    # try words (whitespace, never mid-word)
    words = text.split(" ")
    if len(words) > 1:
        return _greedy_join(words, counter, budget, sep=" ")
    # absolute last resort: ONE run with no break points (minified blob, long
    # base64/hash, space-less CJK) that is still over budget. Hard-split it by
    # character count so we always make progress (otherwise _greedy_join would
    # recurse on the same un-splittable atom forever).
    return _hard_split_chars(text, counter, budget)

def _greedy_join(parts, counter, budget, sep):
    """Greedily pack `parts` into strings each <= budget tokens."""
    out, cur, cur_tok = [], [], 0
    for p in parts:
        pt = counter.count(p)
        if pt > budget:                       # single part still too big -> recurse
            if cur:
                out.append(sep.join(cur)); cur, cur_tok = [], 0
            out.extend(split_oversized(p, counter, budget))
            continue
        if cur and cur_tok + pt > budget:
            out.append(sep.join(cur)); cur, cur_tok = [], 0
        cur.append(p); cur_tok += pt
    if cur:
        out.append(sep.join(cur))
    return out

def _hard_split_chars(text, counter, budget):
    """Slice ONE unbreakable run into pieces each <= budget tokens. Sizes each
    slice from an estimated chars-per-token ratio and trims locally, so every
    count() sees only ~one slice (never the whole remainder). The only place a
    token-run is cut mid-'word', and only when it has zero paragraph/sentence/
    line/space break points. `start` strictly advances, so this terminates."""
    out, start, n = [], 0, len(text)
    cpt = max(1.0, n / (counter.count(text) or 1))   # chars per token, est. once
    while start < n:
        size = max(1, int(budget * cpt))
        end = min(n, start + size)
        while end > start + 1 and counter.count(text[start:end]) > budget:
            size = max(1, int(size * 0.85)); end = start + size
        out.append(text[start:end])
        start = end
    return out

def _tail_tokens(text, counter, n_tokens):
    """Return roughly the trailing n_tokens tokens of text, aligned to whole
    lines where possible. Used to synthesize a recap when a chunk's final block
    is, on its own, larger than the overlap budget."""
    if counter.count(text) <= n_tokens:
        return text
    out, tok = [], 0
    for ln in reversed(text.split("\n")):
        lt = counter.count(ln)
        if out and tok + lt > n_tokens:
            break
        if not out and lt > n_tokens:
            break            # even the final line alone is too big -> char tail
        out.insert(0, ln); tok += lt
    if out:
        return "\n".join(out)
    # one very long line: trim a generous char tail down to <= n_tokens
    tail = text[-(n_tokens * 8):]
    while len(tail) > 1 and counter.count(tail) > n_tokens:
        tail = tail[len(tail) // 8:]
    return tail


# ----------------------------------------------------------------------------- packing

def pack(blocks, counter, content_budget, overlap_tokens):
    """Greedily pack blocks into chunks of <= content_budget tokens of content,
    then carry a block-level recap overlap from each chunk's tail. content_budget
    already excludes headroom for the recap + comment headers (the caller computes
    it the same way it sizes blocks), so the FINAL rendered chunk reliably stays
    under the user's budget - including a chunk made of a single big block."""
    chunks = []           # each = list[Block]
    cur, cur_tok = [], 0
    for b in blocks:
        if cur and cur_tok + b.tokens > content_budget:
            chunks.append(cur); cur, cur_tok = [], 0
        cur.append(b); cur_tok += b.tokens
    if cur:
        chunks.append(cur)

    # build recap overlap = trailing blocks of previous chunk up to overlap budget
    recaps = [None]
    for i in range(1, len(chunks)):
        prev = chunks[i - 1]
        recap, tok = [], 0
        for b in reversed(prev):
            if tok + b.tokens > overlap_tokens:
                break
            recap.insert(0, b); tok += b.tokens
        if not recap and prev:
            # the previous chunk's final block alone exceeds the overlap budget;
            # synthesize a truncated tail so continuity is never silently lost
            last = prev[-1]
            tail = _tail_tokens(last.text, counter, overlap_tokens)
            recap = [Block(tail, last.crumb, counter.count(tail))]
        recaps.append(recap or None)
    return chunks, recaps


# ----------------------------------------------------------------------------- rendering

def render_chunk(idx, total, src, blocks, recap, counter, fmt):
    name_next = f"chunk-{idx+1:03d}.md" if idx < total else "(none - last)"
    crumb = next((b.crumb for b in blocks if b.crumb), "")
    body = ("\n\n" if fmt != "jsonl" else "\n").join(b.text for b in blocks)
    parts = []
    bar = "=" * 12
    parts.append(f"<!-- {bar} CHUNK {idx}/{total} {bar} -->")
    parts.append(f"<!-- source: {os.path.basename(src)} -->")
    if crumb:
        parts.append(f"<!-- section: {crumb} -->")
    if recap:
        rtext = ("\n\n" if fmt != "jsonl" else "\n").join(b.text for b in recap)
        parts.append(f"<!-- recap: last ~{sum(b.tokens for b in recap)} tokens of chunk {idx-1}, for continuity -->")
        parts.append("> " + rtext.replace("\n", "\n> "))
        parts.append(f"<!-- end recap | new content begins -->")
    parts.append("")
    parts.append(body)
    parts.append("")
    parts.append(f"<!-- end chunk {idx}/{total} | next: {name_next} -->")
    out = "\n".join(parts)
    return out, counter.count(out), crumb

def build_index(src, fmt, total, infos, counter_name, budget, overlap):
    src_tokens = sum(i["content_tokens"] for i in infos)
    lines = []
    lines.append(f"# Chunk index - {os.path.basename(src)}")
    lines.append("")
    lines.append(f"- source format: `{fmt}`  ")
    lines.append(f"- total content: ~**{src_tokens:,} tokens** in **{total} chunks**  ")
    lines.append(f"- per-chunk budget: {budget:,} tokens | overlap recap: {overlap} | counter: `{counter_name}`")
    lines.append("")
    lines.append("## How to read this fully")
    lines.append(f"Read `chunk-001.md` ... `chunk-{total:03d}.md` **in order**. Each fits a "
                 f"context-sized budget, opens with a `section:` breadcrumb so you know where "
                 f"you are, and (from chunk 2 on) a short `recap:` of the prior chunk's tail so "
                 f"nothing is lost at the seam. Reading all chunks = reading the whole document.")
    lines.append("")
    lines.append("## Chunks")
    lines.append("")
    lines.append("| # | file | chunk tokens | section |")
    lines.append("|---|------|-------------|---------|")
    for i in infos:
        lines.append(f"| {i['idx']} | `{i['file']}` | {i['chunk_tokens']:,} | {i['crumb'] or '-'} |")
    lines.append("")
    return "\n".join(lines)


# ----------------------------------------------------------------------------- driver

def process(path, budget, overlap, out_dir, counter, plan_only, stdout_n, multi=False):
    text, fmt = extract(path)
    total_tokens = counter.count(text)
    # Reserve headroom for the recap + comment headers up front, and size BOTH
    # block-splitting and packing to the same content budget so the rendered
    # chunk stays under `budget` even when a chunk is a single large block.
    reserve = overlap + max(600, int(budget * 0.02))
    content_budget = max(500, budget - reserve)
    blocks = split_blocks(text, fmt, counter, content_budget)
    chunks, recaps = pack(blocks, counter, content_budget, overlap)
    total = len(chunks)

    if total == 0:
        if stdout_n is None:
            print(f"\n{path}")
            print(f"  format={fmt}  ~{total_tokens:,} tokens  counter={counter.name}")
            print(f"  no content to chunk (file is empty or whitespace-only); nothing written")
        else:
            sys.stderr.write(f"{path}: no content to chunk (empty or whitespace-only)\n")
        return

    # render
    rendered = []
    for i, (bl, rc) in enumerate(zip(chunks, recaps), 1):
        out, ctoks, crumb = render_chunk(i, total, path, bl, rc, counter, fmt)
        rendered.append({"idx": i, "text": out, "chunk_tokens": ctoks, "crumb": crumb,
                         "content_tokens": sum(b.tokens for b in bl),
                         "file": f"chunk-{i:03d}.md"})

    if stdout_n is not None:
        if 1 <= stdout_n <= total:
            sys.stdout.write(rendered[stdout_n - 1]["text"])
        else:
            sys.stderr.write(f"chunk {stdout_n} out of range (1..{total})\n")
        return

    pct1m = total_tokens / 1_000_000 * 100
    print(f"\n{path}")
    print(f"  format={fmt}  ~{total_tokens:,} tokens ({pct1m:.1f}% of a 1M window)  counter={counter.name}")
    print(f"  -> {total} chunks @ budget {budget:,} tok (overlap {overlap})")
    biggest = max(r["chunk_tokens"] for r in rendered)
    print(f"  largest rendered chunk: {biggest:,} tokens "
          f"({'OK, under budget' if biggest <= budget else 'WARN over budget'})")
    if plan_only:
        for r in rendered:
            print(f"    [{r['idx']:>3}/{total}] {r['chunk_tokens']:>8,} tok  {r['crumb'][:60]}")
        return

    base = os.path.splitext(os.path.basename(path))[0]
    if out_dir:
        # one shared --out across many files would collide (every file writes
        # chunk-001.md ...); give each its own subdir when there's more than one.
        odir = os.path.join(out_dir, base + ".chunks") if multi else out_dir
    else:
        odir = os.path.join(os.path.dirname(os.path.abspath(path)), base + ".chunks")
    os.makedirs(odir, exist_ok=True)
    for r in rendered:
        with open(os.path.join(odir, r["file"]), "w", encoding="utf-8") as f:
            f.write(r["text"])
    index = build_index(path, fmt, total, rendered, counter.name, budget, overlap)
    with open(os.path.join(odir, "INDEX.md"), "w", encoding="utf-8") as f:
        f.write(index)
    manifest = {
        "source": os.path.abspath(path), "format": fmt,
        "source_tokens": total_tokens, "chunks": total,
        "budget": budget, "overlap": overlap, "counter": counter.name,
        "files": [{"idx": r["idx"], "file": r["file"],
                   "chunk_tokens": r["chunk_tokens"], "section": r["crumb"]} for r in rendered],
    }
    with open(os.path.join(odir, "_manifest.json"), "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
    print(f"  wrote {total} chunks + INDEX.md + _manifest.json -> {odir}")


def main(argv):
    # Force UTF-8 on stdout/stderr so --stdout and prints never crash on a
    # math symbol or em-dash under a Windows cp1252 console.
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass
    ap = argparse.ArgumentParser(description="Universal token-aware document chunker")
    ap.add_argument("files", nargs="+", help="file paths or globs")
    ap.add_argument("--budget", type=int, default=100000, help="content tokens per chunk (default 100000)")
    ap.add_argument("--overlap", type=int, default=600, help="recap tokens carried between chunks (default 600)")
    ap.add_argument("--out", default=None, help="output dir (default <file>.chunks)")
    ap.add_argument("--plan", action="store_true", help="estimate + show plan, write nothing")
    ap.add_argument("--stdout", type=int, default=None, metavar="N", help="print chunk N to stdout and exit")
    ap.add_argument("--encoding", default="o200k_base", help="tiktoken encoding (default o200k_base)")
    a = ap.parse_args(argv)

    counter = TokenCounter(a.encoding)
    paths = []
    for p in a.files:
        # recursive=True so the documented "docs\**\*.pdf" actually descends
        g = glob.glob(p, recursive=True)
        paths.extend(g if g else [p])
    files = [p for p in paths if os.path.isfile(p)]
    for p in paths:
        if not os.path.isfile(p):
            print(f"  ! not a file: {p}")

    if a.stdout is not None:
        # --stdout emits one chunk to stdout; with many matches it would
        # concatenate, so operate on a single file (warn if we had to choose).
        if not files:
            sys.stderr.write("--stdout: no readable input file\n"); return
        if len(files) > 1:
            sys.stderr.write(f"--stdout expects one file; using first of {len(files)}: {files[0]}\n")
        try:
            process(files[0], a.budget, a.overlap, a.out, counter, a.plan, a.stdout)
        except Exception as e:
            sys.stderr.write(f"  ! {files[0]}: {e}\n")
        return

    multi = len(files) > 1
    for p in files:
        try:
            process(p, a.budget, a.overlap, a.out, counter, a.plan, a.stdout, multi=multi)
        except Exception as e:
            print(f"  ! {p}: {e}")


if __name__ == "__main__":
    main(sys.argv[1:])
