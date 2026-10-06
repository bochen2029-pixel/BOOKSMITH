#!/usr/bin/env python3
"""add_d11.py: source defect D11 (the replaced Epilogue photo vs the chapter's own timeline) into both charters."""
import re
import sys

ZT = "C:/BOOKSMITH/book_workspace/across_borders_zht/translation_charter_zht.md"
ZS = "C:/BOOKSMITH/book_workspace/across_borders_zhs/translation_charter_zhs.md"
D11 = ("the author's replacement for the ch_10 figure (his 2026-10-02 laptop photo of record BRIT606322, the "
       "specimen finished and a 9:35 AM taskbar) sits under the unchanged caption and text of September 22, 2026 "
       "at 1:53 PM with the record just begun; the photo is also 981 px wide, so it prints small under the 300 ppi "
       "floor (the original camera file would print larger); caption and text translated as written")

s = open(ZT, encoding="utf-8").read()
if "| D11 |" not in s:
    m = re.search(r"^\| D10 \|.*\n", s, re.M)
    if not m:
        sys.exit("ABORT zht: D10 row not found")
    s = s[:m.end()] + "| D11 | %s |\n" % D11 + s[m.end():]
    open(ZT, "w", encoding="utf-8", newline="\n").write(s)
    print("OK  zht D11")
s = open(ZS, encoding="utf-8").read()
if "D11 (" not in s:
    old = "D10 ("
    i = s.find(old)
    if i < 0:
        sys.exit("ABORT zhs: D10 entry not found")
    j = s.find("\n", i)
    line = s[i:j]
    s = s[:j] + " D11 (%s)." % D11 + s[j:]
    open(ZS, "w", encoding="utf-8", newline="\n").write(s)
    print("OK  zhs D11")
print("DONE")
