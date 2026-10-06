#!/usr/bin/env python3
"""docx_delta.py: what did the author change? A paragraph-level diff of a revised DOCX against the
text it was edited from (a BOOKSMITH assembled master .md, or the delivered Word edition .docx), with
word-level detail on replacements, the lineage test (which delivered file did the author actually edit),
and the two traps of an exported DOCX: lone heading ornaments that are not text, and consecutive
duplicate paragraphs (paste slips).

The method it serves: docs/BOOK_TRANSLATION_METHOD_v3.md, P0 (source of record) and P10 (re-sync).

Usage:
  python _tools/docx_delta.py --docx NEW.docx --master MASTER.md|OLD.docx --out DIR
  python _tools/docx_delta.py --docx NEW.docx --candidates A.docx B.docx C.md     # lineage test only
Options:
  --ornament CHARS    paragraphs consisting only of these characters are the kit's heading ornament,
                      not text; they are dropped before diffing (default: the ✦ ornament). Pass "" to keep.
Writes into DIR: docx_extracted.md (the DOCX flattened, headings/images/tables marked), docx_meta.json
(styles used, media files, alt texts in document order, consecutive duplicates, core properties),
delta_report.md and delta.json (summary + every change group in document order).
Exit 0 always (a diff is information); exit 2 on usage errors. Stdlib only.
"""
import argparse
import difflib
import json
import os
import re
import sys
import zipfile
import xml.etree.ElementTree as ET

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
WP = "{http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing}"
DEFAULT_ORNAMENT = "✦"


def para_text(p):
    parts = []
    for node in p.iter():
        tag = node.tag
        if tag == W + "t":
            parts.append(node.text or "")
        elif tag == W + "tab":
            parts.append("\t")
        elif tag in (W + "br", W + "cr"):
            parts.append("\n")
        elif tag == W + "footnoteReference":
            parts.append("[^fn]")
    return "".join(parts)


def has_image(p):
    for node in p.iter():
        t = node.tag
        if t.endswith("}drawing") or t.endswith("}pict") or t.endswith("}blip"):
            return True
    return False


def alt_texts(p):
    return [d.get("descr", "") for d in p.iter(WP + "docPr")]


def style_of(p):
    ppr = p.find(W + "pPr")
    if ppr is None:
        return ""
    ps = ppr.find(W + "pStyle")
    return (ps.get(W + "val") if ps is not None else "") or ""


def style_names(z):
    names = {}
    try:
        root = ET.fromstring(z.read("word/styles.xml"))
    except KeyError:
        return names
    for s in root.iter(W + "style"):
        sid = s.get(W + "styleId")
        n = s.find(W + "name")
        names[sid] = (n.get(W + "val") if n is not None else sid) or sid
    return names


def heading_level(style_id, style_name):
    s = (style_name or style_id or "").lower().replace(" ", "")
    m = re.search(r"heading(\d)", s)
    if m:
        return int(m.group(1))
    if s == "title":
        return 1
    return 0


def extract_docx(path, ornament):
    z = zipfile.ZipFile(path)
    names = style_names(z)
    root = ET.fromstring(z.read("word/document.xml"))
    body = root.find(W + "body")
    blocks, alts, dropped = [], [], 0
    img_n = 0
    for child in body:
        if child.tag == W + "p":
            sid = style_of(child)
            sname = names.get(sid, sid)
            txt = para_text(child)
            lvl = heading_level(sid, sname)
            if has_image(child):
                img_n += 1
                alts.extend(alt_texts(child))
                blocks.append({"type": "image", "n": img_n, "text": txt.strip(), "style": sname})
                continue
            t = txt.strip()
            if not t:
                continue
            if ornament and all(c in ornament for c in t):
                dropped += 1
                continue
            if lvl:
                blocks.append({"type": "heading", "level": lvl, "text": t, "style": sname})
            else:
                blocks.append({"type": "para", "text": t, "style": sname})
        elif child.tag == W + "tbl":
            rows = []
            for tr in child.iter(W + "tr"):
                cells = [" ".join(para_text(p).strip() for p in tc.iter(W + "p")).strip() for tc in tr.findall(W + "tc")]
                rows.append(" | ".join(cells))
            blocks.append({"type": "table", "text": "\n".join(rows), "style": "table"})
    media = [n for n in z.namelist() if n.startswith("word/media/")]
    core = ""
    try:
        core = z.read("docProps/core.xml").decode("utf-8", "replace")
    except KeyError:
        pass
    meta = {"styles_used": sorted({b.get("style", "") for b in blocks}), "media_files": len(media), "media": media,
            "alt_texts_in_document_order": alts, "ornament_paragraphs_dropped": dropped, "core_xml": core[:2000]}
    return blocks, meta


