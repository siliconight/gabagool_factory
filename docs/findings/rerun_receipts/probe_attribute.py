"""Attribute every job re-run on levels/panel_trial from its receipts (Level Factory 0.254.0 or later).

    python docs/findings/rerun_receipts/probe_attribute.py

Three runs through the launcher, all on the interpreter factory.cmd uses: the art build twice with nothing changed,
then the time of day changed through the worker and the level walked. After each, every job the run did not take
from the cache is listed with `packages.jobs.receipts.differences` -- what moved in its digest. Prints what it
measured; draws no conclusion. Writes nothing but run directories under _scratch/ and its own output.
"""
import json
import pathlib
import re
import subprocess
import sys
import time

F = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(F / "level_factory"))
from packages.jobs import receipts  # noqa: E402

WS = F / "levels" / "panel_trial" / "workspace"
JOBS = WS / ".level_factory" / "jobs"
DESIGN = F / "levels" / "panel_trial" / "design.json"
RUNS = F / "_scratch" / ("rerun_probe_%s" % time.strftime("%H%M%S"))
LINE = re.compile(r"^\s+(panel_trial_001\.\S+)\s+(cache|succeeded|failed\S*)\s*$")


def ran(log_text):
    return [m.group(1) for m in map(LINE.match, log_text.splitlines()) if m and m.group(2) != "cache"]


def report(label, log_text):
    jobs = ran(log_text)
    total = sum(1 for m in map(LINE.match, log_text.splitlines()) if m)
    print("== %s: %d of %d jobs ran" % (label, len(jobs), total), flush=True)
    for job in jobs:
        d = receipts.differences(JOBS / job)
        print("  %s: %s" % (job, "no previous receipt" if d is None else ("; ".join(d) or "digest unchanged?")))


def art_build(label):
    RUNS.mkdir(parents=True, exist_ok=True)
    out = subprocess.run(["cmd.exe", "/c", str(F / "factory.cmd"), "-C", str(WS), "run", "panel_trial_001", "--art",
                          "--gameplay"], capture_output=True, text=True, encoding="utf-8", errors="replace")
    (RUNS / (label + ".log")).write_text(out.stdout + out.stderr, encoding="utf-8")
    report(label, out.stdout)


def service(op, args, label):
    d = RUNS / label
    d.mkdir(parents=True)
    (d / "request.json").write_text(json.dumps({"schema": "gabagool.service.request.v1", "request_id": label,
                                                "operation": op, "arguments": args}), encoding="utf-8")
    subprocess.run(["cmd.exe", "/c", str(F / "factory.cmd"), "service-run", str(d)], capture_output=True)
    res = json.loads((d / "result.json").read_text(encoding="utf-8"))
    print("== %s: %s" % (label, res["status"] if res["status"] == "ok" else res["error"]), flush=True)
    return d, res


art_build("art_1_nothing_changed")
art_build("art_2_nothing_changed")
doc = json.loads(DESIGN.read_text(encoding="utf-8"))
new_time = "evening" if doc["choices"].get("time_of_day") == "midnight" else "midnight"
_, res = service("update_design", {"path": str(DESIGN), "revision": doc["revision"],
                                   "choices": {"time_of_day": new_time}}, "update_time_of_day")
if res["status"] == "ok":
    d, res = service("walk_level", {"path": str(DESIGN)}, "walk_after_time_change")
    if (d / "legs.log").exists():
        report("walk after the time of day changed to %s" % new_time, (d / "legs.log").read_text(encoding="utf-8"))
