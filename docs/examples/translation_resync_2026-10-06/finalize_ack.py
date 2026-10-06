#!/usr/bin/env python3
"""finalize_ack.py: promote the translation-memory Acknowledgments (zht v4, zhs v7) to current, align the About's
last sentence to the delivered wording (N11), refresh the zhs converter reference copy, rebuild the Epilogue
figure with the tightened crop and propagate it. Gates and builds run from the shell afterwards."""
import json
import os
import shutil
import subprocess
import sys

EN = "C:/BOOKSMITH/book_workspace/across_borders"
ZT = "C:/BOOKSMITH/book_workspace/across_borders_zht"
ZS = "C:/BOOKSMITH/book_workspace/across_borders_zhs"

# 1. drafts -> current
for ws, v in ((ZT, 4), (ZS, 7)):
    d = "%s/translation/drafts/acknowledgments_v%d.md" % (ws, v)
    if not os.path.exists(d):
        sys.exit("ABORT missing " + d)
    shutil.copyfile(d, ws + "/translation/current/acknowledgments.md")
    print("OK  current <- acknowledgments_v%d.md (%s)" % (v, os.path.basename(ws)))
shutil.copyfile(ZT + "/translation/current/acknowledgments.md", ZS + "/_zht_ref/translation_current/acknowledgments.md")
print("OK  _zht_ref refreshed")

# 2. About N11 -> the delivered wording
for ws, ed, old, new in ((ZT, "zht", "正如他常說的，科學無國界。", "他常說，科學無國界。"),
                         (ZS, "zhs", "正如他常说的，科学无国界。", "他常说，科学无国界。")):
    p = "%s/translation/current/config_strings_%s.json" % (ws, ed)
    s = json.load(open(p, encoding="utf-8"))
    a = s["about_the_author"]
    if a.count(old) == 1:
        s["about_the_author"] = a.replace(old, new)
        with open(p, "w", encoding="utf-8", newline="\n") as f:
            json.dump(s, f, ensure_ascii=False, indent=2)
            f.write("\n")
        print("OK  %s About N11 aligned" % ed)
    elif new in a:
        print("--  %s About N11 already aligned" % ed)
    else:
        sys.exit("ABORT %s About: N11 sentence not found" % ed)

# 3. the Epilogue figure with the tightened crop (bezels off): (14, 97, 894, 590)
mf = EN + "/_scripts/make_figures.py"
s = open(mf, encoding="utf-8").read()
old_row = '("HC_2026-10-02_portal_laptop.jpg", "desk_2026-09-22_portal.jpg", (0, 97, 981, 590)),'
new_row = '("HC_2026-10-02_portal_laptop.jpg", "desk_2026-09-22_portal.jpg", (14, 97, 894, 590)),'
if s.count(old_row) == 1:
    with open(mf, "w", encoding="utf-8", newline="\n") as f:
        f.write(s.replace(old_row, new_row))
    print("OK  make_figures.py crop row updated")
elif new_row in s:
    print("--  make_figures.py crop row already updated")
else:
    sys.exit("ABORT make_figures row not found")
sys.path.insert(0, EN + "/_scripts")
import make_figures as m  # noqa: E402
path, size, nb = m.build("HC_2026-10-02_portal_laptop.jpg", "desk_2026-09-22_portal.jpg", (14, 97, 894, 590))
print("OK  figure rebuilt", size, nb // 1024, "KB")
for ws, ed in ((ZT, "zht"), (ZS, "zhs")):
    r = subprocess.run([sys.executable, "%s/_scripts_%s/setup_assets_%s.py" % (ws, ed, ed)], capture_output=True,
                       text=True, encoding="utf-8", errors="replace", env=dict(os.environ, PYTHONUTF8="1"))
    print("OK  setup_assets_%s rc=%d" % (ed, r.returncode), (r.stdout.strip().splitlines() or [""])[-1][:80])
print("DONE")
