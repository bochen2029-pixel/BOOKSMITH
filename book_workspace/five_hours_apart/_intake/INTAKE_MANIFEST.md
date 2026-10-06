# INTAKE MANIFEST — drop of 2026-10-06 (GATE-0)

*Anchored: 2026-10-06 20:02 UTC (Tuesday). Boot mode: INIT (a populated `intake/` with no matching workspace).
Branch `claude/friendly-cray-6g8fpb`, drop committed as `f128218 Add files via upload`. Every file below was sized
with `_tools/estimate_tokens.py` before reading; nothing over 8K tokens was read in one piece.*

## What the drop is

Two things arrived together, and they belong together:

1. **A book to translate.** `five-hours-apart.md` (the CORE), a 13,462-word short story in three parts, plus its own
   PDF export. The operator's order: translate it, at the highest quality, into Chinese; the kit's translation skill
   frames that as a zh-Hant-TW edition first, then a zh-Hans sibling derived from it.
2. **The machinery for exactly that.** The translation method (v3), its dispatch skill, the worked re-sync example
   and a snapshot of `_tools/` carrying the generic translation tools the method names.

The two KELVIN documents are satellites of the story, not a separate book: the story's underground machine
("knots", "rent", "carve", "settle", "quiet", "frontier", "lane", "ORGAN") is the spec's vocabulary in fiction.
They are canon for the technical layer of the translation key.

**Integration question:** answered by the drop itself. This is not synthesis, anthology or reforge of a new book;
it is a translation of a finished text (`BOOK_TRANSLATION_METHOD_v3.md` §6.1 fresh edition, then §6.2 sibling
locale). `integration_mode` is recorded as `n/a (translation)` in the English workspace config.

## The nine items

