#!/usr/bin/env python3
"""apply_terms_fixes.py: apply the GT-TERMS findings.
(i) zht Acknowledgments v2: Latin once for Carlquist, 我太太, 歷史臺紙, 平台 (R18), 癌症存活者.
(ii) zhs Acknowledgments v5: Latin once for Carlquist, 历史台纸.
(iii) final_checks_*: the wife's-name privacy check skips the Acknowledgments unit (R41 / ZR54).
(iv) charters section 11: source defects D08-D10.
(v) registry amendment rows for the new names and companies; zhs locale tripwire for 伫列.
(vi) segment numbers in the earlier notes: .011 -> .010.
Every replacement asserts its expected count.
"""
import os
import re
import shutil
import sys

ZT = "C:/BOOKSMITH/book_workspace/across_borders_zht"
ZS = "C:/BOOKSMITH/book_workspace/across_borders_zhs"


def rd(p):
    return open(p, encoding="utf-8").read()


def wr(p, s):
    with open(p, "w", encoding="utf-8", newline="\n") as f:
        f.write(s)


def rep(s, old, new, n, label):
    c = s.count(old)
    if c != n:
        sys.exit("ABORT %s: expected %d hits, found %d for %r" % (label, n, c, old[:50]))
    return s.replace(old, new)


def next_draft(ws, unit):
    n = 1
    while os.path.exists("%s/translation/drafts/%s_v%d.md" % (ws, unit, n)):
        n += 1
    return "%s/translation/drafts/%s_v%d.md" % (ws, unit, n)


# (i) zht
p = ZT + "/translation/current/acknowledgments.md"
s = rd(p)
s = rep(s, "舍溫·卡爾奎斯特博士（Dr. Sherwin Carlquist）", "舍溫·卡爾奎斯特博士（Sherwin Carlquist）", 1, "zht Dr once")
s = rep(s, "帶我和我妻子 Weiming 參觀", "帶我和我太太 Weiming 參觀", 1, "zht 我太太")
s = rep(s, "要讓這些歷史標本重見天日", "要讓這些歷史臺紙重見天日", 1, "zht 歷史臺紙")
s = rep(s, "平臺", "平台", 2, "zht 平台 R18")
s = rep(s, "癌症倖存者", "癌症存活者", 1, "zht 癌症存活者")
d = next_draft(ZT, "acknowledgments")
wr(d, s)
shutil.copyfile(d, p)
print("OK  zht acknowledgments ->", os.path.basename(d), "+ current")

# (ii) zhs
p = ZS + "/translation/current/acknowledgments.md"
s = rd(p)
s = rep(s, "舍温·卡尔奎斯特博士（Dr. Sherwin Carlquist）", "舍温·卡尔奎斯特博士（Sherwin Carlquist）", 1, "zhs Dr once")
s = rep(s, "要让这些历史标本重见天日", "要让这些历史台纸重见天日", 1, "zhs 历史台纸")
d = next_draft(ZS, "acknowledgments")
wr(d, s)
shutil.copyfile(d, p)
print("OK  zhs acknowledgments ->", os.path.basename(d), "+ current")

# (iii) final_checks privacy loop
ANCHOR = '            for m in re.finditer(pat, text):\n                fails.append(f"{uid}: {kind}: ...'
for fp, ruling in ((ZT + "/_scripts_zht/final_checks_zht.py", "R41"), (ZS + "/_scripts_zhs/final_checks_zhs.py", "ZR54")):
    s = rd(fp)
    skip = ('            if kind == "wife\'s name" and uid == "acknowledgments":\n'
            '                continue  # %s (2026-10-06): the author names her in his own Acknowledgments\n' % ruling)
    if skip in s:
        print("--  already:", fp)
        continue
    s = rep(s, ANCHOR, skip + ANCHOR, 1, "final_checks skip " + ruling)
    wr(fp, s)
    print("OK  final_checks skip added:", os.path.basename(fp))

# (iv) charters section 11
D = [
    ("D08", "ch_01.041 (the plant-survey regulation paragraph) appears twice in a row in the author's 2026-10-05 docx (HC_docx_extracted.md lines 156 and 158); a paste slip, kept once in the English and in both editions"),
    ("D09", "the author's 2026-10-05 edit of the quoted label ch_06.041/.042 removes '1854 earch Institute of Texas' and '1854 年与 … 德克萨斯研究所合作', but ch_06.043, ch_06.044 and ch_06.131 still discuss the year 1854 and the Texas institute; the labels follow the author, the prose stays as written"),
    ("D10", "note_names.015 says his wife prefers to be called simply my wife (as in book one), while the new Acknowledgments name her Weiming twice and give her diagnosis year as 1992 (her memoir: April 1993); translated as written"),
]
s = rd(ZT + "/translation_charter_zht.md")
if "| D08 |" not in s:
    rows = "".join("| %s | %s |\n" % (k, v) for k, v in D)
    m = re.search(r"^\| D07 \|.*\n", s, re.M)
    if not m:
        sys.exit("ABORT: zht D07 row not found")
    s = s[:m.end()] + rows + s[m.end():]
    wr(ZT + "/translation_charter_zht.md", s)
    print("OK  zht charter D08-D10 rows")
