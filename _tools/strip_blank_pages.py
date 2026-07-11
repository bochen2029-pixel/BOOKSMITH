"""
strip_blank_pages.py — Digital-edition blank-verso + header-ghost stripper.

BOOKSMITH toolchain component. Removes the print-only blank versos (introduced
by per-chapter SectionType.ODD_PAGE recto starts) and the header-only "ghost"
pages so the digital PDF reads continuously instead of showing broken
pagination.

CONTRACT (KIT_ARCHITECTURE (c) strip_blank_pages.py / LESSONS_LEDGER §8.1):
  - PyMuPDF (fitz) for detection + a byte-clean rebuild.
  - Keep cover pages 1-2 UNCONDITIONALLY (they are image-only by design and
    carry no extractable text — a naive text check would delete the covers).
  - Drop any body page whose page.get_text().strip() is empty, OR whose
    non-whitespace character count is < 30 (a header-only ghost: e.g. a running
    head "THENIGHTWASYOUNG" + a folio, which compacts to ~18 chars).

PORTED FROM:
  - C:\\BOOK\\build_digital_atd.py           (identify_blank_pages: get_text().strip()==0)
  - C:\\BOOK3\\_tools\\_titanic_source\\strip_blank_pages.py     (MIN_TEXT_CHARS keep-covers)
  - C:\\BOOK3\\_tools\\_titanic_source\\strip_blank_pages_v2.py  (MIN_NON_WS_CHARS header-ghost)
  - C:\\Claude-Titanic\\FIXIT\\strip_blank_pages.py             (fitz byte-clean rebuild + UTF-8 stdout)

The two BOOK3 heuristics are merged: an empty page OR a <30 non-whitespace-char
page is stripped. Detection uses fitz.get_text() throughout (the architecture
names get_text as the detector), and the surviving pages are rebuilt in place so
fonts, images, bookmarks, and annotations are preserved.

Usage:
  python strip_blank_pages.py <in.pdf> <out.pdf> [--min-chars 30] [--keep-covers 2]

Prints a JSON manifest on stdout:
  {"in":..., "out":..., "pages_before":N, "pages_after":M,
   "removed":[{"page":k,"chars":c,"preview":"..."}], "kept_covers":2}
"""
import sys
import os
import re
import json

import fitz  # PyMuPDF

DEFAULT_MIN_NON_WS_CHARS = 30   # header-only ghost pages compact to ~18 chars
DEFAULT_KEEP_COVERS = 2         # pages 1-2 are the image-only front/back covers


def non_ws_count(text: str) -> int:
    """Count non-whitespace characters. A running head has spaced letters that
    look long but compact short, so we strip ALL whitespace before counting."""
    return len(re.sub(r"\s+", "", text or ""))


def strip_blank_pages(in_pdf: str, out_pdf: str,
                      min_chars: int = DEFAULT_MIN_NON_WS_CHARS,
                      keep_covers: int = DEFAULT_KEEP_COVERS):
    in_pdf = os.path.abspath(in_pdf)
    out_pdf = os.path.abspath(out_pdf)

    if not os.path.exists(in_pdf):
        raise FileNotFoundError(f"Input PDF not found: {in_pdf}")

    out_dir = os.path.dirname(out_pdf)
    if out_dir and not os.path.isdir(out_dir):
        os.makedirs(out_dir, exist_ok=True)

    doc = fitz.open(in_pdf)
    total_before = len(doc)

    remove_0idx = []
    removed_manifest = []
    for i in range(total_before):
        page_num = i + 1
        # Keep cover pages unconditionally (image-only, no extractable text).
        if page_num <= keep_covers:
            continue
        text = doc[i].get_text() or ""
        compact = non_ws_count(text)
        if compact < min_chars:
            preview = text.strip().replace("\n", " ")[:80]
            remove_0idx.append(i)
            removed_manifest.append({"page": page_num, "chars": compact, "preview": preview})

    # Delete descending so earlier indices stay valid. Use delete_page()
    # (singular) — its single-int signature is stable across PyMuPDF versions,
    # whereas delete_pages(i) rejects a bare int on newer builds (it expects a
    # range/iterable).
    for i in sorted(remove_0idx, reverse=True):
        doc.delete_page(i)

    # garbage=4 + clean reclaims orphaned objects; deflate re-compresses streams.
    doc.save(out_pdf, deflate=True, garbage=4, clean=True)
    total_after = len(doc)
    doc.close()

    return {
        "in": in_pdf,
        "out": out_pdf,
        "pages_before": total_before,
        "pages_after": total_after,
        "removed": removed_manifest,
        "kept_covers": keep_covers,
    }


def main() -> int:
    # UTF-8 stdout so ✦ / em-dashes in page-text previews don't crash on Windows.
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

    args = sys.argv[1:]
    if len(args) < 2:
        print("Usage: python strip_blank_pages.py <in.pdf> <out.pdf> "
              "[--min-chars 30] [--keep-covers 2]", file=sys.stderr)
        return 2

    in_pdf = args[0]
    out_pdf = args[1]
    min_chars = DEFAULT_MIN_NON_WS_CHARS
    keep_covers = DEFAULT_KEEP_COVERS
    i = 2
    while i < len(args):
        if args[i] == "--min-chars":
            min_chars = int(args[i + 1]); i += 2; continue
        if args[i] == "--keep-covers":
            keep_covers = int(args[i + 1]); i += 2; continue
        i += 1

    result = strip_blank_pages(in_pdf, out_pdf, min_chars, keep_covers)
    print(json.dumps(result))
    return 0


if __name__ == "__main__":
    sys.exit(main())
