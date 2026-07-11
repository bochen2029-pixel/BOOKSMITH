#!/usr/bin/env python3
"""
lint_manuscript.py — manuscript corruption + voice-drift lint (BOOKSMITH).

PURPOSE (KIT_ARCHITECTURE (c) lint_manuscript.py; LESSONS_LEDGER §3.8, §2.7)
    Block release on TWO independent classes of defect:

    (A) PDF-round-trip corruption — the artifacts that appear when a
        manuscript is round-tripped through a rendered PDF/DOCX and back to
        text before final generation (the Second Notebook build's exact
        failure). Ported from C:\\Claude-Titanic\\lint_manuscript.py:
            EMBEDDED_UNDERSCORE, PARAGRAPH_NOT_TERMINATED, UNBALANCED_EMPHASIS,
            STRAY_MARKDOWN, MULTIPLE_SPACES, MID_WORD_HYPHEN_BREAK,
            EMDASH_CONTINUATION.

    (B) SEED-blacklist / voice-drift — the forbidden-vocabulary scrubber
        (case-sensitive + case-insensitive + regex tiers) driven by
        book_config.voice.blacklist, plus sacred-term drift detection driven
        by book_config.voice.sacred_terms. Ported from
        C:\\BOOK3\\_tools\\check_acp_vocabulary.py (the 97-pattern scrubber's
        tiered structure + is_documentation_file dir-exclusion).

    Scaffolding + cached-source dirs are excluded by DEFAULT (they legitimately
    quote banned words / period-authentic vocabulary — LESSONS_LEDGER §2.7).

CONTRACT
    python lint_manuscript.py --config book_config.json [--include-docs]
                              [--root <workspace>] [--verbose]
        scans <workspace>/manuscript/current/ + <workspace>/manuscript/drafts/
        (plus any explicit path positionals). Exit codes:
            0  clean
            1  drift/corruption (BLOCKING — build should halt)
            2  usage / config error

    Blacklist / greenlist / sacred_terms come from book_config.voice.
    The workspace root is derived from the config slug
    (book_workspace/<slug>/) unless --root is given; a positional path
    overrides the manuscript-dir default entirely.

SOURCE
    C:\\Claude-Titanic\\lint_manuscript.py (corruption checks — ported in full)
    C:\\BOOK3\\_tools\\check_acp_vocabulary.py (tiered scrubber + dir-exclusion)
"""
import argparse
import json
import re
import sys
from pathlib import Path

# ─────────────────────────────────────────────────────────────────────────────
# PART A — PDF-round-trip corruption signatures
# (ported from C:\Claude-Titanic\lint_manuscript.py)
# ─────────────────────────────────────────────────────────────────────────────

TERMINAL_PUNCT = (".", "?", "!", "…", ")", "]", "}", ":")
# Trailing closers that still count as terminated: emphasis markers, quote/paren
# characters, em/en-dashes. `*` and `_` close an italic span — the sentence-ending
# punctuation sits inside the italic and is still terminal.
TRAILING_CLOSERS = ('"', "”", "'", "’", ")", "]", "}",
                    "—", "–", "*", "_")


def paragraph_ends_terminated(para: str) -> bool:
    """True if the paragraph ends with sentence-ending punctuation, allowing
    trailing quotes / parens / closing em-dashes after the terminal mark."""
    s = para.rstrip()
    while s and s[-1] in TRAILING_CLOSERS:
        s = s[:-1].rstrip()
    if not s:
        return True  # entirely-empty or all-wrapper paragraph
    return s.endswith(TERMINAL_PUNCT)


def is_structural_line(line: str) -> bool:
    """Lines that don't need to end with terminal punctuation."""
    stripped = line.strip()
    if not stripped:
        return True
    if stripped.startswith("#"):
        return True
    if re.match(r"^[-*_]{3,}$", stripped):
        return True
    if re.match(r"^[-*+]\s+", stripped):
        return True
    if re.match(r"^\d+\.\s+", stripped):
        return True
    return False


