# Ship report: *Five Hours Apart* in German, de-DE (2026-10-07)

Method: `docs/BOOK_TRANSLATION_METHOD_v3.md`, runbook §6.1 (a fresh edition). Scope of this run: P0–P6 and P9 for
the text. Production (P7, P8: print, Kindle, EPUB, cover) was not run here; it needs the operator's Windows machine
(see the last section).

## What shipped

| edition | master (the single source every format must read) | sha256 | units | words |
|---|---|---|---|---|
| de-DE *Fünf Stunden Abstand* | `book_workspace/five_hours_apart_de/outputs/markdown/five_hours_apart_de_v2.md` | `e87ff2d63879aad45961f4643d81bf44930754ec027bd82b1612db5de4ba2b69` | 22 | 13,550 (EN 13,163, ×1.03) |

Subtitle *Ein Gedankenspiel, in drei Teilen*. Parts: *Erster Teil · Fünf Stunden Abstand*, *Zweiter Teil · Nichts
steht an*, *Dritter Teil · Sagen wir*. Source of record: the same frozen English as the zh, es and vi editions (515
segments, `_key/segments.jsonl`, sha256 `6ed2feb4…`). Every unit has exactly as many blocks as the source has
segments. The master is gitignored like the other editions' masters: rebuild it with
`python3 _tools_de/assemble_de.py --version 2` from `translation/current/`, which is committed.

## How it was made

- **P0** the frozen English segments, reused from the earlier editions (the source did not change).
- **P1** the key, built by the moderator: `translation_charter_de.md` (the law; rulings R1–R16 in its log),
  `_key/registry_de.tsv` (186 rows: names, places, the 22 headings, field terms, locked lines, the language-neutral
  meaning rulings imported from the zh, es and vi editions), the row glossary (`ROWS` in `_tools_de/de_common.py`,
  charter §10), the locked lines (§11). Every locked line with two or more sites was a registry row from the start
  (lesson 23.5).
- **P2** a per-unit gate and a whole-book gate (`_tools_de/gate_de.py`: words against English words, German quotation
  marks „…“ and ‚…‘ balanced, no dash of any kind in prose, the comma after the closing quote, NFC, translationese
  and formal-Sie warnings, the row glossary and columns, the refrain count, the lines the rows quote from the prose,
  the echoes, the opening row against the closing row) with a must-fail battery (`_tools_de/test_gate_de.py`: 20
  defect cases on XII and 15 on a copy of the whole book, each with a clean control).
- **P3/P4** the moderator translated all 22 units (R15) and gated each to PASS with 0 WARN; drafts are append-only
  (43 files).
- **P5** quality assurance by four independent agents, every accepted finding applied as count-asserted rounds
  (`_tools_de/apply_de.py` → `_tools/unit_patch.py`, one patch per unit; `_qa/merge_r1.py` records every decision):

| report | what it is | findings | applied | outcome |
|---|---|---|---|---|
| `_qa/back/` (A: front–IX, B: Part Two–XVIII) + `_qa/MODERATOR.tsv` | blind back-translation, then the moderator's English-against-English diff of every unit (`_tools_de/backdiff_view.py`) | 28 moderator rows: wrong antecedents, two-way subject/object "es", idiom collisions, a Celsius misreading, a lost motif | 25 (3 superseded by the register's wording), plus 3 follow-ups (`_qa/APPLY_r2.tsv`) and one row term | R16 |
| `_qa/register/` + `SUMMARY_A.md`, `SUMMARY_B.md` | two German native-register, copy-edit and seam reads, one per half | 94: 4 BLOCK, 60 FIX, 30 NIT | 90 (4 with a different replacement); 4 duplicates of moderator rows; none declined | R16 |

  What the lenses found. The back-translation found the errors German grammar creates out of loose English
  reference: a pronoun whose gender or case offers an antecedent the English never had ("dass sie auf der Liste
  steht" read as *she* is on the list, VI .064; "Hast du sie gehört?" read as Iris, XIII .008; the screen as "es",
  I .015; "sein ganzes Leben" read as the father's, XIII .021), and neuter subject and object that swap ("Nur was es
  nicht selbst geschrieben hat, darf es formen", XII .044, and the same rule in XV's rows). It also found a bare
  "Fünfundfünfzig Grad" that a German reader takes as Celsius (X .008) and "Sonntagnacht" for the night of the
  clock change, which German reads as the night into Monday (XII .080). The register readers found the polarity
  error on XIV's key line („Mehr weiß es nicht. Du auch.“ → „Du auch nicht.“), the two BLOCKs of IX .006 (nobody
  tells themselves it is fine; the arm switches the arm), and most of the idiom collisions: "vor der Wende" (before
  1989), "Bis hierhin und nicht weiter" (a rebuke), "Es war sehr warm" (the weather), "aus dem Nichts" (out of
  nowhere), "Jede Ankunft hat umgedreht" (a flight that turns back), "keinen Preis geben" (award no prize),
  "Rechnungen" (invoices), "wer dahinter ist" (who is behind it all).
