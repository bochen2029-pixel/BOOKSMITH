#!/usr/bin/env python3
r"""
verify_build.py — mechanical verifier (spec checks -> pass/fail JSON) (BOOKSMITH).

PURPOSE (KIT_ARCHITECTURE (c) verify_build.py; LESSONS_LEDGER §10.5, §14)
    The mechanical half of the two-verifier model. Machine-checkable
    production invariants, run at GATE-5 and GATE-7 for every format. Every
    gotcha promoted to a build-time assert.

    Checks (per the ledger's FIRST-PASS DEFAULTS CHECKLIST):
      1  <w:mirrorMargins/> + <w:evenAndOddHeaders/> present in the interior
         DOCX word/settings.xml (zipfile grep).                 [print formats]
      2  every header-free section's word/header*.xml renders []  (empty-
         header fix; body headers show the running title).      [print formats]
      3  recto parity — each Part/chapter heading on an odd page, via
         check_part_pages.py (Word COM).                        [print formats]
      4  page count multiple — KDP x2, Mixam x4.                 [print formats]
      5  re-derived PAGES matches the value fed to composite_cover.py (reads
         the compositor's recorded PAGES if present).           [print formats]
      6  cover wrap dimensions match KDP/Mixam expectation to 4 decimals.
      7  lint_manuscript.py clean (exit 0).                      [all formats]
      8  Kindle word-count parity — the ebook is NOT below the print word
         count (never ships short).                             [kindle]

CONTRACT
    python verify_build.py --config book_config.json --format <profile>
        --format in {kindle, kdp_paperback, kdp_hardcover, mixam_hardcover,
                     mixam_paperback, blurb_paperback, blurb_hardcover,
                     digital_pdf, epub}
        [--config-env kit_env.json] [--root <workspace>]
    -> prints
        {"format":..., "checks":[{"name","pass","detail"}], "all_pass":bool}
       as JSON. Exit 0 if all_pass else 1.

    Cover-dimension checking reads the compositor's cover_meta.json sidecar
    (pages + target) AND independently recomputes the expected dims —
    mixam_paperback via the same spine formula/override, blurb via
    preset_lookup (the SAME module composite_cover.py builds with, so a
    mismatch is a real artifact defect, never re-implementation drift) —
    then compares the PDF MediaBox to 0.001 in.

    Service min-page rules are surfaced as an INFORMATIONAL (never-fail)
    note: mixam_paperback min 32, blurb min 24.

    Reads ONLY book_config.json (per-book knobs) + the generated artifacts
    under book_workspace/<slug>/outputs/. Machine paths (Word availability for
    the recto check) are the platform's; check_part_pages.py + lint_manuscript.py
    are repo-relative siblings.

SOURCE
    Consolidated from LESSONS_LEDGER §3.4/§3.5 (XML inspection), §4.3/§4.4
    (recto + page multiples), §5.5/§5.6 (wrap dims), §2.8/§7.3 (Kindle parity);
    invokes _tools/check_part_pages.py + _tools/lint_manuscript.py.
"""
import argparse
import json
import re
import subprocess
import sys
import zipfile
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
CHECK_PART_PAGES = SCRIPT_DIR / "check_part_pages.py"
LINT_SCRIPT = SCRIPT_DIR / "lint_manuscript.py"

# Shared preset geometry (Mixam paperback + Blurb) — the SAME module
# composite_cover.py builds with, so this verifier recomputes exactly what the
# compositor computed (single code path, no re-implementation drift).
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))
import preset_lookup  # noqa: E402  (sibling module, path pinned above)

PRINT_FORMATS = {"kdp_paperback", "kdp_hardcover", "mixam_hardcover",
                 "mixam_paperback", "blurb_paperback", "blurb_hardcover"}
