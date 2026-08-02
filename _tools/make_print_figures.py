#!/usr/bin/env python3
"""
make_print_figures.py — grayscale print derivatives for mid-flow figures.

BOOKSMITH toolchain component (2026-07-27, the figure-program feature). Print
interiors are black-ink; a color figure dropped straight into one is converted
by the printer with no one checking the contrast. This tool produces the
checked version: for every source image in the figures directory it emits a
"<name>_print.<ext>" sibling — grayscale (ITU-R 601 luma via PIL), a mild
autocontrast stretch so navy-on-cream art keeps its separation in ink, same
pixel dimensions, optimized. generate_book.js PREFERS the _print sibling when
present; kindle/EPUB/digital keep reading the color original.

Skips: files already ending in _print, non-PNG/JPEG files, and derivatives
already newer than their source (unless --force). Reports each figure's pixel
width and its effective print DPI at the requested text-block width so
under-resolution sources are visible before anything builds.

Usage:
  python make_print_figures.py --config book_config.json
        [--dir images/figures] [--block-width-in 4.75] [--force] [--json]
Exit: 0 ok (derivatives current) - 1 error - 2 usage. PIL only.
"""
import argparse
import json
import sys
from pathlib import Path

from PIL import Image, ImageOps

EXTS = {".png", ".jpg", ".jpeg"}


def make_derivative(src: Path, dst: Path):
    im = Image.open(src)
    # Flatten alpha onto white first: print stock is white, and a transparent
    # PNG converted to L directly renders its alpha as black.
    if im.mode in ("RGBA", "LA", "P"):
        rgba = im.convert("RGBA")
        base = Image.new("RGBA", rgba.size, (255, 255, 255, 255))
        base.alpha_composite(rgba)
        im = base.convert("RGB")
    gray = ImageOps.grayscale(im)
    gray = ImageOps.autocontrast(gray, cutoff=1)
    if dst.suffix.lower() in (".jpg", ".jpeg"):
        gray.save(dst, quality=92, optimize=True)
    else:
        gray.save(dst, optimize=True)
    return gray.size


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True, help="book_config.json (workspace root = its parent)")
    ap.add_argument("--dir", default="images/figures",
                    help="figures directory, workspace-relative (default images/figures)")
    ap.add_argument("--block-width-in", type=float, default=4.75,
                    help="print text-block width used for the effective-DPI report")
    ap.add_argument("--force", action="store_true", help="regenerate even when the derivative is newer")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    ws = Path(a.config).resolve().parent
    fig_dir = (ws / a.dir).resolve()
    if not fig_dir.is_dir():
        print(f"error: figures directory not found: {fig_dir}", file=sys.stderr)
        return 1

    rows, made, skipped = [], 0, 0
    for src in sorted(fig_dir.iterdir()):
        if src.suffix.lower() not in EXTS or src.stem.endswith("_print"):
            continue
        dst = src.with_name(f"{src.stem}_print{src.suffix}")
        fresh = dst.exists() and dst.stat().st_mtime >= src.stat().st_mtime
        if fresh and not a.force:
            action = "current"
            skipped += 1
            with Image.open(src) as im:
                w, h = im.size
        else:
            w, h = make_derivative(src, dst)
            action = "made"
            made += 1
        eff_dpi = round(w / a.block_width_in)
        rows.append({"source": src.name, "derivative": dst.name, "action": action,
                     "px": [w, h], "effective_dpi_at_block": eff_dpi,
                     "print_quality": "ok" if eff_dpi >= 240 else "LOW (consider upscaling)"})

    out = {"dir": str(fig_dir), "made": made, "current": skipped,
           "block_width_in": a.block_width_in, "figures": rows}
    if a.json:
        print(json.dumps(out, indent=2))
    else:
        for r in rows:
            print(f"[{r['action']:>7}] {r['source']:<38} {r['px'][0]}x{r['px'][1]}px "
                  f"~{r['effective_dpi_at_block']}dpi at {a.block_width_in}in  {r['print_quality']}")
        print(f"\nMAKE_PRINT_FIGURES: {made} made, {skipped} current, {len(rows)} figure(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