| # | file | bytes | ~tokens | class (KIT_ARCHITECTURE §b seven classes) | read | disposition |
|---|---|---|---|---|---|---|
| 1 | `five-hours-apart.md` | 73,017 | 18.2K | **master spec = the CORE** (the finished manuscript) | in full, twice; Part Three and ch. XII three times | frozen as the source of record → `manuscript/current/` (22 units) + `_translation/segments.jsonl` |
| 2 | `five-hours-apart.pdf` | 483,803 | (67 pp, 432×648 pt = 6×9 in, producer pypdf) | **duplicate of #1** (a prior export) | first two pages + word count | DUPLICATE FLAGGED: 13,522 words vs 13,462 in the .md (the PDF adds a "DALLAS · THE LAST WEEK OF OCTOBER" line and running furniture). The .md wins; the PDF is kept as evidence of the intended trim |
| 3 | `BOOK_TRANSLATION_METHOD_v3.md` | 37,307 | 9.2K | **command-contract** (the procedure) | in full, two slices | installed at `docs/BOOK_TRANSLATION_METHOD_v3.md` (the path the skill cites) |
| 4 | `SKILL.md` (`translate-book`) | 3,751 | 0.9K | **command-contract** (dispatch) | in full | installed at `.claude/skills/translate-book/SKILL.md` |
| 5 | `translation_resync_2026-10-06.zip` | 35,107 | 21 files, 77 KB | **exemplars / tooling** (worked example, verbatim one-off scripts) | README in full; scripts listed | extracted to `docs/examples/translation_resync_2026-10-06/` (the path the method cites) |
| 6 | `_tools.zip` | 4,449,938 | 705 files, 15.4 MB unpacked | **tooling** (a snapshot of the kit's `_tools/` from the operator's machine) | listed, diffed against the repo (below) | the 9 new tools installed into `_tools/`; the rest NOT installed (see below) |
| 7 | `KELVIN_THE-KOSTERLITZ-MIND_SPEC_v1.0_2026-09-24_OPUS5-5.md` | 55,931 | 13.9K | **canon / soul doc** (satellite: the field's vocabulary) | §2–§9 in full (the medium, concepts, learning, reach, tape, self, organs, instruction set) | relational digest in `canon_refs/_digest_kelvin_spec.md`; registry rows for every row kind |
| 8 | `KELVIN_NATIVE_AN-ALIVE-MIND-FOR-THE-SILICON-WE-HAVE_NOTE_v0.3_2026-09-25_OPUS5-5.md` | 42,351 | 10.6K | **canon / soul doc** (satellite) | head + §9 Crystallization + §10 in full | digest in `canon_refs/_digest_kelvin_note.md` ("melt", "regrow", turnover, "quiet is not sleep") |
| 9 | `README_DROP_ZONE.md` | 973 | 0.2K | kit furniture (not part of the drop) | in full | stays |

No huge raw logs and no opaque research returns are in the drop. No image, audio or video.

## `_tools.zip` against the repository's `_tools/`

- 82 tracked files in the repo; all 82 are in the zip. 70 are byte-identical; `cover_compose_yha.py` differs only
  by CRLF; **12 differ in content and the zip is newer in every case**: `book_config.schema.json` (+145 lines:
  `title_lines`, `author_file_as`, `publication_date`, `digital_pdf`, `hyphenate`, `caption`, `part_title_break`,
  `label_cjk_nobreak_max`, `allow_interruption_dash`, …), `build_digital_pdf.py` (+442), `build_epub.py` (+294),
  `composite_cover.py` (+467), `docx_to_pdf.py` (+249), `generate_book.js` (+830), `generate_kindle.js` (+194),
  `kdp_precheck.py` (+20), `lint_manuscript.py` (+19), `regression_fixtures.py` (+1463), `scan_manuscript.py`
  (+10). **Not applied**: that is a kit upgrade, not part of a translation; it is D-row D3 for the operator.
- **New in the zip and installed** (the generic tools v3 §18 names, plus two it does not): `docx_delta.py`,
  `docx_figures.py`, `segment_peek.py`, `unit_patch.py`, `add_unit.py`, `pdf_spot_pages.py`, `word_sweep.py`,
  `kindle_ready.py`, `cover_compose_drdj.py`.
- **New in the zip and NOT installed**: `_fixplan/A…I.md` (nine kit-maintenance fix plans), `kit_env.json` (the
  operator's machine file: Windows paths, no secrets; the repo ships `kit_env.template.json`),
  `lint_manuscript.py.pre-boundaries` (a backup), `_engine/calls/` (empty), `node_modules/` (469 files, vendored
  deps), `__pycache__/`, and three `chunker/_*_chunks/` outputs (the operator's KEEL and Marrow-L1 memory
  transcripts, 414K/166K/314K tokens; other projects, personal, never part of this book's corpus).
- Secret scan of the zip's `kit_env.json`: only `api_key_env` (an environment-variable NAME); no key material.

## Strays outside the drop

None belong to this book. `book_workspace/testvoyage/` is the kit's own pipeline-validation book. No kit-root
`FIVE_HOURS_APART_*` files; no chunker outputs for the story.

## Reconciled canon set

- **Source of record:** `five-hours-apart.md` (sha256 in `_translation/P0_REPORT.json`).
- **Vocabulary canon for the technical layer:** KELVIN spec v1.0 §2.4 (defects, virtual pairs vs concepts), §2.7
  (lanes: SENSORY / CLOCK / ORGAN / READOUT), §3.2 (rent in bits), §4.3 (only consequences carve), §5.4 (quiet),
  §6.2 (row kinds: drive, nucleate, annihilate, pin, unpin, settle, fork, join, discard, carve, verdict, quiet, wake,
  stir), §7 (frontier = active tiles; free-vortex density = confusion), §9 (the instruction set: REWIND, FORK,
  COMMIT…); note v0.3 §9 (melt / regrow, turnover, "quiet is not sleep and not death" lineage).
- **Procedure:** method v3 (§6.1, §6.2, §7, §8.4, §10, §12, §15, §16, §17) and the skill's standing rules.
- Nothing is superseded or merged: there is one version of each document.

## Gate-0 verdict

Intake manifest: this file. Every file classified: yes (9/9). Duplicates flagged: yes (#2 of #1; the 12 newer tool
files). Blind reads over 8K tokens: none.
