# BOOK 3 BUILD — NOTES & LESSONS LEARNED
*The complete journey of building *Claude at Work* (claude_at_work), written for BOOKSMITH itself. Companion to the append-only record (workspace `BUILD_LOG.md` + `CHANGELOG.md`, timestamped) and the distilled rules folded into `LESSONS_LEDGER.md` §21. Written 2026-07-28 by the build session, while the logs were still warm.*

---

## 0. The build in one paragraph

One overnight session (2026-07-27 20:39 CST → 2026-07-28 morning), one prompt, full standing authority, zero interactive pauses. Input: a single 60,146-token canonical master source (gist + thesis + voice bible + refrains + chapter map + four-layer fact base with binding reconciliation rulings + allocations + colophon spec + locked decisions) — the cleanest intake the kit has ever received. Output: 27 units / 69,889 manuscript words (70,414 with config front matter), nine formats all `verify_build` ALL_PASS, a cover that survived four operator rounds, refrain counts grep-exact (3+1), scan gate 0-fail/0-warn, selfcheck 0/0, continuity ledger COMPLETE and machine-consistent. Roughly 30 lint passes, ~9 classes of defect caught by gates during the build, three kit tools improved as side effects. The human never saw an unverified state.

## 1. What the intake taught (the upstream lesson)

**A pre-reconciled master source is worth more than any pipeline improvement.** Book 3's intake arrived as ONE file that had already swallowed its raws: fact base reproduced verbatim in four layers, conflicts pre-adjudicated by numbered rulings (R-1..R-15), per-chapter fact allocations, kill-list enumerated, decisions locked, assumptions logged. The whole INGEST stage collapsed to: size it, slice-read it fully, write the manifest. No digest fan-out, no reconciliation risk, no satellite drift. **Recommendation:** for any future fact-heavy book, spend the tokens on a SYNTHESIZER pass that produces this exact artifact shape *before* BOOKSMITH boots. The master source's section pattern (0 gist / …/ 5 fact-layers+rulings / 6 allocation / 10 assumptions+worklist) should be treated as a reusable template; consider `templates/master_source.template.md`.

**The operator-substituted pause pattern works.** "Instead of a mirror-back pause, write your mirror paragraph and assumptions ledger as the first entry in BUILD_LOG and proceed" — this preserved the *function* of the pause (a falsifiable statement of understanding, reviewable later) without the latency. Same for pre-answering the four sanctioned pauses. The build stayed auditable because every exercise of the authority was logged at the moment of exercise. **Pattern to keep:** autonomy is granted per-decision *in advance, in writing*, and spent *with a log line*.

## 2. Drafting: the length-calibration phenomenon (the build's biggest time cost)

The model consistently drafts **~65–80% of its intended length**. A chapter planned at ~3,200 words landed at ~1,700–2,400 on first pass, *reliably*, across 17 chapters, even after explicit "draft LONG" self-instructions. Dense prose *feels* longer from inside than it measures. Consequences and fixes:

- Nearly every chapter needed 1–4 fix-loop extension passes to clear its ±20% floor. The extensions were real content (worked scenes, cousins catalogs, honest-limits passages), and the book is better for them — but planned-for-expansion beats retrofit.
- **The floors themselves misled twice.** I padded config `target_words` above the master's §4.1 architecture "to land high," which inflated the floors and produced false gate failures; the fix was reverting config to the architecture of record (a CHANGELOG-logged correction). *The config is an instantiation; the architecture wins.*
- **Exact-integer floors produce one-word comedy.** ch_03 passed at 2,439 vs floor 2,440; three chapters landed within 15 words of the line and needed a single sentence added. A ±1–2% tolerance band on the word gate would retire an entire genre of trivial fix loops. (Ledger §21.2.)
- **The working rule adopted mid-build:** brief for +25–35% over target ("cut lumber long"), and when extending, insert *fewer, bigger* passages — my ~200-word insertions netted half of what they felt like; 450–550-word passages moved the number.
- A late total-length crisis (54.8K at all-units-drafted vs a 70K ratified floor) was closed by a designed **enrichment pass**: two full passages per chapter, planned per-chapter for what the contract could still absorb (worked beats, second scenes, honest-limits gathers), which doubled as seam-strengthening. It worked, but it cost hours. Budgeting the overshoot up front is strictly cheaper.

## 3. The voice gates: what it's like to write inside them (ergonomics report)

- **The blacklist bites its author, and that is the feature.** "in this chapter" was caught **five times** across drafts — each a real structure-signaling slip. Zero survived. The em-dash count across ~70K words: zero, enforced, never once painful because the semicolon/colon/period rerouting is now reflex at drafting time.
- **Blacklist atoms are SUBSTRINGS; audit every new atom against innocent containers.** Two live bites: `"very "` ⊂ `"every "` (caught at config time before any prose) and `"the landscape"` ⊂ `"the landscapers"` (caught in a chapter, prose rewritten). Design rule: before adding an atom, grep it against a common-words list; prefer the longest safe form; remember case-insensitive matching. (Ledger §21.3.)
- **The fill-in-blank trap:** a form-style blank written as `____` was rejected by the corruption lint (EMBEDDED_UNDERSCORE) — correct behavior; underscore runs garble print. Blanks are written as prose ("finish this sentence: to undo this, I would"). This became the colophon's flagship caught-defect story.
- **CJK strays are real:** one Chinese numeral (五) appeared mid-English-sentence in an insertion (bilingual model artifact). A full-manuscript CJK/fullwidth sweep is two lines of Python and should run inside `scan_manuscript.py` as a standing check for English-language books. (Ledger §21.13.)

