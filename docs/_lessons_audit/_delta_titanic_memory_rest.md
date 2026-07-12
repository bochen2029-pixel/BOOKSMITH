# DELTA AUDIT — remaining Titanic memory files (project_booksmith / production / ue5_pass / comfyui / keel / sta / dissolution / feedback_no_images / user_bo / user_tori / MEMORY) vs. LESSONS_LEDGER.md

*Anchored 2026-07-12 03:15 -05:00 (Sunday, Central Standard Time). Auditor READ IN FULL (not summarized, not grepped): the current `C:\BOOKSMITH\docs\LESSONS_LEDGER.md` §1–§18; the two prior deltas (`_delta_titanic_references.md`, `_delta_titanic_projects.md`) to avoid repeating them; the five `docs/author_voice/*` files (to test whether voice/theme material is already absorbed); and the eleven assigned memory files: `project_booksmith.md`, `project_production.md`, `project_ue5_pass.md`, `reference_comfyui_hermes_hookup.md`, `reference_keel_qwen_vision.md`, `reference_sta_mappings.md`, `reference_dissolution_layers.md`, `feedback_no_images.md`, `user_bo.md`, `user_tori.md`, `MEMORY.md`. This is a DELTA report: facts present in these files but ABSENT / WEAKER / WRONG in the ledger (+ the BOOKSMITH docs it points to). Honest CONFIRMATIONS at the end.*

**Headline.** These eleven files split cleanly into three buckets, and the split is the finding: (1) **infrastructure references** (`comfyui_hermes_hookup`, `keel_qwen_vision`) that are ALREADY fully absorbed into ledger §6.1/§6.5 + `cover_pipeline.md` + `VALIDATION.md` + `SUPERSTRUCTURE.md` — pure confirmations; (2) **project-specific NOVEL canon** (`sta_mappings`, `dissolution_layers`, `user_tori`, most of `user_bo`, the narrative half of `feedback_no_images`, `project_production`) that is correctly OUT OF SCOPE for a book-agnostic kit — the kit's own rule (`_voiceprofile_feedback.md` line 195: *project-specific cast/parts/targets = ignore outside their project; author-level = always applies*) says so; and (3) a **small handful of genuine, kit-general deltas** — the writer-facing UE5-reference technique, the "no interior images" *rationale*, a production micro-step, and a **stale MEMORY.md index**. No number here CONTRADICTS the ledger. The one WRONG item is an out-of-date index line, not a rule.

The most important negative result, stated plainly so a future scan does not "rediscover" it as a gap: **the Titanic/STA institutional isomorphism and Tori's psychological architecture must NOT be baked into BOOKSMITH.** They are the soul of one specific novel (*The Night Was Young*), not reusable machine knowledge. Baking them would corrupt the next book grown in the kit.

---

## PRODUCTION

### D-P1 — UE5 (or any 3D/game/photo) walkthrough as WRITER-FACING reference material — the "collapse eyes→prose" technique  ·  ABSENT · MED
- **Lesson (verbatim, `project_ue5_pass.md`):** "Bo walks TitanicHG Unreal Engine 5 model at narrative timestamps … Claude reads each screenshot via native multimodal vision … identifies 1-2 specific concrete details NOT in current prose … writes a single Mode B sentence (short, declarative, concrete nouns, no subordinate clauses) for insertion." And the rationale: "Collapses the translation pipeline from 3 layers (eyes → narration → prose) to 1 (eyes → prose) … The screenshots are REFERENCE MATERIAL for the writer, not illustrations for the reader … Text-only book makes this MORE important — the prose IS the only rendering engine."
- **Ledger status:** ABSENT as a drafting technique. §6.5 records only the *forensic* half of this file (how UE5-render was told from a real photo — mist/star uniformity, uniform window color-temp). The generative half — feed the writer a rendered/spatial reference so it names details a human author wouldn't think to mention (shadow patterns, varnish reflections, rivet lines, material properties), then emit ONE concrete Mode-B line per image — is nowhere in §7 (illusion-of-single-author techniques) or §8 (per-unit protocol).
- **Bake-in:** Add to §7 (or `docs/vibe_writing_method.md`) a "VISUAL REFERENCE INGEST (optional)" note: when a book has a spatial source (a 3D/game model, a location the author can photograph, a floor-plan), the author may drop reference stills into an `image_input/`-style dir; the harness resizes ≤2000px (§10.3), vision-reads each, and for each emits a *single* concrete sentence in the book's terse register — reference for the writer, never an illustration for the reader (pairs with the §17.2 NO-interior-images rule). Image sizing note already lands in §10.3.
- **Note:** `project_ue5_pass.md` says "Status: PLANNED, not yet executed" — this technique was designed but never run, so it is a *proposed* method, not a shipped-and-proven one. Flag it advisory, not a gate.

