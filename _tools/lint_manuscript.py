#!/usr/bin/env python3
"""
lint_manuscript.py — manuscript corruption + voice-drift lint (BOOKSMITH).

PURPOSE (KIT_ARCHITECTURE (c) lint_manuscript.py; LESSONS_LEDGER §3.8, §2.7)
    Block release on TWO independent classes of defect:

    (A) PDF-round-trip corruption — the artifacts that appear when a
        manuscript is round-tripped through a rendered PDF/DOCX and back to
        text before final generation (the Second Notebook build's exact
        failure). Ported from C:\\Claude-Titanic\\lint_manuscript.py:
            EMBEDDED_UNDERSCORE, PARAGRAPH_NOT_TERMINATED, UNBALANCED_EMPHASIS,
            STRAY_MARKDOWN, MULTIPLE_SPACES, MID_WORD_HYPHEN_BREAK,
            EMDASH_CONTINUATION.

    (B) SEED-blacklist / voice-drift — the forbidden-vocabulary scrubber
        (case-sensitive + case-insensitive + regex tiers) driven by
        book_config.voice.blacklist, plus sacred-term drift detection driven
        by book_config.voice.sacred_terms. Ported from
        C:\\BOOK3\\_tools\\check_acp_vocabulary.py (the 97-pattern scrubber's
        tiered structure + is_documentation_file dir-exclusion).

    Scaffolding + cached-source dirs are excluded by DEFAULT (they legitimately
    quote banned words / period-authentic vocabulary — LESSONS_LEDGER §2.7).

CONTRACT
    python lint_manuscript.py --config book_config.json [--include-docs]
                              [--root <workspace>] [--verbose]
        scans <workspace>/manuscript/current/ + <workspace>/manuscript/drafts/
        (plus any explicit path positionals). Exit codes:
            0  clean
            1  drift/corruption (BLOCKING — build should halt)
            2  usage / config error

    Blacklist / greenlist / sacred_terms come from book_config.voice.
    The workspace root is derived from the config slug
    (book_workspace/<slug>/) unless --root is given; a positional path
    overrides the manuscript-dir default entirely.

SOURCE
    C:\\Claude-Titanic\\lint_manuscript.py (corruption checks — ported in full)
    C:\\BOOK3\\_tools\\check_acp_vocabulary.py (tiered scrubber + dir-exclusion)
"""
import argparse
import json
import re
import sys
from pathlib import Path

# ─────────────────────────────────────────────────────────────────────────────
# PART A — PDF-round-trip corruption signatures
# (ported from C:\Claude-Titanic\lint_manuscript.py)
# ─────────────────────────────────────────────────────────────────────────────

TERMINAL_PUNCT = (".", "?", "!", "…", ")", "]", "}", ":",
                  # CJK terminators (zh/ja books; absent from Latin text so the
                  # Latin rules are unaffected). Added 2026-07-23 after the DRDJ
                  # replica lint false-failed every zh paragraph ending with 。
                  "。", "！", "？", "；", "：")
# Trailing closers that still count as terminated: emphasis markers, quote/paren
# characters, em/en-dashes. `*` and `_` close an italic span — the sentence-ending
# punctuation sits inside the italic and is still terminal.
TRAILING_CLOSERS = ('"', "”", "'", "’", ")", "]", "}",
                    "—", "–", "*", "_",
                    "」", "』", "）", "】", "》", "〉", "〕")

# Inline spans that are NOT prose and must be masked before the round-trip
# corruption checks: inline `code`, single-line $$block math$$, and inline $math$
# (the last only when it carries a LaTeX backslash or brace, so a prose dollar
# range like "$0.14 ... $30" is left alone). A tech-manual line such as
# 'set `sync_interval: always`' or 'play $\bar{x}_j$' is prose ABOUT code/math,
# not an 'a_Thursday' PDF-round-trip artifact. Fenced ```code``` blocks are
# already skipped wholesale elsewhere; this handles the INLINE case.
_INLINE_SPAN = re.compile(
    r"`[^`\n]*`"
    r"|\$\$[^\n]*?\$\$"
    r"|\$(?=[^$\n]*[\\{])[^$\n]{1,150}?\$"
)


def _mask_spans(s: str) -> str:
    """Replace inline code / math spans with a neutral token so their
    underscores, asterisks, and double-spaces do not trip the corruption checks.
    The token carries no surrounding spaces, so it never manufactures a
    MULTIPLE_SPACES hit out of the original spacing around the span."""
    return _INLINE_SPAN.sub("code", s)


