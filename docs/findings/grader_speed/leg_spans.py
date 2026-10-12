"""Where a cold run's art leg spent its time, from the workspace index's own job records.

For each workspace given: the art leg's jobs (every job the leg ran, cache hits set aside -- the
art leg re-plans the mission, so the shell leg's jobs read as cache hits here and their records
carry the art leg's times), the span from the first start to the last finish, the Blender
window (the same over the `blender` class), and the CRITICAL CHAIN: from the job that finished
last, back through whichever of its dependencies finished last, each job's start and duration
in seconds from the leg's first start, and the gap between that dependency's finish and the
job's start (time the job waited on something other than its dependencies: a class cap, the
scheduler's own work before the command, staging).

It measures and prints; it names no cause.

    python docs/findings/grader_speed/leg_spans.py workspaces/cold-9251-ws [workspaces/cold-9252-ws]
"""
import datetime as dt
import json
import os
import sqlite3
import sys


def _t(s):
    return dt.datetime.fromisoformat(s.replace("Z", "+00:00")).timestamp()


def jobs(ws):
    c = sqlite3.connect(os.path.join(ws, ".level_factory", "index.sqlite"))
    out = {}
    for jid, p in c.execute("select job_id, payload from jobs"):
        d = json.loads(p)
        if d.get("status") == "SUCCEEDED" and d.get("started_at") and d.get("finished_at"):
            out[jid] = d
    return out


def report(ws):
    js = jobs(ws)
    if not js:
        print("%s: no job with a start and a finish" % ws)
        return
    t0 = min(_t(d["started_at"]) for d in js.values())
    t1 = max(_t(d["finished_at"]) for d in js.values())
    print("== %s: %d jobs ran, %.1f s from the first start to the last finish"
          % (os.path.basename(ws.rstrip("/\\")), len(js), t1 - t0))
    by = {}
    for d in js.values():
        by.setdefault(d["resource_class"], []).append(d)
    for cls, ds in sorted(by.items()):
        a = min(_t(d["started_at"]) for d in ds)
        b = max(_t(d["finished_at"]) for d in ds)
        busy = sum(_t(d["finished_at"]) - _t(d["started_at"]) for d in ds)
        print("   %-15s %3d jobs, window %6.1f s (%6.1f -> %6.1f), job-seconds %7.1f"
              % (cls, len(ds), b - a, a - t0, b - t0, busy))
    last = max(js.values(), key=lambda d: _t(d["finished_at"]))
    chain = [last]
    while True:
        deps = [js[j] for j in (chain[-1].get("depends_on") or []) if j in js]
        if not deps:
            break
        chain.append(max(deps, key=lambda d: _t(d["finished_at"])))
    print("   critical chain, first to last (s from the leg's first start):")
    print("   %7s %7s %7s %7s  %s" % ("start", "finish", "ran", "waited", "job"))
    prev_finish = None
    for d in reversed(chain):
        s, f = _t(d["started_at"]) - t0, _t(d["finished_at"]) - t0
        wait = "" if prev_finish is None else "%7.1f" % (s - prev_finish)
        print("   %7.1f %7.1f %7.1f %7s  %s" % (s, f, f - s, wait, d["job_id"]))
        prev_finish = f
    first = chain[-1]
    print("   the chain's first job started %.1f s after the leg's first start"
          % (_t(first["started_at"]) - t0))


if __name__ == "__main__":
    for w in sys.argv[1:]:
        report(os.path.abspath(w))
