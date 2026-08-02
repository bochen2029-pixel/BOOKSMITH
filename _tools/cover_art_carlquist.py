#!/usr/bin/env python3
"""
cover_art_carlquist.py — bespoke cover ART for *The Cursive of Discovery*.

WHY THIS EXISTS (and not cover_gen.py/SDXL): this book's identity IS the
handwriting. A generated painting of "a botanical notebook" would be a picture
of the subject; a real page of Sherwin Carlquist's cursive is the subject. So
the source art is built from an actual archive scan rather than text-to-image.

WHAT IT MAKES: a duotone field of his handwriting on warm herbarium paper, with
a deliberately calm, washed upper third so the composited title has focal room
(the same rule cover_gen.py's prompt enforces: "upper third kept calm"), a soft
vignette, and NO baked text of any kind (typography is composited afterward by
composite_cover.py, per the kit's cover rule).

    python cover_art_carlquist.py --config <book_config.json> [--source <png>]
        [--out cover_art/<slug>_src.png] [--size 2000x3200]

Pure Pillow. Rights: the source scan is Carlquist/BRIT material (IMAGE-RIGHTS?),
tracked in RIGHTS_LEDGER.md like every other figure.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

try:
    from PIL import Image, ImageEnhance, ImageFilter
except ImportError:
    sys.exit("Pillow required:  pip install pillow")


def hex_rgb(h: str):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def duotone(gray: Image.Image, dark, light) -> Image.Image:
    """Map an 8-bit grayscale to a two-point ramp (light paper -> dark ink)."""
    lut = []
    for band in range(3):
        lo, hi = dark[band], light[band]
        lut += [int(round(lo + (hi - lo) * (i / 255.0))) for i in range(256)]
    return gray.convert("RGB").point(lut)


def build(source: Path, out: Path, w: int, h: int, palette: dict) -> dict:
    ink = hex_rgb(palette.get("ink", "1C2A4A"))
    cream = hex_rgb(palette.get("cream", "F1E9D2"))
    herb = hex_rgb(palette.get("herbarium", "2E3A2B"))

    src = Image.open(source).convert("L")

    # A notebook scan is a two-page SPREAD: the binding gutter would run straight
    # down the middle of the cover. Take a single page (the right half, where the
    # specimen numbers sit) so the field is one continuous run of writing.
    if src.width > src.height * 0.9:
        src = src.crop((int(src.width * 0.50), 0, src.width, src.height))

    # Cover the target frame without distortion (crop-to-fill).
    scale = max(w / src.width, h / src.height)
    src = src.resize((max(1, int(src.width * scale)), max(1, int(src.height * scale))),
                     Image.LANCZOS)
    left = (src.width - w) // 2
    top = int((src.height - h) * 0.42)          # bias slightly above center: more writing, less margin
    art = src.crop((left, top, left + w, top + h))

    # Lift the paper and deepen the ink so the cursive reads as texture, not noise.
    art = ImageEnhance.Contrast(art).enhance(1.55)
    art = ImageEnhance.Brightness(art).enhance(1.12)

    # Ink is dark, paper is light: map straight onto the book's palette.
    field = duotone(art, dark=ink, light=cream)

    # A whisper of herbarium green so it reads botanical rather than merely "old
    # paper". Kept light: too much and the warm cream turns to grey.
    wash = Image.new("RGB", (w, h), herb)
    field = Image.blend(field, wash, 0.06)

    # Vertical wash: strongest at the very top (title zone), clearing by ~45%.
    paper = Image.new("RGB", (w, h), cream)
    # The title lands in the upper third, so that band is washed nearly to clean
    # paper (the vision gate wants real focal room, not writing behind type); the
    # wash then falls away and the cursive comes up to full strength below.
    mask = Image.new("L", (1, h))
    for y in range(h):
        f = y / float(h)
        if f < 0.34:
            a = 250 - int(28 * (f / 0.34) ** 2)          # 250 -> ~222: near-clean paper
        elif f < 0.58:
            a = int(222 * (1 - (f - 0.34) / 0.24) ** 1.25)  # 222 -> 0: the reveal
        elif f < 0.74:
            a = 0                                            # full-strength cursive
        else:
            # Second wash at the foot: the subtitle and author line land here, and
            # tracked caps over dense cursive is the one thing that costs legibility.
            a = int(200 * min(1.0, (f - 0.74) / 0.10) ** 0.9)
        mask.putpixel((0, y), max(0, min(255, a)))
    field = Image.composite(paper, field, mask.resize((w, h)))

    # Soft vignette so the lower corners settle and the eye stays centered. Light
    # touch: a heavy vignette reads as a photo filter, not a book cover.
    vig = Image.new("L", (w, h), 0)
    vig.paste(255, (int(w * 0.04), int(h * 0.04), int(w * 0.96), int(h * 0.97)))
    vig = vig.filter(ImageFilter.GaussianBlur(radius=max(w, h) // 16))
    dark_field = Image.new("RGB", (w, h), tuple(int(c * 0.82) for c in herb))
    field = Image.blend(Image.composite(field, dark_field, vig), field, 0.45)

    field = field.filter(ImageFilter.SMOOTH)

    out.parent.mkdir(parents=True, exist_ok=True)
    field.save(out, "PNG")
    return {"art": str(out), "size_px": [w, h], "source": str(source),
            "palette": {"ink": palette.get("ink"), "cream": palette.get("cream"),
                        "herbarium": palette.get("herbarium")},
            "baked_text": False}


def _strip_html(s: str) -> str:
    import re as _re
    s = _re.sub(r"</p>\s*<p>", "\n\n", s)
    s = _re.sub(r"<[^>]+>", "", s)
    return s.replace("&amp;", "&").strip()


def _wrap(draw, text, font, max_w):
    out = []
    for para in text.split("\n\n"):
        words, line = para.split(), ""
        for w in words:
            t = (line + " " + w).strip()
            if draw.textlength(t, font=font) <= max_w:
                line = t
            else:
                out.append(line)
                line = w
        out.append(line)
        out.append("")
    return out


def build_back(cfg, ws: Path, out: Path, w: int, h: int, palette: dict, source: Path) -> dict:
    """Back cover: the same handwriting field, washed almost to paper, carrying the
    book description. Built so the digital PDF stops reusing the front as its back."""
    from PIL import ImageDraw, ImageFont

    ink = hex_rgb(palette.get("ink", "1C2A4A"))
    cream = hex_rgb(palette.get("cream", "F1E9D2"))

    base = build(source, out.with_suffix(".field.png"), w, h, palette)  # reuse the field
    img = Image.open(out.with_suffix(".field.png")).convert("RGB")
    # Wash the whole panel back toward paper: body copy must win over texture.
    img = Image.blend(img, Image.new("RGB", (w, h), cream), 0.72)

    d = ImageDraw.Draw(img)
    fonts = Path(__file__).resolve().parent.parent / "fonts"
    def _f(name, size):
        for cand in (fonts / name, fonts / "library" / name):
            if cand.exists():
                return ImageFont.truetype(str(cand), size)
        return ImageFont.load_default()

    desc = _strip_html((cfg.get("kdp_metadata") or {}).get("description", ""))
    margin = int(w * 0.11)
    top, floor_y = int(h * 0.095), h * 0.815

    # Fit the WHOLE description: shrink until every line clears the rule. A back
    # cover that silently drops its last paragraph is worse than slightly smaller type.
    for pt in range(int(h * 0.0215), int(h * 0.0145), -1):
        body = _f("CormorantGaramond-Light.ttf", pt)
        lines = _wrap(d, desc, body, w - 2 * margin)
        lead = int(body.size * 1.58)
        need = sum(lead if ln else int(body.size * 0.68) for ln in lines)
        if top + need <= floor_y:
            break

    y = top
    for ln in lines:
        d.text((margin, y), ln, font=body, fill=ink)
        y += int(body.size * 1.58) if ln else int(body.size * 0.68)

    rule_y = int(h * 0.845)
    d.line([(margin, rule_y), (w - margin, rule_y)], fill=ink, width=max(1, w // 900))
    auth = _f("CormorantGaramond-Bold.ttf", int(h * 0.021))
    tag = cfg.get("author", "")
    tw = d.textlength(tag, font=auth)
    d.text(((w - tw) / 2, rule_y + int(h * 0.022)), tag, font=auth, fill=ink)

    out.parent.mkdir(parents=True, exist_ok=True)
    img.convert("RGB").save(out, "JPEG", quality=94)
    try:
        out.with_suffix(".field.png").unlink()
    except OSError:
        pass
    return {"back_cover": str(out), "size_px": [w, h], "lines": len(lines)}


def main() -> int:
    ap = argparse.ArgumentParser(description="Bespoke handwriting cover art (no baked text).")
    ap.add_argument("--config", required=True)
    ap.add_argument("--source", help="Handwriting scan to build from.")
    ap.add_argument("--out", help="Output PNG (default cover_art/<slug>_src.png).")
    ap.add_argument("--size", default="2000x3200", help="WxH pixels (default 2000x3200, 1.6:1).")
    ap.add_argument("--back", action="store_true",
                    help="Build the BACK cover (description panel) instead of the front art.")
    a = ap.parse_args()

    cfgp = Path(a.config).resolve()
    cfg = json.loads(cfgp.read_text(encoding="utf-8"))
    ws = cfgp.parent
    slug = cfg.get("slug", "book")
    palette = ((cfg.get("cover") or {}).get("palette") or {})

    src = Path(a.source) if a.source else ws / "images" / "figures" / "handwriting" / "FN11_p003.png"
    if not src.is_absolute():
        src = (ws / src).resolve()
    if not src.exists():
        print(json.dumps({"error": f"source scan not found: {src}"}, indent=2))
        return 1

    w, h = (int(x) for x in a.size.lower().split("x"))

    if a.back:
        out = Path(a.out) if a.out else ws / "outputs" / "kdp_paperback" / f"{slug}_back.jpg"
        if not out.is_absolute():
            out = (ws / out).resolve()
        print(json.dumps(build_back(cfg, ws, out, w, h, palette, src), indent=2))
        return 0

    out = Path(a.out) if a.out else ws / "cover_art" / f"{slug}_src.png"
    if not out.is_absolute():
        out = (ws / out).resolve()

    print(json.dumps(build(src, out, w, h, palette), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
