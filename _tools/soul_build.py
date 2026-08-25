#!/usr/bin/env python3
"""soul_build.py — compile a book's SOUL knowledge base from its manufacturing record.

The first soul (docs/CLOUD_NEXT_PLAN §2.1; FUSOR Addendum C): a book that answers
questions FROM ITS OWN PAGES, with the printed folio on every answer. This tool
builds the grounded substrate:

  * spans = the book's actual prose, paragraph-grain, from manuscript/current/
    in config unit order (image reference lines dropped; captions kept, tagged).
  * every span carries the PRINTED FOLIO the family sees in the delivered digital
    PDF — extracted positionally from each page's footer block, then matched by
    normalized head-substring. The cite chip must show the page a reader can
    actually turn to, or it is theater.
  * the KB is the CITABLE UNIVERSE, and it is the book's pages ONLY. Digests,
    registries, and seed stay out by constitutional design: "every answer must
    trace to the book's own pages or decline." (They may inform a serving
    system prompt; they are never quotable content.)
  * if registry/authorship_ledger.jsonl exists, spans from human-latest units
    are tagged human_authored — the soul may say which lines a human hand wrote.

  python _tools/soul_build.py --config book_workspace/<slug>/book_config.json \
      [--pdf outputs/digital/<slug>_DIGITAL.pdf] [--out soul/kb.json]

Output: <workspace>/soul/kb.json  {meta, spans[{id, unit, unit_title, kind,
folio, text, human}]} — deterministic, reproducible, versionable.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

IMG_RE = re.compile(r"^!\[[^\]]*\]\([^)]+\)\s*$")
CAPTION_RE = re.compile(r"^\*[^*].*\*\s*$")


def norm(s: str) -> str:
    s = unicodedata.normalize("NFC", s)
    return re.sub(r"\s+", "", s)


def page_folios(pdf_path: Path) -> list[tuple[str, str | None]]:
    """[(normalized page text, printed folio or None)] per physical page."""
    import fitz
    out = []
    doc = fitz.open(str(pdf_path))
    for page in doc:
        h = page.rect.height
        folio = None
        cands = []
        for b in page.get_text("blocks"):
            x0, y0, x1, y1, text = b[0], b[1], b[2], b[3], b[4]
            t = text.strip()
            if y0 > h * 0.85 and re.fullmatch(r"\d{1,3}", t):
                cands.append((y0, t))
        if cands:
            folio = sorted(cands)[-1][1]
        out.append((norm(page.get_text()), folio))
    doc.close()
    return out


def find_folio(span_text: str, pages: list[tuple[str, str | None]]) -> str | None:
    # markdown emphasis/backticks exist in the source but not in the rendered
    # PDF text — strip them or caption spans (*...*) never match their page
    span_text = re.sub(r"[*_`]", "", span_text)
    head = norm(span_text)[:60]
    if len(head) < 12:
        return None
    for ptext, folio in pages:
        if head in ptext:
            return folio
    # retry with a shorter head (a span may straddle a page break)
    head = head[:24]
    for ptext, folio in pages:
        if head in ptext:
            return folio
    return None


def build(config_path: Path, pdf_path: Path | None, out_path: Path | None) -> dict:
    cfg = json.loads(config_path.read_text("utf-8"))
    ws = config_path.parent
    slug = cfg["slug"]
    if pdf_path is None:
        cand = ws / "outputs" / "digital" / f"{slug}_DIGITAL.pdf"
        pdf_path = cand if cand.exists() else None
    pages = page_folios(pdf_path) if pdf_path else []

    human_units: set[str] = set()
    hu = ws / "registry" / "human_edited_units.json"
    if hu.exists():
        try:
            human_units = set(json.loads(hu.read_text("utf-8")))
        except (json.JSONDecodeError, TypeError):
            pass

    spans = []
    n = 0
    unmatched = 0
    for u in cfg.get("units", []):
        uid, title = u.get("id"), str(u.get("title") or u.get("id"))
        cur = ws / "manuscript" / "current" / f"{uid}_current.md"
        if not cur.exists():
            continue
        body = cur.read_text("utf-8")
        # drop the H1; walk paragraph blocks
        lines = body.split("\n")
        if lines and lines[0].startswith("# "):
            lines = lines[1:]
        for para in re.split(r"\n\s*\n", "\n".join(lines)):
            p = para.strip()
            if not p or IMG_RE.match(p):
                continue
            kind = "caption" if CAPTION_RE.match(p) else \
                   ("heading" if p.startswith("#") else "prose")
            if kind == "heading":
                continue
            folio = find_folio(p, pages) if pages else None
            if pages and folio is None:
                unmatched += 1
            n += 1
            spans.append({
                "id": f"{slug}-{n:04d}", "unit": uid, "unit_title": title,
                "kind": kind, "folio": folio, "text": p,
                "human": uid in human_units,
            })

    kb = {
        "meta": {
            "slug": slug, "title": cfg.get("title"), "subtitle": cfg.get("subtitle"),
            "author": cfg.get("author"),
            "lang": cfg.get("language") or ("zh" if re.search(r"[一-鿿]", str(cfg.get("title"))) else "en"),
            "pdf": str(pdf_path) if pdf_path else None,
            "spans": len(spans), "folio_unmatched": unmatched,
        },
        "spans": spans,
    }
    if out_path is None:
        out_path = ws / "soul" / "kb.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(kb, ensure_ascii=False, indent=1), "utf-8", newline="\n")
    return {"out": str(out_path), **kb["meta"]}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--config", required=True)
    ap.add_argument("--pdf", default=None, help="digital PDF for folio mapping (default: outputs/digital/<slug>_DIGITAL.pdf)")
    ap.add_argument("--out", default=None)
    args = ap.parse_args(argv)
    r = build(Path(args.config).resolve(),
              Path(args.pdf) if args.pdf else None,
              Path(args.out) if args.out else None)
    print(json.dumps(r, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