# Output subdir per format (mirrors KIT_ARCHITECTURE (b) folder taxonomy).
FORMAT_DIR = {
    "kindle": "kindle",
    "kdp_paperback": "kdp_paperback",
    "kdp_hardcover": "kdp_hardcover",
    "mixam_hardcover": "mixam_hardcover",
    "mixam_paperback": "mixam_paperback",
    "blurb_paperback": "blurb_paperback",
    "blurb_hardcover": "blurb_hardcover",
    "digital_pdf": "digital",
    "epub": "epub",
}

# Interior page-count multiple per print format (§4.4; print_presets
# page_multiple: Mixam perfect-bound/case x4 — CONFIRMED; KDP + Blurb x2).
PAGE_MULTIPLES = {
    "kdp_paperback": 2,
    "kdp_hardcover": 2,
    "mixam_hardcover": 4,
    "mixam_paperback": 4,
    "blurb_paperback": 2,
    "blurb_hardcover": 2,
}

# Service minimum interior page counts — INFORMATIONAL ONLY (never fails a
# build; a tiny validation book must still verify green). Sources:
# print_presets mixam_paperback.min_max_pages (32) + blurb_trade
# .page_count_range_probed (24 — INFERRED from the calculator range).
MIN_PAGES_NOTE = {
    "mixam_paperback": 32,
    "blurb_paperback": 24,
    "blurb_hardcover": 24,
}


# ─────────────────────────────────────────────────────────────────────────────
# config + workspace resolution
# ─────────────────────────────────────────────────────────────────────────────

def load_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as fh:
        return json.load(fh)


def workspace_root(cfg: dict, config_path: Path, explicit_root) -> Path:
    if explicit_root:
        return Path(explicit_root)
    slug = cfg.get("slug")
    base = config_path.resolve().parent
    if slug:
        candidate = base / "book_workspace" / slug
        if candidate.exists():
            return candidate
        if base.name == slug:
            return base
    return base


def find_one(directory: Path, suffix: str, prefer_substr=None):
    """Return a single file in `directory` matching `suffix`, preferring names
    that contain any of `prefer_substr`. Returns None if none / directory
    absent. If multiple and no preference matches, returns the most recent."""
    if not directory.exists():
        return None
    candidates = sorted(directory.glob(f"*{suffix}"),
                        key=lambda p: p.stat().st_mtime, reverse=True)
    if not candidates:
        return None
    if prefer_substr:
        for sub in prefer_substr:
            for c in candidates:
                if sub in c.name.lower():
                    return c
    return candidates[0]


# ─────────────────────────────────────────────────────────────────────────────
# check helpers  (each returns (name, pass_bool, detail))
# ─────────────────────────────────────────────────────────────────────────────

def check_mirror_flags(docx: Path):
    name = "mirror_flags_in_settings"
    if docx is None:
        return (name, False, "interior DOCX not found")
    try:
        with zipfile.ZipFile(docx) as z:
            settings = z.read("word/settings.xml").decode("utf-8", "replace")
    except (KeyError, zipfile.BadZipFile, OSError) as exc:
        return (name, False, f"could not read word/settings.xml: {exc}")
    has_mirror = "<w:mirrorMargins" in settings
    has_evenodd = "<w:evenAndOddHeaders" in settings
    ok = has_mirror and has_evenodd
    detail = (f"mirrorMargins={'y' if has_mirror else 'MISSING'}, "
              f"evenAndOddHeaders={'y' if has_evenodd else 'MISSING'}")
    return (name, ok, detail)


def _header_texts(z: zipfile.ZipFile, part_name: str):
    xml = z.read(part_name).decode("utf-8", "replace")
    return re.findall(r"<w:t[^>]*>([^<]*)</w:t>", xml)


