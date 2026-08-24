#!/usr/bin/env python3
"""authorship_ledger.py — who wrote what: the human-vs-machine provenance ledger.

H0 (cloud/PLAN_H0_2026-08-24.md §0.3, D3): every substantive change to a unit's
current prose is attributed — actor "human" (a manual web/desktop edit) or "ai"
(an engine draft / revise). Append-only JSONL at registry/authorship_ledger.jsonl;
a derived convenience file registry/human_edited_units.json lists the units whose
LATEST author is human (lint downgrades voice findings to advisory there — a
dash a human typed is their voice, not an AI tell; an AI re-roll of the unit
re-enters the hard gate because the latest actor flips back to "ai").

The ledger is data first: rows carry before/after sha256 and added/removed line
counts, so a colored diff view, the passport's human/machine line, and any later
training-data boundary can all be derived without re-instrumenting.

Library + CLI:
  python _tools/authorship_ledger.py append --workspace WS --unit UID \
      --actor human|ai --verb web-edit|revise|draft [--before F] [--after F] [--note "..."]
  python _tools/authorship_ledger.py human-units --workspace WS   # prints JSON list
"""
from __future__ import annotations

import argparse
import difflib
import hashlib
import json
import os
import sys
import time
from pathlib import Path

LEDGER_REL = Path("registry") / "authorship_ledger.jsonl"
HUMAN_REL = Path("registry") / "human_edited_units.json"


def _sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _diff_counts(before: str, after: str) -> tuple[int, int]:
    added = removed = 0
    for line in difflib.unified_diff(before.splitlines(), after.splitlines(), lineterm=""):
        if line.startswith("+") and not line.startswith("+++"):
            added += 1
        elif line.startswith("-") and not line.startswith("---"):
            removed += 1
    return added, removed


def _atomic_write(path: Path, text: str) -> None:
    tmp = path.with_name(f".{path.name}.tmp{os.getpid()}")
    tmp.write_text(text, encoding="utf-8", newline="\n")
    os.replace(tmp, path)


def append_row(workspace: Path, unit: str, actor: str, verb: str,
               before_text: str = "", after_text: str = "", note: str = "") -> dict:
    """Append one attribution row and refresh human_edited_units.json."""
    if actor not in ("human", "ai"):
        raise ValueError(f"actor must be human|ai, got {actor!r}")
    ws = Path(workspace)
    ledger = ws / LEDGER_REL
    ledger.parent.mkdir(parents=True, exist_ok=True)
    added, removed = _diff_counts(before_text, after_text)
    row = {
        "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "unit": unit,
        "actor": actor,
        "verb": verb,
        "sha_before": _sha(before_text) if before_text else None,
        "sha_after": _sha(after_text) if after_text else None,
        "added_lines": added,
        "removed_lines": removed,
    }
    if note:
        row["note"] = str(note)[:500]
    with open(ledger, "a", encoding="utf-8", newline="\n") as fh:
        fh.write(json.dumps(row, ensure_ascii=False) + "\n")
    _refresh_human_units(ws)
    return row


def latest_actor_by_unit(workspace: Path) -> dict:
    ws = Path(workspace)
    ledger = ws / LEDGER_REL
    out: dict[str, str] = {}
    if not ledger.exists():
        return out
    for line in ledger.read_text("utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue  # a torn tail line must never poison the whole ledger
        if row.get("unit") and row.get("actor"):
            out[row["unit"]] = row["actor"]
    return out


def human_units(workspace: Path) -> list[str]:
    return sorted(u for u, a in latest_actor_by_unit(workspace).items() if a == "human")


def _refresh_human_units(workspace: Path) -> None:
    ws = Path(workspace)
    _atomic_write(ws / HUMAN_REL, json.dumps(human_units(ws), indent=2) + "\n")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("append")
    a.add_argument("--workspace", required=True)
    a.add_argument("--unit", required=True)
    a.add_argument("--actor", required=True, choices=["human", "ai"])
    a.add_argument("--verb", required=True)
    a.add_argument("--before", default=None, help="file holding the prior text")
    a.add_argument("--after", default=None, help="file holding the new text")
    a.add_argument("--note", default="")
    h = sub.add_parser("human-units")
    h.add_argument("--workspace", required=True)
    args = ap.parse_args(argv)

    if args.cmd == "human-units":
        print(json.dumps(human_units(Path(args.workspace))))
        return 0
    before = Path(args.before).read_text("utf-8") if args.before else ""
    after = Path(args.after).read_text("utf-8") if args.after else ""
    row = append_row(Path(args.workspace), args.unit, args.actor, args.verb,
                     before, after, args.note)
    print(json.dumps(row, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
