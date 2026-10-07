"""One Laser Tag run of a staged laser_tag_evaluate project, traced, on a copy.
Measures; names no cause.

    python lt_trace_one.py <staging dir> <seed> <out dir>

The command is Level Factory's (adapters/laser_tag plan_commands): the
runner `run_map_eval.gd` with --bake-nav --map res://level.tscn --scenario
res://mission_scenario.tres, plus --runs 1 and --trace (the runner traces
run 1 only; run N uses seed + N, so shifting --seed moves a later run to 1).
The staging is copied first; the original is never touched. Prints every
PlayerStuck event of the run and every trace line naming LT_Player_04.
"""
import json
import os
import shutil
import subprocess
import sys

ROOT = r"C:\Projects\gabagool_studios\gabagool_factory"
sys.path.insert(0, os.path.join(ROOT, "tools"))
import godot_probe  # noqa: E402


def main():
    staging, seed, out = sys.argv[1], sys.argv[2], sys.argv[3]
    copy = os.path.join(out, "lt_%s" % seed)
    if os.path.exists(copy):
        shutil.rmtree(copy)
    shutil.copytree(staging, copy)
    report = os.path.join(out, "lt_%s.report.json" % seed)
    cmd = [godot_probe.require_godot(), "--headless", "--path", copy,
           "--script", "res://addons/laser_tag_tool/runners/run_map_eval.gd", "--",
           "--bake-nav", "--map", "res://level.tscn", "--scenario", "res://mission_scenario.tres",
           "--runs", "1", "--seed", str(seed), "--output", report, "--trace"]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=1200)
    text = (r.stdout or "") + (r.stderr or "")
    open(os.path.join(out, "lt_%s.log" % seed), "w", encoding="utf-8").write(text)
    shutil.rmtree(copy, ignore_errors=True)
    print("exit", r.returncode, "| log lines", len(text.splitlines()))
    if os.path.exists(report):
        ev = json.load(open(report, encoding="utf-8")).get("events", [])
        for e in ev:
            if e["event"] == "PlayerStuck":
                p = e["position"]
                print("  PlayerStuck %s t %.0f level (%.2f, %.2f) h %.2f" % (e["source"], e["time"], p[0], -p[2], p[1]))
    lines = [ln for ln in text.splitlines() if "LT_Player_04" in ln or "Player_04" in ln]
    print("  trace lines naming Player_04: %d" % len(lines))
    for ln in lines[-12:]:
        print("   ", ln[:200])


if __name__ == "__main__":
    main()
