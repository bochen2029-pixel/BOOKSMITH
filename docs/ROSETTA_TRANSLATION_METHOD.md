# ROSETTA TRANSLATION METHOD — EN→ZH edition of a synthesis book whose ideas were mined FROM the target language

*Written 2026-07-28 for the first instantiation: `the_crossing` → 简体中文 edition (then s2tw → 繁體).
The method generalizes to any BOOKSMITH synthesis book whose source corpus is in the target language.
Companion law: CLAUDE.md (gates, autonomy), docs/SUPERSTRUCTURE.md (model policy: subagents = Opus/Sonnet, NEVER Fable), docs/COMPACTION_SURVIVAL.md (ledger discipline).*

---

## 0. The central claim (why this is not "translation")

*The Crossing* was **synthesized from Ben Jin's Chinese corpus**. Its concepts, anecdotes, and many of its
sentences are English derivations of Chinese originals that exist, verbatim, in the atom ledger and in his
three published books. Rendering it "back" into Chinese is therefore **restoration, not translation**:
wherever a passage derives from an atom, the correct Chinese is *the author's own sentence*, not a fresh
paraphrase. Only the connective tissue (the newly authored argument) is genuinely translated, and it must
be translated INTO the register documented by his native prose.

This is the strictly-better-than-any-external-tool guarantee: an outside translator (human or AI) sees only
the English. We hold the key the English was encrypted from.

## 1. The asset map (the rosetta stone, with exact paths)

