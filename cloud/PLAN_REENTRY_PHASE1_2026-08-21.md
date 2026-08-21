# PLAN — Re-entry Phase 1 (magic-link sign-in) + coupon email capture

**Date:** 2026-08-21 (Central) · **Executor:** Claude, on Bo's GO ("write the plan as markdown and
then do, implement and execute against it").
**Design being executed:** `cloud/DESIGN_reentry_revisions.md` §3.3.1 (Phase 1 — minimal port:
magic link **re-mints the existing ticket cookie**). Reference implementation (deployed, production):
`C:\Websites\thaiintexas.com\worker.js` accounts block (`authRequest`/`authRedeem`).
**Companions:** `cloud/RUNBOOK.md` (ops record — gets a dated entry on completion),
`C:\Websites\bookraising\BUILD_LOG.md` (site-side log — same).

---

## 0. Why this item, of everything open

The Aug-17 QC pass left four frontiers: (1) Bo's dashboard steps, (2) image lap a11, (3) re-entry +
revisions (designed, unbuilt), (4) the `authorial_act` advisory-vs-blocking decision. Item 3's
Phase 1 is the hinge: it is small (~1-2 h), fully designed, has a deployed reference next door, and
is the prerequisite for the whole revision story. Its only external dependency (Email Sending
zone-enable) fails soft — the code ships now, sends the moment Bo flips the zone on. Items 1 and 4
are Bo's; item 2 needs a dedicated image-lap session (WSL builds + registry push + idle-instance
window) and stays queued.

## 1. Scope

**IN (this session):**
1. D1 table `login_tokens` (30-min single-use magic-link tokens, sha256-only at rest) — appended to
   `schema_tickets.sql`, applied `--remote`.
2. Worker routes on the site worker (`C:\Websites\bookraising\worker.js`):
   - `POST /api/auth/request {email}` — origin-gated, rate-limited (`auth:<ip>` on the existing
     limiter), enumeration-safe `{ok:true}`; mails `https://bookraising.org/raise?login=<token>`
     via the `EMAIL` binding. NOT fail-open: if the mail cannot send, say so (502/503).
   - `POST /api/auth/redeem {token}` — `^[a-f0-9]{32}$` gate → unused+unexpired → **atomic
     one-winner** `UPDATE used=1 WHERE used=0` → `tickets JOIN orders` on `lower(orders.email)` →
     mint `br_sess` for the **most recent** ticket (Phase-1 rule; picker rides Phase 2/IV).
     0 tickets → `{ok:true, tickets:0}` (honest empty).
   - `POST /api/auth/logout` — delete session row + clear cookie (API only; no UI button yet).
3. Coupon recoverability: optional `email` field on `POST /api/coupon` → written to `orders.email`
   at insert; optional input added to the invite row on `index.html`.
4. `raise.html`: the `v-nosession` view gains "email me a sign-in link"; page boot redeems a
   `?login=<token>` param (then strips it via `history.replaceState`, same hygiene as the Stripe
   return).
5. Deploy (`npx wrangler deploy` from `C:\Websites\bookraising`) + live verification battery (§4).
6. Records: RUNBOOK entry, BUILD_LOG entry, DESIGN doc status line, this plan updated with results.

**OUT (explicitly not this session):**
- Phase II-V of the design (full-workspace R2 archive, `/rehydrate`, per-unit re-roll, email-scoped
  sessions/library, conversational revision) — Phase III is blocked on Bo's pricing decision anyway.
- Image lap a11 (shim busy-gates, fail-closed runner auth, intent extraction, upload short-read
  guard) — needs its own lap with an idle-instance window; queued in RUNBOOK.
- The `authorial_act` advisory-vs-blocking call — Bo's product decision; flagged again in §5.
- The §3.4 recovery-link (belt-and-suspenders) — skipped for the alpha per adopted default D5.

## 2. Decisions adopted (design §6, under Bo's blanket GO — each reversible; veto any)

| # | Question | Adopted | Why |
|---|---|---|---|
| D1 | Revision pricing | **NOT decided — still Bo's** | Phase III only; nothing today depends on it |
| D2 | Coupon email capture | **Optional field** | Recommended in design; keeps the free door frictionless; captured users become recoverable |
| D3 | Library/picker timing | **Defer; mint most-recent** | One-shot MVP ≈ one email one book; picker is Phase 2 |
| D4 | Sign-in surface | **Fold into `/raise` no-session view** | Recommended; fewer pages, house single-file style |
| D5 | Recovery link | **Skip for alpha** | Magic link covers it once email is on; codes get lost (the coupon code itself was lost on 08-16) |

## 3. Security checklist carried from design §3.3.3 (must all hold in the diff)

