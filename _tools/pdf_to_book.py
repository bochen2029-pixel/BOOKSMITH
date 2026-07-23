#!/usr/bin/env python3
r"""
pdf_to_book.py — decompose a finished-book PDF into a BOOKSMITH workspace, so an
already-typeset book (someone else's finished PDF) can be re-fitted to BOOKSMITH's
exact-spec outputs: a reflowable Amazon Kindle ebook, a KDP paperback, and a KDP
hardcover (each a genuinely different build).

WHY THIS IS NOT manuscript_ingest.py: that tool flattens a source to markdown so the
SYNTHESIS engine can re-derive a NEW book. This tool does the opposite — it PRESERVES
the book's own structure (chapters, front/back matter, paragraphs) and re-issues the
SAME content, faithfully, to exact Amazon geometry. Content unchanged; only the vessel.

DESIGN PRINCIPLE — extract CONTENT, discard the source LAYOUT. A finished PDF is
already typeset in its own trim, margins, running heads, and page numbers. We keep
only the text + its chapter structure so the kit can RE-typeset to each KDP target.
Fidelity is to the TEXT, not the source page design. (This is also what lets ONE
manuscript feed both reflowable ebooks and print: the producers add each format's
layout, but only if the manuscript is layout-free.)

PIPELINE
  1. EXTRACT (fitz "dict"): per-page blocks/lines/spans with font size, bold, position.
  2. FURNITURE: strip running heads/feet (lines recurring across pages) + page numbers.
  3. NORMALIZE: de-hyphenate line-break splits; reflow lines to paragraphs; and
     DE-SPACE letter-spaced (tracked) titles — "C H A P T E R  O N E" -> "CHAPTER ONE"
     (BOOKSMITH's own generator tracks chapter titles; the spacing otherwise defeats
     both the keyword and the font-size heading tests).
  4. HEADINGS: chapter/part keyword (post de-space) OR a short block bigger than body;
     TOC entries (dot leaders) are recognized and never treated as chapter openers.
  5. STRUCTURE: the body starts at the first REAL chapter opener; everything before is
     front matter — title/copyright/contents dropped (BOOKSMITH regenerates them to
     spec), dedication/epigraph prose captured; the rest segmented into units.
  6. META: title/author from PDF metadata + title page; language (CJK detect); trim
     snapped to the nearest standard KDP trim.
  7. SCAFFOLD: write book_workspace/<slug>/book_config.json (schema-valid) +
     manuscript/current/<id>_current.md per unit, and PRINT a proposed structure for
     human review. It does NOT produce formats — review first, then produce.

HEADING DETECTION IS HEURISTIC — the tool stops at a proposed structure on purpose.
Review the unit split (and title/author/trim), fix book_config.json, THEN produce.

USAGE
  python pdf_to_book.py <book.pdf> [--slug NAME] [--title T] [--author A]
                        [--trim 6x9] [--out DIR] [--is-fiction] [--json]
  python pdf_to_book.py --selftest        # synthesizes a tiny (letter-spaced) PDF, round-trips it
"""
from __future__ import annotations
import argparse, json, re, sys
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
STD_TRIMS = [(5, 8), (5.06, 7.81), (5.25, 8), (5.5, 8.5), (6, 9), (6.14, 9.21),
             (6.69, 9.61), (7, 10), (7.44, 9.69), (7.5, 9.25), (8, 10), (8.5, 11)]

CHAP_WORD = (r"chapter|part|book|section|prologue|epilogue|introduction|foreword|"
             r"preface|afterword|appendix|conclusion|interlude|coda")
CHAP_RE = re.compile(rf"^\s*(?:{CHAP_WORD})\b", re.I)
NUM_ONLY = re.compile(r"^\s*(?:[ivxlcdm]{1,7}|\d{1,4})\s*$", re.I)
FRONT_KW = re.compile(r"©|copyright|all rights reserved|isbn|no part of this|"
                      r"first (?:edition|printing)|library of congress|work of fiction|"
                      r"product of the author|used fictitiously|resemblance to (?:actual|real)|"
                      r"manufactured in|printed in the", re.I)
