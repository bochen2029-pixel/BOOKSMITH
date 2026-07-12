#!/usr/bin/env python3
"""
doctor.py -- BOOKSMITH preflight / capability checker.

PURPOSE
    A stranger drops the BOOKSMITH kit onto a fresh desktop, runs
        python _tools/doctor.py
    and learns -- BEFORE any mid-run crash -- exactly what works, what is
    missing, and the one concrete action that fixes each gap. It probes the
    third-party runtime (pip packages, Word COM, Node + vendored modules,
    fonts, optional AI/vision add-ons) and prints an aligned table plus a
    TIER VERDICT, then exits with a code the harness can branch on.

    This tool is diagnostic only. It never writes to the tree, never installs
    anything, and NEVER raises an unhandled traceback -- every probe is wrapped
    so a missing dependency becomes a WARN/FAIL row, not a crash.

CAPABILITY TIERS (from the portability audit)
    TIER 1 (full print)  = Windows + Microsoft Word COM. Unlocks the print-PDF
                           pipeline (docx -> PDF, page-count, recto parity).
    TIER 2 (degraded)    = no Word -> still useful: EPUB (pure stdlib), Kindle
                           DOCX (Node), cover COMPOSITING from user-supplied art
                           (PIL + fitz), Claude-vision verification.
    NOT READY            = a hard dependency for even Tier 2 is missing.
    Optional add-ons on any tier: local AI cover art (ComfyUI + GPU), local
    vision (KEEL llama-server). Their absence never lowers the tier.

USAGE
    python _tools/doctor.py                 # human table + tier verdict
    python _tools/doctor.py --json          # machine-readable {checks,tier}
    python _tools/doctor.py --config book_workspace/<slug>/book_config.json
                                            # probe THAT book's body font
    python _tools/doctor.py --smoke         # END-TO-END pipeline smoke test:
                                            # drives the testvoyage fixture through
                                            # assemble -> generate_kindle ->
                                            # verify_build and asserts word-count
                                            # parity (a standing regression gate).
                                            # Exit 0 = pass, 1 = fail.
    Exit codes (preflight): 0 = Tier 1 or Tier 2 achievable
                            1 = NOT READY
                            2 = usage error
    Exit codes (--smoke):   0 = pipeline pass, 1 = pipeline fail

PROVENANCE
    Built 2026-07-11 from the BOOKSMITH portability audit (4-agent sweep).
    Pure Python standard library -- runs with zero pip installs, on
    Windows / macOS / Linux. Windows-only probes report "n/a (not Windows)"
    elsewhere. Repo root is derived from this file's location, never cwd,
    never a hard-coded C:\\BOOKSMITH.
"""

import argparse
import json
import os
import platform
import shutil
import subprocess
import sys
import urllib.request
from pathlib import Path

# ---------------------------------------------------------------------------
# Repo root: this file lives in <repo>/_tools/doctor.py -> parent.parent.
# ---------------------------------------------------------------------------
REPO = Path(__file__).resolve().parent.parent
TOOLS = REPO / "_tools"

PASS, WARN, FAIL, SKIP, INFO = "PASS", "WARN", "FAIL", "SKIP", "INFO"

# Status precedence for the tier verdict. INFO/SKIP never lower a tier.
IS_WINDOWS = platform.system() == "Windows"


class Check:
    """One diagnostic row."""
    __slots__ = ("name", "status", "detail", "remedy")

    def __init__(self, name, status, detail="", remedy=""):
        self.name = name
        self.status = status
        self.detail = detail
        self.remedy = remedy

    def as_dict(self):
        return {
            "name": self.name,
            "status": self.status,
            "detail": self.detail,
            "remedy": self.remedy,
        }


def _try_import(modname):
    """Return (ok, version_or_error). Never raises."""
    import warnings
    try:
        mod = __import__(modname)
        # Some packages (e.g. jsonschema) emit a DeprecationWarning merely on
        # __version__ access; a preflight tool should stay quiet, so suppress.
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            ver = getattr(mod, "__version__", "") or getattr(mod, "VERSION", "")
        return True, str(ver)
    except Exception as exc:  # ImportError and any import-time side effects
        return False, exc.__class__.__name__


def _load_json(path):
    try:
        with open(path, "r", encoding="utf-8") as fh:
            return json.load(fh), None
    except Exception as exc:
        return None, f"{exc.__class__.__name__}: {exc}"


# ---------------------------------------------------------------------------
# (a) Python version
# ---------------------------------------------------------------------------
def check_python():
    v = sys.version_info
    vs = f"{v.major}.{v.minor}.{v.micro}"
    if (v.major, v.minor) >= (3, 10):
        return Check("Python runtime", PASS, f"Python {vs} ({platform.system()})",
                     "")
    return Check("Python runtime", FAIL, f"Python {vs} is below 3.10",
                 "install Python 3.10+ and re-run with it on PATH")