def check_empty_headers(docx: Path):
    """At least one header*.xml must render [] (a header-free ceremonial/blank
    section got the empty-header fix). If EVERY header carries text, the
    empty-header fix was not applied — the most-rediscovered rejection."""
    name = "empty_headers_on_headerfree_sections"
    if docx is None:
        return (name, False, "interior DOCX not found")
    try:
        with zipfile.ZipFile(docx) as z:
            header_parts = sorted(n for n in z.namelist()
                                  if re.match(r"word/header\d*\.xml$", n))
            if not header_parts:
                return (name, False, "no word/header*.xml parts present")
            empties = 0
            summary = []
            for h in header_parts:
                texts = [t for t in _header_texts(z, h) if t.strip()]
                if not texts:
                    empties += 1
                    summary.append(f"{h.split('/')[-1]}=[]")
                else:
                    summary.append(f"{h.split('/')[-1]}={texts[:1]}")
    except (zipfile.BadZipFile, OSError) as exc:
        return (name, False, f"could not inspect headers: {exc}")
    ok = empties >= 1
    detail = ("; ".join(summary) +
              ("" if ok else "  (NO empty header found — empty-header fix likely missing)"))
    return (name, ok, detail)


def check_recto_parity(docx: Path, config_path: Path):
    name = "recto_parity"
    if docx is None:
        return (name, False, "interior DOCX not found")
    if not CHECK_PART_PAGES.exists():
        return (name, False, f"check_part_pages.py not found at {CHECK_PART_PAGES}")
    cmd = [sys.executable, str(CHECK_PART_PAGES), str(docx)]
    if config_path is not None:
        cmd += ["--config", str(config_path)]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    except (subprocess.SubprocessError, OSError) as exc:
        return (name, False, f"check_part_pages.py failed to run: {exc}")
    out = (proc.stdout or "").strip()
    if not out and "Word.Application" in (proc.stderr or ""):
        return (name, False, f"Word COM unavailable: {(proc.stderr or '').strip()[:160]}")
    try:
        obj = json.loads(out.splitlines()[-1])
    except (ValueError, IndexError):
        return (name, False,
                f"could not parse check_part_pages JSON: {(out or proc.stderr or '').strip()[:160]}")
    results = obj.get("results", [])
    if not results:
        return (name, False, "no unit headings resolved to check")
    missing = [r["heading"] for r in results if r.get("page") is None]
    if missing:
        return (name, False,
                f"{len(missing)} heading(s) NOT FOUND in the DOCX (search/render mismatch): {missing[:5]}")
    versos = [r["heading"] for r in results if not r.get("recto")]
    if versos:
        return (name, False, f"{len(versos)} heading(s) on verso (even) pages: {versos[:5]}")
    return (name, True, f"all {len(results)} headings on recto (odd) pages")


def _pdf_page_count(pdf: Path):
    try:
        import fitz
        with fitz.open(str(pdf)) as doc:
            return len(doc)
    except Exception:
        pass
    # Minimal fallback: count /Type /Page objects without a PDF lib.
    try:
        data = pdf.read_bytes()
        return len(re.findall(rb"/Type\s*/Page[^s]", data)) or None
    except OSError:
        return None


def check_page_multiple(pdf: Path, fmt: str):
    name = "page_count_multiple"
    if pdf is None:
        return (name, False, "interior PDF not found")
    pages = _pdf_page_count(pdf)
    if pages is None:
        return (name, False, "could not determine PDF page count")
    multiple = PAGE_MULTIPLES.get(fmt, 2)
    ok = pages % multiple == 0
    return (name, ok, f"{pages} pages; must be a multiple of {multiple} "
                      f"({'ok' if ok else 'FAIL'})")


def check_min_pages_note(pdf: Path, fmt: str):
    """INFORMATIONAL, never-fail: surface the service's minimum interior page
    count so a short book is flagged before upload — without failing a small
    validation build (which must still verify all_pass=true)."""
    name = "min_pages_note"
    minimum = MIN_PAGES_NOTE.get(fmt)
    if minimum is None:
        return None
    pages = _pdf_page_count(pdf) if pdf is not None else None
    if pages is None:
        return (name, True,
                f"INFORMATIONAL: no interior PDF to count; service minimum for "
                f"{fmt} is {minimum} pages (never-fail note)")
    if pages < minimum:
        return (name, True,
                f"INFORMATIONAL: interior is {pages} pages — BELOW the {fmt} "
                f"service minimum of {minimum}; pad or accept at upload "
                f"(never-fail note)")
    return (name, True, f"{pages} pages >= {fmt} service minimum {minimum}")


