#!/usr/bin/env python3
"""
make_giftable.py -- BOOKSMITH distribution packager.

PURPOSE
    One command produces a clean, stranger-safe .zip of the BOOKSMITH kit --
    ready to hand to someone who will run Claude Code on their own desktop.
    It walks the repo, drops everything private/heavy/third-party-encumbered
    per the portability audit, then runs a PERSONAL-DATA GATE over every
    shipped text file. If the gate finds the author's name, email, or a
    machine-specific path, it REFUSES to write the zip (override with
    --allow-personal-data). It never modifies the source tree.

WHAT IT EXCLUDES BY DEFAULT (from the audit)
    .git/ ; dist/ ; __pycache__/ + *.pyc ; _tools/node_modules/ (ship with
    --include-node-modules) ; _tools/kit_env.json (the machine file -- the
    *.template.json ships instead) ; every book_workspace/* except
    book_workspace/testvoyage/** (and even testvoyage keeps only ONE built
    format under outputs/ -- kdp_paperback if present -- and drops
    outputs/markdown; --full-example-outputs keeps them all) ; any
    _REHYDRATION.md or .booksmith_rehydrate anywhere ; SESSION_LOG.md ; the
    third-party Mixam guide + dielines under docs/service_templates/ (ship with
    --keep-service-templates) ; the root Digest_5_5_x_8_5_*.pdf stray ;
    *_r2k.* resized-image scratch ; Thumbs.db / desktop.ini / .DS_Store.

PERSONAL-DATA GATE (text files only)
    Scans .md .txt .py .js .json .html .css .yml .yaml .toml .cfg .ini
    .gitignore .gitattributes for: 'bochen' (case-insensitive), '@gmail',
    'C:\\Users\\user', 'C--Claude-Titanic'. Binary files (ttf/pdf/png/jpg/
    docx/epub/zip/...) are exempt. Any hit is reported as file:line + pattern.
    Hits block the zip (exit 1) unless --allow-personal-data downgrades to a
    loud warning.

USAGE
    python _tools/make_giftable.py                    # build the zip
    python _tools/make_giftable.py --dry-run          # manifest + scan, no write
    python _tools/make_giftable.py --out <path.zip>   # custom output path
    python _tools/make_giftable.py --include-node-modules
    python _tools/make_giftable.py --keep-service-templates
    python _tools/make_giftable.py --full-example-outputs
    python _tools/make_giftable.py --allow-personal-data   # gate -> warning
    Exit codes: 0 = success (or clean dry-run)
                1 = blocked by the personal-data gate
                2 = usage error

PROVENANCE
    Built 2026-07-11 from the BOOKSMITH portability audit (4-agent sweep).
    Pure Python standard library. Repo root is derived from this file's
    location (parent.parent), never cwd, never a hard-coded C:\\BOOKSMITH.
"""

import argparse
import fnmatch
import re
import sys
import time
import zipfile
from pathlib import Path

# Make stdout tolerant of scanned file content that isn't representable in the
# console's legacy code page (e.g. cp1252 on Windows). Without this, printing a
# hit snippet that contains a non-cp1252 glyph raises UnicodeEncodeError and
# crashes the very safety scan we are running. errors='replace' keeps it alive.
try:
    sys.stdout.reconfigure(errors="replace")  # Python 3.7+
except Exception:
    pass

# ---------------------------------------------------------------------------
# Repo root: <repo>/_tools/make_giftable.py -> parent.parent.
# ---------------------------------------------------------------------------
REPO = Path(__file__).resolve().parent.parent

# The single example-output format we keep by default (built proof, small).
KEEP_EXAMPLE_FORMAT = "kdp_paperback"

# Text extensions the personal-data gate reads (everything else is binary).
TEXT_EXTS = {
    ".md", ".txt", ".py", ".js", ".json", ".html", ".css", ".yml", ".yaml",
    ".toml", ".cfg", ".ini", ".gitignore", ".gitattributes",
}

