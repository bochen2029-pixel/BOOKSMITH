# DELTA AUDIT — Second Notebook memories + C:\BOOK\BUILD_LOG.md vs the kit ledger

*Produced 2026-07-12 (Sunday), Central. Method: READ-in-full (not grep) of `C:\BOOK\BUILD_LOG.md` (365 lines, the ATD problem→fix log), the four Second-Notebook / Titanic memory files, cross-checked against `docs/LESSONS_LEDGER.md` §1–§17.*

**Scope rule honored:** §17 already bakes no-em-dashes (hard gate), no-images, no-tricolons, the forbidden-phrase blacklist, and the voice fingerprint (F1–F6). Those are NOT re-reported. Everything below is a prose/craft/production lesson **absent or weaker** in the ledger. Each delta: the lesson (verbatim where it matters) · source · what the ledger has · exact bake-in.

Deltas are ordered by load-bearing weight. D1–D6 are the strong ones; D7–D12 are smaller but real.

---

## D1 — The "clinical-distance" failure mode + the deliberate peak-amp revision pass  ★ TOP DELTA

**Lesson (verbatim, BUILD_LOG v1.2):** *"v1.1's correction against the romantic-narrative misreading produced rendering at clinical distance from the configuration's peak. The framework specifies the n=2 collapse at peak as the substrate's highest registered experiential form; v1.1 specified it but did not render it at the intensity the specification requires. Both readerships failed: readers who experience the peak did not see their experience reflected at the rendering's intensity; readers who have not experienced it did not encounter the framework's claim at the altitude the framework was making it."*

The correction was a whole named revision pass — "peak-aliveness rendering" (v1.2, +1,581 words) — that **amped** the highest-stakes passages to the altitude the thesis claims, WITHOUT re-introducing the failure mode it was originally correcting against. The compliance checklist that made the amp safe (verbatim):
- *"No re-introduction of romantic-narrative failure mode (rendering preserves alterity, third-object grounding, refusal of fusion-as-ideal, refusal of cosmic-grace framing)."*
- *"No genre-romance vocabulary (no passion, yearning, desire-as-cliché, bodice-ripper imagery, melodrama, exclusivity-claim, soulmate-framing)."*

**Source:** `C:\BOOK\BUILD_LOG.md` §"v1.2 revisions (peak-aliveness rendering pass)" (lines 320–360), corroborated by `feedback_prose_discipline.md`: *"Run hot or run cold; never lukewarm."*

**What the ledger has:** ABSENT as a craft rule. §7 lists the anti-AI-tell techniques and §2.7 the banned vocabulary, but there is no rule that **over-correction toward safety/clinical-neutrality is itself a defect**, and no notion of a dedicated intensity-calibration pass. The ledger's only trace of v1.2 is line 311 — recorded purely as a *mechanical* cover-obsolescence event (416→448pp), the craft cause stripped out.

