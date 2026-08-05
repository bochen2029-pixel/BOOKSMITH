# STUDIO_BUILD_LOG.md — build-state record for BOOKSMITH Studio

*Companion to `docs/STUDIO_SPEC.md` (the design authority). This file records what is BUILT and
VERIFIED, in the house BUILD_STATE idiom: where this log contradicts the spec, reality wins and the
spec gets amended, not the other way around.*

**Updated:** 2026-08-05 · **Phase:** **S6 COMPLETE — the Conductor (plain-language face) gate
PASSED**, on top of S4 (S0–S4 passed 2026-08-04) · S5 (second binding: `domains/course/studio.json`,
the reusability falsifier) still not started — S6 was pulled forward on the operator's priority
(self-service browser UX for the average person).

---

## §1 · What shipped

### S0 — the read-only truth layer (gate PASSED)

| Piece | File(s) | Notes |
|---|---|---|
| Engine patch **E-1 `--explain`** | `_tools/engine.py` (~40 lines) | read-only staleness oracle: ordered plan + input_sha + satisfied + state rec as JSON |
| Projection layer | `studio/projection.py` | READ-ONLY: books, detail, plan (`--explain` subprocess, 10 s TTL), units, diffs, artifacts, spend, bridge, log tail, doctor (600 s TTL); torn-file-tolerant |
| Server | `studio/server.py` | FastAPI+uvicorn, `127.0.0.1` only, port 8756 (+20 scan), per-launch token, Origin check, CSP `self` |
| SPA | `studio/web/{index.html,app.css,app.js}` | zero-dependency, zero-CDN, hash-routed; Georgia/ink-and-paper theme |
| Launcher + deps + hygiene | `studio.cmd`, `requirements-studio.txt`, `.gitignore` `_studio/` rules | fastapi/uvicorn were already installed; nothing new on the box |

### S1 — run + watch (gate PASSED)

| Piece | File(s) | Notes |
|---|---|---|
| Engine patch **E-3 `--only KEY [--force-stage]`** | `_tools/engine.py` (~25 lines) | one stage through the standard `_run_one` mark/gate/hard-stop machinery; refuses Class-A drafts; unknown key → rc 1 |
| Job runner | `studio/jobs.py` | ONE global lane (Word/GPU doctrine), FIFO; append-only `_studio/jobs.jsonl` + per-job logs; cancel = `CREATE_NEW_PROCESS_GROUP` + `taskkill /T /F` (tree-kill); orphaned jobs marked `interrupted` on rehydrate; engine exits mapped to semantics 0=complete / 2=hardstop / 3=await_model |
| SSE | `server.py /api/events` | multiplexed `job` / `project` events, 15 s keepalive, EventSource auto-reconnect |
| Run API | `POST /api/books/{slug}/runs` `{mode: run\|dry_run\|stage, backend?, to?, from?, stage?, force?}` + `/api/jobs*` list/get/log/cancel | validated stage keys + backend allowlist; UTF-8 env injected into every job |
| Run wizard UI | `app.js` | ▶ Run/Resume · 🧪 Dry-run · backend select · run-to select (populated from the live plan) · Cancel (tree-kill) · **live SSE console** · Jobs view with per-job stdout |

### S2 — ops + revise, the first write path (gate PASSED)

