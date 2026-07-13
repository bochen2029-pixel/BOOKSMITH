#!/usr/bin/env python3
r"""
palette_transfer.py — recolor a cover image to a book's exact palette (BOOKSMITH, roadmap H1.4).

So any catalog / hypergen cover image can serve any book: shift its colour mood toward the
book's palette while preserving its structure (composition, the calm upper-third title zone).
Uses Reinhard-style mean/std transfer in CIELAB, implemented in PURE PILLOW (Image mode "LAB"
+ ImageStat + per-channel point tables) so it adds no numpy dependency.

The target is a PALETTE (a few hex colours), not a reference photo, so we synthesize a small
"swatch" image from the palette (area-weighted bands) and transfer the source toward the
swatch's LAB statistics. A --strength knob blends the recolour with the original so the shift
stays tasteful; per-channel scale is clamped so a flat source cannot blow up.

CONTRACT
  python palette_transfer.py --src IMG --palette "0D1B2A,F4EFE0,C9A760" --out IMG [--strength 0.8]
  python palette_transfer.py --src IMG --config book_config.json --out IMG   # palette from cover.palette
      -> writes the recoloured image; prints a JSON summary (mean LAB before/after + target).
  python palette_transfer.py --selftest
      -> recolour a cool source toward a warm palette; assert the result moved toward it.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

try:
    from PIL import Image, ImageStat
except ImportError:  # pragma: no cover
    print("palette_transfer needs Pillow (PIL). pip install Pillow", file=sys.stderr)
    raise


def hex_to_rgb(h: str) -> tuple[int, int, int]:
    h = h.strip().lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    if not re.fullmatch(r"[0-9a-fA-F]{6}", h):
        raise ValueError(f"bad hex colour: {h!r}")
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


def make_swatch(hexes: list[str], size: int = 256) -> "Image.Image":
    """A square image of equal-area vertical bands, one per palette colour. Its LAB
    statistics ARE the palette we transfer toward."""
    rgbs = [hex_to_rgb(h) for h in hexes if h.strip()]
    if not rgbs:
        raise ValueError("empty palette")
    img = Image.new("RGB", (size, size))
    band = max(1, size // len(rgbs))
    px = img.load()
    for x in range(size):
        c = rgbs[min(x // band, len(rgbs) - 1)]
        for y in range(size):
            px[x, y] = c
    return img


def _stats(lab_img):
    st = ImageStat.Stat(lab_img)
    return list(st.mean), [s or 1.0 for s in st.stddev]


def lab_transfer(src_rgb, ref_rgb, strength: float = 0.85):
    """Reinhard mean/std transfer src->ref in LAB, blended by `strength` (0=src, 1=full)."""
    src = src_rgb.convert("LAB")
    ref = ref_rgb.convert("LAB")
    smean, sstd = _stats(src)
    rmean, rstd = _stats(ref)
    out_ch = []
    for i in range(3):
        ch = src.getchannel(i)
        scale = rstd[i] / sstd[i]
        scale = max(0.5, min(scale, 2.0))          # clamp: a flat channel can't explode
        full = [(v - smean[i]) * scale + rmean[i] for v in range(256)]
        # blend the transfer with the identity by `strength`
        table = [max(0, min(255, int(round(v * (1 - strength) + f * strength))))
                 for v, f in zip(range(256), full)]
        out_ch.append(ch.point(table))
    return Image.merge("LAB", out_ch).convert("RGB"), smean, rmean


def lab_mean(img_rgb) -> list[float]:
    return [round(m, 1) for m in ImageStat.Stat(img_rgb.convert("LAB")).mean]


def palette_from_config(cfg_path: Path) -> list[str]:
    cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
    pal = ((cfg.get("cover", {}) or {}).get("palette", {}) or {})
    if isinstance(pal, dict):
        return [str(v) for v in pal.values()]
    if isinstance(pal, list):
        return [str(v) for v in pal]
    return []


def _dist(a, b):
    return sum((x - y) ** 2 for x, y in zip(a, b)) ** 0.5


def selftest() -> int:
    fails = []
    # a cool (blue) source, a warm palette (cream/gold/umber)
    src = Image.new("RGB", (64, 64), (30, 50, 120))
    warm = ["F4EFE0", "C9A760", "6B3F1E"]
    before = lab_mean(src)
    swatch = make_swatch(warm)
    target = lab_mean(swatch)
    out, _, _ = lab_transfer(src, swatch, strength=0.9)
    after = lab_mean(out)
    if _dist(after, target) >= _dist(before, target):
        fails.append(f"transfer did not move toward the palette: before {before} after {after} target {target}")
    # structure preserved: a gradient stays monotonic-ish (not collapsed to one colour)
    grad = Image.new("RGB", (64, 1))
    gpx = grad.load()
    for x in range(64):
        gpx[x, 0] = (x * 4, x * 2, 255 - x * 3)
    gout, _, _ = lab_transfer(grad, swatch, strength=0.8)
    lchan = list(gout.convert("LAB").getchannel(0).getdata())
    if max(lchan) - min(lchan) < 20:
        fails.append("structure collapsed: L channel variation lost after transfer")
    if fails:
        print("PALETTE_TRANSFER SELFTEST: FAIL")
        for f in fails:
            print("  - " + f)
        return 1
    print(f"PALETTE_TRANSFER SELFTEST: PASS (cool source moved toward warm palette; "
          f"before {before} -> after {after}, target {target}; structure preserved)")
    return 0


def main(argv=None) -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    ap = argparse.ArgumentParser(description="Recolour a cover image to a book's palette (LAB transfer).")
    ap.add_argument("--src", help="source image (catalog / hypergen cover)")
    ap.add_argument("--out", help="output image path")
    ap.add_argument("--palette", help="comma-separated hex colours, e.g. 0D1B2A,F4EFE0,C9A760")
    ap.add_argument("--config", help="book_config.json (reads cover.palette)")
    ap.add_argument("--strength", type=float, default=0.85, help="0=source .. 1=full transfer (default 0.85)")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)

    if args.selftest:
        return selftest()
    if not args.src or not args.out:
        ap.print_help()
        return 2
    hexes = []
    if args.palette:
        hexes = [h for h in args.palette.split(",") if h.strip()]
    elif args.config:
        hexes = palette_from_config(Path(args.config))
    if not hexes:
        print("no palette: pass --palette or --config with cover.palette", file=sys.stderr)
        return 2
    src_img = Image.open(args.src)
    # transparency survives the transfer: transfer the RGB, re-attach the alpha
    # (silently flattening a transparent source made it opaque against nothing)
    alpha = src_img.getchannel("A") if src_img.mode in ("RGBA", "LA") else None
    src = src_img.convert("RGB")
    swatch = make_swatch(hexes)
    before = lab_mean(src)
    target = lab_mean(swatch)
    out, _, _ = lab_transfer(src, swatch, strength=max(0.0, min(1.0, args.strength)))
    after = lab_mean(out)
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    if alpha is not None:
        if Path(args.out).suffix.lower() == ".png":
            out = out.convert("RGBA")
            out.putalpha(alpha)
        else:
            print("note: source alpha flattened (non-PNG output)", file=sys.stderr)
    out.save(args.out)
    print(json.dumps({"src": args.src, "out": args.out, "palette": hexes,
                      "lab_mean_before": before, "lab_mean_after": after,
                      "lab_mean_target": target, "strength": args.strength}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
