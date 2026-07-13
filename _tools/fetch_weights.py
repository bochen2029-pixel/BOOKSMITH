#!/usr/bin/env python3
r"""
fetch_weights.py — vendored, resumable model/weight downloader for BOOKSMITH.

"Downloads solved once and forever," in-kit. Pure stdlib (urllib) so it ships on
a USB stick and runs on any machine with Python — no personal downloader, no
extra pip installs.

WHAT IT DOES
  * General file fetch:
      python fetch_weights.py --url URL --dest PATH [--sha256 HEX]
                              [--expected-size BYTES]
  * SDXL profile (reads kit_env, targets the checkpoint):
      python fetch_weights.py sdxl [--kit-env PATH]
        -> downloads cover_gen.default_checkpoint_url into
           cover_gen.checkpoints_dir / cover_gen.default_checkpoint

RESUMABLE + SAFE
  * Streams to <dest>.part; sends an HTTP Range header to resume an interrupted
    .part (never re-downloads completed bytes).
  * If the server ignores Range and replies 200 (not 206), the .part is
    truncated and restarted cleanly rather than corrupted.
  * Atomic os.replace(<dest>.part -> <dest>) ONLY after the full body is in and
    (when provided) size + sha256 verify. Never leaves a partial file at the
    final name.
  * Retries with exponential backoff (default 5). Honors redirects. Sends a
    normal User-Agent (some CDNs 403 the default urllib agent).
  * Throttled progress line to stderr (~1/sec): received/total, %, MB/s, ETA.

EXIT CODES
  0  done, or already present and verified
  1  failed after retries (network / hash / size mismatch)
  2  usage error (bad args, empty checkpoints_dir, missing kit_env, ...)
"""

from __future__ import annotations

import argparse
import hashlib
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "booksmith-fetch-weights/1.0 (+stdlib urllib)"
)
CHUNK = 1 << 20  # 1 MiB read blocks
DEFAULT_RETRIES = 5
DEFAULT_TIMEOUT = 60  # seconds, per-connection


# ============================================================
# formatting helpers
# ============================================================
def _human(n: float) -> str:
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if abs(n) < 1024.0:
            return f"{n:,.1f}{unit}"
        n /= 1024.0
    return f"{n:,.1f}PB"


def _fmt_eta(seconds: float) -> str:
    if seconds < 0 or seconds != seconds:  # negative or NaN
        return "?"
    seconds = int(seconds)
    h, rem = divmod(seconds, 3600)
    m, s = divmod(rem, 60)
    if h:
        return f"{h}h{m:02d}m{s:02d}s"
    if m:
        return f"{m}m{s:02d}s"
    return f"{s}s"


class Progress:
    """Throttled stderr progress (~1 update/sec)."""

    def __init__(self, total: int | None, already: int = 0):
        self.total = total if (total and total > 0) else None
        self.start_bytes = already
        self.received = already
        self.t0 = time.time()
        self.last_emit = 0.0

    def update(self, nbytes: int, *, force: bool = False) -> None:
        self.received += nbytes
        now = time.time()
        if not force and (now - self.last_emit) < 1.0:
            return
        self.last_emit = now
        elapsed = max(1e-6, now - self.t0)
        rate = (self.received - self.start_bytes) / elapsed  # bytes/sec this session
        if self.total:
            pct = 100.0 * self.received / self.total
            remaining = self.total - self.received
            eta = remaining / rate if rate > 0 else -1
            line = (f"\r  {_human(self.received)}/{_human(self.total)} "
                    f"({pct:5.1f}%)  {_human(rate)}/s  ETA {_fmt_eta(eta)}   ")
        else:
            line = (f"\r  {_human(self.received)}  {_human(rate)}/s   ")
        sys.stderr.write(line)
        sys.stderr.flush()

    def done(self) -> None:
        self.update(0, force=True)
        sys.stderr.write("\n")
        sys.stderr.flush()


