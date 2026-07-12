# Author Voice Profile — Bo Chen — Feedback Rules Ledger

> **Provenance.** Extracted by reading (not grep-mining) eight accumulated feedback-memory files
> from Bo Chen's prior book projects (`C:\BOOK`, `C:\Claude-Titanic`, `C:\Claude-Titanic\the_second_notebook`).
> These are Bo's crystallized corrections across sessions — the "why the em-dash got through" failure
> was caused by a lessons-scan that grep-mined KDP rejection strings and never READ this corpus.
> This ledger is the READ output. Every rule below is a durable, cross-session standing order until Bo
> explicitly modifies it.
>
> **Source files (all read in full):**
> - `C--BOOK/memory/feedback_no_em_dashes.md`
> - `C--BOOK/memory/feedback_session_discipline.md`
> - `C--BOOK/memory/feedback_refrain_chapter_pattern.md`
> - `C--BOOK/memory/feedback_drafter_guidance_pointer.md`
> - `C--BOOK/memory/feedback_autonomy_grant.md`
> - `C--Claude-Titanic/memory/feedback_no_images.md`
> - `C--Claude-Titanic-the-second-notebook/memory/feedback_prose_discipline.md`
> - `C--Claude-Titanic-the-second-notebook/memory/feedback_claude_md_mismatch.md`
>
> **How to read the columns:** each rule carries NAME · the RULE (verbatim where wording is load-bearing) ·
> WHY (Bo's stated reason + date if given) · HOW A KIT ENFORCES IT (the mechanical/gate/config hook that
> makes it gap-proof, per the BOOKSMITH two-verifier model) · HARD vs SOFT.
>
> **HARD** = a gate must fail loudly if violated; never ship past it. **SOFT** = craft default; honor unless
> the contract or Bo overrides, no mechanical hard-stop but flag in self-assessment.

---

## GROUP 1 — PROSE HARD RULES (mechanical gates; a build must fail if violated)

### 1.1 · NO EM-DASHES IN PROSE
- **RULE (verbatim):** "Do not use em-dashes (—) in prose written for or with Bo. Use commas, colons, periods, or parentheses instead. This applies to book prose, scaffolding documents, memos, drafts, any prose output."
- **Scope is total.** Not just book prose — scaffolding docs, memos, drafts, handoffs, any prose output.
- **WHY:** Bo explicitly flagged em-dashes on **2026-04-22** as "an AI signature that is blatantly obvious." He does not write with them; keeping them is a direct voice tell that undermines the human-authorship illusion the whole project requires. Observable in his canon: `b0_soul_document.md` and his long-form corpus contain effectively zero em-dashes despite long sentences.
- **Timing rule:** strip em-dashes **at draft time, not revision time.** (Session-discipline file reinforces: "Every drafted chapter audits its own prose for em-dashes during composition.")
- **The two legitimate exceptions (do not false-positive on these):**
  1. **Markdown-table `—` used as a "(n/a)" placeholder** is not stylistic punctuation and may be acceptable; when in doubt replace with "(none)" to be safe.
  2. **Hyphens in compound adjectives** ("substrate-level," "cross-generational") are hyphens, not em-dashes, and are fine.
- **Also watch the en-dash (–).** Bo's rule names the em-dash (—); the en-dash is the same class of AI-tell punctuation and the BOOKSMITH sweep already greps `[—–]`. Treat both as forbidden in prose.
- **HOW A KIT ENFORCES IT:**
  - **Lint gate (mechanical, GATE-3 voice gate):** `lint_manuscript.py` blacklist + a `Grep "[—–]"` em-dash/en-dash sweep over every `manuscript/current/` and `manuscript/drafts/` unit. Exit non-zero on any hit outside the two exceptions.
  - **Config blacklist:** add `—` and `–` to `book_config.voice.blacklist` (as characters, not words) so the linter treats them as first-class violations.
  - **Known leak sites to sweep explicitly** (per BOOKSMITH CLAUDE.md §3): section **headers**, `[BO-WRITES]` markers, and table cells — these are where em-dashes most often survive a prose-body scan.
  - **Adapting canon:** the Pattern-Trajectory-Cursor canon and several source docs contain em-dashes; **strip them when adapting source text into book prose** — do not inherit them.
