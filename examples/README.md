# examples/

The worked example ships in the repo as a real, tracked book workspace rather
than a copy in this folder. Look here:

**`book_workspace/testvoyage/`** — the generic proof book. It is the tracked
exception to the `book_workspace/*` gitignore guard, so it clones with the kit
and exercises the whole pipeline end to end.

## What to open first

| You want to see... | Open |
|---|---|
| the per-book config (every knob the toolchain reads) | `book_workspace/testvoyage/book_config.json` |
| every unit's interface contract (written before its prose) | `book_workspace/testvoyage/contracts/` |
| one unit's interface contract, in detail | `book_workspace/testvoyage/contracts/ch_01.md` |
| the drafted manuscript units | `book_workspace/testvoyage/manuscript/current/*_current.md` |
| the single version-pinned master every generator reads | `book_workspace/testvoyage/outputs/markdown/testvoyage_v1.md` |
| a finished print interior + cover wrap | `book_workspace/testvoyage/outputs/kdp_paperback/` |
| the Kindle build | `book_workspace/testvoyage/outputs/kindle/` |

`testvoyage/outputs/` holds a curated proof set (the tracked `*_v1.md` master
plus representative format outputs). Regenerated masters (`*_v2.md`, `*_v3.md`,
…) and large `.pdf.bak` artifacts are gitignored — rebuild them with the
production pipeline (`CLAUDE.md` §12) rather than reading a stale copy.

## Why a pointer instead of a copy

The finished formats are multi-megabyte binaries (DOCX / PDF / EPUB / cover
wraps). Duplicating them into `examples/` would bloat every clone for no gain;
the tracked `testvoyage/` workspace already is the example. To start your own
book, copy `book_workspace/testvoyage/book_config.json` as a template and follow
`INSTALL.md`.
