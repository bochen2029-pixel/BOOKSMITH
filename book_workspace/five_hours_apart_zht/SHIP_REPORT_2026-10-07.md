# Ship report: *Five Hours Apart* in Chinese, zh-Hant-TW and zh-Hans (2026-10-07)

Method: `docs/BOOK_TRANSLATION_METHOD_v3.md`, runbooks §6.1 (a fresh edition) and §6.2 (a sibling locale).
Scope of this run: P0–P6 and P9 for the text of both editions. Production (P7, P8: print, Kindle, EPUB, covers) was
not run here; it needs the operator's Windows machine (see the last section).

## What shipped

| edition | master (the single source every format must read) | sha256 | units | CJK chars |
|---|---|---|---|---|
| zh-Hant-TW 《五小時之隔》 | `book_workspace/five_hours_apart_zht/outputs/markdown/five_hours_apart_zht_v2.md` | `0b8019635015a5b575345b2ec6d545831751f8f31135450cae1d55b8e52737a4` | 22 | 19,143 |
| zh-Hans 《五小时之隔》 | `book_workspace/five_hours_apart_zhs/outputs/markdown/five_hours_apart_zhs_v2.md` | `effad3c3dad52929d05736d81b0df6e2ad482e35c3e0faa728dd014de0e33d8b` | 22 | 19,211 |

Source of record: `intake/five-hours-apart.md` (13,470 words), split into 22 units and frozen as 515 segments
(`book_workspace/five_hours_apart/_translation/segments.jsonl`, sha256 `63438c99…`). In both masters every unit has
exactly as many blocks as the source has segments.

## How it was made

- **P0** source of record, segmentation, round-trip assertion, freeze. The PDF in the intake is a duplicate export of
  the same text (its title-page dateline is D2 below).
- **P1** the key: `translation_charter_zht.md` (the law; rulings R1–R35 in its log), `_key/registry_merged.tsv`
  (902 rows) plus `_key/registry_amendments_zht.tsv` (66 lines), and five ground-truth lanes in `_notes/`
  (GT_NAMES, GT_TERMS, GT_CANON, GT_PRECEDENT, GT_ZHS_LOCALE).
- **P2** a per-unit gate and a whole-book gate generated from the registry, with a must-fail battery
  (`_tools_zht/`).
- **P3** two worker waves (A: II, III, V, VII, VIII, IX, X, XIII; B, reading A: I, IV, VI, XI, XII, XIV); the
  moderator wrote the front matter, the three part titles and all of Part Three (XV–XVIII, the rows).
- **P4** every unit moderator-read against the English and promoted; drafts are append-only (162 zh-Hant drafts).
- **P5** quality assurance, every finding applied by count-asserted patch (`_tools/unit_patch.py`, `_qa/patches/`):

| report | what it is | BLOCK | FIX | NIT | outcome |
|---|---|---|---|---|---|
| `_qa/SEAMS_A.md` / `SEAMS_B.md` | every unit boundary read as one passage | 0 / 1 | 6 / 3 | 4 / 6 | R28, R29 |
| `_qa/ROWS.md` | Part Three's 141 logical rows, cell by cell, both sides | 0 | 5 | 10 | R30 |
| `_qa/REGISTER_TW.md` | a Taiwanese native-register read of the whole book | 2 | 47 | 31 | R31 (74 patches, 6 kept) |
| `_qa/BACKTRANS_A.md` + `BACKDIFF_A.md` | blind back-translation of Part One, then English against English | 1 | 18 | 28 | R33 (most already fixed) |
| `_qa/BACKTRANS_B.md` + `BACKDIFF_B.md` | the same for Parts Two and Three | 0 open | 1 open | 9 | R34 |
| `../five_hours_apart_zhs/_qa/MAINLAND.md` | mainland locale read of the derived zh-Hans text | 1 | 12 | 2 | R35 + layer rules |

- **P6** the moderator's full read of the zh-Hant text, aligned with the English and again as continuous Chinese
  (R32).
- **zh-Hans (§6.2)** derived, never retranslated: `../five_hours_apart_zhs/_tools_zhs/convert_zhs.py` runs OpenCC
  tw2sp, the registry's zh-Hans column, the mainland layer `_key/locale_layer_zhs.txt` (186 rules, each Taiwan form
  guarded by a `forbid:` line), “ ” quotes, and a row pass that re-pads every row block to the zh-Hant columns
  (`rows_zhs.py`). Every mainland-review fix is a rule in that chain, so re-running the converter reproduces the
  reviewed text.

## Verification (mechanical, all green on the final text)

```
cd book_workspace/five_hours_apart_zht
python3 _tools_zht/build_key.py                      # rows 902, gates 1694 sites, problems 0
python3 _tools_zht/test_gate.py                      # battery: ALL CASES BEHAVE
python3 _tools_zht/gate_unit.py <unit> translation/current/<unit>.md   # 22 PASS, 0 FAIL, 5 WARN (below)
python3 _tools_zht/gate_book.py translation/current  # 22 units, 0 FAIL
cd ../five_hours_apart_zhs
python3 _tools_zhs/gate_zhs.py --book translation/current             # 22 units, 0 FAIL
python3 _tools_zhs/test_gate_zhs.py --unit ch_12     # also ch_02, ch_06, ch_13: ALL CASES BEHAVE
python3 _tools_zhs/rows_zhs.py front ch_12 ch_14 ch_15 ch_16 ch_17 ch_18             # no output = aligned
```

