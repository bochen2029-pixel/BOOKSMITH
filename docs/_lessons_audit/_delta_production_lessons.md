# DELTA AUDIT — canonical PRODUCTION_LESSONS docs vs. the kit ledger

**Method:** read-in-full (opposite of the grep-mine that seeded the ledger) of the three canonical docs the ledger claims to consolidate, verified against `docs/LESSONS_LEDGER.md` (§1–§17, 694 lines).
**Anchored date:** 2026-07-12 (Central Daylight; `Get-Date` at audit time).
**Auditor:** subagent, OPUS-class, full-read pass.

## Sources read (in full)
| Doc | Date | Role | Board-add it carries |
|---|---|---|---|
| `C:\ASTRA-7\book\production_lessons_learned.md` (1563 lines, §1–§19) | 2026-05-15 | **current canon** per ledger | +0.348 (new) but see D1 |
| `C:\BOOK3\_tools\PRODUCTION_LESSONS_LEARNED.md` (311 lines) | ~2026-04-20 | Titanic-era "Night Was Young" seed; ledger says **superseded** | +0.302 (old) |
| `C:\AI_BOOK\_tools\PRODUCTION_LESSONS_LEARNED.md` (311 lines) | ~2026-04-20 | **byte-identical to BOOK3** (MD5 `48a52e06…` both) — same file mirrored | +0.302 (old) |

**Headline:** the ledger's consolidation is *substantially faithful and often deeper than the sources* (it adds Mixam non-constant board-add, page-count-band dependence, the 0.75" gutter overshoot rationale, ISBN keep-out coords, the em-dash gate). The deltas below are (a) a small number of **wrong/misleading numbers**, (b) a set of **conventions/aesthetics the miner never surfaced** (spine-side pad, proof copies, category count), and (c) an entire **writing-methodology layer** (M0 soul doc, single-axis multi-pass revision, Mode A/B, parallel-instance cold audit) that the ASTRA canon devotes its first ~130 lines to and the ledger reduces to near-nothing. None overturn a shipped mechanical gate, but D1 and D7 are latent-rejection risks and D5 is a wrong metadata number.

---

## TIER 1 — WRONG or DANGEROUSLY MISLEADING NUMBERS

