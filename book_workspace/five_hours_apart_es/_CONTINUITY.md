# _CONTINUITY.md — five_hours_apart_es (the es-419 edition, translated fresh from five_hours_apart)

STATUS: COMPLETE

✅ SHIPPED 2026-10-07 (the translated text; see SHIP_REPORT_2026-10-07.md). Production (P7/P8) is a separate run.

## RESUME PROTOCOL
1. This is a FRESH edition (BOOK_TRANSLATION_METHOD_v3 §6.1) from the frozen English segments in `_key/segments.jsonl`
   (sha256 6ed2feb4…, the same freeze as the zh editions). The SOURCE outranks the key; the key is
   `translation_charter_es.md` (rulings R1–R18, the row glossary §10, the locked motifs §11) + `_key/registry_es.tsv`.
2. `translation/current/<unit>.md` is the truth; `translation/drafts/<unit>_vN.md` are append-only snapshots (current =
   the latest draft of every unit). Every text change is a count-asserted patch: one edit with
   `python3 ../../_tools/unit_patch.py --workspace . --unit U --old-file A --new-file B --expect N`, a round with
   `python3 _tools_es/apply_es.py <round.tsv>` (columns id, old, new, source, why). A ruling also gets a charter §15
   line and, when it can regress, a registry row or a FORBID line.
3. Gate: `python3 _tools_es/gate_es.py --book translation/current` (0 FAIL) and its battery `python3
   _tools_es/test_gate_es.py` (ALL CASES BEHAVE: unit cases on ch_12 + the book cases). Row units: `python3
   _tools_es/rows_es.py <unit> --fix` re-pads the columns against the English rows (snapshot the result as a draft).
4. Master: `python3 _tools_es/assemble_es.py --version N` → `outputs/markdown/five_hours_apart_es_vN.md` (gitignored;
   rebuild it from translation/current). Shipped master: v2, sha256 501c5a29b8f0.
5. Units: front part_1 ch_01 ch_02 ch_03 ch_04 ch_05 ch_06 ch_07 ch_08 ch_09 part_2 ch_10 ch_11 ch_12 ch_13 ch_14 part_3 ch_15 ch_16 ch_17 ch_18
6. QA tools: `_tools_es/show_blocks.py` (Spanish with unit.NNN ids, for blind reviewers), `_tools_es/backdiff_view.py`
   (English over the back-translation). Briefs in `_brief/`, reports in `_qa/`.

## LOG
- 2026-10-07 SHIPPED. QA round 1: blind back-translation in two halves + the moderator's English-against-English diff
  and full read (50 rows) and a Latin American register review (61 findings: 2 BLOCK, 35 FIX, 24 NIT); merged under
  recorded decisions (`_qa/merge_r1.py`) into 90 edits in 17 units, applied as one count-asserted round; locked lines
  that had drifted restored and gated (R18); gate 22 units 0 FAIL 0 WARN, book 0 FAIL, battery green; master v2
  (13,728 words, sha256 501c5a29b8f0); SHIP_REPORT_2026-10-07.md written.
- 2026-10-07 all 22 units translated by the moderator (R15); book gate 0 FAIL; battery with book cases; drafts v1;
  master v1. R17: "take back" = deshacer.
- 2026-10-07 workspace, frozen source copy, charter R1–R16, registry, gate/rows/assembler/battery written; front +
  Parts One and Two translated and pushed (PR bochen2029-pixel/BOOKSMITH#2).

## DONE
All 22 units translated, reviewed, patched and gated: front part_1 ch_01 ch_02 ch_03 ch_04 ch_05 ch_06 ch_07 ch_08
ch_09 part_2 ch_10 ch_11 ch_12 ch_13 ch_14 part_3 ch_15 ch_16 ch_17 ch_18. Master v2 assembled.

## NEXT -> production on the operator's Windows machine (v3 §6.1 production, then §16): a book_config for the edition
(lang es-419), Word COM builds, ComfyUI cover art, then look at print, Kindle and EPUB. The master in
outputs/markdown/ (v2) is the single source. The author's open decisions are the D-rows in the ship report.

<!-- STATUS: COMPLETE -->
