# Cover Pipeline — art-gen prompt rules + composite + perceptual verify

*Reference for the COVER stage (GATE-6). Both halves of the loop are real, runnable tools on this machine: **generate** = the hermes `comfyui` skill + one checkpoint; **verify** = the KEEL Qwen vision server (or Claude vision via imguard). No net-new engine — only a model file and the glue. All machine paths come from `kit_env.json`; all per-book art params from `book_config.cover`. Sourced from `_kit_research/mechanisms/comfyui_hookup_FOUND.md` + `vision_keel.md` and `LESSONS_LEDGER.md` §6.*

---

## The loop (deterministic once the art is locked)

```
1. Build the art prompt from the Book Bible (genre, mood, palette, motifs; period accuracy).
   RULE: NO title/author/lettering in the image.
2. cover_gen.py  → candidate PNG  (SDXL base via the hermes comfyui skill on :8188)
3. vision_verify.py on the ART     → no baked text / subject / palette / focal room?
      FAIL → re-roll (new seed / adjusted prompt), bounded by cover.art.reroll_budget
      PASS → lock the source art (cover_art/<slug>_src.png — NEVER overwritten)
4. composite_cover.py --profile <p> --pages <N>  → PIL typography onto the source art
5. vision_verify.py on the WRAP    → title/author legible + spelled right, tracking clean,
      spine centered, bleed-safe, ISBN keep-out clear?
      FAIL → adjust composite params / re-roll → PASS → wrap locked
```

Generation is AI; **compositing is 100% deterministic PIL** (no AI at composite time). The AI source art is preserved untouched and every composite is re-derived from source, never from a prior composite — a title-position tweak re-composites from the clean plate.

---

## GENERATE — `cover_gen.py` (ComfyUI via the hermes skill)

### The hookup

