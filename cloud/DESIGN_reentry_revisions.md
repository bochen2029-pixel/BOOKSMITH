# DESIGN — bookraising re-entry (identity) & revisions

**Status:** Phase 1 (§3.3.1) **SHIPPED LIVE 2026-08-21** (site worker `abe3e6dc`; plan + battery
results: `cloud/PLAN_REENTRY_PHASE1_2026-08-21.md`; awaiting only the Email-Sending zone enable to
actually deliver mail). Phases II-V not built. Originally written 2026-08-16 (Central), from a full
read of the shipped code + the reference implementation + the MVP spec.
**Author of note:** Claude, at Bo's request ("brainstorm first, then write it up robust").
**Companions:** `cloud/QC_STOREFRONT_2026-08-16.md` (findings), `cloud/RUNBOOK.md` (ops state),
`docs/CLOUD_ONESHOT_MVP_SPEC.md` §4-§8 (the intended architecture), `C:\Websites\thaiintexas.com`
(the deployed reference: worker.js accounts block + schema.sql).

---

## 0. TL;DR

- **Revisions today: effectively none.** Only the pre-commit outline reroll (≤3). The one crude
  post-`ready` mutation was deliberately closed this morning (M1) because it was unbounded-spend
  abuse, not a feature.
- **Identity today: cookie-only, ticket-scoped, fragile exactly where Bo guessed.** Clear cookies,
  switch device, or switch browser → locked out. Coupon/free users leave **no email at all**, so
  they are not even manually recoverable.
- **The fix is already designed and already built next door.** The MVP spec anchors identity on
  **email via passwordless magic link**; `thaiintexas.com` runs that exact stack in production.
  bookraising already has every primitive. **Phase-1 port is ~1-2 hours**, gated only on the
  Email-Sending zone-enable already owed before launch.
- **Revisions are a bigger, later lift** with two hard prerequisites: (1) persist the **whole**
  workspace to R2 + a shim "rehydrate" verb, (2) a **revision budget** (free-N or paid pack),
  because each revision is real model spend and today's ceiling is per-run.
- **Sequence:** identity first (it is a prerequisite for revisions), then per-unit re-roll, then
  conversational revision.

---

## 1. Current state (what the code actually does)

### 1.1 Identity — cookie-only, keyed to a ticket, not a person
- `br_sess` cookie = 192-bit random token, stored **sha256-only** in `sessions`, `HttpOnly; Secure;
  SameSite=Lax; Max-Age=90d` (`worker.js:264-271` `mintSessionCookie`).
- `sessions` is **ticket-scoped**: `sessions(token_hash PK, ticket_id, created_at, expires_at)`
  (`schema_tickets.sql:12-17`). A cookie resolves to exactly one ticket
  (`worker.js:272-281` `sessionTicket`).
- Minted in three places, all server-side, never on a login: paid confirm
  (`worker.js:208-211`), coupon redeem (`worker.js:455-458`), dev-adopt (`worker.js:469-471`).
- **There is no login/auth route, no `login_tokens` table, no email-based recovery.** Possession of
  the cookie *is* the identity.

### 1.2 Revision — outline reroll only; post-build is now locked
- Pre-commit: `/api/outline` with a note re-architects, capped at 3 (`worker.js` `apiOutlineStart`,
  `MAX_REROLLS`). Post-`ready`: **nothing.**
- The only path that ever mutated a finished ticket (re-`/api/outline`, which made the shim wipe
  `manuscript/ outputs/ _engine/` and rebuild — `shim.py:311-319`) was **closed this morning** by
  the M1 stage-gate. That was correct: it was an unbounded-rebuild hole, not a revision UX. A real
  revision feature is a *different, metered* door (see §4.6).

### 1.3 The lockout matrix (who loses access, and how bad)

| Situation | Recoverable today? | Why |
|---|---|---|
| Same browser, within 90d | ✅ yes | cookie present |
| Cleared cookies / private window | ❌ no | cookie was the only key |
| Different device or browser | ❌ no | cookie is per-browser |
| Paid user, lost cookie | ⚠️ only by operator, manually | `orders.email` exists (`worker.js:116-123`) but no self-serve route |
| **Coupon / free user, lost cookie** | ❌ **no, not even manually** | coupon flow captures **no email** (`worker.js:449-451`); ticket has only title/author |
| 90 days elapsed | ❌ no | session expired |

