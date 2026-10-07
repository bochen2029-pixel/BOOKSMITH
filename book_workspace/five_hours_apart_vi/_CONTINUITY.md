# _CONTINUITY.md — five_hours_apart_vi (the vi-VN edition, translated fresh from five_hours_apart)

STATUS: COMPLETE

✅ SHIPPED 2026-10-07 (the translated text; see SHIP_REPORT_2026-10-07.md). Production (P7/P8) is a separate run.

## RESUME PROTOCOL
1. This is a FRESH edition (BOOK_TRANSLATION_METHOD_v3 §6.1) from the frozen English segments in `_key/segments.jsonl`
   (sha256 6ed2feb4…, the same freeze as the zh and es editions). The SOURCE outranks the key; the key is
   `translation_charter_vi.md` (rulings R1–R16, the row glossary §10, the locked lines §11, the imported meaning
   rulings §12) + `_key/registry_vi.tsv`.
2. `translation/current/<unit>.md` is the truth; `translation/drafts/<unit>_vN.md` are append-only snapshots (current =
   the latest draft of every unit). Every text change is a count-asserted patch: one edit with
   `python3 ../../_tools/unit_patch.py --workspace . --unit U --old-file A --new-file B --expect N`, a round with
   `python3 _tools_vi/apply_vi.py <round.tsv>` (columns id, old, new, source, why). A ruling also gets a charter §15
   line and, when it can regress, a registry row or a FORBID line.
3. Gate: `python3 _tools_vi/gate_vi.py --book translation/current` (0 FAIL) and its battery `python3
   _tools_vi/test_gate_vi.py` (ALL CASES BEHAVE: unit cases on ch_12 + the book cases). Row units: `python3
   _tools_vi/rows_vi.py <unit> --fix` re-pads the columns against the English rows (snapshot the result as a draft).
4. Master: `python3 _tools_vi/assemble_vi.py --version N` → `outputs/markdown/five_hours_apart_vi_vN.md` (gitignored;
   rebuild it from translation/current). Shipped master: v2, sha256 ce8373da85ea.
5. Units: front part_1 ch_01 ch_02 ch_03 ch_04 ch_05 ch_06 ch_07 ch_08 ch_09 part_2 ch_10 ch_11 ch_12 ch_13 ch_14 part_3 ch_15 ch_16 ch_17 ch_18
6. QA tools: `_tools_vi/show_blocks.py` (Vietnamese with unit.NNN ids, for blind reviewers), `_tools_vi/backdiff_view.py`
   (English over the back-translation). Briefs in `_brief/`, reports in `_qa/`.
7. The pronoun scheme (narration "anh"; dialogue tôi / anh / cô; bố / con) is charter R2; the alternatives are in
   `_qa/PRONOUN_SAMPLES.md` for the author to overrule (ship report D2).

## LOG
- 2026-10-07 SHIPPED. QA round 1: blind back-translation in two halves + the moderator's English-against-English diff
  of all 22 units (40 rows) and two Vietnamese register reviews (118 findings: 4 BLOCK, 82 FIX, 32 NIT); merged under
  recorded decisions (`_qa/merge_r1.py`) into 144 edits in 16 units, applied as one count-asserted round, then 3
  follow-ups (X .017 locked form, VIII .003 the bellman, VIII .002 the Southern "lầu"); R16 ruled and gated (rows
  glossary, R.hole, R.sorted, R.bellman, FORBID lines); gate 22 units 0 FAIL 0 WARN, book 0 FAIL, battery green
  (20 + 9 defect cases); master v2 (16,327 syllables, sha256 ce8373da85ea); SHIP_REPORT_2026-10-07.md written.
- 2026-10-07 all 22 units translated by the moderator and gated (22 PASS, 0 WARN; BOOK 0 FAIL); the echo list and the
  battery's book cases now Vietnamese (battery: ALL CASES BEHAVE); "anything is like anything for it" held at both
  sites by the registry row R.likeanything; drafts v1; master v1 (16,321 syllables, EN 13,163 words).
- 2026-10-07 workspace, frozen source copy, charter R1–R15, registry, gate/rows/assembler/battery written; front +
  Part One translated and pushed.

## DONE
All 22 units translated, reviewed, patched and gated: front part_1 ch_01 ch_02 ch_03 ch_04 ch_05 ch_06 ch_07 ch_08
ch_09 part_2 ch_10 ch_11 ch_12 ch_13 ch_14 part_3 ch_15 ch_16 ch_17 ch_18. Master v2 assembled.

## NEXT -> production on the operator's Windows machine (v3 §6.1 production, then §16): a book_config for the edition
(lang vi), Word COM builds, ComfyUI cover art, then look at print, Kindle and EPUB (check the row face renders the
Vietnamese diacritics). The master in outputs/markdown/ (v2) is the single source. The author's open decisions are
the D-rows in the ship report.

<!-- STATUS: COMPLETE -->
