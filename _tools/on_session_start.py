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
        "Prefer a BROWSER? The Studio (localhost web UI over this same kit):",
        "     pip install -r requirements-studio.txt    then run: studio.cmd",
        "  (first launch runs step 1 for you; a tokenized URL opens itself).",
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


# ---------------------------------------------------------------------------
# Boot-into-the-Studio (2026-08-05). On an ORDINARY session start (never during
# a compaction/resume recovery), surface the localhost browser Studio: relay it
# if it is already running; launch it detached when kit_env.studio.autolaunch
# is true (the server opens the browser itself at a tokenized URL); otherwise
# print a one-line offer. The model relays the STUDIO line in its status report
# (CLAUDE.md §1 step 6). Never crash; never block boot.

def _kit_root():
    return Path(__file__).resolve().parent.parent


def _studio_cfg():
    """Read kit_env.studio; an absent block means offer-only defaults."""
    try:
        env = json.loads((Path(__file__).resolve().parent / "kit_env.json")
                         .read_text(encoding="utf-8"))
        s = env.get("studio") or {}
        return {"autolaunch": bool(s.get("autolaunch", False)),
                "port": int(s.get("port", 8756))}
    except Exception:
        return {"autolaunch": False, "port": 8756}


def _studio_token():
    try:
        t = (_kit_root() / "_studio" / "token").read_text(encoding="utf-8").strip()
        return t or None
    except Exception:
        return None


def _studio_alive(port0, token):
    """Return the live Studio's port, else None. Definitive probe: /api/health
    with the per-launch token (the server rewrites _studio/token at every
    launch, so the file always matches the live server). Fallback sniff: the
    guard's token-403 body names studio.cmd. Non-listening loopback ports fail
    instantly, so the scan is fast."""
    import urllib.request
    import urllib.error
    for p in range(port0, port0 + 21):
        req = urllib.request.Request("http://127.0.0.1:%d/api/health" % p)
        if token:
            req.add_header("X-Studio-Token", token)
        try:
            with urllib.request.urlopen(req, timeout=0.8) as r:
                if '"ok"' in r.read(2048).decode("utf-8", "replace"):
                    return p
        except urllib.error.HTTPError as e:
            try:
                body = e.read(2048).decode("utf-8", "replace")
            except Exception:
                body = ""
            if "studio" in body.lower():
                return p           # token-gated 403 from the Studio's own guard
        except Exception:
            continue
    return None


def _studio_deps_ok():
    import importlib.util
    try:
        return all(importlib.util.find_spec(m) is not None
                   for m in ("fastapi", "uvicorn"))
    except Exception:
        return False


def _launch_studio_detached(port):
    """Spawn studio/server.py fully detached so it survives this hook and the
    session. stdin=DEVNULL + close_fds + redirected stdout per the detached-
    launch lesson (cover_gen close_fds fix, 70a8dc8): a capturing caller must
    never wedge on an inherited pipe. The server prints its tokenized URL to
    the log and opens the browser itself."""
    import subprocess
    from datetime import datetime
    kit = _kit_root()
    server = kit / "studio" / "server.py"
    if not server.exists():
        return False
    logdir = kit / "_studio"
    logdir.mkdir(exist_ok=True)
    log = open(logdir / "autolaunch.log", "a", encoding="utf-8", errors="replace")
    log.write("\n--- autolaunch %s ---\n" % datetime.now().isoformat(timespec="seconds"))
    log.flush()
    env = dict(os.environ, PYTHONUTF8="1", PYTHONIOENCODING="utf-8",
               PYTHONUNBUFFERED="1")   # else the child block-buffers its URL line
    argv = [sys.executable, str(server), "--port", str(port)]
    kw = dict(cwd=str(kit), stdin=subprocess.DEVNULL, stdout=log, stderr=log,
              close_fds=True, env=env)
    if os.name == "nt":
        DETACHED_PROCESS = 0x00000008
        CREATE_NEW_PROCESS_GROUP = 0x00000200
        subprocess.Popen(argv,
                         creationflags=DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP,
                         **kw)
    else:
        subprocess.Popen(argv, start_new_session=True, **kw)
    log.close()          # the child holds its own duplicated handle
    return True


def _print_studio_line():
    """Emit the STUDIO block for the model to relay in its status report."""
    kit = _kit_root()
    if not (kit / "studio" / "server.py").exists():
        return
    cfg = _studio_cfg()
    token = _studio_token()
    port = _studio_alive(cfg["port"], token)
    lines = []
    if port:
        url = "http://127.0.0.1:%d/" % port + (("?t=" + token) if token else "")
        lines = [
            "STUDIO: already running at %s" % url,
            "        Relay this URL to the operator in your status report (their",
            "        browser session from the original launch is cookie-authorized).",
        ]
    elif cfg["autolaunch"] and _studio_deps_ok():
        if _launch_studio_detached(cfg["port"]):
            lines = [
                "STUDIO: launching now (kit_env.studio.autolaunch=true). The browser",
                "        opens itself at a tokenized 127.0.0.1 URL in a few seconds.",
                "        If it does not: run studio.cmd. URL lands in",
                "        _studio/autolaunch.log; token in _studio/token. Tell the operator.",
            ]
    elif cfg["autolaunch"]:
        lines = [
            "STUDIO: autolaunch is on but fastapi/uvicorn are not installed.",
            "        Offer the operator: pip install -r requirements-studio.txt,",
            "        then run studio.cmd (the localhost browser UI over this kit).",
        ]
    else:
        lines = [
            'STUDIO: not running. Offer the operator, in one line: "Prefer a',
            '        browser? Run studio.cmd" (the localhost web UI over this kit).',
        ]
    if not lines:
        return
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    sys.stdout.write("\n".join(lines) + "\n")


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
    ordinary = (not trigger) and source in ("startup", "clear", "")
    kit_env = Path(__file__).resolve().parent / "kit_env.json"

    # Boot-into-the-Studio: ordinary starts on a CONFIGURED machine surface the
    # browser Studio (launch/relay/offer). Recovery boots stay pure; fresh
    # copies get the Studio pointer inside the first-run block instead.
    if ordinary and kit_env.exists():
        try:
            _print_studio_line()
        except Exception:
            pass

    # First-run onboarding: a fresh copy (never configured) with NO in-flight book
    # and an ordinary startup (not a compaction/resume). Non-disruptive to recovery.
    if not inflight and not trigger:
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
