# QC PASS — bookraising.org storefront + BOOKSMITH cloud runner (2026-08-16)

> **STATUS UPDATE 2026-08-17:** H1, H2, M1, M3 (+L6, +intent-scrub) **FIXED, DEPLOYED
> (site worker `90723bd7`), AND VERIFIED LIVE** against regression fixtures BR-SIM901 and
> BR-QC0816; fresh end-to-end sim green (6 min, ~$0.02, 31-pp exact-6×9 PDF downloaded).
> Full record: `cloud/PLAN_QC_FIX_2026-08-16.md` RESULTS. Still open: M2 + shim-side items
> (next image lap a11) + the LOW tail + the human dashboard steps.

**Scope:** full read of the $5→book loop before the real-$5 graduation exam.
Files: `C:\Websites\bookraising\worker.js` (497 ln) + `_upload/index.html` + `_upload/raise.html`
+ `schema.sql` + `schema_tickets.sql` + `wrangler.toml`; `C:\BOOKSMITH\cloud\shim.py` (337 ln)
+ `cloud/worker/src/index.ts` + `cloud/worker/wrangler.toml` + `Dockerfile` + `Dockerfile.cf`
+ `.gitignore` + git state of both trees. Static review + two live side-effect-free probes
(earlier this session: homepage 200, wrong-coupon 403, secret list, D1 coupon count).
**Nothing was changed. No build was run. This is the assessment.**

**Verdict: the bones are genuinely good.** Payment integrity, session auth, traversal
posture, spend ceiling, and the ops lessons (15/16) are correctly built in. But there are
**2 HIGH findings** (one breaks the product's own "downloads stay available" promise, one is
a reflected XSS on the live homepage), **3 MEDIUM** (spend-loop logic gap, fail-open runner
auth, secrets-vs-gitignore drift), and a tail of LOW polish. Fix H1+H2 before the real $5.

---

## WHAT HOLDS (verified, so nobody re-litigates it)

- **Payment integrity.** Price is server-side only (`PREPAY`, worker.js:17); order↔session
  binding is sound — confirm derives the order from the session's OWN `metadata.order_id`
  (worker.js:201), so a paid session cannot flip someone else's order and an unpaid one flips
  nothing; `markPaidAndNotify` idempotent via `WHERE paid=0` (worker.js:122); webhook is
  HMAC-verified before parse (worker.js:225-229); pending-row-first means a lost return or
  dropped webhook can never lose an order.
- **Session auth.** 192-bit token, stored as sha256 only, `HttpOnly; Secure; SameSite=Lax`,
  90d expiry enforced server-side (worker.js:264-281). Cookie never readable by JS.
- **Traversal posture.** Shim file GET: prefix allowlist (`outputs/`|`cover_art/`) + `..`
  reject + `resolve().startswith(ws)` — symlink-safe (shim.py:202-205). Intake PUT: basename
  flattening + `intake/` prefix + 60MB cap (shim.py:284-289). R2 keys are literal strings, so
  `../` in a download path resolves nothing.
- **Spend control.** $10/run arithmetic ceiling injected as `BOOKSMITH_TOKEN_BUDGET`
  (index.ts:8-10,24); thinking-disable seam; one job per container via the busy-lock
  (shim.py:118-125); per-ticket instances; friendly 503 at slot capacity (worker.js:366-370).
- **Ops lessons applied.** R2 puts buffered + in-band `s.archive` receipt + pager on failure
  (worker.js:163-185, lesson 15); honest `stalled` state; `history.replaceState` scrubs the
  Stripe session id from the URL (index.html:388); waitlist honeypot + dedupe + rate limit;
  container image built from `git archive HEAD` so untracked local secrets cannot enter it.
- **Closed-verb shim.** No general executor; ticket regex enforced twice; GATE-2 slug law.
- The runbook's open "tiny" item — PDF label mapping in `renderReady` — **is landed**
  (raise.html:245-256, `_DIGITAL.pdf` ranked first, labeled "Your book (PDF)").

---

## HIGH

### H1 — After container sleep, a READY ticket's download page lists NOTHING (promise break)
`apiStatus` (worker.js:373-394) always proxies to the runner; the outputs list is globbed
from the **container filesystem** (shim.py:235-239). Container instances sleep after 2h
(index.ts:14) and eviction destroys the filesystem. So: customer builds a book, comes back
tomorrow, `/raise` boots → stage `ready` → pollBuild → status → a **fresh cold container**
answers `outputs: []` → `renderReady` paints "It's a book." with **zero download links** —
while the artifacts sit safely in R2 and the page itself promises "your downloads stay
available." The R2-first `apiDownload` works; it's the **listing** that dies. Bonus defect:
every status poll on a finished ticket cold-starts a billable container for nothing.
**Fix (worker.js only, ~20 lines):** when `t.stage === 'ready'` (or `stalled`), skip
`runnerFetch` entirely; for `ready`, list R2 instead:
`(await env.BOOKS.list({prefix:"tickets/"+t.id+"/"})).objects.map(o=>o.key.slice(prefix.length))`
→ return as `s.outputs` with `s.stage`. Cheaper, durable, and no container wake.