# ============================================================
# core download
# ============================================================
def _open(url: str, *, offset: int, timeout: int):
    """Open url, optionally with a Range header. Returns the response object.

    Redirects are followed by urllib's default opener. Range requests yield 206
    (partial) when honored, or 200 (full) when ignored.
    """
    headers = {"User-Agent": USER_AGENT, "Accept": "*/*"}
    if offset > 0:
        headers["Range"] = f"bytes={offset}-"
    req = urllib.request.Request(url, headers=headers)
    return urllib.request.urlopen(req, timeout=timeout)


def _content_length(resp, *, resuming: bool, offset: int) -> int | None:
    """Total file size in bytes if derivable, else None.

    For a 206, Content-Length is the REMAINDER; total = offset + remainder
    (or parsed from Content-Range). For a 200, Content-Length is the total.
    """
    cr = resp.headers.get("Content-Range")
    if cr and "/" in cr:
        tail = cr.rsplit("/", 1)[-1].strip()
        if tail.isdigit():
            return int(tail)
    cl = resp.headers.get("Content-Length")
    if cl and cl.isdigit():
        remainder = int(cl)
        return offset + remainder if (resuming and resp.status == 206) else remainder
    return None


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(CHUNK), b""):
            h.update(block)
    return h.hexdigest()


def _attempt(url: str, part: Path, *, timeout: int) -> tuple[bool, int | None]:
    """One download attempt into `part` (resuming if it exists).

    Returns (completed, total_size). `completed` True iff the body was fully
    read and matches the known total (or the connection closed cleanly with no
    known total). Raises on transport errors (caller retries).
    """
    offset = part.stat().st_size if part.exists() else 0
    resuming = offset > 0

    resp = _open(url, offset=offset, timeout=timeout)
    with resp:
        status = resp.status
        # Server ignored Range -> restart cleanly to avoid concatenating a
        # full body onto existing partial bytes.
        if resuming and status == 200:
            sys.stderr.write(
                "  (server ignored Range; restarting download from 0)\n")
            part.unlink()
            offset = 0
            resuming = False

        total = _content_length(resp, resuming=resuming, offset=offset)

        # Already complete? (rare: .part equals full size and server 416/200)
        if total is not None and offset >= total and status in (200, 206, 416):
            return True, total

        mode = "ab" if resuming else "wb"
        prog = Progress(total, already=offset)
        with part.open(mode) as f:
            while True:
                chunk = resp.read(CHUNK)
                if not chunk:
                    break
                f.write(chunk)
                prog.update(len(chunk))
        prog.done()

    got = part.stat().st_size
    if total is not None:
        return got >= total, total
    # No total advertised: a clean EOF is our only completion signal.
    return True, None


