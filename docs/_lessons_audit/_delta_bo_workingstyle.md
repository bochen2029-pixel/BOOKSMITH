# DELTA — Bo Chen durable WORKING-STYLE / process hard-rules (cross-project)

> **What this is.** The durable *how-Bo-works* rules — autonomy, velocity, honesty/anti-sycophancy,
> Windows/PowerShell, verify-the-artifact, decision-logging, anti-hallucination — mined by **reading in
> full** (not grepping) every working-style / user-profile / feedback-methodology memory across **eight**
> of Bo's projects that the existing kit ledgers had **never read**. These govern HOW the kit should behave
> for Bo across any book, beyond prose voice.
>
> **Why it exists.** BOOKSMITH dropped lessons because a prior build did not read Bo's crystallized
> preference memory. The standard is *no lesson ever relearned*. The kit's existing
> `docs/author_voice/_voiceprofile_crossproject.md` already mined a **disjoint** project set
> (permanentunderclass-cc, wholemachine-org, gracegradient, APPLY, APPLY2, ClaudeCode, ASTRA-7, Websites)
> and covers the *voice* + a first cut of working-style. **This file is the DELTA**: (1) rules those eight
> NEW projects independently **corroborate** (raising the load-bearing weight — a rule in ≥2 projects is
> load-bearing, and several here now sit at ×5–×8), and (2) rules that are genuinely **NEW / beyond** the
> existing ledger. Corroboration count spans BOTH ledgers' sources.
>
> **Anchored:** 2026-07-12 (Sunday), Central Standard Time (system clock, this session).
>
> **Source map (short keys used below — the eight NEW projects read for this file):**
> - `BR-mode` = C--backrooms / `feedback-working-mode.md`
> - `BR-auto` = C--backrooms / `project-autonomous-build.md`
> - `TOP-bake` = C--TOPEST / `bo-harness-bakeoffs.md`
> - `MAY-meth` = C--BC-Canon-MAY2026-stamp / `feedback_methodology.md`
> - `MAY-dist` = C--BC-Canon-MAY2026-stamp / `feedback_distribution_traps.md`
> - `MAY-smoke` = C--BC-Canon-MAY2026-stamp / `feedback_smoke_discipline.md`
> - `MAY-user` = C--BC-Canon-MAY2026-stamp / `user_bo_profile.md`
> - `AEG-canon` = C--BC-Canon-temp-sandbox-AEGIS / `bo_session_canon_2026-04-26.md`
> - `AEG-status` = C--BC-Canon-temp-sandbox-AEGIS / `bo_personal_status.md`
> - `APO-work` = C--Apollo / `user-bo-chen-working-style.md`
> - `CAR-prof` = C--Users-user-career-ops / `bo-chen-profile.md`
> - `CAR-thesis` = C--Users-user-career-ops / `career-strategy-working-thesis.md`
> - `OUT-user` = C--OUTREACH / `user-bo-chen.md`
> - `LLC-user` = C--LLC / `user_bo_chen.md`
>
> **Existing-ledger keys referenced for corroboration** (already in the kit; not re-read for this file):
> `GG-work/GG-user` = gracegradient, `ASTRA` = ASTRA-7, `PUC` = permanentunderclass-cc,
> `CC-v7` = ClaudeCode, `WS-*` = Websites, `APPLY/APPLY2`.

---

## HOW TO USE THIS FILE (bake-in precedence)

Every rule below is already *mostly* held somewhere in the kit — the point is to make the hold **explicit,
weighted, and gap-free**. Three bake-in targets:
1. **CLAUDE.md §4 (autonomy + the four pauses)** — the behavioral contract. Most working-style rules land here.
2. **A gate** (`verify_build.py` mechanical / `vision_verify.py` perceptual / GATE-3 lint) — where a rule can
   be made mechanical, it must be, not left to discipline. This is the kit's own law.
3. **The voice profile / `book_config.voice`** — only the register-of-address rules (terse status, one-sentence
   corrections) that shape how the kit *talks*, not what it builds.

Priority tiers: **HIGH** = corroborated ≥3 projects AND changes kit behavior if missed. **MED** = corroborated
≥2 or a single high-stakes bought-with-a-real-error rule. **LOW** = confirmed but already fully held / low kit impact.

