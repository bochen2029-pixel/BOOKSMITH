# DELTA AUDIT — the SUPERSEDED Titanic `PRODUCTION_LESSONS_LEARNED.md` vs. the kit ledger

**Scope of THIS pass (distinct from `_delta_production_lessons.md`):** a full read of the *older, ledger-declared **superseded*** production doc (2026-04-20, "The Night Was Young"), specifically to (1) find any lesson it carries that the newer ASTRA canon + the ledger **DROPPED**, (2) **confirm which of its numbers are stale / known-wrong** so they are never reintroduced, and (3) avoid re-deriving what the prior delta already covered.
**Anchored date:** 2026-07-12 03:15 CDT (Sunday); TZ Central Daylight (`Get-Date` at audit time).
**Auditor:** subagent, OPUS-class, read-in-full (not grep).
**Ledger read:** `docs/LESSONS_LEDGER.md` §1–§18 (726 lines), full.

## Sources read IN FULL this pass
| Path | Lines / bytes | MD5 | Identity |
|---|---|---|---|
| `C:\Claude-Titanic\PRODUCTION_LESSONS_LEARNED.md` | 310 / 19022 | `48a52e06…` | the 2026-04-20 "Night Was Young" doc; ledger §7/§13#7 = **SUPERSEDED** |
| `C:\BOOK\_tools\PRODUCTION_LESSONS_LEARNED.md` | 310 / 19022 | `48a52e06…` | **byte-identical** to the above |
| `C:\BOOK3\_tools\_titanic_source\PRODUCTION_LESSONS_LEARNED.md` | 310 / 19022 | `48a52e06…` | **byte-identical** to the above |

