# Domain-general engine (#10) + typography vision-loop (#6) — build log

*Autonomous build started 2026-07-13 on branch `domain-typography-2026-07-13`. Directive (Bo):
make maximal progress on ROADMAP §9 items #10 and #6; leave a history trail; do NOT regress
(full green sweep after every step); snapshot load-bearing files before editing.*

## Discipline (enforced every step)
- **Branch:** `domain-typography-2026-07-13` — `main` stays untouched until this is proven.
- **Snapshots before edits:** `_snapshots/<file>.pre-spike-20260713.bak` (gitignored). Revert
  target if anything regresses.
- **Green sweep after every step:** `engine_smoketest.py` (A–I) + `selfcheck.py` + every tool
  `--selftest`. A red sweep = stop + revert, never advance.
- **Commit per green increment** — git history is the primary trail; this file is the narrative.

## Phase 0 — safety setup ✅ (done)
- Branch created off `main`.
- Snapshotted: `engine.py`, `book_config.schema.json`, `engine_smoketest.py`,
  `composite_cover.py`, `vision_verify.py`, `cover_pick.py` → `_snapshots/*.pre-spike-20260713.bak`.
- `_snapshots/` added to `.gitignore`. This log created.

## Phase 1 — engine domain-awareness (#10 seam)
Goal: teach the deterministic engine to run ANY domain declared by `domains/<name>/domain.json`,
while the book path (domain absent/"book") stays byte-identical (zero regression). Plan:
1. Schema: add optional `domain` (default "book").
2. Engine loads `domains/<domain>/domain.json` when `domain != "book"`; else built-in book path.
3. `plan()`, `stage_precheck`, `stage_produce`, `stage_verify`, cover-skip, prompt `unit_noun`
   all guarded on `self.domain != "book"`.

**Result ✅ (2026-07-13):** landed in `engine.py` — `__init__` loads `domain` +
`domains/<d>/domain.json`; `_load_domain_spec` / `_resolve_token` helpers; `plan`, `precheck`,
`produce`, `verify`, `emit`, `input_sha(produce)`, `build_draft_prompt`, `_seed_needed` all branch
on `domain != "book"` (book path byte-identical). Schema gains an optional `domain`. Non-book plan =
`precheck → draft:* → integrate → produce:<target>* → verify → emit` (no assemble/cover/print).
**Non-regression sweep 7/7 green** (engine smoketest A–I + selfcheck + all tool selftests).

## Phase 2 — the `course` domain (#10 proof)
A second domain (modules → lessons) proving the engine is domain-general: `domains/course/`
descriptor + producer + verifier, driven end-to-end through the engine on the mock backend.

**Result ✅ (2026-07-13):** `domains/{README, book/README, course/*}` created. The `course` domain =
`domain.json` (targets/producers/verifier) + `produce_course.py` (lessons → modules → `course.md`
+ `course.json`) + `verify_course.py` (structure + advisory authorial-act). A real drive through the
UNCHANGED engine: `precheck(domain=course) → draft:l_01..03 → integrate → produce:course_md +
course_json → verify → emit`, rc 0, 2 modules / 3 lessons produced + verified. Locked as smoketest
scenario **J**. Bonus fix: the integrate→authorial_act advisory parse (`--json` is pretty-printed; it
was reading only `}`) — the advisory + the `quality_gate` opt-in now actually function. **Sweep A–J
7/7 green; book path unchanged.**

## Phase 3 — typography vision-loop (#6)
`composite_cover` proposes N title layouts; score each (vision when available, else a mechanical
legibility proxy over the title band); pick the best. Testable via the mechanical proxy.

**Result ✅ (2026-07-13):** `_tools/cover_layout.py` — proposes N candidate title bands over the
cover ART and scores each: mechanical by default (`0.55*calmness + 0.45*contrast` over the band —
keeps the title off busy areas, onto negative space), `--vision` re-ranks the top-K via
`vision_verify` (the perceptual loop). `--selftest` (calm-top beats busy-bottom) + a real catalog
cover (picked the calm upper band, score 0.60) verified. **WIRED 2026-07-13:** `composite_cover.py`
now takes `--title-y-frac` (guarded; default = house 0.030, so default renders are byte-identical)
and `cover_layout`'s `best.y_frac` feeds it — proven (override moves the title; default unchanged;
render exit 0). **#6 fully done + wired** (palette-transfer + typography loop + compositor wiring).

## Outcome
Both #10 (domain-general engine, proven via `domains/course/` + smoketest J) and #6 (cover
palette-transfer + typography vision-loop) landed with **zero regression** — the full green sweep
(engine smoketest A–J + selfcheck + every tool `--selftest`) passed after every step. Branch
`domain-typography-2026-07-13` (merged to `main`), snapshots in `_snapshots/`.

**Bonus wiring (2026-07-13, on `main`):** the full Cover 2.0 loop is now connected —
`cover_pick.py --recolor` recolours a catalog pick to the book palette (via `palette_transfer`)
on install; `cover_layout.py` picks the calm title band; `composite_cover.py --title-y-frac`
places the title there. Each guarded so defaults are byte-identical; all proven end-to-end. The
only piece left is auto-orchestrating these three from the engine's cover stage.

## Phase 4 — engine cover auto-orchestration ✅ (branch `cover-orchestration-2026-07-13`)
DONE: the engine's `stage_cover` now runs the full loop itself — source art (bespoke SDXL else
`cover_pick --recolor` for catalog picks) → `cover_layout` picks the calm title band →
`composite_cover --title-y-frac` composites the ebook cover. Guarded by `no_cover` (dry-run /
smoketest skip it). **Proven:** a real `proof_oneshot` run `--from cover` → `cover art: cover_pick
+recolor; title-band y_frac=0.02; composited kindle` → `produce:epub` (embeds the composited cover)
→ verify → emit, rc 0. Smoketest A–J + selfcheck green. **#6 fully complete** (all four pieces + the
engine auto-orchestration).

## Phase 5 — non-book auto-architect ✅ (#10 completion)
DONE: a non-book domain can now be architected from a BRIEF (no pre-declared units), matching the
book's brief→structure capability. `stage_seed` branches to `_seed_domain` for non-book: the model
(or the deterministic fallback) outlines the domain's units from the brief, writes them into the
config + a simple domain outline (`seed.md`); gate = units exist. No book schema / §1–§7 / contracts.
`_seed_prompt` + `_fallback_seed_plan` + `_slugify_units` generalized (domain `unit_noun`, `module`
preserved), all guarded so the book path is byte-identical. **Proven:** a course from a `lessons: 3`
brief → `architected 3 lesson(s)` → drafted → produce:course_md+json → verify → emit, rc 0. Locked as
smoketest scenario **K**. Bonus fix: the fallback count regex was missing `lessons|modules` (caught by
a debug trace). Sweep **A–K + all selftests + selfcheck: 8/8 green.** #10 fully complete.

---
*(entries appended above as each phase landed)*
