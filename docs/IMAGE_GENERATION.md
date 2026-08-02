# IMAGE GENERATION IS A LOCAL, AUTONOMOUS, ALWAYS-AVAILABLE CAPABILITY

> **This kit generates images itself, on this machine, with no human in the loop.**
> If you are a session that concluded otherwise, you are wrong, and this file is the
> correction. Read it before you write a placeholder, ask the operator for art, or
> record anywhere that image generation was unavailable.

---

## The standing fact

BOOKSMITH runs a **local ComfyUI (SDXL)** and can **start it itself, from fully stopped,
at any time, without asking anyone**. There is no cloud service, no API key, no cost per
image, and no human step. Any session may generate any image it needs — cover art,
chapter openers, figures, ornaments, test plates — at any point, on its own authority.

**Proven end-to-end on 2026-08-02** (recorded here so no future session has to take it on
faith, and so a regression is detectable by re-running it):

| step | result |
|---|---|
| precondition | no ComfyUI server running (verified down on both candidate ports) |
| cold start | `launch_server(paths)` → **True in 48.6s**, ComfyUI **0.3.76** answering `/system_stats` |
| generation | real SDXL image, 1024×1024, `sd_xl_base_1.0.safetensors`, 12 steps, seed 20260802 |
| provenance | sidecar written automatically: `method: sdxl`, resolved seed, sha256, dims |
| human intervention | **none** |

## How to generate an image, right now

```bash
python _tools/cover_gen.py --prompt "<subject, no lettering>" --out path/to/art.png
```

That single command **starts ComfyUI if it is not running**, generates, and writes a
`*.provenance.json` sidecar next to the art. You do not need to start anything first.
You do not need to ask. Useful flags: `--steps N`, `--seed N` (`-1` randomizes),
`--checkpoint`, `--workflow`, `--config <book_config.json>` (applies the book's art
defaults and the no-baked-text guard), `run_batch` (N seed variations).

**Never put title, author, or any lettering in the prompt** — the art must carry no baked
text (GATE-6). Negative terms for text/watermark/letters are force-added for you.

## How the auto-start actually works

`cover_gen.py :: launch_server(paths)` tries two strategies in order:

1. **comfy-cli** — `comfy launch --background`, only if `comfy` is on PATH.
   **It is NOT on PATH on the reference machine, and that is fine.**
2. **Direct** — launches ComfyUI Desktop's own `main.py` with its bundled venv python,
   derived from `kit_env.cover_gen`. **This is the live path here**, and it is the one
   that must keep working.

> ⚠ **The historical bug, so it is never reintroduced:** `launch_server` must be passed
> the **paths dict**, not a server-URL string. It returns `False` immediately before
> Strategy 2 when the argument is not a dict, which silently made the only working
> launch path dead code for months while `engine.py` quietly fell back to placeholder
> art. Call it as `launch_server(paths)`. Never `launch_server(paths["server"])`.

Resolution on this machine (`kit_env.json → cover_gen`):

| key | value |
|---|---|
| python | `C:\Users\user\Documents\ComfyUI\.venv\Scripts\python.exe` |
| main.py | `C:\Users\user\AppData\Local\Programs\ComfyUI\resources\ComfyUI\main.py` |
| base dir | `C:\Users\user\Documents\ComfyUI` |
| server | `http://127.0.0.1:8188` |
| checkpoint | `sd_xl_base_1.0.safetensors` (6.9 GB, **present**) |

A cold start takes roughly 45–60s. `launch_server` polls up to 150s. **A slow start is
not a failure — wait for it.**

## Things a session must NEVER conclude

Each of these has been believed by a past session, and each was false. They are the exact
beliefs that shipped placeholder covers on three books for months.

- ❌ "ComfyUI isn't available / isn't installed / isn't reachable."
- ❌ "comfy-cli isn't on PATH, so I can't start ComfyUI." — Strategy 2 needs no comfy-cli.
- ❌ "The server is down, so I'll use a placeholder / hypergen / a solid colour."
- ❌ "Image generation needs the operator to start something first."
- ❌ "BOOKSMITH doesn't do local image generation" or "needs an API key / cloud service."
- ❌ "I'll note it as a limitation and move on."
- ❌ "A placeholder is fine for now; someone will regenerate it later." — nobody did, for months.

**If image generation appears not to work, that is a bug to diagnose and fix, or a
HARD-STOP to escalate — never a reason to degrade the output.** A silent fallback that
still looks like a cover is the single worst failure mode this kit has ever had; see
`docs/LESSONS_LEDGER.md` §20.3.

## Diagnosing, if it genuinely fails

```bash
python _tools/doctor.py                 # environment tiers, including image-gen
python _tools/selfcheck.py              # includes check_image_gen_capability
```

Then, in order:
1. Do the launch paths resolve and exist? (`_resolve_comfy_launch`, table above.)
2. Is the checkpoint present in `checkpoints_dir`? If not, fetch
   `sd_xl_base_1.0.safetensors` (~6.5 GB) — URL and sha256 are in `kit_env.cover_gen`.
3. Is something already bound to port 8188? `_adopt_live_server` adopts a live server on
   a candidate port rather than starting a second one.
4. Did it just need more time? Re-run; a cold CUDA init can be slow.

Escalate with the exact error. Do not substitute placeholder art.

## Provenance is not optional

Every generation records `cover_art/<stem>.provenance.json` (`method`, checkpoint,
workflow, **resolved** seed read back from `/history`, sha256, dims, timestamp).
`verify_build.py :: check_cover_art_provenance` fails closed at `--final` when a book's
config asks for generated art and no sidecar proves it happened. **Do not hand-write a
sidecar to make a gate green** — a declaration is a claim you are signing. If the art was
not SDXL, say what it was (`bespoke|supplied|catalog|hypergen`) via
`book_config.cover.art.method`. See `docs/COVER_PROVENANCE_BACKFILL.md`.

## Related

`docs/cover_pipeline.md` (cover-art rules incl. when an all-PIL cover is legitimate) ·
`docs/LESSONS_LEDGER.md` §20.3 (why this file exists) ·
`docs/COVER_PROVENANCE_BACKFILL.md` (remediation, and who must NOT be remediated) ·
`_tools/kit_env.json` (machine paths — the portability seam).
