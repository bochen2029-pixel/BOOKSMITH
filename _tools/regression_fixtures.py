#!/usr/bin/env python3
r"""
regression_fixtures.py — generator behavior regression (the QC-sweep fixture).

Runs BOTH interior generators (generate_book.js kdp_paperback + generate_kindle.js)
over a tiny synthetic book engineered to hit every historically-defective input,
then unzips the DOCX output and asserts the RENDERED text is right. These are the
defects that were invisible under default configs and shipped silently:

  1. currency  — "$14.99 ... $24.99" on one line stays literal prose (dollars
                 kept), never a Cambria-Math run (nonfiction book, math ON).
  2. real math — \rightarrow / \cdots / \bigcup convert to → ⋯ ⋃ (the strippers
                 and the longest-first table hold).
  3. deep headings — an "#### H4" renders as a subsection heading, never body
                 text with literal hashes.
  4. bold+code — **`--config`** renders without orphaned literal ** runs.
  5. dashes    — zero U+2014/2013/2015/2012/2212 anywhere in the rendered text
                 (epigraph attribution included) under no_em_dashes.
  6. even/odd  — with interior.page_number_align="outer", settings.xml carries
                 an ENABLED <w:evenAndOddHeaders/> (not w:val="false").
  7. [IMAGE    — a prose line starting "[IMAGES were everywhere]" is NOT eaten.
  8. midflow   — a standalone "![alt](images/x.png)" line: kindle EMBEDS the
                 original, print EMBEDS too (2026-07-27, the figure-program
                 feature) and must prefer the grayscale "x_print.png" sibling
                 when present, build_epub embeds it as <figure class="midflow">
                 — and the literal markdown never reaches any rendered artifact.

Workspace is a fresh temp dir (config-parent rooted — nothing in the repo is
touched). Needs node + the vendored _tools/node_modules; exits 2 SKIP without
(the epub leg is pure Python and runs regardless).

Usage:  python _tools/regression_fixtures.py [--json]
Exit:   0 all assertions hold · 1 regression · 2 environment missing
"""
from __future__ import annotations
import json
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
ROOT = TOOLS.parent

MASTER = """# Chapter One

The book is $14.99 in paperback and $24.99 hardcover; the audiobook waits.

As $x \\rightarrow \\infty$ the series $a_1, \\cdots, a_n$ collects into $\\bigcup_{i=1}^{n} A_i$.

Run **`--config`** before anything else. *Steady now.*

- **The brain (`d3`), honestly labeled.** A cell can become one.

#### A Deep Subsection

[IMAGES were everywhere] and the crowd still would not look away.

![test photo](images/mf_test.png)

A caption line under the photo.

Body continues, plain and unhurried, with enough words to look like prose.
"""

CONFIG = {
    "title": "Regression Fixture",
    "subtitle": "The Defect Gauntlet",
    "author": "BOOKSMITH QC",
    "slug": "_regfix",
    "is_fiction": False,
    "formats": ["kdp_paperback", "kindle"],
    "min_pages": 1,
    "epigraph": {"text": "Every gate earns its keep.", "attribution": "The Ledger"},
    "front_matter": [{"type": "half_title"}, {"type": "title"},
                     {"type": "copyright"}, {"type": "epigraph"}],
    "interior": {"page_number_align": "outer"},
    "voice": {"unit_noun": "chapter", "no_em_dashes": True, "blacklist": []},
    "units": [{"id": "ch_01", "title": "Chapter One", "class": "C", "target_words": 80}],
}

DASHES = "—–―‒−"


def docx_text_and_settings(docx: Path):
    with zipfile.ZipFile(docx) as z:
        doc = z.read("word/document.xml").decode("utf-8", "replace")
        try:
            settings = z.read("word/settings.xml").decode("utf-8", "replace")
        except KeyError:
            settings = ""
        media = [n for n in z.namelist() if n.startswith("word/media/")]
        media_bytes = [z.read(n) for n in media]
    runs = re.findall(r"<w:t[^>]*>([^<]*)</w:t>", doc)
    # content assertions join with NO separator: adjacent runs in one paragraph
    # render adjacent ("$" + "24.99" is "$24.99" on the page)
    return runs, "".join(runs), settings, media, media_bytes


