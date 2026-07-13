#!/usr/bin/env python3
"""rehydrate.py — post-compaction rehydration orchestrator (the forcing function).

Turns the newest Claude Code session .jsonl into a high-fidelity markdown
transcript sized to fit a token budget, writes it to <workspace>/_REHYDRATION.md,
and prints a LOUD instruction to read it before resuming.

The insight: a .jsonl session record converted to markdown is ~10x smaller than
the raw file, and stripping thinking blocks roughly halves it again. The result
is FAR higher fidelity than any hand-written memory summary because it IS the
record, merely compact. For one-shot book writing it fits a 1M context easily.

Tiered conversion to hit --budget-tokens:
  Tier 1: --strip-thinking (full tool traffic)
  Tier 2: --strip-thinking --no-tools
  Tier 3: --strip-thinking --no-tools --tail-turns N   (fit the tail)
Always reports which tier was used and the reduction ratio.

CLI:
  python rehydrate.py [--session PATH] [--project-dir DIR] [--workspace DIR]
      [--budget-tokens N=250000] [--out OUT.md]

stdlib only. Imports transcript_to_md in-process; optionally uses tiktoken or
C:\\chunker\\estimate_tokens.py for token counting, else chars/4.
"""
import argparse
import os
import re
import subprocess
import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))
import transcript_to_md as t2m  # noqa: E402

def _find_estimate_tokens():
    """Optional external token-counter (an accelerator organ on the reference
    machine, absent on most). Resolved via kit_env.json organs.estimate_tokens;
    when missing, the tiktoken / chars-4 fallbacks below cover it."""
    try:
        import json as _json
        env_path = _HERE / "kit_env.json"
        if env_path.exists():
            organs = _json.loads(env_path.read_text(encoding="utf-8")).get("organs", {})
            p = organs.get("estimate_tokens", "")
            if p:
                cand = Path(p)
                if not cand.is_absolute():
                    cand = _HERE.parent / p  # repo-relative (e.g. _tools/estimate_tokens.py)
                if cand.exists():
                    return cand
    except Exception:
        pass
    vendored = _HERE / "estimate_tokens.py"
    if vendored.exists():
        return vendored
    return None


ESTIMATE_TOKENS_PY = _find_estimate_tokens()


