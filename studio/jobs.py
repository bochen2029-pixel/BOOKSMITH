#!/usr/bin/env python3
r"""
jobs.py — BOOKSMITH Studio's SPAWN primitive (S1).

One global lane, by doctrine (docs/STUDIO_SPEC.md §3.1): Word COM must never run
twice, the GPU holds one model, and an engine run already serializes a book — so
job concurrency is 1, FIFO, with cancel = kill the WHOLE process tree
(CREATE_NEW_PROCESS_GROUP + `taskkill /T /F`; a bare terminate() would orphan
WINWORD/node children).

Every job's stdout+stderr stream to `_studio/jobs/<id>.log` and to SSE
subscribers; every transition appends to `_studio/jobs.jsonl` (append-only).
The engine's own atomic state writes make cancellation safe at ANY instant —
the worst case is a `running` stage record that the next run re-keys by hash.

Engine exit codes are job SEMANTICS, not failures:
  0 complete · 2 hardstop · 3 await_model (harness bridge turn) · else error.
"""
from __future__ import annotations

import json
import os
import queue
import subprocess
import threading
import time
from datetime import datetime, timezone
from pathlib import Path

KIT = Path(__file__).resolve().parents[1]
STATE_DIR = KIT / "_studio"
JOBS_DIR = STATE_DIR / "jobs"
LEDGER = STATE_DIR / "jobs.jsonl"

SEMANTICS = {0: "complete", 2: "hardstop", 3: "await_model"}

_lock = threading.RLock()
_jobs: dict[str, dict] = {}          # id -> record (in-memory mirror of the ledger)
_order: list[str] = []               # insertion order, for listing
_pending: list[str] = []             # FIFO queue of job ids
_current_id: str | None = None
_proc: subprocess.Popen | None = None
_cancelled: set[str] = set()
_subscribers: list[queue.Queue] = []
_worker_on = False
_seq = 0


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _ledger_append(rec: dict, event: str) -> None:
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    line = json.dumps({**rec, "event": event}, ensure_ascii=False)
    with LEDGER.open("a", encoding="utf-8") as f:
        f.write(line + "\n")


# ---------------------------------------------------------------------------
# SSE fan-out
# ---------------------------------------------------------------------------
def subscribe() -> queue.Queue:
    q: queue.Queue = queue.Queue(maxsize=2000)
    with _lock:
        _subscribers.append(q)
    return q


def unsubscribe(q: queue.Queue) -> None:
    with _lock:
        if q in _subscribers:
            _subscribers.remove(q)


def _emit(ev: str, data: dict) -> None:
    for q in list(_subscribers):
        try:
            q.put_nowait((ev, data))
        except queue.Full:
            pass  # a stalled client drops events; the projection is the truth anyway


# ---------------------------------------------------------------------------
# lifecycle
# ---------------------------------------------------------------------------
def rehydrate() -> None:
    """Replay the ledger for history display; any job left 'running' by a dead
    server is marked interrupted (SPEC risk #9 — the queue never lies)."""
    if not LEDGER.exists():
        return
    last: dict[str, dict] = {}
    try:
        for line in LEDGER.read_text(encoding="utf-8", errors="replace").splitlines():
            try:
                rec = json.loads(line)
                if isinstance(rec, dict) and rec.get("id"):
                    last[rec["id"]] = rec
            except Exception:
                continue
    except OSError:
        return
    with _lock:
        for jid, rec in last.items():
            rec.pop("event", None)
            if rec.get("semantics") in ("running", "queued"):
                rec["semantics"] = "interrupted"
                rec.setdefault("ended", _now())
                _ledger_append(rec, "interrupted_on_rehydrate")
            _jobs[jid] = rec
            _order.append(jid)


def submit(kind: str, argv: list[str], book: str | None = None,
           meta: dict | None = None) -> dict:
    global _seq
    with _lock:
        _seq += 1
        jid = f"j_{time.strftime('%Y%m%d_%H%M%S')}_{_seq:03d}"
        rec = {"id": jid, "kind": kind, "book": book, "argv": argv,
               "queued": _now(), "started": None, "ended": None, "exit": None,
               "semantics": "queued", "log": str(JOBS_DIR / f"{jid}.log"),
               "meta": meta or {}}
        _jobs[jid] = rec
        _order.append(jid)
        _pending.append(jid)
        _ledger_append(rec, "queued")
        _ensure_worker()
    _emit("job", {"id": jid, "state": "queued", "book": book, "kind": kind})
    return rec