def paragraph_ends_terminated(para: str) -> bool:
    """True if the paragraph ends with sentence-ending punctuation, allowing
    trailing quotes / parens / closing em-dashes after the terminal mark."""
    s = para.rstrip()
    while s and s[-1] in TRAILING_CLOSERS:
        s = s[:-1].rstrip()
    if not s:
        return True  # entirely-empty or all-wrapper paragraph
    # CJK style exemption (2026-07-23, DRDJ replica): letter-styled Chinese books
    # legitimately carry SHORT unterminated lines — a salutation ending with a
    # comma, a bare signature name, a dateline. Round-trip SHREDDING produces
    # LONG mid-sentence fragments, so short CJK paragraphs are exempt while long
    # unterminated ones still fire.
    if len(s) <= 16 and any("一" <= ch <= "鿿" for ch in s):
        return True
    # A paragraph wholly wrapped in parentheses is a NOTE (attribution, aside),
    # not a shredded sentence — CJK （…） or Latin (...).
    t = para.strip()
    if (t.startswith("（") and t.endswith("）")) or (t.startswith("(") and t.endswith(")")):
        return True
    # CJK enumeration/roster paragraphs (name lists joined with 、) legitimately
    # end on a name; a dense 、 ratio marks a list, not a shredded sentence.
    if t.count("、") >= 3 and t.count("、") / max(len(t), 1) > 0.06:
        return True
    # Label/directory rows ("官方网站：人生悟道 渡人渡己", "YouTube：…-摘录"):
    # a short field name, a colon, a short value — contact/social roster lines,
    # not shredded sentences (2026-07-23, DRDJ replica FAQ pages).
    if ("\n" not in t and len(t) <= 30
            and re.match(r"^[0-9A-Za-z一-鿿]{2,12}[：:]", t)):
        return True
    return s.endswith(TERMINAL_PUNCT)


def is_structural_line(line: str) -> bool:
    """Lines that don't need to end with terminal punctuation."""
    stripped = line.strip()
    if not stripped:
        return True
    if stripped.startswith("#"):
        return True
    if stripped.startswith("$$"):
        # A block-math line ($$...$$): LaTeX, not prose. Never demands terminal
        # punctuation, and its braces/underscores are not emphasis or corruption.
        return True
    if re.match(r"^[-*_]{3,}$", stripped):
        return True
    if re.match(r"^[-*+]\s+", stripped):
        return True
    if re.match(r"^\d+\.\s+", stripped):
        return True
    if re.match(r"^\|", stripped):
        # A markdown table row: never prose, never demands terminal punctuation.
        return True
    if re.match(r"^!\[[^\]]*\]\([^)\s]+\)$", stripped):
        # A standalone mid-flow markdown image line (the kit's image-anchor
        # convention, 2026-07-23): syntax, not prose — its underscores /
        # brackets / missing punctuation are not corruption.
        return True
    return False


def iter_paragraphs(text: str):
    """Yield (start_line, raw_paragraph_text) for each blank-line-delimited
    paragraph, preserving original line numbers for error reporting."""
    lines = text.split("\n")
    buf = []
    buf_start = None
    for idx, line in enumerate(lines, start=1):
        if line.strip() == "":
            if buf:
                yield buf_start, "\n".join(buf)
                buf = []
                buf_start = None
        else:
            if not buf:
                buf_start = idx
            buf.append(line)
    if buf:
        yield buf_start, "\n".join(buf)


