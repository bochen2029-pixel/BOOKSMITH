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

- **Lesson 13 (named at end of session B, FIXED session C 2026-08-13):** `digital_pdf_structure`
  failed on ebook-only tickets — the kindle-DOCX fallback renders via soffice at A4
  (595.3x841.9 pt; Word would render it Letter), and the gate demands exact 432x648 on every
  page. Fix: `refit_interior_to_trim()` in build_digital_pdf — after ensure_interior_pdf, any
  non-6x9 interior is vector re-fit page-by-page onto a 432x648 canvas via fitz show_pdf_page
  (aspect-fit, centered, the pdf_replica_fit pattern); 6x9 interiors pass through byte-untouched
  so every print-format book is unaffected. The gate was NOT relaxed. Micro-proof: synthetic A4
  3pp -> exact 432x648 with text intact + trim passthrough asserted. Full proof: lt4 lap on a10b.
