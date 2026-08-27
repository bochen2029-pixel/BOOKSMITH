# The Book Passport — the machine-legible receipts object

*One JSON file per book that carries the book's receipts: identity, contents, word counts, the
human/machine authorship line, gate verdicts, spend, cover byte-identity, and the physical
dimensions a shelf needs. The Studio has rendered a passport as HTML since S10
(`studio/projection.py:passport_html`, route `GET /api/books/{slug}/passport`); the JSON form is
the durable, versioned contract every consumer reads — the bookshelf.ink 3D shelf, the AEO /
"this book carries its receipts" surface (CLOUD_HORIZON_v6 §39), and the colophon.*

**Schema:** [`_tools/passport.schema.json`](../_tools/passport.schema.json) — v0.1, ratified
2026-08-27 between the book-smith and book-web sessions (Intercom sandbox `book-estate`:
`PASSPORT_SHAPE_2026-08-27_book-smith.md` + `PASSPORT_COMMENTS_2026-08-27_book-web.md`).

**Contract (the never-refactor rules):**
1. Additive-only within a version; consumers MUST ignore unknown fields
   (`additionalProperties: true` everywhere).
2. Removals or type changes bump `passport_version`.
3. **`public` defaults FALSE** and is enforced in DATA: the shelf build refuses any passport
   without `public: true` (the privacy roster rule — Bo's own public books only; family books
   never). Set it via `book_config.passport.public`, or the explicit `--public` operator flag.
4. Cover bytes travel BESIDE the passport at publish time; the texture cache keys on `sha256`.
5. The same schema comes out of BOTH emitters: this kit tool (local books) and, later, the cloud
   worker assembling from the R2 workspace archive (tickets). Schema first, two emitters.

## Emitter

```bash
python _tools/emit_passport.py --config book_workspace/<slug>/book_config.json
# → <ws>/outputs/passport/passport.json (validated against the schema when jsonschema is present)

python _tools/emit_passport.py --config ... --publish <dir>
# → <dir>/passport.json + <slug>_cover_<sha12>.jpg beside it (delta 4)
```

stdout = the written path (machine-parseable); stderr = the one-line human summary.

## Field sources (all read-only projections of the workspace)

| Field | Source |
|---|---|
| identity / `lang` / `unit_noun` | `book_config.json` (`language` defaults en; `voice.unit_noun`) |
| `translation_of`, `public` | `book_config.passport.*` (optional block, schema-declared) |
| `units[].words`, `totals` | `manuscript/current/<uid>_current.md` |
| `spend` (exact when E-4 usage present) | `_engine/calls/call_*.json` + `_studio/chat/calls/` |
| `checks[]` | `_studio/verify/<fmt>.json` (the S4 verify matrix cache) |
| `gates_version` | `git rev-parse --short HEAD` of the kit (null when git absent) |
| `cover.sha256` / `method` | `outputs/kindle/<slug>_KINDLE_cover.jpg` + newest `cover_art/*.provenance.json` |
| `physical` (trim / pages / spine_in) | `book_config.trim` + `outputs/<fmt>/cover_meta.json` |
| `authorship` | `registry/human_edited_units.json` / `registry/authorship_ledger.jsonl` + class map |

The emitter is stdlib-only, atomic-write, and self-validating (structural floor always; full
jsonschema when installed). It never writes into `manuscript/` or mutates any book state.
