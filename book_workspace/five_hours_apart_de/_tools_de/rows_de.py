#!/usr/bin/env python3
"""rows_de.py: keep the German row blocks set in the columns of the English rows they translate (charter §10).

German cells are often longer than the English ones, so a translated block drifts out of its columns. realign_fence()
re-pads a German block against its English block: two cells that start in the same column in the English start in
the same column in the German; a column moves right only as far as a wider cell needs, every column to its right
moves with it, and every gap stays at least two spaces. A wrapped quote keeps its continuation line under the quote.
check() is the gate's half: a German block must be exactly its own realignment. (The same algorithm as the zh-Hans
edition's rows_zhs.py, measured in a Latin monospace face: one column per character, none for a combining mark.)

  python3 _tools_de/rows_de.py <unit> [--fix]      # show (or repair) the rows of translation/current/<unit>.md
"""
import os
import re
import sys
import unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import de_common as C  # noqa: E402

FENCE = re.compile(r"(```.*?```)", re.S)


def width(s):
    w = 0
    for c in s:
        if unicodedata.combining(c):
            continue
        w += 2 if unicodedata.east_asian_width(c) in "WF" else 1
    return w


def cells(row):
    parts = re.split(r"( {2,})", row.rstrip())
    out, col = [], 0
    for i, p in enumerate(parts):
        if i % 2 == 0:
            out.append((col, p))
        col += width(p)
    return out


def _split(fence):
    lines = fence.split("\n")
    return lines[0], lines[1:-1], lines[-1]


def realign_fence(en_fence, es_fence):
    _, en_rows, _ = _split(en_fence)
    head, es_rows, tail = _split(es_fence)
    if len(en_rows) != len(es_rows):
        return es_fence, ["%d rows in the English, %d here" % (len(en_rows), len(es_rows))]
    notes, pairs = [], []
    for k, (a, b) in enumerate(zip(en_rows, es_rows)):
        ca, cb = cells(a), cells(b)
        if len(ca) != len(cb):
            notes.append("row %d: %d cells in the English, %d here" % (k + 1, len(ca), len(cb)))
            cb = None
        pairs.append((ca, cb, b))
    starts = sorted({c[0] for ca, cb, _ in pairs if cb for c in ca})
    f, prev = {}, None
    for p in starts:
        lo = p if prev is None else p + (f[prev] - prev)
        for ca, cb, _ in pairs:
            if not cb:
                continue
            for i in range(1, len(ca)):
                if ca[i][0] == p:
                    lo = max(lo, f[ca[i - 1][0]] + width(cb[i - 1][1]) + 2)
        f[p], prev = lo, p
    out = []
    for ca, cb, raw in pairs:
        if not cb:
            out.append(raw)
            continue
        line = ""
        for (en_start, _), (_, txt) in zip(ca, cb):
            line += " " * max(0, f[en_start] - width(line)) + txt
        out.append(line)
    return "\n".join([head] + out + [tail]), notes


def check(en_fence, es_fence):
    new, notes = realign_fence(en_fence, es_fence)
    issues = list(notes)
    if new != es_fence:
        for x, y in zip(es_fence.split("\n"), new.split("\n")):
            if x != y:
                issues.append("not set in the English columns: %r should be %r" % (x, y))
                break
    return issues


def realign_unit(unit, text, segs):
    """Re-pad every fenced block of a German unit against the English segment it translates."""
    bl = C.blocks(text)
    src = segs[unit]
    changed = 0
    for i, s in enumerate(src):
        if s["type"] == "code" and i < len(bl) and C.de_type(bl[i]) == "code":
            new, _ = realign_fence(s["text"], bl[i])
            if new != bl[i]:
                bl[i], changed = new, changed + 1
    return "\n\n".join(bl) + "\n", changed


def main():
    segs = C.load_segments()
    fix = "--fix" in sys.argv
    for u in [a for a in sys.argv[1:] if not a.startswith("--")]:
        p = os.path.join(C.WS, "translation", "current", u + ".md")
        t = C.read(p)
        if fix:
            new, n = realign_unit(u, t, segs)
            if n:
                C.write(p, new)
            print("%s: %d block(s) re-padded" % (u, n))
            continue
        bl = C.blocks(t)
        for i, s in enumerate(segs[u]):
            if s["type"] == "code" and i < len(bl):
                for iss in check(s["text"], bl[i]):
                    print("%s.%03d  %s" % (u, i + 1, iss))
    return 0


if __name__ == "__main__":
    sys.exit(main())
