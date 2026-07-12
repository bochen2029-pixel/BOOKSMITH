"""
build_digital_pdf.py — Digital / reader PDF assembler.

BOOKSMITH toolchain component. Assembles the email/Drive reader PDF:
  page 1  front cover (exact 6x9-pt MediaBox)
  page 2  back cover  (cropped from the print wrap's bleed back to 6x9 trim)
  pages 3+  the print interior with every print-only blank verso + header-ghost
            page stripped, so it reads continuously.

CONTRACT (KIT_ARCHITECTURE (c) build_digital_pdf.py):
  - Word-COM interior PDF (reuse docx_to_pdf.py) + crop covers
    (BLEED_PX = int(0.80*DPI) = 240 for Mixam-sourced back art) ->
    cover pages as an EXACT 432x648-pt MediaBox via fitz.new_page ->
    pypdf concat -> book_workspace/<slug>/outputs/digital/<slug>_DIGITAL.pdf.

PORTED FROM:
  - C:\\BOOK\\build_digital_atd.py                     (blank-strip + fitz cover pages + interior copy)
  - C:\\Inside_The_Region\\build_digital_with_covers.py (scale-to-fit letterbox cover render)

Cover-source resolution (first existing wins), all under the workspace outputs/:
  FRONT: kindle/<slug>_KINDLE_cover.jpg | kindle/<slug>_KINDLE_COVER.jpg |
         kindle/<slug>_cover.jpg
  BACK : cropped-from-wrap kdp_paperback/<slug>_cover_wrap.jpg |
         kdp_paperback/cover_wrap.jpg   (crop bleed->trim)
         else a standalone kdp_paperback/<slug>_back.jpg (used as-is)
  INTERIOR DOCX: kdp_paperback/<slug>_KDP_PAPERBACK.docx (rendered to PDF if the
         PDF is absent), else the pre-rendered kdp_paperback/*.pdf.

Front art is placed scale-to-fit (letterboxed in the cover color) so edge
content is never cropped; the exact 6x9 MediaBox is written via fitz, never PIL
(PIL truncates the MediaBox to a floor(px/DPI) inch value and KDP-style
4-decimal validators reject it — LESSONS_LEDGER §5.6).

Usage:
  python build_digital_pdf.py --config book_config.json [--kit-env kit_env.json]
                              [--workspace <dir>]

Prints a JSON summary on stdout.
"""
import sys
import os
import io
import json
import tempfile

import fitz  # PyMuPDF
from PIL import Image
# pypdf is the maintained successor to the EOL PyPDF2 (drop-in PdfReader/PdfWriter
# API). Prefer it; fall back to PyPDF2 on machines that only have the old package.
try:
    from pypdf import PdfReader, PdfWriter
except ImportError:  # pragma: no cover - legacy fallback
    from PyPDF2 import PdfReader, PdfWriter

# Local sibling tools.
_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
if _THIS_DIR not in sys.path:
    sys.path.insert(0, _THIS_DIR)
import strip_blank_pages as _strip            # noqa: E402
# docx_to_pdf (Word COM, Windows-only) is imported lazily inside
# ensure_interior_pdf() so this module loads on any platform whenever a
# pre-rendered interior PDF already exists.

DPI = 300
TRIM_W_IN = 6.00
TRIM_H_IN = 9.00
PAGE_W_PTS = TRIM_W_IN * 72   # 432
PAGE_H_PTS = TRIM_H_IN * 72   # 648


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def hex_to_rgb(h: str):
    h = (h or "").lstrip("#")
    if len(h) != 6:
        return (13, 27, 42)  # navy fallback
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def first_existing(*paths):
    for p in paths:
        if p and os.path.exists(p):
            return p
    return None


def resolve_workspace(cfg, workspace_arg):
    """The digital PDF lands under book_workspace/<slug>/outputs/. The workspace
    root is either passed explicitly or derived relative to the kit root."""
    slug = cfg["slug"]
    if workspace_arg:
        return os.path.abspath(workspace_arg)
    # Kit layout: <kit>/_tools/build_digital_pdf.py -> <kit>/book_workspace/<slug>
    kit_root = os.path.dirname(_THIS_DIR)
    return os.path.join(kit_root, "book_workspace", slug)


def bleed_px_for_back(cfg) -> int:
    """The back cover is cropped from the print wrap. resolve_covers() only ever
    sources the KDP paperback wrap ('{slug}_cover_wrap.jpg' / 'cover_wrap.jpg' /
    '{slug}_KDP_PAPERBACK_wrap.jpg') — all 0.125" KDP bleed. The Mixam wrap
    ('cover_wrap_mixam.jpg', 0.80" bleed) is NEVER in that list, so cropping with
    the Mixam bleed shears 0.675" off every edge. Read the KDP paperback bleed."""
    spine = cfg.get("spine") or {}
    kdp_bleed = spine.get("kdp_bleed_in", 0.125)
    return int(round(kdp_bleed * DPI))


