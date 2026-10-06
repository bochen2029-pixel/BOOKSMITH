# BOOK TRANSLATION METHOD v3 — the cold-start edition: fresh translation, sibling locale, and re-sync of a shipped edition

*Version 3.0, 2026-10-06. **Supersedes** `docs/BOOK_TRANSLATION_METHOD_v2.md` (2026-09-25), which superseded v1
(2026-08-13) and the run-3 addendum. The three earlier files stay in `docs/` unchanged as the evidence record;
every rule here that was bought with a real failure points at its story (`v1 §n`, `R3-x`, `v2 §n`, or the 2026-10-06
re-sync, "P10/26"). v3 was written right after the first full **P10 re-sync**: both shipped Chinese editions of
Huagang Chen's* Across Borders and Herbaria *were brought up to the author's revised English in one day, by one
moderator session with four Opus ground-truth lanes, without a single question to the author or the operator
(ship report: `book_workspace/across_borders/_translation/_p10_2026-10-06/RESYNC_REPORT_2026-10-06.md`).*

*Lineage: `ROSETTA_TRANSLATION_METHOD.md` (restoration from a target-language corpus) → v1 (charter-locked parallel
translation) → R3 addendum → v2 (key-first, segment-aligned, locale-aware) → **v3** (self-contained runbooks, the
re-sync path, generic tools, the trap table).*

---

## What changed in v3 (read this first if you know v2)

1. **Three cold-start runbooks (§6)**, each a numbered command list a fresh session can execute: a fresh edition
   (EN → zh-Hant-TW), a sibling locale derived from a ratified edition (zh-Hant → zh-Hans), and the **re-sync of a
   shipped edition after the author revises the source** (P10, now a procedure, not a paragraph).
2. **Generic tools in `_tools/`** for the parts of the work that were being re-written by hand each run:
   `docx_delta.py`, `docx_figures.py`, `segment_peek.py`, `unit_patch.py`, `add_unit.py`, `pdf_spot_pages.py`,
   `word_sweep.py` (§18). The per-book implementation that v2 described in prose now has a named reference
   workspace to clone (§7).
3. **The anatomy of a translated-edition workspace (§7)**: where the key, the gate, the production scripts, the
   converter reference and the ledgers live, and which file is the truth at each stage.
4. **Names, privacy and family (§12)** as one policy: Latin unless the source carries characters, never guess, the
   author's own acknowledgements override a privacy fence by ruling (never by deleting the fence), ground truth from
   the family's own books, contradictions reported as source defects.
5. **Translation memory across sibling books (§13)**: paragraphs identical to an already-ratified sibling edition
   reuse the sibling's Chinese, split as this book's English splits, with this book's locked terms where they differ.
6. **The gate exception syntax (§8.4)** in one place: `@except`, `(condition)`, the 12-field locale layer, the
   mentions file, lint waivers, the amendment-row rules, and which of them a cold session is allowed to touch.
7. **Adding a unit to a shipped edition (§11)**: every enumeration that must change, in order.
8. **The trap table (§14)** grew by the re-sync's own catches: the exported heading ornament, DOCX media numbering,
   a lint waiver feeding the font-coverage gate, the leaked Word process, the build that wipes its output folder,
   the continuity gate's unit census, a 破折号 split across a line, the converter overwriting reviewers' edits.
9. **eBook verification recipe (§16)**: how the Kindle DOCX and the EPUB are looked at, not only counted.

Nothing in v2 was weakened. The override licence (source outranks key, worker overrides and flags) still sits above
every mechanism.

## 0. Which document to read

| you want to | read |
|---|---|
| run a translation or a re-sync now | **this file**, then the workspace ledger of the book in hand |
| understand why a rule exists | the pointer it carries (`v1 §n`, `R3-x`, `v2 §n`) in the earlier files |
| restore a book that was synthesized from a target-language corpus | `ROSETTA_TRANSLATION_METHOD.md` |
| see the moves made on a real re-sync, script by script | `docs/examples/translation_resync_2026-10-06/README.md` |

## 1. The problem and the method in one paragraph

A finished book in language A must become a book in language B, or in locale B′ of a language it already exists in,
at literary quality, fast, with parallel workers; and when the author revises A after B has shipped, B must follow
without being retranslated. Fan-out fails three ways (v1 §0): the patchwork, translationese, and silent loss.
**One mind reads the whole source and builds the KEY (a charter of law plus a machine-readable registry); many
hands translate segment-aligned units in parallel under that key; machines enforce the key at segment level; blind
audits catch what confident rereading cannot; the one mind reads the finished book end to end; the segment
alignment keeps the edition true to its source when the source moves; and every text change, however small,
re-runs assemble → build → verify.**

