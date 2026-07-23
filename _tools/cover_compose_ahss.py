#!/usr/bin/env python3
"""
cover_compose_ahss.py - bespoke cover compositor for *A Human Still Signs*.

Renders the operator-approved type-led design (deep navy field, Georgia serif,
steel-blue accents, pen-stroke-on-a-signing-line motif) as front / back / spine
panels, then composes the per-service artifacts with EXACT-inch MediaBox PDFs
(PyMuPDF, never PIL truncation). One renderer for all three panels => the wrap
is guaranteed self-consistent (the reason this is not the house composite_cover).

Profiles:
  digital : front + back as 6x9 single-page PDFs (no bleed, no barcode zone)
  kindle  : front as RGB JPG (ebook)
  mixam   : front_cover.pdf / back_cover.pdf / spine.pdf (3-panel, bleed)
  kdp     : cover_wrap_hardcover.pdf (one-piece: back | spine | front, wrap bleed)

Spine (hardcover, white paper): pages * per_page + board_add. Mixam board add is
NOT constant across their calculator; the Mixam number is FLAGGED for operator
confirmation. KDP hardcover uses the kit's kdp_hardcover_board_add.

Text content (title/subtitle/author/publisher/back copy/bio) is passed in via
--config (book_config.json) + the back-copy file; this module only sets type.
"""
import argparse
import json
import math
import os
from pathlib import Path

import fitz  # PyMuPDF
from PIL import Image, ImageDraw, ImageFont

FONTS = r"C:\Windows\Fonts"
LANG = "en"           # set to "zh" via --lang; switches serif text to the CJK face
CJK_PATH = None       # resolved in main() from <workspace>/cover_art/fonts/NotoSerifCJK-Regular.ttc
CJK_INDEX = 2         # Noto Serif CJK SC face (0=JP 1=KR 2=SC 3=TC 4=HK)

# ---- approved palette (from the operator-ratified back-cover mock) ----
BG = (10, 17, 32)
TEXT = (233, 237, 243)
BODY = (199, 210, 224)
MUTED = (159, 175, 196)
ACCENT = (91, 147, 214)
BAR = (46, 111, 214)
FAINT = (51, 69, 94)
HAIR = (70, 92, 124)


def _has_cjk(s):
    return any("㐀" <= c <= "鿿" or "＀" <= c <= "￯" for c in s)


# Vietnamese: Windows Georgia lacks 7 precomposed VN codepoints (o-horn, u-horn,
# and stacked-tone vowels) and Pillow does NOT font-fallback the way Word does,
# so Georgia text tofus on the cover. Times New Roman covers the full VN set, so
# the vi serif runs use Times (same serif register). Consolas carries the VN
# chars it needs (eyebrow/credits), so the sans runs are left untouched.
VI_SERIF = {"georgia.ttf": "times.ttf", "georgiab.ttf": "timesbd.ttf",
            "georgiai.ttf": "timesi.ttf"}


def font(name, px):
    # zh mode: every run uses Noto Serif CJK SC (it also carries clean Latin, so
    # BO CHEN / ACCESS INTELLECT still render well).
    if LANG == "zh" and CJK_PATH:
        return ImageFont.truetype(CJK_PATH, index=CJK_INDEX, size=px)
    if LANG == "vi":
        name = VI_SERIF.get(name, name)
    return ImageFont.truetype(os.path.join(FONTS, name), px)


def wrap_lines(draw, text, fnt, maxw):
    if LANG == "zh" or _has_cjk(text):
        lines, cur = [], ""
        for ch in text:
            if ch == "\n":
                lines.append(cur); cur = ""; continue
            if not cur or draw.textlength(cur + ch, font=fnt) <= maxw:
                cur += ch
            else:
                lines.append(cur); cur = ch
        if cur:
            lines.append(cur)
        return lines
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if draw.textlength(t, font=fnt) <= maxw:
            cur = t
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def penstroke(draw, x, y, w, color=ACCENT, base=HAIR):
    """The signing-line motif: an 'x', a baseline, a confident pen squiggle."""
    draw.line([(x, y), (x + w, y)], fill=base, width=max(2, int(w * 0.006)))
    pts = []
    for i in range(81):
        t = i / 80
        px = x + w * 0.08 + t * (w * 0.84)
        py = y - w * 0.055 * math.sin(t * 6.2) * (1 - t * 0.5) - w * 0.05 * t
        pts.append((px, py))
    draw.line(pts, fill=color, width=max(3, int(w * 0.009)), joint="curve")
    xf = font("georgia.ttf", int(w * 0.075))
    draw.text((x - int(w * 0.02), y - int(w * 0.085)), "x", font=xf, fill=(96, 118, 148))


