# KIT_ARCHITECTURE.md — BOOKSMITH Design Spec

**What this is.** BOOKSMITH is a reusable, portable, one-shot vibe-book-writing kit. A user drops a *gist* of the book plus a *folder of source documents* into `intake/` and steps away. The harness (Claude Code, Opus-class, 1M context) autonomously (1) architects the book, (2) drafts a voice-consistent, continuity-checked manuscript, (3) produces every upload-ready output format, and (4) generates and verifies the cover art — surfacing a finished folder only once every mechanical and perceptual gate passes.

**Why it works.** It front-loads every solved idiosyncrasy as a *default* (the mirror-margin XML injection, the empty-header fix, the KDP hardcover turn-in, the Mixam filename router, the spine board-adds, the LaTeX→Unicode ordering, Word-COM as the only trustworthy docx→PDF path), and it makes every stage *verifiable* — a two-verifier model of mechanical checks plus a perceptual vision loop — so the internal build loop converges to one-shot-clean before the human ever sees it.

**This file is the invariant.** It governs structural design. `CLAUDE.md` (the orchestrator) governs session behavior and must be revised to match this file if they conflict — never the reverse. A per-book `seed.md` is an *instantiation*; this spec is the *machine*.

**Target runtime.** Tier 1 (full print pipeline): Windows + Microsoft Word installed (Word COM is the only page-faithful docx→PDF path). Tier 2 (no Word / other OS): EPUB, Kindle DOCX, cover compositing + verification. GPU (optional, cover art only): ≥8 GB VRAM. The **default cover checkpoint is SDXL base** (~6.5 GB); Flux-dev-fp8 (~12 GB) is opt-in when VRAM allows. Node 18+ with `docx@9.6.1` + `jszip@3.10.1`; Python 3.10+ with `pywin32`, `Pillow`, `PyMuPDF (fitz)`, `PyPDF2` (plus optional `requests`, `tiktoken`, `jsonschema`).

**Machine environment (`_tools/kit_env.json`).** Absolute machine paths are NOT hard-coded in scripts; they live in `_tools/kit_env.json` (machine-level, separate from the per-book `book_config.json`). Every tool that needs an external resource reads it: `word` (COM), `cover_gen` (a ComfyUI runner — the vendored `_tools/comfy_client.py` by default — plus `comfyui_server`, `checkpoints_dir`, checkpoint URL), the optional local `vision` backend (`llama_server`, `qwen_model`, `mmproj`, host/port, `start_cmd`), `fonts_dir`, and the optional `organs` accelerators. A template ships as `kit_env.template.json` (copy → `kit_env.json`, fill for the machine); moving the kit to another box means editing this one file, not grepping scripts. This is the portability seam.

---

## (a) THE AUTONOMOUS FLOW — ordered pipeline with a verification gate after each stage

The kit runs as a linear pipeline of eight stages. **Every stage ends in a gate.** A gate either passes (advance) or fails (bounded retry inside the stage; escalate to the human only on a hard-stop). Nothing advances on unverified state.

```
INTAKE            gist + docs folder land in intake/
   │  GATE-0  intake manifest exists; every file classified; duplicates flagged
   ▼
INGEST / ORIENT   discover → size → reconcile duplicate canon versions → CORE-FIRST GESTALT
                  (main loop reads the core in full + skims every satellite) → relational
                  digest fan-out → integration mode declared (asked when core+satellites)
   │  GATE-1  every relevant doc is in context or chunked; a reconciled canon set is named;
   │          the core was read by the MAIN loop (satellites skimmed) BEFORE any digest
   │          fan-out; digests are relational; integration_mode declared;
   │          no blind-read of any file >8K tokens
   ▼
BUILD SEED        emit seed.md (Book Bible) + contracts/ + registry/ + exemplars/ from intake
   │  GATE-2  seed.md §1–§7 present; one contract per unit; thread registry seeded;
   │          voice exemplars extracted; book_config.json validates against the schema
   ▼
DRAFT MANUSCRIPT  chapter/part loop: load Context Pack → draft → self-assess → handoff → audit
   │  GATE-3  per unit: voice gate (blacklist=0, exemplar-consistent) + continuity gate
   │          (threads/callbacks resolve, no forward concept refs) + contract gate
   │          (Must-Accomplish met, word count within ±20%). Bounded 3-iteration fix loop.
   ▼
SEAM / INTEGRATION cross-unit: check seams, audit threads/dependencies/canon/voice/refrain
   │  GATE-4  no orphan seeds/payoffs; refrain at exact placements; registries in sync
   │          with contracts; reads as one continuous authorial act; synthesis mode:
   │          no unit maps ~1:1 onto a single source (the anthology signature)
   ▼
PRODUCE FORMATS   one interior authored once → per-format transforms → 9 upload-ready artifacts
   │  GATE-5  MECHANICAL (verify_build.py): mirror flags present in settings.xml; every
   │          header-free section empty; recto parity holds (check_part_pages.py); page
   │          count ÷2 (KDP) / ÷4 (Mixam); spine math matches re-derived PAGES; lint clean;
   │          Kindle word-count parity with print
   ▼
COVER (gen+verify) build art prompt → cover_gen.py (SDXL) → composite typography → wrap
   │  GATE-6  PERCEPTUAL (vision_verify.py): art has no baked title/author text, subject
   │          + palette match the Bible, focal room for the title; then on the composited
   │          wrap: title/author legible + correctly spelled, tracking clean, spine centered,
   │          bleed-safe, ISBN keep-out clear. Bounded re-roll loop (new seed / adjusted prompt).
   ▼
VERIFY EVERYTHING  full mechanical + perceptual sweep across all artifacts
   │  GATE-7  verify_build.py green for every format AND vision_verify.py green for every
   │          cover AND rendered-page spot checks clean (render → imguard <2000px → vision)
   ▼
EMIT FINISHED FOLDER   outputs/ populated; per-format upload checklist + dimension report written
```

**The gate that follows each stage is the design's load-bearing idea.** The historical failures this kit exists to prevent (four rejected KDP hardcover rounds on *Inside the Region*; a Kindle shipped 8,476 words short of the print; a paperback wrap uploaded to a hardcover listing) were all *unverified-state-advanced-anyway* failures. Each gate is cheap, mechanical where possible, perceptual only where a machine check cannot see the defect.

---

## (b) FOLDER TAXONOMY

### Kit-level (ships in the repo, book-agnostic)

