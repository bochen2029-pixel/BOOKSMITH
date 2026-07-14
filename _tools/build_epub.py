#!/usr/bin/env python3
r"""
build_epub.py — EPUB 3 exporter (BOOKSMITH).

PURPOSE
    Produce a reflowable EPUB 3 ebook from the version-pinned master markdown +
    book_config.json. EPUB is the industry-standard ebook container: it uploads
    directly to Apple Books, Kobo, Google Play Books, Nook, Draft2Digital — and
    KDP itself now RECOMMENDS EPUB for reflowable Kindle uploads (MOBI is
    deprecated), so this can also replace the Kindle DOCX upload path.

    Emitted structure (EPUB 3 + EPUB 2 NCX for maximum device compat):
        mimetype                      (FIRST zip entry, STORED/uncompressed)
        META-INF/container.xml
        OEBPS/content.opf             (metadata / manifest / spine)
        OEBPS/nav.xhtml               (EPUB 3 nav)
        OEBPS/toc.ncx                 (EPUB 2 compat nav)
        OEBPS/css/style.css
        OEBPS/images/cover.jpg|png
        OEBPS/text/cover.xhtml, titlepage.xhtml, copyright.xhtml,
                   [dedication.xhtml], [epigraph.xhtml],
                   <unit_id>.xhtml ..., [about.xhtml]

CONTRACT
    python build_epub.py --config book_config.json [--src master.md]
                         [--out out.epub] [--workspace DIR]
    -> writes outputs/epub/<slug>.epub
    -> prints JSON {"epub":..., "chapters":N, "words":N, "bytes":N, "checks":[...]}
    Exit 0 on success (all self-checks pass), 1 on failure.

DESIGN RULES (mirrors the other generators)
    - Ceremonial front matter is rendered FROM CONFIG (dedication/epigraph/
      about_the_author keys), never parsed out of the master (LESSONS_LEDGER
      front-matter rule).
    - Body units are split from the master at the unit heading level:
      chapter = "# ", part = "## " (same convention as generate_book.js).
    - No page numbers / headers / print concepts — reflowable (Kindle rule G11).
    - Cover: prefers the COMPOSITED ebook cover (outputs/kindle/
      <slug>_KINDLE_cover.jpg — it carries the typography); falls back to raw
      cover_art. properties="cover-image" + EPUB2 <meta name="cover"> both set.
    - Word-count parity: prints the body word count; verify_build.py enforces
      epub >= print (the 8,476-words-short Kindle bug class).

SELF-CHECKS (run after writing; any failure -> exit 1)
    mimetype first + STORED - container/opf/nav/ncx well-formed XML - every
    manifest href present in the zip - every spine idref in the manifest -
    every text/*.xhtml well-formed - cover image present with cover-image
    property.
"""
import argparse
import json
import re
import sys
import uuid
import zipfile
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

# ----------------------------------------------------------------------------
# config + workspace resolution (same conventions as the sibling tools)
# ----------------------------------------------------------------------------

def load_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as fh:
        return json.load(fh)


def workspace_root(cfg: dict, config_path: Path, explicit) -> Path:
    if explicit:
        return Path(explicit).resolve()
    slug = cfg.get("slug")
    base = config_path.resolve().parent
    if slug:
        cand = base / "book_workspace" / slug
        if cand.exists():
            return cand
        if base.name == slug:
            return base
    return base


def find_master(ws: Path, slug: str, override) -> Path:
    if override:
        p = Path(override)
        if not p.exists():
            raise FileNotFoundError(f"--src not found: {p}")
        return p
    md_dir = ws / "outputs" / "markdown"
    cands = []
    for p in md_dir.glob(f"{slug}_v*.md"):
        m = re.search(r"_v(\d+)\.md$", p.name)
        if m:
            cands.append((int(m.group(1)), p))
    if not cands:
        raise FileNotFoundError(
            f"no version-pinned master under {md_dir} (run assemble_manuscript.py first)")
    return sorted(cands)[-1][1]


def find_cover(cfg: dict, ws: Path):
    """Prefer the composited ebook cover (typography included); fall back to raw art."""
    slug = cfg.get("slug", "book")
    for cand in (
        ws / "outputs" / "kindle" / f"{slug}_KINDLE_cover.jpg",
        ws / "outputs" / "kindle" / f"{slug}_cover.jpg",
        ws / "cover_art" / f"{slug}_src.png",
        ws / "cover_art" / f"{slug}_src.jpg",
    ):
        if cand.exists():
            return cand
    return None


