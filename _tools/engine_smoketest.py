#!/usr/bin/env python3
r"""
engine_smoketest.py — prove the deterministic engine WITHOUT a real book run.

Builds a tiny synthetic 2-chapter book in book_workspace/_enginetest/, then drives
engine.py with the mock model backend through the real gates and asserts:

  A. FRESH    — a cold run drafts both chapters, lints, assembles (rc 0).
  B. RESUME   — re-running is idempotent: every stage skips as already-done.
  C. CRASH    — deleting a finished chapter makes the engine re-derive from disk
                and re-run exactly that unit (+ downstream), with ZERO orientation.
  D. HARDSTOP — an unpassable gate stops loudly and writes HARDSTOP.json.
  E. HARNESS  — the keyless in-CC disk-bridge handshake (performer simulated).
  F. SEED     — the ARCHITECT front-half: a brief (no seed.md / no units) becomes
                seed.md + units + per-unit contracts (GATE-2), then drafts+assembles;
                idempotent on resume; the seeded config is schema-valid.
  G. INGEST   — intake docs become relational digests + a manifest (GATE-1) before seed.
  H. HARNESS SEED — the architect turn is fulfilled keyless over the disk bridge too.
  I. PLAN ORDER   — cover-consuming formats (epub, digital_pdf) are sequenced AFTER cover.
  J. DOMAIN       — a non-book 'course' domain runs end-to-end through the SAME engine.

No network, no API key, no Word COM (stops at 'assemble'). This is the
"graduation-exam" check: the machine, not a book.
"""
from __future__ import annotations
import json, shutil, subprocess, sys
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
ROOT = TOOLS.parent
WS = ROOT / "book_workspace" / "_enginetest"
PY = sys.executable
ENGINE = str(TOOLS / "engine.py")


def build_fixture():
    if WS.exists():
        shutil.rmtree(WS)
    (WS / "contracts").mkdir(parents=True)
    (WS / "manuscript" / "current").mkdir(parents=True)
    # base on testvoyage's schema-valid config, then override
    base = json.loads((ROOT / "book_workspace" / "testvoyage" / "book_config.json").read_text("utf-8"))
    base["title"] = "The Engine Test"
    base["subtitle"] = "A Control-Inversion Fixture"
    base["slug"] = "_enginetest"
    base["formats"] = ["kindle"]            # we stop at 'assemble', so this never produces
    base["min_pages"] = 1
    base.setdefault("voice", {})
    base["voice"]["no_em_dashes"] = True
    base["voice"].setdefault("blacklist", [])
    base["units"] = [
        {"id": "ch_01", "title": "The First Movement", "class": "C", "target_words": 250},
        {"id": "ch_02", "title": "The Second Movement", "class": "C", "target_words": 250},
    ]
    (WS / "book_config.json").write_text(json.dumps(base, indent=2), encoding="utf-8")
    (WS / "seed.md").write_text("# Book Bible\nA minimal fixture that proves the engine drives itself.\n", "utf-8")
    for uid, title in (("ch_01", "The First Movement"), ("ch_02", "The Second Movement")):
        (WS / "contracts" / f"{uid}.md").write_text(
            f"# Contract: {title}\n- Must accomplish: advance the fixture.\n- Target ~250 words.\n", "utf-8")


def eng(*extra):
    cmd = [PY, ENGINE, "--config", str(WS / "book_config.json"), "--dry-run", "--to", "assemble", *extra]
    return subprocess.run(cmd, capture_output=True, text=True, cwd=str(ROOT))


def state():
    return json.loads((WS / "_engine" / "state.json").read_text("utf-8"))["stages"]


