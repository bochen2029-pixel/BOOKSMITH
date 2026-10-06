#!/usr/bin/env python3
"""update_ledgers.py: rewrite the STATUS line and insert a P10 re-sync block at the top of the three continuity
ledgers (zht, zhs, EN). The continuity gate scans the ledger for every unit id on disk, so the block names all 19.
Pass --complete to flip the two Chinese ledgers to COMPLETE (after the v2 builds)."""
import sys

COMPLETE = "--complete" in sys.argv
UNITS = ("note_names, part_1, ch_01, ch_02, part_2, ch_03, ch_04, part_3, ch_05, ch_06, ch_07, part_4, ch_08, part_5, "
         "ch_09, ch_10, acknowledgments, glossary, image_credits")

ZT = "C:/BOOKSMITH/book_workspace/across_borders_zht/_CONTINUITY.md"
ZS = "C:/BOOKSMITH/book_workspace/across_borders_zhs/_CONTINUITY.md"
EN = "C:/BOOKSMITH/book_workspace/across_borders/_CONTINUITY.md"

ZT_OLD_STATUS = ("STATUS: COMPLETE (zh-Hant v1 released 2026-09-29 18:04, V7 RELEASE OK; the zh-Hans edition is the next, "
                 "separate job)")
ZS_OLD_STATUS = ("STATUS: COMPLETE (zh-Hans v1 released 2026-09-30 09:07, VZF RELEASE OK twice; both-editions zip 09:14; "
                 "the operator copies to C:/BOOKSMITH/book_workspace/)")
ZT_IP = "STATUS: IN_PROGRESS (v2 re-sync to the author's revised English, 2026-10-06; v1 of 2026-09-29 stays in outputs/_FINAL_backup_2026-10-06/)"
ZS_IP = "STATUS: IN_PROGRESS (v2 re-sync to the author's revised English, 2026-10-06; v1 of 2026-09-30 stays in outputs/_FINAL_backup_2026-10-06/)"
ZT_DONE = "STATUS: COMPLETE (zh-Hant v2 released 2026-10-06, re-synced to the author's revised English; v1 of 2026-09-29 kept beside it)"
ZS_DONE = "STATUS: COMPLETE (zh-Hans v2 released 2026-10-06, re-synced to the author's revised English; v1 of 2026-09-30 kept beside it)"

BLOCK_ZT = """
## P10 RE-SYNC 2026-10-06 (read this block first; it supersedes the resume protocol's step 0 for the v2 work)
- Source of record: the author's revised English docx (intake/Across_Borders_and_Herbaria-HC.docx, sha256 1f426382…,
  his email of 2026-10-05), back-ported into across_borders/manuscript/current + book_config.json and refrozen as
  1,164 segments (sha256 34e74302…); the Sept-28 freeze is kept in _key/_pre_resync_2026-09-28/.
- Units, 19, all in translation/current and manuscript/current: {units}.
  acknowledgments is NEW (致謝, between ch_10 and glossary); the lone ✦ under its heading in the docx was the kit's
  own ornament and is not text.
- Changed text: note_names.003; ch_01.027 and ch_01.031; ch_06.041/.042 (label lines exactly as the author now
  prints them; ch_06.043/.044 still discuss the removed 1854 fragment: source defect D09); the Acknowledgments
  (paragraphs 7-16 reuse book one's ratified Chinese, split where this book's English splits, family names in Latin
  letters as book one prints them, P007 narrowed to the narration by R41); config_strings about_the_author (4
  paragraphs). The ch_10 figure desk_2026-09-22_portal.jpg is the author's 2026-10-02 laptop photo, browser chrome and
  taskbar cropped (880x493; prints small under the 300 ppi floor).
- Key and gates: amendments R41 (P007; P021-P025, INST042, INST044), charter §11 D08-D10, §15 R41; build_key 0
  errors; test_gate 43/43; gate_unit acknowledgments 0 FAIL; gate_book 19/19 0 FAIL; final_checks CLEAN; kit lint
  CLEAN with two source-faithful waivers (the URL lines) in book_config voice.lint_waivers.
- Pipeline edits: UNITS in _tools_zht/zht_common.py; EXPECT 19 in _scripts_zht/final_checks_zht.py and sweeps_zht.py;
  the privacy check skips the acknowledgments unit (R41); layout re-solved on the final text.
- Build: `PYTHONUTF8=1 python _scripts_zht/build_final_zht.py --version v2`. The build DELETES outputs/_FINAL: the v1
  package is backed up at outputs/_FINAL_backup_2026-10-06/ and is copied back beside v2 after the build (same_content.py
  and make_both_editions.py read it).
- Evidence and the four swarm reports: across_borders/_translation/_p10_2026-10-06/.
- NEXT: {next}
"""

