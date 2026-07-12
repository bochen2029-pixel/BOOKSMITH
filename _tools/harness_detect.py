#!/usr/bin/env python3
r"""
harness_detect.py — identify the agentic harness + locate THIS session's transcript.

The cross-harness portability core (roadmap H2.7). BOOKSMITH's compaction survival needs to
find the file where the CURRENT harness records the running session, so it can rehydrate.
Claude Code stores <session>.jsonl under ~/.claude/projects/<slug>/; OpenCode / Cursor / an
unknown harness store it elsewhere (or differently). Two capabilities:

  1. IDENTIFY  — detect the harness from on-disk markers + env, and name the profile to load
     (docs/harness_profiles/<harness>.md).
  2. FIND      — the NONCE PROTOCOL for an unknown harness: you emit a unique nonce in your
     output, then this content-searches the likely session-store roots for the file that now
     contains it. That file is the transcript; rehydration reads from there. No format
     knowledge required up front - the disk tells you where the harness wrote your words.

The `_CONTINUITY.md` ledger and the deterministic engine (`_engine/state.json`) are ALREADY
harness-agnostic (plain disk files the kit owns). This tool covers the one remaining
harness-specific thing: finding the transcript for high-fidelity rehydration.

CONTRACT
  python harness_detect.py --identify [--json]
      -> print the detected harness + the profile path to load.
  python harness_detect.py --find-transcript --nonce "<STR>" [--json] [--root DIR ...]
      -> content-search the session-store roots for <STR>; print holders newest-first.
  python harness_detect.py --selftest
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
ROOT = TOOLS.parent

SKIP_EXT = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp", ".pdf", ".zip", ".gz",
            ".safetensors", ".ckpt", ".onnx", ".ttf", ".otf", ".woff", ".woff2",
            ".mp4", ".mov", ".mp3", ".wav", ".exe", ".dll", ".so", ".dylib", ".pyc",
            ".bak", ".tmp"}
PREFER_EXT = {".jsonl", ".json", ".md", ".txt", ".log", ".ndjson"}


def detect_harness(cwd=None) -> str:
    """Best-effort harness identification. cwd markers win over home stores."""
    cwd = Path(cwd or os.getcwd())
    home = Path.home()
    if os.environ.get("CLAUDECODE") or os.environ.get("CLAUDE_CODE"):
        return "claude_code"
    if (cwd / ".opencode").exists() or (home / ".opencode").exists() \
            or (home / ".local" / "share" / "opencode").exists():
        return "opencode"
    if (cwd / ".cursor").exists() or (cwd / ".cursorrules").exists():
        return "cursor"
    if any(cwd.glob(".aider*")):
        return "aider"
    if (home / ".claude").exists():
        return "claude_code"
    return "generic"


def profile_for(harness: str) -> str:
    p = ROOT / "docs" / "harness_profiles" / f"{harness}.md"
    if p.exists():
        return str(p)
    return str(ROOT / "docs" / "harness_profiles" / "generic.md")


def transcript_roots(extra=None) -> list[Path]:
    home = Path.home()
    cands = [
        home / ".claude" / "projects",
        home / ".opencode",
        home / ".local" / "share" / "opencode",
        home / ".config" / "opencode",
        home / ".cursor",
        Path(os.getcwd()),
    ]
    for e in (extra or []):
        cands.append(Path(e))
    seen, out = set(), []
    for c in cands:
        try:
            rc = c.resolve()
        except Exception:
            rc = c
        if c.exists() and str(rc) not in seen:
            seen.add(str(rc))
            out.append(c)
    return out


def find_transcript(nonce: str, roots=None, max_bytes: int = 80_000_000, cap: int = 40000) -> list[str]:
    """Content-search the roots for `nonce`; return holder paths newest-first. Bounded:
    skips empty/huge/binary files and caps the number scanned."""
    roots = roots if roots is not None else transcript_roots()
    nb = nonce.encode("utf-8", "replace")
    hits, scanned = [], 0
    for root in roots:
        try:
            walker = root.rglob("*")
        except Exception:
            continue
        for p in walker:
            if scanned >= cap:
                break
            try:
                if not p.is_file():
                    continue
                ext = p.suffix.lower()
                if ext in SKIP_EXT:
                    continue
                sz = p.stat().st_size
                if sz == 0 or sz > max_bytes:
                    continue
                scanned += 1
                with p.open("rb") as f:
                    if nb in f.read():
                        # prefer transcript-like files by ranking, but include all
                        rank = 0 if ext in PREFER_EXT else 1
                        hits.append((rank, p.stat().st_mtime, str(p)))
            except Exception:
                continue
    hits.sort(key=lambda t: (t[0], -t[1]))
    return [h[2] for h in hits]


def selftest() -> int:
    import tempfile
    fails = []
    with tempfile.TemporaryDirectory() as td:
        store = Path(td) / "store"
        (store / "sess").mkdir(parents=True)
        nonce = "BOOKSMITH-NONCE-selftest-7Q2X9"
        (store / "sess" / "session.jsonl").write_text(
            '{"role":"user","content":"hello ' + nonce + ' world"}\n', "utf-8")
        (store / "noise.txt").write_text("unrelated content", "utf-8")
        (store / "big.png").write_bytes(b"\x89PNG" + nonce.encode())  # binary: must be skipped
        hits = find_transcript(nonce, roots=[store])
        if not hits:
            fails.append("nonce protocol found nothing")
        elif not hits[0].endswith("session.jsonl"):
            fails.append(f"expected session.jsonl first, got {hits[0]}")
        if any(h.endswith(".png") for h in hits):
            fails.append("binary .png was not skipped")
        # a nonce that exists nowhere returns empty
        if find_transcript("BOOKSMITH-NONCE-absent-000", roots=[store]):
            fails.append("absent nonce should return no holders")
        h = detect_harness()
        if h not in ("claude_code", "opencode", "cursor", "aider", "generic"):
            fails.append(f"detect_harness returned unexpected value: {h}")
        if not Path(profile_for("generic")).name == "generic.md":
            fails.append("profile_for(generic) did not resolve")
    if fails:
        print("HARNESS_DETECT SELFTEST: FAIL")
        for f in fails:
            print("  - " + f)
        return 1
    print("HARNESS_DETECT SELFTEST: PASS (identify + nonce transcript-finder, binaries "
          "skipped, absent-nonce empty)")
    return 0


def main(argv=None) -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    ap = argparse.ArgumentParser(description="Identify the harness + locate the session transcript.")
    ap.add_argument("--identify", action="store_true")
    ap.add_argument("--find-transcript", action="store_true")
    ap.add_argument("--nonce", help="the unique string you emitted this session")
    ap.add_argument("--root", action="append", help="extra root to search (repeatable)")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)

    if args.selftest:
        return selftest()
    if args.find_transcript:
        if not args.nonce:
            print("--find-transcript needs --nonce", file=sys.stderr)
            return 2
        roots = transcript_roots(args.root)
        hits = find_transcript(args.nonce, roots=roots)
        if args.json:
            print(json.dumps({"nonce": args.nonce, "holders": hits,
                              "roots": [str(r) for r in roots]}, ensure_ascii=False))
        else:
            if hits:
                print("transcript holder(s) (newest-first):")
                for h in hits:
                    print("  " + h)
            else:
                print("no file under the session-store roots contains that nonce; fall back to "
                      "the _CONTINUITY.md ledger (it is harness-agnostic).")
        return 0
    # default: identify
    h = detect_harness()
    prof = profile_for(h)
    if args.json:
        print(json.dumps({"harness": h, "profile": prof}, ensure_ascii=False))
    else:
        print(f"harness: {h}\nprofile: {prof}")
        if h == "generic":
            print("unknown harness -> follow docs/harness_profiles/generic.md (the nonce protocol).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
