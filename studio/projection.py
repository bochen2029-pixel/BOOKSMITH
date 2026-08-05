#!/usr/bin/env python3
r"""
projection.py — BOOKSMITH Studio's READ-ONLY projection layer (S0).

Doctrine (docs/STUDIO_SPEC.md §2): the Studio server has exactly two primitives,
SPAWN and PROJECT. This module is PROJECT: every function reads files the kit
already writes and returns JSON-able dicts. Nothing here writes book state, ever
(the one exception is the engine's own `_engine/` mkdir inside Engine.__init__
when we shell `--explain`; that is pre-existing engine behavior, not ours).

Staleness truth comes from `engine.py --explain` (E-1) via subprocess — the hash
logic lives in the engine ONLY and is never reimplemented here (§6.4).

Every reader is torn-file-tolerant: a half-written JSON or a missing file
degrades to a field-level error string, never a crash — the projection of a
live workspace must survive the engine writing under it.
"""
from __future__ import annotations

import difflib
import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

KIT = Path(__file__).resolve().parents[1]
WS_ROOT = KIT / "book_workspace"
TOOLS = KIT / "_tools"

_SLUG_RE = re.compile(r"^[A-Za-z0-9._\-]+$")

# S0 file-serving jail: workspace-relative roots a browser may fetch from.
# canon_refs/ and intake/ are deliberately EXCLUDED (private source material).
_SERVE_ROOTS = {"outputs", "cover_art", "manuscript", "images"}


# ---------------------------------------------------------------------------
# small helpers (mirror the engine's idioms)
# ---------------------------------------------------------------------------
def _iso(ts: float) -> str:
    return datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read_text(p: Path, cap: int | None = None) -> str | None:
    try:
        t = p.read_text(encoding="utf-8", errors="replace")
        return t[:cap] if cap else t
    except OSError:
        return None


def _read_json(p: Path):
    try:
        return json.loads(p.read_text(encoding="utf-8", errors="replace"))
    except Exception:
        return None


def _wc(text: str | None) -> int:
    return len(text.split()) if text else 0


def _run(cmd: list[str], timeout: int = 180) -> tuple[int, str, str]:
    """Subprocess with the standing UTF-8 rule (a CJK glyph in any tool's output
    must never cp1252-crash a projection)."""
    env = dict(os.environ)
    env["PYTHONUTF8"] = "1"
    env["PYTHONIOENCODING"] = "utf-8"
    try:
        r = subprocess.run(cmd, cwd=str(KIT), capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=timeout, env=env)
        return r.returncode, r.stdout, r.stderr
    except subprocess.TimeoutExpired:
        return 124, "", f"timeout after {timeout}s"
    except OSError as e:
        return 126, "", str(e)


def resolve_slug(slug: str) -> Path:
    """Validate a slug names a real workspace; the FIRST gate on every route."""
    if not _SLUG_RE.match(slug or ""):
        raise ValueError(f"invalid slug: {slug!r}")
    ws = WS_ROOT / slug
    if not (ws / "book_config.json").is_file():
        raise ValueError(f"no such workspace: {slug}")
    return ws


def safe_ws_file(slug: str, rel: str) -> Path:
    """Path-jailed file resolution (SPEC §3.4): workspace-relative, realpath-
    checked, and restricted to the serve roots. Raises ValueError on any escape."""
    ws = resolve_slug(slug).resolve()
    if not rel or rel.startswith(("/", "\\")) or ":" in rel:
        raise ValueError("path must be workspace-relative")
    p = (ws / rel).resolve()
    try:
        parts = p.relative_to(ws).parts
    except ValueError:
        raise ValueError("path escapes the workspace")
    if not parts or parts[0] not in _SERVE_ROOTS:
        raise ValueError(f"path root not servable (allowed: {sorted(_SERVE_ROOTS)})")
    if not p.is_file():
        raise ValueError("no such file")
    return p


# ---------------------------------------------------------------------------
# books
# ---------------------------------------------------------------------------
def _state_summary(ws: Path) -> dict:
    sp = ws / "_engine" / "state.json"
    if not sp.is_file():
        return {"engine_ran": False}
    st = _read_json(sp)
    if not isinstance(st, dict):
        return {"engine_ran": True, "error": "state.json unreadable"}
    counts: dict[str, int] = {}
    for rec in (st.get("stages") or {}).values():
        s = rec.get("status", "?")
        counts[s] = counts.get(s, 0) + 1
    return {"engine_ran": True, "counts": counts, "updated": st.get("updated"),
            "config_sha": st.get("config_sha")}


