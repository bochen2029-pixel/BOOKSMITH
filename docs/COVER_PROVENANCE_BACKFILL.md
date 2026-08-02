# Cover-art provenance — backfill guide

*Created 2026-07-31 as part of finishing the cover-provenance node.
**Amended 2026-08-02** after a six-lane review found the original version would have
told an operator to destroy good covers, including a published one. Read
`docs/LESSONS_LEDGER.md` §20.3 first — it is the why. This file is the what-to-do.*

## ⛔ READ THIS BEFORE YOU REMEDIATE ANYTHING

**Failing the gate does NOT mean the cover is bad.** The gate fails whenever it cannot
*prove* how the art was made. Most red books have perfectly good, deliberate covers that
simply never recorded a method. Regenerating those destroys correct work.

**Never run Option A on:**
- a **published** book (its cover is unrecallable — see the census below),
- a book with **deliberate procedural/PIL art** (`gate_and_ledger`),
- a book with **bespoke or author-supplied art** (`Carlquist`, and the two published books),
- any book you have not individually confirmed is a genuine silent-fallback victim.

The original version of this file made exactly this mistake: it listed
`gate_and_ledger` as a fallback victim and recommended regeneration, and it described
the affected set as "unpublished v1.0 builds" while both published books sat in the
gate's red set. Both errors are corrected below.

## What happened

For months `cover_gen.py` could only start ComfyUI via `comfy launch` (comfy-cli),
which is not on PATH here. When that failed, `engine.py` fell through to
`cover_pick.py` and shipped a **hypergen** procedural cover where the book's
`book_config.cover.art` specified **SDXL**. No gate went red: `hypergen.py` makes
*tasteful* abstract art, so it passed the `vision_verify` perceptual rubric that was
supposed to catch placeholders. **A fallback that degrades provenance without
degrading appearance is invisible to a perceptual check.**

Fixed (2026-07-31): `cover_gen.py` now launches ComfyUI Desktop's `main.py` directly
(no comfy-cli needed) **and** writes `cover_art/<slug>_src.provenance.json` on every
generation; `cover_pick.py` writes `method: hypergen|catalog`; and
`verify_build.py :: check_cover_art_provenance` **fails closed** unless a sidecar
proves `method: sdxl` (or the book declares a non-generated `cover.art.method`).

## Genuinely affected books (silent-fallback victims)

| slug | evidence |
|---|---|
| `governed_practice` | shipped art byte-identical to its own hypergen candidate |
| `last_mile` | shipped art byte-identical to its own hypergen candidate; its VERDICT json records `provenance: hypergen.py --style geometric --seed 7` |
| `openworker` | src.png present, 0 provenance, config specifies SDXL |

**`gate_and_ledger` is NOT affected — do not remediate it.** Its cover is deliberate
procedural PIL art. `cover_art/COVER_BUILD_NOTES.md` documents the choice, it ships its
own deterministic generators (`make_art.py`, `make_mark.py`), and
`docs/cover_pipeline.md` sanctions an all-PIL cover explicitly for text-forward books.
It fails the gate only because it never declared a method. It needs **Option B**, and it
was wrongly listed as a victim in the original version of this file.

## The rest of the red set is mostly undeclared, not damaged

The gate treats `cover.art.prompt_seed` alone as intent-to-generate, and nearly every
config inherits a `prompt_seed` from the template. That makes most of the corpus red
for a bookkeeping reason rather than a real one. **Both published books
(`a_human_still_signs`, `your_hermes_agent`) are red this way**: they set `prompt_seed`
but no `checkpoint` and no `workflow`, and their covers came from bespoke compositors
(`cover_compose_ahss.py`, `cover_compose_yha.py`) that never promised SDXL. They need
**Option B**, never Option A.

Check gate status for a book (note `--final`: the provenance gate is enforced on the
final sweep, because the cover stage runs *after* produce):

```bash
python _tools/verify_build.py --config "book_workspace/<slug>/book_config.json" --format kindle --final 2>/dev/null | grep -i cover_art_provenance
```

## Remediation — pick ONE per book

**Option A — regenerate the real SDXL cover.** *Only for a confirmed silent-fallback
victim that is unpublished.* The launcher is fixed, so this now produces genuine SDXL
art AND writes the provenance sidecar. Then recomposite the wrap/ebook cover and
re-verify (an interior-unchanged cover swap):

```bash
python _tools/cover_gen.py --config book_workspace/<slug>/book_config.json \
    --out book_workspace/<slug>/cover_art/<slug>_src.png
# then recomposite every profile the book ships + re-run its gates (see §12 build order)
```

**Option B — keep the existing art, declare it.** The correct path for every book whose
cover is deliberate: bespoke, author-supplied, procedural, catalog, or a hypergen cover
you have decided to keep. Record the truth in
`book_workspace/<slug>/book_config.json`:

```json
"cover": { "art": { "method": "bespoke",
  "_method_note": "hand-composited by cover_compose_<x>.py; never AI-generated." } }
```

Valid values: `bespoke` · `supplied` · `catalog` · `hypergen`. The gate then passes by
declaration. (Do **not** declare `sdxl` for art that was not SDXL — that reintroduces
the exact lie the gate exists to catch. A declaration is a claim you are signing.)

## Verify the fix held

```bash
python _tools/verify_build.py --config book_workspace/<slug>/book_config.json --format <fmt> --final
# cover_art_provenance -> PASS  (either "confirmed by provenance sidecar (methods: sdxl)"
#                                 or "satisfied by declaration")
```

## Known gaps in the gate

Recorded so nobody mistakes a green for a proof. **Closed 2026-08-02 (QC session):**
- ~~The gate reads only the sidecar's `method` field and never opens the art file.~~
  **SHA-BIND landed:** a generative (`sdxl`/`flux`) sidecar is proof only if its
  `art_sha256` equals the sha256 of its named `art_file` on disk; a sidecar without
  those fields is unverifiable-not-proof; a `cover_meta.json` recording a different
  art hash than every verified sidecar FAILs as a stale wrap (§11 cascade). Proven
  by the standing must-fail battery `verify_build.py --selftest` (13 cases, run by
  `selfcheck.py` on every invocation).
- ~~`cover_gen.py --batch` writes no sidecar.~~ `do_batch` now writes one per
  produced image (with each run's seed where the runner reports it).
- ~~A FLUX run records `method: "sdxl"` (hardcoded literal).~~ The method is now
  derived from the workflow actually used; the gate accepts `sdxl` and `flux` as
  generated-proof.

**Still open:**
- `wants_generated` keys off `prompt_seed`, which nearly every config inherits — the
  source of most of the original false red. After the 2026-08-02 method declarations
  + verified backfills this only affects fixture/stub workspaces
  (`_enginetest`, `proof_oneshot`); deliberately deferred (RECONCILE open item 2 —
  if changed, ship the subject-set diff).
- The bespoke compositors (`cover_compose_{ahss,yha,drdj}.py`, `cover_art_carlquist.py`)
  write no sidecar; their books pass by config declaration instead (C-5's completion).