## 2. Roles (v1 §1, v2 §1)

**MODERATOR** holds the entire source; builds the key personally; adjudicates; owns every gate; reads the finished
book. **TRANSLATORS** one per unit, self-sufficient, self-gating, write to disk before returning. **QA WORKERS**: seam
editors, blind back-translation auditors, locale reviewers, asset localizers. **GROUND-TRUTH LANES** (new, P10/26):
read-only agents that hunt names, terms, precedent and pipeline touch points on disk before the moderator writes a
word; they post to the bus and write reports, never prose. **THE BUS** (Intercom) for discovery, never enforcement.
**THE AUTHOR** answers at most four taste questions before ratification and does the final native read; when the
operator rules "no questions", the lanes and the sibling editions answer them instead, and every inference is logged.

## 3. Principles (v2 §2 stands; the additions)

The 22 principles of v2 §2 stand verbatim. v3 adds:

23. **Measure the delta before touching anything.** A revised source is diffed against the artifact the author
    actually edited, found by the lineage test (fewest change groups), never against the markdown master (P10/26:
    7 change groups against the delivered Word edition, 233 against the first delivery).
24. **An exported document carries things that are not the author's text.** The kit's heading ornament, media
    numbered by insertion order, alt texts the kit wrote: strip or resolve them before they become "changes" (§14).
25. **Translate only the delta; reuse everything ratified.** Unchanged segments keep their reviewed translation;
    identical paragraphs in a sibling book keep the sibling's; the converter never re-runs over units a reviewer
    has edited.
26. **A fence is narrowed by a ruling, never deleted.** The privacy regex that guards the narration stays; the
    unit the author wrote himself is exempted by name, and the exemption is logged in the charter.
27. **Every gate that counts units must learn the new count the same hour the unit is added** (§11). A build that
    goes red at stage 50 on `18 != 19` cost twenty-five minutes of Word time each time it happened.
28. **Back up what the build deletes, pin what the packager hashes.** One build wiped its edition's whole output
    folder, including the released package the combined-zip script was pinned to.

## 4. The pipeline at a glance (v2 §3, with P10 made real)

```
P0  SOURCE OF RECORD  identify the artifact the reader bought (or the author edited); extract + segment with stable
                      ids; prove sibling artifacts carry the same text; align to any prior translation (TM);
                      storefront support per format; FREEZE by sha256
P1  GESTALT + KEY     moderator reads everything; harvests sibling editions; censuses; hinge-term test; evidence
                      ladder; author-taste batch (<=4) or, under a no-questions order, the ground-truth lanes;
                      registry + charter + exemplars; generated tables; RATIFY
P2  SCAFFOLD          target workspace (clone the reference edition, §7); localized config + language tags; assets at
                      identical paths; gates generated from the registry; must-fail battery + clean control; packs
P3  WAVES             two waves; wave B reads wave A's finished target text; TM reuse candidates; live rulings
P4  CONSOLIDATE       all workers returned; ledgers parsed; normalizer dry-run -> diffs -> write; promote; gates
P5  QA                seams || blind back-translation || locale reviewer || asset localizers
P6  FULL READ         the moderator reads the whole target book; freeze
P7  PRODUCE           one master -> every format, locale tags, fonts, furniture, covers (one Word job at a time)
P8  VERIFY            mechanical battery + rendered-font check + line-break audit + pages looked at (print, Kindle, EPUB)
P9  SHIP              ship report; open decisions; source-defect register; evidence trail; ledgers COMPLETE
P10 MAINTAIN          the source moved: delta -> back-port -> refreeze -> translate only EDITED/NEW -> gates ->
                      layout re-solve -> rebuild -> package -> ledgers (§6.3)
```