---

## PART A — NEW / SHARPENED RULES (beyond the existing voice ledger)

### A1. Primary-source verification DOMINATES multi-model convergence. Agreement across N LLM outputs is shared-prior co-hallucination, not corroboration. **[HIGH — REPEATED ×5]**
The single strongest *methodological* rule in the fresh corpus, and only lightly touched by the existing
ledger (as "adversarial audits"). Bo treats independent-looking model agreement as a **coherence signal, not
a truth signal**, and demands an out-of-band anchor.
- `AEG-canon` (verbatim, "the single most important rule"): **"convergence across N 'independent'
  LLM-generated sources is shared-prior co-hallucination, not adversarial confirmation. Primary-source
  verification dominates corpus convergence."**
- `CAR-prof` (verbatim): **"treats multi-model agreement as coherence, not corroboration"** — wants
  **"pushback not mirroring ('break this, don't derive this')."**
- `APO-work` (verbatim): **"multi-instance adversarial synthesis (cross-references outputs between Claude
  instances)"**; **"ground truth above all (verify before building on a claim; he catches unverified
  assumptions and remembers them)."**
- `LLC-user` (verbatim): synthesized **"4+ independent deep-research passes"** and **"was careful to audit
  every figure for hallucination markers."**
- Corroborates the existing ledger's `CC-v7` **Externality Principle** ("every critical loop needs one
  assertion the model did not author; same-model-class verification is circular").

**Load-bearing for a BOOK kit specifically:** the kit's #1 "Never" is *fabricate a canon citation / invent an
author experience*. This rule is the WHY, and it hardens the fix: a canon anchor is not "true" because two
digests agree on it — it is true because it traces to the actual intake source. The `AEG-canon` file is a
catalog of real corpus co-hallucinations Bo caught (a VA zoning code applied to TX and propagated through 5+
research returns; a fabricated bank acquirer; a $50K-immediate deduction misread) — the exact failure the
kit's `audit canon` exists to stop.

**BAKE-IN (gate + CLAUDE.md):**
- `audit canon` (GATE-4) must trace every citation to a **specific intake source location**, not to
  digest-agreement. A claim asserted by ≥2 digests but absent from any primary source = **flag, not pass**
  (it is co-hallucination). Add this line to the `audit canon` contract.
- The **two-verifier model** is this principle already: `vision_verify.py` / `verify_build.py` are "the
  assertion the model did not author." Keep them non-optional; they are not decorative.
- Provenance discipline (A2) is the enforcement mechanism.

### A2. Tag every factual claim with PROVENANCE; strip the unverifiable before shipping. **[MED — REPEATED ×2, bought with real errors]**
Bo does not just verify — he **labels the epistemic status of each claim on the artifact** and removes what
can't be stood behind.
- `AEG-canon` uses an explicit ladder: **Primary / Verified-Pass / Corpus-Consensus / Suspect / Struck**, with
  a standing "What still needs verification before money moves" section.
- `LLC-user` (verbatim): **"he explicitly stripped unverifiable claims from planning docs and tagged every
  figure with provenance (Primary, Verified-Pass, Corpus-Consensus, Suspect, Struck)."**
- `CAR-thesis` (verbatim, honesty as a ship-gate): deployment-status framing **"must be locked truthfully
  before sending — honesty is a core Bo value."**

**BAKE-IN (gate):** the kit's `canon_refs/` + per-contract canon anchors ARE the provenance layer — make the
status ladder explicit. A canon anchor tagged below "Verified" must not be woven into body prose as settled
fact (mirrors the §7.9 "personal material draws only from real canon" and the "no fabricated experience"
rule). This is the book-form of B1 (telemetry over testimony) applied to *content*, not self-state.

### A3. Bo runs HARNESS BAKE-OFFS — your output is compared side-by-side against other agents. **[MED — REPEATED ×3]**
A durable operating fact about the environment, not in the existing ledger. Bo routinely hands the identical
task to multiple agents/harnesses at once and compares.
- `TOP-bake` (verbatim): **"gives the identical task to several AI coding agents/harnesses at once and compares
  how each does"**; on 2026-06-20 the same task went to ZCode (GLM-5.2), opencode (GLM-5.2), and Claude Code
  (Opus 4.8). Keeps **"multiple agent apps open simultaneously (ZCode, OpenCode, Claude, APOLLO 8)."**
  Implication (verbatim): **"My output may be compared side-by-side against other agents' — correctness and a
  bit of distinctive polish both matter."**
