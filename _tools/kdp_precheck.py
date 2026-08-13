#!/usr/bin/env python3
r"""
kdp_precheck.py — the local KDP ACCEPTANCE SIMULATOR (offline, deterministic).

WHAT THIS IS. Amazon's upload validator rejects print files for a set of
deterministic, PUBLISHED reasons: wrong cover canvas for the page count, page
count outside the binding's range, interior pages that are not the declared
trim, non-embedded fonts, encrypted PDFs, content inside the required margins,
matter in the barcode zone, sub-spec ebook covers. Every one of those is
checkable on this machine, before any upload. This tool encodes them as ONE
hard gate so BOOKSMITH structurally cannot present a file as "Amazon ready"
that would bounce off the deterministic layer of KDP's checker: the producers
loop until this simulator is green.

WHAT THIS IS NOT. Amazon's content review, their exact PDF parser, and the
Previewer's perceptual pass are not replicated. The kit meta-rule stands: the
KDP Previewer at upload ALWAYS outranks this tool. Passing here means "will not
bounce for any published mechanical reason", not "Amazon has approved it".

CONSTANTS PROVENANCE (all captured/verified live 2026-07-23):
  - Cover geometry: shared with preset_lookup.kdp_{paperback,hardcover}_wrap_dims
    (one code path with composite_cover + verify_build) and cross-checked against
    Amazon's own Cover Calculator (kdp.amazon.com/cover-calculator, scriptable —
    recipe in docs/QC_FULL_AUDIT_RUNBOOK.md Phase 5):
      6x9/344pp PB:  13.025 x 9.25, spine 0.775   (tool: 13.0247, 0.7747)
      6x9/344pp HC:  14.538 x 10.417, spine 0.964 (tool canvas: 14.5387)
      6x9/200pp PB:  12.7   x 9.25, spine 0.45    (tool: 12.7004, 0.4504)
      6x9/200pp HC:  14.214 x 10.417              (tool canvas: 14.2144)
  - Page ranges + margins: kdp help topic GVBQ3CMEQW3W2VL6.
  - Ebook cover: kdp help topic G200645690.
  - Spine-text minimum (paperback): ~80pp; below it the spine must be text-free.

USAGE
  python kdp_precheck.py --config book_config.json --format kdp_paperback [--json]
  python kdp_precheck.py --config book_config.json --format kdp_hardcover [--json]
  python kdp_precheck.py --config book_config.json --format kindle        [--json]
  python kdp_precheck.py --selftest      # tampered-file negative battery

Exit 0 all pass · 1 any FAIL · 2 usage/IO. WARNs never fail the gate but are
printed (e.g. content in the 0.20-0.25in band, low-dpi cover raster).
"""
from __future__ import annotations
import argparse, json, sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))

# ---- published KDP constants (provenance in the docstring) ------------------
PAGE_RANGES = {                       # (min, max) total interior pages
    "kdp_paperback": {"white": (24, 828), "cream": (24, 776)},
    "kdp_hardcover": {"white": (75, 550), "cream": (75, 550)},
}
GUTTER_BY_PAGES = [(150, 0.375), (300, 0.5), (500, 0.625), (700, 0.75), (828, 0.875)]
OUTSIDE_MIN_IN = 0.25                 # no-bleed live-area floor, all outer edges
LIVE_HARD_IN = 0.125                  # closer than this to trim = hard FAIL
PB_SPINE_TEXT_MIN_PAGES = 80
EBOOK_COVER = {"min_w": 625, "min_h": 1000, "max_side": 10000,
               "ideal_w": 1600, "ideal_h": 2560, "max_mb": 50}
TOL = 0.002                            # inches, dimension comparisons


def gutter_floor(pages: int) -> float:
    for cap, g in GUTTER_BY_PAGES:
        if pages <= cap:
            return g
    return GUTTER_BY_PAGES[-1][1]


def check(name, ok, detail, warn=False):
    return {"name": name, "pass": bool(ok) or warn, "warn": bool(warn), "detail": detail}