def lint_corruption(text: str) -> list:
    """Return a list of (code, line_no, detail) corruption findings for one
    manuscript's text. Mirrors the Claude-Titanic linter's logic exactly."""
    findings = []
    in_code = False
    lines = text.split("\n")
    prev_para_lastline = None

    # Pre-pass: line numbers (1-based) that fall inside a ```-fenced code block.
    # The line-level loop below already skips fenced code via its own in_code
    # toggle, but the paragraph-level checks (PARAGRAPH_NOT_TERMINATED, etc.) run
    # off iter_paragraphs, which has no fence state — a ```python block would be
    # linted as a prose paragraph. We skip any paragraph starting inside a fence.
    fenced_lines = set()
    _in_fence = False
    for _idx, _line in enumerate(lines, start=1):
        if _line.strip().startswith("```"):
            _in_fence = not _in_fence
            fenced_lines.add(_idx)  # the fence marker line itself
            continue
        if _in_fence:
            fenced_lines.add(_idx)

    # --- Line-level checks (raw lines) ---
    for idx, line in enumerate(lines, start=1):
        if line.strip().startswith("```"):
            in_code = not in_code
            continue
        if in_code:
            continue
        # A markdown table row legitimately carries column-alignment padding
        # (2+ spaces) and cell tokens with underscores (val_1). These are table
        # formatting, not PDF-round-trip corruption, so the line-level MULTIPLE_
        # SPACES / EMBEDDED_UNDERSCORE / hyphen checks skip table rows.
        if line.lstrip().startswith("|"):
            continue
        # Standalone mid-flow image lines are syntax, not prose (see
        # is_structural_line): skip the line-level corruption checks too.
        if re.match(r"^!\[[^\]]*\]\([^)\s]+\)$", line.strip()):
            continue

        # Mask inline `code` / $math$ so their underscores and column padding are
        # not read as 'a_Thursday' corruption; the detail still shows the raw line.
        scrub = _mask_spans(line)

        # CHECK 5: multiple consecutive spaces mid-content.
        if re.search(r"\S {2,}\S", scrub):
            findings.append(("MULTIPLE_SPACES", idx,
                             f"Line has 2+ consecutive spaces mid-content: {line.strip()[:80]!r}"))

        # CHECK 1: embedded underscore inside a word (a_Thursday).
        for m in re.finditer(r"\w_\w", scrub):
            findings.append(("EMBEDDED_UNDERSCORE", idx,
                             f"Embedded underscore in word: {m.group()!r} in line {line.strip()[:80]!r}"))

        # CHECK 6: mid-word hyphen + end-of-line followed by lowercase.
        if line.rstrip().endswith("-") and not line.rstrip().endswith("--"):
            next_nonblank = next((lines[j].lstrip() for j in range(idx, len(lines))
                                  if lines[j].strip()), "")
            if next_nonblank and next_nonblank[0].islower():
                findings.append(("MID_WORD_HYPHEN_BREAK", idx,
                                 f"Hyphen at line end followed by lowercase continuation: "
                                 f"{line.strip()[-30:]!r} + {next_nonblank[:30]!r}"))

    # --- Paragraph-level checks ---
    for start_line, para in iter_paragraphs(text):
        stripped_para = para.strip()
        if not stripped_para:
            continue

        # Skip paragraphs that begin inside a fenced code block: iter_paragraphs
        # has no fence state, so a ```python block would otherwise be linted as
        # prose (odd '_'/'*', "not terminated", stray-markdown false positives).
        if start_line in fenced_lines:
            prev_para_lastline = None
            continue

        first_line = stripped_para.split("\n", 1)[0]
        if is_structural_line(first_line):
            prev_para_lastline = None
            continue

        # Skip whole markdown-table blocks: a table is one blank-line-delimited
        # paragraph whose every non-blank line is a table row. Its pipes/dashes
        # trip UNBALANCED_EMPHASIS and its cells have no terminal punctuation.
        if all(l.lstrip().startswith("|")
               for l in stripped_para.split("\n") if l.strip()):
            prev_para_lastline = None
            continue

        # Skip blockquotes wholly (quoted text, different rules).
        if all(l.lstrip().startswith(">") for l in stripped_para.split("\n") if l.strip()):
            prev_para_lastline = None
            continue

        # CHECK 3: unbalanced emphasis markers within a paragraph. Inline code /
        # math is masked first, so `base_url` and $n_j$ do not read as stray
        # italic markers.
        masked_para = _mask_spans(stripped_para)
        underscores = len(re.findall(r"(?<!\\)_", masked_para))
        if underscores % 2 != 0:
            findings.append(("UNBALANCED_EMPHASIS", start_line,
                             f"Odd number of '_' markers ({underscores}) in paragraph: {stripped_para[:80]!r}"))
        # A lone asterisk directly after a CJK character or CJK closer is a
        # printed FOOTNOTE MARKER (…《他的肺里装满了尘埃》* — 2026-07-23, DRDJ
        # replica), not an emphasis delimiter: exclude it from the balance.
        # EXCEPT a paragraph-final asterisk when the paragraph itself OPENS
        # with one: a fully wrapped italic caption ending in a CJK closer
        # (*……（图版待补。）* — 2026-08-12, carlquist_zh) is a closing marker,
        # not a footnote.
        emph_probe = masked_para
        _wrapped_tail = (emph_probe.startswith("*") and emph_probe.endswith("*")
                         and not emph_probe.endswith("**") and len(emph_probe) > 2)
        if _wrapped_tail:
            emph_probe = emph_probe[:-1]
        emph_probe = re.sub(r"(?<=[一-鿿》」』）])\*(?!\*)", "", emph_probe)
        if _wrapped_tail:
            emph_probe += "*"
        asterisks = len(re.findall(r"(?<!\*)\*(?!\*)", emph_probe))
        if asterisks % 2 != 0:
            findings.append(("UNBALANCED_EMPHASIS", start_line,
                             f"Odd number of '*' markers ({asterisks}) in paragraph: {stripped_para[:80]!r}"))

        # CHECK 4: stray markdown link syntax inside prose.
        if re.search(r"\[[^\]]+\]\([^)]+\)", masked_para):
            findings.append(("STRAY_MARKDOWN", start_line,
                             f"Link syntax inside prose paragraph: {stripped_para[:80]!r}"))

        # CHECK 2: paragraph not terminated with sentence-ending punctuation.
        last_line_of_para = stripped_para.split("\n")[-1].strip()
        is_attribution = (last_line_of_para.startswith("—") or
                          last_line_of_para.startswith("--"))
        if not is_attribution and not paragraph_ends_terminated(stripped_para):
            last_chars = stripped_para.rstrip()[-30:]
            findings.append(("PARAGRAPH_NOT_TERMINATED", start_line,
                             f"Paragraph ends without terminal punctuation; tail: {last_chars!r}"))

        # CHECK 7: split-sentence signature — previous paragraph didn't
        # terminate AND current paragraph starts with a lowercase letter.
        if prev_para_lastline is not None:
            prev_stripped = prev_para_lastline.rstrip()
            if prev_stripped and not prev_stripped.endswith(TERMINAL_PUNCT + TRAILING_CLOSERS):
                first_char = stripped_para.lstrip()[:1]
                if first_char and first_char.islower():
                    findings.append(("EMDASH_CONTINUATION", start_line,
                                     f"Paragraph starts lowercase {stripped_para[:40]!r} after unterminated "
                                     f"previous paragraph ending {prev_stripped[-30:]!r}"))

        prev_para_lastline = stripped_para

    return findings


