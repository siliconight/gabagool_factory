"""Laser Tag 0.30.0 over the factory's 16 lots: a guard held by another bot is blocked, not stuck (roadmap 242).

    python docs/findings/route_snag/blocked_breadth.py

`engine_breadth.py`'s lots, each graded twice under Godot Physics with today's command (`--fixed-fps 60`, 25
runs from its job's seed):

  0.29.0   the `lasertag` repository's HEAD, exported -- the release before
  0.30.0   the repository's working tree, the change

0.30.0 changes what is COUNTED and nothing that moves: a guard held by another bot is handled as a stuck one,
the same state, the same jitter, the same random draws, and recorded as `EnemyBlocked`. So THE CONTROL is that
the two read identically in every summary field but the ones the change is about: `enemy_stuck_events`,
`enemy_stuck_per_enemy_run`, the new `enemy_blocked_events`, and the grade and score the stuck count feeds. A
lot where anything else moved says so; the change moved the fight there, and its row means nothing else.

Prints, a lot a line, 0.29.0's grade, score and enemy-stuck count against 0.30.0's, and 0.30.0's blocked count.
Copies go to `_scratch/blocked_breadth/` and are removed. Prints what it measured and stops;
`blocked_breadth.out.txt` is its output.
"""
import io
import json
import pathlib
import re
import shutil
import subprocess
import sys
import tarfile

F = pathlib.Path(__file__).resolve().parents[3]
GODOT = "C:/Godot/4.7/Godot_v4.7-stable_win64_console.exe"
SCR = F / "_scratch" / "blocked_breadth"
LOTS = [  # `engine_breadth.py`'s, 2026-10-12
    ("cold-9264-ws", "restaurant_row_001", "seed_9003"),
    ("cold-9264-ws", "restaurant_row_001", "seed_9104"),
    ("cold-9264-ws", "restaurant_row_001", "seed_9205"),
    ("cold-9246-ws", "deli_001", "seed_9191"),
    ("cold-9246-ws", "deli_001", "seed_9292"),
    ("cold-9246-ws", "deli_001", "seed_9393"),
    ("cold-9240-ws", "warehouse_yard_001", "seed_9004"),
    ("cold-9240-ws", "warehouse_yard_001", "seed_9105"),
    ("cold-9240-ws", "warehouse_yard_001", "seed_9206"),
    ("cold-9214-ws", "bank_block_001", "seed_9256"),
    ("cold-9209-ws", "club_block_014", "seed_9282"),
    ("line-after-gas_block_001-ws", "gas_block_001", "seed_9181"),
    ("line-after-gas_block_001-ws", "gas_block_001", "seed_9282"),
    ("line-after-crossroads_9600-ws", "crossroads_9600", "seed_9600"),
    ("line-after-crossroads_9600-ws", "crossroads_9600", "seed_9701"),
    ("line-after-crossroads_9600-ws", "crossroads_9600", "seed_9802"),
]
#: the fields 0.30.0 is allowed to move; every other summary field is the control
ABOUT = {"enemy_stuck_events", "enemy_stuck_per_enemy_run", "enemy_blocked_events"}


def _seed(job_log):
    first = job_log.read_text(encoding="utf-8", errors="replace").splitlines()[0]
    m = re.search(r"--seed (\d+)", first)
    if not m:
        sys.exit("UNKNOWN SHAPE: no --seed in %s" % job_log)
    return m.group(1)


def _grade(staging, addon, dst, seed):
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(staging, dst)
    shutil.rmtree(dst / "addons" / "laser_tag_tool")
    shutil.copytree(addon, dst / "addons" / "laser_tag_tool")
    out = dst / "report.json"
    subprocess.run([GODOT, "--headless", "--path", str(dst), "--import"], cwd=str(dst), capture_output=True,
                   text=True, timeout=900, stdin=subprocess.DEVNULL)
    subprocess.run([GODOT, "--headless", "--fixed-fps", "60", "--path", str(dst), "-s",
                    "res://addons/laser_tag_tool/runners/run_map_eval.gd", "--", "--bake-nav",
                    "--map", "res://level.tscn", "--scenario", "res://mission_scenario.tres",
                    "--runs", "25", "--seed", seed, "--output", str(out)],
                   cwd=str(dst), capture_output=True, text=True, timeout=1800, stdin=subprocess.DEVNULL)
    d = json.loads(out.read_text(encoding="utf-8")) if out.exists() else None
    shutil.rmtree(dst)
    return d


def main():
    if SCR.exists():
        shutil.rmtree(SCR)
    SCR.mkdir(parents=True)
    old = SCR / "lasertag_0290"
    old.mkdir()
    tar = subprocess.run(["git", "-C", str(F / "lasertag"), "archive", "HEAD"], capture_output=True, check=True)
    # unpacked here, not by a `tar` on PATH: Windows' own reads a tape device unless told `-f -`
    with tarfile.open(fileobj=io.BytesIO(tar.stdout)) as t:
        t.extractall(old, filter="data")
    addons = {"0.29.0": old / "addons" / "laser_tag_tool", "0.30.0": F / "lasertag" / "addons" / "laser_tag_tool"}
    for v, a in addons.items():
        ver = (a.parent.parent / "VERSION").read_text(encoding="utf-8").strip()
        print("%s: %s (%s)" % (v, a, ver), flush=True)
        if not ver.endswith(v):
            sys.exit("UNKNOWN SHAPE: %s's VERSION reads %r" % (a, ver))
    totals = {"stuck_0290": 0, "stuck_0300": 0, "blocked_0300": 0}
    for ws, mission, seed_name in LOTS:
        lf = F / "workspaces" / ws / ".level_factory"
        name = "%s.laser_tag_evaluate.candidate.%s" % (mission, seed_name)
        seed = _seed(lf / "jobs" / name / "1" / "job.log")
        rows = {v: _grade(lf / "staging" / name, a, SCR / ("%s_%s_%s" % (mission, seed_name, v)), seed)
                for v, a in addons.items()}
        a, b = rows["0.29.0"], rows["0.30.0"]
        if a is None or b is None:
            print("%s %s: NOT MEASURED (%s)" % (mission, seed_name,
                                                 ", ".join(v for v, r in rows.items() if r is None)), flush=True)
            continue
        moved = sorted(k for k in set(a["summary"]) | set(b["summary"])
                       if k not in ABOUT and a["summary"].get(k) != b["summary"].get(k))
        sa, sb = a["summary"], b["summary"]
        totals["stuck_0290"] += sa["enemy_stuck_events"]
        totals["stuck_0300"] += sb["enemy_stuck_events"]
        totals["blocked_0300"] += sb.get("enemy_blocked_events", 0)
        print("%-20s %-9s %-16s %3s -> %-16s %3s  enemy stuck %3d -> %3d, blocked %3d%s" % (
            mission, seed_name, a["grade"], a["overall_score"], b["grade"], b["overall_score"],
            sa["enemy_stuck_events"], sb["enemy_stuck_events"], sb.get("enemy_blocked_events", 0),
            "" if not moved else "   CONTROL FAILED: also moved %s" % ", ".join(moved)), flush=True)
    shutil.rmtree(SCR, ignore_errors=True)
    print("over the lots measured: enemy stuck %d under 0.29.0, %d under 0.30.0, and %d blocked" % (
        totals["stuck_0290"], totals["stuck_0300"], totals["blocked_0300"]))


if __name__ == "__main__":
    main()