def iter_paragraphs(text: str):
    """Yield (start_line, raw_paragraph_text) for each blank-line-delimited
    paragraph, preserving original line numbers for error reporting."""
    lines = text.split("\n")
    buf = []
    buf_start = None
    for idx, line in enumerate(lines, start=1):
        if line.strip() == "":
            if buf:
                yield buf_start, "\n".join(buf)
                buf = []
                buf_start = None
        else:
            if not buf:
                buf_start = idx
            buf.append(line)
    if buf:
        yield buf_start, "\n".join(buf)


def lint_corruption(text: str) -> list:
    """Return a list of (code, line_no, detail) corruption findings for one
    manuscript's text. Mirrors the Claude-Titanic linter's logic exactly."""
    findings = []
    in_code = False
    lines = text.split("\n")
    prev_para_lastline = None

    # --- Line-level checks (raw lines) ---
    for idx, line in enumerate(lines, start=1):
        if line.strip().startswith("```"):
            in_code = not in_code
            continue
        if in_code:
            continue

        # CHECK 5: multiple consecutive spaces mid-content.
        if re.search(r"\S {2,}\S", line):
            findings.append(("MULTIPLE_SPACES", idx,
                             f"Line has 2+ consecutive spaces mid-content: {line.strip()[:80]!r}"))

        # CHECK 1: embedded underscore inside a word (a_Thursday).
        for m in re.finditer(r"\w_\w", line):
            findings.append(("EMBEDDED_UNDERSCORE", idx,
                             f"Embedded underscore in word: {m.group()!r} in line {line.strip()[:80]!r}"))

        # CHECK 6: mid-word hyphen + end-of-line followed by lowercase.
        if line.rstrip().endswith("-") and not line.rstrip().endswith("--"):
            next_nonblank = next((lines[j].lstrip() for j in range(idx, len(lines))
                                  if lines[j].strip()), "")
            if next_nonblank and next_nonblank[0].islower():
                findings.append(("MID_WORD_HYPHEN_BREAK", idx,
                                 f"Hyphen at line end followed by lowercase continuation: "
                                 f"{line.strip()[-30:]!r} + {next_nonblank[:30]!r}"))

    # --- Paragraph-level checks ---
    for start_line, para in iter_paragraphs(text):
        stripped_para = para.strip()
        if not stripped_para:
            continue

        first_line = stripped_para.split("\n", 1)[0]
        if is_structural_line(first_line):
            prev_para_lastline = None
            continue

        # Skip blockquotes wholly (quoted text, different rules).
        if all(l.lstrip().startswith(">") for l in stripped_para.split("\n") if l.strip()):
            prev_para_lastline = None
            continue

        # CHECK 3: unbalanced emphasis markers within a paragraph.
        underscores = len(re.findall(r"(?<!\\)_", stripped_para))
        if underscores % 2 != 0:
            findings.append(("UNBALANCED_EMPHASIS", start_line,
                             f"Odd number of '_' markers ({underscores}) in paragraph: {stripped_para[:80]!r}"))
        asterisks = len(re.findall(r"(?<!\*)\*(?!\*)", stripped_para))
        if asterisks % 2 != 0:
            findings.append(("UNBALANCED_EMPHASIS", start_line,
                             f"Odd number of '*' markers ({asterisks}) in paragraph: {stripped_para[:80]!r}"))

        # CHECK 4: stray markdown link syntax inside prose.
        if re.search(r"\[[^\]]+\]\([^)]+\)", stripped_para):
            findings.append(("STRAY_MARKDOWN", start_line,
                             f"Link syntax inside prose paragraph: {stripped_para[:80]!r}"))

        # CHECK 2: paragraph not terminated with sentence-ending punctuation.
        last_line_of_para = stripped_para.split("\n")[-1].strip()
        is_attribution = (last_line_of_para.startswith("—") or
                          last_line_of_para.startswith("--"))
        if not is_attribution and not paragraph_ends_terminated(stripped_para):
            last_chars = stripped_para.rstrip()[-30:]
            findings.append(("PARAGRAPH_NOT_TERMINATED", start_line,
                             f"Paragraph ends without terminal punctuation; tail: {last_chars!r}"))

        # CHECK 7: split-sentence signature — previous paragraph didn't
        # terminate AND current paragraph starts with a lowercase letter.
        if prev_para_lastline is not None:
            prev_stripped = prev_para_lastline.rstrip()
            if prev_stripped and not prev_stripped.endswith(TERMINAL_PUNCT + TRAILING_CLOSERS):
                first_char = stripped_para.lstrip()[:1]
                if first_char and first_char.islower():
                    findings.append(("EMDASH_CONTINUATION", start_line,
                                     f"Paragraph starts lowercase {stripped_para[:40]!r} after unterminated "
                                     f"previous paragraph ending {prev_stripped[-30:]!r}"))

        prev_para_lastline = stripped_para

    return findings


