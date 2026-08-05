# SITREP 2026-08-04 — BOOKSMITH Studio (S0→S4), and what the session actually taught

**Session:** Claude Code desktop, `C:\MoneyPrinterTurbo-main` → `C:\FERRYMAN` → `C:\BOOKSMITH`
(models: Opus 5 / Fable 5 / Opus 5 across the arc).
**Shipped:** BOOKSMITH Studio phases S0–S4, four additive engine patches, pushed public as
`e3ba044`.
**Status:** S0–S4 gates PASSED with evidence. S5 (the reusability falsifier) not started.

**Read order for a cold session:** this file (the *why* and the durable lessons) →
`docs/STUDIO_BUILD_LOG.md` (what is built + gate evidence; reality wins over spec) →
`docs/STUDIO_SPEC.md` (the design authority) → `studio/` code.

**Conflict rule, inherited from the house style:** where this file and the spec disagree, this file
records what *happened* and the spec records what was *intended*. Amend the spec; do not quietly
rewrite history.

---

## §1 · The arc of the session (how we got here)

The path was not planned. It is worth recording because the detour produced the framing.

1. **`C:\MoneyPrinterTurbo-main` — "figure it out for me."** A freshly downloaded GitHub repo.
   Environment was already ideal (Python 3.11, uv, ffmpeg, git all present); `uv sync --frozen`
   installed 120 packages; created `config.toml`; smoke-tested imports; launched the Streamlit WebUI
   and verified HTTP 200. ~4 minutes of real work.
2. **"How does this print money?"** An honest answer: it does not. MPT is a *faceless-video
   factory* — it removes production cost, not distribution risk, and YouTube's 2025 rules against
   "mass-produced, repetitious, inauthentic" content make the naive use of it the *highest*-risk
   use. The tool is a means of production; the business model is a separate problem.
3. **"Compare it to my FERRYMAN."** Read `SPEC.md`, `CONTINUATION.md`, `BUILD_STATE.md`, the
   graphics head. FERRYMAN turns out to be the same axis' opposite end (§2).
4. **The realization that reframed everything:** *"what FERRYMAN was missing was this localhost web
   GUI"* — followed immediately by *"scope it for BOOKSMITH instead"*, then, mid-turn,
   *"one-shot is aspiration; in reality there needs to be a chat window for revision."*
5. **Spec** (`docs/STUDIO_SPEC.md`, ~830 lines) written against code read end-to-end, not against
   assumptions.
6. **Build S0→S4**, each phase gated on evidence, each closing with a browser-verified artifact.
7. **Commit + push** to a PUBLIC repo after scanning all 41 unpushed commits for personal data.

**The lesson in the shape of the path:** the GUI insight arrived while comparing two *other*
projects. Cross-project comparison is not a detour from building; it is where the load-bearing
architectural insight came from.

---

## §2 · Three projects, one axis

### 2.1 The axis

MoneyPrinterTurbo and FERRYMAN sit at opposite ends of a single spectrum, and naming it explains
both:

> **How much of the artifact is *yours*?**

- **MPT:** nothing is yours. Stock footage, generic TTS, LLM script, auto-posted. Optimizes ease
  and reach. This is the slop-risk end — the exact thing platform filters now target.
- **FERRYMAN:** everything is yours. A real person's cloned voice, their real face lip-synced onto
  their real footage, oracle-gated, hash-chain-ledgered, published only by a human act. Optimizes
  identity, trust, provenance.
- **BOOKSMITH:** the same end of the axis as FERRYMAN, in prose. One authorial act, append-only
  canon, gate after every stage.

### 2.2 The comparison table (recorded so it does not have to be re-derived)

| Axis | MoneyPrinterTurbo | FERRYMAN |
|---|---|---|
| Output | faceless vertical shorts | long-form talking-head episodes |
| Locality | cloud (LLM + TTS + stock APIs) | fully local, sovereign, offline |
| The visual | downloaded Pexels/Pixabay/Coverr clips | lip-synced real host (MuseTalk/LatentSync on a real idle loop) |
| Voice | generic Edge/Azure/ElevenLabs | cloned, local, unlimited length |
| QA | none — can silently garble | oracles: CER back-transcribe, A/V delta, codec, SyncNet |
| Provenance | none | hash-chained `ledger/runs.jsonl` + per-job manifest + AIGC label |
| Publishing | automatic cross-post | deliberately manual |
| Maturity | shipping product | P0–P6 done, P7 graphics live |

