# BOOKSMITH — First-Session Initialization Prompt

*Paste the whole of this file (or just: "Read START_HERE.md in full and follow it exactly") as the first message of a new session started inside the BOOKSMITH folder. Then do nothing else until you have completed Step 1 and Step 2.*

---

You are booting a fresh session inside the BOOKSMITH kit — a portable, self-contained "vibe book-writing" kit that turns a gist plus a folder of source documents into **nine upload-ready book formats** (Kindle DOCX, EPUB 3, KDP paperback, KDP hardcover, Mixam paperback, Mixam hardcover, Blurb trade paperback, Blurb ImageWrap hardcover, digital PDF) plus a generated, vision-verified cover. Work through the steps below in order before doing anything else.

## 0 — Environment
- **First run on this machine?** Run `python _tools/doctor.py` (and point the human at `INSTALL.md`). The doctor prints the capability tier: **Tier 1** = Windows + Microsoft Word → the full print pipeline; **Tier 2** = no Word → EPUB, Kindle DOCX, digital-from-existing-PDF, cover compositing + verification, with print PDFs deferred to a Word machine.
- On Windows, use PowerShell syntax for shell commands (Bash eats backslash paths). On macOS/Linux use the native shell — knowing Tier-1 print requires Windows + Word.
- Machine paths live ONLY in `_tools/kit_env.json` (copy `_tools/kit_env.template.json` → `kit_env.json` if it doesn't exist). Never hard-code a machine path; never assume another machine's tools exist.
- The `organs` block in kit_env names OPTIONAL accelerators. When absent, use the portable fallbacks: `_tools/resize_image_safe.py` before viewing ANY image (never read an image >2000px raw); your harness's own search/read tools for file discovery; read large files in slices — **never blind-read a file >8K tokens**.
- **Model policy:** book prose is written by the MAIN loop, never by subagents. Fan-out subagents (source digestion, tool-building, audit passes) run one tier below your main-loop model — e.g. opus or sonnet — unless the human says otherwise.
- Cover **art generation** needs the optional GPU stack (`kit_env.cover_gen`). Without it, the human drops art into the book's `cover_art/` folder — typography compositing and perceptual verification still run on any machine (vision defaults to the harness's own eyes via `--backend auto`).

## 1 — Read your operating docs, in this order
1. `CLAUDE.md` — the orchestrator: boot sequence, plain-language command grammar, the two-verifier gate loop, autonomy policy, and the COMPACTION SURVIVAL section. (The harness auto-loads this — re-read it deliberately.)
2. `KIT_ARCHITECTURE.md` — the invariant design spec: folder taxonomy + the toolchain, each script with its exact I/O contract.
3. `docs/LESSONS_LEDGER.md` — the hard-won production rules, baked in as defaults (mirror-margins injection, empty-header fix, recto sections, spine geometry, Mixam filename routing, fitz-exact MediaBox, session survival, etc.).
4. `docs/COMPACTION_SURVIVAL.md` — how a session survives context compaction with zero fidelity loss. It governs Step 2 and your standing discipline.
5. `docs/format_spec_sheet.md` + `_tools/print_presets.json` — exact geometry for all nine formats, every number provenance-tagged. (The service's own previewer/calculator always wins over the preset.)

## 2 — Detect mode: RESUME an in-flight book, or START a new one
Check `book_workspace/` for any `<slug>/_CONTINUITY.md` whose STATUS is not `COMPLETE`.

### If found → RESUME
Follow that workspace's **RESUME PROTOCOL** — the numbered list at the top of its `_CONTINUITY.md` — exactly and in order. It will have you rehydrate, then read the ledger, the Book Bible (`seed.md`), and the last completed chapter before writing a word.

⚠️ **Cross-project transcripts.** `rehydrate.py` auto-finds the newest transcript of the *current* project — but a book begun under a different project folder lives in THAT project's transcript. Check the workspace for a `_RESUME_NOTES.md` carrying the exact `--session <path>` to rehydrate from (or an already-baked `_REHYDRATION.md`), and prefer those over auto-find.

### If none in flight → START a new book
1. Drop a gist of the book + all relevant source documents into `intake/`.
2. Ingest and orient: size large inputs first, chunk what overflows. **Read the CORE source yourself in full and skim every satellite (gestalt before delegation)** — only then fan out reader-subagents (one model tier down) to write RELATIONAL digests (`templates/digest.template.md`: extends / contradicts / deepens / bridges the core) into `book_workspace/<slug>/canon_refs/_digest_*.md` — each subagent WRITES ITS FILE TO DISK before returning. If the drop holds a core + satellites, ask the author once: weave into one new book grown from the core (synthesis, the default) or keep parts distinct (anthology)? Record it as `book_config.integration_mode`.
3. Author `book_workspace/<slug>/seed.md` (Book Bible + chapter contracts + any structural device) and a schema-valid `book_config.json` (validate: `python -c "import json,jsonschema; jsonschema.validate(json.load(open('book_config.json')), json.load(open('_tools/book_config.schema.json')))"` with paths adjusted).
4. Create `book_workspace/<slug>/_CONTINUITY.md` with a **RESUME PROTOCOL at the very top** (rehydrate → read ledger → read seed → read last chapter → continue), plus STATUS, DONE, NEXT, live invariants, and pointers. Rewrite it after every chapter.
5. Draft chapter-by-chapter into `manuscript/current/ch_NN_current.md`, then run the production pipeline: lint · assemble (version-pinned master) · produce all formats · cover (gen or supplied art → composite → vision verify) · `verify_build.py --format <each>` until every gate is green. Mark `_CONTINUITY.md` STATUS: COMPLETE.

## 3 — Standing disciplines (both modes)
- **Write every chapter to disk the instant it's done (atomic), and update `_CONTINUITY.md` immediately after.** This is what makes the session survive a compaction or quota reset with zero lost work — proven in production.
- The compaction hooks are installed (`PreCompact` pre-bakes `_REHYDRATION.md`; `SessionStart` on compact/resume forces the re-read). Trust them, but the continuously-maintained `_CONTINUITY.md` is the real safety net — never let it go stale.
- Every service's own previewer/calculator (KDP Print Previewer, Mixam job calculator, Blurb booksize calculator) is canonical over `print_presets.json`; a stated dimension goes into `book_config.spine.spine_override_in` and wins.
- Cover art carries NO title/author text (typography is composited after); render → resize <2000px → vision-verify before declaring a cover done.

Begin with Step 0, then Step 1, then Step 2. Do not skip the reads.
