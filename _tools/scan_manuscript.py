#!/usr/bin/env python3
"""
scan_manuscript.py - deterministic packaging + placeholder gate.

The checks the executor used to run by hand as PowerShell one-liners, made a
single reproducible gate. Complements lint_manuscript.py (which owns corruption
+ blacklist + the em-dash gate): this owns the STRUCTURAL packaging invariants
that must hold before assembly, and the placeholder class that once shipped a
'[WARN ... AT LINE-READ]' into a printed Acknowledgments.

Per unit in book_config.units[], against manuscript/current/<id>_current.md:
  - file exists (missing = FAIL: assembly hard-errors on it)
  - UTF-8, no BOM
  - exactly ONE '# ' H1 line, and it equals '# ' + the config title byte-for-byte
  - zero '## ' headings (print + Kindle generators silently DROP them)
  - zero em/en dashes when voice.no_em_dashes (default true; auto-relaxed for
    translated editions that set it false)
  - zero markdown tables ('|' rows) and zero bullet/numbered list lines (the
    interior generators render neither; they fall through as literal text)
  - zero placeholders: [WARN-glyph ...], [TODO]/[TK]/[TBD]/[XXX], [BO-WRITES],
    'AT LINE-READ', 'NAME AND CREDENTIAL', angle-bracket <stubs>, ___ fill blanks
  - word count within +/-20% of target_words (WARN only; band, not a wall)
  - every mid-flow "![alt](path)" image reference resolves to an existing file
    under the workspace (all generators embed these since 2026-07-27; a
    dangling reference would build an image-less artifact, so it FAILs here)

Usage: python scan_manuscript.py --config book_config.json [--json] [--strict]
Exit: 0 clean - 1 any FAIL (or WARN with --strict) - 2 usage. Stdlib only.
"""
import argparse
import json
import re
import sys
from pathlib import Path

WARN_GLYPHS = "⚠☠❗‼"          # WARN skull bang bangbang
EM_EN = "—–"                             # em / en dash

PLACEHOLDER_PATTERNS = [
    ("warn_bracket", re.compile(r"\[[^\]]*[" + WARN_GLYPHS + r"][^\]]*\]")),
    ("bo_writes", re.compile(r"\[BO-WRITES", re.I)),
    ("todo_bracket", re.compile(r"\[(TODO|TK|TBD|XXX|FIXME|PLACEHOLDER|INSERT|TBA)\b", re.I)),
    # F-GYM-01 (2026-09-03, found by the gym witness suite on its first run):
    # mustache/template tokens. cloud/shim.py already scrubs these via
    # TEMPLATE_TOKEN_RE because the seed model echoes placeholders MID-LINE
    # (seen live, BR-QC0816), but this pre-build gate was blind to them, so an
    # unfilled {{AUTHOR_NAME}} passed the gate whose stated job is 'zero
    # placeholders' and would ship inside a produced book. Same regex as the
    # shim, deliberately, so the two layers agree.
    # False-positive risk is bounded: _prose_only() blanks fenced code blocks
    # AND inline `code`/$math$ spans before this runs, so a book that
    # legitimately shows template syntax in a code span is unaffected.
    ("mustache", re.compile(r"\{\{[^{}\n]*\}\}")),
    ("instr_caps", re.compile(r"AT LINE-READ|NAME AND CREDENTIAL|WITH CONSENT, AT")),
    ("angle_stub", re.compile(r"<[A-Za-z][A-Za-z0-9 _-]{2,40}>")),
    ("fill_blank", re.compile(r"_{3,}")),
    ("warn_glyph_any", re.compile(r"[" + WARN_GLYPHS + r"]")),
]


