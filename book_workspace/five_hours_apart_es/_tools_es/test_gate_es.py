#!/usr/bin/env python3
"""test_gate_es.py: the must-fail battery of the es-419 gate (the gate is trusted only while this prints ALL CASES
BEHAVE).

  python3 _tools_es/test_gate_es.py [--unit ch_12] [--dir translation/current]

Takes one unit that PASSES (the clean control), then mutates it one defect at a time and asserts the gate FAILS
each: an ASCII quote, «», "...", a raya in narration, a spaced dash in speech, a speech paragraph without its raya,
an unpaired ¿, a decomposed accent, a Spain form, a calque, English left behind, a broken heading, merged blocks,
a dropped machine token, a dropped row line, a shifted row, a removed locked form. Then the book checks on a copy
of the whole edition: a broken locked line inside a wrapped row quote, a broken echo, a dropped refrain, a closing
row that no longer matches the opening row. Exit 1 if any case misbehaves.
"""
import io
import os
import shutil
import sys
import tempfile
import unicodedata
from contextlib import redirect_stdout

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import es_common as C  # noqa: E402
import gate_es as G  # noqa: E402


def run(unit, text, segs, reg):
    with redirect_stdout(io.StringIO()):
        return G.gate(unit, text, segs, reg, quiet=True)


# (name, unit, old, new): one defect the book gate must catch; the old text must occur in the clean unit
BOOK_DEFECTS = [
    ("wrapped row quote broken", "ch_16", "hay mucho movimiento", "hay movimiento"),
    ("echo broken in the prose", "ch_04", "—Es un celular.", "—Es un teléfono."),
    ("refrain dropped", "ch_08", "y nada está por llegar", "y nada más"),
    ("closing row off the opening", "ch_18", "sobre el agua  abierta", "sobre el agua  abierto"),
]


def book_cases(d, segs, reg):
    if not all(os.path.exists(os.path.join(d, u + ".md")) for u in C.UNITS):
        print("skip  book     (the edition is not complete)")
        return 0
    bad = 0
    tmp = tempfile.mkdtemp(prefix="gate_es_book_")
    try:
        for name, unit, old, new in [("clean book", None, None, None)] + BOOK_DEFECTS:
            for u in C.UNITS:
                shutil.copyfile(os.path.join(d, u + ".md"), os.path.join(tmp, u + ".md"))
            if unit:
                path = os.path.join(tmp, unit + ".md")
                t = C.read(path)
                if old not in t:
                    print("BAD   book     %-40s %r not in %s" % (name, old, unit))
                    bad += 1
                    continue
                C.write(path, t.replace(old, new, 1))
            with redirect_stdout(io.StringIO()):
                got = G.book(tmp, segs, reg)
            want = 1 if unit else 0
            ok = got == want
            bad += 0 if ok else 1
            print("%s   %-8s %-40s expected %s got %s" % ("ok " if ok else "BAD", "book", name, "FAIL" if want else "PASS", "FAIL" if got else "PASS"))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    return bad


def main():
    a = sys.argv[1:]
    unit = a[a.index("--unit") + 1] if "--unit" in a else "ch_12"
    d = a[a.index("--dir") + 1] if "--dir" in a else os.path.join(C.WS, "translation", "current")
    path = os.path.join(d, unit + ".md")
    if not os.path.exists(path):
        print("no file %s" % path)
        return 2
    segs, reg = C.load_segments(), C.load_registry()
    text = C.read(path)
    bl = C.blocks(text)
    src = segs[unit]
    para = [i for i, s in enumerate(src) if s["type"] == "para" and C.words(s["text"]) >= 8]
    dial = [i for i, s in enumerate(src) if s["type"] == "dialogue"]
    code = [i for i, s in enumerate(src) if s["type"] == "code"]
    if not para or not dial:
        print("unit %s needs a narration paragraph and a speech paragraph" % unit)
        return 2
    pi, di = para[0], dial[0]

    def with_block(i, new):
        b = list(bl)
        b[i] = new
        return "\n\n".join(b) + "\n"

    cases = [("clean text", text, 0)]
    cases.append(("ASCII quote", with_block(pi, bl[pi] + ' "'), 1))
    cases.append(("comillas «»", with_block(pi, bl[pi] + " «sí»"), 1))
    cases.append(("three dots", with_block(pi, bl[pi] + "..."), 1))
    cases.append(("raya in narration", with_block(pi, bl[pi] + " —dice."), 1))
    cases.append(("spaced dash in speech", with_block(di, bl[di] + " — y nada"), 1))
    cases.append(("speech without its raya", with_block(di, bl[di].lstrip("—")), 1))
    cases.append(("unpaired ¿", with_block(pi, bl[pi] + " ¿Y"), 1))
    cases.append(("decomposed accent", with_block(pi, bl[pi] + " " + unicodedata.normalize("NFD", "está")), 1))
    cases.append(("Spain form coche", with_block(pi, bl[pi] + " El coche."), 1))
    cases.append(("calque en base a", with_block(pi, bl[pi] + " en base a eso."), 1))
    cases.append(("English left behind", with_block(pi, bl[pi] + " and the rest."), 1))
    cases.append(("broken heading", with_block(0, bl[0] + "x"), 1))
    cases.append(("merged blocks (parity)", "\n\n".join(bl[:pi] + [bl[pi] + "\n" + bl[pi + 1]] + bl[pi + 2:]) + "\n", 1))
    if code:
        ci = code[0]
        toks = C.code_tokens(src[ci]["text"])
        if toks:
            cases.append(("dropped machine token %s" % toks[0], with_block(ci, bl[ci].replace(toks[0], "", 1)), 1))
        rows = bl[ci].split("\n")
        if len(rows) > 3:
            cases.append(("dropped row line", with_block(ci, "\n".join(rows[:1] + rows[2:])), 1))
        for k in range(1, len(rows) - 1):
            if "  " in rows[k]:
                cases.append(("row shifted off its column",
                              with_block(ci, "\n".join(rows[:k] + [rows[k].replace("  ", "   ", 1)] + rows[k + 1:])), 1))
                break
    done = False
    for i, s in enumerate(src):
        if done or s["type"] not in ("para", "dialogue"):
            continue
        for r in reg:
            if "spec" not in r or r["tier"] != "H" or not r["re"].search(s["text"]) or s["id"] in r["spec"]["excepts"]:
                continue
            present = [f for f in r["forms"] if f.lower() in bl[i].lower()]
            if present:
                b = bl[i]
                for f in r["forms"]:
                    idx = b.lower().find(f.lower())
                    while idx >= 0:
                        b = b[:idx] + b[idx + len(f):]
                        idx = b.lower().find(f.lower())
                cases.append(("removed locked form %s (%s)" % (present[0], r["id"]), with_block(i, b), 1))
                done = True
                break
    bad = 0
    for name, t, want in cases:
        got = run(unit, t, segs, reg)
        ok = got == want
        bad += 0 if ok else 1
        print("%s   %-8s %-40s expected %s got %s" % ("ok " if ok else "BAD", unit, name, "FAIL" if want else "PASS", "FAIL" if got else "PASS"))
    bad += book_cases(d, segs, reg)
    print("battery: %s" % ("ALL CASES BEHAVE" if bad == 0 else "%d CASES MISBEHAVE" % bad))
    return 0 if bad == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
