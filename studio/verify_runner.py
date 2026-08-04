#!/usr/bin/env python3
r"""
verify_runner.py — run the mechanical verifier across a book's formats and cache
the results for the Studio's QA matrix (S4).

Studio-side code, not kit surface: it only SHELLS `_tools/verify_build.py` once
per configured format and writes each result to `_studio/verify/<format>.json`
(+ `summary.json`). It runs as a JOB because print formats invoke Word COM
through check_part_pages.py — exclusive and slow, so it must share the one lane
(docs/STUDIO_SPEC.md §3.1), never block an HTTP request.

Usage: python studio/verify_runner.py --config <book_config.json> [--final] [--format F]
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

KIT = Path(__file__).resolve().parents[1]
TOOLS = KIT / "_tools"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    ap.add_argument("--final", action="store_true")
    ap.add_argument("--format", default=None, help="verify one format only")
    args = ap.parse_args()

    cfg_path = Path(args.config).resolve()
    ws = cfg_path.parent
    cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
    formats = [args.format] if args.format else list(cfg.get("formats") or [])
    out_dir = ws / "_studio" / "verify"
    out_dir.mkdir(parents=True, exist_ok=True)

    env = dict(os.environ)
    env["PYTHONUTF8"] = "1"
    env["PYTHONIOENCODING"] = "utf-8"

    summary = {"ts": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
               "final": bool(args.final), "formats": {}}
    if not formats:
        print("no formats configured; nothing to verify")
    for fmt in formats:
        cmd = [sys.executable, str(TOOLS / "verify_build.py"),
               "--config", str(cfg_path), "--format", fmt]
        if args.final:
            cmd.append("--final")
        print(f"[verify] {fmt} …", flush=True)
        r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8",
                           errors="replace", cwd=str(KIT), env=env, timeout=1800)
        data = None
        s = (r.stdout or "").strip()
        if s:
            try:
                data = json.loads(s)
            except Exception:
                i, j = s.find("{"), s.rfind("}")
                if 0 <= i < j:
                    try:
                        data = json.loads(s[i:j + 1])
                    except Exception:
                        data = None
        if not isinstance(data, dict):
            data = {"format": fmt, "all_pass": False,
                    "checks": [{"name": "verify_build", "pass": False,
                                "detail": (r.stdout + r.stderr).strip()[-400:]
                                          or f"exit {r.returncode}, no output"}]}
        data["_rc"] = r.returncode
        data["_ts"] = summary["ts"]
        (out_dir / f"{fmt}.json").write_text(
            json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
        n_fail = sum(1 for c in data.get("checks", []) if not c.get("pass"))
        summary["formats"][fmt] = {"all_pass": bool(data.get("all_pass")),
                                   "checks": len(data.get("checks", [])),
                                   "failed": n_fail}
        print(f"[verify] {fmt}: {'ALL PASS' if data.get('all_pass') else f'{n_fail} failing'}",
              flush=True)

    (out_dir / "summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    green = all(v["all_pass"] for v in summary["formats"].values()) if summary["formats"] else False
    print(f"\nverify matrix: {'GREEN' if green else 'RED'} "
          f"({sum(1 for v in summary['formats'].values() if v['all_pass'])}"
          f"/{len(summary['formats'])} formats)")
    return 0 if green else 1


if __name__ == "__main__":
    raise SystemExit(main())
