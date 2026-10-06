#!/usr/bin/env python3
"""zht_common.py: shared machinery of the zh-Hant-TW edition of Five Hours Apart (BOOK_TRANSLATION_METHOD_v3 §7).

UNITS is the reading order and the census of units every gate counts. Blocks are cut exactly as the English
extractor cut the source (blank lines), so the n-th block of a translated unit is the n-th source segment.
The registry grammar (BOOK_TRANSLATION_METHOD_v3 §8.4), in the EN census cell, fields separated by ' ;; ':
    <regex>                     case-insensitive; a leading '=' makes it case-sensitive (and is stripped)
    @except id,id               sites counted but exempt from conformance
    @accept form|form           alternates that also satisfy a site (besides the zh-Hant cell)
    @types code,para,dialogue   check only segments of these types
    @site                       informational: the row is checked only where its pattern matches (always true here)
A zh-Hant cell of '=' means "the English match itself must appear verbatim" (a kept Latin token); an empty cell
means no conformance check (an informational row).
"""
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
WS = os.path.dirname(HERE)
KEY = os.path.join(WS, "_key")
GEN = os.path.join(WS, "_generated")

UNITS = ("front", "part_1", "ch_01", "ch_02", "ch_03", "ch_04", "ch_05", "ch_06", "ch_07", "ch_08", "ch_09",
         "part_2", "ch_10", "ch_11", "ch_12", "ch_13", "ch_14",
         "part_3", "ch_15", "ch_16", "ch_17", "ch_18")

CJK_RE = re.compile(r"[㐀-䶿一-鿿豈-﫿]")
LATIN_RUN_RE = re.compile(r"[A-Za-z][A-Za-z'’\-]+")
# machine tokens that must survive a log row untouched: dates/times, ids like E/1931 #8812 NE/6 S+E, hash stubs,
# scientific numbers, numbers with units, airport codes, the runway, the coordinates
TOKEN_RE = re.compile(
    r"\d{2}-\d{2} \d{2}:\d{2}(?::\d{2}(?:\.\d+)?)?…?"      # 10-27 20:14:09 / 03:11:59.999999…
    r"|\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}"                # 2026-06-14 09:12:40
    r"|\b\d{2}:\d{2}(?:–\d{2}:\d{2})?\b"                   # 18:30–19:00, 03:12
    r"|\b[A-Z]{1,2}/\d+\b|\b[A-Z]\+[A-Z]\b"                 # E/1931 N/2210 NE/6 S+E
    r"|#\d+"                                               # #8812
    r"|\b[0-9a-f]{4}…"                                     # 2c71…
    r"|\b\d+(?:\.\d+)?e\d+\b"                              # 1.0e13 4.1e27
    r"|\b\d+(?:\.\d+)?(?:/\d+)?\b"                         # plain numbers, 1/14000, 0.08
    r"|\b(?:DAL|LHR|UTC|KELVIN)\b|\b27L\b|\b51N 29W\b|\bP4\b|\b10[³⁷⁹¹²]+\b|\bn_f\(S\)")

# characters that only exist in the simplified script (a draft that carries one is not Traditional)
SIMPLIFIED_ONLY = set("这么们国时说为会对还来发东车门问间开关后经让给与书长见样认识记录没点难过马风电头实现应该线组织"
                      "总结进统继续动态术语气权体验务业产资质软单价报标题类义论议设计划层级据库")


def read(p):
    with open(p, encoding="utf-8-sig") as f:
        return f.read().replace("\r\n", "\n")


def write(p, s):
    os.makedirs(os.path.dirname(p) or ".", exist_ok=True)
    with open(p, "w", encoding="utf-8", newline="\n") as f:
        f.write(s)


def blocks(text):
    return [b.strip("\n") for b in re.split(r"\n\s*\n", text) if b.strip()]


def seg_type(b):
    s = b.strip()
    if s.startswith("```"):
        return "code"
    if s.startswith("# "):
        return "h1"
    if s.startswith("## "):
        return "h2"
    if s.startswith(">"):
        return "quote"
    if s.startswith("*") and s.endswith("*") and s.count("*") == 2:
        return "italic"
    if s.startswith('"'):
        return "dialogue"
    return "para"