def _units_of(cfg: dict, ws: Path) -> list[dict]:
    """Mirror Engine.units(): config units, else fall back to manuscript files."""
    us = cfg.get("units")
    if us:
        return us
    cur = sorted((ws / "manuscript" / "current").glob("*_current.md"))
    return [{"id": p.stem.replace("_current", ""), "title": "", "class": "C"} for p in cur]


def list_books() -> list[dict]:
    out = []
    if not WS_ROOT.is_dir():
        return out
    for d in sorted(WS_ROOT.iterdir()):
        cfgp = d / "book_config.json"
        if not d.is_dir() or not cfgp.is_file() or d.name.startswith("_trash"):
            continue
        cfg = _read_json(cfgp) or {}
        state = _state_summary(d)
        mtimes = [cfgp.stat().st_mtime]
        sp = d / "_engine" / "state.json"
        if sp.is_file():
            mtimes.append(sp.stat().st_mtime)
        # Composited ebook cover, when it exists — the shelf renders it via the
        # jailed /file route (outputs/ is a serve root). Cheap existence check.
        cover_rel = f"outputs/kindle/{d.name}_KINDLE_cover.jpg"
        if not (d / cover_rel).is_file():
            cover_rel = None
        out.append({
            "slug": d.name,
            "title": cfg.get("title") or d.name,
            "subtitle": cfg.get("subtitle") or "",
            "cover_rel": cover_rel,
            "author": cfg.get("author") or "",
            "domain": cfg.get("domain", "book"),
            "is_fiction": bool(cfg.get("is_fiction")),
            "formats": cfg.get("formats") or [],
            "units": len(_units_of(cfg, d)),
            "state": state,
            "hardstop": (d / "_engine" / "HARDSTOP.json").is_file(),
            "bridge_pending": any((d / "_engine" / "bridge").glob("*.request.json"))
            if (d / "_engine" / "bridge").is_dir() else False,
            "updated": _iso(max(mtimes)),
        })
    out.sort(key=lambda b: b["updated"], reverse=True)
    return out


def binding_of(cfg: dict) -> dict:
    """S5: the Shell learns a domain entirely from DATA (SPEC §10) — nouns and
    no_cover from domains/<d>/domain.json, presentation extras from the
    optional domains/<d>/studio.json (panels, artifact labels, op subset).
    The book domain is the built-in default. No domain name is ever
    special-cased in Shell code; studio/selfcheck.py holds that falsifier."""
    d = str(cfg.get("domain") or "book").strip() or "book"
    out = {"domain": d, "unit_noun": None, "no_cover": False, "bible_label": None,
           "panels": {"formats_matrix": True, "cover_studio": True},
           "artifact_labels": {}, "ops_enabled": None}
    if d == "book":
        return out
    spec = _read_json(KIT / "domains" / d / "domain.json") or {}
    out["unit_noun"] = spec.get("unit_noun")
    out["no_cover"] = bool(spec.get("no_cover"))
    out["bible_label"] = spec.get("bible_label")
    st = _read_json(KIT / "domains" / d / "studio.json") or {}
    panels = st.get("panels") or {}
    # non-book default: book-only panels OFF unless the sidecar turns one on
    out["panels"] = {"formats_matrix": bool(panels.get("formats_matrix", False)),
                     "cover_studio": bool(panels.get("cover_studio", False))}
    if isinstance(st.get("artifact_labels"), dict):
        out["artifact_labels"] = {str(k): str(v) for k, v in st["artifact_labels"].items()}
    if isinstance(st.get("ops_enabled"), list):
        out["ops_enabled"] = [str(x) for x in st["ops_enabled"]]
    return out