# ---------------------------------------------------------------------------
# (b) pip deps
# ---------------------------------------------------------------------------
def check_pip_deps():
    checks = []
    # Required-for-covers/digital trio.
    required = [
        ("PIL", "Pillow", "cover compositing + font rendering"),
        ("fitz", "PyMuPDF", "exact-inch PDF MediaBox for covers + digital PDF"),
    ]
    for mod, pip_name, unlocks in required:
        ok, info = _try_import(mod)
        if ok:
            ver = f" {info}" if info else ""
            checks.append(Check(f"pip: {pip_name}", PASS,
                                f"import {mod} ok{ver} -- {unlocks}", ""))
        else:
            checks.append(Check(f"pip: {pip_name}", FAIL,
                                f"cannot import {mod} ({info}) -- {unlocks} disabled",
                                f"pip install {pip_name}"))
    # digital PDF concatenation: pypdf (preferred) or the EOL PyPDF2 (accepted fallback)
    pok, pinfo = _try_import("pypdf")
    if pok:
        checks.append(Check("pip: pypdf", PASS,
                            f"import pypdf ok {pinfo} -- digital PDF page concatenation", ""))
    else:
        lok, linfo = _try_import("PyPDF2")
        if lok:
            checks.append(Check("pip: pypdf", PASS,
                                f"pypdf absent; using EOL fallback PyPDF2 {linfo} -- "
                                f"digital PDF page concatenation (pip install pypdf to modernize)", ""))
        else:
            checks.append(Check("pip: pypdf", FAIL,
                                "cannot import pypdf or PyPDF2 -- digital PDF assembly disabled",
                                "pip install pypdf"))
    # Optional -- label exactly what each unlocks.
    optional = [
        ("requests", "requests", "local KEEL vision backend (--backend keel); "
                                 "Claude vision needs nothing"),
        ("tiktoken", "tiktoken", "exact token counts in size/chunk helpers "
                                 "(a heuristic is used otherwise)"),
        ("jsonschema", "jsonschema", "book_config validation at GATE-2 "
                                     "(generate seed)"),
    ]
    for mod, pip_name, unlocks in optional:
        ok, info = _try_import(mod)
        if ok:
            ver = f" {info}" if info else ""
            checks.append(Check(f"pip: {pip_name} (opt)", PASS,
                                f"import {mod} ok{ver} -- {unlocks}", ""))
        else:
            checks.append(Check(f"pip: {pip_name} (opt)", WARN,
                                f"absent -- {unlocks}",
                                f"pip install {pip_name} (optional)"))
    return checks


# ---------------------------------------------------------------------------
# (c) pywin32 + Word COM (Tier-1 gate)
# ---------------------------------------------------------------------------
def check_word_com():
    if not IS_WINDOWS:
        return Check("Word COM (Tier 1)", WARN,
                     "n/a (not Windows) -- Tier 2 only: EPUB/Kindle/"
                     "digital-from-existing-PDF; print PDFs need Windows+Word",
                     "run on Windows with Microsoft Word for the print pipeline")
    ok, info = _try_import("win32com")
    if not ok:
        return Check("Word COM (Tier 1)", WARN,
                     f"pywin32 not importable ({info}) -- Tier 2 only: EPUB/"
                     "Kindle/digital-from-existing-PDF; print PDFs need "
                     "Windows+Word",
                     "pip install pywin32 (then Word must be installed too)")
    # pywin32 present -- try to actually dispatch Word, then Quit cleanly.
    app = None
    try:
        import win32com.client  # noqa: F401
        import pythoncom
        try:
            pythoncom.CoInitialize()
        except Exception:
            pass
        app = win32com.client.Dispatch("Word.Application")
        try:
            app.Visible = False
        except Exception:
            pass
        ver = ""
        try:
            ver = str(app.Version)
        except Exception:
            pass
        detail = f"Word.Application dispatched ok" + (f" (v{ver})" if ver else "")
        return Check("Word COM (Tier 1)", PASS,
                     detail + " -- full print pipeline unlocked", "")
    except Exception as exc:
        return Check("Word COM (Tier 1)", WARN,
                     f"Word.Application dispatch failed "
                     f"({exc.__class__.__name__}) -- Tier 2 only: EPUB/Kindle/"
                     "digital-from-existing-PDF; print PDFs need Windows+Word",
                     "install/repair Microsoft Word (the desktop COM app)")
    finally:
        if app is not None:
            try:
                app.Quit()
            except Exception:
                pass
        try:
            import pythoncom
            pythoncom.CoUninitialize()
        except Exception:
            pass


# ---------------------------------------------------------------------------
# (d) Node + vendored modules
# ---------------------------------------------------------------------------
def _run(cmd, cwd=None, timeout=15):
    """subprocess wrapper, shell=False. Returns (rc, out, err) or (None, ...)."""
    try:
        proc = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True,
                              timeout=timeout, shell=False)
        return proc.returncode, (proc.stdout or "").strip(), (proc.stderr or "").strip()
    except FileNotFoundError:
        return None, "", "not found on PATH"
    except subprocess.TimeoutExpired:
        return None, "", "timed out"
    except Exception as exc:
        return None, "", f"{exc.__class__.__name__}: {exc}"


