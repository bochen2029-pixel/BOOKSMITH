#!/usr/bin/env python3
"""docx_figures.py: the figures of a DOCX in DOCUMENT order, resolved through the drawing relationship
ids, never through the media file numbers (word/media/imageN is insertion order, and in a re-exported
document it mislabels which figure was replaced). For each figure: its media file, pixel size, display
extent, the nearest heading above it, its alt text (docPr descr) and the paragraph that follows it (the
caption candidate). With --match-dir, each figure is matched to the most similar image in a folder of
originals (32x32 grayscale correlation, robust to re-encoding), so a replaced photo shows up as the one
with no good match.

Usage:
  python _tools/docx_figures.py BOOK.docx [--match-dir images/photos] [--extract DIR] [--json]
Exit 0; 2 on usage errors. Needs Pillow for --match-dir and pixel sizes.
"""
import argparse
import io
import json
import os
import re
import sys
import zipfile
import xml.etree.ElementTree as ET

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
WP = "{http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing}"
A = "{http://schemas.openxmlformats.org/drawingml/2006/main}"
R = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}"
PR = "{http://schemas.openxmlformats.org/package/2006/relationships}"
EMU = 914400.0


def para_text(p):
    return "".join((n.text or "") if n.tag == W + "t" else ("\n" if n.tag in (W + "br", W + "cr") else "")
                   for n in p.iter())


def style_names(z):
    names = {}
    try:
        root = ET.fromstring(z.read("word/styles.xml"))
    except KeyError:
        return names
    for s in root.iter(W + "style"):
        n = s.find(W + "name")
        names[s.get(W + "styleId")] = (n.get(W + "val") if n is not None else "") or s.get(W + "styleId")
    return names


def is_heading(p, names):
    ppr = p.find(W + "pPr")
    if ppr is None:
        return False
    ps = ppr.find(W + "pStyle")
    if ps is None:
        return False
    sid = ps.get(W + "val") or ""
    return "heading" in (names.get(sid, sid) or "").lower().replace(" ", "") or sid.lower().startswith("heading")


def thumb(im, n=32):
    from PIL import Image, ImageOps
    im = ImageOps.exif_transpose(im).convert("L").resize((n, n), Image.LANCZOS)
    px = list(im.getdata())
    mean = sum(px) / len(px)
    v = [p - mean for p in px]
    norm = sum(x * x for x in v) ** 0.5 or 1.0
    return [x / norm for x in v]


def corr(a, b):
    return sum(x * y for x, y in zip(a, b))


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("docx")
    ap.add_argument("--match-dir", help="folder of original images to match each figure against")
    ap.add_argument("--extract", help="write each figure's media as fig_NN_<media> into this folder")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    z = zipfile.ZipFile(a.docx)
    rels = {}
    for rel in ET.fromstring(z.read("word/_rels/document.xml.rels")).iter(PR + "Relationship"):
        rels[rel.get("Id")] = rel.get("Target")
    names = style_names(z)
    body = ET.fromstring(z.read("word/document.xml")).find(W + "body")
    paras = [p for p in body if p.tag == W + "p"]
    figs = []
    last_heading = ""
    for i, p in enumerate(paras):
        if is_heading(p, names):
            t = para_text(p).strip()
            if t:
                last_heading = t
        blips = [b.get(R + "embed") for b in p.iter(A + "blip") if b.get(R + "embed")]
        if not blips:
            continue
        descr = [d.get("descr", "") for d in p.iter(WP + "docPr")]
        ext = [(int(e.get("cx")), int(e.get("cy"))) for e in p.iter(WP + "extent")]
        caption = ""
        for q in paras[i + 1:i + 3]:
            t = para_text(q).strip()
            if t:
                caption = t
                break
        for k, rid in enumerate(blips):
            target = rels.get(rid, "")
            media = "word/" + target if not target.startswith("word/") else target
            fig = {"n": len(figs) + 1, "rId": rid, "media": media, "heading": last_heading,
                   "alt": descr[k] if k < len(descr) else (descr[0] if descr else ""),
                   "extent_in": [round(ext[k][0] / EMU, 2), round(ext[k][1] / EMU, 2)] if k < len(ext) else None,
                   "caption": caption}
            figs.append(fig)

    try:
        from PIL import Image
        have_pil = True
    except Exception:
        have_pil = False
    if have_pil:
        for fig in figs:
            try:
                im = Image.open(io.BytesIO(z.read(fig["media"])))
                fig["pixels"] = list(im.size)
                fig["_thumb"] = thumb(im)
            except Exception as e:  # noqa: BLE001
                fig["pixels"] = None
                fig["error"] = str(e)
    if a.match_dir:
        if not have_pil:
            sys.exit("Pillow is needed for --match-dir")
        olds = []
        for name in sorted(os.listdir(a.match_dir)):
            p = os.path.join(a.match_dir, name)
            if not os.path.isfile(p):
                continue
            try:
                im = Image.open(p)
                olds.append((name, list(im.size), thumb(im)))
            except Exception:
                continue
        for fig in figs:
            if "_thumb" not in fig:
                continue
            scored = sorted(((corr(fig["_thumb"], t), n, s) for n, s, t in olds), reverse=True)
            if scored:
                fig["best_match"] = {"file": scored[0][1], "pixels": scored[0][2], "corr": round(scored[0][0], 3),
                                     "second": scored[1][1] if len(scored) > 1 else None,
                                     "second_corr": round(scored[1][0], 3) if len(scored) > 1 else None,
                                     "verdict": "same picture" if scored[0][0] >= 0.9 else "NO GOOD MATCH (new or replaced)"}
    if a.extract:
        os.makedirs(a.extract, exist_ok=True)
        for fig in figs:
            out = os.path.join(a.extract, "fig_%02d_%s" % (fig["n"], os.path.basename(fig["media"])))
            with open(out, "wb") as f:
                f.write(z.read(fig["media"]))
            fig["extracted"] = out
    for fig in figs:
        fig.pop("_thumb", None)
    if a.json:
        print(json.dumps(figs, indent=1, ensure_ascii=False))
    else:
        for fig in figs:
            line = "FIG %2d  %-7s %-22s %-11s %s" % (fig["n"], fig["rId"], os.path.basename(fig["media"]),
                                                     "%dx%d" % tuple(fig["pixels"]) if fig.get("pixels") else "?",
                                                     "under: " + fig["heading"][:40])
            if fig.get("best_match"):
                bm = fig["best_match"]
                line += "  -> %s %.3f (%s)" % (bm["file"], bm["corr"], bm["verdict"])
            print(line)
            if fig["caption"]:
                print("        caption: " + fig["caption"][:110])
            if fig["alt"]:
                print("        alt:     " + fig["alt"][:110])
    return 0


if __name__ == "__main__":
    sys.exit(main())