def book_detail(slug: str) -> dict:
    ws = resolve_slug(slug)
    cfg = _read_json(ws / "book_config.json") or {}
    voice = cfg.get("voice") or {}
    authorship = cfg.get("authorship") or {}
    binding = binding_of(cfg)
    return {
        "slug": slug,
        "title": cfg.get("title") or slug,
        "subtitle": cfg.get("subtitle") or "",
        "author": cfg.get("author") or "",
        "genre": cfg.get("genre") or "",
        "domain": cfg.get("domain", "book"),
        "binding": binding,
        "is_fiction": bool(cfg.get("is_fiction")),
        "formats": cfg.get("formats") or [],
        "unit_noun": binding.get("unit_noun") or voice.get("unit_noun") or "chapter",
        "no_em_dashes": voice.get("no_em_dashes"),
        "blacklist_n": len(voice.get("blacklist") or []),
        "authorship_default": authorship.get("default_class", "C"),
        "state": _state_summary(ws),
        "state_raw": _read_json(ws / "_engine" / "state.json"),
        "hardstop": _read_json(ws / "_engine" / "HARDSTOP.json"),
        "has_brief": (ws / "brief.md").is_file(),
        "has_seed": (ws / "seed.md").is_file(),
        "intake_files": sorted(p.name for p in (ws / "intake").iterdir()
                               if p.is_file()) if (ws / "intake").is_dir() else [],
    }


# ---------------------------------------------------------------------------
# plan (the staleness oracle) — engine.py --explain, short-TTL cached
# ---------------------------------------------------------------------------
_plan_cache: dict[str, tuple[float, dict]] = {}
_PLAN_TTL = 10.0


def plan(slug: str, refresh: bool = False) -> dict:
    ws = resolve_slug(slug)
    now = time.time()
    hit = _plan_cache.get(slug)
    if hit and not refresh and now - hit[0] < _PLAN_TTL:
        return hit[1]
    rc, out, err = _run([sys.executable, str(TOOLS / "engine.py"),
                         "--config", str(ws / "book_config.json"), "--explain"],
                        timeout=180)
    if rc != 0:
        data = {"error": f"engine --explain exit {rc}: {(out + err).strip()[-400:]}"}
    else:
        try:
            data = json.loads(out)
        except Exception:
            data = {"error": f"unparseable --explain output: {out.strip()[:200]}"}
    _plan_cache[slug] = (now, data)
    return data


# ---------------------------------------------------------------------------
# units
# ---------------------------------------------------------------------------
def _versions_of(ws: Path, uid: str) -> list[dict]:
    drafts = ws / "manuscript" / "drafts"
    if not drafts.is_dir():
        return []
    items = []
    for p in drafts.glob(f"{uid}_v*.md"):
        m = re.fullmatch(rf"{re.escape(uid)}_v(\d+)\.md", p.name)
        if m:
            items.append({"v": int(m.group(1)), "name": p.name,
                          "mtime": _iso(p.stat().st_mtime)})
    items.sort(key=lambda x: x["v"])
    return items


def units(slug: str) -> list[dict]:
    ws = resolve_slug(slug)
    cfg = _read_json(ws / "book_config.json") or {}
    st = _read_json(ws / "_engine" / "state.json") or {}
    stages = st.get("stages") or {}
    default_class = (cfg.get("authorship") or {}).get("default_class", "C")
    out = []
    for u in _units_of(cfg, ws):
        uid = u.get("id", "?")
        curp = ws / "manuscript" / "current" / f"{uid}_current.md"
        cur = _read_text(curp)
        notesp = ws / "revision_notes" / f"{uid}.md"
        out.append({
            "id": uid,
            "title": u.get("title") or "",
            "class": str(u.get("class") or default_class or "C").upper(),
            "target_words": u.get("target_words"),
            "current_words": _wc(cur),
            "current_mtime": _iso(curp.stat().st_mtime) if curp.is_file() else None,
            "versions": _versions_of(ws, uid),
            "gate": stages.get(f"draft:{uid}"),
            "has_revision_notes": notesp.is_file(),
        })
    return out


def unit_detail(slug: str, uid: str) -> dict:
    ws = resolve_slug(slug)
    if not _SLUG_RE.match(uid or ""):
        raise ValueError(f"invalid unit id: {uid!r}")
    curp = ws / "manuscript" / "current" / f"{uid}_current.md"
    cur = _read_text(curp)
    versions = _versions_of(ws, uid)
    for v in versions:
        v["words"] = _wc(_read_text(ws / "manuscript" / "drafts" / v["name"]))
    return {
        "id": uid,
        "current": cur,
        "current_words": _wc(cur),
        "contract": _read_text(ws / "contracts" / f"{uid}.md"),
        "revision_notes": _read_text(ws / "revision_notes" / f"{uid}.md"),
        "versions": versions,
    }


