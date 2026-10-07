#!/usr/bin/env python3
"""show_blocks.py: print Spanish units block by block with their ids (unit.NNN), the numbering every QA report uses.

  python3 _tools_es/show_blocks.py ch_04 [ch_05 ...]

Prints only the Spanish of translation/current/<unit>.md (a back-translator stays blind to the English). A fenced row
block is one block; blocks are separated by a blank line.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import es_common as C  # noqa: E402


def main():
    units = sys.argv[1:]
    if not units:
        print(__doc__)
        return 2
    for u in units:
        p = os.path.join(C.WS, "translation", "current", u + ".md")
        if u not in C.UNITS or not os.path.exists(p):
            print("no unit %s" % u)
            return 2
        for i, b in enumerate(C.blocks(C.read(p)), 1):
            print("### %s.%03d" % (u, i))
            print(b)
            print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
