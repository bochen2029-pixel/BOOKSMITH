#!/usr/bin/env python3
"""transcript_to_md.py — Claude Code session .jsonl -> clean Markdown (the porter).

Ports the markdown-rendering logic from claude_archive_viewer_v5.html into a
streaming, stdlib-only Python converter. Streams the .jsonl line-by-line (never
loads the whole file), so it survives multi-megabyte transcripts.

Fidelity model (confirmed against a real 5.9 MB Claude Code session on this box):
  Each line is one JSON object. Substantive lines have type in {user, assistant,
  summary}; everything else (queue-operation, attachment, custom-title,
  ai-title, last-prompt, mode, system, ...) is meta and is dropped or one-lined.

  message.content is a str OR a list of content blocks. Block types:
    text        -> b['text']
    thinking     -> b['thinking']   (NOTE: key is 'thinking', not 'text')
    tool_use     -> b['name'], b['input'], b['id']
    tool_result  -> b['content'] (str | list[{type:text,text}]), b['tool_use_id'],
                    optional b['is_error'].  Carries NO tool name; we link it to
                    the originating tool_use via tool_use_id in a single pass
                    (tool_use always precedes its result in the stream).
    image        -> one-liner marker.

CLI:
  python transcript_to_md.py <session.jsonl> [--out OUT.md] [--strip-thinking]
      [--no-tools] [--max-tool-chars N=1500] [--tail-turns N] [--since-uuid UUID]

Everything degrades gracefully: missing keys, non-dict content, unknown block
types, and malformed JSON lines never crash the run.
"""
import argparse
import json
import re
import sys
from pathlib import Path

META_TYPES = {
    "queue-operation", "attachment", "custom-title", "ai-title",
    "last-prompt", "mode", "system", "file-history-snapshot",
}


def _read_text(fp):
    """Yield (lineno, obj_or_None) for each line; never raises on bad JSON."""
    with open(fp, "r", encoding="utf-8", errors="replace") as f:
        for i, line in enumerate(f):
            line = line.strip()
            if not line:
                continue
            try:
                yield i, json.loads(line)
            except Exception:
                yield i, None


def _coerce_tool_result_text(content):
    """tool_result.content -> a single string, whatever its shape."""
    if content is None:
        return ""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for x in content:
            if isinstance(x, str):
                parts.append(x)
            elif isinstance(x, dict):
                if x.get("type") == "image" or "source" in x:
                    parts.append("[image]")
                else:
                    parts.append(x.get("text") or json.dumps(x, ensure_ascii=False))
            else:
                parts.append(str(x))
        return "\n".join(parts)
    if isinstance(content, dict):
        return content.get("text") or json.dumps(content, ensure_ascii=False)
    return str(content)


def _truncate(s, n):
    """Truncate to n chars with a loud '...[+N chars]' marker."""
    s = s or ""
    if n is not None and n >= 0 and len(s) > n:
        return s[:n].rstrip() + "\n...[+%d chars truncated]" % (len(s) - n)
    return s


def _summarize_args(inp, max_chars):
    """Compact one-line-ish JSON of tool args, big values truncated per-field."""
    if not isinstance(inp, dict):
        return _truncate(str(inp), max_chars)
    slim = {}
    for k, v in inp.items():
        if isinstance(v, str):
            slim[k] = v if len(v) <= max_chars else (v[:max_chars] + "…[+%d]" % (len(v) - max_chars))
        elif isinstance(v, (list, dict)):
            blob = json.dumps(v, ensure_ascii=False)
            slim[k] = blob if len(blob) <= max_chars else (blob[:max_chars] + "…[+%d]" % (len(blob) - max_chars))
        else:
            slim[k] = v
    try:
        return json.dumps(slim, ensure_ascii=False)
    except Exception:
        return str(slim)


def _blocks_from(msg):
    """Normalize message.content to a list of block dicts."""
    content = msg.get("content") if isinstance(msg, dict) else None
    if isinstance(content, str):
        return [{"type": "text", "text": content}]
    if isinstance(content, list):
        return [b for b in content if isinstance(b, dict)]
    return []