### D-P2 — The "strip [IMAGE] blocks but ARCHIVE the prompts to a separate file first" production step  ·  WEAKER · LOW
- **Lesson (verbatim, `feedback_no_images.md` + `project_production.md`):** v10 "Strips ALL `[IMAGE — ...]` placeholder blocks from prose" but "Archives image prompts to separate file first" — "they're excellent writing and useful as shot lists for UE5 pass or future illustrated edition." §3.3 of the ledger already knows `[IMAGE …]` blocks are "consumed and skipped in text-only builds," but the ARCHIVE-before-strip step (don't just drop them; preserve them as a shot-list artifact) is not recorded.
- **Ledger status:** WEAKER. §3.3 skips `[IMAGE …]`; it does not say to preserve the stripped prompts. Minor.
- **Bake-in:** One clause in §3.3 / the assemble step: when stripping `[IMAGE …]` blocks for a text-only build, archive them to `outputs/markdown/<slug>_image_prompts.md` first (future illustrated edition / cover-art prompt seeds), rather than discarding.

### D-P3 — Front-matter page sequence for hardcover (Night Was Young, `project_production.md`)  ·  CONFIRMATION (already in prior delta)
- The half-title="just TITLE centered, small" + title-page="title + 'A Novel' + author" content rules from this file's front-matter table were ALREADY captured as **DELTA 7** in `_delta_titanic_projects.md` (extend §4.5 with content rules off `is_fiction`). Recorded here only so the diff is complete — no new bake-in. The recto-start + "page numbers begin at first prose page" + "÷4 for Mixam" rules are all in §4.3/§4.4/§4.5.

---

## COVER / ART / VISION

### D-C1 — SDXL and the KEEL Qwen vision server CANNOT co-reside on a 16 GB card (the live cover-loop's one hard runtime constraint)  ·  WEAKER · LOW
- **Lesson (verbatim, `reference_comfyui_hermes_hookup.md`):** "VRAM note: SDXL (~7-8GB) and the KEEL Qwen vision server (~7GB) can't co-reside on 16GB." Corroborated in `reference_keel_qwen_vision.md` ("~7GB VRAM resident") and `project_booksmith.md` (the live SDXL proof required launching ComfyUI *after* freeing VRAM).
- **Ledger status:** WEAKER *in the ledger proper*. The constraint IS fully documented in `docs/VALIDATION.md` (line 50: "cannot co-reside (5 GB free)") and `docs/SUPERSTRUCTURE.md` (the COVER gate node: "VRAM free enough? (SDXL ~7–8GB) — else stop KEEL vision on :8080 first"). But ledger §6.1/§6.5 — the constitution a session actually reads at cover time — never states it. A session that reads only the ledger could try to run SDXL gen with the KEEL vision server still resident and OOM.
- **Bake-in:** One clause in §6.1 (or §6.5): on a 16 GB GPU, SDXL (~7–8 GB) and the KEEL Qwen vision server (~7 GB) do not co-reside — the default is `--backend auto` (harness vision, off-GPU) so this is moot; when using `--backend keel`, stop the llama-server on :8080 before cover-gen and restart it for the verify pass. Cross-ref SUPERSTRUCTURE's COVER gate.

### D-C2 — Exact headless-ComfyUI launch mechanics (`--base-directory`, `--lowvram`, the `comfyui-frontend-package` gotcha, comfy-cli-not-on-PATH)  ·  CONFIRMATION
- **Lesson (verbatim, `reference_comfyui_hermes_hookup.md`):** "comfy-cli is NOT on PATH (launch via Comfy Desktop or `python main.py`) … checkpoint `sd_xl_base_1.0.safetensors` (~6.5GB) fetched into `…\Documents\ComfyUI\models\checkpoints`." Corroborated by `project_booksmith.md`: launch = "`main.py --base-directory Documents\ComfyUI --lowvram`; needed one-time `pip install comfyui-frontend-package` in its venv."
- **Ledger status:** CONFIRMED / already absorbed. §6.1 has the `comfy launch --background` + `run_workflow.py` + checkpoint-fetch flow; `docs/VALIDATION.md` (lines 42–52) and `docs/SUPERSTRUCTURE.md` (lines 93, 172) carry the exact `main.py --base-directory … --lowvram` launch AND the `comfyui-frontend-package` fix verbatim. No bake-in — already stronger in the BOOKSMITH docs than in these memory files.

### D-C3 — KEEL Qwen vision: exact `llama-server` invocation + the grammar⊕thinking 400-bug + `--mmproj` mandatory + `--jinja`  ·  CONFIRMATION
- **Lesson (verbatim, `reference_keel_qwen_vision.md`):** `llama-server.exe --model Qwen3.5-9B-Q5_K_M.gguf --mmproj mmproj-F16.gguf --host 127.0.0.1 --port 8080 --jinja --n-gpu-layers 99 --ctx-size 16384`; POST OpenAI-format `/v1/chat/completions` with base64 `image_url`; "`--mmproj` is mandatory … `--jinja` required … Do NOT send a GBNF grammar/json_schema together with thinking enabled (400-bug); parse a trailing `VERDICT: PASS/FAIL` line. ~7GB VRAM."
- **Ledger status:** CONFIRMED / already absorbed nearly verbatim in §6.5 (the full invocation, `--mmproj`-is-THE-switch, `--jinja`, the grammar⊕thinking mutual-exclusion, poll `/health`, port 8080 shared with cognition). No bake-in.

*(No cover ART-QUALITY delta here: the Gemini-Nano-Banana provenance + Topaz upscale + over-saturation-regrade-toward-honey-gold craft note lives in `project_cover.md`, already captured as **DELTA 5** of `_delta_titanic_projects.md`; not re-derived.)*

---

## WRITING / CRAFT

### D-W1 — "No interior images" — the rule is captured, but its ONTOLOGICAL rationale (and the multi-model convergence) is not  ·  WEAKER · LOW
- **Lesson (verbatim, `feedback_no_images.md`):** "No interior images. Text only. Converged independently across two Claude Opus instances and one Gemini Deep Think instance." Rationale: "Images fix the visual and collapse the reader's internal construction. The prose is the rendering engine. The reader builds the [book]." And the deeper cut: "The issue isn't uncanny valley — it's ontological. A photorealistic image … resolves the reader's uncertainty and turns her from renderer to rendered."
- **Ledger status:** The RULE is a hard author rule — §17.2 ("NO interior images (text only between the covers)"). Its *reasoning* is absent. That matters because the rule as stated reads like an aesthetic preference a future author might toggle off; the rationale explains it is load-bearing for any prose whose subject is perception/construction (and it generalizes: "give the reader substrate, not display"). `feedback_no_images.md` is already listed as a source in `_voiceprofile_feedback.md` (line 16), so the file is *absorbed* — only the rationale nuance is thin.
- **Bake-in:** Half a line in §17.2 (or the AUTHOR_VOICE doc): the no-interior-images rule is ontological, not merely aesthetic — images resolve the reader's construction and turn a co-author into a consumer; "the prose is the rendering engine." Author-overridable per book, but the default is text-only and the burden is on the exception. Advisory.

### D-W2 — The THEMATIC FINGERPRINT (floor / door-opens-from-inside / architecture-as-defense / autotelic terminal value) is still ABSENT as *stance*  ·  ABSENT · MED (already recommended, not yet baked)
- **Evidence in-scope this pass:** `user_bo.md` ("scale-invariant zoom, unashamed grandiloquence without irony shield"); the STA/dissolution files show the recurring move (build a room/framework as proof-of-worth; the production is the wall; the door opens from the inside; the attending is its own terminal value) even though those *specific* instances are project-canon.
- **Ledger status:** The voice **mechanics** are captured superbly (§17 + the five `author_voice/*` files: em-dash=0, semicolon ≥40/10k, the hammer, anaphora, "which is to say", "not X not Y", misspellings-as-fingerprints). The *thematic through-line* is NOT — `_voiceprofile_soul.md` mentions "The Floor" / "Same Shape" only as **capitalized sacred-term registry entries**, not as a described recurring motif. This exact gap was already flagged as **DELTA 10** in `_delta_titanic_projects.md` (add an advisory THEMATIC FINGERPRINT block to `AUTHOR_VOICE_Bo_Chen.md`) — and as of this read it is STILL not baked. This pass CORROBORATES that recommendation from a second, independent source set and raises confidence.
- **Bake-in:** As DELTA 10 already specifies — a short, advisory THEMATIC FINGERPRINT block in `docs/author_voice/AUTHOR_VOICE_Bo_Chen.md`: architecture-as-defense, the floor (presence needing no future to justify it), the door that opens from the inside (defenses end by running out of fuel, not external force), autotelic terminal value. Stance, not vocabulary; it guides synthesis-mode drafting, it does not gate. Keep the *instances* (Titanic, STA, Tori) OUT — only the shape travels.

### D-W3 — "Mode A / Mode B prose taxonomy" surfaces again (Mode B = short, declarative, concrete nouns, no subordinate clauses)  ·  WEAKER · LOW
- **Lesson (verbatim, `project_ue5_pass.md`):** the inserted line must be "a single Mode B sentence (short, declarative, concrete nouns, no subordinate clauses)."
- **Ledger status:** WEAKER. §18.3 already lists "the Mode A/B prose taxonomy" as under-captured (ASTRA §1–4). This file gives the crispest one-line *definition* of Mode B seen in the corpus, worth pinning wherever the taxonomy eventually lands.
- **Bake-in:** When §18.3's Mode A/B item is developed, use this definition for Mode B: concrete-sensory register — short, declarative, concrete nouns, no subordinate clauses (vs Mode A = the argumentative/framework register). No standalone edit needed.

---

## VOICE

### D-V1 — `user_bo.md` voice line  ·  CONFIRMATION
- **Lesson (verbatim, `user_bo.md`):** writing voice = "recursive restatement, mechanical metaphors, mixed register, scale-invariant zoom, unashamed grandiloquence without irony shield."
- **Ledger status:** CONFIRMED / fully absorbed. Every element is in the `author_voice/*` corpus: recursive restatement (`_voiceprofile_soul.md` §opening-restatement, `_empirical.md` anaphora/epistrophe), mechanical/architectural metaphors (`AUTHOR_VOICE_Bo_Chen.md` line 20), mixed register (framework vs personal voice, `_voiceprofile_soul.md` §52), scale-invariant zoom (`_voiceprofile_soul.md` §60). No bake-in.

### D-V2 — The narrative canon files (`sta_mappings`, `dissolution_layers`, `user_tori`, biographical `user_bo`) are correctly OUT OF SCOPE  ·  CONFIRMATION (deliberate exclusion)
- **Files:** `reference_sta_mappings.md` (Brad↔Captain Smith, Marcolin↔Captain Lord, Jocelyn↔the band, Bowman↔Ismay, the fourth-funnel dummy role, "binoculars locked in the crow's nest" = Teams recording ban, etc.); `reference_dissolution_layers.md` (the 6-layer Packard-Bell→C++-solver→Three.js→Phase-State-Map→ship stack, run forward in Part I / backward in Part V); `user_tori.md` (unidirectional care circuit, too-good-to-be-true detector, the bathroom door, the snowdrop tattoo, glass-door scars); the biographical body of `user_bo.md`.
- **Ledger status:** ABSENT — and that is CORRECT, not a gap. These are the private canon of one novel. The kit's own doctrine (`_voiceprofile_feedback.md` line 195: project-specific cast/parts/targets are ignored outside their project) forbids baking them. A future lessons-scan should NOT treat their absence as a delta to fix.
- **Bake-in:** NONE. Explicitly recorded as do-not-bake so this negative result survives and is not re-litigated. (If desired, one line could be added to §17's meta-rule: "author-LEVEL voice/theme travels; book-LEVEL narrative canon — characters, institutional mappings, plot devices — stays in its own workspace and is never promoted to the kit.")

---

## PROCESS

### D-X1 — `MEMORY.md` index is STALE on the BOOKSMITH cover-gen status  ·  WRONG · LOW (hygiene)
- **Lesson (verbatim, `MEMORY.md` line 22):** BOOKSMITH "built + loop-tested 2026-07-11 (deterministic pipeline green, live vision proven, **SDXL gen pending VRAM**)."
- **Reality (`project_booksmith.md`, same session, 2026-07-11):** "The live SDXL cover-gen is ALSO now proven … `cover_gen.py` produced real SDXL art, all covers composited onto it, and KEEL Qwen QC-verified the AI's OWN cover → PASS. **Fully validated end-to-end — nothing left unproven.**" Corroborated by `docs/VALIDATION.md` + `SESSION_LOG.md` line 175 ("Live SDXL cover gen PROVEN").
- **Ledger status:** WRONG in the index file. This is a memory-index staleness, not a ledger rule error — the ledger and BOOKSMITH docs are correct. Flagged for hygiene: an index that says "pending" for a proven capability could make a future session redundantly "re-prove" it or under-claim the kit's readiness.
- **Bake-in:** Not a ledger edit. This belongs in the Titanic memory store, not BOOKSMITH — recommend updating `MEMORY.md` line 22 to "SDXL gen PROVEN end-to-end (2026-07-11)." Recorded here so the discrepancy is not lost; the actual fix is a one-line index update in `~/.claude/projects/C--Claude-Titanic/memory/MEMORY.md`, outside this kit's scope.

### D-X2 — Full 9-format roster + Blurb/Mixam-paperback/EPUB preset provenance  ·  WEAKER · LOW
- **Lesson (verbatim, `project_booksmith.md`):** "EPUB export (`build_epub.py`, EPUB 3, KDP-preferred); 25-font OFL library at `fonts\library\` … Mixam paperback + Blurb trade paperback + Blurb ImageWrap hardcover presets (`_tools\print_presets.json` + shared `preset_lookup.py`; sourced from Mixam's live calculator/template APIs + template PDFs and Blurb's own booksize calculator; all three verified green) — 9 formats total."
- **Ledger status:** WEAKER. The ledger's format universe is framed around the five/six core formats (§2.1 outputs subfolders; §5 covers KDP + Mixam); the full **nine**-format roster (adds EPUB, Mixam paperback, Blurb trade paperback, Blurb ImageWrap hardcover) and the fact that the Blurb/Mixam-paperback numbers came from those services' own calculators/template APIs (the same "validator-wins" discipline as §13) is documented in `KIT_ARCHITECTURE.md`/`SESSION_LOG.md` but not surfaced in the ledger's spine-geometry section.
- **Bake-in:** Optional — a one-line pointer in §5 (or §13) that Blurb (trade PB + ImageWrap HC) and Mixam-paperback presets exist in `_tools/print_presets.json`, each derived from the service's own calculator/template (validator-wins per §13), and that EPUB 3 is a produced format alongside Kindle DOCX. Low priority; it is architecture already recorded elsewhere, just not in the ledger.

---

## SUMMARY TABLE (delta → source → ledger status → bake-in → grade)

| # | Delta | Source file(s) | Ledger now | Bake-in target | Grade |
|---|---|---|---|---|---|
| D-P1 | UE5 / spatial reference as WRITER material (eyes→prose, 1 Mode-B line/image) | `project_ue5_pass.md` | ABSENT (only the forensic UE5-vs-real half, §6.5) | §7 / vibe_writing_method | **MED** |
| D-W2 | Thematic fingerprint (floor / door / architecture-as-defense / autotelic) as *stance* | `user_bo`, sta/dissolution (shape only) | ABSENT (already = DELTA 10, still unbaked) | AUTHOR_VOICE doc (advisory) | **MED** |
| D-C1 | SDXL + KEEL-Qwen can't co-reside on 16 GB | `comfyui_hermes_hookup`, `keel_qwen_vision` | in VALIDATION/SUPERSTRUCTURE, not in ledger §6 | §6.1/§6.5 clause | LOW |
| D-P2 | Archive `[IMAGE]` prompts before stripping (shot-list artifact) | `feedback_no_images`, `project_production` | WEAKER (§3.3 strips, doesn't archive) | §3.3 / assemble step | LOW |
| D-W1 | No-interior-images RATIONALE (ontological, not aesthetic) | `feedback_no_images` | rule in §17.2; reasoning absent | §17.2 clause | LOW |
| D-W3 | Mode B one-line definition (short/declarative/concrete/no-subordinate) | `project_ue5_pass` | §18.3 lists taxonomy as under-captured | fold into §18.3 item | LOW |
| D-X1 | MEMORY.md index stale: SDXL "pending" but PROVEN | `MEMORY.md` vs `project_booksmith` | WRONG (index only) | update Titanic `MEMORY.md` (outside kit) | LOW |
| D-X2 | Full 9-format roster + Blurb/Mixam-PB/EPUB preset provenance | `project_booksmith` | WEAKER (ledger frames 5–6 core) | §5/§13 pointer | LOW |
| D-P3 | Night-Was-Young front-matter content rules | `project_production` | already = DELTA 7 (`_delta_titanic_projects`) | — (done) | CONFIRM |
| D-V2 | STA/Tori/dissolution narrative canon | `sta_mappings`, `dissolution_layers`, `user_tori` | ABSENT — CORRECTLY (project-scoped) | NONE (do-not-bake) | CONFIRM |

*Highest value: **D-P1** (a real, missing drafting technique — spatial reference feeding the writer, distinct from the vision-verify loop the kit already has) and **D-W2** (the thematic-stance gap, now corroborated by a second source set — bake the advisory block). Everything else is precision, rationale, or hygiene. The load-bearing NEGATIVE result — **do not bake the novel's STA/Titanic/Tori canon into the kit** — is recorded as D-V2 so it is never re-flagged as a gap.*

---

## CONFIRMATIONS (honest diff — what the ledger + BOOKSMITH docs already have right)

- **ComfyUI cover-gen (`comfyui_hermes_hookup`):** hermes `creative/comfyui` skill v5.1.0 (NOT FERRYMAN); `run_workflow.py` + `_common.py` + `workflows/{sdxl,flux}_txt2img.json`; SDXL base ~6.5 GB default on 16 GB, Flux-dev-fp8 ~12 GB opt-in; **no title/author text in the AI art** (PIL composites typography after); `main.py --base-directory … --lowvram` launch + one-time `comfyui-frontend-package`; comfy-cli not on PATH. → ledger §6.1 + `cover_pipeline.md` + `VALIDATION.md` + `SUPERSTRUCTURE.md`. **Full — the BOOKSMITH docs are stronger than the memory file.**
- **KEEL Qwen vision (`keel_qwen_vision`):** exact `llama-server` line; `--mmproj` mandatory + `--jinja`; POST OpenAI `/v1/chat/completions` base64 image; grammar/json_schema ⊕ thinking = 400-bug → parse a trailing `VERDICT:` line; resize <2000px first; ~7 GB VRAM; port 8080 shared with cognition. → ledger §6.5 (near-verbatim). **Full.**
- **`feedback_no_images` (the RULE):** text-only between the covers; strip `[IMAGE …]` in the production build; the cover + endpapers stay visual. → §17.2 hard author rule; §3.3 consumes `[IMAGE …]`; file already source-listed in `_voiceprofile_feedback.md`. **Full** (only the rationale + archive-step are thin — D-W1/D-P2).
- **`user_bo` (VOICE):** recursive restatement / mechanical metaphors / mixed register / scale-invariant zoom / grandiloquence-without-irony-shield. → fully in the `author_voice/*` corpus. **Full.**
- **`project_production` (Night Was Young v10/v11):** strip `[IMAGE]`, front-matter recto sequence, half-title minimal + "A Novel" form-line, page numbers from first prose page, ÷4 for Mixam, one-generator-per-version (v11 byte-identical to v10 but 6 lines). → §3.3, §4.3, §4.4, §4.5, §3.1, and **DELTA 7** of the prior projects-delta. **Full** (only D-P2 archive-step new).
- **`project_booksmith` (kit self-description):** the config-driven (`book_config.json` + `kit_env.json`) closed-loop one-shot; mechanical + perceptual gates; live vision + live SDXL both proven. → the whole ledger + `KIT_ARCHITECTURE.md` + `VALIDATION.md`. **Full** (D-X2 = the 9-format roster is the only under-surfaced sub-fact; D-X1 = MEMORY.md's *index* is the stale one, not this file).
- **`sta_mappings` / `dissolution_layers` / `user_tori`:** deliberately NOT in the kit — project-scoped novel canon. **Correctly excluded** (D-V2).

*End of delta audit. Written to disk 2026-07-12 03:1x -05:00 (Central). This file is the durable record; the reply summary is disposable.*