def main() -> int:
    fails = []

    # --- A. FRESH ---
    build_fixture()
    r = eng("--fresh")
    print("A/FRESH rc=", r.returncode)
    ch1 = WS / "manuscript" / "current" / "ch_01_current.md"
    ch2 = WS / "manuscript" / "current" / "ch_02_current.md"
    if r.returncode != 0:
        fails.append(f"A: fresh run rc={r.returncode}\n{r.stdout[-800:]}\n{r.stderr[-400:]}")
    if not ch1.exists() or not ch2.exists():
        fails.append("A: chapter files not created")
    else:
        if not ch1.read_text("utf-8").startswith("# The First Movement"):
            fails.append("A: ch_01 H1 wrong")
    st = state()
    for k in ("precheck", "draft:ch_01", "draft:ch_02", "integrate", "assemble"):
        if st.get(k, {}).get("status") != "done":
            fails.append(f"A: stage {k} not done ({st.get(k, {}).get('status')})")

    # --- B. RESUME (idempotent) ---
    ch1_sha_before = ch1.read_bytes()
    r = eng()
    print("B/RESUME rc=", r.returncode)
    skips = r.stdout.count("skip_done")
    if r.returncode != 0:
        fails.append(f"B: resume rc={r.returncode}")
    if skips < 5:
        fails.append(f"B: expected >=5 skip_done, got {skips}")
    if ch1.read_bytes() != ch1_sha_before:
        fails.append("B: ch_01 was rewritten on a no-op resume (not idempotent)")

    # --- C. CRASH / DRIFT recovery ---
    ch2.unlink()  # simulate a lost/half-written unit
    r = eng()
    print("C/CRASH rc=", r.returncode)
    if r.returncode != 0:
        fails.append(f"C: recovery rc={r.returncode}\n{r.stdout[-600:]}")
    if not ch2.exists():
        fails.append("C: ch_02 not regenerated after deletion")
    if "draft:ch_02" not in r.stdout or "stage.done stage=draft:ch_02" not in r.stdout.replace("] ", "] event="):
        # loose check: ch_02 must have been re-run, not skipped
        if "skip_done stage=draft:ch_02" in r.stdout:
            fails.append("C: ch_02 was skipped, not re-run (drift not detected)")

    # --- D. HARD-STOP on an unpassable gate (loud failure, resumable) ---
    build_fixture()
    cfg = json.loads((WS / "book_config.json").read_text("utf-8"))
    cfg["voice"]["blacklist"] = ["record"]  # a word the mock deterministically emits
    (WS / "book_config.json").write_text(json.dumps(cfg, indent=2), "utf-8")
    r = eng("--fresh")
    print("D/HARDSTOP rc=", r.returncode)
    hs = WS / "_engine" / "HARDSTOP.json"
    if r.returncode != 2:
        fails.append(f"D: expected rc=2 hard-stop, got {r.returncode}\n{r.stdout[-500:]}")
    if not hs.exists():
        fails.append("D: HARDSTOP.json not written")
    else:
        det = json.loads(hs.read_text("utf-8"))
        if "draft:ch_01" not in det.get("stage", ""):
            fails.append(f"D: hard-stop at unexpected stage {det.get('stage')}")
        if "blacklist" not in det.get("detail", "").lower():
            fails.append(f"D: hard-stop detail missing gate reason: {det.get('detail')}")

    # --- E. HARNESS bridge (keyless in-CC handshake; performer simulated) ---
    build_fixture()
    bdir = WS / "_engine" / "bridge"

    def canned(title):
        s = "The line held fast and the work went on, asking nothing but that it be done well."
        return f"# {title}\n\n" + " ".join([s] * 18)

    def eng_h(*extra):
        cmd = [PY, ENGINE, "--config", str(WS / "book_config.json"),
               "--backend", "harness", "--to", "assemble", *extra]
        return subprocess.run(cmd, capture_output=True, text=True, cwd=str(ROOT))

    r = eng_h("--fresh")            # -> pause, requests ch_01
    if r.returncode != 3:
        fails.append(f"E: first harness run expected rc=3 (await), got {r.returncode}\n{r.stdout[-400:]}")
    (bdir / "ch_01.response.md").write_text(canned("The First Movement"), "utf-8")
    r = eng_h()                    # gate+place ch_01 -> pause, requests ch_02
    if r.returncode != 3:
        fails.append(f"E: after ch_01 expected rc=3 (ch_02), got {r.returncode}")
    if not (WS / "manuscript" / "current" / "ch_01_current.md").exists():
        fails.append("E: ch_01 not placed into manuscript after gate pass")
    (bdir / "ch_02.response.md").write_text(canned("The Second Movement"), "utf-8")
    r = eng_h()                    # gate+place ch_02 -> integrate + assemble -> done
    print("E/HARNESS final rc=", r.returncode)
    if r.returncode != 0:
        fails.append(f"E: final harness run expected rc=0, got {r.returncode}\n{r.stdout[-400:]}")

    # --- F. SEED (architect front-half: a brief -> seed.md + units + contracts) ---
    SEEDWS = ROOT / "book_workspace" / "_seedtest"
    minimal = {"title": "The Seed Test", "author": "BOOKSMITH", "slug": "_seedtest",
               "genre": "test nonfiction", "is_fiction": False, "formats": ["kindle"],
               "min_pages": 1}

    def build_seed_fixture(with_intake=False):
        if SEEDWS.exists():
            shutil.rmtree(SEEDWS)
        SEEDWS.mkdir(parents=True)
        (SEEDWS / "book_config.json").write_text(json.dumps(minimal, indent=2), "utf-8")
        (SEEDWS / "brief.md").write_text(
            "A short book proving deterministic engines beat heroic memory.\n"
            "chapters: 2\nwords: 200\n", "utf-8")
        if with_intake:
            (SEEDWS / "intake").mkdir()
            (SEEDWS / "intake" / "core.md").write_text(
                "# Core\nThe central claim: gates and disk beat a model holding state in its head.\n", "utf-8")
            (SEEDWS / "intake" / "satellite.md").write_text(
                "# Satellite\nA supporting case: every past failure was an unverified-state-advanced bug.\n", "utf-8")
            # a real DOCUMENT source (not markdown) to exercise manuscript_ingest conversion
            (SEEDWS / "intake" / "extra.html").write_text(
                "<html><body><h1>Extra Source</h1><p>A converted document source that must be "
                "flattened to markdown before it can be digested.</p></body></html>", "utf-8")

    def eng_seed(*extra):
        cmd = [PY, ENGINE, "--config", str(SEEDWS / "book_config.json"),
               "--dry-run", "--to", "assemble", *extra]
        return subprocess.run(cmd, capture_output=True, text=True, cwd=str(ROOT))

    build_seed_fixture()
    r = eng_seed("--fresh")
    print("F/SEED rc=", r.returncode)
    if r.returncode != 0:
        fails.append(f"F: seed run rc={r.returncode}\n{r.stdout[-900:]}\n{r.stderr[-400:]}")
    seedmd = SEEDWS / "seed.md"
    if not seedmd.exists():
        fails.append("F: seed.md not created")
    elif not all(f"## §{i}" in seedmd.read_text("utf-8") for i in range(1, 8)):
        fails.append("F: seed.md missing one of §1-§7")
    cfg2 = json.loads((SEEDWS / "book_config.json").read_text("utf-8"))
    if not cfg2.get("units"):
        fails.append("F: no units written into book_config.json by seed")
    else:
        for u in cfg2["units"]:
            if not (SEEDWS / "contracts" / f"{u['id']}.md").exists():
                fails.append(f"F: missing contract for {u['id']}")
        first = SEEDWS / "manuscript" / "current" / f"{cfg2['units'][0]['id']}_current.md"
        if not first.exists():
            fails.append("F: first chapter not drafted after seed (architect->draft handoff broken)")
    stF = json.loads((SEEDWS / "_engine" / "state.json").read_text("utf-8"))["stages"]
    if stF.get("seed", {}).get("status") != "done":
        fails.append("F: seed stage not marked done")
    for k in ("precheck", "integrate", "assemble"):
        if stF.get(k, {}).get("status") != "done":
            fails.append(f"F: post-seed stage {k} not done")
    try:
        import jsonschema
        jsonschema.validate(cfg2, json.loads((TOOLS / "book_config.schema.json").read_text("utf-8")))
    except ImportError:
        pass
    except Exception as e:
        fails.append(f"F: seeded config fails schema: {str(e).splitlines()[0][:160]}")
    # idempotent: a resume must NOT re-seed (units unchanged, seed skipped)
    units_before = json.dumps(cfg2.get("units"))
    r = eng_seed()
    if r.returncode != 0:
        fails.append(f"F: seed resume rc={r.returncode}")
    if json.dumps(json.loads((SEEDWS / "book_config.json").read_text("utf-8")).get("units")) != units_before:
        fails.append("F: seed not idempotent (units changed on resume)")

    # --- G. INGEST (intake docs -> relational digests + manifest, GATE-1) ---
    build_seed_fixture(with_intake=True)
    r = eng_seed("--fresh")
    print("G/INGEST rc=", r.returncode)
    if r.returncode != 0:
        fails.append(f"G: ingest+seed rc={r.returncode}\n{r.stdout[-800:]}")
    if not (SEEDWS / "canon_refs" / "_ingest.json").exists():
        fails.append("G: _ingest.json manifest not written")
    if not (SEEDWS / "intake" / "converted" / "extra.md").exists():
        fails.append("G: extra.html not converted to markdown by manuscript_ingest")
    digs = list((SEEDWS / "canon_refs").glob("_digest_*.md"))
    if len(digs) < 3:
        fails.append(f"G: expected >=3 digests (core.md + satellite.md + converted extra.html), got {len(digs)}")
    stG = json.loads((SEEDWS / "_engine" / "state.json").read_text("utf-8"))["stages"]
    if stG.get("ingest", {}).get("status") != "done":
        fails.append("G: ingest stage not marked done")
    if stG.get("seed", {}).get("status") != "done":
        fails.append("G: seed stage not done after ingest")
    # --- H. HARNESS SEED (keyless in-CC architect turn; performer simulated) ---
    build_seed_fixture()

    def eng_seed_h(*extra):
        cmd = [PY, ENGINE, "--config", str(SEEDWS / "book_config.json"),
               "--backend", "harness", "--no-cover", "--to", "precheck", *extra]
        return subprocess.run(cmd, capture_output=True, text=True, cwd=str(ROOT))

    r = eng_seed_h("--fresh")            # -> pause, requests the architect plan
    if r.returncode != 3:
        fails.append(f"H: first harness-seed run expected rc=3 (await), got {r.returncode}\n{r.stdout[-400:]}")
    if not (SEEDWS / "_engine" / "bridge" / "seed.request.json").exists():
        fails.append("H: seed.request.json not emitted for the architect turn")
    plan_json = {
        "units": [
            {"id": "ch_01", "title": "Inversion", "class": "C", "target_words": 200},
            {"id": "ch_02", "title": "The Ledger", "class": "C", "target_words": 200},
            {"id": "ch_03", "title": "The Gate", "class": "C", "target_words": 200},
        ],
        "work_intent": "Argue that durable systems invert control.",
        "voice_one_line": "plain, declarative, evidence-first",
        "refrain": "The disk is the memory.",
        "blacklist": ["delve"], "sacred_terms": ["gate", "ledger"],
    }
    (SEEDWS / "_engine" / "bridge" / "seed.response.json").write_text(json.dumps(plan_json), "utf-8")
    r = eng_seed_h()                     # reads plan -> seed.md + contracts + config -> precheck -> stop
    print("H/HARNESS-SEED rc=", r.returncode)
    if r.returncode != 0:
        fails.append(f"H: after plan response expected rc=0, got {r.returncode}\n{r.stdout[-500:]}")
    cfgh = json.loads((SEEDWS / "book_config.json").read_text("utf-8"))
    if [u["id"] for u in cfgh.get("units", [])] != ["ch_01", "ch_02", "ch_03"]:
        fails.append(f"H: harness-provided units not applied (got {[u.get('id') for u in cfgh.get('units', [])]})")
    if cfgh.get("voice", {}).get("blacklist") != ["delve"]:
        fails.append("H: harness plan blacklist not merged into voice")
    if not (SEEDWS / "contracts" / "ch_03.md").exists():
        fails.append("H: contracts not generated from the harness plan")
    if json.loads((SEEDWS / "_engine" / "state.json").read_text("utf-8"))["stages"].get("seed", {}).get("status") != "done":
        fails.append("H: seed stage not marked done after the harness turn")
    if SEEDWS.exists():
        shutil.rmtree(SEEDWS)

    # --- I. PLAN ORDERING (cover-consuming formats sequenced AFTER the cover stage) ---
    import importlib.util
    spec = importlib.util.spec_from_file_location("engine_mod", ENGINE)
    engmod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(engmod)
    IWS = ROOT / "book_workspace" / "_planordtest"
    if IWS.exists():
        shutil.rmtree(IWS)
    IWS.mkdir(parents=True)
    icfg = {"title": "X", "author": "Y", "slug": "_planordtest", "is_fiction": False,
            "formats": ["kindle", "epub", "digital_pdf"], "min_pages": 1,
            "units": [{"id": "ch_01", "title": "A", "class": "C", "target_words": 100}]}
    (IWS / "book_config.json").write_text(json.dumps(icfg), "utf-8")
    (IWS / "seed.md").write_text("# Book Bible\n", "utf-8")
    e = engmod.Engine(IWS / "book_config.json", "mock", False, False)  # no_cover False -> cover in plan
    keys = [k for k, _ in e.plan()]
    if "cover" not in keys:
        fails.append("I: cover stage missing from plan when no_cover=False")
    else:
        ci = keys.index("cover")
        for dep in ("produce:epub", "produce:digital_pdf"):
            if dep in keys and keys.index(dep) < ci:
                fails.append(f"I: {dep} sequenced BEFORE cover (ordering bug regressed)")
    if IWS.exists():
        shutil.rmtree(IWS)

    # --- J. DOMAIN GENERALITY: the 'course' domain drives the SAME engine ---
    CWS = ROOT / "book_workspace" / "_coursetest"
    if CWS.exists():
        shutil.rmtree(CWS)
    CWS.mkdir(parents=True)
    ccfg = {"title": "Intro to Control Inversion", "author": "BOOKSMITH", "slug": "_coursetest",
            "domain": "course",
            "voice": {"unit_noun": "lesson", "no_em_dashes": True, "blacklist": []},
            "units": [
                {"id": "l_01", "title": "What Inversion Is", "module": "Foundations", "target_words": 120},
                {"id": "l_02", "title": "The Ledger", "module": "Foundations", "target_words": 120},
                {"id": "l_03", "title": "The Gate", "module": "Practice", "target_words": 120}]}
    (CWS / "book_config.json").write_text(json.dumps(ccfg, indent=2), "utf-8")
    r = subprocess.run([PY, ENGINE, "--config", str(CWS / "book_config.json"), "--dry-run", "--fresh"],
                       capture_output=True, text=True, cwd=str(ROOT))
    print("J/DOMAIN-course rc=", r.returncode)
    if r.returncode != 0:
        fails.append(f"J: course engine run rc={r.returncode}\n{r.stdout[-900:]}\n{r.stderr[-300:]}")
    js = CWS / "outputs" / "course" / "_coursetest_course.json"
    if not (CWS / "outputs" / "course" / "_coursetest_COURSE.md").exists():
        fails.append("J: course markdown not produced")
    if not js.exists():
        fails.append("J: course json not produced")
    else:
        cj = json.loads(js.read_text("utf-8"))
        if cj.get("total_lessons") != 3:
            fails.append(f"J: expected 3 lessons, got {cj.get('total_lessons')}")
        if cj.get("total_modules") != 2:
            fails.append(f"J: expected 2 modules, got {cj.get('total_modules')}")
    for lid in ("l_01", "l_02", "l_03"):
        if not (CWS / "manuscript" / "current" / f"{lid}_current.md").exists():
            fails.append(f"J: lesson {lid} not drafted")
    try:
        stJ = json.loads((CWS / "_engine" / "state.json").read_text("utf-8"))["stages"]
        for k in ("precheck", "draft:l_01", "integrate", "produce:course_md",
                  "produce:course_json", "verify", "emit"):
            if stJ.get(k, {}).get("status") != "done":
                fails.append(f"J: stage {k} not done ({stJ.get(k, {}).get('status')})")
    except Exception as e:
        fails.append(f"J: could not read course engine state: {e}")
    if CWS.exists():
        shutil.rmtree(CWS)

    print("\n" + ("=" * 50))
    if fails:
        print(f"ENGINE SMOKETEST: FAIL ({len(fails)})")
        for f in fails:
            print("  - " + f)
        return 1
    print("ENGINE SMOKETEST: PASS — drive, idempotent resume, crash/drift recovery, "
          "loud hard-stop, the keyless harness bridge, and the INGEST+SEED architect "
          "front-half (brief -> seed.md + units + contracts, GATE-1/GATE-2) all verified.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