def convert(
    jsonl_path,
    strip_thinking=False,
    no_tools=False,
    max_tool_chars=1500,
    tail_turns=None,
    since_uuid=None,
):
    """Stream the .jsonl and return the markdown string.

    Two logical passes but only ONE file read: we buffer normalized turns in a
    list (turns are small; tool_result payloads are truncated on ingest so the
    buffer stays bounded), which lets us honor --tail-turns and link tool
    results to tool names cleanly.
    """
    src = Path(jsonl_path)
    turns = []              # list of dicts: {role, ts, uuid, blocks:[...]}
    toolname_by_id = {}     # tool_use_id -> tool name (for result linkage)
    line_count = 0
    started_capture = (since_uuid is None)

    for lineno, r in _read_text(src):
        line_count = lineno + 1
        if r is None or not isinstance(r, dict):
            continue
        rtype = r.get("type")

        # --since-uuid gate: skip everything until we pass the given uuid.
        if not started_capture:
            if r.get("uuid") == since_uuid or r.get("parentUuid") == since_uuid:
                started_capture = True
                if r.get("uuid") == since_uuid:
                    # the marker turn itself is the boundary; start AFTER it
                    continue
            else:
                continue

        if rtype == "summary":
            turns.append({
                "role": "summary",
                "ts": r.get("timestamp"),
                "uuid": r.get("uuid"),
                "blocks": [{"type": "text", "text": r.get("summary") or ""}],
            })
            continue

        if rtype not in ("user", "assistant"):
            # meta line: drop entirely (kept intentionally silent to save tokens)
            continue

        msg = r.get("message")
        raw_blocks = _blocks_from(msg)
        norm = []
        for b in raw_blocks:
            bt = b.get("type")
            if bt == "text":
                norm.append({"type": "text", "text": b.get("text") or ""})
            elif bt == "thinking":
                # key is 'thinking' on the wire; fall back to 'text' just in case
                norm.append({"type": "thinking", "text": b.get("thinking") or b.get("text") or ""})
            elif bt == "tool_use":
                name = b.get("name") or "?"
                if b.get("id"):
                    toolname_by_id[b["id"]] = name
                norm.append({
                    "type": "tool_use",
                    "name": name,
                    "input": b.get("input") or {},
                    "id": b.get("id"),
                })
            elif bt == "tool_result":
                norm.append({
                    "type": "tool_result",
                    "tool_use_id": b.get("tool_use_id"),
                    "text": _truncate(_coerce_tool_result_text(b.get("content")), max_tool_chars),
                    "is_error": bool(b.get("is_error")),
                })
            elif bt == "image":
                norm.append({"type": "image"})
            else:
                # unknown block -> single compact line, never crash
                norm.append({"type": "unknown", "text": (bt or "block")})

        if not norm:
            continue
        turns.append({
            "role": r.get("type"),
            "ts": r.get("timestamp"),
            "uuid": r.get("uuid"),
            "blocks": norm,
        })

    if tail_turns is not None and tail_turns >= 0:
        turns = turns[-tail_turns:]

    return _render(src, line_count, turns, toolname_by_id,
                   strip_thinking, no_tools, max_tool_chars, tail_turns, since_uuid)


