# BOOKSMITH — Build Session Log

*Written 2026-07-11. This is the full record of how BOOKSMITH was designed, built, and validated in one session, plus everything needed to resume cold. Author: Bo Chen (bochen2029@gmail.com). Built by Claude (Opus 4.8) in Claude Code, working from `C:\Claude-Titanic`.*

---

## 1. What BOOKSMITH is

A **reusable, portable, one-shot "vibe book-writing" kit** for AI coding harnesses (Claude Code especially). The end-state: a user drops a **gist of the book + a folder of source documents** into `C:\BOOKSMITH\intake\`, steps away, and the harness autonomously (1) architects the book (Book Bible + chapter contracts + thread registry — the "vibe writing" methodology), (2) drafts a voice-consistent, continuity-checked manuscript, (3) produces **all five upload-ready formats**, and (4) generates + verifies the cover art — surfacing a finished folder only after every mechanical and perceptual gate passes.

Five output formats: **Kindle ebook** (reflowable DOCX + front-cover JPG), **KDP paperback** (print PDF interior + wrap cover), **KDP hardcover** (print PDF + case-wrap), **Mixam hardcover** (interior + 3-panel case-laminate cover), **digital/reader PDF**.

It's the generalization of the bespoke, hand-tuned pipelines Bo used to ship several books (The Night Was Young, The Autotelic Disposition, Inside the Region, The Second Notebook, The City and the Girl, etc.). The kit externalizes every per-book knob into one config and front-loads every solved idiosyncrasy as a default.

---

## 2. The mental model (load-bearing — this is WHY it works)

- **One-shot ≠ the AI nails it blind.** One-shot means the AI runs a **closed verification loop internally** — iterating silently until every gate passes — and only *then* surfaces the folder. From the human's chair it's one shot; under the hood it's N verified iterations that *converged*.
- **The loop converges only because it's verifiable.** The gate is the gradient — the "right direction" that measures distance from the known hard specs. No verifier → blind iteration → never closes.
- **Two verifier kinds cover everything:** **mechanical** (deterministic: dimensions, page parity, recto, word-count parity, lint) + **perceptual** (vision: render → imguard <2000px → a vision model judges font size, legibility, spine centering, cover composition — everything a number can't see).
- **"Simulation" = render + imguard.** The AI can't hold a printed book, so it renders the artifact and looks at it through imguard — eyes on the object before a cent is spent at KDP.
- **Totality of on-disk history → the defaults.** Everything Bo ever debugged is written down (repos, memory files, session transcripts). Distilling all of it front-loads every idiosyncrasy so the next book runs the gauntlet clean. The kit's power isn't a smarter AI; it's an AI that **starts where the last session ended.**

---

## 3. Provenance — the corpus this was distilled from

All research notes live at **`C:\Claude-Titanic\_kit_research\`**:
- `00_MASTER_SYNTHESIS.md` — the consolidated two-layer pipeline + all 5 formats + gotchas
- `01_titanic_workshop.md` … `06_memory_and_intake.md` — six deep-dives into the book repos + the memory gotcha layer
- `transcripts/tx_astra7.md, tx_book_aibook.md, tx_canon.md, tx_catchall.md` — idiosyncrasy→fix episodes mined from session transcripts (tx_titanic pending a re-run)
- `mechanisms/vision_keel.md, comfyui_hookup_FOUND.md, comfyui_ferryman.md` — the cover-gen + vision invocations

Sources mined: the book repos `C:\Claude-Titanic` (multi-book workshop), `C:\BOOK` (Autotelic Disposition, 69KB BUILD_LOG), `C:\Inside_The_Region` (most complete cover suite + 91KB SESSION_MEMORY), `C:\BOOK3` (largest seed/spec), `C:\AI_BOOK` + `C:\BOOK-test3` (clean template instances), `C:\BOOK-VERA` (raw intake example); the `~/.claude/projects/C--Claude-Titanic/memory/` reference_*.md gotcha files; and the session transcripts (self-filtered by book-production vocabulary across `C--ASTRA-7`, `C--Claude-Titanic`, `C--BOOK`, `C--AI-BOOK`, `C--AEGIS`, `C--JOBS`, `C--ClaudeCode`).

Transcript reader: **`C:\TRANSPORTER\claude_archive_viewer_v5.html`** converts session JSON → markdown (its logic can be replicated headlessly).

---

## 4. Kit architecture (what's on disk at `C:\BOOKSMITH\`)

```
C:\BOOKSMITH\
├── CLAUDE.md                 orchestrator brain: boot (INIT vs RESUME), command grammar,
│                             autonomous gate loop, two-verifier model, authorship policy
├── KIT_ARCHITECTURE.md       the INVARIANT design spec (governs CLAUDE.md; §a–e)
├── README.md                 human-facing
├── docs/
│   ├── LESSONS_LEDGER.md      64 hard-won rules as enforceable DEFAULTS + checks
│   ├── format_spec_sheet.md   5-format exact-numbers cheat sheet
│   ├── vibe_writing_method.md seed/contract/registry/handoff discipline
│   ├── cover_pipeline.md      art-gen prompt rules + composite + verify loop
│   └── VALIDATION.md          the loop-test report (what passed, 8 bugs fixed, pending SDXL)
├── _tools/                    the parameterized toolchain (see §5) + book_config.schema.json
│   ├── book_config.schema.json / book_config.example.json
│   ├── kit_env.json           MACHINE paths (Word, ComfyUI/hermes, KEEL vision, organs)
│   ├── package.json + node_modules/  (docx@9.6.1, jszip@3.10.1)
│   └── *.js / *.py
├── fonts/                     CormorantGaramond-Light.ttf (variable) + -Bold.ttf (VENDORED)
├── templates/                 seed/contract/handoff/threads/state/WRONG .template.md
├── intake/                    DROP ZONE — user puts gist + docs here
├── examples/
└── book_workspace/
    └── testvoyage/            the loop-test book (proof-of-life; all 5 formats built)