BLOCK_ZS = """
## P10 RE-SYNC 2026-10-06 (read this block first; it supersedes the resume protocol's step 0 for the v2 work)
- Source of record: the author's revised English docx (intake/Across_Borders_and_Herbaria-HC.docx, sha256 1f426382…),
  refrozen as 1,164 segments (sha256 34e74302…); the Sept-28 freeze is kept in _key/_pre_resync_2026-09-28/.
- Units, 19, all in translation/current and manuscript/current: {units}.
  acknowledgments is NEW (致谢, between ch_10 and glossary).
- Changed text: note_names.003, ch_01.027, ch_01.031 derived BY HAND from the zh-Hant text (the converter was not run
  on shipped units: it would overwrite the mainland reviewers' edits); ch_06.041/.042 label lines as the author now
  prints them; the Acknowledgments converted from the zh-Hant text with convert_zhs.py and locale-reviewed (队列,
  档案记录, 档案库, 致以, 试验, 我太太; paragraphs 7-16 are book one's ratified zhs text); about_the_author (4
  paragraphs). The ch_10 figure replaced (see the zht ledger). _zht_ref/translation_current refreshed for
  acknowledgments, note_names, ch_01, ch_06.
- Key and gates: amendments ZR54 (P007 narrowed, folded into the base P007 row), ZR55 (ML59 no longer fires on
  档案记录), ZR56 (ML157 tripwire 伫列 -> 队列), P021-P025, INST042, INST044; charter §11 D08-D10; build_key 0 errors;
  test_gate 57/57; gate_unit acknowledgments 0 FAIL; gate_book 19/19 0 FAIL; final_checks CLEAN; kit lint CLEAN
  (two URL-line waivers).
- Pipeline edits: UNITS in _tools_zhs/zhs_common.py; EXPECT 19 in final_checks_zhs.py and sweeps_zhs.py; the privacy
  check skips the acknowledgments unit (ZR54); layout_map_zhs.json re-solved (its ch_01 anchor had changed).
- Build: `PYTHONUTF8=1 python _scripts_zhs/layout_zhs.py solve --fresh` then
  `PYTHONUTF8=1 python _scripts_zhs/build_final_zhs.py --version v2`; v1 backed up at outputs/_FINAL_backup_2026-10-06/.
  Both-editions zip: _tools_zhs/make_both_editions.py (its ZHT_PKG/ZHT_SHA pins must point at the zht v2 package).
- NEXT: {next}
"""

BLOCK_EN = """
## P10 RE-SYNC 2026-10-06 (the manuscript is now AHEAD of the delivered 2026-09-24 package)
- The author's revised English (intake/Across_Borders_and_Herbaria-HC.docx, his email of 2026-10-05) was back-ported
  into manuscript/current + book_config.json (versions snapshotted): note_names.003; ch_01.027, ch_01.031;
  ch_06.041/.042 label lines; NEW unit acknowledgments (between ch_10 and glossary); about_the_author (4 paragraphs);
  the ch_10 figure desk_2026-09-22_portal.jpg rebuilt from his 2026-10-02 laptop photo (make_figures.py row).
- Units, 19: {units}.
- Gates: scan PASS (19 units), lint CLEAN (two URL-line waivers), config schema-valid. The English package was NOT
  rebuilt (build_final.py deletes outputs/_FINAL including the delivered zip; back it up first; the KDP kit's
  page-dependent numbers must be re-derived). The Chinese editions were re-synced to this text (their ledgers).
- Running log entry 2026-10-06 ~09:40; evidence and swarm reports in _translation/_p10_2026-10-06/.
"""


def rd(p):
    return open(p, encoding="utf-8").read()


def wr(p, s):
    with open(p, "w", encoding="utf-8", newline="\n") as f:
        f.write(s)


def apply(path, old_status, new_status, block, marker):
    s = rd(path)
    if marker in s:
        # already inserted: only the STATUS line may change
        for cand in (ZT_IP, ZS_IP, ZT_DONE, ZS_DONE, old_status):
            if cand in s and cand != new_status:
                s = s.replace(cand, new_status, 1)
                wr(path, s)
                print("OK  status ->", path.split("/")[-2])
                return
        print("--  unchanged:", path.split("/")[-2])
        return
    if old_status:
        if s.count(old_status) != 1:
            sys.exit("ABORT %s: STATUS line not found once" % path)
        s = s.replace(old_status, new_status + "\n" + block.rstrip("\n") + "\n", 1)
    else:
        # EN: insert after the first line that starts with "**STATUS"
        lines = s.split("\n")
        for i, ln in enumerate(lines):
            if ln.startswith("**STATUS"):
                lines.insert(i + 1, block.rstrip("\n") + "\n")
                break
        else:
            sys.exit("ABORT EN: STATUS line not found")
        s = "\n".join(lines)
    wr(path, s)
    print("OK  block inserted:", path.split("/")[-2])


nxt_zt = ("v2 build -> visual check of the touched pages -> copy the v1 package back beside v2 -> zhs -> both-editions zip -> COMPLETE."
          if not COMPLETE else "nothing; v2 delivered. A later author revision goes through the same P10 path.")
nxt_zs = ("zht v2 first (one Word job at a time), then layout solve + v2 build here, then the both-editions zip."
          if not COMPLETE else "nothing; v2 delivered with the both-editions zip.")
apply(ZT, ZT_OLD_STATUS, ZT_DONE if COMPLETE else ZT_IP, BLOCK_ZT.format(units=UNITS, next=nxt_zt), "## P10 RE-SYNC 2026-10-06")
apply(ZS, ZS_OLD_STATUS, ZS_DONE if COMPLETE else ZS_IP, BLOCK_ZS.format(units=UNITS, next=nxt_zs), "## P10 RE-SYNC 2026-10-06")
apply(EN, None, None, BLOCK_EN.format(units=UNITS), "## P10 RE-SYNC 2026-10-06")
print("DONE")