### H2 — Reflected XSS on the live homepage via `?order=`
`banner()` assembles `innerHTML` with the raw `order` query param on **all three** confirm
branches (index.html:381, 384, 385, 387; `banner()` at 364-372). A crafted link
`https://bookraising.org/?order=<img src=x onerror=...>&session=cs_x` executes attacker JS on
the production origin (the `.catch`/processing branch fires even with a garbage session id).
The `br_sess` cookie is HttpOnly (safe from theft), but injected JS can still call every
`/api/*` with the victim's cookie (read ticket, spend rerolls, commit builds) or fake UI.
**Fix (one line):** validate before use — `if(!/^BR-[0-9A-Z]{6}$/.test(order)) order="";` —
or build the banner with `textContent`. Same treatment for the `canceled` branch is free.

---

## MEDIUM

### M1 — No stage-gating server-side: reroll-cap bypass, post-ready wipe, unbounded rebuild spend
Chain of four related gaps (all curl-reachable; the UI hides them but the API is the product):
1. **Empty-note outline is free and uncounted** — `if (note)` guards both the cap and the
   counter (worker.js:338-342). Anyone can re-architect forever without touching the 3-reroll
   budget (each run = real model seed spend + occupies the container).
2. **Outline is accepted at ANY stage** — including `ready`. The shim then **wipes**
   `manuscript/`, `outputs/`, `_engine/` (shim.py:311-319). R2 keeps the downloads, but the
   ticket re-enters the loop.
3. **Commit is accepted whenever an `_outline.json` exists** (worker.js:360-372,
   shim.py:324-329) → outline(free) → commit → build → repeat: **one $0 coupon ticket can
   serially trigger unlimited builds, each with a fresh $10 token ceiling** (the ALPHA FLOOR
   is per-run env, not per-ticket, index.ts:24). Realistic cost ~$0.06/lap, worst-case $10/lap,
   plus a permanently-hogged build slot (of 5).
4. **Shim `/init` and intake `/file` PUT are not busy-gated** (shim.py:257, 277 — only
   outline/build check the lock): a brief re-POST **during a build** rewrites
   `book_config.json` under the running engine.
**Fix:** worker-side — count every outline POST after the first (note or not) against
`MAX_REROLLS`; allow brief/intake/outline only in `briefing|outlining|outline_ready`; allow
commit only in `outline_ready`; optionally a lifetime `builds` counter per ticket (refuse >2).
Shim-side (next image lap, lesson-16 discipline) — 409 `/init` and `/file` PUT while running.

### M2 — Runner auth FAILS OPEN if DEMO_TOKEN is ever unset
`if (env.DEMO_TOKEN) { ...check... }` (index.ts:37-42): delete or fat-finger the secret and
the runner is **wide open** — anyone can drive the engine and spend the DeepSeek key.
**Fix:** fail closed — `if (!env.DEMO_TOKEN) return new Response("locked", {status:503});`.
(Deploying this touches the runner: per lesson 16, only when `wrangler containers list`
shows no live ticket instances.)

### M3 — Secrets NOT gitignored, contradicting the runbook, in a repo whose lap says "commit + push"
`git check-ignore` proves: `cloud/worker/.demo_token` ignored (.gitignore:121), but
**`cloud/worker/.dev_key` and `cloud/worker/.test_cookies` are NOT ignored** — RUNBOOK §1
claims all three are. `cloud/_receipts/` (test artifacts) is also unignored. Lesson 14 made
these dotfiles the **source of truth** for live secrets; one `git add -A` in the lap's
"commit (public-safe) + push" step publishes `DEV_KEY` (which mints free signed-in tickets
via `/api/dev/adopt`) to the public repo. **Fix (2 min):** add to `.gitignore`:
`cloud/worker/.dev_key`, `cloud/worker/.test_cookies`, `cloud/_receipts/`. Decide
`cloud/worker/package-lock.json` (recommend: track it). Also noteworthy:
**`C:\Websites\bookraising` is not a git repo at all** — the live production source has no
VCS, only manual `_backups/`. Recommend `git init` (private) with a `.gitignore` for
`.coupon_code`, `.wrangler/`, `_backup*/` first.

---

## LOW / POLISH (none block launch)

- **L1 Coupon cap race** (worker.js:444-451): COUNT-then-INSERT isn't atomic; concurrent
  redemptions can land 21/20. Pager fires per use; accept, or make it one statement
  (`INSERT ... SELECT ... WHERE (SELECT COUNT(*)...) < 20`).
