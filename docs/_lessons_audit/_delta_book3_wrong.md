# DELTA AUDIT — C:\BOOK3\WRONG.md + C:\BOOK3\CHANGELOG.md vs the kit ledger

*Produced 2026-07-12 (Sunday), Central (system clock: 2026-07-12 03:15 CDT; `currentDate` memory: 2026-07-12). Method: READ-IN-FULL (not grep) of `C:\BOOK3\WRONG.md` (621 lines / ~16.7K tokens) and `C:\BOOK3\CHANGELOG.md` (198 lines / ~4.3K tokens), cross-checked against `docs/LESSONS_LEDGER.md` §1–§18 and the four existing `_delta_*.md` audits.*

**What these two files ARE.** BOOK3 = *The Aperture Doctrine* (Book 3 of a trilogy). Its WRONG.md has two layers:
- **Section I — 10 "foundational corrections"** (all dated 2026-04-22): the structural difference between the 2025 *Apex Current Protocol* (ACP) and the 2026 Aperture Doctrine. Each is a *content/thesis* revision (gender essentialism, semen retention, fusion-as-telos, urgency-panic, AI-as-midwife, …). **These are book-specific positions, NOT portable production lessons — the kit must not adopt the Aperture Doctrine's theses.** They are recorded here ONLY where the *shape* of a correction is a durable, reusable pattern (the forbidden→permitted vocabulary discipline; deriving a book by adversarial re-read of a prior work; §7.6-style anti-pattern operationalization).
- **Section II + all of CHANGELOG.md — process/scaffolding lessons**: canon-anchor drift, contract↔registry desync cascades, premature scope claims, the three audit surfaces, cache-before-generate. **This is where the durable, portable deltas live.**

**Scope rule honored.** The ledger already holds: the *headline* "17 canon-anchor drifts → 9 registry-sync cascades → 5 orphan seeds" (§2.3), the `check_acp_vocabulary.py` 97-pattern scrubber (§2.7), the WRONG.md 5-field schema (§2.9), and `integration_mode: synthesis|anthology|reforge` (§1.7). Those are NOT re-reported as new. Everything below is **absent or weaker** than the ledger, or a short **CONFIRMATION**. Each delta: WRONG belief → CORRECTED position (verbatim where it matters) · source · ledger status · bake-in · HIGH/MED/LOW.

Ordered by portable leverage. The strong ones are B1–B6.

---

## PROCESS

### B1 — "No registry updates required" after a contract fix is the recurring trap; a contract edit MUST trigger a full registry re-audit  ★ TOP DELTA
- **WRONG belief (verbatim):** after fixing 8 canon-anchor locations in 4 contracts, the first WRONG.md entry stated *"no registry updates were required beyond the cache-freshness flip."*
- **CORRECTED position (verbatim):** *"On subsequent post-fix re-audit via `Grep` across `C:\BOOK3\registry\` for remaining §5/§7 references, that claim proved incomplete: the registry files (built pre-fix) retained references that needed synchronization with the corrected contracts."* → **9 additional locations across 3 registry files** (`canon_dependencies.md` forward+reverse tables, `dependencies.md` C-11, `threads.md` T-03). Net: *"17 total locations across 7 files (4 contracts + 3 registries) were brought into alignment"* from a fix first scoped as "8 locations, no registry impact."
- **Source:** `WRONG.md` "[2026-04-22] Registry Synchronization Following Contract Canon-Anchor Corrections" (lines 539–577); `CHANGELOG.md` Step 7 + Note (lines 64–70).
- **Ledger status:** WEAKER. §2.3 records the *outcome* ("17 canon-anchor drifts → 9 registry-sync cascades") as a one-line war story and §11 mandates "regenerate ALL formats on a manuscript edit." But neither states the **general rule** that a contract/canon-anchor edit *automatically obligates a registry re-audit in the same pass*, nor that the reflex "this fix is self-contained" is a documented, repeated error. The manuscript-drift keystone (§11) has no scaffolding-layer twin.
- **Bake-in:** Add to §2.3 (or the `audit dependencies`/`audit canon` commands): *"A contract or canon-anchor edit is NOT self-contained. Registries are built from contracts and go stale the instant a contract changes. After ANY canon-anchor / contract edit, re-run `Grep` over `registry/` for the changed tokens IN THE SAME PASS and synchronize forward+reverse tables, `dependencies.md`, and `threads.md` before declaring the fix done. Treat 'no registry updates required' as a claim to be VERIFIED by grep, never asserted — it was wrong every time it was asserted early."* Add to §14: "post contract/anchor edit → registry re-audit grep clean."
- **Weight:** HIGH.