TOC_KW = re.compile(r"^\s*(?:table of )?contents\s*$", re.I)
LIGATURES = {"ﬀ": "ff", "ﬁ": "fi", "ﬂ": "fl", "ﬃ": "ffi", "ﬄ": "ffl"}


def u8():
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


def slugify(s: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "_", (s or "").lower()).strip("_")
    return s or "imported_book"


def despace(t: str) -> str:
    """Collapse letter-spaced (tracked) runs: 'C H A P T E R  O N E' -> 'CHAPTER ONE'.
    Words are separated by 2+ spaces, letters within a word by single spaces. Only a
    run of >=3 tokens that is >=70% single characters is collapsed, so ordinary prose
    (with its stray 'I', 'a') is never mangled."""
    if "  " not in t and not re.search(r"(?:^|\s)\S(?:\s\S){3,}(?:\s|$)", t):
        return t
    out = []
    for part in re.split(r"\s{2,}", t):
        toks = part.split(" ")
        if len(toks) >= 3 and sum(1 for x in toks if len(x) == 1) >= 0.7 * len(toks):
            out.append("".join(toks))
        else:
            out.append(part)
    return re.sub(r"\s+", " ", " ".join(out)).strip()


def is_toc_entry(t: str) -> bool:
    """A Contents line: dot leaders (optionally spaced) and/or a trailing page number."""
    return bool(re.search(r"[.·]\s?[.·]\s?[.·]", t) or re.search(r"\.{3,}\s*\d{0,4}$", t))


def clean(t: str) -> str:
    for k, v in LIGATURES.items():
        t = t.replace(k, v)
    return t.replace("­", "").replace(" ", " ")   # soft hyphen, nbsp


# ---------------------------------------------------------------- extract
def extract(path: Path):
    import fitz
    doc = fitz.open(str(path))
    meta = dict(doc.metadata or {})
    toc = doc.get_toc(simple=True) if hasattr(doc, "get_toc") else []
    pages = []
    for page in doc:
        d = page.get_text("dict")
        blocks = []
        for b in d.get("blocks", []):
            if b.get("type") != 0:            # 0 = text; skip images
                continue
            lines = []
            for ln in b.get("lines", []):
                spans = [s for s in ln.get("spans", []) if s.get("text", "").strip()]
                if not spans:
                    continue
                lines.append({
                    "text": clean("".join(s["text"] for s in spans)),
                    "size": round(max(s["size"] for s in spans), 1),
                    "bold": any(int(s.get("flags", 0)) & 16 for s in spans),
                    "x0": round(ln["bbox"][0], 1), "y0": round(ln["bbox"][1], 1),
                })
            if lines:
                blocks.append({"lines": lines})
        pages.append({"w": page.rect.width, "h": page.rect.height, "blocks": blocks})
    doc.close()
    return meta, pages, toc


def body_size(pages) -> float:
    c = Counter()
    for p in pages:
        for b in p["blocks"]:
            for ln in b["lines"]:
                c[ln["size"]] += len(ln["text"])
    return c.most_common(1)[0][0] if c else 11.0


# ---------------------------------------------------------------- furniture
def _fnorm(t: str) -> str:
    return re.sub(r"\d+", "#", despace(t).strip().lower())


def running_furniture(pages):
    """Lines recurring in the top/bottom band across many pages = running heads/feet."""
    tops, bots = Counter(), Counter()
    for p in pages:
        lines = sorted((ln for b in p["blocks"] for ln in b["lines"]), key=lambda l: l["y0"])
        if not lines:
            continue
        band = p["h"] * 0.12
        for l in [l for l in lines if l["y0"] <= lines[0]["y0"] + band]:
            tops[_fnorm(l["text"])] += 1
        for l in [l for l in lines if l["y0"] >= lines[-1]["y0"] - band]:
            bots[_fnorm(l["text"])] += 1
    thr = max(4, len(pages) * 0.25)
    return ({t for t, c in tops.items() if c >= thr and t},
            {t for t, c in bots.items() if c >= thr and t})


def is_furniture(text, heads, feet):
    t = text.strip()
    if not t or NUM_ONLY.match(t):            # blank or bare page number
        return True
    return _fnorm(t) in heads or _fnorm(t) in feet