```

**Per-book working structure** (created under `book_workspace/<slug>/`): `seed.md`, `book_config.json`, `contracts/`, `state/`, `registry/`, `handoffs/`, `reviews/`, `exemplars/`, `manuscript/{drafts,current}`, `cover_art/`, `outputs/{markdown,kindle,kdp_paperback,kdp_hardcover,mixam_hardcover,digital}`, `WRONG.md`, `CHANGELOG.md`, `_warm_start.md`.

**Two layers:** the **writing layer** (seed → chapter-by-chapter drafting, orchestrated by CLAUDE.md) and the **production layer** (a two-language toolchain). They meet at the filesystem: writing emits `outputs/markdown/<slug>_vN.md`; production consumes it and emits the format artifacts.

**The gated flow:** INTAKE → INGEST → BUILD SEED → DRAFT → SEAM → PRODUCE FORMATS → COVER (gen+verify) → VERIFY → EMIT. Each stage ends in a gate; nothing advances on unverified state; bounded retries; hard-stop escalation only when a bounded loop can't pass.

---

## 5. The toolchain (`_tools/`) — every script config-driven

**Config:** one `book_config.json` per book (validated against `book_config.schema.json`) externalizes every per-book knob (title/trim/paper/margins/formats/cover/spine/kdp_metadata/authorship/voice/**units[]**/dedication/epigraph). Machine paths live separately in `kit_env.json` (the portability seam — move machines = edit one file).

Interior (Node, docx@9.6.1 + jszip):
- `generate_book.js` — one parameterized print interior; `--format kdp_paperback|kdp_hardcover|mixam_hardcover` (only 4 margins + filename + page-multiple differ; hardcover shares paperback interior). ODD_PAGE recto + trailing EVEN_PAGE blank + inline mirror injection.
- `generate_kindle.js` — reflowable ebook DOCX (no print concepts, H1 auto-TOC, Cambria Math tags).
- `inject_mirror_margins.js` — injects `<w:mirrorMargins/>` + `<w:evenAndOddHeaders/>` (docx@9 drops them).
- `inject_front_matter_valign.js` — injects `<w:vAlign>` per ceremonial section.
- `latex_to_unicode.js` — LaTeX→Unicode math (subscripts-before-fractions order; Cambria Math).

PDF + page-count (Python, Word COM + PyMuPDF):
- `docx_to_pdf.py` — the ONLY reliable docx→PDF (Word COM, FileFormat=17); **field-update-BY-INDEX crash fix** baked in; returns page/word count; `--pad-multiple N` appends blank pages (Mixam ÷4).
- `check_part_pages.py` — recto parity via Word COM; **structural discovery** (outline-level-1 paragraphs — immune to the auto-TOC, uppercasing, dash variants).
- `strip_blank_pages.py` — drops blank versos for the digital edition.
- `build_digital_pdf.py` — front cover + back cover + blank-stripped interior → reader PDF.
- `assemble_manuscript.py` — stitches `manuscript/current/` into the version-pinned master (the anti-drift keystone).

Covers (Python, PIL + PyMuPDF):
- `composite_cover.py` — parameterized; `--profile kdp-wrap|kdp-hardcover|mixam-3panel|kindle --pages N`; exact-inch MediaBox via fitz; scale_to_cover vs scale_to_fit; spine math from config; ISBN keep-out clear; Mixam filename routing.
- `cover_gen.py` — SDXL art via the hermes ComfyUI skill's `run_workflow.py` (no baked text). **Not yet smoke-tested live (see §7).**

Verification:
- `vision_verify.py` — image + rubric → verdict JSON; imguard resize → KEEL Qwen (or Claude vision). **Proven live.**
- `verify_build.py` — mechanical gate: mirror flags, empty headers, recto parity, page-multiple, cover-wrap dims to 4 decimals, lint, Kindle parity.
- `lint_manuscript.py` — corruption + voice-blacklist lint (hard exit-1 gate).
- `resize_image_safe.py` — 2000px ingestion guard.
- `init_contracts.py` — idempotent per-unit contract stubs from `units[]`.

---

## 6. Build phases (how it was built)

- **Phase 1 — Contracts** (2 agents): consolidated all research → `docs/LESSONS_LEDGER.md` (64 rules); authored `KIT_ARCHITECTURE.md` + `book_config.schema.json`. Then the orchestrator (me) **reviewed + hardened** the contracts: added the `kit_env.json` seam, `assemble_manuscript.py`, vendored fonts.
- **Phase 2 — Builders** (5 agents, parallel, contract-first): ported the proven source scripts into the config-driven toolchain + wrote `CLAUDE.md`. Builders caught real bugs during their own testing (PyMuPDF `delete_pages`→`delete_page`, the field-update crash, a 3.11 f-string SyntaxError, argparse routing).
- **Phase 3 — Loop-test** (driven by me): a throwaway 3-chapter book ("The Test Voyage") through the whole pipeline until every gate passed. See §7–8.

---

## 7. Validation results (loop-test, all green)

Full record in `docs/VALIDATION.md`. Summary:
- **4 interiors** validated on real Word-rendered output: mirror margins + empty headers + **true recto parity** (CH1=p11, CH2=p13, CH3=p15) + Mixam ÷4 padding → 20pp.
- **4 cover outputs**: KDP wrap 12.2950×9.2500", hardcover wrap 13.8045×10.4170", Mixam 3-panel (front/back 7.6×10.6, spine 1.76), Kindle front 1600×2400 — **every dimension matched verify's independent recompute to 4 decimals (Δ=0.0000)**.
- **Digital PDF** (15pp: 2 covers + 13 blank-stripped interior).
- **Live perceptual verify** — KEEL Qwen read the composited cover text ("THE TEST VOYAGE" / "A Pipeline Validation" / "BOOKSMITH") and returned `VERDICT: PASS`.

All five formats' upload-ready deliverables exist in `book_workspace/testvoyage/outputs/`.

## 8. The 8 bugs found & fixed during the loop-test (fixed in the shipping toolchain)

1. `check_part_pages` searched `"CHAPTER N"` (never matched the real uppercase title) then collided with the auto-TOC → rewrote to **structural (outline-level-1) discovery**.
2. `verify_build` recto check ran without `--config` and parsed the *old* output → passed **vacuously**; now parses JSON, fails on not-found/verso.
3. `verify_build` interior-PDF finder grabbed the *cover* once covers existed (`"paperback"`⊃`"back"`, `"hardcover"`⊃`"cover"`) → precise `_is_cover_name` + `_find_interior_pdf`.
4. Mixam ÷4 padding didn't exist → added `--pad-multiple N` to `docx_to_pdf.py`.
5. No Kindle front-cover profile → added `kindle` profile to `composite_cover.py` (1600×2400, front-panel renderer).
6. `init_contracts` read `per_chapter_overrides` only → now prefers `units[]`.
7. Schema rejected `dedication/epigraph/about_the_author/units[]` → added them + `spine.spine_override_in`.
8. Portability hardening: `kit_env.json`, vendored fonts, `assemble_manuscript.py`.

---

## 9. The two external mechanisms (verified invocations)

**Cover-art generation — hermes ComfyUI skill** (`C:\Users\user\AppData\Local\hermes\hermes-agent\skills\creative\comfyui\`): `run_workflow.py --workflow workflows/sdxl_txt2img.json --args '{"prompt":"...","seed":-1,"steps":30}' --output-dir ...` against a ComfyUI server on `:8188`. Checkpoint `sd_xl_base_1.0.safetensors` (6.46 GB) is fetched into `C:\Users\user\Documents\ComfyUI\models\checkpoints`. comfy-cli is NOT on PATH; launch ComfyUI via Comfy Desktop or `python main.py`. Rule: NO title/author text in the AI art (typography composited after).

**Local vision/OCR — KEEL Qwen** (proven live): `C:\llama.cpp\llama-server.exe --model C:\models\Qwen3.5-9B-Q5_K_M.gguf --mmproj C:\models\mmproj-F16.gguf --host 127.0.0.1 --port 8080 --jinja --n-gpu-layers 99 --ctx-size 16384` → POST OpenAI-format `/v1/chat/completions` with a base64 image data-URI → read `choices[0].message.content`. Claude vision (via imguard) is the alternate backend.

---

## 10. Environment specifics

- Windows 11, RTX 4070 Ti SUPER **16 GB VRAM**, Microsoft Word installed (hard dep for docx→PDF).
- **VRAM contention:** KEEL Qwen vision (~7 GB, resident on :8080) + SDXL (~7–8 GB) cannot co-reside on 16 GB (~5 GB free). Run cover-gen with the vision server stopped, or vice-versa.
- Node 18+ (`docx@9.6.1`, `jszip@3.10.1` in `_tools/node_modules`); Python 3.10+ (`pywin32`, `Pillow`, `PyMuPDF`, `PyPDF2`, `python-docx`, `jsonschema`).
- **Invoke tools via PowerShell, not Bash** — Bash eats Windows backslash paths (`C:\fetcher\fetch.py` → `fetcherfetch.py`).
- Local "organ" tools available: `C:\imguard` (image guard), `C:\chunker` (oversized text), `C:\earshot` (audio), `C:\Everything` (name search), `C:\fetcher` (downloads), `C:\kernel.sh` (disposable browsers). Paths recorded in `kit_env.json`.

---

## 11. What remains / how to resume

- **Live SDXL cover-gen smoke-test** (only unproven piece — a runtime VRAM constraint, not a code defect). Steps: stop the KEEL server on :8080 → launch ComfyUI → `python _tools\cover_gen.py --prompt "<art>" --workflow sdxl_txt2img.json --out cover_art\<slug>_src.png` → re-run `composite_cover.py` + `vision_verify.py` on the real art.
- **Polish:** add `interior.include_toc` flag (generate_book.js currently inserts a CONTENTS/TOC page unconditionally — fine for nonfiction, off-convention for a novel). Re-run the `tx_titanic` transcript miner (failed on an API error). Consider a LibreOffice fallback for docx→PDF (currently Windows+Word only).
- **To ship a real book:** put the gist + docs in `intake/`, then drive CLAUDE.md's commands (`ingest` → `generate seed` → `generate chapter/part N` → `produce format X` → `generate cover` → `verify` → `export`). The production spine is validated; the writing layer is the harness following the seed.

## 12. Key file pointers

- Kit root: `C:\BOOKSMITH\` (CLAUDE.md, KIT_ARCHITECTURE.md, README.md)
- Constitution + spec: `C:\BOOKSMITH\docs\LESSONS_LEDGER.md`, `format_spec_sheet.md`, `VALIDATION.md`
- Config contract: `C:\BOOKSMITH\_tools\book_config.schema.json` (+ `.example.json`), `kit_env.json`
- Research corpus: `C:\Claude-Titanic\_kit_research\` (00 synthesis, 01–06 deep-dives, transcripts/, mechanisms/)
- Proof book: `C:\BOOKSMITH\book_workspace\testvoyage\` (all 5 formats in `outputs/`)
- Memory: `C:\Users\user\.claude\projects\C--Claude-Titanic\memory\project_booksmith.md` (+ reference_comfyui_hermes_hookup.md, reference_keel_qwen_vision.md)

---

## 13. Session 2 additions (2026-07-11, same day continued)

1. **Live SDXL cover gen PROVEN** — ComfyUI launched headless (`main.py --base-directory Documents\ComfyUI --lowvram`; needed one-time `pip install comfyui-frontend-package` in its venv), `cover_gen.py` generated real art (fixed: strip non-node `_comment` keys before `/prompt`), composited all profiles, **KEEL Qwen QC'd the AI's own cover → PASS**. Full loop: generate → composite → see → verify, autonomous.
2. **EPUB export** — new `_tools/build_epub.py` (hand-rolled EPUB 3 + NCX, no pandoc), wired into schema + `verify_build.py --format epub`; first-pass green. KDP now prefers EPUB for Kindle uploads.
3. **Font library** — `fonts/library/`: 25 OFL fonts (EB Garamond, Literata, Crimson Pro, Alegreya, Lora, Libre Baskerville; Playfair, Cinzel, Oswald, Montserrat, Inter, Cormorant variable; Great Vibes; JetBrains Mono), all PIL-verified with weight-axis probe; `FONTS.md` catalog with genre pairings. Covers need zero install; interior faces need Windows font install for Word.
4. **Mixam + Blurb prevalidated presets** — `_tools/print_presets.json` (provenance-tagged) + shared `_tools/preset_lookup.py`; three new formats wired end-to-end and verified green on the test book: `mixam_paperback` (0.125" wrap — from Mixam's own template PDFs the user downloaded + live calculator capture: spine ≈ pages×0.0023+0.04 cream, ÷4 confirmed, min 32pp), `blurb_paperback` + `blurb_hardcover` ImageWrap (probed from Blurb's official booksize calculator; table interpolation; Blurb interior page model 6.125×9.25). Evidence vendored at `docs/service_templates/`. Book now has **9 possible formats**.
5. **cover_meta.json sidecar** — every compositor profile records `{pages, spine_in, target_wrap_in}`; verifier cross-checks MediaBox vs sidecar AND independent recompute.
6. **GitHub** — repo pushed (see README badge/URL); `gh` auth as bochen2029-pixel; private by default.
7. Research method note: Blurb blocks plain fetches + rate-limits; the working path was a cookie-session urllib probe of their calculator (agent-built, artifacts in `docs/service_templates/blurb_probe*.json`). A dense spine table (every 12pp) may still land at `C:\Claude-Titanic\docs\temp\blurb_spine_tables.json` — merge into presets if present.