# ----------------------------------------------------------------------------
# markdown -> xhtml
# ----------------------------------------------------------------------------

def esc(t: str) -> str:
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def esc_attr(t: str) -> str:
    """Attribute-safe escaping: a title containing a double quote must not break
    out of an alt="..." sink (malformed XML hard-blocks the whole build)."""
    return esc(t).replace('"', "&quot;")


def inline(t: str) -> str:
    """Inline markup AFTER escaping. Order mirrors the print generator:
    backticks -> bold -> italic (backticks first so code spans shield markers)."""
    t = esc(t)
    t = re.sub(r"`([^`]+)`", r"<code>\1</code>", t)
    t = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", t)
    t = re.sub(r"\*([^*\n]+)\*", r"<em>\1</em>", t)
    # Legacy micro-syntax used in some back matter ({i}...{/i}).
    t = t.replace("{i}", "<em>").replace("{/i}", "</em>")
    return t


SCENE_BREAK = re.compile(r"^\s*(✦|\*\s*\*\s*\*|\* \* \*|\*\*\*)\s*$")


def body_to_xhtml(lines, unit_level: int, ornament: str) -> str:
    """Convert a unit body (markdown lines, heading excluded) to XHTML blocks."""
    out = []
    para: list = []
    quote: list = []
    first_para = True

    def flush_para():
        nonlocal first_para
        if para:
            cls = ' class="first"' if first_para else ""
            out.append(f"<p{cls}>{inline(' '.join(para))}</p>")
            para.clear()
            first_para = False

    def flush_quote():
        if quote:
            inner = "".join(f"<p>{inline(q)}</p>" for q in quote)
            out.append(f"<blockquote>{inner}</blockquote>")
            quote.clear()

    sub_h = "#" * (unit_level + 1)      # e.g. "##" inside chapters
    subsub_h = "#" * (unit_level + 2)

    for raw in lines:
        line = raw.rstrip()
        if not line.strip():
            flush_para(); flush_quote()
            continue
        if SCENE_BREAK.match(line):
            flush_para(); flush_quote()
            out.append(f'<p class="scenebreak">{esc(ornament)}</p>')
            first_para = True
            continue
        if line.startswith(subsub_h + " "):
            flush_para(); flush_quote()
            out.append(f"<h3>{inline(line[len(subsub_h)+1:].strip())}</h3>")
            first_para = True
            continue
        if line.startswith(sub_h + " "):
            flush_para(); flush_quote()
            out.append(f"<h2>{inline(line[len(sub_h)+1:].strip())}</h2>")
            first_para = True
            continue
        if line.startswith("> "):
            flush_para()
            quote.append(line[2:].strip())
            continue
        if line.startswith(">"):
            flush_para()
            quote.append(line[1:].strip())
            continue
        flush_quote()
        para.append(line.strip())
    flush_para(); flush_quote()
    return "\n".join(out)


def split_units(text: str, unit_level: int):
    """Split the master into [(heading, body_lines)] at the unit heading level."""
    hmark = "#" * unit_level
    head_re = re.compile(rf"^{re.escape(hmark)}(?!#)\s+(.+)$")
    lines = text.splitlines()
    starts = [(i, m.group(1).strip()) for i, l in enumerate(lines)
              if (m := head_re.match(l))]
    units = []
    for n, (i, heading) in enumerate(starts):
        end = starts[n + 1][0] if n + 1 < len(starts) else len(lines)
        units.append((heading, lines[i + 1:end]))
    return units


# ----------------------------------------------------------------------------
# xhtml documents
# ----------------------------------------------------------------------------

XHTML_SHELL = """<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" xml:lang="{lang}" lang="{lang}">
<head>
<title>{title}</title>
<link rel="stylesheet" type="text/css" href="../css/style.css"/>
</head>
<body>
{body}
</body>
</html>
"""

