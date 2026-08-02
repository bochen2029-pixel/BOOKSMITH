#!/usr/bin/env python3
r"""
vision_verify.py — perceptual verifier (image + rubric -> verdict JSON) (BOOKSMITH).

PURPOSE (KIT_ARCHITECTURE (c) vision_verify.py; LESSONS_LEDGER §6.5)
    The perceptual half of the cover loop (GATE-6 / GATE-7). Judges an image
    against a rubric a mechanical check cannot see:
      - cover ART: no baked title/author text, subject + palette match the
        Bible, focal room for the title;
      - composited WRAP: title/author legible + correctly spelled, tracking
        clean, spine centered, bleed-safe, ISBN keep-out clear.

    Two backends:
      keel  (default $0 on-box): resize <=2000px, then POST an OpenAI-format
            /v1/chat/completions to the KEEL llama-server (Qwen3.5-9B + mmproj)
            with the image as a base64 data-URI image_url part; read
            choices[0].message.content and parse a verdict out of it.
      claude: resize <=2000px and PRINT the safe path + rubric as JSON for the
            harness to read the image with its own vision and return a verdict.

    ALWAYS returns/prints a single JSON object:
        {"verdict":"PASS|FAIL","issues":[...],"ocr":"..."}
    (claude backend adds {"backend":"claude","image":<safe path>,"rubric":...,
     "verdict":"PENDING"} — the harness fills the verdict in.)

CONTRACT
    python vision_verify.py --image <png> --rubric <rubric.txt|inline text>
                            [--backend auto|keel|claude] [--config kit_env.json]
                            [--start-server] [--timeout 120] [--max-tokens 1024]

    Machine paths (llama_server, qwen_model, mmproj, host, port, start_cmd)
    are read from kit_env.json -> "vision"; NEVER hard-coded. The resize step
    calls resize_image_safe.py (repo-relative). If no --config is given, the
    script looks for kit_env.json next to itself.

BACKEND WIRING (mechanisms/vision_keel.md)
    llama-server.exe --model <qwen> --mmproj <proj> --host <h> --port <p>
        --jinja --n-gpu-layers 99 --ctx-size 16384
    POST http://<h>:<p>/v1/chat/completions  (OpenAI shape)
        messages:[{role:user, content:[
            {type:text,  text:<rubric>},
            {type:image_url, image_url:{url:"data:image/png;base64,<b64>"}}]}]
    read choices[0].message.content.
    --mmproj is THE vision switch; --jinja required for the thinking toggle.
    NOTE: grammar/json_schema and thinking are mutually exclusive — we request
    the verdict in the prompt and parse it, and set enable_thinking:false so the
    answer is lean/deterministic (no GBNF, so no 400).

SOURCE
    C:\\Claude-Titanic\\_kit_research\\mechanisms\\vision_keel.md (§1.A/§1.B)
    C:\\BOOKSMITH\\_tools\\resize_image_safe.py (the <=2000px guard)
"""
import argparse
import base64
import json
import re
import subprocess
import sys
import time
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_KIT_ENV = SCRIPT_DIR / "kit_env.json"
RESIZE_HELPER = SCRIPT_DIR / "resize_image_safe.py"

# The default rubric if the caller passes none — the wrap-verify checklist.
DEFAULT_RUBRIC = (
    "You are an OCR + book-cover layout verifier. First, transcribe EVERY line "
    "of text visible in this image verbatim. Then judge it against these rules: "
    "(1) the title and author are legible and correctly spelled; "
    "(2) letter tracking looks clean and even; "
    "(3) if a spine is visible, its text is centered; "
    "(4) no text is clipped by or too close to any edge (bleed-safe); "
    "(5) the bottom-right ISBN barcode keep-out area is clear of text. "
    "End your answer with a single line: 'VERDICT: PASS' if every rule holds, "
    "otherwise 'VERDICT: FAIL' followed by a short reason for each failed rule."
)


def emit(obj: dict) -> None:
    """Print the single JSON contract object to stdout."""
    print(json.dumps(obj, ensure_ascii=False))


def load_kit_env(config_path: Path) -> dict:
    with config_path.open(encoding="utf-8") as fh:
        return json.load(fh)


