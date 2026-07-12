#!/usr/bin/env python3
r"""
run_batch.py — batch dispatcher for the vendored ComfyUI client.

cover_gen.py resolves the batch runner as `<run_workflow>.parent / "run_batch.py"`.
When kit_env points cover_gen.run_workflow at `_tools/comfy_client.py`, that
derives `_tools/run_batch.py` (this file). It simply forwards to
comfy_client.main() in batch mode, so there is ONE real implementation.

Accepts the same flags cover_gen passes to a batch run:
  --workflow --args --count --randomize-seed --output-dir --host [--timeout]
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import comfy_client  # noqa: E402


def main() -> int:
    argv = list(sys.argv[1:])
    # Force batch mode regardless of how the caller spelled the flags.
    if "--mode" not in argv:
        argv += ["--mode", "batch"]
    return comfy_client.main(argv)


if __name__ == "__main__":
    sys.exit(main())
