# _CONTINUITY.md — five_hours_apart_zhs (the zh-Hans edition, derived from five_hours_apart_zht)

STATUS: IN_PROGRESS

## RESUME PROTOCOL
1. The zh-Hant-TW edition is canonical; this edition is DERIVED (BOOK_TRANSLATION_METHOD_v3 §6.2): never retranslate.
2. `python3 _tools_zhs/bootstrap_zhs.py` refreshes _zht_ref/ and _key/ from the Taiwan workspace (hash-verified).
3. `python3 _tools_zhs/convert_zhs.py --all --publish --version N` derives every unit (OpenCC tw2sp + the registry's
   zh-Hans column + _key/locale_layer_zhs.txt + “ ” quotes) and prints every replacement.
4. `python3 _tools_zhs/gate_zhs.py --book translation/current` is the gate (0 FAIL); then the mainland reviewers read
   it whole and their edits go in by hand (append-only drafts); never re-run the converter over a reviewed unit.
5. Units: front part_1 ch_01 ch_02 ch_03 ch_04 ch_05 ch_06 ch_07 ch_08 ch_09 part_2 ch_10 ch_11 ch_12 ch_13 ch_14 part_3 ch_15 ch_16 ch_17 ch_18

## LOG
- 2026-10-06 machinery written (converter, bootstrap, gate, locale layer v1 from GT_TERMS/GT_CANON); waiting on the ratified zh-Hant text.

## DONE
(none yet)

## NEXT -> bootstrap after the zh-Hant edition is ratified; convert; gate; mainland review.

<!-- STATUS: IN_PROGRESS -->
