"""
assemble_manuscript.py — Version-pinned master stitcher (the anti-drift keystone).

BOOKSMITH toolchain component. Stitches the front matter + every unit in order
from manuscript/current/ into the ONE version-pinned master
book_workspace/<slug>/outputs/markdown/<slug>_vN.md that EVERY downstream
generator reads.

WHY THIS EXISTS (LESSONS_LEDGER §2.8 / KIT_ARCHITECTURE (c)):
  A Kindle once shipped 8,476 words SHORT of the print because the print
  generator read v7 and the Kindle read v6 — divergent sources. The fix is a
  single version-pinned master: assemble once, and every format builds from
  that exact file. This script writes that file (append-only version bump: it
  never overwrites v1 — it writes v2, v3, ...) and prints the total word count,
  which is the parity baseline every format is checked against.

SOURCE: new — formalizes the implicit by-hand stitch every prior book did.
  The word-count-parity discipline (parts-sum == stitched master) is
  LESSONS_LEDGER §1.3 / §2.8.

Unit ordering (explicit include-list, NEVER a directory glob — §1.3):
  Ordered unit ids are resolved from book_config in this precedence:
    1. book_config.units[] / structure[] / unit_order[]   (explicit list), else
    2. book_config.authorship.per_chapter_overrides keys   (ordered dict), else
    3. hard error (we refuse to glob the directory and risk shipping a
       superseded draft — repos hold up to 5 byte-identical mirror copies).

Front matter:
  Assembled from book_config.front_matter[] in order. For each entry we look for
  manuscript/current/front_<type>.md (e.g. front_half_title.md, front_copyright.md).
  A "blank" entry contributes nothing to the stitched markdown (blanks are a
  print-layout concept the generators insert, not manuscript text). A declared
  front-matter file that does not exist on disk is skipped with a note (front
  matter is often ceremonial and Class-A/human-authored — its absence must not
  block assembly), but every MISSING BODY UNIT is a hard error.

Per-unit file resolution under manuscript/current/:
  <unit_id>_current.md  (preferred)  |  <unit_id>.md

Usage:
  python assemble_manuscript.py --config book_config.json [--workspace <dir>]
                                [--version N]   # force a specific version number
                                [--overwrite]   # permit replacing an existing vN
                                                # (required if --version N already
                                                #  exists; append-only otherwise)

Prints a JSON summary on stdout including the total word count (the baseline):
  {"master":..., "version":N, "words":W, "parts_word_sum":S, "parity_ok":bool,
   "units":[{"id":...,"words":w}], ...}
and, on its own final stdout line, `TOTAL_WORDS=W` (the parity baseline a stdout
parser can read). parts_word_sum is an INDEPENDENT re-read of each source file
from disk, so parity_ok is a real cross-check, not a tautology.
"""
import sys
import os
import re
import json
import glob

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def word_count(text: str) -> int:
    """Whitespace-delimited word count — the same definition wc -w uses, so the
    parity baseline lines up with the manual checks in the ledger."""
    return len(text.split())


def resolve_workspace(cfg, workspace_arg, config_path):
    """Workspace root = the CONFIG's directory (the engine/compositor/verifier
    convention). The old kit-root book_workspace/<slug> default silently wrote
    into a DIFFERENT book's tree whenever a workspace dirname and its slug
    diverged (e.g. a scratch copy carrying the original slug)."""
    if workspace_arg:
        return os.path.abspath(workspace_arg)
    ws = os.path.dirname(os.path.abspath(config_path))
    if os.path.basename(ws) != cfg.get("slug"):
        print(f"[assemble] NOTE: workspace dirname {os.path.basename(ws)!r} != slug "
              f"{cfg.get('slug')!r}; using the config's parent as the workspace root",
              file=sys.stderr)
    return ws


