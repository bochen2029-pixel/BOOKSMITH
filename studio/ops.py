#!/usr/bin/env python3
r"""
ops.py — BOOKSMITH Studio's SINGLE WRITE PATH (S2).

Every mutation any Studio surface makes (button today, chat in S3) is an
Operation from the closed catalog below (docs/STUDIO_SPEC.md §8). Risk classes:

  SAFE     regenerate-only via the engine — executes immediately, still ledgered.
  CONTENT  changes what the book says/shows — ALWAYS wrapped in a Proposal the
           human approves; the approval click is the same click on a button flow.

Invariants enforced HERE (not trusted to callers or models):
  * Class-A units reject content ops (human-authored, mirror of stage_draft);
  * drafts are append-only — before anything replaces manuscript/current, the
    current text is archived as drafts/<uid>_v{N+1}.md (the versioning the
    harness lane does by hand, done by the ops layer for the engine lane);
  * every op appends one line to the book's CHANGELOG.md and one JSON record to
    book_workspace/<slug>/_studio/ops.jsonl;
  * revise submits `--only draft:<uid>` WITHOUT --force-stage on purpose: the
    E-2 note hash MUST re-open the draft. If the engine skips it, that is an
    E-2 regression and the drift watcher flags it loudly.

The staleness predictor is CONSERVATIVE (SPEC §6.4): it may over-predict (the
cascade materializes progressively — produce goes stale only once assemble
emits a new master), and the drift ALARM fires only on UNDER-prediction:
a stage that went stale which the table did not predict.
"""
from __future__ import annotations

import json
import re
import shutil
import threading
import time
from datetime import datetime, timezone
from pathlib import Path

import jobs
import projection as P

KIT = P.KIT
_UID_RE = re.compile(r"^[A-Za-z0-9._\-]+$")
_pseq = 0
_plock = threading.Lock()


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


class OpError(ValueError):
    """Validation failure — surfaces as a 4xx with its message verbatim."""


# ---------------------------------------------------------------------------
# ledgers
# ---------------------------------------------------------------------------
def _studio_dir(ws: Path) -> Path:
    d = ws / "_studio"
    (d / "proposals").mkdir(parents=True, exist_ok=True)
    return d


def _ledger(ws: Path, op: str, detail: str, proposal: str | None, job: str | None):
    line = (f"- {_now()} [studio] {op} {detail}"
            + (f" proposal={proposal}" if proposal else "")
            + (f" job={job}" if job else ""))
    ch = ws / "CHANGELOG.md"
    try:
        if not ch.exists():
            ch.write_text("# CHANGELOG\n\n", encoding="utf-8")
        with ch.open("a", encoding="utf-8") as f:
            f.write(line + "\n")
    except OSError:
        pass
    rec = {"ts": _now(), "op": op, "detail": detail, "proposal": proposal, "job": job}
    with (_studio_dir(ws) / "ops.jsonl").open("a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")


# ---------------------------------------------------------------------------
# unit helpers (append-only versioning lives HERE)
# ---------------------------------------------------------------------------
def _cfg(ws: Path) -> dict:
    return json.loads((ws / "book_config.json").read_text(encoding="utf-8"))


def _unit(ws: Path, uid: str) -> dict:
    if not _UID_RE.match(uid or ""):
        raise OpError(f"invalid unit id: {uid!r}")
    cfg = _cfg(ws)
    for u in cfg.get("units") or []:
        if u.get("id") == uid:
            eff = str(u.get("class")
                      or (cfg.get("authorship") or {}).get("default_class", "C")).upper()
            if eff == "A":
                raise OpError(f"unit {uid} is Class A (human-authored) — "
                              "content ops are refused by doctrine")
            return u
    # engine fallback books (no config units): allow if a current file exists
    if (ws / "manuscript" / "current" / f"{uid}_current.md").exists():
        return {"id": uid, "class": "C"}
    raise OpError(f"no such unit: {uid}")