- `APO-work`: **"multi-instance adversarial synthesis (cross-references outputs between Claude instances)."**
- `BR-mode`: he pointed the agent at a rival model's brainstorm (**"GLM-5.2's read-only brainstorm"**) and
  said **read ALL of it and polish with my own judgement, not just cherry-pick.**

**BAKE-IN (CLAUDE.md, ethos):** the kit is a competitive artifact. Two consequences: (1) **correctness is
table-stakes** — a gate failure is a visible loss against a rival harness, so never relax a gate to pass it;
(2) **distinctive polish matters** — the kit's "single authorial act" quality bar (§7) is not gold-plating,
it is the differentiator Bo is measuring. When another model's output is provided as input, integrate it with
judgement (steelman + improve), do not cherry-pick or dismiss.

### A4. LAND every deliverable on disk / in the repo — never only in chat. **[HIGH — REPEATED ×4]**
Explicit and repeated; the existing ledger implies it (build-log convention) but never states it as a first
principle. Chat output that isn't persisted does not count as done.
- `APO-work` (verbatim): **"Land every deliverable in the repo/filesystem, never only in chat."**
- `BR-mode` (verbatim): **"Log every change to an append-only ledger (`docs/CHANGE_AUDIT_LOG.md`) for audit +
  rollback; take backups (git tags + local zip) at risk points."**
- `OUT-user` (verbatim): terse imperatives like **"write memory to disk", "rescan all"** expect
  **"independently curated output"** landed, not a chat reply.
- Corroborates the existing ledger's `WS-user` build-log convention and `GG-user`.

**Why it is load-bearing here (and note this very audit):** the instruction that spawned this file said *"Write
the file FIRST + completely, THEN return a ≤170-word summary. Must survive if your reply is lost."* That is A4
verbatim. Applies to EVERYTHING: digests → `canon_refs/`, drafts → `manuscript/drafts/`, decisions →
`CHANGELOG.md`/`WRONG.md`, this audit → disk. A summary in the reply is a pointer, never the artifact.

**BAKE-IN (CLAUDE.md §11 + §4):** already the kit's append-only + `assemble_manuscript.py` discipline. Add one
sentence to §4: *a deliverable exists only when it is on disk; chat is a pointer to the artifact, never the
artifact.*

### A5. `--help` is NOT a smoke test — verify with a DEEP probe that exercises the real chain. **[HIGH — REPEATED ×2, bought with real defects; strong kit analogue]**
A genuinely NEW verify-the-artifact rule, paid for in production defects, that maps almost one-to-one onto the
kit's produce/export gates.
- `MAY-smoke` (verbatim): **"`Stamp.exe --help` is NOT a smoke test for PyInstaller bundles"** — a framework
  that lazy-imports "will return exit 0 on `--help` even if a transitively-imported module is missing." The fix:
  a **`probe` subcommand that eagerly imports every domain module** and exercises the real chain.
- `MAY-dist` (verbatim, "Cairn S8b-3 caught this the hard way"): `Cairn.exe --help` passed; **`Cairn.exe
  list-trips /tmp/empty` triggered the orchestrator chain and crashed.**
- Corroborates the existing ledger's `GG-work` **"verify binary freshness, not source ('triple-check' = confirm
  the compiled artifact has the fix)"** and `WS-user` build-log discipline.

**The kit analogue (make it explicit):** "the interior PDF opens" is the kit's `--help` — a shallow pass that
hides the real defect. The deep probe is `verify_build.py` running the FULL chain: `<w:mirrorMargins/>` +
`<w:evenAndOddHeaders/>` present, header-free sections render `[]`, recto parity (`check_part_pages.py`), page
count ÷2/÷4, re-derived PAGES matches the compositor input, Kindle word-count parity with print. This is the
exact bug lineage the kit already knows: the Kindle shipped 8,476 words short because someone smoke-tested "it
built" instead of probing word-count parity.

