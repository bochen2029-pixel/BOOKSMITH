"""
docx_to_pdf.py — The only trustworthy docx->PDF path (Microsoft Word COM).

BOOKSMITH toolchain component. Renders a DOCX to a page-faithful PDF via Word
COM automation (the primary, page-faithful path). Pandoc / cloud converters
break fonts, TOC hyperlinks, and pagination; LibreOffice is close but not
guaranteed page-faithful, so it is a TIER-2 FALLBACK used only when Word is
absent (Mac / Linux / no-Word), never in preference to Word. Also returns the
authoritative page + word count that downstream spine math and parity checks use.

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
import shutil

try:
    import win32com.client
    _WIN32COM_IMPORT_ERROR = None
except ImportError as _exc:  # non-Windows, or pywin32 not installed
    win32com = None
    _WIN32COM_IMPORT_ERROR = _exc


def _require_word():
    """Fail with an actionable JSON error instead of an import traceback."""
    if win32com is None:
        print(json.dumps({
            "error": "word_com_unavailable",
            "detail": "Print docx->PDF needs Microsoft Word COM (pywin32, page-faithful) "
                      "OR LibreOffice ('soffice' on PATH, Tier-2 best-effort). Neither was "
                      "found. Produce EPUB / Kindle DOCX here (Tier 2), install LibreOffice "
                      "for print PDFs off Windows, or render the DOCX externally.",
            "import_error": str(_WIN32COM_IMPORT_ERROR),
        }))
        raise SystemExit(3)

# Word enum constants (avoid importing the makepy typelib — plain ints are stable).
WD_FORMAT_PDF = 17       # wdFormatPDF
WD_STAT_PAGES = 2        # wdStatisticPages
WD_STAT_WORDS = 0        # wdStatisticWords
WD_ALERTS_NONE = 0       # wdAlertsNone


def _make_word():
    """Robust Word.Application factory.

    Late-bound Dispatch() can attach to a leftover/stuck Word instance whose
    dynamic dispatch then fails to resolve standard members (observed:
    AttributeError on TablesOfContents / Repaginate). Prefer EARLY binding
    (gencache.EnsureDispatch loads the Word type library so every member
    resolves); then a fresh out-of-process instance (DispatchEx); then plain
    late binding as a last resort."""
    w = win32com.client
    for factory in (
        lambda: w.gencache.EnsureDispatch("Word.Application"),
        lambda: w.DispatchEx("Word.Application"),
        lambda: w.Dispatch("Word.Application"),
    ):
        try:
            return factory()
        except Exception:
            continue
    return w.Dispatch("Word.Application")


def update_all_tocs(doc):
    """Update every TablesOfContents field. This is what deletes/recreates the
    underlying field handles, which is why the subsequent field loop must go by
    index, not by a live iterator."""
    # Resilient: a print interior with no TOC — or late-bound COM dispatch that
    # cannot resolve the TablesOfContents collection — must not kill the render.
    try:
        toc_count = doc.TablesOfContents.Count
    except Exception:
        return 0
    for i in range(1, toc_count + 1):
        try:
            doc.TablesOfContents(i).Update()
        except Exception:
            pass
    return toc_count


def update_fields_by_index(doc):
    """Update fields BY INDEX, each guarded in try/except.

    A live `for field in doc.Fields: field.Update()` can dereference handles
    that a prior TOC update deleted -> COM error -> exit 1 (LESSONS_LEDGER
    §3.7 / tx_book_aibook). Iterating by index and swallowing per-field errors
    is the crash fix."""
    # Snapshot the count once; do not trust a live iterator across updates.
    try:
        field_count = doc.Fields.Count
    except Exception:
        return
    for i in range(1, field_count + 1):
        try:
            doc.Fields(i).Update()
        except Exception:
            # Update fields by index (live iteration can hit deleted handles).
            pass


def _soffice_bin():
    """Locate a LibreOffice/OpenOffice 'soffice' binary for the Tier-2 fallback."""
    for name in ("soffice", "libreoffice", "soffice.bin"):
        p = shutil.which(name)
        if p:
            return p
    for c in (r"C:\Program Files\LibreOffice\program\soffice.exe",
              r"C:\Program Files (x86)\LibreOffice\program\soffice.exe",
              "/Applications/LibreOffice.app/Contents/MacOS/soffice",
              "/usr/bin/soffice", "/usr/bin/libreoffice", "/snap/bin/libreoffice"):
        if os.path.exists(c):
            return c
    return None


def _docx_to_pdf_libreoffice(soffice: str, docx_path: str, pdf_path: str):
    """Tier-2 (no Word): render via 'soffice --headless --convert-to pdf'. Best-effort,
    NOT guaranteed page-faithful (fonts/TOC/pagination can drift vs Word), so it runs
    only when Word COM is unavailable. Page + word counts are read back from the
    rendered PDF with PyMuPDF. An isolated user-profile dir avoids the soffice lock."""
    import subprocess
    import tempfile
    import glob
    outdir = tempfile.mkdtemp(prefix="bs_lo_")
    try:
        profile = "-env:UserInstallation=file:///" + outdir.replace("\\", "/") + "/profile"
        cmd = [soffice, "--headless", "--norestore", profile,
               "--convert-to", "pdf:writer_pdf_Export", "--outdir", outdir, docx_path]
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        produced = glob.glob(os.path.join(outdir, "*.pdf"))
        if not produced:
            raise RuntimeError(f"LibreOffice produced no PDF (rc={r.returncode}): "
                               f"{(r.stdout + r.stderr).strip()[-300:]}")
        shutil.move(produced[0], pdf_path)
    finally:
        shutil.rmtree(outdir, ignore_errors=True)
    import fitz
    with fitz.open(pdf_path) as d:
        pages = d.page_count
        words = sum(len(pg.get_text("text").split()) for pg in d)
    return pages, words


def docx_to_pdf(docx_path: str, pdf_path: str):
    """Convert DOCX -> PDF. Primary: Word COM (page-faithful). Fallback: LibreOffice
    (Tier-2, best-effort) only when Word is unavailable. Returns (pages, words, renderer)."""
    docx_path = os.path.abspath(docx_path)
    pdf_path = os.path.abspath(pdf_path)

    if not os.path.exists(docx_path):
        raise FileNotFoundError(f"Input DOCX not found: {docx_path}")

    out_dir = os.path.dirname(pdf_path)
    if out_dir and not os.path.isdir(out_dir):
        os.makedirs(out_dir, exist_ok=True)

    if win32com is not None:
        try:
            pages, words = _docx_to_pdf_word(docx_path, pdf_path)
            return pages, words, "word"
        except Exception:
            soffice = _soffice_bin()
            if soffice:
                pages, words = _docx_to_pdf_libreoffice(soffice, docx_path, pdf_path)
                return pages, words, "libreoffice_after_word_error"
            raise
    soffice = _soffice_bin()
    if soffice:
        pages, words = _docx_to_pdf_libreoffice(soffice, docx_path, pdf_path)
        return pages, words, "libreoffice"
    _require_word()  # emits the structured error + SystemExit(3)


def _docx_to_pdf_word(docx_path: str, pdf_path: str):
    """The page-faithful Word COM path. Returns (pages, words). Paths are already
    absolute and the output dir exists (the docx_to_pdf dispatcher guarantees that)."""
    word = _make_word()
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
    pages, words, renderer = docx_to_pdf(docx_path, pdf_path)
    final_pages = pages
    if pad_multiple:
        final_pages = pad_pdf_to_multiple(os.path.abspath(pdf_path), pad_multiple)
    out = {
        "docx": os.path.abspath(docx_path),
        "pdf": os.path.abspath(pdf_path),
        "pages": final_pages,
        "words": words,
        "renderer": renderer,
    }
    if pad_multiple:
        out["pages_before_pad"] = pages
    print(json.dumps(out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
