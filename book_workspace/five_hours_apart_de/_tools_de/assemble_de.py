#!/usr/bin/env python3
"""assemble_es.py: stitch translation/current/<unit>.md, in UNITS order, into the ONE version-pinned master
outputs/markdown/five_hours_apart_de_v<N>.md (the anti-drift keystone) and print the census: blocks per unit against
the frozen source, German and English words, the sha256.

  python3 _tools_de/assemble_es.py --version 1
Exit 1 if a unit is missing or a unit's block count differs from the source.
"""
import argparse
import hashlib
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import de_common as C  # noqa: E402


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--version", type=int, required=True)
    a = ap.parse_args()
    segs = C.load_segments()
    parts, bad, es_total, en_total = [], 0, 0, 0
    for u in C.UNITS:
        p = os.path.join(C.WS, "translation", "current", u + ".md")
        if not os.path.exists(p):
            print("MISSING  %s" % u)
            bad += 1
            continue
        t = C.read(p).rstrip("\n") + "\n"
        n_t, n_s = len(C.blocks(t)), len(segs[u])
        es_w, en_w = C.words(t), sum(C.words(s["text"]) for s in segs[u])
        es_total, en_total = es_total + es_w, en_total + en_w
        flag = "" if n_t == n_s else "   <-- block count differs from the source (%d)" % n_s
        bad += 1 if flag else 0
        print("  %-8s %4d blocks  %6d words (EN %5d)%s" % (u, n_t, es_w, en_w, flag))
        parts.append(t)
    master = "\n".join(parts)
    out = os.path.join(C.WS, "outputs", "markdown", "five_hours_apart_de_v%d.md" % a.version)
    C.write(out, master)
    print("master: %s   units %d/%d   words %d (EN %d, x%.2f)   sha256 %s" % (
        os.path.relpath(out, C.WS), len(parts), len(C.UNITS), es_total, en_total, es_total / max(en_total, 1),
        hashlib.sha256(master.encode("utf-8")).hexdigest()[:16]))
    return 0 if bad == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