# ─────────────────────────────────────────────────────────────────────────────
# PART B — voice-drift / blacklist scrubber
# (tiered structure ported from C:\BOOK3\_tools\check_acp_vocabulary.py)
# ─────────────────────────────────────────────────────────────────────────────

# A blacklist entry may be a bare phrase (case-insensitive substring) or a
# "regex:<pattern>" / "cs:<phrase>" tagged form. Bare phrases with an uppercase
# character are treated as case-SENSITIVE (proper-noun style), matching the
# check_acp_vocabulary convention that capitalized forbidden terms are only
# forbidden when capitalized.

def compile_blacklist(blacklist: list) -> tuple:
    """Split the config blacklist into (case_sensitive, case_insensitive, regex)
    tiers. Returns three lists of (needle_or_pattern, label)."""
    cs, ci, rx = [], [], []
    for raw in blacklist:
        entry = str(raw).strip()
        if not entry:
            continue
        if entry.startswith("regex:"):
            pat = entry[len("regex:"):]
            try:
                rx.append((re.compile(pat), f"blacklist regex {pat!r}"))
            except re.error as exc:
                print(f"[warn] bad blacklist regex {pat!r}: {exc}", file=sys.stderr)
            continue
        if entry.startswith("cs:"):
            phrase = entry[len("cs:"):]
            cs.append((phrase, f"blacklist (case-sensitive) {phrase!r}"))
            continue
        # Heuristic: a phrase containing an uppercase letter is a proper-noun
        # style term → case-sensitive; otherwise case-insensitive.
        if any(c.isupper() for c in entry):
            cs.append((entry, f"blacklist (case-sensitive) {entry!r}"))
        else:
            ci.append((entry.lower(), f"blacklist {entry!r}"))
    return cs, ci, rx


def parse_sacred_terms(sacred_terms: list) -> list:
    """A sacred-term entry uses the config convention:
        'exact wording | note about locked usage'
    The text BEFORE the first '|' is the locked wording; we detect near-miss
    paraphrase drift. Returns [(exact_phrase, note)]. Only entries whose note
    hints at an exact/refrain lock are drift-checked; the rest are informational
    (they carry a term name, not a phrase to preserve verbatim)."""
    locked = []
    for raw in sacred_terms:
        entry = str(raw)
        parts = entry.split("|", 1)
        phrase = parts[0].strip()
        note = parts[1].strip() if len(parts) > 1 else ""
        if not phrase:
            continue
        note_l = note.lower()
        # Only enforce verbatim-preservation for terms flagged as an exact
        # wording / refrain that must never drift.
        if any(k in note_l for k in ("exact", "refrain", "never paraphrase",
                                     "verbatim", "locked", "must not drift")):
            locked.append((phrase, note))
    return locked


def scan_voice(text: str, cs, ci, rx, locked_terms) -> list:
    """Return (code, line_no, detail) findings for blacklist + sacred-term drift."""
    findings = []
    lines = text.splitlines()
    for line_num, line in enumerate(lines, 1):
        line_lower = line.lower()
        for phrase, label in cs:
            if phrase in line:
                findings.append(("BLACKLIST", line_num, f"{label}: {line.strip()[:80]!r}"))
        for needle, label in ci:
            if needle in line_lower:
                findings.append(("BLACKLIST", line_num, f"{label}: {line.strip()[:80]!r}"))
        for pattern, label in rx:
            m = pattern.search(line)
            if m:
                findings.append(("BLACKLIST", line_num, f"{label} matched {m.group(0)!r}: {line.strip()[:80]!r}"))

    # Sacred-term drift: for each locked exact wording, flag a near-miss —
    # the same words in the same order but with altered punctuation/casing that
    # is NOT the exact string. A whole-manuscript scan (drift can span a line).
    for phrase, note in locked_terms:
        exact_count = text.count(phrase)
        # Build a loose pattern: word tokens of the phrase separated by any
        # non-word run, case-insensitive. A loose hit that is not also an
        # exact hit is a paraphrase-drift candidate.
        tokens = re.findall(r"\w+", phrase)
        if not tokens:
            continue
        loose = r"\W+".join(re.escape(t) for t in tokens)
        loose_hits = re.findall(loose, text, flags=re.IGNORECASE)
        drift = len(loose_hits) - exact_count
        if drift > 0:
            findings.append(("SACRED_DRIFT", 0,
                             f"sacred term {phrase!r} appears paraphrased {drift} time(s) "
                             f"(loose={len(loose_hits)}, exact={exact_count}) — {note}"))
    return findings


