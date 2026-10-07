#!/usr/bin/env python3
"""gate_zhs.py: the per-unit and whole-book gate of the zh-Hans edition.

  python3 _tools_zhs/gate_zhs.py ch_04 translation/current/ch_04.md      # one unit
  python3 _tools_zhs/gate_zhs.py --book translation/current                # every unit

The zh-Hant gate's structure checks (parity, headings, rows, tokens, floor), with the mainland key: the registry's
zh-Hans forms, “ ” quotes, no Traditional-only characters, no Taiwan residue the locale layer names as forbidden,
您 nowhere, the rows set in the zh-Hant columns (rows_zhs.py), the refrain 没有什么该来 as often as the source says "nothing is due", the cross-unit echoes.
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WS = os.path.dirname(HERE)
ZHT = os.path.join(os.path.dirname(WS), "five_hours_apart_zht")
sys.path.insert(0, os.path.join(ZHT, "_tools_zht"))
import zht_common as C  # noqa: E402

FLOOR, CEILING = 0.8, 3.6
# characters that exist only in the traditional script (a residue of an unconverted span)
TRADITIONAL_ONLY = set("這麼們國時說為會對還來發東車門問間開關後經讓給與書長見樣認識記錄沒點難過馬風電頭實現應該線組織"
                       "總結進統繼續動態術語氣權體驗務業產資質軟單價報標題類義論議設計劃層級據庫號灣幾個號辦廳廠")
ECHOES = [
("ch_16", "ch_04", "不糟"),     ("ch_16", "ch_04", "从来没有人替我举过牌子"), ("ch_16", "ch_04", "这是手机"), ("ch_16", "ch_04", "这是牌子"),
    ("ch_16", "ch_04", "是我"), ("ch_16", "ch_06", "是十一点。而十一点很忙"), ("ch_16", "ch_06", "对它有区别"),
    ("ch_16", "ch_12", "这星期没有"), ("ch_16", "ch_12", "你问过为什么是降落"),
    ("ch_16", "ch_09", "一张音符清单对一首歌来说是真的"), ("ch_17", "ch_01", "假设这是一个星期二"),
    ("front", "ch_18", "预期   重型机  海上   未闭"),
]


sys.path.insert(0, HERE)
from convert_zhs import convert, registry_map, locale_layer  # noqa: E402
import rows_zhs as R  # noqa: E402

_TW = {}


def tw_blocks(unit):
    """The zh-Hant blocks this unit derives from (the hash-verified copy in _zht_ref/)."""
    if unit not in _TW:
        p = os.path.join(WS, "_zht_ref", "translation_current", unit + ".md")
        _TW[unit] = C.blocks(C.read(p)) if os.path.exists(p) else []
    return _TW[unit]


def _variants(form):
    """A form as the converter prints it in prose (no space between a 汉字 and a Latin letter or digit) and as given."""
    nospace = re.sub(r"([㐀-鿿，。：、])[ ]+(?=[A-Za-z0-9])", r"\1", form)
    nospace = re.sub(r"(?<=[A-Za-z0-9])[ ]+([㐀-鿿，。：、])", r"\1", nospace)
    return {f for f in (form, nospace) if f}


def load_key():
    """The gates of the mainland edition. For every site: the registry's zh-Hans cell, plus the zh-Hant cell and every
    @accept alternate AS THE CONVERTER PRINTS THEM, so the key and the text are derived by the same rules and a
    hand-written zh-Hans cell can only add a locale form, never contradict the derivation."""
    rows = C.parse_registry(os.path.join(ZHT, "_key", "registry_merged.tsv"),
                            amendments=os.path.join(ZHT, "_key", "registry_amendments_zht.tsv"))
    segs = C.load_segments(os.path.join(WS, "_key", "segments.jsonl"))
    rmap, rules = registry_map(), locale_layer()

    def conv(s):
        return convert(s, rmap, rules, []).strip()

    gates, headings = {}, {}
    for r in rows:
        hans, hant = r["zh-Hans"], r["zh-Hant"]
        if r["id"].startswith("heading."):
            want = set()
            if hans and hans != "=":
                want.add(hans)
            if hant and hant != "=":
                want.add(conv(hant))
            headings[r["id"][len("heading."):]] = want
            continue
        if not r["re"] or r["tier"] not in ("H", "M"):
            continue
        accepts = (r.get("spec") or {}).get("accepts", [])
        for u in C.UNITS:
            for s in segs.get(u, []):
                if r["spec"]["types"] and s["type"] not in r["spec"]["types"]:
                    continue
                m = r["re"].search(s["text"])
                if not m or s["id"] in r["spec"]["excepts"]:
                    continue
                forms = set()
                if hans == "=" or (not hans and hant == "="):
                    forms.add(m.group(0))
                if hans and hans != "=":
                    forms |= _variants(hans)
                if hant and hant != "=":
                    forms |= _variants(conv(hant))
                for alt in accepts:
                    forms |= _variants(conv(alt))
                if forms:
                    gates.setdefault(u, {}).setdefault(str(s["seq"]), []).append(
                        {"id": r["id"], "tier": r["tier"], "forms": sorted(forms), "en": r["EN"].split(";;")[0].strip()})
    return segs, gates, headings


def forbidden_residue():
    out = []
    p = os.path.join(WS, "_key", "locale_layer_zhs.txt")
    if not os.path.exists(p):
        return out
    for ln in C.read(p).split("\n"):
        if ln.startswith("forbid:"):
            cells = ln[len("forbid:"):].split("\t")
            out.append((re.compile(cells[0].strip()), cells[1].strip() if len(cells) > 1 else ""))
    return out


def gate(unit, text, segs, gates, headings, residue, allowed, quiet=False):
    fails, warns = [], []
    tgt, src = C.blocks(text), segs[unit]
    if len(tgt) != len(src):
        fails.append("PARITY  %s: source %d blocks, draft %d" % (unit, len(src), len(tgt)))
    for ch in sorted(set(text) & TRADITIONAL_ONLY):
        fails.append("SCRIPT  traditional-only character %s present" % ch)
    if "「" in text or "」" in text or "『" in text or "』" in text:
        fails.append("QUOTES  corner quotes present; the mainland edition uses “ ” and ‘ ’")
    if text.count("“") != text.count("”"):
        fails.append("QUOTES  unbalanced “ ” (%d vs %d)" % (text.count("“"), text.count("”")))
    for i in range(min(len(tgt), len(src))):
        s, t = src[i], tgt[i]
        sid, st = s["id"], s["type"]
        for g in gates.get(unit, {}).get(str(s["seq"]), []):
            if not any(f in t for f in g["forms"]):
                (fails if g["tier"] == "H" else warns).append("TERM    %s: %s expects one of %s for /%s/" % (sid, g["id"], " | ".join(g["forms"]), g["en"]))
        if st in ("h1", "h2"):
            want = headings.get(unit) or set()
            if want and t.strip() not in want:
                fails.append("HEADING %s: expected %r got %r" % (sid, " | ".join(sorted(want)), t.strip()))
            continue
        if st == "code":
            if C.seg_type(t) != "code":
                fails.append("CODE    %s: not a fenced block" % sid)
                continue
            srows = [r for r in s["text"].split("\n")[1:-1] if r and not r[0].isspace()]
            trows = [r for r in t.split("\n")[1:-1] if r and not r[0].isspace()]
            if len(srows) != len(trows):
                fails.append("CODE    %s: %d rows in source, %d in draft" % (sid, len(srows), len(trows)))
            missing = [tok for tok in C.code_tokens(s["text"]) if tok not in t]
            if missing:
                fails.append("TOKENS  %s: missing %s" % (sid, ", ".join(sorted(set(missing)))))
            tw = tw_blocks(unit)
            if i < len(tw):
                for iss in R.check(tw[i], t):
                    fails.append("ROWALIGN %s: %s" % (sid, iss))
            continue
        if st == "quote" and not t.startswith(">"):
            fails.append("QUOTE   %s" % sid)
        if st == "italic" and not (t.startswith("*") and t.rstrip().endswith("*")):
            fails.append("ITALIC  %s" % sid)
        if st == "dialogue" and not t.lstrip("*").startswith("“"):
            fails.append("DIALOG  %s: must open with “" % sid)
        if '"' in t:
            fails.append("ASCIIQ  %s" % sid)
        if re.search(r"(?<!—)—(?!—)", t):
            fails.append("DASH    %s: a lone em dash" % sid)
        if "您" in t:
            fails.append("FORBID  %s: 您" % sid)
        for rx, why in residue:
            if rx.search(t):
                fails.append("RESIDUE %s: /%s/ %s" % (sid, rx.pattern, why))
        for run in C.LATIN_RUN_RE.findall(t):
            if run.lower() not in {x.lower() for x in allowed}:
                warns.append("LATIN   %s: %r" % (sid, run))
        words, cjk = len(s["text"].split()), C.cjk_count(t)
        if words >= 8 and cjk < FLOOR * words:
            fails.append("FLOOR   %s: %d chars for %d words" % (sid, cjk, words))
        elif words >= 8 and cjk > CEILING * words:
            warns.append("CEIL    %s" % sid)
    if not quiet or fails:
        for w in warns:
            print("WARN  " + w)
        for f in fails:
            print("FAIL  " + f)
    print("%s  %s: %d FAIL, %d WARN" % ("PASS" if not fails else "FAIL", unit, len(fails), len(warns)))
    return 0 if not fails else 1


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    segs, gates, headings = load_key()
    residue = forbidden_residue()
    allowed = C.load_allowed_latin(os.path.join(ZHT, "_key", "allowed_latin.txt"))
    if "--book" in sys.argv:
        d = args[0]
        texts, fails = {}, 0
        for u in C.UNITS:
            p = os.path.join(d, u + ".md")
            if not os.path.exists(p):
                print("FAIL  MISSING %s" % u)
                fails += 1
                continue
            texts[u] = C.read(p)
            fails += gate(u, texts[u], segs, gates, headings, residue, allowed, quiet=True)
        book = "\n\n".join(texts[u] for u in C.UNITS if u in texts)
        src = "\n\n".join(s["text"] for u in C.UNITS for s in segs[u])
        n_src = len(re.findall(r"nothing(?:'s| is) due", src, flags=re.I))
        if book.count("没有什么该来") < n_src:
            print("FAIL  REFRAIN 没有什么该来 %d < %d" % (book.count("没有什么该来"), n_src))
            fails += 1
        for quoting, quoted, line in ECHOES:
            if quoting in texts and quoted in texts and (line not in texts[quoting] or line not in texts[quoted]):
                print("FAIL  ECHO %r in %s and %s" % (line, quoting, quoted))
                fails += 1
        print("BOOK  %d units, %d FAIL" % (len(texts), fails))
        return 0 if fails == 0 else 1
    if len(args) != 2:
        print(__doc__)
        return 2
    return gate(args[0], C.read(args[1]), segs, gates, headings, residue, allowed)


if __name__ == "__main__":
    sys.exit(main())
