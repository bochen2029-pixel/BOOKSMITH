# The BOOKSMITH Engine — control inversion (the graduation-exam one-shot)

*The deterministic pipeline engine. Companion to `CLAUDE.md` (the interactive,
session-driven flow) and `KIT_ARCHITECTURE.md` (the invariant spec). Files:
`_tools/engine.py`, `_tools/model_client.py`, `_tools/engine_smoketest.py`.*

## Why this exists

Every failure in this kit's history came from ONE place: a model *session* being
the engine of the pipeline, holding sequence, state, and discipline in its head
across a long horizon. Sessions drift, compact, forget an ordering, resume off a
stale map. The parts that NEVER failed are the gates and the disk.

So the engine inverts control. The interactive flow (`CLAUDE.md`) has the model
holding the loop and calling tools. The engine flips it: **deterministic code
holds the loop; the model is a pure function it calls.**

| | Interactive flow (CLAUDE.md) | Engine (engine.py) |
|---|---|---|
| Who holds sequence/state | the model session (in context) | code, on disk (`_engine/state.json`) |
| The model's role | the driver; uses tools; has discretion | a pure function: prose in, prose out, NO tools |
| Gates | the model remembers to run them | the engine runs every gate itself |
| Resume after crash/compaction | re-read ledger + orient | read state.json, re-hash inputs, continue. ZERO orientation |

## The three invariants

1. **The model is a pure function.** `model_client.complete(system, prompt) -> text`.
   Stateless. No tools. No memory. No discretion. Every call is independent and
   logged to `_engine/calls/`. Quality of prose is the model's job; *everything
   else* is the engine's.
2. **The engine owns all state on disk**, keyed by content hashes. There is no
   in-memory "where am I". A stage is `done` only if its inputs hash the same AND
   its output artifacts still exist. Delete a finished chapter and the engine
   re-derives that exactly one unit is missing and re-runs it.
3. **Every gate is the engine's, and it fails loudly.** After each stage the
   engine runs the real gate (in-code voice/word checks per unit; the real
   `lint_manuscript.py` / `verify_build.py` subprocesses for integration and
   formats), retries a bounded number of times, and on persistent failure writes
   `_engine/HARDSTOP.json` and exits nonzero. Re-running resumes at the stop.

## Stages (fixed, deterministic order)

```
[ingest] -> [seed] -> precheck -> draft:<unit>* -> integrate -> assemble -> produce:<format>* -> [cover] -> verify -> emit
```

The bracketed **[ingest] -> [seed]** front-half is the ARCHITECT preamble: it runs only
when a book arrives as a *brief* (a `brief.md` gist + optional `intake/` docs) with no
`seed.md` and no `units` yet. It turns a gist + sources into a full Book Bible + contracts
+ a schema-valid config, so `engine.py --config <brief-config>` runs INTAKE -> EMIT end to
end. An already-architected book (seed.md + units present) skips it untouched.

- **[ingest]** — (architect; only when a brief arrives with `intake/` docs and no digests)
  normalize real documents (PDF via PyMuPDF, DOCX/EPUB/HTML via stdlib) to markdown with
  `manuscript_ingest.py` (into `intake/converted/`), then discover + classify every source
  and write one relational digest per source to `canon_refs/_digest_*.md` plus a
  `_ingest.json` manifest. Gate **GATE-1**. (`intake/converted/` is excluded from the
  ingest input-hash, so normalizing a doc never makes the stage look stale.)
- **[seed]** — (architect; only when there is no `seed.md` / no `units`) turn the brief
  (+ digests) into a structured plan via the model as a pure function, then deterministically
  write `seed.md` (§1–§7), per-unit `contracts/`, `registry/`, `exemplars/`, and a
  schema-valid `book_config.json`. Gate **GATE-2** (schema-valid + one contract per unit +
  seed present). Keyless under `--backend harness`: the plan comes back over the same disk
  bridge the draft turns use (a `seed.request.json` -> `seed.response.json` handshake). When
  no model JSON is available (dry-run/mock), a deterministic fallback keeps the spine moving.
- **precheck** — `book_config.json` validates against the schema; seed/contracts present.
- **draft:<unit>** — build the Context Pack from disk (this contract + prior unit's
  full prose + seed + registries), call the model as a pure function, write
  `manuscript/current/<id>_current.md`, run the per-unit gate (H1 == title, word
  count within 0.6-1.6x, no em-dash if `voice.no_em_dashes`, no blacklist term),
  bounded 3-attempt retry with the gate feedback fed back into the prompt.
  Class-A units are never drafted (outline-only, left for the human).
- **integrate** — the real `lint_manuscript.py` over the whole manuscript.
- **assemble** — `assemble_manuscript.py` -> the one version-pinned master.
- **produce:<format>** — the interior generator for the format, then
  `verify_build.py --format <fmt>` as the gate.
