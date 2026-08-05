#!/usr/bin/env python3
r"""
server.py — BOOKSMITH Studio S1: read-only truth (S0) + run-and-watch (S1).

Launch:  studio.cmd            (kit root; sets the UTF-8 env, opens the browser)
   or:   python studio/server.py [--port 8756] [--no-open]

Security (docs/STUDIO_SPEC.md §3.4): binds 127.0.0.1 only; a per-launch session
token gates EVERY request (header `X-Studio-Token`, cookie, or one-time `?t=`
which then sets the cookie); Origin is checked when a browser sends one; CSP is
`self`-only and no asset is ever fetched from a CDN. Keys are never read,
stored, logged, or echoed by this server.

S1 adds the SPAWN primitive: a one-lane job runner over `engine.py` (run /
dry-run / --only single stage), SSE streaming of job logs, and cancel with
process-tree kill. Still NO ops layer and NO chat — those are S2/S3. The only
writes this server performs are its own `_studio/` runtime state; book state is
written exclusively by the engine subprocesses it spawns.
"""
from __future__ import annotations

import argparse
import json
import os
import queue as _queue
import re
import secrets
import shutil
import socket
import sys
import threading
import webbrowser
from pathlib import Path
from urllib.parse import urlparse

from fastapi import Body, FastAPI, File, HTTPException, Query, Request, UploadFile
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles

sys.path.insert(0, str(Path(__file__).resolve().parent))
import chat  # noqa: E402
import jobs  # noqa: E402
import ops  # noqa: E402
import projection as P  # noqa: E402

STUDIO_VERSION = "0.1.0-S4"
STATE_DIR = P.KIT / "_studio"
WEB_DIR = Path(__file__).resolve().parent / "web"

TOKEN: str = ""
PORT: int = 8756

_STAGE_KEY_RE = re.compile(r"^[a-z_]+(:[A-Za-z0-9._\-]+)?$")
_BACKENDS = {"mock", "anthropic", "openai", "harness"}

app = FastAPI(title="BOOKSMITH Studio", version=STUDIO_VERSION, docs_url=None,
              redoc_url=None, openapi_url=None)


# ---------------------------------------------------------------------------
# security middleware: token + origin on EVERYTHING, CSP on every response
# ---------------------------------------------------------------------------
@app.middleware("http")
async def guard(request: Request, call_next):
    origin = request.headers.get("origin")
    if origin:
        host = urlparse(origin).netloc
        if host not in {f"127.0.0.1:{PORT}", f"localhost:{PORT}"}:
            return JSONResponse({"detail": "origin not allowed"}, status_code=403)
    qt = request.query_params.get("t") or ""
    # accept ANY matching credential — a stale cookie must never shadow a fresh
    # ?t= (found live: a browser holding an old-launch cookie 403'd a valid URL)
    candidates = (request.headers.get("x-studio-token"),
                  request.cookies.get("studio_token"), qt)
    if not any(c and secrets.compare_digest(str(c), TOKEN) for c in candidates):
        return JSONResponse(
            {"detail": "missing/invalid session token — open the URL printed "
                       "by studio.cmd (it carries ?t=…)"}, status_code=403)
    response = await call_next(request)
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; img-src 'self' data:; style-src 'self'; "
        "script-src 'self'; connect-src 'self'")
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Referrer-Policy"] = "no-referrer"
    # a localhost tool is edited while it runs: never let a browser serve a
    # stale app.js/app.css (a cached broken build once looked like a dead page)
    response.headers["Cache-Control"] = "no-store, must-revalidate"
    if qt:  # one-time query token → cookie, so links/assets need no token juggling
        response.set_cookie("studio_token", TOKEN, httponly=True, samesite="strict")
    return response


def _err(e: Exception) -> HTTPException:
    return HTTPException(status_code=404 if isinstance(e, ValueError) else 500,
                         detail=str(e))


# ---------------------------------------------------------------------------
# projection API (S0, unchanged surface)
# ---------------------------------------------------------------------------
@app.get("/api/health")
def health():
    return {"ok": True, "version": STUDIO_VERSION, "kit_root": str(P.KIT),
            "port": PORT, "scope": "S4 full book surface"}


@app.get("/api/doctor")
def doctor(refresh: int = 0):
    return P.doctor(refresh=bool(refresh))


@app.get("/api/books")
def books():
    return P.list_books()