# ─────────────────────────────────────────────────────────────────────────────
# PART A2 — the em-dash HARD gate (AUTHOR VOICE, docs/author_voice/AUTHOR_VOICE_Bo_Chen.md §1)
# ─────────────────────────────────────────────────────────────────────────────
# Bo's named #1 AI-tell: NO em-dashes (U+2014) or en-dashes (U+2013) in prose.
# This existed only as prose guidance + a per-book blacklist entry nobody set,
# so the first book shipped saturated with them. It is a real gate now: enabled
# by voice.no_em_dashes (DEFAULT TRUE). Compound-adjective hyphens (U+002D, "-")
# are a DIFFERENT character and are never flagged; only U+2014 / U+2013 are.
EM_DASHES = {"—": "U+2014 em-dash", "–": "U+2013 en-dash",
             "―": "U+2015 horizontal bar", "‒": "U+2012 figure dash",
             "−": "U+2212 minus sign"}


def lint_em_dashes(text: str) -> list:
    """Flag every em/en-dash outside fenced code blocks. Route the pause to a
    comma, colon, period, semicolon, or parentheses (Bo's real substitute is the
    semicolon). Table '(n/a)' placeholder dashes are rare in prose; if one is
    legitimate, replace it with '(none)'."""
    findings = []
    in_code = False
    for idx, line in enumerate(text.split("\n"), start=1):
        if line.strip().startswith("```"):
            in_code = not in_code
            continue
        if in_code:
            continue
        # Carve-out (LESSONS_LEDGER §18.1): a markdown table row may use '—' as an
        # (n/a) placeholder, which feedback_no_em_dashes.md sanctions. That
        # exemption is ONLY for a standalone-dash cell — a cell whose entire
        # stripped content is the dash character. An em-dash used as prose
        # punctuation INSIDE a table cell still blocks the HARD gate.
        scan_line = line
        if line.lstrip().startswith("|"):
            # Split into cells on unescaped pipes; drop the empty leading/trailing
            # cells produced by the row's border pipes. Keep only cells whose
            # stripped content is NOT exactly one dash char (those are the
            # sanctioned (n/a) placeholders); rejoin the rest for dash detection.
            cells = re.split(r"(?<!\\)\|", line)
            kept = [c for c in cells if c.strip() not in EM_DASHES]
            scan_line = " ".join(kept)
        for ch, name in EM_DASHES.items():
            n = scan_line.count(ch)
            if n:
                findings.append(("EM_DASH", idx,
                                 f"{n}x {name} in prose — Bo forbids em-dashes "
                                 f"(AI tell); use , : . ; or ( ): {line.strip()[:80]!r}"))
    return findings


# ─────────────────────────────────────────────────────────────────────────────
# PART B — voice-drift / blacklist scrubber
# (tiered structure ported from C:\BOOK3\_tools\check_acp_vocabulary.py)
# ─────────────────────────────────────────────────────────────────────────────

# A blacklist entry may be a bare phrase (case-insensitive substring) or a
# "regex:<pattern>" / "cs:<phrase>" tagged form. Bare phrases with an uppercase
# character are treated as case-SENSITIVE (proper-noun style), matching the
# check_acp_vocabulary convention that capitalized forbidden terms are only
# forbidden when capitalized.

def compile_blacklist(blacklist: list) -> tuple:
    """Split the config blacklist into (case_sensitive, case_insensitive, regex)
    tiers. Returns three lists of (needle_or_pattern, label)."""
    cs, ci, rx = [], [], []
    for raw in blacklist:
        entry = str(raw).strip()
        if not entry:
            continue
        if entry.startswith("regex:"):
            pat = entry[len("regex:"):]
            try:
                rx.append((re.compile(pat), f"blacklist regex {pat!r}"))
            except re.error as exc:
                print(f"[warn] bad blacklist regex {pat!r}: {exc}", file=sys.stderr)
            continue
        if entry.startswith("cs:"):
            phrase = entry[len("cs:"):]
            cs.append((phrase, f"blacklist (case-sensitive) {phrase!r}"))
            continue
        # Slash-wrapped entry (/pattern/) is a regex — the form the voice docs
        # mandate for H2/H3 meta-opener/summary atoms. Must be recognized BEFORE
        # the uppercase heuristic, or `/(?i)Key Takeaways/` lands in the literal
        # case-sensitive tier (slashes included) and never matches prose.
        if len(entry) >= 2 and entry.startswith("/") and entry.endswith("/"):
            pat = entry[1:-1]
            try:
                rx.append((re.compile(pat), f"blacklist regex {pat!r}"))
            except re.error as exc:
                print(f"[warn] bad blacklist regex {pat!r}: {exc}", file=sys.stderr)
            continue
        # Heuristic: a phrase containing an uppercase letter is a proper-noun
        # style term → case-sensitive; otherwise case-insensitive.
        if any(c.isupper() for c in entry):
            cs.append((entry, f"blacklist (case-sensitive) {entry!r}"))
        else:
            ci.append((entry.lower(), f"blacklist {entry!r}"))
    return cs, ci, rx


