# DELTA AUDIT — Titanic `reference_*.md` memory files vs. LESSONS_LEDGER.md

*Anchored 2026-07-12 02:57 -05:00 (Sunday, Central). Auditor read the current ledger `C:\BOOKSMITH\docs\LESSONS_LEDGER.md` in FULL (§1–§17) and the seven assigned reference files in FULL. This is a DELTA report: facts/numbers/procedures present in the reference files but MISSING, WEAKER, or CONTRADICTED in the ledger. Confirmations (things the ledger already has right) are listed at the end so the diff is honest.*

**Headline:** The ledger already absorbed the bulk of these seven files — they are its source material, distilled into §3, §4, §5, §7, §10, §11, and the §13 conflicts table. Most files are ~90–100% covered. The genuine deltas are small, specific, and mostly **verification-technique / exact-coordinate / edge-case** facts that the ledger paraphrased away or omitted. Nothing here contradicts the ledger's numbers; the deltas ADD precision or a missing check.

---

## FILE 1 — `reference_docx_mirror_margins_gotcha.md`

**Ledger coverage:** §3.4 (mirror-margins JSZip injection), §4.1 (0.75" gutter rationale), §13.5 (gutter conflict). Strong coverage.

### DELTA 1.1 — The exact charbox overshoot MEASUREMENTS are absent
- **Lesson (verbatim, file lines 83–85):** "Verso text right edge lands at 42.3pt (instead of 45pt) → trailing space extended ~2.7pt. Recto italic `f` renders at L=43.1pt (instead of 45pt) → side-bearing overshoot ~2pt."
- **Ledger has:** §4.1 states the *magnitudes* ("~2.7pt trailing-space + ~2pt italic side-bearing") and §3.4 names the pypdfium2 charbox scan, but NOT the concrete pt-landing values (42.3pt / 43.1pt vs the 45pt = 0.625" edge) that let you interpret a scan result as pass/fail.
- **Bake-in:** Add the two measured landing values to §3.4's Verify block as the reference numbers a `get_charbox()` scan is compared against (edge=45pt at 0.625"; overshoot lands at 42.3/43.1pt). Low priority — precision, not a new rule.

### DELTA 1.2 — The dark-column scan uses a specific 1.5× scale and named page indices
- **Lesson (file lines 60–74):** verification renders **pages 49–50** (a verso/recto pair) at **scale=1.5** and expects verso `left=54px,right=67px` / recto `left=67px,right=54px`, with the **13px** delta = the 0.125" gutter-vs-outside difference.
- **Ledger has:** §3.4 Verify DOES carry the 54/67px pattern and the 13px note — **covered.** The only sub-delta is that the ledger doesn't state the render `scale=1.5` explicitly inside §3.4 (it's implied). Trivial.
- **Bake-in:** none required (already in §3.4). Noted for honesty.

**Verdict:** File 1 is ~95% covered. Only DELTA 1.1 (the 42.3/43.1pt landing values) is a real, if minor, missing datum.

---

## FILE 2 — `reference_docx_valign_injection.md`

**Ledger coverage:** §3.6 (vAlign JSZip injection), §4.5. Strong.

### DELTA 2.1 — `w:val` accepts a FOURTH value: `both` (justified vertical fill)
- **Lesson (file line 59):** "w:val accepts: `top` (default), `center`, `bottom`, `both`."
- **Ledger has:** §3.6 lists only `center|bottom` (and mentions `top` as the body default). **`both` is absent.**
- **Bake-in:** §3.6 — add `both` to the documented `w:val` enum (vertical justification, spreads content to fill the page). Minor completeness fix; `both` is rarely wanted for book pages but belongs in the reference.

### DELTA 2.2 — Explicit "when NOT to use" boundary
- **Lesson (file lines 84–86):** "Body content pages should top-flow normally. Don't use vAlign on chapter pages."
- **Ledger has:** §3.6 says "NEVER on body pages (they must top-flow)." **Covered** — same rule, ledger states it.
- **Bake-in:** none.

**Verdict:** File 2 is ~98% covered. Only DELTA 2.1 (`both` enum value) is a genuine omission.

---

## FILE 3 — `reference_image_2000px_limit.md`

**Ledger coverage:** §10.3 (2000px cap + `resize_image_safe.py`), and the CLAUDE.md image-discipline block. Very strong.

### DELTA 3.1 — The error is NON-RECOVERABLE WITHIN THE SESSION (must skip the image or start a new session)
- **Lesson (file lines 9–10):** "The error is non-recoverable within the session — you have to either skip that image or start a new session."
- **Ledger has:** §10.3 says the oversize image "aborts the conversation non-recoverably" and quotes the error string — **covered.** The actionable remedy ("skip it OR start a new session") is implied but not spelled out.
- **Bake-in:** §10.3 — one clause: on a hit, the only recoveries are skip-the-image or new-session (no in-session retry). Minor.

### DELTA 3.2 — The `_r2k` suffix naming convention + LANCZOS + echo-unchanged behavior
- **Lesson (file lines 17, 31–32):** resizes into a 2000² box with **PIL LANCZOS**, saves with a **`_r2k` suffix**, and **deliberately echoes the original path unchanged** when ≤2000px so the tool is safe to run unconditionally.
- **Ledger has:** §10.3 carries `_r2k` suffix, LANCZOS-into-2000² box, and "echoes the path unchanged … safe to run unconditionally." **Fully covered.**
- **Bake-in:** none.

### DELTA 3.3 — Screenshot tools named as the recurring source (Snipping Tool / Greenshot, high-DPI → 2400px+)
- **Lesson (file lines 11–12, 28):** high-res screenshots from Windows Snipping Tool / Greenshot on high-DPI displays "often produce 2400x+ images"; watch `C:\Users\user\Desktop\___greenshots\`.
- **Ledger has:** §10.3 names cover wraps (4255×3125 / 3801×2775) as the trip source but NOT the screenshot-tool provenance or the specific greenshots dir.
- **Bake-in:** §10.3 or §10.2 — add screenshots (Snipping Tool/Greenshot, 2400px+ on high-DPI) as a second common trip source alongside cover wraps, and the `___greenshots\` watch-dir. Minor; useful for anyone doing perceptual spot-checks from a screenshot.

**Verdict:** File 3 is ~97% covered. Deltas are small clarifications only.

---

## FILE 4 — `reference_kdp_print_recto_enforcement.md`

**Ledger coverage:** §4.3 (ODD_PAGE per chapter + trailing EVEN_PAGE), §4.4, §3.5, §3.7, §10.1. Very strong.

### DELTA 4.1 — The EVEN_PAGE trailing-blank parity logic has a subtle documented case-analysis (and a self-caught confusion)
- **Lesson (file lines 124–129):** spells out BOTH branches: if the last chapter ends on **odd** page N → EVEN_PAGE blank lands on N+1 → total even; if it ends on **even** page N → the odd N+1 is skipped-with-a-blank, blank content on N+2 → total even. The file even flags its own mid-note confusion ("wait, we used EVEN_PAGE not ODD_PAGE here") and resolves it. Conclusion: "Either way: even total. No empirical tuning needed."
- **Ledger has:** §4.3 states the trailing EVEN_PAGE gives even parity and "survives markdown edits" but does NOT carry the two-branch case analysis proving WHY it's always even.
- **Bake-in:** §4.3 — add the one-line case analysis (odd-N→+1; even-N→+2; both even) as the justification. Low priority — the rule is right; this is the proof behind it.

### DELTA 4.2 — The trailing blank in THIS file uses a `TextRun({text:""})`, which §3.5 later CORRECTS to a truly-empty paragraph
- **Lesson (file lines 53–55, 116–122):** the trailing EVEN_PAGE child is `new Paragraph({ children: [new TextRun({ text: "" })] })`.
- **Ledger has:** §3.5 (correctly) supersedes this: "make the trailing blank a truly empty `new Paragraph({})`, NOT a Paragraph with an invisible size-2 white TextRun (even an invisible run can trip the rejection)." So the ledger is **STRONGER** than File 4 here.
- **Bake-in:** none — this is a case where the ledger already improved on the reference. Recorded so the diff is honest (the reference's own code snippet is the weaker version).

### DELTA 4.3 — Footer page-number color/size specifics (`size:18, color:"888888"`)
- **Lesson (file lines 61–76):** `pageNumberFooters()` renders `PageNumber.CURRENT` at `size: 18, color: "888888"`, RIGHT-aligned default (recto/outer), LEFT-aligned even (verso/outer).
- **Ledger has:** §4.3 describes the RIGHT/LEFT outer-edge alignment logic but NOT the `size:18 color:888888` styling. NOTE: §16.2 later OVERRIDES the alignment to bottom-**center** as house style — so the outer-edge alignment from File 4 is superseded for Bo's house, but the color/size detail is still useful and unrecorded.
- **Bake-in:** §4.3 — record the footer run styling (`size:18`=9pt, `color:888888` grey) as the default page-number style, cross-referencing §16.2 for the center-vs-outer alignment override. Minor.

**Verdict:** File 4 is ~95% covered; the ledger is actually stronger than the reference on the trailing-blank fix (DELTA 4.2). Only the parity case-analysis (4.1) and footer styling (4.3) are minor missing details.

---

## FILE 5 — `reference_kdp_trailing_blank_inheritance_gotcha.md`

**Ledger coverage:** §3.5 (empty Header/Footer objects; the "margin=0 is the WRONG fix" trap). Very strong — this file is the direct source of §3.5.

### DELTA 5.1 — Word inherits headers/footers FORWARD, and the section AFTER a body section is highest-risk (mechanism stated explicitly)
- **Lesson (file lines 12–16, 60–62):** the mechanism — "Word inherits headers and footers from the **previous section** when the current section doesn't specify them … Sections immediately after a body section are most at risk because Word inherits forward."
- **Ledger has:** §3.5 says "Sections immediately after a body section are highest-risk (Word inherits forward)." **Fully covered.**
- **Bake-in:** none.

### DELTA 5.2 — The complete per-section checklist for "which sections need `emptyHeadersFooters()`"
- **Lesson (file lines 54–62, 83–91):** enumerated list — Front matter section, TOC section, **Reader's note / preface section (anything before the body)**, Trailing EVEN_PAGE blank. Plus a full "Quick checklist for any future KDP print interior" (8 items).
- **Ledger has:** §3.5 lists "front matter, TOC, preface/reader's-note, and the trailing EVEN_PAGE blank" — **covered.** The 8-item quick-checklist is effectively reproduced across §14's Interior block.
- **Bake-in:** none.

### DELTA 5.3 — WHY this recurred: the fix lived in `generate_book_*.js` and was never promoted to a `reference_*.md` (the meta-lesson)
- **Lesson (file lines 78–80):** "Past sessions for *The Night Was Young*, *The City and the Girl*, *The Second Notebook*, and *The Autotelic Disposition* all hit this and fixed it inline, but the fix was buried in `generate_book_*.js` files without a dedicated reference. The fix was correct but the lesson never got promoted."
- **Ledger has:** §10.5 states the general meta-rule ("a fix rediscovered ≥3× MUST be promoted to a persistent reference … inline fixes die with the project"). **The general principle is covered**; the four specific book names that hit THIS bug are not recorded against §3.5.
- **Bake-in:** §3.5 — a parenthetical "(hit inline by Night Was Young / City and the Girl / Second Notebook / Autotelic Disposition before promotion)" to reinforce it as a ≥4× rediscovery. Trivial provenance.

**Verdict:** File 5 is ~98% covered — this file essentially IS ledger §3.5. No substantive delta.

---

## FILE 6 — `reference_latex_unicode_converter.md`

**Ledger coverage:** §3.9 (LaTeX→Unicode ordering), §7.3 (Cambria Math tag). Strong on the ORDERING; **WEAKER on the exact Unicode glyph-coverage tables** — this is the biggest real delta set in the whole audit.

### DELTA 6.1 — The EXACT subscript-coverage table (which chars HAVE Unicode subscripts, which are MISSING) is absent
- **Lesson (verbatim, file lines 33–34):** "Subscripts have Unicode forms for: 0-9, +, -, =, (, ), a, e, h, i, j, k, l, m, n, o, p, r, s, t, u, v, x. **Missing: b, c, d, f, g, q, w, y, z and all uppercase.** Unmapped chars pass through at normal size."
- **Ledger has:** §3.9 says "subscripts `_{...}` BEFORE fractions" and names `_{\max}`→`ₘₐₓ`, but does NOT list WHICH characters can/can't be subscripted. This is load-bearing: it tells you in advance which subscripts will render correctly and which silently fall back to full-size (a visual inconsistency you must anticipate).
- **Bake-in:** §3.9 — add the subscript coverage table verbatim (present: 0-9 + - = ( ) a e h i j k l m n o p r s t u v x; MISSING: b c d f g q w y z + all uppercase). Medium priority for math books.

### DELTA 6.2 — The EXACT superscript-coverage table is absent
- **Lesson (verbatim, file line 37):** "Superscripts: 0-9, +, -, =, (, ), i, n, *. Missing most letters."
- **Ledger has:** §3.9 mentions "superscripts" as step 6 but lists no coverage. Absent.
- **Bake-in:** §3.9 — add: superscripts available for `0-9 + - = ( ) i n *`; most letters missing.

### DELTA 6.3 — The EXACT `\dot{}` precomposed-glyph coverage table is absent
- **Lesson (verbatim, file line 39):** "`\dot{X}` precomposed coverage: A, B, C, D, E, F, G, H, M, N, O, P, R, S, T, W, X, Y, Z + lowercase. Missing: I, J, K, L, Q, U, V … fall back to letter + combining dot above (U+0307)."
- **Ledger has:** §3.9 names "`\dot{x}`→precomposed dot-above (ẋ, Ġ)" but not WHICH letters have a precomposed form and which fall back to U+0307 combining.
- **Bake-in:** §3.9 — add the `\dot{}` coverage (present: A-H, M-P, R-T, W-Z + lowercase; missing I J K L Q U V → combining U+0307 fallback).

### DELTA 6.4 — WHY subscripts-before-fractions (the concrete failing case)
- **Lesson (file lines 28–30):** "`\frac{K(t)}{K_{\max}}` — inner braces from `_{\max}` in denominator defeat `\frac{([^{}]*)}{([^{}]*)}` regex. Resolving subscripts first leaves `\frac{K(t)}{Kₘₐₓ}` which has no inner braces."
- **Ledger has:** §3.9 states the RULE ("subscripts before fractions so `_{\max}`→`ₘₐₓ` removes inner braces that would defeat the `\frac` regex") — **covered**, and even names the regex intent. Good.
- **Bake-in:** none — ledger has the reasoning.

### DELTA 6.5 — The acknowledged limitations list (what this converter CANNOT do)
- **Lesson (file lines 68–74):** `\frac` renders as `(a)/(b)` not a stacked bar; `\mathcal{P}`→italic `P` not script 𝒫; unmapped sub/superscripts render full-size; "Doesn't handle matrices, integrals with bounds, complex alignment. Use OMML or image-embed for those."
- **Ledger has:** §3.9 notes `\frac`→`(a)/(b)` implicitly via the step-7 mapping, but does NOT carry the explicit "cannot do matrices / bounded integrals / complex alignment → fall back to OMML or image-embed" boundary.
- **Bake-in:** §3.9 — add a one-line "OUT OF SCOPE (use OMML/image): matrices, integrals-with-bounds, complex alignment; `\mathcal`→italic not script." Medium priority — tells a math-book run when to STOP using this path.

### DELTA 6.6 — `fixProseSubscripts()` is safe-before-math-splitting because math uses `\Omega` not literal Ω
- **Lesson (file lines 45–46):** "Safe to apply to prose before math-splitting because math uses `\Omega` (backslash escape), not direct Unicode Ω."
- **Ledger has:** §3.9 names `fixProseSubscripts()` and the `[Greek]_word` prose case but not the SAFETY reasoning (why it can run before the `$...$` split without corrupting math).
- **Bake-in:** §3.9 — half a line: prose-subscript pass runs first safely because in-math Greek is backslash-escaped (`\Omega`), so the pass can't touch it.

**Verdict:** File 6 is the LEAST-covered file — ~70%. The ledger has the pipeline ORDER but dropped the three exact Unicode coverage tables (6.1/6.2/6.3), the out-of-scope boundary (6.5), and two reasoning notes. These matter for any math/technical book because they predict which glyphs render and when to switch to OMML.

---

## FILE 7 — `reference_mixam_hardcover_pipeline.md`

**Ledger coverage:** §5.1 (0.80" bleed), §5.4 (non-constant board add), §5.5 (panel dims), §11.3 + §5.7 (filename routing), §4.4 (÷4 padding), §6.4 (spine layout). Very strong.

### DELTA 7.1 — The four-panel Mixam cover dimensions stated as concrete inches (front/back = 7.60"×10.60"; spine = (spine+1.60")×10.60")
- **Lesson (file lines 11–18):** front cover **7.60" × 10.60"**, back cover **7.60" × 10.60"**, spine **(spine_width + 1.60") × 10.60"** — trim 6×9 + 0.80" bleed all sides.
- **Ledger has:** §5.5 carries "front & back `7.60"×10.60"`, spine `(spine+1.60")×10.60"`" — **fully covered.**
- **Bake-in:** none.

### DELTA 7.2 — The spine cap-height worked example (0.28 ratio → 124px ≈ 21pt at a 1.48" spine)
- **Lesson (file lines 81–82):** "`spine_text_size = int(SPINE_W_IN * DPI * 0.28)` for a 1.48" spine produces 124px font (≈21pt) — fits the trim with margin."
- **Ledger has:** §6.4 carries "Mixam spine `int(spine_px × 0.28)`" and §16.1 the dynamic-font warning, but NOT the worked example (1.48" → 124px ≈ 21pt) that anchors what "0.28" produces at a real spine width.
- **Bake-in:** §6.4 or §16.1 — add the worked example as the calibration anchor for the 0.28 ratio. Reinforces §16.1's thin-spine clamp with a concrete "here's what it gives at 1.48"." Minor.

### DELTA 7.3 — The board-add empirical pair stated with the DERIVATION (204pp→0.67"→0.160; 548pp→1.48"→0.110)
- **Lesson (file lines 41–46):** "204 pp at 6×9 cream → 0.67" spine → board add ≈ **0.160"**; 548 pp → 1.48" spine → board add = **0.110"**." Plus first-build procedure: estimate `pages × 0.0025 + 0.16`, upload, read Mixam's actual spec, adjust, **regenerate spine only (front/back unaffected)**.
- **Ledger has:** §5.4 + §13.3 carry the 0.160@204pp / 0.110@548pp pair AND the "regenerate spine.pdf only" workflow AND the 548pp→1.48" back-solve. **Fully covered.** The `0.16` first-guess constant is in §12.7 / §5.4.
- **Bake-in:** none.

### DELTA 7.4 — "Word COM is the ONLY reliable converter" is asserted in File 7 as gotcha #5 with the specific failure modes for Mixam
- **Lesson (file lines 102):** "Word COM is the only reliable docx→PDF converter — Pandoc, LibreOffice, online services all produced bad PDFs (font substitution, broken TOC, mis-pagination)."
- **Ledger has:** §10.1 covers this globally with the same three failure modes. **Fully covered.**
- **Bake-in:** none.

### DELTA 7.5 — The full Mixam misroute table with EVERY variant (`back.pdf`→Body Page 1; `<title>.pdf` no `inner`→inconsistent/errors)
- **Lesson (file lines 22–32):** the complete table: `front_cover.pdf`✓ / `back_cover.pdf`✓ / **`back.pdf`→Body Page 1 (silent!)** / `spine.pdf`✓ / `inner_<title>.pdf`✓ / `<title>.pdf` (no `inner`)→inconsistent/errors. Rule: "Always use `inner_` prefix on body and `_cover` suffix on front/back."
- **Ledger has:** §11.3 + §5.7 carry the full routing table including bare-`back.pdf`→body and `<title>.pdf`-without-`inner`→inconsistent. **Fully covered.**
- **Bake-in:** none.

**Verdict:** File 7 is ~97% covered — the ledger's §5 + §11.3 + §13.3 absorbed nearly all of it. Only the spine worked-example (7.2) is a minor missing calibration anchor.

---

## SUMMARY OF ACTIONABLE DELTAS (ranked)

| # | Delta | Source file | Ledger now | Bake-in target | Priority |
|---|---|---|---|---|---|
| 6.1 | Subscript Unicode coverage table (have: 0-9 +-=() a e h i j k l m n o p r s t u v x; MISSING b c d f g q w y z + uppercase) | File 6 | absent | §3.9 | **MED** |
| 6.2 | Superscript coverage (0-9 +-=() i n *; most letters missing) | File 6 | absent | §3.9 | **MED** |
| 6.3 | `\dot{}` precomposed coverage (A-H,M-P,R-T,W-Z+lc; miss I J K L Q U V→U+0307) | File 6 | partial (2 examples) | §3.9 | **MED** |
| 6.5 | Out-of-scope boundary: no matrices / bounded integrals / complex alignment / `\mathcal`→italic → use OMML or image | File 6 | absent | §3.9 | **MED** |
| 2.1 | `w:vAlign` accepts a 4th value `both` (vertical justify) | File 2 | lists only center/bottom | §3.6 | LOW |
| 1.1 | Charbox overshoot landing values (verso 42.3pt / recto italic-`f` 43.1pt vs 45pt edge) | File 1 | magnitudes only | §3.4 Verify | LOW |
| 3.3 | Screenshots (Snipping Tool/Greenshot, 2400px+ high-DPI) as 2nd trip source; `___greenshots\` dir | File 3 | wraps only | §10.2/§10.3 | LOW |
| 7.2 | Spine 0.28-ratio worked example (1.48"→124px≈21pt) | File 7 | ratio only | §6.4/§16.1 | LOW |
| 4.1 | EVEN_PAGE parity two-branch proof (odd-N→+1; even-N→+2; both even) | File 4 | rule w/o proof | §4.3 | LOW |
| 4.3 | Page-number footer run style (`size:18`=9pt, `color:888888`) + xref §16.2 center override | File 4 | alignment only | §4.3 | LOW |
| 6.4/6.6/3.1/5.3 | Reasoning/provenance notes (subscript-before-frac case; prose-pass safety; non-recoverable remedy; 4 book names) | Files 3/5/6 | principle covered | inline parentheticals | TRIVIAL |

**The one cluster worth a real edit: §3.9 (LaTeX→Unicode).** File 6 is the only meaningfully under-absorbed file (~70%). The ledger kept the pipeline ORDER but dropped the three exact glyph-coverage tables and the out-of-scope boundary — precisely the facts that tell a math-book run *which* subscripts/superscripts/dots will render vs. silently fall back to full size, and *when to abandon* this path for OMML. Recommend appending a "§3.9a — Unicode math glyph coverage (the exact tables)" sub-entry.

Everything else is precision/provenance polish. No number in these seven files CONTRADICTS the ledger, and in one place (§3.5 trailing-blank = truly-empty paragraph, DELTA 4.2) **the ledger is already STRONGER than the reference file's own code snippet.**

---

## CONFIRMATIONS — things the ledger already captured correctly (honest diff)

- **Mirror margins (File 1):** `page.mirror:true` in docx@9.6.1 does NOT emit `<w:mirrorMargins/>` → JSZip-inject both `<w:mirrorMargins/>` + `<w:evenAndOddHeaders/>` into `settings.xml`, BETWEEN generator and Word-COM PDF. Verse/recto 54/67px + 13px delta verify. Gutter→0.75" (1080 DXA) to absorb ~2.7pt trailing-space + ~2pt italic side-bearing. → **§3.4, §4.1, §13.5. Full.**
- **vAlign (File 2):** two separate injectors (settings.xml vs document.xml); per-page sections required; `center` half-title/title, `bottom` copyright; never on body pages; pipeline order gen→mirror-inject→valign-inject→Word-COM→fitz-pad. → **§3.6, §4.5, §12. Full except the `both` enum value.**
- **2000px (File 3):** hard cap aborts the conversation; `resize_image_safe.py` LANCZOS-into-2000², `_r2k` suffix, echoes-unchanged-if-small, safe to run unconditionally; cover wraps always trip it. → **§10.3, §10.2. Full.**
- **Recto (File 4):** ODD_PAGE per chapter (Word auto-inserts blank verso) + trailing EVEN_PAGE blank; robust vs the naive hard-coded-blank-verso trick; first body section `pageNumbers:{start:1}`; `leadingPageBreak=false` for the first H1 of an ODD_PAGE section (avoids double-advance); mirror footers RIGHT=recto/LEFT=verso (outer); Word-COM `ComputeStatistics(2)` page count. → **§4.3, §4.4, §3.7. Full** (and §16.2 supersedes the outer-edge footer with center house style).
- **Trailing-blank inheritance (File 5):** Word inherits header/footer forward; `margin.header=0/footer=0` is the WRONG fix (only shrinks the zone, content still renders); real fix = explicit empty `Header`+`Footer` objects on every h/f-free section; verify each `header*.xml` shows `[]`; sections after a body section are highest-risk. → **§3.5. Full — this file IS §3.5**, and the ledger improved it (truly-empty paragraph, not an invisible TextRun).
- **LaTeX→Unicode (File 6):** the 8-step ORDER (strip \left/\right/\big → unwrap \text/\mathrm/\mathcal/\mathbb/\mathbf/\mathit → \dot precomposed → symbols longest-first → subscripts BEFORE fractions → superscripts → \frac→(a)/(b) → cleanup); WHY subscripts-before-fractions (`\frac{K(t)}{K_{\max}}` inner-brace defeat); `fixProseSubscripts()` for `Ω_ext`; Cambria Math italic runs; tool trio latex_to_unicode.js + check_docx_latex.py + find_latex.py. → **§3.9. Order fully covered** (coverage tables + scope boundary are the deltas).
- **Mixam (File 7):** 4 PDFs; 0.80" bleed all sides (case-board wrap, not 0.125"); front/back 7.60"×10.60", spine (spine+1.60")×10.60"; ÷4 padding via fitz (432×648pt blanks); board-add NON-constant (0.160@204pp / 0.110@548pp) → trust Mixam's calculator, regenerate spine-only; filename routing SILENT (`back.pdf`→Body Page 1; use `inner_`+`_cover`); spine title-only 0.28 ratio, build-horizontal-then-rotate-90; Word COM the only reliable converter. → **§5.1, §5.4, §5.5, §5.7, §11.3, §4.4, §13.3, §6.4. Full** except the 0.28 worked example.

*End of delta audit. Written to disk 2026-07-12.*