# ─────────────────────────────────────────────────────────────────────────────
# Documentation / scaffolding exclusion (ported from check_acp_vocabulary)
# ─────────────────────────────────────────────────────────────────────────────

EXCLUDED_NAMES = {
    "wrong.md", "readme.md", "_readme.md", "claude.md", "architecture.md",
    "seed.md", "changelog.md", "_warm_start.md", "kit_architecture.md",
    "lessons_ledger.md", "production_lessons_learned.md",
}

META_DIR_MARKERS = {
    "contracts", "registry", "exemplars", "handoffs", "reviews", "state",
    "canon_refs", "fiction_refs", "appendices", "_tools", "_reference",
    "_titanic_source", "outputs", "archive", "backups", "intake", "_kit_research",
}


def is_documentation_file(path: Path) -> bool:
    """Files/dirs that legitimately quote forbidden vocabulary or period-
    authentic language — excluded from the voice scrub by default. Manuscript
    prose lives at manuscript/current/ and manuscript/drafts/; drafts under a
    manuscript/ dir are IN scope."""
    if path.name.lower() in EXCLUDED_NAMES:
        return True
    parts_l = [p.lower() for p in path.parts]
    for part in parts_l:
        if part in META_DIR_MARKERS:
            # manuscript/drafts/ is in scope even though 'drafts' is generic.
            if part == "drafts" and "manuscript" in parts_l:
                continue
            return True
    return False


# ─────────────────────────────────────────────────────────────────────────────
# File collection + config
# ─────────────────────────────────────────────────────────────────────────────

def load_config(config_path: Path) -> dict:
    with config_path.open(encoding="utf-8") as fh:
        return json.load(fh)


def workspace_root(cfg: dict, config_path: Path, explicit_root) -> Path:
    """Resolve the book workspace root. Priority: --root > book_workspace/<slug>
    relative to the config's parent dir > the config's own directory."""
    if explicit_root:
        return Path(explicit_root)
    slug = cfg.get("slug")
    base = config_path.resolve().parent
    if slug:
        candidate = base / "book_workspace" / slug
        if candidate.exists():
            return candidate
        # Config may itself live inside book_workspace/<slug>/.
        if base.name == slug:
            return base
    return base


def collect_manuscript_files(root: Path, positionals: list) -> list:
    """Collect .md files to scan. Explicit positionals win; otherwise scan
    manuscript/current/ + manuscript/drafts/ under the workspace root."""
    files = []
    if positionals:
        for p in positionals:
            path = Path(p)
            if path.is_file() and path.suffix.lower() == ".md":
                files.append(path)
            elif path.is_dir():
                files.extend(sorted(path.rglob("*.md")))
        return files

    for sub in ("manuscript/current", "manuscript/drafts"):
        d = root / sub
        if d.exists():
            files.extend(sorted(d.rglob("*.md")))
    return files


def read_text(path: Path) -> str:
    for enc in ("utf-8", "utf-8-sig"):
        try:
            return path.read_text(encoding=enc)
        except UnicodeDecodeError:
            continue
    # Last resort: replace undecodable bytes so the scan still runs.
    return path.read_text(encoding="utf-8", errors="replace")