# Personal-data patterns. NOTE: raw strings so backslashes are literal.
PERSONAL_PATTERNS = [
    ("bochen", re.compile(r"bochen", re.IGNORECASE)),
    ("@gmail", re.compile(r"@gmail")),
    (r"C:\Users\user", re.compile(re.escape(r"C:\Users\user"))),
    ("C--Claude-Titanic", re.compile(r"C--Claude-Titanic")),
    # Reference-machine organ/tool roots: shipped text must never instruct a
    # stranger's session to run these (they exist on exactly one PC).
    (r"C:\chunker", re.compile(re.escape(r"C:\chunker"), re.IGNORECASE)),
    (r"C:\imguard", re.compile(re.escape(r"C:\imguard"), re.IGNORECASE)),
    (r"C:\Everything", re.compile(re.escape(r"C:\Everything"), re.IGNORECASE)),
    (r"C:\fetcher", re.compile(re.escape(r"C:\fetcher"), re.IGNORECASE)),
    (r"C:\llama.cpp", re.compile(re.escape(r"C:\llama.cpp"), re.IGNORECASE)),
    (r"C:\models", re.compile(re.escape(r"C:\models"), re.IGNORECASE)),
    ("hermes skill path", re.compile(r"AppData\\+Local\\+hermes", re.IGNORECASE)),
]

# Simple scratch/junk filename globs excluded anywhere.
JUNK_GLOBS = ["*_r2k.*", "Thumbs.db", "desktop.ini", ".DS_Store"]


def _rel_posix(path):
    """Repo-relative path using forward slashes (stable across OSes)."""
    return path.relative_to(REPO).as_posix()


def _matches_any(name, globs):
    return any(fnmatch.fnmatch(name, g) for g in globs)


def is_excluded(path, opts):
    """Decide whether `path` (a file under REPO) is excluded from the gift.

    Returns (excluded: bool, reason: str)."""
    rel = _rel_posix(path)
    parts = rel.split("/")
    name = path.name

    # --- always-excluded top-level trees ------------------------------------
    if parts[0] == ".git":
        return True, ".git/"
    if parts[0] == "dist":
        return True, "dist/ (build output)"

    # --- pycache / compiled -------------------------------------------------
    if "__pycache__" in parts:
        return True, "__pycache__/"
    if name.endswith(".pyc"):
        return True, "*.pyc"

    # --- junk / scratch anywhere -------------------------------------------
    if _matches_any(name, JUNK_GLOBS):
        return True, f"junk/scratch ({name})"

    # --- private rehydration artifacts anywhere ----------------------------
    if name == "_REHYDRATION.md":
        return True, "_REHYDRATION.md (private rehydration dump)"
    if name == ".booksmith_rehydrate":
        return True, ".booksmith_rehydrate (private flag)"

    # --- author's diary -----------------------------------------------------
    if rel == "SESSION_LOG.md":
        return True, "SESSION_LOG.md (author diary)"

    # --- machine config: ship the TEMPLATE, not the live file --------------
    if rel == "_tools/kit_env.json":
        return True, "_tools/kit_env.json (machine paths; template ships instead)"

    # --- vendored node_modules (opt-in) ------------------------------------
    if len(parts) >= 2 and parts[0] == "_tools" and parts[1] == "node_modules":
        if not opts.include_node_modules:
            return True, "_tools/node_modules/ (use --include-node-modules)"

    # --- book_workspace: only testvoyage ships -----------------------------
    # NOTE: never exclude the `book_workspace` dir itself (parts == ['book_workspace'])
    # or we would prune testvoyage with it. Only its non-testvoyage CHILDREN drop.
    if parts[0] == "book_workspace" and len(parts) >= 2:
        if parts[1] != "testvoyage":
            return True, (f"book_workspace/{parts[1]} "
                          "(private; only testvoyage ships)")
        # Inside testvoyage: trim outputs/. Keep ONLY one built format subfolder
        # (KEEP_EXAMPLE_FORMAT) plus drop outputs/markdown. Must stay dir/file
        # aware so we don't prune `outputs/` (len 3) or the kept format dir
        # before the walker can descend into them.
        if len(parts) >= 3 and parts[2] == "outputs" and not opts.full_example_outputs:
            # parts[2]=='outputs' itself (len 3) -> let it through so we descend.
            if len(parts) == 3:
                return False, ""
            fmt = parts[3]  # the outputs child (a format dir, or a loose file)
            # A loose FILE directly under outputs/ (len 4, and it's a file).
            if len(parts) == 4 and path.is_file():
                return True, "testvoyage/outputs/ loose file"
            if fmt == "markdown":
                return True, "testvoyage/outputs/markdown (source dump)"
            if fmt != KEEP_EXAMPLE_FORMAT:
                return True, (f"testvoyage/outputs/{fmt} "
                              f"(only {KEEP_EXAMPLE_FORMAT} ships)")

    # --- docs/service_templates: third-party copyrighted assets ------------
    if not opts.keep_service_templates:
        if len(parts) >= 2 and parts[0] == "docs" and parts[1] == "service_templates":
            # guide.pdf, guide.chunks/*, mixam_template_*.pdf
            if name == "guide.pdf":
                return True, "service guide.pdf (3rd-party, --keep-service-templates)"
            if len(parts) >= 3 and parts[2] == "guide.chunks":
                return True, "service guide.chunks/ (3rd-party)"
            if fnmatch.fnmatch(name, "mixam_template_*.pdf"):
                return True, "mixam dieline (3rd-party, --keep-service-templates)"

    # --- root Digest stray --------------------------------------------------
    if len(parts) == 1 and fnmatch.fnmatch(name, "Digest_5_5_x_8_5_*.pdf"):
        return True, "root Digest_*.pdf stray"

    return False, ""