def _read_recorded_pages(fmt_dir: Path):
    """composite_cover.py records the PAGES it used. Look for a PAGES marker in
    a sidecar (pages.txt / *_dims.json / *_cover_meta.json). Returns int|None."""
    for meta_name in ("pages.txt", "PAGES.txt"):
        p = fmt_dir / meta_name
        if p.exists():
            m = re.search(r"\d+", p.read_text(encoding="utf-8", errors="replace"))
            if m:
                return int(m.group(0))
    for meta in list(fmt_dir.glob("*dims*.json")) + list(fmt_dir.glob("*meta*.json")):
        try:
            obj = load_json(meta)
        except (json.JSONDecodeError, OSError):
            continue
        for key in ("pages", "PAGES", "page_count"):
            if isinstance(obj, dict) and key in obj:
                try:
                    return int(obj[key])
                except (TypeError, ValueError):
                    pass
    return None


def check_pages_match_compositor(pdf: Path, fmt_dir: Path):
    name = "pages_match_compositor"
    if pdf is None:
        return (name, False, "interior PDF not found")
    derived = _pdf_page_count(pdf)
    recorded = _read_recorded_pages(fmt_dir)
    if derived is None:
        return (name, False, "could not derive PAGES from the interior PDF")
    if recorded is None:
        # No sidecar to compare against — informational pass (the single
        # re-derived PAGES is the interior PDF itself; nothing contradicts it).
        return (name, True, f"re-derived PAGES={derived}; no compositor sidecar "
                            f"to cross-check (single-source ok)")
    ok = derived == recorded
    return (name, ok, f"re-derived PAGES={derived} vs compositor PAGES={recorded} "
                      f"({'match' if ok else 'MISMATCH'})")


def _expected_wrap(cfg: dict, fmt: str, pages):
    """Compute the expected wrap (W, H) inches for a print format, per
    LESSONS_LEDGER §5.5. Returns (w, h) rounded to 4 decimals, or None if pages
    is unknown."""
    if pages is None:
        return None
    trim = cfg.get("trim", {"w": 6, "h": 9})
    tw, th = float(trim.get("w", 6)), float(trim.get("h", 9))
    spine = cfg.get("spine", {})
    paper = cfg.get("paper", "cream")
    per_page = float(spine.get("per_page_cream", 0.0025)) if paper == "cream" \
        else float(spine.get("per_page_white", 0.002252))

    if fmt == "kdp_paperback":
        bleed = float(spine.get("kdp_bleed_in", 0.125))
        spine_w = pages * per_page  # no board add
        w = tw * 2 + spine_w + bleed * 2
        h = th + bleed * 2
        return (round(w, 4), round(h, 4))
    if fmt == "kdp_hardcover":
        # KDP hardcover is white-only.
        per_page_hc = float(spine.get("per_page_white", 0.002252))
        board = float(spine.get("kdp_hardcover_board_add", 0.348))
        turn_in = float(spine.get("kdp_hardcover_turn_in_in", 0.708))
        height = float(spine.get("kdp_hardcover_height_in", 10.417))
        spine_w = pages * per_page_hc + board
        w = tw * 2 + spine_w + turn_in * 2
        return (round(w, 4), round(height, 4))
    if fmt == "mixam_hardcover":
        # Mixam ships FOUR panels; the front panel is trim + 2*bleed each side.
        bleed = float(spine.get("mixam_bleed_in", 0.80))
        w = tw + bleed * 2
        h = th + bleed * 2
        return (round(w, 4), round(h, 4))
    if fmt == "mixam_paperback":
        # Same spine formula/override the compositor used (preset_lookup —
        # single code path): override wins, else cream/white fit formulas.
        spine_w = preset_lookup.mixam_paperback_spine(
            pages, paper, spine.get("spine_override_in"))
        d = preset_lookup.mixam_paperback_wrap_dims(tw, th, spine_w)
        return (d["cover_w"], d["cover_h"])
    if fmt == "blurb_paperback":
        d = preset_lookup.softcover_dims(
            preset_lookup.trim_key(tw, th),
            preset_lookup.blurb_paper_from_config(cfg), pages)
        return (d["cover_w"], d["cover_h"])
    if fmt == "blurb_hardcover":
        d = preset_lookup.imagewrap_dims(
            preset_lookup.trim_key(tw, th),
            preset_lookup.blurb_paper_from_config(cfg), pages)
        return (d["cover_w"], d["cover_h"])
    return None