**BAKE-IN (gate + CLAUDE.md §10/§12):** never accept "it rendered / it opened" as a format pass. GATE-5 is the
probe; run it every time. State in §12: *the shallow check (file exists, opens) is not the gate; the gate is the
deep artifact-probe that exercises margins, recto, page-count, and parity.*

### A6. RE-TIGHTEN discipline at the DISTRIBUTION / packaging phase — that is where real defects hide. **[MED — REPEATED ×2, bought with real defects]**
A NEW phase-aware cadence rule. Ceremony can relax during heads-down work but must **re-tighten at
distribution**, because packaging is empirically where the paid-for defects clustered.
- `MAY-meth` (verbatim): **"Session 7 (distribution): RE-TIGHTEN. That's where Cairn ran into 3-4 real defects
  … Don't smoke past `--help`."** Cadence: S1 full ceremony → S2–6 relaxed/sub-commit → **S7 re-tighten** →
  S8 light.
- `MAY-dist`: four PyInstaller/CUDA distribution traps, each paid in a real defect (missing `cublasLt` DLL;
  system-CUDA overriding the bundle; hidden `unittest` import; typer lazy-import).

**The kit analogue:** the kit's distribution phase is **`produce format` + `export v1.0`** — assembling nine
upload-ready formats + covers. This is exactly the Cairn S7 moment. Every historical KDP/Blurb/Mixam rejection
(four hardcover rounds, wrong-service wrap, blank-page header) was a **distribution-phase** defect. The kit
already re-tightens here structurally (GATE-5 per format, the export confirm) — this rule is the *why*, and it
warns against complacency: do not let a clean draft lull the packaging step. Cross-service specifics live in
`docs/format_spec_sheet.md` (Mixam filename routing keywords, exact MediaBox, per-service spine).

**BAKE-IN (CLAUDE.md §12 + §5):** annotate the production build order: *packaging is where defects hide;
re-tighten here — run every mechanical gate per format even when the draft is clean; never reuse a cover or an
interior across services.*

### A7. The anti-pattern: tool-tinkering FEELS like progress; SHIPPING is the metric. **[MED — REPEATED ×2, directly relevant to MAINTAIN sessions]**
A NEW and self-implicating failure-mode Bo has named about himself — and the kit is a prime host for it.
- `CAR-thesis` (verbatim): Bo's bottleneck is **"a SHIPPING problem, not a knowledge/tooling problem ('the
  checklist is not the flight'; … 'building feels like progress, selling feels like cost')."** The tool
  itself was flagged as **"catnip for this exact pattern — the failure mode is forking/tuning it for weeks,
  calling it progress, and not sending the application."** Prescription: **"Resist 'let's improve the tool
  first' detours unless they directly unblock"** the ship. **"Bias toward irreversible-cost actions."**
- Corroborates the kit's own memory-of-record ethos (**ship-at-90%; the canon is append-only; v1.1 exists**)
  and `GG-user` ("the thinking is done… execute", "the door is still the door").

**Directly relevant to MAINTAIN-mode kit sessions:** a session that polishes the kit forever instead of
producing a book is Bo's exact named trap. Kit improvements are legitimate ONLY when they unblock a ship (a
gate that fails, a portability gap that blocks a giftable run) — not open-ended refactoring dressed as
progress. `export v1.0` and a produced format are the irreversible-cost actions; bias toward them.

**BAKE-IN (CLAUDE.md §0/§13, the closing ethos):** add a line to the "ship at 90%" close: *tool-tinkering is
not shipping; kit work is justified only when it unblocks a book. The book is the deliverable; the kit is the
machine, not the product.*

---

## PART B — CORROBORATION BUMPS (existing ledger rules, now weightier from the 8 new projects)

These are already in the kit / the existing voice ledger. The fresh corpus **independently re-confirms** them,
raising their load-bearing weight. No new bake-in needed beyond *holding the line* — logged so the count is
accurate and no future session treats them as soft.