@app.get("/api/books/{slug}")
def book(slug: str):
    try:
        return P.book_detail(slug)
    except ValueError as e:
        raise _err(e)


@app.get("/api/books/{slug}/plan")
def plan(slug: str, refresh: int = 0):
    try:
        return P.plan(slug, refresh=bool(refresh))
    except ValueError as e:
        raise _err(e)


@app.get("/api/books/{slug}/units")
def units(slug: str):
    try:
        return P.units(slug)
    except ValueError as e:
        raise _err(e)


@app.get("/api/books/{slug}/units/{uid}")
def unit(slug: str, uid: str):
    try:
        return P.unit_detail(slug, uid)
    except ValueError as e:
        raise _err(e)


@app.get("/api/books/{slug}/units/{uid}/version")
def unit_version(slug: str, uid: str, v: str = "current"):
    """S10 take-picker: one archived (or current) take's full text."""
    try:
        return P.unit_version_text(slug, uid, v)
    except ValueError as e:
        raise _err(e)


@app.get("/api/books/{slug}/passport")
def passport(slug: str):
    """S10: the shareable, self-contained receipts page for one book."""
    try:
        html = P.passport_html(slug)
    except ValueError as e:
        raise _err(e)
    from fastapi.responses import HTMLResponse
    return HTMLResponse(html)


@app.get("/api/books/{slug}/units/{uid}/diff")
def unit_diff(slug: str, uid: str, a: str = Query("v1"), b: str = Query("current")):
    try:
        return P.unit_diff(slug, uid, a, b)
    except ValueError as e:
        raise _err(e)


@app.get("/api/books/{slug}/artifacts")
def artifacts(slug: str):
    try:
        return P.artifacts(slug)
    except ValueError as e:
        raise _err(e)


@app.get("/api/books/{slug}/file")
def ws_file(slug: str, path: str):
    try:
        p = P.safe_ws_file(slug, path)
    except ValueError as e:
        raise _err(e)
    return FileResponse(p, filename=p.name)


@app.get("/api/books/{slug}/bridge")
def bridge(slug: str):
    try:
        return P.bridge(slug)
    except ValueError as e:
        raise _err(e)


@app.get("/api/books/{slug}/spend")
def spend(slug: str):
    try:
        return P.spend(slug)
    except ValueError as e:
        raise _err(e)


@app.get("/api/books/{slug}/log")
def book_log(slug: str, n: int = 120):
    try:
        return P.log_tail(slug, n=max(1, min(n, 500)))
    except ValueError as e:
        raise _err(e)


# ---------------------------------------------------------------------------
# S1: runs + jobs + SSE (the SPAWN primitive behind SAFE-class actions)
# ---------------------------------------------------------------------------
@app.post("/api/books/{slug}/runs")
def start_run(slug: str, payload: dict = Body(default={})):
    try:
        ws = P.resolve_slug(slug)
    except ValueError as e:
        raise _err(e)
    mode = str(payload.get("mode") or "run")
    backend = payload.get("backend") or None
    stage = payload.get("stage") or None
    to = payload.get("to") or None
    frm = payload.get("from") or None
    force = bool(payload.get("force"))
    if mode not in {"run", "dry_run", "stage"}:
        raise HTTPException(400, "mode must be run | dry_run | stage")
    if backend is not None and backend not in _BACKENDS:
        raise HTTPException(400, f"backend must be one of {sorted(_BACKENDS)}")
    for k, v in (("stage", stage), ("to", to), ("from", frm)):
        if v is not None and not _STAGE_KEY_RE.match(str(v)):
            raise HTTPException(400, f"bad {k} stage key: {v!r}")
    argv = [sys.executable, str(P.TOOLS / "engine.py"),
            "--config", str(ws / "book_config.json")]
    if mode == "dry_run":
        argv.append("--dry-run")
    elif mode == "stage":
        if not stage:
            raise HTTPException(400, "mode=stage requires a stage key")
        argv += ["--only", str(stage)]
        if force:
            argv.append("--force-stage")
    if backend:
        argv += ["--backend", backend]
    if to:
        argv += ["--to", str(to)]
    if frm:
        argv += ["--from", str(frm)]
    rec = jobs.submit("engine_stage" if mode == "stage" else "engine_run",
                      argv, book=slug,
                      meta={"mode": mode, "backend": backend or "(kit default)",
                            "stage": stage, "to": to, "from": frm, "force": force})
    return rec