def parse_sacred_terms(sacred_terms: list) -> list:
    """A sacred-term entry uses the config convention:
        'exact wording | note about locked usage'
    The text BEFORE the first '|' is the locked wording; we detect near-miss
    paraphrase drift. Returns [(exact_phrase, note)]. Only entries whose note
    hints at an exact/refrain lock are drift-checked; the rest are informational
    (they carry a term name, not a phrase to preserve verbatim)."""
    locked = []
    for raw in sacred_terms:
        entry = str(raw)
        parts = entry.split("|", 1)
        phrase = parts[0].strip()
        note = parts[1].strip() if len(parts) > 1 else ""
        if not phrase:
            continue
        note_l = note.lower()
        # Only enforce verbatim-preservation for terms flagged as an exact
        # wording / refrain that must never drift.
        if any(k in note_l for k in ("exact", "refrain", "never paraphrase",
                                     "verbatim", "locked", "must not drift")):
            locked.append((phrase, note))
    return locked


def _greenlisted(needle: str, line_lower: str, greenlist_l) -> bool:
    """True if EVERY occurrence of a blacklist `needle` (already lowercased) on
    this line falls inside a sanctioned greenlist phrase that is itself on the
    line. Protects Bo-isms whose text contains a banned substring (voice.greenlist,
    documented as scrub-protection in the voice profile). Occurrence-aware: a
    banned word used standalone still fires even if a greenlist phrase that also
    contains it appears elsewhere on the same line."""
    if not needle or not greenlist_l:
        return False
    # Build the set of character positions covered by any greenlist phrase that
    # itself contains the needle and is present on the line.
    covered = []
    for g in greenlist_l:
        if not g or needle not in g:
            continue
        start = 0
        while True:
            gi = line_lower.find(g, start)
            if gi < 0:
                break
            covered.append((gi, gi + len(g)))
            start = gi + 1
    if not covered:
        return False
    # Every occurrence of the needle must sit fully inside a covered span.
    start = 0
    while True:
        ni = line_lower.find(needle, start)
        if ni < 0:
            return True  # all occurrences accounted for
        ne = ni + len(needle)
        if not any(cs <= ni and ne <= cend for cs, cend in covered):
            return False  # this occurrence is not greenlist-protected
        start = ni + 1


def scan_voice(text: str, cs, ci, rx, locked_terms, greenlist=None) -> list:
    """Return (code, line_no, detail) findings for blacklist + sacred-term drift.
    A greenlisted phrase (voice.greenlist) present on a line suppresses a
    BLACKLIST finding whose matched needle falls inside that phrase."""
    findings = []
    greenlist_l = [str(g).lower() for g in (greenlist or []) if str(g).strip()]
    lines = text.splitlines()
    for line_num, line in enumerate(lines, 1):
        line_lower = line.lower()
        for phrase, label in cs:
            if phrase in line and not _greenlisted(phrase.lower(), line_lower, greenlist_l):
                findings.append(("BLACKLIST", line_num, f"{label}: {line.strip()[:80]!r}"))
        for needle, label in ci:
            if needle in line_lower and not _greenlisted(needle, line_lower, greenlist_l):
                findings.append(("BLACKLIST", line_num, f"{label}: {line.strip()[:80]!r}"))
        for pattern, label in rx:
            m = pattern.search(line)
            if m and not _greenlisted(m.group(0).lower(), line_lower, greenlist_l):
                findings.append(("BLACKLIST", line_num, f"{label} matched {m.group(0)!r}: {line.strip()[:80]!r}"))

    # Sacred-term drift: for each locked exact wording, flag a near-miss —
    # the same words in the same order but with altered punctuation/casing that
    # is NOT the exact string. A whole-manuscript scan (drift can span a line).
    # Titles are exempt from the sacred-term paraphrase rule (a chapter titled
    # after the refrain is a sanctioned echo, not drift); count body prose only.
    body_text = "\n".join(ln for ln in text.splitlines()
                          if not ln.lstrip().startswith("#"))
    for phrase, note in locked_terms:
        exact_count = body_text.count(phrase)
        # Build a loose pattern: word tokens of the phrase separated by any
        # non-word run, case-insensitive. A loose hit that is not also an
        # exact hit is a paraphrase-drift candidate.
        tokens = re.findall(r"\w+", phrase)
        if not tokens:
            continue
        loose = r"\W+".join(re.escape(t) for t in tokens)
        loose_hits = re.findall(loose, body_text, flags=re.IGNORECASE)
        drift = len(loose_hits) - exact_count
        if drift > 0:
            findings.append(("SACRED_DRIFT", 0,
                             f"sacred term {phrase!r} appears paraphrased {drift} time(s) "
                             f"(loose={len(loose_hits)}, exact={exact_count}) — {note}"))
    return findings