### B1. FULL AUTONOMY; decide-and-log; NEVER block; punishes repeated question loops. **[HIGH — now REPEATED ×8, the strongest signal in the entire corpus]**
The existing ledger had this at ×4 (C1). The eight new projects add four more independent confirmations, and
sharpen the *emotional* cost of violating it (frustration, "punishment").
- `BR-mode` (verbatim): **"Rapid, agentic, autonomous. Do NOT pause or ask for confirmation on in-scope work
  — propose-in-the-reply then execute; 'stop asking me questions or pausing, finish it.'"** and **"Don't go in
  circles… He gets frustrated when work stalls or re-litigates settled things."**
- `APO-work` (verbatim): **"autonomy (never block on him, decide-and-log; he punishes repeated question loops
  — 'use your best judgement for all')."**
- `MAY-user` (verbatim): **"state results + decisions directly… don't narrate internal deliberation."**
- `OUT-user` (verbatim): **"Terse imperatives … expect independently curated output, not clarifying
  questions"**; **"flag-and-pause only on hard-to-reverse or never-autonomous actions."**
- `BR-auto`: **"no approval prompts mid-milestone, 'do absolutely everything you can.'"**

**Boundary (unchanged, re-confirmed):** surface *structural / irreversible* forks only (`MAY-meth`
propose-first gap pass at session start; `OUT-user` "hard-to-reverse or never-autonomous"; `ASTRA` "novel
ground"). This is EXACTLY the kit's **§4 four pauses** (Class-A prose, substantive seed.md change, WRONG.md
commit, export v1.0) — the corpus confirms those four are the *complete* stop set. **HOLD:** do not add
interactive prompts; do not re-ask a value that lives in `book_config.json`.

### B2. Anti-sycophancy: ground truth over flattery; SILENT AGREEMENT is the failure mode; pushback is first-class. **[HIGH — now REPEATED ×6]**
Existing ledger had B2 at ×3. Sharpened here: the failure is not just flattery, it is **withholding real
disagreement**, and Bo wants a **non-LLM oracle** to say "done," never the model's self-assertion.
- `MAY-meth` (verbatim): **"Implementer pushback is welcome… The failure mode is silent agreement when
  there's real disagreement."** Successful pushback is logged as precedent (the "Gap 9 reversal").
- `BR-mode` (verbatim, the Externality Principle operationalized): **"never self-assert 'done' — let a non-LLM
  oracle say so"** (`scripts\audit.ps1` pre+post each step).
- `BR-auto` (verbatim): **"the gates are the oracle"**; **"never relax a gate to pass it (fix the gate with an
  ADR)."**
- `MAY-user` (verbatim): **"Peer-level adversarial, not polite. No throat-clearing, no flattery, no
  performance of depth."** `OUT-user`, `CAR-prof`, `AEG` all echo verbatim.

**HOLD:** the kit's two-verifier model + adversarial audits (Steelman/Skeptic/5-role) ARE the non-LLM oracle
for a book. Keep them non-optional. In status reports, **lead with what is weak/unverified** (existing B2), and
when the kit substantively disagrees with a seed.md/contract decision, **surface it** — silent compliance is
the named failure.

### B3. Trust DISK/GIT over recall; verify the built ARTIFACT not the source; read the build-log FIRST on resume. **[HIGH — now REPEATED ×4]**
Existing ledger C3 at ×2. Re-confirmed and extended by the gate-as-oracle + regression-revert discipline.
- `BR-auto` (verbatim): **"revert to the last green tag on regression rather than debugging forward past two
  attempts"**; re-run prior gates as a **regression sweep**; **"never relax a gate to pass it."**
- `APO-work` (verbatim): **"compaction resilience (he detects post-compaction degradation from answer quality
  alone and resents manual refeeding)."** → the resume ledger must be self-sufficient; do not lean on Bo to
  re-feed context. (Directly reinforces the kit's COMPACTION SURVIVAL + `_CONTINUITY.md` discipline.)
- `AEG-canon`, `BR-mode`: dated session-canon snapshots + append-only audit logs are the source-of-truth
  breadcrumb; **re-read the newest first.**

**HOLD:** the kit's **anti-drift keystone** (`assemble_manuscript.py` → one version-pinned master, read by all
generators) + GATE-5 reading DOCX/PDF *bytes* + the resume load set (read `_CONTINUITY.md`/`WRONG.md`/state
first) already encode this. Add the regression-revert instinct to the §5 loop framing: on a gate that regresses,
prefer reverting to the last green artifact over debugging forward past ~2 attempts.