def _cover_mediabox_inches(cover_pdf: Path):
    """Return (w_in, h_in) of the cover PDF's first-page MediaBox (rounded to 4)."""
    try:
        import fitz
        with fitz.open(str(cover_pdf)) as doc:
            r = doc[0].rect
            return (round(r.width / 72.0, 4), round(r.height / 72.0, 4))
    except Exception:
        return None


def _find_cover_pdf(fmt_dir: Path, fmt: str):
    """Return a GENUINE cover-wrap PDF, or None. Excludes interior PDFs FIRST
    (whose names carry a format token — note 'hardcover' contains 'cover', so a
    bare 'cover' keyword would false-match the interior), then matches an
    unambiguous cover marker."""
    if not fmt_dir.exists():
        return None
    interior_tokens = ("inner_", "interior", "kdp_paperback", "kdp_hardcover",
                       "mixam_hardcover", "mixam_paperback", "_blurb_trade")
    keys = ("front_cover",) if fmt == "mixam_hardcover" else ("wrap", "cover_wrap")
    for p in sorted(fmt_dir.glob("*.pdf"),
                    key=lambda x: x.stat().st_mtime, reverse=True):
        n = p.name.lower()
        if any(t in n for t in interior_tokens):
            continue
        if any(k in n for k in keys):
            return p
    return None


def _is_cover_name(name: str) -> bool:
    """True if a PDF name is a COVER file. Uses precise markers that do NOT
    collide with interior format tokens (bare 'cover' matches 'hardcover';
    bare 'back' matches 'paperback')."""
    n = name.lower()
    if n == "spine.pdf" or n.endswith("_spine.pdf"):
        return True
    return any(m in n for m in ("cover_wrap", "front_cover", "back_cover", "_wrap.", "wrap.pdf"))


def _find_interior_pdf(fmt_dir: Path):
    """The interior PDF is the newest PDF that is NOT a cover file."""
    if not fmt_dir.exists():
        return None
    cands = [p for p in sorted(fmt_dir.glob("*.pdf"),
                               key=lambda x: x.stat().st_mtime, reverse=True)
             if not _is_cover_name(p.name)]
    return cands[0] if cands else None


def _read_cover_meta(fmt_dir: Path):
    """Read the compositor's cover_meta.json sidecar ({profile, pages,
    spine_in, target_wrap_in, files}). Returns dict or None."""
    p = fmt_dir / "cover_meta.json"
    if not p.exists():
        return None
    try:
        obj = load_json(p)
    except (json.JSONDecodeError, OSError):
        return None
    return obj if isinstance(obj, dict) else None