def dehyphenate(lines):
    out = ""
    for t in lines:
        t = t.rstrip()
        if out and out.endswith("-") and len(out) > 1 and out[-2].isalpha() and t[:1].islower():
            out = out[:-1] + t.lstrip()
        elif out:
            out = out + " " + t.lstrip()
        else:
            out = t
    return re.sub(r"[ \t]+", " ", out).strip()


# ---------------------------------------------------------------- classify
def classify_blocks(pages, bsz, heads, feet):
    """Ordered blocks as {kind, text, size, page, chap, toc}."""
    heading_min = bsz * 1.3
    seq = []
    for pi, p in enumerate(pages):
        for b in p["blocks"]:
            lines = [l for l in b["lines"] if not is_furniture(l["text"], heads, feet)]
            if not lines:
                continue
            # de-space PER LINE first, while the double-space word gaps are still
            # intact (dehyphenate collapses runs of spaces, which would fuse
            # "C H A P T E R  O N E" into "CHAPTERONE" and defeat the keyword test).
            text = dehyphenate([despace(l["text"]) for l in lines])
            if not text:
                continue
            size = max(l["size"] for l in lines)
            words = len(text.split())
            toc = is_toc_entry(text)
            short = words <= 12 and len(lines) <= 2
            chap = bool(CHAP_RE.match(text)) and not toc
            big = size >= heading_min and short and not toc
            seq.append({"kind": "heading" if (chap or big) else "body", "text": text,
                        "size": size, "page": pi, "words": words, "chap": chap, "toc": toc})
    return seq


def find_toc_titles(seq):
    """Harvest Contents entry titles (for cross-check / reporting)."""
    titles, grabbing = [], False
    for blk in seq:
        if TOC_KW.match(blk["text"]):
            grabbing = True
            continue
        if grabbing:
            if blk.get("chap") and not blk.get("toc"):
                break
            for line in re.split(r"\s{2,}|\n", blk["text"]):
                m = re.match(r"^(.*?)[\s.·]*\d{1,4}$", line.strip())
                cand = (m.group(1) if m else line).strip(" .·—-")
                if cand and 1 <= len(cand.split()) <= 12:
                    titles.append(cand)
            if len(titles) > 80:
                break
    return titles


def norm_title(s: str) -> str:
    return re.sub(r"[^0-9a-z一-鿿]+", "", despace(s or "").lower())


def apply_toc(seq, pdftoc, contents_titles):
    """Cross-check chapter detection against the book's OWN table of contents — the PDF
    bookmark outline AND the printed Contents page — and mark openers that the keyword/
    size tests missed. This is what makes the tool robust for books whose chapters are
    neither keyworded ('Chapter N') nor set in a larger font (literary titles at body
    size). Guards: only body pages (never the Contents/copyright page), only short
    blocks, and each TOC title marks at most ONE opener (its first occurrence), so a
    repeated running head can't spawn phantom units. Additive — never un-marks a hit."""
    titles = {norm_title(t) for (lvl, t, _pg) in (pdftoc or []) if lvl <= 2}
    titles |= {norm_title(t) for t in contents_titles}
    titles.discard("")
    if not titles:
        return 0
    drop_pages = {b["page"] for b in seq if is_front_drop(b["text"])}
    used, marked = set(), 0
    for b in seq:
        if b["chap"] or b["toc"] or b["words"] > 14 or b["page"] in drop_pages:
            continue
        nb = norm_title(b["text"])
        if len(nb) < 4:
            continue
        hit = next((t for t in titles if t not in used
                    and (nb == t or (len(nb) >= 6 and (nb in t or t in nb)))), None)
        if hit:
            b["kind"], b["chap"] = "heading", True
            used.add(hit); marked += 1
    return marked


def is_front_drop(text):
    """Title/copyright/contents pages BOOKSMITH regenerates to spec -> drop from units."""
    return bool(FRONT_KW.search(text) or TOC_KW.match(text))


