#!/usr/bin/env python3
"""render_pages.py: render the touched pages of a built interior PDF to small PNGs for a visual check.
Usage: python render_pages.py PDF OUTDIR NEEDLE [NEEDLE ...]
Each needle is searched in the PDF text; the first page carrying it is rendered at 100 dpi (6x9 in -> 600x900 px,
under the 2000 px vision guard). Prints the page numbers found."""
import os
import sys

import fitz

pdf, out = sys.argv[1], sys.argv[2]
needles = sys.argv[3:]
os.makedirs(out, exist_ok=True)
doc = fitz.open(pdf)
print("pages:", doc.page_count)
done = set()
for nd in needles:
    hit = None
    for i, page in enumerate(doc):
        if nd in page.get_text():
            hit = i
            break
    if hit is None:
        print("NOT FOUND:", nd)
        continue
    for pno in (hit, hit + 1):
        if pno >= doc.page_count or pno in done:
            continue
        done.add(pno)
        pix = doc[pno].get_pixmap(dpi=100)
        name = "%s/p%03d.png" % (out, pno + 1)
        pix.save(name)
        print("page %d (%s) -> %s %dx%d" % (pno + 1, nd[:20], os.path.basename(name), pix.width, pix.height))
