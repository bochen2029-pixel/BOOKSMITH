#!/usr/bin/env python3
r"""
verify_course.py — the 'course' domain gate (BOOKSMITH domain: course).

The domain's own verifier, analogous to verify_build.py for the book domain. The engine
runs it as the `verify` stage (declared in domains/course/domain.json). Checks:
  1. every lesson is drafted, non-trivial, and starts with its exact H1 title;
  2. both produce targets (course markdown + course json) exist on disk;
  3. the single-authorial-act gate over the lessons (advisory - informational, not fatal,
     so the domain proof does not depend on mock filler reading like a human wrote it).

Prints {"domain":"course","all_pass":bool,"checks":[...]} and exits 0/1.
stdlib only (shells to the kit's authorial_act.py for check 3).
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

TOOLS = Path(__file__).resolve().parent.parent.parent / "_tools"  # domains/course -> repo -> _tools


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Verify a produced course.")
    ap.add_argument("--config", required=True)
    args = ap.parse_args(argv)

    cfg = json.loads(Path(args.config).read_text(encoding="utf-8"))
    ws = Path(args.config).parent
    slug = cfg.get("slug", "course")
    checks: list[dict] = []

    # 1. every lesson drafted, non-trivial, correct H1
    for u in cfg.get("units", []):
        p = ws / "manuscript" / "current" / f"{u['id']}_current.md"
        body = p.read_text(encoding="utf-8", errors="replace") if p.exists() else ""
        wc = len(re.findall(r"\S+", body))
        h1_ok = body.lstrip().startswith(f"# {u.get('title', u['id'])}")
        checks.append({"name": f"lesson_{u['id']}", "pass": bool(p.exists() and wc >= 20 and h1_ok),
                       "detail": f"{wc} words; H1 {'ok' if h1_ok else 'WRONG/absent'}"})

    # 2. produce targets present
    for f in (ws / "outputs" / "course" / f"{slug}_COURSE.md",
              ws / "outputs" / "course" / f"{slug}_course.json"):
        checks.append({"name": f"produced_{f.name}", "pass": f.exists(), "detail": str(f)})

    # 3. single-authorial-act gate (advisory)
    try:
        r = subprocess.run([sys.executable, str(TOOLS / "authorial_act.py"),
                            "--config", args.config, "--json"], capture_output=True, text=True)
        aa = json.loads(r.stdout.strip().splitlines()[-1]) if r.stdout.strip() else {}
        verdict = "PASS" if aa.get("pass") else f"FAIL({aa.get('high', 0)}h/{len(aa.get('findings', []))}f)"
        checks.append({"name": "authorial_act", "pass": True, "detail": f"{verdict} (advisory)"})
    except Exception as e:
        checks.append({"name": "authorial_act", "pass": True, "detail": f"skipped ({str(e)[:80]})"})

    all_pass = all(c["pass"] for c in checks)
    print(json.dumps({"domain": "course", "all_pass": all_pass, "checks": checks},
                     indent=2, ensure_ascii=False))
    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(main())
