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

Stages (fixed order):  [ingest] -> [seed] -> precheck -> draft:<unit>* -> integrate
                       -> assemble -> produce:<format>* -> [cover] -> verify -> emit

The bracketed front-half ([ingest], [seed]) is the ARCHITECT phase (roadmap H1.1):
it runs ONLY when a book arrives as a brief (brief.md + optional intake/ docs) with
no seed.md and no units yet. It turns a gist + sources into relational digests,
seed.md, per-unit contracts, registries, and a schema-valid book_config.json
(GATE-1 / GATE-2), so `engine.py --config <brief-config>` runs INTAKE -> EMIT end to
end. An already-architected book skips the preamble untouched.

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


class HarnessTurnNeeded(Exception):
    """Not a failure — a PAUSE. Under backend=harness the engine gets prose from
    the Claude Code session itself (no API key): it writes a request under
    _engine/bridge/, the session writes the response file, then re-runs the
    engine, which gates the prose and continues. Exit code 3 = 'model turn'."""
    def __init__(self, unit: str, response_file: str):
        self.unit, self.response_file = unit, response_file
        super().__init__(f"harness turn needed for {unit} -> {response_file}")


# ---------------------------------------------------------------------------
# the engine
# ---------------------------------------------------------------------------
class Engine:
    def __init__(self, config_path: Path, backend: str | None, dry_run: bool,
                 no_cover: bool):
        self.config_path = config_path.resolve()
        self.cfg = load_json(self.config_path)
        self.slug = self.cfg["slug"]
        self.domain = str(self.cfg.get("domain", "book"))
        self.domain_spec = self._load_domain_spec()
        self.dry_run = dry_run
        self.no_cover = no_cover or dry_run
        if self.domain_spec and self.domain_spec.get("no_cover"):
            self.no_cover = True  # non-book domains have no book cover stage
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

    # -- domain descriptor (book = built-in default; others in domains/<name>/) --
    def _load_domain_spec(self):
        """A non-book domain declares its stages/producers/verifier in
        domains/<domain>/domain.json. Book ('book' or absent) uses the built-in path."""
        if self.domain == "book":
            return None
        p = ROOT / "domains" / self.domain / "domain.json"
        if not p.exists():
            return None
        try:
            return load_json(p)
        except Exception:
            return None

    def _resolve_token(self, x) -> str:
        """Expand a producer/verifier command token: 'python' -> this interpreter;
        {config}/{ws}/{slug} placeholders; repo-relative script paths -> absolute."""
        x = str(x)
        if x == "python":
            return sys.executable
        x = (x.replace("{config}", str(self.config_path))
              .replace("{ws}", str(self.ws)).replace("{slug}", self.slug))
        if x.startswith(("domains/", "_tools/")):
            return str(ROOT / x)
        return x

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
        if self.domain != "book" and self.domain_spec:
            # Non-book domain: producers read manuscript/current directly; no book
            # assemble / cover / print-format machinery. (The book branch below is unchanged.)
            for t in self.domain_spec.get("produce_targets", []):
                steps.append((f"produce:{t}", "produce"))
            steps.append(("verify", "verify"))
            steps.append(("emit", "emit"))
            return steps
        steps.append(("assemble", "assemble"))
        fmts = list(self.cfg.get("formats", []))
        # Cover-consuming formats MUST follow the cover stage: epub embeds the cover
        # image (properties="cover-image"), digital_pdf composites front+back covers
        # onto the interior (§12: covers before the outputs that consume them).
        cover_dependent = {"epub", "digital_pdf"}
        for fmt in fmts:
            if fmt not in cover_dependent:
                steps.append((f"produce:{fmt}", "produce"))
        if not self.no_cover:
            steps.append(("cover", "cover"))
        for fmt in fmts:
            if fmt in cover_dependent:
                steps.append((f"produce:{fmt}", "produce"))
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

        # Domain wording. Book stays BYTE-IDENTICAL (role='book author', noun='chapter',
        # 'Book Bible'); a non-book domain generalizes the nouns from its descriptor.
        if self.domain != "book" and self.domain_spec:
            noun = self.cfg.get("voice", {}).get("unit_noun", "chapter")
            role = self.domain_spec.get("author_role", f"{noun} author")
            bible_label = self.domain_spec.get("bible_label", "Outline")
        else:
            role, noun, bible_label = "book author", "chapter", "Book Bible"
        system = (
            f"You are a {role} writing one {noun}. You are a pure text "
            "function: you receive context and return finished prose, nothing else. "
            f"No preamble, no meta-commentary, no 'in this {noun}'. "
            f"Honor the author's voice. {'Do NOT use em-dashes (U+2014/U+2013); use semicolons, colons, or periods. ' if no_em else ''}"
            + (f"Never use these words: {', '.join(blacklist)}. " if blacklist else "")
        )
        prompt = (
            (f"# {bible_label} (excerpt)\n{seed}\n\n" if seed else "")
            + (f"# Previous {noun} (for continuity; echo its close with variation, do not quote)\n{prior}\n\n" if prior else "")
            + f"# Your contract for this {noun}\n{contract}\n\n"
            + f"# Task\nWrite the {noun} titled \"{title}\" at ~{target} words. "
            + f"Begin with the exact line: # {title}\n"
            + f"Return only the {noun} markdown."
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

    # -- ARCHITECT FRONT-HALF: ingest + seed (produce digests + seed.md + units)
    # A book can arrive as a BRIEF (a one-line gist + optional intake/ docs) with no
    # seed.md and no units. These two stages are the code half of the creative
    # architecting the engine used to assume was done by hand. The model stays a PURE
    # FUNCTION: it returns a structured plan (JSON) / a relational digest; the engine
    # deterministically writes seed.md, the per-unit contracts, the registries, the
    # exemplars, and a schema-valid book_config.json, then GATE-2 must pass. When no
    # model JSON comes back (dry-run/mock), a deterministic fallback keeps the whole
    # spine testable without a live model.

    def _brief_path(self) -> Path:
        return self.ws / "brief.md"

    def _seed_needed(self) -> bool:
        if self.domain != "book":
            return not self.cfg.get("units")  # non-book domains supply units directly (no book-seed)
        return (not (self.ws / "seed.md").exists()) or (not self.cfg.get("units"))

    def _ingest_needed(self) -> bool:
        intake = self.ws / "intake"
        if not intake.exists() or not any(p.is_file() for p in intake.rglob("*")):
            return False
        return not list((self.ws / "canon_refs").glob("_digest_*.md"))

    def _read_brief(self) -> str:
        p = self._brief_path()
        if p.exists():
            return p.read_text(encoding="utf-8", errors="replace")[:8000]
        bits = [str(self.cfg.get("title", self.slug))]
        if self.cfg.get("subtitle"):
            bits.append(str(self.cfg["subtitle"]))
        if self.cfg.get("genre"):
            bits.append("Genre: " + str(self.cfg["genre"]))
        bits.append("Fiction." if self.cfg.get("is_fiction") else "Nonfiction.")
        return " ".join(bits)

    def _read_digests(self) -> str:
        digs = sorted((self.ws / "canon_refs").glob("_digest_*.md"))
        if not digs:
            return ""
        per = max(600, 12000 // len(digs))
        return "\n\n".join(f"## {d.stem}\n{d.read_text(encoding='utf-8', errors='replace')[:per]}"
                           for d in digs)

    @staticmethod
    def _extract_json(text: str):
        s = text.strip()
        m = re.search(r"```(?:json)?\s*(.+?)```", s, re.S)
        if m:
            s = m.group(1).strip()
        start = s.find("{")
        if start < 0:
            return None
        depth = 0
        for i in range(start, len(s)):
            if s[i] == "{":
                depth += 1
            elif s[i] == "}":
                depth -= 1
                if depth == 0:
                    try:
                        return json.loads(s[start:i + 1])
                    except Exception:
                        return None
        return None

    @staticmethod
    def _num_word(i: int) -> str:
        w = ["Zero", "One", "Two", "Three", "Four", "Five", "Six", "Seven",
             "Eight", "Nine", "Ten", "Eleven", "Twelve", "Thirteen", "Fourteen",
             "Fifteen", "Sixteen", "Seventeen", "Eighteen", "Nineteen", "Twenty"]
        return w[i] if 0 <= i < len(w) else str(i)

    def _slugify_units(self, raw: list) -> list:
        out, used = [], set()
        for i, u in enumerate(raw, 1):
            if isinstance(u, str):
                u = {"title": u}
            if not isinstance(u, dict):
                continue
            base = re.sub(r"[^a-z0-9_]+", "_",
                          str(u.get("id") or f"ch_{i:02d}").lower()).strip("_") or f"ch_{i:02d}"
            uid, k = base, 2
            while uid in used:
                uid, k = f"{base}_{k}", k + 1
            used.add(uid)
            item = {"id": uid, "title": str(u.get("title") or f"Chapter {self._num_word(i)}")}
            if u.get("class") in ("A", "B", "C"):
                item["class"] = u["class"]
            tw = u.get("target_words")
            if isinstance(tw, int) and tw > 0:
                item["target_words"] = tw
            out.append(item)
        return out

    def _fallback_seed_plan(self, brief: str) -> dict:
        m = re.search(r"(?:chapters|units|parts)\s*[:=]\s*(\d{1,3})", brief, re.I)
        n = max(1, min(int(m.group(1)) if m else 5, 60))
        mw = re.search(r"(?:words|target_words)\s*[:=]\s*(\d{2,6})", brief, re.I)
        tw = int(mw.group(1)) if mw else 1500
        units = [{"id": f"ch_{i:02d}", "title": f"Chapter {self._num_word(i)}",
                  "class": "C", "target_words": tw} for i in range(1, n + 1)]
        first = next((ln.strip() for ln in brief.splitlines() if ln.strip()), "")
        return {"units": units, "work_intent": first[:300], "_source": "fallback"}

    def _seed_prompt(self, brief: str, digests: str):
        system = (
            "You are a book architect. Given a brief (and optional source digests), return ONE "
            "JSON object and NOTHING else. Keys: units (array of {id,title,class,target_words}), "
            "work_intent, primary_theme, voice_one_line, division_scheme, refrain, blacklist (array), "
            "sacred_terms (array), cover_prompt_seed. ids look like ch_01; class is A|B|C (default C); "
            "target_words is an integer. cover_prompt_seed must contain NO title/author text. "
            "Choose a natural unit count for the material.")
        prompt = (f"# Brief\n{brief}\n\n"
                  + (f"# Source digests (each says how it relates to the core)\n{digests}\n\n" if digests else "")
                  + "# Task\nReturn the JSON object.")
        return system, prompt

    def _seed_plan_via_harness(self, brief: str, digests: str) -> dict:
        """Keyless architect turn: the Claude Code session writes the plan JSON via
        the same disk bridge the draft turns use. Pause (rc 3) until the response lands."""
        bridge = self.eng_dir / "bridge"
        bridge.mkdir(parents=True, exist_ok=True)
        resp = bridge / "seed.response.json"
        if resp.exists():
            raw = resp.read_text(encoding="utf-8", errors="replace")
            resp.unlink()
            (bridge / "seed.request.json").unlink(missing_ok=True)
            data = self._extract_json(raw)
            if isinstance(data, dict) and isinstance(data.get("units"), list) and data["units"]:
                data["units"] = self._slugify_units(data["units"])
                if data["units"]:
                    data.setdefault("_source", "harness")
                    return data
            self.log("seed.harness_unparseable", chars=len(raw))
            return self._fallback_seed_plan(brief)
        system, prompt = self._seed_prompt(brief, digests)
        req = {"stage": "seed", "write_plan_json_to": str(resp), "system": system, "prompt": prompt,
               "must_return": ("ONE JSON object: units[{id,title,class,target_words}], work_intent, "
                               "primary_theme, voice_one_line, division_scheme, refrain, blacklist[], "
                               "sacred_terms[], cover_prompt_seed (NO title/author text in it).")}
        (bridge / "seed.request.json").write_text(json.dumps(req, indent=2, ensure_ascii=False), encoding="utf-8")
        directive = (f"[BOOKSMITH harness turn] Architect the book SEED. Read "
                     f"{bridge / 'seed.request.json'} (brief + digests + the required JSON shape), "
                     f"write the plan JSON to {resp}, then re-run the engine (same command). The engine "
                     f"will write seed.md + per-unit contracts + a schema-valid config and gate it (GATE-2).")
        (self.eng_dir / "NEXT.md").write_text(directive + "\n", encoding="utf-8")
        self.log("harness.turn_needed", stage="seed",
                 request=str(bridge / "seed.request.json"), response=str(resp))
        print("\n" + directive)
        raise HarnessTurnNeeded("seed", str(resp))

    def _model_seed_plan(self, brief: str, digests: str) -> dict:
        system, prompt = self._seed_prompt(brief, digests)
        try:
            raw = self.model.complete(system, prompt, max_tokens=4096, temperature=0.4)
        except Exception as e:
            self.log("seed.model_error", detail=str(e)[:160])
            return self._fallback_seed_plan(brief)
        data = self._extract_json(raw)
        if not isinstance(data, dict) or not isinstance(data.get("units"), list) or not data["units"]:
            self.log("seed.unparseable_plan", out_chars=len(raw))
            return self._fallback_seed_plan(brief)
        data["units"] = self._slugify_units(data["units"])
        if not data["units"]:
            return self._fallback_seed_plan(brief)
        data.setdefault("_source", "model")
        return data

    def _validate_config(self, cfg: dict) -> None:
        try:
            import jsonschema
        except ImportError:
            return
        try:
            jsonschema.validate(cfg, load_json(TOOLS / "book_config.schema.json"))
        except Exception as e:
            raise HardStop("seed", f"seeded config invalid vs schema: {str(e).splitlines()[0][:200]}")

    def _apply_seed_to_config(self, plan: dict) -> None:
        cfg = load_json(self.config_path)
        cfg["units"] = plan["units"]
        auth = cfg.setdefault("authorship", {"default_class": "C", "per_chapter_overrides": {}})
        auth.setdefault("default_class", "C")
        ov = auth.setdefault("per_chapter_overrides", {})
        for u in plan["units"]:
            if u.get("class") in ("A", "B"):
                ov[u["id"]] = u["class"]
        voice = cfg.setdefault("voice", {})
        voice.setdefault("unit_noun", "chapter")
        voice.setdefault("no_em_dashes", True)
        voice.setdefault("exemplars_path", "exemplars/")
        voice.setdefault("greenlist", voice.get("greenlist", []))
        if plan.get("blacklist") and not voice.get("blacklist"):
            voice["blacklist"] = [str(x) for x in plan["blacklist"]][:64]
        voice.setdefault("blacklist", voice.get("blacklist", []))
        if plan.get("sacred_terms") and not voice.get("sacred_terms"):
            voice["sacred_terms"] = [str(x) for x in plan["sacred_terms"]][:64]
        voice.setdefault("sacred_terms", voice.get("sacred_terms", []))
        ps = plan.get("cover_prompt_seed")
        if ps:
            cfg.setdefault("cover", {}).setdefault("art", {}).setdefault("prompt_seed", str(ps)[:600])
        self._validate_config(cfg)
        save_json_atomic(self.config_path, cfg)
        self.cfg = cfg

    def _write_seed_md(self, plan: dict, brief: str) -> None:
        tpl_p = ROOT / "templates" / "seed.template.md"
        tpl = (tpl_p.read_text(encoding="utf-8") if tpl_p.exists()
               else "# SEED.md - {{TITLE}}\n\n## §1.\n## §2.\n## §3.\n## §4.\n## §5.\n## §6.\n## §7.\n")
        cfg, units = self.cfg, plan["units"]
        unit_noun = cfg.get("voice", {}).get("unit_noun", "chapter")
        idx_rows = "\n".join(
            f"| {u['id']} | {u.get('title', '')} | {u.get('class', 'C')} |  | {u.get('target_words', 1500)} |"
            for u in units) or "| (none) |  |  |  |  |"
        repl = {
            "{{TITLE}}": str(cfg.get("title", self.slug)),
            "{{GENRE_FORM}}": str(cfg.get("genre", "book")),
            "{{WHAT_IT_DOES}}": str(plan.get("work_intent", "")),
            "{{WHO_IT_SERVES}}": "its intended reader",
            "{{WHY}}": str(plan.get("work_intent", "")),
            "{{INTEGRATION_MODE}}": str(cfg.get("integration_mode", "synthesis")),
            "{{UNIT_COUNT}}": str(len(units)),
            "{{UNIT_NOUN}}": unit_noun,
            "{{FORMATS}}": ", ".join(cfg.get("formats", [])),
            "{{WORD_TARGET}}": str(sum(int(u.get("target_words", 1500)) for u in units)),
            "{{VOICE_ONE_LINE}}": str(plan.get("voice_one_line", "")),
            "{{PRIMARY_THEME}}": str(plan.get("primary_theme", "")),
            "{{DIVISION_SCHEME}}": str(plan.get("division_scheme", f"{len(units)} {unit_noun}s")),
            "{{UNIT_MAP}}": "; ".join(f"{u['id']}:{u.get('target_words', 1500)}w" for u in units),
            "{{REFRAIN}}": str(plan.get("refrain", "")),
            "{{DEFAULT_CLASS}}": str(cfg.get("authorship", {}).get("default_class", "C")),
            "{{VERSION}}": "1.0-engine",
        }
        out = tpl.replace("| {{UNIT_ID}} | {{UNIT_TITLE}} | {{CLASS}} | {{REGISTER}} | {{LENGTH}} |", idx_rows)
        for k, v in repl.items():
            out = out.replace(k, v)
        (self.ws / "seed.md").write_text(out, encoding="utf-8")

    def _seed_registry_and_exemplars(self, plan: dict) -> None:
        reg = self.ws / "registry"
        reg.mkdir(parents=True, exist_ok=True)
        seeds = {
            "threads.md": "# Thread Registry\n\n*seed -> payoff, callbacks, motifs. One row per thread.*\n\n| id | kind | planted | resolved | status |\n|---|---|---|---|---|\n",
            "dependencies.md": "# Dependency Registry\n\n*concept A must land before concept B.*\n",
            "compression_pairs.md": "# Compression Pairs\n\n*mirror / echo unit pairs (e.g. ch_01 <-> ch_N).*\n",
            "refrain.md": f"# Refrain\n\n**Exact wording (never paraphrase):** {plan.get('refrain', '')}\n\n**Placements:** TBD\n",
            "canon_refs.md": "# Canon Anchors Index\n\n*files under canon_refs/ each unit derives from.*\n",
        }
        for name, body in seeds.items():
            p = reg / name
            if not p.exists():
                p.write_text(body, encoding="utf-8")
        exd = self.ws / "exemplars"
        exd.mkdir(parents=True, exist_ok=True)
        anchor = exd / "anchor.md"
        if not anchor.exists():
            anchor.write_text(
                "# Voice anchor exemplar\n\n*The single passage the whole book's voice is measured "
                "against. Replace with a real anchor passage from the author's own prose.*\n\n"
                + str(plan.get("voice_one_line", "")) + "\n", encoding="utf-8")

    def _gate_seed(self) -> None:
        cfg = load_json(self.config_path)
        self._validate_config(cfg)
        units = cfg.get("units") or []
        if not units:
            raise HardStop("seed", "GATE-2: no units produced")
        default_cls = cfg.get("authorship", {}).get("default_class", "C")
        missing = []
        for u in units:
            cls = u.get("class", default_cls)
            name = f"{u['id']}_outline.md" if cls == "A" else f"{u['id']}.md"
            if not (self.ws / "contracts" / name).exists():
                missing.append(name)
        if missing:
            raise HardStop("seed", f"GATE-2: missing contract(s): {', '.join(missing[:8])}")
        seed_p = self.ws / "seed.md"
        if not seed_p.exists():
            raise HardStop("seed", "GATE-2: seed.md not written")
        txt = seed_p.read_text(encoding="utf-8", errors="replace")
        gaps = [f"§{i}" for i in range(1, 8) if f"## §{i}" not in txt]
        if gaps:
            raise HardStop("seed", f"GATE-2: seed.md missing section(s): {', '.join(gaps)}")
        v = cfg.get("voice", {})
        if "no_em_dashes" not in v or "unit_noun" not in v:
            raise HardStop("seed", "GATE-2: voice block incomplete (needs unit_noun + no_em_dashes)")

    def stage_seed(self):
        brief = self._read_brief()
        digests = self._read_digests()
        plan = (self._seed_plan_via_harness(brief, digests)
                if self.model.backend == "harness"
                else self._model_seed_plan(brief, digests))
        self._apply_seed_to_config(plan)
        self._write_seed_md(plan, brief)
        rc, o, e = run([sys.executable, str(TOOLS / "init_contracts.py"),
                        "--config", str(self.config_path)])
        if rc != 0:
            raise HardStop("seed", f"init_contracts exit {rc}: {(o + e).strip()[-300:]}")
        self._seed_registry_and_exemplars(plan)
        self._gate_seed()
        return f"seeded {len(plan['units'])} units ({plan.get('_source', 'model')}); GATE-2 pass"

    @staticmethod
    def _classify_intake(p: Path) -> str:
        ext = p.suffix.lower()
        if ext in {".md", ".txt", ".markdown"}:
            return "canon_text"
        if ext in {".pdf", ".docx", ".epub"}:
            return "document"
        if ext in {".png", ".jpg", ".jpeg", ".webp", ".gif"}:
            return "image"
        if ext in {".mp3", ".wav", ".m4a", ".mp4", ".mov"}:
            return "media"
        return "other"

    def stage_ingest(self):
        intake = self.ws / "intake"
        canon = self.ws / "canon_refs"
        canon.mkdir(parents=True, exist_ok=True)
        text_ext = {".md", ".txt", ".markdown"}
        doc_ext = {".pdf", ".docx", ".epub", ".htm", ".html"}
        top = [p for p in sorted(intake.iterdir()) if p.is_file()] if intake.exists() else []
        # 1) normalize any real documents (PDF/DOCX/EPUB/HTML) to markdown first
        converted_dir = intake / "converted"
        conv = None
        if any(p.suffix.lower() in doc_ext for p in top):
            rc, o, e = run([sys.executable, str(TOOLS / "manuscript_ingest.py"),
                            "--intake", str(intake), "--out", str(converted_dir)])
            if rc != 0:
                raise HardStop("ingest", f"manuscript_ingest exit {rc}: {(o + e).strip()[-300:]}")
            try:
                conv = json.loads(o.strip().splitlines()[-1]) if o.strip() else None
            except Exception:
                conv = None
        # 2) the normalized corpus to digest: top-level text + every converted markdown
        sources = [p for p in top if p.suffix.lower() in text_ext]
        if converted_dir.exists():
            sources += sorted(converted_dir.glob("*.md"))
        manifest = {"ts": now(), "discovered": [], "converted": conv, "digests": []}
        for p in top:
            manifest["discovered"].append({
                "name": p.name, "bytes": p.stat().st_size,
                "class": self._classify_intake(p),
                "is_text": p.suffix.lower() in text_ext,
                "convertible": p.suffix.lower() in doc_ext,
            })
        # 3) one relational digest per source (the model is a pure function)
        brief = self._read_brief()[:1500]
        used = set()
        for p in sources:
            base = re.sub(r"[^a-z0-9_]+", "_", p.stem.lower()).strip("_") or "src"
            slug, k = base, 2
            while slug in used:
                slug, k = f"{base}_{k}", k + 1
            used.add(slug)
            body = p.read_text(encoding="utf-8", errors="replace")
            system = ("You write a RELATIONAL source digest for a book kit. In <=250 words, state what "
                      "this source contains and where it EXTENDS / CONTRADICTS / DEEPENS / BRIDGES the "
                      "book's core. Prose only, no preamble.")
            prompt = f"# Book brief\n{brief}\n\n# Source: {p.name}\n{body[:6000]}\n\n# Task\nWrite the relational digest."
            try:
                dg = self.model.complete(system, prompt, max_tokens=1200, temperature=0.3).strip()
            except Exception as ex:
                dg = f"(auto-digest unavailable: {str(ex)[:120]}) Source {p.name}: {len(body.split())} words."
            dpath = canon / f"_digest_{slug}.md"
            dpath.write_text(f"# Digest - {p.name}\n\n{dg}\n", encoding="utf-8")
            manifest["digests"].append(dpath.name)
        save_json_atomic(canon / "_ingest.json", manifest)
        if sources and len(manifest["digests"]) < len(sources):
            raise HardStop("ingest", "GATE-1: a source did not produce a digest")
        return f"ingested {len(top)} source(s); {len(manifest['digests'])} digest(s)"

    # -- stages -----------------------------------------------------------
    def stage_precheck(self):
        if self.domain != "book":
            if not self.units():
                raise HardStop("precheck", f"domain '{self.domain}': no units declared in config")
            return f"ok (domain={self.domain}, {len(self.units())} units)"
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
        if self.model.backend == "harness":
            return self._draft_via_harness(unit, system, prompt, out)
        # in-process backends (anthropic / openai / mock): retry inline
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

    # -- the harness bridge: prose from the Claude Code session, no API key -----
    def _draft_via_harness(self, unit: dict, system: str, prompt: str, out: Path):
        uid = unit["id"]
        bridge = self.eng_dir / "bridge"
        bridge.mkdir(parents=True, exist_ok=True)
        resp = bridge / f"{uid}.response.md"
        att_f = bridge / f"{uid}.attempts"
        attempts = int(att_f.read_text()) if att_f.exists() else 0
        if resp.exists():
            text = resp.read_text(encoding="utf-8").strip()
            ok, detail = self.gate_draft(unit, text)
            resp.unlink()
            if ok:
                out.write_text(text + "\n", encoding="utf-8")
                att_f.unlink(missing_ok=True)
                (bridge / f"{uid}.request.json").unlink(missing_ok=True)
                return f"drafted via harness ({len(text.split())} words, attempt {attempts + 1})"
            attempts += 1
            att_f.write_text(str(attempts), encoding="utf-8")
            if attempts >= 3:
                raise HardStop(f"draft:{uid}", f"harness prose failed the gate {attempts}x: {detail}")
            self._emit_harness_request(unit, system, prompt, resp, feedback=detail, attempt=attempts)
            raise HarnessTurnNeeded(uid, str(resp))
        self._emit_harness_request(unit, system, prompt, resp, feedback="", attempt=attempts)
        raise HarnessTurnNeeded(uid, str(resp))

    def _emit_harness_request(self, unit, system, prompt, resp: Path, feedback: str, attempt: int):
        uid = unit["id"]
        title = unit.get("title", uid)
        bridge = self.eng_dir / "bridge"
        req = {
            "unit": uid,
            "title": title,
            "attempt": attempt + 1,
            "write_finished_chapter_markdown_to": str(resp),
            "must_pass_gates": (f"first line exactly '# {title}'; word count within "
                                f"0.6-1.6x of {int(unit.get('target_words', 1500))}; "
                                f"{'NO em-dash/en-dash (U+2014/U+2013); ' if self.cfg.get('voice', {}).get('no_em_dashes', True) else ''}"
                                f"no blacklisted term"),
            "system": system,
            "prompt": prompt + (f"\n\n# YOUR PRIOR DRAFT FAILED THESE GATES - fix exactly these:\n{feedback}" if feedback else ""),
        }
        (bridge / f"{uid}.request.json").write_text(json.dumps(req, indent=2, ensure_ascii=False), encoding="utf-8")
        directive = (f"[BOOKSMITH harness turn] Write unit '{uid}' ({title}). "
                     f"Read the request at {bridge / (uid + '.request.json')} (system + prompt + gates), "
                     f"write the finished chapter markdown to {resp}, then re-run the engine "
                     f"(same command). The engine will gate your prose and continue; if it fails a "
                     f"gate it will ask you to rewrite.")
        (self.eng_dir / "NEXT.md").write_text(directive + "\n", encoding="utf-8")
        self.log("harness.turn_needed", unit=uid,
                 request=str(bridge / (uid + ".request.json")), response=str(resp))
        print("\n" + directive)

    def stage_integrate(self):
        rc, out, err = run([sys.executable, str(TOOLS / "lint_manuscript.py"),
                            "--config", str(self.config_path)])
        if rc != 0:
            raise HardStop("integrate", f"lint_manuscript exit {rc}: {(out + err).strip()[-300:]}")
        # The single-authorial-act gate (invariant #2). Advisory by default: the verdict
        # is logged, never blocks. Set authorship.quality_gate=true to hard-fail on it.
        verdict = "n/a"
        aa_rc, aa_o, aa_e = run([sys.executable, str(TOOLS / "authorial_act.py"),
                                 "--config", str(self.config_path), "--json"])
        try:
            aa = json.loads(aa_o.strip()) if aa_o.strip() else {}  # --json is one (pretty) object
            verdict = ("PASS" if aa.get("pass")
                       else f"FAIL({aa.get('high', 0)}h/{len(aa.get('findings', []))}f)")
            self.log("authorial_act", verdict=verdict, score=aa.get("score", 0))
            if not aa.get("pass") and self.cfg.get("authorship", {}).get("quality_gate"):
                tells = "; ".join(f"{f['detector']}@{f['unit']}" for f in aa.get("findings", [])[:6])
                raise HardStop("integrate", f"authorial_act gate FAIL: {tells}")
        except HardStop:
            raise
        except Exception:
            pass
        return f"lint clean; authorial_act {verdict}"

    def stage_assemble(self):
        rc, out, err = run([sys.executable, str(TOOLS / "assemble_manuscript.py"),
                            "--config", str(self.config_path)])
        if rc != 0:
            raise HardStop("assemble", f"assemble exit {rc}: {(out + err).strip()[-300:]}")
        return out.strip().splitlines()[-1] if out.strip() else "assembled"

    PRINT_FMTS = {"kdp_paperback", "kdp_hardcover", "mixam_paperback",
                  "mixam_hardcover", "blurb_paperback", "blurb_hardcover"}

    def _print_docx(self, fmt: str) -> Path:
        # mirrors generate_book.js resolveOutPath (the naming is upload-routing-significant)
        s = self.slug
        m = {
            "kdp_paperback": ("kdp_paperback", f"{s}_KDP_PAPERBACK.docx"),
            "kdp_hardcover": ("kdp_hardcover", f"{s}_KDP_HARDCOVER.docx"),
            "mixam_paperback": ("mixam_paperback", f"inner_{s}.docx"),
            "mixam_hardcover": ("mixam_hardcover", f"inner_{s}.docx"),
            "blurb_paperback": ("blurb_paperback", f"{s}_BLURB_TRADE.docx"),
            "blurb_hardcover": ("blurb_hardcover", f"{s}_BLURB_TRADE.docx"),
        }
        d, f = m[fmt]
        return self.ws / "outputs" / d / f

    def stage_produce(self, fmt: str):
        if self.domain != "book" and self.domain_spec:
            spec = (self.domain_spec.get("producers", {}) or {}).get(fmt)
            if not spec:
                raise HardStop(f"produce:{fmt}", f"domain '{self.domain}' declares no producer for '{fmt}'")
            rc, o, e = run([self._resolve_token(x) for x in spec])
            if rc != 0:
                raise HardStop(f"produce:{fmt}", f"{fmt} producer exit {rc}: {(o + e).strip()[-300:]}")
            return f"produced {fmt} (domain={self.domain})"
        cfgp = str(self.config_path)
        # --- interior (the real §12 build order, per format family) ---
        if fmt == "kindle":
            rc, o, e = run(["node", str(TOOLS / "generate_kindle.js"), "--config", cfgp])
            if rc != 0:
                raise HardStop(f"produce:{fmt}", f"generate_kindle exit {rc}: {(o + e).strip()[-300:]}")
        elif fmt == "epub":
            rc, o, e = run([sys.executable, str(TOOLS / "build_epub.py"), "--config", cfgp])
            if rc != 0:
                raise HardStop(f"produce:{fmt}", f"build_epub exit {rc}: {(o + e).strip()[-300:]}")
        elif fmt == "digital_pdf":
            # consumes the print interior PDF, so a print format must run before it
            rc, o, e = run([sys.executable, str(TOOLS / "build_digital_pdf.py"), "--config", cfgp])
            if rc != 0:
                raise HardStop(f"produce:{fmt}", f"build_digital_pdf exit {rc}: {(o + e).strip()[-300:]}")
        elif fmt in self.PRINT_FMTS:
            docx = self._print_docx(fmt)
            pdf = docx.with_suffix(".pdf")
            rc, o, e = run(["node", str(TOOLS / "generate_book.js"), "--config", cfgp, "--format", fmt])
            if rc != 0:
                raise HardStop(f"produce:{fmt}", f"generate_book exit {rc}: {(o + e).strip()[-300:]}")
            if not docx.exists():
                raise HardStop(f"produce:{fmt}", f"generator did not write expected docx: {docx}")
            # idempotent injections (generate_book inline-injects mirror; these are
            # belt-and-suspenders). Non-fatal: verify_build is the authoritative gate.
            run(["node", str(TOOLS / "inject_mirror_margins.js"), str(docx)])
            run(["node", str(TOOLS / "inject_front_matter_valign.js"), str(docx)])
            pad = ["--pad-multiple", "4"] if fmt.startswith("mixam") else []
            rc, o, e = run([sys.executable, str(TOOLS / "docx_to_pdf.py"), str(docx), str(pdf), *pad])
            if rc != 0:
                raise HardStop(f"produce:{fmt}", f"docx_to_pdf exit {rc}: {(o + e).strip()[-300:]}")
        else:
            raise HardStop(f"produce:{fmt}", f"unknown format {fmt}")
        # --- the gate ---
        rc, o, e = run([sys.executable, str(TOOLS / "verify_build.py"), "--config", cfgp, "--format", fmt])
        if rc != 0:
            raise HardStop(f"produce:{fmt}", f"verify_build FAIL: {(o + e).strip()[-400:]}")
        return "produced + verify_build pass"

    def stage_cover(self):
        if self.no_cover:
            return "skipped (dry-run / --no-cover)"
        # Portable art source: try bespoke SDXL (needs a GPU + ComfyUI); on any
        # failure fall back to cover_pick (hypergen abstract cover / catalog match),
        # which renders anywhere. A cover is never a hard-stop; art always lands.
        rc, o, e = run([sys.executable, str(TOOLS / "cover_gen.py"),
                        "--config", str(self.config_path)])
        if rc == 0:
            return "cover art: bespoke SDXL"
        rc2, o2, e2 = run([sys.executable, str(TOOLS / "cover_pick.py"),
                           "--config", str(self.config_path), "--auto", "--write"])
        if rc2 == 0:
            return "cover art: cover_pick fallback (hypergen/catalog; no GPU art stack)"
        return "cover art UNRESOLVED (gen rc=%d, pick rc=%d) — place art in cover_art/" % (rc, rc2)

    def stage_verify(self):
        if self.domain != "book" and self.domain_spec:
            spec = self.domain_spec.get("verifier")
            if not spec:
                return f"domain '{self.domain}': no verifier declared"
            rc, o, e = run([self._resolve_token(x) for x in spec])
            if rc != 0:
                raise HardStop("verify", f"domain '{self.domain}' verify FAIL: {(o + e).strip()[-400:]}")
            return f"domain '{self.domain}' verified"
        # Verify ONLY the formats this book actually produces. verify_build's own
        # "all" spans every possible format; a book that ships a subset must not be
        # failed for formats it never requested (and never produced on disk).
        fmts = list(self.cfg.get("formats", []))
        failed = []
        for fmt in fmts:
            rc, o, e = run([sys.executable, str(TOOLS / "verify_build.py"),
                            "--config", str(self.config_path), "--format", fmt])
            if rc != 0:
                failed.append(f"{fmt}: {(o + e).strip()[-200:]}")
        if failed:
            raise HardStop("verify", "verify_build FAIL for " + " | ".join(failed))
        return f"{len(fmts)} configured format(s) verified: {', '.join(fmts)}"

    def stage_emit(self):
        if self.domain != "book" and self.domain_spec:
            manifest = {
                "slug": self.slug, "emitted": now(), "domain": self.domain,
                "produce_targets": self.domain_spec.get("produce_targets", []),
                "outputs_root": str((self.ws / "outputs").resolve()),
            }
        else:
            manifest = {
                "slug": self.slug, "emitted": now(),
                "formats": self.cfg.get("formats", []),
                "outputs_root": str((self.ws / "outputs").resolve()),
            }
        save_json_atomic(self.ws / "outputs" / "MANIFEST.json", manifest)
        return "emitted manifest"

    # -- the driver -------------------------------------------------------
    def _run_one(self, key: str, kind: str, arg: str = "", force: bool = False):
        """Run ONE stage through the standard mark/gate/hard-stop machinery.
        Returns None to proceed, or an int rc (2 hard-stop / 3 await-model) to bubble up."""
        isha = self.input_sha(key, kind, arg)
        if not force and self.satisfied(key, kind, arg, isha):
            self.log("stage.skip_done", stage=key)
            return None
        self.state.mark(key, "running", isha, attempts=self.state.rec(key).get("attempts", 0) + 1)
        try:
            detail = self.run_stage(key, kind)
        except HarnessTurnNeeded as ht:
            self.state.mark(key, "awaiting_model", isha, gate="await",
                            detail=f"awaiting harness prose -> {ht.response_file}")
            self.log("AWAIT_MODEL", stage=key, response=ht.response_file)
            return 3
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
        return None

    def _architect(self, only_from: str | None):
        """Front-half preamble: digests (ingest) + seed.md/units (seed) when a book
        arrives as a brief. No-op for an already-architected book. Returns None to
        proceed to the main plan, or an int rc to return immediately."""
        if only_from not in (None, "ingest", "seed"):
            return None
        if self._ingest_needed() and only_from in (None, "ingest"):
            rc = self._run_one("ingest", "ingest", force=True)
            if rc is not None:
                return rc
        if self._seed_needed() and only_from in (None, "ingest", "seed"):
            rc = self._run_one("seed", "seed", force=True)
            if rc is not None:
                return rc
            self.cfg = load_json(self.config_path)  # reload: units now exist -> plan() sees drafts
        return None

    def input_sha(self, key: str, kind: str, arg: str) -> str:
        if kind == "draft":
            unit = next(u for u in self.units() if u["id"] == arg)
            return self.draft_inputs_sha(unit)
        if kind == "assemble":
            cur = sorted((self.ws / "manuscript" / "current").glob("*_current.md"))
            # config included: assemble stitches config-driven front matter into the master
            return sha_text(sha_file(self.config_path) + "|" + "|".join(sha_file(p) for p in cur))
        if kind in ("integrate",):
            cur = sorted((self.ws / "manuscript" / "current").glob("*_current.md"))
            # config included: lint scans config ceremonial/marketing fields too
            return sha_text("integrate|" + sha_file(self.config_path) + "|" + "|".join(sha_file(p) for p in cur))
        if kind == "produce":
            if self.domain != "book":
                cur = sorted((self.ws / "manuscript" / "current").glob("*_current.md"))
                return sha_text(f"produce|{self.domain}|{arg}|" + "|".join(sha_file(p) for p in cur))
            master = sorted((self.ws / "outputs" / "markdown").glob(f"{self.slug}_v*.md"))
            msha = sha_file(master[-1]) if master else "-"
            return sha_text(f"produce|{arg}|{msha}")
        if kind == "seed":
            # inputs seed consumes but does NOT mutate (it writes units into config,
            # so keying on the whole config would make seed perpetually stale)
            digs = sorted((self.ws / "canon_refs").glob("_digest_*.md"))
            core = {k: self.cfg.get(k) for k in
                    ("title", "author", "slug", "is_fiction", "subtitle", "genre",
                     "formats", "integration_mode")}
            return sha_text("seed|" + sha_file(self._brief_path()) + "|"
                            + "|".join(sha_file(p) for p in digs) + "|"
                            + json.dumps(core, sort_keys=True, ensure_ascii=False))
        if kind == "ingest":
            intake = self.ws / "intake"
            # hash the TRUE sources only; exclude intake/converted/ (ingest's own
            # output) so normalizing a doc does not change ingest's input signature.
            files = ([p for p in sorted(intake.rglob("*"))
                      if p.is_file() and "converted" not in p.relative_to(intake).parts]
                     if intake.exists() else [])
            sig = "|".join(f"{p.relative_to(self.ws)}:{p.stat().st_size}" for p in files)
            return sha_text("ingest|" + sig)
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
        if kind == "seed":
            return [self.ws / "seed.md"]
        if kind == "ingest":
            return [self.ws / "canon_refs" / "_ingest.json"]
        return []

    def satisfied(self, key: str, kind: str, arg: str, isha: str) -> bool:
        if not self.state.is_satisfied(key, isha):
            return False
        return all(p.exists() for p in self.expected_outputs(kind, arg))

    def run_stage(self, key: str, kind: str):
        arg = key.split(":", 1)[1] if ":" in key else ""
        if kind == "precheck":
            return self.stage_precheck()
        if kind == "seed":
            return self.stage_seed()
        if kind == "ingest":
            return self.stage_ingest()
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
        self.log("run.start", slug=self.slug, backend=self.model.backend,
                 dry_run=self.dry_run)
        arc = self._architect(only_from)   # ingest + seed if the book arrived as a brief
        if arc is not None:
            return arc
        plan = self.plan()
        started = only_from is None
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
                except HarnessTurnNeeded as ht:
                    self.state.mark(key, "awaiting_model", isha, gate="await",
                                    detail=f"awaiting harness prose -> {ht.response_file}")
                    self.log("AWAIT_MODEL", stage=key, response=ht.response_file)
                    return 3
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
    ap.add_argument("--backend", choices=["mock", "anthropic", "openai", "harness"], default=None,
                    help="harness = get prose from THIS Claude Code session via the disk bridge (no API key)")
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
