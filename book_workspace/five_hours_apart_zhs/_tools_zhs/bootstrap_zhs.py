#!/usr/bin/env python3
"""bootstrap_zhs.py: seed (or refresh) the zh-Hans workspace from the canonical zh-Hant-TW workspace.

Copies, hash-verified, the Taiwan edition's translation/current/*.md into _zht_ref/translation_current/ (the text
the converter reads), the frozen source (_key/segments.jsonl, source_of_record.md, P0_REPORT.json) and the charter
(as _zht_ref/translation_charter_zht.md). Prints every file with its sha256. Run again after any zh-Hant change;
the converter must never read a stale reference.
"""
import hashlib
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WS = os.path.dirname(HERE)
ZHT = os.path.join(os.path.dirname(WS), "five_hours_apart_zht")


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def copy(src, dst):
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    shutil.copyfile(src, dst)
    assert sha(src) == sha(dst)
    print("  %s  %s" % (sha(dst)[:12], os.path.relpath(dst, WS)))


def main():
    cur = os.path.join(ZHT, "translation", "current")
    n = 0
    for name in sorted(os.listdir(cur)):
        if name.endswith(".md"):
            copy(os.path.join(cur, name), os.path.join(WS, "_zht_ref", "translation_current", name))
            n += 1
    for name in ("segments.jsonl", "source_of_record.md", "P0_REPORT.json"):
        copy(os.path.join(ZHT, "_key", name), os.path.join(WS, "_key", name))
    copy(os.path.join(ZHT, "translation_charter_zht.md"), os.path.join(WS, "_zht_ref", "translation_charter_zht.md"))
    print("bootstrapped: %d units" % n)
    return 0


if __name__ == "__main__":
    sys.exit(main())