```
BOOKSMITH\                    (the kit folder — location-independent)
├── CLAUDE.md                 Orchestrator: boot sequence + command grammar + autonomy + gates
├── README.md                 Human-facing: what it is, how to drop intake, how to run
├── KIT_ARCHITECTURE.md       THIS FILE — the invariant design spec
├── docs/                     Methodology + the crown-jewel gotcha corpus
│   ├── LESSONS_LEDGER.md               the canonical symptom→cause→fix ledger (the constitution)
│   ├── vibe_writing_method.md          seed/contract/registry/handoff discipline
│   ├── format_spec_sheet.md            the exact-numbers cheat sheet (all formats + service presets)
│   ├── cover_pipeline.md               art-gen prompt rules + composite + verify loop
│   ├── COMPACTION_SURVIVAL.md          jsonl→md rehydration + hooks (session survival)
│   └── VALIDATION.md                   the loop-test report (what was proven green)
├── _tools/                   The portable toolchain (see (c)) — ported from proven scripts
├── fonts/                    VENDORED TTFs, repo-relative (never C:\Claude-Titanic\fonts\)
│   ├── CormorantGaramond-Light.ttf     house cover default (variable, wght 300–700)
│   ├── CormorantGaramond-Bold.ttf      dedicated bold TTF
│   └── library/                        curated OFL font library (25 files, PIL-verified)
│       ├── FONTS.md                    catalog: family / license / use-case / pairings
│       └── *.ttf                       body serifs (EB Garamond, Literata, Crimson Pro,
│                                       Alegreya, Lora, Libre Baskerville) + display faces
│                                       (Playfair, Cinzel, Oswald, Montserrat, Inter) +
│                                       Great Vibes script + JetBrains Mono code — all
│                                       variable-weight where available
├── templates/                Blank scaffolds the SEED builder copies + fills per book
│   ├── seed.template.md
│   ├── contract.template.md
│   ├── handoff.template.md
│   ├── digest.template.md
│   ├── threads.template.md
│   ├── state.template.md
│   └── WRONG.template.md
├── intake/                   DROP ZONE — user places gist + source docs here, then steps away
└── book_workspace/testvoyage/  ships as the filled reference book (config + contracts + all outputs)
```