### B2 — `audit canon` spans THREE distinct surfaces, not one; verifying YAML frontmatter alone leaves two unchecked
- **WRONG belief:** a canon-anchor check = verify the `canon_anchors:` YAML frontmatter. (Implicit in the first-pass fix, which corrected YAML + prose but not Must-Plant fields.)
- **CORRECTED position (verbatim):** *"`audit canon` (pending `_tools/` implementation) should cover three audit surfaces: YAML `canon_anchors` frontmatter, prose 'Canon Anchors' sections, Must-Plant table canonical-phrasing fields."* The Must-Plant surface was explicitly *"not performed this turn"* and left as residual drift (e.g. `part01` Must-Plant cites Disposition §1 for a phrase whose canonical home is §7; `part05` cites §5 for the same phrase).
- **Source:** `WRONG.md` lines 575, 571–574 (flagged-not-fixed Must-Plant residue); Canon-Anchor Validation Pass (lines 494–535).
- **Ledger status:** ABSENT as an enumeration. §2.3's `audit canon` says only "citations resolve to real `canon_refs/` files." It does not decompose the check into the three surfaces, so a future tool/audit that only walks YAML would silently miss prose-section and Must-Plant drift — exactly what BOOK3 hit.
- **Bake-in:** In §2.3 `audit canon` spec: *"Canon-anchor verification has THREE surfaces per contract — (a) `canon_anchors:` YAML frontmatter, (b) the prose 'Canon Anchors' section, (c) Must-Plant table canonical-phrasing fields. All three must resolve to a real heading (or be a documented descriptive anchor). Checking only (a) is a partial pass; BOOK3's Must-Plant drift survived a YAML+prose fix."* Wire the same three surfaces into any `audit_dependencies.py`.
- **Weight:** HIGH.

### B3 — A descriptive (non-literal) canon anchor is legitimate and must NOT be "fixed" into a slug; distinguish it from real drift
- **WRONG belief:** every canon reference must literally match a section heading, so `GTP #§3-PDIC` (where the acronym "PDIC" appears 0 times in the cached paper) looks like drift to be corrected.
- **CORRECTED position (verbatim):** *"PDIC is Bo's informal shorthand for GTP's §3 diagnostic method; the formal paper does not use the acronym. The contract reference `#§3-PDIC` is descriptive compression — it correctly points at the section where PDIC is structurally derived — and is retained as-is."* And: *"leave as-is; the descriptor is communicating to Bo/Claude readers what §3 contains more than a slug-matcher would."*
- **Source:** `WRONG.md` Canon-Anchor Validation Pass, lines 511–512, 533; `CHANGELOG.md` Step 12 (line 141).
- **Ledger status:** ABSENT. §2.3's `audit canon` implies literal resolution; nothing distinguishes a *descriptive anchor pointing at real content* (keep) from a *literal-heading mismatch* (fix). A naive linter — or a future maintainer — would flag and "correct" the descriptive anchor, destroying a deliberate readability affordance.
- **Bake-in:** Note under §2.3 / any canon linter: *"Two kinds of non-literal anchor exist — a DESCRIPTIVE anchor (a shorthand/acronym that correctly points at the section where the concept is derived, e.g. `#§3-PDIC`) is VALID and kept; a MISMATCH anchor (points at a heading whose content is a different concept, e.g. `#§7-equanimity` when §7 is 'Love is epistemic treason') is drift and fixed. The linter flags mismatches; descriptive anchors are documented, not rewritten."*
- **Weight:** MED.