### 2.3 The only three things MPT has that FERRYMAN does not

Worth keeping because they are the *entire* legitimate borrow list:

1. **`app/services/material.py`** — keyword → stock-footage search + download (Pexels/Pixabay/Coverr,
   optional TwelveLabs semantic rerank). This is the one genuine capability gap: FERRYMAN's
   *fullscreen cutaway* cue is the perfect slot for real b-roll, but HyperFrames only authors HTML
   cards today.
2. **`app/services/upload_post.py`** — TikTok/IG/YouTube Shorts distribution. Against FERRYMAN's
   doctrine as an *auto* step; fine as a *human-triggered* publish of an approved episode.
3. **The Streamlit + FastAPI split** — a working reference for a P8 console. (Read it; do not adopt
   Streamlit. See §3.6.)

**Verdict recorded:** bolt-on one-way, never merge. Pulling FERRYMAN's concerns into MPT would just
be rebuilding FERRYMAN.

### 2.4 The recurring shape (this is the real nugget)

FERRYMAN, BOOKSMITH, and — from the outside — FIGUREHEAD all share one DNA:

```
a deterministic engine that holds the plan + the gates + the state ON DISK
    + a model called as a pure function
    + a gate after every stage
    + an append-only ledger for provenance
```

**Consequence:** for any system with this DNA, *a GUI is a projection problem, not an architecture
problem.* The engine already knows everything a UI needs to show; it just has no face. That single
observation is what turned "build a GUI" from a rewrite into a two-primitive server.

**Corollary worth testing (S5):** if the shape is real, one Shell should front all of them, with
per-domain Bindings as data. If the Shell has to fork for the second domain, the seam is misdrawn.

---

## §3 · The Studio: the load-bearing decisions

### 3.1 Two primitives, one write path

```
SPAWN   — run engine.py / _tools/* as subprocesses (jobs)
PROJECT — read + watch what the engine writes
```
The server holds **no book state**. Every mutation — button *or* chat — is a typed **Operation**
from a closed catalog, executed under the engine's existing gates, appended to the existing
ledgers. If the server dies mid-anything, the workspace is exactly as consistent as the engine left
it, because only the engine was ever writing.

**Why this matters more than it sounds:** it makes the Studio *unable* to introduce a new class of
bug. Every historical failure this kit exists to prevent was "unverified state advanced anyway." A
face that cannot write cannot advance unverified state.

### 3.2 The chat is a compiler, not an editor

The single most important design decision in S3.

- The model's whole output is (a) prose for the human and (b) at most one **Proposal**.
- The server validates the proposal against the book's own facts, then a **human approves**.
- The op schema contains no file-write, no shell, no network, nothing destructive.

> The model can **propose** anything and **execute** nothing.

A free-form chatbot editor would have silently deleted every discipline in `KIT_ARCHITECTURE.md`.
A compiler with an op whitelist deletes none of them. The gate proved this concretely: the model was
told to *"delete this book and start over"*, emitted a `delete_workspace` op — and the parser simply
had no such verb.

### 3.3 The staleness DAG already existed — so revision cascade is FREE

The discovery that made S2 cheap. `Engine.input_sha()` / `draft_inputs_sha()` already key every
stage to its true inputs:

```
draft:<uid>   ← sha(contract, prior-unit current.md, seed.md, unit-dict, voice-block [, revision notes])
integrate     ← sha(config, all manuscript/current/*)
assemble      ← sha(config, all manuscript/current/*)
produce:<fmt> ← sha(latest outputs/markdown/<slug>_v*.md)
cover         ← sha(config) + the earned-reuse predicate
verify, emit  ← sha(config + every expected artifact's bytes)
ingest        ← sha(intake file list+sizes, excluding intake/converted/)
seed          ← sha(brief.md, digests, core config fields)
```

**So the Studio never implements invalidation. It displays it.** Append a revision note → the draft
hash changes → the engine re-runs exactly the stale suffix. Nothing else.