def resolve_unit_ids(cfg):
    """Ordered body-unit ids from the EXPLICIT config units[] — never a glob.
    (The old structure[]/unit_order[] aliases were schema-forbidden — root
    additionalProperties:false — so they were dead branches for any config
    that passes GATE-2.)"""
    v = cfg.get("units")
    if isinstance(v, list) and v:
        ids = []
        for item in v:
            if isinstance(item, str):
                ids.append(item)
            elif isinstance(item, dict):
                ids.append(item.get("id") or item.get("unit_id") or "")
        ids = [i for i in ids if i]
        if ids:
            return ids
    overrides = (cfg.get("authorship") or {}).get("per_chapter_overrides") or {}
    if isinstance(overrides, dict) and overrides:
        return list(overrides.keys())
    raise ValueError(
        "Cannot resolve an ordered unit list from book_config "
        "(need units[] or authorship.per_chapter_overrides). Refusing to glob "
        "the directory (risk of shipping a superseded mirror copy).")


def find_unit_file(current_dir, unit_id):
    """Preferred <id>_current.md, else <id>.md."""
    for name in (f"{unit_id}_current.md", f"{unit_id}.md"):
        p = os.path.join(current_dir, name)
        if os.path.exists(p):
            return p
    return None


def find_front_matter_file(current_dir, fm_type):
    """front_<type>_current.md | front_<type>.md | <type>_current.md | <type>.md"""
    candidates = [
        f"front_{fm_type}_current.md",
        f"front_{fm_type}.md",
        f"{fm_type}_current.md",
        f"{fm_type}.md",
    ]
    for name in candidates:
        p = os.path.join(current_dir, name)
        if os.path.exists(p):
            return p
    return None