def _parse_major(vstr):
    s = vstr.strip().lstrip("vV")
    try:
        return int(s.split(".")[0])
    except Exception:
        return None


def check_node():
    checks = []
    node_bin = shutil.which("node")
    rc, out, err = _run(["node", "--version"])
    if rc is None or not out:
        checks.append(Check("Node runtime", FAIL,
                            f"`node --version` failed ({err or 'no output'})",
                            "install Node.js >= 14 and put it on PATH "
                            "(needed for Kindle + print DOCX generators)"))
        # modules can still be reported for diagnostics
    else:
        major = _parse_major(out)
        if major is not None and major >= 14:
            loc = f" [{node_bin}]" if node_bin else ""
            checks.append(Check("Node runtime", PASS,
                                f"node {out}{loc}", ""))
        else:
            checks.append(Check("Node runtime", WARN,
                                f"node {out} is below 14",
                                "upgrade Node.js to >= 14"))
    # Vendored modules.
    nm = TOOLS / "node_modules"
    docx_dir = nm / "docx"
    jszip_dir = nm / "jszip"
    if docx_dir.is_dir() and jszip_dir.is_dir():
        checks.append(Check("Node modules (vendored)", PASS,
                            "node_modules/docx + node_modules/jszip present", ""))
        # Real smoke test only if node actually ran above.
        if rc is not None and out:
            src = "require('docx');require('jszip');console.log('ok')"
            src2, out2, err2 = _run(["node", "-e", src], cwd=str(TOOLS))
            if src2 == 0 and "ok" in out2:
                checks.append(Check("Node require() smoke test", PASS,
                                    "require('docx') + require('jszip') ok "
                                    "(cwd=_tools)", ""))
            else:
                checks.append(Check("Node require() smoke test", WARN,
                                    f"require failed ({err2 or out2 or 'unknown'})",
                                    "verify _tools/node_modules is intact "
                                    "(re-copy from the kit)"))
    else:
        missing = []
        if not docx_dir.is_dir():
            missing.append("docx")
        if not jszip_dir.is_dir():
            missing.append("jszip")
        checks.append(Check("Node modules (vendored)", FAIL,
                            f"missing under _tools/node_modules: "
                            f"{', '.join(missing)}",
                            "restore _tools/node_modules from the kit, or run "
                            "`npm install docx@9.6.1 jszip@3.10.1` inside _tools"))
    return checks


# ---------------------------------------------------------------------------
# (e) Vendored cover fonts
# ---------------------------------------------------------------------------
def check_fonts():
    checks = []
    fdir = REPO / "fonts"
    light = fdir / "CormorantGaramond-Light.ttf"
    bold = fdir / "CormorantGaramond-Bold.ttf"
    have_light, have_bold = light.is_file(), bold.is_file()
    if have_light and have_bold:
        # Render smoke test if PIL is around.
        pil_ok, _ = _try_import("PIL")
        if pil_ok:
            try:
                from PIL import ImageFont
                ImageFont.truetype(str(light), 48)
                checks.append(Check("Cover fonts (vendored)", PASS,
                                    "CormorantGaramond Light+Bold present; "
                                    "PIL truetype load ok", ""))
            except Exception as exc:
                checks.append(Check("Cover fonts (vendored)", WARN,
                                    f"fonts present but PIL failed to load "
                                    f"({exc.__class__.__name__})",
                                    "verify the .ttf files are not corrupt"))
        else:
            checks.append(Check("Cover fonts (vendored)", PASS,
                                "CormorantGaramond Light+Bold present "
                                "(PIL absent -- render smoke test skipped)", ""))
    else:
        miss = []
        if not have_light:
            miss.append("CormorantGaramond-Light.ttf")
        if not have_bold:
            miss.append("CormorantGaramond-Bold.ttf")
        checks.append(Check("Cover fonts (vendored)", FAIL,
                            f"missing in fonts/: {', '.join(miss)}",
                            "restore fonts/ from the kit (cover typography "
                            "depends on these)"))
    # OFL library count (informational).
    lib = fdir / "library"
    if lib.is_dir():
        n = len(list(lib.glob("*.ttf"))) + len(list(lib.glob("*.otf")))
        checks.append(Check("OFL font library", INFO,
                            f"{n} vendored OFL face(s) in fonts/library/", ""))
    else:
        checks.append(Check("OFL font library", INFO,
                            "fonts/library/ not present (optional interior "
                            "faces)", ""))
    return checks


# ---------------------------------------------------------------------------
# (f) Interior body-font availability in the OS
# ---------------------------------------------------------------------------
# Common filename spellings for the fonts we care about, per OS lookup.
_FONT_FILE_HINTS = {
    "georgia": ["georgia.ttf", "Georgia.ttf", "Georgia.ttc"],
    "times new roman": ["times.ttf", "Times New Roman.ttf", "Times.ttc"],
    "cambria": ["cambria.ttc", "Cambria.ttf"],
    "garamond": ["GARA.TTF", "Garamond.ttf"],
    "palatino linotype": ["pala.ttf", "Palatino Linotype.ttf"],
    "book antiqua": ["BKANT.TTF", "Book Antiqua.ttf"],
}


