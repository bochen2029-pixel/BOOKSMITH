#!/usr/bin/env python3
"""on_precompact.py — PreCompact hook body.

Fires just before Claude Code compacts the context. Best-effort actions so a
fresh, high-fidelity rehydration is waiting on the far side of the compaction:

  (a) snapshot every in-flight book's _CONTINUITY.md to _CONTINUITY.snapshot.md
  (b) write <cwd>/.booksmith_rehydrate containing the resolved session .jsonl path
  (c) best-effort run rehydrate.py so _REHYDRATION.md is regenerated

Reads the hook JSON from stdin (may carry session_id / transcript_path / cwd);
tolerates a malformed or empty payload. NEVER fails the hook: all work is wrapped
in try/except and the process always exits 0. Prints nothing sensitive.

stdlib only.
"""
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent


def _load_stdin():
    try:
        raw = sys.stdin.read()
    except Exception:
        return {}
    if not raw or not raw.strip():
        return {}
    try:
        d = json.loads(raw)
        return d if isinstance(d, dict) else {}
    except Exception:
        return {}


def _resolve_session(payload, cwd):
    # 1) explicit transcript path from the hook payload
    for key in ("transcript_path", "transcriptPath", "transcript"):
        v = payload.get(key)
        if v and Path(v).exists():
            return Path(v)
    # 2) derive from session_id + project slug
    sid = payload.get("session_id") or payload.get("sessionId")
    slug = str(cwd)
    for ch in (":", "\\", "/"):
        slug = slug.replace(ch, "-")
    proj = Path(os.path.expanduser("~")) / ".claude" / "projects" / slug
    if sid:
        cand = proj / (str(sid) + ".jsonl")
        if cand.exists():
            return cand
    # 3) newest .jsonl in the project dir
    try:
        cands = list(proj.glob("*.jsonl"))
        if cands:
            return max(cands, key=lambda f: f.stat().st_mtime)
    except Exception:
        pass
    return None


def _iter_continuities(cwd):
    """Yield _CONTINUITY.md paths under <cwd>/book_workspace/*/ ."""
    bw = Path(cwd) / "book_workspace"
    if not bw.is_dir():
        return
    for sub in bw.iterdir():
        try:
            if sub.is_dir():
                c = sub / "_CONTINUITY.md"
                if c.exists():
                    yield c
        except Exception:
            continue


def main():
    payload = _load_stdin()
    cwd = payload.get("cwd") or os.getcwd()

    # (a) snapshot continuity ledgers
    try:
        for c in _iter_continuities(cwd):
            try:
                shutil.copyfile(c, c.with_name("_CONTINUITY.snapshot.md"))
            except Exception:
                pass
    except Exception:
        pass

    # (b) write the flag file with the resolved session path
    session = None
    try:
        session = _resolve_session(payload, cwd)
        if session is not None:
            (Path(cwd) / ".booksmith_rehydrate").write_text(str(session), encoding="utf-8", errors="replace")
    except Exception:
        pass

    # (c) best-effort rehydrate so _REHYDRATION.md is waiting. Write it into each
    #     in-flight book workspace if any; else into cwd.
    try:
        rehydrate = _HERE / "rehydrate.py"
        if rehydrate.exists():
            targets = [c.parent for c in _iter_continuities(cwd)] or [Path(cwd)]
            for ws in targets:
                cmd = [sys.executable, "-X", "utf8", str(rehydrate), "--workspace", str(ws)]
                if session is not None:
                    cmd += ["--session", str(session)]
                try:
                    subprocess.run(cmd, capture_output=True, text=True, timeout=180)
                except Exception:
                    pass
    except Exception:
        pass

    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        # absolutely never fail the hook
        sys.exit(0)
