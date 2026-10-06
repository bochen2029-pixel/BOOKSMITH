#!/usr/bin/env python3
"""apply_zh_edits.py: patch the four edited source segments into BOTH Chinese editions.
Positional alignment (paragraph n of translation/current/<unit>.md = source segment n).
Each replacement asserts exactly one hit; drafts are append-only (writes drafts/<unit>_v<N>.md,
N = next free), then copies to current/<unit>.md. Run with PYTHONUTF8=1.
"""
import os
import shutil
import sys

ED = {
    "zht": "C:/BOOKSMITH/book_workspace/across_borders_zht/translation",
    "zhs": "C:/BOOKSMITH/book_workspace/across_borders_zhs/translation",
}

# unit -> list of (old substring, new substring) ; all must hit exactly once
EDITS = {
    "zht": {
        "note_names": [
            ("它們的標籤用漢字、日文、英文寫成", "它們的標籤用漢字（簡體或繁體）、日文、英文寫成"),
        ],
        "ch_01": [
            ("這批收藏是1944年在達拉斯的南美以美大學開始的。BRIT 本身成立於1987年，為的是給這批收藏一個自己的家。讀到的時候，我注意到了這個年份，因為1987年也是我來到這個國家的那一年。",
             "這批收藏是1944年在達拉斯的南美以美大學開始的。BRIT 本身成立於1987年，為的是給這批收藏一個自己的家。這個年份引起了我的注意，因為1987年也是我來到這個國家的那一年，我落腳奧斯汀，在德州大學藥學院當訪問學者。"),
            ("那天我們見到了 Craig Meyer，Craig 帶我們走了一遍收藏室。從那以後，我認識 Craig 大多是透過電子郵件，那些信總是很開朗，最短的幾封只署了一個字母。",
             "那天我們見到了 Craig Meyer。他個子高，相貌英俊，儀容整潔，留著修剪得很短的鬍子。Craig 帶我們走了一遍收藏室。後來，我認識他大多是透過他的電子郵件，那些信總是很開朗；最短的幾封只署了一個字母。"),
        ],
        "ch_06": [
            ("T616188 Wen-Pen Leu 1854 earch Institute of Texas with C.-C. Liao", "T616188 Wen-Pen Leu with C.-C. Liao"),
            ("T616188 Wen-Pen Leu 1854 年与 C.-C. 德克萨斯研究所合作。廖S.-L。 Ho", "T616188 Wen-Pen Leu 与 C.-C. 廖S.-L。 Ho"),
        ],
    },
    "zhs": {
        "note_names": [
            ("它们的标签用汉字、日文、英文写成", "它们的标签用汉字（简体或繁体）、日文、英文写成"),
        ],
        "ch_01": [
            ("这批收藏是1944年在达拉斯的南卫理公会大学开始的。BRIT 本身成立于1987年，为的是给这批收藏一个自己的家。读到的时候，我注意到了这个年份，因为1987年也是我来到这个国家的那一年。",
             "这批收藏是1944年在达拉斯的南卫理公会大学开始的。BRIT 本身成立于1987年，为的是给这批收藏一个自己的家。这个年份引起了我的注意，因为1987年也是我来到这个国家的那一年，我落脚奥斯汀，在得克萨斯大学药学院当访问学者。"),
            ("那天我们见到了 Craig Meyer，Craig 带我们走了一遍收藏室。从那以后，我认识 Craig 大多是通过电子邮件，那些信总是很开朗，最短的几封只署了一个字母。",
             "那天我们见到了 Craig Meyer。他个子高，相貌英俊，仪容整洁，留着修剪得很短的胡子。Craig 带我们走了一遍收藏室。后来，我认识他大多是通过他的电子邮件，那些信总是很开朗；最短的几封只署了一个字母。"),
        ],
        "ch_06": [
            ("T616188 Wen-Pen Leu 1854 earch Institute of Texas with C.-C. Liao", "T616188 Wen-Pen Leu with C.-C. Liao"),
            ("T616188 Wen-Pen Leu 1854 年与 C.-C. 德克萨斯研究所合作。廖S.-L。 Ho", "T616188 Wen-Pen Leu 与 C.-C. 廖S.-L。 Ho"),
        ],
    },
}


def next_draft(drafts, unit):
    n = 1
    while os.path.exists(os.path.join(drafts, "%s_v%d.md" % (unit, n))):
        n += 1
    return os.path.join(drafts, "%s_v%d.md" % (unit, n))


def main():
    dry = "--apply" not in sys.argv
    for ed, root in ED.items():
        cur, drafts = os.path.join(root, "current"), os.path.join(root, "drafts")
        for unit, pairs in EDITS[ed].items():
            p = os.path.join(cur, unit + ".md")
            s = open(p, encoding="utf-8").read()
            before = s
            for old, new in pairs:
                n = s.count(old)
                if n != 1:
                    sys.exit("ABORT %s/%s: expected 1 hit, found %d for: %s" % (ed, unit, n, old[:60]))
                s = s.replace(old, new)
            paras_before = sum(1 for ln in before.split("\n") if ln.strip())
            paras_after = sum(1 for ln in s.split("\n") if ln.strip())
            if paras_before != paras_after:
                sys.exit("ABORT %s/%s: paragraph count changed %d -> %d" % (ed, unit, paras_before, paras_after))
            if dry:
                print("DRY %s/%s: %d replacement(s) ok, paragraphs %d (unchanged)" % (ed, unit, len(pairs), paras_after))
                continue
            d = next_draft(drafts, unit)
            with open(d, "w", encoding="utf-8", newline="\n") as f:
                f.write(s)
            shutil.copyfile(d, p)
            print("OK  %s/%s: %d replacement(s) -> %s + current" % (ed, unit, len(pairs), os.path.basename(d)))
    print("DRY RUN (pass --apply to write)" if dry else "APPLIED")


if __name__ == "__main__":
    main()