### ⚠ CRITICAL IDENTITY FINDING — all three targets are ONE file, already partly audited
All three paths hash to **`48a52e060133b88b2be8ba32511c178b`** (verified `md5sum` this pass). This is the **same MD5** the prior `_delta_production_lessons.md` recorded for `C:\BOOK3\_tools\PRODUCTION_LESSONS_LEARNED.md` **and** `C:\AI_BOOK\_tools\PRODUCTION_LESSONS_LEARNED.md` (that delta's source table, row 2–3: "`48a52e06…` both — same file mirrored", +0.302 old). So the "three not-yet-audited copies" named in this task are **byte-identical to the doc the prior delta already diffed as BOOK3≡AI_BOOK.** There is exactly ONE superseded source, mirrored across ≥5 repos (Claude-Titanic, BOOK/_tools, BOOK3/_tools/_titanic_source, BOOK3/_tools, AI_BOOK/_tools).

**Consequence for overlap:** the prior delta already handled this doc's *content* deltas against the ledger (categories, spine-side pad, methodology layer, etc. — its D1–D15). To avoid re-emitting them, THIS delta focuses on what that pass did **not** foreground: the **DROPPED-lesson question** and a **hardened STALE-NUMBERS list** with the operative-form corrections, since this file is the *origin* of the stale numbers the ledger warns against. Content deltas already in the prior file are cross-referenced, not repeated.

---

## PART A — STALE / KNOWN-WRONG NUMBERS IN THIS DOC (the do-NOT-reintroduce list)

*Every value here is verbatim from the superseded doc with its line number, the ledger's current/correct value, and the arithmetic. These are the numbers a future maintainer must NOT copy back in "from the canonical source."*

### S1. `+0.302"` hardcover board-add — **KNOWN-WRONG / SUPERSEDED** — severity HIGH
- **Doc says (verbatim):** L41 *"KDP hardcover adds: `+ 0.302"` for the case boards"*; L79 *"+0.302" for the board thickness"*; L232 (script table) *"0.708" wrap, +0.302" board"*; L267 *"Spine with boards = `pages × 0.0025 + 0.302` (cream) or `pages × 0.002252 + 0.302` (white)"*.
- **Ledger status:** SUPERSEDED. Ledger §5.3 + §13#1 name `0.302` explicitly as *"legacy, known-wrong, caused v1 rejections."* Current safe default = **white × 0.002252 + 0.348** (then Previewer-calibrate `SPINE_OVERRIDE_IN` per page-band).
- **DO NOT reintroduce `0.302` as the board-add.**

### S2. 186pp HC spine `0.767"` derived as **CREAM+0.302** — **latent-regression TRAP** — severity HIGH
- **Doc says (verbatim):** L81-83 *"So a 186-page **cream** book: … Hardcover wrap: 14.183" × 10.416", spine **0.767"**"*; L114 *"The spine at 186 pages is only 0.767" wide (KDP hardcover)"*.
- **Arithmetic (re-derived this pass):** cream 186pp = `186×0.0025 + 0.302 = 0.465 + 0.302 = 0.767` ✓ — but **HC is WHITE-only** (ledger §5.2/§9.2). The *number* 0.767 is right; the *paper + board* that produced it are both wrong. Operative form = **white 186pp = `186×0.002252 + 0.348 = 0.4189 + 0.348 = 0.767`.**
- **Why it's a trap:** identical output (0.767) makes the wrong derivation look validated. This doc is the **origin** of the "reconcile toward cream" hazard the prior delta flagged as D1. The reverse-derive ground truth is `stated_wrap_width − 12 − 1.416 = 14.183 − 13.416 = 0.767`.
- **Ledger status:** ledger §5.5/§13#1 already pins white+0.348→0.767 correctly; prior delta D1 asks for a footnote. **This doc is why that footnote matters — do not port its cream framing.**

### S3. `pages × 0.002252 + 0.302` (white variant) — **ARITHMETICALLY BROKEN number** — severity HIGH
- **Doc says (verbatim):** L267 gives the white board formula as `pages × 0.002252 + **0.302**`.
- **This is wrong even on its own terms:** white 186pp with +0.302 = `0.4189 + 0.302 = 0.721"`, which is neither the validator's 0.767 nor any shipped value. The doc's own cream example (0.767) and this white formula (0.721) **disagree by 0.046"** for the same book. The correct white constant is **0.348** (0.4189+0.348 = 0.767). This is a distinct defect from S1 (which is cream): the doc ships a white-HC formula that yields a rejected spine.
- **DO NOT reintroduce `0.002252 + 0.302`.** Correct = `0.002252 + 0.348` (Previewer-calibrated per band).

### S4. HC wrap HEIGHT `10.416"` — **stale arithmetic; validator wants 10.417"** — severity MED
- **Doc says (verbatim):** L48 *"14.183" × 10.416""*; L83 *"14.183" × 10.416""*; L266 *"Height = `9 + (0.708 × 2) = 10.416""*.
- **The doc even contradicts itself:** its own rejection quote at L85 shows KDP's *expected* height as **10.417** (*"expected cover size is 14.183×10.417"*), while its formula prints **10.416**. This is exactly the `0.708×2` trap (ledger §13#2). Validator-canonical = **10.417** (hardcode).
- **DO NOT reintroduce `10.416` as the HC height.** Use `WRAP_H_IN = 10.417`.

### S5. Cream-paper hardcover instruction — **REJECTION-RISK convention** — severity MED
- **Doc says (verbatim):** L271 (Step 4, KDP HC upload) *"Upload docx for interior, **select cream paper**"*; L81 frames the worked HC book as "cream."
- **Ledger status:** ledger §5.2/§9.2 = **KDP hardcover is WHITE-only (cream not offered).** Selecting cream on an HC listing risks rejection and pairs with the wrong spine multiplier (0.0025 vs 0.002252).
- **DO NOT reintroduce "select cream paper" for KDP hardcover.**

### S6. KDP paperback gutter `0.5"/0.625"/0.625"/0.5"` — **WEAKER than the hardened default** — severity MED
- **Doc says (verbatim):** L89 *"KDP paperback uses tighter margins (**0.5"/0.625"/0.625"/0.5"**)"*.
- **Ledger status:** ledger §4.1 + §13#5 **raise the gutter to 0.75" (1080 DXA)** to absorb ~2.7pt justified-trailing-space + ~2pt italic side-bearing overshoot that trips "insufficient gutter" at 0.625" exact. This is a deliberate, documented hardening (prior delta Tier-4 flags it "do not revert to 0.625 per canon").
- **DO NOT reintroduce 0.625" as the paperback gutter.** Use 0.75".

**STALE-NUMBERS QUICK LIST (never reintroduce):** `0.302` board-add · cream-derived `0.767` framing · white `0.002252 + 0.302` (=0.721, broken) · `10.416` HC height · "select cream paper" for HC · `0.625"` PB gutter.

---

## PART B — LESSONS THIS SUPERSEDED DOC HAS THAT THE NEWER CANON + LEDGER **DROPPED**

*The core task question: does the OLD doc preserve anything the newer canon lost? Read-in-full verdict: the ledger is a strict superset of this doc's mechanical content EXCEPT the four operational/procedural items below. None are numeric gotchas; all are "how-to-ship" procedure that the grep-built ledger thinned.*

### B1. The explicit "clone-from-Kindle-docx to build a print docx" bootstrap — DROPPED — severity LOW→MED
- **Doc has (verbatim, L245-252, Step 1):** a full procedure for when a **Kindle docx already exists and print does not** — clone `generate_book_kdp.js`, point it at the part markdown, add print furniture (page numbers, mirror margins, recto starts, front matter), output `*_KDP.docx`. *"The Kindle docx has no page numbers, no mirror margins … For print you need: Page numbers (outside corners, not on Part openers), Mirror margins …, A recto start for each Part, Front matter."*
- **Ledger has:** the canonical build order (§12/§10.4) assumes you generate ALL formats from the version-pinned markdown master. It does **not** cover the "Kindle-shipped-first, now retrofit print" bootstrap as a named path. Given ledger §7.5 explicitly says *"ship Kindle first"*, the retrofit-print-from-existing-Kindle case is a real workflow the ledger leaves implicit.
- **Bake-in (LOW):** ledger §12 — one advisory line: *"If a Kindle shipped before print exists, still regenerate print from the version-pinned markdown master (not from the Kindle docx); the markdown is the single source (§2.8). The Kindle docx lacks page numbers / mirror margins / recto starts / front matter by design."* (This both preserves the old doc's intent AND redirects it to the anti-drift keystone.)

### B2. The Python word-count parity SNIPPET (python-docx, not a named tool) — DROPPED as inline code — severity LOW
- **Doc has (verbatim, L210-218 + L281-285):** a drop-in `python-docx` parity check — `sum(len(r.text.split()) for para in d.paragraphs for r in para.runs)` across Kindle vs hardcover docx, with the rule *"Kindle may be slightly HIGHER (About-the-Author); if LOWER, some revision didn't cross — check the source markdown version in both generators."*
- **Ledger has:** the *rule* is fully present (§2.8, §7.3 name `kindle_parity_check.py` and the "never lower" invariant). Only the **runnable snippet** is dropped — fine, because the ledger points at a tool. **No bake-in needed; logged so a maintainer knows the snippet's provenance is this doc.** CONFIRMATION, not a gap.

### B3. `strip_blank_pages.py` **v1 AND v2** existed as twins — DROPPED the v2 mention — severity LOW
- **Doc has (verbatim, L235):** *"`strip_blank_pages.py` and `strip_blank_pages_v2.py` are utilities for trimming accidental blank pages that some generators emit."*
- **Ledger has:** ledger §8.1 references `strip_blank_pages.py` (single) as the legacy PyPDF2 path; the modern path is fitz-based. The existence of a **v2** twin is dropped — consistent with the ledger's "collapse N clones into one parameterized tool" philosophy (§3.1). **No bake-in; the ledger's single-tool stance supersedes the twin. Logged.** CONFIRMATION.

### B4. "Body pages ≠ printed pages — add front matter carefully" as an explicit caution — DROPPED phrasing — severity LOW
- **Doc has (verbatim, L53):** *"Body pages ≠ printed pages — add front matter carefully (half-title, title, copyright, dedication, epigraph, blank verso pages to keep Parts on recto)."*
- **Ledger has:** fully covered and deeper — §4.5 front-matter sequence, §4.3 recto via ODD_PAGE, §5.8 "PAGES re-derived from the generated PDF, never hardcoded." The old doc's caution is subsumed. **No gap. Logged as CONFIRMATION** (the ledger's re-derived-PAGES rule is the strict improvement).

**Verdict on the DROPPED question:** the only genuinely *droppable-and-worth-recovering* item is **B1** (the Kindle→print retrofit path), and even that is best re-expressed as a pointer back to the markdown master rather than the doc's "clone from the Kindle docx" instruction (which would invite source-drift, the very bug ledger §2.8 exists to kill). B2–B4 are inline code / tool-twins / cautions the ledger already covers better. **Nothing mechanically load-bearing was lost in supersession.**

---

## PART C — CONFIRMATIONS (short) — this doc corroborates ledger rules; recorded so a future pass doesn't "re-discover" them

- **Mixam filename keyword routing** (doc L59-73, full table) == ledger §11.3. Verbatim match incl. `back` alone → interior body, `back_cover/rear_cover/outer_back_cover` → back cover, `inner_` → body, `spine` → spine. ✓
- **KDP HC 0.708" WRAP is turn-in, not bleed** (doc L36, L47) == ledger §5.1. "single most common KDP hardcover error." ✓
- **Rejection string** *"expected cover size is 14.183×10.417 but the submitted file size is 12.713×9.250"* (doc L85) == ledger §5.1 verbatim. ✓ (Note the validator height in the quote is **10.417**, confirming S4.)
- **Word COM is the only reliable docx→PDF** (doc L95-110, snippet) == ledger §10.1. ✓
- **Spine font floor `int(spine_px × 0.42)` + weight 700 + double-draw +1px** (doc L114-123) == ledger §6.4 / §16.1. ✓ (Ledger §16.1 goes deeper: blank-below-0.0625" + 0.55 legible fill.)
- **Typography ≥ bleed+0.25" (Mixam 1.05 / KDP-PB 0.375 / KDP-HC 0.958); "BO CHEN" trimmed at 0.74"** (doc L125-129) == ledger §5.7. ✓
- **Preserve source art, re-composite from source** (doc L151-158) == ledger §6.4. ✓
- **Image discipline — never inline in chat; a prior session DIED** (doc L160-168) == ledger §10.2/§10.3. ✓
- **Kindle print-furniture-forbidden table** (doc L178-192) == ledger §7.1/§7.2. ✓
- **G12 parser asymmetry (backticks before italics)** (doc L198) == ledger §3.3. ✓
- **G13 source-version drift → Kindle 8,476 words short** (doc L200) == ledger §2.8/§7.3 (the ledger's headline anti-drift example). ✓
- **G14 Kindle updates don't auto-push to existing buyers** (doc L202) == ledger §7.5. ✓
- **G15 math needs explicit Cambria Math font** (doc L204) == ledger §7.3/§3.9. ✓
- **Digital PDF: crop Mixam covers bleed→trim `BLEED_PX = int(0.80×300)=240`, PyPDF2 concat** (doc L140-149) == ledger §8.1 (legacy path). ✓
- **Page-count multiples KDP ×2 / Mixam ×4** (doc L50-53) == ledger §4.4. ✓
- **Fonts at `C:\Claude-Titanic\fonts\`, Cormorant variable weight-axis 300–700** (doc L303) — this is the **portability LANDMINE** ledger §11.2 fixes (repo-relative fonts). The doc *embodies* the hard-coded cross-repo path; ledger correctly supersedes it. ✓ (do NOT port the absolute path.)

---

## PART D — OVERLAP WITH THE PRIOR `_delta_production_lessons.md` (explicit, to prevent double-baking)

The prior delta diffed this same file (as BOOK3≡AI_BOOK, +0.302). Items it ALREADY raised that also arise from this doc — **do not re-bake, they are queued there:**
- Board-add supersession 0.302→0.348 + page-count-band dependence → prior **D1 / Tier-4** (and my S1/S2 sharpen the *cream-origin trap* — same fix, this doc is the origin).
- HC height 10.416 vs 10.417 → prior **D2** (my S4 confirms with this doc's self-contradiction at L85).
- "Add a hardcover to the existing Kindle title — Amazon links them" (doc L270) → prior **D7** (add-format-not-new-title). ✓ same.
- Mixam premium version deferral / "KDP HC quality is good now" (doc L275-276) → prior **D8** neighborhood (Mixam premium knobs).
- Gutter 0.625 vs hardened 0.75 → prior **Tier-4** "do not revert." My **S6** restates as a stale-number-not-to-reintroduce.

**NET-NEW in this pass (not in the prior delta):** (a) the **three-way byte-identity** of the task's named targets to the already-audited BOOK3/AI_BOOK file; (b) the consolidated **STALE-NUMBERS do-not-reintroduce list** (S1–S6) with the **broken white `0.002252+0.302`=0.721** defect (S3) — which the prior delta did not isolate; (c) the **DROPPED-lesson analysis** (B1–B4), answering this task's specific question, with the finding that only B1 is worth recovering and only as a pointer to the markdown master.

---

## PRIORITIZED BAKE-IN (this pass only; highest first)
1. **S1/S2/S3 (HIGH)** — ledger §5.5 footnote: *"The superseded Titanic doc derives 186pp HC spine as cream+0.302=0.767; HC is white-only, operative = white×0.002252+0.348=0.767. Its white formula `×0.002252+0.302`=0.721 is broken. Never reintroduce 0.302 or the cream framing."* (Sharpens prior D1 with the origin + the broken-white number.)
2. **S4 (MED)** — already ledger §13#2; add the provenance note that the superseded doc's own rejection quote (10.417) contradicts its formula (10.416).
3. **S5/S6 (MED)** — reinforce ledger §9.2 (HC white-only) + §4.1 (0.75 gutter) with a one-line "superseded-doc says cream/0.625 — do not port."
4. **B1 (LOW)** — ledger §12 advisory: retrofit print from the markdown master, not from a shipped Kindle docx.

## Meta-observation
This file is the **taproot of the ledger's stale numbers** — the 0.302 board-add, the cream-HC framing, the 10.416 height, the 0.625 gutter all originate here and are all correctly superseded by the ASTRA canon + the ledger's hardenings. The task's three "not-yet-audited copies" are one file mirrored; the real deliverable of this pass is not new lessons but a **hardened do-not-reintroduce fence** around the values a maintainer would most plausibly copy back when reading a file that still *looks* authoritative (it is self-contained, confident, and shipped four formats). The one recoverable dropped lesson (B1) is best re-expressed as a pointer to the anti-drift keystone. A READ (not a grep) is what surfaced the self-contradiction at L85 and the broken white formula at L267.

---
*Audit written 2026-07-12. Three named targets confirmed byte-identical (`md5sum`) to each other AND to the prior delta's BOOK3/AI_BOOK source (`48a52e06…`). All S1–S4 arithmetic re-derived this pass. Source read in full, not sampled.*
