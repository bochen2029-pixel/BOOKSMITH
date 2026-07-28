#!/usr/bin/env python3
r"""
ledger_stage.py — auto-draft candidate lessons from gate failures (BOOKSMITH, roadmap H2.6).

The kit's anti-forgetting rule: every gate failure should become a rule AND a gate, so it
can never recur. The deterministic engine already records every hard-stop on disk
(`_engine/HARDSTOP.json` + HARDSTOP events in `_engine/log.jsonl`). This tool harvests
those, de-duplicates them, and drafts symptom -> cause -> fix -> proposed-gate entries into
a STAGING file (`docs/_lessons_staging.md`) for human endorsement. A curator then promotes
an endorsed entry into `docs/LESSONS_LEDGER.md` (and binds its gate) and deletes it here.

It NEVER edits LESSONS_LEDGER.md itself (curation is human; §4 pause). It only stages.

Sources scanned (under --root, default the kit root):
  book_workspace/*/_engine/HARDSTOP.json     the current hard-stop, if any
  book_workspace/*/_engine/log.jsonl         all historical HARDSTOP events

CONTRACT
  python ledger_stage.py [--root DIR] [--out docs/_lessons_staging.md] [--json]
      -> append a PROPOSED entry per NEW (stage, normalized-detail) failure; idempotent
         (an already-staged failure, keyed by a short hash, is skipped). Prints a summary.
  python ledger_stage.py --add "stage | symptom | cause | fix"
      -> stage one entry by hand. cause/fix are optional: a supplied segment renders
         verbatim in the staged block; an omitted one keeps its curator placeholder.
  python ledger_stage.py --selftest
      -> synthesize HARDSTOPs + manual --adds, assert each staged once (idempotent)
         and that a hand-supplied cause/fix survives into the block. No deps.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
ROOT = TOOLS.parent
DEFAULT_OUT = ROOT / "docs" / "_lessons_staging.md"

STAGE_MARK = "<!-- ledger_stage:key="  # idempotency marker embedded per entry


def _norm(detail: str) -> str:
    """Normalize a failure detail so cosmetically-different instances of the same defect
    collapse to one lesson (strip absolute paths, digits, hashes, whitespace)."""
    d = re.sub(r"[A-Za-z]:\\[^\s'\"]+|/[^\s'\"]+/", " <path> ", detail or "")
    d = re.sub(r"\b[0-9a-f]{8,}\b", "<hash>", d)
    d = re.sub(r"\d+", "<n>", d)
    return re.sub(r"\s+", " ", d).strip().lower()


def key_of(stage: str, detail: str) -> str:
    return hashlib.sha256(f"{stage}|{_norm(detail)}".encode("utf-8", "replace")).hexdigest()[:12]


def harvest(root: Path) -> list[dict]:
    """Collect unique {stage, detail, provenance, key} failures from every workspace."""
    seen: dict[str, dict] = {}
    for eng in sorted(root.glob("book_workspace/*/_engine")):
        slug = eng.parent.name
        hs = eng / "HARDSTOP.json"
        if hs.exists():
            try:
                d = json.loads(hs.read_text(encoding="utf-8"))
                _add(seen, d.get("stage", "?"), d.get("detail", ""), f"{slug} (HARDSTOP.json @ {d.get('ts','?')})")
            except Exception:
                pass
        log = eng / "log.jsonl"
        if log.exists():
            for line in log.read_text(encoding="utf-8", errors="replace").splitlines():
                line = line.strip()
                if '"HARDSTOP"' not in line:
                    continue
                try:
                    ev = json.loads(line)
                except Exception:
                    continue
                if ev.get("event") == "HARDSTOP":
                    _add(seen, ev.get("stage", "?"), ev.get("detail", ""), f"{slug} (log @ {ev.get('ts','?')})")
    return list(seen.values())


def _add(seen: dict, stage: str, detail: str, provenance: str) -> None:
    k = key_of(stage, detail)
    if k not in seen:
        seen[k] = {"key": k, "stage": stage, "detail": detail.strip(), "provenance": provenance}


def existing_keys(out: Path) -> set[str]:
    if not out.exists():
        return set()
    return set(re.findall(re.escape(STAGE_MARK) + r"([0-9a-f]{12})", out.read_text(encoding="utf-8", errors="replace")))


def render_entry(e: dict) -> str:
    raw = re.sub(r"\s+", " ", (e["detail"] or "").strip())
    # the engine stores the TAIL of a tool's output as detail; cut the JSON dump off so
    # the symptom line stays legible (the curator can open the run for the full context).
    symptom = (raw.split("{", 1)[0].strip() or raw)[:180] if raw else "(no detail)"
    # a cause/fix supplied by hand (--add) renders verbatim; harvested entries carry no
    # such keys and keep the curator placeholders (curation stays human, the §4 pause).
    cause = re.sub(r"\s+", " ", (e.get("cause") or "").strip()) or "_[curator: root cause]_"
    fix = re.sub(r"\s+", " ", (e.get("fix") or "").strip()) or "_[curator: the change that prevents it]_"
    return (
        f"\n### [PROPOSED] {e['stage']} — {symptom[:80]}\n"
        f"{STAGE_MARK}{e['key']} -->\n"
        f"- **Symptom:** {symptom}\n"
        f"- **Cause:** {cause}\n"
        f"- **Fix:** {fix}\n"
        f"- **Proposed gate:** _[curator: the mechanical/perceptual check that would catch this next time]_\n"
        f"- **Provenance:** {e['provenance']}\n"
        f"- **STATUS:** PROPOSED — endorse, then move into `docs/LESSONS_LEDGER.md` (with its gate) and delete this block.\n"
    )


def stage_entries(entries: list[dict], out: Path) -> dict:
    have = existing_keys(out)
    fresh = [e for e in entries if e["key"] not in have]
    if fresh:
        header = ("# Lessons staging (auto-drafted, awaiting human endorsement)\n\n"
                  "*Auto-drafted by `ledger_stage.py` from engine gate failures. Each block is a "
                  "PROPOSED lesson: fill Cause/Fix/Proposed-gate, then promote it into "
                  "`docs/LESSONS_LEDGER.md` and delete it here. This file is scratch; the ledger is canon.*\n")
        out.parent.mkdir(parents=True, exist_ok=True)
        body = out.read_text(encoding="utf-8", errors="replace") if out.exists() else header
        body += "".join(render_entry(e) for e in fresh)
        out.write_text(body, encoding="utf-8")
    return {"scanned": len(entries), "staged_new": len(fresh),
            "already_present": len(entries) - len(fresh), "out": str(out)}


def selftest() -> int:
    import contextlib, io, tempfile
    fails = []
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        eng = root / "book_workspace" / "_x" / "_engine"
        eng.mkdir(parents=True)
        (eng / "HARDSTOP.json").write_text(json.dumps(
            {"stage": "produce:epub", "detail": "build_epub exit 1: no cover-image property",
             "ts": "2026-07-12T00:00:00Z"}), "utf-8")
        (eng / "log.jsonl").write_text(
            json.dumps({"ts": "t", "event": "HARDSTOP", "stage": "verify",
                        "detail": "verify_build --format all FAIL: interior PDF not found"}) + "\n", "utf-8")
        out = root / "docs" / "_lessons_staging.md"
        r1 = stage_entries(harvest(root), out)
        if r1["staged_new"] != 2:
            fails.append(f"expected 2 staged, got {r1['staged_new']} ({r1})")
        # idempotent: a second scan stages nothing new
        r2 = stage_entries(harvest(root), out)
        if r2["staged_new"] != 0:
            fails.append(f"second scan should stage 0, staged {r2['staged_new']}")
        txt = out.read_text("utf-8")
        if txt.count("### [PROPOSED]") != 2:
            fails.append(f"expected 2 PROPOSED blocks, got {txt.count('### [PROPOSED]')}")
        if "produce:epub" not in txt or "verify" not in txt:
            fails.append("staged entries missing expected stages")
        # --add carrying cause/fix (drive the real CLI path — that is where the segments
        # were being dropped). Idempotency must still key on stage+detail alone, so the
        # re-add with a different cause/fix stages nothing new.
        add4 = "gate-3 | blacklist term leak in running headers | lint swept prose only | sweep header XML too"
        dup4 = "gate-3 | blacklist term leak in running headers | some other cause | some other fix"
        add2 = "gate-5 | page count not divisible by four"
        with contextlib.redirect_stdout(io.StringIO()):
            for spec in (add4, dup4, add2):
                main(["--add", spec, "--out", str(out), "--json"])
        txt = out.read_text("utf-8")
        if txt.count("### [PROPOSED]") != 4:
            fails.append(f"--add: expected 4 PROPOSED blocks, got {txt.count('### [PROPOSED]')}")
        if "- **Cause:** lint swept prose only" not in txt:
            fails.append("--add: supplied cause missing from the staged block")
        if "- **Fix:** sweep header XML too" not in txt:
            fails.append("--add: supplied fix missing from the staged block")
        if "some other cause" in txt:
            fails.append("--add: same stage+symptom re-staged (key must be stage+detail only)")
        tail = txt.split("### [PROPOSED] gate-5", 1)
        if len(tail) < 2 or "_[curator: root cause]_" not in tail[1] \
                or "_[curator: the change that prevents it]_" not in tail[1]:
            fails.append("--add without cause/fix must keep the curator placeholders")
    if fails:
        print("LEDGER_STAGE SELFTEST: FAIL")
        for f in fails:
            print("  - " + f)
        return 1
    print("LEDGER_STAGE SELFTEST: PASS (harvests HARDSTOPs -> proposed lessons, idempotent; --add carries cause/fix)")
    return 0


def main(argv=None) -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    ap = argparse.ArgumentParser(description="Auto-draft candidate lessons from engine gate failures.")
    ap.add_argument("--root", default=str(ROOT), help="kit root to scan (default: the kit)")
    ap.add_argument("--out", default=str(DEFAULT_OUT), help="staging file to append to")
    ap.add_argument("--add", help='stage one entry by hand: "stage | symptom | cause | fix" '
                                  "(cause/fix optional; omitted segments keep the curator placeholders)")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)

    if args.selftest:
        return selftest()
    out = Path(args.out)
    if args.add:
        # the advertised contract is "stage | symptom | cause | fix", but segments 3 and 4
        # were parsed and silently dropped until 2026-07-28: the nested-additionalProperties
        # lesson (staging key a31bc99cbf09) landed with curator placeholders that had to be
        # hand-edited in docs/_lessons_staging.md after the fact. Carry them through; blank
        # or omitted segments fall back to the placeholders in render_entry(). maxsplit=3
        # lets the fix segment itself contain "|" without truncation.
        parts = [p.strip() for p in args.add.split("|", 3)]
        stage = parts[0] if parts else "manual"
        detail = parts[1] if len(parts) > 1 else ""
        e = {"key": key_of(stage, detail), "stage": stage, "detail": detail,
             "provenance": "manual --add",
             "cause": parts[2] if len(parts) > 2 else "",
             "fix": parts[3] if len(parts) > 3 else ""}
        res = stage_entries([e], out)
    else:
        res = stage_entries(harvest(Path(args.root)), out)
    if args.json:
        print(json.dumps(res, ensure_ascii=False))
    else:
        print(f"ledger_stage: scanned {res['scanned']} failure(s); staged {res['staged_new']} new, "
              f"{res['already_present']} already present -> {res['out']}")
        if res["staged_new"]:
            print("  review + endorse the PROPOSED blocks, then promote into docs/LESSONS_LEDGER.md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
