# Author Voice Profile — Cross-Project Rules Ledger (Bo Chen)

> **Provenance.** Mined by *reading* (not grepping) ten preference-memory files scattered across
> Bo's projects (permanentunderclass-cc, wholemachine-org, gracegradient, APPLY, APPLY2, ClaudeCode,
> ASTRA-7, Websites). This ledger exists because the kit once shipped a book that violated Bo's
> voice (em-dashes everywhere) — the prior lessons-mining grep'd for KDP rejection strings and never
> read *this* corpus. Rules that appear in **≥2 independent projects** are the most load-bearing and
> are marked **[REPEATED ×N]**. Each rule carries a verbatim anchor where the exact wording matters,
> and a concrete **ENFORCE** note describing how a mechanical or perceptual gate holds it.
>
> **Source map (short keys used below):**
> - `PUC` = permanentunderclass-cc / `bo-writing-voice-plain.md`
> - `WM` = wholemachine-org / `house-style-spec.md`
> - `GG-work` = gracegradient / `bo-working-style.md`
> - `GG-user` = gracegradient / `user-bo-chen.md`
> - `APPLY` = APPLY / `feedback_hard_rules.md`
> - `APPLY2` = APPLY2 / `feedback_hard_rules.md`
> - `CC-v7` = ClaudeCode / `feedback_methodology_hard_rules.md`
> - `ASTRA` = ASTRA-7 / `user_profile.md`
> - `WS-ctx` = Websites / `feedback-no-self-reported-context-claims.md`
> - `WS-user` = Websites / `user-bo-chen.md`

---

## PART A — VOICE + PROSE RULES (the writing-the-book layer)

### A1. NO EM-DASHES in prose. **[REPEATED ×3 — the single most corroborated rule]**
The rule the kit already broke. It is confirmed in three separate project memories, two of them
about Bo's *own* writing voice.
- `GG-work` (verbatim): **"No em-dashes in prose (AI tell)."**
- `ASTRA` (verbatim): **"Avoids em-dashes in own prose."**
- `GG-work` again ties the ban to the bo-voice profile: *"bo-voice = maximalist commitment, no irony
  shield, mechanical metaphors, recursive restatement."*

**This corroborates and hard-extends the kit's existing "no em-dashes" line: it is not a stylistic
nicety, it is Bo's named #1 AI-tell.** Note the scope trap: em-dashes leak most through *headers* and
`[BO-WRITES]` markers and machine-inserted connective text, not just body prose — the kit's own
LESSONS_LEDGER already flags headers + markers as the top leak sites.

**ENFORCE:**
- Blocking `Grep "[—–]"` sweep (em-dash U+2014 **and** en-dash U+2013) over the *assembled* master
  AND over every `manuscript/current/*` unit — exit non-zero on any hit outside an explicitly cached
  source dir. This is GATE-3's em-dash sweep; it must run on headers and injected front-matter too,
  not only prose bodies.
- Add `—` and `–` to `book_config.voice.blacklist` so `lint_manuscript.py` also catches them.
- Substitution policy the drafter must apply *while writing* (not post-hoc): recast with a period,
  a colon, a comma, or parentheses. Recasting into two sentences is preferred — it matches the plain
  register in A2.

### A2. Write PLAIN, DIRECT, PEER-LEVEL. Bo has a strong allergy to AI-slop and florid "literary" prose. **[REPEATED ×3]**
- `PUC` is the whole-file thesis (verbatim): *"Bo despises AI-slop and overwrought 'literary'
  prose."* He flagged, **"with visible irritation,"** lines like **"these gatherings have a way of
  folding the years in on themselves"** and **"the patience of getting a formulation exactly right,
  the discipline of doing it under regulation, and the quiet pride when..."** — calling it
  **"crap no human would write."**
- `PUC` prescription (verbatim): **"Write plain, direct, peer-level. No flattery, no hedging, no
  purple prose, no padding. Say the useful thing and stop."**
- `GG-work` (verbatim): **"Terse, dense, no corporate padding."**
- `ASTRA` (verbatim): **"Engineering register: precise, terse, anti-performance discipline."**