# ─────────────────────────────────────────────────────────────────────────────
# Documentation / scaffolding exclusion (ported from check_acp_vocabulary)
# ─────────────────────────────────────────────────────────────────────────────

EXCLUDED_NAMES = {
    "wrong.md", "readme.md", "_readme.md", "claude.md", "architecture.md",
    "seed.md", "changelog.md", "_warm_start.md", "kit_architecture.md",
    "lessons_ledger.md", "production_lessons_learned.md",
}

META_DIR_MARKERS = {
    "contracts", "registry", "exemplars", "handoffs", "reviews", "state",
    "canon_refs", "fiction_refs", "appendices", "_tools", "_reference",
    "_titanic_source", "outputs", "archive", "backups", "intake", "_kit_research",
}


def is_documentation_file(path: Path) -> bool:
    """Files/dirs that legitimately quote forbidden vocabulary or period-
    authentic language — excluded from the voice scrub by default. Manuscript
    prose lives at manuscript/current/ and manuscript/drafts/; drafts under a
    manuscript/ dir are IN scope."""
    parts_l = [p.lower() for p in path.parts]
    # A name-based exclusion must never reach into the manuscript tree: a unit
    # file saved as manuscript/current/readme.md is PROSE and stays in scope.
    if path.name.lower() in EXCLUDED_NAMES and "manuscript" not in parts_l:
        return True
    # The workspace slug (the segment directly under book_workspace/) is never a
    # meta-dir even if its name happens to be a marker word (e.g. a book slugged
    # 'state'). Anchoring the META_DIR_MARKERS test to skip that one segment stops
    # an entire manuscript from being silently excluded and falsely reported CLEAN.
    skip_idx = parts_l.index("book_workspace") + 1 if "book_workspace" in parts_l else -1
    for i, part in enumerate(parts_l):
        if i == skip_idx:
            continue
        if part in META_DIR_MARKERS:
            # manuscript/drafts/ is in scope even though 'drafts' is generic.
            if part == "drafts" and "manuscript" in parts_l:
                continue
            return True
    return False


# ─────────────────────────────────────────────────────────────────────────────
# File collection + config
# ─────────────────────────────────────────────────────────────────────────────

def load_config(config_path: Path) -> dict:
    with config_path.open(encoding="utf-8") as fh:
        return json.load(fh)


def workspace_root(cfg: dict, config_path: Path, explicit_root) -> Path:
    """Resolve the book workspace root. Priority: --root > book_workspace/<slug>
    relative to the config's parent dir > the config's own directory."""
    if explicit_root:
        return Path(explicit_root)
    slug = cfg.get("slug")
    base = config_path.resolve().parent
    if slug:
        candidate = base / "book_workspace" / slug
        if candidate.exists():
            return candidate
        # Config may itself live inside book_workspace/<slug>/.
        if base.name == slug:
            return base
    return base


def collect_manuscript_files(root: Path, positionals: list) -> list:
    """Collect .md files to scan. Explicit positionals win; otherwise scan
    manuscript/current/ + manuscript/drafts/ under the workspace root."""
    files = []
    if positionals:
        for p in positionals:
            path = Path(p)
            if path.is_file() and path.suffix.lower() == ".md":
                files.append(path)
            elif path.is_dir():
                files.extend(sorted(path.rglob("*.md")))
        return files

    for sub in ("manuscript/current", "manuscript/drafts"):
        d = root / sub
        if d.exists():
            files.extend(sorted(d.rglob("*.md")))
    return files


def read_text(path: Path) -> str:
    for enc in ("utf-8", "utf-8-sig"):
        try:
            return path.read_text(encoding=enc)
        except UnicodeDecodeError:
            continue
    # Last resort: replace undecodable bytes so the scan still runs.
    return path.read_text(encoding="utf-8", errors="replace")


