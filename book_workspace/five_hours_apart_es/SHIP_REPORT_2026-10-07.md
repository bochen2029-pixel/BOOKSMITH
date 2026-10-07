# Ship report: *Five Hours Apart* in Latin American Spanish, es-419 (2026-10-07)

Method: `docs/BOOK_TRANSLATION_METHOD_v3.md`, runbook §6.1 (a fresh edition). Scope of this run: P0–P6 and P9 for
the text. Production (P7, P8: print, Kindle, EPUB, cover) was not run here; it needs the operator's Windows machine
(see the last section).

## What shipped

| edition | master (the single source every format must read) | sha256 | units | words |
|---|---|---|---|---|
| es-419 *Cinco horas de diferencia* | `book_workspace/five_hours_apart_es/outputs/markdown/five_hours_apart_es_v2.md` | `501c5a29b8f051b2c058874a70ca7031e89989e0acb2ae2449c76f140e080a3c` | 22 | 13,728 (EN 13,163) |

Subtitle *Un supuesto, en tres partes*. Source of record: the same frozen English as the Chinese editions (515
segments, `_key/segments.jsonl`, sha256 `6ed2feb4…`, copied from the zh-Hant key). Every unit has exactly as many
blocks as the source has segments. The master is gitignored like the other editions' masters: rebuild it with
`python3 _tools_es/assemble_es.py --version 2` from `translation/current/`, which is committed.

## How it was made

- **P0** the frozen English segments, reused from the zh editions (the source did not change).
- **P1** the key, built by the moderator: `translation_charter_es.md` (the law; rulings R1–R18 in its log),
  `_key/registry_es.tsv` (names, places, the 22 headings, field terms, locked motifs, the language-neutral meaning
  rulings imported from zh-Hant), the row glossary (charter §10), the locked lines (§11).
- **P2** a per-unit gate and a whole-book gate (`_tools_es/gate_es.py`) with a must-fail battery
  (`_tools_es/test_gate_es.py`: 18 unit cases on XII and 5 book cases). The row realigner `_tools_es/rows_es.py`
  re-pads every row block against the English columns.
- **P3/P4** the moderator translated all 22 units (R15) and gated each to PASS; drafts are append-only (41 files).
- **P5** quality assurance by three independent agents, every accepted finding applied in one count-asserted round
  (`_tools_es/apply_es.py` → `_tools/unit_patch.py`, one patch per unit; `_qa/merge_r1.py` records every decision):

| report | what it is | findings | applied | outcome |
|---|---|---|---|---|
| `_qa/back/` (A: front–IX, B: Part Two–XVIII) + `_qa/MODERATOR.tsv` | blind back-translation, then the moderator's English-against-English diff (`_tools_es/backdiff_view.py`); plus the moderator's full read | no meaning reversed; 41 rows from the diff (ambiguous pronouns, calques, regional words, drifted echoes) + 9 from the full read | 42 (8 superseded by the register's wording) | R18 |
| `_qa/register/` + `SUMMARY.md` | a Latin American native-register, copy-edit and seam read of the whole book | 2 BLOCK, 35 FIX, 24 NIT | 2 BLOCK, 28 FIX, 18 NIT (8 duplicates of moderator rows; 5 NIT declined) | R18 |

  The register review's two BLOCKs: VI .051 "tratarse de" with a subject (DPD: impersonal) and XV .003 "nada con
  qué medirlo" (a relative, no accent). The most useful finding: three of the moderator's own locked lines had
  drifted at their second site (the father's "—Un pesado, del sur.", the handshake's "de la duración exacta" /
  "el tiempo exacto", I/XIV "blancas en tu dirección y rojas en la otra"); all restored and now gated.
- **P6** the moderator's full read (Part One read again after the context reset; Parts Two and Three through the
  back-translation diff), and a read of every patched sentence in context after the round.

## Verification (mechanical, all green on the final text)

```
cd book_workspace/five_hours_apart_es
python3 _tools_es/gate_es.py --book translation/current   # 22 units PASS, 0 FAIL, 0 WARN; BOOK 0 FAIL
python3 _tools_es/test_gate_es.py                          # battery: ALL CASES BEHAVE (unit + book cases)
python3 _tools_es/rows_es.py front ch_12 ch_14 ch_15 ch_16 ch_17 ch_18   # 0 blocks re-padded
python3 _tools_es/assemble_es.py --version 2               # 22/22 units, block counts = source
python3 ../../_tools/check_continuity.py --workspace .     # ledger consistent, COMPLETE
```

