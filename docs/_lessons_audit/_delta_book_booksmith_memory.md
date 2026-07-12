# DELTA AUDIT — C--BOOK project memory + C--BOOKSMITH kit memory vs. LESSONS_LEDGER.md

*Anchored 2026-07-12 03:15 -05:00 (Sunday, Central Standard Time). Method: READ-in-full (not grep) of the memory files NOT covered by the four prior `_delta_*.md` audits, cross-checked against `docs/LESSONS_LEDGER.md` §1–§18, the existing deltas, and `docs/author_voice/AUTHOR_VOICE_Bo_Chen.md` (confirmed present + 4 `_voiceprofile_*.md`).*

**Scope boundary (what the prior four audits already covered, NOT re-reported here):** `_delta_titanic_projects.md` = the eight `C--Claude-Titanic/memory/project_*.md`; `_delta_titanic_references.md` = the seven Titanic `reference_*.md`; `_delta_secondnotebook_buildlog.md` = `C:\BOOK\BUILD_LOG.md` + Second-Notebook memories; `_delta_production_lessons.md` = the three canonical `PRODUCTION_LESSONS_LEARNED.md`. This audit targets the **untouched** corpus:

**Sources read IN FULL this pass:**
- `C:\Users\user\.claude\projects\C--BOOK\memory\project_v1_1_ship_state.md` (ATD ship state, 2026-04-24)
- `C:\Users\user\.claude\projects\C--BOOK\memory\MEMORY.md` (C--BOOK index)
- `C:\Users\user\.claude\projects\C--BOOKSMITH\memory\user-bo-chen.md`
- `C:\Users\user\.claude\projects\C--BOOKSMITH\memory\booksmith-session-modes.md`
- `C:\Users\user\.claude\projects\C--BOOKSMITH\memory\portability-initiative.md`
- `C:\Users\user\.claude\projects\C--BOOKSMITH\memory\MEMORY.md` (C--BOOKSMITH index)

**Explicitly SKIPPED (prior-agent-covered):** the six `C--BOOK/memory/feedback_*.md` (autonomy_grant, no_em_dashes, session_discipline, refrain_chapter_pattern, drafter_guidance_pointer, next_session_snapshot) — the task states these voice files were already read; their content is baked at ledger §17 + `AUTHOR_VOICE_Bo_Chen.md`. Not re-diffed.

**Headline:** the C--BOOKSMITH memory is a *process/mission* layer the ledger barely touches — MAINTAIN mode (now landed in CLAUDE.md §1 but NOT in the ledger), the OPUS-not-fable subagent rule (a hard model-policy atom the ledger states loosely), and the portability mission's own status surface. The C--BOOK `project_v1_1_ship_state.md` is a *shipped-book* record that corroborates most of §3/§5/§7 but carries a handful of concrete anchors (the ATD halo two-tone rule, the F9-TOC + math-recheck open items, the "don't over-inject author voice into an analytical blend" trade) that are absent or weaker. Nothing contradicts a mechanical gate. Grouped below: PRODUCTION · WRITING/CRAFT · VOICE · PROCESS/CONTINUITY.

---

## PRODUCTION

### P1 — Cover-text HALO is a TWO-TONE, contrast-adaptive rule (dark-text+cream-halo on pale ground; cream-text+dark-halo on dark ground)  — ABSENT · MED
- **Lesson (verbatim), `project_v1_1_ship_state.md` (Key session conventions):** *"Halo/stroke technique for cover text on mixed-contrast backgrounds: dark text + cream halo (for title on pale wall), cream text + dark halo (for subtitle/author on dark sill)."* Corroborated by the hardcover note: subtitle/author use "cream halo trick + nudged lower (2.6% bottom margin)."
- **Ledger status:** §6.4 has ONE direction only — *"Title: cream halo stroke (~2% of font px) for legibility across a gradient."* It never states that the halo must **flip** with the local background luminance: dark text needs a light (cream) halo, light text needs a dark halo, chosen per text-element against the pixels behind it.
- **Bake-in:** Extend §6.4 halo note: *"The halo is contrast-adaptive PER text element against the pixels behind it — dark glyph → cream/light halo (title over a pale wall); light glyph → dark halo (subtitle/author over a dark sill). One book routinely uses BOTH on the same cover. Halo stroke ≈ 2% of font px. `vision_verify` should confirm each text element clears its own local background, not a single global assumption."* Optionally have `composite_cover.py` sample mean luminance under each text box and pick halo polarity automatically.

