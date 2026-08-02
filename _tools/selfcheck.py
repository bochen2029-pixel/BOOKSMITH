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
    if not live.exists():
        add("kit_env_parity", PASS,
            "kit_env.json not created yet; copy kit_env.template.json to kit_env.json "
            "and edit for your machine (key parity is enforced once it exists)")
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
    "opencc": "opencc-python-reimplemented",
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
    ROADMAP = {"PORTABILITY_GAP_ANALYSIS.md", "ROADMAP.md"}
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
            if script == "kit_env.json":
                continue  # user-created from kit_env.template.json; absent in a fresh clone by design
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


# ---- 9. config keys the toolchain READS are declared in the schema -----------
# additionalProperties:false means an undeclared-but-read key is a feature NO
# valid config can ever use (the H1/H2/VER-4 gate-hole class) — at the root AND
# equally inside every nested block that pins it (voice/interior/spine/cover/
# art/...). Include-list of the book-config consumers; kit_env/infra tools are
# out of scope.
_BOOKCFG_PY = [
    "assemble_manuscript.py", "build_epub.py", "build_digital_pdf.py",
    "lint_manuscript.py", "verify_build.py", "check_part_pages.py",
    "composite_cover.py", "cover_gen.py", "cover_pick.py", "cover_layout.py",
    "palette_transfer.py", "init_contracts.py", "engine.py", "authorial_act.py",
    "check_synthesis.py", "check_continuity.py",
]
_BOOKCFG_JS = ["generate_book.js", "generate_kindle.js"]
# keys read dynamically for legit non-schema reasons (none today; add sparingly);
# a nested key goes in as its dotted path ("voice.some_key")
_CFGKEY_ALLOW: set = set()


def _schema_blocks(schema: dict) -> dict:
    """Property name -> union of declared keys, for every object subschema below
    the root that pins additionalProperties:false. Keyed by property NAME because
    that is the toolchain's binding convention (voice = cfg.get("voice", {});
    art = cover.get("art", {})); same-named blocks at different depths union."""
    out: dict = {}

    def walk(name, node):
        if not isinstance(node, dict):
            return
        props = node.get("properties")
        if isinstance(props, dict):
            if name and node.get("additionalProperties") is False:
                out.setdefault(name, set()).update(props.keys())
            for k, v in props.items():
                walk(k, v)
        walk(None, node.get("items"))  # arrays bind to loop vars, never block names
    for k, v in schema.get("properties", {}).items():
        walk(k, v)
    return out


