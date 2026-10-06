#!/usr/bin/env python3
"""unit_patch.py: change ONE thing in a unit's text with the discipline the translation method demands:
an exact-count assertion before any write, append-only versioned drafts, the promoted copy refreshed,
the block count held (positional alignment to the source segments depends on it), and the changed block
printed in full so the editor reads it in its sentence.

Usage (translation workspaces: translation/drafts + translation/current):
  python _tools/unit_patch.py --workspace WS --unit ch_01 --old-file old.txt --new-file new.txt [--expect 1]
  python _tools/unit_patch.py --workspace WS --unit ch_01 --seq 27 --with-file para.txt
English workspaces (manuscript/drafts + manuscript/current/<unit>_current.md): add --manuscript.
Options: --dry-run (report only), --allow-count-change (when the edit is meant to add or drop a block),
--drafts DIR / --current FILE to override the layout.
Put the old and new text in files (UTF-8), never on the command line: apostrophes, CJK and backslashes
travel badly through shells. Exit 0 ok / 1 refused (count mismatch, block-count drift) / 2 usage.
"""
import argparse
import os
import re
import shutil
import sys


def rd(p):
    with open(p, encoding="utf-8-sig") as f:
        return f.read()


def wr(p, s):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8", newline="\n") as f:
        f.write(s)


def blocks(s):
    return [b.strip() for b in re.split(r"\n\s*\n", s) if b.strip()]


def next_draft(drafts, unit):
    n = 1
    for name in os.listdir(drafts) if os.path.isdir(drafts) else []:
        m = re.fullmatch(re.escape(unit) + r"_v(\d+)(?:_[^.]*)?\.md", name)
        if m:
            n = max(n, int(m.group(1)) + 1)
    return os.path.join(drafts, "%s_v%d.md" % (unit, n))


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--workspace", required=True)
    ap.add_argument("--unit", required=True)
    ap.add_argument("--manuscript", action="store_true", help="English layout: manuscript/current/<unit>_current.md")
    ap.add_argument("--drafts")
    ap.add_argument("--current")
    ap.add_argument("--old-file")
    ap.add_argument("--new-file")
    ap.add_argument("--expect", type=int, default=1)
    ap.add_argument("--seq", type=int, help="replace the n-th block (1-based) with --with-file")
    ap.add_argument("--with-file")
    ap.add_argument("--allow-count-change", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    ws = a.workspace
    if a.manuscript:
        drafts = a.drafts or os.path.join(ws, "manuscript", "drafts")
        current = a.current or os.path.join(ws, "manuscript", "current", a.unit + "_current.md")
    else:
        drafts = a.drafts or os.path.join(ws, "translation", "drafts")
        current = a.current or os.path.join(ws, "translation", "current", a.unit + ".md")
    if not os.path.exists(current):
        sys.exit("no such unit file: " + current)
    s = rd(current)
    before = blocks(s)
    if a.old_file and a.new_file:
        old = rd(a.old_file).strip("\n")
        new = rd(a.new_file).strip("\n")
        c = s.count(old)
        if c != a.expect:
            print("REFUSED: expected %d occurrence(s), found %d" % (a.expect, c))
            return 1
        s2 = s.replace(old, new)
    elif a.seq and a.with_file:
        new = rd(a.with_file).strip()
        if not (1 <= a.seq <= len(before)):
            print("REFUSED: seq %d out of range 1..%d" % (a.seq, len(before)))
            return 1
        target = before[a.seq - 1]
        c = s.count(target)
        if c != 1:
            print("REFUSED: block %d is not unique in the file (%d hits); use --old-file/--new-file" % (a.seq, c))
            return 1
        s2 = s.replace(target, new)
    else:
        ap.error("give --old-file/--new-file or --seq/--with-file")
        return 2
    after = blocks(s2)
    if len(after) != len(before) and not a.allow_count_change:
        print("REFUSED: block count would change %d -> %d (pass --allow-count-change if intended)" % (len(before), len(after)))
        return 1
    changed = [(i + 1, b) for i, (x, b) in enumerate(zip(before, after)) if x != b]
    for i, b in changed:
        print("block %d now reads:\n    %s\n" % (i, b.replace("\n", "\n    ")))
    if len(after) != len(before):
        print("block count %d -> %d" % (len(before), len(after)))
    if a.dry_run:
        print("DRY RUN: nothing written")
        return 0
    d = next_draft(drafts, a.unit)
    wr(d, s2)
    shutil.copyfile(d, current)
    print("OK  %s written and promoted to %s" % (os.path.basename(d), current))
    return 0


if __name__ == "__main__":
    sys.exit(main())
