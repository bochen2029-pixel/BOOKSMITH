#!/usr/bin/env python3
r"""
authorial_act.py — the "single authorial act" quality gate (BOOKSMITH, roadmap H1.3).

Mechanizes invariant #2: the manuscript must read as one continuous authorial act, not
N units generated in isolation and stitched. This is a SCORING gate over the assembled
manuscript that fails a book which passes the mechanical GATE-3/4 today but *reads*
mass-produced. It is the missing half of the two-verifier model for prose quality:
lint_manuscript catches banned vocab + corruption; this catches the structural tells.

Detectors:
  register_uniformity — >=3 units whose mean sentence length AND lexical diversity are
                        near-identical across the whole book (uniform register is *the*
                        AI tell; a human book breathes, units differ). [high]
  callback_exactness  — a long word-sequence (default 7-gram) repeated VERBATIM across
                        two different units. Human callbacks vary the wording; exact
                        quotation is the AI signature. The sanctioned refrain / sacred
                        terms are exempt. [high]
  meta_openers        — a unit opening with "In this chapter", "We will explore",
                        "Building on", "This chapter", etc. [med]
  summary_boxes       — "Key Takeaways" / "In summary" / "To summarize" / "In conclusion"
                        blocks (the listicle tell). [med]
  ending_repetition   — two or more units ending on the identical final sentence (AI
                        books close every unit the same way). [med]

CONTRACT
  python authorial_act.py --config book_config.json [--src master.md] [--json] [--strict]
      -> reads the assembled master (outputs/markdown/<slug>_v*.md) or, failing that,
         manuscript/current/*.md; splits into units at H1; scores. Prints a human report
         (or --json). Exit 0 clean / 1 the gate fails / 2 usage. --strict fails on ANY
         finding (default fails on any HIGH, or on >=4 findings total).
  python authorial_act.py --selftest
      -> proves it PASSES a varied book and FAILS a uniform/verbatim one. No deps.
"""
from __future__ import annotations

import argparse
import json
import re
import statistics
import sys
from pathlib import Path

TOOLS = Path(__file__).resolve().parent

SEVERITY_WEIGHT = {"high": 5, "med": 2, "low": 1}
NGRAM = 7  # a 7-word verbatim cross-unit repeat is the callback-exactness signal


# ---------------------------------------------------------------------------
# text helpers
# ---------------------------------------------------------------------------
def split_units(md: str) -> list[dict]:
    """Split a manuscript into units at H1 ('# Title'). Front matter before the first
    H1 is ignored. Returns [{title, body}]."""
    units, cur = [], None
    for line in md.splitlines():
        m = re.match(r"^#\s+(.*\S)\s*$", line)
        if m:
            if cur is not None:
                units.append(cur)
            cur = {"title": m.group(1).strip(), "lines": []}
        elif cur is not None:
            cur["lines"].append(line)
    if cur is not None:
        units.append(cur)
    for u in units:
        u["body"] = "\n".join(u.pop("lines")).strip()
    return [u for u in units if u["body"]]


def words(text: str) -> list[str]:
    return re.findall(r"[A-Za-z']+", text.lower())


def sentences(text: str) -> list[str]:
    # strip markdown headings/list markers, then split on sentence enders
    flat = re.sub(r"(?m)^\s{0,3}#{1,6}\s+", "", text)
    flat = re.sub(r"(?m)^\s*[-*|>]\s*", "", flat)
    parts = re.split(r"(?<=[.!?])\s+", flat.replace("\n", " "))
    return [s.strip() for s in parts if len(s.strip()) > 1]


def _cv(xs: list[float]) -> float:
    xs = [x for x in xs if x is not None]
    if len(xs) < 2:
        return 1.0
    m = statistics.mean(xs)
    if m == 0:
        return 1.0
    return statistics.pstdev(xs) / m


# ---------------------------------------------------------------------------
# detectors -> list of findings {detector, severity, unit, detail}
# ---------------------------------------------------------------------------
META_OPENERS = re.compile(
    r"^\W*(in this (chapter|part|section)|this (chapter|part|section)\b|"
    r"we will (explore|examine|discuss|look at|cover)|in the (previous|last) (chapter|part)|"
    r"building on|as we (saw|discussed|noted) (earlier|above|previously)|"
    r"having (established|seen|covered))", re.I)

SUMMARY_BOX = re.compile(
    r"(?im)^\s{0,3}(#{1,6}\s*)?(key takeaways?|in summary|to summarize|in conclusion|"
    r"summary\s*:|takeaways?\s*:|to sum up|recap\s*:)")