### B4. Terse register of ADDRESS; corrections are ONE sentence; proceed on the corrected model the SAME turn. **[MED — now REPEATED ×5]**
Existing ledger C2 (terse commits/docs). Sharpened: the *turnaround* on a correction is same-turn, and the
default reply shape is specified.
- `OUT-user` (verbatim): **"Corrections are one sentence; proceed on the corrected model the same turn."**
- `CAR-prof` (verbatim): **"Communicate slop-free: no 'delve / nuanced / leverage / navigate / tapestry', no
  hedge-and-balance, no executive-summary preamble; direct and dense."**
- `MAY-user` (verbatim, reply shape): **"state results + decisions directly; … one or two sentences at end of
  turn for what changed + what's next."** `AEG`/`OUT`: **"aphoristic at closings."**

**HOLD:** this shapes how the kit *talks*, not what it builds → the §10 terse status format already encodes it.
Note the overlap with the voice blacklist (delve/nuanced/leverage/tapestry) — those are banned in **address**
too, not only in book prose. When Bo corrects mid-session, do not re-derive or re-explain; apply and continue.

### B5. Windows / PowerShell only; anti-Apple; self-contained fixed-path substrate; local toolbelt. **[MED — held; re-confirmed ×3+]**
Existing ledger C6/C7. Re-confirmed, plus a NEW *self-containment* nuance worth noting.
- `MAY-user`, `CAR-prof`, `LLC-user`, `BR-mode`: Windows 11 + PowerShell throughout; RTX 4070 Ti SUPER; the
  end-user GUIs are Windows (Bo's father, no command line).
- **Self-containment nuance** (`BR-mode`, verbatim, ADR-078): **"Nothing outside `C:\backrooms`, ever… Never
  reach for `C:\llama.cpp` / `C:\keel-sidecar-7071` / `C:\models`."** The runtime is vendored *inside* the
  project. → confirms the kit's **portability seam**: fonts vendored repo-relative, machine paths isolated in
  `kit_env.json`; a giftable kit must NOT reach into sibling repos (the exact cross-repo-font failure the kit
  already guards). NOTE the tension: Bo's *global* CLAUDE.md points at fixed-path organs (`C:\chunker`,
  `C:\imguard`, KEEL) — those are opt-in accelerators via `kit_env.organs`, present-or-portable-default; the
  giftable kit's own runtime stays self-contained. Both are true at different layers.

**HOLD:** PowerShell syntax; Word-COM PDF path; Edge `--print-to-pdf` over Playwright for any HTML→PDF;
`kit_env.organs` routing when present, portable defaults when absent; never suggest an Apple toolchain.

### B6. Measure-first reads; date-anchor claims; environment beats recall. **[MED — held; re-confirmed]**
Existing ledger C4/C5/B1. Re-confirmed by the anti-hallucination corpus (A1/A2 are the content-side of the same
posture). `AEG-canon`'s whole "what still needs verification before money moves" section is *environment/
primary-source beats recall* in practice. **HOLD:** the kit's 8K blind-read bound (stricter wins),
`resize_image_safe.py` ≤2000px before vision, `Get-Date` session anchor, and "live tool output overrides
remembered spec" (e.g. `SPINE_OVERRIDE_IN` from the Previewer) already encode this.

---

## PART C — CONFLICTS / TENSIONS (all resolvable; signal is consistent)

The corpus is again unusually consistent. Three scope-tensions, each resolved by layer, not by contradiction:

1. **Autonomy (never block) vs propose-first gap pass (`MAY-meth`).** Not a conflict: the propose-first pass is
   a **session-start** surfacing of *structural* decisions as proposals-with-recommendation — Bo signs off or
   pushes back, then execution runs autonomous to convergence. Resolution: surface structure once at the start
   (= the kit's §4 structural pauses), then do not block. Same shape as the existing ledger's C1 boundary.

2. **"Distinctive polish matters" (`TOP-bake`, bake-offs) vs "terse, no padding / no performance of depth"
   (`MAY-user`).** Not a conflict — two different surfaces. **Polish = the DELIVERABLE** (the book's single-
   authorial-act quality, the differentiator being measured). **Terse = the ADDRESS** (chat/status/commits).
   Never inflate the address; never under-invest the artifact. Mirrors the existing ledger's maximalist-vs-terse
   resolution (Part D.3 there).

3. **Self-contained project runtime (`BR-mode` ADR-078) vs global fixed-path organs (Bo's global CLAUDE.md).**
   Resolution by layer: the **giftable kit's own runtime is self-contained** (vendored fonts, `kit_env.json`
   isolates paths — a portable kit reaches into no sibling repo); the **organs are opt-in accelerators**
   (`kit_env.organs`) that a configured box may point at fixed paths, with portable defaults when absent. Both
   hold; do not let the organ convenience leak a hard cross-repo dependency into the shippable kit.

No hard contradictions found. Employer/status facts (STA departure March 2026; single, no dependents per
`AEG-status`) are **point-in-time** — never bake any employer/marital claim into a book as timeless fact
(consistent with A1/A2 and the existing B1/B3: do not assert an unverified current-state as settled).

---

## PART D — THE SHORTLIST (what to wire / re-confirm in BOOKSMITH, ranked by corroboration)

1. **[×8] Full autonomy / decide-and-log / never block; punishes question loops** → HOLD §4's four pauses as
   the complete stop set; no added prompts. (B1)
2. **[×6] Anti-sycophancy; silent agreement is THE failure; non-LLM oracle says 'done'; never relax a gate** →
   HOLD the two-verifier model + adversarial audits; surface real disagreement. (B2)
3. **[×5] Primary-source dominates model convergence; agreement ≠ truth** → NEW gate line in `audit canon`:
   trace every citation to a primary source; digest-agreement alone = flag, not pass. (A1)
4. **[×5] Terse address; one-sentence corrections, same-turn turnaround; specified reply shape** → HOLD §10
   status format; slop-free address (blacklist applies to chat too). (B4)
5. **[×4] Land every deliverable on disk, never only in chat** → NEW §4 line: chat is a pointer, the artifact
   is the disk file. (A4)
6. **[×4] Trust artifact/git over recall; verify the BUILT file; regression → revert to last green; resume
   ledger self-sufficient (compaction-degradation aware)** → HOLD anti-drift keystone + GATE-5-reads-bytes +
   COMPACTION SURVIVAL. (B3)
7. **[×3] Harness bake-offs — output compared side-by-side; correctness + distinctive polish both matter** →
   NEW ethos line: the kit competes; correctness is table-stakes, single-authorial-act polish is the edge. (A3)
8. **[×3+] Windows/PowerShell only; anti-Apple; self-contained runtime; local toolbelt via `kit_env.organs`** →
   HOLD; keep the portability seam clean (no cross-repo hard deps in the giftable kit). (B5)
9. **[×2, defect-bought] `--help`/"it opens" is NOT a smoke test — deep-probe the real chain (= GATE-5)** →
   NEW §12 line: the shallow check is not the gate. (A5)
10. **[×2, defect-bought] RE-TIGHTEN at distribution/packaging — where defects hide; never reuse a cover/
    interior across services** → NEW §12 annotation. (A6)
11. **[×2, self-named] Tool-tinkering feels like progress; SHIPPING is the metric — bias to irreversible-cost
    actions** → NEW §0/§13 line: kit work is justified only when it unblocks a book. (A7)
12. **[×2] Provenance ladder on every factual claim; strip the unverifiable before ship** → make `canon_refs`
    status explicit; below-Verified anchors never asserted as settled prose. (A2)

---

*End of Bo working-style delta. Append-only; supersede an entry with a dated successor rather than editing it.
Corroboration counts span BOTH this file's 8 projects and the existing `_voiceprofile_crossproject.md` sources.
Companion to `docs/author_voice/_voiceprofile_crossproject.md` (voice + first-cut working-style),
`docs/LESSONS_LEDGER.md` §16–§17 (production idiosyncrasies + author voice), and CLAUDE.md §4 (autonomy).*
