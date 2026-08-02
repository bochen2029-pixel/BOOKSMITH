# Cover-art provenance — backfill for the four silent-fallback books

*Created 2026-07-31 as part of finishing the cover-provenance node. Read
`docs/LESSONS_LEDGER.md` §20.3 first — it is the why. This file is the what-to-do.*

## What happened

For months `cover_gen.py` could only start ComfyUI via `comfy launch` (comfy-cli),
which is not on PATH here. When that failed, `engine.py` fell through to
`cover_pick.py` and shipped a **hypergen** procedural cover where the book's
`book_config.cover.art` specified **SDXL**. No gate went red: `hypergen.py` makes
*tasteful* abstract art, so it passed the `vision_verify` perceptual rubric that was
supposed to catch placeholders. **A fallback that degrades provenance without
degrading appearance is invisible to a perceptual check.**

Fixed (2026-07-31): `cover_gen.py` now launches ComfyUI Desktop's `main.py` directly
(no comfy-cli needed) **and** writes `cover_art/<slug>_src.provenance.json` on every
generation; `cover_pick.py` writes `method: hypergen|catalog`; and
`verify_build.py :: check_cover_art_provenance` **fails closed** unless a sidecar
proves `method: sdxl` (or the book declares a non-generated `cover.art.method`).

## The four known-affected books

Each has `cover_art/<slug>_src.png` on disk but **no** `*.provenance.json` — the
fingerprint of the silent fallback. Under the new gate they FAIL CLOSED until fixed.

| slug | workspace | state |
|---|---|---|
| `governed_practice` | `book_workspace/governed_practice/` | src.png present, 0 provenance |
| `last_mile`         | `book_workspace/last_mile/`         | src.png present, 0 provenance |
| `openworker`        | `book_workspace/openworker/`        | src.png present, 0 provenance |
| `gate_and_ledger`   | `book_workspace/gate_and_ledger/`   | src.png present, 0 provenance |

Check current gate status for all four at once:

```bash
for s in governed_practice last_mile openworker gate_and_ledger; do
  python _tools/verify_build.py --config "book_workspace/$s/book_config.json" --format kindle 2>/dev/null \
    | grep -i cover_art_provenance || echo "$s: (run manually)"
done
```

## Remediation — pick ONE per book

These are unpublished v1.0 builds, so either path is legitimate; the point is that
intent and record must agree.

**Option A — regenerate the real SDXL cover (recommended).** The launcher is fixed,
so this now produces genuine SDXL art AND writes the provenance sidecar. Then
recomposite the wrap/ebook cover and re-verify (an interior-unchanged cover swap):

```bash
python _tools/cover_gen.py --config book_workspace/<slug>/book_config.json \
    --out book_workspace/<slug>/cover_art/<slug>_src.png
# then recomposite every profile the book ships + re-run its gates (see §12 build order)
```

**Option B — keep the hypergen art, declare it.** If the shipped abstract cover is
acceptable, record the truth in `book_workspace/<slug>/book_config.json`:

```json
"cover": { "art": { "method": "hypergen",
  "_method_note": "v1.0 shipped a hypergen cover during the comfy-cli-absent window; kept deliberately." } }
```

The gate then passes by declaration. (Do **not** declare `sdxl` for a hypergen
cover — that reintroduces the exact lie the gate exists to catch.)

## Verify the fix held

```bash
python _tools/verify_build.py --config book_workspace/<slug>/book_config.json --format <fmt>
# cover_art_provenance -> PASS  (either "confirmed by provenance sidecar (methods: sdxl)"
#                                 or "satisfied by declaration")
```