def load_segments(path=None):
    """unit -> ordered list of segment dicts (id, unit, seq, type, text)."""
    path = path or os.path.join(KEY, "segments.jsonl")
    out = {}
    with open(path, encoding="utf-8") as f:
        for ln in f:
            d = json.loads(ln)
            out.setdefault(d["unit"], []).append(d)
    for u in out:
        out[u].sort(key=lambda d: d["seq"])
    return out


def cjk_count(s):
    return len(CJK_RE.findall(s))


def code_tokens(text):
    return TOKEN_RE.findall(text)


def _parse_en(cell):
    parts = [p.strip() for p in cell.split(";;")]
    pat = parts[0]
    flags = re.IGNORECASE
    if pat.startswith("="):
        pat = pat[1:]
        flags = 0
    spec = {"pattern": pat, "flags": flags, "excepts": set(), "accepts": [], "types": None, "site": False}
    for p in parts[1:]:
        if p.startswith("@except"):
            spec["excepts"] |= {x.strip() for x in p[len("@except"):].split(",") if x.strip()}
        elif p.startswith("@accept"):
            spec["accepts"] += [x.strip() for x in p[len("@accept"):].split("|") if x.strip()]
        elif p.startswith("@types"):
            spec["types"] = {x.strip() for x in p[len("@types"):].split(",") if x.strip()}
        elif p.startswith("@site"):
            spec["site"] = True
    return spec


def parse_registry(path=None, amendments=None):
    """Rows of the registry (+ amendments that win on id; '=' keeps a cell). Returns a list of dicts."""
    path = path or os.path.join(KEY, "registry_merged.tsv")
    cols = ["id", "tier", "EN", "zh-Hans", "zh-Hant", "first_use", "count", "note"]
    rows, seen = [], {}
    for p in [path] + ([amendments] if amendments and os.path.exists(amendments) else []):
        amend = p != path
        for ln in read(p).split("\n"):
            if not ln.strip() or ln.startswith("#") or ln.startswith("id\t"):
                continue
            cells = ln.split("\t")
            cells += [""] * (len(cols) - len(cells))
            row = dict(zip(cols, [c.strip() for c in cells[:len(cols)]]))
            if amend:
                if row["id"] in seen:
                    base = rows[seen[row["id"]]]
                    for k in cols:
                        if row[k] != "=" and (row[k] or k in ("first_use", "count")):
                            base[k] = row[k]
                    continue
                if any(row[k] == "=" for k in cols):
                    raise SystemExit("amendment %s has '=' cells but no base row" % row["id"])
            if row["id"] in seen:
                raise SystemExit("duplicate registry id %s" % row["id"])
            seen[row["id"]] = len(rows)
            rows.append(row)
    for r in rows:
        r["spec"] = _parse_en(r["EN"]) if r["EN"] else None
        try:
            r["re"] = re.compile(r["spec"]["pattern"], r["spec"]["flags"]) if r["spec"] else None
        except re.error as e:
            raise SystemExit("bad regex in registry row %s: %s" % (r["id"], e))
    return rows


def required_forms(row):
    """The forms that satisfy a site for this row: the zh-Hant cell plus @accept alternates ('=' = the match)."""
    forms = []
    if row["zh-Hant"] and row["zh-Hant"] != "=":
        forms.append(row["zh-Hant"])
    forms += row["spec"]["accepts"] if row["spec"] else []
    return forms


def load_forbidden(path=None):
    """Rows: pattern, tier (FAIL/WARN), scope (prose/all), reason."""
    path = path or os.path.join(KEY, "forbidden_zht.tsv")
    out = []
    if not os.path.exists(path):
        return out
    for ln in read(path).split("\n"):
        if not ln.strip() or ln.startswith("#") or ln.startswith("pattern\t"):
            continue
        cells = [c.strip() for c in ln.split("\t")] + ["", "", ""]
        out.append({"re": re.compile(cells[0]), "tier": cells[1] or "FAIL", "scope": cells[2] or "prose",
                    "reason": cells[3], "pattern": cells[0]})
    return out


def load_allowed_latin(path=None):
    path = path or os.path.join(KEY, "allowed_latin.txt")
    if not os.path.exists(path):
        return set()
    return {ln.strip() for ln in read(path).split("\n") if ln.strip() and not ln.startswith("#")}