def resize_safe(image: Path) -> Path:
    """Run resize_image_safe.py and return the safe (<=2000px) path. Falls back
    to the original path if the helper is missing or fails non-fatally."""
    if not RESIZE_HELPER.exists():
        return image
    try:
        proc = subprocess.run(
            [sys.executable, str(RESIZE_HELPER), str(image)],
            capture_output=True, text=True, timeout=120,
        )
    except (subprocess.SubprocessError, OSError):
        return image
    out = (proc.stdout or "").strip().splitlines()
    if proc.returncode == 0 and out:
        candidate = Path(out[-1].strip())
        if candidate.exists():
            return candidate
    return image


def read_rubric(rubric_arg: str) -> str:
    """A rubric arg is a path to a text file if it exists, else inline text."""
    if not rubric_arg:
        return DEFAULT_RUBRIC
    p = Path(rubric_arg)
    if p.exists() and p.is_file():
        return p.read_text(encoding="utf-8").strip()
    return rubric_arg


def mime_for(path: Path) -> str:
    ext = path.suffix.lower()
    if ext in (".jpg", ".jpeg"):
        return "image/jpeg"
    if ext == ".webp":
        return "image/webp"
    return "image/png"


def data_uri(path: Path) -> str:
    b64 = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime_for(path)};base64,{b64}"


# ─────────────────────────────────────────────────────────────────────────────
# KEEL backend
# ─────────────────────────────────────────────────────────────────────────────

def server_healthy(host: str, port: int, timeout: float = 3.0) -> bool:
    import requests
    try:
        r = requests.get(f"http://{host}:{port}/health", timeout=timeout)
        return r.status_code == 200
    except requests.RequestException:
        return False


def wait_for_health(host: str, port: int, deadline_s: float) -> bool:
    end = time.time() + deadline_s
    while time.time() < end:
        if server_healthy(host, port):
            return True
        time.sleep(2.0)
    return False


def start_server(vision_cfg: dict) -> None:
    """Launch the KEEL llama-server detached, using start_cmd from kit_env if
    present, else reconstructing the argv from the pinned fields."""
    start_cmd = vision_cfg.get("start_cmd")
    if start_cmd:
        # start_cmd is a full command line; run it detached.
        subprocess.Popen(start_cmd, shell=True)
        return
    exe = vision_cfg.get("llama_server")
    model = vision_cfg.get("qwen_model")
    mmproj = vision_cfg.get("mmproj")
    host = str(vision_cfg.get("host", "127.0.0.1"))
    port = str(vision_cfg.get("port", 8080))
    if not (exe and model and mmproj):
        raise RuntimeError("kit_env.vision is missing llama_server/qwen_model/mmproj "
                           "and no start_cmd is set; cannot launch the vision server.")
    argv = [exe, "--model", model, "--mmproj", mmproj,
            "--host", host, "--port", port,
            "--jinja", "--n-gpu-layers", "99", "--ctx-size", "16384"]
    subprocess.Popen(argv)


def parse_verdict(content: str) -> dict:
    """Extract {verdict, issues, ocr} from the model's free-text answer.
    Prefers a trailing 'VERDICT: PASS/FAIL ...' line; the whole content is
    returned as ocr (it contains the verbatim transcription the rubric asks
    for). If the model emitted a JSON object, prefer that."""
    content = (content or "").strip()

    # If the model returned a JSON object with a verdict, honor it.
    stripped = content
    if stripped.startswith("```"):
        # strip a fenced block
        stripped = stripped.strip("`")
        if "\n" in stripped:
            stripped = stripped.split("\n", 1)[1]
    try:
        obj = json.loads(stripped)
        if isinstance(obj, dict) and ("verdict" in obj or "legible" in obj):
            verdict = str(obj.get("verdict", "")).upper()
            if not verdict:
                verdict = "PASS" if obj.get("legible") else "FAIL"
            issues = obj.get("issues", [])
            if isinstance(issues, str):
                issues = [issues]
            return {"verdict": "PASS" if verdict.startswith("PASS") else "FAIL",
                    "issues": list(issues),
                    "ocr": obj.get("ocr", content)}
    except (json.JSONDecodeError, ValueError):
        pass

    verdict = "FAIL"
    issues = []
    # Find the last explicit VERDICT line.
    verdict_line = None
    for line in content.splitlines():
        if "verdict" in line.lower():
            verdict_line = line
    if verdict_line is not None:
        vl = verdict_line.lower()
        # PASS requires a WHOLE-WORD 'pass' (a bare substring like "passengers"
        # must not read as PASS) and no 'fail' anywhere on the line. FAIL stays a
        # lenient substring match — the fail-safe direction — so a run-together
        # "FAILfaint" still registers as FAIL.
        if re.search(r"\bpass\b", vl) and "fail" not in vl:
            verdict = "PASS"
        elif "fail" in vl:
            verdict = "FAIL"
            reason = verdict_line.split(":", 1)[-1].strip()
            # Strip a leading 'FAIL' prefix (run-together or word-bounded) —
            # NOT lstrip(), which drops every leading char in {F,A,I,L}.
            reason = re.sub(r"^\s*fail", "", reason, flags=re.IGNORECASE).strip(" -–—:")
            if reason:
                issues.append(reason)
    else:
        # No explicit VERDICT line — fail safe. Never infer PASS from a stray
        # 'pass' substring in OCR text.
        verdict = "FAIL"
        issues.append("model emitted no explicit VERDICT line; defaulting to FAIL")

    return {"verdict": verdict, "issues": issues, "ocr": content}


