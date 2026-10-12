"""The physics-engine question beyond one lot: every mission family whose generated lots are still staged
somewhere, run through today's Laser Tag under Godot Physics and under Jolt (roadmap 242).

    python docs/findings/route_snag/engine_breadth.py

`engine_ab.py` answered on restaurant_row_001 alone. The other families' staged evaluation projects
are older -- their jobs ran Laser Tag before 0.27.0's fixed clock, whose reports do not repeat -- so a
copy here cannot be checked against its job. Instead each copy gets TODAY's Laser Tag addon (the
`lasertag` repo's `addons/laser_tag_tool`, replacing the one staged with it) and runs the current
command: `--fixed-fps 60`, 25 runs from the seed its job used. Three passes a lot:

  godot    the staged project as it is (it names no engine: Godot Physics)
  godot2   the same again: THE CONTROL -- it must read identically to `godot` in every field read, or
           the lot cannot separate an engine from noise and its row says so
  jolt     the project naming Jolt Physics, nothing else changed

The levels are the generator output of their day (older Lot and Deli Counter); the question is how
each engine moves bodies through the kinds of level the factory makes, which the same level answers.
A pin is counted the way `snag_trace.py` found one: player-stuck events at one position to a
millimetre, recurring in two or more runs. Copies go to `_scratch/engine_breadth/` and are removed.
It prints what it measured and stops; `engine_breadth.out.txt` is its output.
"""
import collections
import json
import pathlib
import re
import shutil
import subprocess
import sys

F = pathlib.Path(__file__).resolve().parents[3]
GODOT = "C:/Godot/4.7/Godot_v4.7-stable_win64_console.exe"
#: the Laser Tag addon dropped into each copy: the repository's, or another one named by `LT_ADDON`
#: (how Laser Tag 0.28.0's draft was measured before its release)
LT_ADDON = pathlib.Path(__import__("os").environ.get("LT_ADDON") or F / "lasertag" / "addons" / "laser_tag_tool")
SCR = F / "_scratch" / "engine_breadth"
LOTS = [  # (workspace, mission, seed): the newest staged lots of each family, 2026-10-12
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


def _pins(d):
    """Player-stuck events at a position recurring (to a millimetre) in two or more runs."""
    at = collections.defaultdict(set)
    count = collections.Counter()
    for e in d["events"]:
        if e["event"] != "PlayerStuck":
            continue
        k = tuple(round(v, 3) for v in e["position"])
        at[k].add(e["run_id"])
        count[k] += 1
    return sum(count[k] for k, runs in at.items() if len(runs) >= 2), sum(1 for runs in at.values() if len(runs) >= 2)


def _row(d):
    s = d["summary"]
    pinned, places = _pins(d)
    return (d["grade"], d["overall_score"], s["route_completion_rate"], s["player_stuck_events"], pinned,
            places, s["enemy_stuck_events"], s["player_deaths"])


def _fmt(r):
    return ("%-16s %3s  route %4s  player stuck %3s (pinned %3s at %2s places)  enemy stuck %3s  deaths %3s" % r)


def _seed(job_log):
    first = job_log.read_text(encoding="utf-8", errors="replace").splitlines()[0]
    m = re.search(r"--seed (\d+)", first)
    if not m:
        sys.exit("UNKNOWN SHAPE: no --seed in %s" % job_log)
    return m.group(1)


def main():
    if not (LT_ADDON / "runners" / "run_map_eval.gd").exists():
        sys.exit("no Laser Tag addon at %s" % LT_ADDON)
    version = LT_ADDON.parent.parent / "VERSION"
    print("Laser Tag addon: %s (%s)" % (LT_ADDON, version.read_text().strip() if version.exists() else "?"),
          flush=True)
    if SCR.exists():
        shutil.rmtree(SCR)
    SCR.mkdir(parents=True)
    totals = collections.defaultdict(lambda: [0, 0])
    worst = 0
    for ws, mission, seed in LOTS:
        lf = F / "workspaces" / ws / ".level_factory"
        name = "%s.laser_tag_evaluate.candidate.%s" % (mission, seed)
        n = _seed(lf / "jobs" / name / "1" / "job.log")
        rows = {}
        for arm in ("godot", "godot2", "jolt"):
            dst = SCR / ("%s_%s_%s" % (mission, seed, arm))
            shutil.copytree(lf / "staging" / name, dst)
            shutil.rmtree(dst / "addons" / "laser_tag_tool")
            shutil.copytree(LT_ADDON, dst / "addons" / "laser_tag_tool")
            if arm == "jolt":
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
                   "--runs", "25", "--seed", n, "--output", str(out)]
            # an import first: the copy's addon is new to its cache
            subprocess.run([GODOT, "--headless", "--path", str(dst), "--import"], cwd=str(dst),
                           capture_output=True, text=True, timeout=900, stdin=subprocess.DEVNULL)
            subprocess.run(cmd, cwd=str(dst), capture_output=True, text=True, timeout=1800,
                           stdin=subprocess.DEVNULL)
            rows[arm] = _row(json.loads(out.read_text(encoding="utf-8"))) if out.exists() else None
            shutil.rmtree(dst)
        held = rows["godot"] is not None and rows["godot"] == rows["godot2"]
        if not held:
            worst = max(worst, 1)
        print("%s %s (seed %s)%s" % (mission, seed, n, "" if held else "   CONTROL FAILED: two Godot Physics passes differ"))
        for arm in ("godot", "godot2", "jolt"):
            print("   %-7s %s" % (arm, _fmt(rows[arm]) if rows[arm] else "NOT MEASURED"))
        if held and rows["jolt"]:
            for i, key in ((3, "player stuck"), (4, "pinned")):
                totals[key][0] += rows["godot"][i]
                totals[key][1] += rows["jolt"][i]
        sys.stdout.flush()
    shutil.rmtree(SCR, ignore_errors=True)
    print("over the lots whose control held: " + ", ".join(
        "%s %d under Godot Physics, %d under Jolt" % (k, v[0], v[1]) for k, v in totals.items()))
    return worst


if __name__ == "__main__":
    sys.exit(main())
