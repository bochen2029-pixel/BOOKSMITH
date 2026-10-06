#!/usr/bin/env python3
"""fix_ml59_and_rulings.py: (1) narrow the zhs locale tripwire ML59 (檔案->文件, the computer-file sense) so the
archive sense 档案记录 is not flagged; (2) log the two rulings in both charters' amendment logs and as amendment
rows: P007 (the author's own Acknowledgments name his wife; the privacy rule applies to the narrative units) and
the ML59 narrowing; (3) the zhs .015 wording uses 档案库 for "archive" (excluded by the tripwire's own lookahead).
Every text edit asserts exactly one hit.
"""
import os
import shutil
import sys

ZT = "C:/BOOKSMITH/book_workspace/across_borders_zht"
ZS = "C:/BOOKSMITH/book_workspace/across_borders_zhs"


def rd(p):
    return open(p, encoding="utf-8").read()


def wr(p, s):
    with open(p, "w", encoding="utf-8", newline="\n") as f:
        f.write(s)


def replace_once(p, old, new, label):
    s = rd(p)
    if s.count(old) != 1:
        sys.exit("ABORT %s: expected 1 hit, found %d" % (label, s.count(old)))
    wr(p, s.replace(old, new))
    print("OK ", label)


def append(p, line, label):
    s = rd(p)
    if line in s:
        print("-- ", label, "already present")
        return
    if not s.endswith("\n"):
        s += "\n"
    wr(p, s + line + "\n")
    print("OK ", label)


# 1. ML59 narrowing (zhs locale layer)
replace_once(ZS + "/_key/locale_layer_zhs.txt",
             "/档案(?!库|室|馆|盒|员|鉴|考|侦)/", "/档案(?!库|室|馆|盒|员|鉴|考|侦|记录)/",
             "ML59 lookahead + 记录 (archival records)")

# 2. amendment rows (note-only: the cells stay "=")
append(ZT + "/_key/registry_amendments_zht.tsv",
       "P007\t=\t=\t=\t=\t=\t=\tR41 (2026-10-06, P10 re-sync): the author's own Acknowledgments (acknowledgments.006, .011) "
       "name his wife Weiming, in Latin letters as book one's Chinese editions print her (their P21); the privacy rule "
       "of this row governs the narrative units only. note_names.015 (her stated wish) is translated as written and "
       "reported to the author as a source inconsistency.",
       "zht amendment P007/R41")
append(ZS + "/_key/registry_amendments_zhs.tsv",
       "P007\t=\t=\t=\t=\t=\t=\tZR54 (2026-10-06, P10 re-sync): the author's own Acknowledgments (acknowledgments.006, .011) "
       "name his wife Weiming in Latin letters (book one's zhs P21); 我太太 stays the form at the ZR19 (f) sites and at "
       "acknowledgments.006; the privacy rule governs the narrative units only.",
       "zhs amendment P007/ZR54")
append(ZS + "/_key/registry_amendments_zhs.tsv",
       "ML59\t=\t=\t=\t=\t=\t=\tZR55 (2026-10-06): the computer-file tripwire 档案->文件 no longer fires on 档案记录 "
       "(archival records, acknowledgments.014); the archive sense keeps 档案 (现汉: 档案 = archives); "
       "acknowledgments.015 renders 'a vast, complex archive' as 档案库.",
       "zhs amendment ML59/ZR55")

# 3. charter amendment logs (append-only tables at the end of each charter)
append(ZT + "/translation_charter_zht.md",
       "| R41 | 2026-10-06 | P10 re-sync to the author's revised English (HC docx, sha256 1f426382…): Acknowledgments unit "
       "added between the Epilogue and the Glossary (致謝; family names in Latin letters as book one's Chinese editions, "
       "P21-P25 there); About the Author rewritten (4 paragraphs); note_names.003, ch_01.027, ch_01.031 re-translated; "
       "the ch_06.041/.042 label quote follows the author's new wording (the explanatory .043/.044 still discuss the "
       "removed 1854 fragment: source inconsistency, reported); the Epilogue photo replaced by the author's new laptop "
       "photo (browser chrome and taskbar cropped as the book's privacy convention). P007 narrowed to the narrative "
       "units. Key segments refrozen (1,165 segments). |",
       "zht charter R41")
append(ZS + "/translation_charter_zhs.md",
       "| ZR54 | 2026-10-06 | P10 re-sync to the author's revised English (HC docx, sha256 1f426382…): 致谢 unit added "
       "between the Epilogue and the Glossary, derived from the zh-Hant text by the converter and locale-reviewed "
       "(队列, 档案, 儿媳, 创始人, 致以, 试验); About rewritten; note_names.003, ch_01.027, ch_01.031 re-derived; "
       "ch_06.041/.042 labels follow the author's new wording; Epilogue photo replaced; P007 narrowed to the narrative "
       "units (我太太 kept at acknowledgments.006). Key segments refrozen (1,165 segments). |",
       "zhs charter ZR54")
append(ZS + "/translation_charter_zhs.md",
       "| ZR55 | 2026-10-06 | ML59 (檔案→文件, computer-file sense) no longer fires on 档案记录; the archive sense keeps "
       "档案; acknowledgments.015 renders 'a vast, complex archive' as 档案库. |",
       "zhs charter ZR55")

# 4. zhs .015 wording -> v4 draft + current
cur = ZS + "/translation/current/acknowledgments.md"
s = rd(cur)
old = "把一座庞大而复杂的档案，化为一部结构分明、易于掌握的书稿"
new = "把一座庞大而复杂的档案库，化为一部结构分明、易于掌握的书稿"
if s.count(old) != 1:
    sys.exit("ABORT .015 wording: %d hits" % s.count(old))
s = s.replace(old, new)
n = 1
while os.path.exists(ZS + "/translation/drafts/acknowledgments_v%d.md" % n):
    n += 1
wr(ZS + "/translation/drafts/acknowledgments_v%d.md" % n, s)
shutil.copyfile(ZS + "/translation/drafts/acknowledgments_v%d.md" % n, cur)
print("OK  zhs acknowledgments v%d -> current (档案库 at .015)" % n)
print("DONE")
