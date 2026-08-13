#!/usr/bin/env python3
"""cloud/shim.py — the engine container's HTTP face (P0 demo jobs + Session A tickets).

Closed-verb doctrine: this is NEVER a general executor. The only verbs are the kit's
own proof jobs (/run/smoketest|selfcheck) and the fixed per-ticket book phases
(init -> intake files -> outline -> build -> download). The Worker in front holds the
bearer token; this shim additionally validates every ticket id and path prefix.

Ticket layout (one per paid order): /kit/book_workspace/<BR-XXXXXX>/
Model + spend config arrive as container ENV (set by the Worker's Container class):
  BOOKSMITH_MODEL_BACKEND / _ID / _BASE_URL, OPENAI_API_KEY,
  BOOKSMITH_TOKEN_BUDGET  <- the ALPHA FLOOR (hard E-6 stop inside model_client).
"""
from __future__ import annotations
import json, re, shutil, subprocess, sys, threading, time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

KIT = Path("/kit")
WSROOT = KIT / "book_workspace"
TICKET_RE = re.compile(r"^BR-[0-9A-Z]{6}$")
LENGTH_BANDS = {"S": (8, 1200), "M": (12, 1500), "L": (16, 1800)}
MAX_UPLOAD = 60 * 1024 * 1024

PROOF_JOBS = {
    "smoketest": [sys.executable, "_tools/engine_smoketest.py"],
    "selfcheck": [sys.executable, "_tools/selfcheck.py"],
}
STATE = {"job": None, "ticket": None, "running": False, "rc": None, "started": None}
LOCK = threading.Lock()
OUT = "/tmp/job.out"


def slug(ticket: str) -> str:
    """Ticket id (BR-XXXXXX) -> kit slug/dir (br_xxxxxx): GATE-2 requires ^[a-z0-9_]+$."""
    return ticket.lower().replace("-", "_")


def ws(ticket: str) -> Path:
    return WSROOT / slug(ticket)


def engine(ticket: str, *extra: str) -> int:
    cmd = [sys.executable, "_tools/engine.py", "--config",
           str(ws(ticket) / "book_config.json"), "--backend", "openai", *extra]
    with open(OUT, "wb") as f:
        return subprocess.Popen(cmd, stdout=f, stderr=subprocess.STDOUT, cwd=str(KIT)).wait()


def normalize_classes(ticket: str) -> None:
    """One-shot rules: (G-M1) no human fills Class A/B; and the LENGTH BAND is the
    product's promise — the plan model may shrink per-unit targets (it guessed 150w
    live), so target_words is forced back to the band's figure deterministically."""
    w = ws(ticket)
    p = w / "book_config.json"
    cfg = json.loads(p.read_text("utf-8"))
    wpu = 0
    try:
        wpu = int(json.loads((w / "_band.json").read_text("utf-8")).get("wpu", 0))
    except Exception:  # noqa: BLE001
        pass
    for u in cfg.get("units", []):
        u["class"] = "C"
        if wpu:
            u["target_words"] = wpu
    cfg.setdefault("authorship", {})["default_class"] = "C"
    cfg["authorship"]["per_chapter_overrides"] = {}
    p.write_text(json.dumps(cfg, indent=2), "utf-8")


def outline_json(ticket: str) -> dict:
    w = ws(ticket)
    cfg = json.loads((w / "book_config.json").read_text("utf-8"))
    intent = ""
    seed = w / "seed.md"
    if seed.exists():
        txt = seed.read_text("utf-8", errors="replace")
        m = re.search(r"## §1[^\n]*\n(.*?)(?=\n## §|\Z)", txt, re.S)
        raw = (m.group(1) if m else txt[:1200])
        # keep prose lines only: drop headings, italic template instructions, tables
        keep = [ln.strip() for ln in raw.splitlines()
                if ln.strip() and not ln.strip().startswith(("#", "*", "|", "{{"))]
        intent = " ".join(keep).strip()[:900]
    return {"title": cfg.get("title"), "author": cfg.get("author"), "intent": intent,
            "units": [{"id": u.get("id"), "title": u.get("title"),
                       "target_words": u.get("target_words")} for u in cfg.get("units", [])]}


def job_outline(ticket: str) -> None:
    rc = engine(ticket, "--to", "precheck", "--fresh")
    if rc == 0:
        try:
            normalize_classes(ticket)
            (ws(ticket) / "_outline.json").write_text(
                json.dumps(outline_json(ticket)), "utf-8")
        except Exception as e:  # noqa: BLE001
            with open(OUT, "ab") as f:
                f.write(f"\n[shim] outline post-process failed: {e}\n".encode())
            rc = 1
    with LOCK:
        STATE.update(running=False, rc=rc)


