#!/usr/bin/env python3
"""test_gate_zhs.py: the must-fail battery of the zh-Hans gate (the gate is trusted only while this prints ALL CASES BEHAVE).

  python3 _tools_zhs/test_gate_zhs.py [--dir translation/current] [--suffix .md] [--unit ch_16]

Takes one derived unit that PASSES, then mutates it one defect at a time (corner quotes, ASCII quotes, 您, a Taiwan
residue, a traditional-only character, a broken heading, merged blocks, a dropped machine token, a row shifted off its column, a removed H form)
and asserts the gate FAILS each one. Exit 1 if any case misbehaves.
"""
import io
import os
import sys
from contextlib import redirect_stdout

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import gate_zhs as G  # noqa: E402
C = G.C


def run(unit, text, key):
    segs, gates, headings, residue, allowed = key
    with redirect_stdout(io.StringIO()):
        return G.gate(unit, text, segs, gates, headings, residue, allowed, quiet=True)


def main():
    args = sys.argv[1:]
    d = args[args.index("--dir") + 1] if "--dir" in args else os.path.join(G.WS, "translation", "current")
    suffix = args[args.index("--suffix") + 1] if "--suffix" in args else ".md"
    unit = args[args.index("--unit") + 1] if "--unit" in args else "ch_12"  # prose + rows
    path = os.path.join(d, unit + suffix)
    if not os.path.exists(path):
        print("no file %s" % path)
        return 2
    segs, gates, headings = G.load_key()
    key = (segs, gates, headings, G.forbidden_residue(), C.load_allowed_latin(os.path.join(G.ZHT, "_key", "allowed_latin.txt")))
    text = C.read(path)
    blocks = C.blocks(text)
    src = segs[unit]
    prose = [i for i, s in enumerate(src) if s["type"] in ("para", "dialogue") and i < len(blocks)]
    code = [i for i, s in enumerate(src) if s["type"] == "code" and i < len(blocks)]
    if not prose:
        print("unit %s has no prose block" % unit)
        return 2
    pi = prose[0]
    cases = [("clean text", text, 0)]

    def with_block(i, new):
        b = list(blocks)
        b[i] = new
        return "\n\n".join(b) + "\n"

    cases.append(("corner quote", with_block(pi, blocks[pi] + "「"), 1))
    cases.append(("ASCII quote", with_block(pi, blocks[pi] + '"'), 1))
    cases.append(("您", with_block(pi, blocks[pi] + "您"), 1))
    cases.append(("Taiwan residue 航厦", with_block(pi, blocks[pi] + "航厦"), 1))
    cases.append(("traditional-only 這", with_block(pi, blocks[pi] + "這"), 1))
    cases.append(("lone em dash", with_block(pi, blocks[pi] + "—"), 1))
    cases.append(("broken heading", with_block(0, blocks[0] + "x"), 1))
    cases.append(("merged blocks (parity)", "\n\n".join(blocks[:pi] + [blocks[pi] + "\n" + blocks[pi + 1]] + blocks[pi + 2:]) + "\n", 1))
    if code:
        ci = code[0]
        toks = C.code_tokens(src[ci]["text"])
        if toks:
            cases.append(("dropped machine token %s" % toks[0], with_block(ci, blocks[ci].replace(toks[0], "", 1)), 1))
        rows = blocks[ci].split("\n")
        if len(rows) > 3:
            cases.append(("dropped row", with_block(ci, "\n".join(rows[:1] + rows[2:])), 1))
        for k in range(1, len(rows) - 1):
            if "  " in rows[k]:
                shifted = rows[:k] + [rows[k].replace("  ", "   ", 1)] + rows[k + 1:]
                cases.append(("row shifted off its column", with_block(ci, "\n".join(shifted)), 1))
                break
    # remove every occurrence of one H form that the text carries
    done = False
    for i in prose:
        for g in gates.get(unit, {}).get(str(src[i]["seq"]), []):
            if g["tier"] != "H" or done:
                continue
            present = [f for f in g["forms"] if f in blocks[i]]
            if present:
                b = blocks[i]
                for f in g["forms"]:
                    b = b.replace(f, "")
                cases.append(("removed H form %s (%s)" % (present[0], g["id"]), with_block(i, b), 1))
                done = True
    bad = 0
    for name, t, want in cases:
        got = run(unit, t, key)
        ok = got == want
        bad += 0 if ok else 1
        print("%s   %-8s %-36s expected %s got %s" % ("ok " if ok else "BAD", unit, name, "FAIL" if want else "PASS", "FAIL" if got else "PASS"))
    print("battery: %s" % ("ALL CASES BEHAVE" if bad == 0 else "%d CASES MISBEHAVE" % bad))
    return 0 if bad == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