def _next_version(ws: Path, uid: str) -> int:
    n = 0
    drafts = ws / "manuscript" / "drafts"
    if drafts.is_dir():
        for p in drafts.glob(f"{uid}_v*.md"):
            m = re.fullmatch(rf"{re.escape(uid)}_v(\d+)\.md", p.name)
            if m:
                n = max(n, int(m.group(1)))
    return n + 1


def _archive_current(ws: Path, uid: str) -> str | None:
    """Append-only doctrine: current is archived as the next vN before anything
    replaces it. Returns the archived version name, or None if no current."""
    cur = ws / "manuscript" / "current" / f"{uid}_current.md"
    if not cur.is_file():
        return None
    n = _next_version(ws, uid)
    dst = ws / "manuscript" / "drafts" / f"{uid}_v{n}.md"
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(cur, dst)
    return f"v{n}"


# ---------------------------------------------------------------------------
# the staleness predictor (conservative; table transcribed from engine hashes)
# ---------------------------------------------------------------------------
def _predict_unit_change(ws: Path, uid: str) -> dict:
    cfg = _cfg(ws)
    units = [u.get("id") for u in (cfg.get("units") or [])]
    nxt = None
    if uid in units:
        i = units.index(uid)
        if i + 1 < len(units):
            nxt = units[i + 1]
    immediate = ["integrate", "assemble"] + ([f"draft:{nxt}"] if nxt else [])
    eventual = ([f"draft:{uid}"] + immediate
                + [f"produce:{f}" for f in cfg.get("formats") or []]
                + ["verify", "emit"])
    return {"immediate": immediate, "eventual": eventual,
            "formats_stale": cfg.get("formats") or [],
            "note": ("produce/verify/emit go stale progressively as assemble "
                     "emits a new master; Reconverge settles the whole suffix")}


# ---------------------------------------------------------------------------
# the op catalog
# ---------------------------------------------------------------------------
def _engine_argv(ws: Path, *extra: str) -> list[str]:
    import sys
    return [sys.executable, str(P.TOOLS / "engine.py"),
            "--config", str(ws / "book_config.json"), *extra]


def _exec_revise(ws: Path, slug: str, params: dict, pid: str) -> dict:
    uid = params["uid"]
    note = str(params.get("note") or "").strip()
    if not note:
        raise OpError("revise_unit needs a non-empty note")
    if len(note) > 2000:
        raise OpError("note too long (≤2000 chars)")
    _unit(ws, uid)
    archived = _archive_current(ws, uid)
    nd = ws / "revision_notes"
    nd.mkdir(exist_ok=True)
    with (nd / f"{uid}.md").open("a", encoding="utf-8") as f:
        f.write(f"\n\n## {_now()} — studio revise ({pid})\n{note}\n")
    # NO --force-stage: the E-2 hash must re-open the draft (see module doc)
    extra = ["--only", f"draft:{uid}"]
    backend = params.get("backend")
    if backend:
        if backend not in {"mock", "anthropic", "openai", "harness"}:
            raise OpError("bad backend")
        extra += ["--backend", backend]
    if params.get("dry_run"):
        extra.append("--dry-run")
    rec = jobs.submit("engine_stage", _engine_argv(ws, *extra), book=slug,
                      meta={"op": "revise_unit", "uid": uid, "proposal": pid})
    _ledger(ws, "revise_unit", f"{uid} archived={archived or '—'} note={len(note)}ch",
            pid, rec["id"])
    return {"job": rec, "archived": archived}


def _exec_revert(ws: Path, slug: str, params: dict, pid: str) -> dict:
    uid = params["uid"]
    to = str(params.get("to_version") or "")
    _unit(ws, uid)
    m = re.fullmatch(r"v(\d+)", to)
    if not m:
        raise OpError(f"to_version must be 'vN', got {to!r}")
    src = ws / "manuscript" / "drafts" / f"{uid}_{to}.md"
    if not src.is_file():
        raise OpError(f"no such archived version: {src.name}")
    archived = _archive_current(ws, uid)
    cur = ws / "manuscript" / "current" / f"{uid}_current.md"
    cur.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, cur)
    _ledger(ws, "revert_unit", f"{uid} -> {to} (was archived as {archived or '—'})",
            pid, None)
    return {"job": None, "archived": archived, "reverted_to": to}