**Portability rules baked into the taxonomy:** fonts are vendored repo-relative and every compositor references `fonts/` via a path computed from the script location — the cross-repo `C:\Claude-Titanic\fonts\` dependency that bit every prior book is designed out. The gotcha corpus (`docs/LESSONS_LEDGER.md`) ships *with* the kit so the first upload passes rather than being rediscovered per book.

### Per-book working structure (created at build time)

Every book gets its own workspace under `book_workspace/<slug>/`. `<slug>` is derived from `book_config.slug`.

```
book_workspace/<slug>/
├── seed.md                   the Book Bible for THIS book (§1–§7; instantiation of the template)
├── book_config.json          the single per-book config object (validates against the schema)
├── contracts/                one contract per unit (chapter or part) + _TEMPLATE.md
├── state/                    reader-state snapshots per boundary (after_ch{N}.md / after_part_{N}.md)
├── registry/                 threads.md, dependencies.md, compression_pairs.md, refrain.md, canon_refs.md
├── handoffs/                 3-layer handoff per unit (ch{N}_handoff.md)
├── reviews/                  adversarial review outputs (steelman + skeptic + role passes)
├── exemplars/                voice-calibration passages (anchor + supporting) extracted from intake
├── manuscript/
│   ├── drafts/               versioned, append-only: ch{N}_v1.md, v2.md, …
│   └── current/              latest-approved pointer/copy: ch{N}_current.md
├── cover_art/                AI-generated SOURCE art at full res — NEVER overwritten; composites derive from it
├── outputs/                  the upload-ready deliverables (9 formats)
│   ├── markdown/             stitched version-pinned master (the single source for all generators)
│   ├── kindle/               *_KINDLE.docx + cover JPG
│   ├── epub/                 <slug>.epub (EPUB 3 — Apple/Kobo/Google/Nook + KDP-preferred upload)
│   ├── kdp_paperback/        interior DOCX+PDF + cover_wrap.pdf/.jpg
│   ├── kdp_hardcover/        (same interior) + cover_wrap_hardcover.pdf/.jpg
│   ├── mixam_paperback/      interior (÷4-padded) + 0.125" wrap at Mixam geometry
│   ├── mixam_hardcover/      inner_*.pdf + front_cover.pdf + back_cover.pdf + spine.pdf (+ previews)
│   ├── blurb_paperback/      trade softcover interior + wrap (Blurb 6.125×9.25 page model)
│   ├── blurb_hardcover/      ImageWrap interior + wrap (visible-face typography)
│   └── digital/              *_DIGITAL.pdf (covers + blank-stripped interior)
├── WRONG.md                  append-only position-revision ledger (5-field entries)
├── CHANGELOG.md              append-only mechanical action log
└── _warm_start.md            compressed rehydration pointer for a fresh session
```

**Design constants across the workspace:** drafts are append-only (never overwrite `v1` — write `v2`); `current/` is a pointer to the latest approved draft; `cover_art/` holds the untouched AI source and every composite is regenerated *from source*, never from a prior composite; `outputs/markdown/` holds the ONE version-pinned manuscript every generator reads (the fix for the Kindle-vs-print source-drift bug).

---

## (c) THE TOOLCHAIN COMPONENT LIST

Every script lives in `_tools/`. Each has a single PURPOSE and an exact I/O contract. The SOURCE column cites the proven script this is ported from. **The kit's central refactor: every per-book knob these scripts currently hard-code is read from `book_config.json` instead.**

### Interior generation (Node.js, `docx@9.6.1`)

**`generate_book.js`** — *Parameterized print interior generator.*
- PURPOSE: emit the print-interior DOCX for a given format profile (`kdp_paperback` | `kdp_hardcover` | `mixam_hardcover` | `mixam_paperback` | `blurb_paperback` | `blurb_hardcover`) from the version-pinned manuscript. One script, format selected by config; the *only* difference between KDP and Mixam interiors is the four margin constants + output filename + page-count multiple.
- I/O: `node generate_book.js --config book_config.json --format <profile>` → reads `outputs/markdown/<slug>_vN.md` + `book_config.json`; writes `outputs/<profile>/<naming>.docx`. Emits the mirror-margin + evenAndOddHeaders JSZip injection inline (post-Packer). Prints computed section count + margins.
- Encodes: 6×9 (`PAGE_W=8640, PAGE_H=12960` DXA); Georgia body from `interior.body_pt`; per-chapter `SectionType.ODD_PAGE` recto sections + trailing `SectionType.EVEN_PAGE` blank; `emptyHeadersFooters()` on every header-free section; leading-PageBreak suppression on first-in-section; markdown parser splits **backticks-first, then math, then bold, then italic**; `[IMAGE …]` blocks skipped; standalone mid-flow markdown image lines (`![alt](relpath)`) are skipped-with-warning in print interiors (the replica route or `interior.chapter_art` carries print images) — never rendered as literal text.
- SOURCE: `C:\BOOK\generate_book_kdp.js` + `C:\BOOK\generate_book_mixam.js` + `C:\BOOK3\_tools\_titanic_source\generate_book_v12.js` (byte-identical modulo margins — unified here).

**`generate_kindle.js`** — *Reflowable Kindle DOCX generator.*
- PURPOSE: emit the reflowable ebook DOCX for direct KDP upload (not epub). Strips every print concept.
- I/O: `node generate_kindle.js --config book_config.json` → reads the same version-pinned markdown; writes `outputs/kindle/<slug>_KINDLE.docx`. Single section, uniform 1" margins, `header:0 footer:0 gutter:0`; NO page numbers/headers/mirror/blank-versos/forced-rectos; chapter titles styled `HeadingLevel.HEADING_1` + `PageBreak` chapter boundaries (Amazon builds ebook navigation from the Heading-1 structure); the in-book CONTENTS page + hyperlinked `TableOfContents` field is **OMITTED by default** (§16.4 — set `kindle_include_toc: true` to embed one, which also arms `Document({features:{updateFields:true}})`); math runs tagged `Cambria Math`; About-the-Author back matter. (Doc truth-synced 2026-07-23 to the shipped generator behavior.) **Mid-flow images:** a standalone markdown image line `![alt](workspace-relative path)` embeds the PNG/JPEG at that point in the flow (centered `ImageRun`, natural size at 150dpi capped 5.0in; missing/unreadable = warn + skip, never literal markdown) — added 2026-07-23 for image-bearing replica ebooks (DRDJ 人生篇/教育篇).
- SOURCE: `C:\BOOK\generate_kindle.js` / `C:\Inside_The_Region\generate_kindle.js`.

**`inject_mirror_margins.js`** — *JSZip post-processor: mirror margins + even/odd headers.*
- PURPOSE: inject `<w:mirrorMargins/>` and `<w:evenAndOddHeaders/>` into `word/settings.xml` because docx@9 silently drops them from `page.mirror:true`. Without this, verso gutters land on the wrong side → KDP "insufficient gutter."
- I/O: `node inject_mirror_margins.js <docx>` → mutates the DOCX in place (idempotent — only injects if absent). Run **between** `generate_book.js` and `docx_to_pdf.py`.
- SOURCE: `C:\BOOK\_tools\inject_mirror_margins.js`.

**`inject_front_matter_valign.js`** — *JSZip post-processor: vertical alignment on ceremonial pages.*
- PURPOSE: inject `<w:vAlign w:val="center|bottom"/>` into per-section `<w:sectPr>` in `word/document.xml` (docx@9 doesn't expose vAlign) so the half-title/title center vertically and the copyright anchors to the bottom. Requires front matter built as separate one-page sections.
- I/O: `node inject_front_matter_valign.js <docx>` → mutates in place (idempotent — strips existing vAlign first). Config drives which section index gets which alignment via `front_matter` sequence.
- SOURCE: `C:\BOOK\_tools\inject_front_matter_valign.js`.

**`latex_to_unicode.js`** — *LaTeX math → Unicode converter (avoids OMML).*
- PURPOSE: convert `$…$`/`$$…$$` to Unicode math + tag runs `Cambria Math`, so equations survive DOCX and Kindle without an equation editor. Only invoked for `is_fiction:false` math-bearing books.
- I/O: importable module `convert(latexString) -> {runs:[{text,font}]}`; also a `fixProseSubscripts()` pass. **Load-bearing order:** strip `\left/\right/\big` → unwrap `\text/\mathrm/…` → `\dot{}` precomposed → symbols longest-first → **subscripts before fractions** → superscripts → `\frac{a}{b}→(a)/(b)` → brace cleanup.
- SOURCE: `C:\BOOK\_tools\latex_to_unicode.js` / `C:\Inside_The_Region\_tools\latex_to_unicode.js`.

### PDF + page-count (Python, Word COM + PyMuPDF)

**`docx_to_pdf.py`** — *The only trustworthy docx→PDF path (Word COM).*
- PURPOSE: render a DOCX to a page-faithful PDF via Microsoft Word COM (Pandoc / LibreOffice-headless / cloud all break fonts + TOC hyperlinks + pagination). Also returns the authoritative page count.
- I/O: `python docx_to_pdf.py <in.docx> <out.pdf>` → `Dispatch("Word.Application")`, updates all `TablesOfContents` + fields, `Repaginate()` (twice for TOC-bearing docs), `SaveAs(FileFormat=17)`; prints `ComputeStatistics(2)` (pages) + `(0)` (words) as JSON on stdout. Windows + installed Word required.
- SOURCE: `C:\BOOK\_tools\docx_to_pdf.py` + `C:\Inside_The_Region\update_hardcover_and_count.py`.

**`check_part_pages.py`** — *Recto-parity verifier (empirical, via Word COM).*
- PURPOSE: prove each chapter/part heading lands on a recto (odd) page — arithmetic is not trusted because a markdown edit re-breaks parity.
- I/O: `python check_part_pages.py <docx>` → opens read-only in Word, `Repaginate()`, `Selection.Find` each unit heading, reads `Selection.Information(3)`; prints per-unit page number + PASS/FAIL (even = verso = fail) as JSON. Feeds GATE-5.
- SOURCE: `C:\BOOK3\_tools\_titanic_source\check_part_pages.py`.

**`strip_blank_pages.py`** — *Digital-edition blank-verso stripper.*
- PURPOSE: remove the print-only blank versos (from ODD_PAGE recto starts) and header-only ghost pages so the digital PDF reads continuously.
- I/O: `python strip_blank_pages.py <in.pdf> <out.pdf>` → PyMuPDF; keeps cover pages 1–2 unconditionally; drops any body page whose `page.get_text().strip()` is empty (or `<30` non-whitespace chars for header-only ghosts).
- SOURCE: `C:\BOOK\_tools\build_digital_atd.py` (strip stage) / `C:\BOOK3\_tools\_titanic_source\strip_blank_pages.py`.

**`build_digital_pdf.py`** — *Digital / reader PDF assembler.*
- PURPOSE: assemble the email/Drive PDF: page 1 front cover, page 2 back cover (cropped from bleed back to 6×9 trim), then the blank-stripped interior.
- I/O: `python build_digital_pdf.py --config book_config.json` → Word-COM interior PDF + crop covers (`BLEED_PX=int(0.80*DPI)=240` for Mixam-sourced back art) → cover pages as exact 432×648 pt MediaBox via `fitz.new_page` → `PyPDF2` concat → `outputs/digital/<slug>_DIGITAL.pdf`.
- SOURCE: `C:\BOOK\_tools\build_digital_atd.py` / `C:\Inside_The_Region\build_digital_with_covers.py`.

### Covers (Python, PIL + PyMuPDF)

**`composite_cover.py`** — *Parameterized cover compositor (all print formats).*
- PURPOSE: composite typography onto the AI-art source and assemble the cover for a given profile: `kdp-wrap` (single `[back│spine│front]`, 0.125" bleed), `kdp-hardcover` (single wrap, 0.708" turn-in + board-add spine, height hardcoded 10.417"), `mixam-3panel` (three separate PDFs, 0.80" bleed), `mixam-paperback-wrap` (single wrap at 0.125" Mixam PB geometry), `blurb-wrap` (Blurb trade softcover wrap), `blurb-imagewrap` (Blurb hardcover ImageWrap), `kindle` (front-only ebook cover). Deterministic (no AI at composite time).
- I/O: `python composite_cover.py --config book_config.json --profile <p> --pages <N>` → reads `cover_art/<source>` + `book_config.json` + re-derived `PAGES`; writes the profile's cover PDF(s)+JPG(s) to `outputs/<format>/`. Prints computed wrap dimensions (target-vs-actual inches) for self-verification.
- Encodes: `load_font` (Cormorant Garamond variable via `set_variation_by_axes` + Bold TTF, from vendored `fonts/`); `measure_tracked`/`draw_tracked` (per-glyph tracking); `scale_to_cover` (full-bleed front) vs `scale_to_fit` (content-at-edges back art, letterboxed); cream/dark halo strokes; spine text double-drawn +1px, composed horizontal then `rotate(-90)`; typography ≥ `bleed+0.25"` from edges; PDFs written with **exact-inch MediaBox via PyMuPDF** (PIL truncates → KDP 4-decimal rejection); ISBN keep-out left clear (no baked box); Mixam names `front_cover.pdf`/`back_cover.pdf`/`spine.pdf`.
- Spine math (from config): `spine = pages × per_page_paper + board_add`; `per_page` 0.0025 cream / 0.002252 white; `board_add` 0 (KDP paper) / `kdp_hardcover_board_add` default 0.348 (KDP HC) / `mixam_board_add` (Mixam, reverse-derived from Mixam's calculator).
- SOURCE: `C:\BOOK\composite_cover_atd_kdp.py` + `_kdp_hardcover.py` + `_mixam.py`; `C:\Inside_The_Region\composite_cover_*.py`; `C:\BOOK3\_tools\_titanic_source\composite_cover_{kdp,kdp_hardcover,titanic}.py`.

**`cover_gen.py`** — *AI cover-art generator (ComfyUI via the hermes skill).*
- PURPOSE: generate front-cover art from a Book-Bible-derived prompt. **Rule: no title/author text in the image** (typography is composited afterward). Default checkpoint SDXL base; Flux-dev-fp8 opt-in.
- I/O: `python cover_gen.py --prompt "<art prompt>" --negative "text, watermark, letters" --workflow sdxl_txt2img.json --seed -1 --steps 30 --out cover_art/<slug>_src.png` → shells to the hermes comfyui skill `run_workflow.py` (`comfy launch --background` on :8188; `run_workflow.py --workflow workflows/sdxl_txt2img.json --args '{…}' --output-dir …`); returns the PNG path as JSON. `run_batch.py --count 8 --randomize-seed` for variations.
- REQUIRES: one checkpoint in `ComfyUI\models\checkpoints\` (empty by default) — default `stabilityai/stable-diffusion-xl-base-1.0/sd_xl_base_1.0.safetensors` (~6.5 GB), fetched via `comfy model download` or any downloader (the `default_checkpoint_url` in `kit_env.cover_gen`).
- SOURCE: a hermes-style ComfyUI runner skill (`run_workflow.py`, `workflows/sdxl_txt2img.json`, `flux_dev_txt2img.json`) — all paths resolved via `kit_env.cover_gen` (historical provenance, not a runtime dependency).

**`cover_layout.py`** — *Title-band auto-layout: propose → score → pick.*
- PURPOSE: decide WHERE the title should sit on the cover art (`composite_cover.py` places it; this chooses the band). Proposes N candidate title bands, scores each for legibility, returns the best band's `y_frac` for `composite_cover.py --title-y-frac`. Closes the typography-placement loop the way the prose gates do.
- I/O: `python cover_layout.py --art <img> --palette "<hex,…>" [--n 6] [--json]` (or `--config book_config.json` for palette + colour from `cover.palette`) → prints the best band `{y_frac,h_frac,score,calmness,contrast}` + ranked candidates. Mechanical scoring by default (`0.55*calmness + 0.45*contrast`, pure PIL, no GPU); `--vision` upgrades to a `vision_verify` per-candidate score; `--aspect` scores in the compositor's frame.
- SOURCE: new (roadmap H1.4) — the auto-layout half of the cover typography loop.

**`palette_transfer.py`** — *LAB recolor of catalog art to the book palette.*
- PURPOSE: recolor any catalog / hypergen cover image toward a book's exact palette while preserving its structure (composition + the calm upper-third title zone), so one image can serve any book. Used by `cover_pick.py --recolor`.
- I/O: `python palette_transfer.py --src <img> --palette "<hex,…>" --out <img> [--strength 0.8]` (or `--config book_config.json` for the palette from `cover.palette`) → writes the recoloured image; prints a JSON summary (mean LAB before/after + target). Reinhard-style mean/std transfer in CIELAB, pure Pillow (no numpy); `--strength` blends the shift so it stays tasteful.
- SOURCE: new (roadmap H1.4) — the recolor stage of the prerendered-catalog cover path.

### Verification (the two-verifier model)

**`vision_verify.py`** — *Perceptual verifier (image + rubric → verdict JSON).*
- PURPOSE: the perceptual half of the cover loop — judge an image against a rubric a mechanical check cannot see: art has no baked text / subject + palette match the Bible / focal room for the title; and on the composited wrap: title+author legible + spelled right, tracking clean, spine centered, bleed-safe, ISBN keep-out clear.
- I/O: `python vision_verify.py --image <png> --rubric <rubric.txt|inline> [--backend auto|keel|claude]` → resizes ≤2000px first, then POSTs a `{text-rubric + image_url data-URI}` to the backend; returns `{"verdict":"PASS|FAIL","issues":[…],"ocr":"…"}` as JSON. **Backends** (`auto` is the default): a local KEEL-style Qwen server when `kit_env.vision` configures one (`<llama_server> --model <qwen_model> --mmproj <mmproj> --host 127.0.0.1 --port 8080 --jinja --n-gpu-layers 99 --ctx-size 16384`, POST `/v1/chat/completions`, read `choices[0].message.content`); else Claude vision via the harness — the portable zero-setup path. Optionally constrain output with a `json_schema`.
- SOURCE: `C:\Claude-Titanic\_kit_research\mechanisms\vision_keel.md` (§1.B PowerShell block) + `_tools/resize_image_safe.py`.

**`verify_build.py`** — *Mechanical verifier (spec checks → pass/fail JSON).*
- PURPOSE: the mechanical half — machine-checkable production invariants, run at GATE-5 and GATE-7 for every format.
- I/O: `python verify_build.py --config book_config.json --format <p>` → returns `{"format":…, "checks":[{name,pass,detail}], "all_pass":bool}` as JSON. Checks: `<w:mirrorMargins/>` + `<w:evenAndOddHeaders/>` present in `settings.xml` (zipfile grep); every header-free section's `header*.xml` renders `[]` (empty-header fix); recto parity (invokes `check_part_pages.py`); page count ÷2 (KDP) / ÷4 (Mixam); re-derived `PAGES` matches the value fed to `composite_cover.py`; cover wrap dimensions match KDP/Mixam expectation to 4 decimals; `lint_manuscript.py` clean; Kindle word-count parity with print (never lower).
- SOURCE: consolidated from the XML-inspection verify snippets across `06_memory_and_intake.md` G-1/G-4 + `PRODUCTION_LESSONS_LEARNED.md`.

**`lint_manuscript.py`** — *Manuscript corruption + voice-drift lint (hard exit-1 gate).*
- PURPOSE: block release on PDF-round-trip corruption (`a_Thursday` underscores, unbalanced emphasis, mid-word hyphen breaks, sentence ripped across a paragraph) AND on SEED-blacklist / anachronism drift. Excludes scaffolding + cached source dirs by default (they legitimately quote banned words / period vocabulary).
- I/O: `python lint_manuscript.py --config book_config.json [--include-docs]` → scans `manuscript/current/` + `drafts/`; exit `0` clean / `1` drift (blocking) / `2` usage. Blacklist/greenlist/sacred-terms come from `book_config.voice`.
- SOURCE: `PRODUCTION_LESSONS_LEARNED.md` lint rules + `C:\BOOK3\_tools\check_acp_vocabulary.py` (97-pattern scrubber; case-sensitive/insensitive/regex tiers; dir-exclusion).

**`check_continuity.py`** — *`_CONTINUITY.md` self-consistency gate (invoked by `verify_build --final`).*
- PURPOSE: prove a workspace's COMPACTION-SURVIVAL ledger (`_CONTINUITY.md`) is internally consistent, so a resuming session is never sent to a stale place (the one shipped book carried a header saying COMPLETE while its footer token still said IN_PROGRESS and its DONE list named 4 of 13 chapters — nothing gated it).
- I/O: `python check_continuity.py --workspace <book_workspace/slug> [--ledger <path>] [--fix]` → JSON `{"ledger":…, "consistent":bool, "defects":[…], "status":{…}}`; exit 0 consistent / 1 any defect / 2 usage. Flags: STATUS disagreement (header vs footer vs SHIPPED marker), COMPLETE-but-still-mid-draft, DONE undercount vs `manuscript/current/*_current.md` on disk. Read-only by default (`--fix` is the export-path rewrite; `verify_build --final` calls it without `--fix`).
- SOURCE: new — the mechanical gate for CLAUDE.md's COMPACTION SURVIVAL ledger discipline.

**`check_synthesis.py`** — *Synthesis-mode anti-anthology audit (GATE-4).*
- PURPOSE: make GATE-4's prose rule mechanical — in `synthesis` integration mode, fail any unit whose `## Canon Anchors` map ~1:1 onto a single source document while the corpus holds two or more (the "anthology tell", where a synthesis book quietly reverts to a stitched anthology along source boundaries).
- I/O: `python check_synthesis.py --workspace <book_workspace/slug>` → per-unit rows + verdict as JSON. Discovers the source corpus from `canon_refs/_digest_<slug>.md` + `registry/canon_refs.md`; a unit's sources are the corpus slugs cited in its `contracts/<id>.md` Canon Anchors. Diagnostic + deterministic: a missing registry / unfilled template / single-source corpus becomes a SKIP row with a reason, never a crash.
- SOURCE: new — mechanizes CLAUDE.md GATE-4 ("no unit maps ~1:1 onto a single source document").

**`resize_image_safe.py`** — *2000px ingestion guard.*
- PURPOSE: prevent the non-recoverable session crash from reading an image >2000px in any dimension. Run before ANY `Read`/vision ingest of a screenshot or cover.
- I/O: `python resize_image_safe.py <img>` → echoes the source path unchanged if ≤2000px both dims; else LANCZOS-downsamples into a 2000×2000 box, saves with `_r2k` suffix, prints the safe path. Safe to run unconditionally.
- SOURCE: ported from a prior kit's resize guard (the reference machine's global imguard organ mirrors it) — fully self-contained here, PIL only.

### Scaffolding

**`init_contracts.py`** — *Idempotent contract-stub generator.*
- PURPOSE: generate one `contracts/{unit_id}.md` stub per unit from the seed's structural map, in one pass. Won't overwrite (use `--force`).
- I/O: `python init_contracts.py --config book_config.json` → writes stubs to `book_workspace/<slug>/contracts/` using the contract template + unit list.
- SOURCE: `init_contracts.py` referenced across `AI_BOOK` / `BOOK-test3`.

**`print_presets.json` + `preset_lookup.py`** — *Prevalidated service geometry (Mixam paperback/hardcover, Blurb trade softcover/ImageWrap) + the shared lookup/interpolation module.*
- PURPOSE: single source of truth for per-service geometry beyond KDP, every value provenance-tagged (shipped / mixam-template / blurb-calculator-probe / INFERRED). `preset_lookup.py` is imported by BOTH `composite_cover.py` and `verify_build.py` — one code path, so verifier-vs-compositor drift is impossible. Meta-rule: the service's own calculator/previewer always beats the preset; a stated dimension goes into `book_config.spine.spine_override_in` and wins.
- FORMATS ADDED: `mixam_paperback` (0.125" wrap, ÷4, spine fit pages×0.0023+0.04 cream), `blurb_paperback` (6.125×9.25 interior page model, table-interpolated spine), `blurb_hardcover` (ImageWrap: probed-row interpolation, visible-face typography). Evidence vendored at `docs/service_templates/`.
- SOURCE: Mixam official spec pages + live calculator/template API capture + template-generator PDFs; Blurb booksize-calculator probe (2026-07-11).

**`build_epub.py`** — *EPUB 3 exporter (Apple Books / Kobo / Google Play / Nook / Draft2Digital — and KDP's now-preferred reflowable upload).*
- PURPOSE: emit a standards-valid EPUB 3 (with EPUB 2 NCX compat) from the version-pinned master + config. Ceremonial front matter from config; body units split at the unit heading level; the composited ebook cover embedded with `properties="cover-image"`; `mimetype` first + STORED. **Mid-flow images:** a standalone `![alt](workspace-relative path)` line embeds the image at that point as `<figure class="midflow">` (files deduped by source into `OEBPS/images/mf_NNN_*.ext` + manifest entries; missing/unsupported = warn + drop, never literal markdown) — added 2026-07-23 for image-bearing replica ebooks.
- I/O: `python build_epub.py --config book_config.json [--src master.md] [--out x.epub]` → writes `outputs/epub/<slug>.epub`, prints JSON (chapters, words, self-checks). Structural self-checks run inline; `verify_build.py --format epub` re-verifies independently (structure + word-count parity vs print).
- SOURCE: new — hand-rolled EPUB 3 (zipfile + XHTML), no pandoc/calibre dependency.

**`assemble_manuscript.py`** — *Version-pinned master stitcher (the anti-drift keystone).*
- PURPOSE: stitch `manuscript/current/{unit}_current.md` (front matter + every unit in order) into the ONE version-pinned master `outputs/markdown/<slug>_vN.md` that EVERY generator reads. This is the single fix for the Kindle-vs-print source-drift bug (a Kindle once shipped 8,476 words short of the print because generators read different source versions). All formats build from this one file, never from divergent sources.
- I/O: `python assemble_manuscript.py --config book_config.json` → reads the ordered unit list + `manuscript/current/`; writes `outputs/markdown/<slug>_v{N}.md` (append-only version bump) and prints the total word count (the parity baseline every format is checked against).
- SOURCE: new — formalizes the implicit stitch step every prior book did by hand.

### Maintainer tools (run by the kit maintainer, not in a per-book pipeline)

**`regression_fixtures.py`** — *Generator behavior regression (the QC-sweep fixture).*
- PURPOSE: run both interior generators over a tiny synthetic book engineered to hit every historically-defective input (currency `$…$` pairs, `\rightarrow`/`\cdots`/`\bigcup` math, `####` deep headings, bold-wrapped code, rendered em-dashes, `page_number_align:"outer"` even/odd flags, `[IMAGE`-prefixed prose, mid-flow `![](…)` image lines — kindle/epub EMBED, print SKIPS, literal markdown never renders), then unzip the DOCX (+ EPUB) and assert the RENDERED artifacts are right. The defects it guards were invisible under default configs.
- I/O: `python _tools/regression_fixtures.py [--json]` → temp-dir workspace, repo untouched; exit 0 pass / 1 regression / 2 node absent (SKIP).
- SOURCE: new — the 2026-07-13 QC sweep's fixture recommendations, made a standing gate.

**`hypergen.py`** — *Abstract cover art from pure code (the no-GPU cover floor).*
- PURPOSE: render a tasteful abstract cover BACKGROUND (no baked text; upper third calm for the title) on ANY machine in a fraction of a second — 8 styles × 8 mood palettes × seed, fully deterministic. `cover_pick.py` shortlists these beside catalog matches when no SDXL stack is up.
- I/O: `python _tools/hypergen.py --style horizon --mood dark_literary --seed 7 --out cover_art/x.png` (or `--palette "hex,hex,…"`; `--contact-sheet` renders all styles into one grid). Pillow only.
- SOURCE: new — the portability floor of the Cover 2.0 loop.

**`catalog_build.py`** — *Prerendered cover-catalog builder.*
- PURPOSE: run ONCE on a capable machine to populate `cover_catalog/` with a spread of covers that machines WITHOUT a render stack can then pick from (via `cover_pick.py`). The durable value is the genre×mood prompt MATRIX; images fill in per entry.
- I/O: `python catalog_build.py [--dry-run | --hypergen | --sdxl | --all]` → `--dry-run` prints the matrix + writes stubs; `--hypergen` renders pure-code abstract entries (no GPU, keyless); `--sdxl` renders photographic/painterly entries via ComfyUI+SDXL (needs a GPU box); resumable (existing rendered entries skipped).
- SOURCE: new — the build side of the prerendered-catalog cover fallback.

**`make_giftable.py`** — *Stranger-safe distribution zip packager.*
- PURPOSE: produce one clean `.zip` of the kit ready to hand to someone who will run Claude Code on their own desktop — drops everything private/heavy/third-party-encumbered per the portability audit, then runs a PERSONAL-DATA GATE over every shipped text file and REFUSES to write the zip on a hit. Never modifies the source tree.
- I/O: `python make_giftable.py [--allow-personal-data] [--include-node-modules] [--keep-service-templates] [--full-example-outputs]` → writes the dist zip (or exits 1 with `file:line + pattern` if the personal-data gate finds the author name/email or a machine path). Excludes `.git/`, `__pycache__/`, `kit_env.json`, all `book_workspace/*` except a trimmed `testvoyage/`, rehydration scratch, and session logs by default.
- SOURCE: new — the portability-audit packager for the giftable-kit initiative.

**`illustrations_gen.py`** — *Chapter-opener illustration batch driver (SDXL via ComfyUI).*
- PURPOSE: drive the vendored `comfy_client` over a per-book `cover_art/illustrations/briefs.json` (locked style prefix + negative + one subject line per unit) to produce N candidates per chapter, entirely on disk and crash/rewind-safe: the manifest is rewritten after EVERY image, so a fresh session resumes by reading it, never by regenerating. Feeds the `interior.chapter_art` injection in the interior generators.
- I/O: `python illustrations_gen.py --config book_config.json [--generate] [--contact-sheets] [--pick] [--candidates N] [--only ids]` → writes `cover_art/illustrations/candidates/<id>_c<k>_s<seed>.png`, `contact_sheets/`, ink-heuristic auto-picks post-processed (grayscale/autocontrast/white-point) into `live/<id>.png`, and `illustrations_manifest.json`. Idempotent per step.
- SOURCE: new (2026-07-14) — the illustrated-interior initiative.

**`cover_compose_ahss.py`** — *Bespoke type-led cover compositor (per-book design reference).*
- PURPOSE: render an operator-approved type-led cover design (navy field, Georgia serif, pen-stroke-on-a-signing-line motif) as front/back/spine panels and compose the per-service artifacts with EXACT-inch MediaBox PDFs (PyMuPDF). One renderer for all panels so the wrap is self-consistent; Mixam/KDP geometry pulled from the shared `preset_lookup` so the verifier and compositor agree. The alternative to the house `composite_cover.py` when a book ships a bespoke design instead of AI art. (Named for its first book; a template for future bespoke covers.)
- I/O: `python cover_compose_ahss.py --config book_config.json --back back_copy.json --pages N --profile <digital|kindle|mixam|kdp> --out <dir>` → writes the profile's PDF(s)/JPG + `cover_meta_<profile>.json`.
- SOURCE: new (2026-07-14) — *A Human Still Signs* production.

**`scan_manuscript.py`** — *Deterministic packaging + placeholder gate.*
- PURPOSE: the structural packaging invariants the executor used to check by hand, made one reproducible gate (complements `lint_manuscript.py`, which owns corruption + blacklist + the em-dash gate). Per unit: file exists, UTF-8 no-BOM, exactly one `# ` H1 that byte-matches the config title, zero `## ` (generators drop them), zero em/en dashes when `voice.no_em_dashes`, zero tables / list lines, zero placeholders (the `[⚠ … AT LINE-READ]` class that once shipped into a printed Acknowledgments; also `[BO-WRITES]`, `[TODO]`, angle-stubs, fill-blanks), and word count within ±20% of `target_words` (WARN).
- I/O: `python scan_manuscript.py --config book_config.json [--json] [--strict]` → exit 0 clean / 1 FAIL / 2 usage. Auto-relaxes the dash check for translated editions (`no_em_dashes:false`).
- SOURCE: new (2026-07-14) — codifies the executor's ad-hoc packaging scans + closes the placeholder gap.

**`pdf_replica_fit.py`** — *Page-REPLICA re-fit of a finished PDF onto a KDP trim (the OTHER reimport route).*
- PURPOSE: when the order is "replica clone, change nothing" (re-issuing an author's own typeset book), preserve every page AS RENDERED — embedded fonts, colors, line breaks, folios — and re-fit only the geometry. Mechanism: **margin-swap** — measure the source CONTENT BOX (percentile bbox of text+image blocks; finished books carry generous margins, so a 7.25×10.24 source fits 6×9 at ~95% instead of the naive 72%), then place each page's content box into KDP-compliant margins (gutter from the KDP table by final page count, mirrored recto/verso) at one uniform scale via vector `show_pdf_page` — no rasterization. Pads ÷2; never upscales.
- I/O: `python pdf_replica_fit.py <book.pdf> --out-dir DIR [--trim 6x9|7x10] [--skip-front N] [--sample "p,p,p"] [--json]` → `<stem>_REPLICA_<trim>.pdf` + JSON report (scale, achieved margins, gutter_ok, page_multiple_ok) + side-by-side A/B sample PNGs. `--selftest` synthesizes and round-trips a known book.
- SOURCE: new (2026-07-23) — the DRDJ three-volume replica re-issue.

**`cover_compose_drdj.py`** — *Replica-project cover compositor (DRDJ set; template for replica covers).*
- PURPOSE: for replica re-issues the SOURCE cover is the front panel (its typography IS the design — the "no baked text" rule governs generated art only); back + spine are DERIVED from the book's own elements: field color sampled from the art, series/volume/author/motto strings, stacked upright vertical CJK spine glyphs. Exact-inch MediaBox via fitz; PB/HC spine math from kit constants; kindle at the 1600×2560 ideal (fit-with-fill, never crops the source cover).
- I/O: `python cover_compose_drdj.py --art cover.png --pages N --profile kdp-wrap|kdp-hardcover|kindle --out DIR [--series …] [--volume …] [--author …] [--motto …] [--cjk-font …]` → wrap PDF+JPG (or kindle JPG) + `cover_meta_*.json`.
- SOURCE: new (2026-07-23) — DRDJ replica pathfinder (投资篇 dims verified formula-exact).

**`pdf_to_book.py`** — *Inbound PDF re-import (the front-end: a finished PDF → a BOOKSMITH workspace).*
- PURPOSE: decompose an already-typeset finished-book PDF (someone else's, or a prior export) into a clean, layout-free, per-unit manuscript + a schema-valid seed `book_config.json`, so the kit can RE-issue it to the exact KDP formats (reflowable Kindle, EPUB, paperback, hardcover, digital). The inverse of the forward pipeline. Design principle: **extract the CONTENT, discard the source LAYOUT** — a finished PDF is already typeset in its own trim/margins/running-heads/page-numbers; keep only text + chapter structure, then re-typeset to each target. Distinct from `manuscript_ingest.py`, which flattens a source to markdown for the SYNTHESIS engine to re-derive a NEW book; this PRESERVES the book. Extraction via fitz "dict" blocks: strip running heads/feet + page numbers, de-hyphenate + reflow, **collapse letter-spaced titles** ("C H A P T E R  O N E"→"CHAPTER ONE"), detect chapters (keyword/size) **cross-checked against the book's own bookmark outline + printed Contents** (the authoritative chapter list, so non-keyworded body-size titles are still recovered), drop the source title/copyright/contents pages (regenerated to spec) while capturing dedication/epigraph, and snap the page size to the nearest standard KDP trim. It STOPS at a proposed structure for human review (heading detection is heuristic); it does not produce. Scanned/image-only PDFs are reported (OCR not wired).
- I/O: `python pdf_to_book.py "<book.pdf>" --slug <slug> [--title T --author A --trim 6x9 --is-fiction --json]` → writes `book_workspace/<slug>/` (`manuscript/current/<id>_current.md` per unit + `front_*` + a schema-valid `book_config.json`) and prints the proposed split. Then review → `produce_book.py`. `--selftest` synthesizes a letter-spaced PDF and round-trips it (regression guard). Runbook: `docs/PDF_REIMPORT_RUNBOOK.md`.
- SOURCE: new (2026-07-22) — the PDF-reformat front-end; fitz (PyMuPDF), otherwise pure-Python.

**`produce_book.py`** — *Deterministic production orchestrator.*
- PURPOSE: turn the whole "assembled markdown → finished PDFs" chain into one reproducible command. Codifies CLAUDE.md §12 plus the production fixes learned in this book (always re-inject vAlign standalone; fold the digital + website PDF assembly in here rather than a temp script). It invents nothing and stops loudly on any pre-gate failure; it does not write prose, place units, brief/pick art, design a cover, or diagnose a red gate (those need a mind).
- I/O: `python produce_book.py --config CFG [--formats kdp_hardcover,kindle,digital,website] [--back back_copy.json] [--interior-for-digital kdp_hardcover] [--skip-lint] [--dry-run] [--json]`. Runs scan + lint → assemble → per-format generate/inject×2/render/cover/verify → digital+website concat; prints a per-format verify summary; exits nonzero on any red. Any failed step (nonzero rc, or a verify without a true `all_pass`) aborts the rest of that format's chain and flips `green:false`; digital/website refuse to build from the interior of a format that went red this run (no stale-PDF builds). `--dry-run` prints the exact command chain without executing. `--selftest` runs the error-propagation regression (dry-run + `PRODUCE_BOOK_FAIL_STEP` injection, no real tools; also run by `selfcheck.py`) — guards the 2026-07-23 bug where a failed render/verify still shipped `green:true` exit 0.
- SOURCE: new (2026-07-14) — the scripted form of the session's by-hand production chain.

---

## (d) THE CLAUDE.md COMMAND GRAMMAR SPEC

`CLAUDE.md` is the operating contract for the session. It is NOT the book. It specifies the boot sequence, the plain-language command grammar (each command auto-loads its context and runs its verification gate), the autonomous loop, and the two-verifier model.

### Boot sequence (every session, in order — no prose before it completes)

1. Read `CLAUDE.md` (this orchestrator) fully.
2. Read `KIT_ARCHITECTURE.md` (the invariant) fully.
3. Detect mode: is `intake/` populated with a new gist+docs (→ INIT), or does a `book_workspace/<slug>/` already exist (→ RESUME)?
4. RESUME: read `seed.md`, `book_config.json`, scan `manuscript/`, latest `state/` snapshot, most-recent `handoffs/`, tail of `WRONG.md` + `CHANGELOG.md`, and `_warm_start.md`. Check for live in-progress work (a `.in_progress` marker / `current_unit` pointer) → resume mid-unit.
5. Report status briefly, then act (autonomous) or standby per the invoked command.

### Command grammar ("match intent, not syntax" — plain language dispatches to these)

- **Init / ingest:** `init` | `ingest` — run INTAKE + INGEST/ORIENT (GATE-0, GATE-1): discover the drop folder, size-then-chunk large inputs, reconcile duplicate canon versions, then core-first gestalt (main loop reads the core + skims every satellite BEFORE fan-out), relational digests, and the one-time integration question (`synthesis` default | `anthology` | `reforge`). Auto-loads: `intake/` manifest. Gate: intake manifest complete, core read by the main loop pre-delegation, digests relational, mode declared, no blind reads.
- **Generate seed:** `generate seed` — run BUILD SEED (GATE-2): emit `seed.md` §1–§7, `contracts/`, `registry/`, `exemplars/`, and a validated `book_config.json`. Auto-loads: reconciled canon set + intake gist. Gate: schema-valid config + one contract per unit + thread registry seeded.
- **Generate unit:** `generate {chapter|part} N` (unit noun from `book_config.voice`/structure) — draft one unit. Auto-loads the **Context Pack** (below). Gate GATE-3: voice + continuity + contract gates, bounded 3-iteration fix loop. `generate prologue|epilogue|coda|appendix X` respect authorship class (Class A → outline only).
- **Revise:** `revise {chapter|part} N [with <note>]` — re-draft to a new version (append-only `v{M+1}`). Same Context Pack + the note. Same gate.
- **Audit:** `audit {chapter|part} N` — adversarial review (steelman always; skeptic on select units) → `reviews/`. `audit threads|dependencies|canon|voice|refrain` — registry-drift audits (these are load-bearing, not decorative: they catch orphan seeds and contract↔registry drift).
- **Check seams:** `check seams` | `check refrain` | `check compression-pairs` — cross-unit continuity (GATE-4).
- **Produce format:** `produce format <kindle|epub|kdp_paperback|kdp_hardcover|mixam_paperback|mixam_hardcover|blurb_paperback|blurb_hardcover|digital_pdf>` — run that format's transform + GATE-5 (`verify_build.py`). Auto-loads: version-pinned `outputs/markdown/` + `book_config.json`.
- **Generate cover:** `generate cover [<format>]` — run COVER (GATE-6): `cover_gen.py` → `composite_cover.py` → `vision_verify.py`, bounded re-roll loop.
- **Verify:** `verify [all]` — full mechanical + perceptual sweep (GATE-7).
- **Export:** `export v1.0` — the one big final pass: fan out ALL formats + covers in parallel from the single version-pinned source, run every gate, emit the finished folder. **Gated on a ship-at-90% confirm** ("Ship at 90%? canon is append-only; v1.1 exists"). This is the only sanctioned human checkpoint (see (e)).
- **Status / maintenance:** `status` | `next` | `progress`; `update registry` | `update state N` | `wrong <topic>`.

### Context Pack auto-assembly (on `generate {unit} N`)

Auto-load a fixed set: Book Bible (`seed.md` §1–§2) · this unit's contract · adjacent contracts (N−1, N+1, N+2) · **prior unit FULL prose** (`current/{N−1}_current.md`) — mandatory, not the handoff (prose carries residue; the handoff carries state) · N−2 prose if it exists · earlier handoffs (compressed) · state snapshot at boundary · all registries · voice exemplars (anchor + relevant) · canon anchors per contract · this `CLAUDE.md`. Budget ~100–250K tokens loaded; 750K+ left for writing at 1M context. Fresh-session-per-unit is *not* required (a 200K-era workaround).

### THE AUTONOMOUS LOOP

Each command runs to its gate and **loops until the gate passes**:

```
run stage → run gate (mechanical, else perceptual)
   pass → advance / report
   fail → diagnose against docs/LESSONS_LEDGER.md → apply fix → retry
          (bounded: max 3 iterations per gate for content, re-roll budget per config for covers)
   still failing after the bound → HARD STOP: write the failure + diagnosis to CHANGELOG,
          surface to the human with the exact rejection detail and options
```

Autonomy grant: **act without asking** for scans/reads/writes to workspace dirs, script cloning/adaptation, draft iteration, registry/state updates, audits, and cover re-rolls. **Pause only for:** Class-A prose (human-authored), substantive `seed.md` changes, committing `WRONG.md` entries, and `export v1.0`. **Never:** fabricate canon citations, silent-upgrade a Class A, overwrite a prior draft version, break refrain wording, or import blacklisted vocabulary.

### THE TWO-VERIFIER MODEL

Every gate is one or both of:
- **Mechanical** (`verify_build.py`, `check_part_pages.py`, `lint_manuscript.py`, dimension self-reports): deterministic, cheap, run always. XML zipfile inspection of `settings.xml`/`header*.xml`, Word-COM page counts, spine-math reconciliation, word-count parity.
- **Perceptual** (`vision_verify.py` via **render → imguard <2000px → vision**): only where a machine check cannot see the defect — cover art (no baked text, subject/palette/focal-room), composited wrap (legibility, tracking, spine centering, bleed-safety, ISBN keep-out), and rendered-page spot checks. Backend defaults to the local KEEL Qwen server ($0/token, on-box); Claude vision is the alternate. **Never inline image bytes into chat — read from disk, keep the context window clean.**

---

## (e) AUTHORSHIP-CLASS + HUMAN-CHECKPOINT POLICY

Authorship class is a config knob (`authorship.default_class` + `authorship.per_chapter_overrides`) that sets the human-in-the-loop dial per unit. It is authoritative from the contract and **never silently upgraded**.

- **Class A — human-only / outline.** The harness produces an *outline only* (`contracts/{id}_outline.md`); the manuscript file stays empty until the human writes it. Applied to the most emotionally load-bearing units (in fiction: the scenes that must land — a prologue, a grief chapter, an ending). No intermediate drafts exist for a Class A unit.
- **Class B — scaffold with markers.** The harness produces a full scaffold with load-bearing voice-authentic passages marked `[BO-WRITES: {description}]` and does *not* draft prose into those markers. The human fills them.
- **Class C — full draft.** The harness drafts the full first draft in-voice; the human revises. The default for connective-tissue and derivable-structure units.

**Human checkpoint policy.** The kit is designed to run unattended from a single intake drop. The **one sanctioned human checkpoint** is the `export v1.0` ship-at-90% confirm — the harness pauses once, before fanning out final production, to confirm the human wants to ship. Class-A units are the other place human authorship is required, but that is a *content* boundary declared in config, not an interactive stop: the harness simply produces outlines and proceeds. Everything else — every gate, every fix loop, every re-roll — runs autonomously to convergence, with a hard-stop escalation only when a bounded loop cannot pass its gate.
