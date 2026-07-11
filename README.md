# BOOKSMITH

**A portable, one-shot vibe-book-writing kit.** Drop a gist of the book plus a folder of source documents into `intake/`, step away, and the harness autonomously architects the book, drafts a voice-consistent and continuity-checked manuscript, produces every upload-ready format, and generates and verifies the cover — surfacing a finished folder only once every mechanical and perceptual gate has passed.

This README is for a human. If you are the harness (Claude Code), your operating contract is `CLAUDE.md`; read that and `KIT_ARCHITECTURE.md` first.

---

## What you get

From one intake drop, BOOKSMITH produces five upload-ready deliverables plus a cover:

- **Kindle** — reflowable DOCX for direct KDP upload + a 1600×2560 front-cover JPG.
- **KDP paperback** — interior DOCX + page-faithful PDF + a single `[back│spine│front]` cover wrap.
- **KDP hardcover** — the same interior + a hardcover wrap (case-board turn-in, board-added spine).
- **Mixam hardcover** — `inner_*.pdf` interior + three separate cover PDFs (`front_cover.pdf`, `back_cover.pdf`, `spine.pdf`).
- **Digital PDF** — covers + a blank-stripped interior, for email/Drive (not for upload).

Each is checked against the production gates before the folder is surfaced — the mirror-margin flags, the empty-header fix, recto parity, spine math, cover legibility, ISBN keep-out, Kindle/print word-count parity.

---

## How to use it

### 1. Drop your intake

Put two things in `intake/`:

1. **A gist** — a short plain-language description of the book: what it is, who it's for, roughly how long, fiction or nonfiction, the register/voice you want, any hard constraints (a refrain that must appear verbatim, a title, an ending you'll write yourself).
2. **A folder of source documents** — anything the book draws on: research returns, character docs, prior fiction, voice samples, transcripts, raw logs. Duplicates and overlapping versions are fine; the harness reconciles them. Large files are fine; the harness sizes and chunks them.

You do not need to organize the folder or name files a particular way. The harness discovers and classifies what's there.

### 2. Boot the harness

Open Claude Code in `C:\BOOKSMITH\` and say, in plain language, what you want. The harness matches intent, not syntax:

- `init` — ingest and orient on the intake drop.
- `generate seed` — architect the book (Book Bible, contracts, registries, voice exemplars, config).
- `generate chapter 3` / `generate part 5` — draft one unit.
- `audit part 5`, `check seams`, `check refrain` — review and continuity.
- `produce format kdp_paperback` — build one format.
- `generate cover` — art + typography + perceptual verify.
- `export v1.0` — the final pass: fan out every format + cover, verify everything, emit the finished folder.

`export v1.0` pauses once to ask you to confirm ship-at-90%. That is the only interactive stop in the pipeline. Everything else runs to convergence.

### 3. Collect the finished folder

After `export v1.0`, the deliverables land under `book_workspace/<slug>/outputs/`, one subfolder per format, plus a per-format upload checklist and a dimension report. Upload to KDP and Mixam separately.

---

## The idea

Two commitments make BOOKSMITH work.

**A gate after every stage.** The pipeline is eight ordered stages (intake, ingest, seed, draft, seam, formats, cover, verify), and none advances on unverified state. Every failure this kit was built to prevent was an unverified-state-advanced-anyway failure: four rejected hardcover rounds on a prior book, a Kindle shipped 8,476 words short of its print edition, a paperback wrap uploaded to a hardcover listing, a "blank" page that rendered an inherited header and drew a rejection. Each gate is cheap and mechanical where a machine can check it, and perceptual (a vision model reads the rendered page or cover) only where a machine cannot see the defect.

**One authorial act.** The manuscript is written to read as if one person wrote the whole thing with continuous attention — residue carried across unit boundaries, callbacks that vary their source wording, motifs that recur in altered frames, register that varies by unit. A book that reads mass-produced fails, so this discipline is enforced as strictly as any dimension check.

Every hard-won production fix — the mirror-margin XML injection, the empty-header objects, the KDP hardcover turn-in, the Mixam filename router, the spine board-adds, Word COM as the only trustworthy DOCX→PDF path — ships as a *default* baked into the toolchain, so the first upload passes rather than being rediscovered per book.

---

## Requirements (a hard platform dependency)

- **Windows 11 + Microsoft Word installed.** Word COM is the only reliable DOCX→PDF path; Pandoc, LibreOffice-headless, and cloud converters all break fonts, TOC hyperlinks, or pagination. This is not portable to Mac/Linux without a substitute renderer.
- **Node 18+** with `docx@9.6.1` + `jszip@3.10.1` (interior generation).
- **Python 3.10+** with `pywin32`, `Pillow`, `PyMuPDF`, `PyPDF2`, `python-docx`, `numpy`, `pypdfium2`, `requests`, `jsonschema`.
- **GPU for cover art** — RTX-class, ~16 GB VRAM. Default cover checkpoint is SDXL base (~6.5 GB); Flux-dev-fp8 (~12 GB) is opt-in. The checkpoint is fetched once before the first cover generation (`ComfyUI/models/checkpoints/` ships empty).
- **Optional local vision** — a KEEL Qwen `llama-server` for on-box, $0/token cover verification. Claude vision is the alternate backend.

All machine paths live in `_tools/kit_env.json` — the one file you edit when moving the kit to another box.

---

## Layout

```
C:\BOOKSMITH\
├── CLAUDE.md              the orchestrator (the harness's operating contract)
├── README.md              this file
├── KIT_ARCHITECTURE.md    the invariant design spec
├── docs/
│   ├── LESSONS_LEDGER.md      the enforceable production-rules ledger
│   ├── vibe_writing_method.md the seed/contract/registry/handoff writing discipline
│   ├── format_spec_sheet.md   the 5-format exact-numbers cheat sheet
│   └── cover_pipeline.md      art-gen prompt rules + composite + perceptual verify
├── _tools/                the portable toolchain + book_config schema/example + kit_env
├── fonts/                 vendored cover TTFs (Cormorant Garamond Light + Bold)
├── templates/             blank scaffolds the seed builder fills per book
├── intake/                DROP ZONE — your gist + source docs go here
├── examples/              one or two filled reference books
└── book_workspace/<slug>/ created per book; holds seed, manuscript, outputs
```

## Per book

Each book gets its own workspace under `book_workspace/<slug>/` — its Book Bible (`seed.md`), config (`book_config.json`), contracts, registries, handoffs, versioned drafts, the untouched cover source art, and the `outputs/` deliverables. Drafts are append-only; the covers are always re-composited from the untouched AI source; and every generator reads one version-pinned manuscript, so no two formats can drift apart.

---

*BOOKSMITH is a machine for turning one intake drop into a finished, upload-ready book. The architecture is the invariant; a book is an instantiation. Ship at 90% — the canon is append-only.*