def job_build(ticket: str) -> None:
    rc = engine(ticket)
    with LOCK:
        STATE.update(running=False, rc=rc)


def job_proof(job: str) -> None:
    with open(OUT, "wb") as f:
        rc = subprocess.Popen(PROOF_JOBS[job], stdout=f, stderr=subprocess.STDOUT,
                              cwd=str(KIT)).wait()
    with LOCK:
        STATE.update(running=False, rc=rc)


def start(job: str, ticket: str | None, target) -> bool:
    with LOCK:
        if STATE["running"]:
            return False
        STATE.update(job=job, ticket=ticket, running=True, rc=None, started=time.time())
    open(OUT, "wb").close()
    threading.Thread(target=target, daemon=True).start()
    return True


def engine_stage_summary(ticket: str) -> dict:
    try:
        st = json.loads((ws(ticket) / "_engine" / "state.json").read_text("utf-8"))["stages"]
        done = [k for k, v in st.items() if v.get("status") == "done"]
        cur = [f'{k}:{v.get("status")}' for k, v in st.items() if v.get("status") != "done"]
        return {"done": len(done), "pending": cur[:4], "last_done": done[-1] if done else None}
    except Exception:  # noqa: BLE001
        return {}


def ledger(ticket: str) -> dict:
    tin = tout = n = 0
    for f in (ws(ticket) / "_engine" / "calls").glob("call_*.json"):
        try:
            c = json.loads(f.read_text("utf-8"))
            n += 1
            tin += c.get("in_tokens") or 0
            tout += c.get("out_tokens") or 0
        except Exception:  # noqa: BLE001
            pass
    return {"calls": n, "in_tokens": tin, "out_tokens": tout}