CSS = """/* BOOKSMITH EPUB stylesheet */
body { font-family: serif; line-height: 1.5; margin: 0 5%; }
h1.unit { text-align: center; font-weight: normal; letter-spacing: 0.08em;
          text-transform: uppercase; margin: 3em 0 2em 0; font-size: 1.3em; }
h2 { text-align: left; font-size: 1.1em; margin: 1.6em 0 0.6em 0; }
h3 { text-align: left; font-size: 1.0em; margin: 1.4em 0 0.5em 0; }
p { margin: 0; text-indent: 1.25em; text-align: justify; }
p.first { text-indent: 0; }
p.scenebreak { text-indent: 0; text-align: center; margin: 1.2em 0; }
p.centered { text-indent: 0; text-align: center; }
blockquote { margin: 1em 2em; font-style: italic; }
blockquote p { text-indent: 0; }
.titlepage { text-align: center; margin-top: 20%; }
.titlepage .title { font-size: 1.8em; letter-spacing: 0.10em; }
.titlepage .subtitle { font-size: 1.1em; font-style: italic; margin-top: 1em; }
.titlepage .author { font-size: 1.1em; letter-spacing: 0.18em; margin-top: 3em;
                     text-transform: uppercase; }
.copyright { font-size: 0.85em; margin-top: 30%; text-align: center; }
.copyright p { text-indent: 0; margin-bottom: 0.8em; }
.dedication { text-align: center; font-style: italic; margin-top: 35%; }
.epigraph { text-align: center; font-style: italic; margin-top: 30%; }
.epigraph .attribution { font-style: normal; font-size: 0.9em; margin-top: 1em; }
img.cover { max-width: 100%; height: auto; }
div.coverwrap { text-align: center; }
figure.chapterart { text-align: center; margin: 0.8em 0 1.2em 0; }
figure.chapterart img { max-width: 92%; height: auto; }
"""


def unit_xhtml(lang, heading, body_html, art_html=""):
    body = (f'<section epub:type="chapter">\n<h1 class="unit">{inline(heading)}</h1>\n'
            f'{art_html}{body_html}\n</section>')
    return XHTML_SHELL.format(lang=lang, title=esc(heading), body=body)


def simple_page(lang, title, inner):
    return XHTML_SHELL.format(lang=lang, title=esc(title), body=inner)


# ----------------------------------------------------------------------------
# build
# ----------------------------------------------------------------------------

