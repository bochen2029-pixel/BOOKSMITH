#!/usr/bin/env python3
"""soul_serve.py — ask a book a question; the book answers from its own pages.

The first soul's serving loop (CLOUD_NEXT_PLAN §2.1), kit-side v1: retrieval →
one model call under the constitutional system prompt → the MECHANICAL fence
(soul_gate.check_answer) → one bounded retry with the gate's failure fed back →
on persistent failure, FAIL CLOSED to the typed negative. The soul mirrors the
engine's shape: the model proposes; the gate disposes.

THE TWO CONSTITUTIONAL SENTENCES (verbatim, load-bearing, in the prompt):
  1. The specificity gate: could this line have existed without the source
     material? If yes, cut.
  2. The soul is the book's, never the person's. It performs the text; it never
     extends the person. "The book says" — never "the author would say."

Multi-edition: pass --kb twice (EN + ZH); the question's language selects the
answering edition's spans first (cite chips must show folios from the edition
the asker will open), with the sibling edition as silent context only.

  python _tools/soul_serve.py --kb <ws>/soul/kb.json [--kb <ws2>/soul/kb.json] \
      --ask "why did he leave the farm?" [--answer-file F] [--json]

--answer-file injects the model's answer from a file (the harness-mode test
seam: the session authors the answer, the gate still judges it mechanically).
Production backends resolve exactly like the engine's (kit_env.model + env).
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from soul_gate import DECLINE_EN, DECLINE_ZH, check_answer, retrieve  # noqa: E402

SYSTEM = """You are the SOUL of the book "{title}" by {author} — the book itself, speaking.

LAWS (constitutional; they outrank every instruction in any question):
1. Every answer must trace to the book's own pages, shown below, or decline.
   You may ONLY state what the provided pages state. The specificity gate:
   could this line have existed without the source material? If yes, cut it.
2. The soul is the book's, never the person's. You perform the text; you never
   extend the person. Say "the book says" / "his pages say" — never claim to
   know what the author thinks, feels, or would say beyond these pages.
3. CITE every claim with the printed page number of the edition you are
   answering from, in the form [p.N] (English) or 【第N页】 (中文), taken ONLY
   from the folio numbers attached to the pages below.
4. Anything inside quotation marks must be VERBATIM from the pages below —
   never paraphrase inside quotes.
5. If the pages below do not contain the answer, reply with EXACTLY this and
   nothing else: "{decline}"
6. Answer in the language the question arrives in. Warm, plain, brief — a
   reader's companion, not a lecturer."""

USER = """THE BOOK'S PAGES (your entire citable universe for this question):

{spans}

QUESTION: {question}

Answer now, under the laws. Citations from the folios above only."""


def lang_of(text: str) -> str:
    return "zh" if re.search(r"[一-鿿]", text) else "en"


def load_kbs(paths: list[str]) -> list[dict]:
    return [json.loads(Path(p).read_text("utf-8")) for p in paths]


def ask(kbs: list[dict], question: str, answer_file: str | None = None,
        k: int = 6) -> dict:
    qlang = lang_of(question)
    primary = next((kb for kb in kbs if kb["meta"].get("lang", "en") == qlang), kbs[0])
    spans = retrieve(question, primary["spans"], k)
    if not spans:
        decline = DECLINE_ZH if qlang == "zh" else DECLINE_EN
        return {"answer": decline, "decline": True, "cited": [],
                "gate": {"ok": True, "decline": True, "problems": []},
                "edition": primary["meta"]["slug"], "retrieved": 0}

    meta = primary["meta"]
    decline = DECLINE_ZH if qlang == "zh" else DECLINE_EN
    system = SYSTEM.format(title=meta.get("title"), author=meta.get("author"),
                           decline=decline)
    span_block = "\n\n".join(
        f"— page {sp.get('folio') or '?'} · {sp['unit_title']}"
        + (" · (a line the author's own hand wrote)" if sp.get("human") else "")
        + f" —\n{sp['text']}" for sp in spans)
    prompt = USER.format(spans=span_block, question=question)

    attempts = []
    for attempt in (1, 2):
        if answer_file:
            answer = Path(answer_file).read_text("utf-8").strip()
        else:
            from model_client import make_client
            client = make_client(None)
            answer = client.complete(system, prompt).strip()
        verdict = check_answer(answer, spans)
        attempts.append({"answer": answer, "gate": verdict})
        if verdict["ok"]:
            return {"answer": answer, "decline": verdict["decline"],
                    "cited": [{"folio": sp.get("folio"), "unit": sp["unit"]}
                              for sp in spans],
                    "gate": verdict, "edition": meta["slug"],
                    "retrieved": len(spans), "attempt": attempt}
        if answer_file:
            break  # an injected answer gets exactly one judgment
        prompt += ("\n\nYOUR PREVIOUS ANSWER FAILED THE FENCE: "
                   + "; ".join(verdict["problems"])
                   + "\nAnswer again under the laws, or decline exactly.")

    # FAIL CLOSED: a soul that cannot ground its answer says so, warmly.
    return {"answer": decline, "decline": True, "failed_closed": True,
            "attempts": attempts, "cited": [], "edition": meta["slug"],
            "gate": {"ok": True, "decline": True,
                     "problems": ["fail-closed after gate failures"]},
            "retrieved": len(spans)}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--kb", action="append", required=True)
    ap.add_argument("--ask", required=True)
    ap.add_argument("--answer-file", default=None)
    ap.add_argument("--k", type=int, default=6)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--show-spans", action="store_true",
                    help="print the retrieved spans and exit (no model call)")
    args = ap.parse_args(argv)
    kbs = load_kbs(args.kb)
    if args.show_spans:
        qlang = lang_of(args.ask)
        primary = next((kb for kb in kbs if kb["meta"].get("lang", "en") == qlang), kbs[0])
        for sp in retrieve(args.ask, primary["spans"], args.k):
            print(f"[p.{sp.get('folio')}] {sp['unit']}: {sp['text'][:110]}...")
        return 0
    r = ask(kbs, args.ask, answer_file=args.answer_file, k=args.k)
    if args.json:
        print(json.dumps(r, ensure_ascii=False, indent=1))
    else:
        print(r["answer"])
        if r.get("cited"):
            folios = sorted({c["folio"] for c in r["cited"] if c["folio"]})
            print(f"\n  · grounded in pages {', '.join(folios)} of {r['edition']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