CORRUPTION_ORDER = [
    "EM_DASH",
    "EMBEDDED_UNDERSCORE", "PARAGRAPH_NOT_TERMINATED", "EMDASH_CONTINUATION",
    "MID_WORD_HYPHEN_BREAK", "UNBALANCED_EMPHASIS", "STRAY_MARKDOWN",
    "MULTIPLE_SPACES", "BLACKLIST", "SACRED_DRIFT",
]


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

    ap = argparse.ArgumentParser(
        description="Manuscript corruption + voice-drift lint (BOOKSMITH). "
                    "Exit 0 clean / 1 drift (blocking) / 2 usage.")
    ap.add_argument("--config", help="Path to book_config.json (drives blacklist/"
                                     "greenlist/sacred_terms + workspace slug).")
    ap.add_argument("--root", help="Override the workspace root "
                                   "(default: book_workspace/<slug>/).")
    ap.add_argument("--include-docs", action="store_true",
                    help="Do NOT exclude scaffolding/cached-source dirs from the "
                         "voice scrub (debugging only; they legitimately quote "
                         "banned/period vocabulary).")
    ap.add_argument("--verbose", "-v", action="store_true",
                    help="Show extra context.")
    ap.add_argument("paths", nargs="*",
                    help="Explicit .md files/dirs to scan (overrides the "
                         "manuscript-dir default).")
    args = ap.parse_args()

    cfg = {}
    config_path = None
    if args.config:
        config_path = Path(args.config)
        if not config_path.exists():
            print(f"[ERROR] config not found: {config_path}", file=sys.stderr)
            return 2
        try:
            cfg = load_config(config_path)
        except (json.JSONDecodeError, OSError) as exc:
            print(f"[ERROR] could not parse config {config_path}: {exc}", file=sys.stderr)
            return 2

    voice = cfg.get("voice", {}) if isinstance(cfg, dict) else {}
    blacklist = voice.get("blacklist", []) or []
    greenlist = voice.get("greenlist", []) or []
    sacred_terms = voice.get("sacred_terms", []) or []
    # Em-dash HARD gate defaults ON (Bo's #1 AI-tell). A non-Bo book that
    # legitimately uses em-dashes sets voice.no_em_dashes=false.
    no_em_dashes = bool(voice.get("no_em_dashes", True)) if isinstance(voice, dict) else True
    cs, ci, rx = compile_blacklist(blacklist)
    locked_terms = parse_sacred_terms(sacred_terms)

    # Resolve scan targets.
    if config_path is not None:
        root = workspace_root(cfg, config_path, args.root)
    else:
        root = Path(args.root) if args.root else Path.cwd()
    files = collect_manuscript_files(root, args.paths)

    if not args.paths and not args.include_docs:
        files = [f for f in files if not is_documentation_file(f)]

    # Marketing/ceremonial copy renders into the book + Amazon listing but lives
    # in the CONFIG, not manuscript/ — it bypassed the manuscript scan (a live
    # leak: an epigraph attribution shipped an em-dash). Scan it too (§19.3).
    config_findings = []
    if no_em_dashes and isinstance(cfg, dict):
        epi = cfg.get("epigraph") or {}
        km = cfg.get("kdp_metadata") or {}
        ceremonial = {
            "title": cfg.get("title"),
            "author": cfg.get("author"),
            "epigraph.text": epi.get("text"),
            "epigraph.attribution": epi.get("attribution"),
            "about_the_author": cfg.get("about_the_author"),
            "dedication": cfg.get("dedication"),
            "readers_note": cfg.get("readers_note"),
            "subtitle": cfg.get("subtitle"),
            "kdp_metadata.description": km.get("description"),
        }
        for fld, val in ceremonial.items():
            if isinstance(val, str):
                for ch, name in EM_DASHES.items():
                    if ch in val:
                        config_findings.append(
                            (fld, f"{val.count(ch)}x {name} in config.{fld} "
                                  f"(renders into the book/listing): {val[:80]!r}"))

    if not files:
        print(f"[info] No manuscript .md files found to lint under {root}.")
        print("[info] (Scaffolding/cached-source dirs are excluded unless --include-docs.)")
        if config_findings:
            print(f"\n  [EM_DASH] config ceremonial/marketing copy — {len(config_findings)} finding(s):")
            for fld, detail in config_findings:
                print(f"    {detail}")
            return 1
        # An EMPTY manuscript scan is NOT a silent pass: a misresolved or empty
        # root would otherwise report the em-dash + voice gate green (exit 0) when
        # it never ran. Return 2 (usage/environment error) so verify_build's
        # returncode==0 pass-check cannot be fooled by a manuscript that was never
        # collected. A real book with files still exits 0 below.
        print(f"[WARNING] No files collected — the em-dash + voice gate did NOT run "
              f"under the resolved root {root}. This is an environment/config error, "
              f"not a clean manuscript. Check --root / config slug.", file=sys.stderr)
        return 2

    print(f"[lint] {len(files)} file(s) under {root}")
    print(f"[lint] corruption checks: 7 | em-dash gate: "
          f"{'ON (hard)' if no_em_dashes else 'OFF'} | blacklist tiers: "
          f"{len(cs)} cs + {len(ci)} ci + {len(rx)} regex | "
          f"locked sacred terms: {len(locked_terms)}")

    # voice.lint_waivers (2026-07-23, replica books): exact strings adjudicated
    # as SOURCE-FAITHFUL blemishes (the printed page was rendered and eyeballed;
    # the artifact is the source's own, e.g. a typo printed in the original
    # book). A finding whose detail carries a waived string is suppressed, with
    # a WAIVED notice so the suppression is always visible in the output.
    lint_waivers = [w for w in (voice.get("lint_waivers", []) or [])
                    if isinstance(w, str) and w.strip()] if isinstance(voice, dict) else []

    # H0 (cloud/PLAN_H0_2026-08-24.md §2 D2): a unit whose LATEST author is the
    # HUMAN (per registry/human_edited_units.json, maintained by
    # _tools/authorship_ledger.py) carries the customer's own voice. Its
    # findings print as HUMAN-EDIT ADVISORY and never gate the build — a dash a
    # human typed is their voice, not an AI tell (the same doctrine as the ZH
    # 破折号 rule). The moment an AI re-draft replaces the prose, the ledger's
    # latest actor flips to "ai" and the unit re-enters this hard gate.
    _human_cache: dict = {}

    def _human_units_for(fp) -> set:
        p = Path(fp).resolve()
        ws = None
        for anc in p.parents:
            if anc.name == "manuscript":
                ws = anc.parent
                break
        if ws is None:
            return set()
        key = str(ws)
        if key not in _human_cache:
            hu = ws / "registry" / "human_edited_units.json"
            try:
                _human_cache[key] = set(json.loads(hu.read_text("utf-8")))
            except (OSError, json.JSONDecodeError, TypeError):
                _human_cache[key] = set()
        return _human_cache[key]

    def _unit_of(fp) -> str:
        stem = Path(fp).stem
        if stem.endswith("_current"):
            return stem[: -len("_current")]
        m = re.match(r"^(.*?)_v\d+(?:_[a-z_]+)?$", stem)
        return m.group(1) if m else stem

    exit_code = 0
    total = 0
    for f in files:
        text = read_text(f)
        findings = lint_corruption(text)
        if no_em_dashes and (not is_documentation_file(f) or args.include_docs or args.paths):
            findings += lint_em_dashes(text)
        waived = []
        if lint_waivers:
            def _is_waived(x):
                detail = x[2]
                if any(w in detail for w in lint_waivers):
                    return True
                # finding details truncate the offending text (e.g. a 30-char
                # paragraph tail): also waive when a quoted fragment from the
                # detail sits INSIDE a waiver string
                frags = re.findall(r"'([^']{8,})'", detail)
                return any(fr in w for fr in frags for w in lint_waivers)
            waived = [x for x in findings if _is_waived(x)]
            findings = [x for x in findings if x not in waived]
        if not args.include_docs or args.paths:
            # Voice scrub runs on manuscript files (already filtered above),
            # or on any explicit target the caller named.
            if not is_documentation_file(f) or args.include_docs or args.paths:
                findings += scan_voice(text, cs, ci, rx, locked_terms, greenlist)

        print(f"\n=== {f} ===")
        for code, line, detail in waived:
            print(f"  WAIVED [{code}] line {line}: source-faithful blemish "
                  f"(voice.lint_waivers): {detail[:90]}")
        if not findings:
            print("  CLEAN — no corruption or voice-drift artifacts.")
            continue

        if _unit_of(f) in _human_units_for(f):
            print(f"  HUMAN-EDIT ADVISORY — {len(findings)} finding(s) in a unit "
                  f"whose latest author is the customer; their own words are "
                  f"not gated (authorship ledger, PLAN_H0 D2):")
            for code, line, detail in findings[:20]:
                loc = f"line {line}" if line else "(whole-file)"
                print(f"    [{code}] {loc}: {detail[:90]}")
            if len(findings) > 20:
                print(f"    ... {len(findings) - 20} more")
            continue

        exit_code = 1
        by_code = {}
        for code, line, detail in findings:
            by_code.setdefault(code, []).append((line, detail))
        for code in CORRUPTION_ORDER:
            if code not in by_code:
                continue
            hits = by_code[code]
            print(f"\n  [{code}] — {len(hits)} finding(s):")
            for line, detail in hits[:50]:
                loc = f"line {line}" if line else "(whole-file)"
                print(f"    {loc}: {detail}")
            if len(hits) > 50:
                print(f"    ... {len(hits) - 50} more")
        print(f"\n  TOTAL FINDINGS: {len(findings)}")
        total += len(findings)

    if config_findings:
        exit_code = 1
        total += len(config_findings)
        print(f"\n=== config: ceremonial/marketing copy (renders into the book + listing) ===")
        print(f"\n  [EM_DASH] — {len(config_findings)} finding(s):")
        for fld, detail in config_findings:
            print(f"    {detail}")

    print(f"\n{'=' * 72}")
    if exit_code == 0:
        print(f"[CLEAN] {len(files)} file(s) scanned; zero findings.")
    else:
        print(f"[DRIFT] {len(files)} file(s) scanned; {total} finding(s). "
              f"Build should HALT; revise before generation/export.")
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