def build(cfg: dict, master: Path, ws: Path, out_path: Path):
    lang = cfg.get("language", "en")
    title = cfg["title"]
    subtitle = cfg.get("subtitle", "")
    author = cfg["author"]
    slug = cfg.get("slug", "book")
    is_fiction = bool(cfg.get("is_fiction", True))
    ornament = ((cfg.get("interior") or {}).get("ornament_glyph") or "✦")
    unit_noun = ((cfg.get("voice") or {}).get("unit_noun") or "chapter").lower()
    unit_level = 1 if unit_noun == "chapter" else 2

    text = master.read_text(encoding="utf-8")
    units = split_units(text, unit_level)
    if not units:
        raise ValueError(
            f"no unit headings found at level {'#' * unit_level} in {master.name}")

    cover_src = find_cover(cfg, ws)
    year = datetime.now(timezone.utc).year

    # ---- assemble document list: (id, filename, title, xhtml, in_toc) ----
    docs = []

    if cover_src is not None:
        cover_ext = cover_src.suffix.lower().lstrip(".")
        cover_name = f"cover.{'jpg' if cover_ext in ('jpg', 'jpeg') else cover_ext}"
        docs.append(("coverpage", "cover.xhtml", "Cover", simple_page(
            lang, "Cover",
            f'<div class="coverwrap"><img class="cover" src="../images/{cover_name}" alt="{esc_attr(title)}"/></div>'),
            False))
    else:
        cover_name = None

    tp = [f'<div class="titlepage">',
          f'<p class="title centered">{esc(title.upper())}</p>']
    if subtitle:
        tp.append(f'<p class="subtitle centered">{esc(subtitle)}</p>')
    tp.append(f'<p class="author centered">{esc(author)}</p>')
    tp.append("</div>")
    docs.append(("titlepage", "titlepage.xhtml", "Title Page",
                 simple_page(lang, "Title Page", "\n".join(tp)), False))

    cp = ['<div class="copyright">',
          f"<p>Copyright © {year} {esc(author)}. All rights reserved.</p>"]
    if is_fiction:
        cp.append("<p>This is a work of fiction. Names, characters, places, and "
                  "incidents are the products of the author’s imagination or are "
                  "used fictitiously. Any resemblance to actual persons, living or "
                  "dead, events, or locales is entirely coincidental.</p>")
    cp.append("</div>")
    docs.append(("copyright", "copyright.xhtml", "Copyright",
                 simple_page(lang, "Copyright", "\n".join(cp)), False))

    if cfg.get("dedication"):
        docs.append(("dedication", "dedication.xhtml", "Dedication", simple_page(
            lang, "Dedication",
            f'<div class="dedication"><p class="centered">{inline(cfg["dedication"])}</p></div>'),
            False))

    epi = cfg.get("epigraph") or {}
    if isinstance(epi, dict) and epi.get("text"):
        # same rendered-character rule as the print/kindle generators: no
        # em-dash prefix unless the voice contract explicitly allows em-dashes
        dash = "— " if (cfg.get("voice") or {}).get("no_em_dashes", True) is False else ""
        attr = (f'<p class="attribution centered">{dash}{inline(epi.get("attribution", ""))}</p>'
                if epi.get("attribution") else "")
        docs.append(("epigraph", "epigraph.xhtml", "Epigraph", simple_page(
            lang, "Epigraph",
            f'<div class="epigraph"><p class="centered">{inline(epi["text"])}</p>{attr}</div>'),
            False))

    if cfg.get("readers_note"):
        # print (generate_book.js readersNoteChildren) renders this; the EPUB
        # must too, or the editions diverge and parity drifts
        paras = [p.strip() for p in re.split(r"\n\s*\n", str(cfg["readers_note"])) if p.strip()]
        inner = ('<div class="readersnote">\n<p class="centered">A NOTE TO THE READER</p>\n'
                 + "\n".join(f"<p>{inline(p)}</p>" for p in paras) + "\n</div>")
        docs.append(("readersnote", "readersnote.xhtml", "A Note to the Reader",
                     simple_page(lang, "A Note to the Reader", inner), False))

    unit_ids = [u.get("id") for u in (cfg.get("units") or []) if isinstance(u, dict)]
    if unit_ids and len(units) != len(unit_ids):
        # ids are bound to headings BY POSITION: a count mismatch would silently
        # mislabel every chapter's filename/manifest/spine/nav entry
        raise SystemExit(
            f"unit count mismatch: master has {len(units)} unit heading(s) at level "
            f"{'#' * unit_level} but config declares {len(unit_ids)} unit(s) — "
            f"positional id binding would mislabel every chapter. Fix the master or "
            f"config before building the EPUB.")
    # Chapter-opener art (kept identical in behavior to the DOCX generators):
    # interior.chapter_art {enabled, dir}; default dir cover_art/illustrations/
    # live under the workspace; one <unit_id>.png per unit; missing = no-op.
    _ca = ((cfg.get("interior") or {}).get("chapter_art") or {})
    art_dir = None
    if _ca.get("enabled") is not False:
        _cand = ws / (_ca.get("dir") or "cover_art/illustrations/live")
        art_dir = _cand if _cand.is_dir() else None
    art_files: dict = {}  # sanitized uid -> Path

    body_words = 0
    for n, (heading, body_lines) in enumerate(units):
        uid = unit_ids[n] if n < len(unit_ids) and unit_ids[n] else f"unit_{n+1:02d}"
        uid = re.sub(r"[^a-zA-Z0-9_]", "_", uid)
        body_html = body_to_xhtml(body_lines, unit_level, ornament)
        body_words += len(re.sub(r"<[^>]+>", " ", body_html).split())
        art_html = ""
        if art_dir is not None:
            af = art_dir / f"{uid}.png"
            if af.is_file():
                art_files[uid] = af
                art_html = (f'<figure class="chapterart">'
                            f'<img src="../images/art_{uid}.png" alt=""/></figure>\n')
        docs.append((uid, f"{uid}.xhtml", heading,
                     unit_xhtml(lang, heading, body_html, art_html), True))

    if cfg.get("about_the_author"):
        paras = [p.strip() for p in re.split(r"\n\s*\n", cfg["about_the_author"]) if p.strip()]
        inner = ('<section epub:type="backmatter">\n<h1 class="unit">About the Author</h1>\n'
                 + "\n".join(f"<p{' class=' + chr(34) + 'first' + chr(34) if i == 0 else ''}>{inline(p)}</p>"
                             for i, p in enumerate(paras))
                 + "\n</section>")
        docs.append(("about", "about.xhtml", "About the Author",
                     simple_page(lang, "About the Author", inner), True))

    # ---- package documents ----
    book_uuid = uuid.uuid5(uuid.NAMESPACE_URL, f"booksmith:{slug}:{title}:{author}")
    modified = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    manifest = []
    spine = []
    if cover_name:
        mt = "image/jpeg" if cover_name.endswith("jpg") else "image/png"
        manifest.append(f'<item id="cover-image" href="images/{cover_name}" '
                        f'media-type="{mt}" properties="cover-image"/>')
    manifest.append('<item id="nav" href="nav.xhtml" '
                    'media-type="application/xhtml+xml" properties="nav"/>')
    manifest.append('<item id="ncx" href="toc.ncx" '
                    'media-type="application/x-dtbncx+xml"/>')
    manifest.append('<item id="css" href="css/style.css" media-type="text/css"/>')
    for uid in art_files:
        manifest.append(f'<item id="art-{uid}" href="images/art_{uid}.png" '
                        f'media-type="image/png"/>')
    for did, fname, _t, _x, _toc in docs:
        manifest.append(f'<item id="{did}" href="text/{fname}" '
                        f'media-type="application/xhtml+xml"/>')
        spine.append(f'<itemref idref="{did}"/>')

    sub_meta = (f"<dc:title id=\"subtitle\">{esc(subtitle)}</dc:title>\n  "
                f"<meta refines=\"#subtitle\" property=\"title-type\">subtitle</meta>\n  "
                if subtitle else "")
    cover_meta = '<meta name="cover" content="cover-image"/>\n  ' if cover_name else ""
    opf = f"""<?xml version="1.0" encoding="utf-8"?>
<package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="pub-id" xml:lang="{lang}">
 <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
  <dc:identifier id="pub-id">urn:uuid:{book_uuid}</dc:identifier>
  <dc:title id="main">{esc(title)}</dc:title>
  <meta refines="#main" property="title-type">main</meta>
  {sub_meta}<dc:creator id="author">{esc(author)}</dc:creator>
  <dc:language>{lang}</dc:language>
  <meta property="dcterms:modified">{modified}</meta>
  {cover_meta}</metadata>
 <manifest>
  {chr(10).join('  ' + m for m in manifest).strip()}
 </manifest>
 <spine toc="ncx">
  {chr(10).join('  ' + s for s in spine).strip()}
 </spine>
</package>
"""

    toc_entries = [(fname, t) for _d, fname, t, _x, in_toc in docs if in_toc]
    nav_lis = "\n".join(f'   <li><a href="text/{f}">{esc(t)}</a></li>'
                        for f, t in toc_entries)
    nav = f"""<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" xml:lang="{lang}" lang="{lang}">
<head><title>Contents</title><link rel="stylesheet" type="text/css" href="css/style.css"/></head>
<body>
 <nav epub:type="toc" id="toc">
  <h1>Contents</h1>
  <ol>
{nav_lis}
  </ol>
 </nav>
</body>
</html>
"""

    nav_points = "\n".join(
        f'  <navPoint id="np{i+1}" playOrder="{i+1}">'
        f'<navLabel><text>{esc(t)}</text></navLabel>'
        f'<content src="text/{f}"/></navPoint>'
        for i, (f, t) in enumerate(toc_entries))
    ncx = f"""<?xml version="1.0" encoding="utf-8"?>
<ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" version="2005-1">
 <head>
  <meta name="dtb:uid" content="urn:uuid:{book_uuid}"/>
  <meta name="dtb:depth" content="1"/>
  <meta name="dtb:totalPageCount" content="0"/>
  <meta name="dtb:maxPageNumber" content="0"/>
 </head>
 <docTitle><text>{esc(title)}</text></docTitle>
 <navMap>
{nav_points}
 </navMap>
</ncx>
"""

    container = """<?xml version="1.0" encoding="utf-8"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
 <rootfiles>
  <rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/>
 </rootfiles>
</container>
"""

    # ---- write the zip (mimetype FIRST + STORED) ----
    out_path.parent.mkdir(parents=True, exist_ok=True)
    if out_path.exists():
        out_path.unlink()
    with zipfile.ZipFile(out_path, "w") as z:
        z.writestr(zipfile.ZipInfo("mimetype"), "application/epub+zip",
                   compress_type=zipfile.ZIP_STORED)
        def w(name, data):
            z.writestr(name, data, compress_type=zipfile.ZIP_DEFLATED)
        w("META-INF/container.xml", container)
        w("OEBPS/content.opf", opf)
        w("OEBPS/nav.xhtml", nav)
        w("OEBPS/toc.ncx", ncx)
        w("OEBPS/css/style.css", CSS)
        if cover_name:
            z.write(str(cover_src), f"OEBPS/images/{cover_name}",
                    compress_type=zipfile.ZIP_DEFLATED)
        for uid, af in art_files.items():
            z.write(str(af), f"OEBPS/images/art_{uid}.png",
                    compress_type=zipfile.ZIP_DEFLATED)
        for _d, fname, _t, xhtml, _toc in docs:
            w(f"OEBPS/text/{fname}", xhtml)

    # A raw-art cover (from cover_art/) has NO title/author typography — the
    # composited kindle cover is preferred. Flag it so the operator sees the
    # EPUB is shipping bare AI art (see the cover_typography advisory in main()).
    cover_is_raw_art = bool(cover_src is not None
                            and cover_src.parent.name == "cover_art")

    return {
        "chapters": len(units),
        "toc_entries": len(toc_entries),
        "words": body_words,
        "cover": str(cover_src) if cover_src else None,
        "cover_is_raw_art": cover_is_raw_art,
        "chapter_art_images": len(art_files),
    }