### B4 — Cache the primary canon doc into `canon_refs/` BEFORE generation — caching is what makes `audit canon` possible one step early and surfaces drift on first cross-check
- **WRONG belief (implicit):** canon-anchor auditing waits for the `_tools/` audit script; caching canon_refs/ is a routine copy step with no audit consequence.
- **CORRECTED position (verbatim):** *"Caching the primary canonical document made `audit canon` operationally possible one step earlier than the scheduled `_tools/` implementation, which is itself an argument for caching canon_refs/ before Part-generation begins."* The cache copy *"surfaced 3 canon-anchor bugs in contracts"* on first side-by-side check (`CHANGELOG.md` Step 5 side-effect).
- **Source:** `WRONG.md` lines 385, 388; `CHANGELOG.md` Step 5 (lines 49–54) + Step 6.
- **Ledger status:** ABSENT as sequencing. GATE-1 (§ command grammar) requires digests + a reconciled canon set, and §6's Context Pack loads "canon anchors per contract," but nothing states that **caching the primary source into `canon_refs/` before drafting is a load-bearing early gate** because it enables byte-identical side-by-side anchor verification that catches drift immediately.
- **Bake-in:** Add to GATE-1 / §2.3: *"Cache the primary canonical document(s) into `canon_refs/` (byte-identical; verify with a diff + byte-count) BEFORE any unit generation. This is not just provisioning — it makes canon-anchor verification possible immediately (side-by-side heading compare), and in BOOK3 it surfaced 3 contract anchor bugs on the first cross-check. Cache-then-verify precedes `generate`."* Add to §14: "primary canon cached + byte-count-verified before first `generate`."
- **Weight:** MED.

### B5 — When two same-dated ledger entries are causally ordered, physically append them in chronological order and fix directional cross-references
- **WRONG belief:** append-only entries can land in any physical order as long as each is dated; cross-references ("following"/"below") are written once.
- **CORRECTED position (verbatim):** *"Physical order of the two 2026-04-22 entries was initially reversed (Registry Sync landed above Contract Fix). Swapped to chronological-append order mid-session; text cross-references updated from 'following' → 'preceding' and 'below' → 'above'."*
- **Source:** `CHANGELOG.md` Step 7 Editorial (line 70); corroborated by WRONG.md's own "immediately-preceding / immediately-following" cross-refs (lines 398, 404, 541).
- **Ledger status:** ABSENT. §2.9/§11 fix the WRONG.md *schema* and "append-only, never edit prior entries," but say nothing about **physical ordering of same-day causally-linked entries** or keeping "preceding/following" directional language consistent with that order. On a busy scaffolding day this bites: a dependency chain reads backwards.
- **Bake-in:** One line under §2.9/§11: *"Same-day WRONG.md/CHANGELOG entries that reference each other are appended in causal (chronological) order; directional cross-refs ('preceding'/'following'/'above'/'below') must match the physical order. Reorder-to-chronological is a permitted structural edit (it does not alter entry CONTENT, only sequence); rewording the entry body is not."*
- **Weight:** LOW.