def _font_dirs_for_os():
    if IS_WINDOWS:
        win = os.environ.get("WINDIR", r"C:\Windows")
        local = os.environ.get("LOCALAPPDATA", "")
        dirs = [Path(win) / "Fonts"]
        if local:
            dirs.append(Path(local) / "Microsoft" / "Windows" / "Fonts")
        return dirs
    if platform.system() == "Darwin":
        home = Path.home()
        return [Path("/System/Library/Fonts"), Path("/Library/Fonts"),
                home / "Library" / "Fonts"]
    # Linux / other
    home = Path.home()
    return [Path("/usr/share/fonts"), Path("/usr/local/share/fonts"),
            home / ".fonts", home / ".local" / "share" / "fonts"]


def _font_present(font_name):
    """Best-effort: does a font matching `font_name` exist on this OS?

    Returns (found: bool, how: str)."""
    key = font_name.strip().lower()
    # 1) Vendored library (repo-relative) -- an OFL face shipped with the kit.
    lib = REPO / "fonts" / "library"
    if lib.is_dir():
        norm = key.replace(" ", "").replace("-", "")
        for f in list(lib.glob("*.ttf")) + list(lib.glob("*.otf")):
            if norm in f.stem.lower().replace(" ", "").replace("-", ""):
                return True, f"vendored fonts/library/{f.name}"
    # 2) Linux: fc-list is authoritative when available.
    if not IS_WINDOWS and platform.system() != "Darwin":
        if shutil.which("fc-list"):
            rc, out, _ = _run(["fc-list", ":", "family"], timeout=10)
            if rc == 0 and out:
                if key in out.lower():
                    return True, "fc-list"
    # 3) Filename probe in OS font dirs.
    hints = _FONT_FILE_HINTS.get(key)
    dirs = _font_dirs_for_os()
    if hints:
        for d in dirs:
            for h in hints:
                if (d / h).exists():
                    return True, f"{d / h}"
    # 4) Fallback: scan dir listings for the family token in filenames.
    token = key.replace(" ", "")
    for d in dirs:
        if not d.is_dir():
            continue
        try:
            for f in d.iterdir():
                if f.suffix.lower() in (".ttf", ".otf", ".ttc"):
                    if token in f.stem.lower().replace(" ", ""):
                        return True, f"{f}"
        except Exception:
            continue
    return False, ""


def check_interior_font(config_path):
    body_font = "Georgia"
    src = "default"
    if config_path:
        cfg, err = _load_json(config_path)
        if cfg is None:
            return [Check("Interior body font", WARN,
                          f"could not read --config ({err}); using default "
                          f"'{body_font}'",
                          "pass a valid book_config.json path")]
        body_font = (cfg.get("interior", {}) or {}).get("body_font", body_font)
        src = f"book_config"
    found, how = _font_present(body_font)
    if found:
        return [Check("Interior body font", PASS,
                      f"'{body_font}' ({src}) available via {how}", "")]
    # Not found -- this is a pagination/spine-drift risk, so WARN.
    is_ms = body_font.strip().lower() in _FONT_FILE_HINTS and body_font.strip().lower() != "garamond"
    note = ""
    if not IS_WINDOWS and body_font.strip().lower() == "georgia":
        note = " (Georgia is a Microsoft system font, absent off Windows)"
    return [Check("Interior body font", WARN,
                  f"'{body_font}' ({src}) NOT found on this OS{note} -- Word "
                  "will substitute -> pagination/spine drift",
                  "pick a vendored OFL face in book_config.interior.body_font "
                  "and install it (see fonts/library/)")]


# ---------------------------------------------------------------------------
# (g) kit_env.json + capability blocks
# ---------------------------------------------------------------------------
def _paths_exist(*paths):
    return [p for p in paths if p and Path(p).exists()]