# ---------------------------------------------------------------- token counting
def _count_tokens(text):
    """Best available token count. Returns (n_tokens, method)."""
    # 1) tiktoken in-process (fast, exact BPE proxy)
    try:
        import tiktoken
        enc = tiktoken.get_encoding("o200k_base")
        return len(enc.encode(text, disallowed_special=())), "tiktoken/o200k_base"
    except Exception:
        pass
    # 2) fall back to chars/4 (estimate_tokens.py is file-based; we already have
    #    the text in memory, so the heuristic avoids a temp-file round trip)
    return max(1, len(text) // 4), "chars/4"


def _count_tokens_file(path):
    """Token count for an on-disk file; tries estimate_tokens.py, else chars/4."""
    if ESTIMATE_TOKENS_PY:
        try:
            p = subprocess.run(
                [sys.executable, "-X", "utf8", str(ESTIMATE_TOKENS_PY), str(path)],
                capture_output=True, text=True, encoding="utf-8", errors="replace",
                timeout=120,
            )
            m = re.search(r"tiktoken\S*\s*=\s*([\d,]+)\s*tokens", p.stdout)
            if m:
                return int(m.group(1).replace(",", "")), "estimate_tokens.py"
            m = re.search(r"heuristic\s*~\s*([\d,]+)\s*tokens", p.stdout)
            if m:
                return int(m.group(1).replace(",", "")), "estimate_tokens.py(heuristic)"
        except Exception:
            pass
    txt = Path(path).read_text(encoding="utf-8", errors="replace")
    n, meth = _count_tokens(txt)
    return n, meth


# ---------------------------------------------------------------- session finding
def slugify_cwd(path):
    """C:\\My-Project -> C--My-Project (Claude Code project-dir slug)."""
    s = str(path)
    for ch in (":", "\\", "/"):
        s = s.replace(ch, "-")
    return s


def default_project_dir(cwd):
    return Path(os.path.expanduser("~")) / ".claude" / "projects" / slugify_cwd(cwd)


def newest_jsonl(project_dir):
    p = Path(project_dir)
    if not p.is_dir():
        return None
    cands = list(p.glob("*.jsonl"))
    if not cands:
        return None
    return max(cands, key=lambda f: f.stat().st_mtime)


# ---------------------------------------------------------------- tiering
def _estimate_turns(jsonl_path):
    """Count substantive (user/assistant/summary) turns for tail-fit math."""
    import json
    n = 0
    with open(jsonl_path, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                r = json.loads(line)
            except Exception:
                continue
            if isinstance(r, dict) and r.get("type") in ("user", "assistant", "summary"):
                n += 1
    return n


def tiered_convert(jsonl_path, budget_tokens):
    """Return (markdown, meta_dict). Escalates stripping until under budget."""
    raw_bytes = Path(jsonl_path).stat().st_size

    # measurement pass: all three headline sizes for the report
    md_full = t2m.convert(jsonl_path, strip_thinking=False, no_tools=False)
    tok_full, meth = _count_tokens(md_full)
    md_strip = t2m.convert(jsonl_path, strip_thinking=True, no_tools=False)
    tok_strip, _ = _count_tokens(md_strip)
    md_strip_notools = t2m.convert(jsonl_path, strip_thinking=True, no_tools=True)
    tok_strip_notools, _ = _count_tokens(md_strip_notools)

    meta = {
        "raw_bytes": raw_bytes,
        "token_method": meth,
        "tok_full": tok_full,
        "tok_strip": tok_strip,
        "tok_strip_notools": tok_strip_notools,
        "budget": budget_tokens,
    }

    # Tier selection
    if tok_strip <= budget_tokens:
        meta["tier"] = "1 (strip-thinking)"
        meta["chosen_tokens"] = tok_strip
        meta["chosen_md"] = md_strip
    elif tok_strip_notools <= budget_tokens:
        meta["tier"] = "2 (strip-thinking + no-tools)"
        meta["chosen_tokens"] = tok_strip_notools
        meta["chosen_md"] = md_strip_notools
    else:
        # Tier 3: tail-fit. Binary-search the number of tail turns that fits.
        total_turns = _estimate_turns(jsonl_path)
        lo, hi, best_md, best_tok, best_n = 1, max(1, total_turns), None, None, 1
        # coarse geometric probe then refine
        n = max(1, total_turns)
        while n >= 1:
            md = t2m.convert(jsonl_path, strip_thinking=True, no_tools=True, tail_turns=n)
            tok, _ = _count_tokens(md)
            if tok <= budget_tokens:
                best_md, best_tok, best_n = md, tok, n
                break
            n = n // 2
        if best_md is None:
            # even 1 turn over budget (pathological) — take it anyway, truncated hard
            best_md = t2m.convert(jsonl_path, strip_thinking=True, no_tools=True,
                                  tail_turns=1, max_tool_chars=400)
            best_tok, _ = _count_tokens(best_md)
            best_n = 1
        meta["tier"] = "3 (strip-thinking + no-tools + tail-turns=%d of %d)" % (best_n, total_turns)
        meta["chosen_tokens"] = best_tok
        meta["chosen_md"] = best_md
        meta["tail_turns"] = best_n
        meta["total_turns"] = total_turns

    meta["reduction_ratio"] = (raw_bytes / max(1, meta["chosen_tokens"]))
    return meta["chosen_md"], meta


# ---------------------------------------------------------------- output
HOWTO = """<!-- HOW TO USE THIS FILE ------------------------------------------------
This is an auto-generated, high-fidelity rehydration of the current Claude Code
session, converted from the raw .jsonl transcript to compact markdown. It is the
REAL record of what happened this session, not a summary. If you are resuming
after a context compaction:

  1. READ THIS FILE IN FULL (below the fence).
  2. THEN read the in-flight book's _CONTINUITY.md (RESUME PROTOCOL at its top)
     and seed.md before writing any prose.

Regenerate anytime with:
  python C:\\BOOKSMITH\\_tools\\rehydrate.py --workspace <this workspace>
------------------------------------------------------------------------- -->
"""


def _write_out(out_path, md, meta):
    header = [HOWTO, ""]
    header.append("<!-- rehydration meta: tier=%s | chosen=%d tok | raw=%.2f MB |"
                  " full=%d strip=%d strip+notools=%d tok | method=%s -->" % (
                      meta["tier"], meta["chosen_tokens"], meta["raw_bytes"] / 1e6,
                      meta["tok_full"], meta["tok_strip"], meta["tok_strip_notools"],
                      meta["token_method"]))
    header.append("")
    body = "\n".join(header) + "\n" + md
    outp = Path(out_path)
    outp.parent.mkdir(parents=True, exist_ok=True)
    outp.write_text(body, encoding="utf-8", errors="replace")
    return outp


def _loud_block(out_path, meta, workspace):
    cont = Path(workspace) / "_CONTINUITY.md"
    # also look one level down (book_workspace/<slug>/_CONTINUITY.md)
    cont_hint = ""
    if cont.exists():
        cont_hint = "\n  - and READ: %s (its RESUME PROTOCOL is at the top)" % cont
    bar = "=" * 72
    return (
        "\n" + bar +
        "\n  COMPACTION-SURVIVAL REHYDRATION READY" +
        "\n" + bar +
        "\n  A fresh high-fidelity transcript has been written:" +
        "\n    %s" % out_path +
        "\n  tier used: %s" % meta["tier"] +
        "\n  size: %d tokens  (raw jsonl %.2f MB -> %d tok; reduction ~%.0fx bytes/tok)" % (
            meta["chosen_tokens"], meta["raw_bytes"] / 1e6,
            meta["chosen_tokens"], meta["reduction_ratio"]) +
        "\n" +
        "\n  BEFORE RESUMING ANY WORK:" +
        "\n  - READ %s IN FULL." % out_path +
        cont_hint +
        "\n  - Do NOT write prose or make edits until you have read both." +
        "\n" + bar + "\n"
    )


def main(argv=None):
    ap = argparse.ArgumentParser(description="Rehydrate a session from its .jsonl into a budgeted markdown transcript.")
    ap.add_argument("--session", help="explicit path to session .jsonl (else auto-find newest)")
    ap.add_argument("--project-dir", help="Claude projects dir for this cwd (else derived from --workspace/cwd)")
    ap.add_argument("--workspace", help="where to write _REHYDRATION.md (default: cwd)")
    ap.add_argument("--budget-tokens", type=int, default=250000)
    ap.add_argument("--out", help="explicit output path (default: <workspace>/_REHYDRATION.md)")
    args = ap.parse_args(argv)

    workspace = Path(args.workspace) if args.workspace else Path.cwd()
    # cwd for slug purposes: prefer an explicit project cwd; workspace may be a
    # sub-folder of the project, so also try to detect the project root.
    session = None
    if args.session:
        session = Path(args.session)
        if not session.exists():
            sys.stderr.write("warning: --session not found: %s (falling back to auto-find)\n" % session)
            session = None

    if session is None:
        # try flag file first (written by PreCompact hook)
        flag = Path.cwd() / ".booksmith_rehydrate"
        if flag.exists():
            try:
                cand = Path(flag.read_text(encoding="utf-8", errors="replace").strip())
                if cand.exists():
                    session = cand
            except Exception:
                pass

    if session is None:
        proj = Path(args.project_dir) if args.project_dir else default_project_dir(Path.cwd())
        session = newest_jsonl(proj)
        if session is None:
            # last resort: search a couple of likely project dirs derived from workspace
            for base in {Path.cwd(), workspace}:
                pj = default_project_dir(base)
                s = newest_jsonl(pj)
                if s:
                    session = s
                    break

    if session is None:
        sys.stderr.write("error: could not locate a session .jsonl. Pass --session PATH.\n")
        return 2

    md, meta = tiered_convert(session, args.budget_tokens)
    out_path = Path(args.out) if args.out else (workspace / "_REHYDRATION.md")
    out_path = _write_out(out_path, md, meta)

    # consume-then-delete: the precompact flag is a one-shot session pointer; a
    # flag that outlives its recovery pins future rehydrations to an OLD session
    try:
        (Path.cwd() / ".booksmith_rehydrate").unlink(missing_ok=True)
    except Exception:
        pass

    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    sys.stdout.write(_loud_block(out_path, meta, workspace))
    # machine-readable one-liner for logs
    sys.stderr.write(
        "rehydrate: session=%s raw=%.2fMB full=%dtok strip=%dtok strip+notools=%dtok "
        "tier=%s chosen=%dtok out=%s\n" % (
            session, meta["raw_bytes"] / 1e6, meta["tok_full"], meta["tok_strip"],
            meta["tok_strip_notools"], meta["tier"], meta["chosen_tokens"], out_path))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
