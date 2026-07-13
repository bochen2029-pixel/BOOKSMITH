#!/usr/bin/env python3
r"""
produce_course.py — assemble drafted lessons into a course (BOOKSMITH domain: course).

The 'course' domain producer (roadmap #10 proof that the deterministic engine is domain-
general). Reads the drafted lessons in manuscript/current/<id>_current.md plus the units
(with an optional 'module' grouping) from the course config, and emits one of:

  --target course_md    -> outputs/course/<slug>_COURSE.md    (modules -> lessons, readable)
  --target course_json  -> outputs/course/<slug>_course.json  (structured: modules/lessons/words)

The engine calls this per produce target it declares in domains/course/domain.json.
stdlib only.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


def load(cfg_path: str):
    cfg = json.loads(Path(cfg_path).read_text(encoding="utf-8"))
    return cfg, Path(cfg_path).parent


def read_lessons(cfg: dict, ws: Path) -> list[dict]:
    out = []
    for u in cfg.get("units", []):
        p = ws / "manuscript" / "current" / f"{u['id']}_current.md"
        body = p.read_text(encoding="utf-8", errors="replace") if p.exists() else ""
        out.append({
            "id": u["id"], "title": u.get("title", u["id"]),
            "module": u.get("module", "Course"),
            "words": len(re.findall(r"\S+", body)), "body": body.strip(),
        })
    return out


def build_md(cfg: dict, lessons: list[dict]) -> str:
    lines = [f"# {cfg.get('title', 'Course')}", ""]
    if cfg.get("author"):
        lines += [f"*by {cfg['author']}*", ""]
    current_mod = None
    for les in lessons:
        if les["module"] != current_mod:
            current_mod = les["module"]
            lines += [f"## Module: {current_mod}", ""]
        lines += [les["body"], ""]
    return "\n".join(lines).strip() + "\n"


def build_json(cfg: dict, lessons: list[dict]) -> dict:
    modules: list[dict] = []
    by_mod: dict[str, list] = {}
    order: list[str] = []
    for les in lessons:
        if les["module"] not in by_mod:
            by_mod[les["module"]] = []
            order.append(les["module"])
        by_mod[les["module"]].append({"id": les["id"], "title": les["title"], "words": les["words"]})
    for m in order:
        modules.append({"module": m, "lessons": by_mod[m]})
    return {
        "course": cfg.get("title"), "author": cfg.get("author"), "slug": cfg.get("slug"),
        "modules": modules, "total_modules": len(modules),
        "total_lessons": len(lessons), "total_words": sum(x["words"] for x in lessons),
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Assemble drafted lessons into a course.")
    ap.add_argument("--config", required=True)
    ap.add_argument("--target", required=True, choices=["course_md", "course_json"])
    args = ap.parse_args(argv)

    cfg, ws = load(args.config)
    lessons = read_lessons(cfg, ws)
    outdir = ws / "outputs" / "course"
    outdir.mkdir(parents=True, exist_ok=True)
    slug = cfg.get("slug", "course")

    if args.target == "course_md":
        out = outdir / f"{slug}_COURSE.md"
        out.write_text(build_md(cfg, lessons), encoding="utf-8")
    else:
        out = outdir / f"{slug}_course.json"
        out.write_text(json.dumps(build_json(cfg, lessons), indent=2, ensure_ascii=False), encoding="utf-8")

    print(json.dumps({"target": args.target, "out": str(out), "lessons": len(lessons)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