def check_kit_env():
    checks = []
    env_path = TOOLS / "kit_env.json"
    tmpl_path = TOOLS / "kit_env.template.json"
    if not env_path.is_file():
        remedy = ("copy _tools/kit_env.template.json -> _tools/kit_env.json "
                  "and edit the machine paths")
        if not tmpl_path.is_file():
            remedy = ("create _tools/kit_env.json (no template present either; "
                      "see _tools/kit_env.json docs in CLAUDE.md)")
        checks.append(Check("kit_env.json", WARN,
                            "not present -- machine paths unconfigured",
                            remedy))
        # Without kit_env there are no capability blocks to probe.
        checks.append(Check("kit_env capabilities", INFO,
                            "skipped -- kit_env.json absent", ""))
        return checks
    env, err = _load_json(env_path)
    if env is None:
        checks.append(Check("kit_env.json", FAIL,
                            f"present but unparseable ({err})",
                            "fix the JSON syntax in _tools/kit_env.json"))
        return checks
    checks.append(Check("kit_env.json", PASS, "present and valid JSON", ""))

    # word / node / python blocks: sanity only.
    for blk in ("word", "node", "python"):
        if blk in env:
            checks.append(Check(f"kit_env.{blk}", INFO,
                                "declared (sanity ok)", ""))
        else:
            checks.append(Check(f"kit_env.{blk}", WARN,
                                f"'{blk}' block absent from kit_env.json",
                                f"add a '{blk}' block (see the template)"))

    # cover_gen -> AI cover art (OPTIONAL capability).
    cg = env.get("cover_gen", {}) or {}
    cg_paths = [cg.get("comfyui_skill_dir"), cg.get("run_workflow"),
                cg.get("workflows_dir")]
    present = _paths_exist(*cg_paths)
    if cg and present:
        ckpt = cg.get("checkpoints_dir")
        ckpt_note = ""
        if ckpt and not _paths_exist(ckpt):
            ckpt_note = " (checkpoints_dir missing -- fetch the SDXL model first)"
        checks.append(Check("cap: AI cover art (cover_gen)", PASS,
                            f"ComfyUI/hermes paths resolve{ckpt_note}", ""))
    else:
        checks.append(Check("cap: AI cover art (cover_gen)", WARN,
                            "cover_gen paths missing -> AI cover art disabled",
                            "supply your own art in cover_art/ -- compositing + "
                            "verification still work (Tier 2)"))

    # vision -> local KEEL verification (OPTIONAL; Claude vision is the fallback).
    vis = env.get("vision", {}) or {}
    vis_paths = [vis.get("llama_server"), vis.get("qwen_model"), vis.get("mmproj")]
    if vis and _paths_exist(*vis_paths):
        checks.append(Check("cap: local vision (KEEL)", PASS,
                            f"llama-server + Qwen model + mmproj resolve "
                            f"({vis.get('host','?')}:{vis.get('port','?')})", ""))
    else:
        checks.append(Check("cap: local vision (KEEL)", WARN,
                            "KEEL vision paths missing -> local vision disabled",
                            "use --backend claude for perceptual gates "
                            "(no local setup needed)"))

    # organs -> optional accelerators; repo-local resize_image_safe.py replaces imguard.
    org = env.get("organs", {}) or {}
    org_present = _paths_exist(*[org.get(k) for k in
                                 ("imguard", "chunker", "estimate_tokens",
                                  "fetcher", "everything")])
    if org and org_present:
        checks.append(Check("cap: organ accelerators", INFO,
                            f"{len(org_present)}/5 organ path(s) resolve "
                            "(optional speedups)", ""))
    else:
        checks.append(Check("cap: organ accelerators", INFO,
                            "organ paths absent (expected on a stranger's box) "
                            "-> repo-local _tools/resize_image_safe.py replaces "
                            "imguard; other organs are optional", ""))
    return checks, env


# ---------------------------------------------------------------------------
# (h) LibreOffice soffice (future Tier-2 print path)
# ---------------------------------------------------------------------------
def check_soffice():
    where = shutil.which("soffice")
    if not where:
        # Probe common install dirs.
        candidates = [
            r"C:\Program Files\LibreOffice\program\soffice.exe",
            r"C:\Program Files (x86)\LibreOffice\program\soffice.exe",
            "/Applications/LibreOffice.app/Contents/MacOS/soffice",
            "/usr/bin/soffice", "/usr/local/bin/soffice",
            "/snap/bin/libreoffice",
        ]
        for c in candidates:
            if Path(c).exists():
                where = c
                break
    if where:
        return Check("LibreOffice (soffice)", INFO,
                     f"found at {where} -- potential future Tier-2 print path",
                     "")
    return Check("LibreOffice (soffice)", INFO,
                 "not found -- not required (print uses Word COM on Tier 1)",
                 "optional: install LibreOffice for a future non-Word print path")


# ---------------------------------------------------------------------------
# (i)/(j) HTTP reachability probes (stdlib urllib, short timeout)
# ---------------------------------------------------------------------------
def _http_ok(url, timeout=2.0):
    try:
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return True, f"HTTP {getattr(resp, 'status', '200')}"
    except urllib.error.HTTPError as exc:
        # A response (even 4xx/405) means the server is up and reachable.
        return True, f"HTTP {exc.code} (server reachable)"
    except Exception as exc:
        return False, exc.__class__.__name__


def check_comfyui(env):
    cg = (env or {}).get("cover_gen", {}) or {}
    server = cg.get("comfyui_server")
    if not server:
        return Check("ComfyUI reachability", SKIP,
                     "cover_gen.comfyui_server unconfigured -- skipped", "")
    ok, how = _http_ok(server, timeout=2.0)
    if ok:
        return Check("ComfyUI reachability", PASS,
                     f"{server} reachable ({how})", "")
    return Check("ComfyUI reachability", WARN,
                 f"{server} unreachable ({how}) -- AI cover art needs ComfyUI "
                 "running",
                 f"start ComfyUI (see cover_gen.comfyui_app) or supply your own "
                 "cover art")


