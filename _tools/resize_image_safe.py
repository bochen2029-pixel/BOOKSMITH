#!/usr/bin/env python3
"""
resize_image_safe.py — 2000px ingestion guard (BOOKSMITH).

PURPOSE
    Prevent the non-recoverable session crash that happens when a >2000px
    image is Read into Claude's conversation. The API hard-caps image
    dimensions for many-image requests; exceeding the cap aborts the
    conversation with:
        "An image in the conversation exceeds the dimension limit for
         many-image requests (2000px)."
    Cover wraps are ~4255x3125 (hardcover) / ~3801x2775 (paperback) and
    ALWAYS trip it, so every image handed to Read/vision must pass through
    this guard first. Safe to run unconditionally.

BEHAVIOR (LESSONS_LEDGER §10.3)
    - If the source is already <=2000px in BOTH dimensions: print the source
      path unchanged and exit 0. It is safe to Read directly.
    - If the source exceeds 2000px in EITHER dimension: LANCZOS-downsample to
      fit within a 2000x2000 bounding box (aspect ratio preserved), save to
      the same directory with a `_r2k` suffix, and print the new path. The
      caller should Read the printed path.

CONTRACT (KIT_ARCHITECTURE (c) resize_image_safe.py)
    python resize_image_safe.py <img>
        -> pass-through if <=2000px else LANCZOS into 2000x2000 with `_r2k`
           suffix. Prints the safe path on stdout. Exit 0 on success,
           non-zero on error.

    Wrapper pattern for calling from another tool / agent:
        safe = $(python _tools/resize_image_safe.py "$image_path")
        # then Read "$safe"

SOURCE
    C:\\Claude-Titanic\\_tools\\resize_image_safe.py (organ mirror:
    C:\\imguard\\imguard.py). Ported verbatim in behavior; only the module
    docstring + banner were kit-adapted.
"""
import sys
from pathlib import Path

MAX_DIM = 2000
R2K_SUFFIX = "_r2k"


def resize_if_needed(src: Path) -> Path:
    """Return a path <=2000px in both dims. Echoes the source if already
    safe; otherwise downsamples with LANCZOS to a 2000x2000 box and returns
    the `_r2k`-suffixed output path. Raises on missing Pillow / bad image."""
    from PIL import Image

    img = Image.open(src)
    w, h = img.size

    if w <= MAX_DIM and h <= MAX_DIM:
        # Already safe — do not touch the file, echo the original path.
        return src

    # Compute the scale that fits the image inside MAX_DIM x MAX_DIM.
    scale = min(MAX_DIM / w, MAX_DIM / h)
    new_w = max(1, int(round(w * scale)))
    new_h = max(1, int(round(h * scale)))

    # Normalize exotic modes so resize + save behave; keep RGB/RGBA/L as-is.
    if img.mode not in ("RGB", "RGBA", "L"):
        img = img.convert("RGB")
    resized = img.resize((new_w, new_h), Image.LANCZOS)

    # Output next to the source with a `_r2k` suffix before the extension.
    out = src.with_name(src.stem + R2K_SUFFIX + src.suffix)

    save_kwargs = {}
    if src.suffix.lower() in (".jpg", ".jpeg"):
        save_kwargs["quality"] = 92
        # JPEG cannot carry an alpha channel — flatten if present.
        if resized.mode == "RGBA":
            resized = resized.convert("RGB")

    resized.save(out, **save_kwargs)
    print(f"[INFO] resized {w}x{h} -> {new_w}x{new_h}  (saved to {out.name})",
          file=sys.stderr)
    return out


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: resize_image_safe.py <path_to_image>", file=sys.stderr)
        return 2

    src = Path(sys.argv[1])
    if not src.exists():
        print(f"[ERROR] not found: {src}", file=sys.stderr)
        return 2

    try:
        from PIL import Image  # noqa: F401  (import-guard for a friendly error)
    except ImportError:
        print("[ERROR] Pillow not installed (pip install Pillow)", file=sys.stderr)
        return 3

    try:
        safe = resize_if_needed(src)
    except Exception as exc:  # noqa: BLE001 — surface any decode/save failure
        print(f"[ERROR] could not process {src}: {exc}", file=sys.stderr)
        return 3

    # The one line of stdout is the machine-readable contract: the safe path.
    print(str(safe))
    return 0


if __name__ == "__main__":
    sys.exit(main())
