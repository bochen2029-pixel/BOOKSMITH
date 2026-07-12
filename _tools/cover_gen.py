#!/usr/bin/env python3
r"""
cover_gen.py — AI cover-art generator for BOOKSMITH (ComfyUI via the hermes skill).

Generates FRONT-cover art from a Book-Bible-derived prompt. The composited
typography (title/author/spine) is added LATER by composite_cover.py — so the
HARD RULE enforced here is: NO title / author / lettering text in the image
prompt. The negative prompt always suppresses text/watermark/letters.

What it does:
  1. Reads machine paths from kit_env.json (cover_gen block): the hermes
     run_workflow.py, run_batch.py, workflows_dir, comfyui_server, comfyui_app,
     checkpoints_dir, default_checkpoint.
  2. Ensures the local ComfyUI daemon is up (`comfy launch --background` on :8188)
     unless it already answers /system_stats.
  3. Resolves the workflow graph (default sdxl_txt2img.json) and injects the
     requested checkpoint filename into the graph's CheckpointLoaderSimple node
     (the schema does NOT surface ckpt_name, so we patch the JSON directly).
  4. Shells to run_workflow.py with --args {prompt, negative_prompt, seed, steps}
     and --output-dir <cover_art>, parses its JSON, and returns the generated PNG
     path as JSON on stdout.
  5. run_batch subcommand: shells to run_batch.py --count N --randomize-seed for
     seed variations, returns all produced PNG paths as JSON.

I/O contract (single):
  python cover_gen.py \
    --prompt "<art prompt, NO title/author text>" \
    --negative "text, watermark, letters" \
    --workflow sdxl_txt2img.json \
    --seed -1 --steps 30 \
    --out cover_art/<slug>_src.png \
    [--config book_config.json]  [--kit-env kit_env.json]  [--no-launch]
  -> {"status":"success","png":"<abs path>","seed":<n>,"steps":<n>, ...}

I/O contract (batch):
  python cover_gen.py run_batch \
    --prompt "<art prompt>" --negative "..." --count 8 --steps 30 \
    --out-dir cover_art/ [--config ...] [--kit-env ...]
  -> {"status":"success","pngs":[...], "count":N}

SOURCE: a hermes-style ComfyUI runner skill (run_workflow.py, run_batch.py,
        workflows\sdxl_txt2img.json, flux_dev_txt2img.json) — every path is
        resolved via kit_env.cover_gen (historical provenance, not a runtime path).
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent

# COMMERCIAL-USE PROVENANCE: the shipped default checkpoint resolves to
# SDXL-base 1.0 (sd_xl_base_1.0.safetensors), released under the permissive
# CreativeML Open RAIL++-M license — generated art may be sold (e.g. KDP covers).
# Do NOT default this to FLUX.1-dev: its weights are NON-commercial. See
# docs/cover_pipeline.md for the full provenance/license note (fonts + art).
DEFAULT_NEGATIVE = "text, watermark, letters, title, signature, frame, border"

# Prompt-safety: tokens that signal the caller is asking the model to render
# words. These are rejected so a title/author string never gets painted in.
# NOTE: bare 'title'/'subtitle'/'author'/'text'/'word(s)' were removed — they
# collide with compositional idioms the kit's own shipped seeds use ("room for
# the title", "negative space for a title", "no text"). The remaining tokens are
# unambiguous requests to paint lettering. The config-driven check below (the
# book's literal title/author strings) stays as the real anti-baking guard.
TEXT_SIGNAL_TOKENS = (
    "byline", "lettering", "typography", "caption", "writing", "inscription",
    "signage", "book cover text", "cover text", "logo text", "nameplate",
)

# Negated / compositional phrases that must NOT trip the guard even though they
# contain a signal substring. Negated spans are stripped before scanning; the
# whitelist phrases suppress a flag on the surviving word 'title'.
_NEGATED_TEXT_SPANS = ("no text", "without text", "no lettering", "no title")
_TITLE_COMPOSITION_PHRASES = (
    "for a title", "for title placement", "title placement",
    "room for the title", "for the title", "quiet for title",
)


# ============================================================
# kit_env + config loading
# ============================================================
def load_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def load_kit_env(path: str | None) -> dict:
    p = Path(path).expanduser() if path else (SCRIPT_DIR / "kit_env.json")
    if not p.exists():
        raise FileNotFoundError(f"kit_env.json not found: {p}")
    return load_json(p)


# ============================================================
# Prompt safety — reject title/author/lettering in the ART prompt
# ============================================================
def check_prompt_no_text(prompt: str, config: dict | None) -> list[str]:
    """Return a list of violations if the prompt asks for baked text.

    Flags generic text-signal tokens AND the book's own title/author strings
    (so the exact cover title can't be requested inside the art).
    """
    violations: list[str] = []
    low = prompt.lower()

    # Strip negated spans so "no text" / "no title" cannot trip the guard.
    for span in _NEGATED_TEXT_SPANS:
        low = low.replace(span, "")

    for tok in TEXT_SIGNAL_TOKENS:
        if tok in low:
            violations.append(f"prompt contains text-signal token {tok.strip()!r}")

    if config:
        # If the prompt uses a compositional "…for the title" idiom, don't let a
        # book whose literal title happens to be that idiom's word false-fire.
        composition_ok = any(ph in low for ph in _TITLE_COMPOSITION_PHRASES)
        for key in ("title", "subtitle", "author"):
            val = (config.get(key) or "").strip()
            if val and len(val) >= 3 and val.lower() in low:
                if key == "title" and composition_ok and val.lower() in " ".join(_TITLE_COMPOSITION_PHRASES):
                    continue
                violations.append(f"prompt contains the book {key} {val!r} (would bake it as text)")

    return violations


def ensure_text_negatives(negative: str) -> str:
    """Guarantee the negative prompt suppresses text/watermark/letters."""
    neg = (negative or "").strip()
    if not neg:
        return DEFAULT_NEGATIVE
    low = neg.lower()
    needed = ["text", "watermark", "letters"]
    missing = [w for w in needed if w not in low]
    if missing:
        neg = neg.rstrip(", ") + ", " + ", ".join(missing)
    return neg


# ============================================================
# ComfyUI daemon lifecycle
# ============================================================
def server_up(server_url: str, timeout: float = 3.0) -> bool:
    """True if the ComfyUI server answers /system_stats."""
    url = server_url.rstrip("/") + "/system_stats"
    try:
        with urllib.request.urlopen(url, timeout=timeout) as r:
            return r.status == 200
    except (urllib.error.URLError, OSError, ValueError):
        return False


def launch_server(server_url: str, comfy_bin: str = "comfy",
                  wait_s: float = 90.0) -> bool:
    """Start the ComfyUI daemon via `comfy launch --background`, then poll.

    Returns True once the server answers. If `comfy` isn't on PATH, returns
    False (the caller decides whether that's fatal).
    """
    if server_up(server_url):
        return True
    if shutil.which(comfy_bin) is None:
        return False
    try:
        # comfy-cli daemonizes with --background; capture output so we don't
        # block on its pipes.
        subprocess.run(
            [comfy_bin, "launch", "--background"],
            check=False, capture_output=True, text=True, timeout=120,
        )
    except (subprocess.SubprocessError, OSError):
        return False
    deadline = time.time() + wait_s
    while time.time() < deadline:
        if server_up(server_url):
            return True
        time.sleep(2.0)
    return server_up(server_url)


# ============================================================
# Workflow resolution + checkpoint injection
# ============================================================
def resolve_workflow(workflow: str, workflows_dir: Path) -> Path:
    """Resolve a workflow name/path to an existing file.

    Accepts a bare filename (looked up under workflows_dir), a relative path,
    or an absolute path.
    """
    p = Path(workflow).expanduser()
    if p.is_absolute() and p.exists():
        return p
    # bare name or relative → try workflows_dir first, then CWD.
    cand = workflows_dir / workflow
    if cand.exists():
        return cand
    if p.exists():
        return p.resolve()
    raise FileNotFoundError(
        f"workflow not found: {workflow} (looked in {workflows_dir} and {Path.cwd()})"
    )


def patch_checkpoint(workflow_path: Path, checkpoint: str | None) -> Path:
    """Prepare the API-format graph for submission: STRIP non-node keys and
    optionally set the checkpoint, writing a temp copy.

    Community/skill workflow JSONs often carry a documentation key like
    '_comment' whose value is a string, not a node. ComfyUI's /prompt endpoint
    rejects the whole graph with "a node is missing the class_type property", so
    we keep ONLY real nodes (dict values carrying a class_type). We also set
    every CheckpointLoaderSimple.ckpt_name when a checkpoint is given (the schema
    does not surface ckpt_name as a param, so we patch the JSON directly).
    """
    graph = load_json(workflow_path)
    clean = {k: v for k, v in graph.items()
             if isinstance(v, dict) and "class_type" in v}
    dropped = [k for k in graph if k not in clean]
    if checkpoint:
        for node in clean.values():
            if node.get("class_type") == "CheckpointLoaderSimple":
                node.setdefault("inputs", {})["ckpt_name"] = checkpoint
    if not dropped and not checkpoint:
        return workflow_path
    tmp = Path(tempfile.mkdtemp(prefix="booksmith_wf_")) / workflow_path.name
    with tmp.open("w", encoding="utf-8") as f:
        json.dump(clean, f)
    return tmp


# ============================================================
# run_workflow.py shell
# ============================================================
def _extract_png(run_json: dict) -> str | None:
    """Pull the first image file path out of run_workflow.py's success JSON.

    run_workflow emits {"status":"success","outputs":[{"file":..,"type":"image"|..}]}.
    Prefer image-typed entries; fall back to any file with an image suffix.
    """
    outputs = run_json.get("outputs") or []
    if isinstance(outputs, dict):
        # Defensive: some paths return the raw comfy outputs dict.
        outputs = [outputs]
    image_exts = (".png", ".jpg", ".jpeg", ".webp")
    # Pass 1: explicitly image-typed
    for o in outputs:
        if isinstance(o, dict) and o.get("type") == "image" and o.get("file"):
            return o["file"]
    # Pass 2: any file with an image extension
    for o in outputs:
        if isinstance(o, dict):
            f = o.get("file") or ""
            if f.lower().endswith(image_exts):
                return f
    return None


def run_single(run_workflow_py: Path, workflow_path: Path, args_obj: dict,
               output_dir: Path, host: str, timeout: int) -> dict:
    """Shell to run_workflow.py, return its parsed JSON (last JSON line on stdout)."""
    output_dir.mkdir(parents=True, exist_ok=True)
    cmd = [
        sys.executable, str(run_workflow_py),
        "--workflow", str(workflow_path),
        "--args", json.dumps(args_obj),
        "--output-dir", str(output_dir),
        "--host", host,
    ]
    if timeout and timeout > 0:
        cmd += ["--timeout", str(timeout)]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    return _parse_runner_json(proc)


def run_batch_shell(run_batch_py: Path, workflow_path: Path, args_obj: dict,
                    output_dir: Path, host: str, count: int, timeout: int) -> dict:
    """Shell to run_batch.py --count N --randomize-seed."""
    output_dir.mkdir(parents=True, exist_ok=True)
    cmd = [
        sys.executable, str(run_batch_py),
        "--workflow", str(workflow_path),
        "--args", json.dumps(args_obj),
        "--count", str(count),
        "--randomize-seed",
        "--output-dir", str(output_dir),
        "--host", host,
    ]
    if timeout and timeout > 0:
        cmd += ["--timeout", str(timeout)]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    return _parse_runner_json(proc)


def _parse_runner_json(proc: subprocess.CompletedProcess) -> dict:
    """Parse the JSON the runner emits on stdout. The runner uses emit_json for
    its final result; be tolerant of leading log lines by scanning for the last
    parseable JSON object in stdout, else the whole thing."""
    out = (proc.stdout or "").strip()
    # Try whole-stdout first.
    for candidate in (out, _last_json_blob(out)):
        if not candidate:
            continue
        try:
            data = json.loads(candidate)
            if isinstance(data, dict):
                return data
        except json.JSONDecodeError:
            continue
    return {
        "status": "error",
        "error": "could not parse runner JSON",
        "returncode": proc.returncode,
        "stdout_tail": out[-1000:],
        "stderr_tail": (proc.stderr or "")[-1000:],
    }


def _last_json_blob(text: str) -> str | None:
    """Return the substring from the last top-level '{' to the final '}'."""
    if not text:
        return None
    end = text.rfind("}")
    if end == -1:
        return None
    depth = 0
    for i in range(end, -1, -1):
        c = text[i]
        if c == "}":
            depth += 1
        elif c == "{":
            depth -= 1
            if depth == 0:
                return text[i:end + 1]
    return None


# ============================================================
# High-level entry points
# ============================================================
def _resolve_cover_gen_paths(env: dict) -> dict:
    cg = env.get("cover_gen") or {}
    run_workflow = cg.get("run_workflow")
    workflows_dir = cg.get("workflows_dir")
    if not run_workflow or not workflows_dir:
        raise KeyError("kit_env.cover_gen must define run_workflow + workflows_dir")

    # Anchor non-absolute kit_env paths under the kit root (not the CWD), so a
    # relative workflows_dir/run_workflow (e.g. the vendored '_tools/…' defaults)
    # resolves the same from any working directory. Mirrors composite_cover.py's
    # FONTS_DIR anchoring. SCRIPT_DIR is _tools/; the kit root is its parent.
    def _anchor(p):
        if not p:
            return None
        pp = Path(p)
        return pp if pp.is_absolute() else (SCRIPT_DIR.parent / pp)

    run_workflow_p = _anchor(run_workflow)
    # run_batch.py sits next to run_workflow.py in the skill's scripts/ dir.
    run_batch_p = run_workflow_p.parent / "run_batch.py"
    return {
        "run_workflow": run_workflow_p,
        "run_batch": run_batch_p,
        "workflows_dir": _anchor(workflows_dir),
        "server": cg.get("comfyui_server", "http://127.0.0.1:8188"),
        "comfyui_app": cg.get("comfyui_app"),
        "checkpoints_dir": _anchor(cg.get("checkpoints_dir")),
        "default_checkpoint": cg.get("default_checkpoint", "sd_xl_base_1.0.safetensors"),
    }


def _default_checkpoint(config: dict | None, env_default: str) -> str:
    """Book config's cover.art.checkpoint wins over kit_env default."""
    if config:
        art = ((config.get("cover") or {}).get("art") or {})
        ck = art.get("checkpoint")
        if ck:
            return ck
    return env_default


def _default_workflow(config: dict | None, cli_workflow: str | None) -> str:
    if cli_workflow:
        return cli_workflow
    if config:
        art = ((config.get("cover") or {}).get("art") or {})
        wf = art.get("workflow")
        if wf:
            return wf
    return "sdxl_txt2img.json"


def _require_prompt(args) -> bool:
    """Emit an error + return False if --prompt was omitted (validated here
    rather than via argparse required=True — see build_parser note)."""
    if not (args.prompt and args.prompt.strip()):
        print(json.dumps({"status": "error", "error": "--prompt is required"}))
        return False
    return True


def _cover_gen_env_error(e: KeyError) -> int:
    """Structured status-error for a misconfigured kit_env.cover_gen (task 11)."""
    print(json.dumps({
        "status": "error",
        "error": str(e),
        "hint": "Fill kit_env.cover_gen.run_workflow + workflows_dir (the vendored "
                "defaults point at _tools/comfy_client.py + _tools/workflows), or "
                "skip AI art generation and place your own cover art in the book's "
                "cover_art/ folder — composite_cover.py and vision_verify.py still work.",
    }, indent=2))
    return 1


def _apply_art_defaults(args, config: dict | None) -> None:
    """Default any unset CLI knob from book_config.cover.art (task 10), so
    prompt_seed/negative_prompt/steps/seed in the config drive generation when
    the corresponding CLI flag is omitted (single source of knobs)."""
    art = ((config or {}).get("cover") or {}).get("art") or {}
    if not art:
        return
    if not args.prompt and art.get("prompt_seed"):
        args.prompt = art["prompt_seed"]
    if args.negative == DEFAULT_NEGATIVE and art.get("negative_prompt"):
        args.negative = art["negative_prompt"]
    if getattr(args, "steps", None) == 30 and "steps" in art:
        args.steps = art["steps"]
    if getattr(args, "seed", None) == -1 and "seed" in art:
        args.seed = art["seed"]


def do_single(args) -> int:
    env = load_kit_env(args.kit_env)
    config = load_json(Path(args.config)) if args.config else None
    _apply_art_defaults(args, config)
    if not _require_prompt(args):
        return 2
    try:
        paths = _resolve_cover_gen_paths(env)
    except KeyError as e:
        return _cover_gen_env_error(e)

    # ---- prompt safety ----
    violations = check_prompt_no_text(args.prompt, config)
    if violations:
        print(json.dumps({
            "status": "error",
            "error": "prompt requests baked text — cover art must contain NO title/author/lettering",
            "violations": violations,
        }, indent=2))
        return 2

    negative = ensure_text_negatives(args.negative)
    checkpoint = args.checkpoint or _default_checkpoint(config, paths["default_checkpoint"])
    workflow_name = _default_workflow(config, args.workflow)

    # ---- resolve workflow + inject checkpoint ----
    try:
        workflow_path = resolve_workflow(workflow_name, paths["workflows_dir"])
    except FileNotFoundError as e:
        print(json.dumps({"status": "error", "error": str(e)}))
        return 1
    effective_wf = patch_checkpoint(workflow_path, checkpoint)

    # ---- ensure server ----
    if not args.no_launch:
        if not launch_server(paths["server"]):
            print(json.dumps({
                "status": "error",
                "error": f"ComfyUI server not reachable at {paths['server']} and could not "
                         "auto-launch it (comfy-cli not on PATH). Start ComfyUI so it serves "
                         f"{paths['server']}, or install comfy-cli, or pass --no-launch once it "
                         "is running. Note: the vendored comfy_client.py is a CLIENT only and "
                         "cannot start a server.",
                "hint": f"A checkpoint must be present in {paths['checkpoints_dir']}.",
            }, indent=2))
            return 1
    elif not server_up(paths["server"]):
        print(json.dumps({
            "status": "error",
            "error": f"ComfyUI server not reachable at {paths['server']} (--no-launch set)",
        }))
        return 1

    # ---- run ----
    out_path = Path(args.out).expanduser()
    output_dir = out_path.parent if out_path.suffix else out_path
    args_obj = {
        "prompt": args.prompt,
        "negative_prompt": negative,
        "seed": args.seed,
        "steps": args.steps,
    }
    run_json = run_single(paths["run_workflow"], effective_wf, args_obj,
                          output_dir, paths["server"], args.timeout)

    if run_json.get("status") != "success":
        print(json.dumps({"status": "error", "error": "workflow run failed",
                          "runner": run_json}, indent=2))
        return 1

    png = _extract_png(run_json)
    if not png:
        print(json.dumps({"status": "error", "error": "no image in runner outputs",
                          "runner": run_json}, indent=2))
        return 1

    # ---- rename to the requested --out target if it names a file ----
    final_png = png
    if out_path.suffix:
        try:
            out_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(png, out_path)
            final_png = str(out_path.resolve())
        except OSError:
            final_png = png  # keep the runner's location if the move fails

    print(json.dumps({
        "status": "success",
        "png": str(Path(final_png).resolve()),
        "seed": args.seed,
        "steps": args.steps,
        "checkpoint": checkpoint,
        "workflow": str(workflow_path),
        "negative_prompt": negative,
        "prompt_id": run_json.get("prompt_id"),
    }, indent=2))
    return 0


def do_batch(args) -> int:
    env = load_kit_env(args.kit_env)
    config = load_json(Path(args.config)) if args.config else None
    _apply_art_defaults(args, config)
    if not _require_prompt(args):
        return 2
    try:
        paths = _resolve_cover_gen_paths(env)
    except KeyError as e:
        return _cover_gen_env_error(e)

    violations = check_prompt_no_text(args.prompt, config)
    if violations:
        print(json.dumps({
            "status": "error",
            "error": "prompt requests baked text — cover art must contain NO title/author/lettering",
            "violations": violations,
        }, indent=2))
        return 2

    negative = ensure_text_negatives(args.negative)
    checkpoint = args.checkpoint or _default_checkpoint(config, paths["default_checkpoint"])
    workflow_name = _default_workflow(config, args.workflow)

    try:
        workflow_path = resolve_workflow(workflow_name, paths["workflows_dir"])
    except FileNotFoundError as e:
        print(json.dumps({"status": "error", "error": str(e)}))
        return 1
    effective_wf = patch_checkpoint(workflow_path, checkpoint)

    if not args.no_launch:
        if not launch_server(paths["server"]):
            print(json.dumps({
                "status": "error",
                "error": f"ComfyUI server not reachable at {paths['server']} and could not "
                         "auto-launch it (comfy-cli not on PATH). Start ComfyUI so it serves "
                         f"{paths['server']}, or install comfy-cli, or pass --no-launch once it "
                         "is running. Note: the vendored comfy_client.py is a CLIENT only and "
                         "cannot start a server.",
            }, indent=2))
            return 1
    elif not server_up(paths["server"]):
        print(json.dumps({
            "status": "error",
            "error": f"ComfyUI server not reachable at {paths['server']} (--no-launch set)",
        }))
        return 1

    if not paths["run_batch"].exists():
        print(json.dumps({"status": "error",
                          "error": f"run_batch.py not found at {paths['run_batch']}"}))
        return 1

    output_dir = Path(args.out_dir).expanduser()
    # Base args for the batch; run_batch.py assigns a fresh seed per run.
    args_obj = {
        "prompt": args.prompt,
        "negative_prompt": negative,
        "steps": args.steps,
    }
    run_json = run_batch_shell(paths["run_batch"], effective_wf, args_obj,
                               output_dir, paths["server"], args.count, args.timeout)

    # run_batch.py aggregates per-run results; collect every image path we can find.
    pngs = _collect_batch_pngs(run_json)
    if not pngs:
        print(json.dumps({"status": "error", "error": "batch produced no images",
                          "runner": run_json}, indent=2))
        return 1

    print(json.dumps({
        "status": "success",
        "pngs": pngs,
        "count": len(pngs),
        "checkpoint": checkpoint,
        "workflow": str(workflow_path),
        "negative_prompt": negative,
    }, indent=2))
    return 0


def _collect_batch_pngs(run_json: dict) -> list[str]:
    """Walk run_batch.py's aggregate JSON for every produced image path.

    run_batch emits a 'runs' (or 'results') list; each entry mirrors a
    run_workflow result with an 'outputs' list. Be tolerant of shape.
    """
    image_exts = (".png", ".jpg", ".jpeg", ".webp")
    found: list[str] = []

    def _harvest(outputs) -> None:
        if isinstance(outputs, dict):
            outputs = [outputs]
        if not isinstance(outputs, list):
            return
        for o in outputs:
            if isinstance(o, dict):
                f = o.get("file") or ""
                if f.lower().endswith(image_exts) and f not in found:
                    found.append(str(Path(f).resolve()))

    # Top-level outputs (single-shape) …
    _harvest(run_json.get("outputs"))
    # … and nested per-run lists.
    for key in ("runs", "results", "batch"):
        seq = run_json.get(key)
        if isinstance(seq, list):
            for entry in seq:
                if isinstance(entry, dict):
                    _harvest(entry.get("outputs"))
    return found


# ============================================================
# CLI
# ============================================================
def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="BOOKSMITH AI cover-art generator (ComfyUI via the hermes skill). "
                    "NO title/author text is allowed in the art prompt.",
    )
    sub = p.add_subparsers(dest="command")

    # ---- shared options factory ----
    # NOTE: --prompt is deliberately NOT required at parse time. argparse routes
    # bare options to the PARENT parser, so a required parent --prompt would make
    # `cover_gen.py run_batch --prompt ...` fail (the subparser's --prompt hasn't
    # been consumed yet). Presence is validated in the command handlers instead.
    def add_common(sp, batch: bool):
        sp.add_argument("--prompt", default=None,
                        help="Art prompt (REQUIRED). MUST NOT request title/author/lettering text.")
        sp.add_argument("--negative", default=DEFAULT_NEGATIVE,
                        help="Negative prompt (text/watermark/letters are force-added).")
        sp.add_argument("--workflow", default=None,
                        help="Workflow name/path (default from config or sdxl_txt2img.json).")
        sp.add_argument("--checkpoint", default=None,
                        help="Checkpoint filename override (default from config/kit_env).")
        sp.add_argument("--steps", type=int, default=30, help="Sampler steps.")
        sp.add_argument("--config", default=None, help="book_config.json (title/author guard + defaults).")
        sp.add_argument("--kit-env", default=None, help="kit_env.json (machine paths).")
        sp.add_argument("--timeout", type=int, default=0, help="Runner timeout seconds (0=auto).")
        sp.add_argument("--no-launch", action="store_true",
                        help="Do not auto-launch ComfyUI; fail if the server is down.")

    # single (default command)
    add_common(p, batch=False)
    p.add_argument("--seed", type=int, default=-1, help="Seed (-1 = randomize).")
    p.add_argument("--out", default="cover_art/cover_src.png",
                   help="Output PNG path (or dir). File suffix => rename runner output to it.")

    # run_batch subcommand
    bp = sub.add_parser("run_batch", help="Generate N seed variations.")
    add_common(bp, batch=True)
    bp.add_argument("--count", type=int, default=8, help="Number of seed variations.")
    bp.add_argument("--out-dir", default="cover_art/", help="Directory for the variation PNGs.")

    return p


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "run_batch":
        return do_batch(args)
    return do_single(args)


if __name__ == "__main__":
    sys.exit(main())
