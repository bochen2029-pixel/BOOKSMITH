#!/usr/bin/env python3
r"""
pdf_replica_fit.py — page-REPLICA re-fit of a finished PDF onto a KDP trim.

THE OTHER reimport route. `pdf_to_book.py` extracts CONTENT and discards layout
(re-typeset to spec). This tool PRESERVES the layout: every source page is kept
as rendered — exact fonts (embedded subsets ride along), colors, line breaks,
folios, images — and only the PAGE GEOMETRY is re-fitted to a KDP trim with
compliant margins. Use it when the order is "replica clone, change nothing"
(e.g. re-issuing an author's own already-typeset book).

THE MECHANISM — margin-swap, not page-in-page:
  1. Measure the source CONTENT BOX (percentile bbox of text+image blocks across
     body pages; a finished book's own margins are usually generous — the DRDJ
     books carry ~1.0in margins around a 5.3x8.7in content box on a 7.25x10.24
     page, so a 6x9 re-fit needs only ~95% scale instead of the naive 72%).
  2. Build the TARGET content box: trim minus KDP-compliant margins (gutter by
     final page count per the KDP table, mirrored recto/verso; outside/top/
     bottom floors with a folio allowance at the bottom).
  3. Place each source page's content box into the target box at one uniform
     scale (min of width/height ratios), centered, via show_pdf_page with a
     clip — vector-perfect, no rasterization, fonts stay embedded.
  4. Pad to the page-count multiple (blank pages at trim size).

KDP gutter table (inside margin minimum, in): 24-150pp 0.375 · 151-300 0.5 ·
301-500 0.625 · 501-700 0.75 · 701-828 0.875. Outside/top/bottom minimum 0.25
(no bleed). Defaults here add safety: outside/top 0.3, bottom 0.35, gutter
table+0.05. (Live-verified 2026-07-23, kdp help GVBQ3CMEQW3W2VL6.)

WHAT THIS DOES NOT DO: touch the text layer (Kangxi-radical ToUnicode quirks
in the source stay in the source — they only matter for the reflowable-ebook
route, which uses extraction + normalization, not this tool); build covers;
OCR scans. Blank/near-blank source pages are kept (replica).

USAGE
  python pdf_replica_fit.py <book.pdf> --out-dir DIR [--trim 6x9] [--skip-front 1]
      [--skip-back 0] [--gutter G] [--outside O] [--top T] [--bottom B]
      [--pad-multiple 2] [--sample "12,40,120"] [--json]
  python pdf_replica_fit.py --selftest
"""
from __future__ import annotations
import argparse, json, sys
from pathlib import Path

GUTTER_TABLE = [(150, 0.375), (300, 0.5), (500, 0.625), (700, 0.75), (828, 0.875)]
SAFETY = 0.05


def u8():
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


def kdp_gutter(pages: int) -> float:
    for lim, g in GUTTER_TABLE:
        if pages <= lim:
            return g
    return GUTTER_TABLE[-1][1]


def content_bbox(doc, skip_front, skip_back, lo_q=0.05, hi_q=0.95):
    """Global content box (pts) from per-page text+image bounds at percentiles —
    robust to outlier furniture while keeping folios/running heads inside."""
    import fitz
    xs0, ys0, xs1, ys1 = [], [], [], []
    n = doc.page_count
    for i in range(skip_front, n - skip_back):
        pg = doc[i]
        boxes = [w[:4] for w in pg.get_text("words")]
        for im in pg.get_images(full=True):
            try:
                r = pg.get_image_bbox(im)
                boxes.append((r.x0, r.y0, r.x1, r.y1))
            except Exception:
                pass
        boxes = [b for b in boxes if b[2] > b[0] and b[3] > b[1]]
        if not boxes:
            continue
        xs0.append(min(b[0] for b in boxes)); ys0.append(min(b[1] for b in boxes))
        xs1.append(max(b[2] for b in boxes)); ys1.append(max(b[3] for b in boxes))
    if not xs0:
        r = doc[0].rect
        return fitz.Rect(r)
    q = lambda v, k: sorted(v)[int(k * (len(v) - 1))]
    return fitz.Rect(q(xs0, lo_q), q(ys0, lo_q), q(xs1, hi_q), q(ys1, hi_q))