**Exact bake-in:** New §7 technique (call it #10, "Intensity calibration / no clinical distance"): *"Each unit's peak must be rendered at the altitude its own thesis claims for it — the correction against a failure mode (sentimentality, romance-cliché, hype) must not overshoot into clinical distance, which fails both readerships: those who know the peak don't see it reflected, those who don't aren't shown the claim at its real altitude. Run hot or run cold; never lukewarm. When a load-bearing passage reads safe-but-flat, run a scoped amp pass gated by an explicit anti-failure-mode checklist (preserve the structural guards; ban the genre vocabulary) so intensity rises without the original defect returning."* Add to CLAUDE.md §7's "Never do" list: *over-hedged clinical neutrality at an emotional peak*. Optional verifier note: a peak unit whose register never leaves "measured/analytical" is a flag for an amp pass.

---

## D2 — Greenlist / sacred phrases are DEPLOYED at deliberate weight (not merely "allowed")

**Lesson:** BUILD_LOG treats the greenlist as an active authorial instrument, placed at calculated maximum-impact moments and defended in-text against misreading. Verbatim (v1.2 compliance): *"Greenlist phrases used at intentional weight ('It is so very beautiful' admitted at peak; 'highest of highs' admitted at peak)."* And Ch 3's amp (line 328): *"the configuration at peak as 'so very beautiful' with structural defense of the phrase against sentimentality readings."* The Phase-A greenlist was 8 curated canonical lines (e.g. "The math is the math. The people are the point." / "The rest is boundary conditions." / "It is so very beautiful.").

**Source:** `C:\BOOK\BUILD_LOG.md` lines 29, 328–329, 341.

**What the ledger has:** WEAKER. Greenlist appears only as a static SEED §1 section to *render* and for `audit voice` to *read* (ledger lines 88, 91). There is no rule that greenlist phrases are positioned deliberately at peaks, reserved (not scattered), and defended structurally when a "sentimental-sounding" sacred line is used on purpose.

**Exact bake-in:** Extend §2.7 / §17.2. Add: *"The greenlist is an instrument, not just a permission. Reserve sacred/greenlist phrases for the exact beats where they land hardest (peaks, unit closes, refrain-adjacent lines); do not scatter them. When a greenlist line reads 'sentimental' out of context, that is intended weight — earn it with a structural defense in the surrounding prose rather than deleting it. A greenlist phrase burned early at low stakes is spent; treat placement as scarce."* Consider a `voice.greenlist_reserve` note in book_config for phrases reserved to specific units.

---

## D3 — Parallel drafting breaks callbacks: draft callbacks as concepts, then a mandatory concretization pass

**Lesson (verbatim):** *"Phase B-D chapters drafted callbacks as conceptual references (because prior chapters weren't yet drafted when later chapters wrote); Phase E revises with concrete phrasings from drafted chapters."* Worked example: *"Ch 11 opening references Ch 10's cathedral/scaffolding distinction conceptually; revise once Ch 10 v1 exists."* This is logged as a first-class, tracked integration task (each handoff carries a Layer-3 "Note for Phase E integration pass"), not an ad-hoc fixup.

**Source:** `C:\BOOK\BUILD_LOG.md` lines 167–171, 198–200, 206.

**What the ledger has:** PARTIAL. §2.7/§6 say callbacks must *vary the source wording* (exact quotation = AI tell), and GATE-4 catches orphan seeds/payoffs. But nothing addresses the **ordering hazard of non-linear / parallel drafting**: when unit N is written before unit N−k exists, its callback can only be conceptual, and there must be a dedicated later pass that swaps the concept for the concrete phrasing of the now-existing source. Without it, either the callback stays vague or (worse) a later linear reader fabricates a quote.

**Exact bake-in:** Add to §11 (version discipline) or GATE-4: *"When units are drafted out of order, callbacks to not-yet-written units are written as CONCEPTUAL references and flagged in that unit's handoff Layer 3 ('concretize vs {source unit}'). Before `check seams`/export, run a concretization pass that replaces each conceptual callback with a concrete phrasing lifted (and varied) from the now-drafted source. GATE-4 fails if any handoff still carries an open concretize-flag."* Add a checklist line to §14: "no open callback-concretization flags remain."

---

## D4 — Adversarial review returns findings the AUTHOR then patches surgically (and it changes the thesis's honesty, not just prose)

**Lesson:** Bo commissioned external multi-instance review (Gemini 2.5 Pro + two Claude 4.7 1M instances, 4 rounds). It surfaced substantive weaknesses that became **targeted Tier-1/Tier-2 text insertions**, e.g. *"the book-as-L1-artifact recursion being metaphorical by Ch 6's own criteria"* → an explicit self-acknowledgment inserted at Ch 22; *"the 1.5% calibration point being consistency check rather than empirical discrimination"* → an honesty caveat at Ch 11; *"the reader-side cognitive-consumption failure mode as the uncovered flank"* → a whole new "Reader-Side Orphan" section. Gemini's meta-finding: *"translation-into-technical-vocabulary as the book's distinctive contribution rather than first-principles derivation"* → a new "Translation as Distinctive Contribution" section. Each patch logged to WRONG.md with perturbation-event attribution.

**Source:** `C:\BOOK\BUILD_LOG.md` lines 287–304.

**What the ledger has:** WEAKER. §2.9 makes adversarial review "first-class, not optional" and names the 5-role rubric. But it stops at *running* the review; it does not encode (a) that findings become **surgical, sited insertions** (add an honesty caveat exactly where the claim overreaches, rather than diluting the whole book), nor (b) the pattern of **acknowledging a weakness in-text instead of pre-relaxing** (see D5), nor (c) that an external/cross-model review is a distinct, high-value perturbation beyond the in-session Steelman/Skeptic.

**Exact bake-in:** Extend §2.9 / the `audit` command: *"Adversarial-review findings are resolved as SITED insertions, not global dilution — patch the exact passage where a claim overreaches (an honesty caveat, a named-limit paragraph, a new failure-mode section), and log each as a WRONG.md entry with the perturbation event. Cross-model / external review (a different model family, a fresh 1M instance) is a first-class perturbation and its findings outrank in-session self-audit when they conflict."*

---

## D5 — Honor the claim's full strength in the body; acknowledge its limit AT THE SITE — do not pre-relax at the cover/title

**Lesson (verbatim):** *"kept as 'A Cosmological Derivation of What a Life Is For.' The acknowledgment sentences at Ch 18 and Ch 22 honor the relaxation at the sites where the claim operates rather than pre-relaxing at the cover level. This is the framework's own discipline applied to its own production."*

**Source:** `C:\BOOK\BUILD_LOG.md` lines 316, 360.

**What the ledger has:** ABSENT. §9 (metadata) covers subtitle mechanics (no "Book 1", char limits) but nothing about the **rhetorical stance** between a strong title-claim and its honest in-body qualification. The kit could easily default to watering down a bold subtitle to be "safe"; the ATD discipline is the opposite — keep the strong claim, and place each limit precisely where the argument makes that claim.

**Exact bake-in:** Add a note under §9.4 / §7: *"A strong title/subtitle claim is kept strong; its qualifications live as sited acknowledgments at the exact passages where the claim operates, never as a pre-emptively hedged cover. Applying the book's own honesty discipline to its own packaging is the rule — don't relax the promise, honor it and bound it in place."*

---

## D6 — The whole-book "de-concretize" (abstraction) sweep is a supported, high-blast-radius operation

**Lesson:** Mid-project Bo reversed the entire autobiographical strategy: *"abandon the Class B authorship distribution... Strip all personal-specific references (Sam, Tori, STA, March 29, Marcolin, Debra, Jocelyn, ... AORTA, GOLA, OIG, CMS-3409, fifty-two years, etc.). The book is a framework-of-frameworks; the concepts speak for themselves."* Execution filled all 27 [BO-WRITES] markers impersonally, removed named sections wholesale (Ch 3 Sam section deleted; Ch 13 March-29 → "The Compressed-Release Cluster"), rendered three named portraits as "first/second/third portrait" structural placeholders, and **preserved anonymized empirical hooks** (kept the "1.5% fit" as an anonymized calibration claim while stripping the identifying data). Cost was tracked: word count fell to 121,548 and *"the gap tracks the stripped autobiographical content per Bo's direction."*

**Source:** `C:\BOOK\BUILD_LOG.md` §"Phase D-plus" (lines 265–276).

**What the ledger has:** ABSENT. §9 nods at proper-noun/positioning avoidance for metadata, and §2.4 governs Class-A/B/C, but there is no procedure for a **repo-wide concretion-level change** — the direction that a book can be flipped between personal-specific and fully-abstract, that it touches manuscript + contracts + registries + threads (Titanic renamed "The Observer" in threads.md; init_contracts.py de-named), that named constructs get structural replacements, and that anonymized empirical anchors are retained even when their source is stripped.

**Exact bake-in:** Add a §7/§11 procedure "Concretion-level sweeps": *"'Make it abstract' / 'make it personal' is a supported whole-repo operation, not a local edit. It cascades to manuscript, [BO-WRITES] fills, contracts, and every registry (rename the entity in threads/dependencies, de-name generators/tooling). Named constructs get structural replacements (a dated event → a named structural pattern; three named people → first/second/third portrait). Preserve anonymized empirical anchors (keep '~1.5% fit' as an anonymized calibration claim even after the identifying data is stripped). Expect and record the word-count delta — a large abstraction sweep legitimately shrinks the book."* Recommend a `book_config.concretion_level` (personal | abstract) knob.

---

## D7 — The em-dash HARD gate needs a narrow, stated TABLE exception (lint false-positive guard)

**Lesson (verbatim):** *"No em-dashes in prose. ... Hyphens in compound adjectives are fine. Tables can use em-dash as 'n/a' placeholder."*

**Source:** `feedback_no_em_dashes.md` as summarized in `C:\BOOK\BUILD_LOG.md` line 193.

**What the ledger has:** WEAKER / a latent false-positive. §17.1 is an absolute exit-1 gate on U+2014/U+2013 with the only carve-out being compound-adjective hyphens (U+002D, a different char). BUILD_LOG records a real, sanctioned em-dash use — an em-dash as the "n/a" cell filler in a table — that the current hard gate would flag and block. Unstated exceptions become either false rejections or, worse, a reason to weaken the whole gate.

**Exact bake-in:** In `lint_manuscript.py`'s em-dash rule and §17.1, add the single documented exception: *"an em-dash used solely as an empty/'n/a' placeholder inside a Markdown table cell is permitted; every other U+2014/U+2013 in prose still fails."* Implement as: ignore a `—` that is the entire trimmed content of a table cell (line contains `|` and the cell is exactly `—`). Keep it this narrow — it is the ONLY sanctioned em-dash.

---

## D8 — Per-book "leak-tripwire" greps for project-specific forbidden proper nouns (name-scrub enforcement)

**Lesson:** BUILD_LOG shows a recurring class of catch distinct from the vocabulary blacklist: a specific **name/identifier that must never appear** in this book's prose (Tori removed; then the entire personal-name/institution set). This needs a per-book grep tripwire, because the forbidden token is book-specific, not a universal AI-slop word. The de-concretize sweep's success depended on it (line 272, cross-chapter cleanup of "residual personal/institutional specifics").

**Source:** `C:\BOOK\BUILD_LOG.md` lines 14, 30, 194, 267, 272; corroborated by `feedback_prose_discipline.md` cross-reference discipline.

**What the ledger has:** PARTIAL. §2.7 mentions an *optional* per-book "no-leak" grep for forbidden proper nouns in a character's voice — but it's a one-line aside, not tied to config, and not part of the defaults checklist. Given how central the name-scrub was to ATD, this deserves promotion.

**Exact bake-in:** Promote to a first-class knob: `book_config.voice.forbidden_proper_nouns[]` (per-book), swept by `lint_manuscript.py` (exit 1 on any hit outside cached-source dirs) and added to the §14 FIRST-PASS checklist ("forbidden-proper-noun grep clean"). This is the mechanical backstop that makes a name-scrub or de-concretize sweep verifiable rather than hopeful.

---

## D9 — In-review exact-phrase leak of the REFRAIN is a recurring, named catch (the refrain leaks into ordinary prose)

**Lesson:** Repeatedly, the exact refrain phrase leaked into non-placement prose and was caught only in review, then reworded before commit. Verbatim instances: Ch 22 line 89 — *"Exact-phrase leak caught in review at line 119 ('whether the pattern holds when external readers traverse it'); revised to 'whether the closure persists' before commit."* Ch 21 line 125 — *"Initial refrain leak at line 93 ('The pattern holds is the doctrine's terminal claim') caught and revised to 'The refrain there is the doctrine's terminal claim'."*

**Source:** `C:\BOOK\BUILD_LOG.md` lines 89, 125.

**What the ledger has:** WEAKER. §2.7/§16 enforce that the refrain appears *at exactly its designated placements with exact wording*. But the failure here is the inverse and more insidious: the refrain's **words appearing OUTSIDE a placement** (as a natural-language fragment), which dilutes the locked phrase's impact and inflates its count. The current "appears at exactly N placements" check does not necessarily catch a stray in-prose occurrence that isn't a formal placement.

**Exact bake-in:** Strengthen the refrain check (`check refrain` / GATE-3 contract gate): *"Grep the whole assembled master for the exact refrain string; every occurrence must be an approved placement. A refrain-phrase fragment appearing in ordinary prose OUTSIDE a placement is a leak — reword it (as in ATD: 'whether the pattern holds' → 'whether the closure persists'). Count of exact-string occurrences must equal the locked placement count, no more."* Add to §14: "refrain exact-string occurrences == placement count (no in-prose leaks)."

---

## D10 — Ship-order is Kindle-FIRST (fastest to market, immune to print rejections), and updates don't auto-push

**Lesson:** BUILD_LOG's production reality shows Kindle DOCX shipping ahead of print, regenerated every revision independently.

**Source:** `C:\BOOK\BUILD_LOG.md` lines 280–285, 308–312, 345–350 (Kindle regenerated at each of v1.0/v1.1/v1.2 alongside but ahead of the print PDF).

**What the ledger has:** ALREADY PRESENT — §7.5 states "Kindle first (fastest to market)" and the no-auto-push caveat. **This is NOT a delta; recorded here only to note it is corroborated, not missing.** (Included for the parent's completeness; no bake-in needed.)

---

## D11 — Word-count-below-target is acceptable when it tracks a deliberate content decision (don't pad to hit a number)

**Lesson (verbatim):** *"Manuscript complete: 26 chapters, 121,548 words (below the 140-160K target; the gap tracks the stripped autobiographical content per Bo's direction)."* The shortfall was accepted, attributed, and NOT back-filled — the opposite reflex from "make it 204 pages."

**Source:** `C:\BOOK\BUILD_LOG.md` line 275 (and §7.3 "'Make it 204 pages' is the wrong framing" corroborates the anti-padding stance).

**What the ledger has:** PARTIAL. §7.3 rejects page-count-as-target for Kindle parity, and §16.5 sets a 75-page FLOOR. But there's no general rule that a **word/page count landing below an aspirational target is fine when it's a recorded, deliberate content choice** — the ledger's contract gate enforces ±20% per unit and the floor enforces a minimum, which could push an instance to pad. The lesson: attribute the gap, don't manufacture words.

**Exact bake-in:** Add a one-line note to §11/§16.5: *"A total below the aspirational word/page target is acceptable when it tracks a recorded content decision (e.g. an abstraction sweep) and clears the hard floor (§16.5). Attribute the gap in the log; never pad prose to hit a vanity number — padding fails the single-authorial-act bar faster than a shorter honest book does."*

---

## D12 — "Do not correct the author's own-voice misspellings/idiolect" applies inside [BO-WRITES] and informal passages (fingerprint preservation)

**Lesson:** `feedback_prose_discipline.md` (verbatim): *"When editing, preserve recurring lines across works (e.g., 'the night was young,' 'the universe noticing itself noticing itself is love') — they are deliberate cross-references, not accidents."* BUILD_LOG confirms these cross-work lines were consciously reused ("the universe noticing itself noticing itself" appears as an amped Ch 3/Ch 10 beat, lines 328–329).

**Source:** `feedback_prose_discipline.md` line 31; `C:\BOOK\BUILD_LOG.md` lines 328–329.

**What the ledger has:** PARTIAL. §17.2 has "Do NOT 'correct' Bo's own-voice misspellings (they are fingerprints)." But it does not extend the rule to **cross-work recurring lines** — deliberate phrases that repeat across *different books* and must survive an edit pass untouched (a lint or a "tighten this" pass would otherwise flatten them).

**Exact bake-in:** Extend §17.2: *"Preserve deliberate cross-work recurring lines verbatim (e.g. 'the night was young', 'the universe noticing itself noticing itself is love') — they are intentional cross-references across the author's body of work, not repetition to be edited out. Treat them like sacred/refrain lines: exempt from tightening, dedup, and 'vary the wording' passes."* Optionally list them in `book_config.voice.sacred_terms` so the voice audit protects them.

---

## Summary of ledger sections touched

| Delta | Ledger target | Strength vs ledger |
|---|---|---|
| D1 clinical-distance / peak-amp pass | §7 (+CLAUDE.md §7 Never-do) | ABSENT (craft) |
| D2 greenlist deployed at weight | §2.7 / §17.2 | WEAKER (static only) |
| D3 parallel-draft callback concretization | §11 / GATE-4 / §14 | PARTIAL |
| D4 sited adversarial-review insertions | §2.9 / `audit` | WEAKER |
| D5 keep strong claim, sited limits | §9.4 / §7 | ABSENT |
| D6 whole-repo concretion-level sweep | §7 / §11 (+config knob) | ABSENT |
| D7 em-dash table 'n/a' exception | §17.1 / lint_manuscript.py | WEAKER (false-positive) |
| D8 per-book forbidden-proper-noun grep | §2.7 → config + §14 | PARTIAL |
| D9 refrain in-prose leak grep | `check refrain` / §14 | WEAKER |
| D10 Kindle-first ship order | §7.5 | ALREADY PRESENT (no-op) |
| D11 under-target is OK if deliberate | §11 / §16.5 | PARTIAL |
| D12 preserve cross-work recurring lines | §17.2 | PARTIAL |

*Top-3 to bake first: **D1** (the named anti-clinical-distance / peak-amp discipline — pure craft, entirely missing), **D3** (parallel-drafting callback concretization — a real continuity hazard with a clean mechanical gate), **D7** (the em-dash table carve-out — a latent hard-gate false positive that will block a legitimate build). D6 and D8 together make "de-concretize / name-scrub" a verifiable operation instead of a hope.*
