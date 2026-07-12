#!/usr/bin/env python3
"""
selfcheck.py — the kit self-consistency meta-gate.

BOOKSMITH demands a gate after every stage of a *book*; this is the gate the kit
turns on *itself*. It answers one question mechanically: "if a stranger cloned this
folder right now, is it internally coherent and runnable?" — every Python tool
compiles, every JS tool parses, every JSON is valid, the example config validates
against the schema, kit_env and its template agree on keys, requirements.txt covers
the imports, no doc names a script that does not exist, and the vendored fonts are
present.

Portable + defensive: never tracebacks; missing node/jsonschema degrade to WARN,
not FAIL. Exit code is nonzero only on a real FAIL. `--json` emits machine output.

Usage:  python _tools/selfcheck.py [--json]
"""
from __future__ import annotations
import argparse, ast, glob, json, os, re, subprocess, sys, py_compile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TOOLS = ROOT / "_tools"

PASS, WARN, FAIL = "PASS", "WARN", "FAIL"
results: list[tuple[str, str, str]] = []


def add(name: str, status: str, detail: str = "") -> None:
    results.append((name, status, detail))


def rel(p) -> str:
    try:
        return str(Path(p).resolve().relative_to(ROOT)).replace("\\", "/")
    except Exception:
        return str(p)


# ---- 1. Python tools compile -------------------------------------------------
def check_py_compile():
    bad = []
    for f in sorted(TOOLS.glob("*.py")):
        if f.name.startswith("_"):  # scratch/helper scripts are not shipped gates
            continue
        try:
            py_compile.compile(str(f), doraise=True)
        except py_compile.PyCompileError as e:
            bad.append(f"{f.name}: {str(e).splitlines()[-1][:120]}")
    if bad:
        add("python_compiles", FAIL, "; ".join(bad))
    else:
        add("python_compiles", PASS, f"all shipped _tools/*.py compile")


# ---- 2. JS tools parse -------------------------------------------------------
def check_js_parse():
    node = _which("node")
    js = sorted(TOOLS.glob("*.js"))
    if not node:
        add("js_parses", WARN, "node not found on PATH; cannot syntax-check the JS generators")
        return
    bad = []
    for f in js:
        try:
            r = subprocess.run([node, "--check", str(f)], capture_output=True, text=True, timeout=30)
            if r.returncode != 0:
                bad.append(f"{f.name}: {(r.stderr or r.stdout).strip().splitlines()[-1][:120]}")
        except Exception as e:
            bad.append(f"{f.name}: {e}")
    add("js_parses", FAIL if bad else PASS, "; ".join(bad) if bad else f"all {len(js)} _tools/*.js pass node --check")


# ---- 3. JSON valid -----------------------------------------------------------
def check_json_valid():
    bad = []
    targets = list(TOOLS.glob("*.json")) + list((TOOLS / "workflows").glob("*.json"))
    for f in targets:
        try:
            json.load(open(f, encoding="utf-8"))
        except Exception as e:
            bad.append(f"{rel(f)}: {str(e)[:100]}")
    add("json_valid", FAIL if bad else PASS, "; ".join(bad) if bad else f"all {len(targets)} json parse")


# ---- 4. example config validates against schema ------------------------------
def check_schema():
    schema_p = TOOLS / "book_config.schema.json"
    ex_p = TOOLS / "book_config.example.json"
    if not schema_p.exists() or not ex_p.exists():
        add("config_schema_valid", FAIL, "schema or example missing")
        return
    try:
        import jsonschema
    except Exception:
        add("config_schema_valid", WARN, "jsonschema not installed; skipped (pip install jsonschema)")
        return
    try:
        schema = json.load(open(schema_p, encoding="utf-8"))
        ex = json.load(open(ex_p, encoding="utf-8"))
        jsonschema.validate(ex, schema)
        add("config_schema_valid", PASS, "book_config.example.json validates against schema")
    except Exception as e:
        add("config_schema_valid", FAIL, str(e).splitlines()[0][:160])


# ---- 5. kit_env vs template key parity ---------------------------------------
def _keys(d, prefix=""):
    out = set()
    if isinstance(d, dict):
        for k, v in d.items():
            if k.startswith("_"):
                continue
            kp = f"{prefix}.{k}" if prefix else k
            out.add(kp)
            out |= _keys(v, kp)
    return out


def check_kit_env_parity():
    live = TOOLS / "kit_env.json"
    tmpl = TOOLS / "kit_env.template.json"
    if not tmpl.exists():
        add("kit_env_parity", WARN, "kit_env.template.json missing")
        return
    try:
        lk = _keys(json.load(open(live, encoding="utf-8"))) if live.exists() else set()
        tk = _keys(json.load(open(tmpl, encoding="utf-8")))
    except Exception as e:
        add("kit_env_parity", FAIL, f"parse error: {e}")
        return
    live_only = sorted(lk - tk)
    tmpl_only = sorted(tk - lk)
    if live_only or tmpl_only:
        add("kit_env_parity", WARN, f"live-only={live_only} template-only={tmpl_only}")
    else:
        add("kit_env_parity", PASS, "kit_env.json and template share all (non-doc) keys")


