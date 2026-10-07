#!/usr/bin/env python3
"""gate_unit.py: the per-unit gate of the zh-Hant-TW edition (BOOK_TRANSLATION_METHOD_v3 §10).

  python _tools_zht/gate_unit.py ch_04 translation/drafts/ch_04_v1.md [--quiet]

Checks, in order: segment parity (block for block with the frozen source); structure per block (headings byte-exact
against the heading table; code blocks fenced, same row count, every machine token kept; quotes keep '>'; italics
keep '*…*'; a dialogue segment opens with 「); registry conformance (H = FAIL, M = WARN, @accept honoured);
forbidden forms (您, particles, AI tells, simplified characters, ASCII quotes, single em dashes, three-dot
ellipses); stray source language (Latin runs outside the allowed tokens: WARN); the character floor and ceiling
(a dropped or padded sentence); quote balance. Exit 0 = PASS (warnings allowed), 1 = FAIL, 2 = usage.
"""
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import zht_common as C  # noqa: E402

FLOOR, CEILING = 0.8, 3.6   # CJK characters per English word, prose blocks of 8+ words


def heading_table(rows):
    return {r["id"][len("heading."):]: r["zh-Hant"] for r in rows if r["id"].startswith("heading.")}


def gate(unit, text, segs, gates, headings, forbidden, allowed, quiet=False):
    fails, warns = [], []
    tgt = C.blocks(text)
    src = segs[unit]
    if len(tgt) != len(src):
        fails.append("PARITY  %s: source %d blocks, draft %d (the n-th block must be the n-th segment)" % (unit, len(src), len(tgt)))
    # whole-text checks
    for ch in sorted(set(text) & C.SIMPLIFIED_ONLY):
        fails.append("SCRIPT  simplified-only character %s present" % ch)
    if text.count("「") != text.count("」"):
        fails.append("QUOTES  unbalanced 「」 (%d vs %d)" % (text.count("「"), text.count("」")))
    if text.count("『") != text.count("』"):
        fails.append("QUOTES  unbalanced 『』")
    n = min(len(tgt), len(src))

    def conform(s, t):
        for g in gates.get(unit, {}).get(str(s["seq"]), []):
            if not any(form in t for form in g["forms"]):
                msg = "TERM    %s: %s expects one of %s for /%s/" % (s["id"], g["id"], " | ".join(g["forms"]), g["en"])
                (fails if g["tier"] == "H" else warns).append(msg)

    for i in range(n):
        s, t = src[i], tgt[i]
        sid = s["id"]
        st = s["type"]
        tt = C.seg_type(t)
        conform(s, t)   # registry conformance applies to every block, log rows included
        if st in ("h1", "h2"):
            want = headings.get(unit if st == "h1" and unit.startswith("part") else unit)
            if unit == "front" and st == "h1":
                want = headings.get("front")
            if want and t.strip() != want:
                fails.append("HEADING %s: expected %r got %r" % (sid, want, t.strip()))
            continue
        if st == "code":
            if tt != "code" or not t.rstrip().endswith("```"):
                fails.append("CODE    %s: the draft block is not a fenced code block" % sid)
                continue
            # a row is a line that starts at column 0; an indented line is the wrap of a long quoted row
            srows = [r for r in s["text"].split("\n")[1:-1] if r and not r[0].isspace()]
            trows = [r for r in t.split("\n")[1:-1] if r and not r[0].isspace()]
            if len(srows) != len(trows):
                fails.append("CODE    %s: %d rows in source, %d in draft" % (sid, len(srows), len(trows)))
            missing = [tok for tok in C.code_tokens(s["text"]) if tok not in t]
            if missing:
                fails.append("TOKENS  %s: machine tokens missing from the draft row(s): %s" % (sid, ", ".join(sorted(set(missing)))))
            continue
        if st == "quote" and not t.startswith(">"):
            fails.append("QUOTE   %s: the source is a '>' block; the draft is not" % sid)
        if st == "italic" and not (t.startswith("*") and t.rstrip().endswith("*")):
            fails.append("ITALIC  %s: the source is an *italic* block; keep the asterisks" % sid)
        if st == "dialogue" and not t.lstrip("*").startswith("「"):
            fails.append("DIALOG  %s: the source opens with a quotation mark; the draft must open with 「" % sid)
        # prose-only checks
        if '"' in t:
            fails.append("ASCIIQ  %s: ASCII double quote in the draft; use 「」" % sid)
        if re.search(r"(?<!—)—(?!—)", t):
            fails.append("DASH    %s: a lone em dash; a Chinese dash is —— (two)" % sid)
        if "..." in t or re.search(r"(?<!…)…(?!…)", t.replace("……", "")):
            fails.append("ELLIP   %s: use …… (two) in prose" % sid)
        for f in forbidden:
            if f["scope"] == "prose" and f["re"].search(t):
                (fails if f["tier"] == "FAIL" else warns).append("FORBID  %s: /%s/ %s" % (sid, f["pattern"], f["reason"]))
        for run in C.LATIN_RUN_RE.findall(t):
            if run not in allowed and run.lower() not in {a.lower() for a in allowed}:
                warns.append("LATIN   %s: Latin run %r in the draft (allowed? add to _key/allowed_latin.txt)" % (sid, run))
        words = len(s["text"].split())
        cjk = C.cjk_count(t)
        if words >= 8:
            if cjk < FLOOR * words:
                fails.append("FLOOR   %s: %d CJK chars for %d English words (ratio %.2f < %.1f): a sentence is missing?" % (sid, cjk, words, cjk / words, FLOOR))
            elif cjk > CEILING * words:
                warns.append("CEIL    %s: %d CJK chars for %d English words (ratio %.2f > %.1f): explaining instead of translating?" % (sid, cjk, words, cjk / words, CEILING))
    if not quiet or fails:
        for w in warns:
            print("WARN  " + w)
        for f in fails:
            print("FAIL  " + f)
    print("%s  %s: %d FAIL, %d WARN" % ("PASS" if not fails else "FAIL", unit, len(fails), len(warns)))
    return 0 if not fails else 1


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if len(args) != 2:
        print(__doc__)
        return 2
    unit, path = args
    segs = C.load_segments()
    if unit not in segs:
        print("unknown unit %s" % unit)
        return 2
    gates = json.load(open(os.path.join(C.GEN, "key_gates.json"), encoding="utf-8"))
    rows = C.parse_registry(amendments=os.path.join(C.KEY, "registry_amendments_zht.tsv"))
    return gate(unit, C.read(path), segs, gates, heading_table(rows), C.load_forbidden(), C.load_allowed_latin(),
                quiet="--quiet" in sys.argv)


if __name__ == "__main__":
    sys.exit(main())
