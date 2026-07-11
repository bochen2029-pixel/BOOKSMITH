# BOOKSMITH — Loop-Test Validation Report

*Phase 3 of the build: a throwaway book ("The Test Voyage", 3 chapters, 855 words) driven through the entire pipeline until every gate passed. Bugs found were fixed in the actual toolchain (not the test), so the fixes ship with the kit.*

## What passed (green, on real Word-rendered output)

| Stage | Tool | Result |
|---|---|---|
| Config validation | jsonschema vs book_config.schema.json | VALID |
| Version-pinned assembly | assemble_manuscript.py | master v1, 855 words |
| KDP paperback interior | generate_book.js | DOCX + mirror/vAlign injected |
| KDP hardcover interior | generate_book.js | shares paperback interior |
| Mixam interior | generate_book.js | + fitz ÷4 pad → 20pp |
| Kindle interior | generate_kindle.js | reflowable, H1 TOC, 953 words |
| docx→PDF (all) | docx_to_pdf.py | Word COM, field-by-index fix, page counts |
| Recto parity | check_part_pages.py | CH1=11, CH2=13, CH3=15 — all recto |
| Mechanical gates (4 fmts) | verify_build.py | mirror flags, empty headers, recto, ÷2/÷4, lint — all_pass |
| KDP paperback wrap | composite_cover.py | 12.2950×9.2500", exact MediaBox, self-verify OK |
| KDP hardcover wrap | composite_cover.py | 13.8045×10.4170", exact, board-add 0.348 |
| Mixam 3-panel | composite_cover.py | front/back 7.6×10.6, spine 1.76, filename routing |
| Kindle front cover | composite_cover.py (kindle profile) | 1600×2400 JPG |
| Cover-wrap dimension check | verify_build.py | all 3 wraps match to 4 decimals (Δ=0.0000) |
| Digital PDF | build_digital_pdf.py | 15pp (2 covers + 13 blank-stripped interior) |
| Contract scaffolding | init_contracts.py | 3 stubs from units[] |
| **Perceptual verify (LIVE)** | vision_verify.py → KEEL Qwen | read title/subtitle/author, VERDICT: PASS |

**All five formats produce their complete upload-ready deliverables.**

## Bugs found and fixed during the loop-test (all fixed in the kit)

1. **check_part_pages** searched a synthesized `"CHAPTER N"` (never matched the real uppercase `"CHAPTER ONE — DEPARTURE"`), then a text-Find collided with the auto-inserted CONTENTS/TOC page (all chapters reported the same page). → Rewrote to **structural discovery** (outline-level-1 paragraphs), immune to the TOC, uppercasing, and dash variants.
2. **verify_build recto check** ran check_part_pages without `--config` and parsed the *old* human-readable output — matched `"recto"` in the JSON and passed **vacuously**. → Now passes `--config`, parses JSON, fails on not-found/verso.
3. **verify_build interior-PDF finder** grabbed the *cover* once covers existed (`"paperback"` contains `"back"`, `"hardcover"` contains `"cover"`; find_one fell back to any PDF). → Precise `_is_cover_name` markers + `_find_interior_pdf`.
4. **Mixam ÷4 page padding** was deferred to "a fitz post-step" that didn't exist. → Added `--pad-multiple N` to docx_to_pdf.py (appends blank pages).
5. **No Kindle front-cover profile** (needed for Kindle upload + the digital PDF front page). → Added a `kindle` profile to composite_cover.py (front-only, 1600×2400, reuses the front-panel renderer).
6. **init_contracts** read units from `per_chapter_overrides` only. → Now prefers the canonical `units[]`.
7. **Schema** rejected `dedication`/`epigraph`/`about_the_author`/`units[]` (additionalProperties:false) that the generators read. → Added them + `spine.spine_override_in`.
8. **Portability hardening** (done before the test): `kit_env.json` machine-path seam, fonts vendored into `fonts/`, `assemble_manuscript.py` as the anti-drift keystone.

## Live cover-gen: PROVEN 2026-07-11

