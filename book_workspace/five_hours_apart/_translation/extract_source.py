#!/usr/bin/env python3
"""extract_source.py: FREEZE the English source of record for translation (BOOK_TRANSLATION_METHOD_v3 §6.1 step 1).

Reads manuscript/current/<unit>_current.md in UNITS order (the reading order), cuts every unit into segments
exactly as segment_peek.py and unit_patch.py cut a translation (blocks separated by blank lines), types each
segment, and writes:
  segments.jsonl      one line per segment: id, unit, seq, type, text   (the gate's and the workers' alignment)
  source_of_record.md the concatenation of the units, the single text every edition is aligned to
  P0_REPORT.json      sha256 of the source of record, per-unit counts, totals, freeze time
Run from the English workspace: python _translation/extract_source.py
"""
import datetime
import hashlib
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WS = os.path.dirname(HERE)

UNITS = ("front", "part_1", "ch_01", "ch_02", "ch_03", "ch_04", "ch_05", "ch_06", "ch_07", "ch_08", "ch_09",
         "part_2", "ch_10", "ch_11", "ch_12", "ch_13", "ch_14",
         "part_3", "ch_15", "ch_16", "ch_17", "ch_18")


def seg_type(b):
    s = b.strip()
    if s.startswith("```"):
        return "code"
    if s.startswith("# "):
        return "h1"
    if s.startswith("## "):
        return "h2"
    if s.startswith(">"):
        return "quote"
    if s.startswith("*") and s.endswith("*") and s.count("*") == 2:
        return "italic"
    if s.startswith('"'):
        return "dialogue"
    return "para"


def main():
    cur = os.path.join(WS, "manuscript", "current")
    segs, bodies, report_units = [], [], []
    for u in UNITS:
        p = os.path.join(cur, u + "_current.md")
        with open(p, encoding="utf-8-sig") as f:
            body = f.read().replace("\r\n", "\n")
        bodies.append(body.rstrip("\n") + "\n")
        blocks = [b.strip("\n") for b in re.split(r"\n\s*\n", body) if b.strip()]
        types = {}
        for i, b in enumerate(blocks, 1):
            t = seg_type(b)
            types[t] = types.get(t, 0) + 1
            segs.append({"id": "%s.%03d" % (u, i), "unit": u, "seq": i, "type": t, "text": b})
        report_units.append({"unit": u, "segments": len(blocks), "words": len(body.split()), "types": types,
                             "sha256": hashlib.sha256(body.encode("utf-8")).hexdigest()})
    sor = "\n".join(bodies)
    out = HERE
    with open(os.path.join(out, "segments.jsonl"), "w", encoding="utf-8", newline="\n") as f:
        for s in segs:
            f.write(json.dumps(s, ensure_ascii=False) + "\n")
    with open(os.path.join(out, "source_of_record.md"), "w", encoding="utf-8", newline="\n") as f:
        f.write(sor)
    sha = hashlib.sha256(sor.encode("utf-8")).hexdigest()
    rep = {
        "frozen_at": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
        "source_of_record": "_translation/source_of_record.md",
        "sha256": sha,
        "units": report_units,
        "segments_total": len(segs),
        "words_total": len(sor.split()),
        "types_total": {t: sum(1 for s in segs if s["type"] == t) for t in sorted(set(s["type"] for s in segs))},
    }
    # the intake file, when present, must be the same text
    intake = os.path.join(os.path.dirname(os.path.dirname(WS)), "intake", "five-hours-apart.md")
    if os.path.exists(intake):
        with open(intake, encoding="utf-8-sig") as f:
            it = f.read().replace("\r\n", "\n")
        rep["intake_identical"] = (it.rstrip("\n") == sor.rstrip("\n"))
        rep["intake_sha256"] = hashlib.sha256(it.encode("utf-8")).hexdigest()
    with open(os.path.join(out, "P0_REPORT.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump(rep, f, ensure_ascii=False, indent=2)
    print("segments: %d   words: %d   sha256: %s" % (len(segs), rep["words_total"], sha))
    for r in report_units:
        print("  %-8s %4d seg  %6d words  %s" % (r["unit"], r["segments"], r["words"], r["types"]))
    if "intake_identical" in rep:
        print("intake identical:", rep["intake_identical"])
        if not rep["intake_identical"]:
            sys.exit(1)


if __name__ == "__main__":
    main()
