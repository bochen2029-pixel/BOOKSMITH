#!/usr/bin/env python3
r"""
cover_compose_drdj.py — replica-project cover compositor (DRDJ three-volume set).

For REPLICA re-issues the source cover IS the front panel (its typography is the
design — the "no baked text" rule governs generated art only). Online-reading
editions have no back/spine, so those are DERIVED strictly from the book's own
elements: field color sampled from the cover art, the book's own series title /
volume / author / motto, stacked-vertical CJK spine glyphs. Exact-inch MediaBox
via fitz. Spine math: PB pages*0.002252; HC +0.348 board-add, height 10.417
(kit constants, Previewer-confirmed lineage).

USAGE
  python cover_compose_drdj.py --art cover.png --pages 256 --profile kdp-wrap
      --out DIR [--series 人生悟道,渡人渡己] [--volume 投资篇] [--author 金冰]
      [--motto "line1,line2,..."] [--cjk-font path.ttc] [--json]
Profiles: kdp-wrap (paperback) | kdp-hardcover | kindle (1600x2560 front).
"""
from __future__ import annotations
import argparse, json, sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

DPI = 300
PER_PAGE = 0.002252
HC_BOARD = 0.348
HC_TURNIN = 0.708
HC_H = 10.417
PB_BLEED = 0.125
DEFAULT_FONT = Path(r"C:\BOOKSMITH\book_workspace\a_human_still_signs\cover_art\fonts\NotoSerifCJK-Regular.ttc")


def u8():
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


def load_font(path: Path, px: int):
    try:
        return ImageFont.truetype(str(path), px, index=0)
    except Exception:
        return ImageFont.truetype(str(path), px)