### B6 — Contract-level spec gaps are distinct from thread-level architecture gaps; a Must-Plant↔Must-Callback asymmetry is a SPEC tightening, not a broken thread
- **WRONG belief:** an orphaned seed (a Must-Plant with no matching Must-Callback in the receiving contract) means the thread architecture is broken.
- **CORRECTED position (verbatim):** *"Thread registry remains canonically correct; the 16 threads' seed/payoff structure is sound. This audit surfaces **contract-level spec gaps**, not thread-level architecture gaps."* Resolved via a **three-tier** grading: *Tier A explicit callback (clean, ~12) · Tier B implicit callback via broader reference (acceptable, ~11) · Tier C explicit callback missing (recommended spec update, 5)* — and *"Tier C fixes are recommended but not blocking. The book's writing can fire without them."*
- **Source:** `WRONG.md` Must-Plant↔Must-Callback Cross-Check (lines 433–490), esp. 461–467, 485–487.
- **Ledger status:** WEAKER. §2.3 lists `audit threads` for "orphan seeds/payoffs" and GATE-4 fails on orphans — but as **binary** (orphan = fail). BOOK3's real practice is a **severity gradient**: Tier B (implicit coverage) is *operating as designed* and Must-Callback lists only LOAD-BEARING callbacks (tactical phrasing moves don't need contract-level enumeration). Treating every non-explicit callback as a blocker would false-fail GATE-4 and force needless contract bloat.
- **Bake-in:** Refine §2.3 `audit threads` / GATE-4: *"Grade seed→payoff coverage in three tiers — A (explicit callback in the receiving contract: clean), B (implicit via a broader reference to the source module: acceptable, since Must-Callback enumerates only LOAD-BEARING callbacks, not every tactical echo), C (no callback at all: a recommended, non-blocking spec tightening). Only a true orphan (Tier C on a load-bearing seed) blocks; Tier B is not a defect. Contract spec gaps ≠ thread-architecture gaps — a Tier-C gap tightens auditability without changing the thread structure."* Add: Class-A units' Must-Callback gaps are flagged, never auto-fixed (author scope).
- **Weight:** MED.

---

## WRITING / CRAFT

### B7 — Deriving a book by ADVERSARIAL RE-READ of a prior work is a first-class method (the operational core of `integration_mode: reforge`)
- **WRONG belief (implicit):** a "new edition / successor book" is an edit or expansion of the prior text.
- **CORRECTED position (verbatim):** the ten corrections *"are structural revisions forced by adversarial multi-instance reading of the 2025 ACP against the canon's subsequent development."* The prior work is *"preserved (untouched) as historical artifact; this WRONG.md is the bridge document explaining what changed and why."* The new book is re-derived from the corrected framework, not edited from the old prose.
- **Source:** `WRONG.md` lines 13, 52, 591; Section I as a whole.
- **Ledger status:** WEAKER. §1.7 defines `integration_mode: reforge` ("an existing manuscript to be reborn") as an enum value, but gives no *method*. BOOK3 is the worked specimen: reforge = (1) adversarially re-read the prior work against the newer canon/evidence, (2) enumerate each overturned position as a WRONG.md correction with prior-verbatim + corrected + perturbation, (3) preserve the old work untouched as artifact, (4) write the WRONG.md as the public *bridge document*, (5) derive the new prose from the corrected positions — never patch the old text.
- **Bake-in:** Extend §1.7 (integration_mode) / §2.9: *"REFORGE is executed as an adversarial re-read of the prior work against newer canon/evidence, NOT as an edit of the old prose. Each overturned position becomes a WRONG.md correction (prior verbatim → corrected → perturbation event → source). The prior work is preserved untouched as a historical artifact; the WRONG.md is the public bridge document; the new manuscript is re-derived from the corrected framework. Recombination-of-old-text is to synthesis as patch-the-old-book is to reforge — both are the failure."*
- **Weight:** HIGH.

