"""Where Laser Tag's crew bot "arrives": every route point it counts as reached, and how far it stood from it (roadmap 246).

    python docs/findings/lt_arrival/arrival_trace.py <workspace> <mission> <seed name> [<runs>]
    python docs/findings/lt_arrival/arrival_trace.py cold-9185-ws restaurant_row_001 seed_9003 2

Roadmap 245's census found cold run 9185's restaurant_row_001 seed_9003 graded at route completion 1.00, every
run, while the walk test's path to its objective stopped 60.99 m short on a navmesh island. The reading filed as 246:
`LT_BotPlayerController` counts a route point reached when `_nav_finished()` -- `NavigationAgent3D.
is_navigation_finished()`, true at the end of the path the server returned, which for a point the network does not
reach is the closest point it does -- and never asks `is_target_reached()`.

This copies the candidate's staged evaluation (`.level_factory/staging/<mission>.laser_tag_evaluate.candidate.
<seed name>/`) to `_scratch/lt_arrival/`, swaps in a copy of the repository's addon -- Laser Tag as it is now --
with one print at the arrival (`LT_TRACE`, the anchor asserted once, the file checked by `tools/gdcheck.py`), and
runs Laser Tag's own command with the job's seed for ``runs`` runs. Every arrival prints: the run, the route
point's index, where the bot stood and where the point is (Godot metres: x, y up, z), their flat distance, and what
`is_target_reached()` and `get_final_position()` said at that moment. Then the report's route completion. The copy
is removed. Laser Tag itself is not changed. Prints what it measured and stops.
"""
import json
import pathlib
import re
import shutil
import subprocess
import sys

F = pathlib.Path(__file__).resolve().parents[3]
GODOT = "C:/Godot/4.7/Godot_v4.7-stable_win64_console.exe"
SCR = F / "_scratch" / "lt_arrival"
BOT = "scripts/player/LT_BotPlayerController.gd"
ANCHOR = ("\t\t_route_index += 1\n"
          "\t\t_route_reached += 1\n"
          "\t\t# a route point reached restarts the stuck window (0.28.1)\n")
TRACE = ("\t\tvar _trace_rp: Vector3 = route_points[_route_index]\n"
         "\t\tvar _trace_reached: String = \"n/a\"\n"
         "\t\tvar _trace_final: String = \"n/a\"\n"
         "\t\tif nav_agent != null:\n"
         "\t\t\t_trace_reached = str(nav_agent.is_target_reached())\n"
         "\t\t\t_trace_final = str(nav_agent.get_final_position())\n"
         "\t\tvar _trace_here: Vector3 = body.global_position\n"
         "\t\tvar _trace_flat: float = Vector2(_trace_rp.x - _trace_here.x, _trace_rp.z - _trace_here.z).length()\n"
         "\t\tvar _trace_line: String = \"LT_TRACE arrive idx=%d at=%s point=%s flat=%.2f reached=%s final=%s\"\n"
         "\t\tprint(_trace_line % [_route_index, str(_trace_here), str(_trace_rp), _trace_flat, _trace_reached,"
         " _trace_final])\n")


def _seed(job_log):
    m = re.search(r"--seed (\d+)", job_log.read_text(encoding="utf-8", errors="replace").splitlines()[0])
    if not m:
        sys.exit(f"UNKNOWN SHAPE: no --seed in {job_log}")
    return m.group(1)


def main():
    ws, mission, seed_name = sys.argv[1], sys.argv[2], sys.argv[3]
    runs = sys.argv[4] if len(sys.argv) > 4 else "2"
    lf = F / "workspaces" / ws / ".level_factory"
    name = f"{mission}.laser_tag_evaluate.candidate.{seed_name}"
    staging = lf / "staging" / name
    seed = _seed(lf / "jobs" / name / "1" / "job.log")
    dst = SCR / name
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(staging, dst)
    shutil.rmtree(dst / "addons" / "laser_tag_tool")
    shutil.copytree(F / "lasertag" / "addons" / "laser_tag_tool", dst / "addons" / "laser_tag_tool")
    bot = dst / "addons" / "laser_tag_tool" / BOT
    text = bot.read_text(encoding="utf-8")
    assert text.count(ANCHOR) == 1, ("the arrival anchor", text.count(ANCHOR))
    bot.write_text(text.replace(ANCHOR, TRACE + ANCHOR), encoding="utf-8")
    chk = subprocess.run([sys.executable, str(F / "tools" / "gdcheck.py"), str(bot)], capture_output=True, text=True)
    if chk.returncode:
        sys.exit("gdcheck refused the traced file:\n" + chk.stdout[-800:] + chk.stderr[-400:])
    out = dst / "report.json"
    subprocess.run([GODOT, "--headless", "--path", str(dst), "--import"], cwd=str(dst), capture_output=True,
                   text=True, timeout=900, stdin=subprocess.DEVNULL)
    r = subprocess.run([GODOT, "--headless", "--fixed-fps", "60", "--path", str(dst), "-s",
                        "res://addons/laser_tag_tool/runners/run_map_eval.gd", "--", "--bake-nav",
                        "--map", "res://level.tscn", "--scenario", "res://mission_scenario.tres",
                        "--runs", runs, "--seed", seed, "--output", str(out)],
                       cwd=str(dst), capture_output=True, text=True, timeout=1800, stdin=subprocess.DEVNULL)
    lines = [l for l in r.stdout.splitlines() if "LT_TRACE" in l]
    print(f"{ws} {mission} {seed_name}: seed {seed}, {runs} run(s), {len(lines)} arrival(s) traced")
    for l in lines:
        print("  " + l[l.index("LT_TRACE"):])
    if out.exists():
        d = json.loads(out.read_text(encoding="utf-8"))
        s = d.get("summary", {})
        print(f"  report: route completion {s.get('route_completion_rate')}, progress {s.get('route_progress_rate')}, "
              f"grade {d.get('grade')} {d.get('overall_score')}")
    else:
        print("  report: none written; Godot's last lines: " + " | ".join(r.stdout.splitlines()[-5:]))
    shutil.rmtree(dst)


if __name__ == "__main__":
    main()
