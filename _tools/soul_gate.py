#!/usr/bin/env python3
"""soul_gate.py — the soul's citation fence: retrieval + the mechanical gate.

The constitutional law this enforces (FUSOR Addendum C; CLOUD_NEXT_PLAN §2.1):
**every answer must trace to the book's own pages or decline.** The fence is
CHECKED, never trusted — scriptorium measured 28.5% of model "quotes" as
paraphrase-as-quote, which is why the verbatim check below is mechanical.

Two halves, both deterministic (no model, no network):

  retrieve(question, spans, k)  — keyless lexical retrieval: lowercase word
      tokens + CJK bigrams, idf-weighted overlap. Good for a book-sized corpus;
      upgradeable later without touching the gate.

  check_answer(answer, cited_spans) — the gate:
      * a substantive answer with ZERO page citations FAILS
      * every cited folio must belong to the spans actually provided
      * every quoted fragment (".." «»「」 “”) of >=8 chars must appear VERBATIM
        (whitespace/NFC-normalized) inside the cited spans — else FAIL
        (the paraphrase-as-quote catch)
      * the typed negative ("the book doesn't tell us that part." /
        「书里没有讲到这一段。」) PASSES only bare: no citations, no smuggled
        content around it

CLI self-test:  python _tools/soul_gate.py --selftest
"""
from __future__ import annotations

import argparse
import json
import math
import re
import sys
import unicodedata
from collections import Counter

DECLINE_EN = "the book doesn't tell us that part."
DECLINE_ZH = "书里没有讲到这一段。"

CITE_RE = re.compile(r"[\[（(【]\s*(?:p\.?\s*|第)\s*(\d{1,3})\s*(?:页)?\s*[\]）)】]", re.I)
QUOTE_RE = re.compile(r"[\"“„«「『]([^\"”«»「」『』]{8,400})[\"”»「」』]")


def _norm(s: str) -> str:
    return re.sub(r"\s+", "", unicodedata.normalize("NFC", s))


def _norm_ci(s: str) -> str:
    # decline detection is case-insensitive (a model will capitalize the typed
    # negative at sentence start); QUOTE checks stay case-PRESERVING via _norm,
    # because a wrong-case quotation is not verbatim.
    return _norm(s).casefold()


def _tokens(s: str) -> list[str]:
    s = unicodedata.normalize("NFC", s.lower())
    words = re.findall(r"[a-z0-9]{2,}", s)
    cjk = re.findall(r"[一-鿿]", s)
    bigrams = ["".join(p) for p in zip(cjk, cjk[1:])]
    return words + bigrams


def retrieve(question: str, spans: list[dict], k: int = 6) -> list[dict]:
    q = Counter(_tokens(question))
    if not q:
        return []
    df: Counter = Counter()
    toks = []
    for sp in spans:
        t = set(_tokens(sp["text"]))
        toks.append(t)
        for w in t:
            df[w] += 1
    n = max(len(spans), 1)
    scored = []
    for sp, t in zip(spans, toks):
        s = sum(c * math.log(1 + n / (1 + df[w])) for w, c in q.items() if w in t)
        if s > 0:
            scored.append((s, sp))
    scored.sort(key=lambda x: -x[0])
    return [sp for _s, sp in scored[:k]]


def is_decline(answer: str) -> bool:
    a = answer.strip().strip('"“”「」')
    return _norm_ci(a) in (_norm_ci(DECLINE_EN), _norm_ci(DECLINE_ZH))


def check_answer(answer: str, cited_spans: list[dict]) -> dict:
    problems = []
    a = answer.strip()
    if not a:
        return {"ok": False, "decline": False, "problems": ["empty answer"]}

    if is_decline(a):
        return {"ok": True, "decline": True, "problems": []}
    # a decline phrase buried inside a longer answer = smuggled content
    if _norm_ci(DECLINE_EN) in _norm_ci(a) or _norm_ci(DECLINE_ZH) in _norm_ci(a):
        problems.append("decline phrase mixed with other content; the negative must stand alone")

    cited_folios = {str(m.group(1)) for m in CITE_RE.finditer(a)}
    allowed = {str(sp.get("folio")) for sp in cited_spans if sp.get("folio")}
    if not cited_folios:
        problems.append("substantive answer carries no page citation")
    else:
        bogus = cited_folios - allowed
        if bogus:
            problems.append(f"cited folio(s) not in the provided spans: {sorted(bogus)}")

    corpus = _norm(" ".join(sp["text"] for sp in cited_spans))
    for m in QUOTE_RE.finditer(a):
        frag = _norm(m.group(1))
        if len(frag) >= 8 and frag not in corpus:
            problems.append(f"quote is not verbatim from the cited pages: "
                            f"“{m.group(1)[:60]}…”")

    return {"ok": not problems, "decline": False, "problems": problems}


# ---------------------------------------------------------------- self-test
def _selftest() -> int:
    spans = [
        {"id": "s1", "folio": "4", "text": "Close to half of my volunteer time went to "
         "Carlquist's notebooks. I was not decoding it. I was receiving it."},
        {"id": "s2", "folio": "23", "text": "The notebooks had been photographed page by "
         "page, and we would each take a notebook and type at home."},
    ]
    ok = 0
    fail = 0

    def t(name, got, want):
        nonlocal ok, fail
        if got == want:
            ok += 1
            print(f"  PASS {name}")
        else:
            fail += 1
            print(f"  FAIL {name}: got {got}")

    r = retrieve("where did his volunteer time go?", spans, 2)
    t("retrieve hits s1 first", r[0]["id"] if r else None, "s1")

    t("grounded answer passes",
      check_answer('He spent close to half his time on the notebooks [p.4].', spans)["ok"], True)
    t("no citation fails",
      check_answer("He spent half his time on the notebooks.", spans)["ok"], False)
    t("bogus folio fails",
      check_answer("He worked at home [p.99].", spans)["ok"], False)
    t("verbatim quote passes",
      check_answer('He wrote: "I was not decoding it. I was receiving it." [p.4]', spans)["ok"], True)
    t("paraphrase-as-quote fails",
      check_answer('He wrote: "I never decoded it, only received it." [p.4]', spans)["ok"], False)
    t("bare decline passes", check_answer(DECLINE_EN, spans)["ok"], True)
    t("bare ZH decline passes", check_answer(DECLINE_ZH, spans)["ok"], True)
    t("decline+content fails",
      check_answer("The book doesn't tell us that part. But I think it was 1963 [p.4].",
                   spans)["ok"], False)
    t("ZH cite format accepted",
      check_answer("他把将近一半的时间给了笔记本【第4页】。", spans)["ok"], True)

    print(f"SOUL_GATE SELFTEST: {ok} pass / {fail} fail")
    return 1 if fail else 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--kb", default=None, help="kb.json for an ad-hoc retrieve")
    ap.add_argument("--ask", default=None)
    args = ap.parse_args(argv)
    if args.selftest:
        return _selftest()
    if args.kb and args.ask:
        kb = json.loads(open(args.kb, encoding="utf-8").read())
        for sp in retrieve(args.ask, kb["spans"], 6):
            print(f"[p.{sp.get('folio')}] {sp['unit']}: {sp['text'][:100]}...")
        return 0
    ap.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())