def crop_back_trim_from_wrap(wrap_path: str, cfg) -> Image.Image:
    """Crop the back-cover trim (6x9, no bleed) out of a print wrap laid out as
    [back bleed | back trim | spine | front trim | front bleed]."""
    wrap = Image.open(wrap_path).convert("RGB")
    bleed_px = bleed_px_for_back(cfg)
    back_trim_right = bleed_px + int(round(TRIM_W_IN * DPI))
    back_trim_bottom = wrap.height - bleed_px
    cropped = wrap.crop((bleed_px, bleed_px, back_trim_right, back_trim_bottom))
    exp_w = int(round(TRIM_W_IN * DPI))
    exp_h = int(round(TRIM_H_IN * DPI))
    assert abs(cropped.size[0] - exp_w) <= 2 and abs(cropped.size[1] - exp_h) <= 2, (
        f"back-cover crop {cropped.size} != expected ({exp_w},{exp_h}); "
        f"wrong bleed for source {wrap_path}")
    return cropped


def render_cover_jpeg(img: Image.Image, cover_rgb, dpi: int = DPI) -> bytes:
    """Scale-to-fit the source image into an exact 6x9 @ dpi canvas, letterboxed
    in the cover color. Never crops edge content (a title baked at the top or a
    timestamp at an edge survives). Returns JPEG bytes."""
    page_w_px = int(round(TRIM_W_IN * dpi))
    page_h_px = int(round(TRIM_H_IN * dpi))
    src = img.convert("RGB")
    sw, sh = src.size
    scale = min(page_w_px / sw, page_h_px / sh)
    nw, nh = max(1, int(sw * scale)), max(1, int(sh * scale))
    scaled = src.resize((nw, nh), Image.LANCZOS)
    canvas = Image.new("RGB", (page_w_px, page_h_px), cover_rgb)
    canvas.paste(scaled, ((page_w_px - nw) // 2, (page_h_px - nh) // 2))
    buf = io.BytesIO()
    canvas.save(buf, format="JPEG", quality=92, optimize=True, dpi=(dpi, dpi))
    return buf.getvalue()


def build_cover_pages_pdf(front_jpeg: bytes, back_jpeg: bytes, out_path: str):
    """Two-page PDF, each page an EXACT 432x648-pt MediaBox (via fitz, not PIL)."""
    doc = fitz.open()
    p_front = doc.new_page(width=PAGE_W_PTS, height=PAGE_H_PTS)
    p_front.insert_image(p_front.rect, stream=front_jpeg)
    p_back = doc.new_page(width=PAGE_W_PTS, height=PAGE_H_PTS)
    p_back.insert_image(p_back.rect, stream=back_jpeg)
    doc.save(out_path, deflate=True, garbage=4, clean=True)
    doc.close()


def ensure_interior_pdf(cfg, ws: str) -> str:
    """Return a path to the print interior PDF, rendering it from the paperback
    DOCX via Word COM if only the DOCX exists."""
    slug = cfg["slug"]
    pb_dir = os.path.join(ws, "outputs", "kdp_paperback")

    existing_pdf = first_existing(
        os.path.join(pb_dir, f"{slug}_KDP_PAPERBACK.pdf"),
        os.path.join(pb_dir, f"{slug}_KDP.pdf"),
        os.path.join(pb_dir, f"{slug}.pdf"),
    )
    if existing_pdf:
        return existing_pdf

    docx = first_existing(
        os.path.join(pb_dir, f"{slug}_KDP_PAPERBACK.docx"),
        os.path.join(pb_dir, f"{slug}_KDP.docx"),
        os.path.join(pb_dir, f"{slug}.docx"),
    )
    if not docx:
        raise FileNotFoundError(
            f"No interior PDF or DOCX found in {pb_dir}. Produce the "
            f"kdp_paperback format first.")

    out_pdf = os.path.join(pb_dir, f"{slug}_KDP_PAPERBACK.pdf")
    import docx_to_pdf as _docx_to_pdf  # lazy: Word COM (or Tier-2 LibreOffice), Windows-first
    pages, words, renderer = _docx_to_pdf.docx_to_pdf(docx, out_pdf)
    print(f"  Rendered interior via {renderer}: {pages} pages, {words} words",
          file=sys.stderr)
    return out_pdf


def resolve_covers(cfg, ws: str):
    """Return (front_source_image, back_source_image) as PIL Images."""
    slug = cfg["slug"]
    kindle_dir = os.path.join(ws, "outputs", "kindle")
    pb_dir = os.path.join(ws, "outputs", "kdp_paperback")
    palette = ((cfg.get("cover") or {}).get("palette")) or {}
    cover_rgb = hex_to_rgb(palette.get("navy") or palette.get("umber") or "0D1B2A")

    front_path = first_existing(
        os.path.join(kindle_dir, f"{slug}_KINDLE_cover.jpg"),
        os.path.join(kindle_dir, f"{slug}_KINDLE_COVER.jpg"),
        os.path.join(kindle_dir, f"{slug}_kindle_cover.jpg"),
        os.path.join(kindle_dir, f"{slug}_cover.jpg"),
        os.path.join(kindle_dir, f"{slug}_KINDLE_cover.png"),
    )
    if not front_path:
        raise FileNotFoundError(
            f"No Kindle/front cover image found under {kindle_dir}. Produce the "
            f"kindle cover first.")
    front_img = Image.open(front_path).convert("RGB")

    # Back cover: prefer cropping the paperback wrap; else a standalone back art.
    wrap_path = first_existing(
        os.path.join(pb_dir, f"{slug}_cover_wrap.jpg"),
        os.path.join(pb_dir, "cover_wrap.jpg"),
        os.path.join(pb_dir, f"{slug}_KDP_PAPERBACK_wrap.jpg"),
    )
    if wrap_path:
        back_img = crop_back_trim_from_wrap(wrap_path, cfg)
        back_src = wrap_path
    else:
        back_standalone = first_existing(
            os.path.join(pb_dir, f"{slug}_back.jpg"),
            os.path.join(pb_dir, "back_cover.jpg"),
        )
        if not back_standalone:
            # Fall back to reusing the front as the back rather than failing —
            # a reader PDF still opens; note it in the summary.
            back_img = front_img
            back_src = front_path + " (reused as back)"
        else:
            back_img = Image.open(back_standalone).convert("RGB")
            back_src = back_standalone

    return front_img, back_img, cover_rgb, front_path, back_src


def build(config_path, workspace_arg):
    cfg = load_json(config_path)
    slug = cfg["slug"]
    ws = resolve_workspace(cfg, workspace_arg)

    out_dir = os.path.join(ws, "outputs", "digital")
    os.makedirs(out_dir, exist_ok=True)
    out_pdf = os.path.join(out_dir, f"{slug}_DIGITAL.pdf")

    # 1. Interior PDF (render from DOCX via Word COM if needed).
    interior_pdf = ensure_interior_pdf(cfg, ws)

    # 2. Strip print-only blanks + header ghosts into a temp PDF.
    #    keep_covers=1 (NOT the default 2, NOT 0): the strip runs on the
    #    cover-LESS interior (covers are prepended below), so page 1 is the real
    #    half-title (e.g. 'THE TEST VOYAGE' = 13 chars, below min_chars=30);
    #    keep_covers=1 protects it unconditionally while still stripping page 2,
    #    the true blank verso. keep_covers=2 would preserve that blank verso.
    fd, stripped_pdf = tempfile.mkstemp(suffix="_stripped.pdf", dir=out_dir)
    os.close(fd)
    strip_result = _strip.strip_blank_pages(interior_pdf, stripped_pdf, keep_covers=1)

    # 3. Build the two exact-MediaBox cover pages.
    front_img, back_img, cover_rgb, front_src, back_src = resolve_covers(cfg, ws)
    front_jpeg = render_cover_jpeg(front_img, cover_rgb)
    back_jpeg = render_cover_jpeg(back_img, cover_rgb)
    fd, cover_pdf = tempfile.mkstemp(suffix="_covers.pdf", dir=out_dir)
    os.close(fd)
    build_cover_pages_pdf(front_jpeg, back_jpeg, cover_pdf)

    # 4. Concatenate covers + stripped interior via pypdf (per the contract).
    writer = PdfWriter()
    cover_reader = PdfReader(cover_pdf)
    for page in cover_reader.pages:
        writer.add_page(page)
    interior_reader = PdfReader(stripped_pdf)
    for page in interior_reader.pages:
        writer.add_page(page)
    with open(out_pdf, "wb") as f:
        writer.write(f)

    # 5. Cleanup temps.
    for tmp in (stripped_pdf, cover_pdf):
        try:
            os.remove(tmp)
        except OSError:
            pass

    total_pages = len(PdfReader(out_pdf).pages)
    size = os.path.getsize(out_pdf)

    summary = {
        "out": out_pdf,
        "total_pages": total_pages,
        "interior_source": interior_pdf,
        "interior_pages_before_strip": strip_result["pages_before"],
        "interior_pages_after_strip": strip_result["pages_after"],
        "blanks_stripped": len(strip_result["removed"]),
        "front_cover_source": front_src,
        "back_cover_source": back_src,
        "size_bytes": size,
        "size_mb": round(size / 1024 / 1024, 2),
    }
    print(json.dumps(summary))
    return summary


def main() -> int:
    args = sys.argv[1:]
    config_path = None
    workspace_arg = None
    i = 0
    while i < len(args):
        a = args[i]
        if a == "--config":
            config_path = args[i + 1]; i += 2; continue
        if a == "--kit-env":
            # Accepted for interface symmetry; digital build needs no kit_env paths.
            i += 2; continue
        if a == "--workspace":
            workspace_arg = args[i + 1]; i += 2; continue
        i += 1

    if not config_path:
        print("Usage: python build_digital_pdf.py --config book_config.json "
              "[--workspace <dir>]", file=sys.stderr)
        return 2

    build(config_path, workspace_arg)
    return 0


if __name__ == "__main__":
    sys.exit(main())
