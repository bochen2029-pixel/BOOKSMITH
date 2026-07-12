# AGENTS.md — BOOKSMITH, on any harness

*The cross-harness front door. Many agentic harnesses (OpenCode, Cursor, Aider, Codex, …)
read `AGENTS.md` as their instructions file the way Claude Code reads `CLAUDE.md`. This file
boots BOOKSMITH under ANY of them. If you are Claude Code, `CLAUDE.md` is your full contract
and is auto-loaded; this file simply routes a non-Claude harness to the same machine.*

BOOKSMITH turns one intake drop (a gist + source docs) into nine upload-ready book formats
plus a generated, verified cover. It is built to run on any machine, under any capable model,
under any agentic harness. Two facts make that possible:

- **The deterministic engine owns the work.** `_tools/engine.py` holds the plan, the state
  (`_engine/state.json`), and every gate on disk; the model is a pure function it calls. This
  is harness-agnostic by construction — it works the same whether the model is reached via an
  API key, a local server, or the harness's own session (`--backend harness`).
- **State lives on disk, not in context.** `book_workspace/<slug>/_CONTINUITY.md` (rewritten
  after every chapter) and the engine's `state.json` are plain files. Any harness reads them.

## Boot step 0 — identify your harness, load its profile

    python _tools/harness_detect.py --identify

It prints your harness and the profile to read under `docs/harness_profiles/`:

- `claude_code.md` — hooks, `~/.claude` jsonl transcripts, the Agent tool, auto-loaded CLAUDE.md
- `opencode.md` — `AGENTS.md` + `.opencode/command` slash-commands + its own session store
- `cursor.md` — `AGENTS.md` / `.cursorrules` + its own session store
- `generic.md` — **any unknown harness**: the nonce protocol to find your own transcript

## Boot steps 1–3 (every harness)

1. Read `CLAUDE.md` — the full operating contract (boot sequence, plain-language command
   grammar, the two-verifier gate loop, autonomy policy, compaction survival). It is written
   for Claude Code but is ~95% harness-agnostic; wherever it names "the Agent tool" or "the
   `.jsonl` transcript," substitute your harness's equivalent from your profile. Then read
   `KIT_ARCHITECTURE.md` (the invariant spec) and `docs/SUPERSTRUCTURE.md` (the wiring).
2. Run `python _tools/doctor.py` (and `python _tools/autoconfig.py` if `_tools/kit_env.json`
   is missing) to detect this machine's capabilities + tier.
3. Detect mode: a `book_workspace/<slug>/_CONTINUITY.md` with STATUS ≠ COMPLETE means RESUME
   (follow its RESUME PROTOCOL); an empty `intake/` + no workspace means START.

## The two ways to run (both harness-agnostic)

- **Interactive** (the model drives, per CLAUDE.md's command grammar): "write chapter N",
  "generate cover", "export v1.0". The model holds the loop and calls tools.
- **Deterministic engine** (code drives; the model is a pure function):

      python _tools/engine.py --config book_workspace/<slug>/book_config.json --backend harness

  The engine runs INTAKE → EMIT itself, gating every stage, resumable from disk after any
  interruption. `--backend harness` is keyless: it hands each chapter to YOUR session via a
  disk bridge (`_engine/bridge/<unit>.request.json` → you write `<unit>.response.md` → re-run).
  See `docs/ENGINE.md`.

## Compaction / session survival on any harness

BOOKSMITH survives context compaction by rehydrating from the session transcript. On Claude
Code that is the `.jsonl` under `~/.claude/projects/` (hooks pre-bake it). On an unknown
harness, use the **nonce protocol** (`docs/harness_profiles/generic.md`): emit a unique nonce
now, then

    python _tools/harness_detect.py --find-transcript --nonce "<it>"

locates the file your harness is recording into. Worst case, the `_CONTINUITY.md` ledger
alone is enough to resume — it is a plain disk file the kit rewrites after every chapter.

---

*Precedence: `KIT_ARCHITECTURE.md` (invariant) ▸ `CLAUDE.md` (session contract) ▸ this file
(cross-harness adapter) ▸ a per-book `seed.md` (instantiation). This file never overrides the
architecture; it only routes a non-Claude harness to it.*
