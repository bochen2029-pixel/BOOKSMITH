#!/usr/bin/env python3
"""add_unit.py: add (or move) a unit in one or more book_config.json files, schema-validated, with a
backup, and print the checklist of every OTHER place a translated edition's pipeline enumerates its
units, because the config is only the first of them (see docs/BOOK_TRANSLATION_METHOD_v3.md, the
"adding a unit" section).

Usage:
  python _tools/add_unit.py --config EN/book_config.json --config ZHT/book_config.json --config ZHS/book_config.json \
      --id acknowledgments --titles "Acknowledgments" "致謝" "致谢" --after ch_10 [--class C] [--target-words 700]
  python _tools/add_unit.py --config ... --id acknowledgments --move --after ch_10      # relocate an existing unit
One --titles value per --config, in the same order (ignored with --move). --before ID instead of --after ID.
Exit 0 ok / 1 refused (unit exists, anchor missing, schema invalid) / 2 usage.
"""
import argparse
import json
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SCHEMA = os.path.join(HERE, "book_config.schema.json")

CHECKLIST = """
Other places that enumerate or count units (check each; the config is only the first):
  - the frozen source: re-run the English workspace's _translation/extract_source.py after adding its UNITS
    tuple, then copy segments.jsonl into every edition's _key/ and run build_key.py there
  - hard-coded UNITS lists in the per-edition gate modules (e.g. _tools_zht/zht_common.py, _tools_zhs/zhs_common.py):
    build_key.py raises ValueError('x' is not in list) and gate_unit.py says 'unknown unit' otherwise
  - EXPECT counts in final_checks_*.py and sweeps_*.py (units, h1), docstrings mentioning '18 units'
  - the continuity ledger (_CONTINUITY.md) must NAME every unit id: the continuity gate scans for them
  - privacy/fence regexes written for the narration (e.g. the author's wife's name) may need the new unit exempted
  - layout maps (layout_map_*.json): re-solve after the text changes
  - package READMEs / upload checklists with unit counts or page counts
  - the new unit's own file in manuscript/current (English) and translation/current (editions), one H1 equal to the title
"""


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--config", action="append", required=True)
    ap.add_argument("--id", required=True)
    ap.add_argument("--titles", nargs="*", default=[])
    ap.add_argument("--after")
    ap.add_argument("--before")
    ap.add_argument("--move", action="store_true")
    ap.add_argument("--class", dest="klass", default="C")
    ap.add_argument("--target-words", type=int)
    a = ap.parse_args()
    if not (a.after or a.before) or (a.after and a.before):
        ap.error("give exactly one of --after ID / --before ID")
    if not a.move and len(a.titles) != len(a.config):
        ap.error("give one --titles value per --config (%d configs, %d titles)" % (len(a.config), len(a.titles)))
    try:
        import jsonschema
        schema = json.load(open(SCHEMA, encoding="utf-8"))
    except Exception:
        jsonschema = None
        schema = None
    rc = 0
    for i, cp in enumerate(a.config):
        c = json.load(open(cp, encoding="utf-8"))
        ids = [u["id"] for u in c["units"]]
        anchor = a.after or a.before
        if anchor not in ids:
            print("REFUSED %s: anchor %s not in units" % (cp, anchor))
            rc = 1
            continue
        if a.move:
            if a.id not in ids:
                print("REFUSED %s: %s not in units (nothing to move)" % (cp, a.id))
                rc = 1
                continue
            entry = [u for u in c["units"] if u["id"] == a.id][0]
            c["units"] = [u for u in c["units"] if u["id"] != a.id]
        else:
            if a.id in ids:
                print("REFUSED %s: %s already in units" % (cp, a.id))
                rc = 1
                continue
            entry = {"id": a.id, "title": a.titles[i], "class": a.klass}
            if a.target_words:
                entry["target_words"] = a.target_words
        ids = [u["id"] for u in c["units"]]
        pos = ids.index(anchor) + (1 if a.after else 0)
        c["units"].insert(pos, entry)
        if jsonschema and schema:
            try:
                jsonschema.validate(c, schema)
            except Exception as e:  # noqa: BLE001
                print("REFUSED %s: schema invalid after edit: %s" % (cp, str(e)[:200]))
                rc = 1
                continue
        shutil.copy2(cp, cp + ".before_add_unit.bak")
        with open(cp, "w", encoding="utf-8", newline="\n") as f:
            json.dump(c, f, ensure_ascii=False, indent=2)
            f.write("\n")
        print("OK  %s: %s %s -> %s (%d units)" % (cp, "moved" if a.move else "added", a.id,
                                                   [u["id"] for u in c["units"]], len(c["units"])))
    print(CHECKLIST)
    return rc


if __name__ == "__main__":
    sys.exit(main())
