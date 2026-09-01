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
import hashlib, json, re, shutil, subprocess, sys, threading, time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

KIT = Path("/kit")
sys.path.insert(0, str(KIT / "_tools"))
WSROOT = KIT / "book_workspace"
TICKET_RE = re.compile(r"^BR-[0-9A-Z]{6}$")
LENGTH_BANDS = {"S": (8, 1200), "M": (12, 1500), "L": (16, 1800)}
MAX_UPLOAD = 60 * 1024 * 1024
TEMPLATE_TOKEN_RE = re.compile(r"\{\{[^{}\n]*\}\}")

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
    # The intent blurb is CUSTOMER-FACING (raise.html outline review). The
    # customer's own brief is the only text guaranteed prose-clean; the
    # architected seed §1 is template-shaped, and slot fragments like
    # "Success means the reader ." / "- **Sentence rhythm:**" survive any
    # line filter (seen live, BR-A11B01). Brief first; seed only as fallback.
    intent = ""
    brief = w / "brief.md"
    if brief.exists():
        btxt = brief.read_text("utf-8", errors="replace")
        m = re.search(r"^#[^\n]*\n(.*?)(?=\nWho it is for:|\nchapters:|\Z)", btxt, re.S)
        if m:
            intent = re.sub(r"\s+", " ", m.group(1)).strip()[:900]
    if not intent:
        seed = w / "seed.md"
        if seed.exists():
            txt = seed.read_text("utf-8", errors="replace")
            m = re.search(r"## §1[^\n]*\n(.*?)(?=\n## §|\Z)", txt, re.S)
            raw = (m.group(1) if m else txt[:1200])
            # prose lines only: drop headings, template bullets/labels, tables,
            # blockquotes, numbered slot lists; then scrub {{TOKENS}} wherever
            # they sit — the seed model echoes placeholders MID-LINE too
            # (seen live, BR-QC0816).
            keep = [ln.strip() for ln in raw.splitlines()
                    if ln.strip() and not ln.strip().startswith(
                        ("#", "*", "|", ">", "-", "{{",
                         "0", "1", "2", "3", "4", "5", "6", "7", "8", "9"))]
            intent = TEMPLATE_TOKEN_RE.sub(" ", " ".join(keep))
            intent = re.sub(r"\s{2,}", " ", intent).strip()[:900]
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


def _ledger_row(ticket: str, uid: str, actor: str, verb: str,
                before: str, after: str, note: str = "") -> None:
    try:
        from authorship_ledger import append_row
        append_row(ws(ticket), uid, actor, verb, before, after, note)
    except Exception as e:  # noqa: BLE001 — attribution must never kill a build
        with open(OUT, "ab") as f:
            f.write(f"\n[shim] ledger append failed (non-fatal): {e}\n".encode())


def job_revise(ticket: str, uid: str, note: str) -> None:
    """H0 L1 (PLAN_H0 §3): AI re-roll of ONE unit, then the targeted suffix.

    THE CASCADE FENCE: after any human edit, a bare engine pass would see the
    prior-prose input hash changed and redraft DOWNSTREAM units over their
    current text. So revise is exactly two targeted invocations — never bare:
      1) --only draft:<uid> --force-stage   (E-2 note honored; gates + 3 tries)
      2) --from integrate                    (lint -> assemble -> produce -> verify)
    """
    w = ws(ticket)
    cur = w / "manuscript" / "current" / f"{uid}_current.md"
    before = cur.read_text("utf-8") if cur.exists() else ""
    notes = w / "revision_notes"
    notes.mkdir(parents=True, exist_ok=True)
    with open(notes / f"{uid}.md", "a", encoding="utf-8") as f:
        f.write(f"\n- {note}\n")
    rc = engine(ticket, "--only", f"draft:{uid}", "--force-stage")
    if rc == 0:
        after = cur.read_text("utf-8") if cur.exists() else ""
        _ledger_row(ticket, uid, "ai", "revise", before, after, note[:200])
        rc = engine(ticket, "--from", "integrate")
    with LOCK:
        STATE.update(running=False, rc=rc)