def cancel(jid: str) -> str:
    with _lock:
        rec = _jobs.get(jid)
        if not rec:
            return "unknown"
        if jid in _pending:
            _pending.remove(jid)
            rec.update(semantics="cancelled", ended=_now())
            _ledger_append(rec, "cancelled_queued")
            _emit("job", {"id": jid, "state": "exit", "book": rec.get("book"),
                          "exit": None, "semantics": "cancelled"})
            return "cancelled"
        if jid == _current_id and _proc is not None and _proc.poll() is None:
            _cancelled.add(jid)
            pid = _proc.pid
    if jid in _cancelled:
        # kill the TREE: engine spawns python/node/word children
        subprocess.run(["taskkill", "/T", "/F", "/PID", str(pid)],
                       capture_output=True)
        return "killing"
    return "finished"


def list_jobs(limit: int = 100) -> list[dict]:
    with _lock:
        return [dict(_jobs[j]) for j in reversed(_order[-limit:])]


def get(jid: str) -> dict | None:
    with _lock:
        rec = _jobs.get(jid)
        return dict(rec) if rec else None


def log_text(jid: str, offset: int = 0) -> dict:
    rec = get(jid)
    if not rec:
        return {"error": "unknown job"}
    p = Path(rec["log"])
    text = ""
    size = 0
    if p.is_file():
        raw = p.read_bytes()
        size = len(raw)
        text = raw[offset:offset + 262144].decode("utf-8", "replace")
    return {"id": jid, "offset": offset, "next_offset": min(size, offset + 262144),
            "size": size, "text": text,
            "ended": rec.get("ended") is not None}


# ---------------------------------------------------------------------------
# the worker (one lane)
# ---------------------------------------------------------------------------
def _ensure_worker() -> None:
    global _worker_on
    if _worker_on:
        return
    _worker_on = True
    threading.Thread(target=_worker, name="studio-jobs", daemon=True).start()


def _worker() -> None:
    global _current_id, _proc
    while True:
        with _lock:
            jid = _pending.pop(0) if _pending else None
            if jid:
                _current_id = jid
        if not jid:
            time.sleep(0.25)
            continue
        rec = _jobs[jid]
        JOBS_DIR.mkdir(parents=True, exist_ok=True)
        env = dict(os.environ)
        env["PYTHONUTF8"] = "1"            # the standing CJK rule (SPEC §3.2)
        env["PYTHONIOENCODING"] = "utf-8"
        rec.update(started=_now(), semantics="running")
        _ledger_append(rec, "started")
        _emit("job", {"id": jid, "state": "started", "book": rec.get("book"),
                      "kind": rec.get("kind")})
        code: int | None = None
        try:
            with open(rec["log"], "w", encoding="utf-8", errors="replace") as logf:
                _proc = subprocess.Popen(
                    rec["argv"], cwd=str(KIT), stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT, text=True, encoding="utf-8",
                    errors="replace", env=env,
                    creationflags=subprocess.CREATE_NEW_PROCESS_GROUP)
                assert _proc.stdout is not None
                for line in _proc.stdout:
                    logf.write(line)
                    logf.flush()
                    _emit("job", {"id": jid, "state": "log",
                                  "book": rec.get("book"),
                                  "chunk": line[-2000:]})
                code = _proc.wait()
        except OSError as e:
            code = 126
            try:
                with open(rec["log"], "a", encoding="utf-8") as logf:
                    logf.write(f"\nspawn failed: {e}\n")
            except OSError:
                pass
        was_cancelled = jid in _cancelled
        sem = "cancelled" if was_cancelled else SEMANTICS.get(code, "error")
        rec.update(ended=_now(), exit=code, semantics=sem)
        _ledger_append(rec, "ended")
        with _lock:
            _current_id = None
            _proc = None
            _cancelled.discard(jid)
        _emit("job", {"id": jid, "state": "exit", "book": rec.get("book"),
                      "exit": code, "semantics": sem})
        _emit("project", {"book": rec.get("book"), "hint": "state"})
        # a finished run changes staleness truth — drop the plan cache entry
        try:
            import projection
            projection._plan_cache.pop(rec.get("book"), None)
        except Exception:
            pass
