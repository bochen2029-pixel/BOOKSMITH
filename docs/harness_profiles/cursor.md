# Harness profile — CURSOR

*Cursor's agent reads `AGENTS.md` (and/or `.cursorrules`). The kit runs the same way; only the
transcript location and the fan-out model differ.*

- **Instructions file:** `AGENTS.md` at the repo root routes you to `CLAUDE.md` for the full
  contract. A short `.cursorrules` that points at `AGENTS.md` also works.
- **Transcript / session store:** Cursor stores chats in its own application data, not a repo
  file. Use the **nonce protocol** (`generic.md`) with `harness_detect.py --find-transcript`
  to locate the record; if it is not on the searchable filesystem, rely on `_CONTINUITY.md`
  (the kit's harness-agnostic ledger) to resume.
- **Fan-out:** Cursor runs a single agent loop — do source digestion + audit passes inline in
  the main loop (no separate sub-agent tier), and keep the Context Pack small (CLAUDE.md §6
  shrink note for sub-1M context).
- **Model backend:** Cursor supplies the model → drive the engine with `--backend harness`; or
  set `kit_env.model` for an API / local backend.
- **Print tier:** on a Mac Cursor box (no Word COM) you are Tier 2 — EPUB / Kindle / digital
  plus the LibreOffice print fallback (`docx_to_pdf.py` auto-detects `soffice`).
