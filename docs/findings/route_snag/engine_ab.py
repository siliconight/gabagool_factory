"""Is roadmap 242's swing the physics engine's corner pin? seed_9104's graded lot in cold runs 9261 (steel
lamps), 9262 (the pole line) and 9263 (0.118.1's corner pole), each run through the Laser Tag job's own
command -- 25 runs from seed 9104, the fixed clock -- under the engine the staged project runs (it names
none, so Godot Physics) and under Jolt Physics, nothing else changed.

    python docs/findings/route_snag/engine_ab.py

`snag_trace.py` found the dominant snag is a body pinned at the deli register counter's corner: Godot
Physics' move_and_slide reports the floor first and never slides along the counter, where Jolt slides.
If the swing between the three lots is that pin, the three should read closer under Jolt.

THE CONTROL: each Godot Physics arm must reproduce its job's report (grade, score, route completion,
player and enemy stuck counts, deaths); an arm that does not is not the job and the row says so.
Copies go to `_scratch/engine_ab/` and are removed after. It prints what it measured and stops.

CANNOT RUN AGAIN AS WRITTEN (2026-10-12). That day's cold-run retire steps removed
workspaces/cold-9261-ws and workspaces/cold-9262-ws: this script built their names as
`"cold-%d-ws" % run`, which `tools/factory_retire.py`'s reference scan cannot see, and no
other record named them. Its 9261 and 9262 arms have no lot to read; `engine_ab.out.txt` is
their record, kept as measured. As written it stops at 9261's missing job report, and 9263's
arm runs with RUNS cut to that one. RUNS writes the names out so the scan sees what is left.
"""
import json
import math
import pathlib
import shutil
import subprocess
import sys

F = pathlib.Path(__file__).resolve().parents[3]
GODOT = "C:/Godot/4.7/Godot_v4.7-stable_win64_console.exe"
JOB = "restaurant_row_001.laser_tag_evaluate.candidate.seed_9104"
SCR = F / "_scratch" / "engine_ab"
CORNER = (-66.35, -4.94)          # plan: the deli register counter's south-west corner pin
#: (run, its workspace), the names written out: `tools/factory_retire.py` keeps a workspace
#: a record names, and `"cold-%d-ws" % run` named none (see above)
RUNS = ((9261, "cold-9261-ws"), (9262, "cold-9262-ws"), (9263, "cold-9263-ws"))


def _row(d):
    s = d["summary"]
    near = sum(1 for e in d["events"] if e["event"] == "PlayerStuck"
               and math.hypot(e["position"][0] - CORNER[0], -e["position"][2] - CORNER[1]) < 1.0)
    return (d["grade"], d["overall_score"], s["route_completion_rate"], s["player_stuck_events"], near,
            s["enemy_stuck_events"], s["player_deaths"])


def _fmt(r):
    return "%-16s %3s  route %4s  player stuck %2s (at the counter %2s)  enemy stuck %2s  deaths %2s" % r


def main():
    if SCR.exists():
        shutil.rmtree(SCR)
    SCR.mkdir(parents=True)
    worst = 0
    for run, name in RUNS:
        ws = F / "workspaces" / name / ".level_factory"
        job = json.loads((ws / "jobs" / JOB / "1" / "out" / "lasertag.report.json").read_text(encoding="utf-8"))
        print("%d job          %s" % (run, _fmt(_row(job))))
        for engine in ("godot", "jolt"):
            dst = SCR / ("%d_%s" % (run, engine))
            shutil.copytree(ws / "staging" / JOB, dst)
            if engine == "jolt":
                pg = dst / "project.godot"
                text = pg.read_text(encoding="utf-8")
                if "3d/physics_engine" in text:
                    sys.exit("UNKNOWN SHAPE: %s already names a physics engine" % pg)
                pg.write_text(text.rstrip("\n") + '\n\n[physics]\n\n3d/physics_engine="Jolt Physics"\n',
                              encoding="utf-8", newline="\n")
            out = dst / "report.json"
            cmd = [GODOT, "--headless", "--fixed-fps", "60", "--path", str(dst), "-s",
                   "res://addons/laser_tag_tool/runners/run_map_eval.gd", "--", "--bake-nav",
                   "--map", "res://level.tscn", "--scenario", "res://mission_scenario.tres",
                   "--runs", "25", "--seed", "9104", "--output", str(out)]
            subprocess.run(cmd, cwd=str(dst), capture_output=True, text=True, timeout=1200,
                           stdin=subprocess.DEVNULL)
            if not out.exists():
                print("%d %-12s NOT MEASURED" % (run, engine))
                worst = 2
                continue
            r = _row(json.loads(out.read_text(encoding="utf-8")))
            note = ""
            if engine == "godot":
                note = "   control held" if r == _row(job) else "   CONTROL FAILED: not the job"
                if r != _row(job):
                    worst = max(worst, 1)
            print("%d %-12s %s%s" % (run, engine, _fmt(r), note))
            shutil.rmtree(dst)
    shutil.rmtree(SCR)
    return worst


if __name__ == "__main__":
    sys.exit(main())
