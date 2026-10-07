#!/usr/bin/env python3
"""seg_peek.py: show a source segment and its aligned zh-Hant / zh-Hans target paragraphs.
Alignment is positional (segment parity: n-th segment of a unit = n-th non-empty paragraph of
the unit's translation/current file).
Usage: python seg_peek.py UNIT SEQ [SEQ ...]
"""
import json
import sys

AB = "C:/BOOKSMITH/book_workspace/across_borders/_translation/segments.jsonl"
ZT = "C:/BOOKSMITH/book_workspace/across_borders_zht/translation/current/%s.md"
ZS = "C:/BOOKSMITH/book_workspace/across_borders_zhs/translation/current/%s.md"


def paras(path):
    with open(path, encoding="utf-8") as f:
        return [ln.strip() for ln in f.read().split("\n") if ln.strip()]


def main():
    unit = sys.argv[1]
    seqs = [int(s) for s in sys.argv[2:]]
    segs = {}
    with open(AB, encoding="utf-8") as f:
        for ln in f:
            d = json.loads(ln)
            if d["unit"] == unit:
                segs[d["seq"]] = d
    zt = paras(ZT % unit)
    zs = paras(ZS % unit)
    print("unit %s: src=%d zht=%d zhs=%d paragraphs" % (unit, len(segs), len(zt), len(zs)))
    for s in seqs:
        d = segs.get(s)
        print("\n--- %s.%03d [%s]" % (unit, s, d["type"] if d else "?"))
        print("SRC: " + (d["text"] if d else "(none)"))
        print("ZHT: " + (zt[s - 1] if s - 1 < len(zt) else "(none)"))
        print("ZHS: " + (zs[s - 1] if s - 1 < len(zs) else "(none)"))


if __name__ == "__main__":
    main()