def load_master(path):
    blocks, quote_buf, para = [], [], []

    def flush_quote():
        if quote_buf:
            blocks.append({"type": "para", "text": "\n".join(quote_buf), "style": "quote"})
            quote_buf.clear()

    def flush_para():
        if para:
            blocks.append({"type": "para", "text": " ".join(para), "style": "body"})
            para.clear()

    with open(path, encoding="utf-8") as f:
        lines = f.read().split("\n")
    for line in lines:
        s = line.rstrip()
        if s.startswith(">"):
            flush_para()
            q = s[1:].strip()
            if q:
                quote_buf.append(q)
            continue
        flush_quote()
        if not s.strip():
            flush_para()
            continue
        m = re.match(r"^(#{1,6})\s+(.*)", s)
        if m:
            flush_para()
            blocks.append({"type": "heading", "level": len(m.group(1)), "text": m.group(2).strip(), "style": "md"})
            continue
        m = re.match(r"^!\[(.*?)\]\((.*?)\)", s)
        if m:
            flush_para()
            blocks.append({"type": "image", "text": m.group(1), "path": m.group(2), "style": "md"})
            continue
        if s.startswith("[IMAGE"):
            flush_para()
            continue
        if s.startswith("|"):
            flush_para()
            blocks.append({"type": "table", "text": s, "style": "md"})
            continue
        if s.strip() in ("---", "***", "* * *"):
            flush_para()
            blocks.append({"type": "break", "text": "* * *", "style": "md"})
            continue
        para.append(s.strip())
    flush_para()
    flush_quote()
    return blocks


def load_any(path, ornament):
    if path.lower().endswith(".docx"):
        return extract_docx(path, ornament)[0]
    return load_master(path)


def norm(t):
    t = t.replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')
    t = t.replace(" ", " ").replace("—", "-").replace("–", "-").replace("‑", "-")
    t = t.replace("‍", "").replace("⁠", "")
    t = re.sub(r"[*_`]+", "", t)
    t = re.sub(r"\s+", " ", t).strip()
    return t


def words(t):
    return len(re.findall(r"\S+", t))


def word_diff(a, b):
    aw, bw = a.split(" "), b.split(" ")
    sm = difflib.SequenceMatcher(None, aw, bw, autojunk=False)
    out = []
    for op, i1, i2, j1, j2 in sm.get_opcodes():
        if op == "equal":
            seg = aw[i1:i2]
            out.append(" ".join(seg) if len(seg) <= 8 else " ".join(seg[:3]) + " ... " + " ".join(seg[-3:]))
        elif op == "delete":
            out.append("[-" + " ".join(aw[i1:i2]) + "-]")
        elif op == "insert":
            out.append("{+" + " ".join(bw[j1:j2]) + "+}")
        else:
            out.append("[-" + " ".join(aw[i1:i2]) + "-]{+" + " ".join(bw[j1:j2]) + "+}")
    return " ".join(out)


def matchable(blocks):
    idx = [k for k, b in enumerate(blocks) if b["type"] in ("para", "heading", "table")]
    return idx, [norm(blocks[k]["text"]) for k in idx]


def nearest_heading(blocks, k):
    for j in range(min(k, len(blocks) - 1), -1, -1):
        if blocks[j]["type"] == "heading":
            return blocks[j]["text"]
    return "(before first heading)"


def diff_blocks(mblocks, dblocks):
    midx, mseq = matchable(mblocks)
    didx, dseq = matchable(dblocks)
    sm = difflib.SequenceMatcher(None, mseq, dseq, autojunk=False)
    changes, equal_blocks = [], 0
    for op, i1, i2, j1, j2 in sm.get_opcodes():
        if op == "equal":
            equal_blocks += i2 - i1
            continue
        entry = {"op": op,
                 "where_docx": nearest_heading(dblocks, didx[j1] if j1 < len(didx) else len(dblocks) - 1),
                 "where_master": nearest_heading(mblocks, midx[i1] if i1 < len(midx) else len(mblocks) - 1),
                 "master": [mblocks[midx[k]]["text"] for k in range(i1, i2)],
                 "docx": [dblocks[didx[k]]["text"] for k in range(j1, j2)]}
        if op == "replace" and (i2 - i1) == (j2 - j1):
            entry["word_diff"] = [word_diff(mseq[i1 + k], dseq[j1 + k]) for k in range(i2 - i1)]
        changes.append(entry)
    return changes, equal_blocks, len(mseq), len(dseq)