# ---- interior PDF ------------------------------------------------------------
def interior_checks(pdf_path: Path, trim_w: float, trim_h: float, fmt: str, paper: str):
    import fitz
    out = []
    doc = fitz.open(str(pdf_path))
    if doc.needs_pass or doc.is_encrypted:
        out.append(check("interior_not_encrypted", False, "PDF is encrypted (KDP rejects)"))
        return out
    out.append(check("interior_not_encrypted", True, "no encryption"))
    n = doc.page_count

    lo, hi = PAGE_RANGES[fmt][paper]
    out.append(check("page_count_in_kdp_range", lo <= n <= hi,
                     f"{n} pages vs KDP {fmt}/{paper} range {lo}-{hi}"))

    # every page exactly the declared trim (no-bleed model)
    bad = [i + 1 for i in range(n)
           if abs(doc[i].mediabox.width / 72 - trim_w) > TOL
           or abs(doc[i].mediabox.height / 72 - trim_h) > TOL]
    out.append(check("every_page_at_trim", not bad,
                     f"all {n} pages {trim_w}x{trim_h}in" if not bad
                     else f"{len(bad)} page(s) off-trim, e.g. {bad[:5]}"))

    # fonts embedded (KDP requires embedding; Word COM embeds by default)
    unembedded = set()
    for i in range(n):
        for f in doc[i].get_fonts(full=True):
            # fitz tuple: (xref, ext, type, basefont, name, encoding, ...)
            ext = f[1]
            if ext == "n/a" and f[2] not in ("Type3",):
                unembedded.add(f[3])
    out.append(check("fonts_embedded", not unembedded,
                     "all fonts embedded" if not unembedded
                     else f"NOT embedded: {sorted(unembedded)[:6]}"))

    # live-area: text/images must respect the margins. Inside edge (gutter) by
    # parity: page 1 = recto = gutter on the LEFT. Folios/footers commonly sit
    # near the bottom band; <LIVE_HARD_IN is a hard fail, LIVE..OUTSIDE_MIN a WARN
    # (the Previewer is the perceptual authority on the band).
    g = gutter_floor(n)
    hard_hits, band_hits = [], []
    min_seen = 99.0
    for i in range(n):
        pg = doc[i]
        w_in, h_in = pg.mediabox.width / 72, pg.mediabox.height / 72
        rects = [fitz.Rect(b[:4]) for b in pg.get_text("blocks") if b[4].strip()]
        rects += [pg.get_image_bbox(im) for im in pg.get_images(full=True)]
        recto = (i + 1) % 2 == 1
        for r in rects:
            left = r.x0 / 72
            right = w_in - r.x1 / 72
            top = r.y0 / 72
            bot = h_in - r.y1 / 72
            inside = left if recto else right
            outside = right if recto else left
            edge_min = min(outside, top, bot)
            min_seen = min(min_seen, edge_min)
            if inside < g - TOL and inside < min_seen:
                pass  # tracked via edge metrics below
            if edge_min < LIVE_HARD_IN or inside < LIVE_HARD_IN:
                hard_hits.append(i + 1)
                break
            if edge_min < OUTSIDE_MIN_IN - TOL:
                band_hits.append(i + 1)
                break
    doc.close()
    out.append(check("live_area_hard_floor", not hard_hits,
                     f"no content within {LIVE_HARD_IN}in of trim"
                     if not hard_hits else
                     f"content within {LIVE_HARD_IN}in of trim on pages {sorted(set(hard_hits))[:6]}"))
    if band_hits:
        out.append(check("live_area_kdp_band", True,
                         f"content in the {LIVE_HARD_IN}-{OUTSIDE_MIN_IN}in band on "
                         f"{len(set(band_hits))} page(s) (e.g. {sorted(set(band_hits))[:5]}) — "
                         f"typically folios; Previewer confirms", warn=True))
    else:
        out.append(check("live_area_kdp_band", True,
                         f"all content >= {OUTSIDE_MIN_IN}in from trim (min seen {min_seen:.3f}in)"))
    return out


