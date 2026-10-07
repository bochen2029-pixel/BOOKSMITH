#!/usr/bin/env python3
"""merge_r1.py: QA round 1 of the vi-VN edition, the moderator's merge. Reads the moderator's own findings
(_qa/MODERATOR.tsv: the full read plus the English-against-English diff of the blind back-translations) and the
register review (_qa/register/<unit>.md), applies the decisions recorded below, and writes _qa/APPLY_r1.tsv for
_tools_vi/apply_vi.py. Prints every decision so the ship report can count them.

  python3 _qa/merge_r1.py
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WS = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(WS, "_tools_vi"))
import vi_common as C  # noqa: E402

# Moderator rows that a register finding supersedes (id, start of old): the register's wording is the better fix.
MOD_SUPERSEDED = {
}
# Register findings not taken (id, start of old): why.
REG_REJECTED = {
}
# Register findings taken with a different replacement (id, start of old): new text.
REG_MODIFIED = {
}
# Register findings that duplicate or overlap a moderator row (id, start of old): the moderator row stands.
REG_DUPLICATE = {
}

LINE = re.compile(r'^- \[(BLOCK|FIX|NIT)\] (\S+) \| old: "(.*)" \| new: "(.*)" \| why: (.*)$')


def match(table, sid, old):
    for (i, start), v in (table.items() if isinstance(table, dict) else ((k, True) for k in table)):
        if i == sid and old.startswith(start):
            return v
    return None


def main():
    out, log = [], []
    with open(os.path.join(HERE, "MODERATOR.tsv"), encoding="utf-8") as f:
        for line in f.read().split("\n")[1:]:
            if not line.strip():
                continue
            sid, old, new, src, why = line.split("\t")
            sup = match(MOD_SUPERSEDED, sid, old)
            if sup:
                log.append(("MOD", "superseded", sid, old, sup))
                continue
            out.append((sid, old, new, src, why))
            log.append(("MOD", "applied", sid, old, why))
    reg_dir = os.path.join(HERE, "register")
    for u in C.UNITS:
        p = os.path.join(reg_dir, u + ".md")
        if not os.path.exists(p):
            log.append(("REG", "MISSING", u, "", "no register report for this unit"))
            continue
        for line in C.read(p).split("\n"):
            m = LINE.match(line.strip())
            if not m:
                continue
            sev, sid, old, new, why = m.groups()
            rej = match(REG_REJECTED, sid, old)
            if rej:
                log.append(("REG " + sev, "rejected", sid, old, rej))
                continue
            if match(REG_DUPLICATE, sid, old):
                log.append(("REG " + sev, "duplicate", sid, old, "the moderator row covers it"))
                continue
            mod = match(REG_MODIFIED, sid, old)
            if mod:
                new = mod
                log.append(("REG " + sev, "modified", sid, old, "new: " + mod))
            else:
                log.append(("REG " + sev, "applied", sid, old, why))
            out.append((sid, old, new, "REG " + sev, why))
    with open(os.path.join(HERE, "APPLY_r1.tsv"), "w", encoding="utf-8") as f:
        f.write("id\told\tnew\tsource\twhy\n")
        for row in sorted(out, key=lambda r: (C.UNITS.index(r[0].rpartition(".")[0]), r[0])):
            f.write("\t".join(row) + "\n")
    counts = {}
    for src, verdict, *_ in log:
        counts[(src, verdict)] = counts.get((src, verdict), 0) + 1
    for (src, verdict), n in sorted(counts.items()):
        print("%-10s %-11s %3d" % (src, verdict, n))
    for src, verdict, sid, old, why in log:
        if verdict not in ("applied",):
            print("  %-10s %-11s %-10s %s | %s" % (src, verdict, sid, old[:60], why))
    print("APPLY_r1.tsv: %d edits" % len(out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
