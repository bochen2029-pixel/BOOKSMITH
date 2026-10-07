#!/usr/bin/env python3
"""gate_es.py: the per-unit and whole-book gate of the es-419 edition (charter §5–§13; method v3 §10).

  python3 _tools_es/gate_es.py ch_04 translation/current/ch_04.md [--quiet]   # one unit
  python3 _tools_es/gate_es.py --book translation/current                      # every unit + the book checks

Per unit: block parity with the frozen source; headings byte-exact; block types (a speech paragraph opens with the
raya, italics stay italic, the text message stays a quote); the rows (line structure, every machine token, the §10
glossary, the English columns); the registry's locked forms at every site; the dash rule (the raya only in speech
paragraphs, never spaced like an English dash, never closing a paragraph; no en dash in prose); quotes (no ASCII,
no «», “ ” balanced; ¿? and ¡! paired); NFC; Spain-only forms, calques, English left behind; a word floor against
the English. Book: the refrain as often as the English says "nothing is due", the cross-unit echoes, the opening row
identical to the closing row.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import es_common as C  # noqa: E402
import rows_es as R  # noqa: E402

FLOOR, CEILING = 0.75, 1.9
REFRAIN = "nada está por llegar"
# (quoting unit, quoted unit, the line both must carry verbatim): the rows quote the prose
ECHOES = [
    ("ch_16", "ch_04", "Soy yo."), ("ch_16", "ch_04", "Es un celular."), ("ch_16", "ch_04", "Es un letrero."),
    ("ch_16", "ch_04", "No lo fue."), ("ch_16", "ch_06", "Son las once. Y a las once hay mucho movimiento."),
    ("ch_16", "ch_06", "A eso le importaría."), ("ch_16", "ch_12", "Nada esta semana."), ("ch_16", "ch_12", "No sé."),
    ("ch_16", "ch_12", "Me preguntaste por qué el aterrizaje."),
    ("ch_16", "ch_09", "una lista de notas es verdad sobre una canción"),
    ("ch_17", "ch_01", "Digamos que es un martes"),
]


def gate(unit, text, segs, reg, quiet=False):
    fails, warns = [], []
    tgt, src = C.blocks(text), segs[unit]
    if len(tgt) != len(src):
        fails.append("PARITY  %s: source %d blocks, draft %d" % (unit, len(src), len(tgt)))
    if text != C.nfc(text):
        fails.append("NFC     %s: not in NFC (a decomposed accent)" % unit)
    heads = {r["unit"]: r["es"] for r in reg if "unit" in r}
    for i in range(min(len(tgt), len(src))):
        s, t = src[i], tgt[i]
        sid, st, tt = s["id"], s["type"], C.es_type(t)
        if st in ("h1", "h2"):
            if i == 0 and unit in heads and t.strip() != heads[unit]:
                fails.append("HEADING %s: expected %r got %r" % (sid, heads[unit], t.strip()))
            continue
        for r in reg:
            if "spec" not in r:
                continue
            sp = r["spec"]
            if sp["types"] and st not in sp["types"]:
                continue
            if sid in sp["excepts"] or not r["re"].search(s["text"]):
                continue
            if not C.has_form(t, r["forms"]):
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
        if t.count("¿") != t.count("?") or t.count("¡") != t.count("!"):
            fails.append("INVERT  %s: ¿? %d/%d  ¡! %d/%d" % (sid, t.count("¿"), t.count("?"), t.count("¡"), t.count("!")))
        if "—" in t and tt != "dialogue":
            fails.append("DASH    %s: a raya outside a speech paragraph" % sid)
        if re.search(r"\s—\s", t):
            fails.append("DASH    %s: a spaced dash (the English em dash), not a raya" % sid)
        if t.rstrip().endswith("—"):
            fails.append("DASH    %s: a raya closing the paragraph" % sid)
        if "–" in t:
            fails.append("DASH    %s: an en dash in prose" % sid)
        for rx, why in C.FORBID:
            m = rx.search(t)
            if m:
                fails.append("FORBID  %s: %r (%s)" % (sid, m.group(0), why))
        for rx, why in C.WARN:
            m = rx.search(t)
            if m:
                warns.append("WARN    %s: %r (%s)" % (sid, m.group(0)[:40], why))
        en_w, es_w = C.words(s["text"]), C.words(t)
        if en_w >= 8 and es_w < FLOOR * en_w:
            fails.append("FLOOR   %s: %d words for %d English" % (sid, es_w, en_w))
        elif en_w >= 8 and es_w > CEILING * en_w:
            warns.append("CEIL    %s: %d words for %d English" % (sid, es_w, en_w))
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
        if quoting in texts and quoted in texts and (line not in texts[quoting] or line not in texts[quoted]):
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
