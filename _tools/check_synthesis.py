#!/usr/bin/env python3
"""
check_synthesis.py -- BOOKSMITH GATE-4 synthesis / anthology-tell gate.

PURPOSE
    In *synthesis* integration mode the promise is that satellite sources
    DISSOLVE into a book grown from the core -- recombination is not synthesis.
    The failure signature is the "anthology tell": a unit whose canon draws
    map ~1:1 onto a single source document, so the book quietly reverts to a
    stitched anthology along source-document boundaries.

    CLAUDE.md GATE-4 states the rule as prose ("in synthesis mode, no unit maps
    ~1:1 onto a single source document -- the anthology signature -- check each
    unit's canon-anchor distribution"). This tool makes that rule mechanical:
    it reads each unit's `## Canon Anchors` against the source corpus and fails
    (in synthesis mode) any unit that references exactly one source while the
    corpus holds two or more. Taste becomes a machine-checkable gate.

    Diagnostic + deterministic. It never writes to the tree and never raises an
    unhandled traceback: a missing registry, an unfilled contract template, or
    a single-source corpus becomes a SKIP row with a reason, not a crash.

WHAT COUNTS AS A "SOURCE"
    The source corpus is discovered from two places under the workspace:
      1. `canon_refs/_digest_<slug>.md` -- one relational digest per satellite
         (see templates/digest.template.md); each filename's <slug> is a source.
      2. `registry/canon_refs.md` -- if present, any `_digest_<slug>` or
         explicit source tokens named there.
    A unit's sources are the corpus slugs whose token appears in that unit's
    `## Canon Anchors` section of `contracts/<id>.md`. The core source is not a
    satellite; drawing on the core alone is never the anthology tell.

USAGE
    python _tools/check_synthesis.py --config book_config.json
    python _tools/check_synthesis.py --config book_config.json --json
    python _tools/check_synthesis.py --config book_config.json --root <workspace>
    python _tools/check_synthesis.py --config book_config.json --strict
        # --strict: also fail on the tell in anthology/reforge modes (default:
        #           only synthesis mode fails; other modes report INFO)

    Exit codes: 0 = gate clean (or not applicable: <2 sources / no data)
                1 = anthology tell found in a mode that fails on it
                2 = usage / config error

PROVENANCE
    Built from the BOOKSMITH portability audit (PORTABILITY_GAP_ANALYSIS.md
    TOP-FIVE #4 + Wave 3 GATE-4). Pure Python standard library -- runs with
    zero pip installs on Windows / macOS / Linux. Repo root is derived from
    this file's location, never cwd, never a hard-coded path. Config knobs are
    read from book_config.json; nothing that belongs in config is hard-coded.
"""

import argparse
import json
import re
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Repo root: this file lives in <repo>/_tools/check_synthesis.py.
# ---------------------------------------------------------------------------
REPO = Path(__file__).resolve().parent.parent

PASS, WARN, FAIL, SKIP, INFO = "PASS", "WARN", "FAIL", "SKIP", "INFO"

# Modes in which a 1:1 unit->source mapping is a defect. Synthesis always
# fails; the others fail only under --strict (anthology keeps parts distinct
# by design; reforge is a rebirth whose source coupling is intentional).
FAIL_MODES_DEFAULT = {"synthesis"}
FAIL_MODES_STRICT = {"synthesis", "anthology", "reforge"}


class Row:
    """One per-unit finding."""
    __slots__ = ("unit", "status", "sources", "detail")

    def __init__(self, unit, status, sources, detail=""):
        self.unit = unit
        self.status = status
        self.sources = sources
        self.detail = detail

    def as_dict(self):
        return {
            "unit": self.unit,
            "status": self.status,
            "sources": sorted(self.sources),
            "detail": self.detail,
        }


def _load_json(path):
    try:
        with open(path, "r", encoding="utf-8") as fh:
            return json.load(fh), None
    except Exception as exc:
        return None, f"{exc.__class__.__name__}: {exc}"


def workspace_root(cfg, config_path, explicit_root):
    """Resolve the book workspace root. Mirrors lint_manuscript.py:
    Priority: --root > book_workspace/<slug> relative to the config's parent
    dir > the config's own directory."""
    if explicit_root:
        return Path(explicit_root)
    slug = (cfg or {}).get("slug")
    base = config_path.resolve().parent
    if slug:
        candidate = base / "book_workspace" / slug
        if candidate.exists():
            return candidate
        if base.name == slug:
            return base
    return base


def _norm(token):
    """Lowercase, strip non-alphanumerics -> a matchable token stem."""
    return re.sub(r"[^a-z0-9]+", "", str(token).lower())