- **HARD.** This is the flagship hard rule; it is the exact failure this ledger exists to prevent.

### 1.2 · NO INTERIOR IMAGES (TEXT ONLY BETWEEN THE COVERS)
- **RULE:** No interior images. Text only. The book is prose only between the covers.
- **WHY:** Converged independently across two Claude Opus instances and one Gemini Deep Think instance on **2026-04-16**. Stated reason (Titanic novel): the core mechanism is *dissolution* — the boundary between seen and imagined becoming permeable; images fix the visual and collapse the reader's internal construction. "The prose is the rendering engine. The reader builds the ship." Even at perfect photorealism the objection is **ontological, not uncanny-valley**: an image turns a figure from renderer into rendered.
- **Scope caveat:** this reason is specific to that novel's thesis, so treat "no interior images" as **HARD for that book / project-declared elsewhere.** For a new book, honor it by default and only add interior images if the book's own `book_config` explicitly opts in. The *mechanical discipline* it teaches (strip all placeholder image blocks from the production docx) is universal.
- **What stays visual (the allowed exceptions):** the **cover** (AI-generated art), and **endpapers/deck-plans** if the book specifies them. Nothing else.
- **Rejected alternative (do not resurrect):** leaving image *prompts* in the text as "metadata bleeding through" — rejected because the prose already achieves diegetic metadata; production-scaffolding prompts are extradiegetic and break the ontological level.
- **HOW A KIT ENFORCES IT:**
  - **Mechanical gate:** strip all `[IMAGE — ...]` placeholder blocks from the production docx before PDF; a `Grep "\[IMAGE"` over the assembled master must return zero.
  - **Archive, don't embed:** move any image prompts to a separate file (they are useful as shot lists), never into the manuscript body.
  - **Cover pipeline unaffected:** the cover art / endpapers path (`cover_gen.py` → `composite_cover.py`) is the sanctioned visual surface.
- **HARD** (as a strip-the-placeholders build gate) · **SOFT/opt-in** (as a per-book "may this book ever have interior figures" policy).

### 1.3 · NO STRUCTURAL FORMATTING THAT BREAKS NARRATIVE FLOW (no bullets/headers inside prose)
- **RULE:** Never use bullet points, headers within prose, or structural formatting that breaks narrative flow inside the running prose. No "Key Takeaways" / summary boxes.
- **WHY:** From Bo's fiction-voice discipline: "Trust the reader to assemble structure from rendered detail." Structural furniture inside prose is an AI-tell and breaks the single-authorial-act illusion. (Reinforced by BOOKSMITH §7 "Never do" list: no bullet lists inside prose, no summary boxes.)
- **HOW A KIT ENFORCES IT:** drafting gate / self-assessment checklist item — flag any `^\s*[-*•]` bullet or mid-unit `^#{1,6}` header appearing *inside a prose unit's body* (front-matter and legitimate part/chapter headings excepted). Reviewer pass on the assembled markdown.
- **HARD** (for prose bodies).

### 1.4 · NO METANARRATIVE APOLOGIES / CONTENT WARNINGS / AUTHOR'S NOTES
- **RULE:** Never include content warnings, author's notes, or metanarrative apologies. No meta-commentary openers ("In this chapter we will explore…").
- **WHY:** These are irony shields and AI-tells; Bo's prose "runs hot or runs cold, never lukewarm." Metanarrative apology protects the writer from the emotion of the line — forbidden.
- **HOW A KIT ENFORCES IT:** drafting gate + reviewer pass; blacklist phrases ("In this chapter," "it could be argued," "to be fair," "on the other hand") in `book_config.voice.blacklist`.
- **HARD.**

