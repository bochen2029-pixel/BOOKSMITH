#!/usr/bin/env python3
"""
export_master_pdf.py — full-resolution MASTER PDF export (Word COM).

WHY: `docx_to_pdf.py` uses SaveAs(FileFormat=17), which is Word's screen-optimized
PDF path — it downsamples embedded images (~200 ppi observed). That is correct for
an upload/reading copy and wrong for an ARCHIVE MASTER, where the whole point is
that the notebook scans keep every pixel the archive gave us.

This uses ExportAsFixedFormat with OptimizeFor=wdExportOptimizeForPrint (0) and
bitmap-missing-fonts off, which preserves image resolution. The result is a large
file on purpose.

    python export_master_pdf.py <in.docx> <out.pdf> [--covers front.jpg back.jpg]

With --covers, the front and back cover images are prepended/appended as exact
6x9-inch (432x648 pt) pages via PyMuPDF, matching build_digital_pdf.py's geometry,
so the master is a complete book object rather than a bare interior.
Prints JSON. Windows + Word required.
"""
from __future__ import annotations

import argparse
import json
import os
import sys

WD_EXPORT_PDF = 17
WD_OPTIMIZE_FOR_PRINT = 0
WD_EXPORT_ALL_DOC = 0
WD_EXPORT_DOC_WITH_MARKUP = 7
WD_EXPORT_CREATE_HEADING_BOOKMARKS = 1


def export(docx: str, pdf: str) -> dict:
    import pythoncom
    import win32com.client as win32

    pythoncom.CoInitialize()
    word = None
    doc = None
    try:
        try:
            word = win32.DispatchEx("Word.Application")
        except Exception:
            word = win32.Dispatch("Word.Application")
        word.Visible = False
        word.DisplayAlerts = 0
        doc = word.Documents.Open(os.path.abspath(docx), ReadOnly=False, Visible=False)

        # Repaginate so the page count and any fields are current.
        try:
            for i in range(1, doc.TablesOfContents.Count + 1):
                doc.TablesOfContents(i).Update()
        except Exception:
            pass
        try:
            doc.Repaginate()
        except Exception:
            pass

        doc.ExportAsFixedFormat(
            OutputFileName=os.path.abspath(pdf),
            ExportFormat=WD_EXPORT_PDF,
            OpenAfterExport=False,
            OptimizeFor=WD_OPTIMIZE_FOR_PRINT,   # <- the setting that keeps image resolution
            Range=WD_EXPORT_ALL_DOC,
            Item=WD_EXPORT_DOC_WITH_MARKUP - 7,  # 0 = document contents only
            IncludeDocProps=True,
            KeepIRM=True,
            CreateBookmarks=WD_EXPORT_CREATE_HEADING_BOOKMARKS,  # navigable chapter bookmarks
            DocStructureTags=True,                                # tagged PDF (accessibility)
            BitmapMissingFonts=False,
            UseISO19005_1=False,
        )
        pages = int(doc.ComputeStatistics(2))
        words = int(doc.ComputeStatistics(0))
        return {"pages": pages, "words": words}
    finally:
        try:
            if doc is not None:
                doc.Close(False)
        except Exception:
            pass
        try:
            if word is not None:
                word.Quit()
        except Exception:
            pass
        pythoncom.CoUninitialize()


def add_covers(pdf: str, front: str, back: str) -> int:
    """Prepend the front cover and append the back cover as exact 6x9in pages."""
    import fitz

    W, H = 432.0, 648.0  # 6x9 inches in points
    src = fitz.open(pdf)
    out = fitz.open()

    def cover_page(img_path):
        page = out.new_page(width=W, height=H)
        # Scale-to-fit inside the trim so nothing is cropped, centered.
        pix = fitz.Pixmap(img_path)
        ar_img, ar_pg = pix.width / pix.height, W / H
        if ar_img > ar_pg:
            w, h = W, W / ar_img
        else:
            h, w = H, H * ar_img
        rect = fitz.Rect((W - w) / 2, (H - h) / 2, (W + w) / 2, (H + h) / 2)
        page.insert_image(rect, filename=img_path)

    if front and os.path.exists(front):
        cover_page(front)
    out.insert_pdf(src)
    if back and os.path.exists(back):
        cover_page(back)
    total = out.page_count
    tmp = pdf + ".tmp"
    out.save(tmp, deflate=True, garbage=3)
    out.close()
    src.close()
    os.replace(tmp, pdf)
    return total