- The five zh-Hant WARNs are one heuristic (在那裡 followed by a comma) firing on true "be there" predicates
  (II .004, .016, VI .057, VIII .007, XII .088); each was read and kept.
- Whole-book checks on both masters: the refrain 沒有什麼該來 / 没有什么该来 appears 5 times, as "nothing is due" does in
  the English; the opening row is byte-identical to the closing row; the only dashes are the four sanctioned 「——」
  cut-offs and the author's own "—" null in XVI's depth row; the zh-Hans gate fails any corner quote,
  Traditional-only character, ASCII quote, Taiwan residue or misaligned row block.
- Not done here: the rendered-page checks of §16 (print, Kindle, EPUB), because nothing was produced.

## Open decisions for the author (D-rows)

- **D1** The title 《五小時之隔》/《五小时之隔》, chosen over 《相隔五小時》 and 《五小時的距離》.
- **D2** The PDF export's title-page dateline "DALLAS · THE LAST WEEK OF OCTOBER" is not in the markdown source and
  was not translated.
- **D3** Author attribution: the English config says "Bo Chen" by inference from the kit; the PDF carries no author.
- **D4** 「它無我。它有她。」 (R9) over the plainer 「它沒有『我』。它有她。」; 無我 carries a Buddhist overtone.
- **D5** Minor Dallas names rest on transliteration convention, not attested print forms (zh-Hant 尤利斯, 巴克曼湖,
  史坦蒙斯, 卡本特; Las Colinas and Deep Ellum kept in Latin). zh-Hans uses the names lane's mainland forms (斯特蒙斯,
  卡彭特, 重逢塔, 特里尼蒂河, 格雷普韦恩, 深艾勒姆, 拉斯科利纳斯).
- **D6** Fahrenheit, feet and miles kept, as the narrator would say them.
- **D7** The intake's `_tools.zip` carries 12 shared kit tools newer than the repository's (schema, generators,
  EPUB, cover compositor, …). They are a kit upgrade, not part of a translation, and were not applied (the intake
  manifest calls this its D3).
- **D8** Pilot's callouts are written in Chinese numerals in prose (二七左, 七七七) while the rows keep 27L.
- **D9** In the zh-Hans rows the curly quotes are counted full-width, which is how a CJK face sets them; in a Latin
  code font (GitHub's preview, for one) the quoted rows look two columns short.

## Source-defect register

- **S1** VIII: "Far out, where he pointed" — in VI he never visibly points; the narration names the amber without a
  gesture. Translated as written (他指過的地方 / 他指过的地方).
- Checked and consistent: the clocks, floors and dates (41 floors down to L, then P1–P4: the 45 floors of XIV;
  Tuesday 27 October 2026; the UK clocks change 25 October, the US 1 November); XIII .021, where the narrator keeps
  speaking after "She looks at you", reads the same way in the English.

## Production (P7, P8): not part of this run

The masters above are the single source for every format. Producing them needs the operator's Windows machine:
Word COM for the DOCX → PDF path and page counts, the local ComfyUI for cover art (CLAUDE.md), and a schema-valid
`book_config.json` per edition (title, `lang` zh-Hant-TW / zh-Hans, Noto Serif CJK TC / SC, cover typography in
Chinese). Follow v3 §6.1 production for zh-Hant and §6.2 step 4 for zh-Hans (KDP publishes no Simplified Chinese:
EPUB to Google Play / Apple Books, print through a non-KDP printer), then §16: look at the printed pages, the Kindle
file and the EPUB.

## Evidence trail

Rulings log: `translation_charter_zht.md` (R1–R35). QA reports: `_qa/` in each workspace. Patches: `_qa/patches/`.
Drafts: `translation/drafts/` (append-only; 162 zh-Hant, 88 zh-Hans). Derivation logs:
`../five_hours_apart_zhs/_qa/convert_v1.log` … `convert_v4.log`. Ledgers: `_CONTINUITY.md` in each workspace.
Three late reviewers (the Parts Two–Three back-translation diff and both mainland halves) and the NIT tail of the
Part One diff were lost to a usage limit; the moderator did those reviews, as each report says.

## Lessons from this run

1. A one-character registry key runs before the locale layer and pre-empts its longer rules (訊→消息 turned 傳訊 into
   传消息 before the layer's 傳訊→发消息 could fire). Keep single-character keys out of the derivation, or give the
   layer a rule for the result.
2. A derivation that changes a cell's width moves every column after it; a derived edition with tables needs a
   realignment pass and a gate (now `rows_zhs.py`).
3. A key cell can contradict its own ground-truth lane (Iris 艾丽斯 against GT_NAMES's 艾丽丝); a check of the
   registry's name cells against the lanes' tables would catch it at P1.
4. Background reviewers die with the quota: have them write their report incrementally (the Part One diff's partial
   report saved every BLOCK and FIX row).