def download(url: str, dest: Path, *, sha256: str | None = None,
             expected_size: int | None = None, retries: int = DEFAULT_RETRIES,
             timeout: int = DEFAULT_TIMEOUT) -> int:
    """Resumable download of `url` -> `dest`. Returns an exit code (0/1)."""
    dest = dest.expanduser()
    part = dest.with_name(dest.name + ".part")

    # ---- already present + verified? ----
    if dest.exists():
        if _verify(dest, sha256, expected_size, label="existing file"):
            print(f"[fetch-weights] already present and verified: {dest}")
            return 0
        sys.stderr.write(
            f"[fetch-weights] existing {dest.name} failed verification; "
            "re-downloading\n")
        try:
            dest.unlink()
        except OSError:
            pass

    dest.parent.mkdir(parents=True, exist_ok=True)

    # ---- disk-space preflight: a ~6.5GB pull onto a full disk must fail in
    # one actionable line, not as a raw OSError minutes into the stream ----
    if expected_size:
        import shutil as _sh
        try:
            free = _sh.disk_usage(str(dest.parent)).free
        except OSError:
            free = None
        have = part.stat().st_size if part.exists() else 0
        need = int(expected_size * 1.02) - have + (64 << 20)
        if free is not None and need > 0 and free < need:
            sys.stderr.write(
                f"[fetch-weights] INSUFFICIENT DISK SPACE: ~{_human(need)} more "
                f"needed for {dest.name}, only {_human(free)} free on "
                f"{dest.parent}\n")
            return 1

    last_err: str | None = None
    for attempt in range(1, retries + 1):
        have = part.stat().st_size if part.exists() else 0
        sys.stderr.write(
            f"[fetch-weights] attempt {attempt}/{retries}: {url}\n"
            f"  -> {dest}"
            + (f"  (resuming from {_human(have)})\n" if have else "\n"))
        try:
            completed, total = _attempt(url, part, timeout=timeout)
        except (urllib.error.HTTPError, urllib.error.URLError, OSError,
                TimeoutError) as e:
            last_err = f"{type(e).__name__}: {e}"
            # Range-not-satisfiable can mean the .part is already whole.
            if isinstance(e, urllib.error.HTTPError) and e.code == 416 and part.exists():
                completed, total = True, part.stat().st_size
            else:
                sys.stderr.write(f"  ! {last_err}\n")
                if attempt < retries:
                    delay = min(60.0, 2.0 ** attempt)
                    sys.stderr.write(f"  retrying in {delay:.0f}s...\n")
                    time.sleep(delay)
                continue

        if not completed:
            # Partial write; loop will resume from the enlarged .part.
            last_err = "connection closed before full body received"
            sys.stderr.write(f"  ! {last_err} (will resume)\n")
            if attempt < retries:
                delay = min(60.0, 2.0 ** attempt)
                time.sleep(delay)
            continue

        # ---- verify size/hash on the .part BEFORE the atomic rename ----
        eff_size = expected_size if expected_size is not None else total
        if not _verify(part, sha256, eff_size, label="downloaded file"):
            last_err = "verification failed after download"
            try:
                part.unlink()
            except OSError:
                pass
            if attempt < retries:
                sys.stderr.write("  re-downloading from scratch...\n")
            continue

        # ---- atomic promotion ----
        os.replace(part, dest)
        print(f"[fetch-weights] done: {dest} ({_human(dest.stat().st_size)})")
        return 0

    sys.stderr.write(f"[fetch-weights] FAILED after {retries} attempts: {last_err}\n")
    return 1


def _verify(path: Path, sha256: str | None, expected_size: int | None,
            *, label: str) -> bool:
    """Check size then hash when provided. No checks provided => trusts EOF."""
    if expected_size is not None:
        actual = path.stat().st_size
        if actual != expected_size:
            sys.stderr.write(
                f"  size mismatch on {label}: got {actual:,}, "
                f"expected {expected_size:,}\n")
            return False
    if sha256:
        sys.stderr.write(f"  verifying sha256 of {label}...\n")
        actual = _sha256_file(path)
        if actual.lower() != sha256.lower():
            sys.stderr.write(
                f"  sha256 mismatch on {label}:\n    got      {actual}\n"
                f"    expected {sha256.lower()}\n")
            return False
        sys.stderr.write("  sha256 OK\n")
    return True


# ============================================================
# sdxl profile (kit_env driven)
# ============================================================
def _load_kit_env(path: str | None) -> tuple[dict, Path]:
    p = Path(path).expanduser() if path else (Path(__file__).resolve().parent / "kit_env.json")
    if not p.exists():
        raise FileNotFoundError(
            f"kit_env.json not found: {p} — copy kit_env.template.json to "
            "kit_env.json and fill cover_gen.checkpoints_dir")
    import json
    return json.loads(p.read_text(encoding="utf-8")), p


# Integrity constants for the well-known SDXL-base checkpoint (read from the
# HuggingFace tree API for stabilityai/stable-diffusion-xl-base-1.0, 2026-07-13).
# kit_env cover_gen.default_checkpoint_sha256/_size override; CLI flags win.
SDXL_BASE_SHA256 = "31e35c80fc4829d14f90153f4c74cd59c90b779f6afe05a74cd6120b893f7e5b"
SDXL_BASE_SIZE = 6938078334


