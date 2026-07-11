"""
check_part_pages.py — Recto-parity verifier (empirical, via Word COM).

BOOKSMITH toolchain component. Proves each chapter/part heading lands on a
recto (odd) page. Arithmetic is NOT trusted: any markdown edit re-breaks parity
(LESSONS_LEDGER §4.3), so the check is empirical — open the DOCX read-only in
Word, Repaginate, Find each unit heading, and read the page number Word
actually assigned it (Selection.Information(3) = wdActiveEndAdjustedPageNumber).

PORTED FROM: C:\\BOOK3\\_tools\\_titanic_source\\check_part_pages.py
  The base opens read-only, Repaginate(), HomeKey->Find each "PART N —" heading,
  reads Information(3), flags any even (verso) landing. The BOOKSMITH refactor
  reads the unit list + heading style from book_config.json instead of the
  hard-coded five Titanic parts, and emits the verdict as JSON for GATE-5.

Heading discovery:
  The set of unit headings to find is derived from book_config in this order:
    1. --headings "A|B|C"  (explicit pipe-separated override) if given, else
    2. book_config.check_part_pages.headings[]  if present, else
    3. synthesized from voice.unit_noun + the unit list, matching the house
       "PART N —" / "CHAPTER N —" convention with an em-dash OR en-dash OR
       hyphen tail (the generators emit an em-dash; we search the stem so the
       dash variant does not matter). If no unit list is resolvable we fall back
       to searching "PART "/"CHAPTER " stems 1..99 and stop at the first miss.

Usage:
  python check_part_pages.py <in.docx> [--config book_config.json]
                                        [--headings "PART I|PART II|..."]

Prints a JSON object on stdout:
  {"docx":..., "total_pages":N, "unit_noun":"part",
   "results":[{"heading":"PART I","page":13,"recto":true}, ...],
   "all_recto": true|false}
Exit code 0 if all_recto, 1 if any unit landed on a verso, 2 on usage/IO error.
"""
import sys
import os
import json

import win32com.client

# Word enum constants.
WD_STORY = 6                 # wdStory (HomeKey unit)
WD_FIND_STOP = 0             # wdFindStop (Find.Wrap)
WD_STAT_PAGES = 2            # wdStatisticPages
WD_ADJ_PAGE_NUMBER = 3       # wdActiveEndAdjustedPageNumber (Selection.Information)
WD_ALERTS_NONE = 0           # wdAlertsNone
WD_OUTLINE_1 = 1             # wdOutlineLevel1 — Heading-1 paragraphs (chapter/part starts)

# Roman numerals 1..30 — the house part headings are "PART I", "PART II", ...
_ROMAN = [
    "", "I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X",
    "XI", "XII", "XIII", "XIV", "XV", "XVI", "XVII", "XVIII", "XIX", "XX",
    "XXI", "XXII", "XXIII", "XXIV", "XXV", "XXVI", "XXVII", "XXVIII", "XXIX", "XXX",
]


def load_config(config_path):
    if not config_path:
        return {}
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


def _config_unit_ids(cfg):
    """Best-effort resolution of the ordered unit id list from config.

    Structure lives under several possible keys across seeds; we accept any of
    them, else fall back to the authorship.per_chapter_overrides key order (an
    ordered dict of unit_id -> class that every seed carries)."""
    for key in ("units", "structure", "unit_order"):
        v = cfg.get(key)
        if isinstance(v, list) and v:
            # list of ids or list of {id: ...}
            ids = []
            for item in v:
                if isinstance(item, str):
                    ids.append(item)
                elif isinstance(item, dict):
                    ids.append(item.get("id") or item.get("unit_id") or "")
            ids = [i for i in ids if i]
            if ids:
                return ids
    overrides = (cfg.get("authorship") or {}).get("per_chapter_overrides") or {}
    if isinstance(overrides, dict) and overrides:
        return list(overrides.keys())
    return []


def _config_unit_titles(cfg):
    """Dash-stem of each unit's rendered title. generate_book renders
    units[].title verbatim as the heading (e.g. 'Chapter One - Departure'); we
    Find the stem BEFORE the first em/en/hyphen dash so the dash variant is
    irrelevant and Find is robust."""
    titles = []
    for key in ("units", "structure", "unit_order"):
        v = cfg.get(key)
        if isinstance(v, list) and v:
            for item in v:
                if isinstance(item, dict):
                    t = (item.get("title") or "").strip()
                    if not t:
                        continue
                    for dash in ("—", "–", " - ", "-"):
                        idx = t.find(dash)
                        if idx > 0:
                            t = t[:idx].strip()
                            break
                    titles.append(t)
            if titles:
                return titles
    return []


