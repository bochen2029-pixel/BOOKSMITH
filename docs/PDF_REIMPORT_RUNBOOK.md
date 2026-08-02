# PDF → KDP formats — the re-import runbook

**Goal:** someone hands you a *finished* book as a PDF, and you want BOOKSMITH to re-issue it
to Amazon's exact specs — a reflowable **Kindle** ebook, an **EPUB**, a KDP **paperback**, a
KDP **hardcover**, and a **digital PDF**. Each of those is a genuinely different build; BOOKSMITH
already knows how to make all five. The only missing piece was turning an arbitrary finished PDF
*back into* a clean manuscript the kit can produce from. That is `_tools/pdf_to_book.py`.

**The one idea:** extract the *content*, discard the source *layout*. A finished PDF is already
typeset in its own trim, margins, running heads, and page numbers. We keep only the text and its
chapter structure, then RE-typeset to each KDP target. This is also why one manuscript can feed
both reflowable ebooks and print — the manuscript must be layout-free, and the producers add each
format's layout.

---

## Step 1 — decompose the PDF into a workspace

```
python _tools/pdf_to_book.py "path\to\finished_book.pdf" --slug my_book \
    [--title "Real Title"] [--author "Real Author"] [--trim 6x9] [--is-fiction]
```
It writes `book_workspace/my_book/` with:
- `manuscript/current/<id>_current.md` — one clean unit per chapter (H1 + reflowed paragraphs),
- `book_config.json` — a **schema-valid** seed (title/author/trim/units/formats/cover/voice),
- and prints the proposed chapter split for review.

What it does under the hood: fitz block extraction → strip running heads/feet + page numbers →
de-hyphenate + reflow → **collapse letter-spaced titles** (`C H A P T E R  O N E` → `CHAPTER ONE`)
→ detect chapters (keyword or font size, TOC-aware) → drop the source title/copyright/contents
pages (BOOKSMITH regenerates them to spec) and capture the dedication/epigraph → snap the page
size to the nearest standard KDP trim → emit.

## Step 2 — REVIEW (the tool stops here on purpose)

Heading detection is heuristic. Open `book_workspace/my_book/book_config.json` and check:
- **Unit split** — are the chapters right? (front/back matter separated from body?)
- **Titles** — they come out UPPERCASE as rendered; retitle if you want mixed case.
- **title / author / trim / is_fiction** — set anything the tool marked "Unknown"/"REVIEW".
- **dedication / epigraph / readers_note** — captured front matter; move between fields if needed
  (epigraph is an object `{text, attribution}`).
- **cover** — supply the source cover art into `cover_art/`, or leave the prompt for a fresh one.

## Step 3 — produce the five formats (each a distinct build)

```
python _tools/produce_book.py --config book_workspace/my_book/book_config.json \
    --formats kindle,epub,kdp_paperback,kdp_hardcover,digital
```
This runs the proven chain per format: `scan → lint → assemble → generate → inject mirror/vAlign
(print only) → render PDF (Word COM) → verify_build`. Outputs land in `book_workspace/my_book/outputs/`.
- **kindle / epub** — reflowable, no print concepts (page numbers, rectos, margins stripped).
- **kdp_paperback / kdp_hardcover** — recto chapter starts, mirror margins, spine from the real
  page count; hardcover uses white paper + turn-in + board-add (a byte-identical interior to the paperback).
- **digital** — front+back cover + blank-stripped interior.

---

## Known limitations (v1)

- **Scanned / image-only PDFs need OCR** — detected and reported, not crashed. OCR is not wired.
- **Heading detection is heuristic, but cross-checked against the book's own table of contents**
  (the PDF bookmark outline *and* the printed Contents page). So chapters that are neither
  keyworded ("Chapter N") nor set in a larger font are still recovered *when the book has a TOC*
  (`toc_openers_marked` in the report shows how many were caught this way). Only a book with none
  of the three signals — keyword, larger font, TOC — may under-split; the report warns when <2
  units. Always glance at the split.
- **Titles render UPPERCASE** (as the source displayed them). Retitle in the config for mixed case.
- **Cover** is not auto-extracted — supply the source art or generate fresh.
- **Fidelity is to the text, not the source's page design** — that is the point.

Regression guard: `python _tools/pdf_to_book.py --selftest` synthesizes a tiny letter-spaced PDF
and round-trips it (guards the letter-spacing + front-matter-drop + schema bugs found on 2026-07-22).

---

## Step 2b — when the auto-split is WRONG: rebuild from the printed TOC (the escape hatch)

Heading detection can still **over-split** a book whose Contents uses TAB leaders (not dots) and
whose chapter titles are running FOOTERS at body-ish size — you get bogus "chapters" that are
really TOC entries (a title ending in a page number, e.g. `… Quantitative Funds? 226`),
mid-paragraph fragments, and TOC/body duplicates. If the split is polluted, **do not produce.**
Rebuild it deterministically from the book's own Contents:

1. Read the book's printed **Contents**: capture `(chapter title, printed start page)` for every unit.
2. Verify the mapping on 2–3 chapters: **printed page number == the PDF's physical `## Page N`**
   (true when front matter is unnumbered-then-restarts at 1; check it). Then each
   `chapter K = pages[start_K … start_{K+1})`.
3. Segment the clean page-marked text by those ranges, reusing `pdf_to_book`'s own
   `extract / running_furniture / is_furniture / dehyphenate`; strip the per-chapter running-foot
   title by position + title-match; prepend the clean `# Title`.
4. Build the config with `pdf_to_book.build_config` + `scaffold` (schema-valid, `no_em_dashes:false`),
   then continue at Step 3. Worked example: `book_workspace/value_investing_en/` (43 chapters
   recovered from 107 bogus units, 2026-07-22 — `REIMPORT_SUMMARY.md`).

## Gotchas learned (2026-07-22, value_investing_en) — see LESSONS_LEDGER §20.1

- **`produce_book.py` is partial** (no `kdp_paperback`/`epub` branch). For the full five formats,
  drive the §12 individual tools directly (`generate_book.js` / `generate_kindle.js` /
  `build_epub.py` / `build_digital_pdf.py` / `composite_cover.py` / `verify_build.py`).
- **De-hyphenation now spans block/page breaks** (soft-hyphen EOL→hyphen + reflow-repair on
  non-terminal-punctuation) — coded in `pdf_to_book`.
- **Author NAME CANON:** set `book_config.author` from memory `author-name-ben-jin.md` (**Ben Jin**,
  not "Jin Bing"); scan produced PDFs for the wrong form (must be 0).
- **Cover:** back blurb ← `kdp_metadata.description`; gold refrain ← `voice.greenlist[0]` (≤40 chars);
  start ComfyUI manually (`C:\FERRYMAN\imagehead\start_comfyui.cmd`) then `cover_gen.py … --no-launch`.