def d_register_uniformity(units, strict) -> list[dict]:
    if len(units) < 3:
        return []
    means, ttrs = [], []
    for u in units:
        ss = sentences(u["body"])
        ws = words(u["body"])
        means.append(statistics.mean([len(words(s)) for s in ss]) if ss else 0)
        ttrs.append((len(set(ws)) / len(ws)) if ws else 0)
    cv_len, cv_ttr = _cv(means), _cv(ttrs)
    thr_len = 0.14 if strict else 0.09
    thr_ttr = 0.10 if strict else 0.06
    if cv_len < thr_len and cv_ttr < thr_ttr:
        return [{"detector": "register_uniformity", "severity": "high", "unit": "(book)",
                 "detail": f"units are near-uniform: sentence-length CV={cv_len:.3f} "
                           f"(< {thr_len}) and lexical-diversity CV={cv_ttr:.3f} (< {thr_ttr}). "
                           f"A single authorial act varies register across units."}]
    return []


def d_callback_exactness(units, exempt_texts) -> list[dict]:
    exempt = " ".join(t.lower() for t in exempt_texts)
    seen: dict[tuple, int] = {}
    findings, reported = [], set()
    for idx, u in enumerate(units):
        ws = words(u["body"])
        grams = {tuple(ws[i:i + NGRAM]) for i in range(len(ws) - NGRAM + 1)}
        for g in grams:
            phrase = " ".join(g)
            if phrase in exempt:
                continue
            prev = seen.get(g)
            if prev is not None and prev != idx and g not in reported:
                reported.add(g)
                findings.append({
                    "detector": "callback_exactness", "severity": "high",
                    "unit": f'{units[prev]["title"]!r} + {u["title"]!r}',
                    "detail": f'verbatim {NGRAM}-word repeat across units: "...{phrase}...". '
                              f"Vary the wording; exact quotation is the AI tell."})
            elif prev is None:
                seen[g] = idx
    return findings


def d_meta_openers(units) -> list[dict]:
    out = []
    for u in units:
        opener = " ".join(words(u["body"])[:1]) and u["body"].lstrip().splitlines()[0] if u["body"].strip() else ""
        first = re.sub(r"^\W*", "", opener)
        if META_OPENERS.match(first):
            out.append({"detector": "meta_openers", "severity": "med", "unit": u["title"],
                        "detail": f'opens with meta-commentary: "{first[:60]}..."'})
    return out


def d_summary_boxes(units) -> list[dict]:
    out = []
    for u in units:
        m = SUMMARY_BOX.search(u["body"])
        if m:
            out.append({"detector": "summary_boxes", "severity": "med", "unit": u["title"],
                        "detail": f'contains a summary/takeaways block: "{m.group(0).strip()[:40]}"'})
    return out


def d_ending_repetition(units) -> list[dict]:
    last = {}
    out = []
    for u in units:
        ss = sentences(u["body"])
        if not ss:
            continue
        key = " ".join(words(ss[-1]))
        if len(key.split()) < 4:
            continue
        if key in last:
            out.append({"detector": "ending_repetition", "severity": "med",
                        "unit": f'{last[key]!r} + {u["title"]!r}',
                        "detail": "two units end on the identical final sentence; rotate unit endings."})
        else:
            last[key] = u["title"]
    return out


def analyze(md: str, exempt_texts=None, strict=False) -> dict:
    units = split_units(md)
    exempt_texts = exempt_texts or []
    findings = []
    findings += d_register_uniformity(units, strict)
    findings += d_callback_exactness(units, exempt_texts)
    findings += d_meta_openers(units)
    findings += d_summary_boxes(units)
    findings += d_ending_repetition(units)
    score = sum(SEVERITY_WEIGHT.get(f["severity"], 1) for f in findings)
    highs = [f for f in findings if f["severity"] == "high"]
    if strict:
        ok = not findings
    else:
        ok = (not highs) and (len(findings) < 4)
    return {"units": len(units), "findings": findings, "score": score,
            "high": len(highs), "pass": ok}


# ---------------------------------------------------------------------------
# input resolution
# ---------------------------------------------------------------------------
def load_manuscript(cfg_path: Path, src: str | None) -> tuple[str, str]:
    if src:
        p = Path(src)
        return p.read_text(encoding="utf-8", errors="replace"), str(p)
    cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
    slug = cfg.get("slug", "")
    ws = cfg_path.parent
    masters = sorted((ws / "outputs" / "markdown").glob(f"{slug}_v*.md"))
    if masters:
        return masters[-1].read_text(encoding="utf-8", errors="replace"), str(masters[-1])
    cur = sorted((ws / "manuscript" / "current").glob("*_current.md"))
    if cur:
        return "\n\n".join(p.read_text(encoding="utf-8", errors="replace") for p in cur), \
            f"{len(cur)} unit(s) in manuscript/current/"
    return "", "(no manuscript found)"