def _exec_run_stage(ws: Path, slug: str, params: dict, pid: str | None) -> dict:
    stage = str(params.get("stage") or "")
    if not re.fullmatch(r"[a-z_]+(:[A-Za-z0-9._\-]+)?", stage):
        raise OpError(f"bad stage key: {stage!r}")
    extra = ["--only", stage]
    if params.get("force"):
        extra.append("--force-stage")
    if params.get("dry_run"):
        extra.append("--dry-run")
    if params.get("backend"):
        if params["backend"] not in {"mock", "anthropic", "openai", "harness"}:
            raise OpError("bad backend")
        extra += ["--backend", params["backend"]]
    rec = jobs.submit("engine_stage", _engine_argv(ws, *extra), book=slug,
                      meta={"op": params.get("_op", "run_stage"), "stage": stage,
                            "proposal": pid})
    _ledger(ws, params.get("_op", "run_stage"), stage + (" (forced)" if params.get("force") else ""),
            pid, rec["id"])
    return {"job": rec}


# ---------------------------------------------------------------------------
# S4 executors: verify matrix, cover studio, harness-bridge fulfillment
# ---------------------------------------------------------------------------
_WRAP_PROFILE = {
    "kdp_paperback": "kdp-wrap", "kdp_hardcover": "kdp-hardcover",
    "mixam_paperback": "mixam-paperback-wrap", "mixam_hardcover": "mixam-3panel",
    "blurb_paperback": "blurb-wrap", "blurb_hardcover": "blurb-imagewrap",
}
_PRINT_DOCX = {
    "kdp_paperback": "{s}_KDP_PAPERBACK", "kdp_hardcover": "{s}_KDP_HARDCOVER",
    "mixam_paperback": "inner_{s}", "mixam_hardcover": "inner_{s}",
    "blurb_paperback": "{s}_BLURB_TRADE", "blurb_hardcover": "{s}_BLURB_TRADE",
}


def _exec_verify_matrix(ws: Path, slug: str, params: dict, pid: str | None) -> dict:
    import sys
    argv = [sys.executable, str(KIT / "studio" / "verify_runner.py"),
            "--config", str(ws / "book_config.json")]
    if params.get("final"):
        argv.append("--final")
    if params.get("format"):
        argv += ["--format", str(params["format"])]
    rec = jobs.submit("tool", argv, book=slug,
                      meta={"op": "verify_matrix", "final": bool(params.get("final"))})
    _ledger(ws, "verify_matrix", "final" if params.get("final") else "standard", pid, rec["id"])
    return {"job": rec}


def _exec_reroll_cover(ws: Path, slug: str, params: dict, pid: str | None) -> dict:
    extra = ["--only", "cover", "--force-stage", "--force-cover"]
    if params.get("backend"):
        extra += ["--backend", str(params["backend"])]
    rec = jobs.submit("engine_stage", _engine_argv(ws, *extra), book=slug,
                      meta={"op": "reroll_cover", "proposal": pid})
    _ledger(ws, "reroll_cover", "forced regeneration (prior art preserved aside)",
            pid, rec["id"])
    return {"job": rec}


def _pages_for(ws: Path, slug: str, fmt: str) -> int | None:
    stem = _PRINT_DOCX.get(fmt, "").format(s=slug)
    if not stem:
        return None
    pdf = ws / "outputs" / fmt / f"{stem}.pdf"
    if not pdf.is_file():
        return None
    try:
        import fitz
        with fitz.open(str(pdf)) as doc:
            return doc.page_count
    except Exception:                                             # noqa: BLE001
        return None


