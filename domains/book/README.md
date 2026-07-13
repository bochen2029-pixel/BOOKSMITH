# domains/book/ — the built-in default domain

The **book** domain is the engine's native, reference pipeline: one intake drop → nine
upload-ready publishing formats (Kindle, EPUB, KDP paperback/hardcover, Mixam
paperback/hardcover, Blurb paperback/hardcover, digital PDF) + a generated, verified cover.

Unlike other domains, the book domain has **no `domain.json`** — its stages, producers, and
gates are built into `_tools/engine.py` (and the wider toolchain: `generate_book.js`,
`build_epub.py`, `docx_to_pdf.py`, `composite_cover.py`, `verify_build.py`, …). A config with
`domain` absent or set to `"book"` uses this path, and it is byte-identical to the pre-
domain-seam engine.

Think of this folder as documentation of the reference domain that every other
`domains/<name>/domain.json` is modeled on:

| domain concept | book realization |
|---|---|
| unit | chapter (`voice.unit_noun`) |
| architect (seed) | `stage_seed` → `seed.md` + contracts + schema-valid `book_config.json` |
| produce targets | the `formats[]` (kindle/epub/kdp_*/mixam_*/blurb_*/digital_pdf) |
| producers | `generate_book.js` / `generate_kindle.js` / `build_epub.py` / `build_digital_pdf.py` |
| cover | `stage_cover` (SDXL / hypergen) → `composite_cover.py` |
| verifier | `verify_build.py` (mechanical) + `vision_verify.py` (perceptual) |

See `../README.md` for the domain system and `../course/` for a second, non-book domain
proving the engine is domain-general.
