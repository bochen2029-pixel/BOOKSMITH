#!/usr/bin/env python3
"""img_match.py: match every image in NEW_DIR to its most similar image in OLD_DIR by a
32x32 grayscale normalized correlation (robust to Google-Docs re-encoding and resizing).
Usage: python img_match.py OLD_DIR NEW_DIR
"""
import glob
import os
import sys

from PIL import Image, ImageOps


def thumb(path, n=32):
    im = Image.open(path)
    im = ImageOps.exif_transpose(im).convert("L").resize((n, n), Image.LANCZOS)
    px = list(im.getdata())
    mean = sum(px) / len(px)
    v = [p - mean for p in px]
    norm = sum(x * x for x in v) ** 0.5 or 1.0
    return [x / norm for x in v], Image.open(path).size


def corr(a, b):
    return sum(x * y for x, y in zip(a, b))


def main():
    old_dir, new_dir = sys.argv[1], sys.argv[2]
    olds = {}
    for p in sorted(glob.glob(os.path.join(old_dir, "*"))):
        try:
            olds[os.path.basename(p)] = thumb(p)
        except Exception as e:  # noqa
            print("skip old", p, e)
    print("%-14s %-12s -> %-14s %-12s %s" % ("NEW", "size", "BEST OLD", "size", "corr (2nd)"))
    for p in sorted(glob.glob(os.path.join(new_dir, "*")), key=lambda s: (len(os.path.basename(s)), s)):
        try:
            t, size = thumb(p)
        except Exception as e:  # noqa
            print("skip new", p, e)
            continue
        scores = sorted(((corr(t, ot), name, osz) for name, (ot, osz) in olds.items()), reverse=True)
        best, second = scores[0], scores[1] if len(scores) > 1 else (0, "-", (0, 0))
        flag = "" if best[0] >= 0.90 else "   <== NO GOOD MATCH"
        print("%-14s %-12s -> %-14s %-12s %.3f (%.3f %s)%s" % (
            os.path.basename(p), "%dx%d" % size, best[1], "%dx%d" % best[2], best[0], second[0], second[1], flag))


if __name__ == "__main__":
    main()