s = rd(ZS + "/translation_charter_zhs.md")
if "D08 (" not in s:
    para = "\n2026-10-06 (P10 re-sync): " + " ".join("%s (%s)." % (k, v) for k, v in D) + "\n"
    s = rep(s, "\n## 12. Pending units", para + "\n## 12. Pending units", 1, "zhs charter D08-D10")
    wr(ZS + "/translation_charter_zhs.md", s)
    print("OK  zhs charter D08-D10 paragraph")

# (v) amendment rows (new full rows) + zhs locale tripwire
ROWS = [
    "P021\tLOCK\tWeiming\tWeiming\tWeiming\tacknowledgments.006\t2\tR41/ZR54 (2026-10-06): the author's wife, named by him in the Acknowledgments only; Latin letters, never guessed characters (book one P21).",
    "P022\tLOCK\tBo Chen\tBo Chen\tBo Chen\tacknowledgments.014\t1\t2026-10-06: eldest son; Bo alone stays Latin (P008); book one P22.",
    "P023\tLOCK\tMajor Frank Chen\tFrank Chen 少校\tFrank Chen 少校\tacknowledgments.016\t1\t2026-10-06: second son, teaches history at West Point (西点军校 / 西點軍校); book one P23.",
    "P024\tLOCK\tSarah-Gail Chen\tSarah-Gail Chen\tSarah-Gail Chen\tacknowledgments.016\t1\t2026-10-06: daughter-in-law; book one P24.",
    "P025\tLOCK\tLevi and Caroline\tLevi 和 Caroline\tLevi 和 Caroline\tacknowledgments.017\t1\t2026-10-06: grandchildren; no characters exist for Caroline; book one P25.",
    "INST042\tLOCK\tAccess Intellect\tAccess Intellect\tAccess Intellect\tacknowledgments.014\t2\t2026-10-06: Bo Chen's company; no Chinese name exists (his own zh pages keep the Latin); book one I25.",
    "INST044\tGUIDE\tBRIT Press\tBRIT 出版社\tBRIT 出版社\tacknowledgments.007\t1\t2026-10-06: the shipped ch_08 form (BRIT 出版社的主任); Craig Meyer's post.",
]
for fp in (ZT + "/_key/registry_amendments_zht.tsv", ZS + "/_key/registry_amendments_zhs.tsv"):
    s = rd(fp)
    added = 0
    for row in ROWS:
        rid = row.split("\t", 1)[0]
        if re.search(r"^%s\t" % rid, s, re.M):
            continue
        if not s.endswith("\n"):
            s += "\n"
        s += row + "\n"
        added += 1
    wr(fp, s)
    print("OK  %s: %d new rows" % (os.path.basename(fp), added))
lp = ZS + "/_key/locale_layer_zhs.txt"
s = rd(lp)
if "伫列" not in s:
    if not s.endswith("\n"):
        s += "\n"
    s += ("ML157 | lex | TRIP | queue | 佇列 | acknowledgments.008 | 队列 | 伫列 | \\bqueues?\\b | H | "
          "名词委: queue 队列 | added 2026-10-06 (ZR56): OpenCC tw2s leaves Taiwan 佇列 as 伫列, which is not a mainland word; "
          "the mainland form is 队列.\n")
    wr(lp, s)
    print("OK  locale layer ML157 伫列 -> 队列")

# (vi) segment numbers in the earlier notes
for fp in (ZT + "/_key/registry_amendments_zht.tsv", ZS + "/_key/registry_amendments_zhs.tsv",
           ZT + "/translation_charter_zht.md", ZS + "/translation_charter_zhs.md"):
    s = rd(fp)
    c = s.count("acknowledgments.006, .011")
    if c:
        wr(fp, s.replace("acknowledgments.006, .011", "acknowledgments.006, .010"))
        print("OK  %s: %d segment-number fixes" % (os.path.basename(fp), c))
# ZR56 charter line
s = rd(ZS + "/translation_charter_zhs.md")
line = "| ZR56 | 2026-10-06 | Locale tripwire ML157: 伫列 (OpenCC's rendering of Taiwan 佇列) is not a mainland word; queue = 队列 (acknowledgments.008). |"
if line not in s:
    wr(ZS + "/translation_charter_zhs.md", s.rstrip("\n") + "\n" + line + "\n")
    print("OK  zhs charter ZR56")
print("DONE")
