# _CONTINUITY.md — five_hours_apart_de (the de-DE edition, translated fresh from five_hours_apart)

STATUS: COMPLETE

✅ SHIPPED 2026-10-07 (the translated text; see SHIP_REPORT_2026-10-07.md). Production (P7/P8) is a separate run.

## RESUME PROTOCOL
1. This is a FRESH edition (BOOK_TRANSLATION_METHOD_v3 §6.1) from the frozen English segments in `_key/segments.jsonl`
   (sha256 6ed2feb4…, the same freeze as the zh, es and vi editions). The SOURCE outranks the key; the key is
   `translation_charter_de.md` (rulings R1–R16 in its §15 log, the row glossary §10, the locked lines §11, the imported
   meaning rulings §12) + `_key/registry_de.tsv`.
2. `translation/current/<unit>.md` is the truth; `translation/drafts/<unit>_vN.md` are append-only snapshots (current =
   the latest draft of every unit). Every text change is a count-asserted patch: one edit with
   `python3 ../../_tools/unit_patch.py --workspace . --unit U --old-file A --new-file B --expect N`, a round with
   `python3 _tools_de/apply_de.py <round.tsv>` (columns id, old, new, source, why). A ruling also gets a charter §15
   line and, when it can regress, a registry row or a FORBID line.
3. Gate: `python3 _tools_de/gate_de.py --book translation/current` (0 FAIL) and its battery `python3
   _tools_de/test_gate_de.py` (ALL CASES BEHAVE: unit cases on ch_12 + the book cases). Row units: `python3
   _tools_de/rows_de.py <unit> --fix` re-pads the columns against the English rows (snapshot the result as a draft).
4. Master: `python3 _tools_de/assemble_de.py --version N` → `outputs/markdown/five_hours_apart_de_vN.md` (gitignored;
   rebuild it from translation/current). Shipped master: v2, sha256 e87ff2d63879.
5. Units: front part_1 ch_01 ch_02 ch_03 ch_04 ch_05 ch_06 ch_07 ch_08 ch_09 part_2 ch_10 ch_11 ch_12 ch_13 ch_14 part_3 ch_15 ch_16 ch_17 ch_18
6. QA tools: `_tools_de/show_blocks.py` (German with unit.NNN ids, for blind reviewers), `_tools_de/backdiff_view.py`
   (English over the back-translation). Briefs in `_brief/`, reports in `_qa/`.
7. Address is charter R2 ("du" narration; "du" between Iris and the narrator; Papa / Junge); the author may overrule it
   (ship report D2).

## LOG
- 2026-10-07 SHIPPED. QA round 1: blind back-translation in two halves + the moderator's English-against-English diff
  of all 22 units (28 rows) and two German register reviews (94 findings: 4 BLOCK, 60 FIX, 30 NIT); merged under
  recorded decisions (`_qa/merge_r1.py`) into 115 edits in 17 units, applied as one count-asserted round; then the
  XVII row term "Zeitscheibe" (one patch, 8 rows) and 3 follow-ups from register B's decision list
  (`_qa/APPLY_r2.tsv`: "Etikettenstreifen" at XI and XV, XII .097 "dreht"); R16 ruled and gated (registry R.behind,
  ROWS tokens, FORBID lines, echo pairs II/XII, VII/XIII, III/IX); gate 22 units 0 FAIL 0 WARN, book 0 FAIL, battery
  green (20 + 15 defect cases); master v2 (13,550 words, sha256 e87ff2d63879); SHIP_REPORT_2026-10-07.md written.
- 2026-10-07 all 22 units translated by the moderator and gated (22 PASS, 0 WARN; BOOK 0 FAIL); German echoes and
  the battery's book cases set (battery: ALL CASES BEHAVE, 20 + 9 defect cases); drafts v1; master v1 (13,510 words,
  EN 13,163).
- 2026-10-07 workspace, frozen source copy, charter R1–R15, 186-row registry, gate/rows/assembler/battery written
  (cloned from vi, adapted for „…“ and the German comma, no dashes in prose).

## DONE
All 22 units translated, reviewed, patched and gated: front part_1 ch_01 ch_02 ch_03 ch_04 ch_05 ch_06 ch_07 ch_08
ch_09 part_2 ch_10 ch_11 ch_12 ch_13 ch_14 part_3 ch_15 ch_16 ch_17 ch_18. Master v2 assembled.

## NEXT -> production on the operator's Windows machine (v3 §6.1 production, then §16): a book_config for the edition
(lang de; the Word document language de-DE so the long compounds hyphenate correctly), Word COM builds, ComfyUI cover
art, then look at print, Kindle and EPUB. The master in outputs/markdown/ (v2) is the single source. The author's open
decisions are the D-rows in the ship report.

<!-- STATUS: COMPLETE -->
