#!/usr/bin/env python3
"""ingest_dag.py — the scripted gestalt ingest (the no-harness null for G4).

The engine's classic ingest writes one digest per source from a 6,000-char
excerpt against the brief. That is smoketest-grade: no core/satellite
distinction, no gestalt, satellites related to the BRIEF instead of to the
book's spine. The books that read as one authorial act were ingested by a
SESSION doing CLAUDE.md §3: read the core in full, skim every satellite, only
then fan out RELATIONAL digests. This module is that behavior as deterministic
code over pure model calls — the "no-harness DAG" of cloud/PLAN_H0 §1 item 6
and ARM-C of the pre-registered G4 blind side-by-side.

The DAG (every model call is `model.complete` — stateless, logged, E-6-floored):

  1. CLASSIFY   core vs satellites — `config.ingest.core` names the core file;
                absent, the largest source by words is the core (logged).
  2. GESTALT    rolling core synopsis: the core is read WHOLE through a window
                chain (each call: brief + synopsis-so-far + next window → an
                updated synopsis), so the last synopsis has seen every word.
  3. RELATE     one digest per satellite from a 24,000-char excerpt, prompted
                AGAINST THE CORE SYNOPSIS (extends / contradicts / deepens /
                bridges the core — not the brief).
  4. SYNTHESIZE one pass over synopsis + all digests → ordering hints, tensions,
                and HOLES (what no source answers).

Outputs land in canon_refs/ under names `stage_seed._read_digests` already
globs, ordered so the seed model reads the gestalt first and the synthesis
last:

  _digest_00_core_synopsis.md · _digest_<slug>.md × N · _digest_zz_synthesis.md

Enablement: `config.ingest.dag: true` (schema-declared) or env
`BOOKSMITH_INGEST_DAG=1`. The engine's default path stays BYTE-IDENTICAL when
the flag is off (the domain-seam law: non-default branches provably change
nothing). To re-ingest an already-ingested workspace after flipping the flag:
`python _tools/engine.py --config ... --only ingest --force-stage`.

Selftest (offline, mock backend, temp workspace): `python _tools/ingest_dag.py --selftest`
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

WINDOW_CHARS = 24_000        # core chars per rolling-synopsis call
MAX_WINDOWS = 40             # hard cap (~1M chars of core) — loud note beyond
SAT_CHARS = 24_000           # satellite excerpt (4x the classic 6K)
SYNOPSIS_TOKENS = 1_400
DIGEST_TOKENS = 1_200
SYNTHESIS_TOKENS = 1_600


def _slug(stem: str, used: set) -> str:
    base = re.sub(r"[^a-z0-9_]+", "_", stem.lower()).strip("_") or "src"
    s, k = base, 2
    while s in used:
        s, k = f"{base}_{k}", k + 1
    used.add(s)
    return s


def classify(sources: list[Path], cfg: dict) -> tuple[Path, list[Path]]:
    """Core = config.ingest.core (by filename) or the largest source by words."""
    named = ((cfg.get("ingest") or {}).get("core") or "").strip()
    if named:
        for p in sources:
            if p.name == named:
                return p, [s for s in sources if s is not p]
    sized = sorted(sources, key=lambda p: len(p.read_text(encoding="utf-8", errors="replace").split()),
                   reverse=True)
    return sized[0], sized[1:]


def rolling_synopsis(model, brief: str, core: Path, log) -> str:
    text = core.read_text(encoding="utf-8", errors="replace")
    windows = [text[i:i + WINDOW_CHARS] for i in range(0, len(text), WINDOW_CHARS)] or [""]
    if len(windows) > MAX_WINDOWS:
        log(note=f"core windows capped {len(windows)}->{MAX_WINDOWS}")
        windows = windows[:MAX_WINDOWS]
    synopsis = ""
    system = ("You maintain the WORKING SYNOPSIS of a book's core source as it is read in order. "
              "Return the UPDATED synopsis only (<=600 words, prose): the arc so far, the voice "
              "and register, chronology anchors, load-bearing scenes/claims/people, and open "
              "questions the remaining text may answer. Fold the new window in; never lose "
              "earlier established facts; no preamble.")
    for i, w in enumerate(windows, 1):
        prompt = (f"# Book brief\n{brief}\n\n# Working synopsis (after {i - 1} of {len(windows)} windows)\n"
                  f"{synopsis or '(none yet - this is the first window)'}\n\n"
                  f"# Core source: {core.name} - window {i}/{len(windows)}\n{w}\n\n"
                  f"# Task\nReturn the updated working synopsis.")
        synopsis = model.complete(system, prompt, max_tokens=SYNOPSIS_TOKENS, temperature=0.3).strip()
        log(window=i, windows=len(windows), synopsis_words=len(synopsis.split()))
    return synopsis


def satellite_digest(model, brief: str, synopsis: str, p: Path) -> str:
    body = p.read_text(encoding="utf-8", errors="replace")
    system = ("You write a RELATIONAL source digest for a book kit. In <=250 words, state what this "
              "satellite source contains and where it EXTENDS / CONTRADICTS / DEEPENS / BRIDGES the "
              "CORE (whose synopsis you are given). Name specifics (people, dates, claims). "
              "Prose only, no preamble.")
    prompt = (f"# Book brief\n{brief}\n\n# Core synopsis\n{synopsis}\n\n"
              f"# Satellite source: {p.name}\n{body[:SAT_CHARS]}\n\n"
              f"# Task\nWrite the relational digest (against the CORE, not the brief).")
    return model.complete(system, prompt, max_tokens=DIGEST_TOKENS, temperature=0.3).strip()


def synthesis(model, brief: str, synopsis: str, digests: list[tuple[str, str]]) -> str:
    joined = "\n\n".join(f"## {n}\n{t}" for n, t in digests) or "(no satellites)"
    system = ("You write the INGEST SYNTHESIS for a book architect. In <=400 words: (1) a suggested "
              "narrative ORDER and why; (2) TENSIONS - where sources disagree and which to trust; "
              "(3) HOLES - what no source answers that the book will need (the elicitation list). "
              "Numbered sections, terse, no preamble.")
    prompt = (f"# Book brief\n{brief}\n\n# Core synopsis\n{synopsis}\n\n"
              f"# Satellite digests\n{joined}\n\n# Task\nWrite the ingest synthesis.")
    return model.complete(system, prompt, max_tokens=SYNTHESIS_TOKENS, temperature=0.3).strip()


def run_dag(ws: Path, cfg: dict, model, brief: str, sources: list[Path], log) -> list[str]:
    """Execute the DAG; write canon_refs/_digest_*.md; return the digest filenames
    (the engine folds them into its _ingest.json manifest and GATE-1 count)."""
    canon = ws / "canon_refs"
    canon.mkdir(parents=True, exist_ok=True)
    core, sats = classify(sources, cfg)
    log(core=core.name, satellites=len(sats))
    names: list[str] = []

    syn = rolling_synopsis(model, brief, core, log)
    p = canon / "_digest_00_core_synopsis.md"
    p.write_text(f"# Core synopsis - {core.name} (gestalt, read whole)\n\n{syn}\n", encoding="utf-8")
    names.append(p.name)

    used: set = set()
    pairs: list[tuple[str, str]] = []
    for s in sats:
        dg = satellite_digest(model, brief, syn, s)
        dp = canon / f"_digest_{_slug(s.stem, used)}.md"
        dp.write_text(f"# Digest - {s.name} (relational to {core.name})\n\n{dg}\n", encoding="utf-8")
        names.append(dp.name)
        pairs.append((s.name, dg))
        log(satellite=s.name)

    sy = synthesis(model, brief, syn, pairs)
    zp = canon / "_digest_zz_synthesis.md"
    zp.write_text(f"# Ingest synthesis (order - tensions - holes)\n\n{sy}\n", encoding="utf-8")
    names.append(zp.name)
    return names


def _selftest() -> int:
    import shutil
    import tempfile
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import model_client
    tmp = Path(tempfile.mkdtemp(prefix="dag_selftest_"))
    try:
        ws = tmp / "ws"
        (ws / "intake").mkdir(parents=True)
        core = ws / "intake" / "core_memoir.txt"
        core.write_text(("In the spring of 1902 the narrator left the valley. " * 400) +
                        ("The river work began in earnest that autumn. " * 400) +
                        ("Years later the letters resumed, changed in tone. " * 400),
                        encoding="utf-8")
        (ws / "intake" / "sat_letters.txt").write_text("Letters from the brother, 1903-1911. " * 60, encoding="utf-8")
        (ws / "intake" / "sat_gazette.txt").write_text("The county gazette entry for the flood year. " * 60, encoding="utf-8")
        model = model_client.ModelClient({"backend": "mock"})
        events: list[dict] = []
        sources = sorted((ws / "intake").glob("*.txt"))
        names = run_dag(ws, {}, model, "A memoir of the valley years.", sources, log=lambda **kw: events.append(kw))
        canon = ws / "canon_refs"
        assert names[0] == "_digest_00_core_synopsis.md", names
        assert names[-1] == "_digest_zz_synthesis.md", names
        assert len(names) == 4, names                      # synopsis + 2 sats + synthesis
        assert all((canon / n).is_file() and (canon / n).stat().st_size > 40 for n in names)
        assert sorted(canon.glob("_digest_*.md"))[0].name == "_digest_00_core_synopsis.md"
        wins = [e for e in events if "window" in e]
        assert len(wins) >= 2, f"rolling chain did not roll: {events}"    # ~66K chars -> >=2 windows
        assert any(e.get("core") == "core_memoir.txt" for e in events)    # largest won
        ws2 = tmp / "ws2"
        (ws2 / "intake").mkdir(parents=True)
        a = ws2 / "intake" / "small_named_core.txt"
        a.write_text("Named core, deliberately small. " * 20, encoding="utf-8")
        b = ws2 / "intake" / "big_satellite.txt"
        b.write_text("A much larger satellite that would win by size. " * 500, encoding="utf-8")
        c2, sats2 = classify([a, b], {"ingest": {"core": "small_named_core.txt"}})
        assert c2.name == "small_named_core.txt" and [s.name for s in sats2] == ["big_satellite.txt"]
        print("INGEST_DAG SELFTEST: PASS (8/8 assertions held)")
        return 0
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        raise SystemExit(_selftest())
    print(__doc__)
