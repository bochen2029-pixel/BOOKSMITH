#!/usr/bin/env python3
"""gate_vi.py: the per-unit and whole-book gate of the vi-VN edition (charter §5–§13; method v3 §10).

  python3 _tools_vi/gate_vi.py ch_04 translation/current/ch_04.md [--quiet]   # one unit
  python3 _tools_vi/gate_vi.py --book translation/current                      # every unit + the book checks

Per unit: block parity with the frozen source; headings byte-exact; block types (a speech paragraph opens with the
dialogue dash "– ", italics stay italic, the text message stays a quote); the rows (line structure, every machine
token, the §10 glossary, the English columns); the registry's locked forms at every site; the dash rule (the en dash
only in speech paragraphs and always spaced, never the em dash, never a hyphen as a dash); quotes (no ASCII, no «»,
“ ” balanced); NFC; one tone-mark style; calques, English left behind; a syllable floor and ceiling against the
English words. Book: the refrain as often as the English says "nothing is due", the cross-unit echoes, the opening row
identical to the closing row.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import vi_common as C  # noqa: E402
import rows_vi as R  # noqa: E402

FLOOR, CEILING = 0.85, 2.8
REFRAIN = "chẳng có gì sắp đến"
# (quoting unit, quoted unit, the words both must carry verbatim): the rows quote the prose. No closing period in the
# line, because the prose may close the speech with an attribution ("– Tôi đây, – cô nói."); a row quote that wraps is
# rejoined.
ECHOES = [
    ("ch_16", "ch_04", "Tôi đây"), ("ch_16", "ch_04", "Chưa từng có ai cầm biển đón tôi"),
    ("ch_16", "ch_04", "Đó là cái điện thoại"), ("ch_16", "ch_04", "Đó là tấm biển"), ("ch_16", "ch_04", "Không hề"),
    ("ch_16", "ch_06", "Là mười một giờ. Mà mười một giờ thì đông"),
    ("ch_16", "ch_06", "Với nó thì có quan trọng"), ("ch_16", "ch_12", "Tuần này thì không có gì"),
    ("ch_16", "ch_12", "Tôi không biết"), ("ch_16", "ch_12", "Cô đã hỏi tại sao lại là hạ cánh"),
    ("ch_16", "ch_09", "một dãy nốt nhạc là thật về một bài hát"),
    ("ch_17", "ch_01", "Cứ cho đó là một ngày thứ Ba"),
    # the prose echoes the book returns to (charter §11): I/XIV the freeways, I/XVIII the odd week, XII/XVIII the room
    ("ch_14", "ch_01", "Các xa lộ trắng về phía anh và đỏ ở chiều ngược lại"),
    ("ch_18", "ch_01", "trong tuần cuối cùng của tháng Mười, cái tuần lệch"),
    ("ch_18", "ch_12", "căn phòng nhỏ nhất mà công ty thuê"),
]


def row_quotes(text):
    """Every “…” inside the fenced rows, a quote that wraps onto continuation lines rejoined with one space."""
    out = []
    for blk in C.blocks(text):
        if not blk.startswith("```"):
            continue
        lines = blk.split("\n")[1:-1]
        for i, line in enumerate(lines):
            for m in re.finditer("“", line):
                rest = line[m.end():]
                if "”" in rest:
                    out.append(rest[:rest.index("”")])
                    continue
                frag = re.split(r"\s{2,}", rest)[0]
                for cont in lines[i + 1:]:
                    cont = cont.strip()
                    if "”" in cont:
                        frag += " " + cont[:cont.index("”")]
                        break
                    frag += " " + re.split(r"\s{2,}", cont)[0]
                out.append(frag)
    return out


def carries(text, line):
    return line in text or any(line in q for q in row_quotes(text))


def gate(unit, text, segs, reg, quiet=False):
    fails, warns = [], []
    tgt, src = C.blocks(text), segs[unit]
    if len(tgt) != len(src):
        fails.append("PARITY  %s: source %d blocks, draft %d" % (unit, len(src), len(tgt)))
    if text != C.nfc(text):
        fails.append("NFC     %s: not in NFC (a decomposed accent)" % unit)
    heads = {r["unit"]: r["vi"] for r in reg if "unit" in r}
    for i in range(min(len(tgt), len(src))):
        s, t = src[i], tgt[i]
        sid, st, tt = s["id"], s["type"], C.vi_type(t)
        if st in ("h1", "h2"):
            if i == 0 and unit in heads and t.strip() != heads[unit]:
                fails.append("HEADING %s: expected %r got %r" % (sid, heads[unit], t.strip()))
            continue
        # a row quote that wraps is rejoined, so a locked line is found whole
        t_terms = t if st != "code" else t + "\n" + "\n".join(row_quotes(t))
        for r in reg:
            if "spec" not in r:
                continue
            sp = r["spec"]
            if sp["types"] and st not in sp["types"]:
                continue
            if sid in sp["excepts"] or not r["re"].search(s["text"]):
                continue
            if not C.has_form(t_terms, r["forms"]):
                (fails if r["tier"] == "H" else warns).append(
                    "TERM    %s: %s expects %s for /%s/" % (sid, r["id"], " | ".join(r["forms"]), sp["pattern"]))
        if st == "code":
            if tt != "code":
                fails.append("CODE    %s: not a fenced block" % sid)
                continue
            if len(s["text"].split("\n")) != len(t.split("\n")):
                fails.append("CODE    %s: %d lines in the English, %d here" % (sid, len(s["text"].split("\n")), len(t.split("\n"))))
            missing = sorted({tok for tok in C.code_tokens(s["text"]) if tok not in t})
            if missing:
                fails.append("TOKENS  %s: missing %s" % (sid, ", ".join(missing)))
            for en_rx, es_rx in C.ROWS:
                if en_rx.search(s["text"]) and not es_rx.search(t):
                    fails.append("ROWWORD %s: /%s/ needs /%s/" % (sid, en_rx.pattern, es_rx.pattern))
            for iss in R.check(s["text"], t):
                fails.append("ROWALIGN %s: %s" % (sid, iss))
            continue
        want = {"dialogue": "dialogue", "italic": "italic", "quote": "quote", "para": "para"}.get(st)
        if want and tt != want:
            fails.append("TYPE    %s: the English is %s, this block reads as %s" % (sid, st, tt))
        if '"' in t:
            fails.append("ASCIIQ  %s: an ASCII quote" % sid)
        if t.count("“") != t.count("”"):
            fails.append("QUOTES  %s: “ ” unbalanced (%d / %d)" % (sid, t.count("“"), t.count("”")))
        if C.DASH in t and tt != "dialogue":
            fails.append("DASH    %s: the dialogue dash outside a speech paragraph" % sid)
        if tt == "dialogue" and re.search(r"[^ ]–|–[^ ]", t):
            fails.append("DASH    %s: a dialogue dash without its spaces" % sid)
        if t.rstrip().endswith(C.DASH):
            fails.append("DASH    %s: a dash closing the paragraph" % sid)
        for rx, why in C.FORBID:
            m = rx.search(t)
            if m:
                fails.append("FORBID  %s: %r (%s)" % (sid, m.group(0), why))
        for rx, why in C.WARN:
            m = rx.search(t)
            if m:
                warns.append("WARN    %s: %r (%s)" % (sid, m.group(0)[:40], why))
        en_w, vi_w = C.words(s["text"]), C.words(t)
        if en_w >= 8 and vi_w < FLOOR * en_w:
            fails.append("FLOOR   %s: %d syllables for %d English words" % (sid, vi_w, en_w))
        elif en_w >= 8 and vi_w > CEILING * en_w:
            warns.append("CEIL    %s: %d syllables for %d English words" % (sid, vi_w, en_w))
    if not quiet or fails:
        for w in warns:
            print("WARN  " + w)
        for f in fails:
            print("FAIL  " + f)
    print("%s  %s: %d FAIL, %d WARN" % ("PASS" if not fails else "FAIL", unit, len(fails), len(warns)))
    return 0 if not fails else 1


def book(d, segs, reg):
    texts, fails = {}, 0
    for u in C.UNITS:
        p = os.path.join(d, u + ".md")
        if not os.path.exists(p):
            print("FAIL  MISSING %s" % u)
            fails += 1
            continue
        texts[u] = C.read(p)
        fails += gate(u, texts[u], segs, reg, quiet=True)
    allt = "\n\n".join(texts[u] for u in C.UNITS if u in texts)
    src = "\n\n".join(s["text"] for u in C.UNITS for s in segs[u])
    n_src = len(re.findall(r"nothing(?:'s| is) due", src, flags=re.I))
    n = len(re.findall(re.escape(REFRAIN), allt, flags=re.I))
    if n < n_src:
        print("FAIL  REFRAIN %r %d < %d" % (REFRAIN, n, n_src))
        fails += 1
    for quoting, quoted, line in ECHOES:
        if quoting in texts and quoted in texts and (not carries(texts[quoting], line) or not carries(texts[quoted], line)):
            print("FAIL  ECHO %r must be in %s and %s" % (line, quoting, quoted))
            fails += 1
    if "front" in texts and "ch_18" in texts:
        a = [b for b in C.blocks(texts["front"]) if b.startswith("```")]
        b = [b for b in C.blocks(texts["ch_18"]) if b.startswith("```")]
        if not a or not b or a[0] != b[-1]:
            print("FAIL  ECHO the opening row must be the closing row, byte for byte")
            fails += 1
    print("BOOK  %d units, %d FAIL" % (len(texts), fails))
    return 0 if fails == 0 else 1


def main():
    segs, reg = C.load_segments(), C.load_registry()
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if "--book" in sys.argv:
        return book(args[0], segs, reg)
    if len(args) != 2:
        print(__doc__)
        return 2
    return gate(args[0], C.read(args[1]), segs, reg, quiet="--quiet" in sys.argv)


if __name__ == "__main__":
    sys.exit(main())
