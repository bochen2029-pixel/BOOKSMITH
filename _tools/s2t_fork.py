#!/usr/bin/env python3
r"""
s2t_fork.py — fork a Simplified-Chinese BOOKSMITH workspace into a
Traditional-Chinese sibling (an EBOOK-ONLY edition; KDP supports Chinese
(Traditional) as eBook only and no Chinese in print — live-verified
2026-07-23, kdp help G200673300).

What it does (nothing in the SOURCE workspace is touched):
  - converts every units[] manuscript (H1 + body) via OpenCC into a new
    workspace book_workspace/<dst-slug>/manuscript/current/,
  - converts the config's title/subtitle/units[].title/dedication/
    epigraph/readers_note strings the same way; slug becomes <dst-slug>;
    formats are forced to ["kindle", "epub"],
  - copies images/ (mid-flow image files) so workspace-relative anchors
    keep resolving,
  - writes _S2T_AUDIT_LOG.md in the destination: per-unit sha256
    before/after, CJK char counts, length deltas, changed-char counts,
    tool + config provenance.

Conversion config (--opencc, default s2tw): Taiwan CHARACTER variants
(裡/為/…), with OpenCC's built-in phrase-level disambiguation for
ambiguous chars (发→發/髮 etc.) — but NOT s2twp, which localizes
vocabulary and would rewrite the author's wording. Alternatives: s2t
(orthodox variants, 裏), s2hk (Hong Kong).

Code fences (``` blocks) and standalone markdown image lines pass through
unconverted; ASCII is inherently unaffected.

Usage:
  python s2t_fork.py --src-config book_workspace/<slug>/book_config.json
                     --dst-slug <slug>_zht [--opencc s2tw] [--force] [--json]
Exit: 0 ok · 1 error · 2 usage.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import re
import shutil
import sys
from datetime import datetime
from pathlib import Path

MD_IMAGE_LINE = re.compile(r"^!\[[^\]]*\]\([^)\s]+\)\s*$")
FENCE = re.compile(r"^\s*```")


def sha256(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def cjk_count(s: str) -> int:
    return sum(1 for c in s if "一" <= c <= "鿿")


def convert_markdown(text: str, conv) -> str:
    """Convert prose lines; leave fenced code + standalone image lines as-is."""
    out = []
    in_fence = False
    for line in text.split("\n"):
        if FENCE.match(line):
            in_fence = not in_fence
            out.append(line)
            continue
        if in_fence or MD_IMAGE_LINE.match(line.strip()):
            out.append(line)
            continue
        out.append(conv.convert(line))
    return "\n".join(out)


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    ap = argparse.ArgumentParser()
    ap.add_argument("--src-config", required=True)
    ap.add_argument("--dst-slug", required=True)
    ap.add_argument("--opencc", default="s2tw",
                    help="OpenCC config: s2tw (default) | s2t | s2hk")
    ap.add_argument("--force", action="store_true",
                    help="allow writing into an existing destination workspace")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    try:
        from opencc import OpenCC
    except ImportError:
        print("s2t_fork: OpenCC missing — pip install opencc-python-reimplemented",
              file=sys.stderr)
        return 1
    conv = OpenCC(a.opencc)

    src_cfg_p = Path(a.src_config).resolve()
    cfg = json.loads(src_cfg_p.read_text(encoding="utf-8"))
    src_ws = src_cfg_p.parent
    dst_ws = src_ws.parent / a.dst_slug
    if dst_ws.exists() and not a.force:
        print(f"s2t_fork: destination exists: {dst_ws} (use --force)", file=sys.stderr)
        return 1
    (dst_ws / "manuscript" / "current").mkdir(parents=True, exist_ok=True)

    rows = []
    for u in cfg.get("units") or []:
        uid = u["id"]
        sp = src_ws / "manuscript" / "current" / f"{uid}_current.md"
        raw = sp.read_bytes()
        text = raw.decode("utf-8")
        conv_text = convert_markdown(text, conv)
        dp = dst_ws / "manuscript" / "current" / f"{uid}_current.md"
        dp.write_text(conv_text, encoding="utf-8")
        changed = (sum(1 for x, y in zip(text, conv_text) if x != y)
                   if len(text) == len(conv_text) else -1)
        rows.append({
            "id": uid, "src_sha256": sha256(raw),
            "dst_sha256": sha256(conv_text.encode("utf-8")),
            "src_cjk": cjk_count(text), "dst_cjk": cjk_count(conv_text),
            "len_delta": len(conv_text) - len(text), "chars_changed": changed,
        })
        u["title"] = conv.convert(u["title"])

    for key in ("title", "subtitle", "dedication", "readers_note"):
        if isinstance(cfg.get(key), str):
            cfg[key] = conv.convert(cfg[key])
    if isinstance((cfg.get("epigraph") or {}).get("text"), str):
        cfg["epigraph"]["text"] = conv.convert(cfg["epigraph"]["text"])
        if isinstance(cfg["epigraph"].get("attribution"), str):
            cfg["epigraph"]["attribution"] = conv.convert(cfg["epigraph"]["attribution"])
    cfg["slug"] = a.dst_slug
    cfg["formats"] = ["kindle", "epub"]
    cfg["genre"] = f"{cfg.get('genre', '')} [zh-Hant ebook edition]".strip()
    (dst_ws / "book_config.json").write_text(
        json.dumps(cfg, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    imgs = src_ws / "images"
    n_img = 0
    if imgs.is_dir():
        shutil.copytree(imgs, dst_ws / "images", dirs_exist_ok=True)
        n_img = sum(1 for _ in (dst_ws / "images").iterdir())

    try:
        import opencc as _oc
        oc_ver = getattr(_oc, "__version__", "unknown")
    except Exception:
        oc_ver = "unknown"
    log = [
        f"# _S2T_AUDIT_LOG — {cfg['title']} ({a.dst_slug})",
        "",
        f"- Generated: {datetime.now().isoformat(timespec='seconds')}",
        f"- Tool: _tools/s2t_fork.py · OpenCC config **{a.opencc}** "
        f"(character variants only; NO vocabulary localization) · "
        f"opencc-python-reimplemented {oc_ver}",
        f"- Source workspace: {src_ws}",
        f"- KDP facts (live-verified 2026-07-23, help G200673300): Chinese "
        f"(Simplified) unsupported in every format; Chinese (Traditional) "
        f"eBook ONLY — hence formats forced to kindle+epub.",
        f"- Images copied: {n_img}",
        "",
        "| unit | len Δ | chars changed | src CJK | dst CJK | src sha256 (12) | dst sha256 (12) |",
        "|---|---|---|---|---|---|---|",
    ]
    for r in rows:
        log.append(f"| {r['id']} | {r['len_delta']} | {r['chars_changed']} "
                   f"| {r['src_cjk']} | {r['dst_cjk']} "
                   f"| {r['src_sha256'][:12]} | {r['dst_sha256'][:12]} |")
    tot_changed = sum(r["chars_changed"] for r in rows if r["chars_changed"] >= 0)
    log.append("")
    log.append(f"Totals: units {len(rows)} · chars changed {tot_changed} · "
               f"len deltas nonzero: {sum(1 for r in rows if r['len_delta'])}")
    (dst_ws / "_S2T_AUDIT_LOG.md").write_text("\n".join(log) + "\n", encoding="utf-8")

    summary = {
        "dst_workspace": str(dst_ws), "units": len(rows),
        "chars_changed_total": tot_changed,
        "units_with_len_delta": sum(1 for r in rows if r["len_delta"]),
        "images_copied": n_img, "opencc": a.opencc,
        "audit_log": str(dst_ws / "_S2T_AUDIT_LOG.md"),
    }
    print(json.dumps(summary, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
