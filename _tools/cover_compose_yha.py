#!/usr/bin/env python3
"""cover_compose_yha.py - bespoke type-led cover compositor for *Your Hermes Agent*.

Series-matched to Book 1's cover_compose_ahss.py (same navy field, accent bar,
Georgia serif, tracked sans credits, pen-stroke-on-a-signing-line motif) so a
reader holding both books sees one shelf. Book 2 adds the OWNED LOOP: a closed
ink loop returning to its own origin, drawn beneath the signing line, which is
the second refrain made visual.

Covers every profile Book 2 ships: kindle (1600x2560 KDP ideal), digital,
kdp-pb, kdp-hc, mixam-pb, mixam-hc (3 panel), blurb-pb, blurb-hc. Optional
cover.ebook_logo (2026-07-27): an emblem composited onto EBOOK fronts only
(kindle + digital; print wraps untouched) as tinted ink, alpha from darkness,
so B&W line art reads as cover-native ink. All wrap
geometry comes from preset_lookup, the SAME module verify_build.py recomputes
against, so compositor/verifier drift is impossible. Exact-inch MediaBox via
PyMuPDF (PIL truncates and KDP rejects at 4 decimals).

Usage:
  python cover_compose_yha.py --config CFG --back back_copy.json --pages N \
      --profile kdp-pb --out DIR
"""
import argparse
import json
import math
import os
import sys
from pathlib import Path

import fitz
from PIL import Image, ImageDraw, ImageFont, ImageOps

sys.path.insert(0, str(Path(__file__).resolve().parent))
import preset_lookup

FONTS = r"C:\Windows\Fonts"

# Palette: Book 1's ratified navy set, with one Book 2 accent (the loop ink).
BG = (10, 17, 32)
TEXT = (233, 237, 243)
BODY = (199, 210, 224)
MUTED = (159, 175, 196)
ACCENT = (91, 147, 214)
LOOP = (201, 167, 96)          # the owned loop: warm against the rented cool
BAR = (46, 111, 214)
FAINT = (51, 69, 94)
HAIR = (70, 92, 124)

TRIM_W, TRIM_H = 6.0, 9.0


def font(name, px):
    return ImageFont.truetype(os.path.join(FONTS, name), px)


def wrap_lines(draw, text, fnt, maxw):
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


def tracked_width(draw, text, fnt, track):
    return sum(draw.textlength(c, font=fnt) + track for c in text) - track if text else 0


def draw_tracked(draw, xy, text, fnt, fill, track=0):
    x, y = xy
    for c in text:
        draw.text((x, y), c, font=fnt, fill=fill)
        x += draw.textlength(c, font=fnt) + track


def penstroke_and_loop(draw, x, y, w):
    """Book 1's signing line and pen stroke, with Book 2's closed loop returning
    to its own origin beneath it. The stroke is the signature; the loop is the
    thing that was owned. They share a baseline."""
    draw.line([(x, y), (x + w, y)], fill=HAIR, width=max(2, int(w * 0.006)))
    pts = []
    for i in range(81):
        t = i / 80
        px = x + w * 0.08 + t * (w * 0.84)
        py = y - w * 0.055 * math.sin(t * 6.2) * (1 - t * 0.5) - w * 0.05 * t
        pts.append((px, py))
    draw.line(pts, fill=ACCENT, width=max(3, int(w * 0.009)), joint="curve")
    xf = font("georgia.ttf", int(w * 0.075))
    draw.text((x - int(w * 0.02), y - int(w * 0.085)), "x", font=xf, fill=(96, 118, 148))
    # the owned loop: a closed return, tucked under the signing line so the two
    # read as one mark (the signature, and the thing that was kept)
    cx, cy = x + w * 0.42, y + w * 0.072
    rx, ry = w * 0.26, w * 0.046
    loop = []
    for i in range(97):
        t = i / 96 * 2 * math.pi
        loop.append((cx + rx * math.cos(t), cy + ry * math.sin(t) * (1 + 0.16 * math.cos(t))))
    draw.line(loop + [loop[0]], fill=LOOP, width=max(2, int(w * 0.006)), joint="curve")


