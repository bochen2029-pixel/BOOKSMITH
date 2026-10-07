#!/usr/bin/env python3
"""test_gate.py: the must-fail battery of the zh-Hant-TW gate (BOOK_TRANSLATION_METHOD_v3 §6.1 step 3).

A gate that cannot fail protects nothing. For a sample unit this builds a synthetic clean draft (every required
form present, the structure right, enough characters) and asserts PASS; then one mutation at a time (a dropped
block, an untranslated unit, 您, a simplified character, an ASCII quote, a lone em dash, a missing locked term,
a wrong heading, a missing machine token, a particle) and asserts FAIL. Exit 0 when every case behaves.
"""
import contextlib
import io
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import zht_common as C  # noqa: E402
import gate_unit as G  # noqa: E402


def synth(unit, segs, gates, headings):
    out = []
    for s in segs[unit]:
        forms = "".join(f["forms"][0] for f in gates.get(unit, {}).get(str(s["seq"]), []))
        if s["type"] in ("h1", "h2"):
            out.append(headings[unit if s["type"] == "h2" or unit.startswith("part") or unit == "front" else unit])
        elif s["type"] == "code":
            rows = [r for r in s["text"].split("\n")[1:-1] if r and not r[0].isspace()]   # wrapped lines are not rows
            out.append("```\n" + "\n".join("譯 " + " ".join(C.code_tokens(r)) + " " + forms for r in rows) + "\n```")
        else:
            words = len(s["text"].split())
            body = forms + "字" * max(0, int(words * 1.5) - C.cjk_count(forms))
            if s["type"] == "dialogue":
                body = "「" + body + "」"
            elif s["type"] == "quote":
                body = "> " + body
            elif s["type"] == "italic":
                body = "*" + body + "*"
            out.append(body)
    return "\n\n".join(out) + "\n"


def run(unit, text, ctx):
    with contextlib.redirect_stdout(io.StringIO()):
        rc = G.gate(unit, text, *ctx, quiet=True)
    return rc


def main():
    segs = C.load_segments()
    gates = json.load(open(os.path.join(C.GEN, "key_gates.json"), encoding="utf-8"))
    rows = C.parse_registry(amendments=os.path.join(C.KEY, "registry_amendments_zht.tsv"))
    headings = G.heading_table(rows)
    ctx = (segs, gates, headings, C.load_forbidden(), C.load_allowed_latin())
    bad = 0
    for unit in ("ch_04", "ch_12", "ch_16"):
        clean = synth(unit, segs, gates, headings)
        cases = [("clean control", clean, 0)]
        b = C.blocks(clean)
        cases.append(("dropped block", "\n\n".join(b[:-1]) + "\n", 1))
        cases.append(("untranslated (the English source)", "\n\n".join(s["text"] for s in segs[unit]) + "\n", 1))
        has_prose = "字字" in clean
        if has_prose:   # prose mutations only mean something in a unit with prose blocks
            cases.append(("您 present", clean.replace("字字", "您字", 1), 1))
            cases.append(("simplified character", clean.replace("字字", "这字", 1), 1))
            cases.append(("ASCII quote", clean.replace("字字", '"字', 1), 1))
            cases.append(("lone em dash", clean.replace("字字", "—字", 1), 1))
            cases.append(("sentence-final 喔", clean.replace("字字", "字喔」", 1).replace("」」", "」", 1), 1))
        cases.append(("wrong heading", clean.replace(headings[unit], headings[unit] + "x", 1), 1))
        req = [f["forms"][0] for v in gates.get(unit, {}).values() for f in v if f["tier"] == "H"]
        if req:
            cases.append(("missing locked term", clean.replace(req[0], ""), 1))   # every occurrence
        codes = [s for s in segs[unit] if s["type"] == "code"]
        if codes:
            tok = C.code_tokens(codes[0]["text"])[0]
            cases.append(("missing machine token", clean.replace(tok, ""), 1))   # every occurrence
        for name, text, want in cases:
            rc = run(unit, text, ctx)
            ok = (rc == want)
            bad += 0 if ok else 1
            print("%s  %-8s %-36s expected %s got %s" % ("ok " if ok else "BAD", unit, name, "PASS" if want == 0 else "FAIL", "PASS" if rc == 0 else "FAIL"))
    print("battery: %s" % ("ALL CASES BEHAVE" if bad == 0 else "%d case(s) misbehave" % bad))
    return 0 if bad == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
