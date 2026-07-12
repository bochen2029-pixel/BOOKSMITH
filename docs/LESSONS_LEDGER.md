# BOOKSMITH — LESSONS LEDGER (the kit constitution)

*Consolidated, deduplicated, from every file under `C:\Claude-Titanic\_kit_research\` (00 master synthesis; 01 Titanic workshop; 02 ATD; 03 Inside the Region; 04 BOOK3; 05 AI_BOOK/BOOK-test3 template instances; 06 memory+intake; `mechanisms/vision_keel.md`, `mechanisms/comfyui_hookup_FOUND.md`, `mechanisms/comfyui_ferryman.md`; `transcripts/tx_astra7.md`, `tx_book_aibook.md`, `tx_canon.md`, `tx_catchall.md`).*

**How to read this file.** Every entry is an enforceable RULE the kit obeys BY DEFAULT, plus the failure it prevents, the exact params/code, and the VERIFY step (mechanical check or vision check). This is the kit's memory of every hard-won fix. When two sources conflict on a number, BOTH are recorded with provenance and a stated safe default. The single overriding meta-rule: **calibrate against the KDP Print Previewer's stated dimensions — the validator is canonical, arithmetic is not.**

**Provenance of "current canon":** the authoritative gotcha catalog is `C:\ASTRA-7\book\production_lessons_learned.md` (2026-05-15, §1–§18). The older `C:\Claude-Titanic\PRODUCTION_LESSONS_LEARNED.md` (2026-04-20) is **superseded** and still carries stale numbers (notably the `0.302"` board-add). Where the ledger states a default, it tracks the ASTRA-7 catalog.

**Target runtime (assumed by all defaults):** Windows 11 + Microsoft Word installed (Word COM is the only reliable docx→PDF path). GPU RTX 4070 Ti SUPER (16 GB VRAM) → default cover checkpoint is **SDXL base** (~6.5 GB); Flux-dev-fp8 (~12 GB) is opt-in when VRAM is free.

---

## Section list

1. INTAKE
2. SEED & WRITING
3. INTERIOR (docx / OOXML)
4. MARGINS & RECTO
5. SPINE & COVER GEOMETRY
6. COVER ART GEN & VERIFY
7. KINDLE / EBOOK
8. DIGITAL PDF
9. PUBLISHING METADATA
10. VERIFICATION LOOP
11. CROSS-PLATFORM / RUNTIME
12. AUDIOBOOK (bonus stage)
13. UNRESOLVED NUMERIC CONFLICTS
14. FIRST-PASS DEFAULTS CHECKLIST
15. SESSION SURVIVAL & COMPACTION

---

## 1. INTAKE

### 1.1 Discover the folder before reading anything
- Rule: On boot, the harness performs filesystem discovery first (`ls` the intake folder recursively, size each file), then decides an ingestion strategy. Never blind-read; never assume the documented structure is what is on disk. First action: scan and confirm.
- Why / symptom if violated: The documented layout is "a guide, not gospel" — files land in unexpected locations and under misleading names. Blind-reading a 336 KB raw log burns the context window.
- Exact params/code: Size-then-chunk any large text via a chunker (`prepare.py` / `vera_chunker.py` pattern; chunk anything > ~8K tokens). Route by modality: text → chunk & read; image → resize ≤2000px then vision-read; audio/video → transcribe.
- Verify: A status report enumerating every discovered file + its class before any generation begins.