def render_front(px_w, px_h, bleed, cfg):
    """Deep navy field, left accent bar, eyebrow, title, subtitle, motif, credits."""
    img = Image.new("RGB", (px_w, px_h), BG)
    d = ImageDraw.Draw(img)
    dpi = px_w / (6 + 2 * bleed) if bleed else px_w / 6.0
    tl = int(bleed * dpi)                       # trim-left in px
    tr = px_w - tl
    tt = int(bleed * dpi)
    tb = px_h - tt
    trimw = tr - tl
    trimh = tb - tt
    safe = int(0.45 * dpi)

    # left accent bar (inside trim)
    barx = tl + int(0.34 * dpi)
    d.rectangle([barx, tt + safe, barx + int(0.055 * dpi), tb - safe], fill=BAR)

    lx = barx + int(0.34 * dpi)
    if LANG == "zh":
        eyebrow, title_lines = "得州企业主指南", [cfg.get("title", "仍由人签字")]
        sub = "让人工智能为你所用，而不赌上整个生意"
        eb_track, t_px, t_gap, s_px, s_gap = int(0.03 * dpi), 0.80, 1.02, 0.24, 0.36
    elif LANG == "es":
        eyebrow, title_lines = "GUÍA PARA EL DUEÑO TEJANO", ["Un humano", "todavía firma"]
        sub = "Poner la IA a trabajar sin arriesgar el negocio"
        eb_track, t_px, t_gap, s_px, s_gap = int(0.045 * dpi), 0.74, 0.80, 0.25, 0.34
    elif LANG == "vi":
        eyebrow, title_lines = "CẨM NANG CHO CHỦ DOANH NGHIỆP TEXAS", ["Con Người", "Vẫn Ký Tên"]
        sub = "Đưa AI vào làm việc mà không đánh cược cả cơ nghiệp"
        eb_track, t_px, t_gap, s_px, s_gap = int(0.024 * dpi), 0.74, 0.80, 0.24, 0.33
    else:
        eyebrow, title_lines = "A TEXAS OWNER'S GUIDE", ["A Human", "Still Signs"]
        sub = "Putting AI to work without betting the business."
        eb_track, t_px, t_gap, s_px, s_gap = int(0.045 * dpi), 0.86, 0.92, 0.27, 0.36
    # eyebrow
    eb = font("consolab.ttf", int(0.145 * dpi))
    draw_tracked(d, (lx, tt + int(1.45 * dpi)), eyebrow, eb, ACCENT, track=eb_track)
    # title
    tf = font("georgiab.ttf", int(t_px * dpi))
    ty = tt + int(1.95 * dpi)
    for line in title_lines:
        d.text((lx - int(0.02 * dpi), ty), line, font=tf, fill=TEXT)
        ty += int(t_gap * dpi)
    # subtitle
    sf = font("georgiai.ttf", int(s_px * dpi))
    ty += int(0.15 * dpi)
    for line in wrap_lines(d, sub, sf, trimw - (lx - tl) - safe):
        d.text((lx, ty), line, font=sf, fill=MUTED)
        ty += int(s_gap * dpi)
    # motif lower third
    penstroke(d, lx, tt + int(trimh * 0.72), int(trimw * 0.52))
    # credits row
    cf = font("consola.ttf", int(0.135 * dpi))
    draw_tracked(d, (lx, tb - safe - int(0.2 * dpi)), "BO CHEN", cf, MUTED,
                 track=int(0.05 * dpi))
    pub = "ACCESS INTELLECT"
    pw = tracked_width(d, pub, cf, int(0.05 * dpi))
    draw_tracked(d, (tr - safe - pw, tb - safe - int(0.2 * dpi)), pub, cf, (124, 141, 166),
                 track=int(0.05 * dpi))
    # free-appendix call-out sticker (English cover only)
    if LANG == "en":
        draw_free_badge(d, tr - safe, tt + safe, dpi)
    return img


def tracked_width(draw, text, fnt, track):
    return sum(draw.textlength(c, font=fnt) + track for c in text) - track if text else 0


def draw_tracked(draw, xy, text, fnt, fill, track=0):
    x, y = xy
    for c in text:
        draw.text((x, y), c, font=fnt, fill=fill)
        x += draw.textlength(c, font=fnt) + track


BADGE_FILL = (205, 68, 86)      # rosy red (S3, operator-picked 2026-07-19)
BADGE_H_IN = 0.46               # banner height
BADGE_TOP_IN = 0.45             # banner top, measured from trim top (== safe)