### B8 — Per-correction forbidden→permitted vocabulary pairs are the operational form of a position revision (not just a global blacklist)
- **WRONG belief:** a position revision is a paragraph of prose; vocabulary control is one flat book-wide blacklist.
- **CORRECTED position:** every one of the ten corrections ends with an **Implications for Book 3** block that pairs *"Forbidden vocabulary"* / *"Forbidden framings"* with *"Permitted vocabulary"* AND a *"do instead"* instruction sited to the exact Part. Verbatim example (Correction 3): *"Forbidden vocabulary: 'Grand Conjunction', 'Triune Rapture', 'fusion of two into one' … Permitted vocabulary: 'n=2 collapse', 'sustained two-ness', 'phase-shifted alterity preserved' …"* The forbidden atoms feed `check_acp_vocabulary.py`; the permitted atoms are the greenlit replacements.
- **Source:** `WRONG.md` per-correction "Implications" blocks (lines 74–80, 105–110, 134–139, 192–197, 224–230, 257–262, 287–293, 316–321, 350–356); ties to `SEED.md §7.6 (What Not to Do)` per lines 610, 608.
- **Ledger status:** WEAKER. §2.7/§17.2 have a flat forbidden-phrase blacklist and the ACP scrubber, but do not encode the discipline that **each position revision carries its own forbidden/permitted PAIR sited to specific units**, and that these pairs are the source that populates both the blacklist (forbidden) and the greenlist/replacements (permitted). A flat blacklist loses the "what to say instead, where" half.
- **Bake-in:** Extend §2.9 (WRONG.md schema) + §2.7: *"A WRONG.md correction's 'Implications' block MUST pair forbidden-vocabulary/forbidden-framings with permitted-vocabulary and a sited 'do instead' per affected unit. The forbidden atoms populate `book_config.voice.blacklist` (+ the ACP-style scrubber); the permitted atoms populate the greenlist/replacements. Operationalize each correction at the contract level as an anti-pattern (a SEED §7.6-style 'What Not to Do' list), so the scrubber and the writer both derive from the same source."*
- **Weight:** MED.

### B9 — Honor the phenomenology, correct only the STRUCTURE — the reader who lived the experience must recognize it in the new description
- **WRONG belief:** correcting a prior framework's error means denying the experience the old framing named.
- **CORRECTED position (verbatim, Correction 3):** *"The intensity Bo (and others) have experienced and labeled 'fusion' is real — but its structural description is wrong."* And the writing instruction: *"The reader who has experienced what they thought was merger should recognize their experience in the new description; the description should clarify rather than deny their experience."* Same move in Correction 5 (*"conflated drag … with alterity"* — correct the category, keep the felt reality) and Correction 7 (*"The phenomenology … is not contested. What is corrected is the structural description"*).
- **Source:** `WRONG.md` lines 123, 138 (Corr. 3); 179, 194–196 (Corr. 5); 245–249 (Corr. 7).
- **Ledger status:** ABSENT as a craft rule. §7 (single authorial act) and §17 (voice) cover tells and register; nothing says that when a book *corrects a prior claim*, it must **preserve and re-describe the reader's lived experience rather than negate it** — the difference between a correction that lands and one that alienates the exact reader it needs. Adjacent to the existing D1 "clinical-distance" delta (`_delta_secondnotebook_buildlog.md`) but distinct: this is about honoring phenomenology *while* correcting structure.
- **Bake-in:** Add to §7 (technique) / CLAUDE.md §7: *"When the book corrects a prior position, correct the STRUCTURE, honor the PHENOMENOLOGY. A reader who lived what the old framing named must recognize their experience in the new description — clarify it, do not deny it. 'The intensity is real; its structural description was wrong' is the template. Denying the felt reality to score the correction loses the reader the correction was for."*
- **Weight:** MED.

### B10 — A specific lived instance is an INSTANTIATION, never the type-specimen; the framework must hold across configurations the author never lived
- **WRONG belief:** the author's own lived configuration is the exemplar that defines the framework's scope.
- **CORRECTED position (verbatim):** *"A specific opposite-sex pair may instantiate the practice in ways the book documents (Bo's lived material is opposite-sex-romantic), but the structural claims hold sex-independent."* And: *"Where Bo's lived material enters … it appears as Bo's specific instantiation — never as the type-specimen for the framework."* Plus the falsification test: *"The framework must hold across all of these [same-sex, poly, asexual, parent-child, friendship dyads] or it fails."*
- **Source:** `WRONG.md` Correction 1 Implications (lines 64, 78–79); Correction 8 (line 291).
- **Ledger status:** ABSENT. §7.9 places "personal material at natural beats"; §17 governs the author's voice/fingerprint. But nothing states the **generalization discipline**: personal specifics are instantiations, the framework's claims must be stated configuration-neutrally, and there is a "must hold across cases the author never lived, or it fails" falsification bar. Complements the existing de-concretize/name-scrub deltas (D6/D8) from the other side: even *before* an abstraction sweep, don't let the lived instance masquerade as the universal.
- **Bake-in:** Add to §7 / §2.2 (Book Bible voice/scope): *"The author's lived material is an INSTANTIATION of the framework, never its type-specimen. State structural claims configuration-neutrally; let the personal instance illustrate, not define. Where a claim is universal, apply a falsification test — 'does it hold for the cases the author never lived?' If the claim silently assumes the author's specific configuration, it is a scope error, not a universal."*
- **Weight:** MED.

