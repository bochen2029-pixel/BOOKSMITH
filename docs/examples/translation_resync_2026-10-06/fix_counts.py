#!/usr/bin/env python3
"""fix_counts.py: the book now has 19 units / 19 H1 (Acknowledgments added). Update the hard-coded expectations in
final_checks_*.py and sweeps_*.py of both editions. Every replacement asserts exactly one hit."""
import sys

EDITS = [
    ("C:/BOOKSMITH/book_workspace/across_borders_zht/_scripts_zht/final_checks_zht.py",
     'EXPECT = {"units": 18, "h1": 18, "h3": 84, "images": 14, "labels_min": 70}',
     'EXPECT = {"units": 19, "h1": 19, "h3": 84, "images": 14, "labels_min": 70}  # 19 since the 2026-10-06 Acknowledgments unit'),
    ("C:/BOOKSMITH/book_workspace/across_borders_zhs/_scripts_zhs/final_checks_zhs.py",
     'EXPECT = {"units": 18, "h1": 18, "h3": 84, "images": 14, "labels_min": 70}',
     'EXPECT = {"units": 19, "h1": 19, "h3": 84, "images": 14, "labels_min": 70}  # 19 since the 2026-10-06 Acknowledgments unit'),
    ("C:/BOOKSMITH/book_workspace/across_borders_zht/_scripts_zht/sweeps_zht.py",
     "EXPECT_H1, EXPECT_H3, EXPECT_IMG = 18, 84, 14",
     "EXPECT_H1, EXPECT_H3, EXPECT_IMG = 19, 84, 14  # 19 since the 2026-10-06 Acknowledgments unit"),
    ("C:/BOOKSMITH/book_workspace/across_borders_zhs/_scripts_zhs/sweeps_zhs.py",
     "EXPECT_H1, EXPECT_H3, EXPECT_IMG = 18, 84, 14",
     "EXPECT_H1, EXPECT_H3, EXPECT_IMG = 19, 84, 14  # 19 since the 2026-10-06 Acknowledgments unit"),
    ("C:/BOOKSMITH/book_workspace/across_borders_zht/_scripts_zht/sweeps_zht.py",
     "(18 units + About", "(19 units + About"),
    ("C:/BOOKSMITH/book_workspace/across_borders_zhs/_scripts_zhs/sweeps_zhs.py",
     "(18 units + About", "(19 units + About"),
]
for p, old, new in EDITS:
    s = open(p, encoding="utf-8").read()
    if s.count(new) == 1 and s.count(old) == 0:
        print("--  already:", p.rsplit("/", 1)[1], old[:40])
        continue
    if s.count(old) != 1:
        sys.exit("ABORT %s: expected 1 hit for %r, found %d" % (p, old[:50], s.count(old)))
    with open(p, "w", encoding="utf-8", newline="\n") as f:
        f.write(s.replace(old, new))
    print("OK ", p.rsplit("/", 1)[1], "->", new[:60])
print("DONE")
