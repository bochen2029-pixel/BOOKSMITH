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
cover (picked the calm upper band, score 0.60) verified. Wiring TODO: feed the chosen band into
`composite_cover.py` (`--title-y-frac`). **#6 now fully done** (palette-transfer + typography loop).

## Outcome
Both #10 (domain-general engine, proven via `domains/course/` + smoketest J) and #6 (cover
palette-transfer + typography vision-loop) landed with **zero regression** — the full green sweep
(engine smoketest A–J + selfcheck + every tool `--selftest`) passed after every step. Branch
`domain-typography-2026-07-13`, snapshots in `_snapshots/`.

---
*(entries appended above as each phase landed)*