def walk_repo(opts):
    """Return (included, excluded) lists of Paths, applying exclusion rules.

    Prunes excluded directories so we do not descend into .git / node_modules /
    private workspaces (fast, and avoids scanning huge trees)."""
    included, excluded = [], []

    def _dir_excluded(dpath):
        exc, reason = is_excluded(dpath, opts)
        return exc, reason

    stack = [REPO]
    while stack:
        d = stack.pop()
        try:
            entries = sorted(d.iterdir(), key=lambda p: p.name.lower())
        except Exception:
            continue
        for e in entries:
            if e.is_symlink():
                # Do not follow symlinks into the gift (safety + loops).
                excluded.append((e, "symlink (not shipped)"))
                continue
            if e.is_dir():
                exc, reason = _dir_excluded(e)
                if exc:
                    excluded.append((e, reason + " [dir pruned]"))
                    continue
                stack.append(e)
            elif e.is_file():
                exc, reason = is_excluded(e, opts)
                if exc:
                    excluded.append((e, reason))
                else:
                    included.append(e)
    included.sort(key=lambda p: _rel_posix(p))
    excluded.sort(key=lambda pr: _rel_posix(pr[0]))
    return included, excluded


def scan_personal_data(included):
    """Scan included TEXT files. Returns list of (rel, line_no, pattern, text)."""
    hits = []
    for p in included:
        if p.name == "make_giftable.py":
            continue  # the scanner itself carries the patterns as literals
        if "node_modules" in p.parts:
            continue  # third-party packages legitimately carry their own authors' emails
        if p.suffix.lower() not in TEXT_EXTS and p.name not in TEXT_EXTS:
            continue
        try:
            content = p.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue
        rel = _rel_posix(p)
        for i, line in enumerate(content.splitlines(), 1):
            for label, rx in PERSONAL_PATTERNS:
                if rx.search(line):
                    snippet = line.strip()
                    if len(snippet) > 100:
                        snippet = snippet[:97] + "..."
                    hits.append((rel, i, label, snippet))
    return hits


def human_size(nbytes):
    for unit in ("B", "KB", "MB", "GB"):
        if nbytes < 1024 or unit == "GB":
            return f"{nbytes:.1f} {unit}" if unit != "B" else f"{nbytes} B"
        nbytes /= 1024.0
    return f"{nbytes:.1f} GB"