The proof was surgical: adding one note file flipped **exactly** `draft:ch_02 True→False` in
`--explain`, and nothing else moved.

### 3.4 The harness bridge is fulfiller-agnostic

`_draft_via_harness` writes `bridge/<uid>.request.json` + a nonce (= `draft_inputs_sha`) and exits
**3**. Nothing in that protocol says *who* writes the response. Therefore the browser can render a
pending turn and let (a) the Claude Code harness, (b) a human pasting prose, or (c) the API model
fulfill it — and the engine gates the result identically in all three cases.

Harness-backend books became fully monitorable *and drivable* from the browser for free.

### 3.5 Risk classes, and where the line actually falls

- **SAFE** — regenerate-only; executes immediately, still ledgered.
- **CONTENT** — changes what the book *says or shows*, or supplies prose → always an approval card.
- **DESTRUCTIVE** — typed confirmation; **absent from the chat schema entirely**.

The line got tested in practice: `adjudicate_cover` was specced CONTENT, but clicking "Pass"
produced a card asking me to approve the Pass. A verdict changes no artifact and *the click is the
decision*. Reclassified SAFE (§9).

### 3.6 Streamlit evaluated and rejected — with evidence from this very session

The fast path would have been Streamlit (a day's work, and MPT's WebUI is the proof it renders
nicely). Rejected because its whole-page rerun model fights exactly the states this product is made
of: long jobs with streamed logs, approval cards that must survive reruns, and a chat panel needing
server push.

**The evidence was in the room:** MPT's own `app/config/config.py` carries a bespoke re-entrant
`_SynchronizedConfig` dict + `runtime_config_lock` whose docstrings say, in Chinese, that Streamlit
rewrites every widget value back into config on every rerun and that this must not deadlock a
running video task. That is a lot of machinery to buy back what a plain REST+SSE server never
loses. Cost of the alternative: ~40 lines of `h()` DOM helper and no ceiling.

---

## §4 · Engine ground truth (the reference table — pinned, do not re-derive)

Everything the Studio binds to, verified by reading `_tools/engine.py` (1,606 lines pre-patch) and
`_tools/model_client.py` end to end.

| Fact | Detail |
|---|---|
| Exit codes | `0` complete · `1` config not found · `2` HARD-STOP · `3` AWAIT_MODEL (bridge turn) |
| `--status` | prints `_engine/state.json` as JSON — already machine-readable |
| `_engine/log.jsonl` | **already a structured event stream**: `{ts, event, ...kw}` per line. Events seen: `run.start`, `run.complete`, `stage.skip_done`, `stage.done`, `HARDSTOP`, `AWAIT_MODEL`, `harness.turn_needed`, `harness.stale_response_discarded`, `draft.gate_fail`, `draft.skip_classA`, `precheck.slug_mismatch`, `authorial_act`, `cover`, `cover.reroll`, `cover.art_superseded`, `cover.vision_unadjudicated`, `seed.unparseable_plan` |
| State writes | atomic (`tmp` + `os.replace`) → a kill at any instant leaves valid JSON |
| `satisfied()` | state hash match **AND** `expected_outputs()` still exist on disk → deleting an artifact forces a re-run |
| Stage plan | `precheck → draft:<uid>* → integrate → assemble → produce:<non-cover-fmt>* → cover → produce:<epub|digital_pdf> → verify → emit`, with `[ingest] [seed]` as the architect front-half |
| Cover reuse | **earned**, not assumed (`_may_reuse_art`): `bespoke/supplied/catalog` permanently trusted; generative needs a provenance sidecar whose `art_sha256` matches the bytes. Unreusable art is *preserved aside*, never overwritten |
| Vision verdicts | `PASS|FAIL|PENDING|SKIP`; only FAIL triggers the bounded re-roll; PENDING is logged as `cover.vision_unadjudicated` — never silently passed |
| Model seam | `complete(system, prompt) -> str`, stdlib urllib only, 4 retries on transport errors, every call logged |
| Domain generality | `domain != "book"` loads `domains/<d>/domain.json`; stage machinery, gates, hashes, and bridge are all domain-invariant |

---

## §5 · The four engine patches (~155 additive lines, no default behavior changed)

