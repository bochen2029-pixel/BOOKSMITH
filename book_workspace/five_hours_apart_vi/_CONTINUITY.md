# _CONTINUITY.md — five_hours_apart_vi (the vi-VN edition, translated fresh from five_hours_apart)

STATUS: IN_PROGRESS

## RESUME PROTOCOL
1. This is a FRESH edition (BOOK_TRANSLATION_METHOD_v3 §6.1) from the frozen English segments in `_key/segments.jsonl`
   (sha256 6ed2feb4…, the same freeze as the zh and es editions). The SOURCE outranks the key; the key is
   `translation_charter_vi.md` (rulings in its §15 log, the row glossary §10, the locked lines §11, the imported
   meaning rulings §12) + `_key/registry_vi.tsv`.
2. `translation/current/<unit>.md` is the truth; `translation/drafts/<unit>_vN.md` are append-only snapshots (current =
   the latest draft of every unit). Every text change is a count-asserted patch: one edit with
   `python3 ../../_tools/unit_patch.py --workspace . --unit U --old-file A --new-file B --expect N`, a round with
   `python3 _tools_vi/apply_vi.py <round.tsv>` (columns id, old, new, source, why). A ruling also gets a charter §15
   line and, when it can regress, a registry row or a FORBID line.
3. Gate: `python3 _tools_vi/gate_vi.py --book translation/current` (0 FAIL) and its battery `python3
   _tools_vi/test_gate_vi.py` (ALL CASES BEHAVE: unit cases on ch_12 + the book cases). Row units: `python3
   _tools_vi/rows_vi.py <unit> --fix` re-pads the columns against the English rows (snapshot the result as a draft).
4. Master: `python3 _tools_vi/assemble_vi.py --version N` → `outputs/markdown/five_hours_apart_vi_vN.md` (gitignored;
   rebuild it from translation/current). Latest: v1, sha256 013cf45dd9a4.
5. Units: front part_1 ch_01 ch_02 ch_03 ch_04 ch_05 ch_06 ch_07 ch_08 ch_09 part_2 ch_10 ch_11 ch_12 ch_13 ch_14 part_3 ch_15 ch_16 ch_17 ch_18
6. QA tools: `_tools_vi/show_blocks.py` (Vietnamese with unit.NNN ids, for blind reviewers), `_tools_vi/backdiff_view.py`
   (English over the back-translation). Briefs in `_brief/`, reports in `_qa/`.
7. The pronoun scheme (narration "anh"; dialogue tôi / anh / cô; bố / con) is charter R2; the alternatives are in
   `_qa/PRONOUN_SAMPLES.md` for the author to overrule before the edition ships.

## LOG
- 2026-10-07 all 22 units translated by the moderator and gated (22 PASS, 0 WARN; BOOK 0 FAIL); the echo list and the
  battery's book cases now Vietnamese (battery: ALL CASES BEHAVE); "anything is like anything for it" held at both
  sites by the registry row R.likeanything; drafts v1; master v1 (16,321 syllables, EN 13,163 words).
- 2026-10-07 workspace, frozen source copy, charter R1–R15, registry, gate/rows/assembler/battery written; front +
  Part One translated and pushed.

## DONE
All 22 units translated and gated: front part_1 ch_01 ch_02 ch_03 ch_04 ch_05 ch_06 ch_07 ch_08 ch_09 part_2 ch_10
ch_11 ch_12 ch_13 ch_14 part_3 ch_15 ch_16 ch_17 ch_18. Master v1 assembled.

## NEXT -> QA round 1 (v3 §P5): blind back-translation in two halves (front–IX, Part Two–XVIII) diffed English against
English by the moderator (`_tools_vi/backdiff_view.py`); a Vietnamese native-register, copy-edit and seam review in two
halves; merge decisions in `_qa/merge_r1.py`; one count-asserted round (`_tools_vi/apply_vi.py`); re-pad the rows,
snapshot drafts v2, gates and battery green; master v2; ship report; this ledger COMPLETE.

<!-- STATUS: IN_PROGRESS -->