**Named tells to kill (from `PUC`, verbatim examples):**
1. **"Folding the years in on themselves"-style temporal/abstract flourishes** — evocative
   metaphors that do no work.
2. **Three-part parallel constructions with ascending emotional intensity** ("the patience of X,
   the discipline of Y, and the quiet pride when Z"). This is the "weight-average mashing toward the
   average impressive-sounding template" that Bo spent a whole session dissecting. **Ascending
   tricolons are a named Bo-tell — treat like em-dashes.**
3. **Flattery, hedging, padding.** "Say the useful thing and stop."

**ENFORCE:**
- Extend `book_config.voice.blacklist` with the sentimental/flourish vocabulary that this corpus
  names and that the kit's §7 AI-tell list already forbids (generic sentimentality, "quiet pride,"
  "a way of," "folding … in on themselves," etc.). `lint_manuscript.py` fails on any hit.
- Add an **ascending-tricolon heuristic** to the voice gate: flag sentences containing three
  comma-or-"and"-joined abstract-noun phrases climbing to an emotional payoff. This is advisory-flag
  (hard to make zero-false-positive), surfaced for author review, not an auto-fail — but it MUST be
  surfaced, because it is the exact structure Bo called "crap."
- The anchor exemplar in `exemplars/anchor.md` must be a genuine bo-voice sample so the
  exemplar-consistency check in GATE-3 has real plain-register ground truth to measure drift against.

### A3. bo-voice, when writing *as* Bo, is a specific positive profile — not merely "absence of slop." **[REPEATED ×2]**
- `GG-work` (verbatim): **"bo-voice = maximalist commitment, no irony shield, mechanical metaphors,
  recursive restatement."**
- `PUC`: the default *working* voice with Bo is "clean and unadorned"; prose **written as him** is a
  distinct registered voice (`PUC` names it the `anthropic-skills:bo-voice` skill).

The four positive markers, unpacked:
- **Maximalist commitment** — full-throated assertion, not hedged ranges. (Consistent with A2's
  "unhedged" and Part C's "ground truth over flattery.")
- **No irony shield** — say it straight; no defensive winking or self-deprecating distance.
- **Mechanical metaphors** — his imagery is machine/systems-flavored (fits the whole-body-of-work
  through-line: mind-as-pattern, harness/tenancy, "core-wire," "the door is still the door").
- **Recursive restatement** — deliberately circles back and restates a claim in a sharpened form.

**Load-bearing distinction:** "recursive restatement" (a *wanted* bo-voice move) must not be lint-
confused with the AI-tell of mechanical repetition. The kit's §7 already prizes **authorial
self-correction** ("I said X earlier; the sharper version is…") — that IS Bo's recursive
restatement, and it is a feature. Do not scrub it.

**ENFORCE:**
- If `book_config.is_fiction` or the unit's voice spec targets first-person Bo, load the bo-voice
  profile (the four markers above) into the Context Pack's voice block, not just the blacklist.
- The exemplar-consistency check should reward, not penalize, sharpened restatement and mechanical
  imagery. Encode the four positive markers as greenlist signals in `book_config.voice.greenlist`.

### A4. Do NOT leak "research notes" / loaded context into the output. (Bo's named "cardinal sin.")
- `PUC` (verbatim): **"Don't leak 'research notes' (everything I just loaded) into output just
  because it's topically relevant — the cardinal sin he identified."**

For a book: the Context Pack (contracts, registries, handoffs, canon digests, this ledger) is
*scaffolding*. None of it may surface as prose. No "as the contract requires," no meta-narration of
the machinery, no dumping a canon digest into a chapter because it was in context.

**ENFORCE:**
- This maps directly onto the kit's existing §7 AI-tell ban on meta-commentary openers ("In this
  chapter we will explore…") and "Key Takeaways" boxes. Keep those in the blacklist.
- Add a scaffolding-leak check to GATE-3: grep the drafted unit for contract/registry vocabulary
  ("Must-Accomplish," "Must-Plant," "handoff," "Layer 1," "callback," "refrain placement,"
  "canon_ref," "thread registry"). Any hit = leak = fail.

---

## PART B — HONESTY POSTURE (governs both prose content AND how the kit talks to Bo)

### B1. NEVER state internal-state / self-reported context as fact. Telemetry over testimony. **[Websites — bought with a real caught error]**
- `WS-ctx` (verbatim event): On 2026-07-10 the assistant told Bo its context window was "200k total"
  and that "the harness has already summarized older portions at least once." **Both were false** —
  Bo's UI showed **1M window, ~68% used, zero compactions.**
- `WS-ctx` prescription (verbatim): **"Never assert context size, usage, or compaction history as
  fact. If asked: say it is not measurable from inside, give any estimate as weakly-held with its
  basis, and defer to Bo's UI meter."** Generalized: **"telemetry over testimony"** for **any**
  self-state claim.
- Named failure mode: **"fail-plausible self-state fabrication"** (L13 / F-FAILPLAUSIBLE) — reasoning
  from stale priors and delivering the *inference as observation*.

Directly relevant to the kit because the kit's status reports make quantitative self-claims (word
counts, page counts, "gates green"). Those must come from **measured artifacts**, never from
recall or arithmetic-in-the-head.

