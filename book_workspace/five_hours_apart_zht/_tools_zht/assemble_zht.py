#!/usr/bin/env python3
"""assemble_zht.py: stitch translation/current/<unit>.md in UNITS order into the ONE version-pinned master
outputs/markdown/<slug>_v<N>.md (the anti-drift keystone: every format and every reviewer reads this file), and
print the census: units present, blocks per unit against the frozen source, CJK characters, the sha256.

  python3 _tools_zht/assemble_zht.py --version 1 [--dir translation/current] [--slug five_hours_apart_zht]
Exit 1 if a unit is missing or a unit's block count differs from the source.
"""
import argparse
import hashlib
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import zht_common as C  # noqa: E402


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--version", type=int, required=True)
    ap.add_argument("--dir", default=os.path.join(C.WS, "translation", "current"))
    ap.add_argument("--slug", default=os.path.basename(C.WS))
    ap.add_argument("--segments", default=os.path.join(C.KEY, "segments.jsonl"))
    a = ap.parse_args()
    segs = C.load_segments(a.segments)
    parts, bad, total_cjk = [], 0, 0
    for u in C.UNITS:
        p = os.path.join(a.dir, u + ".md")
        if not os.path.exists(p):
            print("MISSING  %s" % u)
            bad += 1
            continue
        t = C.read(p).rstrip("\n") + "\n"
        n_t, n_s = len(C.blocks(t)), len(segs[u])
        cjk = C.cjk_count(t)
        total_cjk += cjk
        flag = "" if n_t == n_s else "   <-- block count differs from the source (%d)" % n_s
        if flag:
            bad += 1
        print("  %-8s %4d blocks  %6d CJK%s" % (u, n_t, cjk, flag))
        parts.append(t)
    master = "\n".join(parts)
    out = os.path.join(C.WS, "outputs", "markdown", "%s_v%d.md" % (a.slug, a.version))
    C.write(out, master)
    print("master: %s   units %d/%d   CJK %d   sha256 %s" % (os.path.relpath(out, C.WS), len(parts), len(C.UNITS),
                                                              total_cjk, hashlib.sha256(master.encode("utf-8")).hexdigest()[:16]))
    return 0 if bad == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