def check_vision(env):
    vis = (env or {}).get("vision", {}) or {}
    host, port = vis.get("host"), vis.get("port")
    if not (host and port):
        return Check("Vision backend", INFO,
                     "no local vision configured -- perceptual gates will use "
                     "Claude vision (--backend claude); no local setup needed",
                     "")
    url = f"http://{host}:{port}/health"
    ok, how = _http_ok(url, timeout=2.0)
    if not ok:
        # Some llama-server builds lack /health; try the root.
        ok, how = _http_ok(f"http://{host}:{port}/", timeout=2.0)
    if ok:
        return Check("Vision backend", PASS,
                     f"KEEL llama-server up at {host}:{port} ({how})", "")
    return Check("Vision backend", INFO,
                 f"KEEL llama-server not answering at {host}:{port} ({how}) -- "
                 "fall back to --backend claude",
                 f"start it via kit_env.vision.start_cmd, or use --backend claude")


# ---------------------------------------------------------------------------
# Assembly + rendering
# ---------------------------------------------------------------------------
def run_all(config_path):
    checks = []
    checks.append(check_python())
    checks.extend(check_pip_deps())
    checks.append(check_word_com())
    checks.extend(check_node())
    checks.extend(check_fonts())
    checks.extend(check_interior_font(config_path))
    ke = check_kit_env()
    env = None
    if isinstance(ke, tuple):
        kchecks, env = ke
        checks.extend(kchecks)
    else:
        checks.extend(ke)
    checks.append(check_soffice())
    checks.append(check_comfyui(env))
    checks.append(check_vision(env))
    return checks


def derive_tier(checks):
    """Map the check set to a tier verdict + a list of NOT-READY reasons."""
    by_name = {c.name: c for c in checks}

    def st(name):
        c = by_name.get(name)
        return c.status if c else SKIP

    blockers = []
    # Tier-2 hard deps: Python 3.10+, the cover/digital pip trio, Node runtime,
    # vendored node modules, vendored cover fonts.
    if st("Python runtime") == FAIL:
        blockers.append("Python < 3.10")
    for pipname in ("pip: Pillow", "pip: PyMuPDF", "pip: pypdf"):
        if st(pipname) == FAIL:
            blockers.append(pipname.replace("pip: ", "") + " missing")
    if st("Node runtime") == FAIL:
        blockers.append("Node.js missing")
    if st("Node modules (vendored)") == FAIL:
        blockers.append("vendored node_modules missing")
    if st("Cover fonts (vendored)") == FAIL:
        blockers.append("cover fonts missing")

    if blockers:
        return "NOT READY", blockers
    # Tier 1 iff Word COM is usable.
    if st("Word COM (Tier 1)") == PASS:
        return "TIER 1 (full print)", []
    return "TIER 2 (EPUB/Kindle/compositing)", []


_ICON = {PASS: "[PASS]", WARN: "[WARN]", FAIL: "[FAIL]", SKIP: "[SKIP]",
         INFO: "[INFO]"}


def render_table(checks):
    name_w = max((len(c.name) for c in checks), default=4)
    name_w = max(name_w, len("CHECK"))
    lines = []
    header = f"  {'CHECK'.ljust(name_w)}  STATUS  DETAIL"
    lines.append(header)
    lines.append("  " + "-" * (name_w + 2) + "  ------  " + "-" * 48)
    for c in checks:
        icon = _ICON.get(c.status, "[????]")
        lines.append(f"  {c.name.ljust(name_w)}  {icon}  {c.detail}")
        if c.remedy and c.status in (WARN, FAIL):
            lines.append(f"  {' ' * name_w}          -> fix: {c.remedy}")
    return "\n".join(lines)


def render_verdict(tier, blockers, checks):
    counts = {}
    for c in checks:
        counts[c.status] = counts.get(c.status, 0) + 1
    tally = "  ".join(f"{k}:{counts.get(k, 0)}"
                      for k in (PASS, WARN, FAIL, SKIP, INFO))
    out = []
    out.append("")
    out.append("=" * 66)
    out.append(f"  TIER VERDICT:  {tier}")
    out.append(f"  tally:         {tally}")
    if tier == "NOT READY":
        out.append("  missing:       " + "; ".join(blockers))
        out.append("  -> resolve the FAIL rows above, then re-run doctor.py.")
    elif tier.startswith("TIER 2"):
        out.append("  Word COM not available -> print PDFs are disabled.")
        out.append("  You CAN: build EPUB + Kindle DOCX, composite covers from")
        out.append("  your own art, and verify with Claude vision.")
    else:
        out.append("  Full print pipeline available (Windows + Word COM).")
    out.append("=" * 66)
    return "\n".join(out)