# ----------------------------------------------------------------------------
# self-checks
# ----------------------------------------------------------------------------

def self_check(epub_path: Path):
    checks = []

    def add(name, ok, detail):
        checks.append({"name": name, "pass": bool(ok), "detail": detail})

    with zipfile.ZipFile(epub_path) as z:
        infos = z.infolist()
        names = set(z.namelist())

        first = infos[0]
        add("mimetype_first_and_stored",
            first.filename == "mimetype"
            and first.compress_type == zipfile.ZIP_STORED
            and z.read("mimetype") == b"application/epub+zip",
            f"first entry={first.filename}, compress={first.compress_type}")

        ok_xml = True
        bad = []
        for n in sorted(names):
            if n.endswith((".xhtml", ".opf", ".ncx", ".xml")):
                try:
                    ET.fromstring(z.read(n))
                except ET.ParseError as e:
                    ok_xml = False
                    bad.append(f"{n}: {e}")
        add("all_xml_well_formed", ok_xml, "; ".join(bad) if bad else
            "every .xhtml/.opf/.ncx/.xml parses")

        try:
            opf_xml = z.read("OEBPS/content.opf").decode("utf-8")
            hrefs = re.findall(r'href="([^"]+)"', opf_xml)
            ids = set(re.findall(r'<item id="([^"]+)"', opf_xml))
            idrefs = re.findall(r'<itemref idref="([^"]+)"', opf_xml)
            missing = [h for h in hrefs if f"OEBPS/{h}" not in names]
            add("manifest_hrefs_exist", not missing,
                f"missing: {missing}" if missing else f"{len(hrefs)} hrefs all present")
            orphan = [r for r in idrefs if r not in ids]
            add("spine_idrefs_in_manifest", not orphan,
                f"orphans: {orphan}" if orphan else f"{len(idrefs)} idrefs all resolve")
            add("cover_image_property", 'properties="cover-image"' in opf_xml,
                "cover-image property present" if 'properties="cover-image"' in opf_xml
                else "no cover-image property (no cover embedded)")
        except KeyError:
            add("opf_present", False, "OEBPS/content.opf missing")

    return checks