def paste_ebook_logo(img, cfg, ws, dpi, tl, tr, tt, trimh):
    """Emblem for EBOOK fronts only (cover.ebook_logo; the kindle and digital
    branches pass logo_ws, print wraps never do). The source's dark pixels
    become ink on the field (alpha = darkness, tinted), so B&W line art reads
    as cover-native ink rather than a pasted white plate. Centered on the TRIM
    width (front and center), sized by width_in."""
    spec = (cfg.get("cover") or {}).get("ebook_logo") or {}
    rel = spec.get("path")
    if not rel:
        return
    p = Path(ws) / rel
    if not p.exists():
        print(f"[cover_yha] ebook_logo missing, skipped: {p}", file=sys.stderr)
        return
    g = Image.open(p).convert("L")
    w_px = max(1, int(float(spec.get("width_in", 1.5)) * dpi))
    h_px = max(1, round(w_px * g.height / g.width))
    g = g.resize((w_px, h_px), Image.LANCZOS)
    ink = spec.get("ink")
    color = tuple(int(ink[i:i + 2], 16) for i in (0, 2, 4)) if ink else BODY
    layer = Image.new("RGBA", g.size, color + (0,))
    layer.putalpha(ImageOps.invert(g))
    img.paste(layer, ((tl + tr) // 2 - w_px // 2,
                      tt + int(float(spec.get("center_y_frac", 0.76)) * trimh) - h_px // 2),
              layer)


def render_front(px_w, px_h, bleed, cfg, logo_ws=None):
    img = Image.new("RGB", (px_w, px_h), BG)
    d = ImageDraw.Draw(img)
    dpi = px_w / (TRIM_W + 2 * bleed) if bleed else px_w / TRIM_W
    tl = int(bleed * dpi); tr = px_w - tl
    tt = int(bleed * dpi); tb = px_h - tt
    trimw, trimh = tr - tl, tb - tt
    safe = int(0.45 * dpi)

    barx = tl + int(0.34 * dpi)
    d.rectangle([barx, tt + safe, barx + int(0.055 * dpi), tb - safe], fill=BAR)
    lx = barx + int(0.34 * dpi)
    maxw = trimw - (lx - tl) - safe

    # eyebrow, shrunk to fit the measure (tracking makes it wide)
    eb_track = int(0.030 * dpi)
    eyebrow = "A SMALL BUSINESS OWNER'S GUIDE"
    eb_px = int(0.128 * dpi)
    while eb_px > int(0.07 * dpi):
        eb = font("consolab.ttf", eb_px)
        if tracked_width(d, eyebrow, eb, eb_track) <= maxw:
            break
        eb_px -= 2
    draw_tracked(d, (lx, tt + int(1.30 * dpi)), eyebrow, eb, ACCENT, track=eb_track)

    # title: shrink-to-fit the longest line (the playbook's clipped-subtitle lesson,
    # applied to every line rather than only the subtitle)
    title_lines = ["Your Hermes", "Agent"]
    t_px = int(0.82 * dpi)
    while t_px > int(0.30 * dpi):
        tf = font("georgiab.ttf", t_px)
        if max(d.textlength(l, font=tf) for l in title_lines) <= maxw:
            break
        t_px -= 4
    ty = tt + int(1.80 * dpi)
    for line in title_lines:
        d.text((lx - int(0.02 * dpi), ty), line, font=tf, fill=TEXT)
        ty += int(t_px * 1.17)

    # subtitle: shrink-to-fit too, then wrap
    s_px = int(0.235 * dpi)
    while s_px > int(0.13 * dpi):
        sf = font("georgiai.ttf", s_px)
        sub = "Build an AI coworker you can see, check, undo, and own."
        if len(wrap_lines(d, sub, sf, maxw)) <= 2:
            break
        s_px -= 3
    ty += int(0.14 * dpi)
    for line in wrap_lines(d, sub, sf, maxw):
        d.text((lx, ty), line, font=sf, fill=MUTED)
        ty += int(s_px * 1.40)

    # Emblem-led ebook front (2026-07-27, author's direction): when the emblem
    # is active the signing motif comes OFF the front, the emblem takes the
    # center at full prominence, and the small lines step up a size for 6x9
    # reading distance. Print wraps (no logo_ws) keep the classic type-led
    # front, motif included, byte-identical.
    emblem = ((cfg.get("cover") or {}).get("ebook_logo") or {}) if logo_ws is not None else {}
    emblem_on = bool(emblem.get("path"))
    if emblem_on:
        paste_ebook_logo(img, cfg, logo_ws, dpi, tl, tr, tt, trimh)
    else:
        penstroke_and_loop(d, lx, tt + int(trimh * 0.60), int(trimw * 0.52))

    sr = font("consola.ttf", int((0.150 if emblem_on else 0.112) * dpi))
    draw_tracked(d, (lx, tb - safe - int((0.55 if emblem_on else 0.52) * dpi)),
                 "A COMPANION TO  A HUMAN STILL SIGNS", sr, (124, 141, 166),
                 track=int(0.032 * dpi))

    cf = font("consola.ttf", int((0.165 if emblem_on else 0.135) * dpi))
    draw_tracked(d, (lx, tb - safe - int(0.2 * dpi)), "BO CHEN", cf, MUTED,
                 track=int(0.05 * dpi))
    pub = "ACCESS INTELLECT"
    pw = tracked_width(d, pub, cf, int(0.05 * dpi))
    draw_tracked(d, (tr - safe - pw, tb - safe - int(0.2 * dpi)), pub, cf,
                 (124, 141, 166), track=int(0.05 * dpi))
    return img


def para(d, x, y, text, fnt, fill, maxw, leading):
    lh = int(fnt.size * leading)
    for line in wrap_lines(d, text, fnt, maxw):
        d.text((x, y), line, font=fnt, fill=fill)
        y += lh
    return y


def para_around(d, x, y, text, fnt, fill, maxw, leading, kx, etop, ebot, egap):
    lh = int(fnt.size * leading)

    def linew(yy):
        if kx is not None and (yy + lh > etop) and (yy < ebot):
            return (kx - egap) - x
        return maxw
    words, i = text.split(), 0
    while i < len(words):
        w = linew(y)
        cur = words[i]; i += 1
        while i < len(words) and d.textlength(cur + " " + words[i], font=fnt) <= w:
            cur += " " + words[i]; i += 1
        d.text((x, y), cur, font=fnt, fill=fill)
        y += lh
    return y


def render_back(px_w, px_h, bleed, cfg, back, keepout=False):
    img = Image.new("RGB", (px_w, px_h), BG)
    d = ImageDraw.Draw(img)
    dpi = px_w / (TRIM_W + 2 * bleed) if bleed else px_w / TRIM_W
    tl = int(bleed * dpi); tr = px_w - tl
    tt = int(bleed * dpi); tb = px_h - tt
    trimw = tr - tl
    d.line([(tr - int(0.06 * dpi), tt + int(0.4 * dpi)),
            (tr - int(0.06 * dpi), tb - int(0.4 * dpi))], fill=(37, 56, 84), width=3)
    LM = tl + int(0.6 * dpi)
    RM = int(0.6 * dpi)
    maxw = trimw - (LM - tl) - RM

    if keepout:
        kw, kh = int(2.0 * dpi), int(1.2 * dpi)
        kx = tr - int(0.25 * dpi) - kw
        ky = tb - int(0.25 * dpi) - kh
        excl_top, excl_bot, excl_gap = ky - int(0.12 * dpi), ky + kh, int(0.2 * dpi)
    else:
        kx = excl_top = excl_bot = excl_gap = None

    y = tt + int(0.62 * dpi)
    hf = font("georgiab.ttf", int(0.275 * dpi))
    for line in back["hook"]:
        d.text((LM, y), line, font=hf, fill=TEXT)
        y += int(0.34 * dpi)
    y += int(0.14 * dpi)

    bf = font("georgia.ttf", int(0.152 * dpi))
    y = para(d, LM, y, back["body"], bf, BODY, maxw, 1.34)
    y += int(0.10 * dpi)

    penstroke_and_loop(d, LM, y + int(0.14 * dpi), int(1.85 * dpi))
    y += int(0.44 * dpi)

    itf = font("georgiai.ttf", int(0.152 * dpi))
    y = para(d, LM, y, back["teaser_lead"], itf, BODY, maxw, 1.34)
    y += int(0.05 * dpi)
    rf = font("georgiab.ttf", int(0.235 * dpi))
    for line in back["refrain"]:
        d.text((LM, y), line, font=rf, fill=TEXT)
        y += int(0.30 * dpi)
    y += int(0.10 * dpi)
    y = para(d, LM, y, back["teaser_body"], bf, BODY, maxw, 1.34)
    y += int(0.10 * dpi)
    y = para(d, LM, y, back["honesty"], itf, MUTED, maxw, 1.34)
    y += int(0.09 * dpi)
    d.line([(LM, y), (tr - RM, y)], fill=FAINT, width=2)
    y += int(0.14 * dpi)
    biof = font("georgia.ttf", int(0.138 * dpi))
    y = para_around(d, LM, y, back["bio"], biof, (174, 188, 207), maxw, 1.34,
                    kx, excl_top, excl_bot, excl_gap)
    wf = font("consola.ttf", int(0.128 * dpi))
    draw_tracked(d, (LM, tb - int(0.55 * dpi)), "ACCESS INTELLECT", wf,
                 (124, 141, 166), track=int(0.05 * dpi))
    return img


def render_spine(px_long, px_thick, inset=0.09):
    img = Image.new("RGB", (px_long, px_thick), BG)
    d = ImageDraw.Draw(img)
    m = max(int(px_long * inset), int(px_long * 0.09))
    tf = font("georgiab.ttf", int(px_thick * 0.30))
    d.text((m, (px_thick - tf.size) / 2 - int(px_thick * 0.02)),
           "Your Hermes Agent", font=tf, fill=TEXT)
    af = font("consola.ttf", int(px_thick * 0.15))
    au = "B O   C H E N"
    aw = d.textlength(au, font=af)
    d.text((px_long - m - aw, (px_thick - af.size) / 2), au, font=af, fill=MUTED)
    return img.rotate(-90, expand=True)


def img_to_pdf(img, out_pdf, w_in, h_in):
    tmp = str(Path(out_pdf).with_suffix(".embed.png"))
    img.save(tmp)
    doc = fitz.open()
    page = doc.new_page(width=w_in * 72, height=h_in * 72)
    page.insert_image(fitz.Rect(0, 0, w_in * 72, h_in * 72), filename=tmp)
    doc.save(out_pdf)
    doc.close()
    os.remove(tmp)


def assemble_wrap(cover_w, cover_h, spine_in, edge_in, dpi, cfg, back, keepout):
    """[edge | back(6) | spine | front(6) | edge] on a full-bleed canvas."""
    vy = int(round((cover_h - TRIM_H) / 2 * dpi))
    fw, fh = int(TRIM_W * dpi), int(TRIM_H * dpi)
    front = render_front(fw, fh, 0, cfg)
    backi = render_back(fw, fh, 0, cfg, back, keepout=keepout)
    spine = render_spine(int(TRIM_H * dpi), max(1, int(round(spine_in * dpi))))
    canvas = Image.new("RGB", (int(round(cover_w * dpi)), int(round(cover_h * dpi))), BG)
    xb = int(round(edge_in * dpi))
    canvas.paste(backi, (xb, vy))
    canvas.paste(spine, (xb + fw, vy))
    canvas.paste(front, (xb + fw + int(round(spine_in * dpi)), vy))
    return canvas


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    ap.add_argument("--back", required=True)
    ap.add_argument("--pages", type=int, required=True)
    ap.add_argument("--profile", required=True, choices=[
        "kindle", "digital", "kdp-pb", "kdp-hc",
        "mixam-pb", "mixam-hc", "blurb-pb", "blurb-hc"])
    ap.add_argument("--dpi", type=int, default=300)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()

    cfg = json.load(open(a.config, encoding="utf-8"))
    back = json.load(open(a.back, encoding="utf-8"))
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    dpi = a.dpi
    paper = cfg.get("paper", "white")
    sp = cfg.get("spine", {})
    meta = {"pages": a.pages, "profile": a.profile, "dpi": dpi, "book": cfg["title"]}

    ws = Path(a.config).resolve().parent
    ebook_logo = ((cfg.get("cover") or {}).get("ebook_logo") or {}).get("path")

    if a.profile == "kindle":
        render_front(1600, 2560, 0, cfg, logo_ws=ws).save(str(out / "cover_kindle.jpg"), quality=93)
        meta.update({"px": [1600, 2560], "ratio": round(2560 / 1600, 4),
                     "files": ["cover_kindle.jpg"]})
        if ebook_logo:
            meta["ebook_logo"] = ebook_logo

    elif a.profile == "digital":
        fw, fh = int(TRIM_W * dpi), int(TRIM_H * dpi)
        img_to_pdf(render_front(fw, fh, 0, cfg, logo_ws=ws), str(out / "front_digital.pdf"), TRIM_W, TRIM_H)
        img_to_pdf(render_back(fw, fh, 0, cfg, back, keepout=False),
                   str(out / "back_digital.pdf"), TRIM_W, TRIM_H)
        meta["files"] = ["front_digital.pdf", "back_digital.pdf"]
        if ebook_logo:
            meta["ebook_logo"] = ebook_logo

    elif a.profile == "kdp-pb":
        d = preset_lookup.kdp_paperback_wrap_dims(TRIM_W, TRIM_H, a.pages, paper)
        canvas = assemble_wrap(d["cover_w"], d["cover_h"], d["spine"], d["bleed_in"],
                               dpi, cfg, back, keepout=True)
        img_to_pdf(canvas, str(out / "cover_wrap.pdf"), d["cover_w"], d["cover_h"])
        canvas.convert("RGB").save(str(out / "cover_wrap.jpg"), quality=90)
        meta.update({"spine_in": d["spine"], "wrap_w_in": d["cover_w"],
                     "wrap_h_in": d["cover_h"], "bleed_in": d["bleed_in"],
                     "files": ["cover_wrap.pdf", "cover_wrap.jpg"]})

    elif a.profile == "kdp-hc":
        d = preset_lookup.kdp_hardcover_wrap_dims(TRIM_W, TRIM_H, a.pages)
        canvas = assemble_wrap(d["cover_w"], d["cover_h"], d["spine"], d["turn_in_in"],
                               dpi, cfg, back, keepout=True)
        img_to_pdf(canvas, str(out / "cover_wrap_hardcover.pdf"), d["cover_w"], d["cover_h"])
        canvas.convert("RGB").save(str(out / "cover_wrap_hardcover.jpg"), quality=90)
        meta.update({"spine_in": d["spine"], "wrap_w_in": d["cover_w"],
                     "wrap_h_in": d["cover_h"], "turn_in_in": d["turn_in_in"],
                     "files": ["cover_wrap_hardcover.pdf", "cover_wrap_hardcover.jpg"]})

    elif a.profile == "mixam-pb":
        s = preset_lookup.mixam_paperback_spine(a.pages, paper)
        d = preset_lookup.mixam_paperback_wrap_dims(TRIM_W, TRIM_H, s)
        canvas = assemble_wrap(d["cover_w"], d["cover_h"], d["spine"], d["bleed_in"],
                               dpi, cfg, back, keepout=False)
        img_to_pdf(canvas, str(out / "cover_wrap.pdf"), d["cover_w"], d["cover_h"])
        meta.update({"spine_in": d["spine"], "wrap_w_in": d["cover_w"],
                     "wrap_h_in": d["cover_h"], "bleed_in": d["bleed_in"],
                     "files": ["cover_wrap.pdf"]})

    elif a.profile == "mixam-hc":
        bleed = sp.get("mixam_bleed_in", 0.80)
        pw, ph = TRIM_W + 2 * bleed, TRIM_H + 2 * bleed
        fw, fh = int(pw * dpi), int(ph * dpi)
        img_to_pdf(render_front(fw, fh, bleed, cfg), str(out / "front_cover.pdf"), pw, ph)
        img_to_pdf(render_back(fw, fh, bleed, cfg, back, keepout=False),
                   str(out / "back_cover.pdf"), pw, ph)
        sw = round(a.pages * 0.002252 + sp.get("mixam_board_add", 0.110), 4)
        img_to_pdf(render_spine(int(ph * dpi), int(sw * dpi), inset=bleed / ph),
                   str(out / "spine.pdf"), sw, ph)
        meta.update({"spine_in": sw, "panel_w_in": round(pw, 4), "panel_h_in": round(ph, 4),
                     "bleed": bleed,
                     "board_add_note": "mixam_board_add is non-constant; confirm on Mixam's calculator",
                     "files": ["front_cover.pdf", "back_cover.pdf", "spine.pdf"]})

    elif a.profile == "blurb-pb":
        bp = preset_lookup.blurb_paper_from_config(cfg)
        d = preset_lookup.softcover_dims("6x9", bp, a.pages)
        canvas = assemble_wrap(d["cover_w"], d["cover_h"], d["spine"], d["bleed_in"],
                               dpi, cfg, back, keepout=False)
        img_to_pdf(canvas, str(out / "cover_wrap_blurb.pdf"), d["cover_w"], d["cover_h"])
        meta.update({"spine_in": d["spine"], "wrap_w_in": d["cover_w"],
                     "wrap_h_in": d["cover_h"], "trim_w": d["trim_w"], "trim_h": d["trim_h"],
                     "files": ["cover_wrap_blurb.pdf"]})

    elif a.profile == "blurb-hc":
        bp = preset_lookup.blurb_paper_from_config(cfg)
        d = preset_lookup.imagewrap_dims("6x9", bp, a.pages)
        edge = round((d["cover_w"] - 2 * TRIM_W - d["spine"]) / 2, 4)
        canvas = assemble_wrap(d["cover_w"], d["cover_h"], d["spine"], max(edge, 0),
                               dpi, cfg, back, keepout=False)
        img_to_pdf(canvas, str(out / "cover_wrap_blurb_imagewrap.pdf"), d["cover_w"], d["cover_h"])
        meta.update({"spine_in": d["spine"], "wrap_w_in": d["cover_w"],
                     "wrap_h_in": d["cover_h"], "edge_in": edge,
                     "files": ["cover_wrap_blurb_imagewrap.pdf"]})

    json.dump(meta, open(out / f"cover_meta_{a.profile}.json", "w"), indent=2)
    print(json.dumps(meta))


if __name__ == "__main__":
    main()