def check_template_presence():
    """Warn if the kit_env template that SHOULD ship is missing."""
    tmpl = REPO / "_tools" / "kit_env.template.json"
    return tmpl.is_file()


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="make_giftable.py",
        description="Package a stranger-safe BOOKSMITH .zip (stdlib-only).")
    parser.add_argument("--out", metavar="PATH",
                        help="output zip path (default: "
                             "dist/BOOKSMITH_giftable_<YYYYMMDD>.zip)")
    parser.add_argument("--dry-run", action="store_true",
                        help="print manifest + scan; write nothing")
    parser.add_argument("--include-node-modules", action="store_true",
                        help="ship _tools/node_modules/ (default: excluded)")
    parser.add_argument("--keep-service-templates", action="store_true",
                        help="ship docs/service_templates 3rd-party guide+dielines")
    parser.add_argument("--full-example-outputs", action="store_true",
                        help="ship ALL testvoyage outputs/ (default: only "
                             f"{KEEP_EXAMPLE_FORMAT})")
    parser.add_argument("--allow-personal-data", action="store_true",
                        help="downgrade the personal-data gate from block to warn")
    try:
        opts = parser.parse_args(argv)
    except SystemExit:
        return 2

    # ---- walk + classify ---------------------------------------------------
    included, excluded = walk_repo(opts)

    total_size = 0
    for p in included:
        try:
            total_size += p.stat().st_size
        except Exception:
            pass

    # ---- manifest ----------------------------------------------------------
    print()
    print(f"BOOKSMITH make_giftable -- repo: {REPO}")
    print(f"included files: {len(included)}   "
          f"excluded entries: {len(excluded)}   "
          f"total size: {human_size(total_size)}")
    print()
    print("--- MANIFEST (files to ship) ---")
    for p in included:
        try:
            sz = human_size(p.stat().st_size)
        except Exception:
            sz = "?"
        print(f"  {_rel_posix(p):<60} {sz:>10}")

    # A compact summary of what got dropped and why (grouped by reason).
    print()
    print("--- EXCLUDED (grouped by reason) ---")
    by_reason = {}
    for p, reason in excluded:
        by_reason.setdefault(reason, 0)
        by_reason[reason] += 1
    for reason in sorted(by_reason):
        print(f"  [{by_reason[reason]:>3}] {reason}")

    # ---- template presence warning ----------------------------------------
    if not check_template_presence():
        print()
        print("  !! WARNING: _tools/kit_env.template.json is MISSING.")
        print("     The gift will have NO kit_env template for strangers to")
        print("     copy -> they cannot configure machine paths. Create it")
        print("     before shipping (a redacted copy of kit_env.json).")

    # ---- top-10 largest shipped files -------------------------------------
    sized = []
    for p in included:
        try:
            sized.append((p.stat().st_size, p))
        except Exception:
            pass
    sized.sort(reverse=True)
    print()
    print("--- TOP 10 LARGEST SHIPPED FILES ---")
    for sz, p in sized[:10]:
        print(f"  {human_size(sz):>10}  {_rel_posix(p)}")

    # ---- personal-data gate -----------------------------------------------
    hits = scan_personal_data(included)
    print()
    print("--- PERSONAL-DATA SCAN ---")
    if not hits:
        print("  CLEAN: no personal-data patterns found in shipped text files.")
        scan_ok = True
    else:
        scan_ok = False
        print(f"  {len(hits)} HIT(S) across "
              f"{len(set(h[0] for h in hits))} file(s):")
        for rel, line_no, label, snippet in hits:
            print(f"    {rel}:{line_no}  [{label}]  {snippet}")

    verdict = "CLEAN" if scan_ok else (
        "OVERRIDDEN (--allow-personal-data)" if opts.allow_personal_data
        else "BLOCKED")

    # ---- decide + write ----------------------------------------------------
    print()
    print("=" * 66)
    print(f"  scan verdict:  {verdict}")
    print(f"  shipped files: {len(included)}   size: {human_size(total_size)}")

    if not scan_ok and not opts.allow_personal_data:
        print("  RESULT:        NO ZIP WRITTEN -- resolve the hits above, or")
        print("                 re-run with --allow-personal-data to override.")
        print("=" * 66)
        return 1

    if opts.dry_run:
        print("  RESULT:        DRY RUN -- nothing written.")
        print("=" * 66)
        return 0

    if not scan_ok and opts.allow_personal_data:
        print("  !! OVERRIDE:   shipping DESPITE personal-data hits above.")

    # Resolve output path.
    if opts.out:
        out_path = Path(opts.out)
        if not out_path.is_absolute():
            out_path = Path.cwd() / out_path
    else:
        stamp = time.strftime("%Y%m%d")
        out_path = REPO / "dist" / f"BOOKSMITH_giftable_{stamp}.zip"
    out_path.parent.mkdir(parents=True, exist_ok=True)

    # Write the zip. Guard against zipping our own output if it lands under REPO.
    written = 0
    with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for p in included:
            try:
                if p.resolve() == out_path.resolve():
                    continue
                zf.write(p, arcname=_rel_posix(p))
                written += 1
            except Exception as exc:
                print(f"  !! skip {(_rel_posix(p))}: "
                      f"{exc.__class__.__name__}: {exc}")

    zsize = out_path.stat().st_size
    print(f"  RESULT:        WROTE {out_path}")
    print(f"                 {written} files, {human_size(zsize)} compressed.")
    print("=" * 66)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        sys.exit(2)
