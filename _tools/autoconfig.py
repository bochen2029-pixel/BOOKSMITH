#!/usr/bin/env python3
r"""
autoconfig.py — write a machine-correct _tools/kit_env.json by DETECTION.

Makes BOOKSMITH "just work" when the folder is copied to a new machine: no manual
path editing. Starts from kit_env.template.json, fills in what it can detect
(node, python, ComfyUI app + checkpoints, GPU, fonts), sets the keyless
in-Claude-Code defaults (model.backend=harness, vision.backend=claude), backs up
any existing kit_env.json, and writes the result. Then prints what it found and
what it could not, with a one-line remedy per gap.

Never destructive: an existing kit_env.json is copied to kit_env.json.bak first.
Portable: stdlib only, tracebacks never escape.

Usage:
  python _tools/autoconfig.py            # detect + write kit_env.json (backs up any existing)
  python _tools/autoconfig.py --dry-run  # detect + print, write nothing
  python _tools/autoconfig.py --stdout   # print the resulting JSON to stdout
"""
from __future__ import annotations
import argparse, json, os, shutil, sys
from datetime import datetime
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
ROOT = TOOLS.parent
TEMPLATE = TOOLS / "kit_env.template.json"
TARGET = TOOLS / "kit_env.json"

found: list[str] = []
gaps: list[str] = []


def which(exe):
    return shutil.which(exe)


def first_existing(cands):
    for c in cands:
        try:
            if c and Path(c).exists():
                return str(Path(c))
        except Exception:
            pass
    return ""


def detect_comfy_app():
    la = os.environ.get("LOCALAPPDATA", "")
    home = Path.home()
    cands = [
        Path(la) / "Programs" / "ComfyUI" if la else None,
        home / "Documents" / "ComfyUI",
        Path("C:/ComfyUI"),
        Path(os.environ.get("PROGRAMFILES", "C:/Program Files")) / "ComfyUI",
        home / "ComfyUI",
    ]
    return first_existing([str(c) for c in cands if c])


def probe_comfy_server():
    """Probe for a LIVE ComfyUI on the two ports it actually uses: :8000 (the desktop
    app) and :8188 (the portable / manual launch). Returns (base_url, port) for the
    first that answers ComfyUI's /system_stats, else (None, None). Fixes the kit_env
    default that assumed :8188 while the desktop app serves :8000."""
    import urllib.request
    for port in (8000, 8188):
        base = f"http://127.0.0.1:{port}"
        try:
            with urllib.request.urlopen(base + "/system_stats", timeout=1.5) as r:
                if getattr(r, "status", 200) == 200:
                    return base, port
        except Exception:
            continue
    return None, None


def detect_checkpoints(comfy_app):
    home = Path.home()
    cands = []
    if comfy_app:
        cands += [Path(comfy_app) / "models" / "checkpoints",
                  Path(comfy_app) / "ComfyUI" / "models" / "checkpoints"]
    cands += [home / "Documents" / "ComfyUI" / "models" / "checkpoints"]
    hit = first_existing([str(c) for c in cands])
    if hit:
        return hit
    # return the most likely intended path even if absent, so fetch_weights has a target
    return str(cands[0]) if cands else ""


