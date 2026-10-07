# _CONTINUITY.md — five_hours_apart_zhs (the zh-Hans edition, derived from five_hours_apart_zht)

STATUS: COMPLETE

✅ SHIPPED 2026-10-07 (the translated text; see the ship report). Production (P7/P8) is a separate run.

## RESUME PROTOCOL
1. The zh-Hant-TW edition is canonical; this edition is DERIVED (BOOK_TRANSLATION_METHOD_v3 §6.2): never retranslate.
2. `python3 _tools_zhs/bootstrap_zhs.py` refreshes _zht_ref/ and _key/ from the Taiwan workspace (hash-verified).
3. `python3 _tools_zhs/convert_zhs.py --all --publish --version N` derives every unit (OpenCC tw2sp + the registry's
   zh-Hans column + _key/locale_layer_zhs.txt + “ ” quotes) and prints every replacement.
4. `python3 _tools_zhs/gate_zhs.py --book translation/current` is the gate (0 FAIL), `python3 _tools_zhs/test_gate_zhs.py
   --unit ch_12` its battery. Every mainland-review edit lives in the derivation (a registry zh-Hans cell or a layer line,
   each with a forbid: guard), never in a hand edit, so re-running the converter reproduces the reviewed text exactly.
   `python3 _tools_zhs/rows_zhs.py <units>` shows any row block that has left the zh-Hant columns (the gate fails it).
5. Units: front part_1 ch_01 ch_02 ch_03 ch_04 ch_05 ch_06 ch_07 ch_08 ch_09 part_2 ch_10 ch_11 ch_12 ch_13 ch_14 part_3 ch_15 ch_16 ch_17 ch_18

## LOG
- 2026-10-07 SHIPPED with the zh-Hant edition: ../five_hours_apart_zht/SHIP_REPORT_2026-10-07.md. Production P7/P8 not run.
- 2026-10-07 derived from the ratified zh-Hant master v2 (convert v2–v4); rows re-padded to the zh-Hant columns (rows_zhs.py, in the converter and the gate, battery case added); 传消息 → 发消息; mainland review by the moderator (_qa/MAINLAND.md: BLOCK 1 Iris 艾丽丝 not 艾丽斯, FIX 12, NIT 2), all as registry/layer rules with forbid guards; gate 22 units 0 FAIL, batteries green; master outputs/markdown/five_hours_apart_zhs_v2.md (sha256 effad3c3dad5).
- 2026-10-06 machinery written (converter, bootstrap, gate, locale layer v1 from GT_TERMS/GT_CANON); waiting on the ratified zh-Hant text.

## DONE
All 22 units derived (translation/current = drafts v4), mainland-reviewed, gated; master v2 assembled.

## NEXT -> production on the operator's Windows machine (v3 §6.1 / §6.2 step 4, then §16): a book_config per edition, Word COM builds, ComfyUI cover art, then look at print, Kindle and EPUB. The masters in outputs/markdown/ (v2) are the single source.

<!-- STATUS: COMPLETE -->
