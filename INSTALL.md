# BOOKSMITH — Install & First Run

*You received BOOKSMITH as a folder. This page gets you from "unzipped it" to "the kit is writing my book." About ten minutes on a typical machine.*

## What you need

| Requirement | Why | Without it |
|---|---|---|
| **Claude Code** (or a comparable agentic coding harness) | BOOKSMITH is markdown-driven: the session boots on `CLAUDE.md` and runs the whole pipeline | Nothing works — this is the engine |
| **Python 3.10+** | The production toolchain (`_tools/*.py`) | Nothing works |
| **Node 18+** (anything ≥14 works) | The interior DOCX generators | No Kindle or print interiors |
| **Windows + Microsoft Word** | The only page-faithful docx→PDF path (Word COM). Unlocks **Tier 1**: all print formats, authoritative page counts, recto checks, spine math | **Tier 2**: EPUB, Kindle DOCX, digital-from-existing-PDF, cover compositing + verification still work |
| GPU (~8 GB VRAM) + ComfyUI + SDXL checkpoint (~6.5 GB) — *optional* | Local AI cover-**art** generation | Supply your own cover art in the book's `cover_art/`; compositing + verification run everywhere |
| Local llama.cpp vision server — *optional* | $0/token perceptual verification | The harness's own vision verifies instead (this is the default) |

## Setup, in order

1. **Put the folder anywhere.** `C:\BOOKSMITH`, `D:\kits\booksmith`, `~/booksmith` — nothing depends on the location.
2. **Python deps:** `pip install -r requirements.txt`
3. **Node deps:** already vendored in `_tools/node_modules` — nothing to do. (If that folder is absent: `npm install --prefix _tools`.)
4. **Machine config:** copy `_tools/kit_env.template.json` → `_tools/kit_env.json`. The template's defaults are correct for a first run — the optional blocks (cover art gen, local vision, accelerator organs) are simply off until you fill their paths.
5. **Preflight:** `python _tools/doctor.py` — prints PASS/WARN/FAIL per capability plus your tier verdict. Fix anything it flags FAIL; WARNs tell you which optional capability is off and how to enable it.
6. **Fonts (print interiors only):** the interior default is Georgia (ships with Windows). To use a vendored open font instead (EB Garamond, Literata, Crimson Pro, …): install the TTF from `fonts/library/` into your OS so Word can see it, and set `interior.body_font` in your book's `book_config.json`. Cover typography needs no install — the compositor reads the TTFs straight from `fonts/`.

## Your first book

1. Drop into `intake/`:
   - a **gist** — a short plain-language description: what the book is, who it's for, rough length, fiction or nonfiction, register/voice, any hard constraints (a refrain, a title, an ending you'll write yourself);
   - your **source documents** — research, notes, prior writing, voice samples, transcripts. Duplicates and huge raw files are fine; the kit reconciles and chunks.
2. Open Claude Code in the BOOKSMITH folder.
3. Paste: **`Read START_HERE.md in full and follow it exactly.`**
4. Say **`init`**. From there the plain-language commands drive everything: `generate seed` → `generate chapter 1` (or "keep going") → `produce format kdp_paperback` → `generate cover` → `verify` → `export v1.0`.

The one built-in human checkpoint is the final "ship at 90%?" confirm at `export v1.0` — plus any chapters you reserve for your own hand (authorship Class A/B in `book_config.json`).

## Small-context models

On a model with less than a 1M-token window, run chapter-per-session: every chapter is written to disk the instant it's done, `_CONTINUITY.md` tracks exact state, and the rehydration machinery in `docs/COMPACTION_SURVIVAL.md` restores full fidelity across sessions and compactions. The kit is built to survive interruption — lean on it.

## Fast triage

- A tool prints `word_com_unavailable` → you're on Tier 2 (no Word). Produce `epub` / `kindle`; render print PDFs on a Windows+Word machine.
- `generate cover` fails at art generation → no GPU stack configured. Put art in the book's `cover_art/` and rerun — compositing + verification work everywhere.
- Vision verdict FAILs with "server not reachable" → you forced `--backend keel` without a local server. Use the default (`auto`, which falls back to the harness's own vision).
- A production gate fails → the session diagnoses against `docs/LESSONS_LEDGER.md` and retries within bounds; on a hard stop it reports the exact defect and your options.