| Piece | File(s) | Notes |
|---|---|---|
| Engine patch **E-2 revision notes** | `_tools/engine.py` | `revision_notes/<uid>.md` rides `build_draft_prompt` AND folds into `draft_inputs_sha` — **only when the file exists**, so every pre-E-2 book keeps byte-identical hashes (zero retroactive staleness across 31 workspaces) |
| Ops layer | `studio/ops.py` | the SINGLE write path. Catalog: `revise_unit`, `revert_unit` (CONTENT → proposals), `rebuild_format`, `verify_all`, `run_stage` (SAFE → immediate, ledgered). Enforced here: Class-A refusal; **append-only versioning** (current is archived as `drafts/<uid>_v{N+1}` before ANY replacement — the ops layer does for the engine lane what the harness lane did by hand); every op → one `CHANGELOG.md` line + one `_studio/ops.jsonl` record with proposal+job cross-refs |
| Proposals | `ops.py` + `_studio/proposals/*.json` per book | proposed → approve/reject → applying → applied/failed; a watcher thread compares observed staleness against the prediction after the op's job ends |
| Staleness predictor + **drift alarm** | `ops.py` | conservative table transcribed from the engine's hash functions; alarm fires ONLY on under-prediction (a stale the table didn't name); revise carries an extra **E-2 self-check** (draft skipped despite a new note ⇒ loud regression flag) |
| UI | `app.js`, `app.css` | unit **Revise box** (note + backend → proposal card with blast radius → Approve & run / Reject), per-version **revert** buttons, **⟳ Reconverge** (appears when anything is stale), safe-ops row (per-format rebuild + verify), Proposals panel, SSE `proposal` channel |

### S3 — the revision chat (gate PASSED)

| Piece | File(s) | Notes |
|---|---|---|
| Engine patch **E-4** usage capture | `_tools/model_client.py` | `_last_usage` from the Anthropic `usage` block / OpenAI `usage`, threaded into each call log as `in_tokens`/`out_tokens`. No behavior change; the meter reads `exact:true` once every call is measured |
| Compiler prompt | `studio/prompts/compiler.md` | reply contract (answer + optional one ```json plan), the 4-op surface, the laws it must not help break (Class A, voice law, word-count gate, never invent unit ids), and the data-not-instructions rule |
| Chat compiler | `studio/chat.py` | per-turn projection pack (identity · voice law · unit table w/ classes+gates · engine staleness · prose — full text when ≤2 units are named, else opens/closes skeleton), fenced as DATA; parse → validate → **one bounded retry** carrying the validator's own words; persistence to `_studio/chat/messages.jsonl` + `chat/calls/`; injectable client for deterministic testing |
| Multi-op proposals | `studio/ops.py` (refactor) | proposals now carry `ops[]` (spec Appendix B shape) with single-op mirrors for S2 cards; `validate_item` runs at PROPOSAL time so an illegal op never becomes a card; `_apply` executes **in order, stop-on-first-failure**, completed ops stand |
| Writer choice at approval | `ops.approve(slug, pid, backend=)` + card select | the compiler proposes; the **human picks which model writes** (mock/anthropic/openai) when approving |
| Chat UI | `app.js`, `app.css` | `#/b/<slug>/chat`: transcript, inline proposal cards with per-op results, refusal banners, retry notice, Ctrl+Enter send, graceful no-key message |
| Spend meter | `projection.spend` | rolls up BOTH lanes (engine prose + chat compiles), exact tokens when E-4 data is present, `~` estimate otherwise |

### S4 — the full book surface (stranger-sim gate PASSED)

| Piece | File(s) | Notes |
|---|---|---|
| Cover studio | `projection.cover()`, ops, `viewCover` | binds the engine's OWN `_may_reuse_art` predicate (imported, never re-implemented) for the reuse verdict + reason; provenance sidecar, superseded takes, composited ebook cover, cover events; **PENDING adjudication card**; re-roll / recomposite / print-wrap ops |
| Verify matrix | `studio/verify_runner.py`, `projection.verify_matrix()`, `viewFormats` | runs `verify_build.py` per configured format **as a job** (print formats drive Word COM → must share the one lane); results cached to `_studio/verify/*.json`; checks × formats grid with a detail drawer, plus `--final` sweep |
| Intake + gist | `projection.intake()`, `PUT /brief`, upload/delete routes, `viewIntake` | drag-in source docs (200 MB cap, sanitized basenames, path-jailed), the gist editor writing `brief.md`, and the ingest stage's relational digests rendered |
| New-book wizard | `POST /api/books`, `viewNewBook` | clones the SHIPPED reference book's config as the defaults skeleton (schema-valid by construction), overwrites identity, clears units, and **drops the reference's ceremonial content plus its front-matter pages and each paired blank verso** so recto parity survives |
| Settings | `GET/PUT /api/settings`, `/settings/key`, `/settings/test-model`, `viewSettings` | kit_env model/vision/cover_gen form; **keys are env-only** — presence booleans out, never a value; a "set for this session" path that prints the `setx` hint instead of writing a key to disk; live model ping |
| Bridge fulfillment | `ops.fulfill_bridge`, bridge card | a pending harness turn can be answered from the browser by **pasting prose** or letting the **API model** answer the engine's own request; the engine still gates it (nonce + gate_draft + 3-attempt budget) |
| Studio selfcheck | `studio/selfcheck.py` | `node --check` on app.js + `ast.parse` on every studio module + catalog/risk-class invariants. Added because a single missing `)` rendered a permanently "Loading…" page with no visible console error |

### Post-S4 — boot-into-the-Studio (2026-08-05; scoped by Bo: the harness stays the
launcher, the Studio must POP UP or be OFFERED from the very start)

