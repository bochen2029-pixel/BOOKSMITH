# BOOKSMITH — The Ambition & The Roadmap

*Written 2026-07-12. The most ambitious version of what this kit can become, and the
detailed path there. Grounded in what already exists on `main` (the deterministic
engine, the keyless harness bridge, the gate architecture, the cover catalog) so
every moonshot below is a credible extension of a working machine, not a wish.*

*This is a living document. It is subordinate to `KIT_ARCHITECTURE.md` (the invariant
spec) and `CLAUDE.md` (the session contract); where it proposes change, that change
must keep the two invariants in §1 true.*

---

## 0 · The North Star

**A single sentence becomes a finished, verified, distributed, and marketed book —
on any machine, with any capable model, under any agentic harness, with the quality
of a skilled human author working with continuous attention — and the machine gets
measurably better with every book it makes.**

The endgame is not "a tool that helps write books." It is an **autonomous creative
production system** whose book-making is the first, best-proven instantiation of a
domain-general engine: *deterministic code holds the plan and the gates; the model is
a pure function; the disk is the memory; quality is enforced, not hoped for.*

---

## 1 · The two invariants (these never change, at any horizon)

Everything below is negotiable except these. They are the reason the kit works and
the constraint every future feature must satisfy.

1. **No stage advances on an un-green gate.** Every requirement is bound to a
   mechanical or perceptual check that fails loudly if skipped. Ambition never buys
   its way past a gate; it buys *more and better gates*.
2. **The manuscript reads as one continuous authorial act.** Residue, callbacks-with-
   variation, register variation, earned peaks, ending rotation. A book that reads
   mass-produced has failed on its own terms, no matter how automated its production.

A corollary the session proved and that now joins them in practice:

3. **Control is inverted: the engine (code) holds sequence/state/discipline on disk;
   the model is a pure, stateless function.** Sessions drift and compact; code and
   disk do not. Every new capability is a new deterministic stage or a new gate, not
   a new thing the model must "remember to do."

---

## 2 · The foundation we can build on (honest inventory, 2026-07-12)

What exists today, verified green, is the platform. The roadmap is what we hang on it.