**RESOLVED — the full agentic cover loop ran end-to-end live.** ComfyUI launched headless (`main.py --base-directory C:\Users\user\Documents\ComfyUI --lowvram --cpu-vae` on :8188), `cover_gen.py` produced real SDXL art (tall ship at dusk, seed 42, 30 steps), `composite_cover.py` assembled all profiles onto it, and **KEEL Qwen QC-verified the AI's own composited cover → VERDICT: PASS** (it checked for fused masts / impossible rigging / distorted hull, confirmed the title legible + correctly spelled, no defects). Two fixes made during the live run:
- Installed `comfyui-frontend-package` (+ workflow-templates, embedded-docs) into `Documents\ComfyUI\.venv` — Comfy Desktop bundles the frontend outside the venv, so a headless `main.py` launch needs it.
- `cover_gen.patch_checkpoint` now **strips non-node keys** before submission — the hermes `sdxl_txt2img.json` carries a `_comment` string key that ComfyUI's `/prompt` rejects ("a node is missing the class_type property").

The GPU note below is retained for reference.

### (original note) hardware constraint

- **cover_gen.py (SDXL via ComfyUI)** — WIRED and checkpoint-ready (`sd_xl_base_1.0.safetensors`, 6.46 GB, fetched into ComfyUI/models/checkpoints; hermes `run_workflow.py` present). NOT smoke-tested live because on this 16 GB card the KEEL Qwen **vision server (~7 GB, resident on :8080)** and **SDXL (~7–8 GB)** cannot co-reside (5 GB free), ComfyUI is not running, and comfy-cli is not on PATH. This is a **runtime VRAM contention**, not a code defect. To run it live:
  1. Free VRAM: stop the KEEL llama-server on :8080.
  2. Launch ComfyUI (Comfy Desktop, or `python main.py` from the install, or `pipx install comfy-cli && comfy launch --background`).
  3. `python _tools/cover_gen.py --prompt "<art>" --workflow sdxl_txt2img.json --out cover_art/<slug>_src.png` → then re-run composite_cover / vision_verify on the real art.
  The compositing + perceptual-verify halves of the loop are already proven; only the diffusion generation awaits a free GPU.

## Addendum (2026-07-11): four new formats + fonts, all green

- **EPUB** — `build_epub.py` first-pass green: valid EPUB 3 (mimetype/XML/manifest/spine/cover checks), 3 chapters + About in nav, real SDXL cover embedded, word parity 852 vs 941 print (ceremonial allowance). `verify_build.py --format epub` all_pass.
- **mixam_paperback** — all_pass: 20pp ÷4; wrap 12.336×9.25 Δ=0.0000; spine 0.086 (=20×0.0023+0.04) correctly BLANKED (<0.25" rule); min-pages informational note (20 < 32).
- **blurb_paperback** — all_pass: 18pp ÷2; wrap 12.306×9.25 Δ=0.0000; spine clamped at the 24pp table end; Blurb interior page model (6.125×9.25, outer-edge bleed).
- **blurb_hardcover (ImageWrap)** — all_pass: wrap 13.5×9.861 Δ=0.0000; 0.25" board-minimum spine; typography on the visible face (wrap allowance m=0.625 respected).
- **Regressions** — kdp_paperback + mixam_hardcover re-verified all_pass with the new cover_meta.json cross-check live.
- **Geometry provenance** — `_tools/print_presets.json` (Mixam: official pages + live calculator/template API capture + the user's downloaded template PDFs, decoded by MediaBox; Blurb: live probe of their booksize calculator). Shared `preset_lookup.py` = one code path for compositor + verifier. Evidence vendored in `docs/service_templates/`.
- **Font library** — `fonts/library/`: 25 OFL fonts (6 body serifs, 6 display faces, script, code), every file PIL-verified incl. variable-weight axis; cataloged in `FONTS.md`.

## Known behaviors / future polish

- **generate_book.js inserts a CONTENTS/TOC page unconditionally** (even when `front_matter[]` omits `contents`). Fine for nonfiction; for a novel you may want it off. Recommend adding an `interior.include_toc` flag (default true nonfiction / false fiction). The recto check handles the TOC correctly regardless.
- Cover art placeholder used for the loop-test was a plain gradient; real books use cover_gen (SDXL) or an author-supplied image in `cover_art/`.
