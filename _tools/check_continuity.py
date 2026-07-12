#!/usr/bin/env python3
r"""
check_continuity.py — _CONTINUITY.md self-consistency gate (BOOKSMITH).

PURPOSE (KIT_ARCHITECTURE two-verifier model; CLAUDE.md COMPACTION SURVIVAL)
    The COMPACTION-SURVIVAL ledger (book_workspace/<slug>/_CONTINUITY.md) is the
    load-bearing resume artifact: a stale or self-contradicting ledger sends a
    resuming session to the wrong place (the one real book shipped with a header
    that said COMPLETE while the footer token still said IN_PROGRESS and the DONE
    list named 4 of 13 written chapters). Nothing gated that. This does.

    A ledger is INCONSISTENT (nonzero exit) when any of:
      (a) STATUS disagreement — the header 'STATUS:' token, the footer HTML-
          comment 'STATUS:' token, and a SHIPPED marker do not agree on
          COMPLETE-vs-IN_PROGRESS.
      (b) COMPLETE but still mid-draft — header STATUS==COMPLETE yet the ledger
          still carries a 'NEXT -> draft ...' imperative.
      (c) DONE undercount — the DONE chapter list names FEWER units than the
          count of manuscript/current/*_current.md files on disk (the ledger
          fell behind the drafting).

CONTRACT
    python check_continuity.py --workspace <book_workspace/slug dir>
        [--ledger <path>]         explicit ledger path (default <ws>/_CONTINUITY.md)
        [--fix]                   rewrite the ledger to a consistent COMPLETE/
                                  SHIPPED state (export path only; read-only by
                                  default — verify_build calls it without --fix)
    -> prints a JSON object on stdout:
        {"ledger":..., "consistent":bool, "defects":[...], "status":{...}}
       Exit 0 if consistent, 1 if any defect, 2 on usage/IO error.

    verify_build.py wires this into the FINAL/export sweep (--final); it is not
    run on ordinary per-format interim verifies (an in-progress ledger is
    legitimately IN_PROGRESS mid-book).
"""
import argparse
import json
import re
import sys
from pathlib import Path

STATUS_COMPLETE = "COMPLETE"
STATUS_IN_PROGRESS = "IN_PROGRESS"


def _first_status_token(text: str):
    """First COMPLETE/IN_PROGRESS keyword in a fragment, or None."""
    m = re.search(r"\b(COMPLETE|IN_PROGRESS)\b", text)
    return m.group(1) if m else None


def _header_status(lines):
    """STATUS token from the header (a '(STATUS: X)' on the first heading line,
    else the first STATUS: occurrence in the top few lines)."""
    for ln in lines[:6]:
        m = re.search(r"STATUS:\s*([A-Z_]+)", ln)
        if m:
            return _first_status_token(m.group(1)) or _first_status_token(ln)
    return None


def _footer_status(text):
    """STATUS token from the LAST HTML comment that carries 'STATUS:'. A legend
    comment ('STATUS: IN_PROGRESS (working) | COMPLETE (done)') is ambiguous —
    we take the FIRST keyword after 'STATUS:'; a corrected ledger writes a single
    unambiguous token there."""
    comments = re.findall(r"<!--(.*?)-->", text, re.S)
    for c in reversed(comments):
        if "STATUS:" in c:
            frag = c.split("STATUS:", 1)[1]
            return _first_status_token(frag)
    return None


def _has_shipped_marker(text):
    """A SHIPPED marker (e.g. '✅ SHIPPED', 'SHIPPED 2026-...') implies COMPLETE."""
    return bool(re.search(r"\bSHIPPED\b", text))


_NEXT_DRAFT_RE = re.compile(
    r"NEXT\s*(?:->|→|:)?.*?\bdraft\b", re.IGNORECASE)


def _has_next_draft(text):
    """A 'NEXT -> draft ...' imperative still in the ledger."""
    for ln in text.splitlines():
        if _NEXT_DRAFT_RE.search(ln):
            return ln.strip()
    return None


_UNIT_ID_RE = re.compile(r"\b((?:ch|chapter|part|prologue|epilogue|coda)_?\d{1,3})\b",
                         re.IGNORECASE)


def _done_units_in_ledger(text):
    """Unit ids named in DONE sections of the ledger. We scan the whole ledger
    for unit-id tokens (ch_01, part_3, ...) and normalize to lowercase — an
    undercount is what we are guarding, so a superset scan is the safe side."""
    ids = set()
    for m in _UNIT_ID_RE.finditer(text):
        ids.add(m.group(1).lower().replace("chapter", "ch").replace("_", ""))
    return ids


def _disk_current_units(ws: Path):
    """Unit ids with a manuscript/current/*_current.md file on disk."""
    cur = ws / "manuscript" / "current"
    if not cur.exists():
        return []
    ids = []
    for p in sorted(cur.glob("*_current.md")):
        stem = p.name[:-len("_current.md")]
        ids.append(stem)
    return ids


def _norm(uid: str) -> str:
    return uid.lower().replace("chapter", "ch").replace("_", "")