def sample_palette(art: Image.Image):
    """Field + text colors sampled from the cover art, polarity-aware:
    dark covers (the CJK trilogy) keep the original dark-field/cream-text
    behavior; LIGHT covers (the English edition's cream) get a light field
    with the cover's own ink color as text."""
    small = art.convert("RGB").resize((64, 64))
    px = list(small.getdata())
    mean_lum = sum(sum(c) for c in px) / (len(px) * 3)
    dark = min(px, key=lambda c: sum(c))
    darks = [c for c in px if sum(c) <= sum(dark) + 120]
    if mean_lum >= 128:
        light = max(px, key=lambda c: sum(c))
        lights = [c for c in px if sum(c) >= sum(light) - 90]
        field = tuple(sum(ch) // len(lights) for ch in zip(*lights))
        text = tuple(sum(ch) // len(darks) for ch in zip(*darks))
    else:
        field = tuple(sum(ch) // len(darks) for ch in zip(*darks))
        text = (244, 238, 224)
    return field, text


def scale_cover(art, w, h):
    """Fill w x h, cropping overflow symmetrically."""
    s = max(w / art.width, h / art.height)
    im = art.resize((round(art.width * s), round(art.height * s)), Image.LANCZOS)
    x = (im.width - w) // 2
    y = (im.height - h) // 2
    return im.crop((x, y, x + w, y + h))


def fit_with_fill(art, w, h, bg):
    """Fit inside w x h, filling bands with bg (replica: never crop the cover)."""
    s = min(w / art.width, h / art.height)
    im = art.resize((round(art.width * s), round(art.height * s)), Image.LANCZOS)
    canvas = Image.new("RGB", (w, h), bg)
    canvas.paste(im, ((w - im.width) // 2, (h - im.height) // 2))
    return canvas


def stack_vertical(d, cx, y0, y1, text, font, fill, gap=0.15):
    """Stacked upright CJK spine text, centered on cx between y0..y1."""
    chars = [c for c in text if not c.isspace()]
    if not chars:
        return
    sizes = [d.textbbox((0, 0), c, font=font) for c in chars]
    hts = [b[3] - b[1] for b in sizes]
    g = int(font.size * gap)
    total = sum(hts) + g * (len(chars) - 1)
    y = y0 + max(0, ((y1 - y0) - total) // 2)
    for c, b, hh in zip(chars, sizes, hts):
        w = b[2] - b[0]
        d.text((cx - w // 2 - b[0], y - b[1]), c, font=font, fill=fill)
        y += hh + g


def latin_spine(d, img, x0, x1, y0, y1, text, font, fill):
    """Western spine: one horizontal line rotated -90 (reads top-to-bottom
    with the book upright), centered in the spine box."""
    if not text.strip():
        return
    probe = ImageDraw.Draw(Image.new("RGB", (8, 8)))
    bb = probe.textbbox((0, 0), text, font=font)
    tw, th = bb[2] - bb[0], bb[3] - bb[1]
    tile = Image.new("RGBA", (tw + 8, th + 8), (0, 0, 0, 0))
    ImageDraw.Draw(tile).text((4 - bb[0], 4 - bb[1]), text, font=font, fill=fill)
    tile = tile.rotate(-90, expand=True)
    cx = (x0 + x1 - tile.width) // 2
    cy = y0 + max(0, ((y1 - y0) - tile.height) // 2)
    img.paste(tile, (cx, cy), tile)


def img_to_pdf(img, out_pdf, w_in, h_in):
    import fitz
    tmp = str(Path(out_pdf).with_suffix(".embed.png"))
    img.save(tmp)
    doc = fitz.open()
    page = doc.new_page(width=w_in * 72, height=h_in * 72)
    page.insert_image(fitz.Rect(0, 0, w_in * 72, h_in * 72), filename=tmp)
    doc.save(str(out_pdf))
    doc.close()
    Path(tmp).unlink()


def draw_back(d, x0, x1, y0, y1, safe, series, volume, author, motto, font_path, text_col, keepout=None, lang="zh", foot="人生悟道 · 渡人渡己 系列"):
    W = x1 - x0
    f_big = load_font(font_path, int(0.42 * DPI))
    f_mid = load_font(font_path, int(0.26 * DPI))
    f_small = load_font(font_path, int(0.14 * DPI))
    y = y0 + safe + int(0.55 * DPI)
    for line in series:
        w = d.textlength(line, font=f_big)
        d.text((x0 + (W - w) // 2, y), line, font=f_big, fill=text_col)
        y += int(0.58 * DPI)
    y += int(0.12 * DPI)
    if lang == "en":
        vol_line = f"{volume} · {author}" if volume else author
    else:
        vol_line = f"{volume} · {author} 著"
    w = d.textlength(vol_line, font=f_mid)
    d.text((x0 + (W - w) // 2, y), vol_line, font=f_mid, fill=text_col)
    y += int(0.85 * DPI)
    for line in motto:
        w = d.textlength(line, font=f_mid)
        d.text((x0 + (W - w) // 2, y), line, font=f_mid, fill=text_col)
        y += int(0.42 * DPI)
    w = d.textlength(foot, font=f_small)
    fy = y1 - safe - int(0.30 * DPI)
    if keepout:
        kx0 = keepout[0]
        d.text((x0 + safe, fy), foot, font=f_small, fill=text_col)  # left, clear of keep-out
    else:
        d.text((x0 + (W - w) // 2, fy), foot, font=f_small, fill=text_col)


def compose(profile, art_path, pages, out_dir, series, volume, author, motto, font_path, as_json,
            lang="zh", foot="人生悟道 · 渡人渡己 系列"):
    art = Image.open(art_path).convert("RGB")
    field, text_col = sample_palette(art)
    out_dir.mkdir(parents=True, exist_ok=True)
    meta = {"profile": profile, "pages": pages, "dpi": DPI, "field_rgb": field}
    if lang == "en":
        spine_title = " ".join([*series, volume]).strip()
    else:
        spine_title = "".join(series) + volume

    if profile == "kindle":
        W, H = 1600, 2560
        img = fit_with_fill(art, W, H, field)
        f = out_dir / "cover_kindle.jpg"
        img.save(f, "JPEG", quality=92)
        meta.update({"size_px": [W, H], "files": [f.name]})
    else:
        hc = profile == "kdp-hardcover"
        spine = round(pages * PER_PAGE + (HC_BOARD if hc else 0.0), 4)
        edge = HC_TURNIN if hc else PB_BLEED
        trim_h = HC_H if hc else 9 + 2 * PB_BLEED
        panel_w = 6 + edge
        W_in = round(2 * panel_w + spine, 4)
        H_in = trim_h
        W, H = round(W_in * DPI), round(H_in * DPI)
        img = Image.new("RGB", (W, H), field)
        d = ImageDraw.Draw(img)
        sp_x0 = round(panel_w * DPI)
        sp_x1 = round((panel_w + spine) * DPI)
        # FRONT panel (right): the source cover, full-bleed into panel incl. edge
        front = scale_cover(art, W - sp_x1, H)
        img.paste(front, (sp_x1, 0))
        # SPINE: stacked CJK (zh) or one rotated line (en Western spine)
        v_safe = int((edge + 0.25) * DPI)
        if lang == "en":
            f_spine = load_font(font_path, int(min(spine * 0.42, 0.30) * DPI))
            latin_spine(d, img, sp_x0, sp_x1, v_safe, H - v_safe,
                        f"{spine_title}  ·  {author}", f_spine, text_col)
        else:
            f_spine = load_font(font_path, int(min(spine * 0.52, 0.34) * DPI))
            stack_vertical(d, (sp_x0 + sp_x1) // 2, v_safe, H - v_safe - int(1.2 * DPI),
                           spine_title, f_spine, text_col)
            f_auth = load_font(font_path, int(min(spine * 0.40, 0.24) * DPI))
            stack_vertical(d, (sp_x0 + sp_x1) // 2, H - v_safe - int(1.1 * DPI),
                           H - v_safe, author, f_auth, text_col)
        # BACK panel (left)
        safe = int((edge + 0.25) * DPI)
        keep = None
        if not hc or hc:  # KDP overlays its barcode on both PB and HC backs
            kx1 = sp_x0 - int((edge + 0.25) * DPI)
            ky1 = H - int((edge + 0.25) * DPI)
            keep = (kx1 - int(2.0 * DPI), ky1 - int(1.2 * DPI), kx1, ky1)
        draw_back(d, 0, sp_x0, 0, H, safe, series, volume, author, motto,
                  font_path, text_col, keepout=keep, lang=lang, foot=foot)
        name = "cover_wrap_hardcover" if hc else "cover_wrap"
        img_to_pdf(img, out_dir / f"{name}.pdf", W_in, H_in)
        img.save(out_dir / f"{name}.jpg", "JPEG", quality=90)
        meta.update({"spine_in": spine, "wrap_w_in": W_in, "wrap_h_in": H_in,
                     "files": [f"{name}.pdf", f"{name}.jpg"],
                     "expected_check": f"{W_in}x{H_in}"})
    (out_dir / f"cover_meta_{profile.replace('-', '_')}.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(meta, ensure_ascii=False, indent=2) if as_json else
          f"{profile}: {meta.get('wrap_w_in', meta.get('size_px'))} spine={meta.get('spine_in')} -> {out_dir}")
    return meta


def main(argv=None):
    u8()
    ap = argparse.ArgumentParser()
    ap.add_argument("--art", required=True)
    ap.add_argument("--pages", type=int, required=True)
    ap.add_argument("--profile", required=True, choices=["kdp-wrap", "kdp-hardcover", "kindle"])
    ap.add_argument("--out", required=True)
    ap.add_argument("--series", default="人生悟道,渡人渡己")
    ap.add_argument("--volume", default="投资篇")
    ap.add_argument("--author", default="金冰")
    ap.add_argument("--motto", default="便宜硬道理,选股如选妻,人性即黄金,时间便是神",
                    help="back-panel lines; split on '|' when present, else ','")
    ap.add_argument("--cjk-font", default=str(DEFAULT_FONT))
    ap.add_argument("--lang", default="zh", choices=["zh", "en"],
                    help="en = rotated Latin spine + no CJK byline suffix")
    ap.add_argument("--foot", default="人生悟道 · 渡人渡己 系列",
                    help="back-panel footer line")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    msep = "|" if "|" in a.motto else ","
    ssep = "|" if "|" in a.series else ","
    compose(a.profile, Path(a.art), a.pages, Path(a.out),
            [s for s in a.series.split(ssep) if s], a.volume, a.author,
            [s for s in a.motto.split(msep) if s], Path(a.cjk_font), a.json,
            lang=a.lang, foot=a.foot)
    return 0


if __name__ == "__main__":
    sys.exit(main())
