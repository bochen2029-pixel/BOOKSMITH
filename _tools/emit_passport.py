#!/usr/bin/env python3
"""emit_passport.py — the book passport as DATA: one JSON receipts object per book.

The passport is the machine-legible record of a finished book: identity, contents,
word counts, the human/machine authorship line, gate verdicts, spend, cover byte
identity, and the physical dimensions a 3D shelf needs. The Studio has rendered a
passport as HTML since S10 (`studio/projection.py:passport_html`); this tool emits
the same truth as JSON so the bookshelf.ink shelf, the AEO/receipts surface, and
any future consumer read ONE versioned object instead of scraping a page.

Schema: `_tools/passport.schema.json` (v0.1, ratified 2026-08-27 with the web
session — sandbox book-estate, PASSPORT_SHAPE + PASSPORT_COMMENTS). Contract:
additive-only within a version; consumers ignore unknown fields; breaking changes
bump `passport_version`.

Privacy law (delta 3): `public` defaults FALSE and comes from `book_config.passport
.public` (or the explicit --public flag). Consumers must refuse a passport without
`public: true` — the roster rule enforced in data, not just process.

Usage:
  python _tools/emit_passport.py --config book_workspace/<slug>/book_config.json
      [--out PATH]        default: <ws>/outputs/passport/passport.json
      [--publish DIR]     also copy the ebook cover bytes beside the passport
                          (texture cache keys on sha256 — delta 4)
      [--public]          force public:true for this emission (operator act;
                          normally set book_config.passport.public instead)
      [--no-validate]     skip jsonschema validation (validated by default when
                          the jsonschema package is importable)

stdout = the absolute path of the written passport (machine-parseable);
stderr = the human summary. Exit 0 ok · 2 config/workspace missing or invalid.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

KIT_ROOT = Path(__file__).resolve().parent.parent
SCHEMA_PATH = Path(__file__).resolve().parent / "passport.schema.json"


def _read_json(p: Path):
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return None


def _wc(p: Path) -> int:
    try:
        return len(p.read_text(encoding="utf-8").split())
    except Exception:
        return 0


def _sha256_file(p: Path) -> str | None:
    try:
        h = hashlib.sha256()
        with p.open("rb") as f:
            for chunk in iter(lambda: f.read(1 << 20), b""):
                h.update(chunk)
        return h.hexdigest()
    except Exception:
        return None


def _iso_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _gates_version() -> str | None:
    """Kit commit short-sha the gates ran under (delta 5). Null when git absent."""
    try:
        out = subprocess.run(
            ["git", "-C", str(KIT_ROOT), "rev-parse", "--short", "HEAD"],
            capture_output=True, text=True, timeout=10)
        sha = (out.stdout or "").strip()
        return sha if out.returncode == 0 and re.fullmatch(r"[0-9a-f]{4,40}", sha) else None
    except Exception:
        return None


def _spend(ws: Path) -> dict:
    files: list[Path] = []
    for d in (ws / "_engine" / "calls", ws / "_studio" / "chat" / "calls"):
        if d.is_dir():
            files.extend(sorted(d.glob("call_*.json")))
    tin = tout = 0
    with_usage = 0
    for f in files:
        rec = _read_json(f) or {}
        if isinstance(rec.get("in_tokens"), int) and isinstance(rec.get("out_tokens"), int):
            with_usage += 1
            tin += rec["in_tokens"]
            tout += rec["out_tokens"]
    exact = bool(files) and with_usage == len(files)
    return {
        "model_calls": len(files),
        "tokens_in": tin if with_usage else None,
        "tokens_out": tout if with_usage else None,
        "tokens": (tin + tout) if with_usage else None,
        "exact": exact,
    }


def _checks(ws: Path, formats: list[str]) -> list[dict]:
    rows = []
    vdir = ws / "_studio" / "verify"
    for fmt in formats:
        res = _read_json(vdir / f"{fmt}.json")
        if res:
            rows.append({"format": fmt,
                         "all_pass": bool(res.get("all_pass")),
                         "n_checks": len(res.get("checks") or [])})
    return rows


def _cover(ws: Path, slug: str) -> dict:
    rel = f"outputs/kindle/{slug}_KINDLE_cover.jpg"
    f = ws / "outputs" / "kindle" / f"{slug}_KINDLE_cover.jpg"
    method = None
    art_dir = ws / "cover_art"
    if art_dir.is_dir():
        sidecars = sorted(art_dir.glob("*.provenance.json"),
                          key=lambda p: p.stat().st_mtime, reverse=True)
        for sc in sidecars:
            m = (_read_json(sc) or {}).get("method")
            if m:
                method = m
                break
    return {"rel": rel if f.is_file() else None,
            "exists": f.is_file(),
            "sha256": _sha256_file(f) if f.is_file() else None,
            "method": method,
            "published": None}


def _physical(ws: Path, cfg: dict) -> dict:
    trim = cfg.get("trim") or {}
    trim_s = None
    if isinstance(trim, dict) and trim.get("w") and trim.get("h"):
        trim_s = f"{trim['w']}x{trim['h']}"
    pages: dict[str, int | None] = {}
    spine_in = None
    for fmt in cfg.get("formats") or []:
        meta = _read_json(ws / "outputs" / fmt / "cover_meta.json")
        if meta and isinstance(meta.get("pages"), int):
            pages[fmt] = meta["pages"]
            if spine_in is None and isinstance(meta.get("spine_in"), (int, float)):
                spine_in = float(meta["spine_in"])
    return {"trim": trim_s, "pages_by_format": pages, "spine_in": spine_in}


def _authorship(ws: Path, cfg: dict, units: list[dict]) -> dict:
    human: list[str] = []
    hj = _read_json(ws / "registry" / "human_edited_units.json")
    if isinstance(hj, list):
        human = [str(u) for u in hj]
    elif isinstance(hj, dict) and isinstance(hj.get("units"), list):
        human = [str(u) for u in hj["units"]]
    else:
        ledger = ws / "registry" / "authorship_ledger.jsonl"
        if ledger.is_file():
            latest: dict[str, str] = {}
            for line in ledger.read_text(encoding="utf-8").splitlines():
                try:
                    row = json.loads(line)
                    latest[str(row.get("unit"))] = str(row.get("actor"))
                except Exception:
                    continue
            human = sorted(u for u, a in latest.items() if a == "human")
    default_cls = ((cfg.get("authorship") or {}).get("default_class")) or "C"
    overrides = ((cfg.get("authorship") or {}).get("per_chapter_overrides")) or {}
    hist: dict[str, int] = {}
    for u in units:
        cls = overrides.get(u["id"]) or u.get("class") or default_cls
        hist[cls] = hist.get(cls, 0) + 1
    return {"human_edited_units": human, "classes": hist}


def build_passport(config_path: Path, public_flag: bool = False) -> dict:
    cfg = _read_json(config_path)
    if not cfg:
        raise SystemExit(f"[passport] cannot read config: {config_path}")
    ws = config_path.resolve().parent
    slug = cfg.get("slug") or ws.name
    pcfg = cfg.get("passport") or {}
    units_cfg = cfg.get("units") or []
    units = []
    for u in units_cfg:
        uid = u.get("id")
        units.append({"id": uid, "title": u.get("title") or uid,
                      "class": u.get("class"),
                      "words": _wc(ws / "manuscript" / "current" / f"{uid}_current.md")})
    doc = {
        "passport_version": "0.1",
        "slug": slug,
        "title": cfg.get("title") or slug,
        "subtitle": cfg.get("subtitle") or None,
        "author": cfg.get("author") or "unknown",
        "unit_noun": ((cfg.get("voice") or {}).get("unit_noun")) or "chapter",
        "lang": cfg.get("language") or "en",
        "translation_of": pcfg.get("translation_of") or None,
        "public": bool(public_flag or pcfg.get("public") or False),
        "units": [{k: v for k, v in u.items() if k != "class"} for u in units],
        "totals": {"units": len(units), "words": sum(u["words"] for u in units)},
        "spend": _spend(ws),
        "checks": _checks(ws, cfg.get("formats") or []),
        "gates_version": _gates_version(),
        "cover": _cover(ws, slug),
        "physical": _physical(ws, cfg),
        "authorship": _authorship(ws, cfg, units),
        "generated": _iso_now(),
        "made_with": "BOOKSMITH",
        "generator": "emit_passport.py v0.1",
    }
    return doc


def _validate(doc: dict) -> str:
    """Validate against the schema when jsonschema is available; always run the
    cheap structural floor regardless (required keys present, types sane)."""
    for key in ("passport_version", "slug", "title", "author", "units", "totals",
                "public", "generated"):
        if key not in doc:
            raise SystemExit(f"[passport] structural floor failed: missing {key}")
    try:
        import jsonschema  # type: ignore
    except Exception:
        return "floor-only (jsonschema not installed)"
    schema = _read_json(SCHEMA_PATH)
    if not schema:
        raise SystemExit(f"[passport] schema unreadable: {SCHEMA_PATH}")
    jsonschema.validate(doc, schema)
    return "jsonschema PASS"


def main() -> None:
    ap = argparse.ArgumentParser(description="Emit the book passport JSON (schema v0.1)")
    ap.add_argument("--config", required=True)
    ap.add_argument("--out", default=None)
    ap.add_argument("--publish", default=None,
                    help="directory to publish into: passport.json + cover bytes beside it")
    ap.add_argument("--public", action="store_true",
                    help="force public:true for this emission (operator act)")
    ap.add_argument("--no-validate", action="store_true")
    args = ap.parse_args()

    config_path = Path(args.config)
    if not config_path.is_file():
        raise SystemExit(f"[passport] no such config: {config_path}")
    doc = build_passport(config_path, public_flag=args.public)
    ws = config_path.resolve().parent

    if args.publish:
        outdir = Path(args.publish)
        outdir.mkdir(parents=True, exist_ok=True)
        out = outdir / "passport.json"
        cov = doc["cover"]
        if cov["exists"] and cov["sha256"]:
            src = ws / "outputs" / "kindle" / f"{doc['slug']}_KINDLE_cover.jpg"
            pub_name = f"{doc['slug']}_cover_{cov['sha256'][:12]}.jpg"
            (outdir / pub_name).write_bytes(src.read_bytes())
            cov["published"] = pub_name
    else:
        out = Path(args.out) if args.out else ws / "outputs" / "passport" / "passport.json"
        out.parent.mkdir(parents=True, exist_ok=True)

    verdict = "skipped" if args.no_validate else _validate(doc)

    tmp = out.with_name(f".{out.name}.tmp{os.getpid()}")
    tmp.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n",
                   encoding="utf-8", newline="\n")
    os.replace(tmp, out)

    print(str(out.resolve()))
    print(f"[passport] {doc['slug']}: {doc['totals']['units']} units · "
          f"{doc['totals']['words']:,} words · public={doc['public']} · "
          f"cover={'yes' if doc['cover']['exists'] else 'no'} · validate: {verdict}",
          file=sys.stderr)


if __name__ == "__main__":
    main()
