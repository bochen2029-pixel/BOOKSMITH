# Harness profile — CLAUDE CODE

*The reference harness. Most of the kit's machinery (hooks, rehydration, fan-out) is native
here, so almost nothing needs adapting.*

- **Instructions file:** `CLAUDE.md` (auto-loaded every session) is the full operating
  contract. This profile only names the Claude-Code-specific plumbing CLAUDE.md assumes.
- **Transcript:** `~/.claude/projects/<project-slug>/<session-id>.jsonl`. `rehydrate.py`
  auto-finds the newest one for the current project — no nonce protocol needed here.
- **Compaction survival (native):**
  - `PreCompact` hook → `_tools/on_precompact.py` snapshots `_CONTINUITY.md`, drops a
    `.booksmith_rehydrate` marker, and pre-bakes `_REHYDRATION.md`.
  - `SessionStart(compact|resume)` hook → `_tools/on_session_start.py` injects a hard STOP
    recovery block for any in-flight book (`_CONTINUITY.md` STATUS ≠ COMPLETE).
  - First act after a compaction: `python _tools/rehydrate.py --workspace <ws>`, then read
    `_REHYDRATION.md` + `_CONTINUITY.md` in full. See `docs/COMPACTION_SURVIVAL.md`.
- **Fan-out:** the Agent tool. Subagents = opus or sonnet, NEVER a smaller tier for reads
  (model policy, SUPERSTRUCTURE §0). Workflows drive deterministic multi-agent orchestration.
- **Model backend:** `--backend harness` (keyless; prose from this session) is the default
  and the recommended way to run the engine in-session.
- **Commands:** the kit's commands are plain-language (CLAUDE.md §3), dispatched by the model;
  no command files are needed.
