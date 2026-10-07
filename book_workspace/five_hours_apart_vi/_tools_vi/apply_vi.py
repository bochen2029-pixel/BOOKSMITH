#!/usr/bin/env python3
"""apply_es.py: apply a round of accepted QA edits as ONE count-asserted patch per unit (method v3: append-only drafts,
every change asserted before it is written).

  python3 _tools_vi/apply_es.py _qa/APPLY_r1.tsv [--dry-run]

The TSV has a header and the columns id, old, new, source, why (id = unit.NNN, the block numbering of show_blocks.py).
Every edit must find `old` exactly once inside its block, or the whole round is refused before anything is written.
Then, per unit, the edits are applied block by block and the unit goes through ../../_tools/unit_patch.py (whole-unit
old -> new, --expect 1), which writes the next drafts/<unit>_vN.md and refreshes translation/current/<unit>.md.
Re-pad the rows (rows_vi.py --fix) and re-run the gate afterwards.
"""
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import vi_common as C  # noqa: E402

PATCH = os.path.normpath(os.path.join(C.WS, "..", "..", "_tools", "unit_patch.py"))


def load(path):
    rows = []
    with open(path, encoding="utf-8") as f:
        lines = f.read().split("\n")
    for n, line in enumerate(lines[1:], 2):
        if not line.strip() or line.startswith("#"):
            continue
        cells = line.split("\t")
        if len(cells) < 3:
            sys.exit("line %d: needs id, old, new" % n)
        sid, old, new = cells[0].strip(), cells[1], cells[2]
        unit, _, seq = sid.rpartition(".")
        if unit not in C.UNITS or not seq.isdigit() or not old or old == new:
            sys.exit("line %d: bad edit %r" % (n, sid))
        rows.append((unit, int(seq), old, new, sid))
    return rows


def main():
    a = sys.argv[1:]
    if not a:
        print(__doc__)
        return 2
    dry = "--dry-run" in a
    edits = load(a[0])
    by_unit, bad = {}, 0
    texts = {}
    for unit, seq, old, new, sid in edits:
        if unit not in texts:
            texts[unit] = C.read(os.path.join(C.WS, "translation", "current", unit + ".md"))
        bl = C.blocks(texts[unit])
        if seq < 1 or seq > len(bl):
            print("REFUSE %s: no such block" % sid)
            bad += 1
            continue
        n = bl[seq - 1].count(old)
        if n != 1:
            print("REFUSE %s: old found %d times in the block: %r" % (sid, n, old))
            bad += 1
            continue
        by_unit.setdefault(unit, []).append((seq, old, new, sid))
    if bad:
        print("round refused: %d edit(s) do not apply; nothing written" % bad)
        return 1
    for unit in C.UNITS:
        if unit not in by_unit:
            continue
        bl = C.blocks(texts[unit])
        for seq, old, new, sid in by_unit[unit]:
            if bl[seq - 1].count(old) != 1:
                print("REFUSE %s: an earlier edit in this round changed the block" % sid)
                return 1
            bl[seq - 1] = bl[seq - 1].replace(old, new, 1)
            print("  %-10s %s  ->  %s" % (sid, old, new))
        new_text = C.nfc("\n\n".join(bl) + "\n")
        if dry:
            continue
        with tempfile.TemporaryDirectory() as tmp:
            fo, fn = os.path.join(tmp, "old.txt"), os.path.join(tmp, "new.txt")
            C.write(fo, texts[unit])
            C.write(fn, new_text)
            r = subprocess.run([sys.executable, "-I", PATCH, "--workspace", C.WS, "--unit", unit, "--old-file", fo,
                                "--new-file", fn, "--expect", "1"], capture_output=True, text=True)
            if r.returncode != 0:
                print(r.stdout[-2000:] + r.stderr[-2000:])
                print("unit_patch refused %s" % unit)
                return 1
            print("patched %s (%d edit%s)" % (unit, len(by_unit[unit]), "" if len(by_unit[unit]) == 1 else "s"))
    print("round %s: %d edits in %d units" % ("checked (dry run)" if dry else "applied", len(edits), len(by_unit)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