@app.get("/api/jobs")
def jobs_list(limit: int = 100):
    return jobs.list_jobs(limit=max(1, min(limit, 300)))


@app.get("/api/jobs/{jid}")
def job_get(jid: str):
    rec = jobs.get(jid)
    if not rec:
        raise HTTPException(404, "unknown job")
    return rec


@app.get("/api/jobs/{jid}/log")
def job_log(jid: str, offset: int = 0):
    return jobs.log_text(jid, offset=max(0, offset))


@app.post("/api/jobs/{jid}/cancel")
def job_cancel(jid: str):
    return {"id": jid, "result": jobs.cancel(jid)}


# ---------------------------------------------------------------------------
# S2: the ops layer (single write path) + proposals
# ---------------------------------------------------------------------------
@app.post("/api/books/{slug}/ops")
def book_ops(slug: str, payload: dict = Body(default={})):
    try:
        # S10: a button surface may submit a multi-op PLAN (e.g. three takes of
        # one chapter). Same channel the chat uses: every item validated, one
        # proposal, one human approval. Single-op payloads behave as before.
        if isinstance(payload.get("ops"), list):
            prop = ops.submit_plan(slug, payload["ops"], {"kind": "button"},
                                   summary=payload.get("summary") or None)
            return {"proposal": prop}
        return ops.submit_op(slug, payload)
    except ops.OpError as e:
        raise HTTPException(400, str(e))
    except ValueError as e:
        raise _err(e)


@app.get("/api/books/{slug}/proposals")
def proposals(slug: str):
    try:
        return ops.list_proposals(slug)
    except ValueError as e:
        raise _err(e)


@app.post("/api/books/{slug}/proposals/{pid}/approve")
def proposal_approve(slug: str, pid: str, payload: dict = Body(default={})):
    try:
        return ops.approve(slug, pid, backend=payload.get("backend") or None)
    except ops.OpError as e:
        raise HTTPException(400, str(e))
    except ValueError as e:
        raise _err(e)


@app.post("/api/books/{slug}/proposals/{pid}/reject")
def proposal_reject(slug: str, pid: str):
    try:
        return ops.reject(slug, pid)
    except ops.OpError as e:
        raise HTTPException(400, str(e))
    except ValueError as e:
        raise _err(e)


# ---------------------------------------------------------------------------
# S3: the revision chat (a COMPILER — it can only produce proposals)
# ---------------------------------------------------------------------------
@app.get("/api/books/{slug}/chat/history")
def chat_history(slug: str, limit: int = 200):
    try:
        return chat.history(slug, limit=max(1, min(limit, 500)))
    except ValueError as e:
        raise _err(e)


@app.post("/api/books/{slug}/chat/messages")
def chat_send(slug: str, payload: dict = Body(default={})):
    backend = payload.get("backend") or None
    if backend is not None and backend not in _BACKENDS:
        raise HTTPException(400, f"backend must be one of {sorted(_BACKENDS)}")
    try:
        return chat.send(slug, str(payload.get("text") or ""), backend=backend)
    except ops.OpError as e:
        raise HTTPException(400, str(e))
    except ValueError as e:
        raise _err(e)
    except Exception as e:                     # a model/transport failure is a
        # normal outcome here (no key, server down) — report it as data, not a 500
        raise HTTPException(502, f"{type(e).__name__}: {e}")


# ---------------------------------------------------------------------------
# S4: cover studio · verify matrix · intake · new book · settings
# ---------------------------------------------------------------------------
@app.get("/api/books/{slug}/cover")
def cover(slug: str):
    try:
        return P.cover(slug)
    except ValueError as e:
        raise _err(e)


@app.get("/api/books/{slug}/verify")
def verify_matrix(slug: str):
    try:
        return P.verify_matrix(slug)
    except ValueError as e:
        raise _err(e)


@app.get("/api/books/{slug}/intake")
def intake(slug: str):
    try:
        return P.intake(slug)
    except ValueError as e:
        raise _err(e)


@app.put("/api/books/{slug}/brief")
def put_brief(slug: str, payload: dict = Body(default={})):
    """The gist. Writing it is not a book mutation the engine gates — it is the
    INPUT the architect stage reads, and the ingest/seed hashes cover it."""
    try:
        ws = P.resolve_slug(slug)
    except ValueError as e:
        raise _err(e)
    text = str(payload.get("text") or "")
    if len(text) > 200_000:
        raise HTTPException(400, "brief too long")
    (ws / "brief.md").write_text(text, encoding="utf-8")
    return {"ok": True, "chars": len(text)}


