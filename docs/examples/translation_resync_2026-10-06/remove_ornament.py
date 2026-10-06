#!/usr/bin/env python3
"""remove_ornament.py: the lone ✦ paragraph under the Acknowledgments H1 is the kit's own heading ornament (every
unit shows one in the author's docx because the delivered Word edition prints it); it is not text. Remove it from
the English unit and both Chinese units (new append-only drafts), and drop the matching EN lint waiver.
"""
import json
import os
import shutil
import sys

EN = "C:/BOOKSMITH/book_workspace/across_borders"
ZT = "C:/BOOKSMITH/book_workspace/across_borders_zht"
ZS = "C:/BOOKSMITH/book_workspace/across_borders_zhs"


def rd(p):
    return open(p, encoding="utf-8").read()


def wr(p, s):
    with open(p, "w", encoding="utf-8", newline="\n") as f:
        f.write(s)


def strip_orn(s, label):
    old = "\n\n\u2726\n\n"
    if s.count(old) != 1:
        sys.exit("ABORT %s: expected one ornament paragraph, found %d" % (label, s.count(old)))
    return s.replace(old, "\n\n")


def next_draft(ws, unit):
    n = 1
    while os.path.exists("%s/translation/drafts/%s_v%d.md" % (ws, unit, n)):
        n += 1
    return "%s/translation/drafts/%s_v%d.md" % (ws, unit, n)


# EN
p = EN + "/manuscript/current/acknowledgments_current.md"
wr(p, strip_orn(rd(p), "EN"))
print("OK  EN acknowledgments_current.md: ornament removed")
cfg = EN + "/book_config.json"
c = json.load(open(cfg, encoding="utf-8"))
w = c.get("voice", {}).get("lint_waivers", [])
if "\u2726" in w:
    w.remove("\u2726")
    with open(cfg, "w", encoding="utf-8", newline="\n") as f:
        json.dump(c, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print("OK  EN lint waiver for the ornament removed (%d waivers left)" % len(w))

# zht, zhs
for ws, label in ((ZT, "zht"), (ZS, "zhs")):
    p = ws + "/translation/current/acknowledgments.md"
    s = strip_orn(rd(p), label)
    d = next_draft(ws, "acknowledgments")
    wr(d, s)
    shutil.copyfile(d, p)
    print("OK  %s acknowledgments -> %s + current (ornament removed)" % (label, os.path.basename(d)))
print("DONE")
