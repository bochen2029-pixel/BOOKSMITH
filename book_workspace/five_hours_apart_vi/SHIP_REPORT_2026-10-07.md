# Ship report: *Five Hours Apart* in Vietnamese, vi-VN (2026-10-07)

Method: `docs/BOOK_TRANSLATION_METHOD_v3.md`, runbook §6.1 (a fresh edition). Scope of this run: P0–P6 and P9 for
the text. Production (P7, P8: print, Kindle, EPUB, cover) was not run here; it needs the operator's Windows machine
(see the last section).

## What shipped

| edition | master (the single source every format must read) | sha256 | units | syllables |
|---|---|---|---|---|
| vi-VN *Cách nhau năm tiếng* | `book_workspace/five_hours_apart_vi/outputs/markdown/five_hours_apart_vi_v2.md` | `ce8373da85ead2544fc52c4fcb6c714895a818efe01b0d79f967a24447a3f302` | 22 | 16,327 (EN 13,163 words, ×1.24) |

Subtitle *Một giả định, trong ba phần*. Parts: *Phần Một · Cách nhau năm tiếng*, *Phần Hai · Chẳng có gì sắp đến*,
*Phần Ba · Cứ cho là*. Source of record: the same frozen English as the zh and es editions (515 segments,
`_key/segments.jsonl`, sha256 `6ed2feb4…`). Every unit has exactly as many blocks as the source has segments. The
master is gitignored like the other editions' masters: rebuild it with `python3 _tools_vi/assemble_vi.py --version 2`
from `translation/current/`, which is committed.

## How it was made

- **P0** the frozen English segments, reused from the zh editions (the source did not change).
- **P1** the key, built by the moderator: `translation_charter_vi.md` (the law; rulings R1–R16 in its log),
  `_key/registry_vi.tsv` (186 rows: names, places, the 22 headings, field terms, locked lines, the language-neutral
  meaning rulings imported from zh-Hant and es), the row glossary (`ROWS` in `_tools_vi/vi_common.py`, charter §10),
  the locked lines (§11). Every locked line with two or more sites is a registry row from the start (lesson 23.1 of
  the es run).
- **P2** a per-unit gate and a whole-book gate (`_tools_vi/gate_vi.py`: syllables against English words, the dialogue
  dash, the tone-mark style, translationese warnings, the row glossary and columns, the refrain count, the lines the
  rows quote from the prose, the echoes, the opening row against the closing row) with a must-fail battery
  (`_tools_vi/test_gate_vi.py`: 20 defect cases on XII and 9 on a copy of the whole book, each with a clean control).
- **P3/P4** the moderator translated all 22 units (R15) and gated each to PASS with 0 WARN; drafts are append-only
  (42 files).
- **P5** quality assurance by four independent agents, every accepted finding applied in one count-asserted round
  (`_tools_vi/apply_vi.py` → `_tools/unit_patch.py`, one patch per unit; `_qa/merge_r1.py` records every decision):

