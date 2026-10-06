#!/usr/bin/env python3
"""kindle_ready.py -- deep Kindle-readiness validation of a BOOKSMITH Kindle DOCX.

Complements verify_build --format kindle (word parity vs print, cover spec, provenance)
with structural checks of the DOCX itself: language tag, font chain, single-section
reflowable layout, no print furniture, chapter heading structure for Amazon auto-nav,
figure/alt integrity, no internal markers, and the ebook cover spec.

Usage:
  python _tools/kindle_ready.py --config book_config.json [--json]
Exit: 0 all pass | 1 any fail.
"""
import argparse
import io
import json
import os
import re
import sys
import zipfile

from PIL import Image

TOOLS = os.path.dirname(os.path.abspath(__file__))


def check(name, ok, detail):
    return {"name": name, "pass": bool(ok), "detail": detail}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    cfgp = os.path.abspath(a.config)
    root = os.path.dirname(cfgp)
    cfg = json.load(io.open(cfgp, encoding="utf-8"))
    checks = []

    kd = os.path.join(root, "outputs", "kindle")
    docx = None
    if os.path.isdir(kd):
        cands = sorted([f for f in os.listdir(kd) if f.lower().endswith(".docx") and "kindle" in f.lower()],
                       key=lambda f: os.path.getmtime(os.path.join(kd, f)), reverse=True)
        if cands:
            docx = os.path.join(kd, cands[0])
    checks.append(check("kindle_docx_exists", docx is not None, docx or "no KINDLE docx found"))
    if not docx:
        out = {"all_pass": False, "checks": checks}
        print(json.dumps(out, ensure_ascii=False, indent=1) if a.json else out)
        return 1

    z = zipfile.ZipFile(docx)
    names = z.namelist()
    doc = z.read("word/document.xml").decode("utf-8", "ignore")
    styles = z.read("word/styles.xml").decode("utf-8", "ignore") if "word/styles.xml" in names else ""
    settings = z.read("word/settings.xml").decode("utf-8", "ignore") if "word/settings.xml" in names else ""
    text = "".join(re.findall(r"<w:t(?:\s[^>]*)?>([^<]*)</w:t>", doc))

    checks.append(check("docx_zip_readable", "word/document.xml" in names and "word/styles.xml" in names,
                        f"{len(names)} zip entries; document+styles present"))
    checks.append(check("no_internal_markers", not re.search(r"<!--|SEGMENT\s*:|\[BO-WRITES", doc),
                        "no <!-- / SEGMENT / [BO-WRITES] in document.xml"))

    lang = str(cfg.get("language") or "")
    want = "zh-TW" if re.search(r"hant|hk|-tw|-mo", lang.lower()) else "zh-CN"
    stray = [c for c in ("zh-CN", "zh-TW") if c != want and c in doc + styles + settings]
    ok_lang = (want in styles) or (want in doc) or (not re.search(r"zh-", lang.lower()) and not re.search(r"zh-CN|zh-TW", styles + doc))
    checks.append(check("language_tag", ok_lang and not stray,
                        f"want {want}; found in styles={want in styles} doc={want in doc}; stray={stray or 'none'}"))

    body_font = str(((cfg.get("interior") or {}).get("body_font")) or "")
    latin = str(((cfg.get("interior") or {}).get("body_font_latin")) or "")
    ok_fonts = (body_font in doc + styles) and (latin in doc + styles)
    checks.append(check("font_chain", ok_fonts,
                        f"body='{body_font}' present={body_font in doc + styles}; latin='{latin}' present={latin in doc + styles}"))

    nsect = len(re.findall(r"<w:sectPr[ >]", doc + styles))
    checks.append(check("single_section_reflowable", nsect == 1, f"{nsect} sectPr (reflowable want 1)"))
    furn = len(re.findall(r"<w:headerReference|<w:footerReference", doc)) + len(re.findall(r'w:instrText[^>]*>\s*PAGE', doc))
    checks.append(check("no_print_furniture", furn == 0, f"header/footer refs + PAGE fields: {furn}"))

    nunits = len(cfg.get("units") or [])
    about_extra = 1 if cfg.get("about_the_author") else 0
    nhead = len(re.findall(r'<w:pStyle w:val="Heading1"', doc))
    checks.append(check("heading_structure", nhead == nunits + about_extra,
                        f"Heading1 paragraphs={nhead} vs units={nunits}+about={about_extra}"))

    md = os.path.join(root, "outputs", "markdown")
    master = sorted([f for f in os.listdir(md) if f.endswith(".md")], key=lambda f: os.path.getmtime(os.path.join(md, f)), reverse=True)[0] if os.path.isdir(md) else None
    want_imgs = None
    if master:
        t = io.open(os.path.join(md, master), encoding="utf-8").read()
        want_imgs = len(re.findall(r"!\[[^\]]*\]\([^)]+\)", t))
    nblips = len(re.findall(r"<a:blip\b", doc))
    nalts = len(re.findall(r'<wp:docPr[^>]*\bdescr="[^"]+"', doc))
    checks.append(check("figures_and_alts", (want_imgs is None or nblips == want_imgs) and nalts >= nblips - 1,
                        f"blips={nblips} vs master image lines={want_imgs}; docPr descr(alt)={nalts}"))

    pdocx = None
    pb = os.path.join(root, "outputs", "kdp_paperback")
    if os.path.isdir(pb):
        pc = sorted([f for f in os.listdir(pb) if f.lower().endswith(".docx")],
                    key=lambda f: os.path.getmtime(os.path.join(pb, f)), reverse=True)
        if pc:
            pdocx = os.path.join(pb, pc[0])
    ok_parity, pdetail = True, "print docx absent — parity not checkable here (verify_build covers it)"
    if pdocx:
        pd = zipfile.ZipFile(pdocx).read("word/document.xml").decode("utf-8", "ignore")
        ptext = "".join(re.findall(r"<w:t(?:\s[^>]*)?>([^<]*)</w:t>", pd))
        ratio = (len(text) / len(ptext)) if ptext else 0
        ok_parity = ratio >= 0.97
        pdetail = f"kindle chars={len(text)} vs print chars={len(ptext)} ratio={ratio:.4f} (>=0.97)"
    checks.append(check("wordcount_parity_vs_print", ok_parity, pdetail))

    cover = None
    for f in sorted(os.listdir(kd)):
        if f.lower().endswith((".jpg", ".jpeg")) and "cover" in f.lower() and "r2k" not in f.lower():
            cover = os.path.join(kd, f)
            break
    if cover:
        im = Image.open(cover)
        w, h = im.size
        mb = os.path.getsize(cover) / 1048576
        ok = w >= 625 and h >= 1000 and h / w >= 1.6 and im.mode in ("RGB", "L") and mb < 50
        checks.append(check("ebook_cover_spec", ok, f"{os.path.basename(cover)} {w}x{h} {im.mode} {mb:.1f}MB (min 625x1000, ratio>=1.6)"))
    else:
        checks.append(check("ebook_cover_spec", False, "no kindle cover jpg"))

    expect_toc = bool(cfg.get("kindle_include_toc"))
    has_toc = bool(re.search(r"w:instrText[^>]*>\s*TOC\b|w:instr=\"\s*TOC\b", doc))
    checks.append(check("toc_policy", has_toc == expect_toc,
                        f"TOC field present={has_toc}; kindle_include_toc={expect_toc}"))

    all_pass = all(c["pass"] for c in checks)
    out = {"format": "kindle", "root": root, "docx": docx, "master": master, "all_pass": all_pass, "checks": checks}
    if a.json:
        print(json.dumps(out, ensure_ascii=False, indent=1))
    else:
        for c in checks:
            print(f"[{'PASS' if c['pass'] else 'FAIL'}] {c['name']}: {c['detail']}")
        print("ALL PASS" if all_pass else "FAILURES PRESENT")
    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(main())