def load_config(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def unit_list(cfg):
    out = []
    for u in cfg.get("units", []):
        if isinstance(u, dict) and u.get("id"):
            out.append((u["id"], u.get("title", ""), u.get("target_words")))
    return out


def unit_class(cfg, uid):
    """Authorship class for a unit (CLAUDE.md §9): the unit's own `class` wins,
    else `authorship.per_chapter_overrides[uid]`, else `authorship.default_class`
    (default C). Returned uppercased."""
    for u in cfg.get("units", []):
        if isinstance(u, dict) and u.get("id") == uid and u.get("class"):
            return str(u["class"]).upper()
    auth = cfg.get("authorship") or {}
    over = auth.get("per_chapter_overrides") or {}
    if uid in over and over[uid]:
        return str(over[uid]).upper()
    return str(auth.get("default_class") or "C").upper()


# Inline `code` and $math$ spans legitimately hold '<stubs>', '_', '|' and the
# like; they are blanked before the prose structural + placeholder checks (the
# inline analogue of the fenced-block exclusion in _prose_only).
_INLINE_SPAN = re.compile(r"`[^`\n]*`|\$\$[^\n]*?\$\$|\$(?=[^$\n]*[\\{])[^$\n]{1,150}?\$")


def _prose_only(text: str):
    """Lines OUTSIDE fenced code blocks (```), with inline `code`/$math$ spans
    blanked. Fenced blocks and inline code/math legitimately contain '# comments',
    '<stubs>', '|' rows, '_' and '-' items, so they are excluded from the prose
    structural + placeholder checks. A unit with no code is returned unchanged."""
    out, in_code = [], False
    for l in text.split("\n"):
        if l.lstrip().startswith("```"):
            in_code = not in_code
            continue
        if not in_code:
            out.append(_INLINE_SPAN.sub("code", l))
    return out


def scan_unit(path: Path, title: str, target, no_dash: bool, waivers=None):
    """Return (findings, words). findings: list of (level, code, detail)."""
    f = []
    waivers = [w for w in (waivers or []) if w]
    raw = path.read_bytes()
    if raw[:3] == b"\xef\xbb\xbf":
        f.append(("FAIL", "bom", "UTF-8 BOM present (tools expect no-BOM)"))
        raw = raw[3:]
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as e:
        return [("FAIL", "encoding", f"not valid UTF-8: {e}")], 0

    # The interior generators now render fenced code blocks, GFM tables, and
    # bullet/numbered lists (2026-07-15 extension), so tables and lists are no
    # longer flagged. The structural checks (h1 / ## / placeholder) run on PROSE
    # only: a '# comment' or an '<stub>' inside verbatim code is not a heading or
    # a placeholder. The em/en dash gate stays whole-file (Bo's #1 rule).
    prose_lines = _prose_only(text)
    prose_text = "\n".join(prose_lines)

    h1 = [l for l in prose_lines if l.startswith("# ") and not l.startswith("## ")]
    if len(h1) != 1:
        f.append(("FAIL", "h1_count", f"{len(h1)} H1 line(s) outside code (need exactly 1)"))
    if h1 and title and h1[0].rstrip("\r") != f"# {title}":
        f.append(("FAIL", "h1_title", f"H1 {h1[0].rstrip()!r} != config '# {title}'"))
    if not h1:
        f.append(("FAIL", "h1_missing", "no '# ' unit heading"))

    n_h2 = sum(1 for l in prose_lines if l.startswith("## ") and not l.startswith("### "))
    if n_h2:
        f.append(("FAIL", "h2_present", f"{n_h2} '## ' heading(s) (generators drop these)"))

    if no_dash:
        # voice.lint_waivers: exact source-faithful strings (a verbatim quote whose
        # own punctuation carries an em/en dash). A line carrying a waived string is
        # excluded from the dash count and reported as WAIVED, so this gate agrees
        # with lint_manuscript.py instead of contradicting it. Fidelity for quoted
        # source; the hard gate still stands over the author's own prose.
        n = waived = 0
        for line in text.splitlines():
            c = sum(line.count(ch) for ch in EM_EN)
            if not c:
                continue
            if any(w in line for w in waivers):
                waived += c
            else:
                n += c
        if n:
            f.append(("FAIL", "emdash", f"{n} em/en dash(es) (voice.no_em_dashes on)"))
        if waived:
            f.append(("WAIVED", "emdash_waived",
                      f"{waived} em/en dash(es) in verbatim quote(s) (voice.lint_waivers)"))

    for code, pat in PLACEHOLDER_PATTERNS:
        m = pat.search(prose_text)
        if m:
            ctx = prose_text[max(0, m.start() - 20):m.end() + 20].replace("\n", " ")
            f.append(("FAIL", f"placeholder_{code}", f"{m.group(0)[:60]!r}  ...{ctx}..."))

    words = len(re.findall(r"\S+", text))
    if isinstance(target, (int, float)) and target > 0:
        lo, hi = target * 0.8, target * 1.2
        if not (lo <= words <= hi):
            f.append(("WARN", "wordcount", f"{words} words vs target {target} (band {int(lo)}-{int(hi)})"))
    return f, words


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--strict", action="store_true", help="WARN counts as failure")
    ap.add_argument("--allow-midflow-print", action="store_true",
                    help="deprecated no-op (print interiors embed mid-flow "
                         "images since 2026-07-27; the divergence guard this "
                         "waived is retired)")
    a = ap.parse_args()

    cfgp = Path(a.config).resolve()
    cfg = load_config(cfgp)
    ws = cfgp.parent
    cur = ws / "manuscript" / "current"
    no_dash = (cfg.get("voice") or {}).get("no_em_dashes", True) is not False
    waivers = (cfg.get("voice") or {}).get("lint_waivers") or []

    report = {"config": str(cfgp), "units": [], "total_words": 0}
    any_fail = any_warn = False
    for uid, title, target in unit_list(cfg):
        path = cur / f"{uid}_current.md"
        cls = unit_class(cfg, uid)
        # Class-A awareness (2026-08-02, CLAUDE.md §9): a Class-A manuscript is
        # SUPPOSED to be empty until the author writes it — an empty/absent file
        # is its correct mid-project state, not a packaging failure. Once prose
        # exists it is scanned normally PLUS a visible WARN to confirm the prose
        # is human-authored (machine-drafting a Class-A is the never-list's top
        # entry, and no scan can tell authorship from bytes — a human confirms).
        if cls == "A":
            if not path.exists() or not path.read_text(
                    encoding="utf-8", errors="replace").strip():
                report["units"].append({
                    "id": uid, "verdict": "PASS", "words": 0, "class": "A",
                    "findings": [["PASS", "class_a_empty",
                                  "Class-A unit awaiting the author "
                                  "(empty by design; CLAUDE.md 9)"]]})
                continue
        elif not path.exists():
            report["units"].append({"id": uid, "verdict": "FAIL",
                                     "findings": [["FAIL", "missing_file", str(path)]]})
            any_fail = True
            continue
        findings, words = scan_unit(path, title, target, no_dash, waivers)
        if cls == "A":
            findings.append(("WARN", "class_a_has_prose",
                             "Class-A unit carries prose: confirm it is "
                             "HUMAN-authored (a machine-drafted Class-A "
                             "violates CLAUDE.md 9; no scan can tell "
                             "authorship from bytes)"))
        report["total_words"] += words
        levels = {x[0] for x in findings}
        verdict = "FAIL" if "FAIL" in levels else ("WARN" if "WARN" in levels else "PASS")
        any_fail |= verdict == "FAIL"
        any_warn |= "WARN" in levels
        report["units"].append({"id": uid, "verdict": verdict, "words": words,
                                "class": cls,
                                "findings": [list(x) for x in findings]})
    # Mid-flow image existence check (2026-07-27): every generator now EMBEDS a
    # standalone "![alt](path)" line — print embed arrived with the figure
    # program; kindle/epub have embedded since 2026-07-23 — so the old
    # midflow-vs-print divergence guard is retired (--allow-midflow-print is
    # accepted as a no-op for compatibility). What CAN still go wrong is a
    # dangling reference: generators warn-and-skip a missing file at build time,
    # silently shipping an image-less artifact. Fail that here, before anything
    # builds. Paths resolve workspace-relative, exactly as the generators do.
    mf_re = re.compile(r"^!\[[^\]]*\]\(([^)\s]+)\)\s*$")
    mf_missing = []
    mf_refs = 0
    for uid, _t, _tw in unit_list(cfg):
        p = cur / f"{uid}_current.md"
        if not p.exists():
            continue
        try:
            unit_lines = p.read_text(encoding="utf-8").splitlines()
        except Exception:
            continue
        for l in unit_lines:
            m = mf_re.match(l)
            if not m:
                continue
            mf_refs += 1
            rel = m.group(1)
            if not (ws / rel).exists():
                mf_missing.append(f"{uid}: {rel}")
    report["midflow_image_refs"] = mf_refs
    if mf_missing:
        any_fail = True
        report["units"].append({
            "id": "_midflow_images", "verdict": "FAIL",
            "findings": [["FAIL", "midflow_image_missing",
                          f"{len(mf_missing)} mid-flow image reference(s) do not "
                          f"resolve under the workspace "
                          f"({'; '.join(mf_missing[:6])}{' …' if len(mf_missing) > 6 else ''}); "
                          f"generators would warn-and-skip them and ship "
                          f"image-less artifacts"]]})
    report["all_pass"] = not (any_fail or (a.strict and any_warn))

    if a.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        for u in report["units"]:
            mark = {"PASS": "  ok", "WARN": "WARN", "FAIL": "FAIL"}[u["verdict"]]
            print(f"[{mark}] {u['id']}")
            for lvl, code, detail in u.get("findings", []):
                print(f"        {lvl} {code}: {detail}")
        n_fail = sum(1 for u in report["units"] if u["verdict"] == "FAIL")
        n_warn = sum(1 for u in report["units"] if u["verdict"] == "WARN")
        print(f"\nSCAN: {'PASS' if report['all_pass'] else 'FAIL'}  "
              f"({len(report['units'])} units, {n_fail} fail, {n_warn} warn, "
              f"{report['total_words']} words)")
    return 0 if report["all_pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
