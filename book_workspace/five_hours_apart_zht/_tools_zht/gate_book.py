#!/usr/bin/env python3
"""gate_book.py: the whole-book sweep of the zh-Hant-TW edition.

  python _tools_zht/gate_book.py translation/current

Runs gate_unit on every unit present, then the book-level checks: every unit present; the refrain census
(沒有什麼該來 as often as the source says "nothing is due"); 您 nowhere; the cross-unit echoes (a line the log rows
quote from the prose must be identical in both places); no paragraph identical to another prose paragraph.
Exit 0 = 0 FAIL.
"""
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import zht_common as C  # noqa: E402
import gate_unit as G  # noqa: E402

ECHOES = [
    # (segment that quotes, segment quoted) -> the quoted Chinese line must appear in both blocks
    ("ch_16", "ch_04", "從來沒有人替我舉過牌子"),
    ("ch_16", "ch_04", "不糟"),
    ("ch_16", "ch_04", "這是手機"),
    ("ch_16", "ch_04", "這是牌子"),
    ("ch_16", "ch_04", "是我"),
    ("ch_16", "ch_06", "是十一點。而十一點很忙"),
    ("ch_16", "ch_06", "對它有差"),
    ("ch_16", "ch_12", "這星期沒有"),
    ("ch_16", "ch_12", "你問過為什麼是降落"),
    ("ch_16", "ch_09", "一張音符清單對一首歌來說是真的"),
    ("ch_17", "ch_01", "假設這是一個星期二"),
    ("front", "ch_18", "預期   重型機  海上   未閉"),
]


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    d = sys.argv[1]
    segs = C.load_segments()
    gates = json.load(open(os.path.join(C.GEN, "key_gates.json"), encoding="utf-8"))
    rows = C.parse_registry(amendments=os.path.join(C.KEY, "registry_amendments_zht.tsv"))
    headings, forbidden, allowed = G.heading_table(rows), C.load_forbidden(), C.load_allowed_latin()
    texts, fails = {}, 0
    for u in C.UNITS:
        p = os.path.join(d, u + ".md")
        if not os.path.exists(p):
            p2 = os.path.join(d, u + "_current.md")
            p = p2 if os.path.exists(p2) else None
        if not p:
            print("FAIL  MISSING %s: no file in %s" % (u, d))
            fails += 1
            continue
        texts[u] = C.read(p)
        fails += G.gate(u, texts[u], segs, gates, headings, forbidden, allowed, quiet=True)
    book = "\n\n".join(texts[u] for u in C.UNITS if u in texts)
    src = "\n\n".join(s["text"] for u in C.UNITS for s in segs[u])
    n_src = len(re.findall(r"nothing(?:'s| is) due", src, flags=re.I))
    n_tgt = book.count("沒有什麼該來")
    if n_tgt < n_src:
        print("FAIL  REFRAIN 沒有什麼該來 appears %d times, the source says 'nothing is due' %d times" % (n_tgt, n_src))
        fails += 1
    if "您" in book:
        print("FAIL  您 appears %d times (family and colleagues say 你)" % book.count("您"))
        fails += 1
    for quoting, quoted, line in ECHOES:
        if quoting in texts and quoted in texts:
            if line not in texts[quoting] or line not in texts[quoted]:
                print("FAIL  ECHO %r must appear in both %s and %s" % (line, quoting, quoted))
                fails += 1
    seen = {}
    for u in C.UNITS:
        if u not in texts:
            continue
        for b in C.blocks(texts[u]):
            if C.seg_type(b) in ("para", "dialogue") and C.cjk_count(b) > 25:
                if b in seen:
                    print("FAIL  DUPLICATE paragraph in %s already in %s: %s…" % (u, seen[b], b[:30]))
                    fails += 1
                seen[b] = u
    print("BOOK  %d units checked, %d FAIL" % (len(texts), fails))
    return 0 if fails == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
