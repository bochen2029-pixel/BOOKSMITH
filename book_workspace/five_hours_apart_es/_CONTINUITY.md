# _CONTINUITY.md — five_hours_apart_es (the es-419 edition, translated fresh from five_hours_apart)

STATUS: IN_PROGRESS

## RESUME PROTOCOL
1. This is a FRESH edition (BOOK_TRANSLATION_METHOD_v3 §6.1) from the frozen English segments in `_key/segments.jsonl`
   (sha256 6ed2feb4…, the same freeze as the zh editions). The SOURCE outranks the key; the key is
   `translation_charter_es.md` (rulings R1–R17, the row glossary §10, the locked motifs §11) + `_key/registry_es.tsv`.
2. `translation/current/<unit>.md` is the truth; `translation/drafts/<unit>_vN.md` are append-only snapshots. After v1,
   every text change is a count-asserted patch (`python3 ../../_tools/unit_patch.py --workspace . --unit U --old-file
   A --new-file B --expect N`) with a charter §15 line when it is a ruling.
3. Gate: `python3 _tools_es/gate_es.py --book translation/current` (0 FAIL) and its battery `python3
   _tools_es/test_gate_es.py` (ALL CASES BEHAVE, unit cases on ch_12 + the book cases). Row units: `python3
   _tools_es/rows_es.py <unit> --fix` re-pads the columns against the English rows.
4. Master: `python3 _tools_es/assemble_es.py --version N` → `outputs/markdown/five_hours_apart_es_vN.md` (gitignored;
   rebuild it from translation/current).
5. Units: front part_1 ch_01 ch_02 ch_03 ch_04 ch_05 ch_06 ch_07 ch_08 ch_09 part_2 ch_10 ch_11 ch_12 ch_13 ch_14 part_3 ch_15 ch_16 ch_17 ch_18
6. QA reports go to `_qa/` (briefs in `_brief/`); a reviewer writes its report incrementally, unit by unit.

## LOG
- 2026-10-07 all 22 units translated by the moderator (R15); every unit gates PASS; book gate 0 FAIL (refrain 5/5, echoes,
  opening row = closing row); battery ALL CASES BEHAVE (book cases added: wrapped row quote, echo, refrain, closing row);
  drafts v1 snapshotted; master v1 assembled (13,682 words vs EN 13,163, sha256 70c60e38719e). R17: "take back" =
  deshacer (row "taken back" → deshecho).
- 2026-10-07 workspace, frozen source copy, charter R1–R16, registry, gate/rows/assembler/battery written; front +
  Part One + Part Two translated and pushed (PR bochen2029-pixel/BOOKSMITH#2).

## DONE
Translation v1 of all 22 units; gates and battery green; master v1.

## NEXT -> QA (v3 P5/P6): blind back-translation in two halves + an English-vs-English diff; a Latin American
native-register and seam review; the moderator's full read and rows audit; fixes as count-asserted patches; master v2;
ship report; this ledger to COMPLETE (`python3 ../../_tools/check_continuity.py`).

<!-- STATUS: IN_PROGRESS -->
