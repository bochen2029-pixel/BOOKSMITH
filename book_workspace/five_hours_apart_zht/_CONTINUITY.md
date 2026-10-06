# _CONTINUITY.md — five_hours_apart_zht (the zh-Hant-TW edition of *Five Hours Apart*)

STATUS: IN_PROGRESS

## RESUME PROTOCOL (read first after any compaction or resume)
1. Read `translation_charter_zht.md` in full (the law), then `_key/registry_merged.tsv` is the machine half; `_generated/` is derived (`python3 _tools_zht/build_key.py` regenerates it).
2. `python3 _tools_zht/test_gate.py` must print ALL CASES BEHAVE before any gate is trusted.
3. The translation truth is `translation/current/<unit>.md`; drafts are append-only in `translation/drafts/`; every unit's ledger is `_brief/ledgers/<unit>_ledger.md`.
4. `python3 _tools_zht/gate_book.py translation/current` is the whole-book gate (0 FAIL = ready for QA).
5. Units (22, in reading order): front part_1 ch_01 ch_02 ch_03 ch_04 ch_05 ch_06 ch_07 ch_08 ch_09 part_2 ch_10 ch_11 ch_12 ch_13 ch_14 part_3 ch_15 ch_16 ch_17 ch_18
6. Waves: A = ch_02 ch_03 ch_05 ch_07 ch_08 ch_09 ch_10 ch_13 (workers); B = ch_01 ch_04 ch_06 ch_11 ch_12 ch_14 (workers, reading A); moderator = front part_1 part_2 part_3 ch_15 ch_16 ch_17 ch_18.
7. After every unit lands: update DONE below, rewrite this file.

## LOG
- 2026-10-06 R22–R24 ratified (A.landing scope; XIV close; hint rows caught up); zh-Hans dry run on 18 units in the scratchpad: 0 FAIL after gate_zhs derives its forms through the converter, the converter collapses 漢字–漢字 spaces, the layer gains 搆→够, 廂型車, 橘色, 備忘錄, 磨石子地板.
- 2026-10-06 wave A closed: R12–R21 ratified (charter §15; amendments F.blind F.landed F.readsit F.machines F.colleague G.reunion R.issecret), key rebuilt (902 rows, 0 problems), every promoted unit re-gated PASS; gate_book docstring fixed to 沒有什麼該來.
- 2026-10-06 P0 frozen: 515 segments, sha256 63438c99…; P1 key ratified (charter v1.0, registry 896 rows, R1–R11); gate battery green; wave A launched; the moderator's 8 units gated PASS and promoted.

## DONE (units in translation/current, gate PASS)
front part_1 part_2 part_3 ch_15 ch_16 ch_17 ch_18 (the moderator's units) · wave A complete and moderator-read: ch_02 (v3) ch_03 (v3: R20 patches) ch_05 (v3) ch_07 (v3) ch_08 (v3) ch_09 (v2: R13) ch_10 (v2) ch_13 (v3: R20 列) · wave B so far: ch_04 (v1) ch_06 (v4: R25 patches) ch_11 (v2) ch_14 (v3: R23 close), all moderator-read; ch_18 patched to v2 (他是真心的) · wave B closed: ch_01 (v2) ch_12 (v6: R27 patches), moderator-read. ALL 22 UNITS IN translation/current, book gate 0 FAIL

## NEXT (updated after wave B) -> assemble v1; QA workers; patches; moderator full read; zh-Hans. (old) wave B: ch_06 ch_11 ch_12 ch_14 running; ch_01 (reads front + ch_02) and ch_04 (reads ch_03 + ch_05) launched after wave A closed. Then: gate_book 0 FAIL -> assemble_zht --version 1 -> QA workers (_brief/QA_BRIEFS.md) -> patches -> moderator full read -> zh-Hans derivation (../five_hours_apart_zhs) -> ship report -> commit/push/draft PR.

<!-- STATUS: IN_PROGRESS -->
