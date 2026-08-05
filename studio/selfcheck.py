#!/usr/bin/env python3
r"""
selfcheck.py — cheap pre-flight for the Studio's own sources.

Born from a real cost: a single missing ")" in app.js shipped a page that
rendered "Loading BOOKSMITH Studio…" forever, with no console error visible
through the automation surface and a cached copy that survived a restart. A
browser is a terrible syntax checker; node and ast are excellent ones.

    python studio/selfcheck.py        # exit 0 clean / 1 broken

Checks: every studio/*.py parses; studio/web/app.js passes `node --check`;
the prompt file exists; the op catalog and the chat's op subset agree.
"""
from __future__ import annotations

import ast
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
fails: list[str] = []


def check(ok: bool, label: str, detail: str = "") -> None:
    print(("  OK  " if ok else "  BAD ") + label + (f"  <- {detail}" if detail and not ok else ""))
    if not ok:
        fails.append(f"{label}: {detail}")


print("studio selfcheck")
for p in sorted(HERE.glob("*.py")):
    try:
        ast.parse(p.read_text(encoding="utf-8"), str(p))
        check(True, f"python parses: {p.name}")
    except SyntaxError as e:
        check(False, f"python parses: {p.name}", f"line {e.lineno}: {e.msg}")

for jsname in ("app.js", "conductor.js", "i18n.js"):
    js = HERE / "web" / jsname
    if not js.is_file():
        check(False, f"web/{jsname} exists")
    elif shutil.which("node"):
        r = subprocess.run(["node", "--check", str(js)], capture_output=True, text=True)
        check(r.returncode == 0, f"node --check web/{jsname}",
              (r.stderr or "").strip().splitlines()[:3] and
              " / ".join((r.stderr or "").strip().splitlines()[:3]))
    else:
        print("  --   node absent; skipping the JS syntax gate")

# S6 vocabulary gate: the Conductor is the plain-language face, so no engine
# jargon may appear in any string a reader could see. Mechanical version of
# the invariant: scan conductor.js string literals that LOOK like display
# text (contain a space); token/URL literals pass untouched; a line carrying
# a "jargon-ok" marker is exempt (API values, not display).
import re as _re
_FORBID = _re.compile(
    r"\b(stale|reconverge|hard[ -]?stops?|hardstops?|blast\s+radius|nonce|"
    r"proposals?|backends?|subprocess(es)?|stages?|gate[sd]?)\b", _re.I)
_LIT = _re.compile(r'"((?:[^"\\\n]|\\.)*)"|\'((?:[^\'\\\n]|\\.)*)\'|`((?:[^`\\]|\\.)*)`')
cond = HERE / "web" / "conductor.js"
if cond.is_file():
    hits = []
    for n, line in enumerate(cond.read_text(encoding="utf-8").splitlines(), 1):
        if "jargon-ok" in line:
            continue
        for m in _LIT.finditer(line):
            lit = next(g for g in m.groups() if g is not None)
            if " " not in lit:
                continue                      # token/URL literal, not display text
            hit = _FORBID.search(lit)
            if hit:
                hits.append(f"line {n}: {hit.group(0)!r} in {lit[:60]!r}")
    check(not hits, "conductor speaks plain language (no engine jargon in display strings)",
          " | ".join(hits[:4]))

for page in ("index.html", "pro.html"):
    check((HERE / "web" / page).is_file(), f"web/{page} present")
check((HERE / "reference_config.json").is_file(), "reference_config.json vendored (new-book fallback)")
check((HERE / "prompts" / "compiler.md").is_file(), "prompts/compiler.md present")

sys.path.insert(0, str(HERE))
try:
    import chat
    import ops
    missing = [o for o in chat.CHAT_OPS if o not in ops.OPS]
    check(not missing, "every chat op exists in the ops catalog", ", ".join(missing))
    no_pred = [k for k, v in ops.OPS.items() if "predict" not in v or "exec" not in v]
    check(not no_pred, "every op declares exec + predict", ", ".join(no_pred))
    bad_risk = [k for k, v in ops.OPS.items() if v.get("risk") not in ("SAFE", "CONTENT")]
    check(not bad_risk, "every op declares a known risk class", ", ".join(bad_risk))
except Exception as e:                                            # noqa: BLE001
    check(False, "ops/chat import", f"{type(e).__name__}: {e}")

print()
if fails:
    print(f"STUDIO SELFCHECK: FAIL ({len(fails)})")
    for f in fails:
        print("  - " + f)
    raise SystemExit(1)
print("STUDIO SELFCHECK: PASS")