def tiny_png(path: Path, w=8, h=6, rgb=(180, 40, 40)):
    """Write a minimal valid RGB PNG (stdlib only) for image-embed fixtures."""
    import struct
    import zlib

    def chunk(tag, data):
        return (struct.pack(">I", len(data)) + tag + data
                + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF))

    raw = b"".join(b"\x00" + bytes(rgb) * w for _ in range(h))
    png = (b"\x89PNG\r\n\x1a\n"
           + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0))
           + chunk(b"IDAT", zlib.compress(raw))
           + chunk(b"IEND", b""))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(png)


def main(argv=None) -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    as_json = "--json" in (argv or sys.argv[1:])

    if not shutil.which("node") or not (TOOLS / "node_modules" / "docx").is_dir():
        print(json.dumps({"status": "skip", "detail": "node or vendored node_modules absent"})
              if as_json else "regression_fixtures: SKIP (node/node_modules absent)")
        return 2

    ws = Path(tempfile.mkdtemp(prefix="bs_regfix_"))
    fails: list[str] = []
    try:
        (ws / "manuscript" / "current").mkdir(parents=True)
        (ws / "outputs" / "markdown").mkdir(parents=True)
        (ws / "book_config.json").write_text(json.dumps(CONFIG, indent=2), encoding="utf-8")
        (ws / "outputs" / "markdown" / "_regfix_v1.md").write_text(MASTER, encoding="utf-8")
        tiny_png(ws / "images" / "mf_test.png")
        # Grayscale-derivative sibling: print must PREFER this over the original.
        tiny_png(ws / "images" / "mf_test_print.png", w=10, h=8, rgb=(60, 60, 60))
        tiny_png(ws / "cover_art" / "_regfix_src.png")  # epub leg needs a cover

        for gen, outname in (("generate_book.js", None), ("generate_kindle.js", None)):
            cmd = ["node", str(TOOLS / gen), "--config", str(ws / "book_config.json")]
            if gen == "generate_book.js":
                cmd += ["--format", "kdp_paperback"]
            r = subprocess.run(cmd, capture_output=True, text=True,
                               encoding="utf-8", errors="replace", timeout=180)
            if r.returncode != 0:
                fails.append(f"{gen} rc={r.returncode}: {(r.stderr or r.stdout).strip()[-200:]}")

        checks = []
        for label, docx in (("print", ws / "outputs" / "kdp_paperback" / "_regfix_KDP_PAPERBACK.docx"),
                            ("kindle", ws / "outputs" / "kindle" / "_regfix_KINDLE.docx")):
            if not docx.exists():
                fails.append(f"{label}: DOCX not produced at {docx}")
                continue
            runs, text, settings, media, media_bytes = docx_text_and_settings(docx)
            def chk(name, ok, detail=""):
                checks.append({"target": label, "check": name, "pass": bool(ok), "detail": detail})
                if not ok:
                    fails.append(f"{label}/{name}: {detail}")
            chk("currency_literal", "$14.99" in text and "$24.99" in text,
                "dollar amounts must survive as literal prose")
            chk("math_converts", ("→" in text and "⋯" in text and "⋃" in text),
                f"expected → ⋯ ⋃ in rendered text")
            chk("no_literal_hashes", "####" not in text,
                "H4 heading leaked as body text with hashes")
            chk("h4_text_present", "A Deep Subsection" in text, "H4 content missing")
            chk("no_orphan_bold_markers", not any(t.strip() == "**" for t in runs),
                "orphaned ** run from bold-wrapped code")
            chk("no_literal_doublestar", "**" not in text,
                "literal ** reached the rendered artifact (bold span failed to pair)")
            chk("bold_across_code_intact",
                "The brain (" in text and "), honestly labeled." in text and "d3" in text,
                "bold-span-containing-code content missing or mangled")
            chk("no_dashes_rendered", not any(ch in text for ch in DASHES),
                "em/en dash reached the rendered artifact")
            chk("epigraph_attribution", "The Ledger" in text, "epigraph attribution missing")
            chk("image_prose_kept", "the crowd still would not look away" in text,
                "[IMAGES prose line was eaten by the image-block skip")
            chk("no_literal_md_image", "![test photo]" not in text,
                "literal markdown image line reached the rendered artifact")
            chk("midflow_caption_kept", "A caption line under the photo." in text,
                "caption paragraph after the mid-flow image was lost")
            chk("midflow_embedded", len(media) >= 1,
                f"expected >=1 word/media entry (mid-flow image), got {len(media)}")
            orig_b = (ws / "images" / "mf_test.png").read_bytes()
            print_b = (ws / "images" / "mf_test_print.png").read_bytes()
            if label == "kindle":
                chk("midflow_original_variant", any(b == orig_b for b in media_bytes),
                    "kindle must embed the ORIGINAL (color) mid-flow image")
            if label == "print":
                chk("midflow_print_variant",
                    any(b == print_b for b in media_bytes)
                    and not any(b == orig_b for b in media_bytes),
                    "print must prefer the grayscale _print sibling over the original")
            if label == "print":
                enabled = re.search(r"<w:evenAndOddHeaders\b(?![^>]*w:val=\"(?:false|0)\")", settings)
                chk("evenAndOddHeaders_enabled", bool(enabled),
                    "outer page numbers need the ENABLED flag in settings.xml")

        # ---- EPUB leg (pure Python): mid-flow image embeds as figure.midflow ----
        r = subprocess.run([sys.executable, str(TOOLS / "build_epub.py"),
                            "--config", str(ws / "book_config.json")],
                           capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=180)
        epub = ws / "outputs" / "epub" / "_regfix.epub"
        if r.returncode != 0:
            fails.append(f"build_epub rc={r.returncode}: {(r.stderr or r.stdout).strip()[-300:]}")
        if epub.exists():
            def echk(name, ok, detail=""):
                checks.append({"target": "epub", "check": name, "pass": bool(ok), "detail": detail})
                if not ok:
                    fails.append(f"epub/{name}: {detail}")
            with zipfile.ZipFile(epub) as z:
                nm = z.namelist()
                mf = [n for n in nm if n.startswith("OEBPS/images/mf_")]
                ch1 = ""
                for n in nm:
                    if n.endswith("ch_01.xhtml"):
                        ch1 = z.read(n).decode("utf-8", "replace")
            echk("midflow_file_embedded", len(mf) == 1,
                 f"OEBPS/images mf_* count={len(mf)} (want 1)")
            echk("midflow_figure_referenced",
                 'class="midflow"' in ch1 and "mf_001_mf_test.png" in ch1,
                 "figure.midflow with the image ref missing from ch_01.xhtml")
            echk("no_literal_md_image", "![test photo]" not in ch1,
                 "literal markdown image line leaked into the XHTML")
            echk("midflow_caption_kept", "A caption line under the photo." in ch1,
                 "caption paragraph after the mid-flow image was lost")
        else:
            fails.append(f"epub: not produced at {epub}")

        status = "pass" if not fails else "fail"
        out = {"status": status, "workspace": str(ws), "checks": checks, "fails": fails}
        if as_json:
            print(json.dumps(out, ensure_ascii=False, indent=2))
        else:
            for c in checks:
                print(f"  [{'OK ' if c['pass'] else 'XX '}] {c['target']:6} {c['check']}"
                      + ("" if c["pass"] else f" -- {c['detail']}"))
            print(f"REGRESSION_FIXTURES: {'PASS' if status == 'pass' else 'FAIL'} "
                  f"({len(checks)} checks, {len(fails)} fail)")
        return 0 if status == "pass" else 1
    finally:
        shutil.rmtree(ws, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
