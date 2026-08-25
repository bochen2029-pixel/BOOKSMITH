# cloud/RUNBOOK.md — BOOKSMITH-on-Cloudflare: state, lessons, and the exact how-to
*The durable record (Bo's order, 2026-08-13): everything learned + every step, so no session re-derives.
Companions: cloud/README.md (P0 proofs), docs/CLOUD_ONESHOT_MVP_SPEC.md + docs/CLOUD_MODES_BACKLOG.md
(private), C:\Websites\bookraising\BUILD_LOG.md (site-side log), memory booksmith-cloud-saas-direction.*

## 1 · CURRENT DEPLOYED STATE (as of 2026-08-13 ~03:00 CT, image a9)
- **Loop status: GREEN end-to-end.** Ticket BR-TEST01 reached `stage: ready, rc 0, done=17` on
  Cloudflare: describe → DeepSeek outline → COMMIT → 8 gated chapters → integrate → assemble →
  hypergen cover (1600×2560, sha-bound meta) → kindle DOCX → EPUB → `verify --final` ALL GREEN
  (KDP simulator included) → artifacts downloaded via /api/download. ~$0.06/book model cost.
- **Site worker** `bookraising-org` (C:\Websites\bookraising, `npx wrangler deploy` from there):
  live Stripe $5 (checkout/confirm/webhook, pending-row-first), paid→ticket+`br_sess` cookie→/raise;
  routes /api/{ticket,brief,intake,outline,commit,status,download,dev/adopt}. D1 `bookraising-waitlist`
  (binding DB): waitlist, orders, tickets, sessions (schema_tickets.sql applied --remote).
- **Runner worker** `booksmith-p0-demo` (C:\BOOKSMITH\cloud\worker): bearer DEMO_TOKEN; Container
  class BooksmithP0 → image `registry.cloudflare.com/e13b1f08.../booksmith-cf:a9`, instance name
  `runner-a9`, instance_type basic, max_instances 2, sleepAfter 2h; envVars inject model config +
  ALPHA FLOOR ($10 → BOOKSMITH_TOKEN_BUDGET≈11.49M tokens, E-6 enforces in model_client) +
  BOOKSMITH_MODEL_EXTRA_BODY={"thinking":{"type":"disabled"}}. Secrets: DEMO_TOKEN, DEEPSEEK_API_KEY.
- **Container** runs cloud/shim.py (a9): closed verbs only — /run/{smoketest,selfcheck} +
  /t/<BR-XXXXXX>/{init,file,outline,build,status,outline GET,file GET}. Ticket→workspace slug
  br_xxxxxx. Local tokens (gitignored): cloud/worker/.demo_token, .dev_key, .test_cookies.
- **Test lane:** insert paid order row in D1 → POST /api/dev/adopt {order,key:DEV_KEY} → cookie; then
  drive /api/brief → /api/outline (poll GET) → /api/commit → /api/status → /api/download?path=…

## 2 · LESSONS (each cost real time tonight — bind them)
1. **DeepSeek V4 thinking mode is DEFAULT-ON** and its reasoning spends max_tokens: a seed returned
   3,594 tokens but 805 visible chars → truncated JSON → engine fell back to deterministic architect.
   Fix: `BOOKSMITH_MODEL_EXTRA_BODY={"thinking":{"type":"disabled"}}` (model_client extra_body seam).
2. **GATE-2 slug law:** ticket ids (BR-XXXXXX) must slugify to ^[a-z0-9_]+$ for workspace+config.
3. **One-shot normalization after seed:** force every unit class→C AND target_words→band value
   (model marked units A once; shrank targets to 150w once). shim normalize_classes does both.
4. **Outline phase bounds at `--to precheck`** — bracketed [ingest][seed] ignore `--to seed`.
5. **cover_pick phantom-catalog:** manifest is tracked, images aren't → --auto picked a non-existent
   catalog entry over hypergen. Fixed: candidates filtered by image-file existence.
6. **kdp_precheck crashes:** (a) newer PyMuPDF prints fitz-deprecation warning into stdout →
   verify_build now parses from first '{'; (b) minimal ebook configs have no trim → KeyError →
   now defaults 6×9. BOTH were invisible on Windows (older wheel / full configs).
7. **Docker/Cloudflare iteration recipe (bit us 3×):** Dockerfile.cf FROMs booksmith-p0 → **rebuild
   BASE + cf together every lap**; use a UNIQUE image tag + UNIQUE instance name + shim version
   marker in GET /; a warm DO keeps its OLD container and your own polling blocks rollouts →
   `wrangler containers delete <app-id>` then `wrangler deploy` = clean swap. Push via
   `npx wrangler containers push booksmith-cf:aN --path-to-docker "C:/Websites/computer-lab/_tools/docker-wsl.exe"`.
8. **Empty-completion errors** now say so (model_client message fix) instead of "None".
9. **Prose nondeterminism is real:** one lint DING (dangling quote) per ~3 full drafts → integrate
   hard-stops correctly; re-roll passes. Auto-revise-unit verb = wanted (spec §8).
10. **Compile-test the shim locally before pushing** (a v2 syntax slip cost a lap); grep the built
    image for the fix (`docker run IMG grep -c <marker> file`) before deploying.
11. Engine resume works EXACTLY as designed across transient provider failures (re-POST /build).

## 3 · THE LAP (exact commands; WSL docker; run from repo root unless noted)
```bash
# 0) bump markers: shim '"shim": "aN"', worker/wrangler.toml image :aN, index.ts runner-aN
# 1) commit (public-safe) + push
# 2) stage + build BOTH images from HEAD:
wsl -d Ubuntu-24.04 -u root --exec bash -c 'rm -rf /root/booksmith-p0/src && mkdir -p /root/booksmith-p0/src \
 && git -C /mnt/c/BOOKSMITH archive HEAD | tar -x -C /root/booksmith-p0/src \
 && docker build -q -t booksmith-p0 -f /root/booksmith-p0/src/cloud/Dockerfile /root/booksmith-p0/src \
 && docker build -q -t booksmith-cf:aN -f /root/booksmith-p0/src/cloud/Dockerfile.cf /root/booksmith-p0/src'
# 3) verify fix inside image (grep -c), THEN push (docker bridge), THEN:
#    wrangler containers list → delete <booksmith app id> → cd cloud/worker → wrangler deploy
#    (always CLOUDFLARE_ACCOUNT_ID=e13b1f08e91348c714d04252a43e3a74)
# 4) poll GET / with bearer until {"shim":"aN"}; then drive the test lane (§1).
```

## 4 · THE FINISHING WORK ORDER (Bo's GO, 2026-08-13 — item 1 in flight this session)
1. **a10 image: LibreOffice layer + PDF deliverable.** Dockerfile: apt libreoffice-writer (+fonts);
   shim /init formats → ["kindle","epub","digital_pdf"] (docx_to_pdf soffice fallback + strip_blank
   + build_digital_pdf are already in-kit; digital needs cover art ✓ hypergen). Test in-container:
   full ticket run → outputs/digital/*_DIGITAL.pdf present + verify green.
2. **Durable downloads:** create R2 bucket `bookraising-books`; [[r2_buckets]] binding BOOKS on the
   SITE worker; on status→ready, worker copies each output (runner /file GET) into
   R2 `tickets/<id>/…`; /api/download serves R2-first, runner-fallback.
3. **Per-ticket containers:** runner index.ts getContainer(ns, ticketId from path /t/BR-…) instead
   of fixed name; max_instances 5. (Route: parse ticket from URL before container.fetch.)
4. **Email via Cloudflare Email Service (public beta, on Workers Paid; NO Resend):** enable Email
   Sending on the zone (dash), add [[send_email]] binding to site wrangler.toml, rewrite afterPaid →
   env.EMAIL.send() from orders@bookraising.org (buyer receipt + owner copy); "book ready" mail with
   download link on ready; magic-link re-entry route reusing login_tokens table.
5. **Storefront copy (index.html):** hero → "Raise your book tonight — $5 founder build"; deliverables
   (PDF + EPUB + Kindle file + cover), ~15 min honest expectations, machine-refuses-mistakes line,
   rights attestation sentence, "returning? open your build" → /raise.
6. **ntfy pager:** fetch https://ntfy.sh/<topic in secret NTFY_TOPIC> on paid + stalled.
7. **Graduation:** stranger-sim ticket end-to-end (PDF downloaded), then Bo's real $5 on the phone.

## 5 · KNOWN LIMITS accepted for soft-launch
Mid-build container eviction loses the workspace (R2 snapshot of full workspace = later; downloads
durable after item 2). One build at a time per ticket (fine). Refunds manual in Stripe dashboard.
Rotate the booksmith_DEMO DeepSeek key (it appeared in chat) — replace runner secret when convenient.
Additions (2026-08-13, session C, far-end-confirmed): cover vision gate = SKIP in-container
(consciously accepted for the alpha; MVP spec demoted the perceptual gate to best-effort because
hypergen + deterministic compositing shrinks the surface; the ~50-line vision_verify
--backend claude-api adapter is the clean post-launch item). Concurrency = 5 customer builds
(max_instances 6 minus the shared proof instance); the 6th now gets a friendly 503 from
/api/commit instead of raw platform text. Unit-count band under-enforced: bands S=8/M=12/L=16
units — shim normalize forces words-per-unit but NOT unit count; next image lap should truncate
units to the band N after seed (deterministic; alpha floor caps cost regardless). hypergen mood
derives from genre → consecutive nonfiction tickets get similar earthy palettes (cosmetic).
`wrangler r2 bucket info` object_count lags reality — verify objects with `r2 object get`, never
the metric. Email ready-mail fail-opens until the one-time Email Sending zone enable + orders@
sender setup in the dash (2-min Bo step). Stripe live webhook endpoint registration in the Stripe
dashboard is UNVERIFIED (confirm-on-return is the primary paid-path and works without it).

## 6 · Session-continuation notes (2026-08-13, storefront finish in flight)
- **Lesson 12:** `build_digital_pdf` requires a PRINT interior by design; ebook-only tickets now
  fall back to rendering the KINDLE DOCX via soffice (commit on main). Digital PDF = honest
  reading copy, reflowable styling.
- DONE this pass: a10 image (libreoffice-writer + digital_pdf format), per-ticket container
  instances (name ticket-<id>-a10, max_instances 6), site worker gained sendMail (EMAIL binding)
  + pager (NTFY_TOPIC secret) + archiveOutputs->R2 on ready + R2-first /api/download, R2 bucket
  bookraising-books + BOOKS/EMAIL bindings, homepage hero rewritten ("Raise my book - $5 founder
  build", PDF-first deliverables, rights line, returning link).
- REMAINING: gate test green (in flight) -> push a10 + delete app + deploy runner -> deploy site
  worker -> secrets on SITE worker: OWNER_EMAIL (chen@finaltheoryofeverything.org), NTFY_TOPIC
  (generate; Bo subscribes ntfy.sh/<topic> on phone) -> Email Sending may need a one-time zone
  enable in the dash (code fail-opens if not) -> stranger-sim ticket incl. PDF download from R2
  -> Bo's real $5. raise.html: add PDF label mapping for *_DIGITAL.pdf in renderReady (tiny).

- **SESSION C CLOSE (2026-08-13 ~13:20 CT): storefront LIVE, stranger-sim PASSED.** Deployed:
  runner on :a10b (shim a10b, per-ticket instances ticket-<id>-a10b, digital re-fit fix in-image),
  site worker with R2 archival + EMAIL binding + ntfy pager + $5 hero (version f9aa972a). Sim
  BR-SIM901: brief → 12-unit outline → 12 chapters gated → 3 formats verified rc 0 → ready →
  R2 archive 5/5 → PDF(61pp all 432x648)/EPUB/DOCX downloaded; R2 direct-get byte-identical to
  /api/download. Remaining HUMAN steps: Bo subscribes ntfy.sh/<NTFY_TOPIC value> (topic name
  redacted at first public commit — an unauthenticated ntfy topic IS the pager secret);
  one-time Email Sending zone enable + orders@ sender; eyeball Stripe live webhook registration;
  then the real $5. After launch: rotate DeepSeek key + mint fresh DEMO/DEV tokens (re-put
  secrets AND rewrite dotfiles together per lesson 14).
- **Lesson 14 (session C):** deployed secrets vs local dotfiles drifted (or the `.dev_key`
  var-name trap: it defines DEVK=, not DEV_KEY= — sourcing it wrong sends an empty bearer that
  looks exactly like drift). Rule: the dotfiles are the truth; at any lap that touches auth,
  re-`wrangler secret put` from the files via `printf '%s' "$(tr -d ' \r\n' < file)"` (bash, never
  PowerShell echo) and only then debug. DEMO_TOKEN + RUNNER_TOKEN must always be the same value.
- **Lesson 15 (session C):** `env.BOOKS.put(key, r.body)` with a two-Worker-hop stream throws
  (unknown length) and the old bare `catch {}` ate it — the bucket stayed empty while downloads
  worked via runner-fallback, i.e. the durability promise was silently broken. Fix: buffer small
  artifacts (`await r.arrayBuffer()`), surface the result IN-BAND (`s.archive` on /api/status),
  page on any failure (throw or !r.ok). Corollary: worker deploys propagate lazily — a poll fired
  seconds after `wrangler deploy` can execute the OLD version; trust the in-band receipt, never
  the deploy timestamp. And `wrangler tail` buffers when piped — in-band beats tail for proofs.
- **Lesson 16 (far-end warning, now standing rule):** with per-ticket instance names,
  `wrangler containers delete` kills EVERY live customer build mid-flight. The delete-and-redeploy
  recipe was safe when instances were disposable; from now on swap images only when
  `wrangler containers list` shows no live ticket instances (deploy-modify-in-place + a new
  instance-name suffix already forces fresh pulls without any delete).
- **RE-ENTRY PHASE 1 LIVE (2026-08-21, site worker `abe3e6dc`):** magic-link sign-in shipped per
  `cloud/DESIGN_reentry_revisions.md` §3.3.1; plan+results `cloud/PLAN_REENTRY_PHASE1_2026-08-21.md`.
  New: D1 `login_tokens` (30-min single-use, sha256-only) + `POST /api/auth/{request,redeem,logout}`;
  redeem = atomic one-winner → re-mints `br_sess` for the newest ticket under `orders.email`
  (tickets JOIN orders — no schema migration); raise.html no-session view gained "email me a
  sign-in link" + `?login=` landing (token stripped via replaceState); coupon redeem now captures
  an OPTIONAL email into `orders.email` (free users become recoverable). Live battery V1-V11 ALL
  PASS (redeem/reuse/garbage/expired/logout/regression). `/api/auth/request` answers an honest 502
  until the Email-Sending zone enable — the token row is already purged+minted correctly, so the
  flow goes fully live with ZERO code change the moment the zone + orders@ sender are enabled.
  Adopted defaults (Bo may veto): coupon email optional; most-recent-ticket on redeem (picker =
  Phase 2); sign-in folded into /raise; no recovery link for the alpha. Dev artifact BR-AUTH01
  (auth test lane) left in D1 like the sims.
- **Lesson 18 (2026-08-21):** `wrangler d1 execute --remote --file` fails `Authentication error
  [code: 10000]` on this OAuth token — the D1 *import* API wants a scope the token lacks; the
  query path is fine. Ship D1 deltas as `--command` (or re-login if a bulk import is ever needed).
- **QC PASS + FIX DEPLOY (2026-08-17, site worker `90723bd7`):** full-loop QC
  (`cloud/QC_STOREFRONT_2026-08-16.md`; plan+results `cloud/PLAN_QC_FIX_2026-08-16.md`).
  Fixed+verified live: H2 homepage reflected-XSS via `?order=`; H1 ready-listing death after
  container eviction (status now serves `ready` from R2, `source:"r2"`, never wakes the
  container — proven on BR-SIM901 3 days cold); M1 stage gates + note-less-reroll counting
  (closes the free-rebuild loop); L6 one-winner ready flip; outline `{{TEMPLATE}}` scrub;
  M3 gitignore for `.dev_key`/`.test_cookies`/`_receipts`. Fresh sim BR-QC0816: rc 0 in 365 s,
  archive 5/5, ~$0.02, PDF 31 pp all exactly 432×648 pt. Queued for image lap a11: shim
  busy-gates on `/init`+`/file` PUT, fail-closed runner auth when DEMO_TOKEN unset, proper
  intent extraction, upload short-read guard. OPEN QUESTION: in-container `authorial_act`
  FAILed (66h/66f) yet the build proceeded to ready — confirm advisory-by-design in the MVP
  spec or make it blocking.
- **Lesson 17 (2026-08-17):** the deployed DEV_KEY is the dotfile's ENTIRE content INCLUDING
  its `DEVK=` prefix — the lesson-14 printf recipe strips whitespace only, so the prefix is
  part of the secret. Parsing out the "value" after `=` sends the wrong key and 403s exactly
  like drift. THE FILE BYTES ARE THE SECRET. (Also: stale-isolate deploy propagation bit a
  post-deploy negative test — a 200 from the OLD version seconds after deploy, 409 one minute
  later. Retry negatives; trust in-band version markers, never the deploy timestamp.)
- **Lesson 13 (named at end of session B, FIXED session C 2026-08-13):** `digital_pdf_structure`
  failed on ebook-only tickets — the kindle-DOCX fallback renders via soffice at A4
  (595.3x841.9 pt; Word would render it Letter), and the gate demands exact 432x648 on every
  page. Fix: `refit_interior_to_trim()` in build_digital_pdf — after ensure_interior_pdf, any
  non-6x9 interior is vector re-fit page-by-page onto a 432x648 canvas via fitz show_pdf_page
  (aspect-fit, centered, the pdf_replica_fit pattern); 6x9 interiors pass through byte-untouched
  so every print-format book is unaffected. The gate was NOT relaxed. Micro-proof: synthetic A4
  3pp -> exact 432x648 with text intact + trim passthrough asserted. Full proof: lt4 lap on a10b.

- **H0 LAP a12 (2026-08-24, in flight this entry): manual editing + per-unit AI revise + full-workspace
  archive land end-to-end** (plan `cloud/PLAN_H0_2026-08-24.md`; kit commit ca45938). **Shim a12:**
  `GET/PUT /t/<id>/unit/<uid>` (the human's editor, via `_tools/manual_edit.py` — H1 locked, photo
  lines protected, append-only versions, authorship-ledger row actor=human) · `POST /revise`
  {unit_id, note} (E-2 note append → `--only draft:<uid> --force-stage` → `--from integrate`; ai
  ledger row) · `POST /rebuild` (`--from integrate` only — FREE, no model) · `GET /manifest`
  (rel+sha256 of every workspace file) · `POST /rehydrate?path=` (restore into a cold container) ·
  `/file` GET widened to any workspace path (jail unchanged). **THE CASCADE FENCE (bind it):** after
  any human edit, a BARE engine pass would redraft downstream units (prior-prose input hash) — every
  post-ready verb is a targeted invocation, never bare. **Worker:** `/api/book` `/api/unit` (GET+PUT)
  `/api/revise` (3 free per ticket, D1 `tickets.revisions`) `/api/rebuild`; full-workspace R2 archive
  (sha-skipped via customMetadata) on ready + after saves/revises; `rehydrateIfCold` before post-ready
  verbs; ready-listing scoped to `outputs/` (the workspace archive would otherwise render as
  downloads); revise/rebuild failures return the ticket to READY (previous book intact — stalled stays
  reserved for a first build). **raise.html:** chapter list + on-screen editor ("Save my edit" — free,
  attributed "edited by you") + per-chapter "Rewrite it for me" + "Rebuild my files — free".
  **TAVUS SEAMS (design only, Bo 2026-08-24):** `tickets.intake_mode` (T1 onboarding) ·
  `note_source` on /api/revise (T2 voice revision) · `SUPPORT_MODE` at the stalled path (T3 support
  escalation before the owner). NO Tavus integration — carve-outs only. **NO connector/scanner**
  (privacy/legal hold; uploads stay user-initiated). **Lint law D2:** units whose latest ledger actor
  is human print HUMAN-EDIT ADVISORY and never gate (a dash a human typed is their voice); an AI
  re-draft re-arms the gate. Local proofs: 11/11 H0 battery, smoketest A–L, selfcheck 0-fail, image
  grep + in-image py_compile (lesson 10). D1: `revisions` + `intake_mode` columns applied --remote.
  Deploys: runner 9ae8870e (image :a12, per-ticket suffix -a12, optional CF_AI_TOKEN /
  ANTHROPIC_API_KEY pass-throughs for workers-ai FLUX covers + claude-api vision), site 15dc9f2c.
  Battery: see the entry below this one when it lands.
- **H0 BATTERY RUN 1 (2026-08-24, ticket BR-9UH2BV, a12): 16/18 PASS — the loop is real, and the
  two FAILs bought lesson 23.** Fresh dev ticket → 8-unit outline 31 s → full build 5.5 min →
  workspace archive 53/53 → chapter fetched (8,453 chars) → **manual edit saved** (v1 versions +
  base, ledger row actor=human +2 lines, incremental re-archive 5 stored/52 sha-skipped) → free
  rebuild rc 0 (23 s, no model tokens) → **AI revise rc 0** (56 s incl. the model call; counter 1/3;
  ai ledger row with before/after shas + the note; human flag preserved on ch_01). FAIL 1
  (`ledger-human`) = battery-script artifact only: a ONE-row JSONL parses as a single JSON object
  and PowerShell auto-objectifies it — the row itself was verified perfect by direct fetch. FAIL 2
  was REAL: the marker reached `current`, masters v2/v3, and the kindle DOCX, but **not the digital
  PDF** — see lesson 23. Fix lap a12b (commit a3ac8c3) rebuilt/pushed/deployed same session
  (runner 8d635b68, site fc041fd0); retest record follows this entry.
- **H0 RETEST (2026-08-24, a12b, BR-9UH2BV): 7/7 PASS — the lap closes green.** Runner on :a12b
  (worker 8d635b68, site fc041fd0). The retest ran against a COLD container by construction (the
  -a12b instance suffix starts empty), so `rebuild-start` taking 14 s IS the receipt for
  `rehydrateIfCold` — the full workspace restored from R2 before the verb ran: **the eviction path
  is now live-proven**, not just designed. Then: rebuild rc 0 in 69 s cold → **the customer's
  hand-written line present in the container's digital PDF** (lesson-23 fix a: fresh interior
  re-render) → **and in the R2-first site download** (fix b: unconditional archive puts) → human
  flag + revision counter intact (human=ch_01, used=1). H0's shipped surface as of this entry:
  manual editing (free, attributed), per-unit AI revise (3 free), free rebuild, durable full-
  workspace archive + rehydrate, Tavus seams (fields only), workers-ai FLUX + claude-api vision
  wired but DORMANT until their secrets exist (CF_AI_TOKEN / ANTHROPIC_API_KEY on the runner —
  optional, config-gated). Dev rows BR-9UH2BV left in D1 like the sims. Still-owed human steps
  unchanged: Email-Sending zone enable + orders@ sender; Stripe live-webhook eyeball.
- **H0.1 — THE EMAIL RAIL IS LIVE (2026-08-24 night, site worker `ef6cd3e5`): RESEND, not the
  zone-enable.** Bo supplied a Resend API key; `bookraising.org` was ALREADY VERIFIED in the Resend
  account (domain id c437a606…, DNS pre-done), so the long-owed Email-Sending zone enable is moot.
  worker.js: `sendResend()` (throws on failure) + `sendMail` now Resend-first with the EMAIL
  binding as fallback (still fail-open for receipts/ready-mail); `authRequest` magic-link sends
  via Resend and keeps its fail-LOUD 502. Secret `RESEND_API_KEY` on the site worker (lesson-14
  printf recipe; local dotfile `C:\Websites\bookraising\.resend_key` = the truth; the folder is
  NOT a git repo). Proofs: direct API send accepted (id 6f776514…) + live `/api/auth/request`
  through the deployed worker returned `{ok:true}` on the fail-loud path = a REAL sign-in mail
  delivered. **Receipts, ready-mail, and magic-link re-entry are all live.** Remaining owed human
  steps shrink to: Stripe live-webhook eyeball + ntfy subscription confirm. Pre-change snapshots:
  `_backups/pre_resend_<ts>/` (worker.js, raise.html, wrangler.toml).
- **Lesson 23 (the existence-cache class — bind it everywhere):** an "exists → skip" cache is only
  correct for immutable artifacts; the moment ANY verb can regenerate a key in place, the test must
  be "FRESH → skip" (mtime/sha), or the first rebuild serves build-#1 bytes forever. It bit TWICE
  in one lap, in both halves of the stack: (a) `build_digital_pdf.ensure_interior_pdf` returned any
  existing paperback PDF — which, in the ebook-only fallback, is its OWN build-#1 soffice render of
  the kindle DOCX (fix: reuse only when the PDF mtime ≥ the source DOCX mtime); (b) the worker's
  `archiveOutputs` head-skipped existing R2 keys, so revised artifacts never re-archived and the
  R2-first download stayed stale after the container slept (fix: unconditional puts). Audit any
  future cache with one question: *what regenerates this, and does the skip see it?*

- **IMAGE LAP a11 → a11b → a11c (2026-08-21, runner NOW on :a11c, worker version 0405c17d):**
  the four QC-queued items closed, plus one found live. **a11:** shim busy-gates on `/init` +
  `/file` (409 `{"error":"busy"}` while any job runs — QC #4), runner auth FAIL-CLOSED
  (missing DEMO_TOKEN → 503 "locked", never open — QC M2), outline intent scrubbed AT SOURCE
  (mid-line `{{TOKENS}}` stripped; the worker-side scrub in apiOutlineGet stays as
  belt+suspenders), upload short-read guard (received != Content-Length → 400 + connection
  close, no partial file — QC L10). **a11b — found preparing the lane: the shim never spoke
  PUT.** worker.js apiIntake uploads with `method:"PUT"`; BaseHTTPRequestHandler answers
  unknown verbs 501 (HTML) — every real customer intake upload was dead on arrival since the
  first deploy, invisible because NO sim ever uploaded a file. `do_PUT` now routes
  `/t/<id>/file` into the same `_file_put` as the POST compat path. **Lesson 21: a sim lane
  must exercise every verb the site actually sends — a green lane that skips a path proves
  nothing about that path.** **a11c:** the live lane showed the a11 scrub kills tokens but
  seed §1 is template-SHAPED (empty-slot fragments "Success means the reader .", bullet
  labels "- **Sentence rhythm:**" survive line filters) — intent is customer-facing, so it
  now prefers the customer's own brief text (prose-clean by construction), scrubbed-seed
  fallback only (also drops `-`/digit-prefixed lines). Proven by unit tests + in-image probe
  battery (14/14: marker, PUT/POST upload, PUT non-file 404, short-read 400 + no partial
  file, busy 409 on init/file during a live job); `{"shim":"a11c"}` verified in-band
  post-rollout.
- **Lane BR-A11B01 (a11b, S band, WITH an intake upload this time):** marker `{"shim":"a11b"}`
  in-band → brief → intake `field_notes.txt` stored 152 bytes THROUGH the site (PUT front
  door live; a10b answered 501 here) → outline 8 units, intent token-free → busy proofs
  mid-outline (direct POST /init and PUT /file both `{"error":"busy","job":"outline"}`) →
  commit → build **rc 0, 19/19 stages** (~12 min wall incl. the intake ingest), ledger 10
  calls / 26,140 in / 14,998 out tokens (~$0.02) → **archive 5/5 err null** (lesson-15
  receipt) → status served `source:"r2"` → all 5 artifacts downloaded via /api/download:
  **digital PDF 33 pp, every page exactly 432.0x648.0** + EPUB + KINDLE.docx + cover.
  Fail-closed auth verified by review + dry-run compile only (a live test would mean
  deleting the production secret — not done). Dev rows BR-A11B01 left in D1 like the sims.
- **Lesson 19 (wrangler containers push now 401s → native push recipe):** `npx wrangler
  containers push --path-to-docker docker-wsl.exe` dies at registry login (daemon: 401 on
  /v2/) even though the credentials API mints 201 (wrangler 4.122; bridge stdin path
  suspected, not root-caused). PROVEN workaround, all inside WSL in ONE bash -c (staged
  scripts die — see lesson 22): grep `oauth_token` from `.wrangler/config/default.toml`,
  POST `accounts/<acct>/containers/registries/registry.cloudflare.com/credentials` body
  `{"expiration_minutes":15,"permissions":["push","pull"]}`, pipe the returned password via
  `printf '%s'` into `docker login registry.cloudflare.com --username <u> --password-stdin`,
  then `docker tag booksmith-cf:aN registry.cloudflare.com/<acct>/booksmith-cf:aN` +
  `docker push` (pushed digest must equal the local image id). Two freshness rules: the
  stored OAuth access token goes stale in ~15-30 min — run any wrangler command (whoami)
  immediately before the mint; the minted registry credential lives 15 min — push right away.
- **Lesson 20 (in-place image swap semantics — the delete recipe stays retired):**
  `wrangler deploy` with a changed [containers] image = worker-version upload + app ROLLOUT.
  (a) `wrangler deployments list` prints OLDEST-first — read the tail. (b) in
  `containers info`, `configuration.image` + `active_rollout_id` flip only when the rollout
  COMPLETES; `health.instances.starting` shows the replacement waves; ~10-15 quiet minutes
  for 6 idle instances. (c) THE RACE: any request to the NEW instance-name suffix while the
  rollout is still active provisions the fresh DO from the OLD config — the new name answers
  the OLD shim and pins there (bit this lap: runner-a11 answered a10b for its whole life; the
  actual a11 code first ran as :a11b under runner-a11b). Rule: after deploy, send ZERO runner
  traffic until `containers info` shows the new image + rollout null; only then the first
  in-band marker poll. Lesson-16 quiet-window held: 0 in-flight tickets at every deploy, no
  `containers delete` used.
- **Lesson 22 (Windows↔WSL lap plumbing):** WSL `/tmp` does not survive between wsl.exe
  invocations reliably (VM recycle wipes staged scripts silently — a missing-file stderr
  piped into a grep looks like an empty result; the a11c push ran once with NO login that
  way). Inline multi-step WSL work in one `bash -c`, or re-stage from /mnt/c every call.
  And in Git Bash, `$(... | python -c "print(...)")` on Windows emits \r line ends —
  filenames built from it get CR-tainted and NTFS refuses them; pipe through `tr -d '\r'`.
- Also this lap: session-C ntfy topic name redacted at first public commit (an
  unauthenticated ntfy topic IS the pager secret); M3 gitignore fix committed
  (.dev_key / .test_cookies / _receipts/); cloud QC/PLAN/DESIGN records +
  cloud/worker/package-lock.json now tracked. QC items #4, M2, L10 + intent-leak: CLOSED.