def run_keel(image: Path, rubric: str, vision_cfg: dict,
             max_tokens: int, timeout: float, allow_start: bool) -> dict:
    import requests

    host = str(vision_cfg.get("host", "127.0.0.1"))
    port = int(vision_cfg.get("port", 8080))

    if not server_healthy(host, port):
        if allow_start:
            try:
                start_server(vision_cfg)
            except RuntimeError as exc:
                return {"verdict": "FAIL",
                        "issues": [f"vision server not up and could not start: {exc}"],
                        "ocr": ""}
            if not wait_for_health(host, port, deadline_s=180):
                return {"verdict": "FAIL",
                        "issues": [f"vision server at {host}:{port} did not become "
                                   f"healthy within 180s"],
                        "ocr": ""}
        else:
            return {"verdict": "FAIL",
                    "issues": [f"KEEL vision server not reachable at {host}:{port}/health. "
                               f"Start it (kit_env.vision.start_cmd) or pass --start-server."],
                    "ocr": ""}

    body = {
        "model": "qwen3.5-9b",  # cosmetic — llama-server serves its single model
        "max_tokens": max_tokens,
        "temperature": 0,
        # thinking OFF for a lean deterministic answer (no GBNF, so no 400).
        "chat_template_kwargs": {"enable_thinking": False},
        "messages": [{
            "role": "user",
            "content": [
                {"type": "text", "text": rubric},
                {"type": "image_url", "image_url": {"url": data_uri(image)}},
            ],
        }],
    }
    try:
        r = requests.post(f"http://{host}:{port}/v1/chat/completions",
                          json=body, timeout=timeout)
    except requests.RequestException as exc:
        return {"verdict": "FAIL",
                "issues": [f"POST to vision server failed: {exc}"], "ocr": ""}

    if r.status_code != 200:
        return {"verdict": "FAIL",
                "issues": [f"vision server returned HTTP {r.status_code}: {r.text[:200]}"],
                "ocr": ""}
    try:
        payload = r.json()
        content = payload["choices"][0]["message"]["content"]
    except (ValueError, KeyError, IndexError, TypeError) as exc:
        return {"verdict": "FAIL",
                "issues": [f"could not parse vision response: {exc}"], "ocr": ""}

    return parse_verdict(content)


# ─────────────────────────────────────────────────────────────────────────────
# Claude backend (resize + hand off to the harness)
# ─────────────────────────────────────────────────────────────────────────────

def run_claude(image: Path, rubric: str) -> dict:
    """The harness reads the (already-resized) image from disk with its own
    vision and applies the rubric. We return a PENDING envelope carrying the
    safe path + rubric; the caller/harness fills in the verdict."""
    return {
        "backend": "claude",
        "verdict": "PENDING",
        "issues": [],
        "ocr": "",
        "image": str(image),
        "rubric": rubric,
        "note": "Claude backend: Read the 'image' path with vision, apply "
                "'rubric', then emit {verdict, issues, ocr}.",
    }