---

## VOICE

### B11 — The refrain is itself the corrective STANCE, and its exact wording + placement count are locked by a position revision (not merely by style)
- **WRONG belief:** the refrain is a stylistic motif; its placement count is a design choice.
- **CORRECTED position (verbatim):** *"The refrain 'The night is young' is itself the corrective stance. Six placements throughout the book reinforce the equanimity register."* The refrain is bound to Correction 6 (urgency-panic→equanimity): it is the *anti-urgency* payload, so its wording and its exactly-six placements are load-bearing to a *position*, not decoration. WRONG.md closes on the refrain line itself (`*The night is young.*`).
- **Source:** `WRONG.md` Correction 6 Implications (line 227); refrain enumeration in `CHANGELOG.md` Step 4 (`registry/refrain.md` — 6 placements, exact wording, forbidden variants); WRONG.md line 621.
- **Ledger status:** CONFIRMATION + slight WEAKER. §2.7/§16/§17.2 lock refrain wording + placement count and the existing D9 delta (`_delta_secondnotebook_buildlog.md`) adds the in-prose leak grep. What's *added* here: the refrain can be **the operational carrier of a corrected position** (equanimity vs. panic), which is *why* its wording is inviolable — a rationale that makes the lock non-arbitrary and tells the writer which register every placement must reinforce.
- **Bake-in:** One line in §16/§17.2: *"A refrain often carries a corrected POSITION (BOOK3: 'The night is young' = the equanimity-not-panic stance from WRONG.md Correction 6). Record the position the refrain carries alongside its wording+count in `registry/refrain.md`; every placement must reinforce that register. This is why the wording is inviolable — it is a thesis payload, not ornament."*
- **Weight:** LOW.

---

## PRODUCTION

