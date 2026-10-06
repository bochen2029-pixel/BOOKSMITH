#!/usr/bin/env python3
"""update_both_pins.py: point make_both_editions.py at the zh-Hant v2 package (path + sha256), and restore the v1
package beside it from the backup so same_content.py and the combined zip keep their history."""
import glob
import hashlib
import os
import re
import shutil
import sys

ZT = "C:/BOOKSMITH/book_workspace/across_borders_zht"
MB = "C:/BOOKSMITH/book_workspace/across_borders_zhs/_tools_zhs/make_both_editions.py"

zips = sorted(glob.glob(ZT + "/outputs/_FINAL/across_borders_zht_v2_*.zip"))
if not zips:
    sys.exit("ABORT: no zht v2 zip in outputs/_FINAL")
zp = zips[-1]
pkg = os.path.basename(zp)[:-4]
h = hashlib.sha256(open(zp, "rb").read()).hexdigest()
print("zht v2 zip:", os.path.basename(zp), os.path.getsize(zp), "bytes, sha256", h[:16])

# restore v1 beside v2
bk = ZT + "/outputs/_FINAL_backup_2026-10-06"
for item in os.listdir(bk):
    dst = ZT + "/outputs/_FINAL/" + item
    if not os.path.exists(dst):
        src = bk + "/" + item
        shutil.copytree(src, dst) if os.path.isdir(src) else shutil.copy2(src, dst)
        print("restored beside v2:", item)

s = open(MB, encoding="utf-8").read()
s2 = re.sub(r'ZHT_PKG = BW / "across_borders_zht/outputs/_FINAL/[^"]+"',
            'ZHT_PKG = BW / "across_borders_zht/outputs/_FINAL/%s"' % pkg, s, count=1)
s2 = re.sub(r'ZHT_SHA = "[0-9a-f]{64}"', 'ZHT_SHA = "%s"' % h, s2, count=1)
if s2 == s:
    sys.exit("ABORT: pins not found in make_both_editions.py")
open(MB, "w", encoding="utf-8", newline="\n").write(s2)
print("OK  make_both_editions.py pins -> %s / %s" % (pkg, h[:16]))