### 1.5 · DO NOT GENERATE UNREQUESTED DOCUMENTATION FILES
- **RULE:** Do not generate documentation files (.md notes, READMEs, planning docs) unless explicitly asked.
- **WHY:** Stated twice across Bo's corpus (fiction-voice "Never" list; and the general posture). Unrequested scaffolding clutter is noise; Bo wants deliverables, not meta.
- **HOW A KIT ENFORCES IT:** process rule / agent constraint (already mirrored in BOOKSMITH's own "NEVER proactively create documentation files" guidance). No gate needed; a standing prohibition.
- **HARD (process).**

---

## GROUP 2 — CRAFT DISCIPLINE (the single-authorial-act machinery; mostly SOFT defaults, flagged in self-assessment)

### 2.1 · THE ONE LOAD-BEARING SPEC — SINGLE AUTHORIAL ACT
- **RULE (verbatim):** "The book must read as one person wrote it with continuous attention across a single creative act."
- **Companion bar (fiction):** "Indistinguishable from a published literary novel by a writer who spent years on the material."
- **WHY:** the prose is autobiographical at the bone; the voice is the load-bearing element. Hedged or sanitized prose destroys the work.
- **HOW A KIT ENFORCES IT:** this is the umbrella that every §2 rule and BOOKSMITH §7 technique serves; the seam check (GATE-4) is its mechanical proxy ("reads as one continuous authorial act").
- **HARD as a principle** (the whole project's terminal test) · enforced through SOFT sub-rules below.

### 2.2 · SEAM DISCIPLINE (residue at every chapter open)
- **RULE:** Each chapter's opening **200–500 words** explicitly carries **residue** from the prior chapter's closing — a phrase echoed *with variation*, an image returning in new context, an open question addressed obliquely. Never mechanically ("As we saw in…"); always implicitly.
- **Worked examples from Bo's book:** Ch 11 → Ch 14 ("the math was the math at STA. The math is the math here"); Ch 5 → Ch 6 (Ch 5 promised the W,C,H,O specification; Ch 6 opens by delivering the four definitions in cold succession).
- **WHY:** "It is what makes the book read as continuous authorial attention."
- **HOW A KIT ENFORCES IT:** `check seams` (GATE-4) reads the last ~500 words of unit N and the first ~500 of N+1 as one passage and flags tonal/residue discontinuity. Per-unit writing plan must name the residue it carries.
- **SOFT-but-gated** (no hard-stop on a single chapter, but GATE-4 blocks the seam stage).

### 2.3 · CALLBACKS WITH VARIATION (variation is the human signature)
- **RULE:** Plant callbacks across long arcs (a Part-I detail pays off in Part-V), but **vary the wording** when landing them. Exact quotation is the AI signature; variation is the human signature.
- **WHY:** mechanical exact-quote callbacks are the top AI-tell that a book was generated in isolated units and stitched.
- **HOW A KIT ENFORCES IT:** contract gate (every Must-Callback "landed with variation"); `audit threads` catches orphan seeds/payoffs; loading the **prior unit's FULL prose** (not just the handoff) is the mechanical precondition — skipping it is the #1 cause of exact-quote callbacks.
- **SOFT-but-gated.**

### 2.4 · THE REFRAIN IS SACRED (exact wording, exact placement count)
- **RULE:** The book's refrain has **exact wording** and a **fixed placement count**; it is never paraphrased elsewhere, never varied, never over-placed. For Bo's book: **"The pattern holds."** — exact wording, capitalized sentence-initial, period — at **six placements** (Prologue, Ch 7, Ch 16, Ch 22, Ch 24, Epilogue). "The phrase is sacred… it lands or the chapter has failed its contract."
- **Closing pattern for a refrain chapter (six-step compression, established Ch 7):** (1) compress the chapter to one sentence; (2) compress to one operational directive; (3) compress to one observation about the system; (4) render specific instances at concrete scale; (5) land a canon-derived bridge line; (6) the refrain lands as the natural compression of everything prior. The *function* (each compression steps closer to the refrain's abstract claim) is mandated; the exact six-step shape is not — chapters may vary per contract.
- **Do-not-dilute rule:** in a refrain chapter, do NOT put a *different* signature line in the refrain's closing slot (for Bo's book, the Book II signature "The pattern is the same. The substrate differs." must not close a refrain chapter — the refrain takes that position; the signature may appear earlier or be loosely paraphrased). Ch 7 caught this: "The substrate differs. The geometry is the same." echoed the signature too closely and was revised to "Different substrates. The same geometry beneath." to avoid diluting refrain #2.
- **WHY:** refrain placements are architecturally load-bearing (the spiral's signature at sentence-scale across the book); they compound weight without becoming formulaic.
- **HOW A KIT ENFORCES IT:** `check refrain` (GATE-4) + `registry/refrain.md` — the refrain must appear at **exactly** its designated placements with **exact** wording; count and wording are both verified. BOOKSMITH already forbids "break the refrain's exact wording, exceed its placement count, or vary it."
- **HARD** (wording + count are a hard gate) · the closing-compression shape is **SOFT** (function mandated, form flexible).

### 2.5 · RENDER BEHAVIOR STRUCTURALLY, NOT PSYCHOLOGICAL EXPOSITION
- **RULE:** Render observed physical behavior, not psychological exposition. "She was afraid" → show what fear looks like in her specific body. Also render load-bearing witness/case figures **structurally** — e.g. no personal name for the witness figure; preserve the trajectory (ORC, pregnancy loss during supervisor-assigned travel, FMLA suppression, supervisor's "the mission never stops") without naming.
- **WHY:** trust the reader to assemble structure from rendered detail; and (for the witness material) per Buffone counsel discipline, render the pattern structurally rather than by identity.
- **HOW A KIT ENFORCES IT:** drafting gate / reviewer pass; anonymization is on the "ask/route through counsel" list for real-name material (see 3.3).
- **SOFT** (craft) · the anonymization side is **HARD** (never expose a real name that should be structural).

### 2.6 · BO'S VOICE FINGERPRINT — THE "DO" LIST (fiction register)
- **RULE (do these):** recursive restatement (circle the same idea from three angles to *deepen*, not pad); mixed register (archaic constructions next to colloquial speech in the same paragraph); mechanical/computational metaphors for emotional states (nervous system, signature, bandwidth, throughput, regulatory mechanisms); compound-adjective stacks; maximalist sentences with multiple "and" clauses building toward inevitability; trust the reader to assemble structure.
- **Voice register varies per Book/section but stays inside one fingerprint** ("Bo-in-analytical-mode" is the default): e.g. philosophical-precise → technical-philosophical → technical (Book II); analytical-structural with math-forward equations (Book IV); empirical-geopolitical, event-rendering-forward (Book V). Uniform register across all units is *the* AI tell; the book "breathes because units differ."
- **WHY:** the voice is the load-bearing element; this is the fingerprint the exemplars encode.
- **HOW A KIT ENFORCES IT:** `book_config.voice` exemplars (`exemplars/anchor.md` + supporting) + the voice gate's exemplar-consistency check; per-unit contract "register profile."
- **SOFT** (honored per contract; flagged in self-assessment when drift is intentional vs accidental).

### 2.7 · BO'S VOICE FINGERPRINT — THE "NEVER" LIST (fiction register)
- **RULE (never do these):** no hedging ("to be fair," "it could be argued," "on the other hand"); no irony shield protecting the writer from the emotion of the line; no sanitizing/balancing/moderating ("run hot or run cold; never lukewarm"); no AI-sounding dialogue (characters speak like themselves, from transcripts, not like an assistant); no adding new characters, frame narratives, epilogues, or "resolution" beats not in the source structure; no hedged ranges where a specific belongs; no hypothetical "Company X."
- **WHY:** hedged or sanitized prose destroys autobiographical-at-the-bone work.
- **HOW A KIT ENFORCES IT:** `book_config.voice.blacklist` (hedge phrases) + voice gate + reviewer pass; structural-addition prohibition is a contract-compliance check (units must match the source structure).
- **HARD** (blacklist phrases) · **SOFT** (tonal "run hot/cold," flagged in self-assessment).

### 2.8 · PRESERVE DELIBERATE CROSS-WORK RECURRING LINES
- **RULE:** When editing, preserve recurring lines across works (e.g. "the night was young," "the universe noticing itself noticing itself is love"). They are deliberate cross-references, not accidents — do not "fix" or vary them.
- **WHY:** they are intentional motif anchors spanning multiple books.
- **HOW A KIT ENFORCES IT:** `book_config.voice.sacred_terms` / a "preserve-verbatim" list the linter protects (warns if a sacred line is altered).
- **HARD** (sacred lines are verbatim-protected).

### 2.9 · COMPRESSION AT EVERY SCALE
- **RULE:** Compression is a principle at every scale (sentence, chapter close, book). Chapter closes especially compress content toward the load-bearing claim (see the refrain closing pattern, 2.4).
- **Book II closing signature:** "The pattern is the same. The substrate differs." recurs at Ch 4/5/6 closes (part of the spiral architecture) — but NOT at a refrain chapter's close (2.4).
- **WHY:** compression is the spiral architecture's signature; it compounds meaning.
- **HOW A KIT ENFORCES IT:** `registry/compression_pairs.md` + `check compression-pairs` (GATE-4) verifies compression pairs (e.g. Prologue↔Epilogue) hold their spiral topology.
- **SOFT-but-gated.**

### 2.10 · ENDING ROTATION + FLASH-FORWARDS + AUTHORIAL SELF-CORRECTION
- **RULE:** Rotate unit endings (aphoristic / open question / specific image / unresolved tension / declarative / callback) — never close two units the same way. Use flash-forwards liberally (gesture toward later development from within a unit). 3–5 times across the book, at genuinely load-bearing moments, use authorial self-correction ("I said X earlier; the sharper version is…").
- **WHY:** identical unit closings and zero authorial awareness are AI-tells; these make the author feel like someone thinking across the whole book.
- **HOW A KIT ENFORCES IT:** self-assessment checklist (ending-type per unit tracked so no two adjacent units repeat); reviewer pass. (These come from BOOKSMITH §7 and are consistent with Bo's "plant callbacks across long arcs.")
- **SOFT.**

### 2.11 · THE SELF-ASSESSMENT / CHAPTER-COMPLETION REPORT TEMPLATE
- **RULE:** Every drafted chapter reports to Bo with a fixed template:
  1. **Files produced** (with markdown links).
  2. **Word count vs target.**
  3. **Contract compliance summary** (all Must-Accomplish landed).
  4. **Constraint compliance** (em-dashes = 0, forbidden labels, etc.).
  5. **Voice flag** — honest about "Bo-in-analytical-mode vs full Bo" (i.e. Claude-doing-Bo vs Bo's authentic load).
  6. **Deferred items** (e.g. Phase-E deferred callback concretization).
  7. **Phase/status update.**
  8. **Per-recommendation next move.**
  - Plus (from DRAFTER_GUIDANCE §1): **"Strongest moves identified."**
- **Post-chapter deliverable set (5 artifacts every chapter):** the draft at `manuscript/drafts/{stem}_v1.md`; the 3-layer handoff at `handoffs/ch{N}_handoff.md`; the state snapshot at `state/after_{stem}.md`; the `registry/threads.md` update for any threads touched; the BUILD_LOG.md entry (+ SESSION_HANDOFF.md if continuing). This maps directly onto BOOKSMITH's per-unit protocol §8 steps 6–8.
- **Honest-posture rule (load-bearing):** be honest about "Bo-voice vs Claude-doing-Bo." Do not pretend a Class-C framework chapter carries Bo's full authentic voice; flag it. Likewise do not pretend a callback is concrete when it is still conceptual — flag the deferral in the handoff (Layer 3).
- **WHY:** velocity with rigor; Bo wants the honest voice-flag so he knows which chapters still need his authentic load.
- **HOW A KIT ENFORCES IT:** the status-report format (BOOKSMITH §10) + the per-unit protocol; the honest voice-flag is a required field, not optional.
- **SOFT (template) · HARD (honesty — never overclaim voice authenticity or callback concreteness).**

---

## GROUP 3 — AUTONOMY / PROCESS (what to decide vs. what to ask)

### 3.1 · BROAD AUTONOMY ON TASTE / SCAFFOLDING — INFER, DON'T ASK
- **RULE:** Bo grants broad autonomy on **taste, naming, anonymization tactics, phrasing, and scaffolding** during vibe-writing. "Make the call and act; only ask for things that truly require Bo's judgment." Prefer **velocity with rigor over deliberation with permission-asking.**
- **WHY:** Stated **2026-04-22**: "Opus 4.7 guesses him better than he guesses himself. The structure is already in place. The velocity of vibe-writing depends on not requiring constant approval loops." The authoritative baseline for inferring taste is the **soul document** (`canon_refs/b0_soul_document.md`) + `canon_refs/` + `SEED.md`.
- **DECIDE-AND-REPORT (act autonomously):** construct/other names, anonymization tactics, greenlist/blacklist curation, motif selection, register calls, chapter-opening choices, scaffolding decisions.
- **HOW A KIT ENFORCES IT:** this IS the BOOKSMITH §4 autonomy grant; the soul document is a mandatory Context-Pack load so inference has its baseline.
- **HARD (as a standing grant — do not re-litigate it with approval loops).**

### 3.2 · THE THINGS TO ALWAYS ASK / NEVER TOUCH
- **RULE — pause and ask (or never do) for:**
  - **Class-A chapter content** (Prologue, Ch 24, Epilogue stay Bo's to write — outline only, no prose).
  - **Real-name anonymization** that should route through **Buffone counsel**.
  - **Substantive structural changes to the book's spine** — renaming a construct is fine; **restructuring chapter order is not.**
  - **The refrain phrase or the six-placement architecture** (never change unilaterally).
  - **Read-only source:** do **not** edit `canon_refs/` or `BC_Canon/` — those are read-only source.
- **WHY:** these are the judgment calls autonomy explicitly excludes; the spine, the refrain, and Bo's authentic-voice chapters are his.
- **HOW A KIT ENFORCES IT:** maps onto BOOKSMITH §4 "four pauses" (Class-A prose, substantive seed changes, WRONG.md commit, export v1.0) + the "Never" list (no Class-A prose, no refrain edits, no source edits).
- **HARD.**

### 3.3 · SESSION-BOOT READING ORDER + CROSS-SESSION CONTINUITY
- **RULE:** At session boot, read the continuity set **before drafting any chapter**, in order. For Bo's book that order is: **CLAUDE.md → SEED.md → BUILD_LOG.md → SESSION_HANDOFF.md → DRAFTER_GUIDANCE.md**, then draft. `DRAFTER_GUIDANCE.md` is craft-level (five-condition quality bar, eight drafting traps as a pre-commit checklist, per-chapter register map, refrain architecture, seam discipline, Class B/A discipline, honest voice posture, pause-vs-proceed boundaries, compression-at-every-scale, and the single load-bearing spec). BUILD_LOG = durable phase record; SESSION_HANDOFF = live meta-context (where we are, what was just done, what's next, active voice calibrations/decisions).
- **WHY:** these two files "together provide cross-session continuity"; the craft file hands forward accumulated discipline so each session doesn't relearn it.
- **HOW A KIT ENFORCES IT:** BOOKSMITH §1 boot sequence + COMPACTION SURVIVAL (`_CONTINUITY.md` rewritten after every chapter, `rehydrate.py`). The **eight drafting traps are a pre-commit checklist** to run before committing a draft.
- **HARD (boot order) · SOFT (the craft guidance content).**

### 3.4 · CLAUDE.md SCOPE IS PER-PROJECT; AUTHOR-LEVEL VOICE RULES TRANSFER
- **RULE:** A parent-project `CLAUDE.md` loaded via the project hierarchy governs **that** project's task instructions only (file outputs, part structure, character cast, research targets) and does **not** apply to a different working directory/sub-project. BUT the **author-level voice/discipline rules DO transfer** (bo-voice, no irony shield, render behavior structurally) because they are author-level, not project-level.
- **WHY:** treating a parent CLAUDE.md as authoritative for a sibling project causes wrong assumptions (wrong output dirs, wrong part split, wrong cast). Separating project-scope from author-scope prevents that.
- **The distinction to keep:** **project-specific** (parts, outputs, cast, historical targets) = ignore outside its project; **author-level** (voice, discipline, this whole ledger) = always applies.
- **HOW A KIT ENFORCES IT:** BOOKSMITH's precedence rule (`KIT_ARCHITECTURE.md` invariant > per-session CLAUDE.md > per-book `seed.md`); this ledger is stored as **author-level** (`docs/author_voice/`) precisely so it travels across every book, unlike a per-book seed.
- **HARD (as a scoping discipline).**

### 3.5 · DEFERRED-WORK HONESTY (don't fake concreteness)
- **RULE:** When earlier-phase chapters reference not-yet-drafted chapters, the callbacks are **conceptual, not concrete.** Do not pretend they are concrete — flag the deferral in the handoff (Layer 3) so a later integration pass concretizes them with real phrasings from the drafted chapters.
- **WHY:** honesty about deferred state prevents shipping a book whose cross-references silently don't resolve.
- **HOW A KIT ENFORCES IT:** handoff Layer-3 "deferred concretization" field + a final integration pass; `audit threads`/`audit dependencies` catch unresolved references before export.
- **HARD (never claim concreteness that doesn't exist).**

---

## APPENDIX — LABEL / TERM DISCIPLINE (project-specific, illustrative of the pattern)

These are Bo-book-specific but show the *class* of term-discipline a `book_config.voice` should encode
(`sacred_terms`, `greenlist`, `blacklist`, scale-specific construct names):

- **"Mission as Camouflage"** = the institutional-scale name (Ch 11 territory).
- **"Mission capture"** = the dyadic/human-scale construct that lands at Ch 9, *derived from* D6.
  Phase-B chapters use "Mission as Camouflage"; Ch 9 introduces "mission capture" as the human-scale
  construct. Do not conflate the two scales.
- **Book II signature** "The pattern is the same. The substrate differs." recurs at Ch 4/5/6 closes but
  never at a refrain chapter's close.
- **Refrain** "The pattern holds." — six placements, exact wording (see 2.4).

The transferable rule: **scale-specific constructs and signature lines are tracked, and each has an exact
scope; using a construct at the wrong scale, or a signature line in the refrain's slot, is a defect.**

---

## ENFORCEMENT SUMMARY (what BOOKSMITH must wire so none of this rides on memory)

| Rule | Mechanism | Where |
|---|---|---|
| 1.1 No em-dashes/en-dashes | `Grep "[—–]"` sweep + `lint_manuscript.py` blacklist chars; sweep headers + `[BO-WRITES]` + tables | GATE-3 voice gate |
| 1.2 No interior images | `Grep "\[IMAGE"` = 0; strip placeholder blocks | production/assemble |
| 1.3 No bullets/headers in prose | reviewer/lint pass on prose bodies | GATE-3 |
| 1.4 No metanarrative/apologies | blacklist hedge/meta phrases | GATE-3 voice gate |
| 1.5 No unrequested docs | standing process prohibition | agent policy |
| 2.2 Seam residue | last-500/first-500 read | GATE-4 `check seams` |
| 2.3 Callbacks vary | contract "landed with variation" + full-prior-prose load | GATE-3 contract gate |
| 2.4 Refrain exact+count | `registry/refrain.md` exact wording + placement count | GATE-4 `check refrain` |
| 2.8 Sacred lines verbatim | `voice.sacred_terms` protected | GATE-3 |
| 2.11 Self-assessment + honest voice-flag | required report fields | §8/§10 report |
| 3.1/3.2 Autonomy vs ask | §4 four pauses + never-list | boot/session policy |
| 3.3 Boot order + continuity | §1 boot + `_CONTINUITY.md`/`rehydrate.py` | session boot |
| 3.5 Deferred honesty | handoff Layer-3 + integration pass | handoff/audit |

**The meta-lesson that produced this ledger:** the em-dash shipped because a scan grep-mined KDP-rejection
strings and never READ this feedback corpus. The countermeasure is not a better grep — it is that Bo's
accumulated feedback memory is **read in full** and crystallized into gates. A gate that a machine can fail
loudly is the only durable form of a writing rule here.

*Ledger compiled 2026-07-12. Author-level; travels with the kit across every book. Append-only; supersede
an entry with a dated successor rather than editing it. Subordinate to any explicit later instruction from Bo.*
