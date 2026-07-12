#!/usr/bin/env python3
r"""
cover_setup.py — get this machine cover-ready in one command.

Orchestrates the pieces that already exist so AI cover-ART generation "just
works", and degrades gracefully when it cannot:

  1. GPU present?            (nvidia-smi)
  2. SDXL checkpoint present? else fetch it        (_tools/fetch_weights.py sdxl, resumable)
  3. ComfyUI reachable?      else launch it (comfy-cli), or print the exact command

Report-only by default (safe: touches nothing). Pass --fetch to actually download
the checkpoint if missing, --launch to actually start ComfyUI if it is down.

No GPU / no ComfyUI is NOT an error: put your own art in the book's cover_art/
folder and composite_cover.py + vision_verify.py still work on any machine.

stdlib only; never tracebacks.
"""
from __future__ import annotations
import argparse, json, shutil, subprocess, sys, urllib.request
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
ROOT = TOOLS.parent


def kit_env() -> dict:
    for c in (TOOLS / "kit_env.json", TOOLS / "kit_env.template.json"):
        if c.exists():
            try:
                return json.loads(c.read_text(encoding="utf-8"))
            except Exception:
                pass
    return {}


def reachable(url: str, timeout=3) -> bool:
    for path in ("/system_stats", "/"):
        try:
            with urllib.request.urlopen(url.rstrip("/") + path, timeout=timeout) as r:
                if r.status < 500:
                    return True
        except Exception:
            continue
    return False


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Get this machine cover-ready (report-only by default).")
    ap.add_argument("--fetch", action="store_true", help="download the SDXL checkpoint if missing")
    ap.add_argument("--launch", action="store_true", help="launch ComfyUI if it is not reachable")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)

    env = kit_env()
    cg = env.get("cover_gen", {}) if isinstance(env.get("cover_gen"), dict) else {}
    steps = []            # (name, status, detail)  status in ready/fixable/blocked/skip
    actions = []

    # 1. GPU
    gpu = shutil.which("nvidia-smi")
    steps.append(("gpu", "ready" if gpu else "blocked",
                  "nvidia-smi present" if gpu else "no NVIDIA GPU detected -> AI art unavailable; supply your own art in cover_art/"))

    # 2. checkpoint
    ckdir = cg.get("checkpoints_dir") or ""
    ckname = cg.get("default_checkpoint") or "sd_xl_base_1.0.safetensors"
    ckpath = Path(ckdir) / ckname if ckdir else None
    if ckpath and ckpath.exists():
        steps.append(("checkpoint", "ready", f"{ckname} present in {ckdir}"))
    else:
        steps.append(("checkpoint", "fixable",
                      f"{ckname} not found ({ckdir or 'checkpoints_dir unset'}) -> "
                      f"fetch: python _tools/fetch_weights.py sdxl"))
        if args.fetch and gpu:
            print("  fetching SDXL checkpoint (resumable)...")
            rc = subprocess.call([sys.executable, str(TOOLS / "fetch_weights.py"), "sdxl"])
            actions.append(f"fetch_weights sdxl -> rc {rc}")

    # 3. ComfyUI server
    server = cg.get("comfyui_server") or "http://127.0.0.1:8188"
    if reachable(server):
        steps.append(("comfyui", "ready", f"reachable at {server}"))
    else:
        comfy_cli = shutil.which("comfy")
        app = cg.get("comfyui_app") or ""
        if comfy_cli:
            hint = "launch: comfy launch --background"
        elif app:
            hint = f"start ComfyUI so it serves {server} (its app dir: {app})"
        else:
            hint = f"install + start ComfyUI so it serves {server}"
        steps.append(("comfyui", "fixable", f"not reachable at {server} -> {hint}"))
        if args.launch and comfy_cli:
            print("  launching ComfyUI via comfy-cli (background)...")
            try:
                subprocess.Popen([comfy_cli, "launch", "--background"])
                actions.append("comfy launch --background (spawned)")
            except Exception as e:
                actions.append(f"launch failed: {e}")

    ready = all(s[1] == "ready" for s in steps)
    if args.json:
        print(json.dumps({"cover_ready": ready,
                          "steps": [{"step": n, "status": st, "detail": d} for n, st, d in steps],
                          "actions": actions}, indent=2))
    else:
        print("=== BOOKSMITH cover setup ===")
        mark = {"ready": "[ok]  ", "fixable": "[fix] ", "blocked": "[--]  ", "skip": "[..]  "}
        for n, st, d in steps:
            print(f"  {mark[st]}{n:11} {d}")
        for a in actions:
            print(f"  -> {a}")
        if ready:
            print("\ncover-ready: generate with  python _tools/cover_gen.py --config <book_config.json>")
        elif any(s[0] == "gpu" and s[1] == "blocked" for s in steps):
            print("\nNo local AI art on this machine. Put your art in the book's cover_art/ folder; "
                  "compositing + verification still work. (Re-run with a GPU box to generate.)")
        else:
            print("\nAlmost: resolve the [fix] item(s) above (or re-run with --fetch / --launch), then generate.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