### P2 — The ATD hardcover byline was NUDGED LOWER to a 2.6% bottom margin (a concrete typographic offset)  — ABSENT · LOW
- **Lesson (verbatim):** *"Hardcover uses CormorantGaramond-Bold.ttf dedicated file for subtitle/author + cream halo trick + nudged lower (2.6% bottom margin)."*
- **Ledger status:** §5.7/§6.4 give the quiet-zone/keep-out figures and the "lower third of the back open" rule, but no front-face **byline vertical placement** anchor. The prior Titanic-projects delta (#7) added the half-title/form-line content rules but not this offset.
- **Bake-in:** §6.4 — record a front-face byline anchor: *"Author/byline sits low on the front — ~2.6% up from the bottom trim (ATD hardcover), inside the quiet zone. Keeps the upper-third-front open for the title (§5.7)."* Minor; a calibration anchor, not a gate.

### P3 — Native-ratio cover art (1.491:1) shipped rather than reframed to 1.6:1  — ALREADY FLAGGED (corroboration) · LOW
- **Lesson (verbatim):** ATD Kindle cover "1696×2528, title+subtitle+author composited"; front art "1696×2528, ratio 1.491 — matches book ratio natively"; alternates rejected as "ratio 1.327, too square."
- **Ledger status:** §7.4 mandates 1600×2560 (1.6:1). This exact drift is ALREADY captured in `_delta_titanic_projects.md` DELTA 6 (same 1696×2528 = 1.491:1 datum). **No new bake-in** — recorded here only to confirm the C--BOOK memory is the *same* source and the existing delta stands. Note the secondary datum this file adds: the 1.327:1 Kling alternates were rejected as "too square," i.e. the practical accept band skews toward the taller 1.6:1, reinforcing the existing bake-in (reframe, do not ship the raw native ratio).

### P4 — `PAGES` + trailing-blank pad are the two coupled constants to bump on any reflow (shipped-book restatement)  — CONFIRMATION · (no action)
- **Lesson (verbatim):** *"If manuscript page count changes in future: update `PAGES = 426` constant in both composite_cover_atd_kdp*.py scripts AND the `PAD_BLANKS = 2` trailing-blanks constant in generate_book_kdp.js may need adjustment to keep the final PDF count even."*
- **Ledger status:** COVERED and STRONGER — §5.8/§12 already mandate `PAGES` be a SINGLE re-derived variable (not three hardcodes) and §4.3/§4.4 replace the hand-tuned `PAD_BLANKS` with the `SectionType.EVEN_PAGE` trailing section + fitz ÷2/÷4 padding. The memory shows the *older* two-hardcode approach the ledger deliberately supersedes. Logged so a maintainer doesn't "restore" the `PAD_BLANKS` constant.

### P5 — KDP categories: ATD shipped **3** (Metaphysics / Mind & Body / Epistemology)  — TENSION w/ existing D5 · MED
- **Lesson (verbatim), `project_v1_1_ship_state.md`:** *"Categories: Politics & Social Sciences → Philosophy → Metaphysics / Mind & Body / Epistemology"* — i.e. **three** category paths recorded for a shipped book.
- **Ledger status:** §9.1/§14 say "≤3." `_delta_production_lessons.md` D5 argues the ASTRA canon says **2 max** and recommends changing the default to 2.
- **Delta / reconciliation:** this is a genuine cross-source TENSION, not a clean correction. The ASTRA canon (fiction example) says 2; the ATD shipped record (nonfiction) shows 3. Most likely KDP's picker count is **register/UI-dependent or changed over time** (nonfiction philosophy nests deep and may expose 3). **Do NOT silently adopt 2 as universal on the strength of one fiction canon.**
- **Bake-in:** supersede the raw "change 3→2" in D5 with: *"Category count at submit is not a fixed constant across the corpus — a shipped nonfiction book (ATD) used 3 paths; the ASTRA fiction canon says 2. Anchor to the LIVE KDP picker on the run date (it is the arbiter, like the Previewer for geometry); default to the observed maximum the picker offers, and record the count used. The safe floor is 2; 3 is attested for nonfiction."* Keeps both data points honest instead of picking one.

### P6 — Post-COM math re-check + F9-TOC are BOTH real author-side finishers on a math book  — WEAKER · MED
- **Lesson (verbatim), open items:** *"Bo verifying math rendering on screenshots — may have residual issues with \left or \frac in specific pages (session cut off mid-check)"* and *"Bo's manual F9 TOC refresh in Word on both Kindle + KDP DOCX before upload."*
- **Ledger status:** the F9-TOC finisher is ALREADY captured in `_delta_titanic_projects.md` DELTA 4 + `_delta_production_lessons.md` §18.2. But the **math-render rendered-PDF re-check** as a paired finisher is only implied (§3.9 verifies at DOCX level via `check_docx_latex.py`; §7.3 says equations must render). The lesson here is that even after the converter runs, `\left`/`\frac` can still be visually wrong on specific rendered pages and needed a human screenshot pass.
- **Bake-in:** add to §3.9/§10 VERIFY for math books: *"After the Word-COM PDF, spot-check the RENDERED pages carrying `\left`/`\right`/`\frac` (render → resize ≤2000px → vision) — DOCX-level `check_docx_latex.py` passing does not guarantee the on-page glyph layout is correct (ATD had residual `\left`/`\frac` issues visible only in the rendered PDF)."* Pairs with the existing F9-TOC finisher as the two math-book EMIT checks.

### P7 — CONFIRMATIONS (shipped-book record agrees with the ledger; no action)
- **ODD_PAGE per chapter + trailing EVEN_PAGE** forces recto and even parity → §4.3. ✓ ("SectionType.ODD_PAGE per chapter … trailing EVEN_PAGE blank section guarantees even total.")
- **Mirror margins + page numbers on outer corners** in the KDP generator → §3.4/§4.3. ✓ (note: §16.2 later moves page numbers to bottom-CENTER as house style — the ATD "outer corners" record predates that override; do not treat as a conflict).
- **Dedicated `CormorantGaramond-Bold.ttf` alongside the variable Light TTF** → §6.4/§11.2. ✓ (open-item #5 confirms both files present; the ledger vendors both repo-relative).
- **One-pager "The Book in One Page" as a Heading-1 between TOC and Prologue** for TOC discoverability → consistent with §7.2 H1-drives-autoTOC. ✓ (a concrete instance of the "one-pager" front element; not a new rule).
- **LaTeX→Unicode converter scope** (Greek, operators, \dot precomposed, \frac-after-subscripts, \left/\right strip, prose-mode Ω_ext fixer) → §3.9. ✓ Matches the pipeline order exactly; the exact glyph-coverage tables remain the open delta already filed in `_delta_titanic_references.md` 6.1–6.3.

---

## WRITING / CRAFT

### W1 — "Don't over-inject author-voice signatures into an analytical Claude-doing-Bo blend" — an accepted, deliberate voice-fidelity CEILING  — ABSENT · MED
- **Lesson (verbatim), `project_v1_1_ship_state.md` (Key session conventions):** *"Don't inject Bo-voice signatures beyond what the current Claude-doing-Bo-in-analytical-mode blend already has — Bo accepted this trade-off explicitly."*
- **Ledger status:** ABSENT, and it runs *against the grain* of §17's push to maximize the fingerprint. §17 treats more Bo-voice as strictly better (hit the semicolon density, the hammer, the idiolect markers). This record says the opposite at the top end: on an abstract/analytical treatise written by Claude-as-Bo, there is a point past which *forcing* more idiolect reads as caricature, and Bo **explicitly accepted** the blended register rather than a maxed one.
- **Bake-in:** add a calibration caveat to §17 (near F1–F6): *"Voice fidelity has a ceiling, not just a floor. On abstract/analytical work authored by the model in Bo's register, do NOT over-inject idiolect markers past the natural blend — Bo explicitly accepted the 'Claude-doing-Bo-in-analytical-mode' register on ATD rather than a maxed-signature version. Meet the HARD floors (F1 em-dash=0, F3 no artifacts) always; treat the density markers (F2 semicolons, F4 the hammer, F5 idiolect) as targets to reach, not ceilings to exceed into pastiche. When unsure, the analytical blend is acceptable."* This prevents an over-eager instance from sprinkling "which is to say / in the sense that" to hit a metric and producing parody.

### W2 — The whole "de-concretize / strip personal proper nouns" direction is a STANDING, permanent instruction, verified at ship  — WEAKER · MED
- **Lesson (verbatim):** *"Bo's de-concretization direction from 2026-04-23 is permanent: abstract voice, no Bo biography, strip personal proper nouns"*; and the audit-clean line: *"0 personal proper nouns (Bo Chen / Sam / Tori / STA / Marcolin / Debra / Jocelyn / Weiming / Frank etc. all stripped per Bo's direction)."*
- **Ledger status:** the de-concretize *operation* is filed in `_delta_secondnotebook_buildlog.md` D6/D8 (whole-repo concretion sweep + `forbidden_proper_nouns[]` grep). What this file ADDS: (a) the direction is **permanent/standing**, not a one-off — the default posture for a Bo book is abstract unless he says otherwise; (b) the concrete **verified-clean exit criterion** ("0 personal proper nouns" with a named blocklist) is a shippable check.
- **Bake-in:** reinforce D8's `voice.forbidden_proper_nouns[]` with a default-posture note in §17.2: *"Bo's standing direction (2026-04-23, marked permanent) is abstract voice / no autobiography / strip personal proper nouns UNLESS he opts a given book into personal mode. Seed `voice.forbidden_proper_nouns[]` from the known personal set (Bo Chen + any real names/institutions) at INGEST, and the ship gate asserts 0 occurrences outside cached-source dirs."* Ties the standing posture to the existing mechanical backstop.

### W3 — Adversarial-review integration produced SITED insertions at named chapters (concrete instance of existing D4)  — CONFIRMATION · LOW
- **Lesson (verbatim):** *"v1.1 adversarial-review insertions in Ch 11 (1.5% calibration caveat), Ch 18 (operator-identity acknowledgment), Ch 22 (recursion-metaphorical + Reader-Side Orphan section), Ch 19 (Translation as Distinctive Contribution), Ch 8 (motivated-reasoning discipline)"* + "WRONG.md … 6 entries documenting v1.0→v1.1 revisions."
- **Ledger status:** this is the SAME event already analyzed in `_delta_secondnotebook_buildlog.md` D4/D5 (sited insertions, honesty caveats at the site, WRONG.md attribution). **No new bake-in** — confirms D4/D5 from the crystallized project-memory side (six WRONG.md entries = the append-only discipline §11 mandates, exercised). Corroboration only.

---

## VOICE

*(No NEW voice atoms beyond §17 + `AUTHOR_VOICE_Bo_Chen.md`; the six `feedback_*.md` that carry the primary voice signal were prior-covered and skipped per task. W1 above — the fidelity ceiling — is the one voice-adjacent delta and is filed under WRITING/CRAFT because it modifies the §17 fingerprint stance rather than adding an atom.)*

- **V-confirm:** the C--BOOK `MEMORY.md` index confirms the voice corpus provenance (no-em-dashes tell, refrain six-step closing pattern, session-discipline continuity). All already at §17 / `AUTHOR_VOICE_Bo_Chen.md`. No delta.

---

## PROCESS / CONTINUITY

### C1 — MAINTAIN / kit-polish is a THIRD session mode — landed in CLAUDE.md but NOT in the ledger  — WEAKER (ledger) · MED
- **Lesson (verbatim), `booksmith-session-modes.md`:** *"On 2026-07-11 Bo opened a session with 'we are not writing a book, we are continuing to polish this entire booksmith project itself' — a third session mode that CLAUDE.md §1 does not name (its mode detection only knows INIT and RESUME, both book-centric)."* How-to: full boot, then treat book workspaces as read-mostly (ledger-hygiene fine, prose not); agenda from `PORTABILITY_GAP_ANALYSIS.md` + session log + git status.
- **Ledger status:** the loaded CLAUDE.md §1 step 4 NOW names **MAINTAIN** (the memory's recommendation landed). But `LESSONS_LEDGER.md` has NO session-mode taxonomy at all — §15 covers compaction/resume survival but not the INIT/RESUME/MAINTAIN triad. The ledger is the "constitution"; a mode that governs a whole class of sessions belongs in it, not only in the orchestrator file.
- **Bake-in:** add a short entry to §15 (or a new §1.x in the ledger's INTAKE section): *"Three session modes: **INIT** (new intake drop, no workspace) · **RESUME** (a `book_workspace/<slug>/` exists, load the resume set) · **MAINTAIN** (kit-polish: work `_tools/`/`docs/`/contracts/hooks; leave any in-flight book with `_CONTINUITY.md` STATUS≠COMPLETE untouched — resume state preserved, no prose). MAINTAIN draws its agenda from `docs/PORTABILITY_GAP_ANALYSIS.md`, the session log, and git status."* This closes the gap the memory itself flagged ("propose a formal MAINTAIN mode … so this stops being verbal-override-only").

### C2 — Subagent model policy is a HARD atom: fan-out = OPUS, "not fable class"  — WEAKER · HIGH
- **Lesson (verbatim), `portability-initiative.md`:** *"Model policy: fan-out subagents are OPUS class ('not fable class!' — Bo, verbatim)."* Corroborated by `C--BOOKSMITH/MEMORY.md` ("subagents = OPUS class") and the portability memory's whole framing (four OPUS auditors mapped machine-coupling).
- **Ledger status:** WEAKER / imprecise. §15.3 says fan-out subagents run *"opus or sonnet, never the premium main-loop model"* and the deep-reader tasks are described as "one model tier down." Bo's explicit floor is stronger and directional: for the LESSONS/voice/audit read-sweeps specifically, the class is **OPUS** — the point of an Opus reader is contextual understanding a cheaper "fable"-class model cannot do (the very failure that seeded §17/§18: a keyword grep instead of a reading mind). "sonnet for digestion" (§15.3) undersells the read-sweep tier.
- **Bake-in:** tighten §15.3: *"For fan-out READ-sweeps — source digestion, voice/lessons audits, adversarial cold reads — the class is **OPUS**, not a cheaper 'fable'-class model (Bo, verbatim: 'not fable class!'). The whole value is contextual comprehension a grep/small-model can't provide (§17/§18 exist because a keyword mine skipped the crystallized memory). Sonnet is acceptable only for mechanical/tooling fan-out where no judgment is needed; never for reading the canon. Prose stays in the main loop."* HIGH because it directly governs how THIS class of task (a lessons read-sweep) must be run.

### C3 — The active mission is PORTABILITY (giftable one-shot kit); its status surface is a living doc the ledger doesn't point to  — ABSENT (ledger) · MED
- **Lesson (verbatim), `portability-initiative.md`:** the standing mission is *"booksmith packaged up as a portable folder self contained that can be carried over to any cc instance, given to anyone to use on their own desktop cc… IDEAL aspiration is one-shot finished."* Roadmap at `docs/PORTABILITY_GAP_ANALYSIS.md`; Wave 1 landed 2026-07-11 (gitignore private-book guard, portable hooks, `kit_env` template, `requirements.txt`, Word-COM guards, vision auto-backend, `doctor.py`, `make_giftable.py` with a CLEAN personal-data gate, OFL license vendoring, `INSTALL.md`, genericized `START_HERE`). Wave 2 = the CLAUDE.md generalization pass. **Open decisions Bo owns:** LICENSE choice, Georgia-vs-OFL default font, commit strategy, fresh-history for any public release.
- **Ledger status:** the ledger has the portability *ingredients* scattered (repo-relative fonts §11.2, `kit_env` seam per CLAUDE.md §2, vision auto-backend §6.5/§10, UTF-8 env §11.1) but NEVER frames them as one mission or points to the roadmap. A MAINTAIN-mode instance reading only the ledger would not know the giftability goal or the four open owner-decisions exist.
- **Bake-in:** add a one-line pointer at the ledger head (near the provenance block) and in §11 (cross-platform): *"Standing mission: a giftable, self-contained, one-shot-capable portable kit. Living roadmap + statuses: `docs/PORTABILITY_GAP_ANALYSIS.md` (read it in MAINTAIN mode before kit work). Open owner-decisions (Bo): LICENSE, default interior font (system-Georgia vs vendored-OFL), commit strategy, fresh-history-for-public-release. `make_giftable.py`'s CLEAN gate strips personal data before any handoff."* Turns scattered portability atoms into a named, navigable mission.

### C4 — The "read the crystallized memory, don't grep it" meta-rule is validated a SECOND time by this very audit gap  — CONFIRMATION (strong) · (reinforces §18-META)
- **Observation:** every delta in THIS file comes from memory folders the original kit build skipped — and the four prior audits, though thorough, targeted the *Titanic* memory + `C:\BOOK\BUILD_LOG.md`, leaving the **C--BOOK crystallized project memory** and the **entire C--BOOKSMITH memory** un-diffed until now. The strongest deltas here (MAINTAIN mode, OPUS-not-fable, the voice-fidelity ceiling, the portability mission) are all *process/stance* facts with zero rejection vocabulary and zero presence in the loud production layer — exactly the §16-META / §17-META / §18-META blind spot, one folder deeper.
- **Bake-in:** none new — this is live proof of the existing meta-rule. Recommend one addition to the §18-META checklist of folders to read: *"the per-project crystallized `~/.claude/projects/<slug>/memory/*.md` (project_ AND user AND MEMORY files, not only feedback_), for EVERY relevant project slug (C--BOOK, C--BOOKSMITH, C--Claude-Titanic), is part of the read-sweep — a prior sweep that stopped at one project's memory misses the process/mission layer in the others."*

---

## SUMMARY TABLE (delta → group → ledger status → bake-in → severity)

| # | Delta | Group | Ledger status | Bake-in | Sev |
|---|---|---|---|---|---|
| P1 | Halo is two-tone / contrast-adaptive per element | PRODUCTION | §6.4 one-direction only | Extend §6.4 halo note + auto luminance sample | MED |
| P2 | Byline nudged to ~2.6% bottom margin (front face) | PRODUCTION | absent | §6.4 byline anchor | LOW |
| P3 | Native 1.491:1 shipped (Kling 1.327 rejected too-square) | PRODUCTION | already in titanic-projects D6 | none (corroborates) | LOW |
| P4 | PAGES + PAD_BLANKS coupling (old approach) | PRODUCTION | STRONGER (§4.3/§5.8 supersede) | none (don't restore PAD_BLANKS) | — |
| P5 | ATD shipped 3 categories (vs canon 2) | PRODUCTION | §9.1 "≤3"; D5 wants 2 | supersede D5: picker is live/register-dependent, default to observed max, floor 2 | MED |
| P6 | Rendered-PDF math re-check pairs with F9-TOC | PRODUCTION | §3.9 DOCX-level only | add rendered-page \left/\frac vision check | MED |
| W1 | Voice fidelity has a CEILING (analytical blend accepted) | CRAFT | absent (runs against §17) | §17 calibration caveat: floors always, densities are targets not ceilings | MED |
| W2 | De-concretize is a PERMANENT standing posture + 0-proper-noun exit | CRAFT | operation in D6/D8; posture weaker | §17.2 default-abstract posture + seed forbidden_proper_nouns at ingest | MED |
| W3 | v1.1 sited review insertions at named chapters | CRAFT | same event as D4/D5 | none (corroborates) | LOW |
| C1 | MAINTAIN third session mode | PROCESS | in CLAUDE.md §1, NOT in ledger | add INIT/RESUME/MAINTAIN triad to ledger §15/§1.x | MED |
| C2 | Fan-out = OPUS, "not fable class" | PROCESS | §15.3 says "opus or sonnet" | tighten §15.3: read-sweeps are OPUS; sonnet only for mechanical fan-out | **HIGH** |
| C3 | Portability mission + roadmap pointer + 4 owner-decisions | PROCESS | ingredients scattered, unframed | ledger head + §11 pointer to PORTABILITY_GAP_ANALYSIS.md | MED |
| C4 | Read-not-grep validated again (this audit's own gap) | PROCESS | §18-META exists | add per-project memory folders to the §18-META read list | — |

**Highest-leverage first:** **C2** (OPUS-not-fable is a HARD, user-verbatim policy governing exactly this kind of read-sweep, currently under-stated as "opus or sonnet") · **P5** (resolves a live 3-vs-2 category tension the way the Previewer meta-rule resolves geometry — anchor to the live picker, don't hardcode the wrong constant) · **W1** (a genuine COUNTER-current to §17 — voice fidelity ceiling, prevents pastiche) · **C1** (MAINTAIN mode belongs in the constitution, not only the orchestrator) · **P1/P6** (two concrete production refinements: adaptive halo, rendered-math recheck). Everything else is corroboration or a calibration anchor.

*Written to disk 2026-07-12 03:15 -05:00. Sources read in full, not sampled. No number here contradicts a shipped mechanical gate; the strongest deltas are process/stance facts (MAINTAIN, OPUS-not-fable, voice-ceiling, portability mission) invisible to the production layer — the §18-META blind spot, one project-memory folder deeper than the prior four audits reached.*