| Layer | Asset | Path | Role |
|---|---|---|---|
| SOURCE (what to translate) | 25 EN units, v3-current | `book_workspace\the_crossing\manuscript\current\*.md` | the only base text |
| | version-pinned master v6 (60,821w) | `book_workspace\the_crossing\outputs\markdown\the_crossing_v6.md` | parity baseline |
| KEY (the author's own words) | Idea Ledger, ~1,139 zh atoms + 102 en atoms | `C:\ACCESSINTELLECT\DRDJ\Books\CHUNKED\_synthesis\Idea_Ledger.jsonl` (878KB) | per-passage restoration source |
| | Chapter Map (crossing unit → atom ids) | `..._synthesis\Chapter_Map.md` | which atoms feed which unit |
| | EN↔ZH integration ledger (投资篇 英文版) | `..._synthesis\LEDGER_INTEGRATION_投资篇_英文版.md` | bilingual parallel corpus for terminology |
| ATLAS (register/voice) | Jin Voiceprint | `..._synthesis\Jin_Voiceprint.md` | native register spec |
| | 人生篇 native prose, 36 units | `book_workspace\drdj_life\manuscript\current\` | life/relationship register exemplars |
| | 投资篇 native prose, 42 units | `book_workspace\drdj_investing\manuscript\current\` | investing register exemplars |
| | 教育篇 native prose, 38 units | `book_workspace\drdj_education\manuscript\current\` | parenting/education register exemplars |
| CANON | Name canon | `..._synthesis\NAME_CANON.md` + memory `author-name-ben-jin` | 金冰 / Ben Jin; Western-name renderings |
| WITNESS (never the base) | Jimmy's zh draft, 177pp, v3-derived (verified: all 4 MoS section headings + 市场先生 present) | `C:\BOOKSMITH\intake\seethis渡—The Crossing.pdf` | independent completeness witness + phrase mine |
| TOOLING | s2tw fork, CJK lint, scan, builders | `_tools\s2t_fork.py`, `lint_manuscript.py`, `scan_manuscript.py`, `generate_kindle.js`, `build_epub.py` | the production line |

## 2. Principles (binding)

1. **EN v3 units are the sole base text.** Jimmy's draft is a witness and a phrase mine, never copied structurally.
2. **Charter before prose.** No unit is translated before the Translation Charter (§4) is ratified. Every locked
   rendering in the charter outranks any agent's in-unit judgment.
3. **Restoration beats invention.** Where the Chapter Map ties a passage to atoms, the atom's original Chinese
   wording is used or closely echoed. Deviation requires a logged reason.
4. **Translate ONCE (Simplified), fork mechanically (s2tw) for Traditional.** Two independent translations would drift.
5. **Structure is invariant.** Unit count, H1/H3 heading structure, image lines (`![...]` paths byte-identical),
   paragraph count parity (±1 with logged reason), refrain placements. The zh edition is the same book.
6. **CJK conventions replace EN lint rules.** `no_em_dashes:false` (破折号 is legitimate zh punctuation); full-width
   punctuation; Mainland Simplified orthography; numbers per Jin's native habit (arabic digits in stats, 汉字 in idiom).
7. **The author is the perceptual gate.** Jin's native read is the final QA layer; the pipeline's job is to make
   that read find nothing mechanical to trip on.
8. **Model policy.** Main loop (Fable) = charter, gates, review, integration, stitching. Drafting subagents = **Opus,
   never Fable** (SUPERSTRUCTURE Phase 0 / matrix #24). Every agent writes-to-disk-THEN-returns (crash-safe).
9. **Confidentiality.** Pre-publication drafts stay inside the working group (Jin's standing rule).

## 3. Phase 0 — Setup (mechanical, ~minutes)

1. Fork workspace: `book_workspace\the_crossing_zh\` — copy config; set `language:"zh"`, `author:"金冰"`,
   `formats:["kindle","epub"]`, `voice.no_em_dashes:false`; title provisionally `渡口` with subtitle field carrying
   the open decision (§4.6). Copy `images/` refs (chapter art is language-neutral). Empty `manuscript/`.
2. Extract Jimmy's zh text per-unit: fitz walk of his PDF split by its own TOC → `canon_refs\jimmy_zh\{id}.txt`
   (25 files). These are REFERENCE files, gitignored with the workspace.
3. Stage atom slices: from Chapter_Map, emit per-unit atom files `canon_refs\atoms\{id}_atoms.md` (atom id +
   original zh + the EN sentence it became, where mapped). Keeps each drafting agent's pack small.
4. Initialize `_CONTINUITY.md` (COMPACTION SURVIVAL ledger) with this spec as the RESUME pointer.

## 4. Phase 1 — The Translation Charter (the keystone; main loop builds, ~1 session-hour)

Written to `book_workspace\the_crossing_zh\translation_charter.md`. Sections:

1. **Term canon (glossary).** For every load-bearing term, lock ONE rendering, sourced in priority order:
   (a) Jin's own usage grepped from the three native books + integration ledger (e.g. 安全边际, 能力圈,
   市场先生, 复利, 顺势而为, 一人一文明 — the last is literally his chapter title in 人生篇);
   (b) established zh convention; (c) fresh coinage (logged). Record source-of-truth per term.
2. **Title + heading table.** All 25 unit titles + all 67 in-chapter H3 headings pre-translated HERE, once.
   Every agent uses the table verbatim; consistency cannot then drift by agent. (Jimmy's renderings consulted;
   e.g. his 一个决策的第一要务 for "The first duty of a decision" is good and may be adopted consciously.)
3. **Refrain + motif law.** 渡人渡己 exact at the EN refrain placements (readers-note, prologue close, epilogue
   close, practice); locked renderings for recurring images (the four rivers, the rising river, the lamp, the
   ferryman lexicon 渡口/摆渡人/渡行); callbacks vary wording in zh exactly where EN varies it.
4. **Voice spec for translation.** Distilled from Jin_Voiceprint + native prose: short declaratives; 白话 body with
   四字 seasoning at beats; his connective habits; rhetorical-question ration as in EN; his punctuation habits
   (，。：“”、и 破折号 usage as observed in his books); paragraph lengths mirroring the EN's breathing.
5. **Names/numbers canon.** 金冰 byline; Western names as HE renders them in 投资篇 (巴菲特/芒格/格雷厄姆 …);
   book titles as he cites them; statistics keep EN values + denominators.
6. **Open decisions ledger (for Jin, not for agents).** Book title 《渡口》 (site canon) vs 《渡》(Jimmy's draft)
   vs 《渡口：AI时代的人生摆渡方法》; 后记 title style; any term where his books disagree with convention.
7. **Harvest-from-Jimmy adjudications.** Where Jimmy's rendering of a charter item differs from ours, one line each:
   kept-ours / adopted-his / hybrid, with reason. (Makes "strictly better" auditable, not asserted.)

Charter build protocol: targeted Python/Select-String sweeps over the native corpus (the workspace is gitignored —
rg misses it; use scripts), NOT full reads; the three books total ~370K chars and are sampled, not ingested.

## 5. Phase 2 — Per-unit translation loop (Opus agents, waves)

**Wave plan:** 25 units in 4 waves of 6-7, dependency-light because seam wording is inherited from the EN (the
residue/callback structure already lives in the source; the charter locks its renderings). Load-bearing units
(prologue, ch_14, ch_16, epilogue, colophon, practice) go in the LAST wave so the charter + accumulated
adjudications are at their richest, and get the deepest review.

**Context pack per agent (self-sufficient; ~15-25K tokens):**
- The EN unit (full). The charter (full). This unit's atom file. This unit's Jimmy reference file (labeled:
  witness/phrase-mine only). 2-3 native exemplar passages matched to the unit's register (life/invest/edu per the
  unit's braid tags). The zh of unit N−1 if already on disk (tail 500 chars suffices), else the EN tail of N−1.
- Standing instructions: restore-over-invent where atoms map; charter table for every heading/term/motif; preserve
  structure + image lines byte-identically; CJK punctuation; no English left except intentional loanwords per
  charter; write `manuscript/drafts/{id}_v1.md` THEN return a 10-line self-report (terms touched, atoms restored
  count, uncertainties flagged, Jimmy divergences noticed).

**Main-loop gate per unit (bounded 3-iteration fix loop):**
- Mechanical (scripted): H1/H3 count parity vs EN; image-line byte parity; paragraph count within ±1/logged;
  charter-term conformance grep; refrain exact/absent per placement law; zero stray Latin sentences; 金冰 canon;
  CJK char sanity; lint (CJK mode) clean.
- Perceptual (Fable, me): full read of the zh against the EN for the load-bearing units, deep-sample read
  (open/close + 2 random middles) for connective units; register check against the native exemplars.
- Pass → promote to `manuscript/current/{id}_current.md`, update `_CONTINUITY.md` (after EVERY unit).

## 6. Phase 3 — Integration, QA, fork, production

1. **Seam pass** (main loop): each boundary read as one zh passage.
2. **Refrain audit**: exact strings at exact placements, nowhere else (scripted + eye).
3. **Glossary sweep**: every charter term's EN occurrence count == its zh rendering count (scripted).
4. **Tri-text completeness diff** (the witness earns its keep): per unit, paragraph-align EN / ours / Jimmy.
   Anything present in EN+Jimmy but missing in ours = omission bug. Material meaning divergence between ours and
   Jimmy = adjudicate against EN + atoms; log verdicts.
5. **Back-translation audit** (Opus agents, blind): load-bearing passages + 10 random paragraphs → zh→EN blind →
   diff vs source for meaning drift.
6. **Atom-fidelity audit**: sampled mapped passages verified to actually echo the atom wording.
7. **Gates**: `scan_manuscript` (structure) + `lint_manuscript` (CJK) + assemble (parity baseline vs EN word count
   expectation ~1.6-1.9 chars/word band, logged not blocking).
8. **s2tw fork**: `python _tools\s2t_fork.py --src-config book_workspace\the_crossing_zh\book_config.json
   --dst-slug the_crossing_zht` → audit log; spot-read 3 units for variant-character correctness.
9. **Produce** (both scripts): `generate_kindle.js` + `build_epub.py` + `verify_build --format kindle|epub`
   (mid-flow images embed; covers = zh typography variant via the compositor with the CJK serif on file; kindle
   1600×2560). Print interiors deferred to the IngramSpark decision.
10. **Ship report**: unit QA table + charter + adjudications + open-decisions page for Jin. His read is the gate;
    daughter/son remain the EN gate. Both feed one v-next revision fan-out.

## 7. Execution modes + resource math (2026-07-28 reality)

- **Managed fan-out (RECOMMENDED).** Main loop stays Fable (charter, gates, reviews, integration — the judgment
  work); 25 Opus drafting agents + ~8 QA agents in waves. Keeps the main context lean (agents ingest the packs;
  I ingest self-reports + review reads), survives compaction via the ledger, and spends Opus rather than the
  63%-consumed Fable weekly budget for the bulk tokens.
- **Solo in-session.** Fits neither comfortably nor safely today: session already at ~41% of 1M before drafting
  ~110K chars of zh + reviews; would force mid-book compaction and burn the Fable budget on mechanical drafting.
  Reserved as fallback for single-unit hotfixes.
- **Timeline shape:** Phase 0+1 one sitting; Phase 2 four waves; Phase 3 one sitting. Comfortably a one-to-two
  day project at current limits.

## 8. Definition of done ("strictly better than the witness", auditable)

☐ 25/25 units on disk, gated, promoted; ☐ charter ratified + adjudication log nonempty;
☐ zero omissions in the tri-text diff (witness-verified completeness);
☐ atoms restored wherever mapped (audit sampled); ☐ refrain/motif law exact; ☐ glossary sweep clean;
☐ lint+scan+verify green for zh-Hans AND zh-Hant artifacts; ☐ open-decisions page ready for Jin (title, etc.);
☐ `_CONTINUITY.md` COMPLETE; ☐ nothing published — Jin's read + family EN sign-off remain the human line.