# ---------------------------------------------------------------------------
# (k) end-to-end smoke test (--smoke)
#     doctor.py normally only proves the ENVIRONMENT is present. --smoke proves
#     the PIPELINE still WORKS: it drives the testvoyage proof book through
#         assemble_manuscript -> generate_kindle -> verify_build --format kindle
#     and asserts exit 0 + Kindle word-count parity (the ebook is NOT below the
#     assembled master). This turns testvoyage into a standing regression fixture:
#     a code change that breaks assembly, the Kindle generator, or word parity
#     fails here mechanically. Stdlib + subprocess only; leaves the tree clean.
# ---------------------------------------------------------------------------

_TESTVOYAGE = REPO / "book_workspace" / "testvoyage"
# A high sentinel version the smoke run writes+overwrites+deletes, so repeated
# runs never accumulate outputs/markdown/<slug>_vN.md files.
_SMOKE_VERSION = 999999


def _docx_wt_word_count(docx_path):
    """Approximate DOCX word count from <w:t> runs; mirrors verify_build's
    _docx_word_count so parity is counted the same way on both sides."""
    import re as _re
    import zipfile as _zip
    try:
        with _zip.ZipFile(docx_path) as z:
            xml = z.read("word/document.xml").decode("utf-8", "replace")
    except Exception:
        return None
    texts = _re.findall(r"<w:t[^>]*>([^<]*)</w:t>", xml)
    return len((" ".join(texts)).split())