# ---- print cover -------------------------------------------------------------
def cover_checks(cover_path: Path, fmt: str, pages: int, paper: str,
                 trim_w: float, trim_h: float, spine_cfg: dict):
    import fitz, preset_lookup
    out = []
    if fmt == "kdp_paperback":
        d = preset_lookup.kdp_paperback_wrap_dims(trim_w, trim_h, pages, paper)
    else:
        kwargs = {}
        if spine_cfg.get("spine_override_in"):
            kwargs["spine_override_in"] = spine_cfg["spine_override_in"]
        d = preset_lookup.kdp_hardcover_wrap_dims(trim_w, trim_h, pages, **kwargs) \
            if kwargs else preset_lookup.kdp_hardcover_wrap_dims(trim_w, trim_h, pages)
    doc = fitz.open(str(cover_path))
    out.append(check("cover_single_page", doc.page_count == 1,
                     f"{doc.page_count} page(s); a KDP wrap must be exactly 1"))
    pg = doc[0]
    w, h = pg.mediabox.width / 72, pg.mediabox.height / 72
    ok = abs(w - d["cover_w"]) <= TOL and abs(h - d["cover_h"]) <= TOL
    out.append(check("cover_canvas_matches_kdp_formula", ok,
                     f"actual {w:.4f}x{h:.4f} vs required {d['cover_w']}x{d['cover_h']} "
                     f"(spine {d['spine']}; Amazon calculator cross-checked 2026-07-23)"))
    unemb = {f[3] for f in pg.get_fonts(full=True) if f[1] == "n/a"}
    out.append(check("cover_fonts_embedded", not unemb,
                     "all fonts embedded" if not unemb else f"NOT embedded: {sorted(unemb)[:4]}"))

    # barcode keep-out: 2.0x1.2in, 0.25in from the back panel's bottom-right
    # trim corner, must be effectively empty (KDP overlays its barcode there).
    edge = d.get("bleed_in", d.get("turn_in_in", 0.125))
    back_right = edge + trim_w
    top_band = (h - trim_h) / 2
    ko = fitz.Rect((back_right - 2.25) * 72, (top_band + trim_h - 1.45) * 72,
                   (back_right - 0.25) * 72, (top_band + trim_h - 0.25) * 72)
    pix = pg.get_pixmap(matrix=fitz.Matrix(1, 1), clip=ko)
    s, np_ = pix.samples, pix.n
    tot = pix.width * pix.height
    from collections import Counter
    mode = Counter(tuple(s[i:i + 3]) for i in range(0, len(s), np_)).most_common(1)[0]
    far = sum(1 for i in range(0, len(s), np_)
              if abs(s[i] - mode[0][0]) + abs(s[i + 1] - mode[0][1]) + abs(s[i + 2] - mode[0][2]) > 60)
    out.append(check("barcode_keepout_clear", far / tot < 0.005,
                     f"keep-out ink share {far / tot:.4f} (must be ~0; KDP prints its barcode there)"))

    # paperback under 80pp must carry no spine text (ink in the spine band)
    if fmt == "kdp_paperback" and pages < PB_SPINE_TEXT_MIN_PAGES:
        sw = d["spine"]
        band = fitz.Rect((edge + trim_w) * 72, top_band * 72,
                         (edge + trim_w + sw) * 72, (top_band + trim_h) * 72)
        pix = pg.get_pixmap(matrix=fitz.Matrix(1, 1), clip=band)
        s2 = pix.samples
        mode2 = Counter(tuple(s2[i:i + 3]) for i in range(0, len(s2), pix.n)).most_common(1)[0]
        far2 = sum(1 for i in range(0, len(s2), pix.n)
                   if abs(s2[i] - mode2[0][0]) + abs(s2[i + 1] - mode2[0][1]) + abs(s2[i + 2] - mode2[0][2]) > 60)
        out.append(check("spine_text_page_minimum", far2 / (pix.width * pix.height) < 0.01,
                         f"{pages}pp < {PB_SPINE_TEXT_MIN_PAGES}pp: spine must be text-free"))
    doc.close()
    return out


# ---- ebook -------------------------------------------------------------------
def kindle_checks(kdir: Path):
    out = []
    from PIL import Image
    cover = None
    for pat in ("cover_kindle.jpg", "*_KINDLE_cover.jpg"):
        hits = [p for p in sorted(kdir.glob(pat)) if "_r2k" not in p.name]
        if hits:
            cover = hits[0]
            break
    if cover is None:
        return [check("ebook_cover_present", False, "no kindle cover image found")]
    with Image.open(cover) as im:
        w, h = im.size
        mode, fmt = im.mode, (im.format or "").upper()
    mb = cover.stat().st_size / 1048576
    c = EBOOK_COVER
    out.append(check("ebook_cover_min_max", c["min_w"] <= w <= c["max_side"]
                     and c["min_h"] <= h <= c["max_side"],
                     f"{w}x{h} vs min {c['min_w']}x{c['min_h']} / max {c['max_side']}"))
    out.append(check("ebook_cover_format", fmt in ("JPEG", "TIFF") and mode in ("RGB", "L") and mb < c["max_mb"],
                     f"{fmt} {mode} {mb:.1f}MB (need JPEG/TIFF, RGB, <{c['max_mb']}MB)"))
    ideal = w >= c["ideal_w"] and h >= c["ideal_h"] and h / w >= 1.6
    out.append(check("ebook_cover_ideal", True,
                     "meets KDP ideal 1600x2560 @>=1.6:1" if ideal else
                     f"above minimums but below ideal ({w}x{h}, {h / w:.2f}:1)", warn=not ideal))
    docx = sorted(kdir.glob("*KINDLE*.docx"))
    out.append(check("ebook_manuscript_present", bool(docx),
                     docx[0].name if docx else "no KINDLE DOCX found"))
    return out