def restore_full_res(pdf: str, sources: list[str]) -> dict:
    """Word's PDF export downsamples every embedded image to ~200 ppi and there is
    no COM switch that prevents it (OptimizeFor=print does not). So put the real
    pixels back: walk the interior images in document order and swap each one for
    its original file. Order is reliable because the generator embeds figures in
    manuscript order and the export preserves that order."""
    import fitz

    doc = fitz.open(pdf)
    placements = []
    for pno in range(doc.page_count):
        for img in doc[pno].get_images(full=True):
            xref = img[0]
            rects = doc[pno].get_image_rects(xref)
            if rects:
                placements.append((pno, xref, rects[0]))

    swapped, skipped = 0, []
    # The covers were added by us at full resolution already; only interior
    # figures (everything between them) need restoring.
    interior = [p for p in placements if 0 < p[0] < doc.page_count - 1]
    for (pno, xref, rect), src in zip(interior, sources):
        if not os.path.exists(src):
            skipped.append(src)
            continue
        try:
            doc[pno].replace_image(xref, filename=src)
            swapped += 1
        except Exception as exc:            # noqa: BLE001 - report, don't abort the master
            skipped.append(f"{os.path.basename(src)}: {exc}")

    tmp = pdf + ".hi"
    doc.save(tmp, deflate=True, garbage=3)
    doc.close()
    os.replace(tmp, pdf)
    return {"images_restored": swapped, "interior_images": len(interior), "skipped": skipped}


def figure_sources(master_md: str, workspace: str) -> list[str]:
    """Ordered list of figure paths as they appear in the assembled manuscript."""
    import re as _re
    if not os.path.exists(master_md):
        return []
    text = open(master_md, encoding="utf-8").read()
    out = []
    for m in _re.finditer(r"^!\[[^\]]*\]\(([^)\s]+)\)\s*$", text, _re.M):
        out.append(os.path.join(workspace, m.group(1).replace("/", os.sep)))
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description="Full-resolution master PDF export (Word COM).")
    ap.add_argument("docx")
    ap.add_argument("pdf")
    ap.add_argument("--covers", nargs=2, metavar=("FRONT", "BACK"),
                    help="Front and back cover images to wrap the interior with.")
    ap.add_argument("--restore-from", metavar="MASTER_MD",
                    help="Assembled manuscript markdown; its figure paths are swapped "
                         "back in at full resolution after Word's downsampling.")
    ap.add_argument("--workspace", help="Workspace root for resolving figure paths.")
    a = ap.parse_args()

    if not os.path.exists(a.docx):
        print(json.dumps({"error": f"not found: {a.docx}"}))
        return 1

    info = export(a.docx, a.pdf)
    if a.covers:
        info["total_pages"] = add_covers(a.pdf, a.covers[0], a.covers[1])
    if a.restore_from:
        ws = a.workspace or os.path.dirname(os.path.dirname(os.path.dirname(a.restore_from)))
        srcs = figure_sources(a.restore_from, ws)
        info["restore"] = restore_full_res(a.pdf, srcs)
    info["pdf"] = os.path.abspath(a.pdf)
    info["size_mb"] = round(os.path.getsize(a.pdf) / (1024 * 1024), 2)
    info["optimize_for"] = "print (images NOT downsampled)"
    print(json.dumps(info, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
