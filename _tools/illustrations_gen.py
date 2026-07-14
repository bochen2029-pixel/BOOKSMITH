#!/usr/bin/env python3
"""
illustrations_gen.py - chapter-opener illustration batch driver (BOOKSMITH).

Drives the vendored comfy_client (SDXL via ComfyUI) over a briefs.json to
produce N candidates per chapter, entirely on disk, crash/rewind-safe:
the manifest is rewritten after EVERY image, so a fresh session (or a
context-rewound one) resumes by reading the manifest - never by regenerating.

Layout (all under <workspace>/cover_art/illustrations/):
  briefs.json                       the input (style + per-chapter subjects)
  candidates/<id>_c<k>_s<seed>.png  raw generations
  live/<id>.png                     the picked+post-processed image per chapter
                                    (the dir the generators inject from)
  contact_sheets/sheet_<n>.png      curation grids (<=2000px, safe to view)
  illustrations_manifest.json       full state: brief/prompt/seed/file/status

Usage:
  python illustrations_gen.py --config <book_config.json> [--candidates 4]
        [--only ch_01,ch_02] [--generate] [--contact-sheets] [--pick]
Steps are independent and idempotent: --generate skips chapters that already
have all candidates; --pick only fills empty live slots unless --repick.
"""
import argparse
import json
import shutil
import sys
import tempfile
import time
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
sys.path.insert(0, str(TOOLS))
import comfy_client  # noqa: E402  (vendored beside this file)

from PIL import Image, ImageOps  # noqa: E402