- **cover** — best-effort (skipped in `--dry-run`; a missing art stack never hard-stops).
- **verify** — `verify_build.py --format all`.
- **emit** — write `outputs/MANIFEST.json`.

## Usage

```bash
# a real one-shot (needs a model backend + a seed + contracts already in place)
python _tools/engine.py --config book_workspace/<slug>/book_config.json

# a FRESH book from just a brief: drop a minimal schema-valid book_config.json
# (title/author/slug/is_fiction/formats) + a brief.md (the gist, optionally with
# "chapters: N" / "words: N" hints, and/or intake/ docs) into the workspace. The
# engine architects digests + seed.md + units + contracts FIRST, then drafts to a
# finished folder. Keyless in-session:
python _tools/engine.py --config book_workspace/<slug>/book_config.json --backend harness

# resume: just run the same command again. It reads state.json and continues.
# dry-run the machine with the mock model + all real gates, no cost, no Word:
python _tools/engine.py --config .../book_config.json --dry-run --to assemble

python _tools/engine.py --config .../book_config.json --status     # print on-disk state
python _tools/engine.py --config .../book_config.json --from verify # run a sub-range
```

Flags: `--backend mock|anthropic|openai`, `--to STAGE`, `--from STAGE`,
`--dry-run`, `--no-cover`, `--status`, `--fresh`.

## The model seam (backends)

Configured in `kit_env.model` (env overrides win). The model is chosen per
machine; the engine code never changes.

- **anthropic** — Claude via the Anthropic Messages API, key from `ANTHROPIC_API_KEY`.
  Best prose. The default for a real run.
- **openai** — any OpenAI-compatible `/v1/chat/completions` (a local `llama-server`,
  vLLM, an OpenAI key). The sovereign / offline path.
- **mock** — deterministic, network-free, cost-free. Emits structure-valid prose
  that honours a title and word target so the real gates can run. Used by
  `--dry-run` and the smoke test.
- **harness** — NO API KEY. The engine gets prose from the Claude Code session
  that is running it, via a disk handshake. This is the "just works inside Claude
  Code, keyless" path, and the recommended way to run for real in-session.

### Running inside Claude Code, keyless (the harness bridge)

Inside Claude Code the model is not missing: the session IS the model. So under
`--backend harness` the engine becomes the conductor and the session the
performer. At each draft the engine:

1. writes `_engine/bridge/<unit>.request.json` (system + prompt + the exact gates
   the output must pass) and `_engine/NEXT.md` (a one-line writing order),
2. prints the order and exits with code 3 (a PAUSE, not a failure).

The session reads the request, writes the finished chapter markdown to
`_engine/bridge/<unit>.response.md`, and re-runs the engine (same command). The
engine GATES that prose with its own gates (H1 == title, word count, no em-dash,
no blacklist) and either places it into `manuscript/current/` and advances, or
re-emits the request with the failing gate as feedback and asks for a rewrite
(bounded to 3 attempts, then a hard-stop). No key, no cost beyond the session.

Because all state is on disk, this also makes the engine the durable brain across
compaction: a fresh or just-compacted session re-runs the engine and is told
exactly what to write next. The session is renewable hands; the engine remembers.

```bash
python _tools/engine.py --config book_workspace/<slug>/book_config.json --backend harness
# -> exits 3 with a writing order; write the response file; re-run; repeat to done.
```

## Verifying the machine without a book run

```bash
python _tools/engine_smoketest.py
```

Builds a tiny synthetic 2-chapter book, drives it with the mock backend through
the real gates, and asserts: **A** a cold run drafts+lints+assembles; **B**
re-running is idempotent (every stage skips); **C** deleting a finished chapter
forces a re-derive-from-disk re-run of exactly that unit; **D** an unpassable
gate hard-stops loudly and writes `HARDSTOP.json`; **E** the keyless harness draft
bridge; **F** the SEED architect stage (a brief with no seed.md/units becomes
`seed.md` + units + per-unit contracts under GATE-2, idempotent on resume, config
schema-valid); **G** the INGEST stage (intake docs become relational digests + a
manifest under GATE-1); **H** the keyless architect turn (the seed plan fulfilled
over the disk bridge). No network, no key, no Word.

## What is proven vs. what a real run adds

The smoke test + a real-book `verify` stage run prove the whole mechanical spine:
drive, idempotent resume, crash/drift recovery, hard-stop, and the real gate
subprocesses. A real one-shot adds only the two things a test should not burn:
live model prose (a real backend + key) and the Word-COM interior rebuild in
`produce`. Both are thin wrappers over tools verified elsewhere in the kit.