def do_sdxl(args) -> int:
    try:
        env, env_path = _load_kit_env(args.kit_env)
    except FileNotFoundError as e:
        sys.stderr.write(f"[fetch-weights] {e}\n")
        return 2

    cg = env.get("cover_gen") or {}
    url = args.url or cg.get("default_checkpoint_url")
    ckpt_dir = (cg.get("checkpoints_dir") or "").strip()
    ckpt_name = cg.get("default_checkpoint") or "sd_xl_base_1.0.safetensors"
    # a 6.5GB artifact promoted on size-match alone is an integrity hole: default
    # the hash for the known checkpoint so verification is on unless overridden
    sha = (args.sha256 or cg.get("default_checkpoint_sha256")
           or (SDXL_BASE_SHA256 if ckpt_name == "sd_xl_base_1.0.safetensors" else None))
    size = (args.expected_size or cg.get("default_checkpoint_size")
            or (SDXL_BASE_SIZE if ckpt_name == "sd_xl_base_1.0.safetensors" else None))

    if not url:
        sys.stderr.write(
            "[fetch-weights] cover_gen.default_checkpoint_url is not set in "
            f"{env_path}. Add the checkpoint URL or pass --url.\n")
        return 2
    if not ckpt_dir:
        sys.stderr.write(
            "[fetch-weights] cover_gen.checkpoints_dir is empty in "
            f"{env_path}.\n  Set it to your ComfyUI checkpoints folder, e.g.\n"
            "    \"checkpoints_dir\": \"C:\\\\Users\\\\you\\\\Documents\\\\ComfyUI\\\\models\\\\checkpoints\"\n"
            "  then re-run: python _tools/fetch_weights.py sdxl\n")
        return 2

    dest = Path(ckpt_dir).expanduser() / ckpt_name
    sys.stderr.write(
        f"[fetch-weights] SDXL profile:\n  url : {url}\n  dest: {dest}\n"
        f"  sha256: {sha or '(none — verification off)'}\n"
        "  (~6.5 GB; resumable — safe to Ctrl+C and re-run)\n")
    return download(url, dest, sha256=sha,
                    expected_size=size,
                    retries=args.retries, timeout=args.timeout)


# ============================================================
# CLI
# ============================================================
def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Resumable, stdlib-only weight/file downloader for BOOKSMITH.",
    )
    sub = p.add_subparsers(dest="profile")

    # shared knobs (attached to both root and the sdxl subcommand)
    def add_common(sp):
        sp.add_argument("--sha256", default=None, help="Expected SHA-256 (hex) to verify.")
        sp.add_argument("--expected-size", type=int, default=None,
                        help="Expected byte size to verify.")
        sp.add_argument("--retries", type=int, default=DEFAULT_RETRIES,
                        help=f"Retry attempts (default {DEFAULT_RETRIES}).")
        sp.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT,
                        help=f"Per-connection timeout seconds (default {DEFAULT_TIMEOUT}).")

    # general mode (root)
    p.add_argument("--url", default=None, help="Source URL (general mode).")
    p.add_argument("--dest", default=None, help="Destination path (general mode).")
    add_common(p)

    # sdxl profile
    sp = sub.add_parser("sdxl", help="Fetch the SDXL checkpoint named in kit_env.")
    sp.add_argument("--kit-env", default=None, help="kit_env.json path.")
    sp.add_argument("--url", default=None, help="Override the checkpoint URL.")
    add_common(sp)

    return p


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)

    if args.profile == "sdxl":
        return do_sdxl(args)

    # general mode
    if not args.url or not args.dest:
        sys.stderr.write(
            "usage: fetch_weights.py --url URL --dest PATH "
            "[--sha256 HEX] [--expected-size BYTES]\n"
            "   or: fetch_weights.py sdxl [--kit-env PATH]\n")
        return 2
    return download(
        args.url, Path(args.dest), sha256=args.sha256,
        expected_size=args.expected_size, retries=args.retries, timeout=args.timeout)


if __name__ == "__main__":
    sys.exit(main())
