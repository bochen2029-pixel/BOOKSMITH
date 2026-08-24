#!/usr/bin/env python3
"""cover_gen_workers_ai.py — generative cover art via Cloudflare Workers AI (FLUX).

H0 (cloud/PLAN_H0_2026-08-24.md §3 A4): the cloud's text-to-image path. No GPU,
no ComfyUI — one HTTPS call to the account's Workers AI binding. Same discipline
as every generator in this kit:

  * NO TITLE/AUTHOR TEXT IN THE ART (typography is composited afterward); the
    prompt carries the no-lettering guard and the config title/author are
    refused if found inside the prompt.
  * sha-bound provenance sidecar (method "workers_ai_flux") via cover_gen's own
    write_provenance — the fact verify_build's --final gate trusts.
  * NO SILENT FALLBACK. A declared generative method that cannot generate is a
    loud exit 1 (the §20.3 lesson: silent degradation of provenance is the
    whole failure class this gate exists to kill). Retries are bounded here.

Env: CF_ACCOUNT_ID + CF_API_TOKEN (Workers AI scope). Optional CF_FLUX_MODEL
(default @cf/black-forest-labs/flux-1-schnell).

  python _tools/cover_gen_workers_ai.py --config book_config.json --out cover_art/x_src.png [--seed N] [--steps 4..8]
"""
from __future__ import annotations

import argparse
import base64
import io
import json
import os
import sys
import time
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from cover_gen import write_provenance  # noqa: E402

DEFAULT_MODEL = "@cf/black-forest-labs/flux-1-schnell"
NO_LETTERING = ("no text, no letters, no words, no typography, no watermark, "
                "no signature, no captions")
ATTEMPTS = 3


def build_prompt(cfg: dict) -> str:
    art = (cfg.get("cover", {}) or {}).get("art", {}) or {}
    seed_prompt = str(art.get("prompt_seed") or "").strip()
    if not seed_prompt:
        palette = ", ".join((cfg.get("cover", {}) or {}).get("palette", []) or [])
        genre = str(cfg.get("genre") or "book")
        seed_prompt = (f"an evocative, tasteful abstract book cover background for a "
                       f"{genre}; painterly, atmospheric, calm upper third"
                       + (f"; palette {palette}" if palette else ""))
    return f"{seed_prompt}. {NO_LETTERING}."


def generate(cfg_path: Path, out: Path, seed: int | None, steps: int) -> dict:
    cfg = json.loads(cfg_path.read_text("utf-8"))
    prompt = build_prompt(cfg)
    # the no-baked-text rule, enforced at the prompt: never ask for the title
    for guarded in (str(cfg.get("title") or ""), str(cfg.get("author") or "")):
        if guarded and len(guarded) > 3 and guarded.lower() in prompt.lower():
            print(f"[cover_gen_workers_ai] refusing: prompt contains the book's "
                  f"own {'title' if guarded == cfg.get('title') else 'author'} "
                  f"({guarded!r}) — art must carry no lettering", file=sys.stderr)
            raise SystemExit(1)

    acct = os.environ.get("CF_ACCOUNT_ID", "").strip()
    token = os.environ.get("CF_API_TOKEN", "").strip()
    if not acct or not token:
        print("[cover_gen_workers_ai] CF_ACCOUNT_ID / CF_API_TOKEN not set — this "
              "generator only runs where the platform provides them", file=sys.stderr)
        raise SystemExit(1)
    model = os.environ.get("CF_FLUX_MODEL", DEFAULT_MODEL).strip() or DEFAULT_MODEL

    body: dict = {"prompt": prompt[:2000], "steps": max(1, min(int(steps), 8))}
    if seed is not None and seed >= 0:
        body["seed"] = int(seed)

    url = f"https://api.cloudflare.com/client/v4/accounts/{acct}/ai/run/{model}"
    last_err = "unknown"
    for attempt in range(1, ATTEMPTS + 1):
        try:
            req = urllib.request.Request(
                url, data=json.dumps(body).encode("utf-8"),
                headers={"authorization": f"Bearer {token}",
                         "content-type": "application/json"}, method="POST")
            with urllib.request.urlopen(req, timeout=120) as resp:
                ctype = resp.headers.get("content-type", "")
                raw = resp.read()
            if "application/json" in ctype:
                payload = json.loads(raw.decode("utf-8"))
                if not payload.get("success", True) and payload.get("errors"):
                    raise RuntimeError(str(payload["errors"])[:300])
                b64 = (payload.get("result") or {}).get("image") or ""
                if not b64:
                    raise RuntimeError("no image field in Workers AI response")
                img_bytes = base64.b64decode(b64)
            else:
                img_bytes = raw  # some image models stream raw bytes
            if len(img_bytes) < 10_000:
                raise RuntimeError(f"suspiciously small image ({len(img_bytes)} bytes)")
            from PIL import Image
            im = Image.open(io.BytesIO(img_bytes)).convert("RGB")
            out.parent.mkdir(parents=True, exist_ok=True)
            im.save(out, "PNG")
            record = {"model": model, "steps": body["steps"],
                      "seed": body.get("seed"), "prompt": prompt[:500],
                      "attempt": attempt, "px": f"{im.width}x{im.height}"}
            sidecar = write_provenance(out, "workers_ai_flux", record,
                                       recorded_by="cover_gen_workers_ai.py")
            return {"ok": True, "out": str(out), "sidecar": str(sidecar),
                    "model": model, "px": f"{im.width}x{im.height}",
                    "attempt": attempt}
        except Exception as e:  # noqa: BLE001 — every failure class retries, then exits loud
            last_err = f"{type(e).__name__}: {e}"
            print(f"[cover_gen_workers_ai] attempt {attempt}/{ATTEMPTS} failed: "
                  f"{last_err}", file=sys.stderr)
            if attempt < ATTEMPTS:
                time.sleep(2 * attempt)
    print(f"[cover_gen_workers_ai] FAILED after {ATTEMPTS} attempts: {last_err}. "
          f"No silent fallback: a declared generative cover either generates or "
          f"stops the build loudly.", file=sys.stderr)
    raise SystemExit(1)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--config", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--seed", type=int, default=-1, help="-1 = model chooses")
    ap.add_argument("--steps", type=int, default=6)
    args = ap.parse_args(argv)
    result = generate(Path(args.config).resolve(), Path(args.out),
                      None if args.seed < 0 else args.seed, args.steps)
    print(json.dumps(result))
    return 0


if __name__ == "__main__":
    sys.exit(main())
