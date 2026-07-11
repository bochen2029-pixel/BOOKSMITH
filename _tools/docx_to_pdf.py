"""
docx_to_pdf.py — The only trustworthy docx->PDF path (Microsoft Word COM).

BOOKSMITH toolchain component. Renders a DOCX to a page-faithful PDF via Word
COM automation. Pandoc / LibreOffice-headless / cloud converters all break
fonts, TOC hyperlinks, and pagination, so Word COM is a hard platform
dependency (Windows + installed Microsoft Word). Also returns the authoritative
page count + word count that downstream spine math and parity checks depend on.

PORTED FROM:
  - C:\\BOOK\\_tools\\docx_to_pdf.py            (the base Dispatch/SaveAs shape)
  - C:\\Inside_The_Region\\update_hardcover_and_count.py  (double-Repaginate + stats)

CRITICAL FIX BAKED IN (LESSONS_LEDGER §3.7, transcript tx_book_aibook):
  A TOC .Update() DELETES AND RECREATES field handles. A live
  `for field in doc.Fields: field.Update()` then dereferences stale/deleted
  handles -> COM error -> exit 1. The fix is to iterate fields BY INDEX inside
  a try/except, in the exact order:
      update TOC(s) -> Repaginate() -> fields-by-index -> update TOC(s) -> Repaginate()
  A live iterator is NEVER used. See update_fields_by_index() below.

Word format constants:
  wdFormatPDF = 17 ; wdStatisticPages = 2 ; wdStatisticWords = 0.

Usage:
  python docx_to_pdf.py <input.docx> <output.pdf>

On success prints a single JSON object on stdout:
  {"docx": "...", "pdf": "...", "pages": <int>, "words": <int>}
"""
import sys
import os
import json

import win32com.client

# Word enum constants (avoid importing the makepy typelib — plain ints are stable).
WD_FORMAT_PDF = 17       # wdFormatPDF
WD_STAT_PAGES = 2        # wdStatisticPages
WD_STAT_WORDS = 0        # wdStatisticWords
WD_ALERTS_NONE = 0       # wdAlertsNone


def update_all_tocs(doc):
    """Update every TablesOfContents field. This is what deletes/recreates the
    underlying field handles, which is why the subsequent field loop must go by
    index, not by a live iterator."""
    toc_count = doc.TablesOfContents.Count
    for i in range(1, toc_count + 1):
        doc.TablesOfContents(i).Update()
    return toc_count


def update_fields_by_index(doc):
    """Update fields BY INDEX, each guarded in try/except.

    A live `for field in doc.Fields: field.Update()` can dereference handles
    that a prior TOC update deleted -> COM error -> exit 1 (LESSONS_LEDGER
    §3.7 / tx_book_aibook). Iterating by index and swallowing per-field errors
    is the crash fix."""
    # Snapshot the count once; do not trust a live iterator across updates.
    field_count = doc.Fields.Count
    for i in range(1, field_count + 1):
        try:
            doc.Fields(i).Update()
        except Exception:
            # Update fields by index (live iteration can hit deleted handles).
            pass


def docx_to_pdf(docx_path: str, pdf_path: str):
    """Convert DOCX -> PDF via Word COM. Returns (pages, words)."""
    docx_path = os.path.abspath(docx_path)
    pdf_path = os.path.abspath(pdf_path)

    if not os.path.exists(docx_path):
        raise FileNotFoundError(f"Input DOCX not found: {docx_path}")

    out_dir = os.path.dirname(pdf_path)
    if out_dir and not os.path.isdir(out_dir):
        os.makedirs(out_dir, exist_ok=True)

    word = win32com.client.Dispatch("Word.Application")
    word.Visible = False
    try:
        word.DisplayAlerts = WD_ALERTS_NONE
    except Exception:
        pass

    doc = None
    try:
        doc = word.Documents.Open(docx_path)

        # --- The load-bearing order (LESSONS_LEDGER §3.7) ---
        # 1. update TOC(s)
        update_all_tocs(doc)
        # 2. Repaginate (settle page numbers before touching fields)
        doc.Repaginate()
        # 3. fields-by-index (guarded) — TOC update just invalidated handles
        update_fields_by_index(doc)
        # 4. update TOC(s) again — field updates may have shifted page numbers
        update_all_tocs(doc)
        # 5. Repaginate again — final settle for TOC-bearing docs
        doc.Repaginate()

        pages = int(doc.ComputeStatistics(WD_STAT_PAGES))
        words = int(doc.ComputeStatistics(WD_STAT_WORDS))

        doc.SaveAs(pdf_path, FileFormat=WD_FORMAT_PDF)
        doc.Close(SaveChanges=False)
        doc = None
        return pages, words
    finally:
        if doc is not None:
            try:
                doc.Close(SaveChanges=False)
            except Exception:
                pass
        word.Quit()


def pad_pdf_to_multiple(pdf_path, multiple):
    """Append blank pages (matching page 1 dimensions) until the page count is a
    multiple of `multiple`. Mixam requires the interior page count divisible by 4
    (KDP only needs 2); the JS generator defers this to a fitz post-step. Returns
    the final page count."""
    import fitz
    if not multiple or multiple <= 1:
        with fitz.open(pdf_path) as d:
            return d.page_count
    tmp = pdf_path + ".pad.tmp"
    with fitz.open(pdf_path) as doc:
        n = doc.page_count
        if n % multiple == 0:
            return n
        target = ((n // multiple) + 1) * multiple
        w, h = doc[0].rect.width, doc[0].rect.height
        for _ in range(target - n):
            doc.new_page(width=w, height=h)   # blank page appended at the end
        doc.save(tmp, deflate=True)
    os.replace(tmp, pdf_path)
    return target


def main() -> int:
    args = sys.argv[1:]
    pad_multiple = 0
    positional = []
    i = 0
    while i < len(args):
        if args[i] == "--pad-multiple":
            pad_multiple = int(args[i + 1]); i += 2; continue
        positional.append(args[i]); i += 1
    if len(positional) != 2:
        print("Usage: python docx_to_pdf.py <input.docx> <output.pdf> [--pad-multiple N]",
              file=sys.stderr)
        return 2
    docx_path, pdf_path = positional
    pages, words = docx_to_pdf(docx_path, pdf_path)
    final_pages = pages
    if pad_multiple:
        final_pages = pad_pdf_to_multiple(os.path.abspath(pdf_path), pad_multiple)
    out = {
        "docx": os.path.abspath(docx_path),
        "pdf": os.path.abspath(pdf_path),
        "pages": final_pages,
        "words": words,
    }
    if pad_multiple:
        out["pages_before_pad"] = pages
    print(json.dumps(out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