def run_smoke():
    """Drive testvoyage through assemble -> generate_kindle -> verify_build and
    assert exit 0 + Kindle word parity. Returns (ok: bool, lines: list[str])."""
    lines = []
    ok = True
    cfg_path = _TESTVOYAGE / "book_config.json"

    def step(label, status, detail=""):
        lines.append(f"  [{status}] {label}" + (f" -- {detail}" if detail else ""))

    if not cfg_path.is_file():
        step("locate testvoyage fixture", "FAIL",
             f"{cfg_path} not found (the smoke fixture must ship with the kit)")
        return False, lines
    step("locate testvoyage fixture", "PASS", str(_TESTVOYAGE))

    md_dir = _TESTVOYAGE / "outputs" / "markdown"
    slug = "testvoyage"
    cfg, err = _load_json(cfg_path)
    if cfg and cfg.get("slug"):
        slug = cfg["slug"]
    sentinel_md = md_dir / f"{slug}_v{_SMOKE_VERSION}.md"
    kindle_out = _TESTVOYAGE / "outputs" / "kindle" / f"_smoke_{slug}_KINDLE.docx"
    cleanup = [sentinel_md, kindle_out]

    try:
        # 1) assemble to a throwaway sentinel version (overwrite-safe, repeatable).
        rc, out, cerr = _run(
            [sys.executable, str(TOOLS / "assemble_manuscript.py"),
             "--config", str(cfg_path),
             "--version", str(_SMOKE_VERSION), "--overwrite"],
            cwd=str(REPO), timeout=90)
        master_words = None
        parity_ok = None
        for ln in (out or "").splitlines():
            if ln.startswith("TOTAL_WORDS="):
                try:
                    master_words = int(ln.split("=", 1)[1])
                except ValueError:
                    pass
        try:
            summary = json.loads((out or "").split("TOTAL_WORDS=")[0].strip())
            parity_ok = summary.get("parity_ok")
        except Exception:
            parity_ok = None
        if rc != 0 or not sentinel_md.is_file():
            step("assemble_manuscript", "FAIL",
                 f"rc={rc} {cerr or out or ''}".strip()[:160])
            return False, lines
        if parity_ok is False:
            step("assemble word-count parity", "FAIL",
                 "parts re-read sum != stitched master")
            ok = False
        else:
            step("assemble_manuscript", "PASS",
                 f"master v{_SMOKE_VERSION}, {master_words} words, parity_ok")

        # 2) generate the Kindle DOCX from that master (needs Node + modules).
        node_ok = shutil.which("node") is not None
        nm = TOOLS / "node_modules"
        modules_ok = (nm / "docx").is_dir() and (nm / "jszip").is_dir()
        if not (node_ok and modules_ok):
            step("generate_kindle", "SKIP",
                 "Node runtime or vendored node_modules absent (Tier-2 box) -- "
                 "assembly parity above still proves the source path")
            # Kindle can't be built here; the assemble gate is the smoke floor.
            return ok, lines
        rc, out, cerr = _run(
            ["node", str(TOOLS / "generate_kindle.js"),
             "--config", str(cfg_path), "--out", str(kindle_out)],
            cwd=str(REPO), timeout=120)
        if rc != 0 or not kindle_out.is_file():
            step("generate_kindle", "FAIL",
                 f"rc={rc} {cerr or out or ''}".strip()[:160])
            return False, lines
        kindle_words = _docx_wt_word_count(kindle_out)
        step("generate_kindle", "PASS",
             f"{kindle_out.name}, ~{kindle_words} words")

        # 3) THE core parity claim: Kindle body must NOT be below the master.
        #    Counted directly here so a cross-tool bug can't mask a real shortfall.
        if kindle_words is None or master_words is None:
            step("kindle word-count parity", "WARN",
                 "could not count words on one side (informational)")
        elif kindle_words + 10 < master_words:
            # +10 slack: the DOCX omits a little front-matter furniture text.
            step("kindle word-count parity", "FAIL",
                 f"kindle ~{kindle_words} < master {master_words} (source drift!)")
            ok = False
        else:
            step("kindle word-count parity", "PASS",
                 f"kindle ~{kindle_words} >= master {master_words}")

        # 4) run the mechanical verifier too, and surface its verdict. A failure
        #    here does NOT flip the smoke verdict on its own (verify_build lives
        #    in another module and may carry independent defects), but it IS
        #    reported so a regression there is visible.
        rc, out, cerr = _run(
            [sys.executable, str(TOOLS / "verify_build.py"),
             "--config", str(cfg_path), "--format", "kindle"],
            cwd=str(REPO), timeout=120)
        if rc == 0:
            step("verify_build --format kindle", "PASS", "all kindle checks green")
        else:
            # Prefer the most informative line: a traceback Error/Exception,
            # else a failing-check "detail" line, else the last content line.
            blob = (cerr or "") + "\n" + (out or "")
            detail = "see verify_build (run it directly for the full report)"
            errline = [ln.strip() for ln in blob.splitlines()
                       if ln.strip() and ("Error" in ln or "Exception" in ln)]
            faildetail = [ln.strip().strip(',"') for ln in blob.splitlines()
                          if '"detail"' in ln]
            if errline:
                detail = errline[-1]
            elif faildetail:
                detail = faildetail[-1]
            else:
                tail = [ln.strip() for ln in blob.splitlines()
                        if len(ln.strip()) > 1]
                if tail:
                    detail = tail[-1]
            step("verify_build --format kindle", "WARN", f"rc={rc} -- {detail[:150]}")
        return ok, lines
    finally:
        for p in cleanup:
            try:
                if p.exists():
                    p.unlink()
            except Exception:
                pass


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="doctor.py",
        description="BOOKSMITH preflight / capability checker (stdlib-only).")
    parser.add_argument("--config", metavar="book_config.json",
                        help="probe THIS book's interior body font "
                             "(default: Georgia)")
    parser.add_argument("--json", action="store_true",
                        help="emit machine-readable JSON {checks, tier}")
    parser.add_argument("--smoke", action="store_true",
                        help="run the end-to-end pipeline smoke test over the "
                             "testvoyage fixture (assemble -> generate_kindle -> "
                             "verify_build) and assert word-count parity; exit 0 "
                             "on pass, 1 on failure")
    parser.add_argument("--autoconfig", action="store_true",
                        help="detect this machine and write _tools/kit_env.json "
                             "(backs up any existing) -- run first on a fresh copy")
    try:
        args = parser.parse_args(argv)
    except SystemExit:
        # argparse already printed usage; normalize to exit code 2.
        return 2

    if args.autoconfig:
        import subprocess
        return subprocess.call([sys.executable,
                                str(Path(__file__).resolve().parent / "autoconfig.py")])

    if args.smoke:
        print()
        print(f"  BOOKSMITH doctor --smoke -- end-to-end pipeline test")
        print(f"  repo: {REPO}")
        print()
        try:
            ok, lines = run_smoke()
        except Exception as exc:
            print(f"  [FAIL] smoke test crashed "
                  f"({exc.__class__.__name__}: {exc})")
            return 1
        print("\n".join(lines))
        print()
        print("=" * 66)
        print(f"  SMOKE VERDICT: {'PASS' if ok else 'FAIL'}")
        print("=" * 66)
        return 0 if ok else 1

    config_path = None
    if args.config:
        config_path = Path(args.config)
        if not config_path.is_absolute():
            # Resolve relative to cwd first, then repo root.
            if not config_path.exists() and (REPO / args.config).exists():
                config_path = REPO / args.config

    try:
        checks = run_all(config_path)
    except Exception as exc:
        # Absolute backstop: no probe should escape, but never crash if one does.
        checks = [Check("doctor internal", FAIL,
                        f"unexpected error while probing "
                        f"({exc.__class__.__name__}: {exc})",
                        "report this; run with --json for detail")]

    tier, blockers = derive_tier(checks)

    if args.json:
        payload = {
            "tier": tier,
            "blockers": blockers,
            "platform": platform.system(),
            "checks": [c.as_dict() for c in checks],
        }
        print(json.dumps(payload, indent=2))
    else:
        print()
        print(f"  BOOKSMITH doctor -- preflight for {REPO}")
        print(f"  platform: {platform.system()} {platform.release()}  |  "
              f"python {sys.version_info.major}.{sys.version_info.minor}."
              f"{sys.version_info.micro}")
        print()
        print(render_table(checks))
        print(render_verdict(tier, blockers, checks))

    # Exit codes: 0 if Tier 1 or Tier 2 achievable, 1 if NOT READY.
    return 0 if tier != "NOT READY" else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        sys.exit(2)