CORRUPTION_ORDER = [
    "EMBEDDED_UNDERSCORE", "PARAGRAPH_NOT_TERMINATED", "EMDASH_CONTINUATION",
    "MID_WORD_HYPHEN_BREAK", "UNBALANCED_EMPHASIS", "STRAY_MARKDOWN",
    "MULTIPLE_SPACES", "BLACKLIST", "SACRED_DRIFT",
]


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

    ap = argparse.ArgumentParser(
        description="Manuscript corruption + voice-drift lint (BOOKSMITH). "
                    "Exit 0 clean / 1 drift (blocking) / 2 usage.")
    ap.add_argument("--config", help="Path to book_config.json (drives blacklist/"
                                     "greenlist/sacred_terms + workspace slug).")
    ap.add_argument("--root", help="Override the workspace root "
                                   "(default: book_workspace/<slug>/).")
    ap.add_argument("--include-docs", action="store_true",
                    help="Do NOT exclude scaffolding/cached-source dirs from the "
                         "voice scrub (debugging only; they legitimately quote "
                         "banned/period vocabulary).")
    ap.add_argument("--verbose", "-v", action="store_true",
                    help="Show extra context.")
    ap.add_argument("paths", nargs="*",
                    help="Explicit .md files/dirs to scan (overrides the "
                         "manuscript-dir default).")
    args = ap.parse_args()

    cfg = {}
    config_path = None
    if args.config:
        config_path = Path(args.config)
        if not config_path.exists():
            print(f"[ERROR] config not found: {config_path}", file=sys.stderr)
            return 2
        try:
            cfg = load_config(config_path)
        except (json.JSONDecodeError, OSError) as exc:
            print(f"[ERROR] could not parse config {config_path}: {exc}", file=sys.stderr)
            return 2

    voice = cfg.get("voice", {}) if isinstance(cfg, dict) else {}
    blacklist = voice.get("blacklist", []) or []
    sacred_terms = voice.get("sacred_terms", []) or []
    cs, ci, rx = compile_blacklist(blacklist)
    locked_terms = parse_sacred_terms(sacred_terms)

    # Resolve scan targets.
    if config_path is not None:
        root = workspace_root(cfg, config_path, args.root)
    else:
        root = Path(args.root) if args.root else Path.cwd()
    files = collect_manuscript_files(root, args.paths)

    if not args.paths and not args.include_docs:
        files = [f for f in files if not is_documentation_file(f)]

    if not files:
        print(f"[info] No manuscript .md files found to lint under {root}.")
        print("[info] (Scaffolding/cached-source dirs are excluded unless --include-docs.)")
        return 0

    print(f"[lint] {len(files)} file(s) under {root}")
    print(f"[lint] corruption checks: 7 | blacklist tiers: "
          f"{len(cs)} cs + {len(ci)} ci + {len(rx)} regex | "
          f"locked sacred terms: {len(locked_terms)}")

    exit_code = 0
    total = 0
    for f in files:
        text = read_text(f)
        findings = lint_corruption(text)
        if not args.include_docs or args.paths:
            # Voice scrub runs on manuscript files (already filtered above),
            # or on any explicit target the caller named.
            if not is_documentation_file(f) or args.include_docs or args.paths:
                findings += scan_voice(text, cs, ci, rx, locked_terms)

        print(f"\n=== {f} ===")
        if not findings:
            print("  CLEAN — no corruption or voice-drift artifacts.")
            continue

        exit_code = 1
        by_code = {}
        for code, line, detail in findings:
            by_code.setdefault(code, []).append((line, detail))
        for code in CORRUPTION_ORDER:
            if code not in by_code:
                continue
            hits = by_code[code]
            print(f"\n  [{code}] — {len(hits)} finding(s):")
            for line, detail in hits[:50]:
                loc = f"line {line}" if line else "(whole-file)"
                print(f"    {loc}: {detail}")
            if len(hits) > 50:
                print(f"    ... {len(hits) - 50} more")
        print(f"\n  TOTAL FINDINGS: {len(findings)}")
        total += len(findings)

    print(f"\n{'=' * 72}")
    if exit_code == 0:
        print(f"[CLEAN] {len(files)} file(s) scanned; zero findings.")
    else:
        print(f"[DRIFT] {len(files)} file(s) scanned; {total} finding(s). "
              f"Build should HALT; revise before generation/export.")
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
