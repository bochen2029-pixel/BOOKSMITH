# PLAN — QC remediation + live end-to-end proof (2026-08-16, evening)

**Operator directive:** log the plan → execute → append results honestly (success, failure,
lessons) no matter what. Companion: `cloud/QC_STOREFRONT_2026-08-16.md` (findings H1/H2/M1-M3).

## Objectives
1. **Prove the loop live TODAY** (last proof was 2026-08-13): a fresh $0 dev-adopt ticket,
   S-band (8 chapters), real DeepSeek spend (~$0.06, ceiling $10), ends in a **PDF downloaded**.
2. **Prove R2 durability**: the 3-day-old BR-SIM901 artifacts still fetchable straight from R2.
3. **Fix pre-launch findings** that touch ONLY the site worker + static assets (zero
   container/runner risk, lesson-16 safe): H2 (XSS), H1 (R2-first ready listing, + L6
   double-flip race), M1 (stage gates + reroll counting), M3 (.gitignore lines).
4. **Re-verify after deploy** using the fresh ticket + BR-SIM901 as regression fixtures.

## Steps
- **A. R2 durability probe (read-only).** `wrangler r2 object get` on BR-SIM901's archived
  PDF (key `tickets/BR-SIM901/outputs/digital/...`). Expect: bytes land, PDF opens.
- **B. Launch the live sim (baseline, BEFORE fixes).**
  1. D1: insert paid $0 order `BR-QC0816` (item `qc-sim`).
  2. `/api/dev/adopt` with DEV_KEY (from `cloud/worker/.dev_key`, var-name trap `DEVK=`,
     lesson 14; value never printed) → capture `br_sess` cookie.
  3. `/api/brief`: nonfiction, length **S** (8 ch × 1200w), innocuous QC-themed brief.
  4. `/api/outline` POST → poll GET until outline JSON (budget ~6 min).
  5. `/api/commit` → background poller on `/api/status` every 20s (cap 40 min) → expect
     `ready` + `archive 5/5`-ish receipt.
  6. Download the PDF (+ EPUB, DOCX) via `/api/download`; verify with fitz: page count,
     every page exactly 432×648 pt; sha256 recorded. Log the model-call ledger + est. cost.
- **C. Implement fixes locally while the build runs** (backups to
  `_backups/2026-08-16_qc-fix/` first):
  - H2: validate `?order=` against `^BR-[0-9A-Z]{6}$` before any innerHTML use (index.html).
  - H1: `apiStatus` — `ready` lists from R2 (runner-fallback only if R2 empty), `stalled`
    static; terminal stages never wake a container. + L6: building→ready flip conditional
    (`AND stage='building'`, act on `changes>0`) so mail/archive fire once.
  - M1: brief/intake/outline allowed only in `briefing|outlining|outline_ready`; commit only
    in `outline_ready`; outline calls in `outlining|outline_ready` count as rerolls (note or
    not) against MAX_REROLLS=3; first call (briefing) free.
  - M3: .gitignore += `cloud/worker/.dev_key`, `cloud/worker/.test_cookies`, `cloud/_receipts/`.
- **D. Deploy site worker** (after baseline artifacts are downloaded): wrangler deploy from
  the bookraising config. No container touch.
- **E. Post-deploy verification battery** (all read-only or 4xx-expected):
  1. H1 fixture #1: BR-SIM901 status → `ready` + outputs listed FROM R2 (container long dead).
  2. H1 fixture #2: BR-QC0816 status → same, fast, no container wake.
  3. Re-download the QC PDF → sha256 must equal the pre-deploy download.
  4. M1 negatives on the ready QC ticket: outline POST → 4xx; brief POST → 4xx; commit → 4xx.
  5. H2: served homepage source contains the guard; crafted `?order=<img...>` produces no
     injection (source-level check; optional browser spot-check).
  6. Sanity: homepage 200; wrong coupon 403.
- **F. Append RESULTS below + update QC doc statuses + BUILD_LOG.md entry.** No git commits
  (operator commits; many unrelated modified files in the worktree).

## Risks / rollback
- Sim may fail (3 days of drift: key validity, image pull, platform). That is itself the
  test — log the exact failure, fix or escalate, still proceed with C/D (independent).
- Deploy regression → redeploy from `_backups/2026-08-16_qc-fix/` (2 min).
- D1/R2 changes are additive only (one order row + archived artifacts; kept as fixtures).
- Known accepted: M2 (runner fail-open) + shim busy-gates + L10 ride the NEXT image lap.

---

# RESULTS (execution ran 2026-08-17 ~09:30-10:00 CT; all objectives met)

## A. R2 durability — PASS
`wrangler r2 object get` pulled `tickets/BR-SIM901/outputs/digital/br_sim901_DIGITAL.pdf`
(541,836 B) — SHA256 `7034529d44fef0d33cf2d2ade521b56610c773ff66df2bce8c97a8fef6e89a41`,
**byte-identical to the sha recorded in BUILD_LOG on 2026-08-13**. Three days cold, intact.
(`wrangler r2 object list` does not exist in 4.122.0 — get-by-key only.)