def _exec_compose_wrap(ws: Path, slug: str, params: dict, pid: str | None) -> dict:
    import sys
    fmt = str(params.get("format") or "")
    profile = _WRAP_PROFILE.get(fmt)
    if not profile:
        raise OpError(f"no print wrap profile for format {fmt!r}")
    pages = params.get("pages") or _pages_for(ws, slug, fmt)
    if not pages:
        raise OpError(f"page count unknown for {fmt}: build the interior PDF first "
                      f"(⟳ produce:{fmt}), or pass pages explicitly")
    argv = [sys.executable, str(P.TOOLS / "composite_cover.py"),
            "--config", str(ws / "book_config.json"),
            "--profile", profile, "--pages", str(int(pages))]
    rec = jobs.submit("tool", argv, book=slug,
                      meta={"op": "compose_wrap", "format": fmt, "pages": int(pages)})
    _ledger(ws, "compose_wrap", f"{fmt} profile={profile} pages={pages}", pid, rec["id"])
    return {"job": rec}


def _exec_recomposite_cover(ws: Path, slug: str, params: dict, pid: str | None) -> dict:
    import sys
    argv = [sys.executable, str(P.TOOLS / "composite_cover.py"),
            "--config", str(ws / "book_config.json"), "--profile", "kindle", "--pages", "1"]
    if params.get("title_y_frac") is not None:
        argv += ["--title-y-frac", str(float(params["title_y_frac"]))]
    rec = jobs.submit("tool", argv, book=slug, meta={"op": "recomposite_ebook_cover"})
    _ledger(ws, "recomposite_ebook_cover", "kindle profile", pid, rec["id"])
    return {"job": rec}


def _exec_adjudicate_cover(ws: Path, slug: str, params: dict, pid: str | None) -> dict:
    """The human answers a PENDING perceptual gate. Recorded as a first-class
    verdict beside the artifact (SPEC §1.7) — a gate act, so it is ledgered."""
    verdict = str(params.get("verdict") or "").upper()
    if verdict not in ("PASS", "FAIL"):
        raise OpError("verdict must be PASS or FAIL")
    img = ws / "outputs" / "kindle" / f"{slug}_KINDLE_cover.jpg"
    if not img.is_file():
        raise OpError("no composited ebook cover to adjudicate")
    rec = {"verdict": verdict, "issues": [str(i)[:300] for i in (params.get("issues") or [])],
           "adjudicator": "human", "ts": _now(),
           "image_sha256": None}
    try:
        import hashlib
        rec["image_sha256"] = hashlib.sha256(img.read_bytes()).hexdigest()
    except OSError:
        pass
    out = img.with_suffix(".verdict.json")
    out.write_text(json.dumps(rec, indent=2, ensure_ascii=False), encoding="utf-8")
    _ledger(ws, "adjudicate_cover", f"{verdict} ({len(rec['issues'])} issue(s))", pid, None)
    return {"job": None, "verdict": verdict}


def _exec_fulfill_bridge(ws: Path, slug: str, params: dict, pid: str | None) -> dict:
    """Fulfill a pending harness-bridge turn from the browser: paste prose, or
    have the configured API model answer the engine's own request. The engine
    still gates the prose (nonce + gate_draft + 3-attempt budget) — this only
    supplies it."""
    uid = str(params.get("uid") or "")
    _unit(ws, uid)                                   # Class-A refusal applies here too
    bdir = ws / "_engine" / "bridge"
    req_p = bdir / f"{uid}.request.json"
    if not req_p.is_file():
        raise OpError(f"no pending bridge request for {uid}")
    req = json.loads(req_p.read_text(encoding="utf-8"))
    source = str(params.get("source") or "human_paste")
    if source == "human_paste":
        text = str(params.get("text") or "").strip()
        if not text:
            raise OpError("paste the finished unit markdown")
    elif source == "api_model":
        import sys as _sys
        _sys.path.insert(0, str(P.TOOLS))
        import model_client                                        # noqa: PLC0415
        kit_env = {}
        for cand in (P.TOOLS / "kit_env.json", P.TOOLS / "kit_env.template.json"):
            if cand.exists():
                try:
                    kit_env = json.loads(cand.read_text(encoding="utf-8"))
                    break
                except Exception:                                  # noqa: BLE001
                    pass
        cli = model_client.make_client(
            kit_env, log_dir=ws / "_engine" / "calls",
            backend_override=params.get("backend") or None)
        if cli.backend == "harness":
            raise OpError("backend=harness cannot fulfill itself; choose mock/anthropic/openai")
        text = cli.complete(req.get("system", ""), req.get("prompt", ""))
    else:
        raise OpError("source must be human_paste or api_model")
    (bdir / f"{uid}.response.md").write_text(text.strip() + "\n", encoding="utf-8")
    rec = jobs.submit("engine_stage",
                      _engine_argv(ws, "--only", f"draft:{uid}", "--backend", "harness"),
                      book=slug, meta={"op": "fulfill_bridge", "uid": uid, "source": source})
    _ledger(ws, "fulfill_bridge", f"{uid} source={source} chars={len(text)}", pid, rec["id"])
    return {"job": rec}


