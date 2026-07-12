#!/usr/bin/env python3
r"""
voice_elicit.py — bootstrap an operator's voice from their OWN writing.

BOOKSMITH must not assume any one author. This reads a sample of the operator's
prose and emits (a) a suggested `book_config.voice` block and (b) a
`docs/author_voice/AUTHOR_VOICE_<slug>.md` fingerprint, so a new operator gets a
personal voice spec instead of inheriting someone else's. It suggests; the
operator edits. Deterministic, stdlib only.

Usage:
  python _tools/voice_elicit.py sample1.md [sample2.txt ...] --name "Jane Doe"
  type sample.txt | python _tools/voice_elicit.py --name "Jane Doe"
  ... [--json] [--write]   (--write saves the AUTHOR_VOICE_<slug>.md profile)
"""
from __future__ import annotations
import argparse, json, re, statistics, sys
from collections import Counter
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
ROOT = TOOLS.parent

# A compact, widely-recognized set of machine-prose tells. A STARTING blacklist
# the operator can trim/extend; not a claim about their sample.
AI_TELLS = [
    "tapestry", "delve", "myriad", "plethora", "testament", "realm", "navigate",
    "landscape", "ever-evolving", "ever-changing", "in the realm of", "it's important to note",
    "rich tapestry", "at the end of the day", "a testament to", "navigating the complexities",
    "dive into", "unlock", "elevate", "seamless", "robust", "leverage", "underscore",
    "in today's world", "when it comes to", "a myriad of",
]
STOP = set("the a an and or but of to in on at for with as by is are was were be been being it "
           "its this that these those he she they we you i him her them his hers their our your my "
           "not no yes if then than so such from into over under out up down off about which who "
           "whom whose what when where why how all any each few more most other some no nor only own "
           "same too very can will just don should now had has have do does did would could may might "
           "must shall there here one two".split())


def load_text(files):
    if files:
        chunks = []
        for f in files:
            try:
                chunks.append(Path(f).read_text(encoding="utf-8", errors="replace"))
            except Exception as e:
                print(f"  (skipped {f}: {e})", file=sys.stderr)
        return "\n\n".join(chunks)
    data = sys.stdin.read() if not sys.stdin.isatty() else ""
    return data


def sentences(text):
    # strip headings + markdown noise, split on sentence enders
    body = re.sub(r"^#.*$", "", text, flags=re.M)
    body = re.sub(r"[*_`>#]", "", body)
    parts = re.split(r"(?<=[.!?])\s+", body)
    return [s.strip() for s in parts if len(s.strip().split()) >= 3]


def analyze(text, name):
    words = re.findall(r"[A-Za-z']+", text)
    wc = len(words)
    sents = sentences(text)
    slens = [len(s.split()) for s in sents] or [0]
    em = text.count("—") + text.count("–")
    em_density = round(em / (wc / 1000), 2) if wc else 0.0
    tells_present = sorted({t for t in AI_TELLS if re.search(r"\b" + re.escape(t) + r"\b", text, re.I)})
    # distinctive content words (frequency, minus stopwords) -> greenlist/sacred hints
    freq = Counter(w.lower() for w in words if w.lower() not in STOP and len(w) > 3)
    distinctive = [w for w, _ in freq.most_common(15)]
    # exemplars: the longest coherent paragraphs
    paras = [p.strip() for p in re.split(r"\n\s*\n", re.sub(r"^#.*$", "", text, flags=re.M)) if len(p.split()) >= 40]
    paras.sort(key=lambda p: -len(p.split()))
    exemplars = paras[:2]

    voice = {
        "author": name,
        "unit_noun": "chapter",
        "no_em_dashes": em_density < 0.5,   # if they basically don't use them, ban them in generation
        "blacklist": AI_TELLS[:12],          # a starting AI-tell guard; operator trims/extends
        "greenlist": distinctive[:8],
        "sacred_terms": [],
        "exemplars_path": f"exemplars/anchor.md",
    }
    profile = {
        "name": name,
        "words_sampled": wc,
        "sentences": len(sents),
        "avg_sentence_len": round(statistics.mean(slens), 1),
        "sentence_len_stdev": round(statistics.pstdev(slens), 1) if len(slens) > 1 else 0.0,
        "em_dash_density_per_1000w": em_density,
        "ai_tells_present_in_sample": tells_present,
        "distinctive_vocabulary": distinctive,
        "exemplars": exemplars,
    }
    return voice, profile


def render_profile_md(voice, profile):
    L = profile
    lines = [
        f"# AUTHOR VOICE — {L['name']}",
        "",
        "*Elicited by `voice_elicit.py` from the operator's own writing. Suggestions; edit freely.*",
        "",
        "## Fingerprint",
        f"- Sampled: {L['words_sampled']} words, {L['sentences']} sentences.",
        f"- Sentence rhythm: avg {L['avg_sentence_len']} words (stdev {L['sentence_len_stdev']}).",
        f"- Em-dash density: {L['em_dash_density_per_1000w']} per 1000 words "
        f"-> `no_em_dashes` suggested **{str(voice['no_em_dashes']).lower()}**.",
        f"- AI-tell words found in the sample: {', '.join(L['ai_tells_present_in_sample']) or 'none'}.",
        f"- Distinctive vocabulary: {', '.join(L['distinctive_vocabulary'])}.",
        "",
        "## Suggested book_config.voice",
        "```json",
        json.dumps(voice, indent=2, ensure_ascii=False),
        "```",
        "",
        "## Exemplar passages (representative of the operator's register)",
    ]
    for i, ex in enumerate(L["exemplars"], 1):
        lines += [f"### Exemplar {i}", ex, ""]
    return "\n".join(lines)


def main(argv=None):
    ap = argparse.ArgumentParser(description="Bootstrap an operator's voice from their writing.")
    ap.add_argument("files", nargs="*", help="sample prose files (or pipe via stdin)")
    ap.add_argument("--name", default="Your Name")
    ap.add_argument("--json", action="store_true", help="print the voice block + profile as JSON")
    ap.add_argument("--write", action="store_true", help="save docs/author_voice/AUTHOR_VOICE_<slug>.md")
    args = ap.parse_args(argv)
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # Windows console is cp1252
    except Exception:
        pass

    text = load_text(args.files)
    if not text.strip():
        print("No sample text. Pass files or pipe prose via stdin.", file=sys.stderr)
        return 1
    voice, profile = analyze(text, args.name)

    if args.json:
        print(json.dumps({"voice": voice, "profile": profile}, indent=2, ensure_ascii=False))
    else:
        print(render_profile_md(voice, profile))

    if args.write:
        slug = re.sub(r"[^a-z0-9]+", "_", args.name.lower()).strip("_") or "operator"
        out = ROOT / "docs" / "author_voice" / f"AUTHOR_VOICE_{slug}.md"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(render_profile_md(voice, profile), encoding="utf-8")
        print(f"\nwrote {out}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