**Ground-truth fact for the kit (verbatim):** *"Fable 5 sessions on Bo's setup run a 1M context
window (he says 1M is the floor for Fable 5 and even Opus 4.8 defaults to 1M)."* → do not claim a
200k window or invent compaction events.

**ENFORCE:**
- Every number in a `status` report (words, pages, spine, dimensions, gate pass/fail) must be the
  literal stdout of a tool run this session (`assemble_manuscript.py` word count,
  `ComputeStatistics(2)` pages, `verify_build.py` result) — never a remembered or estimated figure.
  This is the kit's existing **two-verifier model + "PAGES re-derived, never hard-coded"** rule; B1
  is the *why* behind it and extends it to conversational self-claims.
- If a figure was not measured this session, label it explicitly as an estimate with its basis.

### B2. Ground truth over flattery; tell Bo what is weak; adversarial peer engagement. **[REPEATED ×3]**
- `PUC` (verbatim): **"He values rigor, honest caveats, and being told what's weak."**
- `GG-work` (verbatim): **"Ground truth over flattery. He wants adversarial peer engagement,
  calibrated pushback, the unhedged version."**
- `CC-v7` **Externality Principle** (verbatim): **"Every critical loop needs one assertion the model
  did not author… A smarter model produces more convincing wrong output AND more convincing wrong
  verification of it; same-model-class verification is circular."**

**ENFORCE:**
- This is the philosophical root of the kit's **two-verifier model** (mechanical + perceptual) and
  its **adversarial audits** (Steelman / Skeptic / 5-role). Keep them; they are not decorative — they
  are Bo's Externality Principle applied to a book. `vision_verify.py` is the "assertion the model did
  not author" for the cover; `verify_build.py` is it for the interior.
- In status reports, lead with what is *weak or unverified*, not with what passed. Surface caveats
  unprompted.

### B3. No self-reported context claims in the *manuscript* either. (Extends A4 + B1 to prose.)
The book must not claim experiences that did not happen or fabricate canon. The kit's §4 "Never"
list already forbids **"fabricate a canon citation, or invent an author experience that didn't
happen."** B1's caught error is the same failure mode (asserting an unverified internal state as
fact), now in prose form.

**ENFORCE:** Keep the canon-anchor audit (`audit canon`) and the "no fabricated author experience"
rule in GATE-3. Personal-material placement (§7.9) draws only from real intake canon, never invented
anecdote.

---

## PART C — WORKING STYLE FOR A WRITING PROJECT (autonomy, velocity, no-BS)

### C1. FULL AUTONOMY; decide-and-log; NEVER block on Bo. **[REPEATED ×4 — the strongest working-style signal]**
- `GG-work` (verbatim): **"Decide-and-log; propose then proceed; never block on him — full autonomy
  on taste, with snapshot/CHANGELOG as the safety net."**
- `ASTRA` (verbatim): **"Collaborates by giving context once, expecting fast execution after… is
  comfortable letting AI pick within already-discussed ranges."**
- `GG-user` capstone (verbatim): **"the thinking is done; the only missing input is the first
  owner-buyer conversation"** — the *"the door is still the door"* discipline (stop re-deciding
  what's already decided; execute).