**E-1 `--explain`** — the read-only staleness oracle: ordered plan + `input_sha` + `satisfied` +
`expected_outputs` + state rec, as JSON. *The Studio never re-implements hash logic; it asks the
engine.* Independently useful at the CLI.

**E-2 revision notes** — `revision_notes/<uid>.md` rides `build_draft_prompt` **and** folds into
`draft_inputs_sha`. The subtlety that makes it safe:

```python
notes_p = self.ws / "revision_notes" / f"{uid}.md"
if notes_p.exists():                 # ← conditional: pre-E-2 books keep IDENTICAL hashes
    parts.append(sha_file(notes_p))
```

Without the `if`, every one of the 31 existing workspaces would have gone retroactively stale on
first `--explain`. **Lesson: when adding an input to a hash, join it conditionally or you rewrite
the past.**

**E-3 `--only KEY [--force-stage]`** — one stage through the standard `_run_one` mark/gate/hardstop
machinery; refuses Class-A drafts (mirroring `stage_draft`); unknown key → rc 1.

**E-4 usage capture** — real token counts from the Anthropic `usage` / OpenAI `usage` blocks into
each call log; the spend meter reports `exact` when every call is measured, `~` otherwise.

---

## §6 · Bugs found, and what each one teaches

Every one of these was found by *driving the thing*, not by reading it.

### 6.1 The stale cookie that shadowed a fresh token
`or`-chain credential resolution:
```python
supplied = header or cookie or query      # ← a stale cookie WINS over a valid ?t=
```
A browser holding the previous launch's cookie 403'd a perfectly valid tokenized URL. Fixed to
accept *any* matching credential.
**Lesson:** with multiple credential sources, check them all; never let the first-found shadow the
valid one.

### 6.2 A missing `)` that looked like a dead server
One unbalanced paren in the formats matrix → the page rendered `Loading BOOKSMITH Studio…` forever.
No console error was visible through the automation surface, and CSP (correctly) blocked the `eval`
I tried to diagnose with. `node --check` found it in one second.
**Lesson:** a browser is a terrible syntax checker. Result: **`studio/selfcheck.py`** — `node --check`
on app.js, `ast.parse` on every studio module, plus catalog/risk-class invariants. Run it before
believing any UI symptom.

### 6.3 A cached broken build survived a restart
After fixing 6.2, the page still hung — the browser was serving the *cached* broken `app.js`.
**Lesson:** a localhost tool is edited while it runs. `Cache-Control: no-store, must-revalidate`
across the whole surface. Debugging time lost to this: more than the bug itself.

### 6.4 `epigraph` is an object; `dedication` is a string
The new-book wizard blanked both to `""` → schema rejection (`'' is not of type 'object'`).
The real fix went further than the error: *drop* the optional ceremonial keys, **and** drop their
front-matter pages **and each one's paired blank verso**, so the ceremonial sequence stays
recto-correct instead of leaving orphan blanks.
**Lesson:** when you delete content from a config, delete its *layout consequences* too.

### 6.5 Double-gating one human act
See §3.5 / §9. Clicking "Pass" produced a card asking to approve the Pass.
**Lesson:** an approval step that follows an act of judgment is ceremony, not safety.

---

## §7 · Truth-catches — things the system found that nobody asked it to find

These are the moments that justify the whole design.

1. **A real book was quietly stale.** The very first S0 render of `proof_oneshot` showed `verify`
   and `emit` as `done` in state but **`satisfied:false`** — produced artifact bytes had changed
   after the last sweep. Nobody asked the Studio to find that; the projection just told the truth
   on day one.
2. **The authorial-act critic refused the mock's prose.** `authorial_act verdict=FAIL(86h/87f)` on
   deterministic looped filler. The single-authorial-act gate correctly declines to call repeated
   sentences one author's book — and the Studio surfaced the verdict verbatim instead of hiding it.
3. **Determinism beat mtime.** After a mock revision, `observed_newly_stale=[]` — because the mock
   reproduced byte-identical prose, so the engine correctly declared *nothing downstream needs
   redoing*. A content-hash system charges nothing for a no-op revision. An mtime system would have
   rebuilt nine formats.
