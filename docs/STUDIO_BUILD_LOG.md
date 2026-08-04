# STUDIO_BUILD_LOG.md — build-state record for BOOKSMITH Studio

*Companion to `docs/STUDIO_SPEC.md` (the design authority). This file records what is BUILT and
VERIFIED, in the house BUILD_STATE idiom: where this log contradicts the spec, reality wins and the
spec gets amended, not the other way around.*

**Updated:** 2026-08-04 · **Phase:** **S4 COMPLETE — stranger-sim gate PASSED** (S0–S4 all passed
same day) · S5 (second binding: `domains/course/studio.json`, the reusability falsifier) not started.

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