class H(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def _json(self, code: int, obj: dict) -> None:
        body = json.dumps(obj).encode("utf-8")
        self.send_response(code)
        self.send_header("content-type", "application/json")
        self.send_header("content-length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *a):
        pass

    def _ticket(self):
        m = re.match(r"^/t/(BR-[0-9A-Z]{6})(/.*)?$", self.path.split("?")[0])
        if not m or not TICKET_RE.match(m.group(1)):
            return None, None
        return m.group(1), (m.group(2) or "")

    def _body_json(self) -> dict:
        n = int(self.headers.get("content-length") or 0)
        try:
            return json.loads(self.rfile.read(n).decode("utf-8")) if n else {}
        except Exception:  # noqa: BLE001
            return {}

    # ------------------------------------------------------------------ GET
    def do_GET(self):
        path = self.path.split("?")[0]
        if path == "/":
            return self._json(200, {"ok": True, "service": "booksmith-runner",
                                    "shim": "a8", "python": sys.version.split()[0]})
        if path == "/status":
            return self._status(None)
        t, sub = self._ticket()
        if t:
            if sub == "/status":
                return self._status(t)
            if sub == "/outline":
                p = ws(t) / "_outline.json"
                if not p.exists():
                    return self._json(404, {"error": "no outline yet"})
                return self._json(200, json.loads(p.read_text("utf-8")))
            if sub == "/file":
                q = self.path.split("?", 1)[1] if "?" in self.path else ""
                rel = ""
                for kv in q.split("&"):
                    if kv.startswith("path="):
                        from urllib.parse import unquote
                        rel = unquote(kv[5:])
                if not (rel.startswith("outputs/") or rel.startswith("cover_art/")) or ".." in rel:
                    return self._json(400, {"error": "path not allowed"})
                p = (ws(t) / rel).resolve()
                if not str(p).startswith(str(ws(t).resolve())) or not p.is_file():
                    return self._json(404, {"error": "not found"})
                data = p.read_bytes()
                self.send_response(200)
                self.send_header("content-type", "application/octet-stream")
                self.send_header("content-length", str(len(data)))
                self.send_header("x-filename", p.name)
                self.end_headers()
                self.wfile.write(data)
                return
        return self._json(404, {"error": "not found"})

    def _status(self, ticket):
        with LOCK:
            st = dict(STATE)
        st["seconds"] = round(time.time() - st["started"], 1) if st["started"] else None
        tail = ""
        try:
            with open(OUT, "rb") as f:
                f.seek(0, 2)
                f.seek(max(0, f.tell() - 3000))
                tail = f.read().decode("utf-8", "replace")
        except OSError:
            pass
        st["tail"] = tail
        if ticket:
            st["mine"] = (st.get("ticket") == ticket)
            st["stages"] = engine_stage_summary(ticket)
            st["ledger"] = ledger(ticket)
            st["outline_ready"] = (ws(ticket) / "_outline.json").exists()
            outs = []
            for pat in ("outputs/kindle/*", "outputs/epub/*"):
                outs += [str(p.relative_to(ws(ticket))).replace("\\", "/")
                         for p in ws(ticket).glob(pat) if p.is_file()]
            st["outputs"] = sorted(outs)
        return self._json(200, st)

    # ----------------------------------------------------------------- POST
    def do_POST(self):
        path = self.path.split("?")[0]
        if path.startswith("/run/"):
            job = path[len("/run/"):]
            if job not in PROOF_JOBS:
                return self._json(404, {"error": "unknown job"})
            if not start(job, None, lambda: job_proof(job)):
                return self._json(409, {"error": "busy", "job": STATE["job"]})
            return self._json(202, {"started": job})

        t, sub = self._ticket()
        if not t:
            return self._json(404, {"error": "not found"})

        if sub == "/init":
            b = self._body_json()
            n_units, wpu = LENGTH_BANDS.get(str(b.get("length", "M")).upper(), LENGTH_BANDS["M"])
            w = ws(t)
            (w / "intake").mkdir(parents=True, exist_ok=True)
            title = str(b.get("title") or "Untitled")[:120]
            author = str(b.get("author") or "Anonymous")[:80]
            about = str(b.get("about") or "")[:4000]
            audience = str(b.get("audience") or "")[:1000]
            cfg = {"title": title, "author": author, "slug": slug(t),
                   "genre": ("fiction" if b.get("is_fiction") else "nonfiction"),
                   "is_fiction": bool(b.get("is_fiction")), "formats": ["kindle", "epub"],
                   "min_pages": 1, "cover": {"art": {"method": "hypergen"}}}
            (w / "book_config.json").write_text(json.dumps(cfg, indent=2), "utf-8")
            brief = (f"# {title}\n\n{about}\n\nWho it is for: {audience}\n\n"
                     f"chapters: {n_units}\nwords: {wpu}\n")
            (w / "brief.md").write_text(brief, "utf-8")
            (w / "_band.json").write_text(json.dumps({"wpu": wpu}), "utf-8")
            return self._json(200, {"ok": True, "units": n_units, "words_per_unit": wpu})

        if sub == "/file":
            q = self.path.split("?", 1)[1] if "?" in self.path else ""
            rel = ""
            for kv in q.split("&"):
                if kv.startswith("path="):
                    from urllib.parse import unquote
                    rel = unquote(kv[5:])
            name = Path(rel).name  # basename only; uploads land flat in intake/
            if not name or ".." in rel or not rel.startswith("intake/"):
                return self._json(400, {"error": "path must be intake/<name>"})
            n = int(self.headers.get("content-length") or 0)
            if n <= 0 or n > MAX_UPLOAD:
                return self._json(413, {"error": "file too large"})
            dest = ws(t) / "intake" / name
            dest.parent.mkdir(parents=True, exist_ok=True)
            remaining, chunks = n, []
            while remaining > 0:
                c = self.rfile.read(min(1 << 20, remaining))
                if not c:
                    break
                chunks.append(c)
                remaining -= len(c)
            dest.write_bytes(b"".join(chunks))
            return self._json(200, {"ok": True, "stored": f"intake/{name}", "bytes": n})

        if sub == "/outline":
            b = self._body_json()
            note = str(b.get("note") or "").strip()[:2000]
            w = ws(t)
            if not (w / "book_config.json").exists():
                return self._json(409, {"error": "ticket not initialized"})
            if note:
                with open(w / "brief.md", "a", encoding="utf-8") as f:
                    f.write(f"\n\nREVISION NOTE (honor this in the new outline): {note}\n")
            # re-architect cleanly: keep brief + intake, drop derived artifacts
            for d in ("_engine", "contracts", "registry", "exemplars", "canon_refs",
                      "manuscript", "outputs"):
                shutil.rmtree(w / d, ignore_errors=True)
            for f in ("seed.md", "_outline.json"):
                (w / f).unlink(missing_ok=True)
            cfg = json.loads((w / "book_config.json").read_text("utf-8"))
            cfg.pop("units", None)
            (w / "book_config.json").write_text(json.dumps(cfg, indent=2), "utf-8")
            if not start("outline", t, lambda: job_outline(t)):
                return self._json(409, {"error": "busy", "job": STATE["job"]})
            return self._json(202, {"started": "outline"})

        if sub == "/build":
            if not (ws(t) / "_outline.json").exists():
                return self._json(409, {"error": "no approved outline"})
            if not start("build", t, lambda: job_build(t)):
                return self._json(409, {"error": "busy", "job": STATE["job"]})
            return self._json(202, {"started": "build"})

        return self._json(404, {"error": "not found"})


if __name__ == "__main__":
    WSROOT.mkdir(parents=True, exist_ok=True)
    ThreadingHTTPServer(("0.0.0.0", 8080), H).serve_forever()