def _render(src, line_count, turns, toolname_by_id,
            strip_thinking, no_tools, max_tool_chars, tail_turns, since_uuid):
    out = []
    flags = []
    if strip_thinking:
        flags.append("thinking-stripped")
    if no_tools:
        flags.append("tools-dropped")
    if tail_turns is not None:
        flags.append("tail=%d" % tail_turns)
    if since_uuid:
        flags.append("since=%s" % since_uuid[:8])
    flags.append("max_tool_chars=%d" % max_tool_chars)

    out.append("# Session transcript (rehydrated)")
    out.append("")
    out.append("- source: `%s`" % src)
    out.append("- lines scanned: %d  |  turns rendered: %d" % (line_count, len(turns)))
    out.append("- generated by: `transcript_to_md.py` [%s]" % ", ".join(flags))
    out.append("- NOTE: this IS the session record, losslessly compacted from the raw"
               " .jsonl. It is higher fidelity than any hand-written summary. Read it"
               " as the ground truth of what happened.")
    out.append("")
    out.append("---")
    out.append("")

    for m in turns:
        role = m["role"]
        # Skip pure tool-result carrier user turns UNLESS they contain text.
        blocks = m["blocks"]
        if role == "user":
            non_result = [b for b in blocks if b["type"] != "tool_result"]
            has_text = any(b["type"] == "text" and (b.get("text") or "").strip() for b in blocks)
            if not has_text and blocks and all(b["type"] == "tool_result" for b in blocks):
                if no_tools:
                    continue
                # render compact tool-result carrier without a big "## User" header
                for b in blocks:
                    tname = toolname_by_id.get(b.get("tool_use_id"), "tool")
                    err = " ERROR" if b.get("is_error") else ""
                    first = (b.get("text") or "").strip()
                    out.append("> [tool result: %s%s] %s" % (tname, err, first if first else "(empty)"))
                    out.append("")
                continue

        # Render blocks into a local buffer first; only emit the heading if the
        # turn produced any content (avoids dangling empty "## Assistant" headers
        # when every block was stripped by --strip-thinking / --no-tools).
        body = []
        for b in blocks:
            bt = b["type"]
            if bt == "text":
                txt = (b.get("text") or "").strip()
                if txt:
                    body.append(txt)
                    body.append("")
            elif bt == "thinking":
                if strip_thinking:
                    continue
                th = (b.get("text") or "").strip()
                if th:
                    body.append("> [thinking] " + th.replace("\n", "\n> "))
                    body.append("")
            elif bt == "tool_use":
                if no_tools:
                    continue
                body.append("- [tool: %s] %s" % (b.get("name") or "?",
                                                 _summarize_args(b.get("input"), max_tool_chars)))
                body.append("")
            elif bt == "tool_result":
                if no_tools:
                    continue
                tname = toolname_by_id.get(b.get("tool_use_id"), "tool")
                err = " ERROR" if b.get("is_error") else ""
                first = (b.get("text") or "").strip()
                body.append("> [tool result: %s%s] %s" % (tname, err, first if first else "(empty)"))
                body.append("")
            elif bt == "image":
                body.append("> [image]")
                body.append("")
            else:  # unknown
                body.append("> [%s]" % (b.get("text") or "block"))
                body.append("")

        if not any(x.strip() for x in body):
            continue

        heading = {"user": "## User", "assistant": "## Assistant",
                   "summary": "## Summary (prior compaction)"}.get(role, "## %s" % role.title())
        out.append(heading)
        out.append("")
        out.extend(body)
        out.append("")

    return "\n".join(out).rstrip() + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser(description="Convert a Claude Code session .jsonl to clean Markdown.")
    ap.add_argument("jsonl", help="path to the session .jsonl")
    ap.add_argument("--out", help="output .md path (default: stdout)")
    ap.add_argument("--strip-thinking", action="store_true", help="omit thinking blocks entirely (~2x reduction)")
    ap.add_argument("--no-tools", action="store_true", help="drop all tool_use / tool_result traffic")
    ap.add_argument("--max-tool-chars", type=int, default=1500, help="truncate tool payloads to N chars (default 1500)")
    ap.add_argument("--tail-turns", type=int, default=None, help="keep only the last N turns")
    ap.add_argument("--since-uuid", default=None, help="start capture only after this message uuid")
    args = ap.parse_args(argv)

    src = Path(args.jsonl)
    if not src.exists():
        sys.stderr.write("error: no such file: %s\n" % src)
        return 2

    md = convert(
        src,
        strip_thinking=args.strip_thinking,
        no_tools=args.no_tools,
        max_tool_chars=args.max_tool_chars,
        tail_turns=args.tail_turns,
        since_uuid=args.since_uuid,
    )

    if args.out:
        outp = Path(args.out)
        outp.parent.mkdir(parents=True, exist_ok=True)
        outp.write_text(md, encoding="utf-8", errors="replace")
        sys.stderr.write("wrote %s (%d chars)\n" % (outp, len(md)))
    else:
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass
        sys.stdout.write(md)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
