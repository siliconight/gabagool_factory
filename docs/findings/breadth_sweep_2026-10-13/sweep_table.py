"""The breadth sweep of 2026-10-13, read off its runs: one row a cold run.

    python docs/findings/breadth_sweep_2026-10-13/sweep_table.py <N> [<N> ...]

For each cold run N, from `docs/cold_runs/cold_N/driver.log` (written by `tools/cold_drive/sweep_one.sh`) and the
run's workspace, `workspaces/cold-N-ws/.level_factory/`:

  mission      the mission the drive exported (its `exported <mission> [portable-godot]` line)
  outcome      DONE or STOPPED, and where, and the INTERVENTIONS line `cold_run.py --end` printed
  seed         the candidate the driver picked
  findings     the two `total findings` the shell and art legs printed
  bake         the light bake's lightmap users
  grade        the picked candidate's Laser Tag grade and score, with its enemy stuck and blocked and
               its crew stuck, from that job's `out/lasertag.report.json`
  drive        the clock from the driver's first step to DONE

A run whose log lacks a field says so in its cell -- never a blank and never a zero. Prints the table and stops.

WHAT IT KEEPS (2026-10-13). The sweep ran it on cold runs 9278 to 9284 (README.md's table). It reads each
run's workspace for the grade and stuck cells alone and names none of the seven in full, so
`tools/factory_retire.py` keeps them by count only: once one is retired its row reads "(no Laser Tag report)"
there, and README.md's table stays the record. Writing the seven names out here would keep them -- 4.8 GB on
a disk 95% full on 2026-10-13 -- so they are left to the retire.
"""
import json
import pathlib
import re
import sys
from datetime import datetime

F = pathlib.Path(__file__).resolve().parents[3]


def _clock(t):
    return datetime.strptime(t, "%H:%M:%S")


def row(n):
    log = F / "docs" / "cold_runs" / ("cold_%s" % n) / "driver.log"
    if not log.exists():
        return {"run": n, "mission": "(no driver.log)"}
    t = log.read_text(encoding="utf-8", errors="replace")
    out = {"run": n}
    m = re.search(r"exported (\S+) \[portable", t)
    out["mission"] = m.group(1) if m else "(not exported)"
    end = re.findall(r"^(DONE \(\S+\)|STOPPED: .*)$", t, re.M)
    out["outcome"] = end[-1] if end else "(no end)"
    iv = re.findall(r"INTERVENTIONS: (\d+)", t)
    out["interventions"] = iv[-1] if iv else "(not counted)"
    m = re.search(r"picked (seed_\d+)", t)
    out["seed"] = m.group(1) if m else "(none picked)"
    out["findings"] = " / ".join(re.findall(r"total findings: (\d+)", t)) or "(none printed)"
    m = re.search(r"light bake: .*?(\d[\d,]*) users", t)
    out["bake_users"] = m.group(1) if m else "(no bake line)"
    steps = re.findall(r"^== \S+ \((\d\d:\d\d:\d\d)\)", t, re.M)
    done = re.search(r"^DONE \((\d\d:\d\d:\d\d)\)", t, re.M)
    if steps and done:
        secs = int((_clock(done.group(1)) - _clock(steps[0])).total_seconds()) % 86400
        out["drive"] = "%.1f min" % (secs / 60.0)
    else:
        out["drive"] = "(no clock)"
    if out["seed"].startswith("seed_") and not out["mission"].startswith("("):
        rep = (F / "workspaces" / ("cold-%s-ws" % n) / ".level_factory" / "jobs" /
               ("%s.laser_tag_evaluate.candidate.%s" % (out["mission"], out["seed"])) / "1" / "out" /
               "lasertag.report.json")
        if rep.exists():
            d = json.loads(rep.read_text(encoding="utf-8"))
            s = d["summary"]
            out["grade"] = "%s %s" % (d["grade"], d["overall_score"])
            out["stuck"] = "enemy %s, blocked %s, crew %s" % (
                s.get("enemy_stuck_events", "?"), s.get("enemy_blocked_events", "(no field)"),
                s.get("player_stuck_events", "?"))
        else:
            out["grade"] = "(no Laser Tag report)"
            out["stuck"] = "-"
    return out


def main():
    cols = ("run", "mission", "interventions", "outcome", "seed", "grade", "stuck", "findings", "bake_users",
            "drive")
    rows = [row(n) for n in sys.argv[1:]]
    for r in rows:
        print("  ".join("%s=%s" % (c, r.get(c, "-")) for c in cols))


if __name__ == "__main__":
    main()
