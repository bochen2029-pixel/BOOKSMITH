#!/usr/bin/env python3
"""apply_strings_units.py: for both Chinese editions, (1) set about_the_author in
translation/current/config_strings_<ed>.json from the moderator's draft file, (2) insert the
acknowledgments unit into book_config.json units[] after the glossary. Idempotent; backs up first.
"""
import json
import os
import shutil
import sys

S = "C:/Users/user/AppData/Local/Temp/claude/C--BOOKSMITH/3dc2e6dc-74d7-48cc-ba0a-983066f72ee5/scratchpad"
ED = {
    "zht": ("C:/BOOKSMITH/book_workspace/across_borders_zht", "致謝", S + "/about_zht_draft.txt"),
    "zhs": ("C:/BOOKSMITH/book_workspace/across_borders_zhs", "致谢", S + "/about_zhs_draft.txt"),
}


def jload(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def jdump(p, obj):
    with open(p, "w", encoding="utf-8", newline="\n") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)
        f.write("\n")


for ed, (ws, title, about_file) in ED.items():
    bk = ws + "/_key/_pre_resync_2026-09-28"
    os.makedirs(bk, exist_ok=True)
    # 1. config strings
    sp = ws + "/translation/current/config_strings_%s.json" % ed
    if not os.path.exists(bk + "/config_strings_%s.json" % ed):
        shutil.copy2(sp, bk + "/config_strings_%s.json" % ed)
    s = jload(sp)
    about = open(about_file, encoding="utf-8").read().strip()
    if s.get("about_the_author") != about:
        s["about_the_author"] = about
        jdump(sp, s)
        print("OK  %s config_strings about_the_author set (%d chars, %d paragraphs)"
              % (ed, len(about), about.count("\n\n") + 1))
    else:
        print("--  %s config_strings about_the_author already current" % ed)
    # 2. units[]
    cp = ws + "/book_config.json"
    if not os.path.exists(bk + "/book_config.json"):
        shutil.copy2(cp, bk + "/book_config.json")
    c = jload(cp)
    ids = [u["id"] for u in c["units"]]
    if "acknowledgments" in ids:
        print("--  %s units[] already has acknowledgments" % ed)
    else:
        gi = ids.index("glossary")
        c["units"].insert(gi + 1, {"id": "acknowledgments", "title": title, "class": "C", "target_words": 700})
        jdump(cp, c)
        print("OK  %s units[] acknowledgments inserted after glossary with title %s" % (ed, title))
    # schema check
    import jsonschema
    jsonschema.validate(jload(cp), jload("C:/BOOKSMITH/_tools/book_config.schema.json"))
    print("OK  %s book_config.json schema-valid (%d units)" % (ed, len(jload(cp)["units"])))
print("DONE")