# ---- 6. requirements.txt covers imports --------------------------------------
STDLIB = set(getattr(sys, "stdlib_module_names", set())) | {
    "__future__", "typing", "dataclasses", "pathlib", "subprocess", "argparse",
}
# import-name -> pip distribution (normalized lowercase) it comes from
IMPORT_TO_DIST = {
    "PIL": "pillow", "fitz": "pymupdf", "win32com": "pywin32", "win32api": "pywin32",
    "win32": "pywin32", "pythoncom": "pywin32", "pywintypes": "pywin32",
    "jsonschema": "jsonschema", "tiktoken": "tiktoken", "requests": "requests",
    "pypdf": "pypdf", "PyPDF2": "pypdf2", "docx": "python-docx", "yaml": "pyyaml",
    "numpy": "numpy", "pypdfium2": "pypdfium2",
}


def check_requirements():
    req_p = ROOT / "requirements.txt"
    if not req_p.exists():
        add("requirements_cover_imports", WARN, "requirements.txt missing")
        return
    req = req_p.read_text(encoding="utf-8")
    declared = set(re.findall(r"^[ \t]*([A-Za-z0-9_.\-]+)", req, re.M))
    declared = {d.lower().replace("_", "-") for d in declared}
    local = {f.stem for f in TOOLS.glob("*.py")}
    # guarded try/except fallbacks that are intentionally NOT pinned in requirements
    optional_fallback = {"PyPDF2"}
    third = set()
    for f in TOOLS.glob("*.py"):
        if f.name.startswith("_"):
            continue
        try:
            tree = ast.parse(f.read_text(encoding="utf-8"))
        except Exception:
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for n in node.names:
                    third.add(n.name.split(".")[0])
            elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
                third.add(node.module.split(".")[0])
    missing = []
    for mod in sorted(third):
        if mod in STDLIB or mod in local or mod.startswith("_") or mod in optional_fallback:
            continue
        dist = IMPORT_TO_DIST.get(mod, mod).lower().replace("_", "-")
        if dist not in declared:
            missing.append(f"{mod}->{dist}")
    if missing:
        add("requirements_cover_imports", WARN, f"imports not clearly in requirements.txt: {missing}")
    else:
        add("requirements_cover_imports", PASS, "every third-party import maps to a declared dependency")


# ---- 7. no doc names a missing script ----------------------------------------
def check_dead_script_refs():
    # PORTABILITY_GAP_ANALYSIS.md is a roadmap: it names tools that are future work
    # by design, so it is excluded from the "must already exist" scan.
    ROADMAP = {"PORTABILITY_GAP_ANALYSIS.md"}
    docs = [ROOT / "CLAUDE.md", ROOT / "KIT_ARCHITECTURE.md", ROOT / "README.md",
            ROOT / "START_HERE.md", ROOT / "INSTALL.md"]
    docs += [d for d in (ROOT / "docs").glob("*.md") if d.name not in ROADMAP]
    # trailing boundary so `.json` is never mis-read as `.js`
    pat = re.compile(r"_tools/([A-Za-z0-9_]+\.(?:py|js|json))(?![A-Za-z0-9])")
    missing = {}
    for doc in docs:
        if not doc.exists():
            continue
        for m in pat.finditer(doc.read_text(encoding="utf-8", errors="ignore")):
            script = m.group(1)
            if not (TOOLS / script).exists():
                missing.setdefault(script, set()).add(rel(doc))
    if missing:
        detail = "; ".join(f"{k} (cited in {sorted(v)})" for k, v in sorted(missing.items()))
        add("no_dead_script_refs", FAIL, detail)
    else:
        add("no_dead_script_refs", PASS, "every _tools/<script> named in docs exists")


# ---- 8. vendored fonts present -----------------------------------------------
def check_fonts():
    fonts = ROOT / "fonts"
    needed = ["CormorantGaramond-Light.ttf", "CormorantGaramond-Bold.ttf"]
    have = {p.name for p in fonts.glob("*.ttf")} if fonts.exists() else set()
    miss = [n for n in needed if n not in have]
    n_ttf = len(list(fonts.rglob("*.ttf"))) if fonts.exists() else 0
    if miss:
        add("fonts_vendored", FAIL, f"missing core faces: {miss}")
    else:
        add("fonts_vendored", PASS, f"core Cormorant faces present ({n_ttf} ttf total under fonts/)")


def _which(exe):
    from shutil import which
    return which(exe)


def main():
    ap = argparse.ArgumentParser(description="BOOKSMITH kit self-consistency meta-gate")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    for fn in (check_py_compile, check_js_parse, check_json_valid, check_schema,
               check_kit_env_parity, check_requirements, check_dead_script_refs, check_fonts):
        try:
            fn()
        except Exception as e:
            add(fn.__name__, FAIL, f"checker crashed: {e}")

    n_fail = sum(1 for _, s, _ in results if s == FAIL)
    n_warn = sum(1 for _, s, _ in results if s == WARN)

    if args.json:
        print(json.dumps({
            "all_pass": n_fail == 0,
            "fails": n_fail, "warns": n_warn,
            "checks": [{"name": n, "status": s, "detail": d} for n, s, d in results],
        }, indent=2))
    else:
        print("=== BOOKSMITH kit self-check ===")
        for n, s, d in results:
            mark = {"PASS": "OK ", "WARN": "!! ", "FAIL": "XX "}[s]
            print(f"  {mark}{n:28} {s}  {d}")
        verdict = "FAIL" if n_fail else ("WARN" if n_warn else "PASS")
        print(f"--- verdict: {verdict}  ({n_fail} fail, {n_warn} warn) ---")
    return 1 if n_fail else 0


if __name__ == "__main__":
    sys.exit(main())