Observed timing: a fresh 42K-word edition ≈ one long day with three context deaths (v2's runs); the sibling locale
≈ one evening; the re-sync of two editions ≈ one day including two full builds of 25 minutes each plus two layout
solves of 10 minutes each.

## 5. Phase details that v2 did not spell out

### P0 — finding the artifact the author edited
1. Run the lineage test: `python _tools/docx_delta.py --docx REVISED.docx --candidates <delivered Word edition>
   <first delivery> <assembled master.md>`. The candidate with the fewest change groups is the base; a diff against
   any other base reports the kit's own later edits as the author's.
2. Run the full delta against that base (`--master BASE --out DIR`). Read `delta_report.md`: every change group in
   document order with word-level detail; `headings_only_in_docx` (a new unit); `consecutive_duplicate_paragraphs`
   (paste slips); `ornament_paragraphs_dropped` (the kit's heading ornament, not text); `docx_meta.json` for the
   alt texts, media list and the docx's creator and creation date.
3. Map the figures in DOCUMENT order: `python _tools/docx_figures.py REVISED.docx --match-dir images/photos`. A
   figure with "NO GOOD MATCH" is new or replaced; its heading and caption say where. Never map `word/media/imageN`
   by number (P10/26: image3 was the fourteenth figure).
4. If a paragraph in the delta already exists elsewhere in the source (grep the segments), it is a duplicate, not
   new text (P10/26: the "new" chapter-1 paragraph was ch_01.041 pasted twice).

### P1 — ground truth without the author
When the operator rules "no questions", fan out read-only lanes with hard token budgets, each with one slice:
**NAMES** (every person in the new text: characters on disk, sibling precedent, the registry's rule, a
recommendation per locale with evidence rung and confidence); **TERMS** (every term, institution, product and title:
the locked form if one exists, else a proposal per locale with evidence); **PRECEDENT** (how the sibling editions
rendered the same kind of material: heading word, register, URL lines, family address; sentence alignment of any
rewritten config string against the delivered translation; the book's photo-privacy convention and a measured crop
box); **PIPELINE** (every enumeration a new unit touches, the rebuild sequence, hard-coded numbers, what the build
deletes). Each lane registers on the bus (`python C:/Intercom/intercom.py join ... --lane GT-NAMES`), writes its
report to `<source ws>/_translation/_p10_<date>/reports/`, and returns a summary. Their reports are data; the
moderator rules. Lanes contradict the brief when the brief is wrong (P10/26: two of four did, correctly).

### P3/P4 — the small-delta case
For a handful of edited segments the "wave" is the moderator: patch each unit positionally with
`_tools/unit_patch.py` (count-asserted, append-only draft, promoted copy refreshed, block count held), gate it,
promote. A new unit is translated fresh under the key, except where §13 applies.

### P7 — production hygiene learned the hard way
- `python _tools/word_sweep.py` before every layout solve and build; `--kill` only when nobody is editing in Word.
- Back up the edition's released package before `build_final_*.py` (one of them wipes `outputs/_FINAL`); restore
  it beside the new package afterwards, and repoint the combined-zip script's path + sha pins.
- One Word job at a time across all workspaces: solve, then build, then the next edition.
- The layout solver depends on the words: re-run `layout_*.py solve --fresh` after any text change, and once more
  if the build's layout gate asks for it.

### P8 — look at the eBooks too (§16)

## 6. Cold-start runbooks

Conventions for every command: `PYTHONUTF8=1`, forward slashes, files written only with Write/Edit (never a shell
literal), `cd` into the edition workspace, one Word job at a time. `WS_EN` is the English workspace, `WS_ZHT` the
Traditional (Taiwan) edition, `WS_ZHS` the Simplified edition.

### 6.1 A fresh edition (EN → zh-Hant-TW), as `across_borders_zht` was made (2026-09-29)

1. **Freeze the source.** In `WS_EN`: `python _translation/extract_source.py` (clone it from
   `book_workspace/across_borders/_translation/extract_source.py` if the book has none; its UNITS tuple is the
   reading order) → `segments.jsonl`, `source_of_record.md`, `P0_REPORT.json`. Record the sha256.
2. **Build the key** (the moderator, personally): read every segment; census candidates (`census.py`); write
   `registry_merged.tsv` (fields `id tier EN zh-Hans zh-Hant first_use count note`) and `translation_charter.md`
   (15 sections, v2 §5.7); ask the author-taste batch or harvest the siblings (§13). Test the key against any
   translation memory (v2 §P1.7). Ratify; the registry version is recorded.
3. **Scaffold the edition.** Copy the reference edition's machinery: `_tools_zht/` (build_key, gate_unit, gate_book,
   heading_table, test_gate, same_content, zht_common with its UNITS list), `_scripts_zht/` (zht_config, promote,
   layout, build_final, cover, charts, fonts, sweeps, final_checks, setup_assets, the package README), the key into
   `_key/` (registry + amendments + census patterns + locale layer), `book_config.json` localized (language
   `zh-Hant-TW`, strings, fonts), `translation/current/config_strings_zht.json` (title, subtitle, author, dedication,
   epigraph, about, description, keywords, copyright). Edit the book-specific constants (title, refrain, UNITS) and
   run `python _tools_zht/build_key.py` then `python _tools_zht/test_gate.py` (the must-fail battery must pass).
   `python _scripts_zht/setup_assets_zht.py` copies the photos byte-identically from `WS_EN/images/photos`.
4. **Waves.** Generate the worker packs (`_generated/slices/<unit>.md`), launch wave A (expository middle) then wave
   B (load-bearing units, reading wave A's finished text), ≤8 at a time, hard budgets. Each worker: pack → draft to
   `translation/drafts/<unit>_v1.md` → ledger → `python _tools_zht/gate_unit.py <unit> <draft> --quiet` to PASS →
   bus → return. Rulings are registry edits + a charter §15 line + `build_key.py` + `test_gate.py`, in one action.
5. **Consolidate.** `python _tools_zht/gate_book.py translation/current` (0 FAIL), seams, blind back-translation,
   locale reviewer, charts redrawn (`make_charts_zht.py`), the moderator's full read.
6. **Produce.** `python _scripts_zht/promote_zht.py --replace` → `python _scripts_zht/layout_zht.py solve --fresh`
   → `python _scripts_zht/build_final_zht.py --version v1` (≈25 min; the log `outputs/_final_build_log.json`;
   verification in `outputs/_verification/`). Vision sets on the rendered pages; fix; rebuild.
7. **Ship.** The package under `outputs/_FINAL/<slug>_v1_<date>/` + zip + sha256; ledger STATUS COMPLETE; ship
   report; open decisions and source defects for the author.

### 6.2 A sibling locale (zh-Hant-TW → zh-Hans), as `across_borders_zhs` was made (2026-09-30)

1. Seed from the canonical zh-Hant workspace (`_tools_zhs/bootstrap_zhs.py` pattern: hash-verified copy into
   `_zht_ref/` of the QA'd text, charter, briefs, notes).
2. Key: the mainland locale layer `_key/locale_layer_zhs.txt` (12 fields: `id | cat | tier | en | tw | first_use |
   hans | forbidden | pattern | conf | evidence | notes`; a plain forbidden form on an H row FAILs and is replaced
   by `hans`; a `(condition)` or an M/L row WARNs) + `registry_amendments_zhs.tsv` + `mentions_zhs.tsv` (sites
   where a Traditional character is MENTIONED, not used). `build_key.py`, `test_gate.py`.
3. Derive, never retranslate: `python _tools_zhs/convert_zhs.py <units> --publish --version 1` (OpenCC `tw2s` at
   character level with masks for labels, Japanese and printed-script quotes, then the registry and lexicon passes;
   `--publish` writes drafts + current). Then the mainland locale reviewers read it whole; blind back-translation of
   the rewritten passages; vision sets.
4. Production as 6.1 with the zhs scripts (`w:eastAsia zh-CN`, EPUB `zh-Hans`, Noto Serif CJK SC). KDP publishes no
   Simplified Chinese: EPUB to Google Play / Apple Books, print via a non-KDP printer.
5. The both-editions zip: `python _tools_zhs/make_both_editions.py <zhs package dir>` (pinned to the zh-Hant
   package path and sha256 at its top).

### 6.3 Re-sync after the author revises the source (P10), as done 2026-10-06

Inputs: the author's revised DOCX; both editions COMPLETE on disk; the English workspace.

1. **Delta and lineage** (§5 P0): `docx_delta.py` (candidates, then full), `docx_figures.py --match-dir`. Copy the
   evidence into `WS_EN/_translation/_p10_<date>/`.
2. **Ground truth** (§5 P1): launch the four lanes; meanwhile do the mechanical work below. Read their reports
   before translating the new text.
3. **Back-port into English** (so the frozen source can move): snapshot versions
   (`_scripts/snapshot_versions.py`); apply each change with `_tools/unit_patch.py --manuscript` (or a one-off
   script with asserts, see the worked example); write the new unit file with one H1 equal to its config title; put
   rewritten config strings in `book_config.json`; add the unit to the config and the extractor's UNITS tuple at the
   author's position (`_tools/add_unit.py`); route the author's em dashes to commas only if the English edition's
   own rule forbids them; waive source-faithful lint hits (URL lines) by exact string in `voice.lint_waivers`.
   Gates: `scan_manuscript.py`, `lint_manuscript.py`, config schema.
4. **Refreeze and re-key**: `python _translation/extract_source.py`; copy `segments.jsonl`, `source_of_record.md`,
   `P0_REPORT.json` into each edition's `_key/` (keep the previous freeze in `_key/_pre_resync_<date>/`); add the
   unit to each gate module's UNITS list; `build_key.py` + `test_gate.py` in each edition. Segment ids do not shift
   unless a paragraph is inserted into an existing unit; if one is, re-key the id-bound exceptions.
5. **Translate the delta.** Edited segments: `unit_patch.py` per edition (zh-Hans derived by hand from the zh-Hant
   change; never `convert_zhs.py --publish` on a shipped unit). Label lines: exactly as the author now prints them.
   New unit: zh-Hant fresh under the key (and §13 for identical sibling paragraphs); zh-Hans through
   `convert_zhs.py <unit> --publish` after the zh-Hant file is copied into `_zht_ref/translation_current/`, then
   locale-reviewed by hand. Rewritten config strings into both `config_strings_*.json` (reuse the delivered sentences
   where the English is unchanged). Gate each unit; `gate_book.py`; rulings as registry edits + charter lines.
6. **Pipeline counts and fences** (§11): EXPECT counts, privacy regexes narrowed by ruling, the continuity ledgers
   naming every unit, lint waivers in the edition configs for the same URL lines (and nothing that is not printed).
7. **Figures**: a replaced photo goes into `WS_EN/_source/Photos/`, gets a `make_figures.py` row with its crop
   (browser chrome and taskbars off, per the book's privacy convention), is built once, and propagated by each
   edition's `setup_assets_*.py` (byte-identical, sha-verified). Captions and alt texts stay the author's unless
   they became false.
8. **Build**: `word_sweep.py`; back up `outputs/_FINAL`; `promote_*.py --replace`; `<ed>_config.py`;
   `final_checks_*.py`; `layout_*.py solve --fresh`; `build_final_*.py --version v<N+1>`; read the RED/WARN lines;
   fix (a 破折号 across a line break is a text fix in that unit; a count is a pipeline fix) and rebuild. Then the
   next edition. Restore the previous package beside the new one; `same_content.py <old pkg> <new pkg>` explains
   every difference; repoint `make_both_editions.py`; build the combined zip.
9. **Look** (§16); **ship** (§P9): ledgers COMPLETE (`check_continuity.py` consistent), report with every number,
   source defects D-rows for the author, memory and the lessons ledger.

## 7. Anatomy of a translated-edition workspace (reference: `book_workspace/across_borders_zht`, `_zhs`)

| path | role | truth at which stage |
|---|---|---|
| `_key/registry_merged.tsv` | the registry (588 rows for this book), columns `id tier EN zh-Hans zh-Hant first_use count note` | law, both locales |
| `_key/registry_amendments_<ed>.tsv` | rulings that win on id; one row per id; `=` means "unchanged cell"; a NEW id needs a full row | law |
| `_key/census_patterns_<ed>.tsv`, `locale_layer_*.txt`, `mentions_zhs.tsv` | census overrides, locale tripwires and lexicon, mentioned-character allowances | law |
| `_key/segments.jsonl`, `source_of_record.md`, `P0_REPORT.json` | the frozen source the gate reads (copies of the English `_translation/`) | source |
| `translation_charter_<ed>.md` | the charter: 15 sections, §11 source defects, §15 amendment log | law |
| `_generated/key_gates.json`, `slices/`, `validation.txt` | written by `build_key.py`; never edited | derived |
| `_tools_<ed>/` | `<ed>_common.py` (UNITS, block cutting, script classes), `build_key.py`, `gate_unit.py`, `gate_book.py`, `heading_table.py`, `test_gate.py` (battery), `same_content.py`; zhs adds `convert_zhs.py`, `bootstrap_zhs.py`, `make_both_editions.py`, `migrate_ws.py` | machinery |
| `translation/current/<unit>.md` + `config_strings_<ed>.json` | **the translation truth** | text |
| `translation/drafts/<unit>_v<N>.md` | append-only history (also the QA snapshots) | history |
| `_zht_ref/translation_current/` (zhs only) | the zh-Hant text the converter reads; refresh it for any unit you convert | converter source |
| `manuscript/current/<unit>_current.md` | written by `promote_<ed>.py --replace`; the build reads it; the layout pass may touch it | build input |
| `_scripts_<ed>/` | `<ed>_config.py` (strings → config, titles from H1), `promote`, `layout` (+ `layout_map_<ed>.json`), `build_final` (≈70 steps), `cover`, `make_charts`, `fonts`, `docx` fixes, `ebooks`, `sweeps`, `final_checks`, `setup_assets`, `restore_print_images`, `PACKAGE_README` | production |
| `images/`, `cover_art/` | byte-identical copies from the English workspace (photos) + redrawn charts + the art plate and vendored fonts | assets |
| `outputs/_FINAL/<slug>_v<N>_<date>/` + `.zip` | the package: Word + reading PDF, EPUB + Kindle DOCX + cover, paperback and hardcover interiors + covers, verification logs, markdown master, README, upload checklist, manifest | deliverable |
| `_CONTINUITY.md` | the ledger: STATUS, a resume protocol, every unit NAMED, the log | state |
| `_qa/`, `_notes/`, `_brief/` | QA reports (READ-1/2, SEAMS, BACKTRANS, vision V1-V7), lane notes, worker briefs | evidence |

## 8. The key (v2 §5 stands) and the exception syntax

### 8.1 Inclusion test, tiers, evidence ladder, exemplars, slices: v2 §5.3-5.6 verbatim.

### 8.2 Registry rows a re-sync adds
New people and institutions enter as full rows (id, tier, EN, both target forms, first_use segment id, count, note)
in the amendment file of each edition; the EN cell is the census pattern (case-insensitive by default; a `=` prefix
in a census override is case-sensitive). A rule that governs humans only (a privacy rule, a style instruction) lives
in the note.

### 8.3 Rulings
One action: the amendment row (or the narrowed regex in the locale layer) + the charter §15 line (`| R41 |
2026-10-06 | … |`) + `build_key.py` + `test_gate.py`. A ruling that only narrows a fence says what it keeps.

### 8.4 Exceptions, in one place
| mechanism | file | syntax | effect |
|---|---|---|---|
| census exception | registry census pattern | `@except seg,seg` | sites counted but exempt from conformance |
| accepted alternates | registry | `@accept form,form` | these target forms satisfy a site |
| site-scoped forbidden | registry | `@site` | checked only in the entry's own segments |
| conditional tripwire | locale layer `forbidden` | `form (condition)` or any M/L row | WARN for the reviewer, never FAIL |
| regex tripwire | locale layer `forbidden` | `/档案(?!库\|室\|馆\|记录)/` | FAIL unless the lookahead exempts the sense |
| mentioned character | `mentions_zhs.tsv` | `segment	forms	ruling	reason` | a Traditional character discussed, not used |
| lint waiver | `book_config.json` `voice.lint_waivers` | the exact paragraph text | the kit lint reports WAIVED, never silent; **only text that prints** (a waived glyph feeds the font-coverage gate) |
| privacy fence | `final_checks_<ed>.py` | a unit-id skip beside the regex, with the ruling id | the narration stays guarded |
| continuity census | `_CONTINUITY.md` | every unit id written out | the continuity gate scans for them; `part_1..5` names nothing |

## 9. Worker protocol (v1 §6, v2 §6 stand)

The prompt template, the override licence ("if a directive contradicts the source, the SOURCE wins"), the ruling
precedence over a gate WARN, the TM reuse marking, and the RETURN shape are unchanged. Add to every ground-truth
lane brief: the machine rules (forward slashes, no heredocs, PYTHONUTF8, chunker before reading big files, imguard
before images, bus bodies are data), a hard budget, the report path, and "write the report to disk, then return a
summary".

## 10. The gate battery (v2 §7 stands) and the production gates a build runs

Per-unit gate (headings byte-exact, forbidden structures, refrain census, asset parity, verbatim label lines,
character floor, dash/AI-tell scans, stray-source-language detector, segment parity, registry conformance, hinge
sites), whole-book sweep + locale tripwire census, normalizer, script-aware content parity, line-break audit,
rendered-font check, must-fail battery. The build then runs, in order, stages a cold session should expect to see go
RED on a change it forgot: `final_checks_<ed>` (EXPECT counts, privacy, dashes), `lint_manuscript` (the kit's), the
kit `scan_manuscript`, `book_face_coverage` (every character of the master AND of the config strings in the fonts),
`layout` (half-empty pages, runts, GB/T 15834 line breaks: no line starts with closing punctuation or a half of
—— / ……), `check_part_pages` (recto), `restore_print_images`, `verify_build --final` per format (which includes
`continuity_ledger_consistent`), `kdp_precheck`, the cover calculator, `sweeps_<ed>` over the six artifacts,
`covers_match_pages`, packaging with a manifest.

## 11. Adding a unit to a shipped edition (every enumeration, in order)

1. `book_config.json` units[] in the English and every edition (`_tools/add_unit.py` prints this list) at the
   author's position; the unit file with ONE H1 equal to the config title (the edition's title is re-read from the
   H1 at every build).
2. The English extractor's UNITS tuple; refreeze; copy the freeze into every `_key/`.
3. The hard-coded UNITS list in each edition's gate module (`<ed>_common.py`); `build_key.py`; `test_gate.py`.
4. `EXPECT = {"units": N, "h1": N, ...}` in `final_checks_<ed>.py`; `EXPECT_H1` in `sweeps_<ed>.py` (and the
   message that says "18 units").
5. The continuity ledger names the new id (and all the others).
6. Any fence written for the narration that the new unit legitimately breaks (§12).
7. The edition's `translation/current/<unit>.md`; `promote --replace`; `layout solve --fresh`; build.

## 12. Names, privacy and family

- A person's name is Latin letters unless the SOURCE carries the characters; never guess characters (book one's
  P21-P25; registry people rule). Ground truth for the author's family exists on this machine (the mother's memoir,
  the father's first book, the genealogy); it is evidence for a recommendation, not a licence to print characters
  the author did not write.
- The author's own acknowledgements override a "never named" privacy fence: narrow the fence to the narration by
  ruling (R41 / ZR54), exempt the unit by name in `final_checks`, keep the registry row, log the contradiction with
  the Note on Names as a source defect.
- Family address is 你 / 你們, never 您 (zero 您 in four shipped editions); daughters-in-law, grandchildren and ranks
  take the sibling edition's forms (媳婦 / 媳妇, 孫兒女 / 孙儿女, Frank Chen 少校, 西點軍校 / 西点军校).
- A diagnosis year, a date, a count in the author's new text is translated as written even when the family's own
  record disagrees; the disagreement is a D-row for the author.

## 13. Translation memory across sibling books

When the new text repeats a paragraph that an already-ratified edition of a sibling book rendered (the family
paragraphs of an acknowledgements section, boilerplate, a shared epigraph), reuse that Chinese verbatim: it was
reviewed by the author's process and the reader of both books sees one voice. Then: split or merge to this book's
paragraph boundaries (segment parity), replace any term this book locks differently (骨幹 not 骨架 where 骨架 is
this book's locked "skeletal record"; 癌症存活者 / 癌症幸存者 where the sibling softened to 康復者), drop sentences
the new English does not have, add the ones it adds, and log the reuse in the charter. The precedent lane finds the
matches (sentence by sentence against the sibling's English); `docs/examples/translation_resync_2026-10-06/` shows
ten of eighteen paragraphs reused this way.

## 14. Failure modes and standing fixes (v1 §9, R3 A-S, v2 §9 stand; the additions)

| failure (observed 2026-10-06) | standing fix |
|---|---|
| The delta was measured against the first delivery and showed 233 groups | lineage test first (`docx_delta.py --candidates`); diff against the file the author edited |
| A "new" paragraph in the docx was an existing segment pasted twice | `consecutive_duplicate_paragraphs` in the delta; grep the segments before calling anything new; keep one; D-row |
| The lone ✦ under the new heading was treated as text: double ornament in print, a scene break in the EPUB, RED at `book_face_coverage` | `docx_delta.py` drops lone-ornament paragraphs; the generators draw the ornament themselves |
| `word/media/image3` was taken for the third figure; it was the fourteenth | `docx_figures.py`: document order through relationship ids; match by pixels, never by number |
| A waiver string `✦` put the glyph back into the characters the fonts must cover | waive only text that prints |
| Word rejected `Repaginate()` and left a WINWORD holding the probe DOCX (EBUSY next run); `taskkill /PID` failed silently | `word_sweep.py --kill` (PowerShell `Stop-Process -Force`); retry the solve |
| `build_final_zht.py` wiped `outputs/_FINAL` including the released v1 zip the combined-zip script was pinned to | back up before building; restore beside the new package; repoint the pins (`update_both_pins.py` pattern) |
| The continuity gate failed: the ledger wrote `part_1..5` and `ch_01..10` | name every unit id in the ledger |
| Four hard-coded counts of 18 made four build stages red | §11 step 4 the same hour the unit is added |
| A 破折号 fell across a line break in the family paragraph (GB/T 15834 gate) | a punctuation change in that unit (period / comma) or a re-solve; the zh-Hant edition kept the dash where it broke cleanly |
| `convert_zhs.py --publish` on a shipped unit would overwrite the mainland reviewers' 82 edits | derive edited paragraphs by hand; the converter only for new units; refresh `_zht_ref` first |
| The zhs amendment file refused a second row for an existing id and a row for an id with no base row | one row per id; fold a new ruling into the existing row's note; new ids need full rows |
| The layout map's figure anchor was the start of an edited paragraph | `layout_*.py solve --fresh` after any text change (the build's layout gate says so too) |
| `grep -oP` with CJK returned nothing (R3-H); `python -c` with a `/c/...` path could not open the file | CJK context through Python; Windows paths as `C:/...` inside Python strings |
| The kit's `lint_manuscript` flagged the author's URL lines and the ornament in promote's draft copies | waivers for the URL lines; strip the ornament from the superseded copies too |

## 15. Locale appendix

v2 §10 stands (zh-Hans in 10.1, zh-Hant-TW in 10.2). Banked from the 2026-10-06 run:

- **zh-Hant-TW:** 佇列 (queue), 平台 (R18, book one's Taiwan form over the MOE 平臺), 致上, 試作, 媳婦, 創辦人, 高解析度,
  入口網站, 骨幹 (backbone; never 骨架 where it is locked for skeletal records), 癌症存活者, 西點軍校, BRIT 出版社主任,
  臺紙 for a herbarium sheet (not 標本), 本草 for materia medica, 全亞洲專題收藏網路（All Asia TCN）計畫.
- **zh-Hans:** 队列 (never 伫列, the converter's residue of 佇列: tripwire ML157), 平台, 致以, 试验, 媳妇 (book one's
  form), 创办人 (book one) or 创始人 (Bo's own page), 高分辨率, 门户网站, 骨干, 癌症幸存者, 西点军校, 档案记录 /
  档案库 for the archive sense (ML59 keeps 文件 for computer files), 本草, 全亚洲专题收藏网络（All Asia TCN）计划,
  我太太 at every "my wife" site (ZR19).
- **Both:** a URL line must carry at least one Han character (`Access Intellect 網站：https://…`) or the
  untranslated-block check fails; label lines are verbatim data in whatever script the label prints; the
  Latin pair for a person appears once, at first use (`舍溫·卡爾奎斯特博士（Sherwin Carlquist）` in ch_01, then the
  Chinese alone).

## 16. Verification that looks

- **Print:** `python _tools/pdf_spot_pages.py <interior.pdf> --out DIR --needle <text> …` renders the pages the
  needles land on (anchored by text, under 2000 px); look at every touched unit, every figure page, the About.
- **Kindle:** `python _tools/docx_to_pdf.py <KINDLE.docx> <scratch.pdf>` then `pdf_spot_pages.py` on it; then
  `word_sweep.py`.
- **EPUB:** unzip it; find the unit's XHTML; `python C:/peek/peek.py file:///<path> --shot --full` renders it in a
  headless browser (a local file view does not load the stylesheet's font stack, so judge text and structure, not
  the face).
- What to look for: the heading word, paragraph count, the family names, the URL lines, dashes and quotes in the
  locale's forms, the figure under its caption at a sensible size, no literal markdown, no stray `>`.

## 17. Definition of done

v2 §12 verbatim, plus for a re-sync: ☐ lineage test recorded ☐ every change group accounted for (translated /
duplicate / ornament / not text) ☐ the English workspace back-ported and refrozen; the previous freeze kept ☐ both
`_key/` refrozen and `build_key` clean ☐ edited segments patched count-asserted; new units gated ☐ counts, fences
and ledgers updated ☐ layout re-solved per edition ☐ builds green, previous packages restored beside the new ones,
pins repointed, combined zip built ☐ the eBooks looked at ☐ ledgers COMPLETE and consistent ☐ report, D-rows,
memory, lessons ledger.

## 18. Tools

Generic (`_tools/`): `docx_delta.py` (delta + lineage + duplicates + ornaments), `docx_figures.py` (document-order
figure map + perceptual match), `segment_peek.py` (segment beside its aligned paragraphs; parity with gloss lines set
aside), `unit_patch.py` (count-asserted, append-only positional patch), `add_unit.py` (config insert/move +
checklist), `pdf_spot_pages.py` (needle-anchored page renders), `word_sweep.py` (leaked Word), plus the kit's
`docx_to_pdf.py`, `lint_manuscript.py`, `scan_manuscript.py`, `check_continuity.py`, `s2t_fork.py` (the older
script-only fork, superseded by the converter + locale layer for a real locale edition).

Per edition (clone from the reference workspaces): the `_tools_<ed>/` gate kit and the `_scripts_<ed>/` production
kit listed in §7. Worked example of a re-sync, script by script: `docs/examples/translation_resync_2026-10-06/`.

---

*Provenance: v1 from `carlquist_zh` (2026-08-12) and `kimi_k3_zh` (2026-08-13); R3 from `you_stay_one_person_zh`
(2026-08-13); v2 from the `carlquist_zht` key (2026-09-25); the zh-Hant and zh-Hans editions of* Across Borders and
Herbaria *(2026-09-29 / 09-30) are v2's full-scale runs; v3 from their re-sync to the author's revised English
(2026-10-06, `book_workspace/across_borders/_translation/_p10_2026-10-06/`).*