def _resolve_auto_backend(config_path: Path) -> str:
    """Portable default: 'keel' only when kit_env.vision names a local server
    binary that actually exists on this machine AND requests is importable;
    otherwise 'claude' (the harness's own vision — zero local setup)."""
    try:
        import requests  # noqa: F401
    except ImportError:
        print("[vision_verify] note: 'requests' unavailable — auto backend "
              "downgraded keel->claude", file=sys.stderr)
        return "claude"
    try:
        vision = load_kit_env(config_path).get("vision", {}) if config_path.exists() else {}
    except Exception:
        return "claude"
    if not vision:
        return "claude"
    if str(vision.get("backend", "keel")).strip().lower() == "claude":
        return "claude"
    server = str(vision.get("llama_server", ""))
    if server and Path(server).exists():
        # C-21 slice (2026-08-02): a binary on disk is not a live verifier.
        # Probe the configured endpoint; ANY HTTP answer (even 503-loading)
        # proves liveness, a connection failure downgrades to claude so GATE-6
        # stays adjudicable instead of erroring against a stopped server.
        host = str(vision.get("host") or "127.0.0.1")
        port = int(vision.get("port") or 8080)
        try:
            requests.get(f"http://{host}:{port}/health", timeout=2)
            return "keel"
        except Exception:                                          # noqa: BLE001
            print(f"[vision_verify] note: KEEL binary present but {host}:{port} "
                  f"is not answering — auto backend downgraded keel->claude "
                  f"(start it via kit_env.vision.start_cmd for $0 on-box verify)",
                  file=sys.stderr)
            return "claude"
    if server:
        # a configured local verifier silently vanishing must be visible
        print(f"[vision_verify] note: kit_env.vision.llama_server not found on "
              f"disk ({server}) — auto backend downgraded keel->claude",
              file=sys.stderr)
    return "claude"


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

    ap = argparse.ArgumentParser(
        description="Perceptual cover/wrap verifier (image + rubric -> verdict JSON).")
    ap.add_argument("--image", required=True, help="Path to the image (PNG/JPG).")
    ap.add_argument("--rubric", default="",
                    help="Rubric text file path OR inline rubric text. "
                         "Defaults to the wrap-verify checklist.")
    ap.add_argument("--backend", choices=["auto", "keel", "claude"], default="auto",
                    help="auto (default) = keel when kit_env.vision names a local "
                         "server binary that exists on this machine, else claude "
                         "(the portable zero-setup path); "
                         "keel = local Qwen ($0 on-box); "
                         "claude = resize + hand to harness vision.")
    ap.add_argument("--config", default=str(DEFAULT_KIT_ENV),
                    help="Path to kit_env.json (machine paths). "
                         "Default: kit_env.json next to this script.")
    ap.add_argument("--start-server", action="store_true",
                    help="If the KEEL vision server is not up, launch it "
                         "(via kit_env.vision.start_cmd) and wait for /health.")
    ap.add_argument("--timeout", type=float, default=120.0,
                    help="Per-request timeout in seconds (keel backend).")
    ap.add_argument("--max-tokens", type=int, default=1024,
                    help="max_tokens for the verdict response (keel backend).")
    args = ap.parse_args()

    image = Path(args.image)
    if not image.exists():
        emit({"verdict": "FAIL", "issues": [f"image not found: {image}"], "ocr": ""})
        return 2

    rubric = read_rubric(args.rubric)

    # ALWAYS resize first (the 2000px ingestion guard applies to both backends).
    safe_image = resize_safe(image)

    backend = args.backend
    if backend == "auto":
        backend = _resolve_auto_backend(Path(args.config))

    if backend == "claude":
        emit(run_claude(safe_image, rubric))
        # exit 4 = PENDING: the verdict is deferred to the harness. Distinct
        # from 0 so a naive returncode check can never read an UNFILLED
        # perceptual verdict as a PASS.
        return 4

    # keel backend
    config_path = Path(args.config)
    if not config_path.exists():
        emit({"verdict": "FAIL",
              "issues": [f"kit_env config not found: {config_path}"], "ocr": ""})
        return 2
    try:
        kit_env = load_kit_env(config_path)
    except (json.JSONDecodeError, OSError) as exc:
        emit({"verdict": "FAIL",
              "issues": [f"could not parse kit_env {config_path}: {exc}"], "ocr": ""})
        return 2

    vision_cfg = kit_env.get("vision", {})
    if not vision_cfg:
        emit({"verdict": "FAIL",
              "issues": ["kit_env.json has no 'vision' section"], "ocr": ""})
        return 2

    try:
        import requests  # noqa: F401
    except ImportError:
        emit({"verdict": "FAIL",
              "issues": ["requests not installed (pip install requests)"], "ocr": ""})
        return 2

    result = run_keel(safe_image, rubric, vision_cfg,
                      max_tokens=args.max_tokens, timeout=args.timeout,
                      allow_start=args.start_server)
    emit(result)
    return 0


if __name__ == "__main__":
    sys.exit(main())