def consecutive_duplicates(blocks):
    out, prev = [], None
    for b in blocks:
        if b["type"] != "para":
            prev = None
            continue
        n = norm(b["text"])
        if prev is not None and n == prev and len(n) > 40:
            out.append(b["text"][:120])
        prev = n
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--docx", required=True, help="the author's revised DOCX")
    ap.add_argument("--master", help="the text it was edited from: an assembled master .md or the delivered .docx")
    ap.add_argument("--candidates", nargs="*", default=[], help="lineage test: rank these masters by change groups")
    ap.add_argument("--out", help="output directory (required with --master)")
    ap.add_argument("--ornament", default=DEFAULT_ORNAMENT, help="ornament characters to drop (default ✦)")
    a = ap.parse_args()
    if not a.master and not a.candidates:
        ap.error("give --master (with --out) and/or --candidates")
    dblocks, dmeta = extract_docx(a.docx, a.ornament)
    dmeta["consecutive_duplicate_paragraphs"] = consecutive_duplicates(dblocks)

    if a.candidates:
        print("lineage test (fewest change groups = the file the author edited):")
        rows = []
        for c in a.candidates:
            ch, eq, nm, nd = diff_blocks(load_any(c, a.ornament), dblocks)
            rows.append((len(ch), eq, nm, c))
        for n, eq, nm, c in sorted(rows):
            print("  %4d change groups, %4d/%4d blocks identical   %s" % (n, eq, nm, c))
    if not a.master:
        return 0
    if not a.out:
        ap.error("--out is required with --master")
    os.makedirs(a.out, exist_ok=True)
    mblocks = load_any(a.master, a.ornament)
    changes, equal_blocks, nm, nd = diff_blocks(mblocks, dblocks)

    with open(os.path.join(a.out, "docx_extracted.md"), "w", encoding="utf-8") as f:
        for b in dblocks:
            if b["type"] == "heading":
                f.write("#" * b["level"] + " " + b["text"] + "\n\n")
            elif b["type"] == "image":
                f.write("![IMAGE %d] %s\n\n" % (b["n"], b["text"]))
            elif b["type"] == "table":
                f.write("[TABLE]\n" + b["text"] + "\n\n")
            else:
                f.write("<%s> " % b["style"] + b["text"] + "\n\n")
    with open(os.path.join(a.out, "docx_meta.json"), "w", encoding="utf-8") as f:
        json.dump(dmeta, f, indent=1, ensure_ascii=False)

    mheads = [b["text"] for b in mblocks if b["type"] == "heading"]
    dheads = [b["text"] for b in dblocks if b["type"] == "heading"]
    summary = {
        "master": a.master, "docx": a.docx, "ornament_paragraphs_dropped": dmeta["ornament_paragraphs_dropped"],
        "master_blocks": nm, "docx_blocks": nd, "equal_blocks": equal_blocks,
        "master_words": sum(words(b["text"]) for b in mblocks if b["type"] in ("para", "heading", "table")),
        "docx_words": sum(words(b["text"]) for b in dblocks if b["type"] in ("para", "heading", "table")),
        "master_headings": len(mheads), "docx_headings": len(dheads),
        "master_images": sum(1 for b in mblocks if b["type"] == "image"),
        "docx_images": sum(1 for b in dblocks if b["type"] == "image"), "docx_media_files": dmeta["media_files"],
        "change_groups": len(changes),
        "changed_master_blocks": sum(len(c["master"]) for c in changes),
        "changed_docx_blocks": sum(len(c["docx"]) for c in changes),
        "headings_only_in_docx": [h for h in dheads if norm(h) not in {norm(x) for x in mheads}],
        "headings_only_in_master": [h for h in mheads if norm(h) not in {norm(x) for x in dheads}],
        "consecutive_duplicate_paragraphs": dmeta["consecutive_duplicate_paragraphs"],
    }
    with open(os.path.join(a.out, "delta.json"), "w", encoding="utf-8") as f:
        json.dump({"summary": summary, "changes": changes}, f, indent=1, ensure_ascii=False)
    with open(os.path.join(a.out, "delta_report.md"), "w", encoding="utf-8") as f:
        f.write("# DOCX vs master delta\n\n")
        for k, v in summary.items():
            if isinstance(v, list):
                f.write("- %s: %d\n" % (k, len(v)))
                for x in v:
                    f.write("    - %s\n" % x)
            else:
                f.write("- %s: %s\n" % (k, v))
        f.write("\n## Changes (in document order)\n\n")
        for n, c in enumerate(changes, 1):
            f.write("### %d. %s  [docx: %s | master: %s]\n\n" % (n, c["op"].upper(), c["where_docx"], c["where_master"]))
            if c.get("word_diff"):
                for wd in c["word_diff"]:
                    f.write("- WORD DIFF: " + wd + "\n")
            else:
                for t in c["master"]:
                    f.write("- MASTER: " + t.replace("\n", " / ") + "\n")
                for t in c["docx"]:
                    f.write("- DOCX:   " + t.replace("\n", " / ") + "\n")
            f.write("\n")
        if summary["consecutive_duplicate_paragraphs"]:
            f.write("## Consecutive duplicate paragraphs in the DOCX (paste slips; keep one, report to the author)\n\n")
            for d in summary["consecutive_duplicate_paragraphs"]:
                f.write("- " + d + "\n")
    print(json.dumps(summary, indent=1, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