def check_cover_wrap_dims(cfg: dict, fmt: str, fmt_dir: Path, pages):
    """Compare the cover PDF MediaBox against the INDEPENDENTLY recomputed
    expected wrap dims (same formula/preset_lookup code path the compositor
    used), preferring the compositor's recorded PAGES from cover_meta.json.
    Also cross-checks the compositor's recorded target against the recompute —
    a disagreement there means the two sides diverged (a real bug)."""
    name = "cover_wrap_dimensions"
    cover = _find_cover_pdf(fmt_dir, fmt)
    if cover is None:
        # The cover is produced at the cover stage (GATE-6), after the interior
        # verify. Absence here is expected — skip, do not measure the interior.
        return (name, True, "no cover wrap PDF yet (produced at the cover stage) — skipped")
    actual = _cover_mediabox_inches(cover)
    if actual is None:
        return (name, False, f"could not read MediaBox from {cover.name} "
                             f"(PyMuPDF required)")

    # Compositor sidecar: pages the cover was built with + its recorded target.
    meta = _read_cover_meta(fmt_dir)
    meta_pages = None
    meta_target = None
    if meta is not None:
        try:
            meta_pages = int(meta["pages"]) if meta.get("pages") is not None else None
        except (TypeError, ValueError):
            meta_pages = None
        t = meta.get("target_wrap_in")
        if isinstance(t, (list, tuple)) and len(t) == 2:
            try:
                meta_target = (float(t[0]), float(t[1]))
            except (TypeError, ValueError):
                meta_target = None

    pages_used = meta_pages if meta_pages is not None else pages
    pages_src = ("cover_meta.json" if meta_pages is not None
                 else "interior PDF" if pages is not None else "unknown")
    try:
        expected = _expected_wrap(cfg, fmt, pages_used)
    except (KeyError, ValueError) as exc:
        return (name, False, f"could not recompute expected dims: {exc}")
    if expected is None:
        return (name, True, f"{cover.name} MediaBox {actual[0]}x{actual[1]} in; "
                            f"PAGES unknown so cannot compute expected (informational)")

    # KDP validator compares to 4 decimals; allow a 0.001" tolerance for FP.
    dw = abs(actual[0] - expected[0])
    dh = abs(actual[1] - expected[1])
    ok = dw <= 0.001 and dh <= 0.001
    detail = (f"{cover.name}: actual {actual[0]}x{actual[1]} vs expected "
              f"{expected[0]}x{expected[1]} in (Δw={dw:.4f}, Δh={dh:.4f}; "
              f"pages={pages_used} from {pages_src}) — {'ok' if ok else 'MISMATCH'}")

    # Cross-check: the compositor's recorded target must equal the recompute.
    if meta_target is not None:
        mt_ok = (abs(meta_target[0] - expected[0]) <= 0.001
                 and abs(meta_target[1] - expected[1]) <= 0.001)
        if mt_ok:
            detail += "; compositor target agrees with recompute"
        else:
            ok = False
            detail += (f"; compositor target {meta_target[0]}x{meta_target[1]} "
                       f"DISAGREES with recomputed {expected[0]}x{expected[1]}")
    return (name, ok, detail)


def check_lint(config_path: Path):
    name = "lint_manuscript_clean"
    if not LINT_SCRIPT.exists():
        return (name, False, f"lint_manuscript.py not found at {LINT_SCRIPT}")
    try:
        proc = subprocess.run(
            [sys.executable, str(LINT_SCRIPT), "--config", str(config_path)],
            capture_output=True, text=True, timeout=180,
        )
    except (subprocess.SubprocessError, OSError) as exc:
        return (name, False, f"lint failed to run: {exc}")
    ok = proc.returncode == 0
    tail = (proc.stdout or "").strip().splitlines()
    detail = tail[-1] if tail else f"exit {proc.returncode}"
    return (name, ok, f"exit {proc.returncode}: {detail}")


def _docx_word_count(docx: Path):
    """Approximate word count from a DOCX by extracting <w:t> text. Adequate
    for a parity comparison (both sides counted the same way)."""
    if docx is None or not docx.exists():
        return None
    try:
        with zipfile.ZipFile(docx) as z:
            xml = z.read("word/document.xml").decode("utf-8", "replace")
    except (KeyError, zipfile.BadZipFile, OSError):
        return None
    texts = re.findall(r"<w:t[^>]*>([^<]*)</w:t>", xml)
    joined = " ".join(texts)
    return len(joined.split())


