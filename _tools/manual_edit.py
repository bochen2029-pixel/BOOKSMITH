#!/usr/bin/env python3
"""manual_edit.py — the human's own pen: get/put a unit's body for direct editing.

H0 (cloud/PLAN_H0_2026-08-24.md §0.3): the reader can open a chapter and edit the
words themselves — not everything is a prompt. This tool is the ONLY sanctioned
write path for a human edit, and it holds the kit's laws while being friendly:

  * the H1 title line is LOCKED (config units[].title is the identity the gates
    byte-match); `get` strips it, `put` re-attaches it — the editor never sees it.
  * photo lines are PROTECTED: a save that deletes or mangles an image reference
    is refused with a friendly message (nothing is lost; the draft text is kept
    by the caller). Moving a photo line is allowed; losing it is not.
  * append-only: the PRIOR current is preserved as manuscript/drafts/
    {uid}_v{N}_human_base.md and the new text ALSO lands as {uid}_v{N}_human.md
    before atomically becoming current — the kit's version law, kept.
  * every save writes an authorship-ledger row (actor=human) so lint knows this
    unit now carries human voice (advisory, not gated) and the passport knows
    who wrote what.

The engine deliberately never sees this tool: a human-edited current file leaves
draft:<unit> satisfied (outputs exist) while making assemble/produce stale by
hash — so `engine.py --from integrate` rebuilds the book WITHOUT redrafting
anyone's words. (Never run a bare engine pass after manual edits: the prior-prose
input hash would mark DOWNSTREAM units stale and redraft over them. The cloud
shim's rebuild/revise verbs are targeted for exactly this reason.)

CLI (JSON on stdout; exit 0 ok / 1 refused / 2 usage):
  python _tools/manual_edit.py get --config CFG --unit UID
  python _tools/manual_edit.py put --config CFG --unit UID --body-file F [--note "..."]
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from authorship_ledger import append_row  # noqa: E402

IMG_RE = re.compile(r"!\[[^\]]*\]\(([^)\s]+)\)")
TEMPLATE_TOKEN_RE = re.compile(r"\{\{[^{}\n]*\}\}")
MAX_BODY = 2 * 1024 * 1024  # 2 MB of markdown is far beyond any real chapter


def _die(msg: str, code: int = 1) -> int:
    print(json.dumps({"ok": False, "error": msg}, ensure_ascii=False))
    return code


def _load(config: str):
    cfg_path = Path(config).resolve()
    cfg = json.loads(cfg_path.read_text("utf-8"))
    ws = cfg_path.parent
    return cfg, ws


def _unit_title(cfg: dict, uid: str) -> str | None:
    for u in cfg.get("units", []):
        if u.get("id") == uid:
            return str(u.get("title") or uid)
    return None


def _split_h1(text: str, title: str) -> tuple[str, str]:
    """Return (h1_line, body_without_h1). Tolerates a missing/odd H1."""
    lines = text.split("\n")
    if lines and lines[0].startswith("# "):
        h1 = lines[0]
        rest = "\n".join(lines[1:]).lstrip("\n")
        return h1, rest
    return f"# {title}", text.lstrip("\n")


def _image_paths(text: str) -> list[str]:
    return IMG_RE.findall(text)


def cmd_get(args) -> int:
    cfg, ws = _load(args.config)
    title = _unit_title(cfg, args.unit)
    if title is None:
        return _die(f"unknown unit: {args.unit}")
    cur = ws / "manuscript" / "current" / f"{args.unit}_current.md"
    if not cur.exists():
        return _die(f"no current draft for {args.unit}")
    text = cur.read_text("utf-8")
    _h1, body = _split_h1(text, title)
    print(json.dumps({
        "ok": True, "unit": args.unit, "title": title, "body": body,
        "images": _image_paths(body),
        "note": "the chapter title is fixed here; photo lines must stay (they may move)",
    }, ensure_ascii=False))
    return 0


def cmd_put(args) -> int:
    cfg, ws = _load(args.config)
    title = _unit_title(cfg, args.unit)
    if title is None:
        return _die(f"unknown unit: {args.unit}")
    cur = ws / "manuscript" / "current" / f"{args.unit}_current.md"
    if not cur.exists():
        return _die(f"no current draft for {args.unit}")

    raw = Path(args.body_file).read_bytes()
    if len(raw) > MAX_BODY:
        return _die("that chapter is too large to save (2 MB limit)")
    try:
        body = raw.decode("utf-8")
    except UnicodeDecodeError:
        return _die("the text could not be read as UTF-8")
    body = body.replace("\r\n", "\n").replace("\r", "\n").strip("\n")

    # -- guards (friendly, specific; nothing is lost on refusal) -----------
    if TEMPLATE_TOKEN_RE.search(body):
        return _die("the text contains {{template}} markers; please remove them")
    for ln in body.split("\n"):
        if ln.startswith("# ") and not ln.startswith("## "):
            return _die("chapter titles are managed for you; please remove the "
                        "line starting with '# ' (your text is safe, nothing was saved)")

    old_text = cur.read_text("utf-8")
    _h1, old_body = _split_h1(old_text, title)
    old_imgs, new_imgs = _image_paths(old_body), _image_paths(body)
    missing = [p for p in old_imgs if p not in new_imgs]
    if missing:
        return _die("these photo lines went missing or changed; photos can move "
                    f"but must be kept exactly as written: {missing[:5]}")

    new_text = f"# {title}\n\n{body}\n"
    if new_text == old_text:
        print(json.dumps({"ok": True, "unit": args.unit, "changed": False,
                          "note": "no change"}, ensure_ascii=False))
        return 0

    # -- append-only versioning (the kit's law) ----------------------------
    drafts = ws / "manuscript" / "drafts"
    drafts.mkdir(parents=True, exist_ok=True)
    n = 1
    existing = {p.name for p in drafts.glob(f"{args.unit}_v*")}
    while (f"{args.unit}_v{n}_human.md" in existing
           or f"{args.unit}_v{n}_human_base.md" in existing
           or f"{args.unit}_v{n}.md" in existing):
        n += 1
    (drafts / f"{args.unit}_v{n}_human_base.md").write_text(old_text, "utf-8", newline="\n")
    (drafts / f"{args.unit}_v{n}_human.md").write_text(new_text, "utf-8", newline="\n")

    tmp = cur.with_name(f".{cur.name}.tmp{os.getpid()}")
    tmp.write_text(new_text, encoding="utf-8", newline="\n")
    os.replace(tmp, cur)

    row = append_row(ws, args.unit, "human", args.verb or "web-edit",
                     old_text, new_text, args.note or "")
    print(json.dumps({
        "ok": True, "unit": args.unit, "changed": True, "version": n,
        "added_lines": row["added_lines"], "removed_lines": row["removed_lines"],
        "formats_stale": True,
        "rebuild_hint": "engine.py --from integrate  (never a bare run after manual edits)",
    }, ensure_ascii=False))
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    g = sub.add_parser("get")
    g.add_argument("--config", required=True)
    g.add_argument("--unit", required=True)
    p = sub.add_parser("put")
    p.add_argument("--config", required=True)
    p.add_argument("--unit", required=True)
    p.add_argument("--body-file", required=True)
    p.add_argument("--note", default="")
    p.add_argument("--verb", default="web-edit")
    args = ap.parse_args(argv)
    try:
        return cmd_get(args) if args.cmd == "get" else cmd_put(args)
    except FileNotFoundError as e:
        return _die(f"missing file: {e}")
    except json.JSONDecodeError as e:
        return _die(f"config unreadable: {e}")


if __name__ == "__main__":
    sys.exit(main())
