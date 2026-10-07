#!/usr/bin/env python3
"""word_sweep.py: list, and on request stop, leaked Microsoft Word processes before a Word COM build.
A rejected COM call ("Call was rejected by callee", retries exhausted) leaves a WINWORD that still holds
the probe or interior DOCX open, so the next generator run fails with EBUSY and the next build refuses to
start ("WINWORD processes: 1"). `taskkill /PID` has failed silently here; PowerShell Stop-Process works.

Usage:
  python _tools/word_sweep.py            # list WINWORD processes (id, start time, window title)
  python _tools/word_sweep.py --kill     # stop them all (only when YOU are not editing in Word)
  python _tools/word_sweep.py --kill --older-than 20   # stop only instances older than 20 minutes
Exit 0 when no Word is left running, 1 when some remain (listed), 2 on a non-Windows host.
"""
import argparse
import json
import subprocess
import sys


def ps(cmd):
    r = subprocess.run(["powershell", "-NoProfile", "-NonInteractive", "-Command", cmd],
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    return r.returncode, (r.stdout or "").strip(), (r.stderr or "").strip()


def listing():
    rc, out, err = ps("Get-Process WINWORD -ErrorAction SilentlyContinue | "
                      "Select-Object Id, @{n='Start';e={$_.StartTime.ToString('s')}}, "
                      "@{n='Minutes';e={[int]((Get-Date) - $_.StartTime).TotalMinutes}}, MainWindowTitle | ConvertTo-Json")
    if not out:
        return []
    data = json.loads(out)
    return data if isinstance(data, list) else [data]


def main():
    if not sys.platform.startswith("win"):
        print("no Word COM on this host")
        return 2
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--kill", action="store_true")
    ap.add_argument("--older-than", type=int, default=0, help="minutes; with --kill, spare younger instances")
    a = ap.parse_args()
    procs = listing()
    if not procs:
        print("WINWORD: none running")
        return 0
    for p in procs:
        print("WINWORD pid %s  started %s  (%s min)  title: %s" % (p.get("Id"), p.get("Start"), p.get("Minutes"),
                                                                    p.get("MainWindowTitle") or "(no window)"))
    if not a.kill:
        return 1
    targets = [p for p in procs if int(p.get("Minutes") or 0) >= a.older_than]
    for p in targets:
        rc, out, err = ps("Stop-Process -Id %s -Force; 'stopped %s'" % (p["Id"], p["Id"]))
        print(out or err)
    left = listing()
    if left:
        print("still running:", [p.get("Id") for p in left])
        return 1
    print("WINWORD: none left")
    return 0


if __name__ == "__main__":
    sys.exit(main())