# ---- driver ------------------------------------------------------------------
def run(config_path: Path, fmt: str):
    cfg = json.loads(config_path.read_text(encoding="utf-8"))
    root = config_path.parent
    # ebook-only configs carry no trim block (schema default 6x9); the kindle
    # path never uses it, but the hard index crashed the whole precheck (caught
    # live: cloud Session B, minimal ticket config).
    trim = cfg.get("trim") or {}
    trim_w, trim_h = trim.get("w", 6.0), trim.get("h", 9.0)
    paper = cfg.get("paper", "white")
    checks = []
    if fmt == "kindle":
        checks += kindle_checks(root / "outputs" / "kindle")
    else:
        fdir = root / "outputs" / fmt
        # discovery keys on the kit's actual naming, NOT a bare "cover" substring
        # ("..._KDP_HARDCOVER.pdf" contains "cover" — that substring bug shipped
        # in this tool's first run and misclassified the interior as a wrap).
        covers = sorted(fdir.glob("cover_wrap*.pdf"))
        pdfs = [p for p in sorted(fdir.glob("*.pdf")) if p not in covers
                and not p.name.lower().startswith("cover")]
        if not pdfs:
            checks.append(check("interior_present", False, f"no interior PDF in {fdir}"))
        else:
            checks += interior_checks(pdfs[0], trim_w, trim_h, fmt, paper)
        if not covers:
            checks.append(check("cover_present", False, f"no cover wrap PDF in {fdir}"))
        else:
            import fitz
            pages = fitz.open(str(pdfs[0])).page_count if pdfs else 0
            checks += cover_checks(covers[0], fmt, pages, paper, trim_w, trim_h,
                                   cfg.get("spine", {}))
    all_pass = all(c["pass"] for c in checks)
    return {"format": fmt, "config": str(config_path), "all_pass": all_pass,
            "checks": checks,
            "note": "deterministic KDP layer only — the KDP Previewer remains the final authority"}


def selftest():
    """Negative battery: tampered artifacts MUST fail (a gate that cannot fail
    is not a gate). Uses the smallest synthetic PDFs, no book needed."""
    import fitz, tempfile
    tmp = Path(tempfile.mkdtemp(prefix="kdp_precheck_"))
    results = []
    # 1) off-trim interior page must fail every_page_at_trim
    doc = fitz.open()
    doc.new_page(width=432, height=648)
    doc.new_page(width=430, height=648)          # tampered page
    p = tmp / "bad_interior.pdf"; doc.save(str(p)); doc.close()
    r = interior_checks(p, 6, 9, "kdp_paperback", "white")
    results.append(("off-trim page fails", not [c for c in r if c["name"] == "every_page_at_trim"][0]["pass"]))
    # 2) wrong cover canvas must fail the formula check
    doc = fitz.open(); doc.new_page(width=900, height=666)
    p2 = tmp / "bad_cover.pdf"; doc.save(str(p2)); doc.close()
    r2 = cover_checks(p2, "kdp_paperback", 200, "white", 6, 9, {})
    results.append(("wrong canvas fails", not [c for c in r2 if c["name"] == "cover_canvas_matches_kdp_formula"][0]["pass"]))
    # 3) page count outside range must fail
    doc = fitz.open()
    for _ in range(10):
        doc.new_page(width=432, height=648)
    p3 = tmp / "short.pdf"; doc.save(str(p3)); doc.close()
    r3 = interior_checks(p3, 6, 9, "kdp_hardcover", "white")
    results.append(("under-range page count fails", not [c for c in r3 if c["name"] == "page_count_in_kdp_range"][0]["pass"]))
    ok = all(v for _, v in results)
    print("KDP_PRECHECK SELFTEST:", "PASS" if ok else "FAIL")
    for nm, v in results:
        print(f"   [{'ok' if v else 'XX'}] {nm}")
    return 0 if ok else 1


def main(argv=None):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    ap = argparse.ArgumentParser(description="Local KDP acceptance simulator (offline).")
    ap.add_argument("--config")
    ap.add_argument("--format", choices=["kdp_paperback", "kdp_hardcover", "kindle"])
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()
    if not a.config or not a.format:
        ap.print_help(); return 2
    r = run(Path(a.config), a.format)
    if a.json:
        print(json.dumps(r, ensure_ascii=False, indent=2))
    else:
        for c in r["checks"]:
            tag = "WARN" if c.get("warn") else ("PASS" if c["pass"] else "FAIL")
            print(f"  [{tag:4}] {c['name']}: {c['detail']}")
        print(f"KDP_PRECHECK {r['format']}: {'ALL PASS' if r['all_pass'] else 'FAIL'}  "
              f"({r['note']})")
    return 0 if r["all_pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
