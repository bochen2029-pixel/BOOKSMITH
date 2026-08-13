#!/usr/bin/env python3
"""cloud/shim.py — the P0 demo shim: a fixed-job HTTP face for the engine container.

Runs INSIDE the container (CMD of cloud/Dockerfile.cf) so a Cloudflare Worker can
drive the P0 proof over HTTP. Deliberately NOT a general executor: the only verbs
are the kit's own proof gates, by name. Anything else is 404. The Worker in front
adds bearer-token auth; this shim adds the closed verb set (defense in depth).

  GET  /            -> {ok, service, versions}
  POST /run/<job>   -> start one of: smoketest | selfcheck   (409 if one is running)
  GET  /status      -> {job, running, rc, seconds, tail}

Stdlib only. Jobs run in a thread; output tees to /tmp/job.out (tail served).
"""
from __future__ import annotations
import json, subprocess, sys, threading, time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

JOBS = {
    "smoketest": [sys.executable, "_tools/engine_smoketest.py"],
    "selfcheck": [sys.executable, "_tools/selfcheck.py"],
}
STATE = {"job": None, "running": False, "rc": None, "started": None}
LOCK = threading.Lock()
OUT = "/tmp/job.out"


def _run(job: str) -> None:
    with open(OUT, "wb") as f:
        p = subprocess.Popen(JOBS[job], stdout=f, stderr=subprocess.STDOUT, cwd="/kit")
        rc = p.wait()
    with LOCK:
        STATE.update(running=False, rc=rc)


class H(BaseHTTPRequestHandler):
    def _json(self, code: int, obj: dict) -> None:
        body = json.dumps(obj).encode("utf-8")
        self.send_response(code)
        self.send_header("content-type", "application/json")
        self.send_header("content-length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *a):  # quiet
        pass

    def do_GET(self):
        if self.path == "/":
            self._json(200, {"ok": True, "service": "booksmith-p0",
                             "python": sys.version.split()[0]})
        elif self.path == "/status":
            with LOCK:
                st = dict(STATE)
            tail = ""
            try:
                with open(OUT, "rb") as f:
                    f.seek(0, 2)
                    f.seek(max(0, f.tell() - 4000))
                    tail = f.read().decode("utf-8", "replace")
            except OSError:
                pass
            st["seconds"] = round(time.time() - st["started"], 1) if st["started"] else None
            st["tail"] = tail
            self._json(200, st)
        else:
            self._json(404, {"error": "not found"})

    def do_POST(self):
        if not self.path.startswith("/run/"):
            return self._json(404, {"error": "not found"})
        job = self.path[len("/run/"):]
        if job not in JOBS:
            return self._json(404, {"error": f"unknown job; allowed: {sorted(JOBS)}"})
        with LOCK:
            if STATE["running"]:
                return self._json(409, {"error": "a job is already running", "job": STATE["job"]})
            STATE.update(job=job, running=True, rc=None, started=time.time())
        threading.Thread(target=_run, args=(job,), daemon=True).start()
        self._json(202, {"started": job})


if __name__ == "__main__":
    ThreadingHTTPServer(("0.0.0.0", 8080), H).serve_forever()
