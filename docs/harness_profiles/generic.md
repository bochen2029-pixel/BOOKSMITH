# Harness profile — GENERIC (any unknown harness)

*You are running BOOKSMITH under a harness the kit has not been told about. Everything still
works: the engine and the ledger are plain disk files. The ONE thing you must re-derive is
where THIS harness records the session transcript, so compaction survival can rehydrate at
high fidelity. That is the nonce protocol below.*

## What already works with zero adaptation
- `_tools/engine.py` — the deterministic pipeline; all state in `_engine/state.json` on disk,
  resumable after any interruption with zero orientation.
- `book_workspace/<slug>/_CONTINUITY.md` — the curated resume ledger (rewritten per chapter).
- Every gate script (`verify_build.py`, `lint_manuscript.py`, `authorial_act.py`, `check_part_pages.py`, …).
- The model seam: set `kit_env.model.backend` to `anthropic` or `openai` (a local server),
  or, if your harness IS the model, drive the engine with `--backend harness` (keyless).

## The nonce protocol — find your transcript
Rehydration (`_tools/rehydrate.py`) needs the session record. To locate it without knowing
your harness's storage format:

1. **Emit a nonce.** Print a unique, greppable string in your output right now, e.g.
   `BOOKSMITH-NONCE-<8 random chars>`. Vary it per session; never reuse one.
2. **Find who recorded it.**

       python _tools/harness_detect.py --find-transcript --nonce "BOOKSMITH-NONCE-…"

   It content-searches the likely session-store roots (home config dirs + the cwd) for that
   string. The newest file that contains it is your transcript. Add `--root DIR` if your
   harness stores sessions somewhere unusual.
3. **Rehydrate from it.**

       python _tools/rehydrate.py --workspace book_workspace/<slug> --session <that file>

   rehydrate.py tiers the content to your token budget (strip-thinking → +no-tools →
   +tail-turns). If the format is exotic (not jsonl/json/md), read the located file directly
   and extract the readable user/assistant turns; the tiering logic still helps you trim.
4. **If nothing is found**, the harness may not persist a searchable transcript. Then the
   `_CONTINUITY.md` ledger IS your memory: read it in full (its RESUME PROTOCOL is at the
   top), then `seed.md` and the last completed chapter, and continue. Keep the ledger
   ruthlessly current so this fallback always suffices.

## Standing discipline on an unknown harness
- Write every chapter to disk the instant it is done; rewrite `_CONTINUITY.md` immediately
  after. This is what makes a compaction or a fresh session lose nothing.
- Fan-out: if your harness has a sub-agent / task mechanism, use it for source digestion and
  audits (one model tier down). If it does not, run those passes inline in the main loop.
- There are no harness-specific hooks here — you are the hook. Re-run the nonce protocol
  whenever you suspect a compaction happened and you need the verbatim record.
- Prefer the deterministic engine (`engine.py`) over free-form driving: it turns "remember to
  do X" into "the code does X and gates it," which is the same on every harness.