## B. Live end-to-end sim — PASS (the loop is green TODAY, PDF proven)
Ticket **BR-QC0816** ($0 dev lane, no coupon burned): D1 order → dev-adopt → brief
("A Small Proof", nonfiction, S) → outline **8 units exactly on band** → commit →
**build rc 0 in 364.9 s (~6 min)**, 18/18 stages: 8 chapters drafted (1,319-1,682 w each,
one attempt each), lint clean, assemble 11,601 w, kindle + epub + digital_pdf produced,
`verify` green for all 3, emit. **R2 archive 5/5, err null** (lesson-15 in-band receipt).
Ledger: **9 model calls, 25,026 in / 14,080 out tokens ≈ $0.02** (DeepSeek v4-pro, worst-case
rates). Downloads via `/api/download` (R2-first): PDF 424,835 B, EPUB 308,398 B, DOCX
29,649 B, cover JPG 297,768 B → `cloud/_receipts/qc_sim_2026-08-16/`.
**fitz verification: 31 pages, every page exactly 432×648 pt (true 6×9), sha
`87567fbeec649de847e71cebab7f8c79f439b259f6d9facde33b9cfa3e31bf7f`.**

## C+D. Fixes implemented and DEPLOYED — site worker version `90723bd7-65bd-405d-aa0b-bfda5e02bf85`
H2 XSS guard (index.html) · H1 R2-first terminal-stage status + runner-fallback
(worker.js) · L6 one-winner conditional flip · M1 stage gates (brief/intake/outline/commit)
+ note-less reroll counting (counted only on 202) · `{{TEMPLATE}}` scrub in apiOutlineGet ·
M3 gitignore (verified with `git check-ignore`: `.dev_key`, `.test_cookies`, `_receipts/`
all ignored now). `node --check` clean. Backups: `_backups/2026-08-16_qc-fix/`.

## E. Post-deploy battery — ALL PASS
| Check | Result |
|---|---|
| H1 fixture BR-SIM901 (container dead 3 days) | **PASS** — `stage:ready, source:r2, 5 outputs`, zero retries |
| H1 fixture BR-QC0816 | **PASS** — same, listed from R2 |
| PDF re-download sha vs pre-deploy | **PASS** — identical |
| M1 negatives on ready ticket (outline/brief/commit) | **PASS** — all 409 (see lesson below) |
| H2 guard in served homepage source | **PASS** — regex present |
| Sanity (wrong coupon 403, homepage 200) | **PASS** |

## Failures & lessons (the honest column)
1. **DEV_KEY semantics (lesson-14 addendum):** first dev-adopt got 403 because the deployed
   secret is the dotfile's ENTIRE content INCLUDING the `DEVK=` prefix (27 chars) — the
   lesson-14 recipe `printf '%s' "$(tr -d ' \r\n' < file)"` strips whitespace only. Parsing
   out the "value" after `=` (22 chars) breaks auth. **The file bytes ARE the secret.**
2. **Stale-isolate propagation, reconfirmed live:** seconds after `wrangler deploy`, the M1
   brief-negative hit an OLD-version isolate and returned 200 (E1-E3 were already on new
   code in the same script). 60 s later: 409 on first try. Battery design rule: retry
   negatives, trust in-band version markers (`source:"r2"`), never the deploy timestamp.
   Side effect: that stale 200 ran old apiBrief → clobbered the fixture ticket's title in D1
   (restored) and cold-started a throwaway container init. Harmless here; instructive.
3. **NEW shim finding (BR-QC0816 outline):** the customer-facing `intent` blurb leaked raw
   `{{TEMPLATE}}` tokens + a duplicated purpose sentence (shim.py `outline_json()` §1
   extraction keeps lines that merely CONTAIN placeholders). Worker-side scrub deployed as
   mitigation; proper extraction fix belongs to the next image lap (a11).
4. **QUESTION for operator:** `authorial_act` verdict was **FAIL(66h/66f)** yet integrate
   recorded stage.done and the build proceeded to ready. If the one-shot MVP intentionally
   demotes authorial_act to advisory (like the vision gate), fine — but it is not written
   down anywhere I found. Confirm intent; write it into the MVP spec or make it blocking.
5. Cover vision gate SKIP in-container — known accepted limit, observed as documented.
6. Chapter word counts ran up to +40% over the 1,200 band (1,682 max) — band enforcement is
   loose upward; cosmetic at S size, worth a shim clamp eventually.
7. `wrangler r2 object list` doesn't exist; and the earlier `r2 object` misfire also emitted
   a harmless libuv assertion on exit (Windows node quirk) — cosmetic.

## Deltas vs plan
None of substance. Order held (baseline before deploy). One extra fix shipped beyond plan
(the `{{…}}` scrub). Fixture rows BR-SIM901 / BR-QC0816 kept in D1+R2 as standing regression
fixtures; extra sessions minted during testing expire in 90 d.

## Still open (unchanged from QC doc)
M2 fail-closed runner auth + shim busy-gates (/init, /file) + L10 short-read guard + intent
extraction → **next image lap (a11)**, swapped only with no live ticket instances (lesson 16).
Human dashboard steps before the real $5: ntfy subscribe, Email Sending zone enable +
orders@ sender, Stripe live-webhook eyeball. Post-launch: rotate DeepSeek key + fresh
DEMO/DEV tokens (now also: consider whether DEV_KEY should keep its odd prefix form),
L13 durability slice, remaining LOWs.
