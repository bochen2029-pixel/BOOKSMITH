# cloud/ — BOOKSMITH in a Linux container (P0)

The kit's cloud transposition starts here. `Dockerfile` builds the **public tracked tree**
(exactly what a stranger clones) into a Linux image that proves the engine cold:

```bash
# 1) stage the public tree (never the working copy — WIP stays out of the proof)
mkdir -p /tmp/booksmith-src && git archive HEAD | tar -x -C /tmp/booksmith-src
mkdir -p /tmp/booksmith-src/cloud && cp cloud/Dockerfile /tmp/booksmith-src/cloud/

# 2) build
docker build -t booksmith-p0 -f /tmp/booksmith-src/cloud/Dockerfile /tmp/booksmith-src

# 3) prove it (the P0 gates)
docker run --rm booksmith-p0                              # engine smoketest A..L -> PASS
docker run --rm booksmith-p0 python _tools/selfcheck.py   # kit meta-gate -> 0 FAIL
```

**P0 receipts (2026-08-12, docker 29.1.3 in WSL Ubuntu-24.04):** smoketest scenarios A–L all
PASS in-container; selfcheck 0 fail / 1 warn (the warn = this-machine image-gen probe, absent
`kit_env.json`, WARN-by-design); the tracked `testvoyage` reference book re-assembled and
produced kindle DOCX + EPUB (`all_pass: true`) inside the container with no mounts.

**Live model proof (same night):** a 2-chapter micro-book ran brief → architect (GATE-2) →
draft (per-unit gates) → integrate (lint + authorial_act) → assemble against a real cloud
model API via the engine's `openai` backend — configured entirely by env, no code changes:

```bash
docker run --rm \
  -e OPENAI_API_KEY=$YOUR_KEY \
  -e BOOKSMITH_MODEL_BACKEND=openai \
  -e BOOKSMITH_MODEL_ID=<any OpenAI-compatible model id> \
  -e BOOKSMITH_MODEL_BASE_URL=<provider base url> \
  -e BOOKSMITH_TOKEN_BUDGET=200000 \
  booksmith-p0 bash -c "python _tools/engine.py --config <ws>/book_config.json --backend openai --to assemble"
```

Two operational rules learned live (bind them in any cloud runner):
1. **Outline phase stops at `--to precheck`** (the bracketed ingest/seed front-half runs before
   it; `--to seed` does not bound the run).
2. **A one-shot service must normalize unit classes to C after seed** — the architect model may
   mark units A/B (human-authored classes), and the engine will correctly refuse to draft them.

Tier coverage: this image is Tier 2 (kindle/EPUB/covers/verification glue + non-book domains).
Tier-1 print (Word COM) never runs on Linux — it routes to a queued Windows worker. The
LibreOffice Tier-2.5 experiment ships as a later layer, not in the P0 image.

## P0.75 — the same proof, ON Cloudflare (2026-08-12, same night)

`Dockerfile.cf` layers `shim.py` (a fixed-job HTTP face: only `smoketest` and `selfcheck`,
by name — never an arbitrary executor) onto the P0 image; `worker/` is the thinnest
possible Worker + `@cloudflare/containers` binding (bearer-token gated, one instance,
scale-to-zero after 15m idle).

```bash
docker build -t booksmith-cf:p0 -f cloud/Dockerfile.cf <staged-tree>
npx wrangler containers push booksmith-cf:p0        # (Windows: --path-to-docker <docker bridge>)
cd cloud/worker && npm install && npx wrangler deploy
printf "%s" "<token>" | npx wrangler secret put DEMO_TOKEN
curl -H "Authorization: Bearer <token>" -X POST https://<worker>.workers.dev/run/smoketest
curl -H "Authorization: Bearer <token>"         https://<worker>.workers.dev/status
```

**On-platform receipts (Cloudflare Containers, `basic` instance):** engine smoketest A–L
**PASS in 20.2s**; selfcheck **0 FAIL** (the one by-design WARN) in 15.2s; unauthenticated
requests 401. Zero platform blockers encountered end-to-end (registry push, provisioning,
cold start, execution). The engine's crash-safe disk-state design means container eviction
is just another resume.

What runs on top of this image (Worker, D1, R2, ticket runner, the one-shot purchase loop) is
specced privately in `docs/CLOUD_ONESHOT_MVP_SPEC.md`; the full architecture lives in
`docs/CLOUD_HORIZON_v6.md` Part XII (both local-only).