def run(pdf: Path, out_dir: Path, trim, skip_front, skip_back,
        gutter, outside, top, bottom, pad_multiple, sample, as_json):
    import fitz
    tw, th = trim
    src = fitz.open(str(pdf))
    kept = src.page_count - skip_front - skip_back
    final_pages_est = kept + (-kept % pad_multiple if pad_multiple > 1 else 0)
    g = gutter if gutter is not None else round(kdp_gutter(final_pages_est) + SAFETY, 3)
    o = outside if outside is not None else 0.3
    t = top if top is not None else 0.3
    b = bottom if bottom is not None else 0.35

    cbox = content_bbox(src, skip_front, skip_back)
    avail_w = tw - g - o
    avail_h = th - t - b
    s = min(avail_w * 72 / cbox.width, avail_h * 72 / cbox.height)
    if s > 1.0:
        s = min(s, 1.0)          # replica never upscales (soft rule: keep <=100%)
    placed_w, placed_h = cbox.width * s, cbox.height * s
    slack_w = avail_w * 72 - placed_w
    slack_h = avail_h * 72 - placed_h

    out = fitz.open()
    for k, i in enumerate(range(skip_front, src.page_count - skip_back)):
        page = out.new_page(width=tw * 72, height=th * 72)
        recto = (k + 1) % 2 == 1                       # output page 1 = recto
        left = (g if recto else o) * 72 + slack_w / 2
        top_off = t * 72 + slack_h / 2
        target = fitz.Rect(left, top_off, left + placed_w, top_off + placed_h)
        page.show_pdf_page(target, src, i, clip=cbox)
    while pad_multiple > 1 and out.page_count % pad_multiple != 0:
        out.new_page(width=tw * 72, height=th * 72)

    out_dir.mkdir(parents=True, exist_ok=True)
    stem = pdf.stem.replace(" ", "_")
    dst = out_dir / f"{stem}_REPLICA_{tw}x{th}.pdf"
    out.save(str(dst), deflate=True, garbage=3)

    report = {
        "source": str(pdf), "output": str(dst),
        "trim": {"w": tw, "h": th},
        "pages_in": src.page_count, "skip_front": skip_front, "skip_back": skip_back,
        "pages_out": out.page_count,
        "scale": round(s, 4),
        "content_box_in": [round(v / 72, 3) for v in (cbox.x0, cbox.y0, cbox.x1, cbox.y1)],
        "content_size_in": [round(cbox.width / 72, 3), round(cbox.height / 72, 3)],
        "margins_in": {"gutter": g, "outside": o, "top": t, "bottom": b,
                       "achieved_gutter": round(g + slack_w / 144, 3),
                       "achieved_top": round(t + slack_h / 144, 3)},
        "kdp_gutter_required": kdp_gutter(out.page_count),
        "gutter_ok": (g + slack_w / 144) >= kdp_gutter(out.page_count),
        "page_multiple_ok": pad_multiple <= 1 or out.page_count % pad_multiple == 0,
        "fonts_preserved": True,   # vector show_pdf_page: embedded subsets carried over
    }

    samples = []
    if sample:
        sdir = out_dir / "replica_samples"
        sdir.mkdir(exist_ok=True)
        for p in sample:
            si = p - 1 + skip_front               # source index for output page p
            if not (0 <= si < src.page_count and 1 <= p <= out.page_count):
                continue
            m = fitz.Matrix(150 / 72, 150 / 72)
            a = src[si].get_pixmap(matrix=m)
            bpx = out[p - 1].get_pixmap(matrix=m)
            from PIL import Image
            ia = Image.frombytes("RGB", (a.width, a.height), a.samples)
            ib = Image.frombytes("RGB", (bpx.width, bpx.height), bpx.samples)
            h = max(ia.height, ib.height)
            combo = Image.new("RGB", (ia.width + ib.width + 24, h), (245, 245, 245))
            combo.paste(ia, (0, 0)); combo.paste(ib, (ia.width + 24, 0))
            combo.thumbnail((2000, 2000), Image.LANCZOS)
            f = sdir / f"{stem}_{tw}x{th}_p{p:03d}_AB.png"
            combo.save(f)
            samples.append(str(f))
    report["samples"] = samples
    src.close(); out.close()
    print(json.dumps(report, ensure_ascii=False, indent=2) if as_json else
          f"REPLICA: {report['pages_out']}pp @ {tw}x{th} scale {report['scale']}  "
          f"gutter_ok={report['gutter_ok']} -> {dst}")
    return report