def _version_path(ws: Path, uid: str, ref: str) -> Path:
    if ref == "current":
        return ws / "manuscript" / "current" / f"{uid}_current.md"
    m = re.fullmatch(r"v(\d+)", ref or "")
    if not m:
        raise ValueError(f"bad version ref: {ref!r} (use 'current' or 'vN')")
    return ws / "manuscript" / "drafts" / f"{uid}_v{m.group(1)}.md"


def unit_diff(slug: str, uid: str, a: str, b: str) -> dict:
    ws = resolve_slug(slug)
    if not _SLUG_RE.match(uid or ""):
        raise ValueError(f"invalid unit id: {uid!r}")
    pa, pb = _version_path(ws, uid, a), _version_path(ws, uid, b)
    ta, tb = _read_text(pa), _read_text(pb)
    if ta is None or tb is None:
        raise ValueError("one side of the diff does not exist")
    lines = []
    for ln in difflib.unified_diff(ta.splitlines(), tb.splitlines(),
                                   fromfile=a, tofile=b, lineterm="", n=3):
        t = ("hdr" if ln.startswith(("---", "+++", "@@"))
             else "add" if ln.startswith("+")
             else "del" if ln.startswith("-") else "ctx")
        lines.append({"t": t, "s": ln})
    return {"a": a, "b": b, "a_words": _wc(ta), "b_words": _wc(tb), "lines": lines}


# ---------------------------------------------------------------------------
# artifacts / spend / bridge / log
# ---------------------------------------------------------------------------
def artifacts(slug: str) -> dict:
    ws = resolve_slug(slug)
    root = ws / "outputs"
    entries, total, truncated = [], 0, False
    if root.is_dir():
        for p in sorted(root.rglob("*")):
            if not p.is_file():
                continue
            if len(entries) >= 800:
                truncated = True
                break
            st = p.stat()
            total += st.st_size
            entries.append({"rel": str(Path("outputs") / p.relative_to(root)).replace("\\", "/"),
                            "size": st.st_size, "mtime": _iso(st.st_mtime)})
    return {"entries": entries, "total_bytes": total, "truncated": truncated,
            "manifest": _read_json(root / "MANIFEST.json")}


def spend(slug: str) -> dict:
    """Model-call rollup across BOTH lanes: the engine's prose calls and the
    Studio chat's compile calls. E-4 usage fields (real token counts) are used
    when present; otherwise chars/4 keeps the meter honest with an '≈'."""
    ws = resolve_slug(slug)
    n = chars_in = chars_out = errors = 0
    tok_in = tok_out = 0
    measured = 0
    seconds = 0.0
    lanes = {"engine": ws / "_engine" / "calls",
             "chat": ws / "_studio" / "chat" / "calls"}
    per_lane = {}
    for lane, d in lanes.items():
        c = 0
        if d.is_dir():
            for p in sorted(d.glob("call_*.json")):
                rec = _read_json(p) or {}
                n += 1
                c += 1
                chars_in += int(rec.get("prompt_chars") or 0)
                chars_out += int(rec.get("out_chars") or 0)
                seconds += float(rec.get("seconds") or 0)
                errors += 1 if rec.get("error") else 0
                if rec.get("in_tokens") or rec.get("out_tokens"):
                    tok_in += int(rec.get("in_tokens") or 0)
                    tok_out += int(rec.get("out_tokens") or 0)
                    measured += 1
        per_lane[lane] = c
    est = (chars_in + chars_out) // 4
    return {"calls": n, "by_lane": per_lane, "prompt_chars": chars_in,
            "out_chars": chars_out, "seconds": round(seconds, 1), "errors": errors,
            "est_tokens": est, "measured_calls": measured,
            "in_tokens": tok_in, "out_tokens": tok_out,
            "tokens": (tok_in + tok_out) if measured == n and n else est,
            "exact": bool(n) and measured == n}