- Whole-book checks: the refrain "nada está por llegar" appears 5 times, as "nothing is due" does in the English;
  the opening row is byte-identical to the closing row; Part Three's quoted rows carry the prose lines word for word
  (wrapped quotes are rejoined for the check); the only em dashes are the raya of the dialogue and the author's own
  "—" null in XVI's depth row; no «», no ASCII quotes, ¿? and ¡! paired, NFC throughout.
- R18's rulings are now gate rows (windowsill → repisa, council → comité, handshake → exacta/exacto, the father's
  "Un pesado, del sur."), and "pluma" / "maletero" are forbidden; each was mutation-tested to fail.
- Not done here: the rendered-page checks of §16 (print, Kindle, EPUB), because nothing was produced.

## Open decisions for the author (D-rows)

- **D1** The title *Cinco horas de diferencia* (the idiom for a time-zone gap), over *A cinco horas* and *Cinco horas
  de distancia*; Part One shares it; Part Three is *Digamos*.
- **D2** One Latin American Spanish leaning Mexican (carro, celular, manejar, estacionamiento, banqueta, credencial,
  "veinte para las cinco"), with the few Mexico-only words a reviewer flagged replaced by neutral ones (barrera,
  cargador de maletas). A Spain edition would be a sibling locale derived from this one (v3 §6.2), not a retranslation.
- **D3** The refrain "nothing is due" is "nada está por llegar"; the machine "expects" (previsión, prevé) while people
  wait (esperar), so Iris's "Eso es esperar" lands on the distinction.
- **D4** Dialogue with the RAE raya; speech that sits inside a narration paragraph takes “ ”, because a paragraph is
  never split (block parity with the English).
- **D5** Fahrenheit, feet and miles kept, as the narrator would say them; the scale is named twice (IV, X).
- **D6** "Grok" kept as the car's wake word, as in the source.
- **D7** XVIII's row "it has no I. it has her." is "no tiene un yo. la tiene a ella."; XVII's "(a Tuesday it wrote)"
  names the writer, "(un martes que escribió el cuarto)", because ÉL in those rows is the narrator.
- **D8** The PDF export's title-page dateline (zh D2) is not in the markdown source and was not translated.

## Source-defect register

- **S1** VIII "Far out, where he pointed": no pointing occurs earlier (as the zh register found); translated as
  written, "donde él señaló".
- **S2** Iris has been awake "twenty hours" in V and "twenty-four hours" in VI, about two story-hours apart; kept.
- **S3** XVI logs HIM "I don't know." at 19:05:12, but in XII the line comes before the 19:04:43 fork; the row's
  machine tokens are kept verbatim.

## Production (P7, P8): not part of this run

The master above is the single source for every format. Producing it needs the operator's Windows machine: Word
COM for DOCX → PDF and page counts, the local ComfyUI for cover art (CLAUDE.md), and a schema-valid `book_config.json`
for the edition (title, `lang` es-419, Spanish cover typography; the vendored Cormorant Garamond covers Spanish).
KDP publishes Spanish in Kindle, paperback and hardcover. Then §16: look at the printed pages, the Kindle file and
the EPUB.

## Evidence trail

Rulings log: `translation_charter_es.md` (R1–R18). QA: `_qa/back/` (both halves + DONE_A/DONE_B), `_qa/register/`
(+ SUMMARY), `_qa/MODERATOR.tsv`, `_qa/merge_r1.py`, `_qa/APPLY_r1.tsv`. Briefs: `_brief/`. Drafts:
`translation/drafts/` (append-only, 41). Ledger: `_CONTINUITY.md`.

## Lessons from this run

1. A moderator who writes the charter can still drift from it: three locked lines came back reworded at their second
   site and only the register reviewer, checking the charter's §9/§11 against the text, caught them. Every locked
   line with two or more sites should be a registry row from the start, not a charter sentence.
2. Back-translators find ambiguity, register reviewers find drift and grammar: the two reports overlapped on only 8
   of ~100 findings. Run both.
3. A reviewer that writes one file per unit loses nothing when its last write is refused (the register SUMMARY came
   back as text and was saved by the moderator).
4. Wrapped quotes in a fixed-width row defeat a substring check; the gate now rejoins them before the term and echo
   checks (and the battery proves it).
