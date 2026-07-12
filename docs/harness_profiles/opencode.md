# Harness profile — OPENCODE

*OpenCode reads `AGENTS.md` as its instructions file and supports slash-commands + plugins.*

- **Instructions file:** `AGENTS.md` (repo root) boots the kit and routes you to `CLAUDE.md`
  for the full contract — treat its "Agent tool" / "`.jsonl` transcript" mentions as "your
  OpenCode equivalent."
- **Slash commands:** `.opencode/command/*.md` (e.g. a `start.md` that runs the boot). Add kit
  commands here as thin wrappers over the plain-language flow if you want shortcuts.
- **Transcript / session store:** OpenCode keeps its own session store (commonly under
  `~/.local/share/opencode/` or `~/.opencode/`). If `rehydrate.py --session` needs the exact
  file, locate it with the **nonce protocol** (`generic.md`) rather than assuming a path.
- **Fan-out:** use OpenCode's sub-agent / task mechanism if present (one model tier down);
  otherwise run digestion + audit passes inline in the main loop.
- **Hooks:** OpenCode's session hooks / JS plugins can call `_tools/on_precompact.py` and
  `_tools/rehydrate.py` at the analogous lifecycle points; until that is wired, rely on the
  continuously-maintained `_CONTINUITY.md` ledger + the nonce protocol for recovery.
- **Model backend:** if OpenCode supplies the model, drive the engine with `--backend
  harness`; otherwise set `kit_env.model.backend` to `anthropic` / `openai`.

*(A sibling port exists at `C:\BookSmith-OpenCode` on the reference machine — a reference for
OpenCode wiring, not required by this kit.)*