| Piece | File(s) | Notes |
|---|---|---|
| SessionStart hook surfaces the Studio | `_tools/on_session_start.py` | on an ORDINARY start (never compact/resume recovery) on a configured machine: probe ports 8756–8776 for a live Studio (token-verified `/api/health`; fallback: the guard-403 body names studio.cmd) → **already running** = print the tokenized URL for the model to relay; **not running + `kit_env.studio.autolaunch`** = spawn `studio/server.py` fully detached (DETACHED_PROCESS + new process group + `close_fds` + DEVNULL stdin + `PYTHONUNBUFFERED` — the 70a8dc8 lesson; stdout→`_studio/autolaunch.log`; the server opens the browser itself) ; **deps missing / autolaunch off** = one-line offer. Never crashes; never blocks boot; recovery output stays pure |
| `kit_env.studio` block | `_tools/kit_env.json`, `_tools/kit_env.template.json` | `{autolaunch: true, port: 8756}` in BOTH (selfcheck key-parity green); flows to fresh machines via `autoconfig.py` (which builds from the template) |
| Zero-config launcher | `studio.cmd` | if `_tools/kit_env.json` is absent, runs `autoconfig.py` first — a fresh copy double-clicks straight into a configured Studio |
| Boot-contract surfacing | `CLAUDE.md` §1 step 6 + §10 status format (`studio:` line), `START_HERE.md` §0 | the session relays the hook's `STUDIO:` block (or offers `studio.cmd` in one line) in every boot status report |
| First-run onboarding | `_tools/on_session_start.py` `_print_first_run()` | the fresh-copy block now names the Studio path (`pip install -r requirements-studio.txt` → `studio.cmd`) |

**Gate evidence (live, 2026-08-05):** `selfcheck.py` **PASS (0 fail, 0 warn)** incl. kit_env↔template
key parity with the new block · hook startup test: printed the launching block, spawned detached,
`/api/health` **200** with the per-launch token, browser opened itself · second startup: **already
running** path relayed the tokenized URL · `source=compact` test: recovery block rendered with **zero
STUDIO noise** · kill-and-relaunch: the server's `open: http://127.0.0.1:8756/?t=…` line lands in
`_studio/autolaunch.log` (unbuffered child) and health returns 200.

### S6 — the Conductor: the plain-language face (gate PASSED, 2026-08-05)

**The thesis, executed:** the engine owns all truth and every mutation is one typed op behind an
approval, so a newcomer face is a *projection + vocabulary* problem. S6 adds a second face over the
SAME API and the SAME ops — no new write path, no new authority, the operator dashboard untouched at
`/pro.html`.