def job_rebuild(ticket: str) -> None:
    """H0 manual-edit rebuild: production suffix only, no drafting, no model
    tokens — the customer's own hands are always free. Same cascade fence as
    job_revise: NEVER a bare engine pass (it would redraft over human edits)."""
    rc = engine(ticket, "--from", "integrate")
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
                                    "shim": "a13", "python": sys.version.split()[0]})
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
                # a12: /file now serves ANY workspace-relative file (the
                # manifest-driven FULL-workspace archive, H0 §3 C1 — through
                # a11c only outputs/ + cover_art/ were readable). The
                # traversal jail below is unchanged and still authoritative.
                if ".." in rel or rel.startswith(("/", "\\")) or not rel:
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
            m = re.match(r"^/unit/([a-z0-9_]{1,64})$", sub)
            if m:
                # H0 manual editing (a12): the chapter body for the web editor,
                # via the ONE implementation (_tools/manual_edit.py get).
                r = subprocess.run(
                    [sys.executable, "_tools/manual_edit.py", "get",
                     "--config", str(ws(t) / "book_config.json"), "--unit", m.group(1)],
                    capture_output=True, text=True, encoding="utf-8", cwd=str(KIT))
                try:
                    return self._json(200 if r.returncode == 0 else 409,
                                      json.loads(r.stdout))
                except json.JSONDecodeError:
                    return self._json(500, {"error": "unit get failed",
                                            "detail": (r.stdout + r.stderr)[-300:]})
            if sub == "/manifest":
                # a12: rel path + size + sha256 for every workspace file — the
                # worker archives the WHOLE workspace from this (H0 §3 C1).
                root = ws(t).resolve()
                if not root.exists():
                    return self._json(404, {"error": "no workspace"})
                items = []
                for p in sorted(root.rglob("*")):
                    if not p.is_file() or p.name.startswith("."):
                        continue
                    rel = str(p.relative_to(root)).replace("\\", "/")
                    try:
                        digest = hashlib.sha256(p.read_bytes()).hexdigest()
                    except OSError:
                        continue
                    items.append({"path": rel, "bytes": p.stat().st_size,
                                  "sha256": digest})
                    if len(items) >= 4000:
                        break
                return self._json(200, {"ok": True, "count": len(items),
                                        "files": items})
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
            for pat in ("outputs/digital/*", "outputs/kindle/*", "outputs/epub/*"):
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
            with LOCK:
                busy, job = STATE["running"], STATE["job"]
            if busy:
                # a running engine owns the workspace: a re-POSTed brief must not
                # rewrite book_config.json under it (QC 2026-08-16 #4)
                return self._json(409, {"error": "busy", "job": job})
            n_units, wpu = LENGTH_BANDS.get(str(b.get("length", "M")).upper(), LENGTH_BANDS["M"])
            w = ws(t)
            (w / "intake").mkdir(parents=True, exist_ok=True)
            title = str(b.get("title") or "Untitled")[:120]
            author = str(b.get("author") or "Anonymous")[:80]
            about = str(b.get("about") or "")[:4000]
            audience = str(b.get("audience") or "")[:1000]
            cfg = {"title": title, "author": author, "slug": slug(t),
                   "genre": ("fiction" if b.get("is_fiction") else "nonfiction"),
                   "is_fiction": bool(b.get("is_fiction")), "formats": ["kindle", "epub", "digital_pdf"],
                   "min_pages": 1, "cover": {"art": {"method": "hypergen"}}}
            if b.get("ingest_dag"):
                # a13: the gestalt ingest DAG lane (G4 ARM-C2; engine flag is
                # config-gated with a byte-identical default when absent)
                cfg["ingest"] = {"dag": True}
            (w / "book_config.json").write_text(json.dumps(cfg, indent=2), "utf-8")
            brief = (f"# {title}\n\n{about}\n\nWho it is for: {audience}\n\n"
                     f"chapters: {n_units}\nwords: {wpu}\n")
            (w / "brief.md").write_text(brief, "utf-8")
            (w / "_band.json").write_text(json.dumps({"wpu": wpu}), "utf-8")
            return self._json(200, {"ok": True, "units": n_units, "words_per_unit": wpu})

        if sub == "/file":
            return self._file_put(t)

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

        if sub == "/revise":
            # H0 L1 (a12): AI re-roll of ONE named unit. Metering/counting is
            # the WORKER's job; the shim only refuses nonsense + enforces the
            # cascade fence inside job_revise.
            b = self._body_json()
            uid = str(b.get("unit_id") or "").strip()
            note = str(b.get("note") or "").strip()[:2000]
            if not re.match(r"^[a-z0-9_]{1,64}$", uid):
                return self._json(400, {"error": "bad unit_id"})
            if not note:
                return self._json(400, {"error": "a revision note is required"})
            cur = ws(t) / "manuscript" / "current" / f"{uid}_current.md"
            if not cur.exists():
                return self._json(404, {"error": f"no such chapter: {uid}"})
            if not start("revise", t, lambda: job_revise(t, uid, note)):
                return self._json(409, {"error": "busy", "job": STATE["job"]})
            return self._json(202, {"started": "revise", "unit": uid})

        if sub == "/rebuild":
            # H0 manual-edit rebuild (a12): free (no model), targeted suffix.
            if not (ws(t) / "manuscript" / "current").exists():
                return self._json(409, {"error": "nothing to rebuild"})
            if not start("rebuild", t, lambda: job_rebuild(t)):
                return self._json(409, {"error": "busy", "job": STATE["job"]})
            return self._json(202, {"started": "rebuild"})

        if sub == "/rehydrate":
            # a12: the worker restores an archived workspace file into a cold
            # container before a revise/rebuild (H0 §3 C1). Any workspace-
            # relative path; same jail + short-read discipline as /file PUT.
            return self._workspace_put(t)

        return self._json(404, {"error": "not found"})

    # ------------------------------------------------------------------ PUT
    def do_PUT(self):
        # The site worker uploads intake files with PUT (worker.js apiIntake).
        # Through a10b the shim knew only GET/POST, so BaseHTTPRequestHandler
        # answered 501 — and no sim ever uploaded a file, so it was never
        # caught. POST /file stays for the existing receipt drivers; both
        # verbs share _file_put. Closed-verb doctrine (a12): PUT is valid for
        # /t/<ticket>/file and /t/<ticket>/unit/<uid> — nothing else.
        t, sub = self._ticket()
        if t and sub == "/file":
            return self._file_put(t)
        if t and sub:
            m = re.match(r"^/unit/([a-z0-9_]{1,64})$", sub)
            if m:
                return self._unit_put(t, m.group(1))
        return self._json(404, {"error": "not found"})

    def _read_exact(self, cap: int):
        """Read exactly content-length bytes (short-read guarded, QC L10).
        Returns bytes, or None after answering the error itself."""
        n = int(self.headers.get("content-length") or 0)
        if n <= 0 or n > cap:
            self.close_connection = True
            self._json(413, {"error": "body missing or too large"})
            return None
        remaining, chunks = n, []
        while remaining > 0:
            c = self.rfile.read(min(1 << 20, remaining))
            if not c:
                break
            chunks.append(c)
            remaining -= len(c)
        if remaining:
            self.close_connection = True
            self._json(400, {"error": f"short read: got {n - remaining} of {n} bytes"})
            return None
        return b"".join(chunks)

    def _unit_put(self, t, uid: str):
        # H0 manual editing (a12): the human's save. Body = the chapter body
        # (markdown, NO H1 — the title is locked). All laws live in
        # _tools/manual_edit.py; the shim is transport + busy-gate only.
        with LOCK:
            busy, job = STATE["running"], STATE["job"]
        if busy:
            self.close_connection = True
            return self._json(409, {"error": "busy", "job": job})
        data = self._read_exact(2 * 1024 * 1024)
        if data is None:
            return
        tmp = Path(f"/tmp/unit_put_{slug(t)}_{uid}.md")
        tmp.write_bytes(data)
        r = subprocess.run(
            [sys.executable, "_tools/manual_edit.py", "put",
             "--config", str(ws(t) / "book_config.json"), "--unit", uid,
             "--body-file", str(tmp), "--verb", "web-edit"],
            capture_output=True, text=True, encoding="utf-8", cwd=str(KIT))
        tmp.unlink(missing_ok=True)
        try:
            return self._json(200 if r.returncode == 0 else 409, json.loads(r.stdout))
        except json.JSONDecodeError:
            return self._json(500, {"error": "unit save failed",
                                    "detail": (r.stdout + r.stderr)[-300:]})

    def _workspace_put(self, t):
        # a12 rehydrate: restore ONE archived file to any workspace-relative
        # path (the worker drives this from the R2 manifest on a cold start).
        with LOCK:
            busy, job = STATE["running"], STATE["job"]
        if busy:
            self.close_connection = True
            return self._json(409, {"error": "busy", "job": job})
        q = self.path.split("?", 1)[1] if "?" in self.path else ""
        rel = ""
        for kv in q.split("&"):
            if kv.startswith("path="):
                from urllib.parse import unquote
                rel = unquote(kv[5:])
        if not rel or ".." in rel or rel.startswith(("/", "\\")):
            self.close_connection = True
            return self._json(400, {"error": "path must be workspace-relative"})
        dest = (ws(t) / rel)
        try:
            resolved = dest.resolve()
        except OSError:
            return self._json(400, {"error": "bad path"})
        root = ws(t).resolve()
        if not str(resolved).startswith(str(root)):
            self.close_connection = True
            return self._json(400, {"error": "path escapes the workspace"})
        data = self._read_exact(MAX_UPLOAD)
        if data is None:
            return
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(data)
        return self._json(200, {"ok": True, "restored": rel, "bytes": len(data)})

    def _file_put(self, t):
        with LOCK:
            busy, job = STATE["running"], STATE["job"]
        if busy:
            # a running engine owns the workspace (QC 2026-08-16 #4); body is
            # unread here, so the connection must close or keep-alive desyncs
            self.close_connection = True
            return self._json(409, {"error": "busy", "job": job})
        q = self.path.split("?", 1)[1] if "?" in self.path else ""
        rel = ""
        for kv in q.split("&"):
            if kv.startswith("path="):
                from urllib.parse import unquote
                rel = unquote(kv[5:])
        name = Path(rel).name  # basename only; uploads land flat in intake/
        if not name or ".." in rel or not rel.startswith("intake/"):
            self.close_connection = True
            return self._json(400, {"error": "path must be intake/<name>"})
        n = int(self.headers.get("content-length") or 0)
        if n <= 0 or n > MAX_UPLOAD:
            self.close_connection = True
            return self._json(413, {"error": "file too large"})
        remaining, chunks = n, []
        while remaining > 0:
            c = self.rfile.read(min(1 << 20, remaining))
            if not c:
                break
            chunks.append(c)
            remaining -= len(c)
        if remaining:
            # short read (QC L10): a truncated body must never become an
            # intake file, and the dead socket must not be reused
            self.close_connection = True
            return self._json(400, {"error": f"short read: got {n - remaining} of {n} bytes"})
        dest = ws(t) / "intake" / name
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(b"".join(chunks))
        return self._json(200, {"ok": True, "stored": f"intake/{name}", "bytes": n})


if __name__ == "__main__":
    WSROOT.mkdir(parents=True, exist_ok=True)
    ThreadingHTTPServer(("0.0.0.0", 8080), H).serve_forever()