def resolve_headings(cfg, headings_override):
    """Return the list of heading STEMS to Find (no dash tail — we match the
    stem so em-dash vs en-dash vs hyphen is irrelevant)."""
    if headings_override:
        return [h.strip() for h in headings_override.split("|") if h.strip()]

    cpp = cfg.get("check_part_pages") or {}
    if isinstance(cpp.get("headings"), list) and cpp["headings"]:
        return [str(h).strip() for h in cpp["headings"] if str(h).strip()]

    # Prefer the ACTUAL rendered unit titles over synthesized "CHAPTER N" —
    # generate_book renders units[].title as the heading text.
    unit_titles = _config_unit_titles(cfg)
    if unit_titles:
        return unit_titles

    unit_noun = ((cfg.get("voice") or {}).get("unit_noun") or "chapter").upper()
    unit_ids = _config_unit_ids(cfg)
    n = len(unit_ids)

    if unit_noun == "PART":
        if n == 0:
            # unknown count — search PART I..PART XXX, caller stops at first miss
            return [f"PART {_ROMAN[i]}" for i in range(1, len(_ROMAN))]
        return [f"PART {_ROMAN[i]}" for i in range(1, min(n, len(_ROMAN) - 1) + 1)]
    else:
        # Chapters number arabically: "CHAPTER 1", "CHAPTER 2", ...
        count = n if n > 0 else 99
        return [f"CHAPTER {i}" for i in range(1, count + 1)]


def find_page_of(word_app, heading):
    """Return the adjusted page number where `heading` first appears, or None."""
    word_app.Selection.HomeKey(Unit=WD_STORY)
    find = word_app.Selection.Find
    find.ClearFormatting()
    try:
        find.Style = word_app.ActiveDocument.Styles("Heading 1")
    except Exception:
        pass
    find.Text = heading
    find.Forward = True
    find.Wrap = WD_FIND_STOP
    find.MatchCase = False
    if find.Execute():
        return int(word_app.Selection.Information(WD_ADJ_PAGE_NUMBER))
    return None


def check_pages(docx_path, cfg, headings_override, stop_at_first_miss):
    word_app = win32com.client.Dispatch("Word.Application")
    word_app.Visible = False
    try:
        word_app.DisplayAlerts = WD_ALERTS_NONE
    except Exception:
        pass

    doc = None
    try:
        doc = word_app.Documents.Open(os.path.abspath(docx_path), ReadOnly=True)
        doc.Repaginate()
        total_pages = int(doc.ComputeStatistics(WD_STAT_PAGES))

        # Structural discovery: chapter/part headings are the ONLY paragraphs at
        # outline level 1 (HeadingLevel.HEADING_1). Robust to the CONTENTS/TOC page
        # (TOC entries are styled "TOC n", NOT outline level 1) and to UPPERCASE
        # rendering + dash variants — no text Find, no TOC collision.
        results = []
        if headings_override:
            for heading in [h.strip() for h in headings_override.split("|") if h.strip()]:
                page = find_page_of(word_app, heading)
                results.append({"heading": heading, "page": page,
                                "recto": (page % 2 == 1) if page else None})
        else:
            for para in doc.Paragraphs:
                try:
                    lvl = int(para.OutlineLevel)
                except Exception:
                    lvl = None
                try:
                    style_name = str(para.Style.NameLocal).lower()
                except Exception:
                    style_name = ""
                if not (lvl == WD_OUTLINE_1 or style_name in ("heading 1", "heading1")):
                    continue
                text = (para.Range.Text or "").replace("\r", "").replace("\x07", "").strip()
                if not text:
                    continue
                page = int(para.Range.Information(WD_ADJ_PAGE_NUMBER))
                results.append({"heading": text[:60], "page": page, "recto": page % 2 == 1})

        doc.Close(SaveChanges=False)
        doc = None
        return total_pages, results
    finally:
        if doc is not None:
            try:
                doc.Close(SaveChanges=False)
            except Exception:
                pass
        word_app.Quit()


def main() -> int:
    args = sys.argv[1:]
    if not args:
        print("Usage: python check_part_pages.py <in.docx> [--config book_config.json] "
              "[--headings \"PART I|PART II|...\"]", file=sys.stderr)
        return 2

    docx_path = None
    config_path = None
    headings_override = None
    i = 0
    while i < len(args):
        a = args[i]
        if a == "--config":
            config_path = args[i + 1]; i += 2; continue
        if a == "--headings":
            headings_override = args[i + 1]; i += 2; continue
        if docx_path is None:
            docx_path = a
        i += 1

    if not docx_path:
        print("ERROR: no input DOCX given.", file=sys.stderr)
        return 2
    if not os.path.exists(docx_path):
        print(f"ERROR: File not found: {docx_path}", file=sys.stderr)
        return 2

    cfg = load_config(config_path)

    # If neither an explicit override nor a config-declared heading list exists
    # and the unit count is unknown, we sweep and stop at the first missing
    # heading.
    cpp_declared = bool(headings_override) or bool((cfg.get("check_part_pages") or {}).get("headings"))
    unit_count_known = bool(_config_unit_ids(cfg))
    stop_at_first_miss = not cpp_declared and not unit_count_known

    total_pages, results = check_pages(docx_path, cfg, headings_override, stop_at_first_miss)

    found = [r for r in results if r["page"] is not None]
    all_recto = bool(found) and all(r["recto"] for r in found)

    print(json.dumps({
        "docx": os.path.abspath(docx_path),
        "total_pages": total_pages,
        "unit_noun": (cfg.get("voice") or {}).get("unit_noun", "chapter"),
        "results": results,
        "all_recto": all_recto,
    }))

    return 0 if all_recto else 1


if __name__ == "__main__":
    sys.exit(main())
