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
    """Dominant dark field color + a light text color from the cover art."""
    small = art.convert("RGB").resize((64, 64))
    px = list(small.getdata())
    dark = min(px, key=lambda c: sum(c))
    darks = [c for c in px if sum(c) <= sum(dark) + 120]
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


def draw_back(d, x0, x1, y0, y1, safe, series, volume, author, motto, font_path, text_col, keepout=None):
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
    vol_line = f"{volume} · {author} 著"
    w = d.textlength(vol_line, font=f_mid)
    d.text((x0 + (W - w) // 2, y), vol_line, font=f_mid, fill=text_col)
    y += int(0.85 * DPI)
    for line in motto:
        w = d.textlength(line, font=f_mid)
        d.text((x0 + (W - w) // 2, y), line, font=f_mid, fill=text_col)
        y += int(0.42 * DPI)
    foot = "人生悟道 · 渡人渡己 系列"
    w = d.textlength(foot, font=f_small)
    fy = y1 - safe - int(0.30 * DPI)
    if keepout:
        kx0 = keepout[0]
        d.text((x0 + safe, fy), foot, font=f_small, fill=text_col)  # left, clear of keep-out
    else:
        d.text((x0 + (W - w) // 2, fy), foot, font=f_small, fill=text_col)


def compose(profile, art_path, pages, out_dir, series, volume, author, motto, font_path, as_json):
    art = Image.open(art_path).convert("RGB")
    field, text_col = sample_palette(art)
    out_dir.mkdir(parents=True, exist_ok=True)
    meta = {"profile": profile, "pages": pages, "dpi": DPI, "field_rgb": field}
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
        # SPINE: stacked CJK, safe from head/tail turn-in
        f_spine = load_font(font_path, int(min(spine * 0.52, 0.34) * DPI))
        v_safe = int((edge + 0.25) * DPI)
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
                  font_path, text_col, keepout=keep)
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
    ap.add_argument("--motto", default="便宜硬道理,选股如选妻,人性即黄金,时间便是神")
    ap.add_argument("--cjk-font", default=str(DEFAULT_FONT))
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    compose(a.profile, Path(a.art), a.pages, Path(a.out),
            [s for s in a.series.split(",") if s], a.volume, a.author,
            [s for s in a.motto.split(",") if s], Path(a.cjk_font), a.json)
    return 0


if __name__ == "__main__":
    sys.exit(main())
