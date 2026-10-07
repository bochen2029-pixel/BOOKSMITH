#!/usr/bin/env python3
"""fix_zhs_amendments.py: the zhs amendment file allows one row per id and only ids with a base registry row.
Remove the appended duplicate P007 row and the ML59 row; fold the ZR54 note into the existing P007 row.
"""
import sys

P = "C:/BOOKSMITH/book_workspace/across_borders_zhs/_key/registry_amendments_zhs.tsv"
lines = open(P, encoding="utf-8").read().split("\n")
out = []
removed = 0
for ln in lines:
    if ln.startswith("P007\t") and "ZR54 (2026-10-06" in ln:
        removed += 1
        continue
    if ln.startswith("ML59\t") and "ZR55 (2026-10-06" in ln:
        removed += 1
        continue
    out.append(ln)
if removed != 2:
    sys.exit("ABORT: expected to remove 2 appended rows, removed %d" % removed)
base = [i for i, ln in enumerate(out) if ln.startswith("P007\t")]
if len(base) != 1:
    sys.exit("ABORT: expected exactly one base P007 row, found %d" % len(base))
i = base[0]
if "ZR54" not in out[i]:
    out[i] = out[i].rstrip() + (" | ZR54 (2026-10-06, P10 re-sync): the author's own Acknowledgments "
                                "(acknowledgments.006, .011) name his wife Weiming in Latin letters (book one's zhs "
                                "P21); 我太太 stays the form at acknowledgments.006; the privacy rule governs the "
                                "narrative units only. ZR55: the ML59 narrowing lives in locale_layer_zhs.txt.")
with open(P, "w", encoding="utf-8", newline="\n") as f:
    f.write("\n".join(out))
print("OK  removed %d appended rows; ZR54/ZR55 folded into the base P007 note (line %d)" % (removed, i + 1))