def load_json(p: Path):
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def save_json(p: Path, obj):
    tmp = p.with_suffix(".tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2)
    tmp.replace(p)


def kit_env():
    return load_json(TOOLS / "kit_env.json")


def ink_coverage(img: Image.Image) -> float:
    """Fraction of pixels darker than mid-gray (proxy for ink density)."""
    g = img.convert("L").resize((256, 256))
    hist = g.histogram()
    dark = sum(hist[:128])
    return dark / (256 * 256)


def postprocess(src: Path, dst: Path):
    """Print-safe cleanup: grayscale, gentle autocontrast, white point lifted
    so the paper field prints as true white (no gray wash), ink stays ink."""
    img = Image.open(src).convert("L")
    img = ImageOps.autocontrast(img, cutoff=1)
    lut = [0 if v < 8 else (255 if v > 235 else int((v - 8) * 255 / (235 - 8)))
           for v in range(256)]
    img = img.point(lut)
    dst.parent.mkdir(parents=True, exist_ok=True)
    img.save(dst, optimize=True)


def generate(ws: Path, briefs: dict, manifest_path: Path, candidates_n: int,
             only: set[str] | None):
    env = kit_env()
    cg = env.get("cover_gen", {})
    server = cg.get("comfyui_server", "http://127.0.0.1:8188")
    wf_path = Path(cg.get("workflows_dir", "")) / "sdxl_txt2img.json"
    checkpoint = cg.get("default_checkpoint", "sd_xl_base_1.0.safetensors")

    client = comfy_client.ComfyClient(server)
    if not client.server_up():
        print(json.dumps({"status": "error",
                          "error": f"ComfyUI not reachable at {server}"}))
        sys.exit(1)
    workflow = comfy_client._load_workflow(str(wf_path))

    ill_dir = ws / "cover_art" / "illustrations"
    cand_dir = ill_dir / "candidates"
    cand_dir.mkdir(parents=True, exist_ok=True)

    manifest = load_json(manifest_path) if manifest_path.exists() else {
        "style_prefix": briefs["style_prefix"], "negative": briefs["negative"],
        "width": briefs["width"], "height": briefs["height"],
        "steps": briefs["steps"], "chapters": {}}

    chapters = briefs["chapters"]
    seed_base = int(briefs.get("seed_base", 774000))
    ids = [i for i in chapters if not only or i in only]

    for ci, cid in enumerate(ids):
        entry = manifest["chapters"].setdefault(
            cid, {"brief": chapters[cid], "candidates": [], "pick": None})
        have = {c["k"] for c in entry["candidates"] if c.get("status") == "ok"}
        for k in range(candidates_n):
            if k in have:
                continue
            seed = seed_base + list(chapters).index(cid) * 100 + k
            prompt = f"{chapters[cid]}, {briefs['style_prefix']}"
            args_obj = {"prompt": prompt, "negative_prompt": briefs["negative"],
                        "seed": seed, "steps": briefs["steps"],
                        "width": briefs["width"], "height": briefs["height"],
                        "checkpoint": checkpoint}
            t0 = time.time()
            with tempfile.TemporaryDirectory() as td:
                result, code = comfy_client.run_single(
                    client, workflow, args_obj, Path(td))
                pngs = sorted(Path(td).glob("**/*.png"))
                if code != 0 or not pngs:
                    entry["candidates"].append(
                        {"k": k, "seed": seed, "status": "error",
                         "error": str(result)[:400]})
                    save_json(manifest_path, manifest)
                    print(f"[gen] {cid} c{k} ERROR ({str(result)[:120]})")
                    continue
                out = cand_dir / f"{cid}_c{k}_s{seed}.png"
                shutil.copy2(pngs[0], out)
            cov = ink_coverage(Image.open(out))
            entry["candidates"].append(
                {"k": k, "seed": seed, "status": "ok",
                 "file": str(out.relative_to(ill_dir)).replace("\\", "/"),
                 "ink": round(cov, 4), "secs": round(time.time() - t0, 1)})
            save_json(manifest_path, manifest)
            print(f"[gen] {cid} c{k} ok  ink={cov:.2f}  "
                  f"{time.time() - t0:.0f}s  ({ci + 1}/{len(ids)} chapters)")
    print("[gen] DONE")


def contact_sheets(ws: Path, manifest_path: Path, per_sheet: int = 6):
    ill_dir = ws / "cover_art" / "illustrations"
    manifest = load_json(manifest_path)
    sheets_dir = ill_dir / "contact_sheets"
    sheets_dir.mkdir(parents=True, exist_ok=True)
    ids = list(manifest["chapters"])
    thumb_w = 480
    made = []
    for si in range(0, len(ids), per_sheet):
        group = ids[si:si + per_sheet]
        rows = []
        for cid in group:
            cands = [c for c in manifest["chapters"][cid]["candidates"]
                     if c.get("status") == "ok"]
            row = []
            for c in cands:
                img = Image.open(ill_dir / c["file"]).convert("L")
                h = int(thumb_w * img.height / img.width)
                row.append(img.resize((thumb_w, h)))
            if row:
                rows.append((cid, row))
        if not rows:
            continue
        cols = max(len(r) for _, r in rows)
        cell_h = max(im.height for _, r in rows for im in r) + 8
        sheet = Image.new("L", (cols * (thumb_w + 8) + 8,
                                len(rows) * (cell_h + 8) + 8), 255)
        for ri, (cid, row) in enumerate(rows):
            for kx, im in enumerate(row):
                sheet.paste(im, (8 + kx * (thumb_w + 8), 8 + ri * (cell_h + 8)))
        if sheet.width > 2000:
            f = 2000 / sheet.width
            sheet = sheet.resize((2000, int(sheet.height * f)))
        outp = sheets_dir / f"sheet_{si // per_sheet + 1}.png"
        sheet.save(outp, optimize=True)
        made.append({"sheet": outp.name, "chapters": [cid for cid, _ in rows]})
        print(f"[sheet] {outp.name}: {', '.join(cid for cid, _ in rows)}")
    save_json(sheets_dir / "sheets_index.json", made)


def pick(ws: Path, manifest_path: Path, repick: bool, target_ink: float = 0.16):
    ill_dir = ws / "cover_art" / "illustrations"
    live = ill_dir / "live"
    manifest = load_json(manifest_path)
    for cid, entry in manifest["chapters"].items():
        if entry.get("pick") and not repick:
            continue
        ok = [c for c in entry["candidates"] if c.get("status") == "ok"]
        usable = [c for c in ok if 0.04 <= c.get("ink", 0) <= 0.55]
        pool = usable or ok
        if not pool:
            print(f"[pick] {cid}: no candidates")
            continue
        best = min(pool, key=lambda c: abs(c.get("ink", 0) - target_ink))
        postprocess(ill_dir / best["file"], live / f"{cid}.png")
        entry["pick"] = {"k": best["k"], "seed": best["seed"],
                         "file": best["file"], "auto": True}
        save_json(manifest_path, manifest)
        print(f"[pick] {cid}: c{best['k']} (ink={best.get('ink')}) -> live/{cid}.png")
    print("[pick] DONE")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    ap.add_argument("--briefs", default=None)
    ap.add_argument("--candidates", type=int, default=4)
    ap.add_argument("--only", default=None)
    ap.add_argument("--generate", action="store_true")
    ap.add_argument("--contact-sheets", action="store_true")
    ap.add_argument("--pick", action="store_true")
    ap.add_argument("--repick", action="store_true")
    a = ap.parse_args()

    ws = Path(a.config).resolve().parent
    ill_dir = ws / "cover_art" / "illustrations"
    briefs_path = Path(a.briefs) if a.briefs else ill_dir / "briefs.json"
    manifest_path = ill_dir / "illustrations_manifest.json"
    only = set(a.only.split(",")) if a.only else None

    if a.generate:
        generate(ws, load_json(briefs_path), manifest_path, a.candidates, only)
    if a.contact_sheets:
        contact_sheets(ws, manifest_path)
    if a.pick or a.repick:
        pick(ws, manifest_path, a.repick)
    if not (a.generate or a.contact_sheets or a.pick or a.repick):
        print("nothing to do: pass --generate / --contact-sheets / --pick")


if __name__ == "__main__":
    main()
