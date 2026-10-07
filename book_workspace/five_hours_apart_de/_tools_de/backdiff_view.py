#!/usr/bin/env python3
"""backdiff_view.py: the moderator's English-against-English view (method v3 P5): for each segment of a unit, the frozen
English (EN) above the blind back-translation (BT) from _qa/back/<unit>.md, so meaning drift shows as a difference
between two English texts.

  python3 _tools_de/backdiff_view.py ch_04 [ch_05 ...] [--skip-same]

--skip-same leaves out segments whose back-translation is word-for-word the English (after case and punctuation are
set aside). The back-translator's own notes (#### notes) print at the end of the unit.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import de_common as C  # noqa: E402


def load_back(unit):
    p = os.path.join(C.WS, "_qa", "back", unit + ".md")
    if not os.path.exists(p):
        return None, ""
    text = C.read(p)
    notes = ""
    m = re.search(r"^#### notes.*$", text, flags=re.M)
    if m:
        text, notes = text[:m.start()], text[m.start():]
    out, cur = {}, None
    for line in text.split("\n"):
        h = re.match(r"^### (\S+)\s*$", line)
        if h:
            cur = h.group(1)
            out[cur] = []
        elif cur:
            out[cur].append(line)
    return {k: "\n".join(v).strip() for k, v in out.items()}, notes.strip()


def norm(s):
    return " ".join(re.findall(r"[a-z0-9]+", s.lower().replace("’", "'")))


def main():
    a = sys.argv[1:]
    skip = "--skip-same" in a
    segs = C.load_segments()
    for unit in [x for x in a if not x.startswith("--")]:
        back, notes = load_back(unit)
        if back is None:
            print("== %s: no back-translation yet" % unit)
            continue
        print("== %s" % unit)
        for s in segs[unit]:
            bt = back.get(s["id"], "<MISSING>")
            if skip and norm(bt) == norm(s["text"]):
                continue
            print("-- %s" % s["id"])
            print("EN: " + s["text"])
            print("BT: " + bt)
        extra = sorted(set(back) - {s["id"] for s in segs[unit]})
        if extra:
            print("!! ids in the back-translation that the source does not have: %s" % ", ".join(extra))
        if notes:
            print(notes)
        print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
