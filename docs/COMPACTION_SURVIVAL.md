# Compaction Survival — native, default, zero-fidelity-loss rehydration

A long book-writing session in a coding harness will eventually **compact** its
context (the harness summarizes older turns to reclaim room) or be **resumed** in
a fresh process. A hand-written summary loses detail. This subsystem makes a
BOOKSMITH session survive both with effectively **zero memory-fidelity loss**,
by treating the session's own `.jsonl` transcript as the source of truth and
rehydrating from it on demand.

It is **native and default**: no external skill required. It supersedes reliance
on the external perpetual-memory skill by embedding the mechanism in the kit.

---

## The idea (jsonl -> md high-fidelity rehydration)

Every Claude Code session is recorded as a JSON-Lines file at:

```
C:\Users\<you>\.claude\projects\<slugified-cwd>\<session-uuid>.jsonl
```

where the slug replaces `:` `\` `/` with `-` (so `C:\My-Project` ->
`C--My-Project`). Each line is one JSON object: substantive lines have
`type` in `{user, assistant, summary}`; the rest (`queue-operation`,
`attachment`, `custom-title`, `ai-title`, `last-prompt`, `mode`, `system`, ...)
is meta. `message.content` is a string or a list of blocks:
`text`, `thinking`, `tool_use`, `tool_result` (linked to its `tool_use` by
`tool_use_id`), and `image`.

That file is large (a real session here was **6.3 MB** — too big to re-ingest
whole), but converting it to clean **markdown** and dropping the meta/noise
yields roughly a **10x** reduction, and further stripping can take it much
smaller. The converted transcript is **higher fidelity than any summary because
it *is* the record**, merely compact. For one-shot book writing the converted
transcript fits a 1M context with room to spare.

Measured on this machine (`3cfcabad-…-442ca998f973.jsonl`, 6.26 MB, a
tool-heavy, thinking-light agent session):

| variant | tokens | note |
|---|---|---|
| full markdown | ~156,600 | all thinking + all tools |
| `--strip-thinking` | ~156,600 | this session had **0** thinking blocks; on reasoning-heavy sessions this is ~half |
| `--strip-thinking --no-tools` | ~50,900 | tool_result was 61% of raw volume, tool_use 32% |

So the dominant lever varies by session: **thinking** on reasoning-heavy runs,
**tool traffic** on agent runs. The tiering below adapts automatically because it
*measures* rather than assumes.

---

## The two scripts

### `_tools/transcript_to_md.py` — the porter
Streams a session `.jsonl` line-by-line (never loads the whole file) and renders
clean markdown. Ported from `claude_archive_viewer_v5.html`'s markdown exporter.

```
python _tools/transcript_to_md.py <session.jsonl> \
    [--out OUT.md] [--strip-thinking] [--no-tools] \
    [--max-tool-chars N=1500] [--tail-turns N] [--since-uuid UUID]
```

- user turns -> `## User` + text; pure tool_result-carrier user turns render as a
  compact `> [tool result: <name>] <first N chars…truncated>` (skipped under `--no-tools`).
- assistant turns -> `## Assistant` + text; `thinking` -> `> [thinking] …`
  unless `--strip-thinking` (then omitted); `tool_use` -> `- [tool: NAME] {args summarized}`.
- tool_result payloads truncated to `--max-tool-chars` with a `…[+N chars truncated]` marker.
- turn order preserved; a header records source path, line count, and flags.
- robust: tolerates missing keys, string-vs-array content, unknown block types;
  UTF-8 in/out with `errors='replace'`; never crashes on a bad line.

### `_tools/rehydrate.py` — the orchestrator / forcing function
Finds the newest session `.jsonl`, converts it in **tiers** to fit a token
budget, writes `<workspace>/_REHYDRATION.md`, and prints a loud read-me-first block.

```
python _tools/rehydrate.py \
    [--session PATH] [--project-dir DIR] [--workspace DIR] \
    [--budget-tokens N=250000] [--out OUT.md]
```

Auto-find order: explicit `--session` -> `<cwd>\.booksmith_rehydrate` flag ->
newest `*.jsonl` in the derived project dir. Token counting uses `tiktoken`
(`o200k_base`) in-process if available, else the `kit_env.organs.estimate_tokens`
tool if configured (falling back to the vendored `_tools/estimate_tokens.py`),
else `chars/4`.

---

## The three tiers

`rehydrate.py` escalates only as far as needed to fit `--budget-tokens`:

