#!/usr/bin/env python3
"""on_session_start.py — SessionStart hook body (forcing function on resume/compact).

Claude Code runs this at session start and injects this script's STDOUT into the
model's context. We use that to force compaction/resume recovery.

Behavior:
  - Read hook JSON from stdin; it carries a "source" in {startup,resume,compact,clear}.
  - Locate any in-flight book: a book_workspace/*/_CONTINUITY.md whose STATUS is
    NOT "COMPLETE".
  - If found AND (source in {compact, resume} OR a <cwd>/.booksmith_rehydrate flag
    exists), print a hard STOP recovery block: the HEAD of that _CONTINUITY.md
    (first ~60 lines) inline, then explicit first-action instructions.
  - Otherwise print nothing.
  - Never crash; always exit 0.

stdlib only.
"""
import json
import os
import re
import sys
from pathlib import Path

HEAD_LINES = 60


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


def _status_of(continuity_path):
    """Extract STATUS token from the ledger head. Default UNKNOWN.

    Matches forms like:
      # _CONTINUITY — Title  (STATUS: IN_PROGRESS)
      STATUS: COMPLETE
      **STATUS:** DRAFTING
    """
    try:
        with open(continuity_path, "r", encoding="utf-8", errors="replace") as f:
            head = "".join([next(f, "") for _ in range(HEAD_LINES)])
    except Exception:
        return "UNKNOWN", ""
    # Anchored per-line against a known vocabulary: the old first-occurrence
    # regex grabbed the next word after ANY "STATUS" (prose "the STATUS of the
    # world is COMPLETE" -> OF; a legend line -> _TOKEN_LEGEND) and missed
    # table forms entirely.
    vocab = r"(COMPLETE|IN[_\- ]?PROGRESS|DRAFTING|SHIPPED|PAUSED|ABANDONED)"
    status = "UNKNOWN"
    for line in head.splitlines():
        # two documented shapes: a line-led token ("STATUS: X", "**STATUS:** X",
        # "| STATUS | X |") and the header-paren form ("# _CONTINUITY — T  (STATUS: X)")
        m = (re.match(r"\s*(?:[#>*|\s]*)?\**\s*STATUS\b[:*)\s|]*\**\s*" + vocab,
                      line, re.IGNORECASE)
             or re.search(r"\(\s*STATUS\b[:\s]*" + vocab, line, re.IGNORECASE))
        if m:
            status = m.group(1).upper().replace("-", "_").replace(" ", "_")
            break
    return status, head


def _iter_inflight(cwd):
    """Yield (continuity_path, status, head) for non-COMPLETE in-flight books."""
    bw = Path(cwd) / "book_workspace"
    if not bw.is_dir():
        return
    for sub in sorted(bw.iterdir()):
        try:
            if not sub.is_dir():
                continue
            c = sub / "_CONTINUITY.md"
            if not c.exists():
                continue
            status, head = _status_of(c)
            if status != "COMPLETE":
                yield c, status, head
        except Exception:
            continue


def _print_first_run():
    """Injected on a fresh, unconfigured copy: onboard the operator."""
    tools = Path(__file__).resolve().parent
    bar = "=" * 74
    out = [
        bar,
        "  BOOKSMITH — FIRST RUN (fresh copy: no _tools/kit_env.json yet)",
        bar,
        "This machine is not configured yet. Onboard the operator:",
        "",
        "  1. Configure this machine (one command):",
        "       python %s" % (tools / "autoconfig.py"),
        "     detects Node/Python/Word/ComfyUI/GPU/fonts -> writes kit_env.json;",
        "     keyless defaults (model=harness: prose from THIS session, no API key).",
        "  2. Preflight capabilities + tier:  python %s" % (tools / "doctor.py"),
        "  3. Read START_HERE.md and follow it.",
        "",
        "To start a book: drop a gist + source docs into intake/ and say `init` --",
        "or just say hi and walk the operator through it. Greet them, offer to run",
        "step 1, and help them begin. Full flow: INSTALL.md / CLAUDE.md / docs/ENGINE.md.",
        bar,
    ]
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    sys.stdout.write("\n".join(out) + "\n")


def main():
    payload = _load_stdin()
    source = (payload.get("source") or payload.get("trigger") or "").lower()
    cwd = payload.get("cwd") or os.getcwd()

    flag = Path(cwd) / ".booksmith_rehydrate"
    flag_exists = flag.exists()

    inflight = list(_iter_inflight(cwd))
    # A flag with no in-flight book is stale (every ledger COMPLETE): clear it so
    # it cannot pin a future rehydration to an old session or nag every startup.
    if flag_exists and not inflight and source not in ("compact", "resume"):
        try:
            flag.unlink()
        except Exception:
            pass
        flag_exists = False
    # Only force recovery on compaction/resume, or when a precompact flag is set.
    trigger = (source in ("compact", "resume")) or flag_exists

    # First-run onboarding: a fresh copy (never configured) with NO in-flight book
    # and an ordinary startup (not a compaction/resume). Non-disruptive to recovery.
    if not inflight and not trigger:
        kit_env = Path(__file__).resolve().parent / "kit_env.json"
        if not kit_env.exists() and source in ("startup", "clear", ""):
            _print_first_run()
        return 0

    if not inflight:
        return 0
    if not trigger:
        return 0

    # Act on the most RECENTLY TOUCHED in-flight book, not the alphabetically
    # first: with two in-flight workspaces the recovery block must point at the
    # one actually being worked.
    inflight.sort(key=lambda t: t[0].stat().st_mtime if t[0].exists() else 0,
                  reverse=True)
    cont_path, status, head = inflight[0]
    workspace = cont_path.parent
    if len(inflight) > 1:
        others = ", ".join(t[0].parent.name for t in inflight[1:])
        head += f"\n(NOTE: other in-flight workspace(s): {others})"

    head_lines = head.splitlines()[:HEAD_LINES]
    bar = "=" * 74

    out = []
    out.append(bar)
    out.append("  STOP — COMPACTION/RESUME RECOVERY (source=%s)" % (source or "?"))
    out.append(bar)
    out.append("An in-flight book was detected and the context was just compacted or")
    out.append("resumed. You MUST rehydrate before writing any prose or making edits.")
    out.append("")
    out.append("In-flight book: %s  (STATUS: %s)" % (workspace.name, status))
    out.append("Continuity ledger: %s" % cont_path)
    out.append("")
    rehydrate_py = Path(__file__).resolve().parent / "rehydrate.py"
    out.append("FIRST ACTIONS, IN ORDER:")
    out.append("  1. Run:")
    out.append("       python %s --workspace %s" % (rehydrate_py, workspace))
    out.append("     then READ the resulting %s IN FULL." % (workspace / "_REHYDRATION.md"))
    out.append("  2. READ this book's continuity ledger in full: %s" % cont_path)
    out.append("  3. READ the Book Bible in full: %s" % (workspace / "seed.md"))
    out.append("  4. Only THEN resume drafting from the NEXT chapter named in the ledger.")
    out.append("  5. After EACH chapter, rewrite %s (never let it go stale)." % cont_path.name)
    out.append("")
    out.append("--- HEAD OF %s (first %d lines) ---" % (cont_path.name, HEAD_LINES))
    out.extend(head_lines)
    out.append("--- END HEAD --- (read the full file per step 2) ---")
    out.append(bar)

    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    sys.stdout.write("\n".join(out) + "\n")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(0)