def check_config_key_drift():
    schema_p = TOOLS / "book_config.schema.json"
    try:
        schema = json.load(open(schema_p, encoding="utf-8"))
        declared = set(schema["properties"].keys())
    except Exception as e:
        add("config_keys_declared", FAIL, f"cannot read schema properties: {e}")
        return
    # cf61c7e (caught at the 2026-07-28 round table) is why the NESTED scan
    # exists: lint_manuscript.py shipped reading voice.get("lint_waivers") while
    # the schema's voice block never declared it — the waiver feature was
    # unreachable by ANY schema-valid config (GATE-2 rejects a config that
    # carries it), and the receiver regex here never saw the read because it
    # hangs off a local named `voice`, not cfg/config/book_config. Nested reads
    # are therefore checked three ways:
    #   1. Python block-name locals — voice.get("k") / spine["k"] /
    #      voice.setdefault("k"). Deliberately unfenced: on this tree every such
    #      local IS the config block, and the PIL images / Paths that reuse the
    #      names `art`/`cover` never take quoted string keys.
    #   2. Python same-line chains — cfg.get("voice", {}).get("k"), any receiver
    #      (cover_gen's `(config.get("cover") or {}).get("art")` included).
    #   3. JS config.a.b.c chains walked segment-by-segment against the schema
    #      tree (stopping at arrays and open blocks like cover.palette), plus
    #      dotted reads off alias-bound locals (const interior = config.interior
    #      || {}) and destructured forms. JS bare reads MUST stay alias-gated:
    #      generate_kindle.js has a param named `art` that carries
    #      interior.chapter_art, not cover.art — ungated, art.dir false-fails.
    blocks = _schema_blocks(schema)
    names_alt = "|".join(sorted(blocks))
    py_root_pat = re.compile(
        r"\b(?:self\.)?(?:cfg|config|book_config)(?:\.get\(\s*|\[)\s*[\"']([a-z_][a-z0-9_]*)[\"']")
    py_block_pat = re.compile(
        rf"\b({names_alt})(?:\.get\(\s*|\.setdefault\(\s*|\[\s*)[\"']([a-z_][a-z0-9_]*)[\"']")
    py_chain_pat = re.compile(
        rf"\.get\(\s*[\"']({names_alt})[\"'][^)]*\)[ \t]*(?:or[ \t]+\{{\}}[ \t]*)?\)?"
        rf"[ \t]*(?:\.get\(\s*|\[\s*)[\"']([a-z_][a-z0-9_]*)[\"']")
    js_chain_pat = re.compile(r"\bconfig((?:\??\.[a-z_][a-z0-9_]*)+)")
    js_alias_pat = re.compile(rf"\b(?:const|let|var)\s+({names_alt})\s*=\s*\(?\s*config\.\1\b")
    js_destr_pat = re.compile(rf"\{{([^{{}}]*)\}}\s*=\s*\(?\s*config\.({names_alt})\b")
    js_skip = {"get", "slug"}  # attribute noise; slug obviously declared anyway
    offenders = {}

    def flag(path, fname):
        if path not in _CFGKEY_ALLOW:
            offenders.setdefault(path, set()).add(fname)

    def walk_js_chain(segs, fname):
        node = {"properties": schema.get("properties", {}), "additionalProperties": False}
        for depth, seg in enumerate(segs):
            props = node.get("properties") if isinstance(node, dict) else None
            if not isinstance(props, dict) or node.get("additionalProperties") is not False:
                return  # array / open block / scalar: cannot judge deeper segments
            if depth == 0 and seg in js_skip:
                return
            if seg not in props:
                flag(".".join(segs[:depth + 1]), fname)
                return
            node = props[seg]

    for name in _BOOKCFG_PY:
        f = TOOLS / name
        if not f.exists():
            continue
        src = f.read_text(encoding="utf-8", errors="replace")
        for m in py_root_pat.finditer(src):
            if m.group(1) not in declared:
                flag(m.group(1), name)
        for pat in (py_block_pat, py_chain_pat):
            for m in pat.finditer(src):
                b, k = m.group(1), m.group(2)
                if k not in blocks[b]:
                    flag(f"{b}.{k}", name)
    for name in _BOOKCFG_JS:
        f = TOOLS / name
        if not f.exists():
            continue
        src = f.read_text(encoding="utf-8", errors="replace")
        for m in js_chain_pat.finditer(src):
            walk_js_chain([s for s in m.group(1).replace("?.", ".").split(".") if s], name)
        for b in set(js_alias_pat.findall(src)):
            for m in re.finditer(rf"\b{b}\.([a-z_][a-z0-9_]*)\b", src):
                if m.group(1) not in blocks[b]:
                    flag(f"{b}.{m.group(1)}", name)
        for m in js_destr_pat.finditer(src):
            b = m.group(2)
            for part in m.group(1).split(","):
                if part.strip().startswith("..."):
                    continue  # rest-spread catch-all, not a key read
                ident = part.split(":")[0].split("=")[0].strip()
                if re.fullmatch(r"[a-z_][a-z0-9_]*", ident) and ident not in blocks[b]:
                    flag(f"{b}.{ident}", name)
    if offenders:
        detail = "; ".join(f"{k} (read by {sorted(v)})" for k, v in sorted(offenders.items()))
        add("config_keys_declared", FAIL,
            f"read-but-undeclared config key(s): {detail} — a valid config "
            f"cannot carry them (additionalProperties:false at that level)")
    else:
        add("config_keys_declared", PASS,
            f"every config key read by {len(_BOOKCFG_PY) + len(_BOOKCFG_JS)} toolchain "
            f"files is schema-declared (root + {len(blocks)} nested blocks)")


