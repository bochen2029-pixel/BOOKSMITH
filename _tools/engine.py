#!/usr/bin/env python3
r"""
engine.py — the DETERMINISTIC BOOKSMITH engine (control inversion).

Every failure in this kit's history came from one place: a model *session* being
the engine of the pipeline, holding sequence, state, and discipline in its head
across a long horizon. The parts that never failed are the gates and the disk.

So this inverts control. This file is the engine: plain, deterministic code that

  * holds the stage sequence explicitly (no model decides "what's next"),
  * owns ALL state on disk (_engine/state.json), keyed by content hashes,
  * calls the model as a PURE FUNCTION (model_client.complete: prose in, prose
    out; no tools, no memory, no discretion),
  * runs EVERY gate itself (the real gate scripts + in-code checks), with a
    bounded retry loop, and a structured HARD-STOP when a gate cannot pass,
  * can crash at any point and resume from disk with ZERO orientation tokens —
    on restart it reads state.json, re-derives the next action by hashing inputs,
    and continues. No "let me re-read everything to figure out where I am."

Stages (fixed order):  precheck -> draft:<unit>* -> integrate -> assemble
                       -> produce:<format>* -> [cover] -> verify -> emit

Usage:
  python _tools/engine.py --config <book_config.json> [--backend mock|anthropic|openai]
                          [--to STAGE] [--from STAGE] [--dry-run] [--no-cover]
                          [--status] [--fresh]

--dry-run  = backend defaults to mock + external-service stages (cover art) are
             skipped, but every mechanical gate still runs. This is how you
             verify the machine without burning a real book generation.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import model_client  # noqa: E402

TOOLS = Path(__file__).resolve().parent
ROOT = TOOLS.parent


# ---------------------------------------------------------------------------
# small deterministic helpers
# ---------------------------------------------------------------------------
def now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def sha_text(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8", "replace")).hexdigest()[:16]


def sha_file(p: Path) -> str:
    if not p.exists():
        return "-"
    return hashlib.sha256(p.read_bytes()).hexdigest()[:16]


def load_json(p: Path) -> dict:
    return json.loads(p.read_text(encoding="utf-8"))


def save_json_atomic(p: Path, obj) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_suffix(p.suffix + ".tmp")
    tmp.write_text(json.dumps(obj, indent=2, ensure_ascii=False), encoding="utf-8")
    tmp.replace(p)  # atomic on the same volume — a crash never leaves half a file


def run(cmd: list, cwd: Path | None = None, timeout: int = 900) -> tuple[int, str, str]:
    """Run a subprocess; return (rc, stdout, stderr). Never raises on nonzero."""
    try:
        r = subprocess.run(cmd, cwd=str(cwd or ROOT), capture_output=True,
                           text=True, timeout=timeout)
        return r.returncode, r.stdout, r.stderr
    except FileNotFoundError as e:
        return 127, "", f"executable not found: {e}"
    except subprocess.TimeoutExpired:
        return 124, "", f"timeout after {timeout}s"


# ---------------------------------------------------------------------------
# state — the single source of "where am I", on disk, hash-keyed
# ---------------------------------------------------------------------------
class State:
    def __init__(self, path: Path, slug: str, config_sha: str):
        self.path = path
        self.data = {"slug": slug, "config_sha": config_sha, "stages": {},
                     "created": now(), "updated": now()}
        if path.exists():
            try:
                self.data = load_json(path)
            except Exception:
                pass  # corrupt state -> start clean (disk is truth, but a torn file is not)
        self.data.setdefault("stages", {})

    def rec(self, key: str) -> dict:
        return self.data["stages"].get(key, {})

    def is_satisfied(self, key: str, input_sha: str) -> bool:
        r = self.rec(key)
        return r.get("status") == "done" and r.get("input_sha") == input_sha

    def mark(self, key: str, status: str, input_sha: str = "", gate: str = "",
             attempts: int = 0, detail: str = "") -> None:
        self.data["stages"][key] = {
            "status": status, "input_sha": input_sha, "gate": gate,
            "attempts": attempts, "detail": detail[:500], "ts": now(),
        }
        self.data["updated"] = now()
        save_json_atomic(self.path, self.data)


class HardStop(Exception):
    def __init__(self, stage: str, detail: str):
        self.stage, self.detail = stage, detail
        super().__init__(f"HARD-STOP at {stage}: {detail}")


# ---------------------------------------------------------------------------
# the engine
# ---------------------------------------------------------------------------
class Engine:
    def __init__(self, config_path: Path, backend: str | None, dry_run: bool,
                 no_cover: bool):
        self.config_path = config_path.resolve()
        self.cfg = load_json(self.config_path)
        self.slug = self.cfg["slug"]
        self.dry_run = dry_run
        self.no_cover = no_cover or dry_run
        # workspace = the folder that holds this book_config.json
        self.ws = self.config_path.parent
        self.eng_dir = self.ws / "_engine"
        self.eng_dir.mkdir(parents=True, exist_ok=True)
        self.state = State(self.eng_dir / "state.json", self.slug, sha_file(self.config_path))
        # kit_env for the model seam
        kit_env = {}
        for cand in (TOOLS / "kit_env.json", TOOLS / "kit_env.template.json"):
            if cand.exists():
                try:
                    kit_env = load_json(cand)
                    break
                except Exception:
                    pass
        if dry_run and not backend:
            backend = "mock"
        self.model = model_client.make_client(
            kit_env, log_dir=self.eng_dir / "calls", backend_override=backend)
        self.log_path = self.eng_dir / "log.jsonl"

    # -- logging ----------------------------------------------------------
    def log(self, event: str, **kw) -> None:
        line = json.dumps({"ts": now(), "event": event, **kw}, ensure_ascii=False)
        with self.log_path.open("a", encoding="utf-8") as f:
            f.write(line + "\n")
        print(f"[engine] {event}: " + " ".join(f"{k}={v}" for k, v in kw.items()))

    # -- unit list --------------------------------------------------------
    def units(self) -> list[dict]:
        us = self.cfg.get("units")
        if us:
            return us
        # fall back to existing manuscript files (for a book already drafted)
        cur = sorted((self.ws / "manuscript" / "current").glob("*_current.md"))
        return [{"id": p.stem.replace("_current", ""), "title": "", "class": "C"} for p in cur]

    # -- the ordered stage plan -------------------------------------------
    def plan(self) -> list[tuple[str, str]]:
        """Return the ordered list of (stage_key, kind)."""
        steps = [("precheck", "precheck")]
        for u in self.units():
            steps.append((f"draft:{u['id']}", "draft"))
        steps.append(("integrate", "integrate"))
        steps.append(("assemble", "assemble"))
        for fmt in self.cfg.get("formats", []):
            steps.append((f"produce:{fmt}", "produce"))
        if not self.no_cover:
            steps.append(("cover", "cover"))
        steps.append(("verify", "verify"))
        steps.append(("emit", "emit"))
        return steps

    # -- context pack (deterministic, from disk) --------------------------
    def draft_inputs_sha(self, unit: dict) -> str:
        uid = unit["id"]
        contract = self.ws / "contracts" / f"{uid}.md"
        prior = self._prior_prose_path(uid)
        seed = self.ws / "seed.md"
        blob = "|".join([
            sha_file(contract), sha_file(prior), sha_file(seed),
            sha_text(json.dumps(unit, sort_keys=True)),
            str(self.cfg.get("voice", {})),
        ])
        return sha_text(blob)

    def _prior_prose_path(self, uid: str) -> Path:
        us = [u["id"] for u in self.units()]
        if uid in us:
            i = us.index(uid)
            if i > 0:
                return self.ws / "manuscript" / "current" / f"{us[i-1]}_current.md"
        return self.ws / "manuscript" / "current" / "__none__.md"

    def build_draft_prompt(self, unit: dict) -> tuple[str, str]:
        uid = unit["id"]
        title = unit.get("title", uid)
        voice = self.cfg.get("voice", {})
        no_em = voice.get("no_em_dashes", True)
        blacklist = [b for b in voice.get("blacklist", []) if not str(b).startswith("/")]
        contract_p = self.ws / "contracts" / f"{uid}.md"
        contract = contract_p.read_text(encoding="utf-8") if contract_p.exists() else ""
        prior_p = self._prior_prose_path(uid)
        prior = prior_p.read_text(encoding="utf-8")[-6000:] if prior_p.exists() else ""
        seed_p = self.ws / "seed.md"
        seed = seed_p.read_text(encoding="utf-8")[:8000] if seed_p.exists() else ""
        target = int(unit.get("target_words", 1500))

        system = (
            "You are a book author writing one chapter. You are a pure text "
            "function: you receive context and return finished prose, nothing else. "
            "No preamble, no meta-commentary, no 'in this chapter'. "
            f"Honor the author's voice. {'Do NOT use em-dashes (U+2014/U+2013); use semicolons, colons, or periods. ' if no_em else ''}"
            + (f"Never use these words: {', '.join(blacklist)}. " if blacklist else "")
        )
        prompt = (
            (f"# Book Bible (excerpt)\n{seed}\n\n" if seed else "")
            + (f"# Previous chapter (for continuity; echo its close with variation, do not quote)\n{prior}\n\n" if prior else "")
            + f"# Your contract for this chapter\n{contract}\n\n"
            + f"# Task\nWrite the chapter titled \"{title}\" at ~{target} words. "
            + f"Begin with the exact line: # {title}\n"
            + "Return only the chapter markdown."
        )
        return system, prompt

    # -- in-code per-unit gate (fast, deterministic) ----------------------
    def gate_draft(self, unit: dict, text: str) -> tuple[bool, str]:
        title = unit.get("title", "")
        voice = self.cfg.get("voice", {})
        problems = []
        first = text.lstrip().splitlines()[0] if text.strip() else ""
        if title and first.strip() != f"# {title}":
            problems.append(f'H1 must be "# {title}", got "{first[:60]}"')
        if voice.get("no_em_dashes", True):
            if "—" in text or "–" in text:
                problems.append("contains em-dash/en-dash (U+2014/U+2013)")
        for b in voice.get("blacklist", []):
            b = str(b)
            if b.startswith("/"):
                continue  # regex atoms handled by the full lint pass
            if re.search(r"\b" + re.escape(b) + r"\b", text, re.I):
                problems.append(f"blacklisted term: {b}")
        wc = len(text.split())
        target = int(unit.get("target_words", 1500))
        if target and (wc < target * 0.6 or wc > target * 1.6):
            problems.append(f"word count {wc} outside 0.6-1.6x of target {target}")
        return (not problems), "; ".join(problems)

    # -- stages -----------------------------------------------------------
    def stage_precheck(self):
        # schema validation (best-effort) + contracts/seed presence
        schema_p = TOOLS / "book_config.schema.json"
        try:
            import jsonschema
            jsonschema.validate(self.cfg, load_json(schema_p))
        except ImportError:
            pass
        except Exception as e:
            raise HardStop("precheck", f"book_config invalid vs schema: {str(e).splitlines()[0][:200]}")
        return "ok"

    def stage_draft(self, unit: dict):
        uid = unit["id"]
        cls = str(unit.get("class", "C")).upper()
        out = self.ws / "manuscript" / "current" / f"{uid}_current.md"
        out.parent.mkdir(parents=True, exist_ok=True)
        if cls == "A":
            # never draft prose into a Class A unit — human-only
            self.log("draft.skip_classA", unit=uid)
            return "class-A: outline-only, left for human"
        system, prompt = self.build_draft_prompt(unit)
        last = ""
        for attempt in range(1, 4):
            fb = ("" if attempt == 1
                  else f"\n\n# The previous attempt FAILED these gate checks; fix them:\n{last}")
            text = self.model.complete(system, prompt + fb)
            ok, detail = self.gate_draft(unit, text)
            if ok:
                out.write_text(text.strip() + "\n", encoding="utf-8")
                return f"drafted {len(text.split())} words in {attempt} attempt(s)"
            last = detail
            self.log("draft.gate_fail", unit=uid, attempt=attempt, detail=detail)
        raise HardStop(f"draft:{uid}", f"gate failed after 3 attempts: {last}")

    def stage_integrate(self):
        rc, out, err = run([sys.executable, str(TOOLS / "lint_manuscript.py"),
                            "--config", str(self.config_path)])
        if rc != 0:
            raise HardStop("integrate", f"lint_manuscript exit {rc}: {(out + err).strip()[-300:]}")
        return "lint clean"

    def stage_assemble(self):
        rc, out, err = run([sys.executable, str(TOOLS / "assemble_manuscript.py"),
                            "--config", str(self.config_path)])
        if rc != 0:
            raise HardStop("assemble", f"assemble exit {rc}: {(out + err).strip()[-300:]}")
        return out.strip().splitlines()[-1] if out.strip() else "assembled"

    def stage_produce(self, fmt: str):
        # interior
        if fmt in ("kindle",):
            rc, o, e = run(["node", str(TOOLS / "generate_kindle.js"),
                            "--config", str(self.config_path)])
        elif fmt in ("epub",):
            rc, o, e = run([sys.executable, str(TOOLS / "build_epub.py"),
                            "--config", str(self.config_path)])
        elif fmt in ("digital_pdf",):
            rc, o, e = run([sys.executable, str(TOOLS / "build_digital_pdf.py"),
                            "--config", str(self.config_path)])
        else:
            rc, o, e = run(["node", str(TOOLS / "generate_book.js"),
                            "--config", str(self.config_path), "--format", fmt])
        if rc != 0:
            raise HardStop(f"produce:{fmt}", f"interior gen exit {rc}: {(o + e).strip()[-300:]}")
        # gate: verify_build for this format
        rc, o, e = run([sys.executable, str(TOOLS / "verify_build.py"),
                        "--config", str(self.config_path), "--format", fmt])
        if rc != 0:
            raise HardStop(f"produce:{fmt}", f"verify_build FAIL: {(o + e).strip()[-400:]}")
        return "produced + verify_build pass"

    def stage_cover(self):
        if self.no_cover:
            return "skipped (dry-run / --no-cover)"
        rc, o, e = run([sys.executable, str(TOOLS / "cover_gen.py"),
                        "--config", str(self.config_path)])
        # cover is best-effort: a missing art stack must not hard-stop the whole run
        return "cover attempted (rc=%d)" % rc

    def stage_verify(self):
        rc, o, e = run([sys.executable, str(TOOLS / "verify_build.py"),
                        "--config", str(self.config_path), "--format", "all"])
        if rc != 0:
            raise HardStop("verify", f"verify_build --format all FAIL: {(o + e).strip()[-400:]}")
        return "all formats verified"

    def stage_emit(self):
        manifest = {
            "slug": self.slug, "emitted": now(),
            "formats": self.cfg.get("formats", []),
            "outputs_root": str((self.ws / "outputs").resolve()),
        }
        save_json_atomic(self.ws / "outputs" / "MANIFEST.json", manifest)
        return "emitted manifest"

    # -- the driver -------------------------------------------------------
    def input_sha(self, key: str, kind: str, arg: str) -> str:
        if kind == "draft":
            unit = next(u for u in self.units() if u["id"] == arg)
            return self.draft_inputs_sha(unit)
        if kind == "assemble":
            cur = sorted((self.ws / "manuscript" / "current").glob("*_current.md"))
            return sha_text("|".join(sha_file(p) for p in cur))
        if kind in ("integrate",):
            cur = sorted((self.ws / "manuscript" / "current").glob("*_current.md"))
            return sha_text("integrate|" + "|".join(sha_file(p) for p in cur))
        if kind == "produce":
            master = sorted((self.ws / "outputs" / "markdown").glob(f"{self.slug}_v*.md"))
            msha = sha_file(master[-1]) if master else "-"
            return sha_text(f"produce|{arg}|{msha}")
        # precheck/cover/verify/emit key off the config
        return sha_text(f"{kind}|{sha_file(self.config_path)}")

    def expected_outputs(self, kind: str, arg: str) -> list[Path]:
        """The artifact(s) a stage must have left on disk. A stage is only
        'satisfied' on resume if these still exist — so deleting a finished
        chapter (or a lost master) forces a re-run, no matter the input hash."""
        if kind == "draft":
            return [self.ws / "manuscript" / "current" / f"{arg}_current.md"]
        if kind == "assemble":
            masters = sorted((self.ws / "outputs" / "markdown").glob(f"{self.slug}_v*.md"))
            return [masters[-1]] if masters else [self.ws / "outputs" / "markdown" / "__missing__.md"]
        if kind == "emit":
            return [self.ws / "outputs" / "MANIFEST.json"]
        return []

    def satisfied(self, key: str, kind: str, arg: str, isha: str) -> bool:
        if not self.state.is_satisfied(key, isha):
            return False
        return all(p.exists() for p in self.expected_outputs(kind, arg))

    def run_stage(self, key: str, kind: str):
        arg = key.split(":", 1)[1] if ":" in key else ""
        if kind == "precheck":
            return self.stage_precheck()
        if kind == "draft":
            unit = next(u for u in self.units() if u["id"] == arg)
            return self.stage_draft(unit)
        if kind == "integrate":
            return self.stage_integrate()
        if kind == "assemble":
            return self.stage_assemble()
        if kind == "produce":
            return self.stage_produce(arg)
        if kind == "cover":
            return self.stage_cover()
        if kind == "verify":
            return self.stage_verify()
        if kind == "emit":
            return self.stage_emit()
        raise HardStop(key, f"unknown stage kind {kind}")

    def drive(self, only_to: str | None, only_from: str | None) -> int:
        plan = self.plan()
        keys = [k for k, _ in plan]
        started = only_from is None
        self.log("run.start", slug=self.slug, backend=self.model.backend,
                 dry_run=self.dry_run, stages=len(plan))
        for key, kind in plan:
            if not started:
                if key == only_from:
                    started = True
                else:
                    continue
            arg = key.split(":", 1)[1] if ":" in key else ""
            isha = self.input_sha(key, kind, arg)
            if self.satisfied(key, kind, arg, isha):
                self.log("stage.skip_done", stage=key)
            else:
                self.state.mark(key, "running", isha, attempts=self.state.rec(key).get("attempts", 0) + 1)
                try:
                    detail = self.run_stage(key, kind)
                except HardStop as hs:
                    self.state.mark(key, "failed", isha, gate="fail", detail=hs.detail)
                    save_json_atomic(self.eng_dir / "HARDSTOP.json",
                                     {"stage": hs.stage, "detail": hs.detail, "ts": now()})
                    self.log("HARDSTOP", stage=key, detail=hs.detail)
                    print(f"\n=== HARD-STOP at {key} ===\n{hs.detail}\n"
                          f"Fix, then re-run the same command; the engine resumes here.")
                    return 2
                self.state.mark(key, "done", isha, gate="pass", detail=str(detail))
                self.log("stage.done", stage=key, detail=str(detail))
            if only_to and key == only_to:
                break
        # clear any stale hardstop marker on a clean pass
        hs = self.eng_dir / "HARDSTOP.json"
        if hs.exists():
            hs.unlink()
        self.log("run.complete", slug=self.slug)
        print(f"\n=== engine complete: {self.slug} ===")
        return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Deterministic BOOKSMITH engine (control inversion).")
    ap.add_argument("--config", required=True)
    ap.add_argument("--backend", choices=["mock", "anthropic", "openai"], default=None)
    ap.add_argument("--to", dest="to", default=None, help="stop after this stage key")
    ap.add_argument("--from", dest="from_", default=None, help="resume from this stage key")
    ap.add_argument("--dry-run", action="store_true",
                    help="mock model + skip cover art; every mechanical gate still runs")
    ap.add_argument("--no-cover", action="store_true")
    ap.add_argument("--status", action="store_true", help="print state and exit")
    ap.add_argument("--fresh", action="store_true", help="discard prior engine state")
    args = ap.parse_args(argv)

    cfg_path = Path(args.config).resolve()
    if not cfg_path.exists():
        print(f"config not found: {cfg_path}", file=sys.stderr)
        return 1

    eng = Engine(cfg_path, backend=args.backend, dry_run=args.dry_run, no_cover=args.no_cover)
    if args.fresh:
        (eng.eng_dir / "state.json").unlink(missing_ok=True)
        eng.state = State(eng.eng_dir / "state.json", eng.slug, sha_file(cfg_path))
    if args.status:
        print(json.dumps(eng.state.data, indent=2, ensure_ascii=False))
        return 0
    return eng.drive(only_to=args.to, only_from=args.from_)


if __name__ == "__main__":
    sys.exit(main())
