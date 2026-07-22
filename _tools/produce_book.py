#!/usr/bin/env python3
"""
produce_book.py - the deterministic production orchestrator.

Turns "a mind runs 15 commands in the right order and remembers the gotchas"
into one reproducible command. Everything here is deterministic given approved
markdown + config + a cover design + illustrations on disk; it invents nothing.
It codifies CLAUDE.md section 12 (the canonical build order) plus the fixes this
book's production learned: the vAlign re-inject is ALWAYS run standalone (it
does not always stick from the generator's inline pass), and the digital +
website PDF assembly is folded in here instead of living in a temp script.

What it does NOT do (these need a mind, not this script): write prose, place a
new unit, brief or pick illustrations, design a cover, or diagnose a gate
failure. It stops loudly on any pre-gate failure and reports per-format verify
verdicts; it does not paper over red.

Chain per format:
  pre-gates: scan_manuscript.py  +  lint_manuscript.py (skippable for zh)
  assemble_manuscript.py  ->  outputs/markdown/<slug>_vN.md
  print (kdp_hardcover|mixam_hardcover):
    generate_book.js --format F
      -> inject_mirror_margins.js (idempotent)  -> inject_front_matter_valign.js (ALWAYS)
      -> docx_to_pdf.py [--pad-multiple 4 for mixam]  (reads page count)
      -> cover_compose_ahss.py --profile {kdp|mixam} --pages N
      -> verify_build.py --format F --final
  kindle:
    generate_kindle.js -> cover_compose_ahss.py --profile kindle -> verify_build.py --format kindle
  digital / website (built from a chosen print interior PDF):
    cover_compose_ahss.py --profile digital
      -> digital : front + blank-stripped interior + back
      -> website : front + back + interior with ALL blank pages dropped

Usage:
  python produce_book.py --config CFG [--formats kdp_hardcover,kindle,digital,website]
      [--back back_copy.json] [--interior-for-digital kdp_hardcover]
      [--skip-lint] [--dry-run] [--json]
Exit: 0 all green - 1 any gate/verify FAIL - 2 usage / setup error.
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
PY = sys.executable
NODE = "node"

COVER_PROFILE = {"kdp_hardcover": "kdp", "mixam_hardcover": "mixam", "kindle": "kindle"}
PRINT_FORMATS = ("kdp_hardcover", "mixam_hardcover")


def run(cmd, capture=True):
    """Run a command (list). Returns (rc, stdout, stderr)."""
    p = subprocess.run(cmd, capture_output=capture, text=True)
    return p.returncode, (p.stdout or ""), (p.stderr or "")


def last_json(s):
    """Parse the last JSON object printed on stdout (tools print JSON last)."""
    for line in reversed([l for l in s.splitlines() if l.strip()]):
        line = line.strip()
        if line.startswith("{"):
            try:
                return json.loads(line)
            except Exception:
                continue
    return None


class Runner:
    def __init__(self, dry):
        self.dry = dry
        self.log = []

    def step(self, label, cmd, parse=False):
        self.log.append(label)
        printable = " ".join(str(c) for c in cmd)
        if self.dry:
            print(f"  DRY  {label}\n       {printable}")
            return 0, "", ""
        print(f"  ...  {label}", flush=True)
        rc, out, err = run(cmd)
        if rc != 0:
            print(f"  FAIL {label} (rc={rc})\n{(err or out)[-600:]}")
        return rc, out, err


def find_one(directory: Path, suffix: str):
    c = sorted(directory.glob(f"*{suffix}"))
    return c[0] if c else None


def build_digital(ws, slug, comp_dir, interior_pdf, out_dir, dry):
    """front + stripped-interior + back  AND  front + back + no-blank interior."""
    if dry:
        print(f"  DRY  digital+website from {interior_pdf.name} via PyMuPDF")
        return {"digital": None, "website": None, "dry": True}
    import fitz
    out_dir.mkdir(parents=True, exist_ok=True)
    front = fitz.open(str(comp_dir / "front_digital.pdf"))
    back = fitz.open(str(comp_dir / "back_digital.pdf"))
    src = fitz.open(str(interior_pdf))
    keep = [i for i in range(src.page_count)
            if len(src.load_page(i).get_text().strip()) >= 3 or src.load_page(i).get_images()]

    # DIGITAL: front + blank-stripped interior + back
    dig = fitz.open()
    dig.insert_pdf(front)
    inter = fitz.open()
    for i in keep:
        inter.insert_pdf(src, from_page=i, to_page=i)
    dig.insert_pdf(inter)
    dig.insert_pdf(back)
    dpath = out_dir / f"{slug}_DIGITAL.pdf"
    dig.save(str(dpath), garbage=4, deflate=True)
    dpages = dig.page_count

    # WEBSITE: front + back + interior (all blanks dropped)
    web = fitz.open()
    web.insert_pdf(front)
    web.insert_pdf(back)
    web.insert_pdf(inter)
    wpath = out_dir / f"{slug}_WEBSITE.pdf"
    web.save(str(wpath), garbage=4, deflate=True)
    wpages = web.page_count
    # verify zero blanks in website
    v = fitz.open(str(wpath))
    blanks = [i + 1 for i in range(v.page_count)
              if len(v.load_page(i).get_text().strip()) < 3 and not v.load_page(i).get_images()]
    for d in (front, back, src, dig, inter, web, v):
        d.close()
    return {"digital": str(dpath), "digital_pages": dpages,
            "website": str(wpath), "website_pages": wpages,
            "website_blanks_remaining": blanks}


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    ap.add_argument("--formats", default=None,
                    help="comma list of kdp_hardcover,mixam_hardcover,kindle,digital,website")
    ap.add_argument("--back", default=None)
    ap.add_argument("--interior-for-digital", default=None)
    ap.add_argument("--skip-lint", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    cfgp = Path(a.config).resolve()
    if not cfgp.exists():
        print(f"config not found: {cfgp}", file=sys.stderr)
        return 2
    cfg = json.loads(cfgp.read_text(encoding="utf-8"))
    ws = cfgp.parent
    slug = cfg.get("slug", "book")
    back = Path(a.back) if a.back else ws / "cover_art" / "back_copy.json"

    formats = ([f.strip() for f in a.formats.split(",") if f.strip()] if a.formats
               else list(cfg.get("formats", [])) + ["digital", "website"])
    print_fmts = [f for f in formats if f in PRINT_FORMATS]
    do_kindle = "kindle" in formats
    do_digital = "digital" in formats or "website" in formats
    interior_fmt = (a.interior_for_digital or
                    ("kdp_hardcover" if "kdp_hardcover" in print_fmts else
                     ("mixam_hardcover" if "mixam_hardcover" in print_fmts else None)))

    R = Runner(a.dry_run)
    result = {"config": str(cfgp), "formats": formats, "steps": {}, "green": True}

    # --- pre-gates -------------------------------------------------------------
    rc, out, _ = R.step("scan_manuscript", [PY, str(TOOLS / "scan_manuscript.py"),
                                            "--config", str(cfgp)])
    if rc != 0 and not a.dry_run:
        print("HALT: manuscript scan failed. Fix content before producing.")
        return 1
    if not a.skip_lint:
        rc, out, _ = R.step("lint_manuscript", [PY, str(TOOLS / "lint_manuscript.py"),
                                                "--config", str(cfgp)])
        if rc != 0 and not a.dry_run:
            print("HALT: lint failed. Fix content before producing.")
            return 1

    # --- assemble --------------------------------------------------------------
    rc, out, _ = R.step("assemble", [PY, str(TOOLS / "assemble_manuscript.py"),
                                     "--config", str(cfgp)])
    if rc != 0 and not a.dry_run:
        return 1
    asm = last_json(out) if out else None
    result["body_words"] = asm.get("body_words") if asm else None

    # --- print formats ---------------------------------------------------------
    for fmt in print_fmts:
        info = {}
        outdir = ws / "outputs" / fmt
        R.step(f"generate {fmt}", [NODE, str(TOOLS / "generate_book.js"),
                                   "--config", str(cfgp), "--format", fmt])
        docx = None if a.dry_run else find_one(outdir, ".docx")
        if not a.dry_run and not docx:
            info["error"] = "no docx produced"
            result["green"] = False
            result["steps"][fmt] = info
            continue
        docx = docx or (outdir / f"{slug}_{fmt.upper()}.docx")
        R.step(f"inject mirror {fmt}", [NODE, str(TOOLS / "inject_mirror_margins.js"), str(docx)])
        R.step(f"inject vAlign {fmt}", [NODE, str(TOOLS / "inject_front_matter_valign.js"), str(docx)])
        pdf = docx.with_suffix(".pdf")
        cmd = [PY, str(TOOLS / "docx_to_pdf.py"), str(docx), str(pdf)]
        if fmt == "mixam_hardcover":
            cmd += ["--pad-multiple", "4"]
        rc, out, _ = R.step(f"render pdf {fmt}", cmd)
        pj = last_json(out) if out else None
        pages = pj.get("pages") if pj else None
        info["pages"] = pages
        if pages:
            R.step(f"cover {fmt}", [PY, str(TOOLS / "cover_compose_ahss.py"),
                                    "--config", str(cfgp), "--back", str(back),
                                    "--pages", str(pages), "--profile", COVER_PROFILE[fmt],
                                    "--out", str(outdir)])
        rc, out, _ = R.step(f"verify {fmt}", [PY, str(TOOLS / "verify_build.py"),
                                              "--config", str(cfgp), "--format", fmt, "--final"])
        vj = last_json(out) if out else None
        info["verify_all_pass"] = (vj.get("all_pass") if vj else None)
        if info.get("verify_all_pass") is False:
            result["green"] = False
        result["steps"][fmt] = info

    # --- kindle ----------------------------------------------------------------
    if do_kindle:
        info = {}
        outdir = ws / "outputs" / "kindle"
        R.step("generate kindle", [NODE, str(TOOLS / "generate_kindle.js"), "--config", str(cfgp)])
        pages_ref = next((result["steps"][f].get("pages") for f in print_fmts
                          if result["steps"].get(f, {}).get("pages")), 100)
        R.step("cover kindle", [PY, str(TOOLS / "cover_compose_ahss.py"),
                                "--config", str(cfgp), "--back", str(back),
                                "--pages", str(pages_ref or 100), "--profile", "kindle",
                                "--out", str(outdir)])
        rc, out, _ = R.step("verify kindle", [PY, str(TOOLS / "verify_build.py"),
                                              "--config", str(cfgp), "--format", "kindle"])
        vj = last_json(out) if out else None
        info["verify_all_pass"] = (vj.get("all_pass") if vj else None)
        if info.get("verify_all_pass") is False:
            result["green"] = False
        result["steps"]["kindle"] = info

    # --- digital + website -----------------------------------------------------
    if do_digital:
        if not interior_fmt:
            print("digital/website requested but no print interior available to build from.")
            result["green"] = False
        else:
            comp = ws / "cover_art" / "composed"
            lang = (json.load(open(cfgp, encoding="utf-8")).get("language") or "en")
            R.step("cover digital", [PY, str(TOOLS / "cover_compose_ahss.py"),
                                     "--config", str(cfgp), "--back", str(back),
                                     "--pages", "1", "--profile", "digital",
                                     "--lang", lang, "--out", str(comp)])
            interior_pdf = None if a.dry_run else find_one(ws / "outputs" / interior_fmt, ".pdf")
            if not a.dry_run and not interior_pdf:
                print(f"no interior PDF in outputs/{interior_fmt} to build digital from.")
                result["green"] = False
            else:
                d = build_digital(ws, slug, comp, interior_pdf or Path("x"),
                                  ws / "outputs" / "digital", a.dry_run)
                result["steps"]["digital_website"] = d
                if d.get("website_blanks_remaining"):
                    result["green"] = False

    # --- report ----------------------------------------------------------------
    if a.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print("\n==== PRODUCTION SUMMARY ====")
        print(f"body words: {result.get('body_words')}")
        for fmt, info in result["steps"].items():
            print(f"  {fmt}: {json.dumps(info, ensure_ascii=False)}")
        print(f"GREEN: {result['green']}" + ("  (dry-run)" if a.dry_run else ""))
    return 0 if result["green"] else 1


if __name__ == "__main__":
    sys.exit(main())