- Corroborated by the kit's own ethos already in memory (ship-at-90%, autonomy expected).

**Boundary (where autonomy stops — from `ASTRA`, verbatim):** **"Wants architectural decisions
surfaced before unilateral choices on novel ground, but is comfortable letting AI pick within
already-discussed ranges."** → Surface *structural* decisions (Book Bible changes, a unit's
authorship class, integration_mode); do NOT surface taste calls inside an agreed structure.

**ENFORCE:**
- This IS the kit's **§4 "four pauses" contract** (Class-A prose, substantive seed.md changes,
  WRONG.md commit, export v1.0) — and nothing else. C1 confirms those four are the *complete* set of
  stops; everything else runs to convergence. Do not add interactive prompts.
- `CHANGELOG.md` (mechanical actions) + `WRONG.md` (position revisions) + state snapshots are the
  "decide-and-log" safety net Bo explicitly relies on in place of blocking. Keep them current — the
  ledger is the substitute for asking.

### C2. Give context once, expect fast execution. Terse register in commits/docs. **[REPEATED ×3]**
- `ASTRA` (verbatim): **"Match his terse register in commits and docs."**
- `GG-user` (verbatim): **"treat the autotelic-design and Dave-frame rules as load-bearing
  structural commitments, not aesthetic preferences. He has thought about these for years; do not
  relitigate."**
- `APPLY` / `APPLY2` headers (verbatim): **"LOCKED decisions… Do not relitigate."**

The re-litigation tax is a named cost. `GG-work` opens: *"Apply by default; don't make him
re-explain."* For a book: once `seed.md` and `book_config.json` lock a decision (structure, voice,
class map, integration_mode), execute against it; do not reopen it every session.

**ENFORCE:**
- The kit's boot sequence already loads seed.md + config + WRONG.md tail every session precisely so
  locked decisions are re-established, not re-debated. Keep `seed.md` §1–§7 authoritative;
  `book_config.json` is the single source for every knob (never hard-code, never re-ask a value that
  lives in config).
- Status reports use the §10 terse fixed format — no prose preamble, no re-explaining the machine.

### C3. Trust disk/git over recall; never resume blind; verify the ARTIFACT not the source. **[REPEATED ×2]**
- `GG-work` (verbatim): **"Trust disk/git over recall; never resume blind. Verify binary freshness,
  not source ('triple-check' = confirm the compiled artifact has the fix)."**
- `WS-user` (verbatim): **"read that [BUILD_LOG] log first when picking up a project… a stale log
  misleads the next session."** Bo keeps **"a meticulous per-project `*_BUILD_LOG.md`."**

For a book, the "compiled artifact" is the **assembled master + the produced PDF/DOCX**, not the
markdown units. A gate must verify the *built* file (page count, mirror margins, word-count parity),
not assume the source implies the artifact.

**ENFORCE:**
- This is the kit's **anti-drift keystone** (`assemble_manuscript.py` → one version-pinned master,
  read by all generators) and the **"verify the built PDF"** discipline: the Kindle-8,476-words-short
  bug was exactly "verified source, shipped stale artifact." GATE-5 reads the DOCX/PDF bytes.
- Treat the kit's ledgers (`CHANGELOG.md`, `_CONTINUITY.md`, `WRONG.md`) as Bo's `*_BUILD_LOG.md`
  convention: read first on resume, append a dated entry on every change, never let them go stale.

### C4. Environment/artifact beats research/recall when they conflict. **[REPEATED ×2]**
- `GG-work` (verbatim): **"Environment beats research: when a deep-research/model doc conflicts with
  what's on his machine, the machine wins… filesystem-check before tooling."**
- `WS-ctx` is the same principle for self-state: **defer to Bo's UI meter** over the model's
  inference.
- Related date-anchoring rule (`GG-work`, verbatim): **"date-anchor model claims"**; world-refresh is
  a **WebSearch fan-out, not the deep-research workflow** (its verifier rate-limits / false-negatives).

