# PORTABILITY GAP ANALYSIS — "giftable to anyone, one-shot"

*2026-07-11. Method: four parallel Opus auditors (Python toolchain / JS + assets / docs + orchestration / distribution hygiene) read the entire kit; findings synthesized here. This is the working document of the portability initiative — update statuses in place. Goal: BOOKSMITH as a portable, self-contained folder that any stranger can drop onto their own machine running Claude Code and use to vibe-write books, aspiring to one-shot finished.*

**Status legend:** ✅ done · 🔄 in progress · ⬜ open · 🤝 needs Bo's decision

---

## Verdict

The architecture was already portable — the kit_env seam exists and is read by the five scripts that need it, node_modules is vendored pure-JS, 12 of 17 Python tools are cross-platform stdlib-or-common-pip, fonts are vendored repo-relative, and the hook *scripts* were internally relocation-clean. What welded the kit to the reference machine was the **operational layer**: no install story, no kit_env template, hooks invoked by absolute path, docs instructing the session to run organ paths that exist on exactly one PC, START_HERE routing strangers into the author's private in-flight book, an un-guarded `git add -A` path to publishing that book, and OFL fonts shipped without their license texts. **Nearly all of that is now closed (see Wave 1).** The irreducible Tier-1 core is two Word-COM scripts — print fidelity legitimately requires Windows + Word; everything else runs anywhere.

## TOP FIVE — NEXT (chosen 2026-07-11; highest ROI × lowest effort; order = dependency)

