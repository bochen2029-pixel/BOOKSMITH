# DELTA: the writing-project constellations (gracegradient · wholemachine · permanentunderclass · autotelic)

*Read-in-full sweep, 2026-07-12 (anchored: Sunday 2026-07-12 03:15 CDT / America/Chicago). Every `.md` in the four memory stores below was READ, not grepped, and diffed against the crystallized canon: `docs/LESSONS_LEDGER.md` §17 (author voice) + §18 (read-not-grepped deltas), `docs/author_voice/AUTHOR_VOICE_Bo_Chen.md`, and the four `docs/author_voice/_voiceprofile_*.md` detail files. This constellation is the set of Bo's ESSAY/WEBSITE projects: the source docs behind the candidate books (whole-machine, grace-in-the-gradient, permanent-underclass, autotelic). Their memory holds the author's working voice, house style, and drafting rules for exactly this author.*

**Sources read in full (11 files across 4 stores):**
- `C--gracegradient/memory/`: MEMORY, bo-working-style, user-bo-chen, gracefulgradient-website, websites-cloudflare-rig
- `C--Websites-wholemachine-org/memory/`: MEMORY, house-style-spec, wholemachine-org
- `C--Websites-permanentunderclass-cc/memory/`: MEMORY, bo-writing-voice-plain, underclass-essay-plan, the-brain-canon, idle-engine-project, backrooms-sim, brain-repo
- `C--Autotelic-framework-v5/memory/`: MEMORY, user_role