- **P6** the moderator's read: the English-against-English diff of all 22 units, a reading of every flagged block in
  the German, and a reading of every patched paragraph in context after the round.

## Verification (mechanical, all green on the final text)

```
cd book_workspace/five_hours_apart_de
python3 _tools_de/gate_de.py --book translation/current   # 22 units PASS, 0 FAIL, 0 WARN; BOOK 0 FAIL
python3 _tools_de/test_gate_de.py                          # battery: ALL CASES BEHAVE (unit + book cases)
python3 _tools_de/rows_de.py <unit> --fix                  # front ch_12 ch_14 ch_15 ch_16 ch_17 ch_18: 0 blocks re-padded
python3 _tools_de/assemble_de.py --version 2               # 22/22 units, block counts = source
python3 ../../_tools/check_continuity.py --workspace .     # ledger consistent, COMPLETE
```

- Whole-book checks: the refrain "nichts steht an" (once inverted, "steht nichts an", where German word order forces
  it) appears 5 times, as "nothing is due" does in the English; the opening row is byte-identical to the closing row;
  Part Three's quoted rows carry the prose lines word for word (wrapped quotes are rejoined for the check); 349 pairs
  of „…“ in the prose and 13 pairs of “…” in the rows, balanced; no "...", no ASCII quote; the only dashes are the
  rows' two time ranges (en dash, as printed) and the author's own "—" null in XVI's depth row; NFC throughout.
- R16's rulings are gate rows, ROWS tokens or FORBID lines (registry R.behind; the row terms "Selbstgeschriebenes
  prägt nicht", "Zeitscheibe", "über die Mitte hinaus", "Etikettenstreifen"; FORBID "vor der Wende", "bis hierhin und
  nicht weiter", "wer dahinter ist", "eigenen Rechnungen", "aus dem Nichts"; echo pairs II/XII, VII/XIII, III/IX),
  each mutation-tested to fail in the battery.
- The vendored Cormorant Garamond (Light and Bold) has a glyph for every character of the master except "µ", which
  sits only in XVII's rows (as in the English) and is set in the code face.
- Not done here: the rendered-page checks of §16 (print, Kindle, EPUB), because nothing was produced.

## Open decisions for the author (D-rows)

- **D1** The title *Fünf Stunden Abstand*: "Abstand" is a gap in space and time and, in German, also the distance
  people keep from each other; both back-translators noticed the second reading, which suits the book. The
  alternatives are flatter: *Fünf Stunden Zeitunterschied*, *Fünf Stunden auseinander*. Part One shares the title;
  Part Two is the refrain, *Nichts steht an*; Part Three is *Sagen wir*, the book's "Say…". The subtitle *Ein
  Gedankenspiel, in drei Teilen* keeps the English comma (one back-translator found it slightly translated, the
  register reader passed it); *Gedankenexperiment* is the standard word for a thought experiment, *Gedankenspiel* is
  the lighter one and fits "Say…".
- **D2** Address (charter R2): the narration is "du", lowercase, present tense; Iris and the narrator say "du" from the
  first line (colleagues in a tech company; neither reviewer questioned it; "Sie" at the arrivals door, moving to "du"
  later, would be the conservative alternative and a real rewrite of IV–VII); father and son "Papa" / "Junge".
- **D3** The refrain "nothing is due" is "nichts steht an" (nothing is on the schedule); one back-translator heard a
  touch of office register in "anstehen", which is the machine's word for its calendar. The machine "erwartet"
  (Erwartung) while people "warten", so Iris's „Das ist Warten“ lands on the distinction.
- **D4** Typography: „…“ with ‚…‘ nested and the comma after the closing quote („Das bin ich“, sagt sie.); no dash
  of any kind in prose (your rule; asides take commas, colons or a new sentence; interrupted speech ends " …").