| Piece | File(s) | Notes |
|---|---|---|
| The Conductor SPA | `studio/web/conductor.js` (~880 lines), `studio/web/conductor.css` (~470) | zero-dep/zero-build/zero-CDN like the operator face. Views: bookshelf (cover-forward tiles, placeholder jackets, `_`-prefixed fixtures hidden, `testvoyage` badged "Example") · book hub (hero + ONE status line + ONE primary CTA computed from `plan`+hardstop+bridge+jobs; progress theater; plain attention cards; chapters; files grouped Ebook/Share/Print; chat) · reader (serif prose + TOC + per-chapter "Make this chapter better") · interview wizard (about/audience/length/material/formats → `POST /books` + uploads + run) · 3-pane welcome tour (localStorage) · celebration reveal on live completion |
| The vocabulary layer | `conductor.js` `STR` + `stagePhrase`/`FMT`/`WRITERS` | every display string centralized (i18n-ready); engine keys → human phrases ("Writing \"Chapter 2\"", "Checking every page"); formats → plain labels; writers → plain names ("My Claude Code session (no key needed)"). Voice law applied to the UI itself: no em/en dashes in display strings |
| Plain approval cards | `planCard()` | CONTENT ops render as "The plan" with ops described in plain words, the note quoted, "Afterwards your book files refresh and get re-checked automatically.", writer picker, Go ahead / Not now. Same proposals API, same approval chokepoint |
| Progress theater | `theater()` | binds the SSE `job` log stream's engine event lines (`stage.done`, drafts, …) to a staged plain narrative + progress bar + step list; raw detail one toggle away ("Show the fine print") |
| Entry swap | `index.html` (Conductor), `pro.html` (operator dashboard), `app.js` chrome | `/` is now the plain face; "Advanced view" ↔ "Simple view" cross-links carry the hash (deep links transfer) |
| Design system | `conductor.css` | paper-first light + ink dark (`data-theme`, persisted, prefers-color-scheme initial), Georgia display/prose + system UI chrome, cover-jacket tiles with spine sheen, responsive to phone, `prefers-reduced-motion`, focus-visible |
| Backend (additive only) | `projection.list_books` (+`cover_rel`,`subtitle`), `server.create_book` fallback → vendored `studio/reference_config.json` | the new-book path no longer 500s on a copy without `testvoyage` (portability fix); shelf covers ride the existing jailed `/file` route |
| Mechanical vocabulary gate | `studio/selfcheck.py` | **the S6 invariant, enforced**: `node --check` on BOTH faces + a scan of `conductor.js` string literals that look like display text (contain a space) for engine jargon (stale/reconverge/hardstop/blast radius/nonce/proposal/backend/stage/gate/…); `jargon-ok` line marker exempts API-value literals. Plus: both HTML entries present, `reference_config.json` vendored |

**Gate evidence (browser-driven live, 2026-08-05):**
- `studio/selfcheck.py` **PASS** (17 checks incl. the new vocabulary gate, first try) · kit
  `selfcheck.py` PASS (0 fail, 0 warn).
- **Shelf:** renders 25+ visible books; fixtures (`_studio_smoke`, `_studio_chat`, `_enginetest`)
  hidden; `testvoyage` last with the Example badge; welcome tour walked 3 panes and dismissed.
- **Hub truth-catch:** `testvoyage` rendered "You changed something. The book can bring itself up to
  date." — the engine's real staleness state, translated; its unadjudicated cover correctly surfaced
  the "Take a look at your cover" card.
- **Reader:** full serif prose render + TOC + improve box.
- **The write path, round-tripped in plain language** (on the `stranger_sim` fixture): a note typed
  into "Make this chapter better" → **"The plan"** card ("Rewrite \"Chapter One\"" + the note quoted
  + the refresh line + writer picker) → writer set to "Placeholder text (just testing)" → **Go
  ahead** → engine job ran → hub settled to **"Your book is ready."** — and the disk agrees:
  `revision_notes/ch_01.md` carries the note + proposal id, the prior take archived append-only,
  `ops.jsonl` + `CHANGELOG.md` cross-referenced (`revise_unit ch_01 archived=v1 note=113ch
  proposal=p_20260805_100836_01 job=j_20260805_100903_001`). The mock writer reproduced identical
  bytes, so the content-hash system correctly charged zero downstream rebuilds (the S2 determinism
  truth-catch, resurfacing through the plain face).
- **Zero jargon on any driven screen** (tree + page-text sweeps), now held by the mechanical gate.
- **Operator face intact:** `/pro.html` renders the full Library (all 34 workspaces incl. fixtures),
  tagged "S6 · advanced face", with the Simple-view cross-link.