### 1.2 Classify the drop-folder into the seven intake file-classes
- Rule: Sort every intake file into: (a) ONE command-contract (`CLAUDE.md`) that turns the folder into an autonomous job; (b) one master spec/skill; (c) 1–N canon/soul/voice docs (OFTEN DUPLICATED across versions → reconcile); (d) opaque research returns (`compass_artifact_wf-<uuid>_text_markdown.md` / deep-research dumps); (e) one or more huge raw source logs (chunk, don't blind-read); (f) hand-crafted exemplars for calibration (JSONL/voice samples); (g) any tooling/validators/diffs the user already started.
- Why / symptom if violated: The user drops overlapping/duplicated canon versions and huge raw logs. Treating duplicates as distinct sources, or reading logs whole, corrupts the seed and wastes budget. (BOOK-VERA `READALL/` is the reference specimen of this raw-intake state.)
- Exact params/code: The kit's minimal intake contract = the user provides (a) a **gist** of the book + (b) a **folder of documents**; the harness ingests, de-duplicates versions, and self-orients from that alone.
- Verify: A reconciliation note listing which canon versions were merged/superseded and which duplicates were dropped, before writing SEED.md.

### 1.3 Build from an explicit include-list, never folder globs
- Rule: Interior generators read an explicit, ordered `BODY_FILES[]` / `CHAPTER_FILES[]` array — never a directory glob. The numeric filename prefix (`chapter_NN_`, `front_matter_NN_`) is for human sort order only; the generator does not trust the directory listing.
- Why / symptom if violated: Repos hold up to **5 byte-identical mirror copies** of manuscripts across `story_parts/`, `docs/`, etc.; misnamed landmines exist (e.g. a `v1.0.md` that is a philosophy framework, not a draft). A glob picks up superseded drafts and ships the wrong text.
- Exact params/code: Hardcode the ordered file array in the generator (identical array in the Kindle and print generators); insert interludes/appendices at explicit indices.
- Verify: Parts-sum `wc -w` == stitched master `wc -w` (integrity check that shards concatenate losslessly).

### 1.4 Anchor "now" before any recency reasoning
- Rule: Read the system clock before reasoning about "latest/recent" anything (research returns, KDP policy, prices).
- Why / symptom if violated: Stale defaults (e.g. an old board-add value) get treated as current.
- Exact params/code: `Get-Date -Format "yyyy-MM-dd HH:mm:ss K (dddd)"`.
- Verify: The status report cites the anchored date.

### 1.5 Core-first gestalt — skim-then-delegate, never delegate-blind
- Rule: Before ANY digest fan-out, the MAIN loop identifies the CORE source (the book's spine) and reads it in full (sliced if large), and skims every satellite itself (headings + roughly the first/last 500 words). Only a loop that holds the gestalt may set structure; subagents add depth afterward — one per satellite, one model tier down, write-then-return.
- Why / symptom if violated: The first real intake run (2026-07-11) fanned digest subagents straight from the file list; the main loop never formed a gestalt, so the source-file boundaries leaked into the book structure and the drafting read as tacked-on recombination — the author watched it happen and aborted the run. Whoever holds the gestalt owns the architecture; delegate-blind means nobody holds it.
- Exact params/code: ingest order = classify → reconcile → core read (full) → all satellites skimmed → THEN digest fan-out. Subagents provide depth; they NEVER provide structure.
- Verify: GATE-1 — the intake manifest names the core, and the session record shows the core read + every skim before the first agent spawn.

### 1.6 Digests are relational, never standalone
- Rule: Every `canon_refs/_digest_*.md` follows `templates/digest.template.md` and must state where its source EXTENDS / CONTRADICTS / DEEPENS / BRIDGES the core, plus chapter-usable synthesis hooks, retrieval anchors, and a do-not-import list. A digest that merely summarizes its source in isolation is rejected and re-run.
- Why / symptom if violated: Standalone summaries arrive structureless and get stapled into chapters — pre-chewed anthology, the tacked-on tell. Relational digests return half-woven: the collision points and bridges are exactly what the drafting loop composes with.
- Exact params/code: template sections — Source / Key content (with retrieval anchors) / RELATION TO THE CORE / Synthesis hooks / Voice notes / Do NOT import.
- Verify: grep each digest for the "RELATION TO THE CORE" section; missing → the digest agent re-runs.

### 1.7 Integration mode is asked, never assumed (synthesis is the default)
- Rule: When the drop holds a core + satellites, ask the author ONCE, in plain language: weave into one new book grown from the core (**synthesis** — the default), or keep the parts distinct (**anthology**)? An existing manuscript to be reborn is **reforge**. Record the answer as `book_config.integration_mode`. Synthesis = re-derived from first principles, satellites dissolved in; the book must be better than the sum, never the sum.
- Why / symptom if violated: The machine once resolved this ambiguity silently and chose recombination — the outcome perhaps 1 author in 10 wants. The unasked structural assumption cost a full drafting run. Recombination is not synthesis; if concatenation were the goal, a script would do.
- Exact params/code: one intake question → `integration_mode` in book_config (schema enum: synthesis | anthology | reforge, default synthesis); GATE-4 then enforces it: in synthesis mode no unit may map ~1:1 onto a single source document (check each unit's canon-anchor distribution — the anthology signature).
- Verify: `integration_mode` present in book_config at GATE-2; the GATE-4 provenance check passes per unit.

---

## 2. SEED & WRITING

### 2.1 Scaffold the fixed 5-doc + 13-dir taxonomy
- Rule: Ship the proven book-agnostic skeleton: **5 root docs** — `CLAUDE.md` (operating contract), `SEED.md` (Book Bible), `ARCHITECTURE.md` (invariants), `README.md` (human orientation), `WRONG.md` (append-only revision log) — plus `CHANGELOG.md` (mechanical action log) and `_warm_start.md` (rehydration pointer). **13 dirs:** `contracts/ state/ registry/ handoffs/ reviews/ exemplars/ manuscript/{drafts,current}/ outputs/ cover_art/ canon_refs/ appendices/ fonts/ _tools/ _reference/` (+ optional `INTAKE/`). `outputs/` subfolders: always `markdown digital kdp_paperback kdp_hardcover kindle`; add `mixam_hardcover` only for literary/premium register.
- Why / symptom if violated: Proven identical across AI_BOOK vs BOOK-test3 built from one empty skeleton — the same machine with different fills. Ad-hoc layout breaks the Context Pack auto-loader and the audits.
- Exact params/code: ARCHITECTURE precedence rule (verbatim): *"if SEED.md and this file conflict, this file is the invariant; SEED.md is the instantiation … this file wins and CLAUDE.md gets revised to match — never the reverse."*
- Verify: `ls` shows all root docs + dirs; `_warm_start.md` boots a fresh session in ~10 min.

### 2.2 SEED.md is the Book Bible with explicit load discipline
- Rule: SEED.md carries 7 sections. **CORE always-load:** §1 Book Bible, §2 Structure, §4 Thread Registry, §5 Continuity Scaffolding, §7 Execution Protocol. **Load-only-relevant on entry:** §3 Chapter Contracts, §6 State Snapshots. §1 = Work Intent + Confirmed Decisions table + Voice/Tone spec (5 verbatim exemplars + phrase blacklist + greenlist) + Style Rules + Thematic Architecture + Domain Core + Refrain lock + Glossary of Sacred Terms.
- Why / symptom if violated: Without load discipline the pack bloats; without the Confirmed-Decisions table the harness re-litigates trim/paper/length every session.
- Exact params/code: Confirmed Decisions table columns: reader, voice, person, length, chapter/part count, formats, license, distribution, audiobook, paper, finish, trim.
- Verify: SEED §1 renders the 5 voice exemplars + blacklist + greenlist; `audit voice` reads them.

### 2.3 Contract-first, prose-second
- Rule: Every chapter/part gets a versioned interface contract in `contracts/{module_id}.md` written BEFORE any prose. Schema: `Authorship Class` / `Intent` / `Inherits` (reader knows-feels-believes + active concepts + tension 1–10 at entry) / `Must Accomplish` (3–7 verifiable) / `Must Plant` (seed → target module) / `Must Callback` (← source module, **with variation**) / `Delivers` (exit state) / `Constraints` / `Scope` (autonomous vs escalate) / `Length` (±20%) / `Canon Anchors` / `Fiction Substrate` / `Register Profile` / `Refrain Placement`.
- Why / symptom if violated: "The architecture is permanent; the prose is implementation." Without contracts, multi-session writing drifts; registries silently desync (BOOK3 caught 17 canon-anchor drifts → 9 registry-sync cascades → 5 orphan seeds).
- Exact params/code: Module IDs are canonical/stable (`prologue`, `part01_*`, `coda`, `epilogue`, `appendix_a_*`) and drive filenames everywhere. `init_contracts.py` generates stubs idempotently (`--force` to override).
- Verify: `audit threads` (orphan seeds/payoffs), `audit dependencies` (forward references), `audit canon` (citations resolve to real `canon_refs/` files), `check compression-pairs`, `check refrain`.

### 2.4 Honor authorship classes A/B/C — never silent-upgrade
- Rule: Every contract carries `authorship_class`. **Class A** = human-only: harness produces an OUTLINE only (`contracts/{id}_outline.md`); the manuscript file stays empty; even a placeholder draft is wrong. **Class B** = machine scaffold with `[BO-WRITES: {desc}]` markers on load-bearing voice passages; do NOT draft prose into those markers. **Class C** = machine drafts fully for human revision. Class is authoritative from the contract; never reclassify.
- Why / symptom if violated: This is the human-in-the-loop dial that keeps the emotionally load-bearing scenes human-authored (the "illusion of human authorship" bar). Silent-upgrading Class A overwrites the author's signature work.
- Exact params/code: Class A typically = Prologue / Grief chapter / Epilogue. Apply A to the most emotionally load-bearing units.
- Verify: Grep manuscript for surviving `[BO-WRITES]` markers before export; confirm Class-A manuscript files are empty/outline-only.

### 2.5 Context Pack auto-assembles on every `generate`
- Rule: On `generate {chapter|part} N`, auto-load a fixed manifest: SEED §1/§2 + this contract + contracts N−1/N+1/N+2 + **FULL prose of N−1 and N−2** (not the handoff — "the handoff gives state; the prose gives residue") + earlier handoffs (compressed) + State Snapshot at boundary + all registries (threads, compression-pairs, dependencies, refrain, canon, fiction) + voice exemplars (anchor always) + glossary + canon anchors + Execution Protocol.
- Why / symptom if violated: Prior-unit full prose is the continuity engine; skipping it produces exact-quotation callbacks (the AI signature) and register uniformity.
- Exact params/code: Budget ≈ 150–250K tokens loaded, 750K+ remaining at 1M context. **1M-era defaults: no fresh-session-per-chapter; no 80K-token chapter cap** (both were 200K-era workarounds). Write "with the entire book in your head."
- Verify: Pack size fits budget; the generated unit's callbacks vary the wording of the source.

### 2.6 Three-layer handoff + state snapshot after every unit
- Rule: After every unit write `handoffs/{id}_handoff.md`: **Layer 1 State (binding)** = what happened/changed/matters/unresolved/retrieval-anchors; **Layer 2 Craft (informational)** = tonal register, rhythm, imagery, pacing at exit; **Layer 3 Recommendation (advisory)** = opening hint for next. Next unit binds Layer 1 + its own contract; Layer 2 informs craft; Layer 3 is ignorable. Also emit a per-boundary State Snapshot (reader knows/feels/believes + active concepts + tension n/10).
- Why / symptom if violated: Cross-session continuity collapses without a binding state layer; the advisory layer must be separable so it does not over-constrain.
- Exact params/code: Per-unit 10-step protocol: load pack → intent ack → writing plan → draft → self-assessment → handoff → thread-registry update → state snapshot → auto-audit → queue quality gate. "Unit not complete until all ten execute."
- Verify: `status`/`next`/`progress` read the latest handoff + snapshot to resume mid-unit.

### 2.7 Anti-AI-tell cross-interweaving + banned-vocabulary lint
- Rule: Apply the 9 anti-mass-production techniques: residue; **callbacks with variation** ("Exact quotation is the AI signature. Variation is the human signature"); flash-forwards; motif echoes with variation; register variation per unit; authorial self-correction (3–5×); chapter-ending rotation (no two close identically); emergent-resonance recognition; personal material at natural beats. Forbid the AI-tell list: meta-commentary openers, "Key Takeaways"/summary boxes, mechanical transitions, uniform register, hedged ranges-not-specifics, hypothetical "Company X". Run a SEED-blacklist-driven vocabulary lint (case-sensitive + case-insensitive + regex tiers, exit-1 blocks release), excluding scaffolding + cached-source dirs by default (they legitimately quote banned words / period-authentic vocabulary).
- Why / symptom if violated: The single recurring risk is prose reading "mass-produced." Banned words (`delve, nuanced, multifaceted, holistic, leverage, navigate, tapestry, journey, unpack, dive in, lean into, key takeaways, TL;DR`, em-dash-as-workhorse, bullet lists) are also a generic AI-slop filter.
- Exact params/code: `check_acp_vocabulary.py` pattern = 97 annotated patterns (23 case-sensitive + 70 case-insensitive + 4 regex), each tagged with its correction/source; exit 0 clean / 1 drift / 2 usage; `is_documentation_file()` excludes non-manuscript dirs (opt-in `--include-docs`). Per-book **grep gate**: `Grep "[—–]"` (em-dash sweep) after every draft — section headers and `[BO-WRITES]` markers are the highest-frequency leak sites; replace with commas/colons/periods/parentheses. Optional per-book "no-leak" grep (forbidden proper nouns in a character's voice) and "curtain-violation" grep (anachronistic/meta terms).
- Verify: Vocabulary lint exit 0; `Grep "[—–]"` returns clean; word count within ±20% of contract; refrain phrase appears at exactly its designated placements (e.g. 6).

### 2.8 Version discipline + regenerate-all-on-edit
- Rule: Manuscript markdown is **append-only, version-suffixed** (`ch{N}_v{M}.md`; "up to v7 per chapter is normal — don't treat revision count as a problem"). One version-pinned source-of-truth variable. **Every markdown revision regenerates ALL formats in the SAME session.**
- Why / symptom if violated: Source-version drift once shipped a Kindle **8,476 words short** of the hardcover (print generator read `v7`, Kindle read `v6`).
- Exact params/code: Checklist item "update source version in ALL generator scripts"; `Grep` all `.js` generators when revising markdown; `kindle_parity_check.py` word-count diff (ebook may be slightly higher for About-the-Author, never lower).
- Verify: `kindle_parity_check.py` shows parity; all generators reference the same version string.

### 2.9 Ship-at-90% gate + append-only WRONG.md
- Rule: `export v1.0` is gated behind an explicit "Ship at 90%? (canon is append-only; v1.1 exists)" confirmation. `WRONG.md` logs semantic position revisions only, append-only, 5-field schema; `CHANGELOG.md` logs mechanical actions. Adversarial review (5-role or Steelman/Skeptic) is first-class, not optional.
- Why / symptom if violated: Completion anxiety perpetuates paralysis; the harness should offer a scope decision (shelve / compress / ship) rather than defaulting to the maximal "cathedral."
- Exact params/code: WRONG.md entry = `## [YYYY-MM-DD] Topic` / **Prior position** / **Revised position** / **Perturbation event** / **Source**. Never edit prior entries; supersede with a new one. 5-role audit = Primary Source / Steelman / Skeptic / Integrator / Historical / Synthesis (fresh role-switch per pass, do not blend).
- Verify: `export v1.0` refuses to fire without the ship-at-90% confirmation.

---

## 3. INTERIOR (docx / OOXML)

### 3.1 Two-language, dependency-light toolchain
- Rule: Interiors = **Node `docx@9.6.1` + `jszip@3.10.1`** (programmatic OOXML — NO template .docx, NO LaTeX, NO Pandoc, NO headless browser). Covers + final PDFs = **Python** `PIL/Pillow` + `PyMuPDF (fitz)` + `PyPDF2` + `win32com`. The two halves meet at the filesystem: JS writes `*_KDP.docx`; Word COM renders the page-counted PDF; the page count feeds Python spine math.
- Why / symptom if violated: One shared body of code cloned per book; a single `book_config` collapses ~12 JS + ~9 PY per-book clones into ~5 parameterized builders. `generate_book_v11.js` is byte-identical to v10 except 6 lines.
- Exact params/code: `package.json` declares exactly `docx@^9.6.1` + `jszip@^3.10.1`. No puppeteer/sharp/playwright anywhere.
- Verify: `npm ls` shows only the two deps; no headless-browser import.

### 3.2 Shared interior constants (all print formats)
- Rule: **6.00" × 9.00" trim** on ALL formats. `1 inch = 1440 DXA` → `PAGE_W = 8640`, `PAGE_H = 12960`. Body font **Georgia** (`FONT = "Georgia"`). Ornament `✦` (U+2726) via "Segoe UI Symbol"; scene divider `· · ·` (U+00B7 ×3). Code spans → Consolas; math → Cambria Math. Part heading centered, uppercased, `characterSpacing 60`, `✦` under it.
- Why / symptom if violated: One wrong trim/DXA value = rejected upload. Force UTF-8 on every read (the `✦` glyph is NOT cp1252).
- Exact params/code: Body 12pt (`size:24`, novella/Mixam/Kindle) or 11pt (`size:22`, denser books); line 320–340 `atLeast` (~1.35–1.4×); first-line indent 360 DXA; `spacing.after 160`. Body color `#1A1A1A` print / `#000000` Kindle. Palette (Titanic): NAVY `#0D1B2A`, CREAM `#F4EFE0`, GOLD `#C9A760`. (ATD: UMBER `(30,22,15)`, CREAM `(244,239,224)`.)
- Verify: Generator prints its computed DXA page block; `wc` parity across generators.

### 3.3 Markdown parse order: code spans BEFORE italics
- Rule: The body-paragraph parser splits on code spans (backticks) FIRST, then italics (`*...*`) within non-code segments — identical in every generator (print + Kindle).
- Why / symptom if violated: `` `Q = Cd*A*sqrt(2*G*H)` `` rendered fine in the hardcover but showed **literal backticks in the Kindle** because the old ebook parser only handled italics; asymmetric parsers produce different output from the same markdown (Gotcha G12).
- Exact params/code: Structural tokens: `# H1` (chapter/book title), `## H2` (Part heading), `---` / `· · ·` (section break → `✦`), `> ` (blockquote), `*italic*`, `**bold**`, `` `code` `` (Consolas), `$inline$`/`$$display$$` math, `[IMAGE …]` blocks consumed and skipped in text-only builds.
- Verify: A backtick-containing equation renders identically in print and Kindle output.

### 3.4 Mirror margins REQUIRE a JSZip injection — docx@9 drops the flag
- Rule: After `Packer.toBuffer(doc)`, load the docx as a zip with JSZip and inject BOTH `<w:mirrorMargins/>` AND `<w:evenAndOddHeaders/>` into `word/settings.xml`. Run this injector BETWEEN the JS generator and the Word-COM PDF conversion (the PDF is produced from the docx, so the docx must be corrected first).
- Why / symptom if violated: `page: { mirror: true }` in docx@9.6.1 does NOT write `<w:mirrorMargins/>`; Word then applies literal left/right to every page → verso gutter on the wrong side → KDP *"Insufficient gutter. Books with N pages require at least 0.625\" for gutter."* `<w:evenAndOddHeaders/>` is what makes `Footer(default)` vs `Footer(even)` render as separate verso/recto footers (page number on the OUTER corner).
- Exact params/code:
  ```js
  const zip = await JSZip.loadAsync(buffer);
  let settings = await zip.file("word/settings.xml").async("string");
  if (!settings.includes("<w:mirrorMargins"))
    settings = settings.replace(/(<w:settings[^>]*>)/, "$1<w:mirrorMargins/>");
  if (!settings.includes("<w:evenAndOddHeaders"))
    settings = settings.replace(/(<w:settings[^>]*>)/, "$1<w:evenAndOddHeaders/>");
  zip.file("word/settings.xml", settings);
  const finalBuffer = await zip.generateAsync({ type:"nodebuffer", compression:"DEFLATE" });
  ```
  Pipeline order: `node generate_book_kdp.js && node _tools/inject_mirror_margins.js OUT.docx && python _tools/docx_to_pdf.py OUT.docx OUT.pdf`.
- Verify (mechanical): unzip and grep — `'<w:mirrorMargins' in settings.xml` must be True; AND confirm per-section `<w:pgMar>` emits the wider gutter on the correct side (e.g. `left=1260 right=720`) — the flag alone is insufficient if `pgMar` hard-codes `left=900 right=720` and overrides mirror logic. Rendered check: pypdfium2 dark-column scan at 1.5× → verso `left=54px,right=67px`, recto `left=67px,right=54px` (the 13px delta = the 0.125" gutter-vs-outside difference).

### 3.5 Every header/footer-free section needs EXPLICIT EMPTY Header/Footer objects
- Rule: Attach explicit empty `Header` AND `Footer` objects (`emptyHeadersFooters()`) to EVERY header/footer-free section — front matter, TOC, preface/reader's-note, and the trailing EVEN_PAGE blank. Sections immediately after a body section are highest-risk (Word inherits forward).
- Why / symptom if violated: **The most-rediscovered bug (≥4× before it was written down).** Word inherits the previous section's running header + page number; a "blank" trailing page then renders them → KDP *"text outside margins."* **`margin.header=0, margin.footer=0` is the WRONG fix that keeps re-biting** — it only shrinks the zone; the inherited content still renders. Also: make the trailing blank a truly empty `new Paragraph({})`, NOT a Paragraph with an invisible size-2 white TextRun (even an invisible run can trip the rejection).
- Exact params/code:
  ```js
  function emptyHeadersFooters() {
    return {
      headers: { default: new Header({ children: [new Paragraph({})] }) },
      footers: { default: new Footer({ children: [new Paragraph({})] }) },
    };
  }
  ```
- Verify (mechanical): zipfile-inspect each `word/header*.xml` — "no-header" section files must show `[]`; body header files show `['BOOK TITLE']`.
  ```python
  import zipfile, re
  with zipfile.ZipFile(docx) as z:
    for h in sorted(n for n in z.namelist() if 'word/header' in n):
      print(h, re.findall(r'<w:t[^>]*>([^<]*)</w:t>', z.read(h).decode()))
  ```

### 3.6 Front-matter vertical alignment via `<w:vAlign>` JSZip injection
- Rule: Build each ceremonial page as its OWN one-page section (do not cram half-title + verso + title + copyright into one section with PageBreaks). Then JSZip-inject `<w:vAlign w:val="center|bottom"/>` into each section's `<w:sectPr>` in `word/document.xml`. Idempotent (strip any existing vAlign first). NEVER on body pages (they must top-flow).
- Why / symptom if violated: docx@9 doesn't expose vAlign; `spacing.before` is silently dropped after a PageBreak, `lineRule:"exact"` spacers are inconsistent across Word versions, empty-paragraph fillers are fragile → half-title won't center, copyright won't anchor to bottom.
- Exact params/code: `const SECTION_VALIGN = { 1:"center", 3:"center", 4:"bottom" };` (1-indexed: half-title center, title center, copyright bottom; blank verso left alone). Kept in a SEPARATE injector from mirror-margins because `vAlign` lives in `document.xml` while `mirrorMargins`/`evenAndOddHeaders` live in `settings.xml`. Brittle legacy fallback (avoid): push copyright to bottom via `spacing:{ before: ~8500 }` DXA.
- Verify: unzip `document.xml`, confirm `<w:vAlign>` present in the intended sections.

### 3.7 Word COM field-update loop: iterate by INDEX, wrap each in try/except
- Rule: In the Word-COM converter, update fields **by index, not by live iterator**, each guarded: update TOC(s) → `Repaginate()` → `for i in range(1, doc.Fields.Count+1): try doc.Fields(i).Update() except: pass` → update TOC again → `Repaginate()` → `ComputeStatistics`.
- Why / symptom if violated: A TOC `.Update()` **deletes and recreates field handles**; a live `for field in doc.Fields: field.Update()` then dereferences stale/deleted handles → COM error → exit 1 (observed live: *"Exit code 1 … Exporting PDF via Word COM … Traceback"*).
- Exact params/code: Comment the fix inline: "Update fields by index (live iteration can hit deleted handles)."
- Verify: The converter completes and returns a page count without a COM traceback.

### 3.8 Single-pass MD→DOCX; lint as a hard build gate
- Rule: Read the clean `.md` directly and go MD→DOCX in one pass — NEVER round-trip through a rendered PDF/DOCX and back to text. Guard with `lint_manuscript.py` as an exit-1 build gate.
- Why / symptom if violated: A round-tripped manuscript picks up `a_Thursday` (italic markers re-read as underscores), sentences ripped across paragraph breaks, doubled spaces, soft-hyphen line breaks.
- Exact params/code: `lint_manuscript.py` flags EMBEDDED_UNDERSCORE, PARAGRAPH_NOT_TERMINATED, UNBALANCED_EMPHASIS, STRAY_MARKDOWN, MULTIPLE_SPACES, MID_WORD_HYPHEN_BREAK, EMDASH_CONTINUATION.
- Verify: `lint_manuscript.py` exit 0 before generation.

### 3.9 LaTeX → Unicode (avoid OMML) for math books
- Rule: Convert `$...$`/`$$...$$` to Unicode math + italic **Cambria Math** runs rather than emitting OMML. Ordering is load-bearing.
- Why / symptom if violated: Wrong order breaks nested `\frac{K(t)}{K_{\max}}`; OMML is painful to emit via docx-js; raw `\Omega_{\text{ext}}` passes through as literal backslashes.
- Exact params/code: Order = (1) strip `\left/\right/\big`; (2) unwrap `\text/\mathrm/\mathcal/\mathbb/\mathbf/\mathit`; (3) `\dot{x}`→precomposed dot-above (ẋ, Ġ); (4) symbols longest-first (α β Σ Φ ≈ ∑ ∫ ∞ ∂ ∇ → ⇒); (5) **subscripts `_{...}` BEFORE fractions** (so `_{\max}`→`ₘₐₓ` removes inner braces that would defeat the `\frac` regex); (6) superscripts; (7) `\frac{a}{b}`→`(a)/(b)`; (8) cleanup stray braces. Plus `fixProseSubscripts()` for prose-mode `Ω_ext` (bail if any char lacks a subscript glyph). Tool trio: `latex_to_unicode.js` + `check_docx_latex.py` + `find_latex.py`. Alt (non-Kindle Word only): pandoc + `reference.docx` with explicit `<w:rFonts>` (ascii/hAnsi/cs/eastAsia) OXML injection so Word doesn't substitute the math font; `--shift-heading-level-by=-1` maps `##`→Heading 1.
- Verify: `check_docx_latex.py` finds no residual `\` LaTeX; math runs tagged Cambria Math.

---

## 4. MARGINS & RECTO

### 4.1 KDP paperback margin quartet
- Rule: KDP paperback (DXA): top **720** (0.5"), bottom **900** (0.625"), gutter/left **1080** (0.75"), outside/right **720** (0.5"), `header 0, footer 360, gutter 0, mirror true`.
- Why / symptom if violated: **Gutter is 0.75" (1080), NOT the 0.625" minimum**, to absorb two invisible overshoot sources into an exact gutter: justified-line trailing-space bbox extends ~2.7pt past the last glyph, and italic letters (esp. `f`, swashes) render ~2pt left of origin (side-bearing). At 0.625" exact these still trip "insufficient gutter." Bumping to 0.75" grows the text block to 4.75" and page count ~5% → recompute spine after regen.
- Exact params/code: The 0.5/0.625 pair confirmed across Night Was Young, City, Second Notebook. KDP minimums are 0.5" gutter / 0.25" others; these exceed for aesthetics + overshoot safety.
- Verify: pypdfium2 `textpage.get_charbox()` scan confirms no glyph box crosses the gutter edge.

### 4.2 Mixam interior margins (looser, hardcover comfort)
- Rule: Mixam interior (DXA): top **900** (0.625"), bottom **1080** (0.75"), gutter **1260** (0.875"), outside **900** (0.625"); body **12pt Georgia**, line 340 (~1.4×). Do NOT mix with the KDP set.
- Why / symptom if violated: The ONLY difference between the Mixam and KDP interior generators is these 4 margin constants + the output filename. Looser margins → more pages (Mixam ~203–204pp vs KDP ~185pp for the same text) → different spine → covers CANNOT be reused across services.
- Exact params/code: Same mirror-injection, same front matter, same recto logic as KDP.
- Verify: Page count differs from KDP as expected; regenerate the Mixam cover from the Mixam page count.

### 4.3 Recto enforcement via per-chapter ODD_PAGE + trailing EVEN_PAGE blank
- Rule: Make each chapter/Part its own section with `SectionType.ODD_PAGE` (Word auto-inserts the blank verso when the prior unit ended odd) and append one final `SectionType.EVEN_PAGE` blank section for even parity. Prefer this over the brittle hard-coded "single blank verso before Part II" cascade.
- Why / symptom if violated: The naive one-body-section + hard-coded blank-verso trick is tuned to an empirical page count; any markdown edit shifts pages and breaks recto discipline. The ODD_PAGE approach survives markdown edits with no re-tuning.
- Exact params/code: First body section sets `pageNumbers: { start: 1 }`; remaining chapters continue (no `start`). Pass `leadingPageBreak=false` for the first H1 of an ODD_PAGE section (the section break already advances the page → a leading PageBreak would double-advance to an unwanted blank recto). Mirror footer factory: `default` footer RIGHT-aligned `PageNumber.CURRENT` (recto→outer), `even` footer LEFT-aligned (verso→outer). Section layout: [0] front matter (no numbers) → [1] TOC (ODD_PAGE, no numbers) → [2..] chapters (ODD_PAGE, first sets start:1) → [last] EVEN_PAGE blank.
- Verify: `check_part_pages.py` — Word COM opens read-only, `Repaginate()`, `ComputeStatistics(2)` total, `Selection.Find` each "PART N —", reads `Selection.Information(3)` (wdActiveEndAdjustedPageNumber), flags any Part landing on verso (even).

### 4.4 Page-count multiples: KDP ×2, Mixam ×4
- Rule: KDP total pages must be a multiple of **2** (handled by the trailing EVEN_PAGE section). Mixam must be a multiple of **4** — pad AFTER the Word-COM PDF conversion using PyMuPDF.
- Why / symptom if violated: Wrong parity rejects the upload.
- Exact params/code:
  ```python
  import fitz; doc = fitz.open(pdf_path)
  to_add = (4 - len(doc) % 4) % 4
  for _ in range(to_add): doc.insert_page(-1, width=432, height=648)  # 6×9 pt
  doc.save(tmp, deflate=True, garbage=4, clean=True); doc.close(); os.replace(tmp, pdf_path)
  ```
- Verify: `len(fitz.open(pdf)) % 4 == 0` (Mixam) / `% 2 == 0` (KDP).

### 4.5 Front-matter sequence + recto starts
- Rule: Front matter order (all unnumbered, major elements on recto/odd, blank versos between): half-title → blank → title page → copyright (bottom-aligned) → dedication → blank → epigraph → blank → Part I on recto.
- Why / symptom if violated: Convention; a Part landing on verso reads wrong. Page numbers start on the first prose page, not front matter.
- Exact params/code: Blank verso = `new Paragraph({children:[new PageBreak()]})`; copyright bottom via `<w:vAlign val="bottom">` (§3.6) not the brittle big-`before` hack.
- Verify: `check_part_pages.py` reports every Part on recto.

---

## 5. SPINE & COVER GEOMETRY

### 5.1 Bleed / wrap per format (the unforgiving numbers)
- Rule: **Mixam cover bleed 0.80"** all 4 sides (thick — wraps case boards). **Mixam interior bleed 0.125".** **KDP paperback bleed 0.125".** **KDP hardcover WRAP 0.708"** all 4 sides — this is a case-board turn-in, **NOT bleed** (the single most common KDP-hardcover error).
- Why / symptom if violated: Uploading a paperback wrap to a hardcover listing rejects: *"Your expected cover size is 14.183×10.417 but the submitted file size is 12.713×9.250."*
- Exact params/code: KDP HC turn-in derives from wrap height: `(WRAP_H − 9)/2 = (10.417−9)/2 = 0.7085"`.
- Verify: KDP Print Previewer accepts the wrap dimensions.

### 5.2 Spine math — paper multipliers
- Rule: Paperback spine = `PAGES × 0.0025` (cream) or `× 0.002252` (white), **no board add**. Hardcover adds a board term (see §5.3).
- Why / symptom if violated: Cream vs white uses different multipliers; the wrong one mis-sizes the spine.
- Exact params/code: `SPINE_PER_PAGE = 0.0025 if PAPER=="cream" else 0.002252; SPINE_IN = round(PAGES*SPINE_PER_PAGE, 3)`. **KDP hardcover is WHITE-only** (cream not offered) → use `0.002252` for KDP HC. Cream is available for KDP paperback + Mixam.
- Verify: Spine matches the Previewer's stated value (§5.5).

### 5.3 KDP hardcover board add — 0.348" default, but CALIBRATE
- Rule: KDP hardcover spine = `paperback_spine + HARDCOVER_BOARD_ADD_IN`. **Default `HARDCOVER_BOARD_ADD_IN = 0.348"`** (2026 spec, empirically calibrated against ATD Print-Previewer rejections). Treat the first Previewer round as a calibration step and, on any mismatch, hardcode KDP's STATED spine.
- Why / symptom if violated: The board add DRIFTS across books/time (**0.302 → 0.348 → 0.246 → 0.241**). The legacy `0.302` caused v1 rejections and is known-wrong. The Inside-the-Region formula `pages × 0.0025 + 0.241` (fitted at 426pp) does NOT extrapolate: at **186pp** it gave 0.706" but KDP demanded **0.767"** (verbatim rejection *"expected 14.183, got 14.123"*) — the constant term is page-count-dependent.
- Exact params/code: Reverse-derive from KDP's stated wrap width: `spine = stated_wrap_width − 12 − 1.416` (the `1.416` = 2 × 0.708" turn-in). Use a single hardcoded `SPINE_OVERRIDE_IN` bypassing the formula once KDP states its number. Height quirk: arithmetic gives `0.708+9+0.708 = 10.416"` but the validator expects **10.417"** → hardcode `WRAP_H_IN = 10.417`.
- Verify: KDP Print Previewer accepts; if it states a different expected spine, adopt that number and regenerate.

### 5.4 Mixam board add — NON-CONSTANT, trust Mixam's calculator
- Rule: Mixam hardcover spine board-add is NOT a constant (~0.160"@204pp, ~0.110"@548pp, ~0.130" est. mid-range). Read Mixam's own job-config calculator value and use it; back-solve the board-add if you must record one.
- Why / symptom if violated: Any formula is wrong at some page count; Mixam's calculator is authoritative.
- Exact params/code: Workflow: upload once, read Mixam's stated spine, set `SPINE_BOARD_ADD_IN` accordingly, regenerate **spine.pdf only** (front/back don't depend on spine width). E.g. Mixam returned 1.48" for 548pp cream → `1.48 − 548×0.0025 = 0.110"` board add.
- Verify: spine.pdf width matches Mixam's job-spec spine.

### 5.5 Final wrap dimension formulas + validator-wins rule
- Rule: **KDP paperback** = `(6×2) + spine + (0.125×2)` W × `9 + (0.125×2) = 9.25"` H. **KDP hardcover** = `(6×2) + spine_with_boards + (0.708×2)` W × `10.417"` H. **Mixam** = FOUR independent 300-DPI PDFs each with 0.80" bleed: front & back `7.60"×10.60"`, spine `(spine+1.60")×10.60"`, interior `inner_*.pdf`. **When arithmetic and the Previewer disagree, the Previewer's 4-decimal value wins.**
- Why / symptom if violated: The Previewer checks the rounded 4-decimal value it prescribes, not raw arithmetic; a ~0.001–0.002" mismatch rejects.
- Exact params/code: Worked examples — 186pp cream paperback → 12.715"×9.250", spine 0.465". 186pp white HC → 14.183"×10.417", spine 0.767". 426pp white HC → ~14.723"×10.417", spine ~1.306". 446pp cream HC → 14.880"×10.417", spine 1.463". Panel x-boundaries computed from bleed/wrap + trim + spine; spine width computed as the RESIDUAL (`WRAP_W − 2*wrap − 2*trim_w`) for exact canvas fit.
- Verify: fitz reports the exact MediaBox; KDP Previewer accepts.

### 5.6 Cover PDFs need EXACT MediaBox via PyMuPDF, not PIL
- Rule: Write every cover PDF with PyMuPDF (`fitz`) setting an exact MediaBox in points (`inches × 72`) — NOT PIL's `Image.save(..., "PDF")`.
- Why / symptom if violated: PIL computes the MediaBox from `floor(pixels/DPI)`, truncating fractional inches (e.g. 14.829×300=4448.7→4448→reports 14.8267"); KDP/Mixam compare to 4 decimals and reject a 0.002" mismatch.
- Exact params/code:
  ```python
  page = pdf.new_page(width=W_IN*72, height=H_IN*72)
  page.insert_image(page.rect, filename=jpg)
  pdf.save(out, deflate=True, garbage=4, clean=True)
  ```
- Verify: `fitz.open(pdf)[0].rect` == exact points; 4-decimal inches match target.

### 5.7 Cover assembly + typography safe zone
- Rule: KDP (paper + hard) = ONE wrap image `[back│spine│front]`. Mixam = THREE independent PDFs. Keep all typography ≥ `bleed + 0.25"` from every edge (Mixam **1.05"**, KDP paperback **0.375"**, KDP hardcover **0.958"**). Background art may bleed INTO the turn-in (no seam if trimmed long), but readable text stays inside the 6×9 trim + quiet zone.
- Why / symptom if violated: "BO CHEN" once landed at 0.74" from bottom, inside the 0.80" Mixam bleed, and was trimmed off.
- Exact params/code: Cover composition zones — leave the **upper third of the front** open for title typography, the **lower third of the back** open for description + ISBN barcode; spine = typography only, no image, background color matching the cover. Spine composed horizontally on a temp canvas then `.rotate(-90, expand=True)`.
- Verify: Render the wrap to a preview and vision-check every text element sits inside the quiet zone.

### 5.8 Any interior change cascades to the cover
- Rule: Margin change → page count → spine → cover width. Regenerate the cover after ANY interior change; NEVER reuse a cover across services (Mixam vs KDP spine widths differ). Front/back panels don't depend on spine → after a page-count shift, regenerate the spine only.
- Why / symptom if violated: ATD's v1.2 grew 416→448pp (+32 from amped passages) and invalidated the already-computed `cover_wrap.pdf`; `PAGES` must be bumped to 448 and covers regenerated. ATD literally showed the drift 407→412→416→448 obsoleting covers.
- Exact params/code: Make `PAGES` a SINGLE re-derived variable read from the generated PDF (`ComputeStatistics(2)`), injected into every compositor — never hardcoded in three places (ATD's biggest self-inflicted friction: three different hardcoded PAGES).
- Verify: All compositors read the same freshly-derived `PAGES`.

---

## 6. COVER ART GEN & VERIFY

### 6.1 Default generation path — ComfyUI via the hermes skill + SDXL base
- Rule: Generate cover art programmatically via a ComfyUI runner skill — every path read from `kit_env.cover_gen` (reference machine: the hermes `creative/comfyui` skill v5.1.0). Default checkpoint = **SDXL base ~6.5 GB** (fits a 16 GB GPU comfortably). Flux-dev-fp8 ~12 GB is opt-in for best composition when VRAM is free.
- Why / symptom if violated: `ComfyUI\models\checkpoints\` ships EMPTY (`put_checkpoints_here`) — a checkpoint MUST be fetched before any gen. FERRYMAN does NOT drive ComfyUI (its only on-disk image path is an sd-turbo diffusers smoke test — 1-step, 512-native, too weak for covers).
- Exact params/code:
  ```bash
  comfy launch --background                    # :8188
  curl -s http://127.0.0.1:8188/system_stats   # health
  python scripts/run_workflow.py --workflow workflows/sdxl_txt2img.json \
    --args '{"prompt":"<COVER PROMPT>","negative_prompt":"text, watermark, letters","seed":-1,"steps":30}' \
    --output-dir ./outputs
  ```
  Fetch checkpoint: `stabilityai/stable-diffusion-xl-base-1.0/sd_xl_base_1.0.safetensors` (SDXL) or `Comfy-Org/flux1-dev/flux1-dev-fp8.safetensors` (Flux) via the vendored `python _tools/fetch_weights.py sdxl` (resumable) or `comfy model download`. `run_batch.py --count 8 --randomize-seed` for variations. (sd-turbo diffusers path exists as a last-resort in-process fallback: `AutoPipelineForText2Image.from_pretrained(sd-turbo, torch_dtype=fp16)`, `num_inference_steps=1`, `guidance_scale=0.0`, 512² — gate-quality only.)
- Verify: `run_workflow.py` stdout JSON `{"status":"success","outputs":[{"file":...}]}`; the PNG exists.

### 6.2 NO title/author text in the generated image
- Rule: The art prompt must produce NO title/author/lettering in the image — typography is composited afterward in PIL. Build the prompt from the Book Bible (genre, mood, palette, motifs); enforce period accuracy where relevant; leave focal room for the title (upper third front open).
- Why / symptom if violated: AI-rendered text degrades / is misspelled; competing typography ruins the composite.
- Exact params/code: Negative prompt includes `text, watermark, letters`. Anti-patterns to reject: glossy stock-photo / golden-hour-product lighting, saturated colors & vibrant gradients, hand-drawn/cartoon registers, text-heavy compositions. Aspect **2:3** matches 6×9 (Midjourney `--ar 2:3 --style raw --s 50` covers / `--ar 1:8` spine; Imagen `2:3`; Flux "append warm golden-hour" to fix cool cast).
- Verify: Vision-check the candidate — no lettering, correct subject, focal room for the title (§6.5).

### 6.3 Print resolution + upscale + color
- Rule: For 6×9 @ 300 DPI with 0.125" bleed, art needs **≥ 1875×2775 px** (some sources say ≥1999×2775 for the front). Generators emit 1024×1536 or 2048×3072 → upscale (Topaz Gigapixel / Magnific / Real-ESRGAN) before compositing. Convert sRGB→CMYK (FOGRA39 EU / GRACoL2006 NA) before print submission.
- Why / symptom if violated: Under-resolution prints soft; wrong color space shifts on press.
- Exact params/code: Upscale offline; keep the raw + upscaled source untouched (see §6.4).
- Verify: `PIL Image.size` ≥ target px before compositing.

### 6.4 Preserve source art; composite deterministically in PIL
- Rule: Keep the AI-generated art at full resolution, untouched, SEPARATE from the composite. Re-composite typography FROM the source, never from a baked composite. Compositing is 100% deterministic PIL (no AI at composite time).
- Why / symptom if violated: A title-position tweak must re-composite from source; baking into a composite loses the clean plate.
- Exact params/code: Shared PIL toolkit: `load_font(size, weight)` (variable Cormorant Garamond, `set_variation_by_axes([weight])`, weight axis 300–700, + dedicated Bold TTF); `measure_tracked`/`draw_tracked` (per-glyph hand-kerning — PIL has no native tracking); `scale_to_cover` (fill + center-crop, for full-bleed front art) vs `scale_to_fit` (shrink + letterbox in the cover color, for **content-at-edges** art like a chat screenshot). Title: cream halo stroke (~2% of font px) for legibility across a gradient; tracking ~0.04–0.05em (author 0.18–0.20em wide small-caps). Spine title: `int(spine_px × 0.42)`, weight 700, **double-drawn +1px offset** for stroke weight on thin spines; Mixam spine `int(spine_px × 0.28)`, title-only, no author/ornament. Back panel: art darkened (`RGBA (0,0,0,184)`=72% for Mixam / `(0,0,0,200)` for KDP) for cream-text legibility. Auto-fit: shrink title 4px in a while-loop until inside the quiet zone. Minimal all-PIL cover (no external art) is a valid default for text-forward books (ASTRA-7: navy `#060E1C` + hexagon outline + sans wordmark, zero image-gen).
- Verify: `scale_to_fit` used for edge-content art (not `scale_to_cover`, which crops off a timestamp/edge); source art present alongside composite.

### 6.5 Perceptual vision verify — Claude vision default, KEEL Qwen sovereign fallback
- Rule: After generating art AND after rendering the full wrap, run a perceptual verify: resize ≤2000px, then vision-read for composition / no-text / subject accuracy / focal room (art) and title legibility / correct spelling / tracking / spine centering / bleed-safe / ISBN keep-out clear (wrap). Fail → re-roll (new seed / adjusted prompt); pass → lock.
- Why / symptom if violated: This is the loop that makes it true point-and-shoot — the AI catching its own layout defects before the human uploads. UE5-render vs real was told apart by too-uniform mist/star density and uniform window color temp.
- Exact params/code: **Default** (`--backend auto`) = `resize_image_safe.py` + the harness's own vision/OCR. **Sovereign alternative** (for $0 on-box, when `kit_env.vision` configures one): a KEEL-style Qwen vision server —
  ```
  <kit_env.vision.llama_server> --model <kit_env.vision.qwen_model> --mmproj <kit_env.vision.mmproj> --host 127.0.0.1 --port 8080 --jinja --n-gpu-layers 99 --ctx-size 16384
  ```
  `--mmproj` is THE vision switch (omit it and the server is silently text-only). Poll `GET /health` before the first call. POST OpenAI-format to `/v1/chat/completions` with a text rubric part + `{"type":"image_url","image_url":{"url":"data:image/png;base64,..."}}`; read `choices[0].message.content`. Port 8080 is shared with cognition — confirm the running server was launched WITH `--mmproj`. `--jinja` required for the thinking toggle. grammar/json_schema ⊕ thinking are mutually exclusive (a GBNF/schema forces thinking off; supplying both 400s). Model id in the JSON is cosmetic.
- Verify: Vision returns PASS (title legible + correctly spelled + inside quiet zone) or a specific FAIL reason to re-roll.

### 6.6 ISBN barcode keep-out — draw NOTHING
- Rule: On KDP back covers, reserve a **2.25"×1.5"** keep-out at bottom-right and draw nothing there — KDP auto-overlays its own ~2"×1.2" EAN-13 barcode. Do NOT bake an ISBN or a cream placeholder rectangle. Mixam does NOT auto-stamp (add your own or leave blank).
- Why / symptom if violated: A baked cream placeholder was flagged for removal on Inside-the-Region v2; centered back-cover text collides with the auto-overlaid sticker.
- Exact params/code: Barcode auto-overlay coords for a 6×9 hardcover (recorded): wrap x=[1337,1937], y=[2478,2838]; back-panel x=[1125,1725], y=[2266,2626] (right 33% × bottom 13%). Barcode dodge is TWO independent fixes: (a) shift the centered tagline/byline **220px left**; (b) wrap META/URL lines at **60% panel width** so a long URL can't extend into the barcode X zone. The blurb renderer is adaptive-width: full width above the barcode band, narrower beside it.
- Verify: Vision-check the back panel — no text inside the keep-out; render `_back_with_isbn_zone.png` and inspect.

### 6.7 Cover face + matte finish
- Rule: Cover display face = **Cormorant Garamond** (variable Light 300–700 + dedicated Bold TTF) for literary/cream books; **sans-serif** (Inter Bold / Helvetica Neue Bold) for tech-register books. Choose **matte** finish for literary titles (paperback + hardcover).
- Why / symptom if violated: "Cormorant Garamond is the literary face"; sans signals practitioner utility. "Glossy on literary fiction reads as airport thriller."
- Exact params/code: Cover fonts are NOT embedded in interiors (covers are rasterized flat images — only the cover tool needs the TTFs).
- Verify: The composited cover uses the register-correct face; KDP finish set to matte.

---

## 7. KINDLE / EBOOK

### 7.1 Kindle is a reflowable DOCX with print furniture stripped
- Rule: Kindle output = **DOCX** for direct KDP upload (not epub/PDF). Single section, uniform 1" margins (`1440` all sides, `header 0, footer 0, gutter 0`). **FORBIDDEN:** page numbers, running headers, mirror margins, blank versos, forced rectos — all are print concepts that render as broken empty screens.
- Why / symptom if violated: Print furniture in a reflowable ebook = broken screens; Kindle reflows so page count is meaningless.
- Exact params/code: Chapter delimiter = `new Paragraph({ children:[new PageBreak()] })` (Amazon treats these as chapter boundaries). Body Georgia 12pt (`size:24`), line 340, color `000000`.
- Verify: The DOCX has one section, no mirror flag, no footers with page numbers.

### 7.2 H1 chapters + hyperlinked auto-TOC
- Rule: Style chapter/Part titles `HeadingLevel.HEADING_1` (Amazon scans H1 for the auto-TOC); H2/H3/H4 are styled paragraphs, NOT navigable. Add a navigable TOC field; populate it via Word COM.
- Why / symptom if violated: Without H1 the Kindle TOC doesn't build; docx@9 emits the TOC field but only Word fills it.
- Exact params/code: `new TableOfContents("Table of Contents", { hyperlink:true, headingStyleRange:"1-1", stylesWithLevels:[new StyleLevel("Heading1",1)] })` + `new Document({ features:{ updateFields:true } })`. Post-process `update_kindle_toc.py` (Word COM: `doc.TablesOfContents(i).Update()` → `Repaginate()` → `Save()`).
- Verify: Open in Word; the TOC populates with hyperlinked entries.

### 7.3 Content parity, not page parity; math needs Cambria Math
- Rule: Aim for CONTENT parity with print (same words), never page-count parity (the ~18-page gap is all print-only front matter). Tag every math run `font:"Cambria Math"`. Kindle back matter = an extended About-the-Author (helps discoverability; print often omits it).
- Why / symptom if violated: "Make it 204 pages" is the wrong framing. Math glyphs break on Kindle without an explicit math font (G15). Version drift shipped a Kindle 8,476 words short (§2.8).
- Exact params/code: `kindle_parity_check.py` = word-count diff Kindle-docx vs paperback-docx (ebook may be slightly higher for About-the-Author, never lower).
- Verify: `kindle_parity_check.py` shows parity; equations render (not literal `\`); backtick equations render without literal backticks (§3.3).

### 7.4 Kindle cover = front-only JPG
- Rule: Kindle cover is a separate front-only image: **1600×2560 px** (1.6:1 ratio), sRGB, JPEG q92–95 (< 50 MB — "KDP prefers JPEG").
- Why / symptom if violated: Kindle needs a single front cover, not a wrap; wrong ratio/size rejects.
- Exact params/code: `composite_cover_kindle.py` outputs the front at native res as JPG (and optionally PNG).
- Verify: Image is 1600×2560, sRGB, < 50 MB.

### 7.5 Kindle is immune to print rejections; updates don't auto-push
- Rule: Because the Kindle DOCX is reflowable (no cover wrap, no spine, no gutter), it is immune to every spine/gutter/barcode rejection that hits print formats — ship it first. Note that live Kindle content updates do NOT auto-push to existing buyers.
- Why / symptom if violated: Existing buyers must opt in via "Manage Your Content and Devices" → "Update Available", or you request a proactive push via KDP Help; new buyers always get latest (G14).
- Exact params/code: Ship order: Kindle first (fastest to market), then hardcover interior, reuse for paperback, pad for Mixam.
- Verify: Kindle uploaded independently of print-format status.

---

## 8. DIGITAL PDF

### 8.1 Assemble covers + blank-stripped interior via fitz
- Rule: Build the reader PDF (email/Drive, not for upload) as: page 1 front cover + page 2 back cover (both exact 6×9-pt MediaBox) + interior with every print-only blank verso stripped and redundant front matter removed. Reuse the print interior + the print cover.
- Why / symptom if violated: Print interiors deliberately carry blank versos (ODD_PAGE starts) which read as broken pagination in a digital reader.
- Exact params/code: **Modern (fitz):** build 2 cover pages `fitz.new_page(width=432, height=648).insert_image(...)`; copy interior stripping (a) blank pages (`page.get_text().strip()=="" AND get_images() empty`) and (b) redundant front matter (1-indexed `{2,3,4}` = blank-verso/title/copyright; KEEP half-title p1 as a divider); save `deflate=True, garbage=4, clean=True`. Cover art scaled `scale_to_fit` (letterbox in the cover color at ~200 DPI) so no edge content is cropped. **Legacy (PyPDF2):** Word COM docx→PDF, crop Mixam covers from bleed to trim (`BLEED_PX = int(0.80*300)=240`, `img.crop((240,240,w-240,h-240))`), `PyPDF2.PdfWriter` concatenate front+back+body; `strip_blank_pages.py` drops pages < 30 non-whitespace chars (keeps covers p1–2).
- Verify: `_preview_front.png`/`_preview_back.png` render checks; no blank pages mid-body.

---

## 9. PUBLISHING METADATA

### 9.1 `book_config` / `kdp_metadata` schema
- Rule: Externalize all per-book metadata into one config object, injected everywhere (not hard-coded across 3+ scripts). Fields: `title, subtitle, author, license, trim, paper, finish, body_font, src_md[], cover_art, palette, blurb, tagline, categories[≤3 BISAC], keywords[7 ≤50 chars], description ≤4000 chars, kdp_order_opts, mixam_order_opts, isbn_handling`.
- Why / symptom if violated: Literal blurb/tagline/keyword strings are hard-coded per book today (prime parameterization targets). No repo ships a `kdp_metadata.yaml` — that absence is a gap.
- Exact params/code: Categories max 3 at submit (more via Author Central); Philosophy is NOT top-level in KDP's picker (nest under Politics & Social Sciences). Keywords: 7 slots, ≤50 chars, long-tail, no quotes/commas. Description: HTML (`<p><b><i>` allowed), target just under 4000 (Inside-the-Region tuned to 3,991/4,000). Some KDP fields reject the em-dash → substitute " - ".
- Verify: Config validates; description ≤ 4000 chars; 2–3 categories (floor 2; up to 3 where the live picker offers them — see §18.1/§19.3); 7 keywords ≤ 50 chars each.

### 9.2 Paper / finish / trim defaults by register
- Rule: **6×9 trim** all formats. **Cream** paper = literary/premium; **white** = technical. **Matte** finish for literary. **KDP hardcover is white-only** (cream not offered) → its spine uses the white multiplier.
- Why / symptom if violated: Paper drives the spine-per-page constant (0.0025 cream vs 0.002252 white). Cream KDP-hardcover upload risks rejection.
- Exact params/code: Test-cream-first procedure (if ever attempting cream HC): upload one test wrap as cream; if rejected, fall to white (`pages × 0.002252 + 0.348`).
- Verify: KDP listing paper/finish matches the spine multiplier used.

### 9.3 ISBN — only 2 free KDP ISBNs
- Rule: KDP assigns free ISBNs for **paperback + hardcover only (2, not 3)**. Do NOT request/assume a Kindle ISBN (Amazon assigns an ASIN). No ISBN is hardcoded anywhere. The digital PDF's visible back-cover ISBN is the paperback's, kept intentionally for the "real book" register.
- Why / symptom if violated: A digital PDF showing a paperback ISBN could confuse a scanner if mislabeled; assuming a Kindle ISBN wastes an allocation.
- Exact params/code: Print ISBN placeholders `[pending]` in the copyright markdown until KDP assigns.
- Verify: Kindle has no ISBN; print listings use KDP-assigned ISBNs.

### 9.4 Copyright page + fiction disclaimer + compilation-detector avoidance
- Rule: Copyright page carries license (`CC-BY-4.0` content / MIT tools, per house style) + first-edition line + "Set in Georgia" + (for fiction) the "work of fiction / historical persons appear as characters" disclaimer. Do NOT nest a same-named doc inside a same-named larger book; keep "Book 1" OUT of the subtitle.
- Why / symptom if violated: Amazon's copyright/compilation detector rejected a manuscript that nested a 13K "The Second Notebook" inside a 40K book also titled *The Second Notebook* (+ a tonally-different novella). Fix: split into a series; link via Amazon's series feature after Book 2 ships.
- Exact params/code: Author bio discipline: 3–5 sentences, minimum-factual, no adjectives, no achievements-as-identity. Forbidden-positioning list (per book) the description generator must respect (e.g. NOT "AI girlfriend / companion game").
- Verify: Subtitle carries no "Book 1"; no nested same-name manuscript; fiction disclaimer present.

### 9.5 Pricing / royalty context (reference)
- Rule: Kindle 70% royalty on $2.99–$9.99 (35% otherwise); paperback + hardcover 60% royalty minus print cost. Pricing is a marketing decision, not a math decision.
- Why / symptom if violated: Mispriced Kindle drops out of the 70% tier.
- Exact params/code: 6×9 cream B&W ~190pp: paperback print ~$4.50, hardcover ~$8.50. Examples: Inside-the-Region Kindle $5.99, HC $17.94; City Kindle $0.99.
- Verify: Kindle price in $2.99–$9.99 if 70% desired.

### 9.6 Secrets handling — never embed a PAT in a command string
- Rule: Use `gh auth` keyring for GitHub pushes; NEVER embed a Personal Access Token in a URL inside a command string. If a secret leaks into a transcript, rotate immediately.
- Why / symptom if violated: PAT tokens embedded in `git push https://user:ghp_...@github.com/...` URLs persisted in the chat/transcript across ≥4 pushes (plus an `hf_...` token) — an at-rest credential leak.
- Exact params/code: `gh auth status` should confirm keyring auth with `repo` scope; push over keyring/HTTPS.
- Verify: No `ghp_`/`hf_` substrings in any command string or transcript.

---

## 10. VERIFICATION LOOP

### 10.1 Word COM is the ONLY reliable docx→PDF (Edge-headless HTML fallback)
- Rule: Convert docx→PDF ONLY via Word COM. Pandoc, LibreOffice-headless, and docx2pdf-cloud all corrupt (font substitution, broken TOC hyperlinks, mis-paginated headers). A documented fallback exists for HTML→PDF (not a drop-in docx converter) when Word is unavailable.
- Why / symptom if violated: Every non-Word converter breaks TOC + fonts + pagination. This is the single biggest portability constraint (Windows + installed Word).
- Exact params/code:
  ```python
  word = win32com.client.Dispatch("Word.Application"); word.Visible=False; word.DisplayAlerts=0
  doc = word.Documents.Open(str(DOCX.resolve()))
  # update TOC + fields by index (§3.7) + Repaginate() first
  page_count = doc.ComputeStatistics(2)   # 2 = wdStatisticPages
  doc.SaveAs(str(PDF.resolve()), FileFormat=17)   # 17 = wdFormatPDF
  doc.Close(SaveChanges=False); word.Quit()
  ```
  Edge fallback (HTML→PDF): `msedge --headless=new --disable-gpu --no-pdf-header-footer --user-data-dir=<freshTmp> --print-to-pdf=<out.pdf> "file:///<abs/in.html>"` (fresh user-data-dir, wait for exit).
- Verify: PDF opens with intact TOC hyperlinks + correct pagination; `ComputeStatistics(2)` returns the page count that feeds spine math.

### 10.2 Verify by SEEING without burning context
- Rule: Prefer mechanical checks that don't spend image tokens: XML zipfile inspection (mirror flags in `settings.xml`, empty headers in `header*.xml`), pypdfium2 dark-column / charbox scans (gutter overshoot), Word-COM `ComputeStatistics(2)` (page count), and the KDP Print Previewer (external validator). Use vision only for the perceptual cover/interior proofread.
- Why / symptom if violated: A prior session DIED because too many inline screenshot tool-calls filled the context window.
- Exact params/code: Image discipline — user/kit drops files in an `image_input/` dir; Read from DISK path; write outputs to a subdir; NO image bytes go back into chat. Render suspect print pages to PNG (`_overflow_p*.png`, `_check_p*.png`, `_back_with_isbn_zone.png`) and vision-inspect for text overflow / bleed / ISBN-zone.
- Verify: Each format run prints its computed dims banner (target vs actual inches) before upload; KDP Previewer is the gate ("if it passes the previewer, it passes review").

### 10.3 Image ingestion 2000px hard cap
- Rule: Pre-resize EVERY image to ≤2000px in both dimensions before ANY `Read`/vision call.
- Why / symptom if violated: An image >2000px in any dimension aborts the conversation non-recoverably: *"An image in the conversation exceeds the dimension limit for many-image requests (2000px)."* Cover wraps are ~4255×3125 (HC) / ~3801×2775 (PB) and always trip it.
- Exact params/code: `_tools/resize_image_safe.py` — echoes the path unchanged if ≤2000px both dims; else LANCZOS-downsamples into a 2000² box, saves with a `_r2k` suffix, prints the safe path. Safe to run unconditionally. (A vendored equivalent of the reference machine's imguard organ.) For covers specifically: PIL `Image.thumbnail` to ≤1800×1800, save `_preview_*.jpg`, Read the preview, then clean up.
- Verify: Every path handed to `Read` is confirmed ≤2000px.

### 10.4 Canonical build order
- Rule: Run: (1) lint MD (`lint_manuscript.py` exit 0) + vocabulary/em-dash gates → (2) generate interiors (Kindle DOCX / KDP-PB DOCX / Mixam DOCX) → (3) JSZip-inject mirror margins + vAlign → (4) Word COM → PDF for print, **read page count FIRST** → (5) update the single `PAGES` variable in every compositor from the actual count → (6) compute spine → (7) composite covers (KDP-PB wrap / KDP-HC wrap / Mixam 3-panel) → (8) build digital PDF (reuse print interior + print cover) → (9) Kindle parity check → (10) verify (`check_part_pages.py` recto + preview thumbnails + KDP Previewer dry-run) → (11) print dimension report. Paperback + hardcover share a byte-identical interior.
- Why / symptom if violated: Composing covers before the page count is final wastes iterations (spine depends on page count).
- Exact params/code: Per-format command sequence example (hardcover): `node generate_book_kdp_hardcover.js && python update_hardcover_and_count.py && python composite_cover_kdp_hardcover.py`.
- Verify: The internal loop converges to one-shot-clean (every mechanical assert green + vision PASS) before the folder is surfaced.

### 10.5 Turn every gotcha into a build-time assert
- Rule: Before declaring ANY format done, assert: mirror flags present; non-body sections have empty headers/footers; page count meets the format multiple; gutter ≥ 0.75"; cover filenames carry routing keywords; Kindle + print read the same version; cover MediaBox 4-decimal-exact; ISBN keep-out clear.
- Why / symptom if violated: A fix rediscovered ≥3× MUST be promoted to a persistent reference and a build-time assert at solve time — inline fixes die with the project (Inside-the-Region cost 4 rejected hardcover rounds because fixes weren't pre-baked).
- Exact params/code: the invariant runners that already exist — `_tools/verify_build.py --config book_config.json --format <p>` (per-format mechanical gate; runs the mirror/empty-header/page-multiple/gutter/cover-dimension asserts), `_tools/check_part_pages.py` (recto parity), and `_tools/selfcheck.py` (the kit self-consistency meta-gate) — each reports green/red and exits nonzero on FAIL.
- Verify: All asserts green (the FIRST-PASS DEFAULTS CHECKLIST, §14).

---

## 11. CROSS-PLATFORM / RUNTIME

### 11.1 Hard Windows + Word dependency; document it
- Rule: The pipeline is Windows 11 + installed Microsoft Word (COM) locked. Python 3.10+ with `win32com, PIL, PyMuPDF (fitz), PyPDF2`; Node 18+ with `docx@9.6.1` + `jszip@3.10.1`.
- Why / symptom if violated: Word COM has no faithful cross-platform equivalent; Mac/Linux would need a portable DOCX→PDF fallback (not implemented — the Edge-headless path renders from HTML, not docx).
- Exact params/code: For FERRYMAN subprocesses (and any CJK-printing stage), set `PYTHONUTF8=1` + `PYTHONIOENCODING=utf-8` — a CJK print inside a stage can crash a cp1252 console and silently skip work with exit 0.
- Verify: `win32com.client.Dispatch("Word.Application")` succeeds; UTF-8 env set for image/text subprocesses.

### 11.2 Vendor fonts repo-relative — do NOT hard-reference C:\Claude-Titanic\fonts
- Rule: Bundle the cover TTFs INTO the kit repo and reference a repo-relative path. Interiors rely on system Georgia (fonts NOT embedded — covers are rasterized).
- Why / symptom if violated: Every prior repo hard-references `C:\Claude-Titanic\fonts\`; `C:\BOOK\fonts\` and `C:\BOOK3\fonts\` are EMPTY — a portability landmine (the cross-repo path is load-bearing and breaks if that repo moves).
- Exact params/code: Ship `CormorantGaramond-Light.ttf` (variable, weight axis 300–700) + `CormorantGaramond-Bold.ttf`; plus a sans title face (Inter/Helvetica Neue Bold) for tech books. `Segoe UI Symbol` (seguisym.ttf) for `✦`.
- Verify: Compositors load fonts from a repo-relative `fonts/` dir; no absolute cross-repo path.

### 11.3 Mixam filename keyword routing is SILENT
- Rule: Name Mixam cover files by keyword: `front_cover.pdf`, `back_cover.pdf` (or `rear_cover`/`outer_back_cover`), `spine.pdf`; name the body `inner_<title>.pdf`. NEVER name a file bare `back.pdf`.
- Why / symptom if violated: Mixam parses filenames to auto-route slots WITHOUT warning: bare `back.pdf` routes to interior **Body Page 1**; `<title>.pdf` without `inner_` is inconsistent/errors.
- Exact params/code: Routing table — `front`→front cover; `back` alone→interior body; `back_cover`/`rear_cover`/`outer_back_cover`→back cover; `inner`→body; `spine`→spine.
- Verify: All Mixam deliverables carry the routing keywords before upload.

### 11.4 Backup + run-state discipline
- Rule: Before every edit round, snapshot the manuscript to `backups/YYYYMMDD_HHMM_<desc>/`. Keep a single append-only run-state file (`SESSION_MEMORY.md` / `BUILD_LOG.md`) with locked decisions + chronological addenda + word-count deltas. A `RESUME.md` (or `_warm_start.md`) gives an ordered cold-start load sequence (constraints → spec → voice anchor → prior units in order → session memory), ~75–95K tokens, resumable with one line: "Resume per RESUME.md and proceed to unit [N]."
- Why / symptom if violated: Order matters because constraints prime voice; nothing should be unrecoverably overwritten.
- Exact params/code: Promote any fix rediscovered ≥3× to a persistent `reference_*.md` memory file at solve time.
- Verify: A timestamped backup exists before each edit; `RESUME.md` boots a fresh session cleanly.

---

## 12. AUDIOBOOK (bonus stage — the one missing pipeline half)

### 12.1 PDF → TTS chunker via geometry clustering
- Rule: To turn a finished text-layer book PDF into narration-ready input, reconstruct paragraph/scene structure from vertical-gap clustering + a font-size sanity check + hyphen classification; emit size-bounded chunks preferring scene boundaries.
- Why / symptom if violated: A PDF encodes scene breaks only as whitespace; naive splitting mis-narrates. This is the one production stage absent from the print/ebook pipeline.
- Exact params/code: `pdf_to_tts.py` (PyMuPDF `import fitz`). Gap tiers (clean valleys): **≤20 px = line-wrap** within a paragraph · **23–29 = paragraph break** · **37–54 = scene break**. Font-size histogram sanity check (only body ~10.5pt + one title 18pt ⇒ no hidden headings ⇒ continuous prose). Dehyphenation: classify wrap-hyphens vs real compounds before rejoining. `chunk_items(items, title, max_chars)` groups paragraphs into ≤`max_chars` segments preferring scene boundaries. CLI: `pdf_to_tts.py IN.pdf --outdir DIR --title "..." --stem slug --max-chars 4500`. Emits TTS-clean plaintext + reference markdown + `tts_chunks/*.txt`. Target: ElevenLabs Studio.
- Verify: Chunk count ≈ scene count; no chunk exceeds `max_chars`; hyphenated compounds preserved.

---

## 13. UNRESOLVED / RECONCILED NUMERIC CONFLICTS

Recorded with provenance; safe default stated. The overriding rule for all of these: **calibrate against the KDP Print Previewer's stated number.**

1. **KDP hardcover board add — 0.302 vs 0.348 vs 0.246 vs 0.241.**
   - `0.302"` — Titanic-era `PRODUCTION_LESSONS_LEARNED.md` (2026-04-20) and pre-fix handoffs (2026-04-22). **Known-wrong / superseded** — caused v1 rejections.
   - `0.348"` — ATD 2026 spec, empirically calibrated against ATD's KDP Print-Previewer rejections (`composite_cover_atd_kdp_hardcover.py`: `HARDCOVER_BOARD_ADD_IN = 0.348`). **SAFE DEFAULT for white HC:** `pages × 0.002252 + 0.348`.
   - `0.246"` / `0.241"` — Inside-the-Region, refined across 3 rejections (`pages × 0.0025 + 0.241` at 426pp). This is an all-in formulation (different turn-in model) and does NOT extrapolate.
   - **186pp counter-example (ASTRA-7):** `pages × 0.0025 + 0.241` gave 0.706" but KDP demanded **0.767"** (rejection *"expected 14.183, got 14.123"*). **Conclusion: the constant term is page-count-dependent — do NOT reuse a spine constant across page-count bands. Compute a first guess with 0.348, then hardcode KDP's stated spine (`SPINE_OVERRIDE_IN`), reverse-derived as `stated_wrap_width − 12 − 1.416`.**

2. **KDP hardcover wrap HEIGHT — 10.416 (arithmetic) vs 10.417 (validator).** Arithmetic `0.708+9+0.708 = 10.416`, but the KDP validator expects **10.417"**. **SAFE DEFAULT: hardcode 10.417"** (the validator is canonical).

3. **Mixam board add — 0.160 vs 0.130 vs 0.110.** Non-constant across page counts (0.160@204pp, 0.130 est. mid, 0.110@548pp). **NO SAFE CONSTANT — read Mixam's job calculator and use its spine value; regenerate spine.pdf only.**

4. **Body point size — 12pt vs 11pt.** 12pt/340-DXA leading (Night Was Young, Mixam, Kindle) vs 11pt/320-DXA (City, Second Notebook, ATD paperback). **Both pass KDP** — a per-book register call, not a conflict. Default: 12pt for novellas/premium, 11pt for denser books.

5. **KDP paperback gutter — 0.625 vs 0.75.** 0.625" (1080 was later; some early notes 900) vs **0.75" (1080 DXA)**. **SAFE DEFAULT: 0.75"** — absorbs ~2.7pt trailing-space + ~2pt italic side-bearing overshoot that trips "insufficient gutter" at 0.625" exact.

6. **Front print resolution minimum — 1875×2775 vs 1999×2775.** `1875×2775` (300 DPI, 6×9 + 0.125" bleed, general) vs `≥1999×2775` (Inside-the-Region front spec). **SAFE DEFAULT: ≥1999×2775** (the higher bar) then upscale as needed.

7. **Superseded canon file.** `C:\Claude-Titanic\PRODUCTION_LESSONS_LEARNED.md` (2026-04-20) is **superseded** by `C:\ASTRA-7\book\production_lessons_learned.md` (2026-05-15, §1–§18). Track the ASTRA-7 numbers (0.348 board, validator-wins wrap, matte finish, G1–G16).

*No genuinely unresolvable conflicts remain — every number above has a stated safe default plus the meta-rule (calibrate against the Previewer). The one irreducible truth: hardcover spine constants are page-count-band-dependent and must be Previewer-calibrated per book.*

---

## 14. FIRST-PASS DEFAULTS CHECKLIST (run before declaring ANY format done)

**Manuscript / voice**
- [ ] `lint_manuscript.py` exit 0 (no round-trip corruption artifacts).
- [ ] Vocabulary lint exit 0; `Grep "[—–]"` clean (check headers + `[BO-WRITES]` leak sites).
- [ ] Refrain appears at exactly its designated placements; word counts within ±20% of contract.
- [ ] No surviving `[BO-WRITES]` markers; Class-A units are outline-only.
- [ ] All generators read the SAME version-pinned markdown; `kindle_parity_check.py` parity.

**Interior (docx / OOXML)**
- [ ] Body 6×9, Georgia, correct pt/leading; parser splits backticks BEFORE italics.
- [ ] `<w:mirrorMargins/>` + `<w:evenAndOddHeaders/>` present in `settings.xml` (unzip-grep) AND `pgMar` gutter on the correct side.
- [ ] Every header/footer-free section has explicit empty Header/Footer objects (`header*.xml` shows `[]`); trailing blank is a truly-empty paragraph.
- [ ] `<w:vAlign>` injected on ceremonial front-matter sections (each its own section).
- [ ] Word-COM converter updates fields BY INDEX in try/except (no live-iterator crash).

**Margins & recto**
- [ ] KDP margins 0.5/0.625/**0.75**/0.5 mirror; Mixam 0.625/0.75/0.875/0.625.
- [ ] Every chapter/Part `SectionType.ODD_PAGE`; trailing `SectionType.EVEN_PAGE`; `check_part_pages.py` all recto.
- [ ] Page count: KDP ×2, Mixam ×4 (fitz-padded).

**Spine & cover geometry**
- [ ] `PAGES` re-derived from the generated PDF (`ComputeStatistics(2)`), injected into every compositor (never 3 hardcodes).
- [ ] Spine: cream `×0.0025` / white `×0.002252`; KDP-HC `+0.348` (then Previewer-calibrated `SPINE_OVERRIDE_IN`); Mixam from Mixam's calculator.
- [ ] KDP-HC wrap 0.708" turn-in (NOT bleed), height hardcoded **10.417"**; KDP-PB / Mixam-interior bleed 0.125"; Mixam cover bleed 0.80".
- [ ] Cover PDF MediaBox exact via PyMuPDF (4-decimal), NOT PIL.
- [ ] Typography ≥ bleed+0.25" from every edge; ISBN keep-out (2.25"×1.5" bottom-right) clear, nothing baked.
- [ ] Mixam filenames: `inner_*.pdf` / `front_cover.pdf` / `back_cover.pdf` / `spine.pdf` (never bare `back.pdf`).
- [ ] Cover regenerated after ANY interior change; not reused across services.

**Cover art**
- [ ] Art has NO title/author text; upper-third-front focal room; ≥1999×2775 px, sRGB→CMYK.
- [ ] Source art preserved untouched; composite re-derived from source; `scale_to_fit` for edge-content art.
- [ ] Perceptual vision verify PASS (art: no-text/subject/focal room; wrap: title legible+spelled, tracking, spine centered, bleed-safe, ISBN clear) — Claude vision default, KEEL Qwen fallback.

**Kindle / digital**
- [ ] Kindle DOCX: single section, no page numbers/headers/mirror/versos/rectos; H1 chapters + hyperlinked TOC populated via Word COM; math tagged Cambria Math; cover 1600×2560 JPG.
- [ ] Digital PDF: front+back covers (exact 6×9-pt) + blank-stripped interior; preview thumbnails render.

**Metadata / runtime**
- [ ] `book_config`/`kdp_metadata` validates: 2–3 categories (floor 2, max 3; §19.3), 7 keywords ≤50 chars, description ≤4000, paper/finish/trim set, em-dash-free where KDP rejects it.
- [ ] Only 2 free ISBNs assumed (PB+HC); no Kindle ISBN; no ISBN hardcoded.
- [ ] No same-name nested manuscript; "Book 1" out of subtitle; fiction disclaimer on copyright page.
- [ ] No secrets in command strings (`gh auth` keyring).
- [ ] Fonts loaded repo-relative; UTF-8 env set; Word COM available.
- [ ] KDP Print Previewer dry-run accepts paperback + hardcover before publish.

*When every box is checked and the internal loop is one-shot-clean, surface the finished folder to the user.*

---

## 15. SESSION SURVIVAL & COMPACTION

*Added 2026-07-11 from the first real book run ("The Unfinished Mirror", `book_workspace/unfinished_mirror/`), which survived a mid-book overnight quota exhaustion and a cross-project resume with zero lost words. Mechanism spec: `docs/COMPACTION_SURVIVAL.md`.*

### 15.1 Unit-atomic write-to-disk (the survival primitive)
- Rule: Write every completed unit to disk the instant it is done — chapter prose to `manuscript/current/`, subagent digests to `canon_refs/_digest_*.md` — and rewrite `_CONTINUITY.md` immediately after. Subagents write their output file BEFORE returning their summary (write-then-return). Finished work never lives only in context.
- Why / symptom if violated: A quota exhaustion killed the proving session mid-book overnight; ZERO words were lost because every chapter and digest was already on disk — including files left by digest subagents that themselves died at the quota. Context is volatile; disk is the only durable layer.
- Exact params/code: One file per unit (`ch_NN_current.md`); `_CONTINUITY.md` carries a RESUME PROTOCOL at the top plus STATUS / DONE / NEXT / live invariants, rewritten after EVERY unit (header counts included — a stale DONE line is a resume hazard).
- Verify: After each unit: the file exists nonzero on disk, and `_CONTINUITY.md`'s DONE list matches `manuscript/current/` exactly (count, names, and word totals).

### 15.2 Rehydrate from the session's own transcript, never from a summary (the compaction primitive)
- Rule: On any compact/resume with an in-flight book, reconstitute from the session `.jsonl` via `_tools/rehydrate.py` (tiers: strip-thinking → +no-tools → +tail-turns, escalating only as far as needed to fit the token budget), and READ `_REHYDRATION.md` + `_CONTINUITY.md` + `seed.md` before writing any prose. The converted transcript is higher-fidelity than any summary because it *is* the record (~10× smaller than the raw jsonl).
- Why / symptom if violated: Hand summaries lose the specifics that voice and continuity depend on. Measured: a 6.26 MB session jsonl → ~156K tokens at Tier 1 (tools preserved). The hooks make recovery automatic: `PreCompact` snapshots the ledger and pre-bakes `_REHYDRATION.md`; `SessionStart` injects a hard STOP block on compact/resume.
- Exact params/code: `.claude/settings.json` hooks → `_tools/on_precompact.py` / `_tools/on_session_start.py`. CROSS-PROJECT resumes need an explicit `--session <path>` — auto-find targets the current project's (possibly empty) transcript; the proving book's 8-chapter history lived under a different project's slug than the kit's own (record the exact `--session` path in the workspace's `_RESUME_NOTES.md`).
- Verify: `rehydrate.py` prints the tier chosen + token count; `_REHYDRATION.md` exists in the workspace; the SessionStart STOP block fires on `compact`/`resume` whenever any `_CONTINUITY.md` STATUS != COMPLETE.

### 15.3 Model policy under fan-out (prose in the main loop; subagents one tier down)
- Rule: Book prose is written by the MAIN loop only (whatever premium model the session runs). Every fan-out subagent — source digestion, tool-building, audit passes — runs **opus or sonnet, never the premium main-loop model**, unless explicitly overridden by the user.
- Why / symptom if violated: The proving run exhausted its quota overnight; premium-model subagent fleets multiply burn on work that does not need the top model. And prose drafted by many hands breaks the single-authorial-act illusion — the main loop holds the whole book in context; subagents do not.
- Exact params/code: Agent calls pass an explicit `model:` (sonnet for digestion; opus for judgment-heavy audits). The policy is stated in `START_HERE.md` §0 and in each book's `_CONTINUITY.md` MODEL POLICY block.
- Verify: Spot-check spawned agents' models in the transcript; digests exist on disk even when an agent dies mid-run (15.1 write-then-return).

---

## 16. LATE-CAPTURED IDIOSYNCRASIES (2026-07-12 — Bo's post-first-book review)

*These were solved repeatedly in Bo's hand-built books but MISSED by the original transcript mine that seeded this ledger. The mine was **grep-keyed to loud KDP REJECTION phrases** ("insufficient gutter", "text outside margins", "Mixam", "spine width") — and every rule below is a quiet **convention/aesthetic** with no rejection vocabulary to light it up, so the keyword sweep never surfaced it.*

**META-RULE for any future lessons-scan:** hunt conventions and aesthetics, not only rejections. Grep for `spine font` / `too small` / `centered` / `page number` / `contents` / `TOC` / `looks` / `no TOC` / `binder` — not just error strings. A fix that shipped without an Amazon complaint (the author just said "make it bigger / center it / drop the TOC") is invisible to a rejection-keyed miner and is exactly where the residual idiosyncrasies hide.

### 16.1 Spine text font is a DYNAMIC function of page count — thin books get an illegible spine  ✅ CODED (2026-07-12)
- Rule: Spine font size scales with spine width, which scales with page count (`spine_in = pages × per_page + board_add`). A thin book → thin spine → tiny, unreadable spine title. `composite_cover.py` sets spine font ≈ `int(spine_px × 0.42)` (KDP) / `× 0.28` (Mixam); at a 0.185" spine (74pp cream) that renders far too small.
- Why/symptom: Bo repeatedly enlarged the spine font by hand on thin books; **the #1 idiosyncrasy Bo flagged as missed.** A spine title too small to read is unprofessional.
- Fix (in `composite_cover.py` `render_spine`): clamp spine font to a legible floor, AND — because KDP only permits spine text at **≥0.0625" spine width (KDP's page-count form is ~79–80pp; the code gates on width, not pages — see §18.1)** — render a BLANK spine (no text) below that threshold rather than an illegible one. The 75-page floor (§16.5) keeps most books out of the ugly-thin-spine zone but does not by itself guarantee legibility; the clamp is still required.
- Coded: module constant `SPINE_TEXT_MIN_IN = 0.0625`; `render_spine` computes `spine_in = spine_w_px / DPI` and returns a solid dark face (no text) below it — placed INSIDE the shared renderer so it also guards the KDP-wrap / KDP-hardcover / Mixam-3-panel paths, which (unlike `build_flat_wrap`'s stricter 0.25" `spine_blank_below_in`) had no per-profile blank rule. Legible floor: title fill fraction 0.40 → **0.55** and the overflow-prone fixed `max(24, …)` px floor REMOVED (a constant px floor can exceed a thin spine's width and overflow the rotate; the fraction keeps the glyph inside the spine at any legal width, and sub-threshold is already blank). Author/ornament scale off the title via `measure_block()`.
- Verify: `vision_verify` the spine — text legible OR intentionally blank; never tiny. **Tested 2026-07-12 on testvoyage**: 18pp (0.0433" spine) → BLANK (0/8325 core px above text luminance, uniform dark ~24); 120pp (0.30"/90px spine) → legible title, 35px glyph band centered on the 90px spine.

### 16.2 Page numbers CENTERED at the foot, not outer-edge (house style)  ✅ CODED (`interior.page_number_align`, default center)
- Rule: House style puts the page number **bottom-center on every page** (confirmed: *The Autotelic Disposition* p.217 → "217" centered). BOOKSMITH's `generate_book.js` right-aligned recto / left-aligned verso (outer corner) — wrong for this house.
- Fix: `generate_book.js` footer factory (~line 678) — `AlignmentType.CENTER` for the page-number paragraph on both recto and verso. Config knob added: `interior.page_number_align` (enum center|outer, default **center**).
- Verify: rendered spot-check — page number bottom-center on both recto and verso.

### 16.3 The print TOC must not garble — long tracked-caps titles wrap and collide with leaders  ✅ CODED (2026-07-12)
- Rule: Chapter titles rendered in wide-tracked ALL-CAPS ("CHAPTER ONE — THE VIEW FROM SOMEWHERE") wrap to two lines in the Contents and collide with the dot-leaders + page numbers → a garbled TOC. Bo's nonfiction uses **title-case** headings ("Chapter 13: The Entropy Engineer"), single line, moderate tracking.
- Fix (in `generate_book.js`): (a) TOC entries title-case at normal tracking, NOT wide-tracked all-caps; (b) a proper right tab stop with dot leader so the page number aligns cleanly even if a title wraps; (c) gate the whole TOC behind `interior.include_toc` (default true). Also consider restyling the chapter *heading* itself to title-case + colon (not wide-caps + em-dash), which both fixes the TOC and reads better.
- Coded: Word's auto-`TableOfContents` copies the Heading-1 *text* verbatim, so the fix lives at the HEADING, not a separate TOC style. `createUnitHeading` now renders `unitHeadingText(title)` — drops `.toUpperCase()` (keeps the manuscript's own title-case) and swaps a spaced em/en-dash separator for a colon via `.replace(/\s+[—–]\s+/, ": ")` — at light `characterSpacing: 20` (was 60). Word's built-in TOC style supplies the right-tab dot leader automatically once entries are single-line. The section is gated by `const includeToc = !(config.interior && config.interior.include_toc === false)`. Recto parity is unaffected: `check_part_pages.py` default discovery enumerates Heading-1 *outline-level* paragraphs (casing/text-independent), not a text Find.
- Verify: rendered Contents page — each entry clean, number right-aligned, no collision, no ugly wrap. **Tested 2026-07-12 on testvoyage**: Contents shows three single-line title-case entries ("Chapter One: Departure … 1", "… Two: The Crossing … 3", "… Three: Landfall … 5") with aligned dot leaders + right-aligned page numbers; body heading renders "Chapter One: Departure" (title-case, centered) with the centered page number intact.

### 16.4 KINDLE / some ebook upload paths: NO manual TOC page AND NO page numbers  ✅ CODED (2026-07-12)
- Rule: For Kindle / reflowable uploads, Amazon builds navigation from the Heading-1 structure itself; a **manual "CONTENTS" page + TableOfContents field is redundant and, for some KDP upload paths, must be OMITTED** (it renders as a broken/blank screen or a dead page-numbered list — page numbers are meaningless in reflow). Page numbers must ALSO be absent. BOOKSMITH already suppresses Kindle page numbers (`generate_kindle.js` header:0 footer:0 ✓) but STILL injected a manual CONTENTS + TableOfContents (~lines 375–381).
- Why/symptom: Bo flagged this explicitly — *"for some versions of kindle upload you specifically do NOT put TOC and do NOT put page number."*
- Fix: gate the CONTENTS + TableOfContents block behind `kindle_include_toc` (default **FALSE** — rely on Amazon's H1 auto-nav; set true only for an upload path that wants an embedded TOC). NEVER add page numbers to Kindle.
- Coded: `generate_kindle.js` — `const includeToc = config.kindle_include_toc === true` gates the PageBreak + CONTENTS heading + `TableOfContents` block; `features.updateFields` is also gated on `includeToc` (with no TOC there is no field to fill). Chapter headings stay Heading-1 (unchanged casing — reflow has no TOC-collision problem, so §16.3's de-garble is print-only).
- Verify: Kindle DOCX has no page numbers (✓) and, by default, no manual CONTENTS page; H1 headings present for Amazon auto-nav. **Tested 2026-07-12 on testvoyage**: `document.xml` has 0 "CONTENTS" occurrences, 0 TOC field, 3 Heading-1 paragraphs.

### 16.5 MINIMUM 75-PAGE FLOOR  ✅ CODED (`verify_build.py` `check_book_min_pages`, `book_config.min_pages` default 75)
- Rule: No book ships under **75 interior pages** unless explicitly approved. Thinner → illegible spine (§16.1), reads as a pamphlet, undersells the work. Enforced as a HARD `verify_build` check (fails the print gate); override only by setting `book_config.min_pages` lower (a recorded, deliberate exception) or 0 to disable.
- Why/symptom: *The Unfinished Mirror* (2026-07-12) came out 74pp — just under, dense-by-design — and Bo set a hard floor so no future instance ships thin by accident. Prevention is upstream: the DRAFT stage should target ~28–34K words for 6×9 (~250–320 words/page → ~110–135pp).
- Verify: `verify_build --format <print>` → `book_min_pages` pass, or a recorded `min_pages` override.

*Status key: ✅ coded · ⬜ generator TODO. As of 2026-07-12 all of §16.1–§16.5 are CODED and tested on `book_workspace/testvoyage/`: §16.1 spine blank-below-0.0625" + legible 0.55 fill (`composite_cover.py` `render_spine`), §16.2 centered page numbers (`generate_book.js`), §16.3 de-garbled title-case auto-TOC gated by `interior.include_toc` (`generate_book.js`), §16.4 Kindle TOC omitted by default via `kindle_include_toc` (`generate_kindle.js`), §16.5 75-page floor (`verify_build.py`).*

---

## 17. AUTHOR VOICE — the idiosyncrasies that live in the author's MEMORY, not the sources (2026-07-12)

*The failure that forced this section: the first book the kit produced (The Unfinished Mirror) was saturated with em-dashes — Bo's explicitly named "AI signature that is blatantly obvious" — because (a) the rule lived only as prose guidance and a per-book blacklist nobody set, and (b) the kit's ingest read the SOURCE documents but never read the AUTHOR'S accumulated voice/feedback memory, where the rule actually lives. Four OPUS agents then READ (not grepped) the whole voice canon; the result is `docs/author_voice/AUTHOR_VOICE_Bo_Chen.md` + four `_voiceprofile_*.md` detail files.*

**THE META-RULE (root cause).** At INGEST/SEED the harness MUST READ the author's voice canon — `docs/author_voice/AUTHOR_VOICE_<author>.md` AND the author's accumulated memory/feedback files (`~/.claude/projects/*/memory/feedback_*.md`, soul/voice/house-style docs) — BEFORE writing the voice spec. Voice preferences do NOT live in the source documents; matching a source's punctuation (the theory doc's heavy em-dashes) instead of the author's voice is exactly the error that shipped. A language-agent fan-out that greps for keywords instead of READING this corpus defeats its own purpose — the whole point of an Opus reader is contextual understanding, not keyword extraction a script could do.

### 17.1 NO em-dashes / en-dashes — ✅ HARD GATE (`lint_manuscript.py`, `voice.no_em_dashes` default true)
- Rule: zero U+2014 (—) / U+2013 (–) in prose. Bo's #1 named AI-tell (2026-04-22; corroborated in ≥3 separate memories). Strip at DRAFT time, not revision time. Route the pause to a comma / colon / period / semicolon / parentheses — **the semicolon is Bo's real substitute** (~110 per 10k words in his reference book). Compound-adjective hyphens (U+002D) are fine.
- Empirical (measured, not asserted): The Autotelic Disposition = 0 em-dashes / 124,933 words; ASTRA-7 = 0 / 44,876. Inside the Region (older) had 598 — do NOT use it as the voice reference. The ban is a house rule Bo already meets; target the Autotelic register.
- Enforce: the hard em-dash gate in `lint_manuscript.py` (exit 1) + `book_config.voice.blacklist` atoms + the `Grep "[—–]"` backstop over the assembled master, headers, and `[BO-WRITES]` markers. VERIFIED 2026-07-12: the gate fires on every chapter of The Unfinished Mirror (it would have blocked the ship).

### 17.2 Other author HARD rules (from the read corpus)
NO interior images (text only between the covers). NO bullets / sub-headers / summary-boxes / "Key Takeaways" inside prose. NO meta-openers ("In this chapter we will explore…") / content-warnings / author's-notes. NO hedging. NO ascending three-part parallels (tricolons — a Bo-named tell; "crap no human would write"). Forbidden-phrase blacklist: delve, crucial, landscape, paradigm, holistic, cutting-edge, game-changer, empower, leverage/harness-as-verb, tapestry, nuanced, multifaceted, journey, unpack, "key takeaways", "it's important to note", "moreover". Refrain + sacred lines verbatim-locked (exact wording + placement count). Class-A units = outline only. Do NOT "correct" Bo's own-voice misspellings (they are fingerprints in `[BO-WRITES]`/informal passages). The single load-bearing spec: *"the book must read as one person wrote it with continuous attention across a single creative act."*

### 17.3 The voice fingerprint (a verifier can measure)
F1 em/en-dash == 0 (HARD) · F2 semicolon density ≥ 40/10k · F3 no bullets/meta artifacts (HARD) · F4 the hammer (≥ ~12% sentences ≤ 5 words; long-accumulate → short-land) · F5 idiolect markers present ("which is to say", "in the sense that", "not X, not Y", colon-thesis openers) · F6 no tricolons. Full profile + drop-in `book_config.voice` block: `docs/author_voice/AUTHOR_VOICE_Bo_Chen.md`.

---

## 18. DELTAS FROM THE READ-NOT-GREPPED SWEEP (2026-07-12) — what the grep-built kit missed

*Bo flagged that the kit's original build grep-mined and SKIPPED the crystallized memory (esp. `~/.claude/projects/C--Claude-Titanic/memory`, 25 files). Four OPUS agents then READ that memory + every `PRODUCTION_LESSONS_LEARNED.md` + `C:\BOOK\BUILD_LOG.md` IN FULL and diffed against §1–§17. Verdict: the loud mechanical gotchas WERE captured (the kit is not junk; several ledger values are deliberately STRONGER than the sources — 0.75" gutter, page-count-band board-add, repo-relative fonts, the em-dash gate — do NOT revert those). The real deltas cluster in the QUIET-CONVENTION layer (§16's blind spot) and the WRITING-CRAFT layer grep is blind to. Detail with verbatim quotes + sources: `docs/_lessons_audit/_delta_*.md`.*

### 18.1 Corrections — the kit had these WRONG or imprecise
- **KDP categories at submit: safe floor 2, but 3 is attested for nonfiction (ATD shipped 3) — anchor to the LIVE KDP picker on the run date; see §9.1 and §19.3.**
- **KDP spine-text floor = 80 pages**, not 79 (Second Notebook cleared "80 spine-text"). §16.1 said ≥79 — a ±1 boundary that can mis-blank a thin spine. Co-locate the three KDP floors: **paperback ≥24 · hardcover ≥75 · spine text ≥80.**
- **KDP hardcover 0.767" spine (186pp) footnote:** reachable as cream+0.302 (old) OR white+0.348 (new); HC is WHITE-only, so white+0.348 is the operative form. Do NOT "reconcile" back to a cream 0.813" — that is rejected.
- **Em-dash gate carve-out (a bug this pass introduced):** a table "(n/a)" `—` placeholder is legitimate per `feedback_no_em_dashes.md`; the hard gate must not false-positive-block it. FIXED in `lint_em_dashes` — em-dash inside a markdown table row is exempt; prose em-dashes still block.

### 18.2 Print/production additions (quiet conventions the grep could not surface)
- **Mixam free custom ENDPAPERS** (smyth-sewn hardcover): a 4th uploadable PDF beyond front/back/spine/inner — a free premium feature the Mixam path silently omits.
- **Mixam interior safe/quiet area = 0.25"** (distinct from the 0.80" cover bleed and 0.125" interior bleed).
- **Spine-side quiet-zone pad:** add ~0.10–0.15" on the spine-facing edges beyond the uniform bleed+0.25" (ASTRA §5.4).
- **Manual "F9 the TOC" finisher:** on shipped books the TOC/page-number fields sometimes need a manual Word F9 update or page numbers ship stale — doubly relevant now that `docx_to_pdf.py` skips TOC update on a late-bind failure; a TOC-bearing book must be re-verified in the rendered PDF.
- **License is register-split:** treatises → CC-BY-4.0; novels → All Rights Reserved. §9.4 defaulting everything to CC-BY would mis-license a novel — select by `is_fiction`.
- **§3.9 LaTeX→Unicode glyph coverage** (append the exact tables): subscripts missing `b c d f g q w y z` + all caps; superscripts mostly letters missing; `\dot{}` missing `I J K L Q U V` → combining U+0307; matrices / integrals-with-bounds / `\mathcal`(→italic not script) are out of scope → OMML or image.
- **Kindle cover ratio 1.6:1** (1600×2560) — a shipped Kindle cover slipped to 1.491:1; enforce the ratio.

### 18.3 Writing/craft additions (the layer grep is wholly blind to)
- **THE CLINICAL-DISTANCE FAILURE MODE — the biggest miss.** Over-correcting against cliché/sentimentality renders emotional peaks FLAT and analytical — fluent but dead. *The Autotelic Disposition* needed a dedicated **"peak-aliveness rendering" pass** to amp the load-bearing beats back to the thesis's altitude, gated by an anti-flatness checklist. §7 technique AND a "never do": anti-cliché discipline must not flatten the peaks. (Directly relevant: *The Unfinished Mirror* reads clinically in places — dense argument, few felt peaks.)
- **Parallel / out-of-order drafting hazard:** a callback written before its source unit exists is only CONCEPTUAL; a mandatory **concretization pass** must swap in the real, varied phrasing once the source lands. §2.7 has "vary wording" but not the ordering hazard or its gate.
- **Single-authorial-act methodology (ASTRA §1–4), under-captured:** the soul-doc load, the two-voice convergence test, single-axis multi-pass revision with a fixed pass order, the Mode A/B prose taxonomy, and a COLD parallel-instance adversarial audit (cross-model review outranks self-audit).
- **De-concretize / name-scrub** is a real whole-repo operation (strip personal specifics, fill `[BO-WRITES]` impersonally, rename entities across every registry, keep anonymized empirical anchors) — pair with a per-book `voice.forbidden_proper_nouns[]` grep gate.
- **Extend the hedge blacklist:** "to be fair", "it could be argued", "that said", "at the end of the day".
- **Refrain leakage audit:** the sacred phrase leaking into ordinary prose is a recurring in-review catch — verify it appears ONLY at its designated placements, not merely at the right count.

---

## 19. THE EXHAUSTIVE READ-SWEEP (2026-07-12) — 13 Opus readers, the whole corpus, read-in-full not grepped

*Bo's standard, stated absolutely: not one lesson, across dozens of books, ever relearned. 13 OPUS readers read the FULL corpus in full — every project `memory/` folder, Inside-the-Region's 91KB SESSION_MEMORY, the ASTRA book-production dump, BOOK3's 93KB SEED + 72KB WRONG, the template seeds, the superseded PRODUCTION_LESSONS set, the cover-prompt recipes, and the prior build's own `_kit_research/` — each diffing against §1–§18. Verdict: production is well-captured (several ledger values are deliberately STRONGER than the sources — do not revert); the deltas concentrate in WRITING-CRAFT, THREAD-REGISTRY DISCIPLINE, and a few production fences. Full detail with verbatim quotes + sources: `docs/_lessons_audit/_delta_*.md` (13 files).*

### 19.1 Writing / craft — the engine of "one authorial act" (the layer grep is blind to)
- **The earned-peak mechanic — the fix for clinical flatness (§18.3):** pre-designate 1–2 register-lift HINGES per book (the thesis fulcrum + the close); LIFT ONLY THOSE; hold everything else sober. Over-lifting is the mirror failure. (Directly diagnoses *The Unfinished Mirror*'s flatness: dense argument, no designated peaks.)
- **"Perturb, don't admire" (HIGH):** agreement is the failure mode; a synthesis that feels clean and complete is a WARNING. Load-bearing because synthesis books grow from source theory authored by earlier Claude/Fable instances — the drafter RESONATES with in-network prose and mistakes fluency for truth. Ingest + authorship rule; the cold cross-model audit is its mechanism.
- **The accumulation ladder:** a mechanic introduced in unit N becomes a NAMED category in N+1 and plural-self texture in N+2 — the actual engine of continuous authorship. §7 technique.
- **Render-and-stop:** at the peak, render the act and STOP; explaining/annotating it is the AI-tell.
- **Reader-clock sets unit length:** length is set by reader-time, not the story's calendar; a deliberately thin unit is fine but must carry a `thinned` flag so it doesn't false-fail the ±20% gate.
- **Voice-fidelity has a CEILING:** Bo accepted the analytical "Claude-doing-Bo" blend on the reference book; do NOT over-inject idiolect into pastiche (tempers §17's maximize-everything).
- **The leakage test (per-sentence):** would the author literally say "my terminal value is X, who [specific fact]"? If not, a personal specific has leaked — the preventive form of §18.3's whole-repo scrub.
- **Greenlist = a scarce curated instrument** (a signature move ~once per book-stretch, not everywhere); **sacred-terms = a 3-column "Never / Say / Instead" contract.** Register-map + compression-pair + transition-seam grammar (lift/seam/move) are BUILDABLE specs the seed must carry, not just command names.

### 19.2 Thread-registry / continuity / process discipline
- **DISK IS TRUTH, LEDGER IS A HINT (HIGH):** the moment more than one hand touches the files, the continuity ledger must RE-DERIVE state from disk (`ls manuscript/current`, read the actual chapters) and NEVER trust its own last write — a prior instance was one "continue" from resuming off a stale map. Bake into COMPACTION_SURVIVAL/§15 as a mandatory reconcile-against-disk step; a RECALL/`_CONTINUITY` read reconciles against disk first.
- **Thread Immunity flag (HIGH):** each registry thread carries a mutability bit (refrain/sacred motifs = `Immunity: true`); without it a revise-pass silently reshapes a load-bearing motif.
- **Concept-introduction-order is a DISTINCT registry** from seed→payoff, with a `brief-forward-allowed` carve-out — this is what reconciles "flash-forward liberally" (§7) with GATE-3 "no forward references."
- **A contract/canon edit MUST trigger a same-pass registry re-audit (HIGH):** "no registry update needed" was asserted and wrong every time; §11's manuscript-drift keystone needs a scaffolding twin.
- **`audit canon` spans 3 surfaces:** YAML frontmatter + prose + Must-Plant fields (a YAML-only check let a Must-Plant drift ship).
- **reforge method (fills the mode gap):** adversarially re-read the prior work vs newer canon → each overturned position a WRONG.md entry → old text preserved untouched → new prose re-derived (never line-edited).
- **Ship on book-specific audits + an `architecture.template.md`:** the audit set is not fixed; each book declares its own ship-gates in its ARCHITECTURE — but the kit ships NO architecture template though its taxonomy names one. Add it. SEED must also carry a writing-ORDER plan (anchor/voice-defining chapter FIRST, intro/conclusion LAST); contract needs a `Must Flash-Forward` field.

### 19.3 Print / production — corrections, fences, additions
- **STALE-NUMBER FENCE (do NOT reintroduce), §5.5 footnote:** `+0.302` board-add (known-wrong); the 186pp `0.767` reached as cream+0.302 is a latent trap (HC is WHITE-only → operative white+0.348); the broken white formula `×0.002252+0.302=0.721`; `10.416` height (validator wants 10.417); "cream for white-only KDP HC"; `0.625"` PB gutter (hardened to 0.75").
- **Board-add is per-title, page-count-driven, reverse-derived from KDP's rejection widths — NEVER a formula** (the 412→426pp Inside-the-Region chain 0.302→0.246→0.241 is the §13 primary evidence).
- **Gutter for thick books: default 0.875" for ≳350pp** interiors (Inside the Region shipped 0.875" at 412–426pp); flat 0.75" understates thick books.
- **KDP categories = 2 (floor), 3 attested for nonfiction — anchor to the live picker** (Previewer-wins style); §9.1's "≤3" corrected to 2 (§18.1).
- **MARKETING/CEREMONIAL COPY needs the voice gate (HIGH — was a live leak):** the em-dash/blacklist gate scanned `manuscript/current` only; the back-cover blurb, `kdp_metadata.description`, `epigraph`, `about_the_author`, `dedication`, `subtitle` render into the book/listing and bypassed it. (Verified: the Unfinished Mirror epigraph attribution shipped an em-dash.) FIXED this pass — `lint_manuscript.py` now scans those config fields.
- Hardcover front-panel **spine-hinge intrusion ~0.4"** can clip a CENTERED title (inset from the hinge); halo is **two-tone/contrast-adaptive per element**, not one direction; **AI-authorship disclosure is now mandatory** on KDP.

### 19.4 Cover / art / vision — mechanisms that thinned in consolidation
- **`cover_generation_prompts.md` is a reusable prompt-recipe ENGINE** (Style Bible + per-image Concept/Mood/Avoid/Reference schema + generator param tables) — vendor it; period-accuracy + photographic-realism cues + reference-artist anchors are load-bearing vision-verify checkpoints.
- **KEEL vision `:8080` squatter trap:** the resolver reuses any live server on 8080/1234/11434, so a non-vision squatter silently breaks the perceptual gate — probe that it was launched WITH `--mmproj`. Recover the ComfyUI cold-run kit (health/hardware/ws_monitor + img2img/inpaint/upscale graphs) and the FERRYMAN sd-turbo fallback (`PYTHONUTF8`/`PYTHONIOENCODING` or it silent-exits 0) into the cover-pipeline doc.

### 19.5 Model / working-style (repeated across projects = load-bearing)
- **Fan-out READERS are OPUS, "not fable class"** — §15.3's "opus or sonnet" under-states it; a canon read is judgment-heavy → OPUS.
- **Primary source dominates model convergence (×5):** agreement across N LLM outputs is shared-prior co-hallucination, NOT corroboration → `audit canon` must trace every citation to a primary source.
- **Land every deliverable on disk, never only in chat (×4). "--help / it opens" is NOT a smoke test — deep-probe the real chain (×2 = GATE-5). Re-tighten at the packaging phase (×2)** (where KDP rejections historically lived). **Tool-tinkering feels like progress; shipping is the metric (×2)** — warns MAINTAIN off endless kit-polishing. Corroborations to hold: autonomy/never-block (×8), anti-sycophancy / non-LLM oracle beats convergence (×6), trust-artifact-over-recall (×4), terse one-sentence-correction register (×5).