def segment(seq):
    """Front matter = everything before the first REAL chapter opener; from there each
    heading starts a unit. Dedication/epigraph prose is captured; title/copyright/
    contents/TOC entries are dropped (regenerated to spec)."""
    # any page holding copyright/contents furniture is a front-matter page: drop it whole
    # (the copyright disclaimer spans several blocks; per-line matching leaks the rest).
    drop_pages = {b["page"] for b in seq if is_front_drop(b["text"])}
    body_start = next((i for i, b in enumerate(seq) if b["kind"] == "heading" and b["chap"]), None)
    if body_start is None:                    # no keyworded chapters: first heading after front matter
        fm_end = max((i for i, b in enumerate(seq) if is_front_drop(b["text"])), default=-1)
        body_start = next((i for i, b in enumerate(seq) if i > fm_end and b["kind"] == "heading"), None)
    front, units, cur = [], [], None
    for i, b in enumerate(seq):
        if body_start is None or i < body_start:
            if (b["kind"] == "body" and not b["toc"] and b["page"] not in drop_pages
                    and not is_front_drop(b["text"]) and len(b["text"].split()) >= 4):
                front.append(b["text"])       # dedication / epigraph before ch.1
            continue
        if b["kind"] == "heading" and not b["toc"]:
            cur = {"title": b["text"].strip(), "paras": []}
            units.append(cur)
        elif cur is not None and not b["toc"]:
            cur["paras"].append(b["text"])
    return front, [u for u in units if u["paras"] or len(u["title"].split()) <= 14]


# ---------------------------------------------------------------- meta
def detect_meta(meta, pages, seq):
    title = despace((meta.get("title") or "").strip())
    author = despace((meta.get("author") or "").strip())
    if not title or not author:
        first = sorted([b for b in seq if b["page"] == 0], key=lambda b: -b["size"])
        if first and not title:
            title = first[0]["text"].strip()
        if len(first) > 1 and not author:
            author = first[1]["text"].strip()
    txt = " ".join(l["text"] for p in pages[:40] for b in p["blocks"] for l in b["lines"])
    cjk = sum(1 for ch in txt if "一" <= ch <= "鿿")
    lang = "zh" if cjk > max(50, len(txt) * 0.05) else "en"
    w, h = pages[0]["w"] / 72.0, pages[0]["h"] / 72.0
    tw, th = min(STD_TRIMS, key=lambda t: abs(t[0] - w) + abs(t[1] - h))
    return {"title": title or "Untitled", "author": author or "Unknown",
            "language": lang, "trim": {"w": tw, "h": th}}


# ---------------------------------------------------------------- scaffold
def unit_id(i, title, used):
    t = title.lower()
    for k in ("prologue", "epilogue", "foreword", "preface", "introduction",
              "afterword", "appendix", "conclusion", "coda"):
        if k in t and k not in used:
            return k
    return f"ch_{i:02d}"


def build_config(m, units, front, slug, is_fiction):
    zh = m["language"] == "zh"
    ucfg, used = [], set()
    for n, u in enumerate(units, 1):
        wid = unit_id(n, u["title"], used)
        while wid in used:
            wid = f"ch_{n:02d}_{len(used)}"
        used.add(wid); u["_id"] = wid
        words = sum(len(p.split()) for p in u["paras"])
        ucfg.append({"id": wid, "title": u["title"], "target_words": max(50, words)})
    fm = [{"type": "half_title", "valign": "center"}, {"type": "blank"},
          {"type": "title", "valign": "center"}, {"type": "copyright", "valign": "bottom"}]
    if front:
        fm.append({"type": "dedication", "valign": "center"})
    fm.append({"type": "contents"})
    if len(front) > 1:
        fm.append({"type": "readers_note"})
    cfg = {
        "title": m["title"], "author": m["author"], "slug": slug,
        "genre": "imported (re-typeset from PDF)", "is_fiction": bool(is_fiction),
        "language": m["language"], "math": False, "integration_mode": "reforge",
        "units": ucfg, "trim": m["trim"], "paper": "white", "finish": "matte",
        "formats": ["kindle", "epub", "kdp_paperback", "kdp_hardcover", "digital_pdf"],
        "interior": {"body_pt": 11, "leading": 320, "body_font": "SimSun" if zh else "Georgia"},
        "front_matter": fm, "recto_strategy": "odd_page_sections",
        "cover": {"mood": "imported (review)", "title_face": "CormorantGaramond",
                  "palette": {"navy": "0B1420", "cream": "F4EFE0", "gold": "C9A760"},
                  "art": {"prompt_seed": "restrained editorial book cover, generous negative "
                          "space in the upper third for a title, print-safe",
                          "negative_prompt": "text, watermark, letters, title, busy, cluttered"}},
        "authorship": {"default_class": "C", "per_chapter_overrides": {}},
        "voice": {"unit_noun": "chapter", "no_em_dashes": False, "blacklist": [],
                  "greenlist": [], "sacred_terms": []},
    }
    # captured front-matter prose -> schema-valid STRING fields (human may reclassify;
    # dedication + readers_note are strings; epigraph is an object, so we don't guess it).
    # Their front_matter[] entries were added above so the text actually renders.
    if front:
        cfg["dedication"] = front[0]
    if len(front) > 1:
        cfg["readers_note"] = "\n\n".join(front[1:])
    return cfg