**ENFORCE:**
- The kit already **anchors "now"** every session (`Get-Date`) and treats KDP-policy / price /
  "latest" claims as clock-anchored. Keep it. When a remembered spec conflicts with a tool's live
  output (a Previewer's stated spine width, an actual page count), the **tool output wins** and gets
  hard-coded per that measurement (e.g. `SPINE_OVERRIDE_IN` from the Previewer).

### C5. Chunked writes for long outputs; measure-first reads. **[REPEATED ×2]**
- `GG-work` (verbatim): **"Chunked-write discipline: long outputs (>~15-20KB) go to disk in chunks,
  then concatenate — single big writes can truncate and lose work."**
- `CC-v7` (verbatim): **"Measure-first reads. Before any file >20K tokens, image >2000px, dir >200
  entries: inspect first; chunk if exceeded."** And: `Read` **"hard-errors on files >~25K tokens AND
  on files >256KB."**

**ENFORCE:**
- This IS the kit's boot rule **"never blind-read a file >8K tokens; size first with
  `estimate_tokens.py`"** and its **image discipline** (`resize_image_safe.py` ≤2000px before any
  vision — cover wraps ~4255×3125 always trip the cap). Bo's numbers are stricter (8K kit vs 20K
  general) — **keep the stricter 8K kit bound.**
- For very large generated artifacts (a full assembled master, a long ledger), prefer chunked writes
  + concatenate over one giant write. (This ledger itself was written in one pass because it is under
  the truncation risk threshold; larger deliverables should chunk.)

### C6. Windows / PowerShell only. Anti-Apple. Specific tool substitutions. **[REPEATED ×3]**
- `GG-work` (verbatim): **"Anti-Apple: never recommend macOS / iOS / Apple Silicon. Linux + Windows
  only."**
- `WS-user` (verbatim): **"Windows 11 + PowerShell. Prefer the PowerShell tool over Bash for Windows
  paths — Bash mangles backslashes in `C:\...` paths."**
- `GG-work` (verbatim): **"Use the PowerShell tool for cargo/git (git-bash mangles exit codes);
  render PDFs via system Edge `--print-to-pdf` (Playwright hangs on his machine)."**

**ENFORCE:**
- Kit already mandates PowerShell syntax and the Word-COM PDF path (`docx_to_pdf.py`) as "the only
  trustworthy path." Consistent. For any *browser-rendered* PDF (HTML→PDF), prefer Edge
  `--print-to-pdf` over Playwright/Chromium-headless, which hangs on Bo's box.
- Never suggest an Apple toolchain, font, or app anywhere in book output or tooling.

### C7. Use Bo's local toolbelt; do not reinvent it. **[REPEATED ×2, aligns with the kit's `organs` seam]**
- `GG-work` (verbatim toolbelt): **`chunker`** (oversized files), **`imguard`** (downscale images
  ≤2000px BEFORE viewing; >2000px crashes ingestion), **`earshot`** (audio/video→transcript —
  **"treat as his spoken prompt — he uses voice memos"**), **`ff`** (instant file find), **KEEL**
  (his Rust AI substrate/sidecar :7071), plus HyperFrames, TRANSPORTER.
- The user's global CLAUDE.md ("six organs") is the same toolbelt at fixed paths.

**ENFORCE:**
- The kit's `kit_env.json` **`organs` block** + the **KEEL vision backend** (`--backend auto`) are
  exactly this. When present, route through them (chunker for >8K reads, imguard/`resize_image_safe`
  for images, KEEL for on-box vision). When absent, the portable defaults apply. Do NOT hand-roll a
  replacement for a configured organ.
- **Earshot rule for intake:** if the intake drop contains audio/video, it is likely Bo's *spoken
  prompt* (he uses voice memos) — transcribe and treat the transcript as an authoritative instruction,
  not as mere source material.

---

## PART D — CONFLICTS / TENSIONS BETWEEN PROJECTS

Nothing in this corpus **contradicts** another entry; the signal is unusually consistent. The few
tensions are scope/threshold differences, resolved by taking the stricter or more-specific value:

1. **Read/chunk thresholds differ by project (not a contradiction, a scope difference).**
   `CC-v7` says measure-first at **>20K tokens**; the BOOKSMITH `CLAUDE.md` says **never blind-read
   >8K tokens**. → **Resolution: the kit's 8K bound wins inside BOOKSMITH** (it is the more specific,
   stricter, project-local rule). `GG-work`'s chunked-*write* threshold (~15–20KB) is about *writing*,
   not reading, so it does not conflict.

