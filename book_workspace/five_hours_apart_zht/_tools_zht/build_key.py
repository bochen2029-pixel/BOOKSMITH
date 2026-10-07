#!/usr/bin/env python3
"""build_key.py: compile the key (registry + amendments) against the frozen source into the gate tables.

Writes (never edit these by hand):
  _generated/key_gates.json   per unit, per seq: the rows that fire there with their required forms and tier
  _generated/census.tsv       per row: count, first_use, every matching segment id (review the exceptions here)
  _generated/validation.txt   rows whose pattern never matches, rows with no required form, duplicate forms
  _generated/slices/<unit>.md the worker pack for each unit: the segments with ids, and the key rows that fire
Exit 1 on a bad regex, a duplicate id, or a tier other than H/M/L.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import zht_common as C  # noqa: E402


def main():
    segs = C.load_segments()
    rows = C.parse_registry(amendments=os.path.join(C.KEY, "registry_amendments_zht.tsv"))
    forbidden = C.load_forbidden()
    gates, census, problems = {}, [], []
    fired_by_unit = {u: [] for u in C.UNITS}
    for r in rows:
        if r["tier"] not in ("H", "M", "L"):
            raise SystemExit("row %s: tier must be H, M or L" % r["id"])
        if not r["re"]:
            census.append((r["id"], 0, "", ""))
            continue
        hits = []
        for u in C.UNITS:
            for s in segs.get(u, []):
                if r["spec"]["types"] and s["type"] not in r["spec"]["types"]:
                    continue
                m = r["re"].search(s["text"])
                if m:
                    hits.append(s["id"])
                    forms = C.required_forms(r) or ([m.group(0)] if r["zh-Hant"] == "=" else [])
                    if r["tier"] in ("H", "M") and s["id"] not in r["spec"]["excepts"] and forms:
                        gates.setdefault(u, {}).setdefault(str(s["seq"]), []).append(
                            {"id": r["id"], "tier": r["tier"], "forms": forms, "en": r["EN"].split(";;")[0].strip()})
                        if r["id"] not in fired_by_unit[u]:
                            fired_by_unit[u].append(r["id"])
        census.append((r["id"], len(hits), hits[0] if hits else "", " ".join(hits)))
        if not hits:
            problems.append("NO MATCH   %s   pattern=%s" % (r["id"], r["EN"]))
        if r["tier"] in ("H", "M") and not C.required_forms(r) and r["zh-Hant"] != "=":
            problems.append("NO FORM    %s   (H/M row without a zh-Hant form or @accept)" % r["id"])
        bad = r["spec"]["excepts"] - set(hits)
        if bad:
            problems.append("EXCEPT MISS %s   @except names non-matching ids: %s" % (r["id"], ",".join(sorted(bad))))
    C.write(os.path.join(C.GEN, "key_gates.json"), json.dumps(gates, ensure_ascii=False, indent=1))
    C.write(os.path.join(C.GEN, "census.tsv"), "id\tcount\tfirst_use\tmatches\n" +
            "\n".join("%s\t%d\t%s\t%s" % c for c in census) + "\n")
    C.write(os.path.join(C.GEN, "validation.txt"), "\n".join(problems) + ("\n" if problems else "clean\n"))
    byid = {r["id"]: r for r in rows}
    for u in C.UNITS:
        lines = ["# Worker pack: %s" % u, "", "Segments (translate block for block; keep the count exactly):", ""]
        for s in segs.get(u, []):
            lines.append("### %s  [%s]" % (s["id"], s["type"]))
            lines.append("")
            lines.append(s["text"])
            lines.append("")
        lines += ["", "## Key rows that fire in this unit (locked forms; H = must appear, M = should, L = note)", "",
                  "| id | tier | EN | zh-Hant | note |", "|---|---|---|---|---|"]
        for rid in fired_by_unit[u]:
            r = byid[rid]
            lines.append("| %s | %s | %s | %s | %s |" % (rid, r["tier"], r["EN"].split(";;")[0].strip().replace("|", "\\|"),
                                                       (r["zh-Hant"] + (" / " + " / ".join(r["spec"]["accepts"]) if r["spec"]["accepts"] else "")).replace("|", "\\|"),
                                                       r["note"].replace("|", "\\|")))
        lines += ["", "## Forbidden in prose (FAIL unless marked WARN)", ""] + \
                 ["- `%s`  %s  %s" % (f["pattern"], f["tier"], f["reason"]) for f in forbidden] + [""]
        C.write(os.path.join(C.GEN, "slices", u + ".md"), "\n".join(lines))
    print("rows: %d   units: %d   gates: %d sites   problems: %d" % (
        len(rows), len(C.UNITS), sum(len(v) for g in gates.values() for v in g.values()), len(problems)))
    for p in problems:
        print("  " + p)
    return 0


if __name__ == "__main__":
    sys.exit(main())
