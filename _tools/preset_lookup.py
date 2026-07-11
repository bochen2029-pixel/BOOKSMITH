#!/usr/bin/env python3
r"""
preset_lookup.py — shared lookup/interpolation over print_presets.json (BOOKSMITH).

PURPOSE (KIT_ARCHITECTURE (c), two-verifier model)
    The SINGLE code path for service-preset geometry, consumed by BOTH
    composite_cover.py (to BUILD covers) and verify_build.py (to RECOMPUTE the
    expected dimensions independently). Because both sides call these same
    functions, the verifier recomputes exactly what the compositor built — any
    mismatch that survives is a real artifact defect (wrong PDF on disk),
    never re-implementation drift.

    Geometry served:

    Blurb Trade SOFTCOVER            softcover_dims(trim_key, paper, pages)
        spine   = linear interpolation over blurb_trade.spine_tables_in
                  .softcover[paper], CLAMPED at the table ends
        cover_w = 2*trim_w + spine + 0.25      (0.125" bleed each side)
        cover_h = trim_h + 0.25
        (verified against every probed calculator row — see print_presets.json
        blurb_trade.softcover_cover_model)

    Blurb Hardcover IMAGEWRAP        imagewrap_dims(trim_key, paper, pages)
        NEVER derived from first principles (the preset says DO NOT derive):
        spine   = linear interpolation over blurb_trade.spine_tables_in
                  .imagewrap_and_dustjacket[paper], CLAMPED
        then the cover-PDF width slides 1:1 with the spine off the NEAREST
        probed row (W_ref, H, spine_ref):
            cover_w = W_ref + (spine - spine_ref)
            cover_h = H                        (constant per trim)
        (VERIFIED 1:1 movement: 6x9 bw 100pp W 13.625 spine 0.375 vs 200pp
        W 13.75 spine 0.5 — delta 0.125 both.)

    Mixam PAPERBACK spine            mixam_paperback_spine(pages, paper, override)
        spine_override_in wins when present (the Mixam CART value is canonical);
        else cream:          pages * 0.0023  + 0.04
             (fits Mixam's live-calculator US Trade cream-50lb series within
             ±0.005 — print_presets.json mixam_paperback.spine_fit)
        else white/uncoated: pages * 0.00215 + 0.01
             (INFERRED — single-point fit to the one probed uncoated 50lb value,
             200pp -> 0.44. Not confirmed from an official source; verify at
             upload. The cart value goes into book_config.spine.spine_override_in
             and wins.)

    Mixam PAPERBACK wrap             mixam_paperback_wrap_dims(trim_w, trim_h, spine)
        EXACTLY the KDP-wrap single-spread geometry (verified against Mixam's
        own template MediaBoxes — mixam_paperback.cover_model):
            W = 2*trim_w + spine + 2*0.125 ; H = trim_h + 2*0.125 ; bleed 0.125

    print_presets.json is the source of truth and is NEVER modified here.
    Meta-rule: the service's own calculator/previewer ALWAYS beats these
    numbers — a stated dimension from a rejection or cart goes into
    book_config.spine.spine_override_in and wins.

CONTRACT
    import preset_lookup
    preset_lookup.softcover_dims("6x9", "standard_trade_bw_matte_paper", 100)
      -> {"spine": 0.208, "cover_w": 12.458, "cover_h": 9.25, ...}
    preset_lookup.imagewrap_dims("6x9", "standard_trade_bw_matte_paper", 200)
      -> {"spine": 0.5, "cover_w": 13.75, "cover_h": 9.861, ...}
    preset_lookup.mixam_paperback_spine(200, "cream")            -> 0.5
    preset_lookup.mixam_paperback_wrap_dims(6, 9, 0.5)
      -> {"spine": 0.5, "cover_w": 12.75, "cover_h": 9.25, "bleed_in": 0.125}

    Debug CLI:
      python preset_lookup.py blurb-softcover  --trim 6x9 --pages 100
      python preset_lookup.py blurb-imagewrap  --trim 6x9 --pages 200
      python preset_lookup.py mixam-paperback  --trim 6x9 --pages 200 [--paper cream]
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
PRESETS_PATH = SCRIPT_DIR / "print_presets.json"

DEFAULT_BLURB_PAPER = "standard_trade_bw_matte_paper"

# ---- Mixam paperback constants (print_presets.json mixam_paperback) ----
MIXAM_PB_BLEED_IN = 0.125                 # cover_bleed_in — KDP-wrap geometry
MIXAM_PB_SPINE_CREAM_PER_PAGE = 0.0023    # spine_fit: cream 50lb (calc series ±0.005)
MIXAM_PB_SPINE_CREAM_BASE = 0.04
MIXAM_PB_SPINE_WHITE_PER_PAGE = 0.00215   # INFERRED: single-point fit, uncoated 50lb
MIXAM_PB_SPINE_WHITE_BASE = 0.01          #   200pp -> 0.44; cart canonical — verify at upload

_PRESETS_CACHE: dict | None = None


# ─────────────────────────────────────────────────────────────────────────────
# loading + key helpers
# ─────────────────────────────────────────────────────────────────────────────

def load_presets(path: Path | str | None = None) -> dict:
    """Load (and cache) print_presets.json. The file is read-only truth."""
    global _PRESETS_CACHE
    if path is not None:
        with Path(path).open(encoding="utf-8") as fh:
            return json.load(fh)
    if _PRESETS_CACHE is None:
        with PRESETS_PATH.open(encoding="utf-8") as fh:
            _PRESETS_CACHE = json.load(fh)
    return _PRESETS_CACHE


def trim_key(trim_w: float, trim_h: float) -> str:
    """(6, 9) -> "6x9" — the key format used by blurb_trade.trims_offered."""
    def fmt(v: float) -> str:
        v = float(v)
        return str(int(v)) if v == int(v) else ("%g" % v)
    return f"{fmt(trim_w)}x{fmt(trim_h)}"


def blurb_paper_from_config(cfg: dict) -> str:
    """config.blurb_paper, defaulting to the B&W text-book paper (schema default)."""
    return cfg.get("blurb_paper") or DEFAULT_BLURB_PAPER


def _numeric_table(table: dict) -> list:
    """[(pages_float, value), ...] sorted by pages; skips _note/_schema keys."""
    rows = []
    for k, v in table.items():
        try:
            pk = float(k)
        except (TypeError, ValueError):
            continue  # "_note", "_schema", ...
        rows.append((pk, v))
    rows.sort(key=lambda r: r[0])
    if not rows:
        raise ValueError("preset table has no numeric page keys")
    return rows


def interp_table(table: dict, pages: float) -> float:
    """Linear interpolation of a {pages: value} table, CLAMPED at both ends."""
    pts = [(p, float(v)) for p, v in _numeric_table(table)]
    if pages <= pts[0][0]:
        return pts[0][1]
    if pages >= pts[-1][0]:
        return pts[-1][1]
    for (p0, v0), (p1, v1) in zip(pts, pts[1:]):
        if p0 <= pages <= p1:
            if p1 == p0:
                return v0
            t = (pages - p0) / (p1 - p0)
            return v0 + t * (v1 - v0)
    return pts[-1][1]  # unreachable (clamped above)


def _blurb_trim(bt: dict, tkey: str):
    trims = bt.get("trims_offered", {})
    if tkey not in trims:
        raise KeyError(
            f"Blurb trim {tkey!r} not offered; offered: {sorted(trims)}")
    return float(trims[tkey][0]), float(trims[tkey][1])


# ─────────────────────────────────────────────────────────────────────────────
# Blurb Trade — softcover
# ─────────────────────────────────────────────────────────────────────────────

def softcover_dims(tkey: str, paper: str, pages: int,
                   presets: dict | None = None) -> dict:
    """Blurb Trade SOFTCOVER wrap dims for (trim, paper, pages). See module doc."""
    bt = (presets or load_presets())["blurb_trade"]
    tw, th = _blurb_trim(bt, tkey)
    spine_tables = bt["spine_tables_in"]["softcover"]
    if paper not in spine_tables:
        raise KeyError(f"unknown Blurb paper {paper!r}; known: "
                       f"{sorted(k for k in spine_tables if not k.startswith('_'))}")
    spine = round(interp_table(spine_tables[paper], pages), 4)
    return {
        "binding": "softcover",
        "trim_key": tkey, "paper": paper, "pages": int(pages),
        "trim_w": tw, "trim_h": th,
        "spine": spine,
        "cover_w": round(2 * tw + spine + 0.25, 4),   # 0.125" bleed each side
        "cover_h": round(th + 0.25, 4),
        "bleed_in": 0.125,
    }


# ─────────────────────────────────────────────────────────────────────────────
# Blurb Trade — hardcover ImageWrap
# ─────────────────────────────────────────────────────────────────────────────

# Which probed cover-PDF rows table serves a (trim, paper) pair. 6x9 has a B&W
# table and a color table; 5x8/8x10 are single-row tables (any paper).
_IMAGEWRAP_ROWS_BY_TRIM = {
    "6x9": {
        "standard_trade_bw_matte_paper": "imagewrap_cover_pdf_rows_6x9",
        "economy_trade_matte_paper": "imagewrap_cover_pdf_rows_6x9_color",
        "standard_trade_matte_paper": "imagewrap_cover_pdf_rows_6x9_color",
    },
    "5x8": {"*": "imagewrap_cover_pdf_rows_5x8"},
    "8x10": {"*": "imagewrap_cover_pdf_rows_8x10"},
}


def imagewrap_dims(tkey: str, paper: str, pages: int,
                   presets: dict | None = None) -> dict:
    """Blurb Hardcover IMAGEWRAP wrap dims for (trim, paper, pages).

    Interpolates spine from the imagewrap spine table, then slides the probed
    cover-PDF width 1:1 with the spine off the NEAREST probed row. cover_h is
    the probed H, constant per trim. See module doc."""
    bt = (presets or load_presets())["blurb_trade"]
    tw, th = _blurb_trim(bt, tkey)

    by_paper = _IMAGEWRAP_ROWS_BY_TRIM.get(tkey)
    if not by_paper:
        raise KeyError(f"no ImageWrap cover rows table for trim {tkey!r}")
    rows_key = by_paper.get(paper) or by_paper.get("*")
    if rows_key is None or rows_key not in bt:
        raise KeyError(f"no ImageWrap cover rows for trim {tkey!r} paper {paper!r}")

    spine_tables = bt["spine_tables_in"]["imagewrap_and_dustjacket"]
    if paper not in spine_tables:
        raise KeyError(f"unknown Blurb paper {paper!r}; known: "
                       f"{sorted(k for k in spine_tables if not k.startswith('_'))}")
    spine = round(interp_table(spine_tables[paper], pages), 4)

    rows = _numeric_table(bt[rows_key])          # [(pages, [W, H, spine]), ...]
    ref_pages, ref = min(rows, key=lambda r: (abs(pages - r[0]), r[0]))
    w_ref, h_ref, spine_ref = float(ref[0]), float(ref[1]), float(ref[2])

    return {
        "binding": "imagewrap",
        "trim_key": tkey, "paper": paper, "pages": int(pages),
        "trim_w": tw, "trim_h": th,
        "spine": spine,
        "cover_w": round(w_ref + (spine - spine_ref), 4),  # width moves 1:1 with spine
        "cover_h": round(h_ref, 4),                        # constant per trim
        "ref_row": {"pages": int(ref_pages), "cover_w": w_ref,
                    "cover_h": h_ref, "spine": spine_ref},
    }


# ─────────────────────────────────────────────────────────────────────────────
# Mixam paperback
# ─────────────────────────────────────────────────────────────────────────────

def mixam_paperback_spine(pages: int, paper: str = "cream",
                          spine_override_in=None) -> float:
    """Mixam paperback spine. spine_override_in (the CART value — canonical)
    wins when present. cream: pages*0.0023 + 0.04 (live-calc fit ±0.005).
    white/uncoated: pages*0.00215 + 0.01 — INFERRED single-point fit
    (uncoated 50lb @200pp = 0.44); verify at upload."""
    if spine_override_in is not None:
        return round(float(spine_override_in), 4)
    if str(paper).lower() == "cream":
        return round(pages * MIXAM_PB_SPINE_CREAM_PER_PAGE
                     + MIXAM_PB_SPINE_CREAM_BASE, 4)
    return round(pages * MIXAM_PB_SPINE_WHITE_PER_PAGE
                 + MIXAM_PB_SPINE_WHITE_BASE, 4)


def mixam_paperback_wrap_dims(trim_w: float, trim_h: float,
                              spine_in: float) -> dict:
    """Mixam paperback single wrap [back|spine|front] — EXACTLY the KDP-wrap
    geometry: W = 2*trim_w + spine + 2*0.125 ; H = trim_h + 2*0.125."""
    b = MIXAM_PB_BLEED_IN
    return {
        "spine": round(float(spine_in), 4),
        "cover_w": round(2 * float(trim_w) + float(spine_in) + 2 * b, 4),
        "cover_h": round(float(trim_h) + 2 * b, 4),
        "bleed_in": b,
    }


# ─────────────────────────────────────────────────────────────────────────────
# debug CLI
# ─────────────────────────────────────────────────────────────────────────────

def _cli(argv=None) -> int:
    import argparse
    ap = argparse.ArgumentParser(
        description="Debug CLI over print_presets.json geometry (BOOKSMITH).")
    ap.add_argument("what",
                    choices=["blurb-softcover", "blurb-imagewrap", "mixam-paperback"])
    ap.add_argument("--trim", default="6x9", help='Trim key, e.g. "6x9".')
    ap.add_argument("--paper", default=None,
                    help="Blurb paper key, or cream/white for Mixam.")
    ap.add_argument("--pages", type=int, required=True)
    ap.add_argument("--override", type=float, default=None,
                    help="spine_override_in (Mixam cart value — wins).")
    a = ap.parse_args(argv)
    tw, th = (float(x) for x in a.trim.lower().split("x"))
    tkey = trim_key(tw, th)
    if a.what == "blurb-softcover":
        out = softcover_dims(tkey, a.paper or DEFAULT_BLURB_PAPER, a.pages)
    elif a.what == "blurb-imagewrap":
        out = imagewrap_dims(tkey, a.paper or DEFAULT_BLURB_PAPER, a.pages)
    else:
        spine = mixam_paperback_spine(a.pages, a.paper or "cream", a.override)
        out = mixam_paperback_wrap_dims(tw, th, spine)
        out.update({"pages": a.pages, "paper": a.paper or "cream"})
    print(json.dumps(out, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(_cli())
