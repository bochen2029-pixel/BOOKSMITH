# QC FULL-AUDIT RUNBOOK — "is this book actually up to spec?"

*The reusable end-to-end audit + remediation method, distilled from the 2026-07-23 full QC of the
A Human Still Signs English Amazon set (which found one shipped rendering defect, two sub-ideal
specs, and a Word-COM infrastructure bug — all closed same-day with zero manuscript edits).
Run it before any upload, after any rebuild, or whenever the operator asks "check it all out."
Companion detail: `LESSONS_LEDGER.md` (rules), `format_spec_sheet.md` (numbers),
`_QC_EN_AMAZON_2026-07-23/` in the book workspace (the worked example with logs + manifests).*

**Two laws.** (1) Re-verify LIVE — never trust a ledger claim, a sitrep, or a previous session's
green; artifacts and claims drift (the 07-20 sitrep asserted proposals were "not installed";
disk + hashes proved they were). (2) Verification is read-only; remediation only starts on the
operator's word, and then with backups + logs + a rollback path FIRST.

---

## Phase 0 — Backup + rollback discipline (before ANY change; skip for read-only audit)

1. `_BACKUP_<date>_<label>/` inside the workspace: copy every file you may change or regenerate
   (all target `outputs/`, composed covers, any kit file you will touch — pull kit pristines from
   `git show HEAD:<path>` if the working tree is dirty), plus a pristine copy of any canon file
   involved even when you do NOT plan to touch it (audit comparison).
2. `MANIFEST.sha256.txt` (hash every backed-up file) + `GIT_STATE.txt` (HEAD + status) +
   `ROLLBACK.md` (exact copy-back commands + git revert instructions).
3. Kit changes land as ONE commit at the end → rollback = one `git revert`. Do NOT sweep other
   sessions' uncommitted edits into your commit; leave foreign-modified docs uncommitted and say so.
4. After the work: `MANIFEST_POSTFIX.sha256.txt` over the final artifacts. Bonus proof: if canon
   was untouched, the re-assembled master hash MUST equal the pre-fix master hash.

## Phase 1 — Provenance + freshness trace

- List `outputs/**` with mtimes; compare against the newest `manuscript/current/*` mtime.
  **Every artifact must be newer than the newest canon file** (source-drift check; the
  8,476-words-short Kindle was exactly this failure).
- Hash-compare the last two master versions (`outputs/markdown/*_vN.md`) — identical hashes mean
  an idempotent re-assemble, not a content change.
- Read the `cover_meta_*.json` + `*.render.json` sidecars; the recorded `pages` must all agree.
- Note anything stale (e.g. a parked Mixam set) so it cannot be uploaded by accident.

## Phase 2 — Mechanical gates, run live

```
python _tools/lint_manuscript.py  --config <cfg>            # exit 0
python _tools/scan_manuscript.py  --config <cfg>            # PASS (WARNs = operator-known only)
python _tools/verify_build.py --config <cfg> --format kindle
python _tools/verify_build.py --config <cfg> --format <print_fmt> --final   # background; Word COM
```
- Spine math by hand: `pages x per_page + board_add` must equal the compositor meta.
- Word-COM hygiene: before + after, `Get-Process WINWORD` — kill zombies (a leaked instance
  poisons the next run: LESSONS_LEDGER §3.7b). The tools are DispatchEx-first + retry-armored,
  but check anyway.

## Phase 3 — Book-specific invariants (config-driven, not generic)

- Refrain: exact string count in prose + designated placements (+ back-cover placement if contracted).
- Zero placeholders: `[BO-WRITES`, `[TODO`, `[⚠`, fill-blanks (scan_manuscript covers most).
- H1s byte-match `units[].title`; per-unit files UTF-8 no-BOM.
- Whatever this book's contracts made sacred — read the seed/ledger and CHECK those specifically.

## Phase 4 — Perceptual pass (render → view; a machine can't see everything)

