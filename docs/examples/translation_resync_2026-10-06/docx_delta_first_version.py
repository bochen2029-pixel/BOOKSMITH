#!/usr/bin/env python3
"""docx_delta.py: flatten a DOCX to ordered blocks and diff it against a BOOKSMITH
assembled master markdown (paragraph level, with word-level detail on replacements).

Usage:
  python docx_delta.py --docx FILE.docx --master MASTER.md --out DIR
Writes into DIR: docx_extracted.md, docx_styles.json, delta_report.md, delta.json
Stdlib only.
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


def extract_docx(path):
    z = zipfile.ZipFile(path)
    names = style_names(z)
    root = ET.fromstring(z.read("word/document.xml"))
    body = root.find(W + "body")
    blocks = []
    img_n = 0
    for child in body:
        if child.tag == W + "p":
            sid = style_of(child)
            sname = names.get(sid, sid)
            txt = para_text(child)
            lvl = heading_level(sid, sname)
            if has_image(child):
                img_n += 1
                blocks.append({"type": "image", "n": img_n, "text": txt.strip(), "style": sname})
                if not txt.strip():
                    continue
                continue
            if not txt.strip():
                continue
            if lvl:
                blocks.append({"type": "heading", "level": lvl, "text": txt.strip(), "style": sname})
            else:
                blocks.append({"type": "para", "text": txt.strip(), "style": sname})
        elif child.tag == W + "tbl":
            rows = []
            for tr in child.iter(W + "tr"):
                cells = []
                for tc in tr.findall(W + "tc"):
                    cells.append(" ".join(para_text(p).strip() for p in tc.iter(W + "p")).strip())
                rows.append(" | ".join(cells))
            blocks.append({"type": "table", "text": "\n".join(rows), "style": "table"})
    media = [n for n in z.namelist() if n.startswith("word/media/")]
    core = ""
    try:
        core = z.read("docProps/core.xml").decode("utf-8", "replace")
    except KeyError:
        pass
    app = ""
    try:
        app = z.read("docProps/app.xml").decode("utf-8", "replace")
    except KeyError:
        pass
    meta = {
        "styles_used": sorted({b.get("style", "") for b in blocks}),
        "media_files": len(media),
        "media": media,
        "core_xml": core[:2000],
        "app_xml": app[:1000],
    }
    return blocks, meta


def load_master(path):
    blocks = []
    quote_buf = []
    para = []

    def flush_quote():
        nonlocal quote_buf
        if quote_buf:
            blocks.append({"type": "para", "text": "\n".join(quote_buf), "style": "quote"})
            quote_buf = []

    def flush_para():
        nonlocal para
        if para:
            blocks.append({"type": "para", "text": " ".join(para), "style": "body"})
            para = []

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


def norm(t):
    t = t.replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')
    t = t.replace(" ", " ").replace("—", "-").replace("–", "-").replace("‑", "-")
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
            if len(seg) > 8:
                out.append(" ".join(seg[:3]) + " ... " + " ".join(seg[-3:]))
            else:
                out.append(" ".join(seg))
        elif op == "delete":
            out.append("[-" + " ".join(aw[i1:i2]) + "-]")
        elif op == "insert":
            out.append("{+" + " ".join(bw[j1:j2]) + "+}")
        else:
            out.append("[-" + " ".join(aw[i1:i2]) + "-]{+" + " ".join(bw[j1:j2]) + "+}")
    return " ".join(out)


def matchable(blocks):
    idx = [k for k, b in enumerate(blocks) if b["type"] in ("para", "heading", "table")]
    seq = [norm(blocks[k]["text"]) for k in idx]
    return idx, seq


def nearest_heading(blocks, k):
    for j in range(k, -1, -1):
        if blocks[j]["type"] == "heading":
            return blocks[j]["text"]
    return "(before first heading)"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--docx", required=True)
    ap.add_argument("--master", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)

    dblocks, dmeta = extract_docx(a.docx)
    if a.master.lower().endswith(".docx"):
        mblocks, _mmeta = extract_docx(a.master)
    else:
        mblocks = load_master(a.master)

    # flattened docx for reading
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
    with open(os.path.join(a.out, "docx_styles.json"), "w", encoding="utf-8") as f:
        json.dump(dmeta, f, indent=1, ensure_ascii=False)

    midx, mseq = matchable(mblocks)
    didx, dseq = matchable(dblocks)
    sm = difflib.SequenceMatcher(None, mseq, dseq, autojunk=False)
    ops = sm.get_opcodes()

    changes = []
    equal_blocks = 0
    for op, i1, i2, j1, j2 in ops:
        if op == "equal":
            equal_blocks += i2 - i1
            continue
        entry = {
            "op": op,
            "where_docx": nearest_heading(dblocks, didx[j1] if j1 < len(didx) else len(dblocks) - 1),
            "where_master": nearest_heading(mblocks, midx[i1] if i1 < len(midx) else len(mblocks) - 1),
            "master": [mblocks[midx[k]]["text"] for k in range(i1, i2)],
            "docx": [dblocks[didx[k]]["text"] for k in range(j1, j2)],
        }
        if op == "replace" and (i2 - i1) == (j2 - j1):
            entry["word_diff"] = [word_diff(mseq[i1 + k], dseq[j1 + k]) for k in range(i2 - i1)]
        changes.append(entry)

    mwords = sum(words(b["text"]) for b in mblocks if b["type"] in ("para", "heading", "table"))
    dwords = sum(words(b["text"]) for b in dblocks if b["type"] in ("para", "heading", "table"))
    mheads = [b["text"] for b in mblocks if b["type"] == "heading"]
    dheads = [b["text"] for b in dblocks if b["type"] == "heading"]
    mimgs = sum(1 for b in mblocks if b["type"] == "image")
    dimgs = sum(1 for b in dblocks if b["type"] == "image")

    summary = {
        "master": a.master, "docx": a.docx,
        "master_blocks": len(mseq), "docx_blocks": len(dseq), "equal_blocks": equal_blocks,
        "master_words": mwords, "docx_words": dwords,
        "master_headings": len(mheads), "docx_headings": len(dheads),
        "master_images": mimgs, "docx_images": dimgs, "docx_media_files": dmeta["media_files"],
        "change_groups": len(changes),
        "changed_master_blocks": sum(len(c["master"]) for c in changes),
        "changed_docx_blocks": sum(len(c["docx"]) for c in changes),
        "headings_only_in_docx": [h for h in dheads if norm(h) not in {norm(x) for x in mheads}],
        "headings_only_in_master": [h for h in mheads if norm(h) not in {norm(x) for x in dheads}],
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
                f.write("\n")
            else:
                for t in c["master"]:
                    f.write("- MASTER: " + t.replace("\n", " / ") + "\n")
                for t in c["docx"]:
                    f.write("- DOCX:   " + t.replace("\n", " / ") + "\n")
                f.write("\n")
    print(json.dumps(summary, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