OPS = {
    "verify_matrix": {"risk": "SAFE", "exec": _exec_verify_matrix,
                      "predict": lambda ws, p: {"immediate": [], "eventual": [],
                                                "formats_stale": [],
                                                "note": "read-only verification sweep"}},
    "reroll_cover": {"risk": "CONTENT", "exec": _exec_reroll_cover,
                     "predict": lambda ws, p: {
                         "immediate": ["cover"],
                         "eventual": ["cover"] + [f"produce:{f}" for f in
                                                  (_cfg(ws).get("formats") or [])
                                                  if f in ("epub", "digital_pdf", "kindle")]
                         + ["verify", "emit"],
                         "formats_stale": [f for f in (_cfg(ws).get("formats") or [])
                                           if f in ("epub", "digital_pdf", "kindle")],
                         "note": "new art → the ebook cover recomposites; cover-consuming formats re-key"}},
    "recomposite_ebook_cover": {"risk": "SAFE", "exec": _exec_recomposite_cover,
                                "predict": lambda ws, p: {
                                    "immediate": [], "eventual": ["verify", "emit"],
                                    "formats_stale": [], "note": "cover bytes change"}},
    "compose_wrap": {"risk": "SAFE", "exec": _exec_compose_wrap,
                     "predict": lambda ws, p: {"immediate": [], "eventual": ["verify", "emit"],
                                               "formats_stale": [p.get("format")],
                                               "note": "print wrap regenerated at the re-derived page count"}},
    # SAFE, deliberately (deviates from SPEC §8.2's CONTENT listing — see
    # STUDIO_BUILD_LOG §4): a verdict changes no artifact, and the human's click
    # IS the decision. Wrapping it in an approval card would double-gate one
    # human act. It is still ledgered like every other op.
    "adjudicate_cover": {"risk": "SAFE", "exec": _exec_adjudicate_cover,
                         "predict": lambda ws, p: {"immediate": [], "eventual": [],
                                                   "formats_stale": [],
                                                   "note": "records a human gate verdict; no artifact changes"}},
    "fulfill_bridge": {"risk": "CONTENT", "exec": _exec_fulfill_bridge,
                       "predict": lambda ws, p: _predict_unit_change(ws, p.get("uid", "")),
                       },
    "revise_unit": {"risk": "CONTENT", "exec": _exec_revise,
                    "predict": lambda ws, p: _predict_unit_change(ws, p["uid"])},
    "revert_unit": {"risk": "CONTENT", "exec": _exec_revert,
                    "predict": lambda ws, p: _predict_unit_change(ws, p["uid"])},
    "rebuild_format": {"risk": "SAFE",
                       "exec": lambda ws, s, p, pid: _exec_run_stage(
                           ws, s, {"stage": f"produce:{p.get('format')}",
                                   "force": True, "dry_run": p.get("dry_run"),
                                   "_op": "rebuild_format"}, pid),
                       "predict": lambda ws, p: {"immediate": ["verify", "emit"],
                                                 "eventual": ["verify", "emit"],
                                                 "formats_stale": [p.get("format")],
                                                 "note": "artifact bytes change → verify/emit re-key"}},
    "verify_all": {"risk": "SAFE",
                   "exec": lambda ws, s, p, pid: _exec_run_stage(
                       ws, s, {"stage": "verify", "force": True,
                               "dry_run": p.get("dry_run"), "_op": "verify_all"}, pid),
                   "predict": lambda ws, p: {"immediate": [], "eventual": [],
                                             "formats_stale": [], "note": "read-only sweep"}},
    "run_stage": {"risk": "SAFE", "exec": _exec_run_stage,
                  "predict": lambda ws, p: {"immediate": [], "eventual": [],
                                            "formats_stale": [],
                                            "note": "single-stage re-run"}},
}