def build():
    try:
        env = json.loads(TEMPLATE.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"cannot read template {TEMPLATE}: {e}", file=sys.stderr)
        return None

    # --- runtimes ---
    node = which("node")
    if node:
        env["node"]["bin"] = node
        found.append(f"node: {node}")
    else:
        gaps.append("node NOT found on PATH -> install Node >= 14 (interior DOCX generators need it)")
    py = sys.executable or which("python") or "python"
    env["python"]["bin"] = py
    found.append(f"python: {py}")

    # --- Word / print tier (light probe; doctor.py does the authoritative COM check) ---
    if sys.platform == "win32":
        env["word"]["backend"] = "com"
        found.append("platform win32 -> Word COM print tier assumed (run doctor.py to confirm Word is installed)")
    else:
        env["word"]["backend"] = "none"
        soff = which("soffice") or which("libreoffice")
        if soff:
            found.append(f"platform {sys.platform}: no Word COM, but LibreOffice present ({soff}) "
                         "-> Tier-2 print PDFs via the docx_to_pdf soffice fallback (best-effort, not page-faithful)")
        else:
            gaps.append(f"platform {sys.platform}: no Word COM -> Tier 2 (EPUB/Kindle/digital). "
                        "Install LibreOffice for best-effort print PDFs (docx_to_pdf auto-detects 'soffice').")

    # --- fonts (vendored, repo-relative) ---
    env["fonts_dir"] = "fonts"
    if (ROOT / "fonts" / "CormorantGaramond-Light.ttf").exists():
        found.append("fonts: vendored CormorantGaramond present")
    else:
        gaps.append("vendored fonts missing under fonts/ -> the folder copy is incomplete")

    # --- cover art (optional; vendored client is the default runner) ---
    cg = env.get("cover_gen", {})
    cg["run_workflow"] = "_tools/comfy_client.py"
    cg["workflows_dir"] = "_tools/workflows"
    srv, port = probe_comfy_server()
    if srv:
        cg["comfyui_server"] = srv
        found.append(f"ComfyUI server: LIVE on {srv} (probed :8000 desktop / :8188 portable)")
    else:
        # not running at config time: keep the portable default but SAY so —
        # an unprobed port must not read like a verified value
        cg["comfyui_server"] = cg.get("comfyui_server") or "http://127.0.0.1:8188"
        gaps.append(f"ComfyUI not RUNNING during autoconfig -> comfyui_server left at "
                    f"{cg['comfyui_server']} (unprobed guess; desktop app serves :8000, "
                    "portable :8188). cover_gen live-probes both at run time; re-run "
                    "autoconfig with ComfyUI up to pin the real port.")
    app = detect_comfy_app()
    if app:
        cg["comfyui_app"] = app
        found.append(f"ComfyUI app: {app}")
    else:
        gaps.append("ComfyUI not found -> AI cover art disabled; place your own art in cover_art/ "
                    "(compositing + verification still work). Install ComfyUI to enable generation.")
    ck = detect_checkpoints(app)
    if ck:
        cg["checkpoints_dir"] = ck
        has_ckpt = Path(ck).exists() and any(Path(ck).glob("*.safetensors"))
        found.append(f"checkpoints dir: {ck}" + ("" if has_ckpt else " (empty -> run: python _tools/fetch_weights.py sdxl)"))
    env["cover_gen"] = cg

    # GPU note
    if which("nvidia-smi"):
        found.append("GPU: nvidia-smi present (SDXL cover generation viable)")
    else:
        gaps.append("no nvidia-smi -> no detectable NVIDIA GPU; cover ART generation needs one "
                    "(everything else runs CPU-only)")

    # --- vision: portable default is the harness's own vision ---
    env.setdefault("vision", {})["backend"] = "claude"
    found.append("vision backend -> claude (harness vision; zero setup)")

    # --- model seam: keyless in-Claude-Code default ---
    env.setdefault("model", {})
    env["model"]["backend"] = "harness"
    found.append("model backend -> harness (keyless; prose comes from the Claude Code session running the engine)")

    # --- organs: leave empty (portable fallbacks) ---
    return env


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Write a machine-correct kit_env.json by detection.")
    ap.add_argument("--dry-run", action="store_true", help="detect + report, write nothing")
    ap.add_argument("--stdout", action="store_true", help="print the resulting JSON")
    ap.add_argument("--force", action="store_true", help="(kept for symmetry; writing always backs up first)")
    args = ap.parse_args(argv)

    env = build()
    if env is None:
        return 1

    print("=== BOOKSMITH autoconfig ===")
    for f in found:
        print("  [ok]  " + f)
    for g in gaps:
        print("  [--]  " + g)

    if args.stdout:
        print("\n" + json.dumps(env, indent=2, ensure_ascii=False))
    if args.dry_run:
        print("\n(dry-run: kit_env.json NOT written)")
        return 0

    if TARGET.exists():
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        bak = TARGET.with_suffix(f".json.bak_{stamp}")
        try:
            shutil.copy2(TARGET, bak)
            print(f"\n  backed up existing kit_env.json -> {bak.name}")
        except Exception as e:
            print(f"\n  WARNING: could not back up existing kit_env.json ({e}); aborting to avoid data loss",
                  file=sys.stderr)
            return 1
    try:
        TARGET.write_text(json.dumps(env, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"  wrote {TARGET}")
    except Exception as e:
        print(f"  ERROR writing kit_env.json: {e}", file=sys.stderr)
        return 1
    print("\nNext: python _tools/doctor.py   (confirms Word/GPU/ComfyUI capability + your tier)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
