#!/usr/bin/env python3
"""add_zh_waivers.py: the kit lint's PARAGRAPH_NOT_TERMINATED check fires on the two URL lines of the Acknowledgments
(and on the ornament paragraph left in older draft copies). They are source-faithful: waive them by exact string in
both Chinese configs (voice.lint_waivers), as the English edition does."""
import json

W = {
    "zht": ["Access Intellect 網站：https://accessintellect.com/", "Bookraising 網站：https://bookraising.org/", "\u2726"],
    "zhs": ["Access Intellect 网站：https://accessintellect.com/", "Bookraising 网站：https://bookraising.org/", "\u2726"],
}
for ed, waivers in W.items():
    p = "C:/BOOKSMITH/book_workspace/across_borders_%s/book_config.json" % ed
    c = json.load(open(p, encoding="utf-8"))
    lw = c.setdefault("voice", {}).setdefault("lint_waivers", [])
    added = 0
    for s in waivers:
        if s not in lw:
            lw.append(s)
            added += 1
    with open(p, "w", encoding="utf-8", newline="\n") as f:
        json.dump(c, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print("OK  %s: %d waivers added (%d total)" % (ed, added, len(lw)))
print("DONE")