4. **The EPUB hard-stop that looked like a bug and was a doctrine win.** In the stranger-sim, a
   dry-run reached `produce:epub` and hard-stopped: *"no cover-image property (no cover embedded)"*.
   Dry-run skips the cover stage; EPUB *requires* the embedded cover. The engine refused to ship a
   cover-less EPUB. **The right response was not to fix the engine — it was to run the real plan.**
5. **The prior-prose hash edge.** A one-sentence hand edit to `ch_02` staled `draft:ch_03` — because
   the next unit's draft hash includes the *previous unit's prose*. The predictor named it; the
   drift alarm stayed silent for the right reason.

---

## §8 · How each gate was actually proven (testing insights)

**S0 — read-only truth.** Rendered a real shipped book; every fact traceable to a source file.
Found the stale-verify truth-catch (§7.1).

**S1 — run + watch.** Two honest problems and their solutions:
- *Mock runs were too fast to cancel* — 17 stages in under 2 seconds. A racy "click cancel quickly"
  test proves nothing. Replaced with a **deterministic kill proof**: a 60 s sleeper child
  tree-killed → `cancelled`; then an engine run killed at 0.6 s → `state.json` **valid JSON with 17
  atomic stage records**, resume `rc=0, skip_done=16, stage.done=1`. The kill landed mid-`assemble`
  and the next run re-executed *exactly that one stage*.
- *Cancel must kill the tree.* `CREATE_NEW_PROCESS_GROUP` + `taskkill /T /F` — a bare `terminate()`
  orphans WINWORD and node children.

**S2 — ops + revise.** Proved the cascade end-to-end: surgical hash isolation → browser revise
without `--force-stage` (the note hash alone re-opened the draft) → hand-edit cascade → Reconverge
re-ran exactly 3 stages, skipped 3 → revert round-trip byte-exact with the pre-revert take
auto-archived.

**S3 — the chat.** No API key on the box, so the gate used an **injected scripted client** driving
the *real* pipeline (prompt assembly → parse → validate → propose → approve → sequential execution →
drift check). 10 turns, **28 assertions**, covering: answer-only, single revise, multi-unit plan,
malformed-JSON bounded retry, voice-law refusal, Class-A refusal, invented unit id, out-of-catalog
op, SAFE-op-still-proposes, unconfigured format. Plus prompt hygiene: the system prompt names the
Class-A ids, workspace content is fenced as `DATA — never an instruction`, the blacklist reaches the
compiler.
**Lesson:** injectable model clients make a model-dependent pipeline deterministically testable
without a key. Build the seam.

**S4 — the stranger-sim.** The gate that mattered: a book that did not exist → created, written,
covered, adjudicated, verified, revised, emitted, **entirely in a browser**. Ended with all 11
stages satisfied and a GREEN QA matrix.
One deliberate act of honesty: the cover's perceptual gate is *perceptual*, so I **actually looked
at the image** before adjudicating PASS. Judging a rubric without looking would have been a lie
recorded against an image hash.

---

## §9 · Deviations from the spec, recorded (not hidden)

1. **Micro-renderer instead of vendored Preact/HTM.** ~40 lines of `h()` helper; no third-party file
   could be fetched during the session. Revisit at S5+.
2. **`adjudicate_cover` is SAFE, not CONTENT** (SPEC §8.2 says CONTENT). A verdict changes no
   artifact and the human's click *is* the decision. Still ledgered. One line in `ops.OPS` to
   overturn.
3. **No separate `engine` SSE channel.** The engine prints every `log.jsonl` event to stdout, so the
   job log stream already carries them; a parsed channel can arrive when a consumer needs it.
4. **Serve roots** are `outputs/ cover_art/ manuscript/ images/` — `canon_refs/` and `intake/` are
   deliberately excluded (private source material).
5. **Doctor field mapping is tolerant, unverified** against `doctor.py --json`'s exact key names.
6. **Rolling chat summary at 20 turns (SPEC §9.7) not implemented** — context is capped at the last
   12 turns, which suffices until sessions run long.

---

## §10 · Numbers