| # | Change | Effort | Why it's the bang-for-buck |
|---|---|---|---|
| 1 | **Hygiene sweep**: commit everything since `82a1203` (needs Bo's word) + LICENSE (MIT recommended, Bo's call) + one-line hooks disclosure in INSTALL.md + neutralize "Bo Chen" in `book_config.example.json` | minutes | Kills the largest standing risk (two waves of work uncommitted); makes gifting legally defined |
| 2 | **ONBOARD v1 — "just say hi"**: `docs/onboarding_playbook.md` (three doors, react-don't-specify, voice ladder, elicitation branch, sufficiency rubric + assumptions ledger, mirror-back, anti-pattern never-list, 4 test personas) + ONBOARD in CLAUDE.md §1 + first-run branch in `on_session_start.py` (virgin state → inject the onboarding directive) + compile-conversation-to-intake | ~half a day, mostly prose | The entire "hand it to anyone who doesn't know what a harness is" UX; the user manual's promise becomes literally true |
| 3 | **`_tools/manuscript_ingest.py`**: PDF/DOCX/EPUB/TXT → clean markdown into `intake/converted/` (PyMuPDF already ships; docx via zipfile XML; epub via zipfile + HTML strip) | small | Real users drop PDFs on day one — the kit currently can't read them portably; also the enabling tool for REFORGE |
| 4 | **`_tools/check_synthesis.py`**: the GATE-4 anthology tell as a script — per-unit canon-anchor/citation distribution; synthesis mode fails any unit mapping ~1:1 to one source | small | Converts the tacked-on failure from taste into a machine-checkable gate |
| 5 | **The graduation exam**: one true one-shot — fresh small book, intake → finished folder, zero mid-flight help; every stumble becomes a new ledger rule | one supervised run | "One-shot finished" becomes a demonstrated property instead of an aspiration; exercises #2–#4 end-to-end |

*The end-user manual (`HOW_TO_USE.pdf`, kit root + zip) is written against the post-top-five state: "say hi" (=#2) and "make this better" (=#3) are its promises; both carry today-valid fallbacks (the START_HERE paste line; markdown/txt intake).*

## The tier model (what a stranger gets)

| Capability | Tier 1 (Windows + Word) | Tier 2 (anything else) |
|---|---|---|
| EPUB 3, Kindle DOCX | ✅ | ✅ |
| Print interiors → PDF, page counts, recto parity, spine math | ✅ (Word COM) | ⬜ future: LibreOffice + PyMuPDF fallback |
| Cover compositing + wrap geometry (all 9 profiles) | ✅ | ✅ (PIL + fitz) |
| Cover ART generation | optional GPU stack | optional GPU stack (else bring-your-own art) |
| Perceptual verification | ✅ (auto: KEEL if configured, else Claude vision) | ✅ (Claude vision) |
| Compaction survival / rehydration | ✅ | ✅ |

`python _tools/doctor.py` prints the machine's tier + per-capability remedies. `python _tools/make_giftable.py` builds the clean distribution zip (personal-data gate blocks leaks).

---

## Wave 1 — landed 2026-07-11 (all verified: py_compile clean, JSON parses, gate CLEAN, doctor Tier 1 on the reference box)

| # | Fix | Where |
|---|---|---|
| ✅ | `.gitignore` guard: `book_workspace/*` (testvoyage excepted), `_REHYDRATION.md`, `_CONTINUITY.snapshot.md`, `.booksmith_rehydrate`, `dist/` — kills the `git add -A` → private-book-published hazard | `.gitignore` |
| ✅ | Hooks invoked relative (`python _tools/on_session_start.py`) — survive any install location | `.claude/settings.json` |
| ✅ | Recovery instruction derives its path from `Path(__file__)`, not `C:\BOOKSMITH` | `_tools/on_session_start.py` |
| ✅ | Organ token-counter resolved via `kit_env.organs` → vendored `_tools/estimate_tokens.py` → tiktoken/chars-4 (was a hardcoded organ path) | `_tools/rehydrate.py` |
| ✅ | `requirements.txt` — the canonical audited dep list (the old kit_env list named 4 packages nothing imports) | repo root + `_tools/kit_env.json` note |
| ✅ | `kit_env.template.json` — placeholder machine config; optional blocks documented as optional; vision defaults `claude` | `_tools/` |
| ✅ | Word-COM import guards → actionable `word_com_unavailable` JSON instead of ImportError traceback on non-Windows; digital-PDF builder imports Word lazily (runs anywhere given a pre-rendered interior PDF) | `docx_to_pdf.py`, `check_part_pages.py`, `build_digital_pdf.py` |
| ✅ | `vision_verify.py --backend auto` (new default): keel only when kit_env names a real local server binary; else Claude vision. Verified: live kit_env→keel, template→claude, missing→claude | `_tools/vision_verify.py` |
| ✅ | Architecture doc: ghost `PRODUCTION_LESSONS_LEARNED.md` refs → `LESSONS_LEDGER.md` (incl. the autonomous loop's diagnosis target); five→nine formats (pipeline, outputs tree, produce-format grammar); docs tree now matches disk | `KIT_ARCHITECTURE.md` |
| ✅ | `START_HERE.md` genericized (doctor/INSTALL first, organ fallbacks, tier framing, model policy de-personalized); the author's private resume block moved to gitignored `book_workspace/unfinished_mirror/_RESUME_NOTES.md`; `_CONTINUITY.md` now carries the cross-project `--session` pointer | `START_HERE.md` + workspace |
| ✅ | `INSTALL.md` — stranger onboarding: prerequisites table, 6-step setup, first book, small-context note, fast triage | repo root |
| ✅ | OFL compliance: 14 `OFL_<Family>.txt` fetched from canonical google/fonts + attribution README (fonts were redistributable; the license texts weren't shipping) | `fonts/LICENSES/` |
| ✅ | `_tools/doctor.py` — 10-check preflight, PASS/WARN/FAIL + remedy per capability, tier verdict, `--json`; never tracebacks | new (opus builder) |
| ✅ | `_tools/make_giftable.py` — one-command clean zip: excludes private/machine/third-party-copyright material, trims example outputs to one format; a personal-data gate blocks the build on any hit of the author's identifiers, the prior project's slug, or reference-machine tool roots (patterns live in the script) | new (opus builder) |
| ✅ | Personal-data scrub of shipped text: 7 sites genericized (hermes paths → `kit_env.cover_gen` refs; slug examples de-personalized; ledger §15.2 wording) → gate verdict **CLEAN** (132 files, 19.5 MB) | ledger, KIT_ARCH, VALIDATION, cover_gen, rehydrate, COMPACTION_SURVIVAL |

## Wave 1.5 — the cover-stack DNA + the first giftable (landed 2026-07-11, same day)

| # | Item | Notes |
|---|---|---|
| ✅ | `_tools/comfy_client.py` + `_tools/run_batch.py` shim — self-contained pure-stdlib ComfyUI client, drop-in for the hermes runner (verified against cover_gen's OWN parsers; connection-traced node patching works on SDXL and Flux graphs) | replaces the hermes skill dependency |
| ✅ | `_tools/workflows/` — sdxl_txt2img.json + flux_dev_txt2img.json vendored clean | the workflow "genes" now ship |
| ✅ | `_tools/fetch_weights.py` — resumable (Range + .part + atomic rename), retrying, hash-verifying weight downloader; `sdxl` profile reads kit_env. The personal fetcher organ's lessons, vendored | weights self-download on any machine |
| ✅ | `_tools/estimate_tokens.py` — vendored token sizer (tiktoken → chars/4); output format parses under rehydrate.py's existing regex; rehydrate resolves kit_env → vendored → chars/4 | replaces the chunker sizer organ |
| ✅ | Gate hardening: machine-root patterns added (chunker/imguard/Everything/fetcher/llama.cpp/models/hermes); scanner exempts itself and third-party `node_modules` (upstream authors' emails are not leaks) | regression-proof |
| ✅ | All shipped docs scrubbed of organ/machine paths (CLAUDE.md full generalization pass: organs→fallbacks, Bo→the author, five→nine, MAINTAIN mode, small-context profile, relative rehydrate paths; README, cover_pipeline, LESSONS_LEDGER, COMPACTION_SURVIVAL, KIT_ARCHITECTURE, format_spec_sheet, composite_cover comment) | the docs layer no longer instructs dead paths |
| ✅ | **First giftable built: `dist/BOOKSMITH_giftable_20260711.zip`** — 526 files, 12.8 MB compressed (node_modules included for offline install), gate CLEAN, zip integrity verified, zero forbidden entries | the USB artifact |

*Known nuance: the template's repo-relative `cover_gen.run_workflow` resolves against the session's cwd — correct when Claude Code is opened at the kit root (the documented flow); revisit if cover_gen ever runs from elsewhere.*

## Wave 2 — open (ordered)

> **UPDATE 2026-07-12 (kit-hardening campaign; branch `kit-hardening-2026-07-12`, commit 45f27e2):** CLOSED this pass: cover_gen.py graceful no-stack failure ✅ · CLAUDE.md/README nine-format consistency ✅ · format_spec_sheet Kindle 1600×2400 (matches code) ✅ · `.gitattributes` ✅ · PyPDF2→pypdf migration ✅ · book_config.example.json author neutralized ✅ · examples/ pointer fixed ✅ · FONTS.md count ✅. ALSO shipped: NEW `_tools/selfcheck.py` (the kit self-consistency meta-gate, wired into SUPERSTRUCTURE §6 + CLAUDE.md §10); a single-source-of-truth KDP wrap-math dedup (verify_build + composite_cover both delegate to preset_lookup). STILL OPEN below: small-context profile; Tier-2 LibreOffice print fallback; config-driven ornament/code/math fonts; generator `--help` polish.

| # | Item | Notes |
|---|---|---|
| ⬜ | **CLAUDE.md generalization pass** | Organ invocations → "optional accelerators + portable fallbacks" (§1.5 boot, §3 init/ingest, tool-invocation table); five→nine formats (§0, produce-format list, §12); "Bo" → "the author" in operational text (grammar intro, pauses, escalations) while keeping `[BO-WRITES]` as the literal marker token (document it as "the author-writes marker") or make it configurable via `voice`; "64-rule constitution" → unfrozen phrasing; add a **MAINTAIN mode** to §1 mode detection (kit-polish sessions — currently verbal-override only); point boot at `doctor.py`/`INSTALL.md` on fresh machines; vision default text → auto |
| ✅ | **README pass** (landed) | five→nine formats ("nine upload-ready deliverables"), Tier 1/Tier 2 prerequisites banner, INSTALL/doctor pointers; the empty-`examples/` claim is gone (README points at `book_workspace/testvoyage`) |
| ✅ | `format_spec_sheet.md` title now says "all nine formats" (landed) | one-line fix; addendum already correct |
| ✅ | `cover_gen.py` graceful no-stack failure (landed) | `_cover_gen_env_error` emits structured `{"status":"error", ...}` JSON with a "place your own art in cover_art/; compositing/verify still work" hint on a misconfigured/empty `kit_env.cover_gen` |
| ⬜ | Populate `examples/` | copy testvoyage (seed + config + contracts + manuscript + one format's outputs) or fix README to point at book_workspace/testvoyage |
| ⬜ | Small-context operating profile | reduced Context Pack (drop N−2 prose, compress registries) documented in CLAUDE.md §6 + COMPACTION_SURVIVAL framing for <1M models |
| ⬜ | **Tier-2 print fallback** | `docx_to_pdf.py` LibreOffice branch (`soffice --headless --convert-to pdf`) + `verify_build.py` page-count/recto checks from the rendered PDF via PyMuPDF when Word absent; label output "LibreOffice-rendered — verify in the service previewer" |
| ⬜ | Ornament/code/math fonts config-driven | "Segoe UI Symbol"/"Consolas"/"Cambria Math" hardcoded in both generators; expose in `book_config.interior` with portable defaults |
| ⬜ | Neutralize `book_config.example.json` author ("Bo Chen" → placeholder) | example content itself (Titanic novel) is fine |
| ✅ | `.gitattributes` (`* text=auto` + binary marks for ttf/pdf/docx/epub/jpg/png) (landed) | file now ships at repo root |
| ⬜ | PyPDF2 → pypdf migration | PyPDF2 is EOL; drop-in API. STILL OPEN: `requirements.txt` still declares `PyPDF2>=3.0` |
| ✅ | Generators: real `--help`, quiet expected-error output (no stack dump) (landed) | `generate_book.js` + `generate_kindle.js` both parse `-h/--help` and print a USAGE block |
| ⬜ | `FONTS.md` count fix (says 25; 27 TTFs exist) + note pointing at `fonts/LICENSES/` | cosmetic |

## Wave 3 — the organism layer (brainstormed 2026-07-11, Bo voice session; design captured, not yet built)

*The unifying move: the kit stops being "a Claude Code project on one PC" and becomes a self-describing organism — portable contracts + portable toolchain + THIN, re-derivable harness bindings. All items below are additive to Waves 1–2.*

| # | Item | Design notes |
|---|---|---|
| ✅ | **Ingest topology rule — "skim-then-delegate, never delegate-blind"** (landed 2026-07-11) | Baked into CLAUDE.md §3 init/ingest + GATE-1, KIT_ARCHITECTURE §(a)+(d), LESSONS_LEDGER §1.5 (with the failure story), START_HERE step 2. Main loop reads the core fully + skims every satellite BEFORE fan-out; subagents provide depth, never structure. |
| ✅ | **Relational digests** (landed 2026-07-11) | `templates/digest.template.md` created (Source / Key content w/ anchors / RELATION TO THE CORE / Synthesis hooks / Voice / Do-NOT-import); contract enforced by LESSONS_LEDGER §1.6 (digest missing the RELATION section → re-run) + GATE-1. |
| ✅ | **Integration-mode knob + the one clarifying question** (landed 2026-07-11) | `integration_mode` enum (synthesis default \| anthology \| reforge) added to book_config.schema.json + example; the one-time intake question in CLAUDE.md §3 + START_HERE; seed template §1.2 row; GATE-2 requires it declared; LESSONS_LEDGER §1.7. |
| ✅ | **Synthesis gate (GATE-4 extension)** (landed 2026-07-11 — contract-level; the check is model-run at GATE-4, no script) | CLAUDE.md GATE-4 + KIT_ARCHITECTURE GATE-4 + §4 Never-list: in synthesis mode no unit maps ~1:1 onto a single source (canon-anchor distribution = the anthology signature). NOTE: the Unfinished Mirror's return face (ch_09–15) maps nearly one-satellite-per-chapter by seed design — at resume, each return chapter must grow from the core + its mirror-pair with the satellite dissolved in; restructuring the seed itself is a Bo decision. |
| ⬜ | **REFORGE mode** (existing-book rebirth) | Fifth entry mode: user drops a finished/half-finished manuscript (pdf/docx/epub/txt). Decompose with existing tools → hold whole book (or skim+relational-digest if oversized) → interview intent ("what's wrong with it, what do you wish it was, who's it for now, any passages sacred verbatim, real names or changed?") → mirror-back diagnosis → re-synthesize from first principles in the author's register at full altitude (re-derive, never line-edit). Gates: mechanical "nothing lost unintentionally" (inventory claims/scenes in original → coverage map → user-visible consciously-dropped list) + perceptual better-than-sum. Distinct from unit-level `revise`. |
| ⬜ | **Drive-wide discovery, consent-scoped** | When the user hints at scattered material, the session offers (never assumes) a machine-wide search: candidate manifest → user approves → SNAPSHOT into intake/ (never reference originals in place). Accelerators when present: `everything` (names), `everywhere` (contents — C:\everywhere, GPU content-grep, spec-first), `cortex` (meaning); portable fallback = the harness's own glob/grep. Wire as optional `kit_env.organs` slots. |
| ⬜ | **Harness abstraction — AGENTS.md front door + harness profiles** | Ship `AGENTS.md` (the emerging cross-harness rules convention; OpenCode reads it natively) that routes any harness into the same contract. New `docs/harness_profiles/`: `claude-code.md` (hooks, ~/.claude/projects jsonl, Agent tool, 2000px image cap), `opencode.md` (storage at %LOCALAPPDATA%\opencode\storage\ / ~/.local/share/opencode/storage\, JS plugins, session.compacting hook ≈ PreCompact, session-start recall ≈ SessionStart), `generic.md` (the re-derivation protocol). Boot step 0: identify your harness → load profile → unknown harness → generic protocol. |
| ⬜ | **Compaction-survival DNA, harness-generic** | Layer inventory: the _CONTINUITY ledger + unit-atomic writes are ALREADY harness-free (the universal core). Transcript rehydration is harness-specific → per-profile adapter (Claude Code: jsonl, shipped; OpenCode: storage JSON/SQLite → adapt transcript_to_md). Hooks are harness-specific → per-profile equivalents. GENERIC RECIPE for unknown harnesses (the glue): (1) emit a unique nonce into the conversation, (2) content-search the disk for files containing it — whatever file holds it IS the session record, (3) reverse-engineer its format (JSON-lines/JSON/SQLite; strip to role+text), (4) tier to token budget, write _REHYDRATION.md, (5) if no record is findable, fall back to ledger-only discipline. Encode the recipe as text in COMPACTION_SURVIVAL.md — the model re-derives the mechanism on any substrate. |
| ⬜ | **Model-floor honesty** | Harness-agnostic ⇒ model-agnostic ⇒ some operators run weaker models. The gates already protect mechanics; voice/synthesis quality degrades gracefully, not silently: doctor-style self-calibration note ("your model tier affects prose quality; gates still hold") + optional probe (write a test paragraph against exemplars, self-grade). |

## Decisions that are Bo's 🤝

1. **LICENSE** — the kit ships with none; "hand to anyone" is legally undefined without it. MIT or Apache-2.0 for the tooling (the vibe-writing method doc is already CC-BY-4.0; fonts OFL).
2. **Interior default font for NEW books** — keep Georgia (Windows-only, silently substitutes elsewhere → pagination drift; doctor now warns) vs. default new books to a vendored OFL face (EB Garamond/Literata) with Georgia as the reference-machine choice.
3. **Commit strategy** — everything above is uncommitted working tree. Recommended: commit the kit hardening now; the private book workspace stays untracked (gitignore now guarantees it).
4. **Public-release path** — if the GitHub repo ever flips public: `git init` a fresh history from the giftable tree instead. The existing history already embeds the 24 MB testvoyage outputs and the third-party `guide.pdf`, and the packager's exclusions don't rewrite history.
5. **`[BO-WRITES]` marker** — keep the literal token (zero code churn, documented meaning) or rename/configure (`[AUTHOR-WRITES]`) in the generalization pass.

## Third-party material ruling (from the audit)

- `docs/service_templates/guide.pdf` (7.4 MB Mixam print guide) + 3 Mixam dieline PDFs: **excluded from the giftable by default** (`--keep-service-templates` overrides). The load-bearing numbers already live in `format_spec_sheet.md`/`print_presets.json`; keep the originals locally as evidence.
- Captured Blurb calculator JSON + spec-page text extracts: ship (small, our own captured data), low risk.
- `node_modules`: excluded by default (`npm install --prefix _tools` restores from the pinned lockfile); `--include-node-modules` ships it for a truly offline gift.