1. **Tier 1 — `--strip-thinking`** (full tool traffic). The default target.
2. **Tier 2 — `--strip-thinking --no-tools`** if Tier 1 is over budget.
3. **Tier 3 — `--strip-thinking --no-tools --tail-turns N`** if still over: keep
   only the most recent N turns that fit (found by halving the turn count).

It always reports the tier chosen and the reduction ratio (raw jsonl bytes ->
md tokens). At the default 250k budget on the 6.26 MB session above, Tier 1
fits (~156k tokens) so tools are preserved.

---

## The two hooks

Registered in the kit's `.claude/settings.json` with repo-relative commands —
they work wherever the kit folder lives. (If a book is being written under a
*different* project folder, merge the same hooks into that project's
`.claude/settings.json` too, so the in-flight session is protected.)

- **PreCompact -> `_tools/on_precompact.py`.** Just before a compaction:
  (a) snapshots each `book_workspace/*/_CONTINUITY.md` to `_CONTINUITY.snapshot.md`;
  (b) writes `<cwd>\.booksmith_rehydrate` with the resolved session path;
  (c) best-effort runs `rehydrate.py` so a fresh `_REHYDRATION.md` is already
  waiting. All best-effort; the hook never fails (always exits 0).

- **SessionStart -> `_tools/on_session_start.py`.** At session start the harness
  injects this script's **stdout** into the model's context. If an in-flight book
  exists (a `book_workspace/*/_CONTINUITY.md` whose `STATUS` != `COMPLETE`) **and**
  `source` is `compact`/`resume` (or the `.booksmith_rehydrate` flag exists), it
  prints a hard **STOP — COMPACTION/RESUME RECOVERY** block: the head of the
  ledger inline plus explicit first-action instructions (run `rehydrate.py`, then
  read `_REHYDRATION.md` + the full `_CONTINUITY.md` + `seed.md` before any prose).
  Otherwise it prints nothing. Never crashes.

Hooks config schema:

```json
{ "hooks": { "SessionStart": [ { "hooks": [ { "type": "command", "command": "python _tools/on_session_start.py" } ] } ],
             "PreCompact":   [ { "hooks": [ { "type": "command", "command": "python _tools/on_precompact.py"  } ] } ] } }
```

---

## Invoking manually

Any time (before a big turn, or right after a resume):

```
python _tools/rehydrate.py --workspace book_workspace/<slug>
```

Then READ the printed `_REHYDRATION.md` in full, plus that book's `_CONTINUITY.md`
and `seed.md`, before writing prose.

---

## The continuity-ledger convention

Each in-flight book keeps a **`book_workspace/<slug>/_CONTINUITY.md`** that the
harness rewrites **after every chapter** (never let it go stale). Its first
section is a **RESUME PROTOCOL** and its header carries a status token:

```
# _CONTINUITY — <Title>  (STATUS: IN_PROGRESS)

## ⚠️ RESUME PROTOCOL — do this FIRST, before writing any prose
1. Run rehydrate.py --workspace <this dir> and READ the resulting _REHYDRATION.md.
2. Read THIS whole file.
3. Read seed.md IN FULL (the Book Bible).
4. Read the LAST completed chapter for voice.
5. THEN continue drafting from NEXT. After finishing each chapter, rewrite this file.

## THE BOOK (one line)   …
## DONE (chNN, word counts, on disk)   …
## NEXT -> write ch_NN …
## REMAINING CHAPTER CONTRACTS …
```

`STATUS` is any of `IN_PROGRESS` / `DRAFTING` / `COMPLETE` (the hooks treat
anything other than `COMPLETE` as in-flight). The ledger is the **human-curated**
layer; `_REHYDRATION.md` is the **machine-verbatim** layer. Together:

> continuous ledger (the model curates what matters) + jsonl->md rehydration
> (the scripts preserve the verbatim record) + forced-first-action (the hooks) —
> three layers, portable, default.

---

## Fallback — the perpetual-memory principle

If, after many compactions, the converted transcript itself grows past the
budget even at Tier 1, `rehydrate.py` falls through to Tier 2 then Tier 3 (recent
turns verbatim). The general principle when even that is not enough: **distill the
oldest turns into the ledger and keep the recent turns verbatim** — the model that
lived the context decides what survives, and the reconstitution pointers on disk
(the session `.jsonl`, `_CONTINUITY.md`, `seed.md`) let any fresh session
reconstitute cold. This is the perpetual-memory idea, embedded natively in the
kit rather than borrowed from an external skill.