# ---- 10. every shipped tool is documented; format/profile tokens in the spec --
def check_doc_coverage():
    corpus_files = [ROOT / "CLAUDE.md", ROOT / "KIT_ARCHITECTURE.md", ROOT / "README.md",
                    ROOT / "START_HERE.md", ROOT / "START_A_BOOK.md", ROOT / "INSTALL.md",
                    ROOT / "AGENTS.md"] + list((ROOT / "docs").glob("*.md"))
    corpus = "\n".join(p.read_text(encoding="utf-8", errors="ignore")
                       for p in corpus_files if p.exists())
    undocumented = []
    for f in sorted(list(TOOLS.glob("*.py")) + list(TOOLS.glob("*.js"))):
        if f.name.startswith("_"):
            continue
        if f.name not in corpus:
            undocumented.append(f.name)
    problems = []
    if undocumented:
        problems.append(f"tool(s) documented NOWHERE: {undocumented}")
    # token sets: the invariant spec must carry the real format/profile tokens
    kit_arch = (ROOT / "KIT_ARCHITECTURE.md").read_text(encoding="utf-8", errors="ignore")
    gb = (TOOLS / "generate_book.js").read_text(encoding="utf-8", errors="replace")
    m = re.search(r"VALID_FORMATS\s*=\s*\[([^\]]+)\]", gb)
    fmts = re.findall(r'"([a-z_]+)"', m.group(1)) if m else []
    missing_fmt = [t for t in fmts if t not in kit_arch]
    cc = (TOOLS / "composite_cover.py").read_text(encoding="utf-8", errors="replace")
    m2 = re.search(r"choices=\[([^\]]+)\]", cc)
    profs = re.findall(r'"([a-z0-9\-]+)"', m2.group(1)) if m2 else []
    missing_prof = [t for t in profs if t not in kit_arch]
    if missing_fmt:
        problems.append(f"format token(s) absent from KIT_ARCHITECTURE.md: {missing_fmt}")
    if missing_prof:
        problems.append(f"profile token(s) absent from KIT_ARCHITECTURE.md: {missing_prof}")
    if problems:
        add("doc_coverage", FAIL, "; ".join(problems))
    else:
        add("doc_coverage", PASS,
            f"every shipped tool is named in the docs; all {len(fmts)} format + "
            f"{len(profs)} profile tokens present in the invariant spec")


# ---- 11. no em/en dash in JS STRING content (rendered-character guard) --------
_DASH_SET = "—–―‒−"


def check_js_dash_literals():
    hits = []
    for f in sorted(TOOLS.glob("*.js")):
        src = f.read_text(encoding="utf-8", errors="replace")
        src = re.sub(r"/\*.*?\*/", "", src, flags=re.S)      # block comments
        for i, line in enumerate(src.splitlines(), 1):
            code = line.split("//", 1)[0]                     # line comments
            if re.search(r"console\.(log|warn|error)", code):
                continue                                      # console text never renders
            if "const USAGE" in code:
                continue                                      # CLI help header, never renders
            if re.search(r"\[[^\]]*[—–][^\]]*\]", code):
                continue                                      # regex char-class STRIPPING dashes
            if "no_em_dashes === false" in code:
                continue                                      # voice-gated: only when allowed
            if any(ch in code for ch in _DASH_SET):
                hits.append(f"{f.name}:{i}")
    if hits:
        add("js_no_dash_literals", FAIL,
            f"em/en dash in JS code (a generator-injected dash ships into the "
            f"artifact and the source lint can never see it): {hits[:6]}")
    else:
        add("js_no_dash_literals", PASS,
            "no em/en dash in any JS string/code line (comments + console text exempt)")