1. **Token sweep FIRST** (cheap, whole-book): extract full PDF text; search for LaTeX leaks
   (`\frac \iff \wedge` …), literal `**`/`##`/`` ``` ``, tofu `�`, em/en dashes, stray pipes.
   Every hit becomes a page to view. (The one real defect of 2026-07-23 — literal `**` in a
   printed bullet — was found by this sweep on page 305 of 344.)
2. Render a TARGETED page set at 150dpi (≤2000px, imguard-safe): half-title, title, copyright,
   Contents (all pages), reader's note, first + one mid chapter opener (plate + recto + folio),
   the math-densest and code-densest pages, any table pages, acknowledgments, last content page,
   trailing blanks. VIEW them — typography, spacing, plates, folios, headers-absent.
3. Covers: full wrap + crops (spine band, barcode keep-out at TRUE geometry, banner seams,
   title zone) + the ebook cover. Pixel-verify the keep-out is empty (modal-color share = 100%).
4. **Probe gotchas (they bite every time):**
   - Display headings are letter-spaced ("C O N T E N T S") — substring search MISSES them;
     search rendered text loosely or view the page.
   - **Whitespace-normalize before phrase-searching extracted PDF text** — a line-wrapped phrase
     ("ferry others, ferry\nyourself") is invisible to a raw substring search; `" ".join(t.split())`
     first. (2026-07-23: a refrain placement looked missing purely because of this.)
   - `find_page("Chapter N …")` hits the TOC entry first, not the opener — search a body-only phrase.
   - rg/Grep SKIP gitignored `book_workspace/` — use Python or PowerShell Select-String there.
   - Never Read an image >2000px (imguard or render small).
   - Word-COM verify and any other Word user must not run concurrently.
5. **Heading-survival check (cheap, catastrophic when skipped):** extract every `## `/`### `
   heading text from canon and assert each appears in the rendered PDF/DOCX/epub text.
   (2026-07-23, the_crossing: an "all green" build had silently dropped ALL 67 in-chapter
   section headings from print + Kindle — the H2-drop trap — because the build chain skipped
   `scan_manuscript`. verify_build cannot see it; only this cross-check or the pre-build scan can.
   Corollary: **scan_manuscript is a MANDATORY pre-build gate** — any hand-rolled build chain that
   skips it forfeits the packaging guarantees.)

## Phase 5 — Verify against AMAZON'S OWN published specs (not third-party aggregators)

- Help topics (IDs verified live 2026-07-23): eBook cover `G200645690` (ideal 2560h x 1600w,
  ratio ≥1.6:1, min 625x1000, max 10000, RGB JPEG/TIFF <50MB) · eBook formats `G200634390`
  (DOC/DOCX supported, EPUB supported, KPF recommended) · margins + trim + page counts
  `GVBQ3CMEQW3W2VL6` (gutter by page count: 24-150→0.375 / 151-300→0.5 / 301-500→0.625 /
  501-700→0.75 / 701-828→0.875; outside ≥0.25 no-bleed, ≥0.375 bleed; bleed 0.125;
  hardcover range 75-550) · hardcover cover `GDTKFJPNQCBTMRV6`.
- **The Print Cover Calculator is public and scriptable** (`kdp.amazon.com/cover-calculator`,
  no sign-in): select-ids `binding-type-dropdown` (CASE_LAMINATE) / `cover-type-dropdown` /
  `interior-type-dropdown` / `paper-type-dropdown` / `reading-direction-dropdown` /
  `measurement-units-dropdown` / `trim-size-dropdown` (`6X9IN`) / `page-count-input`, set via JS
  + dispatched input/change events, click the submit input → a results table with Full Cover /
  Front / Margin / Wrap / Hinge / Spine / Spine-safe / Barcode numbers FOR YOUR EXACT SPEC.
  Compare Full Cover W×H to the composited wrap to ≤0.001 in; compare the stated spine + safe
  area to what the compositor drew (spine TEXT must fit the safe area; band edges near the
  hinge are a Previewer fold-line check).
- The calculator/Previewer ALWAYS outranks presets and this runbook's cached numbers
  (the kit's standing meta-rule).

## Phase 6 — Report, then (on the operator's word) remediate

- Findings severity-ranked with page/file/line evidence, root cause, and a costed fix per finding;
  remediation is a separate explicit order.
- **Fix at the deepest reusable layer**: prefer a PARSER/toolchain fix over a content edit
  (2026-07-23: fixing bold-across-code in the generators healed the book WITHOUT touching the
  writer-owned manuscript, and heals every future book + translation at their next rebuild).
- Every fix ships with its gate: a regression-fixture case (defect construct → asserted output)
  AND/OR a verify_build check — and the gate gets a NEGATIVE TEST (it must FAIL on the pre-fix
  artifact before it may count as a guard).
- Rebuild via `produce_book.py` (or the §12 chain), then re-run Phase 2 + the defect-signature
  sweep + re-VIEW the fixed pages and covers. Known produce_book issue (2026-07-23, open): it can
  continue past a failed render and print green — read the step lines, not just the summary.
- Close the loop: EXECUTION_LOG (timeline table: action → result), post-fix manifest, ledger
  entry, one kit commit, LESSONS_LEDGER rule(s) for anything new.

---

## The worked example (2026-07-23, for calibration)

344pp 6x9 white KDP hardcover + Kindle: 25+ live checks green; found F1 literal `**` (bold span
containing inline code — parser class, fixed in-kit + gated), F2 ebook cover 1600x2400 below the
2560 ideal (compositors bumped + `kindle_cover_within_kdp_spec` gate added), F3 spine band 1.1227
vs Amazon-stated 0.964 on an identical 14.538x10.417 canvas (text measured inside the 0.839 safe
area → Previewer note, no change), F4 front-matter order = by-design placeholder (documented),
F5 stale kindle-TOC doc (truth-synced), F6 housekeeping. Plus the Word-COM zombie chain
(LESSONS_LEDGER §3.7b) found and cured because the rebuild itself crashed. Total: one session,
zero manuscript edits, everything re-verified 14/14 + all_pass.