def bridge(slug: str) -> dict:
    ws = resolve_slug(slug)
    bdir = ws / "_engine" / "bridge"
    reqs = []
    if bdir.is_dir():
        for p in sorted(bdir.glob("*.request.json")):
            rec = _read_json(p) or {}
            uid = rec.get("unit") or p.name.split(".")[0]
            att = _read_text(bdir / f"{uid}.attempts", cap=200)
            reqs.append({
                "unit": uid, "title": rec.get("title"),
                "attempt": rec.get("attempt"), "nonce": rec.get("nonce"),
                "gates": rec.get("must_pass_gates"),
                "attempts_file": att,
                "response_present": (bdir / f"{uid}.response.md").is_file(),
            })
    return {"requests": reqs,
            "next_md": _read_text(ws / "_engine" / "NEXT.md", cap=2000)}


def log_tail(slug: str, n: int = 120) -> list[dict]:
    ws = resolve_slug(slug)
    p = ws / "_engine" / "log.jsonl"
    if not p.is_file():
        return []
    try:
        raw = p.read_bytes()[-131072:].decode("utf-8", "replace")
    except OSError:
        return []
    out = []
    for line in raw.splitlines():
        try:
            rec = json.loads(line)
            if isinstance(rec, dict):
                out.append(rec)
        except Exception:
            continue
    return out[-n:]


# ---------------------------------------------------------------------------
# cover studio (S4) — the engine's OWN reuse predicate, never a copy of it
# ---------------------------------------------------------------------------
_engine_mod = None


def _engine():
    """Import _tools/engine.py as a module so the Studio can call the kit's own
    `_may_reuse_art` predicate (proven by --selftest-cover-reuse) instead of
    reimplementing provenance rules that would then drift."""
    global _engine_mod
    if _engine_mod is None:
        import importlib.util
        spec = importlib.util.spec_from_file_location("_bs_engine", TOOLS / "engine.py")
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        _engine_mod = mod
    return _engine_mod


def cover(slug: str) -> dict:
    ws = resolve_slug(slug)
    cfg = _read_json(ws / "book_config.json") or {}
    art = ws / "cover_art" / f"{slug}_src.png"
    method = (((cfg.get("cover") or {}).get("art") or {}).get("method") or "").strip().lower()
    reuse, why = (False, "engine predicate unavailable")
    try:
        reuse, why = _engine()._may_reuse_art(art, cfg, force=False)
    except Exception as e:                                        # noqa: BLE001
        why = f"reuse predicate error: {e}"
    sidecar = _read_json(art.with_name(art.stem + ".provenance.json"))
    superseded = []
    cdir = ws / "cover_art"
    if cdir.is_dir():
        superseded = sorted(p.name for p in cdir.glob("*_superseded_*"))
    ebook = ws / "outputs" / "kindle" / f"{slug}_KINDLE_cover.jpg"
    verdict = _read_json(ebook.with_suffix(".verdict.json"))
    st = (_read_json(ws / "_engine" / "state.json") or {}).get("stages", {}).get("cover")
    events = [e for e in log_tail(slug, n=400) if str(e.get("event", "")).startswith("cover")]
    wraps = []
    outs = ws / "outputs"
    if outs.is_dir():
        for p in sorted(outs.rglob("*")):
            n = p.name.lower()
            if p.is_file() and ("cover" in n or n.startswith(("front_", "back_", "spine"))) \
                    and p.suffix.lower() in {".pdf", ".jpg", ".jpeg", ".png"}:
                wraps.append({"rel": str(Path("outputs") / p.relative_to(outs)).replace("\\", "/"),
                              "size": p.stat().st_size, "mtime": _iso(p.stat().st_mtime)})
    return {
        "art": {"rel": f"cover_art/{slug}_src.png", "exists": art.is_file(),
                "size": art.stat().st_size if art.is_file() else 0,
                "mtime": _iso(art.stat().st_mtime) if art.is_file() else None},
        "method": method or "(generative / undeclared)",
        "reuse": {"may_reuse": bool(reuse), "reason": why},
        "provenance": sidecar, "superseded": superseded,
        "ebook_cover": {"rel": f"outputs/kindle/{slug}_KINDLE_cover.jpg",
                        "exists": ebook.is_file(),
                        "mtime": _iso(ebook.stat().st_mtime) if ebook.is_file() else None},
        "vision_verdict": verdict, "stage_state": st, "events": events[-12:],
        "wraps": wraps,
        "reroll_budget": int(((cfg.get("cover") or {}).get("art") or {}).get("reroll_budget", 6)),
        "formats": cfg.get("formats") or [],
    }


