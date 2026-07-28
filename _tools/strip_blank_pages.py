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
  - Keep ANY page carrying an embedded image (2026-07-27, the figure-program
    fix): a mid-flow figure page extracts little or no text, but it is content,
    not a blank — the text heuristics below never run on an image-bearing page.
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


FOLIO_BAND_IN = 1.2   # running heads + folios live within this much of the page edge


def is_header_ghost(page, text: str) -> bool:
    """True when a below-min-chars page is a print-only header/folio 'ghost'.

    POSITIONAL test first: a ghost's text lives ENTIRELY in the top/bottom folio
    bands (a running head at the top, a page number at an edge). Real short
    content sits mid-page — a chapter-number display page ('13', 'IX'), a
    single-word page ('FINIS'), an epigraph, a part-title — and is preserved no
    matter how short, which a character-class heuristic cannot guarantee.

    Falls back to the old text heuristic only when block geometry is
    unavailable: folio digit present, or a single unspaced all-caps run."""
    norm = re.sub(r"\s+", " ", text or "").strip()
    if not norm:
        return True
    try:
        blocks = [b for b in page.get_text("blocks") if (b[4] or "").strip()]
    except Exception:
        blocks = []
    if blocks:
        h = page.rect.height
        band = FOLIO_BAND_IN * 72.0
        # b = (x0, y0, x1, y1, text, ...): every block fully inside a folio band?
        return all((b[3] <= band) or (b[1] >= h - band) for b in blocks)
    upperish = re.fullmatch(r"[A-Z0-9 .·—–\-]+", norm) is not None
    if not upperish:
        return False  # contains lowercase / real words -> content, keep it
    has_folio = re.search(r"\d", norm) is not None
    single_unspaced_run = " " not in norm and norm.isalpha()
    return has_folio or single_unspaced_run


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
        # Keep any image-bearing page unconditionally (2026-07-27): a mid-flow
        # figure page is content whatever its extractable-text count says.
        try:
            if doc[i].get_images(full=True):
                continue
        except Exception:
            pass
        text = doc[i].get_text() or ""
        compact = non_ws_count(text)
        # Truly-empty pages always go. Below-min-chars pages go ONLY if they are
        # header-only ghosts (all text in the top/bottom folio bands) — a short
        # recto part-title, a chapter-number page, or other minimalist front
        # matter sits mid-page and is preserved.
        if compact == 0 or (compact < min_chars and is_header_ghost(doc[i], text)):
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


def _selftest() -> int:
    """Synthesize a 6-page PDF and assert the strip decisions:
    p1/p2 text covers (kept by keep_covers), p3 long body text (kept),
    p4 image-only figure page (kept by the image rule), p5 short mid-page
    text (kept: not a ghost), p6 empty (stripped)."""
    import struct
    import tempfile
    import zlib

    def tiny_png_bytes(w=8, h=6, rgb=(40, 40, 160)):
        def chunk(tag, data):
            return (struct.pack(">I", len(data)) + tag + data
                    + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF))
        raw = b"".join(b"\x00" + bytes(rgb) * w for _ in range(h))
        return (b"\x89PNG\r\n\x1a\n"
                + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0))
                + chunk(b"IDAT", zlib.compress(raw))
                + chunk(b"IEND", b""))

    tmp = tempfile.mkdtemp(prefix="bs_stripself_")
    src = os.path.join(tmp, "src.pdf")
    out = os.path.join(tmp, "out.pdf")
    doc = fitz.open()
    for text in ("FRONT COVER", "BACK COVER",
                 "Body text long enough to clear the thirty character floor easily."):
        p = doc.new_page(width=432, height=648)
        p.insert_text((72, 300), text, fontsize=12)
    p_img = doc.new_page(width=432, height=648)
    p_img.insert_image(fitz.Rect(72, 200, 360, 420), stream=tiny_png_bytes())
    p_short = doc.new_page(width=432, height=648)
    p_short.insert_text((200, 320), "FINIS", fontsize=12)
    doc.new_page(width=432, height=648)          # p6: truly empty -> stripped
    doc.save(src)
    doc.close()

    result = strip_blank_pages(src, out, keep_covers=2)
    ok = (result["pages_before"] == 6 and result["pages_after"] == 5
          and len(result["removed"]) == 1 and result["removed"][0]["page"] == 6)
    check = fitz.open(out)
    ok = ok and any(check[i].get_images(full=True) for i in range(len(check)))
    check.close()
    print(json.dumps({"selftest": "pass" if ok else "FAIL", **result}))
    return 0 if ok else 1


def main() -> int:
    # UTF-8 stdout so ✦ / em-dashes in page-text previews don't crash on Windows.
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

    args = sys.argv[1:]
    if args and args[0] == "--selftest":
        return _selftest()
    if len(args) < 2:
        print("Usage: python strip_blank_pages.py <in.pdf> <out.pdf> "
              "[--min-chars 30] [--keep-covers 2]  |  --selftest", file=sys.stderr)
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