## 4. Truthful-candor features need their own gate (the most important new lesson)

The book's Behind-boxes (candid chapter-end notes about how the pipeline built that chapter) and its colophon are *truth-claiming* features. **Twice, the model drafted plausible-but-false process history** — "a sentence was cut" describing a cut that never happened; "was drafted, read, and rejected" for a rejection that was really a planned choice. Both were caught only because a standing rule existed: *drafted history must match the log*. The generalization matters beyond this trilogy: **any feature where the machine narrates its own process will attract fabricated plausibility, and it needs a mechanical-adjacent review step** (diff the claim against CHANGELOG/BUILD_LOG before promotion). The colophon now publicly commits the pipeline to promoting this from review habit to standing gate. (Ledger §21.4.)

Related, delightful, true: **the colophon was rejected by the very lint it praises** (its first draft *quoted* the banned strings while describing them). Fix: describe-not-quote — and the rejection itself became the strongest sentence in the colophon. Self-referential chapters should expect to trip their own gates; write that expectation into their contracts. (Ledger §21.12.)

## 5. Registry law vs. chapter furniture (a precedence ruling worth keeping)

The "every chapter ends with a Behind box" convention collided with the hard law "the north star is the FINAL LINE of ch_16." Ruling (A-BS-13): **verbatim-placement law outranks furniture conventions; the colophon that follows IS the behind-the-scenes.** Also caught by the GATE-4 refrain grep: a near-verbatim embed of the north star in colophon prose ("It says a human still signs") — rewritten. The refrain audit must grep for the raw four-word sequences *case-insensitively, everywhere*, titles exempted by rule, and near-verbatim embeds count as violations. Both are now demonstrated precedent.

## 6. The production stage: what broke, what held

- **`produce_book.py` is Book-1-shaped.** Its cover step is hardwired to `cover_compose_ahss.py` (demands `back_copy.json`) and its `--formats` roster silently omits epub, both paperbacks, and both Blurb formats. Its interiors chain (generate → inject ×2 → Word-COM render) ran green and its error-propagation is sound (it correctly refused to build digital from a red interior). **Fix needed:** per-book compositor selection (config-driven: house `composite_cover.py` vs bespoke `cover_compose_*`) + the full nine-format roster. Until then: the §12 manual chain is the reliable path and took ~40 minutes for all nine formats. (Ledger §21.5.)
- **Word COM, mirror injection, recto parity, page multiples, spine math, EPUB structure: zero incidents.** The proven core is genuinely proven; every one of the 25 anti-forgetting matrix rows held without drama. 236pp KDP (÷4 even), 252pp Mixam (÷4), spine widths verified to 4 decimals on the first try, all nine `verify_build` ALL_PASS on the first full sweep.
- **`check_continuity` teaches its own format the hard way:** flipping the ledger to COMPLETE failed the meta-gate until the ledger *named every unit id* in a DONE list and carried the footer `STATUS:` token + SHIPPED marker. Document this in the ledger template so the next book writes it right the first time. (Ledger §21.10.)

## 7. The cover: one fallback ladder + four operator rounds (the richest lesson cluster)

**The art ladder worked as designed.** SDXL stack: GPU ✓, checkpoint ✓, but the ComfyUI *desktop app* would not bind :8188 from a cold programmatic start (launched, polled ~4 min, never served; likely needs one interactive first-run). `cover_pick` fallback delivered a real prerendered SDXL catalog piece in seconds. **Action:** run one interactive ComfyUI first-launch on this box so `cover_gen.py` can be exercised next build; keep the ladder exactly as is — it converts a GPU outage into a two-minute detour. (Ledger §21.8.)

**GATE-6 (perceptual) caught what GATE-5 (mechanical) structurally cannot,** three times before any human looked: a 16-word subtitle clipped at both trims (the shrink loop bottomed at its floor and drew anyway), the series line missing from cover copy, and — after fixing those — the back-blurb tail pushed into the bleed by the new series footer. Then the **operator's eye caught what my perceptual pass under-weighted: from-afar/thumbnail legibility.** Four rounds followed, each generalizing into the house compositor:

1. **Subtitle overset → balanced-line wrap below the shrink floor** (never draw overset; wrap 2 then 3 lines and re-fit). The bespoke compositors had learned this on Book 2; now the house tool knows it.
2. **Series line** belongs on the cover for a series book → back-panel footer sourced from config `dedication` (the kit's series-page convention). 
3. **Anything added above the back blurb pushes its tail into the bleed** → the blurb is now fit-to-box: a measurement pass shrinks the size until the full flow + refrain reserve fits above `text_bottom`. General rule: *every text block that grows needs a bounded flow, not a hopeful one.*
4. **Thumbnail contrast law (operator-taught, twice):** on LIGHT art, **dark type with a cream halo** beats cream-with-dark-halo; and **bands/scrims read as haze at 6×9-thumbnail scale** — we added a scrim for contrast and removed it a round later because the *letterform* (size, bold TTF, heavy halo) is where contrast should live. Poster-size the title (0.085·panel vs the old 0.058), push the bottom block up sizes rather than lighting it.
5. **Flat brand marks want the ink-stencil path:** the new `cover.center_icon` (schema'd: path/width/center_y_frac/ink/glow) renders an alpha-masked emblem on every front; native salmon camouflaged against sepia, and one config line (`ink: C3491C`) re-inked it as rich burnt orange. For flat single-color glyphs, solid re-inking loses nothing and gives exact saturation control. Asset triage rule that decided among the three provided logos: *true-alpha + high-res + no embedded words wins* (an RGB no-alpha starburst and a "Claude" wordmark were passed over, reasons logged).
6. **Center-icon effects must be front-panel-constrained** — a naive full-canvas band/glow bleeds onto the back panel of `[back|spine|front]` wraps. Clamp x to the front panel (the rightmost panel on every wrap profile).
7. **IP note now standing:** another party's mark on a cover is a first-class UPLOAD_CHECKLIST counsel item, with the 10-minute removal path documented (delete `center_icon` → recomposite 7 → rebuild digital/EPUB). (Ledger §21.6/21.7.)

**Meta-lesson:** the cover loop with a human in it converged in four cheap rounds *because* every round was config-or-compositor, never hand-edited art. Keep covers 100% regenerable; the operator's taste then costs minutes per iteration.

## 8. The live-pass during build (do this for every fact-based book)

Three checks were run live from the build session and all three *changed the book*: the GitHub API found the author's repos public (superseding two research passes' could-not-verify; WRONG.md entry staged; the colophon's maturity wording rewritten from live READMEs — including replacing a stale "Nothing has run." with the repo's actual "Gate B passes… not an unqualified pass"); the skills manifest recount (exactly 17) went into the chapter *with its build-date*; the MCP spec's release-candidate status turned a "finalizes at the stamp" sentence into an honest two-state sentence. **Pattern:** at ingest, split the source's verification worklist into *feasible-now* (run them, append findings to canon_refs as a dated addendum under the reconciliation's precedence rules) and *preprint* (calendar-stamped checklist). Cheap, high-yield, and it produced the book's single best colophon material. (Ledger §21.9.)

## 9. Small patterns worth keeping (grab bag, all field-tested this build)

- **Ending-shape rotation assigned in contracts** (image / verdict / question / callback / instruction / aside) prevented the same-close tell across 27 units mechanically.
- **Interludes as part-openers with a no-facts law** gave the seam pass five guaranteed-clean boundaries and the book its breathing rhythm; the aperture register survived enrichment untouched.
- **Composite-cast continuity** (June's Tuesday, the Keller office manager, the Arlington shop) let CP-pairs close concretely; the back matter's "cast roll call" then disclosed the device honestly.
- **Per-unit Bash cadence** (`cp draft → current && lint && wc`) after every unit caught leaks within minutes of writing them; total lint cost across the build was trivial against what it caught.
- **The workspace ledger + handoffs carried the build across context compaction with zero loss** — the resume machinery was never *needed* dramatically, which is what it looks like when it works.
- **selfcheck after every kit-tool edit** (three compositor patch rounds + one schema extension) kept the kit giftable throughout; the schema extension pattern (optional key, additionalProperties intact, example config untouched) is the right shape for feature adds.

## 10. Prioritized kit actions (the to-do this document exists to hand over)

1. **produce_book.py:** config-driven cover-compositor selection + full nine-format roster (HIGH — it currently cannot produce this book unattended).
2. **Word-count gate tolerance band** (±1–2% or "floor minus 25 words") in scan/engine gates (HIGH — removes the largest source of trivial fix loops).
3. **Behind-box/colophon truth gate:** diff machine-narrated process claims against BUILD_LOG/CHANGELOG before promotion (HIGH — integrity of the trilogy's signature device).
4. **CJK/fullwidth sweep into scan_manuscript.py** for English books (MEDIUM, two lines).
5. **Blacklist-atom linter:** warn when a new atom is a substring of common English words (MEDIUM; would have caught both live bites at config time).
6. **Interactive ComfyUI first-run on this box**, then re-test `cover_gen.py` end-to-end (MEDIUM).
7. **Master-source template** distilled from Book 3's intake shape (MEDIUM — biggest upstream multiplier).
8. **Drafting contracts: bake the +25–35% overshoot brief** into the engine/contract template (LOW once tolerance lands, else MEDIUM).
9. **check_continuity ledger requirements** documented in the ledger template (LOW, one paragraph).

*Everything above is verifiable against the workspace's CHANGELOG timestamps. Nothing in this document is reconstructed from memory; it is last night's log, organized.*