def draw_free_badge(d, right_x, top_y, dpi):
    """Free-appendix call-out: single-line rosy-red banner with an angled left
    end, running off the right edge of the canvas (bleeds off on print
    profiles). right_x arrives as (trim_right - safe); the band runs to the
    canvas edge while the type keeps 0.30in clear of the trim edge."""
    INK = (0, 0, 0)
    safe = int(0.45 * dpi)
    tr = right_x + safe                    # trim-right edge (any bleed)
    px_w = d.im.size[0]                    # canvas right edge
    h = int(BADGE_H_IN * dpi)
    y0, y1 = top_y, top_y + h
    eb_f = font("consolab.ttf", int(0.105 * dpi))
    tw = int(0.03 * dpi)
    ti_f = font("georgiab.ttf", int(0.175 * dpi))
    eb, ti = "FREE INSIDE", "The HyperCell Blueprint"
    ebw = int(tracked_width(d, eb, eb_f, tw))
    tiw = int(d.textlength(ti, font=ti_f))
    pad_l, gap = int(0.22 * dpi), int(0.20 * dpi)
    pad_r = (px_w - tr) + int(0.30 * dpi)
    slant = int(h * 0.55)
    x0 = px_w - (pad_l + slant + ebw + gap + tiw + pad_r)
    d.polygon([(x0 + slant, y0), (px_w, y0), (px_w, y1), (x0, y1)], fill=BADGE_FILL)
    tx = x0 + pad_l + slant
    draw_tracked(d, (tx, y0 + (h - eb_f.size) // 2 + int(0.01 * dpi)), eb, eb_f,
                 INK, track=tw)
    d.text((tx + ebw + gap, y0 + (h - ti_f.size) // 2 - int(ti_f.size * 0.16)),
           ti, font=ti_f, fill=INK)


def render_back(px_w, px_h, bleed, cfg, back, keepout=False):
    img = Image.new("RGB", (px_w, px_h), BG)
    d = ImageDraw.Draw(img)
    dpi = px_w / (6 + 2 * bleed) if bleed else px_w / 6.0
    tl = int(bleed * dpi); tr = px_w - tl; tt = int(bleed * dpi); tb = px_h - tt
    trimw = tr - tl
    d.line([(tr - int(0.06 * dpi), tt + int(0.4 * dpi)),
            (tr - int(0.06 * dpi), tb - int(0.4 * dpi))], fill=(37, 56, 84), width=3)
    LM = tl + int(0.6 * dpi)
    RM = int(0.6 * dpi)
    maxw = trimw - (LM - tl) - RM

    # KDP barcode keep-out: GEOMETRY ONLY, never drawn. 2.0 x 1.2in, 0.25in from
    # the bottom-right trim corner.
    if keepout:
        kw, kh = int(2.0 * dpi), int(1.2 * dpi)
        kx = tr - int(0.25 * dpi) - kw
        ky = tb - int(0.25 * dpi) - kh
        excl_top, excl_bot, excl_gap = ky - int(0.12 * dpi), ky + kh, int(0.2 * dpi)
    else:
        kx = excl_top = excl_bot = excl_gap = None

    y = tt + int(0.7 * dpi)
    # hook
    hf = font("georgiab.ttf", int(0.29 * dpi))
    for line in back["hook"]:
        d.text((LM, y), line, font=hf, fill=TEXT)
        y += int(0.36 * dpi)
    y += int(0.16 * dpi)
    # body
    bf = font("georgia.ttf", int(0.158 * dpi))
    y = para(d, LM, y, back["body"], bf, BODY, maxw, dpi, 1.36)
    y += int(0.12 * dpi)
    # motif
    penstroke(d, LM, y + int(0.16 * dpi), int(2.0 * dpi))
    y += int(0.34 * dpi)
    # teaser lead-in (italic) + refrain (bold, large)
    itf = font("georgiai.ttf", int(0.158 * dpi))
    y = para(d, LM, y, back["teaser_lead"], itf, BODY, maxw, dpi, 1.36)
    y += int(0.06 * dpi)
    rf = font("georgiab.ttf", int(0.26 * dpi))
    d.text((LM, y), back["refrain"], font=rf, fill=TEXT)
    y += int(0.4 * dpi)
    y = para(d, LM, y, back["teaser_body"], bf, BODY, maxw, dpi, 1.36)
    y += int(0.12 * dpi)
    # honesty line (italic, muted)
    y = para(d, LM, y, back["honesty"], itf, MUTED, maxw, dpi, 1.36)
    y += int(0.1 * dpi)
    d.line([(LM, y), (tr - RM, y)], fill=FAINT, width=2)
    y += int(0.16 * dpi)
    # bio — wraps around the (invisible) keep-out zone like a jigsaw
    biof = font("georgia.ttf", int(0.143 * dpi))
    y = para_around(d, LM, y, back["bio"], biof, (174, 188, 207), maxw, dpi, 1.36,
                    kx, excl_top, excl_bot, excl_gap)
    # wordmark bottom-left
    wf = font("consola.ttf", int(0.135 * dpi))
    draw_tracked(d, (LM, tb - int(0.55 * dpi)), "ACCESS INTELLECT", wf, (124, 141, 166),
                 track=int(0.05 * dpi))
    return img


def para(d, x, y, text, fnt, fill, maxw, dpi, leading):
    lh = int(fnt.size * leading)
    for line in wrap_lines(d, text, fnt, maxw):
        d.text((x, y), line, font=fnt, fill=fill)
        y += lh
    return y


def para_around(d, x, y, text, fnt, fill, maxw, dpi, leading, kx, etop, ebot, egap):
    lh = int(fnt.size * leading)
    def linew(yy):
        if kx is not None and (yy + lh > etop) and (yy < ebot):
            return (kx - egap) - x
        return maxw
    if LANG == "zh" or _has_cjk(text):
        i, n = 0, len(text)
        while i < n:
            w = linew(y); cur = ""
            while i < n and text[i] != "\n":
                if not cur or d.textlength(cur + text[i], font=fnt) <= w:
                    cur += text[i]; i += 1
                else:
                    break
            if i < n and text[i] == "\n":
                i += 1
            d.text((x, y), cur, font=fnt, fill=fill)
            y += lh
        return y
    words = text.split()
    i = 0
    while i < len(words):
        w = linew(y)
        cur = words[i]; i += 1
        while i < len(words) and d.textlength(cur + " " + words[i], font=fnt) <= w:
            cur += " " + words[i]; i += 1
        d.text((x, y), cur, font=fnt, fill=fill)
        y += lh
    return y


def render_spine(px_w, px_h, cfg, inset=0.09):
    """Horizontal compose then rotate -90. px_w is the LONG dimension (height),
    px_h the spine width. `inset` (fraction of px_w) keeps title+author clear of
    the casebound turn-in at top/bottom of the finished spine."""
    img = Image.new("RGB", (px_w, px_h), BG)
    d = ImageDraw.Draw(img)
    m = max(int(px_w * inset), int(px_w * 0.09))
    tf = font("georgiab.ttf", int(px_h * 0.30))
    title = (cfg.get("title") if (LANG in ("zh", "es", "vi") and cfg) else None) or "A Human Still Signs"
    d.text((m, (px_h - tf.size) / 2 - int(px_h * 0.02)), title, font=tf, fill=TEXT)
    af = font("consola.ttf", int(px_h * 0.15))
    au = "B O   C H E N"
    aw = d.textlength(au, font=af)
    d.text((px_w - m - aw, (px_h - af.size) / 2), au, font=af, fill=MUTED)
    return img.rotate(-90, expand=True)


def img_to_pdf(img, out_pdf, w_in, h_in, dpi):
    """Embed a PIL image into a PDF page with an EXACT-inch MediaBox (fitz)."""
    tmp = str(Path(out_pdf).with_suffix(".embed.png"))
    img.save(tmp)
    doc = fitz.open()
    page = doc.new_page(width=w_in * 72, height=h_in * 72)
    page.insert_image(fitz.Rect(0, 0, w_in * 72, h_in * 72), filename=tmp)
    doc.save(out_pdf)
    doc.close()
    os.remove(tmp)


def spine_width(pages, board_add, per_page=0.002252):
    return round(pages * per_page + board_add, 4)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    ap.add_argument("--back", required=True, help="back-copy JSON")
    ap.add_argument("--pages", type=int, required=True)
    ap.add_argument("--profile", required=True,
                    choices=["digital", "kindle", "mixam", "kdp"])
    ap.add_argument("--dpi", type=int, default=300)
    ap.add_argument("--out", required=True)
    ap.add_argument("--lang", default="en", choices=["en", "zh", "es", "vi"])
    a = ap.parse_args()

    global LANG, CJK_PATH
    LANG = a.lang
    if LANG == "zh":
        cand = Path(a.config).resolve().parent / "cover_art" / "fonts" / "NotoSerifCJK-Regular.ttc"
        if not cand.exists():
            raise SystemExit(f"zh cover needs NotoSerifCJK-Regular.ttc at {cand}")
        CJK_PATH = str(cand)

    cfg = json.load(open(a.config, encoding="utf-8"))
    back = json.load(open(a.back, encoding="utf-8"))
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    dpi = a.dpi
    meta = {"pages": a.pages, "profile": a.profile, "dpi": dpi}

    if a.profile == "digital":
        fw, fh = 6 * dpi, 9 * dpi
        img_to_pdf(render_front(fw, fh, 0, cfg), str(out / "front_digital.pdf"), 6, 9, dpi)
        img_to_pdf(render_back(fw, fh, 0, cfg, back, keepout=False),
                   str(out / "back_digital.pdf"), 6, 9, dpi)
        meta["files"] = ["front_digital.pdf", "back_digital.pdf"]

    elif a.profile == "kindle":
        # KDP ebook IDEAL dims: 2560 h x 1600 w, 1.6:1 (QC 2026-07-23; was
        # 1600x2400 @1.5:1 — accepted by KDP but below the published ideal).
        fw, fh = 1600, 2560
        render_front(fw, fh, 0, cfg).save(str(out / "cover_kindle.jpg"), quality=92)
        meta["files"] = ["cover_kindle.jpg"]

    elif a.profile == "mixam":
        # Mixam casebound 3-panel: 0.80in wrap/turn-in each side (verify_build
        # mixam_bleed_in); front/back = trim + 2*0.80 = 7.6 x 10.6; spine.pdf is
        # EXACTLY spine-width (no L/R bleed) x full panel height.
        bleed = 0.80
        pw, ph = 6 + 2 * bleed, 9 + 2 * bleed
        fw, fh = int(pw * dpi), int(ph * dpi)
        img_to_pdf(render_front(fw, fh, bleed, cfg), str(out / "front_cover.pdf"), pw, ph, dpi)
        img_to_pdf(render_back(fw, fh, bleed, cfg, back, keepout=False),
                   str(out / "back_cover.pdf"), pw, ph, dpi)
        sw = spine_width(a.pages, cfg.get("spine", {}).get("mixam_board_add", 0.110))
        img_to_pdf(render_spine(int(ph * dpi), int(sw * dpi), cfg, inset=bleed / ph),
                   str(out / "spine.pdf"), sw, ph, dpi)
        meta.update({"spine_in": sw, "panel_w_in": round(pw, 4), "panel_h_in": round(ph, 4),
                     "bleed": bleed, "board_add_note":
                     "mixam_board_add=0.110 (kit default); confirm final via Mixam calculator",
                     "files": ["front_cover.pdf", "back_cover.pdf", "spine.pdf"]})

    elif a.profile == "kdp":
        # One-piece casebound wrap. Dims from the SHARED preset (same code path
        # verify_build checks against): [turn | back(6) | spine | front(6) | turn]
        # wide, 10.417 tall, 0.708 turn-in top/bottom/sides.
        import preset_lookup
        d = preset_lookup.kdp_hardcover_wrap_dims(6, 9, a.pages)
        cover_w, cover_h, sw, turn = (d["cover_w"], d["cover_h"], d["spine"],
                                      d["turn_in_in"])
        vy = int(round((cover_h - 9) / 2 * dpi))
        fw, fh = int(6 * dpi), int(9 * dpi)
        front = render_front(fw, fh, 0, cfg)
        backi = render_back(fw, fh, 0, cfg, back, keepout=True)
        spine = render_spine(int(9 * dpi), int(sw * dpi), cfg)
        canvas = Image.new("RGB", (int(round(cover_w * dpi)), int(round(cover_h * dpi))), BG)
        xb = int(round(turn * dpi))
        canvas.paste(backi, (xb, vy))
        canvas.paste(spine, (xb + int(6 * dpi), vy))
        canvas.paste(front, (xb + int(6 * dpi) + int(round(sw * dpi)), vy))
        if LANG == "en":
            # continue the S3 banner across the right turn-in so it wraps the
            # board edge instead of stopping at the panel seam
            fx1 = xb + int(6 * dpi) + int(round(sw * dpi)) + int(6 * dpi)
            by0 = vy + int(BADGE_TOP_IN * dpi)
            ImageDraw.Draw(canvas).rectangle(
                [fx1 - 2, by0, canvas.width, by0 + int(BADGE_H_IN * dpi)],
                fill=BADGE_FILL)
        img_to_pdf(canvas, str(out / "cover_wrap_hardcover.pdf"), cover_w, cover_h, dpi)
        meta.update({"spine_in": sw, "wrap_w_in": cover_w, "wrap_h_in": cover_h,
                     "turn_in_in": turn, "files": ["cover_wrap_hardcover.pdf"]})

    json.dump(meta, open(out / f"cover_meta_{a.profile}.json", "w"), indent=2)
    print(json.dumps(meta))


if __name__ == "__main__":
    main()