- **L2 Session-row growth + confirm replay** (worker.js:208-211): every confirm call with a
  known paid `cs_` id mints a NEW session row, forever. Reuse an unexpired session or cap
  rows per ticket; add an occasional `DELETE FROM sessions WHERE expires_at < now`.
- **L3 Checkout unthrottled** (worker.js:73-87): every click writes a pending order row +
  creates a Stripe session; a bot can spam thousands. Add `checkout:<ip>` to the limiter.
- **L4 Webhook hygiene** (worker.js:222-229): hex compare isn't constant-time and no
  timestamp tolerance (replay window unbounded — harmless because idempotent, but
  `crypto.subtle.timingSafeEqual` + reject `|now−t| > 5min` is a 5-line upgrade).
- **L5 apiDownload trusts `path` shape** (worker.js:395-422): safe today only because R2
  keys are literal and the shim allowlists; mirror the allowlist in the worker
  (`^(outputs|cover_art)/`, no `..`) and sanitize the `Content-Disposition` filename
  (strip `"`/CR/LF).
- **L6 Double-ready race** (worker.js:379-391): two concurrent status polls can both flip
  building→ready → two "book ready" emails. Make the flip conditional
  (`... WHERE id=? AND stage='building'`, act only if `changes>0`).
- **L7 Intake volume unbounded per ticket** (worker.js:319-332): 60MB/file but no file-count
  or total cap → container disk exhaustion. Cap ~20 files / 200MB total worker-side.
- **L8 `raise.html` is `robots: index, follow`** (raise.html:6) — a private flow page;
  make it `noindex`.
- **L9 Google Fonts on index.html** (index.html:17-19) — the only third-party dependency in
  an otherwise self-contained house style (raise/vision are single-file). Inline or drop for
  consistency + privacy.
- **L10 Shim upload short-read** (shim.py:287-299): trusts Content-Length; a short body
  writes a truncated file silently (and can desync keep-alive). Compare received bytes to
  `n`, 400 on mismatch.
- **L11 Node 18 in the image** (Dockerfile:30-33) is past upstream EOL — build-time-only
  exposure; bump to 20/22 on a convenient lap.
- **L12 `committed` stage** exists in schema comment + client but is never set — cosmetic;
  delete from the comment or set it on commit-202 before `building`.
- **L13 Outline-stage eviction dead-end** (known limit, now sharpened): brief text
  (`about`/`audience`/`length`) and intake files live ONLY on the container; D1 keeps just
  title/author (worker.js:315-316). Eviction between brief and commit strands the customer at
  an infinite spinner (raise.html:191-202 stall-detect needs `rc` truthy; a fresh container
  reports `rc:null`). Cheapest durable fix: persist the brief JSON in a `tickets.brief_json`
  column + mirror intake uploads to R2 (`tickets/<id>/intake/...`) at upload time; on a 404
  outline with stage `outlining|outline_ready`, worker re-inits the container from D1+R2 and
  re-runs the outline (no reroll charge). This closes the runbook's "R2 workspace snapshots"
  item for the pre-commit half at ~1/10 the effort.
- **L14 Runner 7th-instance UX**: at >6 live instances, outline/status on the overflow ticket
  surfaces raw platform 5xx through `apiOutlineStart`/`apiStatus` (only commit has the
  friendly 503). Low traffic makes this rare; wrap similarly when convenient.

---

## RECOMMENDED ORDER (pre-launch, ~1 focused session)

1. **H2** XSS guard (index.html, one line) — redeploy site.
2. **H1** R2-listing fallback + skip runner on terminal stages (worker.js only) — redeploy site.
3. **M3** .gitignore lines (BOOKSMITH repo) + optionally `git init` the site dir.
4. **M1** worker-side stage gates + reroll counting (worker.js only) — redeploy site.
5. **M2** + shim busy-gates + L10: queue for the NEXT image lap (a11), swapped only when
   `wrangler containers list` shows no live ticket instances (lesson 16).
6. Then the standing human steps from RUNBOOK §6: ntfy subscribe, Email Sending zone enable +
   `orders@` sender, eyeball Stripe live webhook, **then the real $5**.
7. Post-launch: L13 durability slice, key rotation (DeepSeek + DEMO/DEV per runbook), L1-L9.

*Steps 1-4 touch only the site worker + static assets — no container/runner deploy, so no
lesson-16 exposure and no risk to any live build.*

---

*QC by Claude (Fable), 2026-08-16 evening session. Static analysis + prior live read-only
probes; no writes to production, no builds run, no book workspaces touched. Companion
records: `cloud/RUNBOOK.md`, `C:\Websites\bookraising\BUILD_LOG.md`,
`cloud/_receipts/coupon_live_check_2026-08-16.md`.*
