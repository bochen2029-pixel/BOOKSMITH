#!/usr/bin/env python3
"""fix_orn_waiver.py: the book_face_coverage check reads every string in book_config.json, so the ✦ lint waiver
itself put the ornament back into the chars the fonts must cover. Remove that waiver from both Chinese configs and
strip the ornament paragraph from promote's superseded copies under manuscript/drafts (the translation/drafts record
is untouched), so the kit lint stays clean without the waiver."""
import glob
import json

for ed in ("zht", "zhs"):
    ws = "C:/BOOKSMITH/book_workspace/across_borders_%s" % ed
    p = ws + "/book_config.json"
    c = json.load(open(p, encoding="utf-8"))
    lw = c.get("voice", {}).get("lint_waivers", [])
    if "\u2726" in lw:
        lw.remove("\u2726")
        with open(p, "w", encoding="utf-8", newline="\n") as f:
            json.dump(c, f, ensure_ascii=False, indent=2)
            f.write("\n")
        print("OK  %s: ornament waiver removed (%d waivers left)" % (ed, len(lw)))
    n = 0
    for d in glob.glob(ws + "/manuscript/drafts/acknowledgments_v*.md"):
        s = open(d, encoding="utf-8").read()
        if "\n\n\u2726\n\n" in s:
            with open(d, "w", encoding="utf-8", newline="\n") as f:
                f.write(s.replace("\n\n\u2726\n\n", "\n\n"))
            n += 1
    print("OK  %s: ornament stripped from %d superseded manuscript/drafts copies" % (ed, n))
    for m in glob.glob(ws + "/manuscript/**/*.md", recursive=True) + glob.glob(ws + "/translation/current/*.md"):
        if "\u2726" in open(m, encoding="utf-8").read():
            print("!!  ornament still in", m)
print("DONE")
