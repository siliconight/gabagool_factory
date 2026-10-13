"""Two candidate pickers, replayed on every cold workspace on this disk: where do their picks differ?

    python docs/findings/breadth_sweep_2026-10-13/pick_replay.py <picker A> <picker B>

Each picker is a copy of `tools/cold_drive/pick_candidate.py` (for the change of 2026-10-13: the copy before
`patches/patch_pick_candidate_grade.py`, and the patched file). For each `workspaces/cold-NNNN-ws/` whose
`.level_factory/validation/<mission>.json` exists, both are run on that workspace and mission, as the driver
runs one after the shell leg, and their printed seeds compared. Prints every workspace's two picks, marks the
ones that differ with each pick's Laser Tag grade and score, and a total. A picker that fails prints its
error in the row, never a seed. Prints what it measured and stops.
"""
import glob
import json
import os
import pathlib
import subprocess
import sys

F = pathlib.Path(__file__).resolve().parents[3]
A, B = sys.argv[1], sys.argv[2]


def _pick(script, ws, mission):
    run = subprocess.run([sys.executable, script, str(ws), mission], capture_output=True, text=True)
    out = run.stdout.strip()
    return out if run.returncode == 0 and out.isdigit() else "ERROR(%s)" % (run.stderr.strip().splitlines() or ["?"])[-1][:60]


def _grade(ws, mission, seed):
    rep = glob.glob(os.path.join(ws, ".level_factory", "jobs", "%s.laser_tag_evaluate.candidate.seed_%s" % (mission, seed),
                                 "*", "out", "lasertag.report.json"))
    if not rep:
        return "no report"
    d = json.load(open(rep[-1], encoding="utf-8"))
    return "%s %s" % (d.get("grade"), d.get("overall_score"))


def main():
    rows = differ = 0
    for ws in sorted(F.glob("workspaces/cold-*-ws"), key=lambda p: int(p.name.split("-")[1])):
        for v in sorted((ws / ".level_factory" / "validation").glob("*.json")):
            mission = v.stem
            if not glob.glob(str(ws / ".level_factory" / "jobs" / ("%s.lot_assemble.candidate.seed_*" % mission))):
                continue
            a, b = _pick(A, ws, mission), _pick(B, ws, mission)
            rows += 1
            mark = ""
            if a != b:
                differ += 1
                mark = "  DIFFERS: %s (%s) -> %s (%s)" % (a, _grade(ws, mission, a), b, _grade(ws, mission, b))
            print("%-16s %-22s %s -> %s%s" % (ws.name, mission, a, b, mark))
    print("%d workspace mission(s) replayed, %d pick(s) differ" % (rows, differ))


if __name__ == "__main__":
    main()