# ---------------------------------------------------------------------------
# proposals (CONTENT ops pause here for the human)
# ---------------------------------------------------------------------------
def _satisfied_map(slug: str) -> dict:
    data = P.plan(slug, refresh=True)
    return {e["key"]: bool(e.get("satisfied")) for e in data.get("plan", [])} \
        if not data.get("error") else {}


def _proposal_path(ws: Path, pid: str) -> Path:
    return _studio_dir(ws) / "proposals" / f"{pid}.json"


def _save_proposal(ws: Path, prop: dict) -> None:
    p = _proposal_path(ws, prop["id"])
    tmp = p.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(prop, indent=2, ensure_ascii=False), encoding="utf-8")
    tmp.replace(p)


def validate_item(ws: Path, item: dict) -> dict:
    """Validate ONE {op, params} against the catalog + the book on disk. Raises
    OpError with a human-readable reason. Called at PROPOSAL time so an illegal
    op (Class-A target, unknown unit, unconfigured format) never reaches a card."""
    op_id = str(item.get("op") or "")
    spec = OPS.get(op_id)
    if not spec:
        raise OpError(f"unknown op: {op_id!r} (catalog: {', '.join(OPS)})")
    params = dict(item.get("params") or {})
    if op_id in ("revise_unit", "revert_unit", "fulfill_bridge"):
        uid = str(params.get("uid") or "")
        _unit(ws, uid)                      # raises on unknown / Class A
        if op_id == "revise_unit":
            note = str(params.get("note") or "").strip()
            if not note:
                raise OpError("revise_unit needs a non-empty note")
            if len(note) > 2000:
                raise OpError(f"note too long ({len(note)} chars, max 2000)")
        else:
            to = str(params.get("to_version") or "")
            if not re.fullmatch(r"v\d+", to):
                raise OpError(f"to_version must be 'vN', got {to!r}")
            if not (ws / "manuscript" / "drafts" / f"{uid}_{to}.md").is_file():
                raise OpError(f"no archived version {to} for {uid}")
    elif op_id in ("rebuild_format", "compose_wrap"):
        fmt = str(params.get("format") or "")
        configured = _cfg(ws).get("formats") or []
        if fmt not in configured:
            raise OpError(f"format {fmt!r} is not configured for this book "
                          f"({', '.join(configured) or 'none'})")
        if op_id == "compose_wrap" and fmt not in _WRAP_PROFILE:
            raise OpError(f"{fmt} has no print wrap (ebook formats carry a front cover only)")
    elif op_id == "adjudicate_cover":
        if str(params.get("verdict") or "").upper() not in ("PASS", "FAIL"):
            raise OpError("verdict must be PASS or FAIL")
    return {"op": op_id, "params": params}


def _merge_radius(ws: Path, items: list[dict]) -> dict:
    imm, evt, fmts, notes = [], [], [], []
    for it in items:
        r = OPS[it["op"]]["predict"](ws, it["params"])
        for k, dst in (("immediate", imm), ("eventual", evt), ("formats_stale", fmts)):
            for v in r.get(k) or []:
                if v and v not in dst:
                    dst.append(v)
        if r.get("note") and r["note"] not in notes:
            notes.append(r["note"])
    return {"immediate": imm, "eventual": evt, "formats_stale": fmts,
            "note": " · ".join(notes)}