# ---------------------------------------------------------------------------
# S10: one archived version's text (the take-picker reads competing takes)
# ---------------------------------------------------------------------------
def unit_version_text(slug: str, uid: str, ref: str) -> dict:
    ws = resolve_slug(slug)
    if not re.fullmatch(r"[A-Za-z0-9._\-]+", uid or ""):
        raise ValueError(f"bad unit id {uid!r}")
    if ref == "current":
        p = ws / "manuscript" / "current" / f"{uid}_current.md"
    elif re.fullmatch(r"v\d+", ref or ""):
        p = ws / "manuscript" / "drafts" / f"{uid}_{ref}.md"
    else:
        raise ValueError(f"ref must be 'current' or 'vN', got {ref!r}")
    if not p.is_file():
        raise ValueError(f"no such take: {p.name}")
    text = _read_text(p) or ""
    return {"uid": uid, "ref": ref, "words": len(text.split()), "text": text}


# ---------------------------------------------------------------------------
# S10: the book passport — a self-contained, shareable receipts page
# ---------------------------------------------------------------------------
def passport_html(slug: str) -> str:
    """One HTML file, no external assets: what the book is, its cover (inlined),
    its chapters, its checks, and the machine-work ledger. Read-only — derived
    entirely from the projections; writes nothing."""
    import base64
    import html as _h
    ws = resolve_slug(slug)
    d = book_detail(slug)
    us = units(slug)
    sp = spend(slug)
    vm = verify_matrix(slug)
    cov = ws / "outputs" / "kindle" / f"{slug}_KINDLE_cover.jpg"
    cover_uri = ""
    if cov.is_file() and cov.stat().st_size < 3_000_000:
        cover_uri = "data:image/jpeg;base64," + base64.b64encode(cov.read_bytes()).decode()
    total_words = sum(u.get("current_words") or 0 for u in us)
    checks = []
    for fmt, res in (vm.get("results") or {}).items():
        if res:
            checks.append((fmt, bool(res.get("all_pass")),
                           len(res.get("checks") or [])))
    tokens = sp.get("tokens") if sp.get("exact") else sp.get("est_tokens")
    esc_ = _h.escape
    rows = "".join(
        f"<tr><td class='n'>{i + 1}</td><td>{esc_(u.get('title') or u.get('id'))}</td>"
        f"<td class='w'>{(u.get('current_words') or 0):,}</td></tr>"
        for i, u in enumerate(us))
    checkrows = "".join(
        f"<li>{esc_(fmt)}: <b class='{ 'ok' if ok else 'bad'}'>"
        f"{'all checks green' if ok else 'not green'}</b> ({n} checks)</li>"
        for fmt, ok, n in checks) or "<li>no verification sweep recorded yet</li>"
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc_(d['title'])} — book passport</title>
<style>
 body{{font:16px/1.6 Georgia,serif;color:#23201a;background:#f5f0e4;margin:0;padding:2rem 1rem}}
 .card{{max-width:640px;margin:0 auto;background:#fdfbf4;border:1px solid #e3dbc6;
   border-radius:16px;padding:2.2rem;box-shadow:0 10px 34px rgba(60,50,25,.12)}}
 img.cover{{width:200px;border-radius:6px 10px 10px 6px;box-shadow:0 12px 30px rgba(60,50,25,.3);
   display:block;margin:0 auto 1.4rem}}
 h1{{font-size:1.7rem;text-align:center;margin:.2rem 0}}
 .by{{text-align:center;color:#77705e;margin-bottom:1.6rem}}
 h2{{font-size:1.05rem;border-bottom:1px solid #e3dbc6;padding-bottom:.3rem;margin-top:1.8rem}}
 table{{width:100%;border-collapse:collapse;font-size:.92rem}}
 td{{padding:.25rem .4rem;border-bottom:1px solid #efe9d8}} td.n{{color:#a49b85;width:2rem}}
 td.w{{text-align:right;color:#77705e}}
 ul{{padding-left:1.2rem;font-size:.92rem}} .ok{{color:#2e6b47}} .bad{{color:#9c4a33}}
 .foot{{margin-top:2rem;text-align:center;color:#a49b85;font-size:.8rem}}
 .stat{{display:flex;gap:1.6rem;justify-content:center;font-size:.9rem;color:#4a4437;
   flex-wrap:wrap;margin-top:.6rem}}
</style></head><body><div class="card">
{f'<img class="cover" src="{cover_uri}" alt="cover">' if cover_uri else ''}
<h1>{esc_(d['title'])}</h1>
{f"<div class='by'>{esc_(d.get('subtitle') or '')}</div>" if d.get('subtitle') else ''}
<div class="by">by {esc_(d.get('author') or 'unknown')}</div>
<div class="stat"><span>{len(us)} {esc_(d.get('unit_noun') or 'chapter')}s</span>
<span>{total_words:,} words</span>
<span>{(sp.get('calls') or 0)} model calls</span>
{f"<span>~{int(tokens or 0):,} tokens of machine work</span>" if tokens else ''}</div>
<h2>Contents</h2><table>{rows}</table>
<h2>Every page checked</h2><ul>{checkrows}</ul>
<div class="foot">Made with BOOKSMITH · the machine wrote under hard checks;
a human approved every change · {esc_(_iso(time.time()))}</div>
</div></body></html>"""


# ---------------------------------------------------------------------------
# verify matrix (S4) — cached results written by studio/verify_runner.py
# ---------------------------------------------------------------------------
def verify_matrix(slug: str) -> dict:
    ws = resolve_slug(slug)
    cfg = _read_json(ws / "book_config.json") or {}
    d = ws / "_studio" / "verify"
    per = {}
    for fmt in cfg.get("formats") or []:
        per[fmt] = _read_json(d / f"{fmt}.json")
    return {"formats": cfg.get("formats") or [], "results": per,
            "summary": _read_json(d / "summary.json")}


# ---------------------------------------------------------------------------
# intake (S4)
# ---------------------------------------------------------------------------
def intake(slug: str) -> dict:
    ws = resolve_slug(slug)
    idir = ws / "intake"
    files = []
    if idir.is_dir():
        for p in sorted(idir.iterdir()):
            if p.is_file():
                files.append({"name": p.name, "size": p.stat().st_size,
                              "class": _classify_intake(p),
                              "mtime": _iso(p.stat().st_mtime)})
    digests = []
    cdir = ws / "canon_refs"
    if cdir.is_dir():
        for p in sorted(cdir.glob("_digest_*.md")):
            digests.append({"name": p.name,
                            "text": _read_text(p, cap=4000) or ""})
    return {"brief": _read_text(ws / "brief.md") or "",
            "files": files, "digests": digests,
            "ingest": _read_json(cdir / "_ingest.json")}


def _classify_intake(p: Path) -> str:
    ext = p.suffix.lower()
    if ext in {".md", ".txt", ".markdown"}:
        return "canon_text"
    if ext in {".pdf", ".docx", ".epub", ".htm", ".html"}:
        return "document"
    if ext in {".png", ".jpg", ".jpeg", ".webp", ".gif"}:
        return "image"
    if ext in {".mp3", ".wav", ".m4a", ".mp4", ".mov"}:
        return "media"
    return "other"


# ---------------------------------------------------------------------------
# doctor (long-TTL cached; Word-COM checks can take seconds)
# ---------------------------------------------------------------------------
_doctor_cache: tuple[float, dict] | None = None
_DOCTOR_TTL = 600.0


def doctor(refresh: bool = False) -> dict:
    global _doctor_cache
    now = time.time()
    if _doctor_cache and not refresh and now - _doctor_cache[0] < _DOCTOR_TTL:
        return _doctor_cache[1]
    rc, out, err = _run([sys.executable, str(TOOLS / "doctor.py"), "--json"], timeout=240)
    data = None
    s = out.strip()
    if s:
        try:
            data = json.loads(s)
        except Exception:
            i, j = s.find("{"), s.rfind("}")
            if 0 <= i < j:
                try:
                    data = json.loads(s[i:j + 1])
                except Exception:
                    data = None
    if not isinstance(data, dict):
        data = {"error": f"doctor exit {rc}: {(out + err).strip()[-300:]}"}
    _doctor_cache = (now, data)
    return data
