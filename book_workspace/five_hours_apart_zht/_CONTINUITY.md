# _CONTINUITY.md — five_hours_apart_zht (the zh-Hant-TW edition of *Five Hours Apart*)

STATUS: COMPLETE

✅ SHIPPED 2026-10-07 (the translated text; see the ship report). Production (P7/P8) is a separate run.

## RESUME PROTOCOL (read first after any compaction or resume)
1. Read `translation_charter_zht.md` in full (the law), then `_key/registry_merged.tsv` is the machine half; `_generated/` is derived (`python3 _tools_zht/build_key.py` regenerates it).
2. `python3 _tools_zht/test_gate.py` must print ALL CASES BEHAVE before any gate is trusted.
3. The translation truth is `translation/current/<unit>.md`; drafts are append-only in `translation/drafts/`; every unit's ledger is `_brief/ledgers/<unit>_ledger.md`.
4. `python3 _tools_zht/gate_book.py translation/current` is the whole-book gate (0 FAIL = ready for QA).
5. Units (22, in reading order): front part_1 ch_01 ch_02 ch_03 ch_04 ch_05 ch_06 ch_07 ch_08 ch_09 part_2 ch_10 ch_11 ch_12 ch_13 ch_14 part_3 ch_15 ch_16 ch_17 ch_18
6. Waves: A = ch_02 ch_03 ch_05 ch_07 ch_08 ch_09 ch_10 ch_13 (workers); B = ch_01 ch_04 ch_06 ch_11 ch_12 ch_14 (workers, reading A); moderator = front part_1 part_2 part_3 ch_15 ch_16 ch_17 ch_18.
7. After every unit lands: update DONE below, rewrite this file.

## LOG
- 2026-10-07 BACKDIFF_B done by the moderator (R34); master v2 ratified (sha256 0b8019635015); R35 (zh-Hans cells only); ship report SHIP_REPORT_2026-10-07.md. SHIPPED 2026-10-07: translation complete (P0–P6, P9); production P7/P8 not run.
- 2026-10-06 P5 QA applied: SEAMS_A/B (R28–R29), ROWS (R30), REGISTER_TW (R31, 74 patches), BACKTRANS_A/B reader's notes, BACKDIFF_A (R33; its agent stopped on a usage limit after the BLOCK/FIX rows). P6 full read by the moderator, aligned and continuous (R32). zh-Hans v1 derived and published for the mainland review. Book gate 0 FAIL, battery green throughout.
- 2026-10-06 R22–R24 ratified (A.landing scope; XIV close; hint rows caught up); zh-Hans dry run on 18 units in the scratchpad: 0 FAIL after gate_zhs derives its forms through the converter, the converter collapses 漢字–漢字 spaces, the layer gains 搆→够, 廂型車, 橘色, 備忘錄, 磨石子地板.
- 2026-10-06 wave A closed: R12–R21 ratified (charter §15; amendments F.blind F.landed F.readsit F.machines F.colleague G.reunion R.issecret), key rebuilt (902 rows, 0 problems), every promoted unit re-gated PASS; gate_book docstring fixed to 沒有什麼該來.
- 2026-10-06 P0 frozen: 515 segments, sha256 63438c99…; P1 key ratified (charter v1.0, registry 896 rows, R1–R11); gate battery green; wave A launched; the moderator's 8 units gated PASS and promoted.

## DONE (units in translation/current, gate PASS)
front part_1 part_2 part_3 ch_15 ch_16 ch_17 ch_18 (the moderator's units) · wave A complete and moderator-read: ch_02 (v3) ch_03 (v3: R20 patches) ch_05 (v3) ch_07 (v3) ch_08 (v3) ch_09 (v2: R13) ch_10 (v2) ch_13 (v3: R20 列) · wave B so far: ch_04 (v1) ch_06 (v4: R25 patches) ch_11 (v2) ch_14 (v3: R23 close), all moderator-read; ch_18 patched to v2 (他是真心的) · wave B closed: ch_01 (v2) ch_12 (v6: R27 patches), moderator-read. ALL 22 UNITS IN translation/current, book gate 0 FAIL

## NEXT -> production on the operator's Windows machine (v3 §6.1 / §6.2 step 4, then §16): a book_config per edition, Word COM builds, ComfyUI cover art, then look at print, Kindle and EPUB. The masters in outputs/markdown/ (v2) are the single source.

<!-- STATUS: COMPLETE -->
