#!/usr/bin/env python3
"""fix_unit_order.py: the author's file places Acknowledgments between the Epilogue (ch_10) and the
Glossary. Move the unit there in: the three book_config.json files, the two gate UNITS lists, and the
English extractor's UNITS list. Every text edit asserts exactly one hit.
"""
import json
import sys

CONFIGS = [
    "C:/BOOKSMITH/book_workspace/across_borders/book_config.json",
    "C:/BOOKSMITH/book_workspace/across_borders_zht/book_config.json",
    "C:/BOOKSMITH/book_workspace/across_borders_zhs/book_config.json",
]
TEXT_EDITS = [
    ("C:/BOOKSMITH/book_workspace/across_borders_zht/_tools_zht/zht_common.py",
     '"ch_09", "ch_10", "glossary", "acknowledgments", "image_credits"]',
     '"ch_09", "ch_10", "acknowledgments", "glossary", "image_credits"]'),
    ("C:/BOOKSMITH/book_workspace/across_borders_zhs/_tools_zhs/zhs_common.py",
     '"ch_09", "ch_10", "glossary", "acknowledgments", "image_credits"]',
     '"ch_09", "ch_10", "acknowledgments", "glossary", "image_credits"]'),
    ("C:/BOOKSMITH/book_workspace/across_borders/_translation/extract_source.py",
     "    ('glossary', 'glossary_current.md'),\n    ('acknowledgments', 'acknowledgments_current.md'),\n",
     "    ('acknowledgments', 'acknowledgments_current.md'),\n    ('glossary', 'glossary_current.md'),\n"),
]

for p in CONFIGS:
    c = json.load(open(p, encoding="utf-8"))
    ids = [u["id"] for u in c["units"]]
    if ids.index("acknowledgments") == ids.index("ch_10") + 1:
        print("--  already ordered:", p)
        continue
    ack = [u for u in c["units"] if u["id"] == "acknowledgments"][0]
    c["units"] = [u for u in c["units"] if u["id"] != "acknowledgments"]
    c["units"].insert([u["id"] for u in c["units"]].index("ch_10") + 1, ack)
    with open(p, "w", encoding="utf-8", newline="\n") as f:
        json.dump(c, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print("OK  units reordered:", p, [u["id"] for u in c["units"]][-4:])

for p, old, new in TEXT_EDITS:
    s = open(p, encoding="utf-8").read()
    if s.count(new) == 1 and s.count(old) == 0:
        print("--  already ordered:", p)
        continue
    if s.count(old) != 1:
        sys.exit("ABORT %s: expected 1 hit, found %d" % (p, s.count(old)))
    with open(p, "w", encoding="utf-8", newline="\n") as f:
        f.write(s.replace(old, new))
    print("OK  reordered:", p)
print("DONE")