# ----------------------------------------------------------------------------
# main
# ----------------------------------------------------------------------------

def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

    ap = argparse.ArgumentParser(description="BOOKSMITH EPUB 3 exporter.")
    ap.add_argument("--config", required=True)
    ap.add_argument("--src", help="Override the master markdown path.")
    ap.add_argument("--out", help="Override the output .epub path.")
    ap.add_argument("--workspace", help="Override book_workspace/<slug>.")
    args = ap.parse_args()

    cfg_path = Path(args.config).resolve()
    cfg = load_json(cfg_path)
    ws = workspace_root(cfg, cfg_path, args.workspace)
    slug = cfg.get("slug", "book")

    master = find_master(ws, slug, args.src)
    out_path = (Path(args.out).resolve() if args.out
                else ws / "outputs" / "epub" / f"{slug}.epub")

    info = build(cfg, master, ws, out_path)
    checks = self_check(out_path)
    # Non-fatal advisory: the EPUB is shipping raw AI art (no title/author
    # typography). The composited-preferred fallback is intentional resilience,
    # so this stays pass=True — it only surfaces the fact to the operator.
    if info.get("cover_is_raw_art"):
        checks.append({
            "name": "cover_typography",
            "pass": True,
            "detail": "cover=raw AI art (cover_art/); run composite_cover.py "
                      "--profile kindle for title/author typography before shipping",
        })
    all_pass = all(c["pass"] for c in checks)

    # Internal flag — not part of the emitted JSON contract.
    info.pop("cover_is_raw_art", None)

    print(json.dumps({
        "epub": str(out_path),
        "master": str(master),
        **info,
        "bytes": out_path.stat().st_size,
        "self_checks": checks,
        "all_pass": all_pass,
    }, indent=2, ensure_ascii=False))
    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(main())