def analyze(ledger_path: Path, ws: Path):
    """Return (consistent, defects, status_dict)."""
    text = ledger_path.read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines()

    header = _header_status(lines)
    footer = _footer_status(text)
    shipped = _has_shipped_marker(text)
    next_draft = _has_next_draft(text)

    defects = []

    # (a) STATUS disagreement across header / footer / SHIPPED marker.
    tokens = [t for t in (header, footer) if t is not None]
    if shipped:
        tokens.append(STATUS_COMPLETE)
    distinct = set(tokens)
    if len(distinct) > 1:
        defects.append(
            f"STATUS disagreement: header={header}, footer={footer}, "
            f"shipped_marker={'COMPLETE' if shipped else 'none'} — the tokens "
            f"must agree")

    complete = (header == STATUS_COMPLETE) or (footer == STATUS_COMPLETE) or shipped

    # (b) COMPLETE but a NEXT-draft imperative survives.
    if (header == STATUS_COMPLETE or shipped) and next_draft:
        defects.append(
            f"header/marker says COMPLETE but a NEXT-draft imperative remains: "
            f"'{next_draft}'")

    # (c) DONE undercount vs disk.
    disk_units = _disk_current_units(ws)
    if disk_units:
        ledger_ids = _done_units_in_ledger(text)
        disk_ids = {_norm(u) for u in disk_units}
        missing = sorted(disk_ids - ledger_ids)
        if complete and missing:
            defects.append(
                f"DONE undercount: {len(disk_units)} unit(s) on disk "
                f"(manuscript/current) but the ledger does not name "
                f"{len(missing)}: {missing[:8]}")

    status = {
        "header": header, "footer": footer, "shipped_marker": shipped,
        "next_draft": next_draft, "disk_current_units": len(disk_units),
    }
    return (not defects, defects, status)


def _fix_ledger(ledger_path: Path, ws: Path) -> list:
    """Rewrite the ledger to a consistent COMPLETE/SHIPPED state: header STATUS
    -> COMPLETE, footer HTML-comment STATUS token -> COMPLETE, drop the NEXT-draft
    imperative. Returns a list of the edits made. Export-path only."""
    text = ledger_path.read_text(encoding="utf-8", errors="replace")
    edits = []

    def sub_report(pattern, repl, s, label, flags=0):
        new, n = re.subn(pattern, repl, s, flags=flags)
        if n:
            edits.append(f"{label} ({n})")
        return new

    # Header '(STATUS: X)' -> COMPLETE.
    text = sub_report(r"(STATUS:\s*)IN_PROGRESS", r"\1COMPLETE", text,
                      "header/footer STATUS -> COMPLETE")
    # Footer legend comment -> single COMPLETE token.
    text = sub_report(r"<!--\s*STATUS:.*?-->",
                      "<!-- STATUS: COMPLETE (done — recovery will NOT fire). -->",
                      text, "footer comment -> COMPLETE", flags=re.S)
    # Drop NEXT-draft imperative lines.
    kept = []
    for ln in text.splitlines():
        if _NEXT_DRAFT_RE.search(ln):
            edits.append("removed NEXT-draft imperative line")
            continue
        kept.append(ln)
    text = "\n".join(kept)
    if not text.endswith("\n"):
        text += "\n"
    ledger_path.write_text(text, encoding="utf-8")
    return edits


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

    ap = argparse.ArgumentParser(
        description="_CONTINUITY.md self-consistency gate (BOOKSMITH).")
    ap.add_argument("--workspace", required=True,
                    help="book_workspace/<slug> dir holding _CONTINUITY.md.")
    ap.add_argument("--ledger", help="Explicit ledger path "
                                     "(default <workspace>/_CONTINUITY.md).")
    ap.add_argument("--fix", action="store_true",
                    help="Rewrite the ledger to a consistent COMPLETE/SHIPPED "
                         "state (export path only; read-only otherwise).")
    args = ap.parse_args()

    ws = Path(args.workspace)
    ledger_path = Path(args.ledger) if args.ledger else ws / "_CONTINUITY.md"
    if not ledger_path.exists():
        print(json.dumps({"ledger": str(ledger_path), "consistent": True,
                          "defects": [], "note": "no _CONTINUITY.md — nothing to check"}))
        return 0

    if args.fix:
        edits = _fix_ledger(ledger_path, ws)
        # Re-analyze after the fix so the exit code reflects the corrected file.
        consistent, defects, status = analyze(ledger_path, ws)
        print(json.dumps({"ledger": str(ledger_path), "consistent": consistent,
                          "fixed": edits, "defects": defects, "status": status},
                         ensure_ascii=False))
        return 0 if consistent else 1

    consistent, defects, status = analyze(ledger_path, ws)
    print(json.dumps({"ledger": str(ledger_path), "consistent": consistent,
                      "defects": defects, "status": status}, ensure_ascii=False))
    return 0 if consistent else 1


if __name__ == "__main__":
    sys.exit(main())