- [x] 128-bit link token (`randHex(16)`), 256-bit session (existing `randToken`) — no weakening.
- [x] Hash-only at rest for both token and session (sha256, house `sha256hex`).
- [x] Single-use redeem: atomic `UPDATE ... WHERE used=0`, act only on `changes>0` (L6 pattern).
- [x] 30-min link expiry / 90-day session (reference constants).
- [x] Rate-limit `/api/auth/request` (`auth:<ip>`, mirrors coupon limiter; fail-open on missing binding).
- [x] Origin-gate all three auth routes (`ALLOWED_ORIGINS`, house form).
- [x] Enumeration-safe request: `{ok:true}` for any valid-format email; link redeems to empty list.
- [x] No raw token in D1 or logs; `?login=` stripped client-side immediately after redeem.
- [x] Cookie flags unchanged: `HttpOnly; Secure; SameSite=Lax`.
- [x] Payment/session code paths untouched except the additive coupon email column write.

## 4. Verification battery (live, dev lane; lesson 17: retry negatives once — stale isolates lie)

| # | Test | Expect |
|---|---|---|
| V1 | Seed a dev order (`item='dev'`, `paid=1`, `email=<test>`) + ticket via D1/dev-adopt | rows exist |
| V2 | Insert a hand-minted token row (local randHex → sha256 → D1) then `POST /api/auth/redeem` | 200 `{ok, ticket}` + `Set-Cookie br_sess` |
| V3 | `GET /api/ticket` with the V2 cookie | 200, the dev ticket |
| V4 | Redeem the same token again | 400 "already used" |
| V5 | Redeem garbage token | 400 "bad link" |
| V6 | Redeem a token seeded `created_at = now-31min` | 400 "expired" |
| V7 | `POST /api/auth/request` valid email | `{ok:true}` if zone mail is enabled; else honest 502; D1 shows purged+fresh token row either way |
| V8 | `POST /api/auth/request` bad email | 400 |
| V9 | `POST /api/coupon` wrong code (with email field present) | 403 (validation path exercised; no coupon burn) |
| V10 | `POST /api/auth/logout` with V2 cookie | 200 + cleared cookie; V3 repeat → 401 |
| V11 | Storefront regression: `GET /` 200, `GET /raise` 200, `POST /api/waitlist` honeypot path | unchanged |

## 5. Operator checklist (Bo — unchanged from the scan, restated)

1. **Email Sending zone-enable + `orders@bookraising.org` sender** (Cloudflare dash, ~2 min) — the
   single step that turns on receipts, ready-mails, AND these magic links. Until then
   `/api/auth/request` answers with an honest "couldn't send" and nothing else degrades.
2. ntfy: subscribe the phone to the `NTFY_TOPIC` topic.
3. Stripe dashboard: eyeball the live webhook endpoint registration.
4. Rotate the DeepSeek demo key (appeared in chat once) when convenient.
5. Decide: revision pricing (free-N vs packs) — unblocks Phase III.
6. Decide: `authorial_act` in-container gate — advisory-by-design (write it into the MVP spec) or
   blocking (engine change next lap).

## 6. Rollback

- Pre-change copies in `C:\Websites\bookraising\_backups\2026-08-21_reentry\` (worker.js,
  index.html, raise.html, schema_tickets.sql).
- Worker: `npx wrangler rollback` (or redeploy the backup worker.js).
- Schema: additive only (`CREATE TABLE IF NOT EXISTS login_tokens` + one index); nothing existing is
  altered; a rollback can simply leave the empty table in place.

## 7. Results (closed 2026-08-21, same session)

- [x] Deployed worker version: `abe3e6dc-8383-4e0f-8291-817f4c157cc4` (assets `/raise.html` +
      `/index.html` uploaded in the same deploy). Schema delta applied `--remote` via `--command`
      — **lesson 18:** the `--file` import path 403s (auth code 10000) on this OAuth token; ship
      D1 deltas as `--command`.
- [x] Battery V1-V11: **ALL PASS.** V2 redeem → 200 + `Set-Cookie` + ticket BR-AUTH01; V3 ticket
      opens with the minted cookie; V4/V5/V6 reuse/garbage/expired all 400 (V4 sequential-reuse
      reports the reference's "expired" copy — single-use enforced; the distinct "already used"
      branch guards the true race); V7 honest 502 pre-zone-enable **with the token row correctly
      purged + freshly minted in D1** (post-check: exactly 1 row, used=0, fresh); V8 400; V9 403
      (no coupon burn); V10 logout kills the session (V10b 401); V11 `/` + `/raise` 200.
- [x] Records updated: RUNBOOK entry + lesson 18; BUILD_LOG entry; DESIGN status header + §6
      adopted-defaults note.
- Test artifact: order/ticket `BR-AUTH01` (item `dev`) + one inert login_token row left in D1,
  house-style (like BR-SIM901/BR-QC0816).

---
*Execution log lives in the session; durable outcomes go to RUNBOOK + BUILD_LOG on completion.*