The production hookup is a hermes skill, NOT FERRYMAN (FERRYMAN only spec'd ComfyUI as a deferred backend; its only on-disk image path is a 1-step sd-turbo diffusers smoke test — too weak for covers). The skill lives at `kit_env.cover_gen.comfyui_skill_dir` (`…\hermes-agent\skills\creative\comfyui\`, v5.1.0, MIT). Two layers: `comfy-cli` (launch/stop/install/download) and the REST/WS runner scripts. Ready API-format graphs sit in `workflows/`: `sdxl_txt2img.json`, `flux_dev_txt2img.json`, `sdxl_img2img.json`, `sdxl_inpaint.json`, `upscale_4x.json`.

### Invocation

```bash
comfy launch --background                          # :8188 (kit_env.cover_gen.comfyui_server)
curl -s http://127.0.0.1:8188/system_stats         # health

python scripts/run_workflow.py \
  --workflow workflows/sdxl_txt2img.json \
  --args '{"prompt":"<ART PROMPT>","negative_prompt":"text, watermark, letters","seed":-1,"steps":30}' \
  --output-dir ./outputs
# stdout JSON: {"status":"success","outputs":[{"file":"./outputs/sdxl_00001_.png",...}]}
```

`--input-image image=./x.png` for img2img/inpaint. `run_batch.py --count 8 --randomize-seed` for a seed sweep of variants. `cover_gen.py` shells to this runner and returns the PNG path as JSON.

### The one missing piece — a checkpoint

`ComfyUI\models\checkpoints\` (`kit_env.cover_gen.checkpoints_dir`) ships EMPTY (`put_checkpoints_here`). Fetch one before the first gen, via `comfy model download --url <URL> --relative-path models/checkpoints` OR `C:\fetcher\fetch.py`:

- **SDXL base ~6.5 GB** — `stabilityai/stable-diffusion-xl-base-1.0/sd_xl_base_1.0.safetensors` (`kit_env.cover_gen.default_checkpoint` + `default_checkpoint_url`). Needs ≥8 GB VRAM; huge fine-tune ecosystem. **The default** (fits the 16 GB 4070 Ti SUPER comfortably).
- **Flux-dev fp8 ~12 GB** — `Comfy-Org/flux1-dev/flux1-dev-fp8.safetensors`. Needs ≥12 GB VRAM; markedly better composition, can render legible text if ever wanted. Opt-in when VRAM is free.
- **SD 1.5 ~4 GB** — lightest, weakest. Fallback only. (sd-turbo diffusers 1-step 512² exists as a last-resort in-process fallback — gate-quality only.)

### Prompt rules

- **NO title/author/lettering in the image** — typography is composited afterward in PIL; AI-rendered text degrades and misspells, and competing typography ruins the composite. Negative prompt always includes `text, watermark, letters` (extend per `book_config.cover.art.negative_prompt`).
- **Build from the Book Bible:** genre, mood, palette (`book_config.cover.palette`), motifs; enforce period accuracy where relevant. **Leave the upper third of the front open** for the title (focal room).
- **Aspect 2:3** matches 6×9 (`--ar 2:3` / spine `--ar 1:8` for reference tools). For a cool cast, append "warm golden-hour."
- **Anti-patterns to reject:** glossy stock-photo / golden-hour-product lighting, saturated colors & vibrant gradients, hand-drawn/cartoon registers, text-heavy compositions.
- **A minimal all-PIL cover (no image-gen at all) is a valid default** for text-forward/tech books (e.g. navy field + a hexagon outline + a sans wordmark) — `cover_gen.py` can be skipped entirely for that register.

### Resolution + color

For 6×9 @ 300 DPI + 0.125" bleed the art needs **≥ 1999×2775 px** (the higher of the two recorded bars; general minimum 1875×2775). SDXL emits 1024×1536 or 2048×3072 → upscale (Real-ESRGAN / `upscale_4x.json` / Topaz) before compositing; keep the raw + upscaled source untouched. Convert sRGB→CMYK (FOGRA39 EU / GRACoL2006 NA) before print submission.

---

## COMPOSITE — `composite_cover.py` (deterministic PIL, all print profiles)

Profiles: `kdp-wrap` (single `[back│spine│front]`, 0.125" bleed), `kdp-hardcover` (single wrap, 0.708" turn-in + board-added spine, height 10.417"), `mixam-3panel` (three separate PDFs, 0.80" bleed). Reads `cover_art/<source>` + `book_config.json` + a re-derived `PAGES`; writes the profile's cover PDF(s)+JPG(s); prints target-vs-actual wrap inches for self-verification.

Shared PIL toolkit + the load-bearing rules (full numbers in `format_spec_sheet.md` §7–§8):

- **`load_font(size, weight)`** — Cormorant Garamond variable via `set_variation_by_axes([weight])` (axis 300–700) + the dedicated Bold TTF, loaded from vendored **repo-relative `fonts/`** (a path computed from the script location — NEVER `C:\Claude-Titanic\fonts\`).
- **`measure_tracked` / `draw_tracked`** — per-glyph hand-kerning (PIL has no native tracking). Title tracking ~0.04–0.05em (`book_config.cover.title_tracking_em`); author wide small-caps ~0.18–0.20em.
- **`scale_to_cover`** (fill + center-crop) for full-bleed front art vs **`scale_to_fit`** (shrink + letterbox in the cover color) for content-at-edges art (a chat screenshot, a timestamped image) so nothing at the edge is cropped.
- Title cream halo stroke (~2% of font px) for legibility across a gradient. Spine text `int(spine_px × 0.42)` weight 700 double-drawn +1px (Mixam spine `×0.28`, title-only, no author/ornament), composed horizontal then `.rotate(-90, expand=True)`. Back panel art darkened for cream-text legibility.
- **Typography ≥ bleed + 0.25" from every edge** (Mixam 1.05", KDP-PB 0.375", KDP-HC 0.958"). Upper third front for title; lower third back for description + barcode.
- **Cover PDFs written with an EXACT-inch MediaBox via PyMuPDF** (`inches × 72`) — PIL truncates to 4 decimals → KDP rejection.
- **ISBN keep-out 2.25"×1.5" bottom-right — draw nothing** (KDP auto-overlays its barcode; Mixam does not stamp). No baked ISBN, no cream placeholder.
- **Spine math from config:** `spine = pages × per_page_paper + board_add`; cream 0.0025 / white 0.002252; KDP-HC board-add 0.348 first guess then Previewer-calibrated `SPINE_OVERRIDE_IN`; Mixam board-add from Mixam's calculator. `PAGES` is a single re-derived variable injected into every compositor.
- **Mixam filenames carry routing keywords:** `front_cover.pdf` / `back_cover.pdf` / `spine.pdf` / `inner_*.pdf` — never a bare `back.pdf` (Mixam silently routes it to interior body page 1).

---

## VERIFY — `vision_verify.py` (perceptual; a machine cannot see these defects)

### What it judges

- **On the art:** no baked title/author text; subject + palette match the Bible; focal room for the title (upper-third-front open).
- **On the composited wrap:** title + author legible AND correctly spelled; tracking clean; spine centered; bleed-safe (nothing readable inside the quiet zone); ISBN keep-out clear.

### The pipeline

**render → `resize_image_safe.py` <2000px → vision.** Cover wraps are ~4255×3125 (HC) / ~3801×2775 (PB) and ALWAYS exceed the 2000px ingestion cap, which aborts a conversation non-recoverably. Resize first, unconditionally. Read from a disk path; write outputs to a subdir; **never inline image bytes into chat** (a prior session died from too many inline screenshots filling the window).

### Backends

**Default = KEEL local Qwen vision** ($0/token, on-box; `kit_env.vision`). Start (or reuse) the server, then POST OpenAI-format:

```
C:\llama.cpp\llama-server.exe --model C:\models\Qwen3.5-9B-Q5_K_M.gguf \
  --mmproj C:\models\mmproj-F16.gguf --host 127.0.0.1 --port 8080 --jinja \
  --n-gpu-layers 99 --ctx-size 16384
```

- **`--mmproj` is THE vision switch** — omit it and the same server is silently text-only (`image_url` parts ignored). Confirm the running :8080 server was launched WITH `--mmproj` (port 8080 is shared with cognition; embed 8090, rerank 8091).
- **`--jinja` is required** for the thinking toggle; keep it even for pure OCR.
- Poll `GET /health` until ready before the first call. POST to `/v1/chat/completions` with a text part (the rubric) + an `{"type":"image_url","image_url":{"url":"data:image/png;base64,..."}}` part (data URI — the server wants base64, not a path). Read the verdict from `choices[0].message.content`. Optionally constrain with `json_schema` for a parseable `{"legible":bool,"issues":[…]}` — but **grammar/json_schema ⊕ thinking are mutually exclusive** (a schema forces thinking off; supplying both 400s). The `model` id in the JSON is cosmetic.

**Alternate = Claude vision** via the harness (imguard-resized image read from disk). Use if the local path is unavailable.

### Rubric shape

Put the pass/fail rubric in the text part, e.g.: *"You are an OCR + layout verifier. List every line of text on this cover verbatim. Then PASS if the title and author are legible and correctly spelled and sit inside the quiet zone, else FAIL with the specific reason."* Read `choices[0].message.content` → PASS advances; FAIL feeds the bounded re-roll.

---

## Gotchas (baked as defaults)

- **No baked text in the art** — typography is composited; negative prompt carries `text, watermark, letters`.
- **Preserve source art** — `cover_art/<slug>_src.png` is never overwritten; composites derive from it.
- **`scale_to_fit` for edge-content art** — `scale_to_cover` would crop off a timestamp / edge detail.
- **Exact MediaBox via PyMuPDF** — PIL's `floor(px/DPI)` truncation → 4-decimal rejection.
- **Regenerate after any interior change** — margin → pages → spine → cover width. Never reuse a cover across services (Mixam vs KDP spine widths differ). Front/back panels don't depend on spine → after a page-count shift, regenerate `spine.pdf` only.
- **Mixam filename routing is silent** — a bare `back.pdf` becomes interior body page 1. Always `back_cover.pdf`.
- **2000px cap** — resize every image before any Read/vision; cover wraps always trip it.
- **`--mmproj` mandatory, port 8080 shared** — confirm the live server has vision; don't collide with a text-only squatter.

---

*Both halves exist as runnable tools. Generate = hermes `comfyui` skill + one checkpoint download. Verify = KEEL Qwen vision (or Claude vision via imguard). The cover loop closes on itself — the harness catches its own layout defects before the human ever uploads.*