def read_text(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def next_version(markdown_dir, slug, forced=None):
    """Append-only version bump: find the highest existing <slug>_vN.md and add
    one. Never overwrites an existing version."""
    if forced is not None:
        return forced
    highest = 0
    pattern = os.path.join(markdown_dir, f"{slug}_v*.md")
    for path in glob.glob(pattern):
        m = re.search(rf"{re.escape(slug)}_v(\d+)\.md$", os.path.basename(path))
        if m:
            highest = max(highest, int(m.group(1)))
    return highest + 1


def assemble(config_path, workspace_arg, forced_version, overwrite=False):
    cfg = load_json(config_path)
    slug = cfg["slug"]
    ws = resolve_workspace(cfg, workspace_arg, config_path)
    current_dir = os.path.join(ws, "manuscript", "current")
    markdown_dir = os.path.join(ws, "outputs", "markdown")

    if not os.path.isdir(current_dir):
        raise FileNotFoundError(
            f"manuscript/current not found at {current_dir}. Nothing to stitch.")
    os.makedirs(markdown_dir, exist_ok=True)

    pieces = []
    notes = []
    # Disk paths of every source piece, in stitch order; re-read at parity time
    # for an INDEPENDENT word count (not the same in-memory pieces the master was
    # built from), so parity is a real cross-check rather than a tautology.
    source_paths = []

    # --- Front matter (ordered, ceremonial; missing files skipped with a note) ---
    front_report = []
    for entry in (cfg.get("front_matter") or []):
        fm_type = entry.get("type") if isinstance(entry, dict) else str(entry)
        if fm_type == "blank":
            # Blank versos are a print-layout concept inserted by the generators;
            # they contribute no manuscript text.
            front_report.append({"type": "blank", "file": None, "words": 0})
            continue
        fpath = find_front_matter_file(current_dir, fm_type)
        if not fpath:
            notes.append(f"front matter '{fm_type}' declared but no file on disk (skipped)")
            front_report.append({"type": fm_type, "file": None, "words": 0})
            continue
        text = read_text(fpath).rstrip()
        pieces.append(text)
        source_paths.append(fpath)
        front_report.append({"type": fm_type, "file": os.path.basename(fpath),
                             "words": word_count(text)})

    # --- Body units (explicit ordered list; every missing unit is a HARD error) ---
    unit_ids = resolve_unit_ids(cfg)
    unit_report = []
    missing = []
    for unit_id in unit_ids:
        fpath = find_unit_file(current_dir, unit_id)
        if not fpath:
            missing.append(unit_id)
            continue
        text = read_text(fpath).rstrip()
        pieces.append(text)
        source_paths.append(fpath)
        unit_report.append({"id": unit_id, "file": os.path.basename(fpath),
                            "words": word_count(text)})

    if missing:
        raise FileNotFoundError(
            "Missing body unit file(s) under manuscript/current for: "
            + ", ".join(missing)
            + ". Every ordered unit must exist before assembly (refusing to "
              "ship a partial master).")

    # --- Stitch (single trailing newline between units) ---
    master_text = "\n\n".join(pieces).rstrip() + "\n"
    total_words = word_count(master_text)
    body_words = sum(u["words"] for u in unit_report)
    front_words = sum(f["words"] for f in front_report)

    version = next_version(markdown_dir, slug, forced_version)
    master_path = os.path.join(markdown_dir, f"{slug}_v{version}.md")
    if forced_version is None and os.path.exists(master_path):
        # Defensive: append-only means we never clobber. Bump past any race.
        version = next_version(markdown_dir, slug, None)
        master_path = os.path.join(markdown_dir, f"{slug}_v{version}.md")
    elif forced_version is not None and os.path.exists(master_path) and not overwrite:
        # A forced --version must NOT silently clobber a pinned master (the
        # docstring promises append-only). Require an explicit --overwrite.
        raise SystemExit(
            f"refusing to overwrite {master_path} without --overwrite "
            f"(the master is append-only; pass --overwrite to replace v{version}).")

    with open(master_path, "w", encoding="utf-8") as f:
        f.write(master_text)

    # Parity integrity (§1.3): an INDEPENDENT re-read of each source file from
    # disk, summed. This is a genuine cross-check: a whitespace .join can never
    # merge/split tokens, so summing the SAME in-memory pieces would always equal
    # total_words (a tautology). Re-reading catches a source that changed on disk
    # mid-run, or a piece that was dropped/duplicated between stitch and report.
    parts_sum = sum(word_count(read_text(p).rstrip()) for p in source_paths)
    parity_ok = parts_sum == total_words

    summary = {
        "master": master_path,
        "version": version,
        "words": total_words,
        "body_words": body_words,
        "front_matter_words": front_words,
        "front_matter": front_report,
        "units": unit_report,
        "unit_count": len(unit_report),
        "parts_word_sum": parts_sum,
        "parity_ok": parity_ok,
        "notes": notes,
    }
    print(json.dumps(summary, indent=2))
    if not parity_ok:
        print(f"[WARN] parity mismatch: re-read source sum {parts_sum} != "
              f"stitched master {total_words} (a source file changed on disk "
              f"during assembly, or a piece was dropped/duplicated).",
              file=sys.stderr)
    # BODY_WORDS is the parity baseline every format is checked against: the
    # generators render front matter FROM CONFIG and drop any stitched front-
    # matter markdown, so the master total would overstate what a format
    # actually renders whenever front_*.md files exist on disk. TOTAL_WORDS
    # stays (same format, last line) for existing stdout parsers.
    print(f"BODY_WORDS={body_words}")
    print(f"TOTAL_WORDS={total_words}")
    return summary


def main() -> int:
    args = sys.argv[1:]
    config_path = None
    workspace_arg = None
    forced_version = None
    overwrite = False
    i = 0
    while i < len(args):
        a = args[i]
        if a == "--config":
            config_path = args[i + 1]; i += 2; continue
        if a == "--workspace":
            workspace_arg = args[i + 1]; i += 2; continue
        if a == "--version":
            forced_version = int(args[i + 1]); i += 2; continue
        if a == "--overwrite":
            overwrite = True; i += 1; continue
        i += 1

    if not config_path:
        print("Usage: python assemble_manuscript.py --config book_config.json "
              "[--workspace <dir>] [--version N] [--overwrite]", file=sys.stderr)
        return 2

    assemble(config_path, workspace_arg, forced_version, overwrite)
    return 0


if __name__ == "__main__":
    sys.exit(main())
