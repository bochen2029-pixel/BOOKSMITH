#!/usr/bin/env python3
r"""
cover_pick.py — choose cover ART without a GPU (catalog match + hypergen).

The art-source slot for machines that can't render bespoke SDXL. Given a book's
config it derives the book's mood + palette, then offers:
  - a hypergen shortlist (pure-code abstract covers in the book's palette), and
  - the closest entries from the prerendered SDXL catalog (cover_catalog/catalog.json,
    if present), scored by tag/keyword/palette overlap.
The session (or a person) picks; --auto takes the best. The chosen art is written
to the book's cover_art/<slug>_src.png (no baked text) and composite_cover.py +
vision_verify.py take it from there, exactly as with SDXL art.

Usage:
  python _tools/cover_pick.py --config <book_config.json>                 # shortlist
  python _tools/cover_pick.py --config <book_config.json> --auto --write  # pick + install
  python _tools/cover_pick.py --config <book_config.json> --pick hypergen:horizon --write
  python _tools/cover_pick.py --config <book_config.json> --pick catalog:sdxl_042 --write
"""
from __future__ import annotations
import argparse, json, re, shutil, sys
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
ROOT = TOOLS.parent
sys.path.insert(0, str(TOOLS))
import hypergen  # noqa: E402

# genre keyword -> mood palette
GENRE_MOOD = [
    (r"thriller|crime|mystery|suspense|detective", "bold_thriller"),
    (r"sci|science fiction|space|future|cyber", "cool_scifi"),
    (r"romance|love", "soft_romance"),
    (r"memoir|biograph|essay|personal", "warm_memoir"),
    (r"horror|gothic|dark", "noir"),
    (r"fantasy|myth|magic", "botanical"),
    (r"business|self|guide|how|nonfiction|history|science\b", "earthy_nonfiction"),
]
# a spread of styles to shortlist, calm-topped for titles
SHORTLIST_STYLES = ["horizon", "gradient", "contours", "deco"]


def derive(cfg):
    cover = cfg.get("cover", {}) if isinstance(cfg.get("cover"), dict) else {}
    mood = cover.get("mood")
    genre = (cfg.get("genre") or "") + " " + (cfg.get("subtitle") or "")
    if not mood:
        for pat, m in GENRE_MOOD:
            if re.search(pat, genre, re.I):
                mood = m
                break
    if not mood:
        mood = "dark_literary" if cfg.get("is_fiction", True) else "earthy_nonfiction"
    raw = cover.get("palette")
    if isinstance(raw, dict):
        cols = list(raw.values())          # config often names colors {navy, cream, ...}
    elif isinstance(raw, list) and raw:
        cols = raw
    else:
        cols = None
    if cols:
        def _lum(c):
            try:
                r, g, b = hypergen._hex(c)
                return 0.299 * r + 0.587 * g + 0.114 * b
            except Exception:
                return 0
        palette = sorted(cols, key=_lum)   # dark -> light for natural gradients
    else:
        palette = hypergen.MOODS.get(mood, hypergen.MOODS["dark_literary"])
    # keywords describing the wanted art (for catalog scoring)
    art = cover.get("art", {}) if isinstance(cover.get("art"), dict) else {}
    kw = re.findall(r"[a-z]{4,}", (art.get("prompt", "") + " " + genre + " " + mood).lower())
    return mood, palette, set(kw)


def load_catalog():
    p = ROOT / "cover_catalog" / "catalog.json"
    if not p.exists():
        return []
    try:
        d = json.loads(p.read_text(encoding="utf-8"))
        return d.get("entries", d) if isinstance(d, (dict, list)) else []
    except Exception:
        return []


def score_entry(entry, kw, mood):
    tags = set(str(t).lower() for t in entry.get("tags", []))
    desc = re.findall(r"[a-z]{4,}", entry.get("description", "").lower())
    s = len(kw & tags) * 3 + len(kw & set(desc))
    if entry.get("mood") == mood:
        s += 4
    return s