_SAFE_NAME = re.compile(r"^[A-Za-z0-9][A-Za-z0-9 ._\-()一-鿿]{0,120}$")


@app.post("/api/books/{slug}/intake/files")
async def upload_intake(slug: str, file: UploadFile = File(...)):
    try:
        ws = P.resolve_slug(slug)
    except ValueError as e:
        raise _err(e)
    name = Path(file.filename or "").name          # strip any path component
    if not name or not _SAFE_NAME.match(name):
        raise HTTPException(400, f"unsafe filename: {file.filename!r}")
    dest = (ws / "intake" / name)
    dest.parent.mkdir(parents=True, exist_ok=True)
    size = 0
    with dest.open("wb") as out:
        while chunk := await file.read(1 << 20):
            size += len(chunk)
            if size > 200 * (1 << 20):
                out.close()
                dest.unlink(missing_ok=True)
                raise HTTPException(413, "file exceeds the 200 MB intake cap")
            out.write(chunk)
    return {"ok": True, "name": name, "size": size}


@app.delete("/api/books/{slug}/intake/files")
def delete_intake(slug: str, name: str):
    try:
        ws = P.resolve_slug(slug)
    except ValueError as e:
        raise _err(e)
    p = (ws / "intake" / Path(name).name)
    if not p.is_file() or p.parent != (ws / "intake"):
        raise HTTPException(404, "no such intake file")
    p.unlink()
    return {"ok": True}


_SLUG_OK = re.compile(r"^[a-z0-9][a-z0-9_\-]{1,60}$")


@app.post("/api/books")
def create_book(payload: dict = Body(default={})):
    """New book: clone the SHIPPED reference book's config as the defaults
    skeleton (guaranteeing schema validity and pipeline compatibility — the same
    trick engine_smoketest uses), then overwrite identity + clear units so the
    architect stage builds the book from the gist."""
    slug = str(payload.get("slug") or "").strip().lower()
    if not _SLUG_OK.match(slug):
        raise HTTPException(400, "slug must be lowercase letters/digits/-/_ (2–61 chars)")
    ws = P.WS_ROOT / slug
    if ws.exists():
        raise HTTPException(409, f"book_workspace/{slug} already exists")
    ref = P.WS_ROOT / "testvoyage" / "book_config.json"
    if not ref.is_file():
        # Portability: a stranger's fresh copy may lack the reference workspace.
        # A vendored snapshot of the same config ships with the Studio itself.
        ref = Path(__file__).resolve().parent / "reference_config.json"
    if not ref.is_file():
        raise HTTPException(500, "no reference config found (book_workspace/testvoyage/"
                                 "book_config.json or studio/reference_config.json); "
                                 "cannot derive defaults")
    cfg = json.loads(ref.read_text(encoding="utf-8"))
    formats = [f for f in (payload.get("formats") or ["kindle", "epub"]) if isinstance(f, str)]
    if not formats:
        raise HTTPException(400, "pick at least one format")
    cfg.update({
        "title": str(payload.get("title") or slug)[:200],
        "subtitle": str(payload.get("subtitle") or "")[:200],
        "author": str(payload.get("author") or "")[:120],
        "slug": slug,
        "genre": str(payload.get("genre") or "")[:120],
        "is_fiction": bool(payload.get("is_fiction")),
        "formats": formats,
        "units": [],
    })
    if not payload.get("keep_ceremonial"):
        # The reference book's ceremonial content must not be inherited. These
        # keys are optional in the schema, so DROP them (blanking breaks the
        # shape: dedication is a string, epigraph an object) — and drop their
        # front-matter pages plus each one's paired blank verso, so the
        # ceremonial sequence stays recto-correct instead of leaving empty pages.
        for k in ("dedication", "epigraph", "about_the_author"):
            cfg.pop(k, None)
        seq, out, skip_blank = cfg.get("front_matter") or [], [], False
        for entry in seq:
            t = (entry or {}).get("type")
            if t in ("dedication", "epigraph"):
                skip_blank = True
                continue
            if skip_blank and t == "blank":
                skip_blank = False
                continue
            skip_blank = False
            out.append(entry)
        cfg["front_matter"] = out
    if payload.get("domain") and payload["domain"] != "book":
        cfg["domain"] = str(payload["domain"])
    try:
        import jsonschema
        jsonschema.validate(cfg, json.loads(
            (P.TOOLS / "book_config.schema.json").read_text(encoding="utf-8")))
    except ImportError:
        pass
    except Exception as e:
        raise HTTPException(400, f"generated config fails the schema: "
                                 f"{str(e).splitlines()[0][:200]}")
    for sub in ("intake", "contracts", "manuscript/current", "manuscript/drafts"):
        (ws / sub).mkdir(parents=True, exist_ok=True)
    (ws / "book_config.json").write_text(json.dumps(cfg, indent=2, ensure_ascii=False),
                                         encoding="utf-8")
    (ws / "brief.md").write_text(str(payload.get("brief") or ""), encoding="utf-8")
    (ws / "CHANGELOG.md").write_text(
        f"# CHANGELOG\n\n- {P._iso(__import__('time').time())} [studio] book created\n",
        encoding="utf-8")
    return {"ok": True, "slug": slug}


