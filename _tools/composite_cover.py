#!/usr/bin/env python3
r"""
composite_cover.py — Parameterized cover compositor for BOOKSMITH (all print formats).

ONE script, SIX print profiles (+ kindle) selected by --profile:

  --profile kdp-wrap        single wrap image [back|spine|front] with 0.125" bleed
                            -> outputs/kdp_paperback/cover_wrap.pdf + .jpg

  --profile kdp-hardcover   single wrap image [back|spine|front] with 0.708" case-board
                            turn-in (NOT bleed). ALWAYS uses white-paper spine math +
                            10.417" hardcoded height REGARDLESS of book paper — KDP HC
                            is white-only.
                            -> outputs/kdp_hardcover/cover_wrap_hardcover.pdf + .jpg

  --profile mixam-3panel    THREE independent PDFs (front_cover.pdf / back_cover.pdf /
                            spine.pdf) each at 0.80" bleed on all four sides.
                            -> outputs/mixam_hardcover/{front_cover,back_cover,spine}.pdf + .jpg

  --profile mixam-paperback-wrap
                            single wrap [back|spine|front], EXACTLY the kdp-wrap
                            geometry (W = 2*trim_w + spine + 2*0.125, H = trim_h +
                            2*0.125, bleed 0.125). Spine via preset_lookup:
                            spine_override_in wins; else cream pages*0.0023+0.04,
                            else white/uncoated pages*0.00215+0.01 (INFERRED — the
                            Mixam CART value is canonical). Quiet 0.25 all +
                            0.50 spine-side; spine text blanked below 0.25" width
                            (print_presets mixam_paperback.spine_text_rule).
                            -> outputs/mixam_paperback/cover_wrap_mixam.pdf + .jpg

  --profile blurb-wrap      Blurb Trade SOFTCOVER single wrap at preset_lookup
                            .softcover_dims() (spine interpolated from the probed
                            Blurb tables; W = 2*trim_w + spine + 0.25, H = trim_h
                            + 0.25, bleed 0.125). Same visible-face model as
                            kdp-wrap (faces = trim inset by bleed).
                            -> outputs/blurb_paperback/cover_wrap_blurb.pdf + .jpg

  --profile blurb-imagewrap Blurb Hardcover IMAGEWRAP single wrap at preset_lookup
                            .imagewrap_dims() (probed cover-PDF rows; width slides
                            1:1 with spine). Panel math: panel_total = (cover_w -
                            spine)/2; the fold at the spine edge is EXACT and the
                            OUTER edge loses m = panel_total - trim_w to the wrap.
                            Visible front face x-span = [cover_w - panel_total,
                            cover_w - m]; visible back = [m, panel_total]; spine
                            centered. Title/author centered on the VISIBLE front
                            face, not the panel. Vertical text inset >=
                            (cover_h - trim_h)/2 + 0.25 from top/bottom.
                            -> outputs/blurb_hardcover/cover_wrap_imagewrap.pdf + .jpg

EVERY profile (kindle included) writes a cover_meta.json sidecar into its output
dir — {profile, pages, spine_in, target_wrap_in:[w,h], files:[...]} — which
verify_build.py reads and cross-checks against its own preset_lookup recompute.

PAGES is a SINGLE injected value (--pages N), never hard-coded. The generated-PDF page
count is fed here by the caller; spine width is re-derived from it in exactly one place
per profile. KDP/Mixam-hardcover profiles:

    spine_in = pages * per_page_paper + board_add

  per_page_paper:  0.0025 (cream) / 0.002252 (white)   [book_config.spine]
  board_add:       0                         (KDP paperback — no boards)
                   kdp_hardcover_board_add   (KDP hardcover, default 0.348, CALIBRATE)
                   mixam_board_add           (Mixam, NON-constant — trust Mixam calc)

  mixam-paperback-wrap + blurb profiles derive spine/wrap via preset_lookup.py
  (the SAME code path verify_build.py recomputes with — no drift possible).

Design invariants baked in from the LESSONS_LEDGER (§5, §6, §7.4, §11.3):
  - Exact-inch MediaBox via PyMuPDF (PIL truncates floor(px/DPI) -> KDP 4-decimal reject).
  - scale_to_cover for full-bleed FRONT art; scale_to_fit (letterbox) for BACK art that
    has content at the edges (a barcode/timestamp would otherwise be cropped).
  - Cormorant Garamond loaded from the VENDORED repo-relative fonts/ dir, weight axis via
    set_variation_by_axes (never C:\Claude-Titanic\fonts).
  - Typography kept >= bleed + 0.25" from every edge.
  - Spine text double-drawn (+1px) for weight, composed HORIZONTAL then .rotate(-90).
  - ISBN keep-out (2.25"x1.5" bottom-right) left CLEAR — no baked box (KDP auto-overlays).
  - Mixam names carry the routing keywords (front_cover / back_cover / spine); an inner_
    reminder is printed so the body is uploaded as inner_<slug>.pdf.
  - Computed target-vs-actual wrap dimensions printed for self-verification.

I/O contract:
  python composite_cover.py --config book_config.json --profile <p> --pages <N>
       [--workspace <book_workspace/<slug>>]   (where outputs/<format>/ lives)
       [--art <path>]   (override the source art; default cover_art/<slug>_src.png)
       [--kit-env <kit_env.json>]

Ported from:
  C:\BOOK\composite_cover_atd_kdp.py / _kdp_hardcover.py / _mixam.py
  C:\Inside_The_Region\composite_cover_kdp_paperback.py / _kdp_hardcover.py / _mixam.py / _kindle.py
  C:\BOOK3\_tools\_titanic_source\composite_cover_titanic.py
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

try:
    import fitz  # PyMuPDF
except ImportError:  # pragma: no cover - fitz is a declared dependency
    fitz = None

# ============================================================
# CONSTANTS
# ============================================================
DPI = 300
PT_PER_IN = 72.0

# KDP permits spine TEXT only at >= 0.0625" spine width (KDP's documented
# spine-text minimum is ~79-80 pages; 0.0625" is the width form the code gates
# on). Below that the spine is too thin to carry a legible title (and
# KDP forbids spine text there), so render_spine leaves it BLANK — a clean dark
# face, not an illegible sliver. Platform rule, not a per-book knob (§16.1). The
# 75-page floor (§16.5, verify_build) keeps real books well above this at
# >= 0.1875" spine; this constant is the universal safety that also guards the
# KDP wrap / hardcover / Mixam-3-panel paths, which — unlike build_flat_wrap's
# stricter 0.25" spine_blank_below_in — carry no per-profile blank rule.
SPINE_TEXT_MIN_IN = 0.0625

# Repo-relative font dir, computed from THIS script's location — never a
# cross-repo fonts path (that dependency shipped empty font folders in prior
# kits). Kit taxonomy: _tools/ and fonts/ are siblings under the repo root.
SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
FONTS_DIR = REPO_ROOT / "fonts"
FONT_LIGHT = FONTS_DIR / "CormorantGaramond-Light.ttf"   # variable, weight axis 300-700
FONT_BOLD = FONTS_DIR / "CormorantGaramond-Bold.ttf"     # dedicated Bold TTF

# Shared preset geometry (Mixam paperback + Blurb) — the SAME module
# verify_build.py recomputes with, so compositor and verifier cannot drift.
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))
import preset_lookup  # noqa: E402  (sibling module, path pinned above)

TRIM_W_IN = 6.00
TRIM_H_IN = 9.00

# Profile -> (output subdir, format label for config lookups)
PROFILE_OUTDIR = {
    "kdp-wrap": "kdp_paperback",
    "kdp-hardcover": "kdp_hardcover",
    "kindle": "kindle",
    "mixam-3panel": "mixam_hardcover",
    "mixam-paperback-wrap": "mixam_paperback",
    "blurb-wrap": "blurb_paperback",
    "blurb-imagewrap": "blurb_hardcover",
}


# ============================================================
# CONFIG LOADING
# ============================================================
def load_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def _hex_to_rgb(h: str) -> tuple[int, int, int]:
    """Accept 'RRGGBB' or '#RRGGBB'. Returns an (r,g,b) tuple."""
    h = h.strip().lstrip("#")
    if len(h) != 6:
        raise ValueError(f"palette color must be 6 hex digits, got {h!r}")
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))


class CoverConfig:
    """Flattened, defaulted view of the per-book config for cover composition.

    Every per-book value comes from book_config.json; nothing book-specific is
    hard-coded. Where the schema declares a default, we apply the same default
    here so a minimal config still composites.
    """

    def __init__(self, cfg: dict):
        self.raw = cfg
        self.title = cfg["title"]
        self.subtitle = cfg.get("subtitle", "")
        self.author = cfg["author"]
        self.slug = cfg["slug"]

        trim = cfg.get("trim") or {}
        self.trim_w = float(trim.get("w", TRIM_W_IN))
        self.trim_h = float(trim.get("h", TRIM_H_IN))

        self.paper = cfg.get("paper", "cream")
        # Blurb trade paper (drives the blurb spine/cover lookup tables).
        self.blurb_paper = cfg.get("blurb_paper") or preset_lookup.DEFAULT_BLURB_PAPER

        # ---- spine math constants ----
        spine = cfg.get("spine") or {}
        self.per_page_cream = float(spine.get("per_page_cream", 0.0025))
        self.per_page_white = float(spine.get("per_page_white", 0.002252))
        self.kdp_hc_board_add = float(spine.get("kdp_hardcover_board_add", 0.348))
        self.mixam_board_add = float(spine.get("mixam_board_add", 0.110))
        self.kdp_hc_turn_in = float(spine.get("kdp_hardcover_turn_in_in", 0.708))
        self.kdp_hc_height = float(spine.get("kdp_hardcover_height_in", 10.417))
        self.kdp_bleed = float(spine.get("kdp_bleed_in", 0.125))
        self.mixam_bleed = float(spine.get("mixam_bleed_in", 0.80))
        # Optional hard override — once KDP/Mixam states an exact spine, set this
        # in config.spine.spine_override_in and it wins over the formula.
        self.spine_override = spine.get("spine_override_in", None)

        # ---- cover typography / palette ----
        cover = cfg.get("cover") or {}
        pal = cover.get("palette") or {
            "navy": "0D1B2A", "cream": "F4EFE0", "gold": "C9A760", "umber": "1E160F",
        }
        # Named colors with resilient fallbacks so any palette shape works.
        self.col_navy = _hex_to_rgb(pal.get("navy", "0D1B2A"))
        self.col_cream = _hex_to_rgb(pal.get("cream", "F4EFE0"))
        self.col_gold = _hex_to_rgb(pal.get("gold", "C9A760"))
        self.col_umber = _hex_to_rgb(pal.get("umber", pal.get("navy", "1E160F")))
        # The dark background used behind spine + as letterbox fill: prefer umber
        # (literary dark) but fall back to navy for tech-register palettes.
        self.col_dark = self.col_umber
        self.col_shadow = (0, 0, 0)

        self.title_tracking = float(cover.get("title_tracking_em", 0.05))
        self.author_tracking = float(cover.get("author_tracking_em", 0.18))
        # Optional title vertical placement (fraction of panel height below the trim top).
        # None = the house default (0.030). Set via the --title-y-frac CLI flag, e.g. from
        # cover_layout.py's chosen band. Leaves default renders byte-identical.
        self.title_y_frac = None

        # ISBN keep-out (bottom-right by default) — we draw NOTHING here.
        keep = cover.get("isbn_keepout") or {}
        self.isbn_w_in = float(keep.get("w_in", 2.25))
        self.isbn_h_in = float(keep.get("h_in", 1.5))
        self.isbn_corner = keep.get("corner", "bottom_right")

        # ---- marketing copy for the back panel ----
        meta = cfg.get("kdp_metadata") or {}
        self.description_html = meta.get("description", "")

        # Sacred closing refrain / tagline pull-quote, if the voice config names one.
        voice = cfg.get("voice") or {}
        self.greenlist = voice.get("greenlist", []) or []

    # ---- derived spine math (the single source of truth) ----
    def per_page(self, force_white: bool) -> float:
        if force_white:
            return self.per_page_white
        return self.per_page_cream if self.paper == "cream" else self.per_page_white

    def spine_in(self, pages: int, profile: str) -> float:
        """spine = pages * per_page + board_add — mixam-3panel ONLY. Every other
        profile sources its spine exclusively from preset_lookup (the module
        verify_build recomputes with); a second copy of that math here is a
        drift surface, so requesting it is an error rather than a silent
        divergent answer."""
        if self.spine_override is not None:
            return round(float(self.spine_override), 4)
        if profile == "mixam-3panel":
            return round(pages * self.per_page(False) + self.mixam_board_add, 4)
        raise ValueError(f"spine_in: unsupported profile {profile!r} — use preset_lookup")


# ============================================================
# FONT + TEXT HELPERS
# ============================================================
def load_font(size: int, weight: int = 300, use_bold_ttf: bool = False) -> ImageFont.FreeTypeFont:
    """Load Cormorant Garamond from the vendored repo-relative fonts/ dir.

    use_bold_ttf=True loads the dedicated Bold TTF; otherwise the Light variable
    font is loaded and its weight axis set via set_variation_by_axes.

    NOTE: the compositor ALWAYS renders Cormorant Garamond. The
    `cover.title_face` config knob is currently informational only — it is not
    read here, so a family override has no effect on the composited typography.
    (See the schema description for cover.title_face.)
    """
    path = FONT_BOLD if use_bold_ttf else FONT_LIGHT
    f = ImageFont.truetype(str(path), size=size)
    if not use_bold_ttf:
        try:
            f.set_variation_by_axes([weight])
        except Exception:
            # Non-variable build or axis unsupported — degrade gracefully.
            pass
    return f


def measure_tracked(text: str, font: ImageFont.FreeTypeFont, tracking_em: float) -> tuple[int, int]:
    """Width (with per-glyph tracking) and height (ascent+descent) of a string."""
    em = font.size
    widths = []
    for ch in text:
        bbox = font.getbbox(ch)
        w = bbox[2] - bbox[0] if bbox[2] > bbox[0] else em * 0.3
        widths.append(w)
    total_w = sum(widths) + (len(text) - 1) * em * tracking_em
    ascent, descent = font.getmetrics()
    return int(total_w), int(ascent + descent)


def draw_tracked(draw, xy, text, font, tracking_em, color,
                 stroke_width=0, stroke_fill=None, shadow=None):
    """Draw text with per-glyph em-fraction tracking.

    Optional halo via stroke_width/stroke_fill (used against painterly gradients);
    optional drop shadow via shadow=(dx, dy, color) drawn first behind the glyphs.
    """
    x, y = xy
    em = font.size

    if shadow is not None:
        sx, sy, sc = shadow
        cx = x
        for ch in text:
            draw.text((cx + sx, y + sy), ch, font=font, fill=sc)
            bbox = font.getbbox(ch)
            w = bbox[2] - bbox[0] if bbox[2] > bbox[0] else em * 0.3
            cx += w + em * tracking_em

    cx = x
    for ch in text:
        if stroke_width > 0 and stroke_fill is not None:
            draw.text((cx, y), ch, font=font, fill=color,
                      stroke_width=stroke_width, stroke_fill=stroke_fill)
        else:
            draw.text((cx, y), ch, font=font, fill=color)
        bbox = font.getbbox(ch)
        w = bbox[2] - bbox[0] if bbox[2] > bbox[0] else em * 0.3
        cx += w + em * tracking_em


def scale_to_cover(src: Image.Image, canvas_w: int, canvas_h: int,
                   bg=(0, 0, 0)) -> Image.Image:
    """Scale to FILL the canvas (crop overflow symmetrically). Full-bleed FRONT art."""
    src_w, src_h = src.size
    scale = max(canvas_w / src_w, canvas_h / src_h)
    new_w = int(src_w * scale)
    new_h = int(src_h * scale)
    resized = src.resize((new_w, new_h), Image.LANCZOS)
    out = Image.new("RGB", (canvas_w, canvas_h), bg)
    out.paste(resized, (-(new_w - canvas_w) // 2, -(new_h - canvas_h) // 2))
    return out


def scale_to_fit(src: Image.Image, canvas_w: int, canvas_h: int,
                 bg=(0, 0, 0), scale_factor: float = 1.0,
                 x_shift: int = 0, y_shift: int = 0) -> Image.Image:
    """Scale to FIT entirely inside the canvas (letterbox). BACK art with edge content."""
    src_w, src_h = src.size
    scale = min(canvas_w / src_w, canvas_h / src_h) * scale_factor
    new_w = int(src_w * scale)
    new_h = int(src_h * scale)
    resized = src.resize((new_w, new_h), Image.LANCZOS)
    out = Image.new("RGB", (canvas_w, canvas_h), bg)
    out.paste(resized, ((canvas_w - new_w) // 2 + x_shift,
                        (canvas_h - new_h) // 2 + y_shift))
    return out


def _ornament_font(size: int) -> ImageFont.FreeTypeFont:
    """Load a symbol-capable face for the U+2726 four-pointed star ornament."""
    for name in ("seguisym.ttf", "arial.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except Exception:
            continue
    return ImageFont.load_default()


def save_pdf_exact(pil_img: Image.Image, out_pdf: Path,
                   target_w_in: float, target_h_in: float) -> tuple[float, float]:
    """Save a PIL image as a PDF whose MediaBox is EXACTLY target_w_in x target_h_in.

    PIL's Image.save(..., 'PDF') derives the MediaBox from floor(pixels/DPI),
    truncating fractional inches and failing KDP/Mixam's 4-decimal dimension
    check. PyMuPDF lets us set the MediaBox directly in points (inches * 72).
    Returns the (width_pts, height_pts) actually written for self-verification.
    """
    if fitz is None:
        raise RuntimeError(
            "PyMuPDF (fitz) is required for exact-MediaBox PDF output. "
            "pip install PyMuPDF"
        )
    tmp_jpg = out_pdf.with_suffix(".tmp.jpg")
    pil_img.save(tmp_jpg, "JPEG", quality=95, dpi=(DPI, DPI))
    try:
        target_w_pts = target_w_in * PT_PER_IN
        target_h_pts = target_h_in * PT_PER_IN
        pdf = fitz.open()
        page = pdf.new_page(width=target_w_pts, height=target_h_pts)
        page.insert_image(page.rect, filename=str(tmp_jpg))
        pdf.save(str(out_pdf), deflate=True, garbage=3)
        pdf.close()
    finally:
        try:
            tmp_jpg.unlink()
        except OSError:
            pass
    return target_w_pts, target_h_pts


# ============================================================
# BACK-PANEL COPY
# ============================================================
def _strip_html(html: str) -> list[str]:
    """Convert the KDP description HTML into plain paragraph strings.

    The description in book_config is <p>...</p> HTML with <b>/<i> inline tags.
    We keep paragraph breaks, drop all tags, and collapse whitespace so the
    greedy line-fitter can wrap the text to the panel width.
    """
    import re
    if not html:
        return []
    # Split on paragraph boundaries first.
    parts = re.split(r"</p>|<br\s*/?>", html, flags=re.IGNORECASE)
    paragraphs = []
    for part in parts:
        text = re.sub(r"<[^>]+>", "", part)          # drop remaining tags
        text = (text.replace("&amp;", "&")
                    .replace("&lt;", "<")
                    .replace("&gt;", ">")
                    .replace("&#39;", "'")
                    .replace("&quot;", '"'))
        text = " ".join(text.split())                # collapse whitespace
        if text:
            paragraphs.append(text)
    return paragraphs


def _refrain(cfg: CoverConfig) -> str:
    """Pick a short closing pull-quote from the greenlist (sacred refrain), if any."""
    for phrase in cfg.greenlist:
        p = phrase.strip()
        # Prefer a short, sentence-like refrain.
        if 0 < len(p) <= 40:
            # Title-case-ish: keep as authored; ensure trailing period.
            return p if p.endswith(".") else p + "."
    return ""


# ============================================================
# BACK PANEL RENDERER (shared across profiles)
# ============================================================
def render_back_text(canvas: Image.Image, cfg: CoverConfig,
                     text_left: int, text_right: int,
                     text_top: int, text_bottom: int,
                     panel_h: int,
                     isbn_keepout: bool):
    """Render tagline (title) + ornament + blurb + refrain into a text box.

    When isbn_keepout is True (KDP back panels), the blurb narrows to a left
    column once it descends into the bottom-right barcode band, and the refrain
    dodges the band — but NOTHING is drawn inside the keep-out itself.
    """
    draw = ImageDraw.Draw(canvas)
    text_width = text_right - text_left

    # Barcode keep-out geometry (bottom-right). We reserve it; we draw nothing in it.
    if isbn_keepout:
        barcode_w_px = int(cfg.isbn_w_in * DPI)
        barcode_h_px = int(cfg.isbn_h_in * DPI)
        barcode_left = text_right - barcode_w_px
        barcode_top_y = text_bottom - barcode_h_px
        narrow_text_width = barcode_left - text_left - int(0.15 * DPI)
    else:
        barcode_top_y = text_bottom
        narrow_text_width = text_width

    y = text_top

    # --- Title as a small-caps tagline atop the back panel ---
    tag_text = cfg.title.upper()
    tag_size = int(panel_h * 0.028)
    tag_font = load_font(tag_size, weight=500)
    tag_tracking = 0.08
    tw, _ = measure_tracked(tag_text, tag_font, tag_tracking)
    # Auto-shrink if the title is long.
    while tw > text_width and tag_size > int(panel_h * 0.016):
        tag_size -= 2
        tag_font = load_font(tag_size, weight=500)
        tw, _ = measure_tracked(tag_text, tag_font, tag_tracking)
    x = text_left + (text_width - tw) // 2
    draw_tracked(draw, (x, y), tag_text, tag_font, tag_tracking, cfg.col_gold)
    y += int(tag_size * 1.9)

    # --- Ornament separator ---
    orn_size = int(panel_h * 0.020)
    orn_font = _ornament_font(orn_size)
    orn = "✦"
    ob = orn_font.getbbox(orn)
    ow = ob[2] - ob[0]
    draw.text((text_left + (text_width - ow) // 2, y), orn, font=orn_font, fill=cfg.col_gold)
    y += int(orn_size * 2.4)

    # --- Blurb body (from the KDP description), greedy-wrapped, adaptive width ---
    paragraphs = _strip_html(cfg.description_html)
    blurb_size = int(panel_h * 0.0195)
    blurb_font = load_font(blurb_size, weight=400)
    line_h = int(blurb_size * 1.48)

    def render_paragraph(para_text: str, y_start: int) -> int:
        words = para_text.split()
        yy = y_start
        i = 0
        while i < len(words):
            max_w = text_width if (yy + line_h) <= barcode_top_y else narrow_text_width
            current = []
            j = i
            while j < len(words):
                candidate = (" ".join(current) + " " + words[j]) if current else words[j]
                if blurb_font.getlength(candidate) <= max_w:
                    current.append(words[j])
                    j += 1
                else:
                    break
            if not current:
                current = [words[j]]
                j += 1
            draw.text((text_left, yy), " ".join(current), font=blurb_font, fill=cfg.col_cream)
            yy += line_h
            i = j
        return yy

    for para in paragraphs:
        y = render_paragraph(para, y)
        y += int(line_h * 0.55)

    # --- Closing refrain ---
    refrain = _refrain(cfg)
    if refrain:
        y += int(line_h * 0.25)
        refrain_size = int(panel_h * 0.023)
        refrain_font = load_font(refrain_size, weight=500)
        rw = int(refrain_font.getlength(refrain))
        refrain_line_h = int(refrain_size * 1.5)
        in_wide = (not isbn_keepout) or (y + refrain_line_h <= barcode_top_y)
        avail = text_width if in_wide else narrow_text_width
        # Shrink to fit the column: an unclamped refrain wider than the narrow
        # column would center NEGATIVE and run its right edge into the ISBN
        # keep-out (we draw NOTHING there).
        floor = max(12, int(panel_h * 0.014))
        while rw > avail and refrain_size > floor:
            refrain_size -= 2
            refrain_font = load_font(refrain_size, weight=500)
            rw = int(refrain_font.getlength(refrain))
        if rw > avail:
            print("  Refrain: DROPPED (cannot fit clear of the barcode keep-out)")
            return
        x = text_left + (avail - rw) // 2
        draw.text((x, y), refrain, font=refrain_font, fill=cfg.col_gold)


# ============================================================
# FRONT PANEL RENDERER (shared across profiles)
# ============================================================
def render_front_text(canvas: Image.Image, cfg: CoverConfig,
                      center_x: int,
                      trim_top: int, trim_bottom: int,
                      panel_h: int):
    """Render title (1-2 lines) + subtitle + author onto the front art.

    Title uses a dark fill + cream halo so it reads across a painterly gradient;
    author + subtitle sit lower with a dark halo. All kept inside the safe zone
    the caller has already established via trim_top/trim_bottom.
    """
    draw = ImageDraw.Draw(canvas)

    # ---- Title (may wrap to two lines on a space) ----
    title = cfg.title.upper()
    title_font_px = int(panel_h * 0.058)
    title_font = load_font(title_font_px, weight=600)
    title_tracking = cfg.title_tracking
    title_stroke = max(2, int(title_font_px * 0.020))

    # Split into at most two balanced lines if it's wide.
    words = title.split()
    line1, line2 = title, ""
    tw, _ = measure_tracked(title, title_font, title_tracking)
    # Keep ~0.5" clear each side of the BOOK'S trim — the module-constant 6.00
    # would let a 5x8 title overflow its safe zone and force a premature wrap
    # on an 8x10.
    max_title_w = int((cfg.trim_w - 1.0) * DPI)
    if tw > max_title_w and len(words) > 1:
        # Greedy split near the middle by word count.
        mid = len(words) // 2
        best = mid
        # Prefer the split that most balances the two line widths.
        best_delta = None
        for k in range(1, len(words)):
            a = " ".join(words[:k])
            b = " ".join(words[k:])
            wa, _ = measure_tracked(a, title_font, title_tracking)
            wb, _ = measure_tracked(b, title_font, title_tracking)
            delta = abs(wa - wb)
            if best_delta is None or delta < best_delta:
                best_delta = delta
                best = k
        line1 = " ".join(words[:best])
        line2 = " ".join(words[best:])

    _tyf = getattr(cfg, "title_y_frac", None)
    if _tyf is None:
        y = trim_top + int(panel_h * 0.030)
    else:
        # cover_layout best.y_frac: the band TOP as a fraction of the FULL
        # front-panel height from the PANEL top (layout scores on the same
        # scale_to_cover crop via --aspect). Clamp into the typographic safe
        # band so a low band can never collide with the author block.
        y = max(trim_top, min(int(panel_h * float(_tyf)),
                              trim_bottom - int(panel_h * 0.30)))
    for ln in ([line1, line2] if line2 else [line1]):
        w, h = measure_tracked(ln, title_font, title_tracking)
        # Shrink an individual over-wide line to fit.
        fsz = title_font_px
        while w > max_title_w and fsz > int(panel_h * 0.030):
            fsz -= 4
            title_font = load_font(fsz, weight=600)
            title_stroke = max(2, int(fsz * 0.020))
            w, h = measure_tracked(ln, title_font, title_tracking)
        draw_tracked(draw, (center_x - w // 2, y), ln, title_font, title_tracking,
                     cfg.col_dark, stroke_width=title_stroke, stroke_fill=cfg.col_cream)
        y += h - int(fsz * 0.18)

    # ---- Author near the bottom ----
    author = cfg.author.upper()
    author_font_px = int(panel_h * 0.026)
    author_font = load_font(author_font_px, use_bold_ttf=True)
    author_stroke = max(2, int(author_font_px * 0.045))
    aw, ah = measure_tracked(author, author_font, cfg.author_tracking)
    ay = trim_bottom - int(panel_h * 0.030) - ah
    draw_tracked(draw, (center_x - aw // 2, ay), author, author_font, cfg.author_tracking,
                 cfg.col_cream, stroke_width=author_stroke, stroke_fill=cfg.col_dark)

    # ---- Subtitle above the author ----
    if cfg.subtitle:
        sub_font_px = int(panel_h * 0.028)
        sub_font = load_font(sub_font_px, use_bold_ttf=True)
        sub_tracking = 0.025
        sub_stroke = max(2, int(sub_font_px * 0.045))
        sw, sh = measure_tracked(cfg.subtitle, sub_font, sub_tracking)
        sy = ay - int(panel_h * 0.028) - sh
        draw_tracked(draw, (center_x - sw // 2, sy), cfg.subtitle, sub_font, sub_tracking,
                     cfg.col_cream, stroke_width=sub_stroke, stroke_fill=cfg.col_dark)


# ============================================================
# SPINE RENDERER (shared across profiles) — horizontal then rotate(-90)
# ============================================================
def render_spine(spine_w_px: int, spine_h_px: int, cfg: CoverConfig,
                 top_bottom_pad_px: int) -> Image.Image:
    """Compose the spine horizontally (title, ornament, author) then rotate -90.

    Text is double-drawn (+1px) for weight on a narrow spine. The spine face
    matches the cover dark background color; no image on the spine.
    """
    # §16.1 BLANK-SPINE FLOOR — below KDP's spine-text minimum a title can only
    # render as an illegible sliver (and KDP forbids spine text there), so return
    # a clean dark spine face at the final orientation/size. Checked first, before
    # any text setup, so every profile that shares this renderer is protected.
    spine_in = spine_w_px / DPI
    if spine_in < SPINE_TEXT_MIN_IN:
        print(f"  Spine text: BLANKED (spine {spine_in:.4f}\" < {SPINE_TEXT_MIN_IN}\" "
              f"KDP spine-text minimum; LESSONS_LEDGER 16.1) - dark face only")
        return Image.new("RGB", (spine_w_px, spine_h_px), cfg.col_dark)

    # Horizontal temp canvas: width = book height, height = spine width.
    tmp = Image.new("RGB", (spine_h_px, spine_w_px), cfg.col_dark)
    d = ImageDraw.Draw(tmp)

    spine_px = spine_w_px  # spine physical width in px
    # §16.1 LEGIBLE FLOOR — fill 0.55 of the spine width (up from 0.40; Bo kept
    # enlarging thin-book spine titles by hand). No fixed-px floor: a constant px
    # floor on a thin spine would exceed the spine width and overflow the rotate;
    # the fraction keeps the glyph inside the spine at any legal width, and the
    # sub-threshold case is already blanked above, so the title is as large as
    # the spine allows and never an illegible sliver. Author/ornament scale off
    # this via measure_block(), so they track the larger title automatically.
    title_size = int(spine_px * 0.55)
    title_font = load_font(title_size, weight=600)
    spine_title = cfg.title.upper()
    title_tracking = 0.04

    # Shrink to fit the available horizontal run (book height minus pads).
    avail = spine_h_px - 2 * top_bottom_pad_px
    stw, sth = measure_tracked(spine_title, title_font, title_tracking)

    # Combined block = title + ornament + author; measure and shrink together.
    author = cfg.author.upper()
    author_tracking = 0.10

    def measure_block(tsize):
        tf = load_font(tsize, weight=600)
        af = load_font(max(20, int(tsize * 0.85)), weight=600)
        w_t, h_t = measure_tracked(spine_title, tf, title_tracking)
        orn_sz = max(16, int(spine_px * 0.28))
        of = _ornament_font(orn_sz)
        ob = of.getbbox("✦")
        w_o = ob[2] - ob[0]
        w_a, h_a = measure_tracked(author, af, author_tracking)
        gap = int(0.40 * DPI)
        total = w_t + gap + w_o + gap + w_a
        return total, tf, af, of, w_t, w_o, w_a, max(h_t, h_a)

    total, title_font, author_font, orn_font, w_t, w_o, w_a, block_h = measure_block(title_size)
    while total > avail and title_size > 20:
        title_size -= 3
        total, title_font, author_font, orn_font, w_t, w_o, w_a, block_h = measure_block(title_size)

    gap = int(0.40 * DPI)
    start_x = (spine_h_px - total) // 2
    y_center = (spine_w_px - block_h) // 2

    # Title (double-drawn for weight)
    draw_tracked(d, (start_x, y_center), spine_title, title_font, title_tracking, cfg.col_cream)
    draw_tracked(d, (start_x + 1, y_center), spine_title, title_font, title_tracking, cfg.col_cream)

    # Ornament
    orn = "✦"
    ob = orn_font.getbbox(orn)
    orn_h = ob[3] - ob[1]
    orn_x = start_x + w_t + gap
    d.text((orn_x, (spine_w_px - orn_h) // 2), orn, font=orn_font, fill=cfg.col_gold)

    # Author (double-drawn)
    author_x = orn_x + w_o + gap
    draw_tracked(d, (author_x, y_center), author, author_font, author_tracking, cfg.col_cream)
    draw_tracked(d, (author_x + 1, y_center), author, author_font, author_tracking, cfg.col_cream)

    # Rotate -90 (clockwise) so it reads top-to-bottom on the shelf.
    final = tmp.rotate(-90, expand=True)
    if final.size != (spine_w_px, spine_h_px):
        final = final.resize((spine_w_px, spine_h_px), Image.LANCZOS)
    return final


# ============================================================
# PROFILE: KDP SINGLE-WRAP (paperback OR hardcover)
# ============================================================
def build_kdp_wrap(cfg: CoverConfig, pages: int, profile: str,
                   art_path: Path, out_dir: Path) -> dict:
    """Build a single [back|spine|front] wrap PDF+JPG for a KDP profile.

    profile == 'kdp-wrap'      -> 0.125" bleed, no board add.
    profile == 'kdp-hardcover' -> 0.708" turn-in, white-only spine math, height 10.417.
    """
    hardcover = (profile == "kdp-hardcover")

    trim_w = cfg.trim_w
    trim_h = cfg.trim_h

    # SINGLE source of truth for KDP wrap geometry: preset_lookup — the SAME code
    # path verify_build._expected_wrap recomputes from, so the verifier checks
    # exactly what we build (no re-implementation drift). book_config.spine.* is
    # passed straight through; spine_override_in wins inside the helper.
    if hardcover:
        d = preset_lookup.kdp_hardcover_wrap_dims(
            trim_w, trim_h, pages,
            per_page_white=cfg.per_page_white,
            board_add_in=cfg.kdp_hc_board_add,
            turn_in_in=cfg.kdp_hc_turn_in,
            height_in=cfg.kdp_hc_height,
            spine_override_in=cfg.spine_override)
        edge_in = d["turn_in_in"]              # 0.708 case-board turn-in (NOT bleed)
        out_name = "cover_wrap_hardcover"
        quiet_in = 0.375                        # inside the trim, from trim edge
    else:
        d = preset_lookup.kdp_paperback_wrap_dims(
            trim_w, trim_h, pages, cfg.paper,
            per_page_cream=cfg.per_page_cream,
            per_page_white=cfg.per_page_white,
            bleed_in=cfg.kdp_bleed,
            spine_override_in=cfg.spine_override)
        edge_in = d["bleed_in"]                # 0.125 bleed
        out_name = "cover_wrap"
        quiet_in = 0.375
    spine_in = d["spine"]
    wrap_w_in = d["cover_w"]
    wrap_h_in = d["cover_h"]

    wrap_w = math.ceil(wrap_w_in * DPI)
    wrap_h = math.ceil(wrap_h_in * DPI)
    edge_px = int(edge_in * DPI)
    quiet_px = int(quiet_in * DPI)

    # Panel x-boundaries: back | spine | front (spine width = residual for exact fit).
    back_x0 = 0
    back_x1 = int((edge_in + trim_w) * DPI)
    spine_x0 = back_x1
    spine_x1 = spine_x0 + int(spine_in * DPI)
    front_x0 = spine_x1
    front_x1 = wrap_w

    # Build human-readable notes OUTSIDE the f-string replacement fields — a
    # backslash inside a {..} field is a SyntaxError on Python 3.10/3.11 (the
    # kit's floor). Keep all escapes in plain string literals.
    white_note = " | spine math forced WHITE (KDP HC)" if hardcover else ""
    board_note = ("+%.3f\" boards" % cfg.kdp_hc_board_add) if hardcover else "no board add"
    edge_kind = "turn-in" if hardcover else "bleed"

    print(f"\n=== {profile.upper()} WRAP ===")
    print(f"  Pages: {pages} | Book paper: {cfg.paper}{white_note}")
    print(f"  Spine: {spine_in:.4f}\"  ({board_note})")
    print(f"  Edge: {edge_in}\" ({edge_kind}) | Quiet: {quiet_in}\"")
    print(f"  Target wrap: {wrap_w_in:.4f}\" x {wrap_h_in:.4f}\"  ({wrap_w} x {wrap_h} px @ {DPI} DPI)")
    print(f"  Panels: back 0-{back_x1} | spine {spine_x0}-{spine_x1} | front {front_x0}-{front_x1}")

    canvas = Image.new("RGB", (wrap_w, wrap_h), cfg.col_dark)
    src_raw = Image.open(art_path).convert("RGB")

    # ---- FRONT panel: full-bleed art (scale_to_cover) + typography ----
    front_w = front_x1 - front_x0
    front_panel = scale_to_cover(src_raw, front_w, wrap_h, bg=cfg.col_dark)
    canvas.paste(front_panel, (front_x0, 0))

    front_trim_left = front_x0
    front_trim_right = front_x1 - edge_px
    front_trim_top = edge_px
    front_trim_bottom = wrap_h - edge_px
    front_center_x = (front_trim_left + front_trim_right) // 2
    # Typography kept >= edge + quiet from every edge.
    render_front_text(canvas, cfg, front_center_x,
                      front_trim_top + quiet_px, front_trim_bottom - quiet_px, wrap_h)

    # ---- BACK panel: darkened art (scale_to_cover so it fills) + text ----
    back_w = back_x1 - back_x0
    back_panel = scale_to_cover(src_raw, back_w, wrap_h, bg=cfg.col_dark)
    overlay = Image.new("RGBA", (back_w, wrap_h), (0, 0, 0, 200))
    back_panel = Image.alpha_composite(back_panel.convert("RGBA"), overlay).convert("RGB")
    canvas.paste(back_panel, (back_x0, 0))

    back_text_left = back_x0 + edge_px + quiet_px
    back_text_right = back_x1 - quiet_px
    back_text_top = edge_px + quiet_px
    back_text_bottom = wrap_h - edge_px - quiet_px
    render_back_text(canvas, cfg,
                     back_text_left, back_text_right,
                     back_text_top, back_text_bottom,
                     wrap_h, isbn_keepout=True)

    # ---- SPINE ----
    spine_w_px = spine_x1 - spine_x0
    spine_final = render_spine(spine_w_px, wrap_h, cfg, top_bottom_pad_px=edge_px + int(0.5 * DPI))
    canvas.paste(spine_final, (spine_x0, 0))

    # ---- SAVE ----
    out_dir.mkdir(parents=True, exist_ok=True)
    out_jpg = out_dir / f"{out_name}.jpg"
    out_pdf = out_dir / f"{out_name}.pdf"
    canvas.save(out_jpg, "JPEG", quality=95, dpi=(DPI, DPI))
    w_pts, h_pts = save_pdf_exact(canvas, out_pdf, wrap_w_in, wrap_h_in)

    actual_w_in = w_pts / PT_PER_IN
    actual_h_in = h_pts / PT_PER_IN
    print(f"  -> {out_jpg}")
    print(f"  -> {out_pdf}")
    print(f"  -> PDF MediaBox: {w_pts:.2f} x {h_pts:.2f} pts "
          f"= {actual_w_in:.4f}\" x {actual_h_in:.4f}\"")
    print(f"  -> SELF-VERIFY: target {wrap_w_in:.4f}x{wrap_h_in:.4f} vs "
          f"actual {actual_w_in:.4f}x{actual_h_in:.4f} "
          f"[{'OK' if abs(actual_w_in - wrap_w_in) < 1e-4 and abs(actual_h_in - wrap_h_in) < 1e-4 else 'MISMATCH'}]")

    return {
        "profile": profile,
        "pages": pages,
        "spine_in": spine_in,
        "target_wrap_in": [wrap_w_in, wrap_h_in],
        "actual_wrap_in": [round(actual_w_in, 4), round(actual_h_in, 4)],
        "files": [str(out_pdf), str(out_jpg)],
    }


# ============================================================
# PROFILE: MIXAM 3-PANEL
# ============================================================
def build_mixam(cfg: CoverConfig, pages: int, art_path: Path, out_dir: Path) -> dict:
    """Build front_cover.pdf / back_cover.pdf / spine.pdf. Front/back carry
    0.80" bleed on ALL sides; the separate spine.pdf is EXACTLY spine-width
    with bleed on TOP/BOTTOM only — measured from Mixam's own template-
    generator PDFs (docs/service_templates/mixam_template_6x9_hardcover_
    spine060.pdf: spine page 0.6000 x 10.6000 in for a 0.60" spine). An
    L/R-bled spine would also mis-size the spine TITLE, which keys off the
    panel width."""
    trim_w = cfg.trim_w
    trim_h = cfg.trim_h
    spine_in = cfg.spine_in(pages, "mixam-3panel")
    bleed_in = cfg.mixam_bleed  # 0.80

    front_w = int((trim_w + 2 * bleed_in) * DPI)
    front_h = int((trim_h + 2 * bleed_in) * DPI)
    spine_panel_w = int(spine_in * DPI)     # exact spine width — NO L/R bleed

    bleed_px = int(bleed_in * DPI)
    quiet_px = int(0.25 * DPI)          # general content quiet from trim edge
    # Typography kept >= bleed + 0.25" from every edge (Mixam = 1.05").

    print(f"\n=== MIXAM-3PANEL ===")
    print(f"  Pages: {pages} | paper: {cfg.paper}")
    print(f"  Spine: {spine_in:.4f}\"  (= {pages} x per_page + {cfg.mixam_board_add} board add)")
    print(f"  Bleed: {bleed_in}\" all sides on front/back; top/bottom only on the spine file")
    print(f"  Front/Back panel: {trim_w + 2*bleed_in:.2f}\" x {trim_h + 2*bleed_in:.2f}\"  ({front_w} x {front_h} px)")
    print(f"  Spine panel: {spine_in:.4f}\" x {trim_h + 2*bleed_in:.2f}\"  ({spine_panel_w} x {front_h} px; exact spine width per the Mixam template)")

    out_dir.mkdir(parents=True, exist_ok=True)
    src_raw = Image.open(art_path).convert("RGB")
    files = []

    # ---- FRONT ----
    front = scale_to_cover(src_raw, front_w, front_h, bg=cfg.col_dark)
    trim_top = bleed_px
    trim_bottom = front_h - bleed_px
    center_x = front_w // 2
    render_front_text(front, cfg, center_x, trim_top + quiet_px, trim_bottom - quiet_px, front_h)
    f_jpg = out_dir / "front_cover.jpg"
    f_pdf = out_dir / "front_cover.pdf"
    front.save(f_jpg, "JPEG", quality=95, dpi=(DPI, DPI))
    fw_pts, fh_pts = save_pdf_exact(front, f_pdf, trim_w + 2 * bleed_in, trim_h + 2 * bleed_in)
    print(f"  -> {f_pdf}  ({fw_pts/PT_PER_IN:.4f}\" x {fh_pts/PT_PER_IN:.4f}\")")
    files += [str(f_pdf), str(f_jpg)]

    # ---- BACK (darkened art fills; scale_to_cover, text box wider quiet on spine side) ----
    back = scale_to_cover(src_raw, front_w, front_h, bg=cfg.col_dark)
    overlay = Image.new("RGBA", (front_w, front_h), (0, 0, 0, 200))
    back = Image.alpha_composite(back.convert("RGBA"), overlay).convert("RGB")
    quiet_spine_px = int(0.40 * DPI)
    b_text_left = bleed_px + quiet_px
    b_text_right = front_w - bleed_px - quiet_spine_px
    b_text_top = bleed_px + quiet_px
    b_text_bottom = front_h - bleed_px - quiet_px
    # Mixam does NOT auto-stamp an ISBN barcode -> no keep-out narrowing.
    render_back_text(back, cfg, b_text_left, b_text_right, b_text_top, b_text_bottom,
                     front_h, isbn_keepout=False)
    b_jpg = out_dir / "back_cover.jpg"
    b_pdf = out_dir / "back_cover.pdf"
    back.save(b_jpg, "JPEG", quality=95, dpi=(DPI, DPI))
    bw_pts, bh_pts = save_pdf_exact(back, b_pdf, trim_w + 2 * bleed_in, trim_h + 2 * bleed_in)
    print(f"  -> {b_pdf}  ({bw_pts/PT_PER_IN:.4f}\" x {bh_pts/PT_PER_IN:.4f}\")")
    files += [str(b_pdf), str(b_jpg)]

    # ---- SPINE (own panel = EXACT spine width; T/B bleed only). Passing the
    # true spine width also makes render_spine's title sizing and its blank-
    # below-minimum floor operate on the real spine thickness. ----
    spine_final = render_spine(spine_panel_w, front_h, cfg, top_bottom_pad_px=bleed_px)
    s_jpg = out_dir / "spine.jpg"
    s_pdf = out_dir / "spine.pdf"
    spine_final.save(s_jpg, "JPEG", quality=95, dpi=(DPI, DPI))
    sw_pts, sh_pts = save_pdf_exact(spine_final, s_pdf, spine_in, trim_h + 2 * bleed_in)
    print(f"  -> {s_pdf}  ({sw_pts/PT_PER_IN:.4f}\" x {sh_pts/PT_PER_IN:.4f}\")")
    files += [str(s_pdf), str(s_jpg)]

    print(f"  NOTE: upload these three PDFs + the interior as 'inner_{cfg.slug}.pdf' "
          f"(Mixam routes by filename keyword: front_cover/back_cover/spine/inner_).")
    print(f"  NOTE: Mixam board-add is NON-constant; if Mixam's job calculator states a "
          f"different spine, set spine.spine_override_in in book_config and regenerate spine only.")

    return {
        "profile": "mixam-3panel",
        "pages": pages,
        "spine_in": spine_in,
        # target_wrap_in = the FRONT panel dims (what verify_build checks the
        # front_cover.pdf MediaBox against; the 3-panel form has no spread).
        "target_wrap_in": [round(trim_w + 2 * bleed_in, 4), round(trim_h + 2 * bleed_in, 4)],
        "front_panel_in": [round(trim_w + 2 * bleed_in, 4), round(trim_h + 2 * bleed_in, 4)],
        "spine_panel_in": [round(spine_in, 4), round(trim_h + 2 * bleed_in, 4)],
        "files": files,
        "inner_upload_name": f"inner_{cfg.slug}.pdf",
    }


# ============================================================
# GENERIC FLAT SINGLE-WRAP (softcover bleed model) — shared by
# mixam-paperback-wrap and blurb-wrap. Same visible-face model as kdp-wrap
# (faces = trim inset by bleed; fold at the spine edges exact), parameterized
# for quiet zones, barcode keep-out, and the blank-below-minimum spine rule.
# ============================================================
def build_flat_wrap(cfg: CoverConfig, pages: int, profile: str,
                    art_path: Path, out_dir: Path, *,
                    spine_in: float, bleed_in: float,
                    wrap_w_in: float, wrap_h_in: float,
                    out_name: str, quiet_in: float, quiet_spine_in: float,
                    isbn_keepout: bool, spine_blank_below_in: float = 0.0,
                    spine_note: str = "", notes=()) -> dict:
    """Build a single [back|spine|front] wrap PDF+JPG at flat softcover
    geometry. Wrap dims are passed IN (already derived via preset_lookup or
    formula by the profile wrapper) so this stays a pure renderer."""
    trim_w = cfg.trim_w

    wrap_w = math.ceil(wrap_w_in * DPI)
    wrap_h = math.ceil(wrap_h_in * DPI)
    edge_px = int(bleed_in * DPI)
    quiet_px = int(quiet_in * DPI)
    quiet_spine_px = int(quiet_spine_in * DPI)

    # Panel x-boundaries: back | spine | front (spine width = residual for exact fit).
    back_x0 = 0
    back_x1 = int((bleed_in + trim_w) * DPI)
    spine_x0 = back_x1
    spine_x1 = spine_x0 + int(spine_in * DPI)
    front_x0 = spine_x1
    front_x1 = wrap_w

    spine_blank = spine_blank_below_in > 0 and spine_in < spine_blank_below_in

    print(f"\n=== {profile.upper()} ===")
    print(f"  Pages: {pages} | Book paper: {cfg.paper}")
    print(f"  Spine: {spine_in:.4f}\"" + (f"  ({spine_note})" if spine_note else ""))
    print(f"  Bleed: {bleed_in}\" | Quiet: {quiet_in}\" all + {quiet_spine_in}\" spine-side")
    print(f"  Target wrap: {wrap_w_in:.4f}\" x {wrap_h_in:.4f}\"  ({wrap_w} x {wrap_h} px @ {DPI} DPI)")
    print(f"  Panels: back 0-{back_x1} | spine {spine_x0}-{spine_x1} | front {front_x0}-{front_x1}")
    if spine_blank:
        print(f"  Spine text: BLANKED (spine {spine_in:.4f}\" < {spine_blank_below_in}\" kit minimum)")

    canvas = Image.new("RGB", (wrap_w, wrap_h), cfg.col_dark)
    src_raw = Image.open(art_path).convert("RGB")

    # ---- FRONT panel: full-bleed art (scale_to_cover) + typography ----
    front_w = front_x1 - front_x0
    front_panel = scale_to_cover(src_raw, front_w, wrap_h, bg=cfg.col_dark)
    canvas.paste(front_panel, (front_x0, 0))

    front_trim_left = front_x0                      # spine fold — exact, no bleed
    front_trim_right = front_x1 - edge_px           # outer trim edge
    front_center_x = (front_trim_left + front_trim_right) // 2
    render_front_text(canvas, cfg, front_center_x,
                      edge_px + quiet_px, wrap_h - edge_px - quiet_px, wrap_h)

    # ---- BACK panel: darkened art + text (quieter on the spine side) ----
    back_w = back_x1 - back_x0
    back_panel = scale_to_cover(src_raw, back_w, wrap_h, bg=cfg.col_dark)
    overlay = Image.new("RGBA", (back_w, wrap_h), (0, 0, 0, 200))
    back_panel = Image.alpha_composite(back_panel.convert("RGBA"), overlay).convert("RGB")
    canvas.paste(back_panel, (back_x0, 0))

    back_text_left = back_x0 + edge_px + quiet_px   # outer edge: bleed + quiet
    back_text_right = back_x1 - quiet_spine_px      # spine side: spine quiet
    back_text_top = edge_px + quiet_px
    back_text_bottom = wrap_h - edge_px - quiet_px
    render_back_text(canvas, cfg,
                     back_text_left, back_text_right,
                     back_text_top, back_text_bottom,
                     wrap_h, isbn_keepout=isbn_keepout)

    # ---- SPINE (blank below the kit minimum width — dark face only) ----
    spine_w_px = spine_x1 - spine_x0
    if not spine_blank and spine_w_px > 0:
        spine_final = render_spine(spine_w_px, wrap_h, cfg,
                                   top_bottom_pad_px=edge_px + int(0.5 * DPI))
        canvas.paste(spine_final, (spine_x0, 0))

    # ---- SAVE ----
    out_dir.mkdir(parents=True, exist_ok=True)
    out_jpg = out_dir / f"{out_name}.jpg"
    out_pdf = out_dir / f"{out_name}.pdf"
    canvas.save(out_jpg, "JPEG", quality=95, dpi=(DPI, DPI))
    w_pts, h_pts = save_pdf_exact(canvas, out_pdf, wrap_w_in, wrap_h_in)

    actual_w_in = w_pts / PT_PER_IN
    actual_h_in = h_pts / PT_PER_IN
    print(f"  -> {out_jpg}")
    print(f"  -> {out_pdf}")
    print(f"  -> PDF MediaBox: {w_pts:.2f} x {h_pts:.2f} pts "
          f"= {actual_w_in:.4f}\" x {actual_h_in:.4f}\"")
    print(f"  -> SELF-VERIFY: target {wrap_w_in:.4f}x{wrap_h_in:.4f} vs "
          f"actual {actual_w_in:.4f}x{actual_h_in:.4f} "
          f"[{'OK' if abs(actual_w_in - wrap_w_in) < 1e-4 and abs(actual_h_in - wrap_h_in) < 1e-4 else 'MISMATCH'}]")
    for n in notes:
        print(f"  NOTE: {n}")

    return {
        "profile": profile,
        "pages": pages,
        "spine_in": round(spine_in, 4),
        "target_wrap_in": [round(wrap_w_in, 4), round(wrap_h_in, 4)],
        "actual_wrap_in": [round(actual_w_in, 4), round(actual_h_in, 4)],
        "files": [str(out_pdf), str(out_jpg)],
    }


# ============================================================
# PROFILE: MIXAM PAPERBACK WRAP (kdp-wrap geometry, preset_lookup spine)
# ============================================================
def build_mixam_paperback_wrap(cfg: CoverConfig, pages: int,
                               art_path: Path, out_dir: Path) -> dict:
    """Mixam paperback single wrap — EXACTLY the kdp-wrap spread geometry at
    0.125\" bleed. Spine via preset_lookup.mixam_paperback_spine (override wins;
    cream formula from Mixam's live calculator; white INFERRED)."""
    spine_in = preset_lookup.mixam_paperback_spine(pages, cfg.paper, cfg.spine_override)
    dims = preset_lookup.mixam_paperback_wrap_dims(cfg.trim_w, cfg.trim_h, spine_in)
    if cfg.spine_override is not None:
        spine_note = "spine_override_in (cart value — canonical)"
    elif cfg.paper == "cream":
        spine_note = f"= {pages} x 0.0023 + 0.04 (cream 50lb calc fit)"
    else:
        spine_note = f"= {pages} x 0.00215 + 0.01 (white/uncoated — INFERRED, cart canonical)"
    return build_flat_wrap(
        cfg, pages, "mixam-paperback-wrap", art_path, out_dir,
        spine_in=spine_in, bleed_in=dims["bleed_in"],
        wrap_w_in=dims["cover_w"], wrap_h_in=dims["cover_h"],
        out_name="cover_wrap_mixam",
        quiet_in=0.25, quiet_spine_in=0.50,          # preset cover_quiet_in
        isbn_keepout=False,                          # Mixam does not auto-stamp
        spine_blank_below_in=0.25,                   # preset spine_text_rule (kit rule)
        spine_note=spine_note,
        notes=[
            f"upload the body as 'inner_{cfg.slug}.pdf' (Mixam routes by filename keyword).",
            "Mixam's CART spine is canonical; if it states a different width, set "
            "spine.spine_override_in in book_config and regenerate this wrap.",
        ])


# ============================================================
# PROFILE: BLURB TRADE SOFTCOVER WRAP (preset_lookup softcover_dims)
# ============================================================
def build_blurb_wrap(cfg: CoverConfig, pages: int,
                     art_path: Path, out_dir: Path) -> dict:
    """Blurb Trade softcover single wrap at the probed calculator geometry
    (spine interpolated; W = 2*trim_w + spine + 0.25; H = trim_h + 0.25)."""
    tkey = preset_lookup.trim_key(cfg.trim_w, cfg.trim_h)
    d = preset_lookup.softcover_dims(tkey, cfg.blurb_paper, pages)
    return build_flat_wrap(
        cfg, pages, "blurb-wrap", art_path, out_dir,
        spine_in=d["spine"], bleed_in=d["bleed_in"],
        wrap_w_in=d["cover_w"], wrap_h_in=d["cover_h"],
        out_name="cover_wrap_blurb",
        quiet_in=0.375, quiet_spine_in=0.375,        # kdp-wrap model (> Blurb 0.25 safety)
        isbn_keepout=True,                           # INFERRED: Blurb applies its own barcode
        spine_note=f"interpolated from Blurb {cfg.blurb_paper} softcover table",
        notes=[
            "Blurb applies its own barcode for bookstore distribution (INFERRED) — "
            "back-cover bottom-right kept clear.",
            f"interior uploads as {cfg.slug}_BLURB_TRADE (page PDF = trim + 0.125 W / + 0.25 H).",
        ])


# ============================================================
# PROFILE: BLURB HARDCOVER IMAGEWRAP (preset_lookup imagewrap_dims)
# ============================================================
def build_blurb_imagewrap(cfg: CoverConfig, pages: int,
                          art_path: Path, out_dir: Path) -> dict:
    """Blurb Hardcover ImageWrap single wrap.

    Geometry (probed rows via preset_lookup — never derived):
      panel_total = (cover_w - spine) / 2
      m           = panel_total - trim_w      (lost to the OUTER-edge wrap)
      visible front face x-span = [cover_w - panel_total, cover_w - m]  (width = trim_w)
      visible back  face x-span = [m, panel_total]
      spine centered            = [panel_total, panel_total + spine]
      vertical visible span ~= centered trim_h; text inset >=
      (cover_h - trim_h)/2 + 0.25 from top/bottom.
    Title/author are centered on the VISIBLE front face, not the panel."""
    tkey = preset_lookup.trim_key(cfg.trim_w, cfg.trim_h)
    d = preset_lookup.imagewrap_dims(tkey, cfg.blurb_paper, pages)
    cover_w_in, cover_h_in, spine_in = d["cover_w"], d["cover_h"], d["spine"]
    trim_w, trim_h = cfg.trim_w, cfg.trim_h

    panel_total_in = (cover_w_in - spine_in) / 2.0
    m_in = panel_total_in - trim_w                   # outer-edge wrap allowance
    v_margin_in = (cover_h_in - trim_h) / 2.0        # top/bottom wrap allowance
    quiet_in = 0.25                                  # Blurb safety (probed 0.25)

    W = math.ceil(cover_w_in * DPI)
    H = math.ceil(cover_h_in * DPI)
    panel_total_px = int(panel_total_in * DPI)
    spine_px = int(spine_in * DPI)
    m_px = int(m_in * DPI)
    v_margin_px = int(v_margin_in * DPI)
    quiet_px = int(quiet_in * DPI)

    # Visible faces (per spec — fold at the spine edge EXACT, outer edge loses m).
    front_vis_x0 = W - panel_total_px                # == panel_total + spine (px)
    front_vis_x1 = W - m_px
    back_vis_x0 = m_px
    back_vis_x1 = panel_total_px

    print(f"\n=== BLURB-IMAGEWRAP ===")
    print(f"  Pages: {pages} | Blurb paper: {cfg.blurb_paper}")
    print(f"  Spine: {spine_in:.4f}\"  (interpolated; 0.25\" board minimum below ~100pp)")
    print(f"  Target wrap: {cover_w_in:.4f}\" x {cover_h_in:.4f}\"  ({W} x {H} px @ {DPI} DPI)")
    print(f"  panel_total: {panel_total_in:.4f}\" | wrap allowance m: {m_in:.4f}\" "
          f"| vertical allowance: {v_margin_in:.4f}\"")
    print(f"  Panels: back 0-{panel_total_px} | spine {panel_total_px}-{panel_total_px + spine_px} "
          f"| front {panel_total_px + spine_px}-{W}")
    print(f"  Visible faces: back [{back_vis_x0},{back_vis_x1}] | "
          f"front [{front_vis_x0},{front_vis_x1}]  (width = trim_w)")

    canvas = Image.new("RGB", (W, H), cfg.col_dark)
    src_raw = Image.open(art_path).convert("RGB")

    # ---- FRONT panel: art fills the WHOLE physical panel (it wraps the board) ----
    front_panel_w = W - (panel_total_px + spine_px)
    front_panel = scale_to_cover(src_raw, front_panel_w, H, bg=cfg.col_dark)
    canvas.paste(front_panel, (panel_total_px + spine_px, 0))

    # Typography centered on the VISIBLE front face; vertical inset >= v_margin + quiet.
    front_center_x = (front_vis_x0 + front_vis_x1) // 2
    render_front_text(canvas, cfg, front_center_x,
                      v_margin_px + quiet_px, H - v_margin_px - quiet_px, H)

    # ---- BACK panel: darkened art across the whole physical panel ----
    back_panel = scale_to_cover(src_raw, panel_total_px, H, bg=cfg.col_dark)
    overlay = Image.new("RGBA", (panel_total_px, H), (0, 0, 0, 200))
    back_panel = Image.alpha_composite(back_panel.convert("RGBA"), overlay).convert("RGB")
    canvas.paste(back_panel, (0, 0))

    # Back text inside the VISIBLE back face, inset by quiet (spine fold side too).
    render_back_text(canvas, cfg,
                     back_vis_x0 + quiet_px, back_vis_x1 - quiet_px,
                     v_margin_px + quiet_px, H - v_margin_px - quiet_px,
                     H, isbn_keepout=True)   # INFERRED: Blurb applies its own barcode

    # ---- SPINE: dark strip + text kept inside the visible vertical span ----
    if spine_px > 0:
        spine_final = render_spine(spine_px, H, cfg,
                                   top_bottom_pad_px=v_margin_px + quiet_px)
        canvas.paste(spine_final, (panel_total_px, 0))

    # ---- SAVE ----
    out_dir.mkdir(parents=True, exist_ok=True)
    out_jpg = out_dir / "cover_wrap_imagewrap.jpg"
    out_pdf = out_dir / "cover_wrap_imagewrap.pdf"
    canvas.save(out_jpg, "JPEG", quality=95, dpi=(DPI, DPI))
    w_pts, h_pts = save_pdf_exact(canvas, out_pdf, cover_w_in, cover_h_in)

    actual_w_in = w_pts / PT_PER_IN
    actual_h_in = h_pts / PT_PER_IN
    print(f"  -> {out_jpg}")
    print(f"  -> {out_pdf}")
    print(f"  -> PDF MediaBox: {w_pts:.2f} x {h_pts:.2f} pts "
          f"= {actual_w_in:.4f}\" x {actual_h_in:.4f}\"")
    print(f"  -> SELF-VERIFY: target {cover_w_in:.4f}x{cover_h_in:.4f} vs "
          f"actual {actual_w_in:.4f}x{actual_h_in:.4f} "
          f"[{'OK' if abs(actual_w_in - cover_w_in) < 1e-4 and abs(actual_h_in - cover_h_in) < 1e-4 else 'MISMATCH'}]")
    print("  NOTE: dims come from Blurb's probed cover-PDF rows (DO NOT derive); "
          "the Blurb previewer is canonical at upload.")

    return {
        "profile": "blurb-imagewrap",
        "pages": pages,
        "spine_in": round(spine_in, 4),
        "target_wrap_in": [round(cover_w_in, 4), round(cover_h_in, 4)],
        "actual_wrap_in": [round(actual_w_in, 4), round(actual_h_in, 4)],
        "panel_total_in": round(panel_total_in, 4),
        "wrap_allowance_in": round(m_in, 4),
        "files": [str(out_pdf), str(out_jpg)],
    }


# ============================================================
# CLI
# ============================================================
def resolve_art_path(cfg: CoverConfig, workspace: Path, override: str | None) -> Path:
    """Resolve the source AI-art PNG. Default: cover_art/<slug>_src.png under workspace."""
    if override:
        p = Path(override).expanduser()
        if not p.is_absolute():
            p = (workspace / p) if workspace else (Path.cwd() / p)
        return p
    # Default location + a couple of tolerant fallbacks.
    candidates = [
        workspace / "cover_art" / f"{cfg.slug}_src.png",
        workspace / "cover_art" / f"{cfg.slug}_src.jpg",
    ]
    art_dir = workspace / "cover_art"
    if art_dir.is_dir():
        pngs = sorted(art_dir.glob("*.png")) + sorted(art_dir.glob("*.jpg"))
        candidates += pngs
    for c in candidates:
        if c.exists():
            return c
    return candidates[0]  # return the canonical default even if missing (caller errors)


def build_kindle_front(cfg: CoverConfig, art_path: Path, out_dir: Path):
    """Front-only cover image for Kindle upload AND the digital PDF front page.
    High-res at the BOOK'S trim ratio (6:9 -> 1600x2400). No bleed — ebook
    covers are full-image."""
    out_dir.mkdir(parents=True, exist_ok=True)
    W = 1600
    H = int(round(W * (cfg.trim_h / cfg.trim_w)))   # trim-matched; 6:9 -> 2400
    art = Image.open(str(art_path)).convert("RGB")
    canvas = scale_to_cover(art, W, H)
    render_front_text(canvas, cfg, center_x=W // 2,
                      trim_top=0, trim_bottom=H, panel_h=H)
    jpg_path = out_dir / f"{cfg.slug}_KINDLE_cover.jpg"
    canvas.save(str(jpg_path), "JPEG", quality=92)
    print("\n=== KINDLE FRONT COVER ===")
    print(f"  {W}x{H}px  (trim ratio {cfg.trim_w:g}:{cfg.trim_h:g}, full-image, no bleed)")
    print(f"  -> {jpg_path}")
    return {"profile": "kindle", "size_px": [W, H], "files": [str(jpg_path)]}


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="BOOKSMITH parameterized cover compositor.")
    p.add_argument("--config", required=True, help="Path to book_config.json")
    p.add_argument("--profile", required=True,
                   choices=["kdp-wrap", "kdp-hardcover", "mixam-3panel",
                            "mixam-paperback-wrap", "blurb-wrap",
                            "blurb-imagewrap", "kindle"],
                   help="Which cover profile to build.")
    p.add_argument("--pages", required=True, type=int,
                   help="Page count from the generated interior PDF (drives spine math).")
    p.add_argument("--workspace", default=None,
                   help="book_workspace/<slug> dir where cover_art/ + outputs/ live. "
                        "Defaults to the config file's parent directory.")
    p.add_argument("--art", default=None,
                   help="Override the source art path (default cover_art/<slug>_src.png).")
    p.add_argument("--kit-env", default=str(SCRIPT_DIR / "kit_env.json"),
                   help="Path to kit_env.json (machine paths). Optional for compositing.")
    p.add_argument("--out", default=None,
                   help="Override the output dir (default <workspace>/outputs/<format>).")
    p.add_argument("--title-y-frac", type=float, default=None,
                   help="Optional: title band TOP as a fraction of the FULL front-panel height, "
                        "measured from the panel top. Feed cover_layout.py's 'best.y_frac' here, "
                        "scored with cover_layout --aspect so both sides share the scale_to_cover "
                        "frame. Clamped into the safe band. Default: 0.030*panel below the trim top.")
    args = p.parse_args(argv)

    cfg_path = Path(args.config).expanduser().resolve()
    if not cfg_path.exists():
        print(json.dumps({"error": f"config not found: {cfg_path}"}))
        return 1
    cfg = CoverConfig(load_json(cfg_path))
    if getattr(args, "title_y_frac", None) is not None:
        cfg.title_y_frac = float(args.title_y_frac)

    workspace = Path(args.workspace).expanduser().resolve() if args.workspace else cfg_path.parent
    art_path = resolve_art_path(cfg, workspace, args.art)
    if not art_path.exists():
        print(json.dumps({
            "error": f"source cover art not found: {art_path}",
            "hint": "Run cover_gen.py first, or pass --art <path>.",
        }))
        return 1

    if args.profile != "kindle" and args.pages <= 0:
        print(json.dumps({"error": f"--pages must be positive, got {args.pages}"}))
        return 1

    out_dir = (Path(args.out).expanduser().resolve() if args.out
               else workspace / "outputs" / PROFILE_OUTDIR[args.profile])

    print(f"Config:    {cfg_path}")
    print(f"Workspace: {workspace}")
    print(f"Art:       {art_path}")
    print(f"Fonts:     {FONTS_DIR}  (Light exists={FONT_LIGHT.exists()}, Bold exists={FONT_BOLD.exists()})")
    print(f"Output:    {out_dir}")

    if not FONT_LIGHT.exists() or not FONT_BOLD.exists():
        print(json.dumps({
            "error": "vendored Cormorant Garamond fonts missing",
            "expected": [str(FONT_LIGHT), str(FONT_BOLD)],
        }))
        return 1

    if args.profile == "kindle":
        result = build_kindle_front(cfg, art_path, out_dir)
    elif args.profile == "mixam-3panel":
        result = build_mixam(cfg, args.pages, art_path, out_dir)
    elif args.profile == "mixam-paperback-wrap":
        result = build_mixam_paperback_wrap(cfg, args.pages, art_path, out_dir)
    elif args.profile == "blurb-wrap":
        result = build_blurb_wrap(cfg, args.pages, art_path, out_dir)
    elif args.profile == "blurb-imagewrap":
        result = build_blurb_imagewrap(cfg, args.pages, art_path, out_dir)
    else:
        result = build_kdp_wrap(cfg, args.pages, args.profile, art_path, out_dir)

    # ---- cover_meta.json sidecar (EVERY profile) ----
    # verify_build.py reads this (pages + target) and independently recomputes
    # the expected dims via the same preset_lookup/formula code path.
    meta = {
        "profile": args.profile,
        "pages": args.pages,
        "spine_in": result.get("spine_in"),
        "target_wrap_in": result.get("target_wrap_in"),
        # source-art identity: lets a verifier detect a wrap composited from
        # OUTDATED art after a re-roll (page-count staleness alone can't)
        "art": str(art_path),
        "art_sha256": hashlib.sha256(art_path.read_bytes()).hexdigest(),
        "files": result.get("files", []),
    }
    meta_path = out_dir / "cover_meta.json"
    meta_path.write_text(json.dumps(meta, indent=2), encoding="utf-8")
    print(f"\ncover_meta.json -> {meta_path}")

    print("\n" + json.dumps({"status": "success", **result,
                             "cover_meta": str(meta_path)}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
