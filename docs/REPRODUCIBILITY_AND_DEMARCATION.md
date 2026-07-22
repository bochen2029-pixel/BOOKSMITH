# Reproducibility and the demarcation: what is scripted vs what needs a mind

*Written 2026-07-14 for the question "if I add more content later, how much of this is deterministic/programmatic versus needing a model's context-window judgment?" This is the map of that seam, the list of every script that holds a deterministic step, and the one command that regenerates all outputs.*

## The one-sentence answer

**Everything from "approved markdown on disk" to "finished, gated PDFs" is deterministic and scripted. Everything from "intent" to "approved markdown" needs a mind.** The hand-off artifact between the two halves is the manuscript: `manuscript/current/<id>_current.md` (the prose), `book_config.json` (order, titles, front-matter reader's note, metadata), `cover_art/back_copy.json` (back-cover text), and `cover_art/illustrations/live/*.png` (the art). Once those exist and pass the gates, production is a button. A model's context window is needed to *produce* those artifacts and to *diagnose a red gate*; it is not needed to *run the pipeline*.

## The lifecycle, step by step

Legend: **MIND** = needs a model's judgment/context (not scriptable). **GATE** = deterministic check a mind's output must pass. **SCRIPT** = fully deterministic, reproducible, no judgment.

| Step | Kind | Held by | Where |
|---|---|---|---|
| Decide what to add and where (chapter vs addendum vs foreword; placement) | MIND | model + operator | — |
| Write the prose (voice, firewall nuance, the illusion of one author) | MIND | model / writer session | — |
| Install prose as a unit + add to `units[]` at a position | MIND (trivial) + SCRIPTABLE | `new_unit` pattern below | config + `manuscript/current/` |
| Packaging invariants (encoding, one H1 = title, no `##`, no dashes, no tables/lists, no placeholders, word band) | GATE | `scan_manuscript.py` | `_tools/` |
| Corruption + blacklist + em-dash gate | GATE | `lint_manuscript.py` | `_tools/` |
| Stitch units into the one version-pinned master | SCRIPT | `assemble_manuscript.py` | `_tools/` |
| Brief each illustration (what it depicts) | MIND | model (from chapter gist) | `cover_art/illustrations/briefs.json` |
| Generate illustration candidates (SDXL) | SCRIPT (stochastic per seed) | `illustrations_gen.py` + ComfyUI | `_tools/` |
| Pick the best candidate | MIND (perceptual) or heuristic | `illustrations_gen.py --pick` (ink heuristic) | `_tools/` |
| Interior DOCX (print) / Kindle DOCX / EPUB | SCRIPT | `generate_book.js` / `generate_kindle.js` / `build_epub.py` | `_tools/` |
| Mirror margins + even/odd headers, front-matter vAlign | SCRIPT | `inject_mirror_margins.js` / `inject_front_matter_valign.js` | `_tools/` |
| DOCX → PDF + authoritative page count | SCRIPT | `docx_to_pdf.py` (Word COM) | `_tools/` |
| Recto parity (every unit starts odd) | GATE | `check_part_pages.py` | `_tools/` |
| Compose the cover typography at exact geometry from the page count | SCRIPT | `cover_compose_ahss.py` (this book's bespoke design) or `composite_cover.py` (house) | `_tools/` |
| Design a NEW cover, or judge one perceptually | MIND | model + `vision_verify.py` | — / `_tools/` |
| Mechanical build gate per format (mirror flags, empty headers, recto, page-multiple, spine dims, parity) | GATE | `verify_build.py --format F --final` | `_tools/` |
| Digital + website PDF assembly (front/back/interior, blank-strip) | SCRIPT | `produce_book.py` (folded in) | `_tools/` |
| Run the WHOLE chain for every format in order | SCRIPT | **`produce_book.py`** | `_tools/` |
| Diagnose a gate failure and decide the fix | MIND | model (against `docs/LESSONS_LEDGER.md`) | — |
| Translate the prose | MIND (per unit) | model fan-out + `translation/glossary.json` | `translation/` |
| Translation consistency (terms, refrain law, structure) | GATE | `translation/check_consistency.py` | `translation/` |

## The scripts that hold the deterministic half (what / where)

All live in `_tools/` unless noted. These are the reproducibility surface; given the hand-off artifacts, they regenerate every output with no model in the loop.

- **`scan_manuscript.py`** — packaging + placeholder gate (NEW 2026-07-14). The structural checks that used to be by-hand PowerShell.
- **`lint_manuscript.py`** — corruption, blacklist, hard em-dash gate.
- **`assemble_manuscript.py`** — the anti-drift keystone: stitches `manuscript/current/` → `outputs/markdown/<slug>_vN.md`, the single source every generator reads.
- **`generate_book.js`** — print interior DOCX per format (also injects the chapter illustrations from `cover_art/illustrations/live/`).
- **`generate_kindle.js`** — reflowable Kindle DOCX. **`build_epub.py`** — EPUB 3.
- **`inject_mirror_margins.js`**, **`inject_front_matter_valign.js`** — the XML injections (idempotent).
- **`docx_to_pdf.py`** — Word-COM render + page count (the only page-faithful path).
- **`check_part_pages.py`** — recto parity. **`verify_build.py`** — the mechanical build gate. **`vision_verify.py`** — the perceptual gate.
- **`cover_compose_ahss.py`** — this book's bespoke cover compositor (front/back/spine, exact fitz MediaBox, geometry from `preset_lookup`). **`composite_cover.py`** — the house compositor for AI-art covers.
- **`illustrations_gen.py`** — the SDXL illustration batch driver (briefs → candidates → pick → `live/`).
- **`produce_book.py`** — the orchestrator that runs all of the above in order per format (NEW 2026-07-14).
- **`translation/glossary.json` + `SUBAGENT_PROMPT.md` + `check_consistency.py`** — the translation kit: shared term map, per-unit prompt, and the mechanical consistency gate.

## How to regenerate everything (the button)

After any content change to `manuscript/current/` or `book_config.json`:

```
python _tools/produce_book.py --config book_workspace/<slug>/book_config.json \
    --formats kdp_hardcover,kindle,digital,website
```

That runs: `scan_manuscript` + `lint` (halt on red) → `assemble` → for each print format `generate → inject mirror → inject vAlign → docx_to_pdf → cover_compose → verify --final` → Kindle → digital + website PDFs, and prints a per-format verify summary. Add `--dry-run` to see the exact command chain without executing, `--skip-lint` for a translated edition (its own gate is `check_consistency.py`), `--formats mixam_hardcover` to add the Mixam set. Any red gate makes it exit nonzero; it never papers over a failure.

The whole pipeline is also self-checkable: `python _tools/selfcheck.py` proves every tool compiles, JSON validates, docs reference every script, and fonts are vendored; `python _tools/regression_fixtures.py` proves the generators still render historically-defective inputs correctly.

## What a mind must still do, and why it cannot be scripted

1. **Author the prose.** The book's whole thesis is that judgment is the scarce thing; writing that reads as one continuous human author is exactly that. A script can gate it (blacklist, dashes, placeholders, structure) but cannot produce it.
2. **Place new content** into the arc (which chapter, addendum, or front matter) without breaking a designed adjacency (e.g. Ch 24's refrain must stay the last line before the colophon).
3. **Brief the illustrations** from each unit's meaning, and **pick** the best candidate perceptually (the ink-coverage heuristic auto-picks a default, but taste is a mind's).
4. **Design or judge a cover**, including re-imaging for a different language's metrics and confirming the barcode zone is clear (perceptual).
5. **Diagnose a red gate**: a gate says *what* failed; deciding the fix (against `docs/LESSONS_LEDGER.md`) is judgment.
6. **Translate**: each unit is a craft act; the glossary makes it consistent and the gate proves it, but the rendering is a mind's.

Everything else is a script named above. The demarcation is stable: push more of the *checking* into gates over time (that is what `scan_manuscript.py` and `check_consistency.py` did), but the *authoring, placement, design, and diagnosis* stay with a mind by their nature.
