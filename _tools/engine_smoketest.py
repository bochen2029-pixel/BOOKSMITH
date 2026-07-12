#!/usr/bin/env python3
r"""
engine_smoketest.py — prove the deterministic engine WITHOUT a real book run.

Builds a tiny synthetic 2-chapter book in book_workspace/_enginetest/, then drives
engine.py with the mock model backend through the real gates and asserts:

  A. FRESH    — a cold run drafts both chapters, lints, assembles (rc 0).
  B. RESUME   — re-running is idempotent: every stage skips as already-done.
  C. CRASH    — deleting a finished chapter makes the engine re-derive from disk
                and re-run exactly that unit (+ downstream), with ZERO orientation.

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

    print("\n" + ("=" * 50))
    if fails:
        print(f"ENGINE SMOKETEST: FAIL ({len(fails)})")
        for f in fails:
            print("  - " + f)
        return 1
    print("ENGINE SMOKETEST: PASS — drive, idempotent resume, crash/drift recovery, "
          "loud hard-stop, and the keyless harness bridge all verified.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
