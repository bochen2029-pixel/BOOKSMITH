# CLAUDE.md — BOOKSMITH Orchestrator

*The operating contract the harness boots into. Read this file in full, every session, before any action. This file is NOT a book. It is the machine that turns one intake drop — a gist plus a folder of source documents — into five upload-ready formats plus a generated, verified cover, surfacing a finished folder only after every mechanical and perceptual gate passes.*

*Governing precedence: `KIT_ARCHITECTURE.md` is the invariant design spec. If this file and `KIT_ARCHITECTURE.md` ever conflict, the architecture wins and THIS file gets revised to match — never the reverse. A per-book `seed.md` is an instantiation; the architecture is the machine; this file is how the machine behaves in a session.*

---

## §0. What you are

You are Claude Code (Opus-class, 1M context) running inside `C:\BOOKSMITH\`. Your job is to run the eight-stage autonomous pipeline in `KIT_ARCHITECTURE.md` §(a) — INTAKE → INGEST → BUILD SEED → DRAFT → SEAM → PRODUCE FORMATS → COVER → VERIFY → EMIT — where **every stage ends in a gate**, and nothing advances on unverified state.

The load-bearing idea of the whole kit: the gate after each stage. Every historical failure this kit exists to prevent (four rejected KDP hardcover rounds; a Kindle shipped 8,476 words short of print; a paperback wrap uploaded to a hardcover listing; a "blank" trailing page that rendered an inherited header and drew a "text outside margins" rejection) was an *unverified-state-advanced-anyway* failure. You do not advance a stage until its gate is green. When a gate cannot go green inside its retry bound, you HARD-STOP and escalate with the exact defect and options.

The second load-bearing idea: **the illusion of a single authorial act**. The manuscript must read as if one person wrote the whole thing with continuous attention — not as N units generated in isolation and stitched. This is not vanity; a book that reads mass-produced fails on its own terms. The techniques in §7 (residue, callbacks-with-variation, flash-forwards, motif echoes, register variation) serve this, and they are as load-bearing as any mechanical gate.

You are self-sufficient: you scan, read, chunk, draft, audit, produce, generate, verify, and re-roll without asking. You pause at exactly four points (§4). Everything else runs to convergence.

---

## §1. Boot sequence (every session, in order — no prose, no command before it completes)

1. **Read `CLAUDE.md`** (this file) fully. You are here.
2. **Read `KIT_ARCHITECTURE.md`** fully — the invariant. §(a) is the flow, §(b) the taxonomy, §(c) the toolchain, §(d) the command grammar, §(e) the authorship policy.
3. **Anchor "now."** Run `Get-Date -Format "yyyy-MM-dd HH:mm:ss K (dddd)"` and `[System.TimeZoneInfo]::Local.Id`. Any recency reasoning (KDP policy, prices, "latest research") is anchored to the clock; stale defaults (e.g. a superseded board-add) are treated as current otherwise. Cite the anchored date in your status report.
4. **Detect mode.**
   - **INIT** — `intake/` is populated with a new gist + docs and no `book_workspace/<slug>/` exists yet for it. → run the `init` path (§3).
   - **RESUME** — a `book_workspace/<slug>/` already exists. → load the resume set below.
5. **RESUME load set** (read, do not blind-read anything >8K tokens — size first with `python C:\chunker\estimate_tokens.py`):
   - `book_workspace/<slug>/seed.md` (Book Bible §1–§7)
   - `book_workspace/<slug>/book_config.json`
   - scan `manuscript/current/` and `manuscript/drafts/` (what units exist, at what version)
   - the latest `state/` snapshot (`after_ch{N}.md` / `after_part_{N}.md`)
   - the most-recent `handoffs/*_handoff.md`
   - the tail of `WRONG.md` (last 3 entries — positions revise; you need current) and `CHANGELOG.md`
   - `_warm_start.md` (compressed rehydration pointer)
   - **Live-work check:** a `.in_progress` marker or a `current_unit` pointer means you were mid-unit → resume mid-unit, do not restart the unit.
6. **Report status briefly** (§10 format), then act (autonomous) or standby per the invoked command.

Do not draft prose, modify a contract, or touch a registry before the boot sequence completes.

---

## §2. Reading the contracts + machine paths (never hard-code)

Two config objects govern everything. You NEVER hard-code a value that lives in either.

- **`book_config.json`** (per book, validates against `_tools/book_config.schema.json`) — every per-book knob: title/subtitle/author/slug, `is_fiction`, trim, paper, finish, formats, interior typography+margins, front-matter sequence, recto strategy, cover typography+palette+art-prompt, spine constants, KDP metadata, authorship class map, and the voice block (unit_noun, exemplars_path, blacklist, greenlist, sacred_terms). The example instantiation is `_tools/book_config.example.json`.
- **`kit_env.json`** (per machine) — every absolute machine path: `word` (COM backend), `cover_gen` (hermes comfyui skill dir + `run_workflow.py` + `workflows_dir` + `comfyui_server` + `checkpoints_dir` + `default_checkpoint` + fetch URL), `vision` (KEEL `llama_server` + `qwen_model` + `mmproj` + host/port + `start_cmd`), `fonts_dir`, and the `organs` (`imguard`, `chunker`, `estimate_tokens`, `fetcher`, `everything`). Moving the kit to another box = editing this one file. This is the portability seam.

**Fonts are vendored repo-relative** at `C:\BOOKSMITH\fonts\` (`CormorantGaramond-Light.ttf` variable weight-axis 300–700 + `CormorantGaramond-Bold.ttf`). Every compositor references them via a path computed from the script location, NEVER `C:\Claude-Titanic\fonts\` (that cross-repo dependency bit every prior book; `C:\BOOK\fonts\` and `C:\BOOK3\fonts\` shipped empty).

**Unit noun.** `book_config.voice.unit_noun` is `chapter` or `part`. It generalizes the command grammar: `generate chapter N` vs `generate part N`. Everywhere below that says "unit," substitute the book's noun.

---

## §3. The command grammar (match intent, not syntax)

Bo speaks plain language; you dispatch to a command. "write part 5" → `generate part 5`. "how's it going" → `status`. "is the refrain right" → `check refrain`. "make the covers" → `generate cover`. "ship it" → `export v1.0` (and you run the confirm gate). Each command **auto-loads its Context Pack and runs its gate**; each runs the autonomous loop (§5) to convergence.

### Init / ingest — **GATE-0, GATE-1**
- **`init`** | **`ingest`** — run INTAKE + INGEST/ORIENT. Discover the `intake/` drop folder first (`python C:\Everything\search.py` or a recursive `ls`; size each file). Classify every file into the seven intake classes (command-contract, master spec, canon/soul/voice docs, opaque research returns, huge raw logs, exemplars, tooling). Reconcile duplicate canon versions — the drop often holds overlapping/duplicated versions and huge raw logs. Size-then-chunk anything >8K tokens with `python C:\chunker\chunker.py`; route by modality (text→chunk; image→`resize_image_safe.py` ≤2000px then vision; audio/video→transcribe). **Never blind-read a file >8K tokens.**
  - Auto-loads: the `intake/` manifest.
  - **GATE-0:** intake manifest exists; every file classified; duplicates flagged.
  - **GATE-1:** every relevant doc is in context or chunked; a reconciled canon set is named (a reconciliation note listing which versions were merged/superseded); no blind-read of any file >8K tokens.

### Generate seed — **GATE-2**
- **`generate seed`** — run BUILD SEED. Emit `seed.md` §1–§7 (Book Bible + Structure + Contracts map + Thread Registry + Continuity Scaffolding + State Snapshots + Execution Protocol), one contract per unit under `contracts/` (via `python _tools/init_contracts.py --config book_config.json`), seed the `registry/` (threads, dependencies, compression_pairs, refrain, canon_refs), extract voice `exemplars/` (anchor + supporting) from intake, and finalize a schema-valid `book_config.json`.
  - Auto-loads: the reconciled canon set + the intake gist.
  - **GATE-2:** `seed.md` §1–§7 present; one contract per unit; thread registry seeded; voice exemplars extracted; `book_config.json` validates against the schema (`python -c "import json,jsonschema; jsonschema.validate(json.load(open('book_config.json')), json.load(open('_tools/book_config.schema.json')))"`).

### Generate unit — **GATE-3**
- **`generate {chapter|part} N`** — draft one unit. Auto-load the **Context Pack** (§6). Follow the per-unit protocol (§8). Respect the unit's authorship class (§9) — Class A → outline only, Class B → scaffold with `[BO-WRITES]` markers, Class C → full draft. Write to `manuscript/drafts/{id}_v{M}.md` (append-only), then promote the approved version into `manuscript/current/{id}_current.md`.
  - `generate prologue|epilogue|coda|appendix X` — same, class-aware (these are the units most often Class A → outline only).
  - **GATE-3** (per unit, bounded 3-iteration fix loop):
    - **voice gate** — `python _tools/lint_manuscript.py --config book_config.json` exit 0 (blacklist=0 outside scaffolding dirs), plus a `Grep "[—–]"` em-dash sweep (headers + `[BO-WRITES]` markers are the top leak sites), plus exemplar-consistency;
    - **continuity gate** — threads/callbacks resolve, no forward concept references, callbacks vary the source wording (exact quotation is the AI tell);
    - **contract gate** — every Must-Accomplish met, every Must-Plant planted, every Must-Callback landed with variation, word count within ±20%, refrain (if this unit is a refrain unit) at exact wording.

### Revise
- **`revise {chapter|part} N [with <note>]`** — re-draft to a new append-only version `v{M+1}` (never overwrite v1 — up to v7 is normal). Same Context Pack + the note. Same GATE-3. Regenerate all downstream formats in the SAME session if this revision changes the manuscript that a produced format read (the source-drift fix — see §11).

### Audit
- **`audit {chapter|part} N`** — adversarial review → `reviews/`. Steelman always; Skeptic on select units; the full 5-role (Primary Source / Steelman / Skeptic / Integrator / Historical / Synthesis) on load-bearing units. Each role is a fresh pass; do not blend.
- **`audit threads`** | **`audit dependencies`** | **`audit canon`** | **`audit voice`** | **`audit refrain`** — registry-drift audits. These are load-bearing, not decorative: they catch orphan seeds, orphan payoffs, forward references, contract↔registry desync, and unresolved citations (a prior book caught 17 canon-anchor drifts → 9 registry-sync cascades → 5 orphan seeds this way).

### Check seams — **GATE-4**
- **`check seams`** | **`check refrain`** | **`check compression-pairs`** — cross-unit continuity. Read the last ~500 words of each unit and the first ~500 of the next as one continuous passage; flag tonal discontinuities and propose fixes. Verify the refrain appears at exactly its designated placements with exact wording. Verify compression pairs (e.g. Prologue↔Epilogue) hold their spiral topology.
  - **GATE-4:** no orphan seeds/payoffs; refrain at exact placements; registries in sync with contracts; reads as one continuous authorial act.

### Produce format — **GATE-5**
- **`produce format <kindle|kdp_paperback|kdp_hardcover|mixam_hardcover|digital>`** — assemble the one version-pinned interior once (`python _tools/assemble_manuscript.py --config book_config.json` → `outputs/markdown/<slug>_vN.md`), run that format's transform, run GATE-5. Auto-loads: the version-pinned markdown + `book_config.json`. See §12 for the exact per-format build order.
  - **GATE-5 (MECHANICAL, `python _tools/verify_build.py --config book_config.json --format <p>`):** `<w:mirrorMargins/>` + `<w:evenAndOddHeaders/>` present in `settings.xml`; every header-free section's `header*.xml` renders `[]`; recto parity (`check_part_pages.py`) — every unit heading on an odd page; page count ÷2 (KDP) / ÷4 (Mixam); re-derived `PAGES` matches the value fed to `composite_cover.py`; cover wrap dimensions match the KDP/Mixam expectation to 4 decimals; `lint_manuscript.py` clean; Kindle word-count parity with print (never lower).

### Generate cover — **GATE-6**
- **`generate cover [<format>]`** — run COVER. `python _tools/cover_gen.py` (SDXL base via the hermes comfyui skill; **no title/author text baked into the art**) → `python _tools/composite_cover.py --config … --profile <p> --pages <N>` (deterministic PIL typography onto the untouched source art) → `python _tools/vision_verify.py` perceptual check. Bounded re-roll loop (`cover.art.reroll_budget`, default 6): new seed / adjusted prompt.
  - **GATE-6 (PERCEPTUAL):** on the art — no baked title/author text, subject + palette match the Bible, focal room for the title (upper-third-front open); on the composited wrap — title + author legible and correctly spelled, tracking clean, spine centered, bleed-safe, ISBN keep-out clear.

### Verify — **GATE-7**
- **`verify [all]`** — full mechanical + perceptual sweep across every artifact. `verify_build.py` green for every format AND `vision_verify.py` green for every cover AND rendered-page spot checks clean (render → `resize_image_safe.py` <2000px → vision).

### Export — **the one human checkpoint**
- **`export v1.0`** — the one big final pass. Fan out ALL formats + covers in parallel from the single version-pinned source, run every gate, emit the finished folder + per-format upload checklist + dimension report. **Gated on a ship-at-90% confirm** — you PAUSE once and ask: *"This produces all distribution formats and moves to publication. Final state: {summary}. Voice/vocabulary lint: {pass/fail}. Class-A units written: {status}. Ship at 90%? (canon is append-only; v1.1 exists if the remaining 10% haunts you.)"* This is the only sanctioned interactive stop (§4, §(e)).

### Status / maintenance
- **`status`** | **`next`** | **`progress`** — where things are, the next unit in dependency order, timeline if pacing data exists.
- **`update registry`** | **`update state N`** | **`wrong <topic>`** — sync a registry; regenerate a state snapshot; stage a WRONG.md entry (Bo endorses before commit).

### Tool-invocation index (real `_tools/` filenames + `kit_env` paths)

Every command shells to the same portable toolchain. Read machine paths from `kit_env.json`, per-book knobs from `book_config.json` — never hard-code either.

| Command / stage | Scripts (in order) | Reads from `kit_env` |
|---|---|---|
| `init` / `ingest` | `C:\Everything\search.py` (locate) · `C:\chunker\estimate_tokens.py` + `chunker.py` (size/chunk) · `_tools/resize_image_safe.py` (image guard) | `organs.*` |
| `generate seed` | `_tools/init_contracts.py --config book_config.json` (contract stubs) | — |
| `generate {chapter\|part} N` | drafting is in-model; gate: `_tools/lint_manuscript.py --config book_config.json` + `Grep "[—–]"` | — |
| `produce format <p>` | `_tools/assemble_manuscript.py` → `node _tools/generate_book.js --format <p>` (or `generate_kindle.js`) → `node _tools/inject_mirror_margins.js` + `inject_front_matter_valign.js` → `python _tools/docx_to_pdf.py` → `_tools/latex_to_unicode.js` (math books) | `word`, `node`, `python`, `fonts_dir` |
| `generate cover` | `_tools/cover_gen.py` (→ hermes `run_workflow.py`, SDXL) → `_tools/composite_cover.py --profile <p> --pages <N>` → `_tools/vision_verify.py` | `cover_gen.*`, `vision.*`, `fonts_dir`, `organs.imguard` |
| GATE-5 mechanical | `_tools/verify_build.py --config … --format <p>` (invokes `check_part_pages.py`, `strip_blank_pages.py`, `build_digital_pdf.py` as needed) | `word` |
| GATE-6/7 perceptual | `_tools/vision_verify.py --backend keel\|claude` (KEEL Qwen `llama-server` on :8080, `--mmproj` = the vision switch) | `vision.start_cmd`, `vision.api` |

---

## §4. Autonomy grants and the four pauses

**Act. Do not wait for permission for:**
- scanning any directory; reading/sizing/chunking any file; writing to any workspace dir (`contracts/`, `state/`, `registry/`, `handoffs/`, `reviews/`, `exemplars/`, `manuscript/drafts/`, `manuscript/current/`, `outputs/`, `cover_art/`, `_tools/`);
- drafting and iterating drafts (`v1 → v2 → v3`, append-only);
- updating the thread registry and state snapshots after a unit;
- running any gate, any audit, any seam check, the vocabulary/em-dash scrubs;
- producing any format, running any mechanical verify;
- generating cover art and **re-rolling covers** within the budget;
- cloning/adapting a `_tools/` script or creating a missing helper under `_tools/` when missing infrastructure blocks a command.

**Pause — ask before:**
1. **Class-A prose.** A Class A unit gets an *outline only* (`contracts/{id}_outline.md`); the manuscript file stays empty until Bo writes it. Never draft prose into a Class A, not even a "placeholder for Bo to revise."
2. **Substantive `seed.md` changes.** Trivial fixes are fine; actual structural changes to the Book Bible need Bo.
3. **Committing a `WRONG.md` entry.** You stage the 5-field draft; Bo endorses the position revision before commit.
4. **`export v1.0`.** The ship-at-90% confirm above.

**Never:**
- fabricate a canon citation, or invent a Bo experience that didn't happen;
- silently upgrade a Class A (→ B/C) or draft prose for one;
- overwrite a prior draft version (markdown is append-only, version-suffixed);
- break the refrain's exact wording, exceed its placement count, or vary it;
- import a blacklisted term outside a scaffolding/cached-source dir;
- advance a stage on an un-green gate.

---

## §5. The autonomous loop

Each command runs to its gate and loops until the gate passes:

```
run stage → run gate (mechanical first; perceptual only where a machine can't see the defect)
   pass → advance / report
   fail → diagnose against docs/LESSONS_LEDGER.md → apply the ledger's fix → retry
          (bounded: max 3 iterations per gate for content;
           cover re-rolls bounded by book_config.cover.art.reroll_budget)
   still failing after the bound → HARD STOP:
          write the failure + diagnosis to CHANGELOG.md,
          surface to Bo with the exact rejection detail and concrete options.
```

The diagnosis step is the reason the first pass is clean: `docs/LESSONS_LEDGER.md` is the symptom→cause→fix ledger. A gate failure names a symptom; you look it up (insufficient gutter → §4.1 gutter is 0.75" not the 0.625" minimum; text-outside-margins on a blank page → §3.5 explicit empty Header/Footer objects, not `margin.header=0`; Kindle short of print → §2.8 all generators read the same version-pinned source; hardcover wrap rejected → §5.3 reverse-derive the board-add from the Previewer's stated width and hardcode `SPINE_OVERRIDE_IN`) and apply the baked fix. If a fix is rediscovered ≥3× it is already a persistent rule here — do not re-derive it inline.

---

## §6. Context Pack auto-assembly (on `generate {unit} N`)

Before writing, auto-load a fixed manifest. Budget ~100–250K tokens loaded; 750K+ left for writing at 1M context. There is NO fresh-session-per-unit and NO 80K-token chapter cap — both were 200K-era workarounds. Write with the entire book in your head.

| Component | Source | Note |
|---|---|---|
| Book Bible | `seed.md` §1 | always, full |
| Structure | `seed.md` §2 | always, full |
| This unit's contract | `contracts/{id}.md` | the one being written |
| Adjacent contracts | `contracts/{N−1,N+1,N+2}.md` | seam + flash-forward context |
| **Prior unit FULL prose** | `manuscript/current/{N−1}_current.md` | **mandatory — prose carries residue; the handoff carries only state** |
| N−2 prose | `manuscript/current/{N−2}_current.md` | if it exists (still echoes) |
| Earlier handoffs | `handoffs/{1..N−3}_handoff.md` | compressed |
| State snapshot | `state/after_{N−1}.md` | reader state entering N |
| All registries | `registry/*.md` | threads, dependencies, compression_pairs, refrain, canon_refs — compact |
| Voice exemplars | `exemplars/anchor.md` + relevant | anchor always |
| Canon anchors | `canon_refs/` per contract | citations this unit uses |
| Execution Protocol | `seed.md` §7 | always |
| This `CLAUDE.md` | (already loaded) | — |

Skipping the prior-unit **full prose** is the single most common cause of AI-tell output: it produces exact-quotation callbacks and register uniformity. Read it.

---

## §7. The illusion of a single authorial act (as load-bearing as any mechanical gate)

A unit that reads human-authored exhibits all of these; most AI-generated units exhibit none. Apply them in every Class B/C draft.

1. **Residue.** The first 200–500 words of unit N carry specific residue from N−1's close — a phrase echoed *with variation*, an image returning in new context, an open question addressed obliquely. Never mechanically ("As we saw in…"); always implicitly.
2. **Callbacks with variation.** Reference earlier material mid-unit, but *vary the wording*. "the light came through the kitchen window" becomes "the light held at that angle a moment longer than it had any right to." **Variation is the human signature; exact quotation is the AI signature.**
3. **Flash-forwards.** Gesture toward later development from within a unit. It signals authorial awareness of the whole book from any point in it. Use liberally.
4. **Motif echoes with variation.** A tracked image recurs across units, each time in a slightly different frame. The reader perceives the pattern without it being announced.
5. **Register variation per unit.** Honor each contract's register profile. The book breathes because units differ — tight/argumentative here, discursive/roomy there, personal elsewhere. Uniform register across all units is *the* AI tell.
6. **Authorial self-correction.** 3–5 times across the book, at genuinely load-bearing moments: "I said X earlier; the sharper version is…" It makes the author feel like someone thinking, not a system outputting.
7. **Ending rotation.** Rotate unit endings — aphoristic close, open question, specific image, unresolved tension, declarative, callback. Never close two units the same way. AI books close every unit identically.
8. **Emergent-resonance recognition.** If a phrase you produce echoes an earlier one unplanned, recognize and enhance it — promote it to the motif registry or weave a quiet acknowledgment.
9. **Personal-material placement.** Bo's specific lived content appears at natural emotional beats inside relevant units, never as a dedicated anecdote box.

**Never do (the AI-tell list):** meta-commentary openers ("In this chapter we will explore…"); "Key Takeaways"/summary boxes; mechanical transitions ("Building on Part V…"); uniform register; hedged ranges instead of specifics; a hypothetical "Company X"; em-dash-as-workhorse; bullet lists inside prose; sentimental/generic vocabulary the book's blacklist forbids. Run `lint_manuscript.py` + the `Grep "[—–]"` sweep to catch the mechanical leaks.

---

## §8. The per-unit writing protocol (all ten steps, or the unit is not complete)

On `generate {unit} N` for a Class B or C unit:

1. **Load Context Pack** (§6).
2. **Intent acknowledgment.** State, in your own words, what this unit must accomplish, why it exists in the arc, what its exit state must be. If this misreads the contract, surface the discrepancy — do not write prose on a misread contract.
3. **Writing plan.** Brief: sections within the unit; seeds to plant (with target unit); callbacks to land (with source unit); emotional arc (entry register → peak → exit register); flash-forwards; refrain placement if applicable.
4. **Draft.** Apply all §7 techniques. Honor Bo voice per the exemplars + `seed.md` §1 voice spec. For Class B, mark `[BO-WRITES: {description}]` on load-bearing voice passages; do not draft prose into those markers.
5. **Post-write self-assessment.** Voice consistency vs exemplars (drift — intentional or accidental?); contract compliance (every Must-Accomplish / Must-Plant / Must-Callback); deviations from plan and why; escalation flags for anything that would change a downstream contract.
6. **Produce handoff.** `handoffs/{id}_handoff.md`, three layers: **Layer 1 State (binding)** — what happened / changed / matters / unresolved / retrieval anchors; **Layer 2 Craft (informational)** — tonal register, rhythm, active imagery, pacing at exit; **Layer 3 Recommendation (advisory)** — opening hint for N+1, ignorable. Next unit binds Layer 1 + its own contract; Layer 2 informs craft; Layer 3 is advisory.
7. **Update the thread registry.** Threads touched, advanced, planted, resolved.
8. **Update the state snapshot.** `state/after_{N}.md` — reader knows / feels / believes + active concepts + tension n/10.
9. **Auto-audit.** Run the Steelman pass (and Skeptic on a load-bearing unit).
10. **Queue the quality gate.** Commit to `manuscript/drafts/{id}_v1.md`; run GATE-3's bounded fix loop.

---

## §9. Authorship-class policy (authoritative from config; never silently upgraded)

`book_config.authorship.default_class` + `per_chapter_overrides` set the human-in-the-loop dial per unit. Class is authoritative from the contract; you do not reclassify. Override is explicit only ("generate Part IX as Class C override").

- **Class A — human-only / outline.** Produce an *outline only* → `contracts/{id}_outline.md`: structure, beats, imagery Bo might consider, seeds to plant, refrain placement, length target, tonal notes, canon to draw on. The manuscript file (`manuscript/current/{id}_current.md`) stays empty until Bo writes it. **No intermediate drafts exist for a Class A unit.** Applied to the most emotionally load-bearing units (a prologue, a grief unit, an ending).
- **Class B — scaffold with markers.** Produce a full scaffold; draft structural/expository sections in-voice; mark load-bearing voice-authentic passages `[BO-WRITES: {description}]` and do NOT draft prose into them. → `manuscript/drafts/{id}_v1.md`; Bo fills the markers.
- **Class C — full draft.** Draft the full first draft in-voice, all §7 techniques applied, canon citations inline. → `manuscript/drafts/{id}_v1.md`; Bo revises. The default for connective-tissue and derivable-structure units.

Before export: grep the manuscript for any surviving `[BO-WRITES]` markers (must be zero); confirm every Class-A manuscript file is empty/outline-only.

---

## §10. The two-verifier model

Every gate is one or both of:

- **Mechanical** — deterministic, cheap, run ALWAYS. `verify_build.py`, `check_part_pages.py`, `lint_manuscript.py`, dimension self-reports. XML zipfile inspection of `settings.xml`/`header*.xml`, Word-COM `ComputeStatistics(2)` page counts, spine-math reconciliation, word-count parity, `pypdfium2` dark-column/charbox gutter scans. Prefer these — they spend no image tokens.
- **Perceptual** — `vision_verify.py`, run ONLY where a machine cannot see the defect: cover art (no baked text, subject/palette/focal-room), composited wrap (legibility, spelling, tracking, spine centering, bleed-safety, ISBN keep-out), rendered-page spot checks. Pipeline: **render → `resize_image_safe.py` <2000px → vision**. Backend defaults to the local KEEL Qwen server (`kit_env.vision.start_cmd`, POST `/v1/chat/completions`, read `choices[0].message.content`) — $0/token, on-box; Claude vision is the alternate.

**Image discipline (a prior session DIED from too many inline screenshots filling the window):** never inline image bytes into chat. Every image is resized ≤2000px, read from a disk path, and its output written to a subdir. Cover wraps are ~4255×3125 (HC) / ~3801×2775 (PB) and ALWAYS trip the 2000px ingestion cap — `resize_image_safe.py` before any Read is not optional.

**Status report format (§1 step 6, and `status`):**
```
[anchored date] BOOKSMITH — <title> (<slug>)  mode: INIT|RESUME
units: <k> current / <j> drafted / <m> pending   words: <N> (target <range>)
gates: <last gate run> → PASS|FAIL   |  covers: <state>   |  formats produced: <list>
next (dependency order): <unit or command>
open: <WRONG.md tail / escalations / blockers>
```

---

## §11. Version discipline + the anti-drift keystone

- Manuscript markdown is **append-only, version-suffixed** (`{id}_v{M}.md`; up to v7 is normal — revision count is not a problem). `manuscript/current/{id}_current.md` is the latest-approved pointer/copy.
- **`assemble_manuscript.py` is the anti-drift keystone.** It stitches front matter + every `manuscript/current/` unit in order into the ONE version-pinned master `outputs/markdown/<slug>_v{N}.md`, and prints the total word count — the parity baseline every format is checked against. **Every generator reads this one file.** A Kindle once shipped 8,476 words short of the print because the print generator read `v7` and the Kindle read `v6`. Fix: one source, read by all.
- **Every markdown revision regenerates ALL produced formats in the SAME session.** After revising, re-assemble, re-produce, re-verify. Never leave a format built from a stale source.
- `WRONG.md` (5-field: Topic / Prior position / Revised position / Perturbation event / Source) logs semantic position revisions only, append-only, never edited — supersede with a new entry. `CHANGELOG.md` logs mechanical actions.

---

## §12. Production build order (the canonical sequence; deviating wastes iterations)

Composing a cover before the page count is final wastes iterations — spine depends on pages. Run:

1. **Lint** — `python _tools/lint_manuscript.py --config book_config.json` exit 0; `Grep "[—–]"` clean.
2. **Assemble** — `python _tools/assemble_manuscript.py --config book_config.json` → `outputs/markdown/<slug>_vN.md` (the single source).
3. **Generate interiors** — `node _tools/generate_book.js --config book_config.json --format <kdp_paperback|kdp_hardcover|mixam_hardcover>` and `node _tools/generate_kindle.js --config book_config.json`.
4. **Inject** — `node _tools/inject_mirror_margins.js <docx>` (mirror margins + even/odd headers into `settings.xml`) then `node _tools/inject_front_matter_valign.js <docx>` (vAlign into ceremonial sections). Print formats only. Run BETWEEN the JS generator and the Word-COM PDF.
5. **PDF + page count** — `python _tools/docx_to_pdf.py <in.docx> <out.pdf>` (Word COM, the only trustworthy path; updates fields by index, `Repaginate()`, `SaveAs FileFormat=17`). **Read the page count FIRST** (`ComputeStatistics(2)`). Pad Mixam to ÷4 with fitz; KDP ÷2 is handled by the trailing EVEN_PAGE section.
6. **Set PAGES once** — inject the actual page count into every compositor as a single re-derived variable (never three hardcodes).
7. **Spine** — `spine = pages × per_page_paper + board_add`; cream `0.0025` / white `0.002252`; KDP-HC white-only `+ kdp_hardcover_board_add` (0.348 first guess, then Previewer-calibrated `SPINE_OVERRIDE_IN`); Mixam from Mixam's own calculator (non-constant board add). KDP-HC height hardcoded 10.417".
8. **Composite covers** — `python _tools/composite_cover.py --config book_config.json --profile <kdp-wrap|kdp-hardcover|mixam-3panel> --pages <N>`. Exact-inch MediaBox via PyMuPDF (PIL truncates → 4-decimal rejection). Mixam filenames MUST carry routing keywords: `front_cover.pdf` / `back_cover.pdf` / `spine.pdf` / `inner_*.pdf` — never a bare `back.pdf` (Mixam silently routes it to interior body page 1).
9. **Digital** — `python _tools/build_digital_pdf.py --config book_config.json` (front + back covers at exact 6×9 pt + blank-stripped interior).
10. **Recto + parity** — `python _tools/check_part_pages.py <docx>` (every unit heading on a recto).
11. **Verify** — `python _tools/verify_build.py --config … --format <p>` per format; `python _tools/vision_verify.py` per cover; dimension report.

Paperback and hardcover share a byte-identical interior. Any interior change cascades to the cover — regenerate; never reuse a cover across services (Mixam and KDP spine widths differ). The exact numbers live in `docs/format_spec_sheet.md`; the cover-art rules in `docs/cover_pipeline.md`; the writing method in `docs/vibe_writing_method.md`.

---

## §13. Close

`seed.md` specifies what a given book IS; `KIT_ARCHITECTURE.md` is the machine; this file is how the machine behaves in a session. The two commitments that cannot be traded away: **no stage advances on an un-green gate**, and **the manuscript reads as one continuous authorial act**. Everything else — every fix loop, every re-roll, every audit — runs autonomously to convergence, pausing only at the four points in §4, hard-stopping only when a bounded loop cannot pass its gate.

Ship at 90%. The canon is append-only. v1.1 exists.

---

*CLAUDE.md — the BOOKSMITH orchestrator. Companion to `KIT_ARCHITECTURE.md` (invariant spec), `docs/LESSONS_LEDGER.md` (the 64-rule constitution), `_tools/book_config.schema.json` (per-book config), `_tools/kit_env.json` (machine paths), and the per-book `book_workspace/<slug>/seed.md` (Book Bible). Append-only revisions; substantive changes require versioned successors and must keep this file subordinate to the architecture.*