### 1.4 The shipped MVP took a shortcut away from its own spec
`docs/CLOUD_ONESHOT_MVP_SPEC.md` §4 designed identity on **email**: an email-scoped `sessions`
table, a `login_tokens` table ("thaiintexas verbatim"), and `tickets.email` — with the explicit
note *"one email may hold multiple tickets; login simply lists/opens them — that is as close to a
library as the MVP gets, for free."* The shipped storefront simplified to cookie-per-ticket to get
live. **This design is about closing that gap back to the spec, in the right order.**

---

## 2. Framing: these are two independent problems

1. **Re-identification (auth):** how a returning stranger proves they are the same person.
2. **Revision (engine/product):** what they can change once they are back in.

They are orthogonal, but **revision depends on identity** (you cannot offer "come back next week and
revise chapter 4" if they cannot get back in) **and on persisted state**. So identity ships first.

---

## 3. Re-entry (identity) design

### 3.1 Requirements
- Durable across cookie-clear, new device, new browser.
- No password to store or leak (liability + support cost).
- Self-serve (no operator in the loop).
- Works for **both** paid and coupon/free users.
- Minimal new surface on an already-live money worker; must not regress payment/session security.
- Reuse what exists; do not add a vendor.

### 3.2 Options

| Method | Verdict | Notes |
|---|---|---|
| **Passwordless magic link (email)** | ✅ **Recommended** | Already specced; reference code deployed at thaiintexas; email is the durable anchor and its own reset; bonus: one email → many books = the "library" for free. |
| Password account | ❌ Skip | D1 gives the backend, but passwords add hashing + breach surface + a "forgot password" flow that *needs email anyway*. Magic link strictly dominates. |
| Recovery link/code shown at build | ⚠️ Secondary | A signed, bookmarkable resume URL on the ready page works with no email — but users lose codes (the coupon code was lost an hour ago). Belt-and-suspenders, not primary. |
| Google OAuth | ❌ Later/never | Spec explicitly cut it ("magic link only"). Third-party, heavier, privacy cost. |

### 3.3 Recommended: passwordless magic link

**Why this is low-risk:** the whole stack is running in production at `thaiintexas.com` and can be
copied almost verbatim. The reference (`thaiintexas.com/worker.js:1440-1538`):
- `authRequest`: origin-gate → validate email → `randHex(16)` token → delete this email's old tokens
  + anything >24h → insert `login_tokens(sha256(token), email, now, used=0)` → mail a
  `?login=<token>` link. Returns `{ok:true}`.
- `authRedeem`: validate `^[a-f0-9]{32}$` → look up **unused** token → 30-min expiry check → **atomic
  one-winner** `UPDATE ... used=1 WHERE used=0` → mint `randHex(32)` session → `Set-Cookie` 90d
  HttpOnly/Secure/SameSite=Lax.
- `getSession` / `authMe` / `authLogout` / `myOrders` (order history by email).
- Constants: `SESSION_MS = 90d`, `LOGIN_TOKEN_MS = 30min`.

bookraising already has the primitives: `sha256hex` (`worker.js:251`), a random-token helper
(`worker.js:255`), the `sessions` table, and the **`EMAIL` binding** (Cloudflare Email Service —
so the only change from the reference is swapping Resend's `fetch` for `env.EMAIL.send(...)`).

#### 3.3.1 Phase 1 — minimal port: magic link **re-mints the existing ticket cookie** (~1-2 h)

The smallest change that solves the actual pain. Magic link becomes **a fourth way to mint the
existing `br_sess` ticket cookie** — exactly like coupon/dev-adopt already do. No change to
`sessionTicket`, `apiStatus`, or any downstream handler.

**Schema delta (one new table; no backfill):**
```sql
CREATE TABLE IF NOT EXISTS login_tokens (   -- magic-link sign-in (30-min, single-use; hash only)
  token_hash TEXT PRIMARY KEY,
  email      TEXT,
  created_at INTEGER,
  used       INTEGER DEFAULT 0
);
```
No `tickets.email` migration is needed: **`tickets.id == orders.id`**, so email is one join away —
`SELECT t.* FROM tickets t JOIN orders o ON o.id = t.id WHERE lower(o.email)=lower(?)`.

**Route contracts (add to the `fetch` switch, `worker.js:474-495`):**
- `POST /api/auth/request { email }` → origin-gate; require `env.EMAIL`; validate; mint token; purge
  old; insert; `env.EMAIL.send({ from:"orders@bookraising.org", to:email, subject:"Your Bookraising
  sign-in link", text:"...https://bookraising.org/raise?login=<token>..." })`; return `{ok:true}`.
- `POST /api/auth/redeem { token }` → validate hex; look up unused + unexpired; **atomic** mark used;
  `tickets JOIN orders` by email, `ORDER BY t.created_at DESC`:
  - 0 tickets → `{ok:true, tickets:[]}` ("no books found under this email").
  - 1 ticket → `mintSessionCookie(env, ticket.id)` + `{ok:true, raise:"/raise"}` + Set-Cookie.
  - >1 → **Phase 1 mints the most-recent** and notes it; a real picker rides Phase 2 (email
    sessions). One-shot MVP means one email ≈ one book, so this covers ~all cases.
- `POST /api/auth/logout` (optional) → delete the session row + clear cookie.

**UI touches (`_upload/raise.html`):**
- In the `v-nosession` view (`raise.html:48-55`), add an "Email me a sign-in link" field → `POST
  /api/auth/request` → "Check your email."
- On page load, if `?login=<token>` is present → `POST /api/auth/redeem` → on `{raise}` proceed to
  boot(); strip the token from the URL with `history.replaceState` (same hygiene as the Stripe
  return, `index.html:388`).

**Dependency:** outbound email must work = the **same one-time Email-Sending zone-enable +
`orders@bookraising.org` sender** already owed before launch (RUNBOOK §6). One setup unlocks
receipts *and* magic links.

**Make coupon/free users recoverable:** add an **optional email field** to the coupon redeem
("Where should we send your book? — optional") and write it to `orders.email` in `apiCoupon`. Then
the same join recovers them. Without it they stay cookie-only and should be told so.

#### 3.3.2 Phase 2 — email-scoped sessions + true multi-book library (additive)
When multi-book matters, migrate the anchor to email (the spec's design):
- `sessions(token_hash, email, ...)` (add `email`; keep ticket-scoped rows working during
  transition, or run both cookies briefly).
- `GET /api/my/books` → `tickets JOIN orders WHERE email=?` → list titles/stages/download links.
- A ticket **picker** after redeem (choose which book to open) → mint the ticket cookie for the
  chosen one. This is the "library for free" the spec promised.

#### 3.3.3 Security checklist (do not regress the money worker)
- **Token entropy:** `randHex(16)` = 128-bit; session `randHex(32)` = 256-bit. Keep.
- **Hash-only at rest:** never store the raw token or session; sha256 both (matches existing
  `br_sess` handling).
- **Single-use + atomic:** redeem must `UPDATE used=1 WHERE used=0` and act only on `changes>0`
  (one-winner, same pattern as the paid-flip and the L6 fix).
- **Short expiry:** 30-min link, 90-day session (reference values).
- **Rate-limit `/api/auth/request`** on the existing limiter (`auth:<ip>`) — mail-bomb + enumeration
  guard (mirror the coupon limiter, `worker.js:432-437`).
- **Origin-gate** all auth routes (the reference does; match `ALLOWED_ORIGINS`).
- **No token in server logs / no email in query strings** beyond the one-time `?login=` link (strip
  it client-side immediately; per platform rule, keep personal data out of URLs).
- **Enumeration:** `authRequest` returns `{ok:true}` for any valid-format email (sends a link that,
  if the person has no books, simply redeems to an empty list). Accept the small timing signal; it
  matches the house pattern.
- **Cookie flags:** unchanged — `HttpOnly; Secure; SameSite=Lax`.

#### 3.3.4 Edge cases
- **Link forwarded / opened twice:** second redeem → "already used, request a new one" (single-use).
- **Email not yet captured (old coupon tickets):** unrecoverable by email; only the cookie or an
  operator D1 lookup. Acceptable for the alpha; capture email going forward.
- **Multiple browsers signed in:** fine — multiple session rows, all valid until expiry/logout.
- **Stripe email vs typed email mismatch:** identity keys on `orders.email` (from Stripe
  customer_details). If a buyer requests a link with a *different* address, no match. Phase 2 could
  let a signed-in email "claim" a ticket by order number; note for later.

### 3.4 Secondary: the build-time recovery link (belt-and-suspenders)
On the ready page, also show a bookmarkable resume URL. Two ways:
- **Stateful:** `https://bookraising.org/raise?resume=<opaque>` where `<opaque>` is a second,
  long-lived single-use token in a `resume_tokens` table → mints the ticket cookie. Simple, no email
  needed.
- **Stateless:** an HMAC-signed `ticket|exp` value the worker verifies (no table). Lighter, but
  revocation is harder.
Primary is still magic link; this just covers "no email + lost cookie."

---

## 4. Revisions design

### 4.1 What "revision" means — four levels, cheapest first
- **L0 — rebuild-from-tweaked-brief.** Re-outline + full rebuild; destroys prior work. This is the
  door M1 *closed*. Not a real revision; do not reopen it as one.
- **L1 — per-unit re-roll** ("rewrite chapter 4, warmer"). **The sweet spot.** Bounded cost (one
  unit + downstream production), high perceived value. The engine already *wants* this — RUNBOOK
  lesson 9: *"auto-revise-unit verb = wanted (spec §8)."*
- **L2 — structural** (add / remove / reorder chapters). Changes the outline → re-derives more.
- **L3 — conversational** (the Studio chat-compiler bound to the ticket workspace). The richest; the
  spec's endgame (*"bind it to the ticket's workspace; the hash cascade already re-derives only the
  stale suffix"*). Biggest lift.

### 4.2 Two hard prerequisites (name them before promising revisions)
1. **Persist the WHOLE workspace, not just outputs.** Today `archiveOutputs` copies only
   `outputs/{digital,kindle,epub}/*` (`worker.js:163-185`); `manuscript/`, `contracts/`, `registry/`,
   `seed.md`, `book_config.json`, `_engine/state.json`, `brief.md`, `_outline.json`, `intake/` live
   only on the container and die at eviction. Revision needs:
   - archive the full `book_workspace/<slug>/` to `tickets/<id>/workspace/...` on `ready` (the spec's
     R2 layout already mirrors the workspace);
   - a **new shim verb** `POST /t/<id>/rehydrate` that restores it into the container FS before a
     revise. (This is the QC doc's L13 durability item, enlarged from brief+intake to the full tree.)
2. **A revision budget.** `ALPHA_FLOOR` is **per-run** env (`index.ts:8-10,24`), so naive free
   revisions = a fresh $10 ceiling per lap = the exact unbounded-spend hole just closed. Choose:
   - **free N** revisions then paywall (like the 3 outline rerolls), tracked in a `tickets.revisions`
     counter with a per-ticket lifetime token rollup (`tickets.tokens_*` exists in the spec schema); or
   - **paid revision packs** ($X per pack) — fits the `$5 founder build → upsell` model cleanly.

### 4.3 The engine asset that makes L1 cheap
The kit already does **incremental re-derivation**: change one unit and the hash cascade re-runs only
the stale suffix (that unit's gates → assemble → produce → verify), not the whole book. That is the
single fact that makes per-unit revision affordable. (Dependency: an **engine entrypoint to
re-draft one unit** — the "auto-revise-unit verb" — is *wanted, not yet built*; it is engine-side,
not worker-side.)

### 4.4 Concrete L1 flow (per-unit re-roll)
```
customer (signed in, ticket=ready)
  → GET  /api/book         → worker lists units from the R2 workspace (titles + ids)
  → POST /api/revise-unit  { unit_id, note }   (worker: metered; stage ready→revising)
       → runner POST /t/<id>/revise-unit { unit_id, note }
            → shim: rehydrate workspace from R2 (if cold)
            → engine: re-draft that unit → unit gates → re-assemble → re-produce formats
            → archive changed outputs to R2 (+ full workspace)
       → worker: stage revising→ready; page/email "revision N ready"
  → download the updated PDF/EPUB/DOCX (R2-first, unchanged)
```
New pieces: worker routes `GET /api/book` + `POST /api/revise-unit` (both stage-gated to `ready`,
metered); shim verbs `/rehydrate` + `/revise-unit`; engine revise-unit entrypoint; stage machine
`ready → revising → ready`; counter/budget.

### 4.5 This is a NARROW, metered door — not a reopening of what M1 closed
M1 blocked the *wide* door (any post-ready `/api/outline` wipes and rebuilds, unbounded). Revision
opens a *narrow* door (one named unit, counted or paid, workspace preserved not wiped). Keep the M1
gates; add `revise-unit` as an explicitly separate, metered verb. The two are complementary.

---

## 5. Sequencing / roadmap

| Phase | What | Effort | Depends on | Unblocks |
|---|---|---|---|---|
| **I** | Magic-link re-entry (Phase-1 port: link → re-mint ticket cookie) + coupon email capture | ~1-2 h (worker+html) | Email-Sending zone enable (already owed) | returning users on any device; the whole revision story |
| **II** | Full-workspace R2 archive + shim `/rehydrate` | ~½ day (worker+shim, next image lap) | lesson-16 image discipline | any revision; also fixes the pre-commit eviction dead-end (L13) |
| **III** | L1 per-unit re-roll + revision budget (free-N or paid pack) + engine revise-unit verb | ~1-2 days (engine+shim+worker+html) | II; a pricing decision | the headline "revise your book" feature |
| **IV** | Email-scoped sessions + `/api/my/books` library + ticket picker | ~½ day | I | multi-book accounts |
| **V** | L2 structural + L3 conversational (Studio chat bound to the ticket) | larger | II-IV; Studio port | the full editing surface |

Do **I** now (small, proven, high-leverage, and a prerequisite for everything else).

---

## 6. Decisions needed from Bo

> **2026-08-21 execution note:** under Bo's blanket GO, defaults were adopted for #2 (optional —
> shipped), #3 (defer picker; redeem opens the most-recent ticket), #4 (folded into `/raise`),
> #5 (no recovery link for the alpha). Each is reversible. **#1 (revision pricing) remains open
> and still blocks Phase III.**
1. **Revision pricing:** free-N-then-paywall, or paid revision packs? (Sets the metering in Phase III.)
2. **Coupon email capture:** make it optional (recommended) or required? (Optional keeps the free
   door frictionless but leaves some testers unrecoverable.)
3. **Library timing:** ship the multi-book picker (Phase IV) with re-entry, or defer until someone
   actually buys a second book?
4. **Sign-in surface:** a dedicated `/signin` page, or fold the email field into the existing
   `/raise` no-session view (recommended — fewer pages, matches house single-file style)?
5. **Recovery link (§3.4):** worth the extra table now, or rely on magic link alone for the alpha?

---

## 7. Appendix — reference pointers (copyable, file:line)
- **Magic-link reference (deployed):** `C:\Websites\thaiintexas.com\worker.js:1440-1538`
  (`authRequest` / `authRedeem` / `getSession` / `authMe` / `authLogout` / `myOrders`),
  route wiring `:57-61`; tables `C:\Websites\thaiintexas.com\schema.sql:55-66`
  (`login_tokens`, `sessions`) + `:36-41` (`users`).
- **Intended bookraising schema:** `docs/CLOUD_ONESHOT_MVP_SPEC.md:118-136` (tickets email-scoped,
  `login_tokens`/`sessions` verbatim, `events` audit) + the "library for free" note.
- **bookraising primitives to reuse:** `sha256hex` `worker.js:251`, random token `:255`,
  `mintSessionCookie` `:264-271`, `sessionTicket` `:272-281`, coupon email gap `:449-451`,
  `EMAIL` binding `wrangler.toml:43-45`.
- **Revision engine note:** RUNBOOK lesson 9 (auto-revise-unit wanted); shim wipe path
  `cloud/shim.py:311-319`; outputs-only archive `worker.js:163-185`.

---
*Design note by Claude (Opus), 2026-08-16. No code changed. Grounded in the shipped worker/shim,
the thaiintexas reference, and the MVP spec. Update in place as decisions land.*