def _epub_body_word_count(epub: Path):
    """Word count of the EPUB's body chapters (text/*.xhtml minus front/back
    ceremonial pages), counted by stripping tags — adequate for parity."""
    ceremonial = {"cover.xhtml", "titlepage.xhtml", "copyright.xhtml",
                  "dedication.xhtml", "epigraph.xhtml", "about.xhtml"}
    total = 0
    try:
        with zipfile.ZipFile(epub) as z:
            for n in z.namelist():
                if n.startswith("OEBPS/text/") and n.endswith(".xhtml"):
                    if n.split("/")[-1] in ceremonial:
                        continue
                    xml = z.read(n).decode("utf-8", "replace")
                    body = re.search(r"<body[^>]*>(.*)</body>", xml, re.S)
                    text = re.sub(r"<[^>]+>", " ", body.group(1) if body else xml)
                    total += len(text.split())
    except (zipfile.BadZipFile, OSError, KeyError):
        return None
    return total


def check_epub_structure(fmt_dir: Path):
    """Structural EPUB validity: mimetype first+stored, all XML well-formed,
    manifest hrefs exist, spine idrefs resolve, cover-image property present."""
    name = "epub_structure"
    epub = find_one(fmt_dir, ".epub")
    if epub is None:
        return (name, False, "no .epub in the format output dir")
    problems = []
    try:
        with zipfile.ZipFile(epub) as z:
            infos = z.infolist()
            names = set(z.namelist())
            first = infos[0]
            if not (first.filename == "mimetype"
                    and first.compress_type == zipfile.ZIP_STORED
                    and z.read("mimetype") == b"application/epub+zip"):
                problems.append("mimetype not first/STORED/correct")
            import xml.etree.ElementTree as ET
            for n in sorted(names):
                if n.endswith((".xhtml", ".opf", ".ncx", ".xml")):
                    try:
                        ET.fromstring(z.read(n))
                    except ET.ParseError as e:
                        problems.append(f"malformed {n}: {e}")
            if "OEBPS/content.opf" in names:
                opf = z.read("OEBPS/content.opf").decode("utf-8", "replace")
                hrefs = re.findall(r'href="([^"]+)"', opf)
                ids = set(re.findall(r'<item id="([^"]+)"', opf))
                idrefs = re.findall(r'<itemref idref="([^"]+)"', opf)
                missing = [h for h in hrefs if f"OEBPS/{h}" not in names]
                if missing:
                    problems.append(f"manifest hrefs missing from zip: {missing}")
                orphans = [r for r in idrefs if r not in ids]
                if orphans:
                    problems.append(f"spine idrefs not in manifest: {orphans}")
                if 'properties="cover-image"' not in opf:
                    problems.append("no cover-image property in manifest")
            else:
                problems.append("OEBPS/content.opf missing")
    except (zipfile.BadZipFile, OSError) as exc:
        return (name, False, f"could not open EPUB: {exc}")
    ok = not problems
    return (name, ok, "; ".join(problems) if problems else
            f"{epub.name}: mimetype/XML/manifest/spine/cover all valid")


def check_epub_parity(root: Path):
    """EPUB body word count must NOT be below the print word count."""
    name = "epub_wordcount_parity_not_below_print"
    epub = find_one(root / "outputs" / "epub", ".epub")
    if epub is None:
        return (name, False, "no .epub found")
    ew = _epub_body_word_count(epub)
    print_docx = None
    for sub in ("kdp_paperback", "kdp_hardcover", "mixam_hardcover"):
        print_docx = find_one(root / "outputs" / sub, ".docx")
        if print_docx is not None:
            break
    pw = _docx_word_count(print_docx)
    if ew is None:
        return (name, False, "could not count EPUB words")
    if pw is None:
        return (name, True, f"epub={ew} words; no print DOCX to compare "
                            f"(informational — build print first)")
    # Print DOCX carries front matter the EPUB body count excludes; allow a
    # small ceremonial allowance but never a body-sized shortfall.
    ok = ew >= pw - 150
    return (name, ok, f"epub body={ew} words vs print={pw} words "
                      f"({'parity ok' if ok else 'BELOW print — source drift!'})")