def exempts_from_cfg(cfg_path: Path) -> list[str]:
    try:
        cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
    except Exception:
        return []
    voice = cfg.get("voice", {}) or {}
    ex = list(voice.get("sacred_terms", []) or [])
    ex += list(voice.get("greenlist", []) or [])
    # a refrain, if the registry recorded one
    refr = cfg_path.parent / "registry" / "refrain.md"
    if refr.exists():
        m = re.search(r"\*\*Exact wording[^:]*:\*\*\s*(.+)", refr.read_text(encoding="utf-8", errors="replace"))
        if m:
            ex.append(m.group(1).strip())
    return [e for e in ex if e]


# ---------------------------------------------------------------------------
# self-test
# ---------------------------------------------------------------------------
def selftest() -> int:
    fails = []
    good = """# The Quiet Start
It began small. A single line, then a pause. He waited. The room held its breath and
gave nothing back, and still he stayed, because leaving felt worse than the waiting did.
Morning came the way mornings do, without asking permission, and it found him already
awake and unsure whether that counted as a victory or merely as evidence.

# The Long Middle
Everything that follows depends on a claim so large it embarrasses the person making it,
which is why the person making it tends to whisper: that the shape of a life is decided
less by its declared intentions than by the ten thousand unremarked choices that fill the
hours between them. Consider the ledger you keep without meaning to. It records the days.

# The Turn
Then it changed. Not all at once. A hinge, not a door. She noticed the light first, the
way it leaned an extra moment against the wall before letting go, and she understood, in
the wordless way the body understands weather, that something had already begun to end.
"""
    bad = """# Chapter One
In this chapter we will explore the idea. The system holds the state on disk today. The
system holds the state on disk today. Every step is checked before the next one begins.
Every step is checked before the next one begins now.

# Chapter Two
In this chapter we will explore the result. The system holds the state on disk today. Data
moves from one place to another place. Data moves from one place to another place here.

## Key Takeaways
The system holds the state on disk today.

# Chapter Three
In this chapter we will explore the end. Nothing here is left to chance at all. Nothing
here is left to chance at all.
"""
    rg = analyze(good, strict=False)
    if not rg["pass"]:
        fails.append(f"GOOD manuscript should PASS, got findings: {[f['detector'] for f in rg['findings']]}")
    rb = analyze(bad, strict=False)
    if rb["pass"]:
        fails.append("BAD manuscript should FAIL the gate but passed")
    dets = {f["detector"] for f in rb["findings"]}
    for need in ("callback_exactness", "meta_openers", "summary_boxes"):
        if need not in dets:
            fails.append(f"BAD manuscript: detector '{need}' did not fire (got {sorted(dets)})")
    if fails:
        print("AUTHORIAL_ACT SELFTEST: FAIL")
        for f in fails:
            print("  - " + f)
        return 1
    print("AUTHORIAL_ACT SELFTEST: PASS (varied book passes; uniform/verbatim book fails on "
          + ", ".join(sorted(dets)) + ")")
    return 0


def main(argv=None) -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    ap = argparse.ArgumentParser(description="The single-authorial-act quality gate (BOOKSMITH).")
    ap.add_argument("--config", help="path to book_config.json")
    ap.add_argument("--src", help="analyze this markdown file directly")
    ap.add_argument("--json", action="store_true", help="emit JSON")
    ap.add_argument("--strict", action="store_true", help="fail on ANY finding")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)

    if args.selftest:
        return selftest()
    if not args.config and not args.src:
        ap.print_help()
        return 2
    cfg_path = Path(args.config) if args.config else None
    md, where = load_manuscript(cfg_path, args.src) if (cfg_path or args.src) else ("", "")
    if not md.strip():
        print(json.dumps({"pass": True, "units": 0, "findings": [], "note": "no manuscript"}) if args.json
              else "authorial_act: no manuscript found; nothing to score.")
        return 0
    exempts = exempts_from_cfg(cfg_path) if cfg_path else []
    result = analyze(md, exempt_texts=exempts, strict=args.strict)
    result["source"] = where
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        verdict = "PASS" if result["pass"] else "FAIL"
        print(f"=== authorial_act: {verdict} === ({result['units']} units, score {result['score']}, "
              f"{result['high']} high) [{where}]")
        for f in result["findings"]:
            print(f"  [{f['severity']:>4}] {f['detector']}: {f['unit']} - {f['detail']}")
        if result["pass"] and not result["findings"]:
            print("  reads as one continuous authorial act (no structural tells).")
    return 0 if result["pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
