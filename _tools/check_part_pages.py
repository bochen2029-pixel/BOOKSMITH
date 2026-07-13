"""
check_part_pages.py — Recto-parity verifier (empirical, via Word COM).

BOOKSMITH toolchain component. Proves each chapter/part heading lands on a
recto (odd) page. Arithmetic is NOT trusted: any markdown edit re-breaks parity
(LESSONS_LEDGER §4.3), so the check is empirical — open the DOCX read-only in
Word, Repaginate, Find each unit heading, and read the page number Word
actually assigned it (Selection.Information(3) = wdActiveEndAdjustedPageNumber).

PORTED FROM: C:\\BOOK3\\_tools\\_titanic_source\\check_part_pages.py
  The base opens read-only, Repaginate(), HomeKey->Find each "PART N —" heading,
  reads Information(3), flags any even (verso) landing. The BOOKSMITH refactor
  reads the unit list + heading style from book_config.json instead of the
  hard-coded five Titanic parts, and emits the verdict as JSON for GATE-5.

Heading discovery (two tiers — exactly what the live check runs):
    1. An EXPLICIT heading-stem list, if one is given:
         --headings "A|B|C"  (pipe-separated CLI override), else
         book_config.check_part_pages.headings[]  (config-declared stems).
       Each stem is Find'd (Heading-1 style, case-insensitive) and its page read.
    2. else STRUCTURAL: every paragraph at outline level 1 (Heading 1) is a unit
       start. This is robust to the CONTENTS/TOC page (TOC entries are styled
       "TOC n", NOT outline level 1), to UPPERCASE rendering, and to em/en/hyphen
       dash variants — no text Find, no TOC collision. This is the default path.

Usage:
  python check_part_pages.py <in.docx> [--config book_config.json]
                                        [--headings "PART I|PART II|..."]

Prints a JSON object on stdout:
  {"docx":..., "total_pages":N, "unit_noun":"part",
   "results":[{"heading":"PART I","page":13,"recto":true}, ...],
   "all_recto": true|false}
Exit code 0 if all_recto, 1 if any unit landed on a verso, 2 on usage/IO error.
"""
import sys
import os
import json

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
            "detail": "Recto-parity verification requires Microsoft Word COM "
                      "(pywin32) on Windows. Without it, verify page parity "
                      "from the rendered PDF (PyMuPDF text search) or on the "
                      "KDP/Mixam previewer before upload.",
            "import_error": str(_WIN32COM_IMPORT_ERROR),
        }))
        raise SystemExit(3)

# Word enum constants.
WD_STORY = 6                 # wdStory (HomeKey unit)
WD_FIND_STOP = 0             # wdFindStop (Find.Wrap)
WD_STAT_PAGES = 2            # wdStatisticPages
WD_ADJ_PAGE_NUMBER = 3       # wdActiveEndAdjustedPageNumber (Selection.Information)
WD_ALERTS_NONE = 0           # wdAlertsNone
WD_OUTLINE_1 = 1             # wdOutlineLevel1 — Heading-1 paragraphs (chapter/part starts)


def load_config(config_path):
    if not config_path:
        return {}
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


def find_page_of(word_app, heading):
    """Return the adjusted page number where `heading` first appears, or None."""
    word_app.Selection.HomeKey(Unit=WD_STORY)
    find = word_app.Selection.Find
    find.ClearFormatting()
    try:
        find.Style = word_app.ActiveDocument.Styles("Heading 1")
    except Exception:
        pass
    find.Text = heading
    find.Forward = True
    find.Wrap = WD_FIND_STOP
    find.MatchCase = False
    if find.Execute():
        return int(word_app.Selection.Information(WD_ADJ_PAGE_NUMBER))
    return None


def _make_word():
    """Robust Word.Application factory (early binding first).

    Late-bound Dispatch() can attach to a leftover/stuck Word instance whose
    dynamic dispatch fails to resolve standard members (AttributeError on
    Repaginate / ComputeStatistics). EnsureDispatch loads the Word type library
    so every member resolves; DispatchEx forces a fresh instance; plain Dispatch
    is the last resort."""
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