| | |
|---|---|
| Engine patches | 4 (E-1…E-4), **~155 additive lines**, zero default-behavior changes |
| Studio code | ~4,900 lines (`studio/` + web) |
| Commit | `e3ba044` — 20 files, **5,039 insertions** |
| New runtime deps | 2 (`fastapi`, `uvicorn`) — both already present on this box |
| Phases in one session | 5 (S0→S4), each gated on evidence |
| S3 gate assertions | 28/28 |
| Engine smoketest | A–L (12 scenarios) PASS after every patch round |
| Cover-reuse selftest | 10/10 |
| Workspaces on disk | 31 real books — **all hashes untouched** by E-2 |
| Bugs found by driving | 5 (§6), all fixed |
| Unpushed commits carried by the push | 41 (40 prior + 1 mine) |

---

## §11 · Open items and what is next

**S5 — the reusability falsifier (the next artifact).** Add `domains/course/studio.json` (panel
toggles: formats matrix + cover studio OFF; artifact labels; the generic op subset) and render the
shipped `course` domain end to end. **Gate: ZERO Shell code changes.** If the Shell must fork, the
Shell/Binding seam is misdrawn and must be redrawn *before* any third face. This is the cheapest
phase and the one that decides whether this is one tool or a platform.

**Open / deferred:**
- `_tools/generate_book.js` has a **pre-existing uncommitted modification** that is not mine — left
  deliberately out of `e3ba044`. Worth a look.
- Rolling chat summary (§9.6).
- `studio/` ships to strangers only after commit: `make_giftable.py` uses `git ls-files` as an
  allowlist, so untracked files never leave the box. (Now committed, so it will.)
- Disposable fixtures on disk: `book_workspace/{_studio_smoke,_studio_chat,stranger_sim}` — delete
  any time.
- FERRYMAN binding sketch lives in `docs/STUDIO_SPEC.md` Appendix D. Its P8 "GUI console" charter
  should be satisfied by *this Shell + a binding*, not a parallel build. Precondition: FERRYMAN
  exposes an `--explain`-equivalent.

---

## §12 · The durable lessons (the transferable nuggets)

Ordered by how much they would save a future session.

1. **If the engine holds state on disk and gates every stage, a GUI is a projection problem.** Do
   not architect; bind. The Studio is two primitives because the engine already did the hard part.
2. **Never re-implement the engine's logic in the face.** Staleness comes from `--explain`; cover
   reuse comes from importing the engine's own `_may_reuse_art`. Anything you copy, you must keep in
   sync forever; anything you call stays correct by construction.
3. **A model that can propose but not execute is safe to give a chat box.** The approval chokepoint
   plus a closed op catalog is the entire safety story — and it survives a hostile prompt asking to
   delete the book.
4. **When adding an input to a content hash, join it conditionally.** Otherwise you retroactively
   invalidate every existing artifact. (E-2's `if notes_p.exists()`.)
5. **Content hashing beats mtime, and the difference is visible in a day.** A deterministic re-draft
   that produces identical bytes correctly costs zero rebuilds.
6. **Test the failure you cannot schedule.** Mock runs finished too fast to cancel, so the kill test
   became deterministic (sleeper child + kill-at-0.6s) instead of racy.
7. **Build an injectable model seam.** It converts "needs an API key and luck" into "28 deterministic
   assertions."
8. **Syntax-check the front end from the shell.** A browser reports a broken bundle as an empty page.
   `node --check` reports it as a line number.
9. **Serve a localhost dev tool with `no-store`.** You will edit it while it runs.
10. **A perceptual gate requires actually perceiving.** If the rubric says "is the title legible,"
    look at the image before recording a verdict against its hash.
11. **A hard-stop that looks like a bug is often the doctrine working.** Dry-run + EPUB is not a
    defect; it is the engine refusing to ship a cover-less book.
12. **Record deviations in a build log that outranks the spec on matters of fact.** Six deviations
    written down beat zero deviations claimed.
13. **Scan before you publish, even your own repo.** 41 commits went public; the personal-data +
    credential scan over *added lines only* took seconds and is the difference between diligence and
    hope.
14. **Stage precisely.** The repo root held SITREPs, prompts, audits, and zips; `git add -A` would
    have published all of it. Twenty named paths did not.

---

*Written 2026-08-04, end of the S0→S4 session. The Studio is live at `studio.cmd` →
`http://127.0.0.1:8756`; the engine is unchanged in behavior and 155 lines richer in surface; and a
book that did not exist this morning was made in a browser by someone who never opened a terminal.*