def _create_proposal(ws: Path, slug: str, items: list[dict], source: dict,
                     summary: str | None) -> dict:
    global _pseq
    with _plock:
        _pseq += 1
        pid = f"p_{time.strftime('%Y%m%d_%H%M%S')}_{_pseq:02d}"
    prop = {"id": pid, "book": slug, "created": _now(),
            "summary": summary or "; ".join(
                f"{i['op']} {i['params'].get('uid') or i['params'].get('format') or ''}".strip()
                for i in items),
            "ops": items, "source": source,
            "risk": ("CONTENT" if any(OPS[i["op"]]["risk"] == "CONTENT" for i in items)
                     else "SAFE"),
            "blast_radius": _merge_radius(ws, items),
            "state": "proposed", "results": [],
            "satisfied_before": _satisfied_map(slug)}
    if len(items) == 1:                     # convenience mirrors for single-op cards
        prop["op"], prop["params"] = items[0]["op"], items[0]["params"]
    _save_proposal(ws, prop)
    jobs._emit("proposal", {"book": slug, "id": pid, "state": "proposed"})
    return prop


def submit_plan(slug: str, items: list[dict], source: dict,
                summary: str | None = None) -> dict:
    """Create a multi-op proposal (the chat's only write channel). Every item is
    validated first: one bad op rejects the whole plan, nothing is created."""
    ws = P.resolve_slug(slug)
    if not items:
        raise OpError("a plan needs at least one op")
    if len(items) > 12:
        raise OpError(f"plan too large ({len(items)} ops, max 12)")
    validated = [validate_item(ws, it) for it in items]
    return _create_proposal(ws, slug, validated, source, summary)


def submit_op(slug: str, payload: dict) -> dict:
    """Single-op entry (the S2 button path). SAFE ops execute immediately and are
    still ledgered; CONTENT ops become a one-op proposal."""
    ws = P.resolve_slug(slug)
    op_id = str(payload.get("op") or "")
    spec = OPS.get(op_id)
    if not spec:
        raise OpError(f"unknown op: {op_id!r} (catalog: {', '.join(OPS)})")
    params = {k: v for k, v in payload.items() if k != "op"}
    item = validate_item(ws, {"op": op_id, "params": params})
    if spec["risk"] == "SAFE":
        result = spec["exec"](ws, slug, item["params"], None)
        return {"executed": {"op": op_id, "job": result.get("job")}}
    prop = _create_proposal(ws, slug, [item], {"kind": "button"}, None)
    return {"proposal": prop}


def list_proposals(slug: str, limit: int = 30) -> list[dict]:
    ws = P.resolve_slug(slug)
    pdir = _studio_dir(ws) / "proposals"
    items = []
    for p in sorted(pdir.glob("p_*.json"), reverse=True)[:limit]:
        try:
            items.append(json.loads(p.read_text(encoding="utf-8")))
        except Exception:
            continue
    return items


def _load_proposal(ws: Path, pid: str) -> dict:
    p = _proposal_path(ws, pid)
    if not p.is_file():
        raise OpError(f"no such proposal: {pid}")
    return json.loads(p.read_text(encoding="utf-8"))


def reject(slug: str, pid: str) -> dict:
    ws = P.resolve_slug(slug)
    prop = _load_proposal(ws, pid)
    if prop["state"] != "proposed":
        raise OpError(f"proposal is {prop['state']}, not proposed")
    prop["state"] = "rejected"
    prop["decided"] = _now()
    _save_proposal(ws, prop)
    _ledger(ws, ",".join(i["op"] for i in prop.get("ops") or []) or "op",
            "REJECTED " + (prop.get("summary") or "")[:160], pid, None)
    jobs._emit("proposal", {"book": slug, "id": pid, "state": "rejected"})
    return prop


