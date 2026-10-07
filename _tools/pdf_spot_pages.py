#!/usr/bin/env python3
"""pdf_spot_pages.py: render the pages of a built PDF that carry given text needles (or given page
numbers) to PNGs small enough for a vision spot check (longest side capped at 2000 px, the ingestion
guard), and say which page each needle landed on. Anchors by TEXT, never by page number, because
pagination moves between builds; use --context to render the following page(s) as well.

Usage:
  python _tools/pdf_spot_pages.py BOOK.pdf --out DIR --needle 致謝 --needle BRIT606322 [--context 1] [--dpi 100]
  python _tools/pdf_spot_pages.py BOOK.pdf --out DIR --page 10 --page 165
Notes: CJK text in justified lines may extract with stray spaces; a needle that is NOT FOUND is retried
with whitespace stripped from the page text. Needs PyMuPDF (fitz).
"""
import argparse
import os
import re
import sys


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("pdf")
    ap.add_argument("--out", required=True)
    ap.add_argument("--needle", action="append", default=[])
    ap.add_argument("--page", action="append", type=int, default=[], help="1-based page numbers")
    ap.add_argument("--context", type=int, default=0, help="also render this many following pages")
    ap.add_argument("--dpi", type=int, default=100)
    ap.add_argument("--all", action="store_true", help="every page carrying the needle, not only the first")
    a = ap.parse_args()
    import fitz
    doc = fitz.open(a.pdf)
    os.makedirs(a.out, exist_ok=True)
    print("pages:", doc.page_count)
    wanted = {}
    for n in a.page:
        wanted.setdefault(n - 1, []).append("page %d" % n)
    texts = None
    if a.needle:
        texts = [(p.get_text(), re.sub(r"\s+", "", p.get_text())) for p in doc]
    for nd in a.needle:
        nds = re.sub(r"\s+", "", nd)
        hits = [i for i, (t, ts) in enumerate(texts) if nd in t or nds in ts]
        if not hits:
            print("NOT FOUND:", nd)
            continue
        for h in (hits if a.all else hits[:1]):
            for k in range(h, min(doc.page_count, h + 1 + a.context)):
                wanted.setdefault(k, []).append(nd)
        print("%-30s page %s" % (nd[:30], ", ".join(str(h + 1) for h in (hits if a.all else hits[:1]))))
    for pno in sorted(wanted):
        page = doc[pno]
        dpi = a.dpi
        w_in = page.rect.width / 72.0
        h_in = page.rect.height / 72.0
        if max(w_in, h_in) * dpi > 2000:
            dpi = int(2000 / max(w_in, h_in))
        pix = page.get_pixmap(dpi=dpi)
        name = os.path.join(a.out, "p%03d.png" % (pno + 1))
        pix.save(name)
        print("page %d -> %s %dx%d  (%s)" % (pno + 1, os.path.basename(name), pix.width, pix.height,
                                            "; ".join(wanted[pno])[:60]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
