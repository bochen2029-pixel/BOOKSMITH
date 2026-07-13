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

# The canonical format list — the single source of truth for the --format choices
# and the `--format all` fan-out sweep.
FORMAT_CHOICES = ["kindle", "kdp_paperback", "kdp_hardcover", "mixam_hardcover",
                  "mixam_paperback", "blurb_paperback", "blurb_hardcover",
                  "digital_pdf", "epub"]

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
    # Skip Word owner-lock/temp files (~$name.docx) — a force-killed Word leaves
    # these behind, and they are tiny non-zip files that break the OOXML checks.
    candidates = sorted(
        (p for p in directory.glob(f"*{suffix}") if not p.name.startswith("~$")),
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


# Ceremonial front-matter types that must NOT carry a running head (they get
# their own header-free one-page section). 'blank' versos are header-free too.
_HEADERFREE_FRONTMATTER = {"half_title", "blank", "title", "copyright",
                           "dedication", "epigraph", "contents", "readers_note"}


def _expected_headerfree_sections(cfg: dict) -> int:
    """Count the ceremonial/blank front-matter sections that must render an
    EMPTY header, derived from config.front_matter, plus the trailing blank
    verso the recto strategy appends. Falls back to 1 when front_matter is
    absent (so the check never demands more than the legacy floor)."""
    if not isinstance(cfg, dict):
        return 1
    fm = cfg.get("front_matter")
    if not isinstance(fm, list) or not fm:
        return 1
    count = sum(1 for e in fm
                if isinstance(e, dict) and e.get("type") in _HEADERFREE_FRONTMATTER)
    # odd_page_sections appends a trailing EVEN_PAGE blank verso (also header-free).
    if (cfg.get("recto_strategy", "odd_page_sections") == "odd_page_sections"):
        count += 1
    return max(count, 1)


def check_empty_headers(docx: Path, cfg: dict = None):
    """Every header-free ceremonial/blank section must render an EMPTY header.

    A single stray empty header is NOT enough (the old rule); Word deduplicates
    header PARTS (one empty part is shared by many header-free SECTIONS), so we
    map each sectPr's headerReference -> header part -> empty? and count how many
    SECTIONS resolve to an empty header, then require that count to meet the
    expected header-free section count derived from config.front_matter. This is
    what closes the KDP 'text outside margins' gap: it confirms the empty-header
    fix reached the RIGHT sections, not merely that one empty header exists."""
    name = "empty_headers_on_headerfree_sections"
    if docx is None:
        return (name, False, "interior DOCX not found")
    try:
        with zipfile.ZipFile(docx) as z:
            header_parts = sorted(n for n in z.namelist()
                                  if re.match(r"word/header\d*\.xml$", n))
            if not header_parts:
                return (name, False, "no word/header*.xml parts present")
            # part filename -> is-empty
            part_empty = {}
            empties = 0
            summary = []
            for h in header_parts:
                texts = [t for t in _header_texts(z, h) if t.strip()]
                is_empty = not texts
                part_empty[h.split("/")[-1]] = is_empty
                if is_empty:
                    empties += 1
                    summary.append(f"{h.split('/')[-1]}=[]")
                else:
                    summary.append(f"{h.split('/')[-1]}={texts[:1]}")

            # Map rId -> header part filename via document.xml.rels, then walk
            # each sectPr's headerReference to classify SECTIONS (not parts).
            empty_ref_sections = None
            titled_ref_sections = None
            try:
                rels = z.read("word/_rels/document.xml.rels").decode("utf-8", "replace")
                rid_to_part = {}
                for m in re.finditer(
                        r'<Relationship\b[^>]*\bId="([^"]+)"[^>]*\bTarget="([^"]+)"[^>]*/>',
                        rels):
                    rid, target = m.group(1), m.group(2)
                    if "header" in target.lower():
                        rid_to_part[rid] = target.split("/")[-1]
                doc = z.read("word/document.xml").decode("utf-8", "replace")
                empty_ref_sections = 0
                titled_ref_sections = 0
                for m in re.finditer(r'<w:headerReference\b[^>]*\br:id="([^"]+)"', doc):
                    part = rid_to_part.get(m.group(1))
                    if part is None or part not in part_empty:
                        continue
                    if part_empty[part]:
                        empty_ref_sections += 1
                    else:
                        titled_ref_sections += 1
            except (KeyError, OSError):
                empty_ref_sections = None  # rels/document missing — fall back
    except (zipfile.BadZipFile, OSError) as exc:
        return (name, False, f"could not inspect headers: {exc}")

    expected = _expected_headerfree_sections(cfg)
    detail = "; ".join(summary)

    if empty_ref_sections is not None:
        # Section-mapped: require enough SECTIONS to reference an empty header.
        ok = empty_ref_sections >= expected
        detail += (f"  (sections->empty header: {empty_ref_sections}, "
                   f"->titled header: {titled_ref_sections}; "
                   f"expected >= {expected} header-free)")
        if not ok:
            detail += "  FAIL: fewer header-free sections than the front-matter demands"
        return (name, ok, detail)

    # Fallback (rels/document.xml unreadable): count empty header PARTS, and
    # report a lone empty as WEAK rather than a clean pass.
    ok = empties >= 1
    if not ok:
        detail += "  (NO empty header found — empty-header fix likely missing)"
    elif empties == 1 and empties < len(header_parts):
        detail += ("  WEAK: only one empty header PART and titled headers exist "
                   "(cannot confirm the fix reached the right sections)")
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


def check_book_min_pages(pdf: Path, cfg: dict):
    """HARD house floor (Bo's rule, 2026-07-12): no book ships under `min_pages`
    interior pages (default 75) unless explicitly approved. A thinner book yields
    an illegible spine (spine font scales with page count — LESSONS_LEDGER §16.1)
    and reads as a pamphlet. Override: set book_config.min_pages lower to record a
    deliberate exception, or 0 to disable."""
    name = "book_min_pages"
    floor = 75
    if isinstance(cfg, dict) and cfg.get("min_pages") is not None:
        try:
            floor = int(cfg["min_pages"])
        except (TypeError, ValueError):
            floor = 75
    if floor <= 0:
        return (name, True, f"floor disabled (min_pages={floor})")
    pages = _pdf_page_count(pdf) if pdf is not None else None
    if pages is None:
        return (name, False,
                f"no interior PDF to count against the {floor}-page house floor")
    if pages >= floor:
        return (name, True, f"{pages} pages >= {floor}-page house floor")
    return (name, False,
            f"{pages} pages is BELOW the {floor}-page house floor — too thin "
            f"(illegible spine, reads as a pamphlet). Lengthen the manuscript "
            f"(~28-34K words for 6x9), or set book_config.min_pages lower to record "
            f"a deliberate exception.")


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

    if fmt == "kdp_paperback":
        # SINGLE source of truth: preset_lookup.kdp_paperback_wrap_dims — the same
        # code path composite_cover.build_kdp_wrap builds from. No board add; every
        # knob passed through from book_config.spine so nothing is re-hardcoded.
        d = preset_lookup.kdp_paperback_wrap_dims(
            tw, th, pages, paper,
            per_page_cream=float(spine.get("per_page_cream", 0.0025)),
            per_page_white=float(spine.get("per_page_white", 0.002252)),
            bleed_in=float(spine.get("kdp_bleed_in", 0.125)))
        return (d["cover_w"], d["cover_h"])
    if fmt == "kdp_hardcover":
        # SINGLE source of truth: preset_lookup.kdp_hardcover_wrap_dims (white-only
        # spine math + board add + case-board turn-in + hardcoded case height).
        d = preset_lookup.kdp_hardcover_wrap_dims(
            tw, th, pages,
            per_page_white=float(spine.get("per_page_white", 0.002252)),
            board_add_in=float(spine.get("kdp_hardcover_board_add", 0.348)),
            turn_in_in=float(spine.get("kdp_hardcover_turn_in_in", 0.708)),
            height_in=float(spine.get("kdp_hardcover_height_in", 10.417)))
        return (d["cover_w"], d["cover_h"])
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


def check_cover_wrap_dims(cfg: dict, fmt: str, fmt_dir: Path, pages, final=False):
    """Compare the cover PDF MediaBox against the INDEPENDENTLY recomputed
    expected wrap dims (same formula/preset_lookup code path the compositor
    used), preferring the compositor's recorded PAGES from cover_meta.json.
    Also cross-checks the compositor's recorded target against the recompute —
    a disagreement there means the two sides diverged (a real bug).

    When `final` (the export/ship sweep, --final), a MISSING cover is a HARD
    fail: every format must carry its cover at ship time. During the ordinary
    interior-first pipeline (final=False) a not-yet-built cover soft-skips."""
    name = "cover_wrap_dimensions"
    cover = _find_cover_pdf(fmt_dir, fmt)
    if cover is None:
        if final:
            return (name, False, "FINAL verify: cover wrap PDF missing")
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

    # STALE-COVER reconciliation: cover_meta.json records the page count the
    # cover was composited for; the `pages` arg is the CURRENT interior PDF's
    # page count. If the interior shrank/grew since the cover was built, the
    # cover_meta target and its recompute both derive from the SAME (stale)
    # meta_pages and always agree with each other — so the only way to catch a
    # stale cover is to compare meta_pages against the live interior. When they
    # disagree, the expected dims must reflect the CURRENT interior (not the
    # stale meta), and this is a hard fail: recomposite the cover.
    stale_cover = (meta_pages is not None and pages is not None
                   and meta_pages != pages)
    if stale_cover:
        pages_used = pages
        pages_src = "interior PDF (cover_meta STALE)"
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

    if stale_cover:
        ok = False
        detail += (f"; STALE COVER: cover_meta pages={meta_pages} != interior "
                   f"PDF pages={pages} — recomposite the cover")
    return (name, ok, detail)


def _in_to_dxa(inches: float) -> int:
    """Inches -> DXA/twips (1440 per inch)."""
    return int(round(float(inches) * 1440))


def check_gutter_side(docx: Path, cfg: dict):
    """Under mirrorMargins, w:left is the INSIDE (gutter/spine-side) margin and
    w:right is the OUTSIDE margin (generate_book.js sets left=gutter,
    right=outside). Verify every body section's inside margin is >= its outside
    margin AND >= the configured gutter floor — closes the re-opened KDP
    'insufficient gutter' rejection (an existing mirror flag does NOT guarantee
    the gutter is on the correct/adequate side)."""
    name = "gutter_on_inside_and_adequate"
    if docx is None:
        return (name, False, "interior DOCX not found")
    try:
        with zipfile.ZipFile(docx) as z:
            doc = z.read("word/document.xml").decode("utf-8", "replace")
    except (KeyError, zipfile.BadZipFile, OSError) as exc:
        return (name, False, f"could not read word/document.xml: {exc}")
    pgmars = re.findall(r"<w:pgMar\b[^>]*/>", doc)
    if not pgmars:
        return (name, False, "no <w:pgMar> found in document.xml")
    # Gutter floor: config interior.gutter_in (schema default 0.75in = 1080 dxa).
    interior = (cfg or {}).get("interior") or {}
    try:
        gutter_floor_dxa = _in_to_dxa(float(interior.get("gutter_in", 0.75)))
    except (TypeError, ValueError):
        gutter_floor_dxa = _in_to_dxa(0.75)
    offenders = []
    below_floor = []
    checked = 0
    for i, pm in enumerate(pgmars):
        lm = re.search(r'\bw:left="(-?\d+)"', pm)
        rm = re.search(r'\bw:right="(-?\d+)"', pm)
        if not lm or not rm:
            continue
        left, right = int(lm.group(1)), int(rm.group(1))
        checked += 1
        if left < right:
            offenders.append(f"sect#{i}: inside(left)={left} < outside(right)={right}")
        if left < gutter_floor_dxa:
            below_floor.append(f"sect#{i}: inside(left)={left} < floor {gutter_floor_dxa}")
    problems = offenders + below_floor
    ok = not problems
    if ok:
        return (name, True, f"{checked} section(s): inside >= outside and "
                            f">= gutter floor {gutter_floor_dxa} dxa")
    return (name, False, "; ".join(problems[:6]))


def check_front_matter_valign(docx: Path, cfg: dict):
    """inject_front_matter_valign.js writes <w:vAlign w:val="..."> into each
    ceremonial front-matter section that declares a valign. Assert the DOCX
    carries at least as many vAlign elements of each declared value as the
    config demands (row 5 of the anti-forgetting matrix — was visual-only)."""
    name = "front_matter_valign_injected"
    fm = (cfg or {}).get("front_matter")
    if not isinstance(fm, list) or not fm:
        return (name, True, "no front_matter declared — nothing to check")
    want = {}
    for e in fm:
        if isinstance(e, dict) and e.get("valign"):
            want[e["valign"]] = want.get(e["valign"], 0) + 1
    if not want:
        return (name, True, "no front_matter entry declares a valign — skipped")
    if docx is None:
        return (name, False, "interior DOCX not found")
    try:
        with zipfile.ZipFile(docx) as z:
            doc = z.read("word/document.xml").decode("utf-8", "replace")
    except (KeyError, zipfile.BadZipFile, OSError) as exc:
        return (name, False, f"could not read word/document.xml: {exc}")
    have = {}
    for m in re.finditer(r'<w:vAlign\b[^>]*\bw:val="([^"]+)"', doc):
        have[m.group(1)] = have.get(m.group(1), 0) + 1
    missing = {v: (want[v], have.get(v, 0)) for v in want if have.get(v, 0) < want[v]}
    ok = not missing
    if ok:
        return (name, True, f"vAlign present: want {want}, have "
                            f"{ {v: have.get(v, 0) for v in want} }")
    return (name, False, f"vAlign MISSING/short (want,have): {missing} — "
                         f"inject_front_matter_valign not applied to all sections")


def check_mixam_spine_panel(cfg: dict, fmt_dir: Path, pages, final=False):
    """Mixam 3-panel hardcover ships an independent spine.pdf whose width is
    page-count dependent; only the front panel was ever measured. Recompute the
    expected spine-panel width the SAME way composite_cover.build_mixam does
    (spine_override wins, else pages*per_page(paper)+mixam_board_add, then
    +2*mixam_bleed for the panel), and compare the spine.pdf MediaBox width."""
    name = "mixam_spine_panel_width"
    spine_pdf = None
    if fmt_dir.exists():
        for p in sorted(fmt_dir.glob("*.pdf"),
                        key=lambda x: x.stat().st_mtime, reverse=True):
            n = p.name.lower()
            if n == "spine.pdf" or n.endswith("_spine.pdf"):
                spine_pdf = p
                break
    if spine_pdf is None:
        if final:
            return (name, False, "FINAL verify: mixam spine.pdf missing")
        return (name, True, "no spine.pdf yet (produced at the cover stage) — skipped")
    if pages is None:
        return (name, True, f"{spine_pdf.name} present; interior PAGES unknown so "
                            f"cannot recompute spine width (informational)")
    spine = (cfg or {}).get("spine") or {}
    paper = (cfg or {}).get("paper", "cream")
    override = spine.get("spine_override_in")
    if override is not None:
        try:
            spine_in = round(float(override), 4)
        except (TypeError, ValueError):
            spine_in = None
    else:
        per_page = (float(spine.get("per_page_cream", 0.0025)) if paper == "cream"
                    else float(spine.get("per_page_white", 0.002252)))
        board = float(spine.get("mixam_board_add", 0.110))
        spine_in = round(pages * per_page + board, 4)
    if spine_in is None:
        return (name, False, "could not compute expected mixam spine width")
    bleed = float(spine.get("mixam_bleed_in", 0.80))
    expected_panel_w = round(spine_in + 2 * bleed, 4)
    actual = _cover_mediabox_inches(spine_pdf)
    if actual is None:
        return (name, False, f"could not read MediaBox from {spine_pdf.name}")
    dw = abs(actual[0] - expected_panel_w)
    ok = dw <= 0.001
    return (name, ok, f"{spine_pdf.name}: spine panel width actual {actual[0]} vs "
                      f"expected {expected_panel_w} in (spine {spine_in}+2x{bleed} "
                      f"bleed; pages={pages}; Δw={dw:.4f}) — "
                      f"{'ok' if ok else 'MISMATCH — recomposite for the current page count'}")


def check_digital_pdf(cfg: dict, root: Path):
    """The digital/reader PDF is otherwise gated only by lint. Assert its
    structural invariants: it exists; the two front cover pages carry the exact
    trim MediaBox (build_digital_pdf sets 432x648 pt for 6x9 via fitz — PIL
    truncation would drift it); and it has >= 3 pages (2 covers + >=1 interior),
    which also fails if the interior was not concatenated."""
    name = "digital_pdf_structure"
    fmt_dir = root / "outputs" / "digital"
    slug = (cfg or {}).get("slug")
    pdf = None
    if slug:
        cand = fmt_dir / f"{slug}_DIGITAL.pdf"
        if cand.exists():
            pdf = cand
    if pdf is None:
        pdf = find_one(fmt_dir, "_DIGITAL.pdf") or find_one(fmt_dir, ".pdf")
    if pdf is None:
        return (name, False, f"digital PDF not found under {fmt_dir}")
    # Expected cover-page MediaBox = trim (inches) * 72, matching build_digital_pdf.
    trim = (cfg or {}).get("trim") or {}
    exp_w = round(float(trim.get("w", 6)) * 72.0, 3)
    exp_h = round(float(trim.get("h", 9)) * 72.0, 3)
    try:
        import fitz
        with fitz.open(str(pdf)) as doc:
            n = len(doc)
            if n < 3:
                return (name, False, f"{pdf.name}: {n} pages — expected >= 3 "
                                     f"(2 covers + >=1 interior; interior not concatenated?)")
            problems = []
            for idx in (0, 1):
                r = doc[idx].rect
                if abs(r.width - exp_w) > 0.01 or abs(r.height - exp_h) > 0.01:
                    problems.append(f"page{idx+1} MediaBox {r.width:.3f}x{r.height:.3f} pt "
                                    f"!= expected {exp_w}x{exp_h} pt")
    except Exception as exc:
        return (name, False, f"could not open digital PDF with fitz: {exc}")
    ok = not problems
    if ok:
        return (name, True, f"{pdf.name}: {n} pages; both cover pages exact "
                            f"{exp_w}x{exp_h} pt MediaBox")
    return (name, False, "; ".join(problems))


# Raw LaTeX/math delimiters that must NOT survive into an ebook body (they must
# have been converted to Unicode/Cambria-Math glyphs). Compound hyphens and
# ordinary '$' currency are NOT these markers.
_LATEX_MARKERS = (r"\(", r"\)", r"\[", r"\]", r"\frac", r"\sqrt", r"\sum",
                  r"\int", r"\alpha", r"\beta", r"\gamma", r"\theta", r"\times",
                  r"\cdot", r"\begin{", r"\end{")


def _book_is_math(cfg: dict) -> bool:
    """A math book is a non-fiction title whose LaTeX->Unicode path is engaged
    (is_fiction false). Explicit book_config.math or book_config.is_math wins."""
    if not isinstance(cfg, dict):
        return False
    for key in ("math", "is_math", "has_math"):
        if isinstance(cfg.get(key), bool):
            return cfg[key]
    return cfg.get("is_fiction") is False


def check_no_residual_latex(root: Path, cfg: dict, fmt: str):
    """Row 16 of the matrix: for a math book, no raw LaTeX delimiter may survive
    into the Kindle/EPUB body (the LaTeX->Unicode transform must have run). Only
    fires when the book is flagged math; otherwise it is a no-op pass."""
    name = "no_residual_latex_math"
    if not _book_is_math(cfg):
        return (name, True, "book not flagged as math — LaTeX check skipped")
    bodies = []
    try:
        if fmt == "epub":
            epub = find_one(root / "outputs" / "epub", ".epub")
            if epub is None:
                return (name, True, "no .epub to scan (informational)")
            with zipfile.ZipFile(epub) as z:
                for nn in z.namelist():
                    if nn.startswith("OEBPS/text/") and nn.endswith(".xhtml"):
                        bodies.append(z.read(nn).decode("utf-8", "replace"))
        else:  # kindle DOCX
            kindle = find_one(root / "outputs" / "kindle", ".docx",
                              prefer_substr=["kindle"])
            if kindle is None:
                return (name, True, "no kindle DOCX to scan (informational)")
            with zipfile.ZipFile(kindle) as z:
                bodies.append(z.read("word/document.xml").decode("utf-8", "replace"))
    except (zipfile.BadZipFile, OSError, KeyError) as exc:
        return (name, False, f"could not scan body for LaTeX: {exc}")
    joined = "\n".join(bodies)
    hits = sorted({mk for mk in _LATEX_MARKERS if mk in joined})
    # Inline $...$ math (a $ pair on one line with a letter/backslash between).
    if re.search(r"\$[^$\n]*[\\A-Za-z][^$\n]*\$", joined):
        hits.append("$...$")
    ok = not hits
    if ok:
        return (name, True, "no residual raw LaTeX delimiters in the ebook body")
    return (name, False, f"residual raw LaTeX survived into the {fmt} body: "
                         f"{hits[:8]} — the LaTeX->Unicode transform did not run")


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


def check_epub_parity(root: Path, cfg: dict, final: bool = False):
    """EPUB body word count must NOT be below the print word count."""
    name = "epub_wordcount_parity_not_below_print"
    epub = find_one(root / "outputs" / "epub", ".epub")
    if epub is None:
        return (name, False, "no .epub found")
    ew = _epub_body_word_count(epub)
    print_docx = None
    for sub in ("kdp_paperback", "kdp_hardcover", "mixam_hardcover",
                "mixam_paperback", "blurb_paperback", "blurb_hardcover"):
        print_docx = find_one(root / "outputs" / sub, ".docx")
        if print_docx is not None:
            break
    pw = _docx_word_count(print_docx)
    if ew is None:
        return (name, False, "could not count EPUB words")
    if pw is None:
        # never a vacuous pass when this book DECLARES a print edition: interim
        # verifies say DEFERRED loudly; the final sweep hard-fails until the
        # print baseline exists to compare against
        declared = [f for f in (cfg.get("formats") or []) if f in PRINT_FORMATS]
        if declared and final:
            return (name, False,
                    f"epub={ew} words; print format(s) {', '.join(declared)} declared but no "
                    f"print DOCX found — parity NOT verified; build print first")
        if declared:
            return (name, True, f"epub={ew} words; parity DEFERRED (print "
                                f"{', '.join(declared)} not built yet — the final sweep enforces)")
        return (name, True, f"epub={ew} words; no print format declared (ebook-only) — parity n/a")
    # Print DOCX carries front matter the EPUB body count excludes; allow a
    # small ceremonial allowance but never a body-sized shortfall.
    ok = ew >= pw - 150
    return (name, ok, f"epub body={ew} words vs print={pw} words "
                      f"({'parity ok' if ok else 'BELOW print — source drift!'})")


def check_kindle_parity(root: Path, cfg: dict, final: bool = False):
    """Kindle word count must NOT be below the print word count (never short)."""
    name = "kindle_wordcount_parity_not_below_print"
    kindle = find_one(root / "outputs" / "kindle", ".docx",
                      prefer_substr=["kindle"])
    print_docx = None
    for sub in ("kdp_paperback", "kdp_hardcover", "mixam_hardcover",
                "mixam_paperback", "blurb_paperback", "blurb_hardcover"):
        print_docx = find_one(root / "outputs" / sub, ".docx",
                              prefer_substr=["kdp", "mixam", "paperback", "hardcover",
                                             "blurb", "inner_"])
        if print_docx is not None:
            break
    kw = _docx_word_count(kindle)
    pw = _docx_word_count(print_docx)
    if kw is None:
        return (name, False, "kindle DOCX not found / unreadable")
    if pw is None:
        # never a vacuous pass: a declared print edition with no baseline on
        # disk is exactly how the 8,476-words-short Kindle shipped. Interim
        # verifies say DEFERRED loudly; the final sweep hard-fails.
        declared = [f for f in (cfg.get("formats") or []) if f in PRINT_FORMATS]
        if declared and final:
            return (name, False,
                    f"kindle={kw} words; print format(s) {', '.join(declared)} declared but no "
                    f"print DOCX found — parity NOT verified; build print first")
        if declared:
            return (name, True, f"kindle={kw} words; parity DEFERRED (print "
                                f"{', '.join(declared)} not built yet — the final sweep enforces)")
        return (name, True, f"kindle={kw} words; no print format declared (ebook-only) — parity n/a")
    ok = kw >= pw
    return (name, ok, f"kindle={kw} words vs print={pw} words "
                      f"({'>= print, ok' if ok else 'BELOW print — source drift!'})")


_EM_DASH_SET = "—–―‒−"  # mirrors lint_manuscript EM_DASHES (§17 HARD gate)
_EM_DASH_ENTITY = re.compile(r"&#(?:8210|8211|8212|8213|8722);|&(?:mdash|ndash|horbar|minus);")


def check_no_artifact_emdash(path, cfg: dict):
    """The §17 em-dash gate applied to the RENDERED artifact (docx/epub) — the
    markdown-source lint can never see a dash a GENERATOR injects (epigraph
    attribution prefixes were shipping one). Scans extracted document text plus
    headers/footers (docx) and every xhtml/opf/ncx (epub)."""
    name = "no_emdash_in_rendered_artifact"
    if not ((cfg.get("voice") or {}).get("no_em_dashes", True)):
        return (name, True, "voice.no_em_dashes=false — artifact dash scan n/a")
    if path is None or not Path(path).exists():
        return (name, False, "artifact not found — artifact dash scan could not run")
    path = Path(path)
    hits = []
    try:
        with zipfile.ZipFile(path) as z:
            for member in z.namelist():
                if path.suffix.lower() == ".docx":
                    if member != "word/document.xml" and not re.match(
                            r"word/(?:header|footer)\d*\.xml$", member):
                        continue
                    xml = z.read(member).decode("utf-8", "replace")
                    text = " ".join(re.findall(r"<w:t[^>]*>([^<]*)</w:t>", xml))
                elif member.lower().endswith((".xhtml", ".html", ".opf", ".ncx")):
                    xml = z.read(member).decode("utf-8", "replace")
                    text = re.sub(r"<[^>]+>", " ", xml)
                else:
                    continue
                for ch in _EM_DASH_SET:
                    i = text.find(ch)
                    if i >= 0:
                        ctx = text[max(0, i - 24):i + 24].strip()
                        hits.append(f"{member}: U+{ord(ch):04X} ...{ctx}...")
                        break
                if _EM_DASH_ENTITY.search(xml):
                    hits.append(f"{member}: numeric/named dash entity")
    except (zipfile.BadZipFile, OSError, KeyError) as exc:
        return (name, False, f"could not scan artifact: {exc}")
    ok = not hits
    return (name, ok, "rendered text clean (zero em/en dashes)" if ok
            else "; ".join(hits[:4]))


# ─────────────────────────────────────────────────────────────────────────────
# driver
# ─────────────────────────────────────────────────────────────────────────────

def run_checks(cfg: dict, config_path: Path, root: Path, fmt: str,
               final: bool = False) -> list:
    checks = []
    fmt_dir = root / "outputs" / FORMAT_DIR.get(fmt, fmt)

    if fmt in PRINT_FORMATS:
        docx = find_one(fmt_dir, ".docx",
                        prefer_substr=["kdp", "mixam", "paperback", "hardcover",
                                       "blurb", "inner_"])
        pdf = _find_interior_pdf(fmt_dir)

        checks.append(check_mirror_flags(docx))
        checks.append(check_gutter_side(docx, cfg))
        checks.append(check_empty_headers(docx, cfg))
        checks.append(check_front_matter_valign(docx, cfg))
        checks.append(check_no_artifact_emdash(docx, cfg))
        checks.append(check_recto_parity(docx, config_path))
        checks.append(check_page_multiple(pdf, fmt))
        note = check_min_pages_note(pdf, fmt)   # INFORMATIONAL, never fails
        if note is not None:
            checks.append(note)
        checks.append(check_book_min_pages(pdf, cfg))   # HARD 75-page house floor (§16.5)
        checks.append(check_pages_match_compositor(pdf, fmt_dir))
        pages = _pdf_page_count(pdf) if pdf is not None else None
        checks.append(check_cover_wrap_dims(cfg, fmt, fmt_dir, pages, final=final))
        if fmt == "mixam_hardcover":
            checks.append(check_mixam_spine_panel(cfg, fmt_dir, pages, final=final))

    if fmt == "digital_pdf":
        checks.append(check_digital_pdf(cfg, root))

    if fmt == "kindle":
        checks.append(check_kindle_parity(root, cfg, final=final))
        checks.append(check_no_residual_latex(root, cfg, "kindle"))
        checks.append(check_no_artifact_emdash(
            find_one(root / "outputs" / "kindle", ".docx", prefer_substr=["kindle"]), cfg))

    if fmt == "epub":
        checks.append(check_epub_structure(fmt_dir))
        checks.append(check_epub_parity(root, cfg, final=final))
        checks.append(check_no_residual_latex(root, cfg, "epub"))
        checks.append(check_no_artifact_emdash(find_one(fmt_dir, ".epub"), cfg))

    # lint runs for every format (voice + corruption gate).
    checks.append(check_lint(config_path))

    return checks


CHECK_CONTINUITY = SCRIPT_DIR / "check_continuity.py"


def _run_continuity_check(root: Path):
    """Run the sibling check_continuity.py against the workspace's _CONTINUITY.md
    (final/export sweep only). Returns {"all_pass", "detail"} or None if there is
    no ledger to validate (absence is not a failure — not every workspace keeps
    one)."""
    ledger = root / "_CONTINUITY.md"
    if not ledger.exists():
        return None
    if not CHECK_CONTINUITY.exists():
        return {"all_pass": False,
                "detail": f"check_continuity.py not found at {CHECK_CONTINUITY}"}
    try:
        proc = subprocess.run(
            [sys.executable, str(CHECK_CONTINUITY), "--workspace", str(root)],
            capture_output=True, text=True, timeout=120)
    except (subprocess.SubprocessError, OSError) as exc:
        return {"all_pass": False, "detail": f"continuity check failed to run: {exc}"}
    out = (proc.stdout or "").strip().splitlines()
    detail = out[-1] if out else f"exit {proc.returncode}"
    return {"all_pass": proc.returncode == 0, "detail": detail}


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

    ap = argparse.ArgumentParser(
        description="Mechanical build verifier (spec checks -> pass/fail JSON).")
    ap.add_argument("--config", required=True, help="Path to book_config.json.")
    ap.add_argument("--format", required=True,
                    choices=FORMAT_CHOICES + ["all"],
                    help="Which format profile to verify ('all' sweeps every "
                         "format and fails if ANY fails).")
    ap.add_argument("--root", help="Override the workspace root "
                                   "(default: book_workspace/<slug>/).")
    ap.add_argument("--final", action="store_true",
                    help="FINAL/ship sweep: a missing cover is a HARD fail "
                         "(export v1.0 passes this); also validates _CONTINUITY.md.")
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

    # --format all: fan out over every format, aggregate, fail if ANY fails.
    if args.format == "all":
        per_format = {}
        overall = True
        for fmt in FORMAT_CHOICES:
            checks_raw = run_checks(cfg, config_path, root, fmt, final=args.final)
            checks = [{"name": n, "pass": bool(ok), "detail": d}
                      for (n, ok, d) in checks_raw]
            fmt_pass = all(c["pass"] for c in checks) if checks else False
            per_format[fmt] = {"all_pass": fmt_pass, "checks": checks}
            overall = overall and fmt_pass
        continuity = _run_continuity_check(root) if args.final else None
        if continuity is not None:
            per_format["_continuity"] = continuity
            overall = overall and continuity["all_pass"]
        print(json.dumps({"format": "all", "root": str(root),
                          "final": bool(args.final),
                          "all_pass": overall, "formats": per_format},
                         ensure_ascii=False, indent=2))
        return 0 if overall else 1

    checks_raw = run_checks(cfg, config_path, root, args.format, final=args.final)
    checks = [{"name": n, "pass": bool(ok), "detail": d} for (n, ok, d) in checks_raw]
    if args.final:
        continuity = _run_continuity_check(root)
        if continuity is not None:
            checks.append({"name": "continuity_ledger_consistent",
                           "pass": continuity["all_pass"],
                           "detail": continuity["detail"]})
    all_pass = all(c["pass"] for c in checks) if checks else False

    print(json.dumps({"format": args.format, "root": str(root),
                      "final": bool(args.final),
                      "all_pass": all_pass, "checks": checks},
                     ensure_ascii=False, indent=2))
    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(main())