### D1. The 186pp hardcover spine worked-example is only *coincidentally* right, and the canon's own cheat-sheet states it WRONG — the ledger inherits a fragile anchor
- **Source (ASTRA §19.4, verbatim):** *"186pp cream → 14.183\" × 10.417\", spine **0.813\"** (using 0.348 board) or **0.767\"** (using 0.302 board)."* ASTRA §7.1 table row: *"Cream × 186pp … Hardcover spine (paperback spine + 0.348\")"* → i.e. 0.465 + 0.348 = **0.813**.
- **Ledger has (§5.5, §13):** *"186pp **white** HC → 14.183\"×10.417\", spine **0.767\"**."* And the safe-default formula `pages × 0.002252 + 0.348` (white).
- **The arithmetic (verified this pass):**
  - KDP's *stated* wrap width for 186pp = **14.183"** → reverse-derived spine `14.183 − 12 − 1.416` = **0.767"** (this is the ground truth the validator wants).
  - cream+0.302 = 0.465+0.302 = **0.767** ✓ (old Titanic calibration, CREAM)
  - white+0.348 = 0.4189+0.348 = **0.7669 ≈ 0.767** ✓ (new ASTRA calibration, WHITE)
  - cream+0.348 = 0.465+0.348 = **0.813** ✗ (ASTRA §19.4's headline "0.348" number — does NOT match the validator)
- **What this means:** the two calibrations agree on 0.767 for 186pp **only because the paper differs** (cream↔white ≈ 0.046" ≈ the 0.302↔0.348 board delta). The ledger is RIGHT to pin white+0.348→0.767 because **KDP hardcover is white-only** (correctly stated at ledger §5.2/§9.2). But two hazards remain:
  1. **ASTRA §19.4's own "0.813 (using 0.348 board)" is computed on cream and is wrong for a white-only HC** — if a future maintainer "reconciles toward the canon's stated number," they will regress to 0.813 and get rejected. The ledger should explicitly note that the canon's cheat-sheet HC example is cream-based and therefore not the operative number.
  2. The convergence is **page-count-specific** — it does not generalize to other page bands (the ledger already teaches this at §5.3/§13 via the ASTRA-7 186pp counter-example where `×0.0025+0.241`→0.706 but KDP demanded 0.767).
- **Bake-in:** ledger §5.5 worked-examples — add a one-line footnote: *"HC is white-only; the 0.767 for 186pp = white×0.002252 + 0.348. The ASTRA canon §19.4 also lists 0.813 (cream+0.348) — that is cream-based and NOT the operative white-HC number; do not adopt it."* Keeps the Previewer-wins meta-rule as the true arbiter.

### D2. HC wrap-height DERIVATION differs (0.708-turn-in gives 10.416, not 10.417) — the "why" is subtly off in the canon and the ledger silently corrects it
- **Source (BOOK3 gotcha G18 / ASTRA §7.1):** *"Arithmetic `9 + 0.708×2 = 10.416`, KDP uses **10.417**, validator checks the rounded number."* BOOK3 §"Final wrap dims" literally prints the HC height as **10.416** in its formula block, and only the gotcha corrects it to 10.417.
- **Ledger has (§5.3, §13#2, §14):** hardcodes **10.417** and calls it validator-canonical. ✓ Correct.
- **Delta:** none in the *default* (both land on 10.417). Recorded only because BOOK3's formula line (`9 + 0.708×2`) is the exact trap that produces 10.416 — the ledger's decision to hardcode 10.417 rather than derive it is the right call and is already baked (§13 conflict #2). **No change needed; logged for provenance.**

### D3. Mixam spine worked number for *The Night Was Young* (0.67" @ 204pp) is absent from the ledger's examples
- **Source (ASTRA §7.2, verbatim):** *"Spine: **0.67\"** (Mixam-calculated from 204pp × 70lb)."* Also ASTRA §7.2 fixes the stock: **70lb Text Uncoated**.
- **Ledger has:** §5.4 teaches Mixam board-add is non-constant and gives 0.160@204 / 0.110@548 back-solved examples, but does not record the *as-shipped* 0.67"/204pp/70lb data point.
- **Bake-in:** ledger §5.4 — add the shipped anchor `Mixam 204pp 70lb-uncoated → spine 0.67" (board-add ≈ 0.67 − 204×0.0025 = 0.16")`, and record **70lb Text Uncoated** as the Mixam default stock (currently unstated anywhere in the ledger).

---

## TIER 2 — CONVENTIONS / AESTHETICS THE MINER MISSED (no rejection vocabulary → invisible to a grep-keyed mine; exactly the §16-META blind spot)

### D4. Spine-side quiet zone must be padded an EXTRA 0.10–0.15" beyond the normal quiet zone — MISSING
- **Source (ASTRA §5.4, verbatim):** *"**Spine-side quiet zone is wider than other sides** — text near the spine reads cramped because the book bends there. Pad an extra 0.10-0.15\" spine-side."*
- **Ledger has:** §5.7 gives the uniform `bleed+0.25"` quiet zone (Mixam 1.05 / KDP-PB 0.375 / KDP-HC 0.958) but says **nothing** about the asymmetric spine-side pad. This is a pure aesthetic (no KDP rejection string) → the rejection-keyed miner never lit it up.
- **Bake-in:** ledger §5.7 + §14 cover-geometry checklist — add: *"spine-side text pad = quiet-zone + 0.10–0.15\" extra (the bend crowds it)."* Wire into `composite_cover.py` as a `SPINE_SIDE_EXTRA_IN = 0.125` inset on the front/back panel edges adjacent to the spine.

### D5. KDP category count — canon says **2 max**, ledger says **3** (WRONG number in the ledger)
- **Source (ASTRA §13.2, verbatim):** *"**Categories: 2 max** per KDP listing (e.g., Literary Fiction + Historical Fiction > 20th Century)."*
- **Ledger has (§9.1 + §9.1 exact-params, verbatim):** *"`categories[≤3 BISAC]`"* and *"Categories max 3 at submit (more via Author Central)."* — internally consistent with itself but **contradicts the canon's 2**.
- **Assessment:** KDP's self-serve picker historically = **2** at initial submit (canon), with more added later via Author Central. "3 at submit" is likely a conflation with the *keyword/BISAC* allowance or a newer-UI assumption. Anchored to 2026-07-12 this is *not* verifiable from the corpus alone; the corpus's only data point is 2. **The safe number is the lower bound (2).**
- **Bake-in:** ledger §9.1 — change `categories[≤3 BISAC]` → `categories[≤2 at submit; more via Author Central]` and the exact-params line "max 3 at submit" → "**max 2 at submit** (canon: ASTRA §13.2), additional via Author Central." Update the §14 metadata checkbox "≤3 categories" → "**≤2 categories at submit**." (If a live-KDP check on the run date proves 3, record it as a dated override — but default to 2.)

### D6. Order proof copies before mass-publish — MISSING (physical-proof discipline)
- **Source (ASTRA §8.9, verbatim):** *"Order proof copies before mass publishing — they're sold to you at print cost (~$5-8 for a paperback). Hold them, smell them, feel the binding. The PDF doesn't tell you whether the spine looks right. Physical proof does."*
- **Ledger has:** the KDP Print Previewer is treated as the terminal gate; **no** proof-copy step anywhere.
- **Bake-in:** ledger §10 (Verification Loop) + the export checklist — add an advisory post-Previewer step: *"For a physical run, order a proof copy at print cost before enabling distribution; the Previewer validates geometry, not the felt spine/binding."* (Advisory, not a hard gate — export can ship digital without it.)

### D7. Amazon-links-formats + the "add a format, don't create a new title" workflow — thin in the ledger
- **Source (ASTRA §8.5 / BOOK3 Step 4, verbatim):** *"If you already have a Kindle listing … adding a hardcover format to the same title automatically links them. You don't create a new title — you add a new format."*
- **Ledger has:** §9.4 covers the *compilation-detector* / series-linking nuance and §7.5 notes Kindle ships first, but the plain "add-format-to-existing-title auto-links; don't make a second title" operational rule is not stated as such.
- **Bake-in:** ledger §9 — one line: *"Add each new format (HC/PB) to the EXISTING Kindle title on KDP (auto-links editions); never create a separate title per format."*

### D8. Mixam premium extras (Smyth-Sewn vs Adhesive, matte-vs-gloss, head/tail bands, bookmark ribbon, endpapers) + KDP-lacks-these — MISSING
- **Source (ASTRA §7.2/§7.4/§7.5/§9.6/§9.7):** Smyth Sewn (lays flat, premium) vs Adhesive Casebound (faster); **matte = literary, gloss reads airport-thriller**; Mixam offers head/tail bands + bookmark ribbon + custom endpapers; *Night Was Young* shipped Navy ribbon + Navy/White bands, Adhesive, on 70lb; **KDP hardcover offers none of these binding extras**.
- **Ledger has:** §6.7 correctly captures the matte-vs-gloss aesthetic ("Glossy on literary fiction reads as airport thriller") — good. But the **binding options** (Smyth/Adhesive), **head/tail bands**, **bookmark ribbon**, **endpapers**, and the **KDP-can't-do-these** contrast are absent. These are premium-Mixam order knobs with no rejection string → missed.
- **Bake-in:** ledger §9.2 (paper/finish/trim defaults) or a short §5.x Mixam-premium note + `book_config.mixam_order_opts` — record: `binding: smyth|adhesive (default adhesive for speed)`, `lamination: matte (literary default)`, `endpapers: stock-white`, `head_tail_band` / `bookmark_ribbon` (Mixam-only; match palette). Note KDP-HC offers none.

### D9. IngramSpark is explicitly out-of-corpus (a known gap, not a covered platform) — MISSING as a stated gap
- **Source (ASTRA §12.3, verbatim):** *"The three books … did NOT use IngramSpark. There are **no IngramSpark-specific lessons captured here.** … different cover specs than KDP … returnability options … higher upfront fees ($49 setup)…"*
- **Ledger has:** no mention of IngramSpark at all — so a maintainer can't tell whether it's *unsupported* or *forgotten*.
- **Bake-in:** ledger §9 or §11 — one line marking IngramSpark **out of scope / uncalibrated** (library+bookstore channel; different bleed/spine; own validator) so the absence is deliberate, not an oversight.

---

## TIER 3 — THE ENTIRE WRITING-METHODOLOGY LAYER (ASTRA §1–§4, ~130 lines) IS BARELY REPRESENTED

The ledger is *production*-complete but *authorship*-thin. The ASTRA canon opens with four full sections on HOW the prose gets good; the ledger compresses this to §2.7 (anti-AI-tell) + §17 (voice) and drops the rest. These are load-bearing to the "single authorial act" bar the kit itself claims.

### D10. M0 "soul document" — pre-draft character architecture with the two-voice convergence test — MISSING
- **Source (ASTRA §1.1, verbatim):** a 54K-char "Maximum-Zero" consciousness architecture written **before any prose**; companion `M0_System_Prompt.md`; **the structural test:** *"Two voices describe the same person. That convergence is the document's structural test. Where they diverge, the document is wrong."* *"Errors caught at M0 cost minutes; errors caught at draft 5 cost weeks."* (repeated §16.4)
- **Ledger has:** SEED.md §1 "Book Bible" (Work Intent + voice exemplars) is adjacent but is a *book* bible, not a *character* soul doc, and carries no outside-voice/inside-voice convergence test.
- **Bake-in:** ledger §2.2 (SEED) — for fiction, require a per-principal-character M0 soul doc (or a SEED §1 sub-section) built pre-draft, plus the convergence test as a GATE-2 fiction check. Add `is_fiction`-gated. (The kit's `is_fiction` config already exists per CLAUDE.md §2 → wire it.)

### D11. Single-axis multi-pass revision (each pass = ONE dimension) + the empirical pass ORDER — MISSING
- **Source (ASTRA §1.2 + §4.2, verbatim):** *"Each pass has a **single dimension**. Don't mix 'fix historical accuracy' with 'improve interpersonal dynamics' — the conflated pass corrupts both."* + the shipped 8-pass topology (structural rewrite → phenomenology/fact → Mode-B peak rewrites → late research → late biographical → thematic integration → the single load-bearing comprehension → largest additions + tightening). Anti-pattern named: *"'tighten this AND thread a motif' produces a passage both compressed and expanded — the seams show"* (also G22).
- **Ledger has:** §2.8 version discipline (append-only v1→v7) captures *that* revisions happen, but **not** the rule that each revision targets exactly one axis, nor the recommended pass order. Nearest trace: §5 autonomous-loop "bounded 3-iteration fix" (mechanical, not editorial).
- **Bake-in:** ledger §2.8 or a new §2.x "Revision discipline" — bake the single-axis rule + the pass-order template as the `revise {unit}` protocol; forbid multi-axis passes in one version bump.

### D12. Mode A / Mode B prose taxonomy (analytical vs raw-perceptual; contrast IS the event) — MISSING
- **Source (ASTRA §2.3, verbatim):** **Mode A** = analytical/clause-stacking (≈90%); **Mode B** = raw perceptual, short declaratives, concrete nouns, deployed at ~8 peak emotional moments where the analytical apparatus fails; *"Mode B never dominates. It is the rare gas that Mode A flows around. **The contrast IS the event.**"*
- **Ledger has:** §2.7/§7 "register variation per unit" is adjacent but is *inter-unit* register variation, not the *intra-passage* A/B rare-gas contrast at emotional peaks.
- **Bake-in:** ledger §2.7 (anti-AI-tell) — add Mode A/B as a named intra-unit technique and a per-contract `register_profile` note marking each unit's peak-moment Mode-B beats. Corroborates author F4 "the hammer" (ledger §17.3) — same mechanism, name it.

### D13. Parallel-instance COLD audit (a second model, files-only, no chat history, on load-bearing passages) — WEAK
- **Source (ASTRA §1.3 + §16.7, verbatim):** for the highest-load passage, *"a second instance reading cold (no chat history, only files) catches the things the originating instance has locked into. Cost: one focused prompt + ~30K tokens. Yield: structural validation the originating session cannot self-perform."* Three canonical questions: structural audit / missing beat / sufficiency check.
- **Ledger has:** §2.9 mentions "adversarial review (5-role or Steelman/Skeptic) is first-class" and §15.3 sets subagent model policy — but the *cold, files-only, second-instance* discipline (the point being zero shared context) is not specified; the ledger's audits run inside the authoring session.
- **Bake-in:** ledger §2.9 / the `audit {unit}` command — for load-bearing units, spawn a **cold** subagent (files only, no transcript) with the three questions; distinct from the in-session Steelman/Skeptic. Ties to §15.3's one-tier-down model policy.

### D14. Bo-voice DNA specifics + fingerprints-not-typos list — PARTIALLY present, some atoms missing
- **Source (ASTRA §1.5 + §2.x, verbatim):** voice DNA (recursive restatement 3–6 framings; conditional cascades ending *necessarily/inevitable/no choice but*; **metaphors from physical/mechanical systems, never literature/pop-culture/business**; archaic-formality braided with colloquialism *indeed/alas/thereof/whilst/aforementioned* ↔ *etc etc etc/that guy/no-brainer*; scale-invariant cosmic↔bodily zoom; temporal-existential framing). **Bo-isms to preserve (NOT typos):** *"underlining" for underlying*; slash-compounds; **ellipses as connective tissue (not "trailing off")**; loose commas / 60+-word run-ons.
- **Ledger has:** §17 (Author Voice) is strong on the *negative* space (no em-dash, no tricolons, blacklist) and F1–F6 fingerprint, and §17.2 already says "do NOT correct Bo's own-voice misspellings." But some *positive* DNA atoms are thinner: the **mechanical-metaphors-only** rule, the **archaic⊗colloquial braid**, and **ellipsis-as-connective** are in the full profile (`docs/author_voice/…`) but not surfaced as ledger fingerprint atoms.
- **Bake-in:** ledger §17.3 fingerprint — add measurable atoms: F7 *metaphor domain = physical/mechanical only* (flag literary/pop/business vehicles); F8 *ellipsis-as-connective present*; and note the archaic⊗colloquial register-braid. (Most detail already lives in `AUTHOR_VOICE_Bo_Chen.md`; this is a surfacing, not new research.)

### D15. Anti-LLM-leak grep set — the ledger's is a superset EXCEPT two phrase-checks
- **Source (ASTRA §2.2, verbatim greps):** the usual word-list PLUS `it could be said\|one might argue\|on the other hand` and the balanced *"on the one hand / on the other hand"* framing (ASTRA §2.1) and *"crisp topic sentences at paragraph heads"* as a tell.
- **Ledger has:** §2.7/§17.2 blacklist is broad (delve, crucial, landscape, paradigm, holistic…; "it's important to note"; "moreover") and adds the em-dash HARD gate the sources lack — a net improvement. Missing atoms: the **"on the one/other hand" balanced-framing** tell and **"one might argue / it could be said"** hedge-pair, and the **"crisp topic-sentence-at-head"** structural tell.
- **Bake-in:** append to `lint_manuscript.py` / `book_config.voice.blacklist`: `on the one hand`, `on the other hand`, `one might argue`, `it could be said`; and add an advisory note re: topic-sentence-at-head as a soft structural tell (not auto-fail).

---

## TIER 4 — THINGS THE LEDGER GOT RIGHT / IMPROVED ON THE SOURCES (recorded so a future pass doesn't "fix" them back)

- **Em-dash HARD gate (ledger §17.1):** neither source has an *enforced* em-dash ban — ASTRA §2.1/§2.2 only *greps* for it as a "leak to investigate." The ledger's exit-1 gate + measured 0/124,933 (Autotelic) target is a genuine improvement. **Keep.**
- **Board-add page-count-band dependence (ledger §5.3/§13):** the sources treat 0.302→0.348 as a simple supersession (ASTRA §17 C1); the ledger correctly generalizes to "the constant is page-count-dependent; Previewer-calibrate per band" using the 186pp ASTRA-7 counter-example. **Deeper than the canon. Keep.**
- **Mixam non-constant board-add (ledger §5.4/§13#3):** ASTRA only says "Mixam tells you the spine." The ledger back-solves and records the non-constancy across page bands. **Keep.**
- **0.75" gutter overshoot rationale (ledger §4.1/§13#5):** the sources use **0.625"** gutter (ASTRA §6.1, §19.6; BOOK3). The ledger *raises the default to 0.75"* with a specific mechanical justification (justified-line trailing-space ≈2.7pt + italic side-bearing ≈2pt overshoot trips "insufficient gutter" at 0.625" exact). **This is a deliberate, documented divergence from the canon — verify it still matches current KDP behavior on the run date, but it is a defensible hardening, not an error.** Flagging so it is not "reverted to 0.625 per canon."
- **ISBN keep-out exact coords + adaptive-width blurb (ledger §6.6):** ASTRA §5.5 only gives the 2.25×1.5 keep-out size; the ledger adds pixel coords + the 220px-left shift + 60%-width URL wrap. **Deeper. Keep.**
- **Fonts vendored repo-relative (ledger §11.2):** all three sources hard-reference `C:\Claude-Titanic\fonts\`; the ledger's repo-relative mandate fixes the exact portability landmine the sources embody. **Keep — this is the point of the kit.**
- **Cormorant Garamond vs Georgia:** NOTE a face difference to keep straight — the **sources use Cormorant Garamond for COVER display + Georgia for INTERIOR body** (ASTRA §16.8, §5.3). The ledger's §3.2 interior spec also says **Georgia** body ✓, and §6.7 cover face = Cormorant ✓. Consistent. (The kit's `kit_env`/fonts ship Cormorant for covers; interiors rely on system Georgia — matches the canon. No delta; logged to prevent a false "mismatch" flag.)

---

## PRIORITIZED BAKE-IN QUEUE (highest leverage first)
1. **D5** — change category count 3→**2** at submit (§9.1 + §14). *Wrong number, user-facing, cheap fix.*
2. **D1** — footnote the 186pp HC example: white-only, 0.767 = white+0.348; the canon's 0.813 is cream and non-operative (§5.5). *Prevents a spine-rejection regression.*
3. **D4** — spine-side extra 0.10–0.15" quiet-zone pad (§5.7 + §14 + `composite_cover.py`). *Shipped-aesthetic the miner missed.*
4. **D11 + D12 + D10** — writing-methodology layer: single-axis multi-pass + pass order (§2.8/new §2.x), Mode A/B (§2.7), M0 soul doc for fiction (§2.2, `is_fiction`-gated). *Load-bearing to the "single authorial act" claim.*
5. **D3 / D8** — Mixam shipped anchors (0.67"@204pp, 70lb uncoated) + premium order knobs → `mixam_order_opts` (§5.4/§9.2).
6. **D13 / D14 / D15** — cold parallel-instance audit (§2.9); surface mechanical-metaphor + ellipsis fingerprint atoms (§17.3); add 4 hedge/balance phrases to the lint blacklist.
7. **D6 / D7 / D9** — proof-copy advisory (§10); add-format-not-new-title (§9); mark IngramSpark out-of-scope (§9/§11).

## Meta-observation (validates the ledger's own §16-META)
Every Tier-2/Tier-3 miss shares one property: **no KDP rejection string**. Spine-side pad, proof copies, "2 categories", M0 soul docs, single-axis passes, Mode A/B, cold audits — none throw an Amazon error; the author just *did* them (or *didn't ship without* them). The original grep-mine was keyed to loud rejection phrases ("insufficient gutter", "text outside margins", "expected cover size"), so this entire quiet layer was structurally invisible — exactly the failure §16 and §17 were written to name. A full-read pass (this one) is the only thing that surfaces it. **Recommendation:** any future lessons-scan is a READ, never a grep.

---
*Audit written 2026-07-12. All arithmetic in D1/D2 re-derived this pass (`python`, shown in the delta). Sources read in full, not sampled. BOOK3≡AI_BOOK confirmed by MD5.*