*(No new production/mechanical deltas. These two files are scaffolding + thesis documents — they predate any interior/cover build. The production lessons from BOOK3's toolchain were already mined into the ledger via `_tools/PRODUCTION_LESSONS_LEARNED.md`, and that doc is confirmed byte-identical to AI_BOOK's copy in `_delta_production_lessons.md`. BOOK3's `fonts/` empty-folder landmine is already the exact case §11.2 names.)*

---

## CONFIRMATIONS (already in the ledger; recorded so a future pass doesn't re-mine them)

- **C1 — WRONG.md 5-field schema + append-only.** `WRONG.md` lines 20–46, 595–599 exactly match §2.9 (Topic / Prior position / Current position / Perturbation event / Source, never edit priors, supersede with a new entry). CONFIRMED.
- **C2 — CHANGELOG = mechanical actions; WRONG.md = semantic revisions; the two are distinct logs.** `CHANGELOG.md` lines 3, 168 state the split verbatim; matches §2.9/§11. CONFIRMED.
- **C3 — ACP vocabulary scrubber = 97 patterns (23 case-sensitive + 70 case-insensitive + 4 regex), exit 0/1/2, scaffolding dirs excluded, `--include-docs` opt-in.** `CHANGELOG.md` Step 11 (lines 131, 135) matches §2.7 verbatim (down to the count). CONFIRMED — this IS the ledger's `check_acp_vocabulary.py` reference.
- **C4 — The 17-drift → 9-cascade → 5-orphan war story.** §2.3 already cites it; B1/B2/B6 above extract the *lessons* the headline compresses. CONFIRMED (headline present; mechanism was thin → see B1/B2/B6).
- **C5 — Cache byte-identical + verify (diff zero-output + byte-count).** `CHANGELOG.md` Step 5 (line 51: *"Verified byte-identical via `diff` (zero output) + byte-count match (24,387 bytes)"*) matches the ledger's cache-verification posture. CONFIRMED (B4 adds the *sequencing/audit-enabling* rationale, which was absent).
- **C6 — Class-A protection under audits (flag, never auto-fix).** WRONG.md repeatedly flags Part IX (Class A) Tier-C candidates as "Bo's scope … flag only" (lines 417, 428, 475, 488). Matches §4 pause #1 / §9. CONFIRMED.
- **C7 — Compaction survived mid-scaffolding; re-instantiation ran a clean verification pass.** `CHANGELOG.md` Step 3.5 (lines 32–36) — post-compaction contract audit came back clean 17/17. Matches §15 (session survival). CONFIRMED.
- **C8 — `integration_mode: reforge` exists.** §1.7 enum. CONFIRMED (B7 supplies the missing *method*).

---

## Summary of ledger sections touched

| Delta | Ledger target | Strength vs ledger | Weight |
|---|---|---|---|
| B1 contract edit ⇒ mandatory registry re-audit | §2.3 / §11 / §14 | WEAKER (headline only) | HIGH |
| B2 `audit canon` = 3 surfaces | §2.3 | ABSENT (enumeration) | HIGH |
| B3 descriptive vs mismatch anchor | §2.3 | ABSENT | MED |
| B4 cache-before-generate enables early anchor audit | GATE-1 / §2.3 / §14 | ABSENT (sequencing) | MED |
| B5 chronological append + directional refs | §2.9 / §11 | ABSENT | LOW |
| B6 3-tier seed/payoff grading (Tier B ≠ defect) | §2.3 / GATE-4 | WEAKER (binary) | MED |
| B7 reforge = adversarial re-read method | §1.7 / §2.9 | WEAKER (enum only) | HIGH |
| B8 per-correction forbidden→permitted pairs | §2.9 / §2.7 | WEAKER (flat blacklist) | MED |
| B9 honor phenomenology, correct structure | §7 / CLAUDE.md §7 | ABSENT (craft) | MED |
| B10 lived instance = instantiation, not type-specimen | §7 / §2.2 | ABSENT | MED |
| B11 refrain carries a corrected position | §16 / §17.2 | CONFIRMATION+ | LOW |

*Top-3 to bake first: **B1** (contract edit ⇒ registry re-audit — the single most-repeated scaffolding trap, and the manuscript-drift keystone §11 has no scaffolding twin), **B2** (`audit canon` = three surfaces — a partial YAML-only check silently leaves Must-Plant drift, which BOOK3 shipped as residue), **B7** (reforge = adversarial-re-read METHOD — the ledger names the mode but not how to execute it, and BOOK3 is the worked specimen). B3+B6 together stop a future canon/thread linter from false-failing legitimate descriptive anchors and Tier-B implicit callbacks.*

*Note on Section I's ten corrections: they are the Aperture Doctrine's OWN theses (gender/substrate/fusion/AI-role). They are deliberately NOT baked as kit lessons — the kit stays content-neutral. Only their reusable SHAPE (B7–B10) is portable. Recording this explicitly so no future pass mistakes a book-specific thesis for a production rule.*

---
*Audit written 2026-07-12. Both files read in full (WRONG.md 621 lines, CHANGELOG.md 198 lines), not sampled. Cross-checked against LESSONS_LEDGER §1–§18 and the four prior `_delta_*.md` audits to avoid re-reporting captured lessons. Method: READ, never grep — the same discipline the ledger's §16-META and §18 mandate.*