def discover_sources(root):
    """Return {slug: normalized_token} for every satellite source found.

    Sources come from canon_refs/_digest_<slug>.md filenames and any
    _digest_<slug> tokens named in registry/canon_refs.md."""
    sources = {}
    canon_dir = root / "canon_refs"
    if canon_dir.is_dir():
        for f in canon_dir.glob("_digest_*.md"):
            slug = f.stem[len("_digest_"):]
            if slug:
                sources[slug] = _norm(slug)
    reg = root / "registry" / "canon_refs.md"
    if reg.is_file():
        try:
            text = reg.read_text(encoding="utf-8", errors="replace")
        except Exception:
            text = ""
        for m in re.finditer(r"_digest_([A-Za-z0-9][A-Za-z0-9_\-]*)", text):
            slug = m.group(1)
            sources.setdefault(slug, _norm(slug))
    return sources


_ANCHOR_HEADING = re.compile(r"^#{1,6}\s*Canon\s+Anchors\s*$", re.IGNORECASE)
_ANY_HEADING = re.compile(r"^#{1,6}\s+\S")
# A contract still carrying its template placeholder for anchors is "unfilled".
_PLACEHOLDER = re.compile(r"\{[A-Z_]+\}")


def extract_canon_anchor_block(contract_text):
    """Return the raw text of the `## Canon Anchors` section, or None if the
    heading is absent."""
    lines = contract_text.splitlines()
    out = []
    capturing = False
    for line in lines:
        if _ANCHOR_HEADING.match(line.strip()):
            capturing = True
            continue
        if capturing:
            # A new heading of any level ends the section.
            if _ANY_HEADING.match(line):
                break
            out.append(line)
    if not capturing:
        return None
    return "\n".join(out).strip()


def sources_referenced(anchor_block, sources):
    """Which corpus slugs are named in this anchor block."""
    if not anchor_block:
        return set()
    hay = _norm(anchor_block)
    hit = set()
    for slug, token in sources.items():
        if token and token in hay:
            hit.add(slug)
    return hit


def unit_ids_from_config(cfg):
    """Ordered unit ids from book_config.units, if declared."""
    ids = []
    for u in (cfg or {}).get("units", []) or []:
        uid = u.get("id") if isinstance(u, dict) else None
        if uid:
            ids.append(uid)
    return ids


def collect_contracts(root, cfg):
    """Return ordered [(unit_id, Path)] for existing contracts.
    Prefer the config's declared unit order; fall back to sorted files."""
    cdir = root / "contracts"
    if not cdir.is_dir():
        return []
    ordered = unit_ids_from_config(cfg)
    result = []
    seen = set()
    for uid in ordered:
        p = cdir / f"{uid}.md"
        if p.is_file():
            result.append((uid, p))
            seen.add(p.name)
    for p in sorted(cdir.glob("*.md")):
        # Skip templates and already-collected ids.
        if p.name in seen:
            continue
        if p.stem.startswith("_") or p.stem.upper().startswith("TEMPLATE"):
            continue
        result.append((p.stem, p))
    return result


def analyze(root, cfg, mode, strict):
    """Return (rows, meta). meta carries corpus size + applicability."""
    sources = discover_sources(root)
    contracts = collect_contracts(root, cfg)
    fail_modes = FAIL_MODES_STRICT if strict else FAIL_MODES_DEFAULT
    mode_fails = mode in fail_modes

    rows = []
    meta = {
        "integration_mode": mode,
        "source_count": len(sources),
        "sources": sorted(sources.keys()),
        "contracts_found": len(contracts),
        "applicable": True,
        "reason": "",
        "mode_fails_on_tell": mode_fails,
        "strict": strict,
    }

    # Not applicable when the corpus can't produce a 1:1 tell.
    if len(sources) < 2:
        meta["applicable"] = False
        meta["reason"] = (
            f"corpus has {len(sources)} satellite source(s) (<2): a 1:1 "
            "unit->source mapping is not meaningful. Populate "
            "canon_refs/_digest_<slug>.md per satellite to enable the gate."
        )
        return rows, meta
    if not contracts:
        meta["applicable"] = False
        meta["reason"] = (
            "no unit contracts found under contracts/ -- nothing to check."
        )
        return rows, meta

    for uid, path in contracts:
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except Exception as exc:
            rows.append(Row(uid, SKIP, set(),
                            f"could not read contract ({exc.__class__.__name__})"))
            continue
        block = extract_canon_anchor_block(text)
        if block is None:
            rows.append(Row(uid, SKIP, set(),
                            "no `## Canon Anchors` section in the contract"))
            continue
        if not block or _PLACEHOLDER.search(block):
            rows.append(Row(uid, SKIP, set(),
                            "Canon Anchors unfilled (template placeholder / empty)"))
            continue
        refs = sources_referenced(block, sources)
        n = len(refs)
        if n == 0:
            # Draws only on the core (no satellite) -- not the anthology tell.
            rows.append(Row(uid, PASS, refs,
                            "no single satellite dominates (core-only draw)"))
        elif n == 1:
            only = next(iter(refs))
            status = FAIL if mode_fails else INFO
            rows.append(Row(uid, status, refs,
                            f"maps ~1:1 onto a single source '{only}' -- the "
                            "anthology tell" + ("" if mode_fails else
                            f" (allowed in {mode} mode)")))
        else:
            rows.append(Row(uid, PASS, refs,
                            f"draws on {n} sources (dissolved, not 1:1)"))
    return rows, meta