# ---- 12. spine/geometry constants agree: schema <-> compositor <-> verifier ---
def check_spine_constant_parity():
    schema_p = TOOLS / "book_config.schema.json"
    try:
        spine_props = (json.load(open(schema_p, encoding="utf-8"))
                       ["properties"]["spine"]["properties"])
    except Exception as e:
        add("spine_constant_parity", WARN, f"cannot read spine schema block: {e}")
        return
    cc = (TOOLS / "composite_cover.py").read_text(encoding="utf-8", errors="replace")
    vb = (TOOLS / "verify_build.py").read_text(encoding="utf-8", errors="replace")
    pl = (TOOLS / "preset_lookup.py").read_text(encoding="utf-8", errors="replace")
    bad = []
    for key, prop in spine_props.items():
        v = prop.get("default")
        if not isinstance(v, (int, float)):
            continue
        forms = {str(v), f"{v:g}", f"{v:.2f}", f"{v:.3f}", f"{v:.4f}", f"{v:.6f}"}
        in_cc = any(s in cc for s in forms)
        in_check = any(s in vb for s in forms) or any(s in pl for s in forms)
        if not (in_cc and in_check):
            bad.append(f"{key}={v} (compositor={'y' if in_cc else 'MISSING'}, "
                       f"verifier/preset={'y' if in_check else 'MISSING'})")
    if bad:
        add("spine_constant_parity", FAIL,
            "schema spine default(s) not mirrored in code fallbacks: " + "; ".join(bad))
    else:
        add("spine_constant_parity", PASS,
            f"all {len(spine_props)} schema spine defaults mirrored in "
            f"compositor AND verifier/preset fallbacks")


# ---- 13. produce_book error propagation --------------------------------------
def check_produce_book_selftest():
    """A failed step must abort that format's chain, flip green:false, exit 1
    (dry-run + injected failure; runs no node/Word)."""
    try:
        r = subprocess.run([sys.executable, str(TOOLS / "produce_book.py"), "--selftest"],
                           capture_output=True, text=True, timeout=120)
    except Exception as e:
        add("produce_book_selftest", FAIL, f"could not run --selftest: {e}")
        return
    tail = [l for l in (r.stdout or "").splitlines() if l.strip()]
    add("produce_book_selftest", PASS if r.returncode == 0 else FAIL,
        (tail[-1].strip() if tail else f"rc={r.returncode}")[:120])


# ---- 14. KDP acceptance simulator negative battery ---------------------------
def check_kdp_precheck_selftest():
    """kdp_precheck.py must FAIL tampered artifacts (off-trim page, wrong cover
    canvas, out-of-range page count) — a gate that cannot fail is not a gate."""
    try:
        r = subprocess.run([sys.executable, str(TOOLS / "kdp_precheck.py"), "--selftest"],
                           capture_output=True, text=True, timeout=120)
    except Exception as e:
        add("kdp_precheck_selftest", FAIL, f"could not run --selftest: {e}")
        return
    head = [l for l in (r.stdout or "").splitlines() if l.strip()]
    add("kdp_precheck_selftest", PASS if r.returncode == 0 else FAIL,
        (head[0].strip() if head else f"rc={r.returncode}")[:120])


# ---- 15. Image generation is a held, discoverable, autonomous capability -----
def check_verify_build_selftest():
    """verify_build.py --selftest must hold: the provenance gate's must-fail
    fixture battery (tampered sidecars REJECTED, sha-bound good inputs PASS).
    A gate never shown to fail is indistinguishable from `return PASS`
    (INVARIANT T, REMEDIATION_PLAN_v2 §2)."""
    try:
        r = subprocess.run([sys.executable, str(TOOLS / "verify_build.py"), "--selftest"],
                           capture_output=True, text=True, timeout=180)
    except Exception as e:
        add("verify_build_selftest", FAIL, f"could not run --selftest: {e}")
        return
    tail = [l for l in (r.stdout or "").splitlines() if l.strip()]
    add("verify_build_selftest", PASS if r.returncode == 0 else FAIL,
        (tail[-1].strip() if tail else f"rc={r.returncode}")[:120])


