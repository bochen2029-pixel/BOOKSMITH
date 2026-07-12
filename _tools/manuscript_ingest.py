#!/usr/bin/env python3
r"""
manuscript_ingest.py — normalize source documents to clean markdown (BOOKSMITH).

Real operators drop PDFs / DOCX / EPUB / HTML on day one, not tidy markdown. This
converts any such source into clean-ish markdown so the engine's `stage_ingest` (and
the interactive ingest) can size, digest, and synthesize from ONE uniform corpus.
It is the front-door companion to the deterministic engine's INGEST stage: the engine
calls it to flatten `intake/` before it writes relational digests.

Converters (dependency-light on purpose):
  .pdf              -> PyMuPDF (fitz) text extraction, page by page. fitz is an
                       OPTIONAL dep (already used by the cover tools); if it is not
                       installed, PDFs are skipped with a clear note, never a crash.
  .docx             -> stdlib zipfile + xml: word/document.xml paragraphs, with
                       Heading1-6 styles mapped to markdown '#' levels.
  .epub             -> stdlib zipfile + xml/html: the OPF spine XHTML in reading
                       order, tags stripped to text (headings preserved).
  .htm / .html      -> stdlib html.parser tag strip (headings preserved).
  .md / .txt        -> passthrough (already text; only with --include-text).

CONTRACT
  python manuscript_ingest.py --intake <DIR> --out <DIR> [--force] [--include-text]
      -> writes <out>/<stem>.md for every convertible source under <DIR> (top level);
         idempotent (skips a source whose <out>/<stem>.md is newer, unless --force);
         prints a JSON summary {converted, skipped, failed, files:[...]}.
  python manuscript_ingest.py --src <FILE> [--out <FILE|DIR>]
      -> convert a single file (prints the output path).
  python manuscript_ingest.py --selftest
      -> build tiny DOCX/EPUB/HTML fixtures in a temp dir, convert, assert. No deps.

SOURCE
  new for roadmap H1.2 ("the Manuscript Ingest converter"). stdlib only except the
  optional fitz path for PDF (declared via PyMuPDF, shared with the cover tools).
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import zipfile
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from pathlib import Path

DOC_EXT = {".pdf", ".docx", ".epub", ".htm", ".html"}
TEXT_EXT = {".md", ".txt", ".markdown"}


# ---------------------------------------------------------------------------
# HTML / XHTML -> text (headings preserved, script/style dropped)
# ---------------------------------------------------------------------------
class _HTMLText(HTMLParser):
    _BLOCK = {"p", "div", "br", "li", "tr", "section", "article",
              "h1", "h2", "h3", "h4", "h5", "h6"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self._skip = 0

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style"):
            self._skip += 1
        elif tag in self._BLOCK:
            self.parts.append("\n")
            if len(tag) == 2 and tag[0] == "h" and tag[1].isdigit():
                self.parts.append("#" * int(tag[1]) + " ")

    def handle_endtag(self, tag):
        if tag in ("script", "style") and self._skip:
            self._skip -= 1
        elif tag in self._BLOCK:
            self.parts.append("\n")

    def handle_data(self, data):
        if not self._skip:
            self.parts.append(data)


def strip_html(html_text: str) -> str:
    p = _HTMLText()
    try:
        p.feed(html_text)
    except Exception:
        pass
    raw = "".join(p.parts)
    out, blank = [], False
    for ln in raw.splitlines():
        ln = re.sub(r"[ \t]+", " ", ln).strip()
        if ln:
            out.append(ln)
            blank = False
        elif not blank:
            out.append("")
            blank = True
    return "\n".join(out).strip()


# ---------------------------------------------------------------------------
# per-format converters -> markdown string
# ---------------------------------------------------------------------------
def pdf_to_md(path: Path) -> str:
    try:
        import fitz  # PyMuPDF (optional; shared with the cover tools)
    except ImportError:
        raise RuntimeError("PDF conversion needs PyMuPDF (fitz); pip install PyMuPDF")
    doc = fitz.open(str(path))
    try:
        pages = [page.get_text("text").strip() for page in doc]
    finally:
        doc.close()
    return "\n\n".join(t for t in pages if t)


def docx_to_md(path: Path) -> str:
    W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
    with zipfile.ZipFile(path) as z:
        root = ET.fromstring(z.read("word/document.xml"))
    out: list[str] = []
    for p in root.iter(f"{W}p"):
        style = ""
        ppr = p.find(f"{W}pPr")
        if ppr is not None:
            ps = ppr.find(f"{W}pStyle")
            if ps is not None:
                style = ps.get(f"{W}val", "")
        text = "".join(t.text or "" for t in p.iter(f"{W}t")).strip()
        if not text:
            continue
        m = re.match(r"(?i)heading\s*([1-6])", style)
        out.append(("#" * int(m.group(1)) + " " + text) if m else text)
    return "\n\n".join(out)


def epub_to_md(path: Path) -> str:
    OPF = "{http://www.idpf.org/2007/opf}"
    CN = {"c": "urn:oasis:names:tc:opendocument:xmlns:container"}
    with zipfile.ZipFile(path) as z:
        names = set(z.namelist())
        opf_path = None
        if "META-INF/container.xml" in names:
            try:
                c = ET.fromstring(z.read("META-INF/container.xml"))
                rf = c.find(".//c:rootfile", CN)
                if rf is not None:
                    opf_path = rf.get("full-path")
            except Exception:
                opf_path = None
        if not opf_path:
            opf_path = next((n for n in sorted(names) if n.endswith(".opf")), None)
        order: list[str] = []
        if opf_path and opf_path in names:
            opf = ET.fromstring(z.read(opf_path))
            base = opf_path.rsplit("/", 1)[0] + "/" if "/" in opf_path else ""
            idmap = {it.get("id"): it.get("href") for it in opf.iter(f"{OPF}item")}
            for ref in opf.iter(f"{OPF}itemref"):
                href = idmap.get(ref.get("idref"))
                if href:
                    order.append(base + href)
        if not order:
            order = sorted(n for n in names if n.endswith((".xhtml", ".html", ".htm")))
        parts = []
        for href in order:
            if href in names and href.endswith((".xhtml", ".html", ".htm")):
                parts.append(strip_html(z.read(href).decode("utf-8", "replace")))
    return "\n\n".join(p for p in parts if p.strip())


def html_to_md(path: Path) -> str:
    return strip_html(path.read_text(encoding="utf-8", errors="replace"))


def convert_file(path: Path) -> str:
    ext = path.suffix.lower()
    if ext == ".pdf":
        return pdf_to_md(path)
    if ext == ".docx":
        return docx_to_md(path)
    if ext == ".epub":
        return epub_to_md(path)
    if ext in (".htm", ".html"):
        return html_to_md(path)
    if ext in TEXT_EXT:
        return path.read_text(encoding="utf-8", errors="replace")
    raise RuntimeError(f"unsupported source type: {ext}")


# ---------------------------------------------------------------------------
# batch driver
# ---------------------------------------------------------------------------
def slugify(stem: str) -> str:
    return re.sub(r"[^a-z0-9_]+", "_", stem.lower()).strip("_") or "src"


def convert_dir(intake: Path, out: Path, force: bool, include_text: bool) -> dict:
    out.mkdir(parents=True, exist_ok=True)
    want = set(DOC_EXT) | (TEXT_EXT if include_text else set())
    summary = {"converted": 0, "skipped": 0, "failed": 0, "files": []}
    for src in sorted(intake.iterdir()):
        if not src.is_file() or src.suffix.lower() not in want:
            continue
        dest = out / f"{slugify(src.stem)}.md"
        if dest.exists() and not force and dest.stat().st_mtime >= src.stat().st_mtime:
            summary["skipped"] += 1
            summary["files"].append({"src": src.name, "out": dest.name, "status": "skipped"})
            continue
        try:
            md = convert_file(src).strip()
            dest.write_text(f"# Source: {src.name}\n\n{md}\n", encoding="utf-8")
            summary["converted"] += 1
            summary["files"].append({"src": src.name, "out": dest.name,
                                     "status": "converted", "words": len(md.split())})
        except Exception as e:
            summary["failed"] += 1
            summary["files"].append({"src": src.name, "status": "failed", "error": str(e)[:160]})
    return summary


# ---------------------------------------------------------------------------
# self-test (no external deps: builds a tiny DOCX/EPUB/HTML and converts them)
# ---------------------------------------------------------------------------
def _write_min_docx(path: Path) -> None:
    W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
    doc = (f'<?xml version="1.0"?><w:document xmlns:w="{W}"><w:body>'
           f'<w:p><w:pPr><w:pStyle w:val="Heading1"/></w:pPr><w:r><w:t>The Title</w:t></w:r></w:p>'
           f'<w:p><w:r><w:t>First real paragraph of body text.</w:t></w:r></w:p>'
           f'<w:p><w:r><w:t>Second paragraph, still plain.</w:t></w:r></w:p>'
           f'</w:body></w:document>')
    ct = ('<?xml version="1.0"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
          '<Default Extension="xml" ContentType="application/xml"/>'
          '<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/></Types>')
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", ct)
        z.writestr("word/document.xml", doc)


def _write_min_epub(path: Path) -> None:
    with zipfile.ZipFile(path, "w") as z:
        z.writestr("mimetype", "application/epub+zip", compress_type=zipfile.ZIP_STORED)
        z.writestr("META-INF/container.xml",
                   '<?xml version="1.0"?><container version="1.0" '
                   'xmlns="urn:oasis:names:tc:opendocument:xmlns:container">'
                   '<rootfiles><rootfile full-path="OEBPS/content.opf" '
                   'media-type="application/oebps-package+xml"/></rootfiles></container>')
        z.writestr("OEBPS/content.opf",
                   '<?xml version="1.0"?><package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="id">'
                   '<metadata/><manifest><item id="c1" href="c1.xhtml" media-type="application/xhtml+xml"/></manifest>'
                   '<spine><itemref idref="c1"/></spine></package>')
        z.writestr("OEBPS/c1.xhtml",
                   '<?xml version="1.0"?><html xmlns="http://www.w3.org/1999/xhtml"><body>'
                   '<h1>Chapter From Epub</h1><p>An epub paragraph of prose.</p></body></html>')


def selftest() -> int:
    import tempfile
    fails = []
    with tempfile.TemporaryDirectory() as td:
        tdp = Path(td)
        intake = tdp / "intake"
        intake.mkdir()
        _write_min_docx(intake / "doc_source.docx")
        _write_min_epub(intake / "book_source.epub")
        (intake / "page.html").write_text(
            "<html><head><style>x{}</style></head><body><h2>HTML Head</h2>"
            "<p>Hello from html.</p><script>ignored()</script></body></html>", "utf-8")
        out = tdp / "converted"
        summary = convert_dir(intake, out, force=True, include_text=False)
        if summary["converted"] != 3:
            fails.append(f"expected 3 converted, got {summary['converted']} ({summary})")
        docx_md = (out / "doc_source.md").read_text("utf-8") if (out / "doc_source.md").exists() else ""
        if "# The Title" not in docx_md or "First real paragraph" not in docx_md:
            fails.append(f"docx heading/body not converted: {docx_md[:120]!r}")
        epub_md = (out / "book_source.md").read_text("utf-8") if (out / "book_source.md").exists() else ""
        if "Chapter From Epub" not in epub_md or "epub paragraph" not in epub_md:
            fails.append(f"epub not converted: {epub_md[:120]!r}")
        html_md = (out / "page.md").read_text("utf-8") if (out / "page.md").exists() else ""
        if "HTML Head" not in html_md or "Hello from html" not in html_md or "ignored" in html_md:
            fails.append(f"html not converted/cleaned: {html_md[:120]!r}")
        # idempotency: a second pass skips all three
        s2 = convert_dir(intake, out, force=False, include_text=False)
        if s2["skipped"] != 3:
            fails.append(f"expected 3 skipped on 2nd pass, got {s2['skipped']}")
    if fails:
        print("MANUSCRIPT_INGEST SELFTEST: FAIL")
        for f in fails:
            print("  - " + f)
        return 1
    print("MANUSCRIPT_INGEST SELFTEST: PASS (docx + epub + html -> markdown, idempotent)")
    return 0


def main(argv=None) -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    ap = argparse.ArgumentParser(description="Convert source documents to clean markdown (BOOKSMITH).")
    ap.add_argument("--intake", help="directory of source documents (top level)")
    ap.add_argument("--out", help="output directory (batch) or file (with --src)")
    ap.add_argument("--src", help="convert a single file")
    ap.add_argument("--force", action="store_true", help="reconvert even if the output is newer")
    ap.add_argument("--include-text", action="store_true", help="also pass through .md/.txt sources")
    ap.add_argument("--selftest", action="store_true", help="run the built-in converter self-test")
    args = ap.parse_args(argv)

    if args.selftest:
        return selftest()
    if args.src:
        src = Path(args.src)
        if not src.exists():
            print(f"source not found: {src}", file=sys.stderr)
            return 2
        try:
            md = convert_file(src).strip()
        except Exception as e:
            print(f"conversion failed: {e}", file=sys.stderr)
            return 1
        if args.out:
            dest = Path(args.out)
            if dest.is_dir() or args.out.endswith(("/", "\\")):
                dest = dest / f"{slugify(src.stem)}.md"
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text(f"# Source: {src.name}\n\n{md}\n", encoding="utf-8")
            print(str(dest))
        else:
            print(md)
        return 0
    if args.intake:
        intake = Path(args.intake)
        if not intake.exists():
            print(f"intake dir not found: {intake}", file=sys.stderr)
            return 2
        out = Path(args.out) if args.out else intake / "converted"
        summary = convert_dir(intake, out, force=args.force, include_text=args.include_text)
        print(json.dumps(summary, ensure_ascii=False))
        return 0 if summary["failed"] == 0 else 1
    ap.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())
