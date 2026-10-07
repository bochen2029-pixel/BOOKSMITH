#!/usr/bin/env python3
"""rows_zhs.py: keep the zh-Hans row blocks set in the same columns as the zh-Hant rows they derive from.

The rows inside fenced blocks are a table set in a monospace face. The derivation changes the width of some cells
(发消息 for 傳訊, 拉斯科利纳斯 for LAS COLINAS, 工牌 for 識別證), which shifts every column after them. realign()
re-pads each derived block against its zh-Hant block: two cells that start in the same display column in zh-Hant
start in the same display column in zh-Hans; a column moves right only as far as a wider cell needs, and every column
to its right moves with it; every gap stays at least two spaces. check() is the gate's half: a derived block must be
exactly what realign() would make of it.

Display width: East Asian Wide and Fullwidth characters are 2, and so are the curly quotes “ ” ‘ ’, which stand
where 「」『』 stood and are full-width in a CJK face; everything else is 1.

  python3 _tools_zhs/rows_zhs.py ch_16      # show how the published unit's rows differ from their realignment
"""
import os
import re
import sys
import unicodedata

FENCE = re.compile(r"(```.*?```)", re.S)
WIDE_QUOTES = set("“”‘’")


def width(s):
    return sum(2 if (unicodedata.east_asian_width(c) in "WF" or c in WIDE_QUOTES) else 1 for c in s)


def cells(row):
    """[(start column, text), ...]: the row split at runs of two or more spaces."""
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


def realign_fence(tw_fence, cn_fence):
    """Return (the zh-Hans fence re-padded against the zh-Hant fence, notes on rows it could not align)."""
    _, tw_rows, _ = _split(tw_fence)
    head, cn_rows, tail = _split(cn_fence)
    if len(tw_rows) != len(cn_rows):
        return cn_fence, ["%d rows in zh-Hant, %d here" % (len(tw_rows), len(cn_rows))]
    notes, pairs = [], []
    for k, (a, b) in enumerate(zip(tw_rows, cn_rows)):
        ca, cb = cells(a), cells(b)
        if len(ca) != len(cb):
            notes.append("row %d: %d cells in zh-Hant, %d here" % (k + 1, len(ca), len(cb)))
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
        for (tw_start, _), (_, txt) in zip(ca, cb):
            line += " " * max(0, f[tw_start] - width(line)) + txt
        out.append(line)
    return "\n".join([head] + out + [tail]), notes


def realign(tw_text, cn_text, log=None):
    """Re-pad every fenced block of cn_text against the matching fenced block of tw_text."""
    tw_parts, cn_parts = FENCE.split(tw_text), FENCE.split(cn_text)
    tw_f, cn_f = tw_parts[1::2], cn_parts[1::2]
    if len(tw_f) != len(cn_f):
        if log is not None:
            log.append("rows      %d fenced blocks in zh-Hant, %d here: not realigned" % (len(tw_f), len(cn_f)))
        return cn_text
    for j, (a, b) in enumerate(zip(tw_f, cn_f)):
        new, notes = realign_fence(a, b)
        if log is not None:
            for n in notes:
                log.append("rows      block %d: %s" % (j + 1, n))
            moved = sum(1 for x, y in zip(b.split("\n"), new.split("\n")) if x != y)
            if moved:
                log.append("rows      block %d: %d row(s) re-padded to the zh-Hant columns" % (j + 1, moved))
        cn_parts[2 * j + 1] = new
    return "".join(cn_parts)


def check(tw_fence, cn_fence):
    """Gate: the issues that keep cn_fence from being its own realignment against tw_fence."""
    new, notes = realign_fence(tw_fence, cn_fence)
    issues = list(notes)
    if new != cn_fence:
        for x, y in zip(cn_fence.split("\n"), new.split("\n")):
            if x != y:
                issues.append("not set in the zh-Hant columns: %r should be %r" % (x, y))
                break
    return issues


def main():
    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    for u in sys.argv[1:]:
        tw = open(os.path.join(here, "_zht_ref", "translation_current", u + ".md"), encoding="utf-8").read()
        cn = open(os.path.join(here, "translation", "current", u + ".md"), encoding="utf-8").read()
        for a, b in zip(FENCE.split(tw)[1::2], FENCE.split(cn)[1::2]):
            for iss in check(a, b):
                print("%s  %s" % (u, iss))
    return 0


if __name__ == "__main__":
    sys.exit(main())