def check_image_gen_capability():
    """Local ComfyUI image generation must stay AUTONOMOUS and DISCOVERABLE.

    For months the kit could not cold-start ComfyUI, silently fell back to
    placeholder art, and no session knew the capability existed — the capability
    was 'held' only by prose in a session log. This check binds it to a gate.

    FAIL = the KIT forgot (a doc or the call convention rotted).
    WARN = THIS MACHINE is unprovisioned (paths/checkpoint) — not a kit defect.
    """
    name = "image_gen_capability"
    problems, warns = [], []

    # (a) the authoritative doc must exist
    doc = ROOT / "docs" / "IMAGE_GENERATION.md"
    if not doc.is_file():
        problems.append("docs/IMAGE_GENERATION.md missing")

    # (b) CLAUDE.md must carry the standing declaration, so no session can boot
    #     without learning it (CLAUDE.md is read in full every session).
    claude = ROOT / "CLAUDE.md"
    if claude.is_file():
        txt = claude.read_text(encoding="utf-8", errors="replace")
        if "STANDING CAPABILITY" not in txt or "IMAGE_GENERATION.md" not in txt:
            problems.append("CLAUDE.md lost the STANDING CAPABILITY image-gen block")
    else:
        problems.append("CLAUDE.md missing")

    # (c) THE REGRESSION GUARD. launch_server() returns False before the only
    #     working launch strategy when handed anything but the paths dict.
    #     Passing paths["server"] made the cold-start dead code for months.
    cg = TOOLS / "cover_gen.py"
    if cg.is_file():
        src = cg.read_text(encoding="utf-8", errors="replace")
        bad = len(re.findall(r'launch_server\(\s*paths\[', src))
        good = len(re.findall(r'launch_server\(\s*paths\s*\)', src))
        if bad:
            problems.append(f"cover_gen.py passes a STRING to launch_server() at "
                            f"{bad} site(s): Desktop cold-start is unreachable; "
                            f"pass the paths DICT")
        if not good:
            problems.append("cover_gen.py never calls launch_server(paths)")
    else:
        problems.append("_tools/cover_gen.py missing")

    # (d) does the launch actually resolve on THIS box? (machine, not kit)
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location("_cg_probe", cg)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        paths = mod._resolve_cover_gen_paths(mod.load_kit_env(None))
        py, main_py, _base, _extra = mod._resolve_comfy_launch(paths)
        if not (py and os.path.exists(py) and main_py and os.path.exists(main_py)):
            warns.append("ComfyUI launch paths do not resolve on this machine "
                         "(kit_env.cover_gen: comfyui_app / checkpoints_dir)")
        ckpt_dir = paths.get("checkpoints_dir")
        ckpt = paths.get("default_checkpoint")
        if ckpt_dir and ckpt and not (Path(ckpt_dir) / ckpt).is_file():
            warns.append(f"checkpoint {ckpt} not in checkpoints_dir — fetch it "
                         f"(url+sha256 in kit_env.cover_gen)")
    except Exception as e:                                        # noqa: BLE001
        warns.append(f"could not probe the launch path: {type(e).__name__}: {e}")

    if problems:
        add(name, FAIL, "; ".join(problems)[:220])
    elif warns:
        add(name, WARN, "kit contract OK; machine: " + "; ".join(warns)[:180])
    else:
        add(name, PASS, "local ComfyUI auto-launch held, documented, and "
                        "discoverable from CLAUDE.md")


def main():
    ap = argparse.ArgumentParser(description="BOOKSMITH kit self-consistency meta-gate")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    for fn in (check_py_compile, check_js_parse, check_json_valid, check_schema,
               check_kit_env_parity, check_requirements, check_dead_script_refs, check_fonts,
               check_config_key_drift, check_doc_coverage, check_js_dash_literals,
               check_spine_constant_parity, check_produce_book_selftest,
               check_kdp_precheck_selftest, check_verify_build_selftest,
               check_image_gen_capability):
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
