#!/usr/bin/env python3
r"""
estimate_tokens.py — vendored token sizer for BOOKSMITH.

Replaces the reference machine's external chunker/estimate_tokens organ so the
kit sizes files before reading them WITHOUT any external tool. "Never
blind-read a file >8K tokens" (CLAUDE.md) works on any machine this way.

  python estimate_tokens.py FILE [FILE ...]

Per file it prints bytes, chars, words, a token count, and fit hints against
Claude's 200K and 1M context windows. Token count uses tiktoken's o200k_base
BPE when importable (a close proxy for Claude's tokenizer); otherwise it falls
back to a chars/4 heuristic and says so.

Pure stdlib + optional tiktoken.
"""

from __future__ import annotations

import sys
from pathlib import Path

CTX_200K = 200_000
CTX_1M = 1_000_000
HEURISTIC_DIVISOR = 4  # ~4 chars/token, the standard no-API estimate

try:
    import tiktoken  # type: ignore[import-not-found]
    _ENC = tiktoken.get_encoding("o200k_base")
    HAVE_TIKTOKEN = True
except Exception:  # ImportError, or model-data download blocked
    _ENC = None
    HAVE_TIKTOKEN = False


def _read_text(path: Path) -> str:
    # Best-effort decode; replace undecodable bytes so binaries still size.
    return path.read_bytes().decode("utf-8", errors="replace")


def _heuristic_tokens(char_count: int) -> int:
    return (char_count + HEURISTIC_DIVISOR - 1) // HEURISTIC_DIVISOR


def size_one(path: Path) -> int:
    """Print the size block for one file. Returns an exit-code contribution."""
    if not path.exists():
        print(f"{path}\n  ! not found")
        return 1
    if path.is_dir():
        print(f"{path}\n  ! is a directory (pass files, not folders)")
        return 1

    data = path.read_bytes()
    text = data.decode("utf-8", errors="replace")
    n_bytes = len(data)
    n_chars = len(text)
    n_words = len(text.split())
    n_lines = text.count("\n") + (1 if text and not text.endswith("\n") else 0)

    heur = _heuristic_tokens(n_chars)
    if HAVE_TIKTOKEN and _ENC is not None:
        tokens = len(_ENC.encode(text, disallowed_special=()))
        token_label = "tiktoken[o200k_base]"
        token_note = "exact BPE; close proxy for Claude"
    else:
        tokens = heur
        token_label = "heuristic[chars/4]"
        token_note = "no-API estimate (install tiktoken for exact BPE)"

    pct_200k = 100.0 * tokens / CTX_200K
    pct_1m = 100.0 * tokens / CTX_1M

    print(str(path))
    print(f"  {n_bytes:,} bytes | {n_chars:,} chars | "
          f"{n_words:,} words | {n_lines:,} lines")
    print(f"  {token_label} = {tokens:,} tokens  ({token_note})")
    if HAVE_TIKTOKEN:
        print(f"  heuristic     ~ {heur:,} tokens  (no-API estimate, for reference)")
    print(f"  fits: {pct_200k:.1f}% of 200K  |  {pct_1m:.1f}% of 1M")
    return 0


def main(argv=None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if not args or args[0] in ("-h", "--help"):
        print("usage: estimate_tokens.py FILE [FILE ...]", file=sys.stderr)
        return 2 if not args else 0
    rc = 0
    for i, a in enumerate(args):
        if i:
            print()  # blank line between files
        rc |= size_one(Path(a).expanduser())
    return rc


if __name__ == "__main__":
    sys.exit(main())
