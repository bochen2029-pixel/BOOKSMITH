#!/usr/bin/env python3
r"""
model_client.py — the model as a PURE FUNCTION.

The whole point of the BOOKSMITH engine (engine.py) is control inversion: the
*engine* is deterministic code that holds sequence, state, and discipline on
disk; the *model* is a stateless text transducer:

        complete(system, prompt) -> text

No tools. No memory. No discretion. Every call is independent and logged to
disk, so a crash loses nothing and a resume needs zero "orientation."

Backends are pluggable via kit_env.model (or env overrides):
  - anthropic : Claude via the Anthropic Messages API (key from ANTHROPIC_API_KEY).
                Best prose. base_url defaults to https://api.anthropic.com.
  - openai    : any OpenAI-compatible /v1/chat/completions (local llama / KEEL /
                vLLM / an OpenAI key). Sovereign / offline path.
  - mock      : deterministic, network-free, cost-free. Emits structure-valid
                prose (honours a title + word target parsed from the prompt) so
                the engine's real gates can run in a dry-run without a live model.

Dependency-light on purpose: stdlib urllib only (no `requests`), so the engine
runs on a bare Python. Env overrides (win over kit_env):
  BOOKSMITH_MODEL_BACKEND, BOOKSMITH_MODEL_ID, BOOKSMITH_MODEL_BASE_URL,
  ANTHROPIC_API_KEY / OPENAI_API_KEY.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Optional


class ModelError(RuntimeError):
    """A model call failed after retries, or a backend is misconfigured."""


DEFAULTS = {
    "backend": "mock",
    "model": "claude-opus-4-8",
    "base_url": "https://api.anthropic.com",
    "openai_base_url": "http://127.0.0.1:8080/v1",
    "api_key_env": "ANTHROPIC_API_KEY",
    "max_tokens": 8192,
    "temperature": 0.7,
    "timeout_s": 300,
    "max_retries": 4,
}


def load_model_cfg(kit_env: dict | None) -> dict:
    """Merge DEFAULTS < kit_env.model < environment overrides."""
    cfg = dict(DEFAULTS)
    if kit_env and isinstance(kit_env.get("model"), dict):
        for k, v in kit_env["model"].items():
            if not k.startswith("_"):
                cfg[k] = v
    env = os.environ
    if env.get("BOOKSMITH_MODEL_BACKEND"):
        cfg["backend"] = env["BOOKSMITH_MODEL_BACKEND"]
    if env.get("BOOKSMITH_MODEL_ID"):
        cfg["model"] = env["BOOKSMITH_MODEL_ID"]
    if env.get("BOOKSMITH_MODEL_BASE_URL"):
        cfg["base_url"] = env["BOOKSMITH_MODEL_BASE_URL"]
        cfg["openai_base_url"] = env["BOOKSMITH_MODEL_BASE_URL"]
    return cfg


class ModelClient:
    """Stateless pure-function wrapper over a chosen backend."""

    def __init__(self, cfg: dict, log_dir: Optional[Path] = None):
        self.cfg = cfg
        self.backend = cfg.get("backend", "mock")
        self.log_dir = Path(log_dir) if log_dir else None
        self._n = 0
        if self.log_dir:
            self.log_dir.mkdir(parents=True, exist_ok=True)
            # Append-only ledger: a resumed process continues numbering after
            # what the ledger already holds instead of overwriting call_0001
            # onward (silent overwrites under-counted spend and would have
            # under-enforced the E-6 budget floor across restarts).
            try:
                ns = [int(p.stem.split("_")[1]) for p in self.log_dir.glob("call_*.json")]
                self._n = max(ns) if ns else 0
            except Exception:
                self._n = 0

    # -- E-6: the spend floor (conditional; absent env var = zero change) --
    def _ledger_tokens(self) -> int:
        """Sum the call ledger as it stands: exact tokens when logged (E-4),
        chars/4 otherwise. This is the arithmetic the budget floor trusts."""
        if not self.log_dir or not self.log_dir.is_dir():
            return 0
        total = 0
        for p in self.log_dir.glob("call_*.json"):
            try:
                r = json.loads(p.read_text(encoding="utf-8"))
            except Exception:
                continue
            it, ot = r.get("in_tokens"), r.get("out_tokens")
            if it or ot:
                total += int(it or 0) + int(ot or 0)
            else:
                total += (int(r.get("prompt_chars") or 0) + int(r.get("out_chars") or 0)) // 4
        return total

    def _check_budget(self):
        """Floors in code: when BOOKSMITH_TOKEN_BUDGET is set, a METERED call
        (anthropic/openai) may not start once this ledger's usage meets the cap.
        The refusal is a ModelError, so the engine hard-stops with the remedy in
        plain text and resumes cleanly after the cap is raised. mock/harness are
        free and never blocked. Unset or non-positive budget = no check at all."""
        raw = os.environ.get("BOOKSMITH_TOKEN_BUDGET")
        if not raw or self.backend not in ("anthropic", "openai"):
            return
        try:
            cap = int(str(raw).strip())
        except ValueError:
            return
        if cap <= 0:
            return
        spent = self._ledger_tokens()
        if spent >= cap:
            raise ModelError(
                f"token budget reached: ~{spent:,} tokens used of a {cap:,}-token cap "
                f"for this ledger ({self.log_dir}). No further metered model calls "
                "will start. Raise or clear the cap (Studio setup page, or the "
                "BOOKSMITH_TOKEN_BUDGET env var / kit_env.studio.token_budget) and "
                "re-run; the engine resumes where it stopped.")

    # -- the one public method: prompt in, text out -----------------------
    def complete(self, system: str, prompt: str, *,
                 max_tokens: Optional[int] = None,
                 temperature: Optional[float] = None,
                 stop: Optional[list] = None) -> str:
        self._check_budget()
        mt = int(max_tokens or self.cfg.get("max_tokens", 8192))
        temp = self.cfg.get("temperature", 0.7) if temperature is None else temperature
        t0 = time.time()
        err = None
        text = ""
        self._last_usage = None      # E-4: per-call token usage, when the API reports it
        retries = int(self.cfg.get("max_retries", 4))
        for attempt in range(retries):
            try:
                if self.backend == "anthropic":
                    text = self._anthropic(system, prompt, mt, temp, stop)
                elif self.backend == "openai":
                    text = self._openai(system, prompt, mt, temp, stop)
                elif self.backend == "mock":
                    text = self._mock(system, prompt, mt)
                elif self.backend == "harness":
                    raise ModelError(
                        "backend=harness is fulfilled by engine.py's disk bridge (the Claude Code "
                        "session writes the prose), not by model_client.complete().")
                else:
                    raise ModelError(f"unknown model backend: {self.backend!r}")
                err = None
                break
            except ModelError:
                raise
            except (urllib.error.URLError, TimeoutError, ConnectionError, OSError) as e:
                err = e
                # exponential backoff on transient/network errors only
                time.sleep(min(2 ** attempt, 20))
            except Exception as e:  # unexpected -> do not silently retry forever
                err = e
                break
        dt = time.time() - t0
        self._log(system, prompt, text, dt, err)
        if err is not None or not text:
            raise ModelError(f"backend={self.backend} failed after {retries} tries: {err}")
        return text

    # -- backends ---------------------------------------------------------
    def _http_json(self, url: str, headers: dict, body: dict) -> dict:
        data = json.dumps(body).encode("utf-8")
        req = urllib.request.Request(url, data=data, headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=int(self.cfg.get("timeout_s", 300))) as r:
            return json.loads(r.read().decode("utf-8"))

    def _anthropic(self, system, prompt, mt, temp, stop) -> str:
        key = os.environ.get(self.cfg.get("api_key_env", "ANTHROPIC_API_KEY")) \
            or os.environ.get("ANTHROPIC_API_KEY")
        if not key:
            raise ModelError(
                "anthropic backend needs an API key: set ANTHROPIC_API_KEY "
                "(or point kit_env.model.api_key_env at the right env var). "
                "For a no-key dry-run use backend=mock; for a local model use backend=openai.")
        base = self.cfg.get("base_url", "https://api.anthropic.com").rstrip("/")
        headers = {
            "x-api-key": key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        }
        body = {
            "model": self.cfg.get("model", "claude-opus-4-8"),
            "max_tokens": mt,
            "temperature": temp,
            "system": system,
            "messages": [{"role": "user", "content": prompt}],
        }
        if stop:
            body["stop_sequences"] = stop
        resp = self._http_json(base + "/v1/messages", headers, body)
        u = resp.get("usage") or {}
        if u:
            self._last_usage = {"in_tokens": u.get("input_tokens"),
                                "out_tokens": u.get("output_tokens")}
        parts = [b.get("text", "") for b in resp.get("content", []) if b.get("type") == "text"]
        return "".join(parts).strip()

    def _openai(self, system, prompt, mt, temp, stop) -> str:
        base = self.cfg.get("openai_base_url", self.cfg.get("base_url", "")).rstrip("/")
        if not base:
            raise ModelError("openai backend needs kit_env.model.openai_base_url")
        headers = {"content-type": "application/json"}
        key = os.environ.get("OPENAI_API_KEY")
        if key:
            headers["Authorization"] = f"Bearer {key}"
        body = {
            "model": self.cfg.get("model", "local"),
            "max_tokens": mt,
            "temperature": temp,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": prompt},
            ],
        }
        if stop:
            body["stop"] = stop
        url = base + ("/chat/completions" if not base.endswith("/chat/completions") else "")
        resp = self._http_json(url, headers, body)
        u = resp.get("usage") or {}
        if u:
            self._last_usage = {"in_tokens": u.get("prompt_tokens"),
                                "out_tokens": u.get("completion_tokens")}
        return resp["choices"][0]["message"]["content"].strip()

    def _mock(self, system, prompt, mt) -> str:
        """Deterministic, network-free. Honours a title + word target parsed from
        the prompt so the engine's real gates (H1==title, word count, em-dash,
        blacklist) can pass in a dry-run. Prose is bland but structurally valid."""
        title = None
        m = re.search(r'titled\s+"([^"]+)"', prompt) or re.search(r'H1\s*=\s*"([^"]+)"', prompt)
        if m:
            title = m.group(1)
        m = re.search(r'~?\s*(\d{2,5})\s*words', prompt)
        target = int(m.group(1)) if m else 400
        # deterministic filler: no em-dashes, no obvious blacklist words, terminates cleanly.
        seed = int(hashlib.sha256((title or prompt[:80]).encode()).hexdigest(), 16)
        sentences = [
            "The work proceeded in the order the plan required, and each step was checked before the next began.",
            "Nothing was assumed; every claim rested on what the record already held.",
            "What mattered was kept, and what did not fall away without ceremony.",
            "The account stayed close to the evidence, and the evidence stayed close to the account.",
            "A thing was true here only if the page before it had made it so.",
            "The shape held because the parts were placed, not because they were remembered.",
        ]
        out = []
        if title:
            out.append(f"# {title}\n")
        words = 0
        i = seed % len(sentences)
        para = []
        while words < target:
            s = sentences[i % len(sentences)]
            para.append(s)
            words += len(s.split())
            i += 1
            if len(para) >= 4:
                out.append(" ".join(para))
                para = []
        if para:
            out.append(" ".join(para))
        return "\n\n".join(out).strip()

    def _log(self, system, prompt, text, dt, err):
        if not self.log_dir:
            return
        self._n += 1
        rec = {
            "n": self._n,
            "backend": self.backend,
            "model": self.cfg.get("model"),
            "system_sha": hashlib.sha256(system.encode()).hexdigest()[:12],
            "prompt_sha": hashlib.sha256(prompt.encode()).hexdigest()[:12],
            "prompt_chars": len(prompt),
            "out_chars": len(text),
            "seconds": round(dt, 2),
            "error": repr(err) if err else None,
        }
        usage = getattr(self, "_last_usage", None)
        if usage:
            rec.update({k: v for k, v in usage.items() if v is not None})
        try:
            (self.log_dir / f"call_{self._n:04d}.json").write_text(
                json.dumps(rec, indent=2), encoding="utf-8")
        except Exception:
            pass


def make_client(kit_env: dict | None, log_dir: Optional[Path] = None,
                backend_override: Optional[str] = None) -> ModelClient:
    cfg = load_model_cfg(kit_env)
    if backend_override:
        cfg["backend"] = backend_override
    return ModelClient(cfg, log_dir=log_dir)


if __name__ == "__main__":
    # tiny self-test of the mock backend (no network, no key)
    c = ModelClient({"backend": "mock"})
    txt = c.complete("You write prose.", 'Write the chapter titled "Test" at ~120 words. Begin with "# Test".')
    assert txt.startswith("# Test"), txt[:60]
    assert len(txt.split()) >= 100, len(txt.split())
    print("model_client mock self-test OK:", len(txt.split()), "words")