| report | what it is | findings | applied | outcome |
|---|---|---|---|---|
| `_qa/back/` (A: front–IX, B: Part Two–XVIII) + `_qa/MODERATOR.tsv` | blind back-translation, then the moderator's English-against-English diff of every unit (`_tools_vi/backdiff_view.py`) | 2 meaning drifts (X .013, XVI rule 4), 1 direction slip (XII .040), 37 ambiguities, idiom collisions and lost echoes | 34 (6 superseded by the register's wording) | R16 |
| `_qa/register/` + `SUMMARY_A.md`, `SUMMARY_B.md` | two Vietnamese native-register, copy-edit and seam reads, one per half | 118: 4 BLOCK, 82 FIX, 32 NIT | 110 (7 duplicates of moderator rows; 1 NIT declined) | R16 |

  The meaning slips: X .013 "Anh đã quyết định chuyện này từ hôm thứ Ba" (he *had decided*; the English is "you've
  been deciding this since Tuesday"), XII .040 the rewound ripple running into the edge it came *to*, and XVI's rule
  4, where "không gì viết ở đây được khắc" read as "nothing written here gets carved" instead of "nothing written here
  can carve"; the row glossary now says "khắc được". Both back-translators and both register readers found other
  places where a literal choice collides with a fixed Vietnamese idiom ("nghĩ ngược lại" = think the opposite, "nửa
  ngủ" = half-asleep, "giơ tay lên trời" = give up, "tấm bằng" = a diploma, "bốn mươi bộ đèn" = forty light fixtures).
  The register readers found the calque habits of the narration ("với" for English "with", "trong đó" for "in which",
  object "nó"), a false echo of the refrain (XII .051 "nghe nó sắp đến"), and a sexual euphemism one of them proposed
  ("làm chuyện ấy"), which the moderator declined.
- **P6** the moderator's read: the English-against-English diff of all 22 units, a reading of every flagged block in
  the Vietnamese, and a reading of every patched sentence in context after the round (which found the Southern "Trên
  lầu" in VIII that half A had missed).

## Verification (mechanical, all green on the final text)

```
cd book_workspace/five_hours_apart_vi
python3 _tools_vi/gate_vi.py --book translation/current   # 22 units PASS, 0 FAIL, 0 WARN; BOOK 0 FAIL
python3 _tools_vi/test_gate_vi.py                          # battery: ALL CASES BEHAVE (unit + book cases)
python3 _tools_vi/rows_vi.py front ch_12 ch_14 ch_15 ch_16 ch_17 ch_18   # 0 blocks re-padded
python3 _tools_vi/assemble_vi.py --version 2               # 22/22 units, block counts = source
python3 ../../_tools/check_continuity.py --workspace .     # ledger consistent, COMPLETE
```

- Whole-book checks: the refrain "chẳng có gì sắp đến" appears 5 times, as "nothing is due" does in the English, and
  "sắp đến" appears nowhere else (gated); the opening row is byte-identical to the closing row; Part Three's quoted
  rows carry the prose lines word for word (wrapped quotes are rejoined for the check); the only em dash is the
  author's own "—" null in XVI's depth row; no "...", no ASCII quotes, “ ” balanced; NFC and one tone-mark style
  throughout.
- R16's rulings are gate rows or FORBID lines (R.hole, R.sorted, R.bellman, R.likeanything; "sắp đến" outside the
  refrain, "làm chuyện ấy", plural "các cô", the noun "cái sóng đôi", the Southern "lầu"), each mutation-tested to
  fail.
- The vendored Cormorant Garamond (Light and Bold) has a glyph for every character of the master except "µ", which
  sits only in XVII's rows (as in the English) and is set in the code face.
- Not done here: the rendered-page checks of §16 (print, Kindle, EPUB), because nothing was produced.

## Open decisions for the author (D-rows)

- **D1** The title *Cách nhau năm tiếng* ("five hours apart", the plain phrase for a time-zone gap); Part One shares
  it; Part Two is the refrain, *Chẳng có gì sắp đến*; Part Three is *Cứ cho là*, the book's "Say…".
- **D2** The pronouns (charter R2): the narration's "you" is *anh*; Iris and the narrator use *tôi / anh / cô*, never
  *em*; father and son *bố / con*. The cost: both blind back-translators read the narration's *anh* as "he", so the
  English second person reaches a Vietnamese reader as close third-person narration. `_qa/PRONOUN_SAMPLES.md` shows
  the meeting scene in this scheme and in two others (*bạn* narration; *anh / em* dialogue) in case you want to
  switch; a switch is a mechanical pass plus the gates.
- **D3** The refrain "nothing is due" is "chẳng có gì sắp đến" (nothing is about to arrive); the machine "expects"
  (dự kiến) while people wait (chờ, đợi), so Iris's "Đó là chờ đợi" lands on the distinction.
- **D4** Dialogue with the line dash "– " and Russian-style attribution ("– Tôi đây, – cô nói."); speech that sits
  inside a narration paragraph takes “ ”, because a paragraph is never split (block parity with the English).
- **D5** Fahrenheit, feet and miles kept, as the narrator would say them ("bảy mươi mốt độ F"; X names the scale).
- **D6** "Grok" kept as the car's wake word, as in the source; "sandbox" kept in English in X and XI, as an engineer
  says it.
- **D7** The rows: the capitalized lane codes that name a person or thing in the prose are Vietnamese (ANH, BỐ, LAN
  CAN, THỜI TIẾT, NHỎ, PHÒNG, TRÍ, ĐÈN, ĐẠI DƯƠNG); the channel and place codes stay as printed (SKY, WORLD, ORGAN,
  BADGE, CLOCK, BODY, KELVIN, DAL, LHR, LONDON, IRIS, DANA). Both back-translators noticed the split. XVIII's row
  "it has no I. it has her." is "nó không có cái tôi. nó có cô ấy."; "cái tôi" reads first as "the ego", which is
  close enough to keep.
- **D8** A final read by a human Vietnamese reader is recommended before print. The QA readers here were models; both
  register summaries judge the dialogue native and the narration "careful, warm … though not yet one they would take
  for a Vietnamese original" (the residual habit is English clause shape in the narrator's explanations, XI–XII).
- **D9** Whether KDP accepts a Vietnamese-language Kindle eBook, paperback and hardcover was not checked here; check
  the current KDP language list before planning the formats.
- **D10** The PDF export's title-page dateline (zh D2) is not in the markdown source and was not translated.

## Source-defect register

- **S1** VIII "Far out, where he pointed": no pointing occurs earlier (as the zh register found); translated as
  written, "nơi anh đã chỉ".
- **S2** Iris has been awake "twenty hours" in V and "twenty-four hours" in VI, about two story-hours apart; kept.
- **S3** XVI logs HIM "I don't know." at 19:05:12, but in XII the line comes before the 19:04:43 fork; the row's
  machine tokens are kept verbatim.
- **S4** (new) XIII .002 has the car waiting on Commerce "with its hazards on" and a driver who is tipped and sent
  home; XIII .004 then has the narrator take it "up the ramps" and through "the ticket arm" of a garage. Translated as
  written.

## Production (P7, P8): not part of this run

The master above is the single source for every format. Producing it needs the operator's Windows machine: Word COM
for DOCX → PDF and page counts, the local ComfyUI for cover art (CLAUDE.md), and a schema-valid `book_config.json`
for the edition (title, `lang` vi, Vietnamese cover typography). Two font checks belong there: the vendored Cormorant
Garamond covers Vietnamese (above), and the rows are set in `interior.code_font` (default Consolas); confirm in the
first proof that it renders the stacked Vietnamese diacritics (ữ, ặ, ở), or set a monospace face that does. Then §16:
look at the printed pages, the Kindle file and the EPUB.

## Evidence trail

Rulings log: `translation_charter_vi.md` (R1–R16). QA: `_qa/back/` (both halves + DONE_A/DONE_B),
`_qa/register/` (+ SUMMARY_A, SUMMARY_B), `_qa/MODERATOR.tsv`, `_qa/merge_r1.py`, `_qa/APPLY_r1.tsv`,
`_qa/PRONOUN_SAMPLES.md`. Briefs: `_brief/`. Drafts: `translation/drafts/` (append-only, 42). Ledger:
`_CONTINUITY.md`.

## Lessons from this run

1. Registry rows written at P1 for every multi-site locked line held: no locked line drifted in this edition (es had
   three). The one locked-form slip (X .017) came from the moderator's own QA row and was caught by the gate in the
   round.
2. In Vietnamese the dangerous errors are literal choices that collide with a fixed idiom (a reader takes the idiom's
   meaning): both lenses found them, and the back-translation finds them best, because the back-translator writes
   down the idiom's meaning.
3. A gloss that a reviewer proposes can carry a register trap the reviewer did not see (here a sexual euphemism); the
   moderator reads every replacement, not just every finding.
4. A word reserved for the refrain must be gated, or ordinary prose borrows it ("sắp đến" in XII .051).
5. Both register readers' summary writes were refused, as in es; the per-unit files carried everything.
