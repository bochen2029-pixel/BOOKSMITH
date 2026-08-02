# intake/ — the DROP ZONE

Place a **new book's** gist + source documents here, then start a session. The boot
sequence detects a populated `intake/` with no matching workspace as **INIT** and
runs the INTAKE → INGEST path (GATE-0/GATE-1) over exactly what is here.

**Keep this folder empty between books.** Only the CURRENT drop lives here — the
mode detector treats anything present as the next book's corpus, so stale material
from a prior build poisons the next INIT (the wrong-corpus trap).

- Contents from builds before 2026-08-02 were preserved verbatim at
  `_intake_archive/pre_2026-08-02/` (six prior books' gists + sources; nothing was
  deleted).
- A book whose materials were dropped **directly into its workspace** instead does
  not use this folder at all — that is the **STAGED** boot mode (see CLAUDE.md §1
  step 4): the workspace itself is the drop, read in place, and `intake/` is
  ignored for it unless it contains a gist naming that slug.
