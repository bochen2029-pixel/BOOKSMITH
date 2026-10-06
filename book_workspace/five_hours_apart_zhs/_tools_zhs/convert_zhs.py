#!/usr/bin/env python3
"""convert_zhs.py: DERIVE the zh-Hans edition from the ratified zh-Hant-TW text (BOOK_TRANSLATION_METHOD_v3 §6.2).

Never retranslate. For each unit: read the zh-Hant text from _zht_ref/translation_current/<unit>.md (a hash-verified
copy of the Taiwan edition's translation/current), then
  1. OpenCC tw2sp (Taiwan script and phrases -> mainland script and phrases),
  2. the registry pass: every registry row whose zh-Hans form differs from its zh-Hant form, keyed on the tw2s image
     of the zh-Hant form, longest first (names, places, the hard term splits),
  3. the locale layer _key/locale_layer_zhs.txt in file order (tw<TAB>hans; '#' comments; a key may be written in
     either script, it is normalised through tw2s; a line 're:<regex><TAB>repl' is a regex rule),
  4. punctuation: 「」 -> “ ”, 『』 -> ‘ ’ (prose and rows alike),
and write translation/drafts/<unit>_v<N>.md; with --publish also translation/current/<unit>.md.
Prints every replacement it made so a reviewer can read them in their sentence.

  python3 _tools_zhs/convert_zhs.py ch_01 ch_02 --publish --version 1
  python3 _tools_zhs/convert_zhs.py --all --publish --version 1
"""
import argparse
import hashlib
import os
import re
import sys

import opencc

HERE = os.path.dirname(os.path.abspath(__file__))
WS = os.path.dirname(HERE)
ZHT = os.path.join(os.path.dirname(WS), "five_hours_apart_zht")
sys.path.insert(0, os.path.join(ZHT, "_tools_zht"))
import zht_common as C  # noqa: E402

TW2SP = opencc.OpenCC("tw2sp")
TW2S = opencc.OpenCC("tw2s")


def registry_map():
    rows = C.parse_registry(os.path.join(ZHT, "_key", "registry_merged.tsv"),
                            amendments=os.path.join(ZHT, "_key", "registry_amendments_zht.tsv"))
    m = {}
    for r in rows:
        hant, hans = r["zh-Hant"], r["zh-Hans"]
        if not hant or not hans or hant == "=" or hans == "=" or hant == hans:
            continue
        key = TW2S.convert(hant)
        if key != hans:
            m[key] = hans
    return m


def locale_layer():
    rules = []
    p = os.path.join(WS, "_key", "locale_layer_zhs.txt")
    if not os.path.exists(p):
        return rules
    for ln in C.read(p).split("\n"):
        if not ln.strip() or ln.startswith("#"):
            continue
        cells = ln.split("\t")
        if len(cells) < 2:
            continue
        k, v = cells[0].strip(), cells[1].strip()
        if k.startswith("re:"):
            rules.append(("re", re.compile(k[3:]), v))
        else:
            rules.append(("str", TW2S.convert(k), v))
    return rules


def convert(text, rmap, rules, log):
    out = TW2SP.convert(text)
    for key in sorted(rmap, key=len, reverse=True):
        if key in out:
            log.append("registry  %s -> %s  (x%d)" % (key, rmap[key], out.count(key)))
            out = out.replace(key, rmap[key])
    for kind, k, v in rules:
        if kind == "str":
            if k in out:
                log.append("layer     %s -> %s  (x%d)" % (k, v, out.count(k)))
                out = out.replace(k, v)
        else:
            out, n = k.subn(v, out)
            if n:
                log.append("layer re  /%s/ -> %s  (x%d)" % (k.pattern, v, n))
    for a, b in (("「", "“"), ("」", "”"), ("『", "‘"), ("』", "’"), ("‧", "·"), ("・", "·"), ("．", "·")):
        out = out.replace(a, b)
    # mainland print sets no space between a 漢字 and a Latin letter or digit (prose only; the rows keep their columns)
    parts = re.split(r"(```.*?```)", out, flags=re.S)
    for i in range(0, len(parts), 2):
        parts[i] = re.sub(r"([㐀-鿿，。：、])[ ]+(?=[A-Za-z0-9])", r"\1", parts[i])
        parts[i] = re.sub(r"(?<=[A-Za-z0-9])[ ]+([㐀-鿿，。：、])", r"\1", parts[i])
        parts[i] = re.sub(r"(?<=[㐀-鿿，。：、！？；“”])[ ]+(?=[㐀-鿿“”])", "", parts[i])
    return "".join(parts)


def next_draft(drafts, unit):
    n = 1
    for name in os.listdir(drafts) if os.path.isdir(drafts) else []:
        mm = re.fullmatch(re.escape(unit) + r"_v(\d+)\.md", name)
        if mm:
            n = max(n, int(mm.group(1)) + 1)
    return n


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("units", nargs="*")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--publish", action="store_true")
    ap.add_argument("--version", type=int)
    a = ap.parse_args()
    units = list(C.UNITS) if a.all else a.units
    if not units:
        ap.error("name units or pass --all")
    ref = os.path.join(WS, "_zht_ref", "translation_current")
    rmap, rules = registry_map(), locale_layer()
    print("registry map: %d entries   locale layer: %d rules" % (len(rmap), len(rules)))
    for u in units:
        src = os.path.join(ref, u + ".md")
        if not os.path.exists(src):
            print("MISSING  %s (refresh _zht_ref first: python3 _tools_zhs/bootstrap_zhs.py)" % src)
            continue
        text = C.read(src)
        log = []
        out = convert(text, rmap, rules, log)
        drafts = os.path.join(WS, "translation", "drafts")
        n = a.version or next_draft(drafts, u)
        dp = os.path.join(drafts, "%s_v%d.md" % (u, n))
        C.write(dp, out)
        if a.publish:
            C.write(os.path.join(WS, "translation", "current", u + ".md"), out)
        print("== %s -> %s%s  (source sha256 %s)" % (u, os.path.relpath(dp, WS), " + current" if a.publish else "",
                                                   hashlib.sha256(text.encode("utf-8")).hexdigest()[:12]))
        for l in log:
            print("   " + l)
    return 0


if __name__ == "__main__":
    sys.exit(main())