_SETTINGS_WRITABLE = {"model": {"backend", "model", "base_url", "openai_base_url",
                                "max_tokens", "temperature", "timeout_s"},
                      "vision": {"backend"},
                      "cover_gen": {"comfyui_server", "checkpoints_dir", "default_checkpoint"},
                      # S7/S8: the Conductor's setup page — autolaunch, and the
                      # E-6 spend floor (token budget) + optional display pricing
                      "studio": {"autolaunch", "port", "token_budget",
                                 "price_in_per_mtok", "price_out_per_mtok"}}


def _sync_budget_env() -> None:
    """E-6 wiring: kit_env.studio.token_budget becomes BOOKSMITH_TOKEN_BUDGET in
    THIS process's env, which every spawned job (engine runs) and every
    in-process model call (chat compiles, test pings) inherits. The floor itself
    lives in model_client._check_budget — arithmetic, not discretion."""
    try:
        env = json.loads(_kit_env_path().read_text(encoding="utf-8"))
        cap = (env.get("studio") or {}).get("token_budget")
        if cap and int(cap) > 0:
            os.environ["BOOKSMITH_TOKEN_BUDGET"] = str(int(cap))
        else:
            os.environ.pop("BOOKSMITH_TOKEN_BUDGET", None)
    except Exception:
        pass


def _kit_env_path() -> Path:
    p = P.TOOLS / "kit_env.json"
    if not p.is_file():
        shutil.copyfile(P.TOOLS / "kit_env.template.json", p)
    return p


@app.get("/api/settings")
def get_settings():
    env = json.loads(_kit_env_path().read_text(encoding="utf-8"))
    model = dict(env.get("model") or {})
    key_env = model.get("api_key_env") or "ANTHROPIC_API_KEY"
    return {
        "model": {k: v for k, v in model.items() if not k.startswith("_") and k != "note"},
        "vision": {"backend": (env.get("vision") or {}).get("backend")},
        "cover_gen": {k: (env.get("cover_gen") or {}).get(k)
                      for k in _SETTINGS_WRITABLE["cover_gen"]},
        "studio": {k: (env.get("studio") or {}).get(k)
                   for k in _SETTINGS_WRITABLE["studio"]},
        "keys": {  # presence ONLY — a key is never read into a response
            key_env: bool(os.environ.get(key_env)),
            "ANTHROPIC_API_KEY": bool(os.environ.get("ANTHROPIC_API_KEY")),
            "OPENAI_API_KEY": bool(os.environ.get("OPENAI_API_KEY")),
        },
        "api_key_env": key_env,
        "writable": {k: sorted(v) for k, v in _SETTINGS_WRITABLE.items()},
    }


@app.put("/api/settings")
def put_settings(payload: dict = Body(default={})):
    p = _kit_env_path()
    env = json.loads(p.read_text(encoding="utf-8"))
    changed = []
    for block, keys in _SETTINGS_WRITABLE.items():
        incoming = payload.get(block)
        if not isinstance(incoming, dict):
            continue
        env.setdefault(block, {})
        for k, v in incoming.items():
            if k not in keys:
                raise HTTPException(400, f"{block}.{k} is not writable from the Studio")
            if isinstance(v, (str, int, float, bool)) or v is None:
                env[block][k] = v
                changed.append(f"{block}.{k}")
            else:
                raise HTTPException(400, f"{block}.{k} must be a scalar")
    tmp = p.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(env, indent=2, ensure_ascii=False), encoding="utf-8")
    tmp.replace(p)
    _sync_budget_env()      # a changed cap takes effect for the next call/job
    return {"ok": True, "changed": changed}