def scaffold(cfg, units, out_dir: Path):
    cur = out_dir / "manuscript" / "current"
    cur.mkdir(parents=True, exist_ok=True)
    (out_dir / "cover_art").mkdir(exist_ok=True)
    (out_dir / "outputs").mkdir(exist_ok=True)
    for u in units:
        body = "\n\n".join(u["paras"]).strip()
        (cur / f"{u['_id']}_current.md").write_text(f"# {u['title']}\n\n{body}\n", encoding="utf-8")
    (out_dir / "book_config.json").write_text(
        json.dumps(cfg, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def validate(cfg):
    try:
        import jsonschema
        schema = json.loads((REPO / "_tools" / "book_config.schema.json").read_text(encoding="utf-8"))
        jsonschema.validate(cfg, schema)
        return "schema-valid"
    except ImportError:
        return "jsonschema not installed (skipped)"
    except Exception as e:
        return f"SCHEMA WARNING: {str(e)[:180]}"


# ---------------------------------------------------------------- run
def run(pdf: Path, slug, title, author, trim, out, is_fiction):
    meta, pages, pdftoc = extract(pdf)
    if not pages or not any(p["blocks"] for p in pages):
        raise RuntimeError("no extractable text (scanned/image-only PDF? OCR needed — not wired)")
    bsz = body_size(pages)
    heads, feet = running_furniture(pages)
    seq = classify_blocks(pages, bsz, heads, feet)
    toc_titles = find_toc_titles(seq)
    toc_marked = apply_toc(seq, pdftoc, toc_titles)   # book's own TOC = authoritative cross-check
    front, units = segment(seq)
    m = detect_meta(meta, pages, seq)
    if title:
        m["title"] = title
    if author:
        m["author"] = author
    if trim:
        w, h = (float(x) for x in re.split(r"[x×]", trim.lower()))
        m["trim"] = {"w": w, "h": h}
    slug = slug or slugify(m["title"])
    out_dir = Path(out) if out else REPO / "book_workspace" / slug
    cfg = build_config(m, units, front, slug, is_fiction)
    scaffold(cfg, units, out_dir)
    total_words = sum(sum(len(p.split()) for p in u["paras"]) for u in units)
    warnings = []
    if len(units) < 2:
        warnings.append("fewer than 2 units — no PDF outline + weak headings; may need a manual split")
    if m["author"] in ("Unknown", ""):
        warnings.append("author not detected — set it in book_config.json")
    return {
        "pdf": str(pdf), "pages": len(pages), "workspace": str(out_dir),
        "title": m["title"], "author": m["author"], "language": m["language"],
        "trim": m["trim"], "body_pt_detected": bsz, "units": len(units),
        "total_words": total_words, "pdf_toc_entries": len(pdftoc),
        "contents_titles_seen": len(toc_titles), "toc_openers_marked": toc_marked,
        "running_furniture": sorted(heads | feet)[:6],
        "config_validation": validate(cfg),
        "front_matter_captured": [f[:60] for f in front[:3]],
        "unit_titles": [u["title"][:60] for u in units], "warnings": warnings,
    }


def selftest():
    import fitz, tempfile
    tmp = Path(tempfile.mkdtemp())
    doc = fitz.open()
    pg = doc.new_page(width=432, height=648)                 # title page
    pg.insert_text((110, 200), "THE TEST BOOK", fontsize=28)
    pg.insert_text((150, 260), "A. N. Author", fontsize=16)
    pg = doc.new_page(width=432, height=648)                 # copyright
    pg.insert_text((72, 120), "Copyright (c) 2026. All rights reserved. ISBN 000.", fontsize=10)
    pg = doc.new_page(width=432, height=648)                 # dedication
    pg.insert_text((72, 300), "For the ones who kept rowing.", fontsize=12)
    # two chapters — titles LETTER-SPACED like BOOKSMITH's real output (the regression guard)
    for ti, body in [("C H A P T E R  O N E  —  T H E  S T A R T",
                      "This is the first paragraph of chapter one, long enough to be real prose."),
                     ("C H A P T E R  T W O  —  T H E  M I D D L E",
                      "The second chapter opens here with its own paragraph of ordinary text.")]:
        pg = doc.new_page(width=432, height=648)
        pg.insert_text((72, 120), ti, fontsize=14)           # opener title (letter-spaced, like real output)
        pg.insert_text((72, 320), body, fontsize=12)         # body well below -> a separate block
        pg.insert_text((210, 620), "12", fontsize=9)         # page-number furniture
    p = tmp / "test_book.pdf"
    doc.save(str(p)); doc.close()
    r = run(p, "selftest_book", None, None, None, str(tmp / "ws"), False)
    checks = {
        "2 units": r["units"] == 2,
        "title detected": r["title"] == "THE TEST BOOK",
        "de-spaced chapter title": any("CHAPTER ONE" in t for t in r["unit_titles"]),
        "no front matter as unit": not any(x in " ".join(r["unit_titles"])
                                           for x in ("TEST BOOK", "Copyright", "CONTENTS", "12")),
        "schema-valid config": r["config_validation"] == "schema-valid",
    }
    ok = all(checks.values())
    print("PDF_TO_BOOK SELFTEST:", "PASS" if ok else "FAIL")
    for k, v in checks.items():
        print(f"   [{'ok' if v else 'XX'}] {k}")
    if not ok:
        print("   detail:", {k: r[k] for k in ("units", "title", "unit_titles", "config_validation")})
    return 0 if ok else 1


def main(argv=None):
    u8()
    ap = argparse.ArgumentParser(description="Decompose a finished-book PDF into a BOOKSMITH workspace.")
    ap.add_argument("pdf", nargs="?", help="the finished book PDF")
    ap.add_argument("--slug"); ap.add_argument("--title"); ap.add_argument("--author")
    ap.add_argument("--trim", help="e.g. 6x9 (else inferred from the page size)")
    ap.add_argument("--out", help="workspace dir (default book_workspace/<slug>)")
    ap.add_argument("--is-fiction", action="store_true")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()
    if not a.pdf:
        ap.print_help(); return 2
    try:
        r = run(Path(a.pdf), a.slug, a.title, a.author, a.trim, a.out, a.is_fiction)
    except Exception as e:
        print(f"pdf_to_book failed: {e}", file=sys.stderr); return 1
    if a.json:
        print(json.dumps(r, ensure_ascii=False, indent=2)); return 0
    print(f"\n  IMPORTED: {r['title']} — {r['author']}")
    print(f"  {r['pages']} pages | {r['units']} units | {r['total_words']:,} words | "
          f"trim {r['trim']['w']}x{r['trim']['h']} | lang {r['language']} | body ~{r['body_pt_detected']}pt")
    print(f"  config: {r['config_validation']}  |  workspace: {r['workspace']}")
    if r["warnings"]:
        for w in r["warnings"]:
            print(f"  [warn] {w}")
    print("  proposed units:")
    for i, t in enumerate(r["unit_titles"], 1):
        print(f"    {i:>2}. {t}")
    print("\n  >> REVIEW book_config.json (unit split, title/author, trim, titles are UPPERCASE as")
    print("     rendered — retitle if you want mixed case), THEN produce the distinct formats:")
    print(f"     python _tools/produce_book.py --config {r['workspace']}\\book_config.json "
          f"--formats kindle,kdp_paperback,kdp_hardcover,digital")
    print("     (reflowable Kindle + KDP paperback + KDP hardcover are each their own build.)\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