2. **"Recursive restatement" (wanted) vs "mechanical repetition" (an AI-tell, banned).**
   `GG-work` prizes recursive restatement as a bo-voice feature; §7 of the kit bans mechanical
   transitions/uniformity. → **Resolution (A3): these are different things.** Recursive restatement =
   *sharpened* re-assertion (the §7.6 "authorial self-correction" move, a feature). Mechanical
   repetition = verbatim/uniform restatement with no sharpening (a tell). The lint must distinguish:
   reward variation-on-restatement, flag verbatim duplication.

3. **"Maximalist commitment" (bo-voice) vs "terse, no padding" (working register).**
   `GG-work`/`ASTRA` demand terseness; `GG-work` also names bo-voice as *maximalist*. →
   **Resolution:** two different registers for two different outputs. **Working/chat/commit/status
   voice = terse and unadorned** (`PUC` "clean and unadorned"). **Prose-as-Bo = maximalist commitment
   without padding** — maximalist in *conviction and restatement*, still zero flattery/hedging/filler.
   Maximalism is depth of commitment, not verbosity of fluff. Set the register per `book_config.voice`
   / per-unit spec; never blur them.

4. **Day-job employer noted as possibly stale.** `GG-user` says **"Day job (per other-project
   memory, may shift): IT at Southwest Transplant Alliance"** while `ASTRA`/`WS-user` state it
   flatly. Low stakes for a writing kit; flag only so no book bakes an employer claim as timeless
   fact (consistent with B1/B3: don't assert an unverified current-state fact).

---

## PART E — THE SHORTLIST (what to wire into BOOKSMITH first)

Ranked by corroboration count, highest first:

1. **[×4] Full autonomy / decide-and-log / never block** → keep §4's four pauses as the *complete*
   stop set; rely on CHANGELOG/WRONG/state ledgers instead of asking. (C1)
2. **[×3] No em-dashes** → blocking `Grep "[—–]"` sweep on assembled master + every current unit +
   headers/markers; add `—`/`–` to config blacklist. (A1)
3. **[×3] Plain/direct/peer-level; kill AI-slop, purple prose, ascending tricolons, flattery,
   padding** → extend blacklist with named flourish vocabulary; add advisory ascending-tricolon
   flag; real bo-voice anchor exemplar. (A2)
4. **[×3] Give context once, don't relitigate locked decisions; terse commits/docs** → seed.md +
   config are authoritative; terse §10 status format. (C2)
5. **[×3] Windows/PowerShell only, anti-Apple, Edge-print-to-PDF, PowerShell for git** → already the
   kit default; hold the line. (C6)
6. **[×2] bo-voice positive profile** (maximalist / no irony shield / mechanical metaphors /
   recursive restatement) → greenlist signals + voice block, distinct from the blacklist. (A3)
7. **[×2] Trust artifact over source; verify the built PDF; read the build-log first** → anti-drift
   keystone + GATE-5 reads bytes + treat kit ledgers as the BUILD_LOG. (C3)
8. **[×2] Environment/telemetry beats research/recall; date-anchor claims** → clock-anchor every
   session; live tool output overrides remembered spec. (C4)
9. **[×2] Measure-first reads / chunked writes** → 8K read bound (stricter wins), image ≤2000px,
   chunk big writes. (C5)
10. **[×2] Use the local toolbelt/organs, don't reinvent; earshot = spoken prompt** → route through
    `kit_env.organs` + KEEL when configured. (C7)
11. **[×1 but bought with a caught error] No self-reported internal-state as fact; telemetry over
    testimony** → every status number is measured stdout this session, never recall. (B1)
12. **[×1, whole-file] Don't leak loaded context/"research notes" into output (the cardinal sin)** →
    scaffolding-leak grep in GATE-3. (A4)

---

*End of cross-project voice ledger. Append-only; supersede an entry with a dated successor rather
than editing it. If a new project memory adds or sharpens a rule, add it here with its source key and
corroboration count.*
