# _CONTINUITY.md — five_hours_apart_de (the de-DE edition, translated fresh from five_hours_apart)

STATUS: IN_PROGRESS

## RESUME PROTOCOL
1. This is a FRESH edition (BOOK_TRANSLATION_METHOD_v3 §6.1) from the frozen English segments in `_key/segments.jsonl`
   (sha256 6ed2feb4…, the same freeze as the zh, es and vi editions). The SOURCE outranks the key; the key is
   `translation_charter_de.md` (rulings in its §15 log, the row glossary §10, the locked lines §11, the imported
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
   rebuild it from translation/current). Latest: v1, sha256 c25ddb1be056.
5. Units: front part_1 ch_01 ch_02 ch_03 ch_04 ch_05 ch_06 ch_07 ch_08 ch_09 part_2 ch_10 ch_11 ch_12 ch_13 ch_14 part_3 ch_15 ch_16 ch_17 ch_18
6. QA tools: `_tools_de/show_blocks.py` (German with unit.NNN ids, for blind reviewers), `_tools_de/backdiff_view.py`
   (English over the back-translation). Briefs in `_brief/`, reports in `_qa/`.

## LOG
- 2026-10-07 all 22 units translated by the moderator and gated (22 PASS, 0 WARN; BOOK 0 FAIL); German echoes and
  the battery's book cases set (battery: ALL CASES BEHAVE, 20 + 9 defect cases); drafts v1; master v1 (13,510 words,
  EN 13,163).
- 2026-10-07 workspace, frozen source copy, charter R1–R15, 186-row registry, gate/rows/assembler/battery written
  (cloned from vi, adapted for „…“ and the German comma, no dashes in prose).

## DONE
All 22 units translated and gated: front part_1 ch_01 ch_02 ch_03 ch_04 ch_05 ch_06 ch_07 ch_08 ch_09 part_2 ch_10
ch_11 ch_12 ch_13 ch_14 part_3 ch_15 ch_16 ch_17 ch_18. Master v1 assembled.

## NEXT -> QA round 1 (v3 §P5): blind back-translation in two halves (front–IX, Part Two–XVIII) diffed English against
English by the moderator (`_tools_de/backdiff_view.py`); a German native-register, copy-edit and seam review in two
halves; merge decisions in `_qa/merge_r1.py` (read every replacement); one count-asserted round
(`_tools_de/apply_de.py`); re-pad the rows, snapshot drafts, gates and battery green; master v2; ship report; this
ledger COMPLETE.

<!-- STATUS: IN_PROGRESS -->
