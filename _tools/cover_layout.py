#!/usr/bin/env python3
r"""
cover_layout.py — propose + score title layouts over cover art, pick the best (roadmap H1.4).

The typography auto-layout loop. `composite_cover.py` places the title; this decides WHERE the
title should sit. It proposes N candidate title bands over the cover ART, scores each for
legibility, and returns the best band for the compositor to use — closing the loop the way the
prose gates do (propose → score → pick).

Scoring, two modes:
  mechanical (default, runs anywhere, no GPU/vision): a title reads cleanly over a CALM,
      high-CONTRAST region. score = 0.55*calmness + 0.45*contrast, where calmness falls with
      the luminance variance inside the band and contrast is the band-vs-title-colour luminance
      gap. This is what keeps a title off a busy area and onto negative space.
  --vision (perceptual upgrade): render each candidate title onto the art and score it with
      vision_verify (keel/claude), picking the layout the vision model judges most legible.

CONTRACT
  python cover_layout.py --art IMG --palette "0D1B2A,F4EFE0,C9A760" [--title-color HEX] [--n 6] [--json]
  python cover_layout.py --art IMG --config book_config.json     # palette + colour from cover.palette
     -> print the best band {y_frac,h_frac,score,calmness,contrast} + the ranked candidates.
  python cover_layout.py --selftest
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

try:
    from PIL import Image, ImageStat, ImageDraw
except ImportError:  # pragma: no cover
    print("cover_layout needs Pillow (PIL). pip install Pillow", file=sys.stderr)
    raise

TOOLS = Path(__file__).resolve().parent


def hex_to_rgb(h: str):
    h = h.strip().lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


def lum(rgb) -> float:
    r, g, b = rgb
    return 0.299 * r + 0.587 * g + 0.114 * b


def band_stats(art: "Image.Image", y0f: float, y1f: float, x_inset: float = 0.10):
    w, h = art.size
    box = (int(w * x_inset), int(h * y0f), int(w * (1 - x_inset)), int(h * y1f))
    crop = art.crop(box).convert("L")
    st = ImageStat.Stat(crop)
    return st.mean[0], st.stddev[0]


def score_band(art, y0f, y1f, title_lum):
    mean_l, std_l = band_stats(art, y0f, y1f)
    calmness = max(0.0, 1.0 - min(1.0, std_l / 64.0))       # std 0 -> 1 (calm); >=64 -> 0 (busy)
    contrast = min(1.0, abs(mean_l - title_lum) / 200.0)     # 200 lum gap -> full contrast
    return 0.55 * calmness + 0.45 * contrast, calmness, contrast, mean_l, std_l


def candidates(n: int):
    """Band CENTERS to try, weighted toward the (house-style) upper third but spanning the cover."""
    base = [0.10, 0.16, 0.24, 0.34, 0.46, 0.60, 0.78]
    if n < len(base):
        # keep the upper-third-heavy head
        base = base[:n]
    return base


def propose(art: "Image.Image", title_rgb, n: int = 6, band_h: float = 0.16):
    tl = lum(title_rgb)
    out = []
    for yc in candidates(n):
        y0f = max(0.0, yc - band_h / 2)
        y1f = min(1.0, yc + band_h / 2)
        s, calm, contr, mean_l, std_l = score_band(art, y0f, y1f, tl)
        out.append({"y_frac": round(y0f, 3), "h_frac": round(y1f - y0f, 3), "center": yc,
                    "score": round(s, 4), "calmness": round(calm, 4), "contrast": round(contr, 4),
                    "band_lum": round(mean_l, 1), "band_std": round(std_l, 1)})
    out.sort(key=lambda c: c["score"], reverse=True)
    return out


def pick_title_color(hexes, art):
    """Default title colour = the palette colour with the best average contrast vs the whole art
    (falls back to the lightest, then white)."""
    if not hexes:
        return (255, 255, 255)
    art_l = ImageStat.Stat(art.convert("L")).mean[0]
    best, best_c = None, -1
    for h in hexes:
        try:
            rgb = hex_to_rgb(h)
        except Exception:
            continue
        c = abs(lum(rgb) - art_l)
        if c > best_c:
            best, best_c = rgb, c
    return best or (255, 255, 255)


def palette_from_config(cfg_path: Path):
    cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
    pal = ((cfg.get("cover", {}) or {}).get("palette", {}) or {})
    if isinstance(pal, dict):
        return [str(v) for v in pal.values()]
    if isinstance(pal, list):
        return [str(v) for v in pal]
    return []


def vision_rescore(art, ranked, title_rgb, title_text, top_k=3):
    """Optional perceptual pass: render the title on the art for the top-K mechanical
    candidates, score each via vision_verify, and re-rank by the vision verdict. Best-effort:
    if vision is unavailable, the mechanical ranking stands."""
    import subprocess
    import tempfile
    font = None
    for cand in (TOOLS.parent / "fonts" / "CormorantGaramond-Bold.ttf",):
        if cand.exists():
            try:
                from PIL import ImageFont
                font = ImageFont.truetype(str(cand), max(24, art.size[1] // 16))
            except Exception:
                font = None
    scored = []
    for c in ranked[:top_k]:
        im = art.convert("RGB").copy()
        d = ImageDraw.Draw(im)
        y = int((c["y_frac"] + c["h_frac"] / 2) * im.size[1])
        d.text((im.size[0] // 2, y), title_text, fill=title_rgb, anchor="mm", font=font)
        tmp = Path(tempfile.mkdtemp()) / "cand.png"
        im.save(tmp)
        rubric = ("Judge ONLY the title's legibility and placement. Reply with a line "
                  "'VERDICT: PASS' if the title is easy to read and well placed, else "
                  "'VERDICT: FAIL', then list issues.")
        try:
            r = subprocess.run([sys.executable, str(TOOLS / "vision_verify.py"),
                                "--image", str(tmp), "--rubric", rubric, "--backend", "keel"],
                               capture_output=True, text=True, timeout=90)
            v = json.loads(r.stdout.strip().splitlines()[-1]) if r.stdout.strip() else {}
            verdict = str(v.get("verdict", "PENDING")).upper()
            c = dict(c, vision=verdict, vision_issues=len(v.get("issues", [])))
            scored.append((0 if verdict == "PASS" else 1, c.get("vision_issues", 9), -c["score"], c))
        except Exception as e:
            c = dict(c, vision="unavailable", vision_err=str(e)[:80])
            scored.append((2, 9, -c["score"], c))
    scored.sort(key=lambda t: t[:3])
    return [t[3] for t in scored] + ranked[top_k:]


def selftest() -> int:
    fails = []
    # synthetic art: calm dark TOP half, busy noisy BOTTOM half
    w, h = 160, 240
    art = Image.new("RGB", (w, h), (18, 24, 40))            # calm dark everywhere
    px = art.load()
    seed = 12345
    for y in range(h // 2, h):                              # bottom half = high-variance noise
        for x in range(w):
            seed = (1103515245 * seed + 12345) & 0x7FFFFFFF
            v = seed % 256
            px[x, y] = (v, (v * 3) % 256, (v * 7) % 256)
    title_rgb = (244, 239, 224)                            # light title
    ranked = propose(art, title_rgb, n=6)
    best = ranked[0]
    if best["center"] > 0.5:
        fails.append(f"best band should be in the calm top half, got center {best['center']} ({best})")
    # a top band must out-score a bottom band
    top = min(ranked, key=lambda c: c["center"])
    bot = max(ranked, key=lambda c: c["center"])
    if top["score"] <= bot["score"]:
        fails.append(f"calm top ({top['score']}) did not beat busy bottom ({bot['score']})")
    if best["calmness"] < 0.8:
        fails.append(f"best band calmness unexpectedly low: {best['calmness']}")
    if fails:
        print("COVER_LAYOUT SELFTEST: FAIL")
        for f in fails:
            print("  - " + f)
        return 1
    print(f"COVER_LAYOUT SELFTEST: PASS (calm top band chosen: center {best['center']}, "
          f"score {best['score']} vs busy-bottom {bot['score']})")
    return 0


def main(argv=None) -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    ap = argparse.ArgumentParser(description="Propose + score title layouts over cover art.")
    ap.add_argument("--art", help="cover art image")
    ap.add_argument("--palette", help="comma-separated hex colours")
    ap.add_argument("--config", help="book_config.json (reads cover.palette)")
    ap.add_argument("--title-color", help="title hex colour (else best-contrast palette colour)")
    ap.add_argument("--title-text", default="Title", help="title text (for --vision rendering)")
    ap.add_argument("--n", type=int, default=6, help="number of candidate bands")
    ap.add_argument("--vision", action="store_true", help="re-rank top candidates with vision_verify")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)

    if args.selftest:
        return selftest()
    if not args.art:
        ap.print_help()
        return 2
    art = Image.open(args.art).convert("RGB")
    hexes = []
    if args.palette:
        hexes = [h for h in args.palette.split(",") if h.strip()]
    elif args.config:
        hexes = palette_from_config(Path(args.config))
    title_rgb = hex_to_rgb(args.title_color) if args.title_color else pick_title_color(hexes, art)
    ranked = propose(art, title_rgb, n=args.n)
    if args.vision:
        ranked = vision_rescore(art, ranked, title_rgb, args.title_text)
    result = {"art": args.art, "title_color": "#%02X%02X%02X" % title_rgb,
              "best": ranked[0], "candidates": ranked}
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        b = ranked[0]
        print(f"best title band: y_frac={b['y_frac']} h_frac={b['h_frac']} "
              f"(center {b['center']}, score {b['score']}, calm {b['calmness']}, contrast {b['contrast']})")
        for c in ranked:
            tag = f" vision={c['vision']}" if "vision" in c else ""
            print(f"  center {c['center']:>4}  score {c['score']:.4f}  calm {c['calmness']:.2f}  "
                  f"contrast {c['contrast']:.2f}{tag}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
