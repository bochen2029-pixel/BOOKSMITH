#!/usr/bin/env python3
"""assemble_zhs.py: stitch translation/current/<unit>.md of the zh-Hans edition, in UNITS order, into the ONE
version-pinned master outputs/markdown/five_hours_apart_zhs_v<N>.md (the anti-drift keystone), and print the census:
blocks per unit against the frozen source, CJK characters, the sha256.

  python3 _tools_zhs/assemble_zhs.py --version 1
Exit 1 if a unit is missing or a unit's block count differs from the source.
"""
import argparse
import hashlib
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WS = os.path.dirname(HERE)
ZHT = os.path.join(os.path.dirname(WS), "five_hours_apart_zht")
sys.path.insert(0, os.path.join(ZHT, "_tools_zht"))
import zht_common as C  # noqa: E402


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--version", type=int, required=True)
    ap.add_argument("--dir", default=os.path.join(WS, "translation", "current"))
    ap.add_argument("--slug", default=os.path.basename(WS))
    a = ap.parse_args()
    segs = C.load_segments(os.path.join(WS, "_key", "segments.jsonl"))
    parts, bad, total = [], 0, 0
    for u in C.UNITS:
        p = os.path.join(a.dir, u + ".md")
        if not os.path.exists(p):
            print("MISSING  %s" % u)
            bad += 1
            continue
        t = C.read(p).rstrip("\n") + "\n"
        n_t, n_s = len(C.blocks(t)), len(segs[u])
        cjk = C.cjk_count(t)
        total += cjk
        flag = "" if n_t == n_s else "   <-- block count differs from the source (%d)" % n_s
        bad += 1 if flag else 0
        print("  %-8s %4d blocks  %6d CJK%s" % (u, n_t, cjk, flag))
        parts.append(t)
    master = "\n".join(parts)
    out = os.path.join(WS, "outputs", "markdown", "%s_v%d.md" % (a.slug, a.version))
    C.write(out, master)
    print("master: %s   units %d/%d   CJK %d   sha256 %s" % (os.path.relpath(out, WS), len(parts), len(C.UNITS), total,
                                                              hashlib.sha256(master.encode("utf-8")).hexdigest()[:16]))
    return 0 if bad == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