def _config_declared_headings(cfg):
    """book_config.check_part_pages.headings[] — an explicit ordered list of
    heading STEMS to Find, matched before the dash tail (em/en/hyphen agnostic).
    Returns [] when absent."""
    cpp = (cfg or {}).get("check_part_pages") or {}
    hs = cpp.get("headings")
    if isinstance(hs, list) and hs:
        return [str(h).strip() for h in hs if str(h).strip()]
    return []


def check_pages(docx_path, cfg, headings_override):
    _require_word()
    word_app = _make_word()
    word_app.Visible = False
    try:
        word_app.DisplayAlerts = WD_ALERTS_NONE
    except Exception:
        pass

    doc = None
    try:
        doc = word_app.Documents.Open(os.path.abspath(docx_path), ReadOnly=True)
        doc.Repaginate()
        total_pages = int(doc.ComputeStatistics(WD_STAT_PAGES))

        # Heading discovery (two tiers only, matching the live code):
        #   1. --headings "A|B|C" OR book_config.check_part_pages.headings[] —
        #      an explicit stem list, Find each and read its page.
        #   2. else structural: chapter/part headings are the ONLY paragraphs at
        #      outline level 1 (Heading 1). Robust to the CONTENTS/TOC page (TOC
        #      entries are styled "TOC n", NOT outline level 1) and to UPPERCASE
        #      rendering + dash variants — no text Find, no TOC collision.
        results = []
        explicit = ([h.strip() for h in headings_override.split("|") if h.strip()]
                    if headings_override else _config_declared_headings(cfg))
        if explicit:
            for heading in explicit:
                page = find_page_of(word_app, heading)
                results.append({"heading": heading, "page": page,
                                "recto": (page % 2 == 1) if page else None})
        else:
            for para in doc.Paragraphs:
                try:
                    lvl = int(para.OutlineLevel)
                except Exception:
                    lvl = None
                try:
                    style_name = str(para.Style.NameLocal).lower()
                except Exception:
                    style_name = ""
                if not (lvl == WD_OUTLINE_1 or style_name in ("heading 1", "heading1")):
                    continue
                text = (para.Range.Text or "").replace("\r", "").replace("\x07", "").strip()
                if not text:
                    continue
                page = int(para.Range.Information(WD_ADJ_PAGE_NUMBER))
                results.append({"heading": text[:60], "page": page, "recto": page % 2 == 1})

        doc.Close(SaveChanges=False)
        doc = None
        return total_pages, results
    finally:
        if doc is not None:
            try:
                doc.Close(SaveChanges=False)
            except Exception:
                pass
        word_app.Quit()


def main() -> int:
    args = sys.argv[1:]
    if not args:
        print("Usage: python check_part_pages.py <in.docx> [--config book_config.json] "
              "[--headings \"PART I|PART II|...\"]", file=sys.stderr)
        return 2

    docx_path = None
    config_path = None
    headings_override = None
    i = 0
    while i < len(args):
        a = args[i]
        if a == "--config":
            config_path = args[i + 1]; i += 2; continue
        if a == "--headings":
            headings_override = args[i + 1]; i += 2; continue
        if docx_path is None:
            docx_path = a
        i += 1

    if not docx_path:
        print("ERROR: no input DOCX given.", file=sys.stderr)
        return 2
    if not os.path.exists(docx_path):
        print(f"ERROR: File not found: {docx_path}", file=sys.stderr)
        return 2

    cfg = load_config(config_path)

    total_pages, results = check_pages(docx_path, cfg, headings_override)

    found = [r for r in results if r["page"] is not None]
    missing = [r for r in results if r["page"] is None]
    # A heading that was never FOUND cannot be assumed recto: the standalone
    # exit code fails on misses too (verify_build's re-read already did).
    all_recto = bool(found) and all(r["recto"] for r in found) and not missing

    print(json.dumps({
        "docx": os.path.abspath(docx_path),
        "total_pages": total_pages,
        "unit_noun": (cfg.get("voice") or {}).get("unit_noun", "chapter"),
        "results": results,
        "not_found": len(missing),
        "all_recto": all_recto,
    }))

    return 0 if all_recto else 1


if __name__ == "__main__":
    sys.exit(main())