def main(argv=None):
    ap = argparse.ArgumentParser(description="Pick cover art without a GPU (catalog + hypergen).")
    ap.add_argument("--config", required=True)
    ap.add_argument("--auto", action="store_true", help="choose the best automatically")
    ap.add_argument("--pick", help="hypergen:<style> or catalog:<id>")
    ap.add_argument("--write", action="store_true", help="install the choice to cover_art/<slug>_src.png")
    ap.add_argument("--size", default="1600x2400")
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--recolor", action="store_true",
                    help="recolour a CATALOG pick to the book palette via palette_transfer "
                         "(hypergen picks already render in-palette, so they are left as-is)")
    ap.add_argument("--recolor-strength", type=float, default=0.75)
    args = ap.parse_args(argv)

    cfg_path = Path(args.config).resolve()
    cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
    slug = cfg["slug"]
    ws = cfg_path.parent
    mood, palette, kw = derive(cfg)
    w, h = (int(x) for x in args.size.lower().split("x"))

    catalog = load_catalog()
    ranked = sorted(catalog, key=lambda e: -score_entry(e, kw, mood))[:3]

    print(f"book: {slug} | mood: {mood} | palette: {palette}")
    print("candidates:")
    opts = []
    for st in SHORTLIST_STYLES:
        cid = f"hypergen:{st}"
        opts.append(cid)
        print(f"  {cid:22} abstract, {st} style in the book palette (renders anywhere)")
    for e in ranked:
        cid = f"catalog:{e.get('id')}"
        opts.append(cid)
        print(f"  {cid:22} SDXL: {e.get('description','')[:70]}  (score {score_entry(e, kw, mood)})")

    choice = args.pick
    if args.auto and not choice:
        # prefer a strong catalog match; else a hypergen style by mood
        if ranked and score_entry(ranked[0], kw, mood) >= 6:
            choice = f"catalog:{ranked[0].get('id')}"
        else:
            choice = f"hypergen:{'horizon' if cfg.get('is_fiction', True) else 'gradient'}"
    if not choice:
        print("\n(no --pick/--auto: shortlist only. Re-run with --auto --write, or --pick <id> --write.)")
        return 0

    print(f"\nchosen: {choice}")
    if not args.write:
        print("(add --write to install it to cover_art/)")
        return 0

    dest = ws / "cover_art" / f"{slug}_src.png"
    dest.parent.mkdir(parents=True, exist_ok=True)
    if choice.startswith("hypergen:"):
        style = choice.split(":", 1)[1]
        hypergen.render(style, palette, size=(w, h), seed=args.seed).save(dest)
    elif choice.startswith("catalog:"):
        cid = choice.split(":", 1)[1]
        entry = next((e for e in catalog if str(e.get("id")) == cid), None)
        if not entry:
            print(f"catalog id {cid} not found", file=sys.stderr)
            return 1
        src = ROOT / "cover_catalog" / entry.get("file", "")
        if not src.exists():
            print(f"catalog image missing on disk: {src} (fetch the full catalog, or pick a hypergen option)",
                  file=sys.stderr)
            return 1
        shutil.copy2(src, dest)
        if args.recolor and palette:
            import subprocess
            pal = ",".join(str(c) for c in palette)
            rr = subprocess.run([sys.executable, str(TOOLS / "palette_transfer.py"),
                                 "--src", str(dest), "--palette", pal, "--out", str(dest),
                                 "--strength", str(args.recolor_strength)],
                                capture_output=True, text=True)
            print(f"recoloured catalog art to the book palette (strength {args.recolor_strength})"
                  if rr.returncode == 0 else
                  f"(palette recolour skipped: {(rr.stderr or rr.stdout).strip()[-120:]})")
    else:
        print(f"bad --pick {choice}", file=sys.stderr)
        return 1
    print(f"installed cover art -> {dest}")
    print(f"next: python _tools/composite_cover.py --config {cfg_path} --profile <p> --pages <N>")
    return 0


if __name__ == "__main__":
    sys.exit(main())