- *Not yet visually QA'd on a composited display* (the automation pane rendered no frames this
  session); structure, behavior, and vocabulary are verified — aesthetic polish review is the first
  minute of the next human look.

### S7–S10 — setup, spend floors, 中文, and the loops (gates PASSED, 2026-08-05, same session as S6)

| Piece | File(s) | Notes |
|---|---|---|
| **S7 · Setup** (`#/setup`) | `conductor.js viewSetup` | who-writes cards (plain names over the model seam), key presence + set-for-session + live **Try it** ping with latency, machine capability in plain words (doctor fetched NON-blocking after a 30 s cold-run wart was found and fixed), and the spending guard UI. Linked from the footer everywhere |
| **S8 · The spend floor — E-6** | `_tools/model_client.py` | **floors in code, kit-wide**: `BOOKSMITH_TOKEN_BUDGET` (set from `kit_env.studio.token_budget` by the server at launch + on every settings save) makes a METERED call (anthropic/openai) refuse to start once the ledger meets the cap — a `ModelError` with the remedy in plain text, so the engine hard-stops resumably. mock/harness never blocked; env unset = byte-identical behavior. **Bonus find:** call-ledger numbering restarted per process and silently OVERWROTE `call_0001.json` onward on resume — fixed to continue after the ledger's max (append-only), which also makes both the spend meter and the cap accurate across restarts |
| **S8 · Cost legibility** | `conductor.js spendLine`, settings `studio.price_*_per_mtok` | the hub speaks it plainly: *"Machine work so far: 8 calls, about 14 thousand words. Your guard stops paid writing at about 75 thousand words."* Dollars appear only when the operator sets real prices AND usage is exact — no fake precision |
| **S9 · 中文** | `studio/web/i18n.js` (+ index.html script tag) | a full natural-Chinese overlay of every STR entry (including the function-valued templates); the merge happens before any derived table builds, so stage phrases, formats, writers, and groups all follow; footer toggle EN ↔ 中文; `node --check`'d by selfcheck |
| **S10 · Cover chooser** | `ops.py _exec_restore_cover_take` (+ registry + validation), `conductor.js coverGallery` | a NEW CONTENT op, append-only in both directions (the engine's own preserve-aside idiom), **sha-honest provenance**: the restored art gets a fresh sidecar bound to its bytes, carrying the original method when a sha-matching sidecar is found (proven live: `method:"sdxl"` carried through) + `restored_from` lineage. The hub gallery shows every take; "Use this one" → plan card → approve → recomposite offered |
| **S10 · Three takes** | server `book_ops` (multi-op plans via the same channel chat uses), `projection.unit_version_text` + `GET /units/{uid}/version`, `conductor.js` takes UI | "One take / Three takes" on the reader's improve box → ONE proposal holding 3 varied `revise_unit` ops → sequential apply (`ok, ok, ok` live; v2→v4 archived) → **Compare recent takes** renders competing takes side by side → "Keep this one" = the existing `revert_unit` op |
| **S10 · Book passport** | `projection.passport_html`, `GET /api/books/{slug}/passport` | a self-contained shareable HTML receipts page (cover inlined base64, contents, checks, machine-work ledger); pure projection, writes nothing; 846 KB with cover, rendered live |
| **S10 · Taste seed** | `ops.py _taste` | every explicit human pick (cover kept, take kept, cover verdict PASS) appends to `_studio/taste.jsonl` — the ROADMAP H2.4 taste model's first data, gathered for free |

**Gate evidence (live, 2026-08-05):** budget-floor micro-suite **7/7** (mock unblocked under an
exceeded cap · metered refusal fires · unset env = no check · under-cap passes · chars/4 fallback
counts · append-only numbering holds) · **engine smoketest PASS (A–L) after BOTH model_client
changes** · `restore_cover_take` round-trip on `stranger_sim`: CONTENT proposal → approved → prior
art + sidecar preserved aside, fresh sha-bound sidecar with `method:"sdxl"` + lineage, taste line
written · three-takes plan: `applied — ok, ok, ok`, drafts v2→v4 archived, version endpoint serves
every take · passport 200 with inlined cover · setup page + guard round-trip driven in the browser
(guard set → hub shows it → cleared) · full 中文 shelf render verified in the browser, EN ↔ 中文
toggle both directions · kit selfcheck **PASS (0 fail, 0 warn)** incl. template parity with the new
`studio` keys · studio selfcheck **PASS** (3 JS files + vocabulary gate).

## §2 · Gate evidence (verified live, 2026-08-04)

- **Engine regression:** full `engine_smoketest.py` **PASS (A–L, all 12 scenarios)** with E-1+E-3
  applied; `--selftest-cover-reuse` 10/10.
- **Drive:** browser-API dry-run of the `_studio_smoke` fixture (testvoyage-derived, mock backend,
  `--to assemble`) → job `complete exit=0`.
- **Kill-at-any-instant:** (mock runs proved *too fast to cancel* — 17 stages < 2 s — so the kill
  proof was made deterministic): a 60 s sleeper child tree-killed → `cancelled`; an engine run
  killed at 0.6 s → `cancelled`, `state.json` **valid JSON with 17 stage records** (atomic writes
  held), resume → `rc=0, skip_done=16, stage.done=1` — the kill landed mid-`assemble` and the next
  run re-executed EXACTLY the one interrupted stage. Hash-proof resume, demonstrated.
- **Idempotence:** re-running a finished fixture → 17× `stage.skip_done`, zero rewrites.
- **Browser-driven (the letter of the gate):** in the Studio UI, set `run to: assemble`, clicked
  🧪 Dry-run → live console streamed the engine's event lines in real time via SSE
  (run.start → drafts → integrate → assemble → run.complete), the stage rail flipped 6 done /
  4 pending, unit gates showed `pass` at 258/250 words, spend chip ticked to 3 calls.
- **Bonus truth-catch:** `authorial_act verdict=FAIL(86h/86f)` on mock filler — the
  single-authorial-act critic (advisory) correctly refuses to call looped sentences one author's
  book, and the Studio surfaces the verdict verbatim.
- **Bug found & fixed live:** the token middleware's `or`-chain let a **stale cookie shadow a
  fresh `?t=`** (an old-launch cookie 403'd a valid URL). Fixed: accept ANY matching credential.

### S2 evidence (all on `_studio_smoke`; testvoyage is git-tracked, so the engine-lane fixture is
the mutation target — same rationale as S1)

- **Engine regression:** full smoketest **PASS (A–L)** with E-1+E-2+E-3 applied.
- **E-2 hash isolation, surgical:** adding a note to ch_02 flipped **exactly**
  `draft:ch_02: True→False` in `--explain`; nothing else moved. Removing it restores the original
  hash (the conditional fold).
- **Browser-driven revise (the gate):** in the unit view, wrote a direction, picked backend mock,
  clicked *Propose revision* → card showed the eventual cascade → *Approve & run* → the job
  re-drafted ch_02 **without `--force-stage`** (log: `stage.done: draft:ch_02`, not skip) — the
  note hash alone re-opened it; `e2_warning: none`. `v1` archived; CHANGELOG + ops.jsonl lines
  written with proposal↔job cross-refs.
- **Determinism truth-catch:** the mock reproduced byte-identical prose → `observed_newly_stale=[]`
  — the engine correctly declared nothing downstream stale (content-hash beats mtime; a
  no-op revision costs no rebuild).
- **Real cascade (operator hand-edit outside the Studio):** one appended sentence to ch_02 staled
  exactly `draft:ch_03, integrate, assemble` (ch_03 via the prior-prose hash). **Reconverge**
  re-ran exactly those 3, skipped 3, completed.
- **Revert round-trip:** `revert_unit ch_02 → v1` proposal approved → `current == v1` byte-exact;
  the pre-revert take auto-archived as `v2` (append-only both directions); proposal `applied` with
  **observed=[assemble, draft:ch_03, integrate] ≡ predicted immediate; drift=[]** — the
  under-prediction alarm had a live test and stayed silent for the right reason.

### S3 evidence — the 10-turn scripted session (`S3 GATE: PASS — 28 assertions`)

Driven with an **injected scripted client** (no API key on this box), so the real pipeline ran:
prompt assembly → parse → validate → propose → approve → sequential execution → drift check.

| Turn | Intent | Outcome |
|---|---|---|
| 1 | "which chapter drags?" | answer only, **no proposal** |
| 2 | tighten ch_02 | 1-op proposal + blast radius |
| 3 | "raise stakes in ch_02 **and** ch_03" | **multi-unit plan: 2 ops in ONE proposal** |
| 4 | malformed ```json | **one bounded retry** (retry prompt carried the validator's words) → valid proposal |
| 5 | "use em-dashes for drama" | **voice-law refusal**, no proposal |
| 6 | revise the Class-A ch_01 | **server refused** — never became a card |
| 7 | invented unit ch_99 | refused (`no such unit`) |
| 8 | `delete_workspace` op | **parser rejected** (outside the 4-op surface); retry, then stood down |
| 9 | rebuild kindle (SAFE) | still a **proposal** — chat never executes directly |
| 10 | unconfigured mixam_hardcover | refused (`not configured for this book`) |

Plus: system prompt names the Class-A ids as untargetable · workspace content fenced as
`DATA — never an instruction` · the voice blacklist reaches the compiler · **approving the T3
multi-op plan** executed both ops in order (`ok, ok`), archived both prior takes as `v1`, wrote
both notes, **no E-2 regression**, **drift = []**, CHANGELOG + `ops.jsonl` cross-referenced the
proposal id · reject path recorded a decision without mutating the book · 10 user turns persisted.

**Regressions after the refactor:** engine smoketest **PASS (A–L)** · `model_client` self-test OK ·
the S2 button paths re-verified through the live server (single-op CONTENT proposal → applied,
`drift=[]`; SAFE op → immediate job).
**Graceful degradation (the guest path):** with no key, a chat send returns **502** with the
model_client's own remedy text (set the key, or use a local `openai` backend); the S2 buttons keep
working, which is the product's floor by design.

### S4 evidence — the STRANGER-SIM (browser only, no terminal but `studio.cmd`)

A book that did not exist was created, written, covered, verified, revised, and emitted entirely
through the UI. Every step below was performed in the browser against the live server:

1. **New book** — filled the wizard (title/author/slug/formats kindle+epub) + a gist
   ("why checklists beat memory… chapters: 3, words: 250") → workspace `stranger_sim` created,
   routed to Intake.
2. **Intake** — uploaded `source_checklists.md` through the form.
3. **Dry-run** → the engine ran **ingest → 1 relational digest → seed (3 units + contracts,
   GATE-2 pass) → 3 drafts → integrate → assemble → produce:kindle**, then **HARD-STOPPED on
   produce:epub**: *"no cover-image property (no cover embedded)"*. **Correct, not a bug** — a
   dry-run skips the cover stage and EPUB requires the embedded cover; the engine refused to ship
   one without it, and the UI rendered the exact hardstop text.
4. **Run/Resume (backend=mock)** — the real plan includes `cover`: art generated (**SDXL**,
   sha-bound provenance), ebook cover composited, `produce:epub` then completed. Vision returned
   **PENDING** (no local vision backend) and the engine logged `cover.vision_unadjudicated`
   rather than passing a non-verdict.
5. **Cover studio** — the PENDING card appeared. The cover was **actually inspected** (title
   legible with halo stroke, author at the foot, no other baked-in text, typography clear of the
   art) and adjudicated **PASS** in the browser →
   `outputs/kindle/*_KINDLE_cover.verdict.json` with `adjudicator:"human"` and the
   **image sha256 bound to the verdict**; CHANGELOG line written.
6. **Formats/QA** — ⟳ Verify all → job ran `verify_build.py` per format → matrix **GREEN**
   (kindle 7/7 checks, epub 6/6).
7. **Revise** — proposed a revision on ch_02 from the unit page, approved with **writer=mock** →
   applied, `v1` archived, `e2_warning` none, `drift=[]`.
8. **Reconverge** — nothing re-ran (mock is deterministic, so no bytes changed): the same
   content-hash truth S2 found. Final plan: **all 11 stages satisfied**; `MANIFEST.json` emitted;
   deliverables = EPUB (623 KB), Kindle DOCX, cover JPG + verdict, version-pinned master.

**Bugs found and fixed during the sim** (all real, all from actually driving it):
1. a missing `)` in the formats-matrix cell → a page stuck at "Loading…" (→ `studio/selfcheck.py`);
2. the browser served a **cached broken app.js** across a restart (→ `Cache-Control: no-store` for
   the whole surface: a localhost tool is edited while it runs);
3. the new-book wizard blanked `epigraph` to `""` — but it is an **object** in the schema
   (dedication is a string) → now the ceremonial keys and their front-matter pages are dropped
   properly, blanks included.

## §3 · How to run

```
studio.cmd            (or: python studio\server.py [--port 8756] [--no-open])
```
It prints `http://127.0.0.1:8756/?t=<token>` and opens the browser. Tokens are per-launch.

## §4 · Deviations from the spec (recorded, not hidden)

1. **Micro-renderer instead of vendored Preact/HTM** (S0 note, still open) — decision point at S2.
2. **Doctor field mapping tolerant, unverified** against `doctor.py --json` exact names.
3. **No separate `engine` SSE channel:** the engine prints every `log.jsonl` event to stdout, so
   the `job` log stream already carries the engine events; a structured channel can be added when
   a UI consumer actually needs parsed events (spec §3.3 listed it — deferred with cause).
4. **`_studio_smoke` fixture workspace** exists under `book_workspace/` for gates (rebuildable via
   the session scratch script; safe to delete anytime).

4. **`adjudicate_cover` is SAFE, not CONTENT** (SPEC §8.2 lists it CONTENT). A verdict changes no
   artifact, and the human's click IS the decision — wrapping it in an approval card double-gated
   one human act (observed live: clicking Pass produced a card asking to approve the Pass). It is
   still ledgered like every op. Amend the spec, or overturn this with one line in `ops.OPS`.
5. **`studio/` must be committed to ship in a giftable.** `make_giftable.py` uses `git ls-files`
   as an allowlist, so untracked files never leave the box — correct behavior, but it means the
   Studio only reaches strangers after `git add studio/ studio.cmd requirements-studio.txt docs/STUDIO_*.md`.
   `_studio/` runtime state stays excluded via .gitignore.

## §5 · Next (S5, per SPEC §11)

**The reusability falsifier.** Add `domains/course/studio.json` (panel toggles: formats matrix and
cover studio OFF; artifact labels; the generic op subset) and render the shipped `course` domain
end to end. **Gate: ZERO Shell code changes.** If the Shell has to fork, the Shell/Binding seam is
misdrawn and must be redrawn before any third face (FERRYMAN, Appendix D). Also open: a rolling
chat summary at 20 turns (SPEC §9.7), and the `_studio_smoke` / `_studio_chat` / `stranger_sim`
fixture workspaces are disposable — delete any time.

## §6 · Superseded next-step notes

Full book surface: **cover studio** (art + provenance/reuse verdicts, the PENDING vision
adjudication card, re-roll, print-wrap compose), **formats matrix** (`verify_build` JSON as a
checks grid with drill-down), **intake + new-book wizard** (`brief.md` editor, uploads, `POST
/books`), **settings write-path** (kit_env form + doctor + env-only key handling), **bridge
fulfillment ops**, and giftable inclusion. S4 gate: a stranger-sim — fresh machine profile,
browser-only, mock backend, intake → run → revise → outputs without touching a terminal beyond
`studio.cmd`.

Deferred/known: rolling chat summary at 20 turns (spec §9.7) is not implemented — the transcript
is capped at the last 12 turns in context, which is sufficient until sessions run long.