def approve(slug: str, pid: str, backend: str | None = None) -> dict:
    """Approve and execute. `backend` chooses WHICH model writes the prose for
    any drafting op in the plan — the chat compiler never picks the writer; the
    human does, at approval time."""
    ws = P.resolve_slug(slug)
    prop = _load_proposal(ws, pid)
    if prop["state"] != "proposed":
        raise OpError(f"proposal is {prop['state']}, not proposed")
    if backend and backend not in {"mock", "anthropic", "openai", "harness"}:
        raise OpError("bad backend")
    prop["state"] = "applying"
    prop["decided"] = _now()
    if backend:
        prop["backend"] = backend
    _save_proposal(ws, prop)
    jobs._emit("proposal", {"book": slug, "id": pid, "state": "applying"})
    threading.Thread(target=_apply, args=(slug, pid, backend), daemon=True).start()
    return prop


def _wait(jid: str, timeout_s: float = 600.0) -> dict | None:
    for _ in range(int(timeout_s * 2)):
        g = jobs.get(jid)
        if g and g.get("ended"):
            return g
        time.sleep(0.5)
    return jobs.get(jid)


def _apply(slug: str, pid: str, backend: str | None = None) -> None:
    """Execute a proposal's ops IN ORDER, stop-on-first-failure. Completed ops
    stand (append-only makes partial application safe and visible). Then compare
    observed staleness against the prediction: the ALARM fires only on
    UNDER-prediction (SPEC §6.4) — a newly-stale stage the table did not name is
    a spec bug and must be loud, never absorbed."""
    ws = P.resolve_slug(slug)
    prop = _load_proposal(ws, pid)
    items = prop.get("ops") or []
    ok = True
    e2_warning = None
    for i, item in enumerate(items):
        spec = OPS[item["op"]]
        params = dict(item["params"])
        if backend and "backend" not in params:
            params["backend"] = backend
        try:
            result = spec["exec"](ws, slug, params, pid)
        except (OpError, OSError) as e:
            prop["results"].append({"op_index": i, "op": item["op"],
                                    "outcome": "error", "detail": str(e)[:400]})
            ok = False
            break
        job = result.get("job")
        jid = job["id"] if job else None
        outcome, detail = "ok", ""
        if jid:
            g = _wait(jid)
            sem = (g or {}).get("semantics", "error")
            outcome = "ok" if sem == "complete" else sem
            detail = f"exit={(g or {}).get('exit')}"
            # E-2 self-check: a revise MUST re-open the draft, not skip it
            if item["op"] == "revise_unit":
                txt = (jobs.log_text(jid).get("text") or "")
                if f"skip_done: stage=draft:{item['params'].get('uid')}" in txt:
                    e2_warning = ("draft was SKIPPED despite a new revision note — "
                                  "E-2 hash fold regressed; investigate before "
                                  "trusting revise")
                    outcome = "e2_regression"
        prop["results"].append({"op_index": i, "op": item["op"], "job": jid,
                                "outcome": outcome, "detail": detail})
        _save_proposal(ws, prop)
        if outcome != "ok":
            ok = False
            break
    time.sleep(0.3)
    before = prop.get("satisfied_before") or {}
    after = _satisfied_map(slug)
    newly_stale = sorted(k for k, sat in after.items()
                         if not sat and before.get(k) is True)
    radius = prop.get("blast_radius", {})
    predicted = set(radius.get("immediate") or []) | set(radius.get("eventual") or [])
    prop["state"] = "applied" if ok else "failed"
    prop["observed_newly_stale"] = newly_stale
    prop["drift"] = sorted(set(newly_stale) - predicted)
    prop["satisfied_after"] = after
    if e2_warning:
        prop["e2_warning"] = e2_warning
    _save_proposal(ws, prop)
    jobs._emit("proposal", {"book": slug, "id": pid, "state": prop["state"],
                            "drift": prop["drift"]})
