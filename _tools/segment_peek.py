#!/usr/bin/env python3
"""segment_peek.py: show a frozen source segment beside the paragraph aligned to it in one or more
translated editions, and check segment parity per unit. Alignment is positional: the n-th block of a
unit's translation (blocks separated by blank lines, exactly as the key's extractor cut the source)
corresponds to source segment n. A unit whose counts differ is listed so the drift is found before a
gate fails on it.

Usage:
  python _tools/segment_peek.py --segments WS/_translation/segments.jsonl \
      --target zht=WS_zht/translation/current --target zhs=WS_zhs/translation/current ch_06 41 42 43
  python _tools/segment_peek.py --segments ... --target ... --parity        # counts for every unit
The segments file is the JSONL written by the workspace's extract_source.py (fields: id, unit, seq, type, text).
Target directories hold <unit>.md or <unit>_current.md.
"""
import argparse
import json
import os
import re
import sys


GLOSS_MARKER = "大意"  # 大意: the one sanctioned extra block, a gloss line under a verbatim label


def blocks(path, gloss_marker=GLOSS_MARKER):
    """Blocks of a translated unit, split as the extractor split the source (blank lines), with the
    sanctioned gloss lines (a quote block carrying the gloss marker) set aside so positions align."""
    with open(path, encoding="utf-8-sig") as f:
        raw = [p.strip() for p in re.split(r"\n\s*\n", f.read()) if p.strip()]
    aligned, glosses = [], 0
    for b in raw:
        if gloss_marker and b.startswith(">") and gloss_marker in b.split("\n", 1)[0]:
            glosses += 1
            continue
        aligned.append(b)
    return _Blocks(aligned, glosses)


class _Blocks(list):
    def __init__(self, items, glosses):
        super().__init__(items)
        self.glosses = glosses


def unit_file(d, unit):
    for cand in (os.path.join(d, unit + ".md"), os.path.join(d, unit + "_current.md")):
        if os.path.exists(cand):
            return cand
    return None


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--segments", required=True)
    ap.add_argument("--target", action="append", default=[], help="LABEL=DIR (repeatable)")
    ap.add_argument("--parity", action="store_true", help="print source vs target block counts for every unit")
    ap.add_argument("unit", nargs="?")
    ap.add_argument("seqs", nargs="*", type=int)
    a = ap.parse_args()
    segs = {}
    order = []
    with open(a.segments, encoding="utf-8") as f:
        for ln in f:
            d = json.loads(ln)
            if d["unit"] not in segs:
                order.append(d["unit"])
            segs.setdefault(d["unit"], {})[d["seq"]] = d
    targets = []
    for t in a.target:
        label, _, d = t.partition("=")
        targets.append((label, d))
    if a.parity or not a.unit:
        bad = 0
        print("%-16s %6s" % ("unit", "src") + "".join(" %6s" % l for l, _ in targets))
        for u in order:
            row = "%-16s %6d" % (u, len(segs[u]))
            for label, d in targets:
                p = unit_file(d, u)
                b = blocks(p) if p else None
                n = len(b) if b is not None else -1
                row += " %6s" % (("%d+%dg" % (n, b.glosses) if b.glosses else n) if n >= 0 else "none")
                if n != len(segs[u]):
                    bad += 1
            print(row)
        print("units with a count mismatch (gloss lines excluded): %d" % bad)
        return 1 if bad else 0
    u = a.unit
    if u not in segs:
        sys.exit("unknown unit %s (segments hold: %s)" % (u, ", ".join(order)))
    tb = []
    for label, d in targets:
        p = unit_file(d, u)
        tb.append((label, blocks(p) if p else []))
    print("unit %s: src=%d" % (u, len(segs[u])) + "".join(" %s=%d" % (l, len(b)) for l, b in tb))
    for s in a.seqs:
        d = segs[u].get(s)
        print("\n--- %s.%03d [%s]" % (u, s, d["type"] if d else "?"))
        print("SRC: " + (d["text"] if d else "(none)"))
        for label, b in tb:
            print("%s: %s" % (label.upper(), b[s - 1] if 0 < s <= len(b) else "(none)"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