_ICON = {PASS: "[PASS]", WARN: "[WARN]", FAIL: "[FAIL]", SKIP: "[SKIP]",
         INFO: "[INFO]"}


def render_table(rows):
    if not rows:
        return "  (no per-unit rows)"
    unit_w = max(max(len(r.unit) for r in rows), len("UNIT"))
    lines = [f"  {'UNIT'.ljust(unit_w)}  STATUS  DETAIL",
             "  " + "-" * unit_w + "  ------  " + "-" * 44]
    for r in rows:
        icon = _ICON.get(r.status, "[????]")
        lines.append(f"  {r.unit.ljust(unit_w)}  {icon}  {r.detail}")
    return "\n".join(lines)


def render_verdict(rows, meta):
    out = ["", "=" * 66]
    mode = meta["integration_mode"]
    if not meta["applicable"]:
        out.append(f"  SYNTHESIS GATE:  N/A  (mode: {mode})")
        out.append(f"  {meta['reason']}")
        out.append("=" * 66)
        return "\n".join(out)
    fails = [r for r in rows if r.status == FAIL]
    infos = [r for r in rows if r.status == INFO]
    if fails:
        out.append(f"  SYNTHESIS GATE:  FAIL  (mode: {mode})")
        out.append(f"  {len(fails)} unit(s) map ~1:1 onto a single source "
                   "(the anthology tell):")
        for r in fails:
            out.append(f"    - {r.unit}: {sorted(r.sources)[0]}")
        out.append("  Fix: re-derive each flagged unit from the core + its "
                   "source dissolved in;")
        out.append("       recombination along source boundaries is not "
                   "synthesis (CLAUDE.md GATE-4).")
    else:
        note = ""
        if infos:
            note = f"  ({len(infos)} single-source unit(s) allowed in {mode} mode)"
        out.append(f"  SYNTHESIS GATE:  CLEAN  (mode: {mode}){note}")
        out.append(f"  {meta['source_count']} sources; "
                   f"{meta['contracts_found']} contract(s) checked; no "
                   "synthesis-mode anthology tell.")
    out.append("=" * 66)
    return "\n".join(out)


def main(argv=None):
    ap = argparse.ArgumentParser(
        prog="check_synthesis.py",
        description="BOOKSMITH GATE-4 synthesis / anthology-tell gate "
                    "(stdlib-only).")
    ap.add_argument("--config", required=True,
                    help="Path to book_config.json (drives integration_mode + "
                         "workspace slug).")
    ap.add_argument("--root",
                    help="Override the workspace root "
                         "(default: book_workspace/<slug>/).")
    ap.add_argument("--strict", action="store_true",
                    help="Also fail on the tell in anthology/reforge modes "
                         "(default: only synthesis mode fails).")
    ap.add_argument("--json", action="store_true",
                    help="Emit machine-readable JSON {meta, rows}.")
    try:
        args = ap.parse_args(argv)
    except SystemExit:
        return 2

    config_path = Path(args.config)
    if not config_path.is_absolute() and not config_path.exists():
        alt = REPO / args.config
        if alt.exists():
            config_path = alt
    if not config_path.exists():
        print(f"[ERROR] config not found: {config_path}", file=sys.stderr)
        return 2
    cfg, err = _load_json(config_path)
    if cfg is None:
        print(f"[ERROR] could not parse config {config_path}: {err}",
              file=sys.stderr)
        return 2

    mode = cfg.get("integration_mode", "synthesis") or "synthesis"
    root = workspace_root(cfg, config_path, args.root)
    if not root.exists():
        print(f"[ERROR] workspace root not found: {root}", file=sys.stderr)
        return 2

    try:
        rows, meta = analyze(root, cfg, mode, args.strict)
    except Exception as exc:
        # Absolute backstop -- a gate must never crash the pipeline.
        if args.json:
            print(json.dumps({"error": f"{exc.__class__.__name__}: {exc}",
                              "rows": [], "meta": {}}, indent=2))
        else:
            print(f"[ERROR] internal check failure "
                  f"({exc.__class__.__name__}: {exc})", file=sys.stderr)
        return 2

    if args.json:
        print(json.dumps({
            "meta": meta,
            "rows": [r.as_dict() for r in rows],
        }, indent=2))
    else:
        print()
        print(f"  BOOKSMITH synthesis gate -- {root}")
        print(f"  integration_mode: {meta['integration_mode']}  |  "
              f"sources: {meta['source_count']}  |  "
              f"contracts: {meta['contracts_found']}")
        print()
        print(render_table(rows))
        print(render_verdict(rows, meta))

    if not meta["applicable"]:
        return 0
    return 1 if any(r.status == FAIL for r in rows) else 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        sys.exit(2)