def selftest():
    """Synthesize a 2-page book with known content bounds; re-fit to 6x9; assert
    page count (pad to 2), scale < 1, gutter compliance, and vector text survives."""
    import fitz, tempfile
    tmp = Path(tempfile.mkdtemp())
    doc = fitz.open()
    for k in range(3):
        pg = doc.new_page(width=522, height=737)      # 7.25 x 10.24
        pg.insert_text((72, 100), f"Page {k+1} heading", fontsize=16)
        pg.insert_text((72, 300), "Body text well inside one-inch margins.", fontsize=11)
        pg.insert_text((260, 700), str(k + 1), fontsize=9)
    p = tmp / "src.pdf"
    doc.save(str(p)); doc.close()
    r = run(p, tmp / "out", (6, 9), 1, 0, None, None, None, None, 2, [], False)
    out = fitz.open(r["output"])
    text_ok = "Body text well inside" in out[0].get_text()
    checks = {
        "skip_front applied (2 kept -> pad to 2)": r["pages_out"] == 2,
        "scale <= 1": 0.5 < r["scale"] <= 1.0,
        "gutter ok": r["gutter_ok"],
        "page multiple ok": r["page_multiple_ok"],
        "vector text survives": text_ok,
    }
    out.close()
    ok = all(checks.values())
    print("PDF_REPLICA_FIT SELFTEST:", "PASS" if ok else "FAIL")
    for k, v in checks.items():
        print(f"   [{'ok' if v else 'XX'}] {k}")
    return 0 if ok else 1


def main(argv=None):
    u8()
    ap = argparse.ArgumentParser(description="Page-replica re-fit of a finished PDF onto a KDP trim.")
    ap.add_argument("pdf", nargs="?")
    ap.add_argument("--out-dir", default=".")
    ap.add_argument("--trim", default="6x9", help="6x9 | 7x10 | WxH")
    ap.add_argument("--skip-front", type=int, default=0, help="leading pages to drop (e.g. the cover)")
    ap.add_argument("--skip-back", type=int, default=0)
    ap.add_argument("--gutter", type=float); ap.add_argument("--outside", type=float)
    ap.add_argument("--top", type=float); ap.add_argument("--bottom", type=float)
    ap.add_argument("--pad-multiple", type=int, default=2)
    ap.add_argument("--sample", default="", help="comma list of OUTPUT page numbers to render A/B")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()
    if not a.pdf:
        ap.print_help(); return 2
    tw, th = (float(x) for x in a.trim.lower().replace("×", "x").split("x"))
    sample = [int(x) for x in a.sample.split(",") if x.strip()] if a.sample else []
    run(Path(a.pdf), Path(a.out_dir), (tw, th), a.skip_front, a.skip_back,
        a.gutter, a.outside, a.top, a.bottom, a.pad_multiple, sample, a.json)
    return 0


if __name__ == "__main__":
    sys.exit(main())