- **D5** "Heavy" kept for the aircraft class, as pilots say it ("ein Heavy", "das Heavy"); one back-translator found
  it opaque on its own, and the book explains it in III (the father says *Heavy* before you can see it). Fahrenheit,
  feet, miles and yards kept; Fahrenheit is named where a German reader would assume Celsius (IV; X, now also in
  Iris's „Fünfundfünfzig Grad Fahrenheit.“). "Freeway" kept; "Grok" kept as the car's wake word; "Sandbox", "Fix",
  "Paper", "Hash" as a German engineer says them.
- **D6** The rows: the capitalized codes that name a person or thing in the prose are German (ER, VATER, GELÄNDER,
  WETTER, KLEIN, RAUM, GEIST, LAMPE, OZEAN); the channel and place codes stay as printed (SKY, WORLD, ORGAN, BADGE,
  CLOCK, BODY, KELVIN, DAL, LHR, LONDON, IRIS, DANA). Both back-translators noticed the split, and one found "ER" odd
  as a speaker tag. "Raum" is both room and space, so XVI's title, the rows' "Raum" and XVIII's last sentence carry
  both readings (the English "room" carries "space" more faintly).
- **D7** A final read by a human German reader is recommended before print. The QA readers here were models. Both
  register summaries judge that the text reads "as a book written in German" for most of its length, and that with
  the fixes applied it "would pass as original German" (A) and can go "in front of a German reader without apology"
  (B); the residue they named is English clause shape in the long descriptive paragraphs of I–III and in the
  engineer's explanations in XI–XII.
- **D8** German is a KDP language (amazon.de); check the current KDP terms for German hardcover before planning the
  formats.
- **D9** The PDF export's title-page dateline (zh D2) is not in the markdown source and was not translated.

## Source-defect register

- **S1** VIII "Far out, where he pointed": no pointing occurs earlier (as the zh register found); translated as
  written, with "vorhin" so that "er" is the man and not the freeway ("wohin er vorhin gezeigt hat").
- **S2** Iris has been awake "twenty hours" in V and "twenty-four hours" in VI, about two story-hours apart; kept.
- **S3** XVI logs HIM "I don't know." at 19:05:12, but in XII the line comes before the 19:04:43 fork; the row's
  machine tokens are kept verbatim.
- **S4** XIII .002 has the car waiting on Commerce with its hazards on and a driver who is tipped and sent home; XIII
  .004 then has the narrator take it "up the ramps" and through "the ticket arm" of a garage. Translated as written.
- **S5** (new) XIV .006 "At the top of the record, under the row that says *quiet* at 19:15, there's one more"
  contradicts itself (the new row is newer than 19:15, so it cannot be both at the top and under it). The German
  says "Am Ende des Protokolls, unter der Zeile …" (at the newest end).

## Production (P7, P8): not part of this run

The master above is the single source for every format. Producing it needs the operator's Windows machine: Word COM
for DOCX → PDF and page counts, the local ComfyUI for cover art (CLAUDE.md), and a schema-valid `book_config.json`
for the edition (title, `lang` de, German cover typography). One setting matters more in German than in the other
editions: the Word document language must be German (de-DE) so that Word hyphenates the long compounds correctly
(Schubhebelquadrant, Überflutungsgebiet, Etikettenstreifen); check the first proof for bad breaks. The rows are set in
`interior.code_font` (default Consolas), which covers the umlauts, ß and „ “. Then §16: look at the printed pages, the
Kindle file and the EPUB.

## Evidence trail

Rulings log: `translation_charter_de.md` (R1–R16). QA: `_qa/back/` (both halves + DONE_A/DONE_B),
`_qa/register/` (+ SUMMARY_A, SUMMARY_B, saved by the moderator because both reviewers' summary writes were
refused), `_qa/MODERATOR.tsv`, `_qa/merge_r1.py`, `_qa/APPLY_r1.tsv`, `_qa/APPLY_r2.tsv`. Briefs: `_brief/`. Drafts:
`translation/drafts/` (append-only, 43). Ledger: `_CONTINUITY.md`.

## Lessons from this run

1. In German the main error class is the pronoun antecedent: English "it", "she" and "they" carried over become
   "es", "sie" and "er", whose gender and case offer antecedents the English never had, and a neuter subject and
   object ("es … es") swap freely. The blind back-translation finds these best, because the back-translator writes
   down the wrong referent.
2. Idiom collisions were again the most dangerous errors ("vor der Wende", "bis hierhin und nicht weiter", "es war sehr
   warm", "aus dem Nichts", "der Flug dreht um", "dahinterstecken", "Rechnungen"); both lenses found them, and each is
   now a FORBID line or a registry row.
3. On a key line a native's terse fix beats the moderator's paraphrase: for XIV .011 the moderator had written „Du
   weißt genauso viel.“, the register reader „Du auch nicht.“; the merge took the reader's.
4. A reviewer withdrew a correct finding to protect an echo it found in the rows ("Etikettstreifen", XI and XV); the
   moderator changed both sites instead, which keeps the echo and the fix.
5. Both register readers' summary writes were refused, as in es and vi; the per-unit files carried everything.
