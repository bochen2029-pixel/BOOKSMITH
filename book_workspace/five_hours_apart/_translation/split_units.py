#!/usr/bin/env python3
"""split_units.py: cut the finished story into the English workspace's units, verbatim.

The author's structure is kept exactly (the title block, three Part H1s, eighteen chapter H2s); every unit is the
text between one heading and the next, and the concatenation of the units in UNITS order must reproduce the
source byte for byte (asserted). Units:
  front   the H1 title, the italic subtitle, the epigraph row
  part_N  one H1 each
  ch_NN   one H2 each, with its prose, dialogue and log blocks
Usage: python split_units.py --source ../../intake/five-hours-apart.md --out manuscript/current
"""
import argparse
import os
import re
import sys


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--source", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    with open(a.source, encoding="utf-8-sig") as f:
        src = f.read().replace("\r\n", "\n")
    if not src.endswith("\n"):
        src += "\n"
    lines = src.split("\n")
    # heading lines that start a unit: "# Part ..." or "## ..."; the very first "# " is the title (front)
    starts = []
    for i, l in enumerate(lines):
        if i == 0 and l.startswith("# "):
            starts.append((i, "front"))
        elif l.startswith("# Part "):
            starts.append((i, "part"))
        elif l.startswith("## "):
            starts.append((i, "ch"))
    units = []
    n_part = n_ch = 0
    for k, (i, kind) in enumerate(starts):
        j = starts[k + 1][0] if k + 1 < len(starts) else len(lines)
        body = "\n".join(lines[i:j]).rstrip("\n") + "\n"
        if kind == "front":
            uid = "front"
        elif kind == "part":
            n_part += 1
            uid = "part_%d" % n_part
        else:
            n_ch += 1
            uid = "ch_%02d" % n_ch
        units.append((uid, body))
    # round trip: units joined with one blank line == source (modulo the trailing newline)
    joined = "\n".join(u[1] for u in units)
    if joined.rstrip("\n") != src.rstrip("\n"):
        sys.exit("round-trip FAILED: the units do not reproduce the source")
    os.makedirs(a.out, exist_ok=True)
    for uid, body in units:
        p = os.path.join(a.out, uid + "_current.md")
        with open(p, "w", encoding="utf-8", newline="\n") as f:
            f.write(body)
        blocks = [b for b in re.split(r"\n\s*\n", body) if b.strip()]
        print("%-8s %4d blocks  %6d words  %s" % (uid, len(blocks), len(body.split()), body.split("\n")[0][:60]))
    print("UNITS = (" + ", ".join('"%s"' % u[0] for u in units) + ")")
    print("round trip OK: %d units, %d lines" % (len(units), len(lines)))


if __name__ == "__main__":
    main()