def check_kindle_parity(root: Path):
    """Kindle word count must NOT be below the print word count (never short)."""
    name = "kindle_wordcount_parity_not_below_print"
    kindle = find_one(root / "outputs" / "kindle", ".docx",
                      prefer_substr=["kindle"])
    print_docx = None
    for sub in ("kdp_paperback", "kdp_hardcover", "mixam_hardcover"):
        print_docx = find_one(root / "outputs" / sub, ".docx",
                              prefer_substr=["kdp", "mixam", "paperback", "hardcover"])
        if print_docx is not None:
            break
    kw = _docx_word_count(kindle)
    pw = _docx_word_count(print_docx)
    if kw is None:
        return (name, False, "kindle DOCX not found / unreadable")
    if pw is None:
        return (name, True, f"kindle={kw} words; no print DOCX to compare "
                            f"(informational — build print first)")
    ok = kw >= pw
    return (name, ok, f"kindle={kw} words vs print={pw} words "
                      f"({'>= print, ok' if ok else 'BELOW print — source drift!'})")


# ─────────────────────────────────────────────────────────────────────────────
# driver
# ─────────────────────────────────────────────────────────────────────────────

def run_checks(cfg: dict, config_path: Path, root: Path, fmt: str) -> list:
    checks = []
    fmt_dir = root / "outputs" / FORMAT_DIR.get(fmt, fmt)

    if fmt in PRINT_FORMATS:
        docx = find_one(fmt_dir, ".docx",
                        prefer_substr=["kdp", "mixam", "paperback", "hardcover",
                                       "blurb", "inner_"])
        pdf = _find_interior_pdf(fmt_dir)

        checks.append(check_mirror_flags(docx))
        checks.append(check_empty_headers(docx))
        checks.append(check_recto_parity(docx, config_path))
        checks.append(check_page_multiple(pdf, fmt))
        note = check_min_pages_note(pdf, fmt)   # INFORMATIONAL, never fails
        if note is not None:
            checks.append(note)
        checks.append(check_pages_match_compositor(pdf, fmt_dir))
        pages = _pdf_page_count(pdf) if pdf is not None else None
        checks.append(check_cover_wrap_dims(cfg, fmt, fmt_dir, pages))

    if fmt == "kindle":
        checks.append(check_kindle_parity(root))

    if fmt == "epub":
        checks.append(check_epub_structure(fmt_dir))
        checks.append(check_epub_parity(root))

    # lint runs for every format (voice + corruption gate).
    checks.append(check_lint(config_path))

    return checks


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

    ap = argparse.ArgumentParser(
        description="Mechanical build verifier (spec checks -> pass/fail JSON).")
    ap.add_argument("--config", required=True, help="Path to book_config.json.")
    ap.add_argument("--format", required=True,
                    choices=["kindle", "kdp_paperback", "kdp_hardcover",
                             "mixam_hardcover", "mixam_paperback",
                             "blurb_paperback", "blurb_hardcover",
                             "digital_pdf", "epub"],
                    help="Which format profile to verify.")
    ap.add_argument("--root", help="Override the workspace root "
                                   "(default: book_workspace/<slug>/).")
    args = ap.parse_args()

    config_path = Path(args.config)
    if not config_path.exists():
        print(json.dumps({"format": args.format, "all_pass": False,
                          "checks": [{"name": "config", "pass": False,
                                      "detail": f"config not found: {config_path}"}]}))
        return 1
    try:
        cfg = load_json(config_path)
    except (json.JSONDecodeError, OSError) as exc:
        print(json.dumps({"format": args.format, "all_pass": False,
                          "checks": [{"name": "config", "pass": False,
                                      "detail": f"bad config: {exc}"}]}))
        return 1

    root = workspace_root(cfg, config_path, args.root)
    checks_raw = run_checks(cfg, config_path, root, args.format)
    checks = [{"name": n, "pass": bool(ok), "detail": d} for (n, ok, d) in checks_raw]
    all_pass = all(c["pass"] for c in checks) if checks else False

    print(json.dumps({"format": args.format, "root": str(root),
                      "all_pass": all_pass, "checks": checks},
                     ensure_ascii=False, indent=2))
    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(main())