**Headline:** the four OPUS voice agents already mined the big VOICE rules out of these exact files (`bo-writing-voice-plain`, `house-style-spec`, `bo-working-style`: the "folding the years" flourish, the tricolon, the "weight-average mashing" mechanism, the `bo-voice` skill, the "cardinal sin," the 1M-context fact are all in `_voiceprofile_crossproject.md` already). Those are logged below as short CONFIRMATIONS. The genuine DELTAS cluster in three thin seams the voice sweep did not reach: (1) the **two-register SCOPE boundary** (where the em-dash ban and the maximalist voice apply vs where they explicitly do NOT: the AI-companion answer register, the sober-essay register); (2) the **"earned peak in a sober field" craft discipline** (the underclass essay is the worked example the ledger's §18.3 clinical-distance lesson needs); (3) a set of **PROCESS hazards** that recur across every website build (frozen hand-assembled artifacts, compaction-degraded source text, the drafter-persona convention, a live secret leak).

---

## VOICE / PROSE

### V1. The em-dash ban is scoped to BOOK/ESSAY PROSE, NOT to the AI-companion answer register. · ABSENT · MED
The ledger states the em-dash rule as absolute over "ALL prose output: book, scaffolding, memos, drafts" (§17.1, AUTHOR_VOICE H1). But Bo's own shipped systems carve out one register: the grounded `/api/ask` companion worker.
- **Source (`wholemachine-org` MEMORY, verbatim):** the ftoe "Ask the Mirror" builder `_build_worker.py` holds `ASK_SYSTEM` … "**em-dashes ALLOWED here.**"
- **Why it matters:** the ban is a *published-prose-under-Bo's-name* rule, not a universal typographic law. A conversational Q&A agent answering a reader is a different register and Bo explicitly permits em-dashes there. The kit does not ship an ask-companion, so this does not change a gate today; it matters the moment BOOKSMITH grows a "talk to the book" feature (a recurring Bo module, every site has one) or reuses `lint_manuscript.py` on companion output.
- **Ledger status:** §17.1 implies universality; no scope carve-out named. **Bake-in:** add one line to AUTHOR_VOICE §HARD-RULE-1 and ledger §17.1: *"Scope = published prose authored AS Bo (book body, essay, scaffolding, drafts). A grounded AI-companion/Q&A answer register is explicitly EXEMPT (Bo ships em-dashes in his `/api/ask` system prompts); do not run the em-dash gate against companion output."*

### V2. `bo-voice` (maximalist) and the plain working voice are DIFFERENT registers selected by artifact, not a contradiction. · WEAKER · MED
The ledger and AUTHOR_VOICE treat "the voice" as one profile. The corpus is explicit that there are two, and which one is active is a function of *what is being produced*.
- **Source (`bo-writing-voice-plain`, verbatim):** "When he wants prose *as him*, that's the `anthropic-skills:bo-voice` skill; **default working voice with him is just clean and unadorned.**"
- **Source (`underclass-essay-plan`, verbatim):** the parent essay's register is "grand/literary, the ***opposite*** of Bo's working anti-slop voice."
- **Why it matters:** BOOKSMITH always writes in the *published* register, so it should default to the `bo-voice` maximalist profile, NOT the terse working voice the same memories also praise. Confusing the two produces flat, clipped book prose that passes the blacklist but misses the maximalist commitment. The `_voiceprofile_crossproject.md` flags this as an unresolved *conflict* (its §"Conflicts" 3); this delta resolves it: **the selector is the artifact.** Book body → bo-voice maximalist. A chat reply to Bo → plain working voice.
- **Ledger status:** conflict noted in the voiceprofile, not resolved; ledger §17 does not carry the resolution. **Bake-in:** in AUTHOR_VOICE add a "REGISTER SELECTOR" note: *book/essay body = bo-voice maximalist (this profile); Claude's own working replies to Bo = plain/unadorned; never blend them into the manuscript.*

### V3. Named positive voice-DNA devices to ADD to the profile: conditional cascades · archaic+colloquial braid · grand-sincere close · no-irony-shield. · WEAKER · MED
AUTHOR_VOICE VOICE-DNA lists enumeration→compression, long-accumulate→short-hammer, the parenthetical, semicolons, mechanical metaphors. The underclass draft spec adds concrete named devices the profile is missing or under-naming.
- **Source (`underclass-essay-plan`, verbatim voice decision):** written in Bo's own register: "**recursive restatement, conditional cascades, physics/navigation metaphors, archaic+colloquial braid, no bullets, no em-dash-workhorse, no inline citations, grand sincere close.**"
- **New vs the profile:** *conditional cascades* (stacked if/then/then-what constructions building to inevitability) and *physics/navigation metaphors* (a superset the profile narrows to "mechanical/accounting/architectural") and the *grand sincere close* (an ending mode; pairs with the profile's ending-rotation but names the register-lift specifically) and *archaic+colloquial braid* (the profile's two-register oscillation, but named as a within-paragraph texture, not just a between-passage switch). "*no irony shield*" (from `bo-working-style`: "bo-voice = maximalist commitment, no irony shield") is a positive rule the profile omits: Bo does not hedge sincerity behind detachment.
- **Ledger status:** partially present (recursive restatement, mechanical metaphors); the four named devices above are not in AUTHOR_VOICE VOICE-DNA. **Bake-in:** extend AUTHOR_VOICE VOICE-DNA + `greenlist` with: conditional cascades; physics/navigation metaphors (broaden the metaphor family); the grand sincere close; the archaic-next-to-colloquial in-paragraph braid; "no irony shield" as an explicit posture rule.

### V4. The refrain / deliberately-unspoken material is verbatim-locked AND its ABSENCE is enforced (the "third door"). · CONFIRMATION+ · LOW
The ledger's refrain rule = exact wording, exact count. The corpus adds a mirror case: a thing that must NEVER be said.
- **Source (`gracefulgradient-website`, verbatim):** the ask-companion guardrail: "**NEVER name the deliberately-unspoken third door**"; "honor what the essay leaves open."
- **Ledger status:** §18.3 refrain-leakage audit covers "the sacred phrase leaks into ordinary prose." The inverse (a sacred SILENCE that must not be filled) is adjacent but not named. **Bake-in (LOW):** note in the refrain/sacred-terms audit that `sacred_terms` can include a *negative* entry, a concept the manuscript must leave unnamed; the audit greps to confirm it never appears, not that it appears at a count.

---

## WRITING / CRAFT

### C1. THE EARNED-PEAK-IN-A-SOBER-FIELD discipline (the worked example the ledger's clinical-distance lesson §18.3 was missing). · WEAKER · HIGH
§18.3 names the clinical-distance failure (over-correcting against cliché flattens the emotional peaks) and prescribes a "peak-aliveness pass." The underclass plan is the concrete METHOD for executing it, and it is sharper than the ledger's abstraction.
- **Source (`underclass-essay-plan`, verbatim):** "**Voice: mostly sober/concrete/sourced … with 1 to 2 *earned* Grace-register hinges** (the slavery/thermodynamics parallel; the close). **Don't pour the cathedral into the op-ed.**"
- **The method it encodes:** a book/essay in a sober register does not raise every beat to the thesis altitude; it selects **1 to 2 pre-identified load-bearing hinges** and lifts ONLY those to the grand register; everywhere else stays concrete and sourced. This is the operational form of "amp the load-bearing beats back to the thesis's altitude": it says *how many* (1 to 2, named in advance) and *where* (the argument's fulcrum + the close), and it warns against the opposite failure (lifting everything = "pouring the cathedral into the op-ed" = purple overload).
- **Ledger status:** §18.3 has the principle and the anti-flatness checklist, not the "select 1 to 2 named hinges, lift only those" mechanic. **Bake-in:** extend the §7 peak-aliveness technique and its checklist: *for a sober/argumentative book, pre-designate the 1 to 2 register-lift hinges in the seed (the thesis fulcrum + the close); lift ONLY those to the grand register; hold everywhere else concrete/sourced. Over-lifting is the mirror failure of clinical flatness.* Add both poles to the anti-flatness gate.

### C2. Assertive-prose citation discipline: NO inline citations by design; sources wired in a separate block. · ABSENT · MED
The kit's §18.2 print conventions and §7 craft rules do not state where citations live in Bo's assertive register. The corpus is explicit.
- **Source (`underclass-essay-plan`, verbatim):** "assertive prose has no inline cites by design; see SOURCES TO WIRE block in the file"; voice spec lists "**no inline citations**" alongside "no bullets, no em-dash-workhorse."
- **Why it matters:** for a Class-C nonfiction unit the drafting instinct is to drop "(Author, 2024)" or footnote markers inline. Bo's published register forbids this: the prose asserts, and provenance lives in a separate SOURCES block (or a back-matter apparatus), never mid-sentence. Inline citations are, for Bo, an AI-academic tell as much as an em-dash.
- **Ledger status:** absent. **Bake-in:** add to AUTHOR_VOICE HARD RULES / the §7 never-do list: *no inline citations in body prose; provenance goes in a separate SOURCES block / back matter. Inline "(Name, year)" or footnote-number tics are a slop tell in Bo's register.* Consider a lint advisory for a `\(\w+,\s*\d{4}\)` pattern in body prose.

### C3. The compaction-degraded-source hazard: a re-run build can silently render DECAYED text. · ABSENT · MED (craft+process)
A live, named production failure: a source markdown was corrupted by a prior compaction and a build shipped the degraded prose until caught.
- **Source (`gracefulgradient-website`, verbatim):** "The earlier `gracegradient.md` is the **compaction-degraded text: superseded, do not use.**" The canonical file is `the-grace-in-the-gradient-v3.md` and "_build_site.py now reads it." The rebuild "restored the whole spine" (movements, the payoff frame, the specific unifications) that the degraded copy had lost.
- **Why it matters:** BOOKSMITH's own COMPACTION-SURVIVAL machinery protects the *session*, but this shows the *source manuscript* can itself be a compaction casualty. If `assemble_manuscript.py` reads a unit file that was last written by a degraded post-compaction pass, the anti-drift keystone faithfully assembles decayed prose. The single-source guarantee protects against version drift, not against content decay inside the pinned version.
- **Ledger status:** absent (§11 version discipline covers stale-version drift, not intra-version decay). **Bake-in:** add a ledger note under §11 / COMPACTION-SURVIVAL: *after any compaction/resume, before assembling, spot-verify each `manuscript/current/` unit against its last known-good state snapshot / backup for silent content decay; a post-compaction rewrite is the highest-risk author of a degraded unit. Never treat "the file exists and lints clean" as "the prose is intact."*

### C4. Source-doc register is NOT the author's target register: corroborated in a fresh, third instance. · CONFIRMATION · HIGH-value
The ledger's root-cause META-RULE (§17) is: voice lives in the author's memory, not the source docs; matching the source's punctuation is the shipped error. This corpus corroborates it a third independent time and generalizes it from *punctuation* to *whole register*.
- **Source (`underclass-essay-plan`, verbatim):** the parent essay's register "is grand/literary, the ***opposite*** of Bo's working anti-slop voice"; the derived essay had to make a deliberate voice DECISION, not inherit the source's.
- **Ledger status:** already the load-bearing §17 META-RULE; this is a strong confirmation + a generalization (not just em-dashes: the *entire* register of a source doc can be the wrong target). No change needed beyond noting the generalization in §17. **Bake-in (optional):** one clause in §17: *"the mismatch is not only punctuation; a source's whole register (grand/literary, or terse/technical) can be the wrong target. Decide the book's register from the author profile, then treat the source as content, not as a style exemplar."*

---

## HOUSE-STYLE

### H1. Vendored, self-hosted, subsetted display+body fonts with RELATIVE paths: corroborated as a repeat build failure+fix. · CONFIRMATION · HIGH-value
The kit already vendors fonts repo-relative (a deliberately-STRONGER-than-source choice per §18). The corpus shows the exact failure that rule prevents, twice.
- **Source (`gracefulgradient-website`, verbatim):** fonts "subsetted and self-hosted in `_upload/fonts/` (**relative paths**, so it renders locally AND when served)"; and the fix: "source fonts are now **vendored at `…/fonts-src/`** so the build is self-contained; it **no longer reads the Desktop `Cormorant_Garamond.zip`, which the user deleted and which broke a build.**" Same Cormorant Garamond (display) + EB Garamond (body) family the kit uses.
- **Ledger status:** §2/§18 already mandate repo-relative vendored fonts and warn cross-repo font deps "bit every prior book." This is a third corroborating instance (a Desktop-zip dependency that broke a build when the file was deleted). **No change needed**: it strengthens confidence the rule is correctly load-bearing. Keep it.

### H2. The "frozen / hand-assembled artifact / do NOT re-run the builder" hazard. · ABSENT · MED
Across the website builds a recurring, explicitly-flagged failure mode: an artifact was hand-finished past what its generator produces, so re-running the generator REGRESSES it.
- **Source (`wholemachine-org` MEMORY, verbatim, multiple):** "`index_v3.html` is **HAND-ASSEMBLED, do NOT run `_build.py`** (regresses the flagship to the v1.1-only render, wiping the overture/diff/band)"; and later "**do NOT run the OLD `_build.py`** (renders the pre-v3 Mirror)"; a new builder `_build_v3.py` supersedes it.
- **Why it matters for the kit:** BOOKSMITH's whole discipline is *deterministic regeneration from a single source*, the opposite stance. But the moment a human hand-finishes a composited cover, a front-matter page, or a TOC in Word past what the generator emits, re-running `generate_book.js` / `composite_cover.py` silently discards that manual work. The kit assumes idempotent regen; this is the case where that assumption bites.
- **Ledger status:** absent. **Bake-in:** add a §11 / §12 note: *if any artifact is hand-finished beyond generator output (a manually-corrected cover, a hand-set TOC, a Word-side fix), record it in CHANGELOG and either (a) fold the fix back into the generator input so regen reproduces it, or (b) mark the artifact FROZEN and gate regen behind an explicit confirm. Never silently re-run a generator over a hand-finished artifact.* This is the deterministic-regen kit's blind spot.

### H3. `noindex` / "not for general distribution" is a real per-artifact routing flag. · CONFIRMATION · LOW
- **Source (`websites-cloudflare-rig` + `wholemachine-org`, verbatim):** permanentunderclass.cc "Set to `noindex` (its text says 'Not for general distribution.')"; the `/toe /nested /loop` canon pages are "`noindex` and NOT linked from the mainpage yet (staged)."
- **Ledger status:** adjacent to the kit's license register-split (§18.2: treatises CC-BY, novels ARR by `is_fiction`). Distribution-visibility is a separate axis (indexable/public vs staged/private). **Bake-in (LOW):** note that distribution intent is its own knob distinct from license: a book can be ARR *and* privately-staged, or CC-BY *and* public; do not couple them.

---

## PROCESS

### P1. The DRAFTER-PERSONA convention: Bo's long-form prose is authored by a NAMED instance ("Claude Fable 5" / "Fable"). · ABSENT · MED
Every wholemachine/ftoe artifact credits a named drafting persona, distinct from the working assistant.
- **Source (`wholemachine-org`, verbatim):** the BRAIN blueprints are "both by Claude **Fable 5**, 2026-07-02"; the four-model ToE synthesis output is signed "**The View from Somewhere**, Fable"; canon pages are "`by_fable5`."
- **Why it matters:** BOOKSMITH impersonates Bo (first-person, per AUTHOR_VOICE "WHO BO IS"). But Bo's actual working pattern separates *the author (Bo)* from *the drafting instance (Fable 5)*: the instance drafts, Bo owns/signs. This maps cleanly onto the kit's authorship classes (the instance drafts Class C fully, scaffolds Class B, outlines Class A; Bo signs). It also implies a naming convention: long-form Bo artifacts may carry a drafter attribution in metadata/colophon, not in the body.
- **Ledger status:** absent as a named convention. **Bake-in (MED):** a note in §9 / AUTHOR_VOICE: *Bo's working pattern names the drafting instance ("Fable 5") as distinct from the author; the kit already embodies this (instance drafts, Bo signs via the class dial). If a colophon/attribution is wanted, the drafter attribution is metadata/colophon-level, never in the body prose, and never displaces Bo as author.*

### P2. Don't-leak-context ("the cardinal sin") + the honest-posture rule + author-level-transfer. · CONFIRMATION · HIGH-value
The three most load-bearing PROCESS rules in this corpus are already captured by the voice sweep; logged here so the read is provably complete.
- **Source (`bo-writing-voice-plain`, verbatim):** "**Don't leak 'research notes' (everything I just loaded) into output just because it's topically relevant: the cardinal sin he identified.**" → already in `_voiceprofile_crossproject.md` A4 and directly relevant to BOOKSMITH's 250K-context-then-write loop: the loaded canon_refs/digests must dissolve into the prose, never surface as visible "as the research shows" scaffolding.
- **Source (`bo-working-style`, verbatim):** ground-truth-over-flattery; "**never block on him**: full autonomy … with snapshot/CHANGELOG as the safety net"; verify BINARY freshness not source; chunked-write discipline for >~15, 20KB outputs (single big writes truncate). → all already in the kit's autonomy grants (§4), version discipline (§11), and this very task's chunk-then-write instruction.
- **Ledger status:** captured (voiceprofile + CLAUDE.md §4/§11). **No new bake-in;** confirmations that the kit's autonomy + anti-slop + chunked-write posture matches Bo's stated working rules.

### P3. A live secret is leaked in plaintext inside a chunker output + a memory jsonl. · SECURITY · MED (out-of-kit)
Not a book-craft lesson, but surfaced during the read and worth flagging with high confidence.
- **Source (`wholemachine-org` MEMORY, verbatim):** "⚠️ **leaked DIFFERENT DeepSeek key `sk-0f073…` sits in plaintext** in `huagangchen\chunker\_{abc_marrow,transcript}_chunks\chunk-013.md` + huagangchen memory jsonl: rotate + scrub if still valid." (A second key `sk-f26dc…` was pasted as a Cloudflare secret: that one is handled correctly.)
- **Why flagged here:** it is a standing credential exposure in Bo's workspace. Out of scope for BOOKSMITH's gates, but it is exactly the kind of thing to surface once and let Bo decide. **Bake-in:** none in the kit. **Action:** flag to Bo: rotate the `sk-0f073…` DeepSeek key and scrub it from the two chunker chunk files and the huagangchen memory jsonl if still valid.

### P4. The epistemic-order rewrite is a real, reusable revision METHOD (adds to §18.3's under-captured methodology set). · ABSENT · LOW
- **Source (`wholemachine-org` MEMORY, verbatim):** the ftoe flagship was "re-authored in **epistemic order** (Datum→Inference→Ledger→Selection→Page→Someone→Origin/Reader→Horizon/Worth→Knower→Register)" from the review faults: i.e. the argument was reordered so each claim is only introduced after everything it depends on is established.
- **Why it matters:** §18.3 lists ASTRA's "single-axis multi-pass revision with a fixed pass order" as under-captured. Epistemic-order reordering is a *structural* revision axis of the same family: a whole-manuscript pass that reorders units/sections so no concept is used before it is earned: the structural cousin of the kit's "no forward concept references" continuity gate, applied at revision time to the sequence itself.
- **Ledger status:** the family (single-axis multi-pass revision) is noted as under-captured in §18.3; this specific axis is not named. **Bake-in (LOW):** add "epistemic-order reordering (no claim before its dependencies)" to the revision-methodology note §18.3 flags for future capture; pairs with the existing forward-reference continuity gate.

### P5. The autotelic project frames its deliverable as a LITERATE-PROGRAMMING SPEC; honest limits are load-bearing FEATURES. · CONFIRMATION · LOW
- **Source (`autotelic user_role`, verbatim):** "This is a *literate-programming specification*, not a typical codebase"; the framework's "own honest limits (§6 …) are **load-bearing structural commitments: treat them as features, not gaps to be fixed.**"
- **Ledger status:** the "honest-limits-as-features" ethos aligns with the kit's ship-at-90% / append-only-canon posture and the honest-posture voice rule (`_voiceprofile_feedback.md`). The "literate-programming spec" framing corroborates why BOOKSMITH itself (CLAUDE.md + KIT_ARCHITECTURE as prose-that-is-the-machine) is built the way it is. **No bake-in;** confirmation of the surrounding ethos.

---

## SUMMARY TABLE (severity × seam)

| # | Delta | Seam | Gap | Sev |
|---|---|---|---|---|
| V1 | em-dash ban is scoped to published prose; AI-companion register exempt | VOICE | ABSENT | MED |
| V2 | bo-voice(maximalist) vs plain-working = register selected by artifact | VOICE | WEAKER | MED |
| V3 | add named devices: conditional cascades · phys/nav metaphors · grand close · no-irony-shield · archaic+colloquial braid | VOICE | WEAKER | MED |
| V4 | sacred SILENCE (negative refrain) enforced by absence | VOICE | CONFIRM+ | LOW |
| C1 | earned-peak: pre-designate 1 to 2 register-lift hinges, lift only those | CRAFT | WEAKER | **HIGH** |
| C2 | NO inline citations in body prose; sources in a separate block | CRAFT | ABSENT | MED |
| C3 | compaction-degraded SOURCE text can render silently on rebuild | CRAFT | ABSENT | MED |
| C4 | source-doc REGISTER (not just punctuation) is the wrong target | CRAFT | CONFIRM | HIGH-val |
| H1 | vendored/subsetted/relative-path fonts: 3rd corroborating failure | HOUSE | CONFIRM | HIGH-val |
| H2 | hand-assembled/frozen artifact: re-running the generator regresses it | HOUSE | ABSENT | MED |
| H3 | noindex/staged distribution is a knob distinct from license | HOUSE | CONFIRM | LOW |
| P1 | drafter-persona convention (Fable 5 drafts, Bo signs) | PROCESS | ABSENT | MED |
| P2 | don't-leak-context "cardinal sin" + honest-posture + author-transfer | PROCESS | CONFIRM | HIGH-val |
| P3 | live DeepSeek key leaked in plaintext (chunker chunk + jsonl) | PROCESS | SECURITY | MED |
| P4 | epistemic-order rewrite = a structural revision axis | PROCESS | ABSENT | LOW |
| P5 | literate-programming-spec framing; honest limits are features | PROCESS | CONFIRM | LOW |

**Highest-value new bake-ins:** C1 (the earned-peak *mechanic* the clinical-distance lesson was missing) and C2 (no-inline-citations), then V1/V2 (the register-scope boundary) and H2/C3 (the two idempotent-regen / content-decay blind spots the deterministic kit does not currently see). Everything in the VOICE seam that a prior agent would expect to find NEW here was already extracted into `_voiceprofile_crossproject.md`: this constellation's real contribution is the CRAFT + PROCESS scope-and-hazard layer, not fresh voice atoms.