@app.post("/api/settings/key")
def set_key(payload: dict = Body(default={})):
    """Set an API key for THIS server process only (session-scoped). The Studio
    never writes a key to disk; it returns the command to persist it yourself."""
    name = str(payload.get("name") or "").strip()
    if name not in ("ANTHROPIC_API_KEY", "OPENAI_API_KEY"):
        raise HTTPException(400, "key name must be ANTHROPIC_API_KEY or OPENAI_API_KEY")
    value = str(payload.get("value") or "")
    if not value or len(value) > 400:
        raise HTTPException(400, "missing or implausible key value")
    os.environ[name] = value
    return {"ok": True, "name": name, "scope": "this Studio process only",
            "persist_hint": f'setx {name} "<your-key>"   (new terminals only; '
                            f'restart the Studio afterwards)'}


@app.post("/api/settings/test-model")
def test_model(payload: dict = Body(default={})):
    sys.path.insert(0, str(P.TOOLS))
    import model_client  # noqa: PLC0415
    env = json.loads(_kit_env_path().read_text(encoding="utf-8"))
    backend = payload.get("backend") or None
    if backend is not None and backend not in _BACKENDS:
        raise HTTPException(400, "bad backend")
    cli = model_client.make_client(env, log_dir=None, backend_override=backend)
    if cli.backend == "harness":
        return {"ok": False, "backend": "harness",
                "detail": "the harness backend is fulfilled by a Claude Code session "
                          "over the disk bridge, not by a direct call"}
    import time as _t
    t0 = _t.time()
    try:
        txt = cli.complete("Reply with the single word: ready.",
                           "Reply with the single word: ready.", max_tokens=16,
                           temperature=0)
        return {"ok": True, "backend": cli.backend, "model": cli.cfg.get("model"),
                "seconds": round(_t.time() - t0, 2), "reply": txt[:120]}
    except Exception as e:
        return {"ok": False, "backend": cli.backend, "model": cli.cfg.get("model"),
                "detail": f"{type(e).__name__}: {e}"}


@app.get("/api/events")
def events():
    q = jobs.subscribe()

    def gen():
        try:
            yield ": studio event stream\n\n"
            while True:
                try:
                    ev, data = q.get(timeout=15)
                    yield f"event: {ev}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"
                except _queue.Empty:
                    yield ": keepalive\n\n"
        finally:
            jobs.unsubscribe(q)

    return StreamingResponse(gen(), media_type="text/event-stream",
                             headers={"Cache-Control": "no-cache",
                                      "X-Accel-Buffering": "no"})


app.mount("/", StaticFiles(directory=str(WEB_DIR), html=True), name="web")


# ---------------------------------------------------------------------------
# launch
# ---------------------------------------------------------------------------
def _free_port(start: int) -> int:
    for port in range(start, start + 21):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.bind(("127.0.0.1", port))
            s.close()
            return port
        except OSError:
            s.close()
    raise SystemExit(f"no free port in {start}..{start + 20}")


def main() -> int:
    global TOKEN, PORT
    ap = argparse.ArgumentParser(description="BOOKSMITH Studio (S1)")
    ap.add_argument("--port", type=int, default=8756)
    ap.add_argument("--no-open", action="store_true")
    args = ap.parse_args()

    import uvicorn  # deferred so `--help` works without it

    PORT = _free_port(args.port)
    TOKEN = secrets.token_urlsafe(24)
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    (STATE_DIR / "token").write_text(TOKEN, encoding="utf-8")
    jobs.rehydrate()
    _sync_budget_env()      # E-6: the spend floor rides every job + chat call

    url = f"http://127.0.0.1:{PORT}/?t={TOKEN}"
    print(f"\n  BOOKSMITH Studio {STUDIO_VERSION}")
    print(f"  kit:  {P.KIT}")
    print(f"  open: {url}\n")
    if not args.no_open:
        threading.Timer(1.2, lambda: webbrowser.open(url)).start()
    uvicorn.run(app, host="127.0.0.1", port=PORT, log_level="warning")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