- **The engine** (`_tools/engine.py`) — deterministic state machine: `precheck → draft:<unit>* → integrate → assemble → produce:<format>* → cover → verify → emit`. Owns state in `_engine/state.json` (hash-keyed; a stage is done only if inputs match AND outputs exist). Bounded retry, structured hard-stop, crash/compaction resume with zero orientation. **Proven on a real 13-chapter book.**
- **The pure-function model seam** (`_tools/model_client.py`) — backends `anthropic | openai | mock | harness`. The **harness bridge** gets prose from the Claude Code session itself, keyless, via a disk handshake. **Proven: a real book authored in-session with no API key.**
- **The gate architecture** — `verify_build.py` (mirror margins, recto parity, page divisibility, spine/wrap dims to 4 decimals, page-count parity, min-pages floor), `lint_manuscript.py` (hard em-dash gate + blacklist + corruption + config-field scan), `check_part_pages.py`, `check_gutter_side()`, `vision_verify.py` (perceptual), and `selfcheck.py` (the kit's meta-gate on itself).
- **Nine publishing formats** — Kindle, EPUB, KDP paperback/hardcover, Mixam paperback/hardcover, Blurb paperback/hardcover, digital PDF — one byte-identical version-pinned source, read by all.
- **Portability** — `autoconfig.py` writes a machine-correct `kit_env.json`; vendored fonts + ComfyUI client + weight fetcher; keyless defaults; first-run onboarding hook.
- **Cover system** — bespoke SDXL (`cover_gen`), the **hypergen** pure-code abstract generator (any machine, no GPU), and a **24-image prerendered catalog** with tag/mood matching (`cover_pick`), behind a pluggable art-source seam.
- **Voice** — `voice_elicit.py` bootstraps an operator's voice from their own prose; the em-dash gate and blacklist are per-operator config.
- **The anti-forgetting layer** — `LESSONS_LEDGER.md` (§1–§19), `SUPERSTRUCTURE.md` (the wiring + anti-forgetting matrix), the compaction-survival machinery.

**The gap between here and the North Star is the roadmap.**

---

## 3 · HORIZON 1 — Perfect the Autonomous One-Shot

*Theme: close the loop from "drop a gist + docs" to "a finished folder," fully
deterministic, with quality gates that make the output indistinguishable from a
careful human author's. Everything here is buildable now with the current stack.*

### 1.1 Complete the engine: INGEST + SEED as code (`engine.py` extension)
Today the engine drives DRAFT→EMIT and assumes a `seed.md` + contracts exist. The
true one-shot needs the creative-architecting front half as deterministic stages that
call the model as a pure function.
- **`stage_ingest`** — discover `intake/`, size + classify every file (the seven intake classes), reconcile duplicate canon, skim-then-delegate topology, produce relational digests. Gate: GATE-1 (every doc in context or chunked; core identified; digests relational; `integration_mode` declared).
- **`stage_seed`** — synthesize `seed.md` §1–§7, per-unit contracts, thread registry, voice exemplars, a schema-valid `book_config.json`. Gate: GATE-2 (schema-valid, voice canon loaded, one contract per unit).
- **Deliverable:** `python engine.py --config <new-book>` runs INTAKE→EMIT end to end. **DoD:** a fresh small book from a one-line gist + a folder of PDFs to a verified folder, zero mid-flight human input, on the harness backend.

### 1.2 The Manuscript Ingest converter (`manuscript_ingest.py`)
Real operators drop PDFs/DOCX/EPUB on day one. Convert any source → clean markdown into `intake/converted/` (PyMuPDF for PDF, zipfile-XML for DOCX, zipfile+HTML-strip for EPUB). **DoD:** drop a mixed folder of formats, get uniform markdown the ingest stage reads.

### 1.3 Quality Gates 2.0 — mechanize "the single authorial act"
The most ambitious near-term work: make invariant #2 *enforced*, not disciplinary.
- **`authorial_act.py`** — a scoring gate over the assembled manuscript: AI-tell density (meta-openers, "key takeaways", mechanical transitions), **register-uniformity detector** (sentence-length + lexical-diversity variance across units — uniform register = fail), **callback-exactness detector** (a callback that quotes its source verbatim instead of varying it = the AI signature = flag), motif-echo tracking, ending-rotation check (no two units end the same way).
- **The earned-peak gate** — pre-designate 1–2 lift hinges per book; verify the emotional curve is not flat (proxy: imagery density + sentence-rhythm modulation at the designated beats), and that peaks are *earned* (built to, not sprung).
- **Adversarial quality panel** — a multi-agent workflow (fan-out) that reads the manuscript from N distinct lenses (continuity, voice-consistency, does-it-move-the-reader, is-anything-generic) and must reach consensus before EMIT. Findings feed a bounded revision loop.
- **DoD:** a manuscript that passes GATE-3/4 today but *reads* mass-produced now fails a mechanical or perceptual gate.

### 1.4 Cover System 2.0
- **Portrait SDXL workflow** (832×1216) as a catalog variant; typography-aware composition (train the negative prompt + a vision feedback loop so the title zone stays clean).
- **Catalog to 100+** — expand the genre×mood matrix; add a **palette-transfer** pass (recolor a chosen catalog image to the book's exact palette via LAB histogram matching, so any catalog image can serve any palette).
- **Typography auto-layout with a vision loop** — `composite_cover` proposes N title layouts; `vision_verify` scores legibility/balance/tracking; pick the best. Close the loop the way the prose gates do.
- **DoD:** on a no-GPU machine, a book gets a cover a stranger would believe a designer made.

### 1.5 Distribution automation
- **`publish_kdp.py` / `publish_ingram.py`** — browser automation (via the harness's Chrome control) that fills the KDP/IngramSpark upload forms from `book_config.json` + the produced files: metadata, categories, keywords, pricing, the interior + wrap. Human confirms the final "publish" click (the one sanctioned outward-facing pause).
- **DoD:** from a verified folder to a KDP draft listing with everything filled, one human click from live.

### 1.6 Onboarding + Autoconfig 2.0
- The **"just say hi" playbook** (`docs/onboarding_playbook.md`): three doors (I have docs / I have an idea / help me decide), react-don't-specify, a conversation→intake compiler, a sufficiency rubric, an assumptions ledger, anti-pattern never-list, test personas.
- Autoconfig: probe the real ComfyUI port (`:8000` desktop / `:8188` portable), detect the model backend the operator has (key present? local server up?), Mac/Linux tier detection.
- **Tier-2 print fallback** — `docx_to_pdf.py` LibreOffice branch (`soffice --headless --convert-to pdf`) + `verify_build` page-count/recto checks from the rendered PDF via PyMuPDF when Word is absent. Unlocks print on Mac/Linux.

### 1.7 The graduation exam (measured)
One true one-shot, instrumented: fresh small book, intake→finished folder, zero mid-flight help; every stumble becomes a new ledger rule and a new gate. **"One-shot finished" becomes a demonstrated, repeatable property with a pass/fail number.**

---

## 4 · HORIZON 2 — The Self-Improving Publishing Studio

*Theme: the kit stops being a book *compiler* and becomes a *studio* — it markets,
learns, manages series and multiple authors, and improves itself. Each item assumes
Horizon 1's autonomous one-shot as the primitive it composes.*

### 2.1 REFORGE — rebirth of existing books
A fifth entry mode: drop a finished/half-finished manuscript → decompose → interview intent (what's wrong, what you wish it were, who it's for now, sacred passages, real vs changed names) → mirror-back diagnosis → **re-synthesize from first principles in the author's register at full altitude** (re-derive, never line-edit). Gates: mechanical "nothing lost unintentionally" (claim/scene inventory → coverage map → consciously-dropped list) + perceptual better-than-sum.

### 2.2 The Marketing Engine
From the finished book, autonomously produce: back-cover blurb, Amazon A+ copy, ad variants, a launch-week social calendar, a reader-magnet sample, category+keyword research (market-gap analysis). **A/B cover testing**: generate cover variants, score them with a vision panel *and* (later) real click data. Every marketing artifact passes the same voice + no-em-dash gates as the prose.

### 2.3 The Analytics & Iteration Loop
Ingest sales, reviews, and read-through data → diagnose (where do readers drop, what do reviews complain about) → propose a `v1.1` (targeted revision) or a `v2` (REFORGE). The canon is append-only; the studio ships successors, never edits-in-place. **The book becomes a product that improves after launch.**

### 2.4 Voice Studio
- Multi-sample voice modeling: many samples → a rich fingerprint (rhythm, lexicon, syntactic tics, register range, the operator's actual em-dash/semicolon habits).
- **Voice-blending** — "write it in my voice but with X's structural discipline."
- A **taste model**: log every operator choice (which cover, which draft, which phrasing) and learn their preferences, so the studio's defaults converge on *their* taste over time.

### 2.5 Series & Universe management
Shared canon across books: a universe-level thread registry, cross-book continuity gates, character/term consistency across a series, and a "next book in the series" generator that inherits the universe. **The studio manages a bibliography, not a book.**

### 2.6 The self-growing anti-forgetting layer
Every gate failure anywhere becomes a candidate lesson: symptom → cause → fix, auto-drafted into a staging area, curated (human-endorsed) into `LESSONS_LEDGER.md`, and — the key move — **auto-bound to a new gate** so it can never recur. The kit's own audit→fix→verify loop (the one this session ran by hand) becomes a scheduled, autonomous maintenance workflow. `selfcheck.py` grows teeth: it blocks a commit that would regress any invariant.

### 2.7 Multi-harness & multi-model (run anywhere, on anything)
- **`AGENTS.md` + `docs/harness_profiles/`** — the cross-harness front door. Profiles for Claude Code (hooks, jsonl transcripts, the Agent tool), OpenCode (storage, JS plugins, session hooks), Cursor, and a **generic re-derivation protocol** for unknown harnesses (emit a nonce → content-search the disk for the session record → reverse-engineer its format → tier to budget). Boot step 0: identify harness → load profile → else generic.
- **Model-floor honesty + ensemble drafting** — a model-tier probe (write a test paragraph, self-grade against exemplars); on weaker models the gates still hold and voice degrades *gracefully, not silently*; on strong models, optional ensemble drafting (N drafts → judge panel → synthesize) for the highest-stakes units.

---

## 5 · HORIZON 3 — The Creative Production OS (the moonshot)

*Theme: the engine was never really about books. Control-inversion + gates + disk +
pure-function-model is a domain-general recipe for producing any long-form, high-
structure creative artifact. Books proved it. Now generalize.*

### 3.1 The domain-general engine
Abstract the engine's book-specific stages behind a **production schema**: a domain
declares its units, its gates, its produce-targets, its "single authorial act"
criteria. Books are `domains/book/`. New domains:
- **`domains/course/`** — a structured course (modules → lessons → exercises → assessments), produced to SCORM/PDF/video-script.
- **`domains/screenplay/`** — beats → scenes → drafts, produced to Final Draft / Fountain, gated on format + structure + voice.
- **`domains/documentary/`** — research → outline → script → shot list → narration.
- **`domains/album/`** — concept → tracklist → lyrics → liner notes (+ cover via the same catalog engine).
- **`domains/game_narrative/`** — world bible → branching quests → dialogue trees, gated on graph-consistency (no orphan branches — the same orphan-seed gate, generalized).
The invariants and the engine are unchanged; only the schema differs. **The kit becomes a platform.**

### 3.2 The Studio Swarm
A fleet of specialized, deterministically-orchestrated agents — researcher, architect,
drafter, continuity-editor, adversarial critic, illustrator, marketer, distributor,
analyst — composed by the engine (not by a model's discretion). The engine is the
conductor; the swarm is the orchestra; every hand-off is a gated artifact on disk.
This is the current workflow-orchestration pattern, made permanent and domain-general.

### 3.3 The self-authoring kit
The kit runs its own perfection loop autonomously: a scheduled agent audits the
codebase against the invariants, opens fixes on a branch, verifies with `selfcheck`
+ the smoke tests, and proposes the merge — the exact loop this session ran by hand,
now a standing capability. **The machine maintains the machine.**

### 3.4 The taste frontier — indistinguishable-from-human, then better
- **Blind-panel evaluation** — a standing protocol where human readers (and adversarial model judges) blind-compare kit output against skilled-human baselines; the target is >50% "prefer the kit" on literary quality, not just correctness.
- A **learned taste model** trained on accumulated human endorsements across all operators (privacy-scoped), raising the floor of every default.
- The **"emergent-resonance" engine** — mechanize invariant #2's step 8: detect when a phrase unplanned-ly echoes an earlier one, and *promote* it to a motif. The book develops its own internal rhymes.

### 3.5 The full economic loop
Ideation from real market gaps → autonomous production → distribution → marketing →
sales → reinvestment into the next title. A **publishing business that runs itself**,
with the human as the taste-setter and the one who clicks "publish." Every step gated;
nothing outward-facing happens without the sanctioned human confirm.

---

## 6 · Cross-cutting workstreams (run continuously across all horizons)

- **Portability** — every feature ships with its portable fallback; the folder-copy always works; no feature may hard-require the reference machine.
- **The gate discipline** — every new capability lands with its gate in the same commit. No un-held nodes (the SUPERSTRUCTURE "no gaps" rule).
- **The anti-forgetting layer** — every lesson learned becomes a rule *and* a gate.
- **Security & consent** — outward-facing actions (publish, post, spend) always pause for the human; drive-wide discovery is consent-scoped; secrets never enter git or a command string.
- **Provenance & licensing** — generated art + fonts + model weights carry a clear commercial-use story (SDXL-base permissive; never a non-commercial checkpoint as default).

---

## 7 · Definition of Done, per horizon

- **H1 done:** a stranger folder-copies the kit to a fresh Win11+GPU box, says "hi," drops a gist + a folder of PDFs, and gets a verified nine-format folder + a cover a designer would sign — with zero mid-flight help, keyless, and the manuscript passes the mechanized single-authorial-act gates.
- **H2 done:** the same stranger's book comes with its marketing kit, a filled KDP draft one click from live, and a `v1.1` proposed from its first reviews — and the kit runs on their non-Claude-Code harness too.
- **H3 done:** the engine produces a non-book artifact (a course) through the same gates; a blind panel prefers the kit's literary output to a skilled-human baseline more than half the time; and the kit has merged an improvement to itself, autonomously.

---

## 8 · Risks & mitigations

- **Quality plateau / uncanny sameness** → the mechanized authorial-act gates + adversarial panels + the taste model are the direct countermeasure; treat "reads mass-produced" as a build failure.
- **Model/harness lock-in** → the pure-function seam + harness profiles + model-floor honesty keep it portable by construction.
- **Automation overreach** (publishing/spending without consent) → the single sanctioned outward-facing pause is inviolable; gate every irreversible act.
- **Repo/artifact bloat** → images and weights stay on disk / in the giftable, out of git history; catalog ships as curated subset + manifest.
- **Scope sprawl** → horizons are ordered; nothing in H2 starts until H1's one-shot is a demonstrated, measured property.

---

## 9 · The immediate next actions (concrete, ordered — start here)

1. **`engine.py` INGEST+SEED stages** (§1.1) — the single highest-leverage move; it makes the one-shot *whole*. Start with `stage_seed` (seed+contracts+config from a reconciled canon), then `stage_ingest`. **[STARTED 2026-07-12 — landed in `engine.py` as the ARCHITECT preamble: `stage_seed` turns a `brief.md` (+ digests) into `seed.md` §1–§7 + per-unit contracts + a schema-valid `book_config.json` (GATE-2); `stage_ingest` turns `intake/` docs into relational digests + a manifest (GATE-1); the model stays a pure function and the keyless architect turn is wired to the harness disk-bridge. `engine_smoketest.py` scenarios F/G/H are green and `selfcheck` PASSes. Remaining refinements: model-filled contract bodies (not just stubs), chunking for large source docs, and the harness bridge for per-source `ingest` digests.]**
2. **`manuscript_ingest.py`** (§1.2) — small, unblocks real users' day-one PDFs. **[DONE 2026-07-12 — `_tools/manuscript_ingest.py` converts PDF (PyMuPDF) / DOCX / EPUB / HTML -> clean markdown into `intake/converted/`, wired into the engine's `stage_ingest` (docs normalized before digesting; `converted/` excluded from the ingest input-hash for idempotency); `--selftest` (docx+epub+html) + the fitz PDF path verified; smoketest scenario G converts an `.html` source through the engine. `selfcheck` PASS.]**
3. **`authorial_act.py` v1** (§1.3) — the register-uniformity + callback-exactness detectors first; they are the most mechanizable and the highest-quality-leverage. **[DONE 2026-07-12 — `_tools/authorial_act.py`: 5 detectors (register-uniformity + verbatim callback-exactness [both high] + meta-openers + summary-boxes + ending-repetition), a scoring gate with `--json`/`--strict` and a `--selftest` proving it passes a varied book and fails a uniform/verbatim one. Wired into the engine's integrate stage as an advisory (verdict logged); opt-in hard-fail via `authorship.quality_gate`. Validated: the engine-written proof book passes with score 0.]**
4. **Autoconfig port probe + Tier-2 LibreOffice** (§1.6) — closes the last portability gaps (the `:8000` finding; Mac/Linux print). **[DONE 2026-07-12 — autoconfig PROBES a live ComfyUI on :8000 (desktop) and :8188 (portable) and pins the reachable one; `docx_to_pdf` gained a Tier-2 LibreOffice fallback (`soffice --headless --convert-to pdf`; page/word counts read back via PyMuPDF) used only when Word COM is absent, with a `renderer` tag in its JSON; `build_digital_pdf` updated for the new return. Word path re-verified here (renderer=word, 6pp); LibreOffice branch builds + detects gracefully; autoconfig now reports Tier-2 print availability when LibreOffice is found.]**
5. **`publish_kdp.py` skeleton** (§1.5) — metadata + file upload via harness browser control, stopping before the publish click.
6. **Cover 2.0 palette-transfer + typography vision loop** (§1.4) — makes every catalog image serve every book. **[PARTIAL 2026-07-12 — palette-transfer DONE: `_tools/palette_transfer.py` recolours any catalog/hypergen cover image to a book's exact `cover.palette` via Reinhard mean/std transfer in CIELAB (pure Pillow, no numpy; clamped per-channel scale + a `--strength` blend keep it tasteful and preserve structure / the calm title zone). `--selftest` (cool->warm move + structure preserved) + a real catalog recolour verified. TODO: wire into `cover_pick.py` (recolour the chosen image before install) + the typography auto-layout vision loop.]**
7. **The graduation exam, instrumented** (§1.7) — run it, turn every stumble into a ledger rule + a gate.
8. **`AGENTS.md` + `harness_profiles/generic.md`** (§2.7) — the first step off single-harness. **[DONE 2026-07-12 — `AGENTS.md` (root cross-harness front door) + `docs/harness_profiles/{generic,claude_code,opencode,cursor}.md`; `_tools/harness_detect.py` makes it EXECUTABLE: `--identify` detects the harness by markers/env and names its profile, `--find-transcript --nonce` implements the nonce protocol (content-search the session-store roots for a nonce you emit -> your transcript) so compaction-survival rehydration works on an unknown harness. `--selftest` (identify + nonce finder; binaries skipped; absent-nonce empty) verified; identifies claude_code here. selfcheck PASS.]**
9. **Self-growing ledger staging** (§2.6) — auto-draft lessons from gate failures into a staging file for human endorsement. **[DONE 2026-07-12 — `_tools/ledger_stage.py` harvests every engine hard-stop (`_engine/HARDSTOP.json` + HARDSTOP events in `_engine/log.jsonl`) across workspaces, de-dupes by a normalized (stage, detail) key, and drafts symptom -> cause -> fix -> proposed-gate PROPOSED blocks into `docs/_lessons_staging.md` (gitignored scratch) for human endorsement into `docs/LESSONS_LEDGER.md`. It never edits the ledger itself (curation stays human, §4 pause). Idempotent; `--selftest` + a real scan (harvested this session's 5 hard-stops incl. the two one-shot bugs) verified.]**
10. **The domain schema spike** (§3.1) — prove the engine is domain-general by scaffolding `domains/course/` behind the same gates.

---

*The kit already does the impossible thing — it turns one intake drop into nine
verified formats and a real cover, deterministically, keyless, resumable. The roadmap
is not about making it do more tricks. It is about closing the loop (H1), teaching it
to learn and sell and run anywhere (H2), and revealing that the book-engine was a
creative-production OS all along (H3) — while never once trading away the two
invariants that make any of it worth reading.*

*Ship at 90%. The canon is append-only. v1.1 exists. And the next book is always
one command away.*
