"""What restaurant_row_001 seed_9104's stuck enemies were trying to reach (roadmap 242; the stoop breadth's
"found on the way", `enemy_pin_probe.gd`: nothing touches them and they were not fighting).

    python docs/findings/stoop_breadth/enemy_stop_trace.py

Laser Tag counts an enemy stuck when it still has a destination and has moved under 0.5 m in 3 s
(`LT_EnemyMovement._update_stuck`). Its movement stops the body when the next path point is within 0.05 m,
and arrival is the navigation agent's own `is_navigation_finished()`. So this copies cold run 9274's staged
evaluation project to `_scratch/enemy_trace/`, changes the COPY's `LT_EnemyBrain._on_stuck` only -- it prints
the agent's state at each stuck event (its target, whether the target is reachable or reached, whether the
navigation is finished, the path, its index and last point, and the two arrival distances), calling no
function that moves the path on -- and runs the job's own command: 25 runs from the job's seed.

THE CONTROL: the copy's report must equal the job's in every summary field and in its EnemyStuck events
(run, time, source, position). If it does not, the copy is not the job, or the trace moved it, and what it
prints says nothing about the job; it says so and stops. It prints what it measured and stops.

    python docs/findings/stoop_breadth/enemy_stop_trace.py --lot <workspace> <mission> <seed> [...]

THE LOT MODE: any staged lot, graded by TODAY's Laser Tag (the `lasertag` repo's addon, its `_on_stuck`
traced), because a lot staged before Laser Tag 0.27.0's fixed clock cannot reproduce its own job
(`docs/findings/route_snag/engine_breadth.py`). THE CONTROL there is two runs of the copy reading
identically in every summary field and stuck event. Each EnemyStuck is CLASSED by this frame's slide
collisions:
- `teammate`: another enemy, `LT_Enemy_*`;
- `crew`: an `LT_Player_*`;
- `static`: anything else, the level;
- `none`: no collision -- standing for some other reason.

    python docs/findings/stoop_breadth/enemy_stop_trace.py --lot --contacts <workspace> <mission> <seed> [...]

THE CONTACTS (2026-10-13, for Laser Tag 0.30.0's residue). The class above asks whether ANY contact is
another body; Laser Tag 0.30.0 asks whether every contact but the floor is one, and counts a guard stuck
otherwise. `--contacts` prints each traced event's place, its class as 0.30.0 asks it, and each contact of
the level by its node path's last two parts and its normal. Under 0.30.0 only the guards it still counts
stuck are traced -- a blocked guard goes through `_on_blocked` -- so every traced event should class
`level`, `level+body` or `none`; a `body` there is the trace disagreeing with the rule, and it says so by
printing it. The census reads the trace's names, `LT_Enemy_*` and `LT_Player_*`, where 0.30.0 reads the
class, CharacterBody3D. `--raw` also prints every `[enemy trace]` line of the first run: each event's agent
state, its path's head and its contacts, as the job mode does.
"""
import json
import math
import pathlib
import re
import shutil
import subprocess
import sys

F = pathlib.Path(__file__).resolve().parents[3]
WS = F / "workspaces" / "cold-9274-ws" / ".level_factory"
NAME = "restaurant_row_001.laser_tag_evaluate.candidate.seed_9104"
SRC = WS / "staging" / NAME
JOB = WS / "jobs" / NAME / "1"
DST = F / "_scratch" / "enemy_trace"
GODOT = "C:/Godot/4.7/Godot_v4.7-stable_win64_console.exe"
BRAIN = "addons/laser_tag_tool/scripts/enemy/LT_EnemyBrain.gd"

STUCK_OLD = ("func _on_stuck(position: Vector3) -> void:\n"
             "\tstuck_count += 1\n"
             "\tstate = State.STUCK\n")
STUCK_NEW = STUCK_OLD + (
    "\t# TRACE -- a measurement copy (the factory's docs/findings/stoop_breadth/enemy_stop_trace.py)\n"
    "\tif movement != null and movement.nav_agent != null and _body != null:\n"
    "\t\tvar dbg_ag: NavigationAgent3D = movement.nav_agent\n"
    "\t\tvar dbg_path: PackedVector3Array = dbg_ag.get_current_navigation_path()\n"
    "\t\tvar dbg_last: Vector3 = Vector3.ZERO\n"
    "\t\tvar dbg_gap: float = -1.0\n"
    "\t\tif dbg_path.size() > 0:\n"
    "\t\t\tdbg_last = dbg_path[dbg_path.size() - 1]\n"
    "\t\t\tdbg_gap = Vector2(_body.global_position.x - dbg_last.x, _body.global_position.z - dbg_last.z).length()\n"
    "\t\tvar dbg_fmt: String = \"[enemy trace] %s at %s: wants %s, target %s, to target %.3f, reachable %s, reached %s, finished %s, path %d points (index %d), last %s, body to last %.3f m flat, path_desired %.3f, target_desired %.3f, velocity %s\"\n"
    "\t\tprint(dbg_fmt % [_source_name(), str(_body.global_position), str(movement.get(\"_wants_to_move\")),\n"
    "\t\t\tstr(dbg_ag.target_position), dbg_ag.distance_to_target(), str(dbg_ag.is_target_reachable()),\n"
    "\t\t\tstr(dbg_ag.is_target_reached()), str(dbg_ag.is_navigation_finished()), dbg_path.size(),\n"
    "\t\t\tdbg_ag.get_current_navigation_path_index(), str(dbg_last), dbg_gap,\n"
    "\t\t\tdbg_ag.path_desired_distance, dbg_ag.target_desired_distance, str(_body.velocity)])\n"
    "\t\t# the path's head: each point less the agent's height offset, as the agent reads it, and its\n"
    "\t\t# distance from the body flat and in 3D\n"
    "\t\tvar dbg_off: float = dbg_ag.path_height_offset\n"
    "\t\tfor dbg_k in range(mini(dbg_path.size(), 4)):\n"
    "\t\t\tvar dbg_p: Vector3 = dbg_path[dbg_k] - Vector3(0.0, dbg_off, 0.0)\n"
    "\t\t\tvar dbg_flat: float = Vector2(_body.global_position.x - dbg_p.x, _body.global_position.z - dbg_p.z).length()\n"
    "\t\t\tvar dbg_pfmt: String = \"[enemy trace]   path[%d] %s (offset %.3f): flat %.3f m, 3D %.3f m\"\n"
    "\t\t\tprint(dbg_pfmt % [dbg_k, str(dbg_p), dbg_off, dbg_flat, _body.global_position.distance_to(dbg_p)])\n"
    "\t\t# what this frame's move_and_slide met: `_on_stuck` is reached from `_update_stuck`, which runs\n"
    "\t\t# right after it in the movement's `_physics_process`\n"
    "\t\tvar dbg_n: int = _body.get_slide_collision_count()\n"
    "\t\tprint(\"[enemy trace]   this frame's slide collisions: %d\" % dbg_n)\n"
    "\t\tprint(\"[enemy trace]   floor_max_angle %.4f\" % _body.floor_max_angle)\n"
    "\t\tfor dbg_c in range(dbg_n):\n"
    "\t\t\tvar dbg_sc: KinematicCollision3D = _body.get_slide_collision(dbg_c)\n"
    "\t\t\tvar dbg_o: Object = dbg_sc.get_collider()\n"
    "\t\t\tvar dbg_on: String = str(dbg_o)\n"
    "\t\t\tif dbg_o is Node:\n"
    "\t\t\t\tdbg_on = str((dbg_o as Node).get_path())\n"
    "\t\t\tvar dbg_cfmt: String = \"[enemy trace]     %s at %s, normal %s, travel %s\"\n"
    "\t\t\tprint(dbg_cfmt % [dbg_on, str(dbg_sc.get_position()), str(dbg_sc.get_normal()), str(dbg_sc.get_travel())])\n")

#: Laser Tag 0.30.0 moved `_on_stuck`'s body into `_held`, which `_on_blocked` shares, so a stuck guard is traced
#: at `_on_stuck`'s head, before `_held` records it and sets its jitter -- the agent's state as the 0.29.0 trace
#: read it -- and a BLOCKED guard is not traced at all
STUCK_OLD_030 = ("func _on_stuck(position: Vector3) -> void:\n"
                 "\t_held(position, \"EnemyStuck\")\n")
STUCK_NEW_030 = ("func _on_stuck(position: Vector3) -> void:\n" + STUCK_NEW[len(STUCK_OLD):]
                 + "\t_held(position, \"EnemyStuck\")\n")


def _traced(text):
    """The brain's text with `_on_stuck` traced, on 0.29.0's shape or 0.30.0's; any other shape refuses."""
    n29, n30 = text.count(STUCK_OLD), text.count(STUCK_OLD_030)
    if (n29, n30) == (1, 0):
        return text.replace(STUCK_OLD, STUCK_NEW)
    if (n29, n30) == (0, 1):
        return text.replace(STUCK_OLD_030, STUCK_NEW_030)
    sys.exit("UNKNOWN SHAPE: `_on_stuck`'s head %d times as 0.29.0 wrote it, %d as 0.30.0" % (n29, n30))


def _seed(job_log):
    first = job_log.read_text(encoding="utf-8", errors="replace").splitlines()[0]
    m = re.search(r"--seed (\d+)", first)
    if not m:
        sys.exit("UNKNOWN SHAPE: no --seed in %s" % job_log)
    return m.group(1)


def _stuck(d):
    return sorted((e["run_id"], round(float(e["time"]), 2), e.get("source"), tuple(e["position"]))
                  for e in d["events"] if e["event"] == "EnemyStuck")


LT_ADDON = F / "lasertag" / "addons" / "laser_tag_tool"


_AT = re.compile(r"^\[enemy trace\] (LT_\S+) at \(([^)]*)\)")
_HIT = re.compile(r"^\[enemy trace\]     (\S+) at \(([^)]*)\), normal \(([^)]*)\)")
_FMA = re.compile(r"^\[enemy trace\]   floor_max_angle ([0-9.]+)")


def _vec(s):
    return tuple(float(v) for v in s.split(","))


def _classify(stdout):
    """Each `[enemy trace]` block's class, from its slide collisions, in event order.

    `class` is the question the four-lot census asked: is ANY contact another body (a teammate first, then a
    crew member), else the level, else none. `class30` is the question Laser Tag 0.30.0 asks: leaving out
    each contact under the feet (its normal within the body's `floor_max_angle` of up), are all the rest
    bodies (`body`), all the level (`level`), both (`level+body`), or is there nothing (`none`). A bot is a
    body by its name, `LT_Enemy_*` or `LT_Player_*`, where 0.30.0 asks `is CharacterBody3D`.
    """
    out, cur = [], None
    for line in stdout.splitlines():
        m = _AT.match(line)
        if m:
            if cur is not None:
                out.append(cur)
            cur = {"who": m.group(1), "at": _vec(m.group(2)), "hits": [], "fma": None}
            continue
        if cur is None:
            continue
        m = _HIT.match(line)
        if m:
            cur["hits"].append((m.group(1), _vec(m.group(2)), _vec(m.group(3))))
            continue
        m = _FMA.match(line)
        if m:
            cur["fma"] = float(m.group(1))
    if cur is not None:
        out.append(cur)
    for c in out:
        names = [h[0].rsplit("/", 1)[-1] for h in c["hits"]]
        if not names:
            c["class"] = "none"
        elif any(n.startswith("LT_Enemy_") for n in names):
            c["class"] = "teammate"
        elif any(n.startswith("LT_Player_") for n in names):
            c["class"] = "crew"
        else:
            c["class"] = "static"
        c["level"], c["bodies"] = [], []
        for path, at, n in c["hits"]:
            if c["fma"] is not None:
                length = math.sqrt(sum(v * v for v in n)) or 1.0
                if math.acos(max(-1.0, min(1.0, n[1] / length))) <= c["fma"]:
                    continue
            leaf = path.rsplit("/", 1)[-1]
            (c["bodies"] if leaf.startswith(("LT_Enemy_", "LT_Player_")) else c["level"]).append((path, at, n))
        if c["fma"] is None:
            c["class30"] = "unknown"
        elif c["level"] and c["bodies"]:
            c["class30"] = "level+body"
        elif c["level"]:
            c["class30"] = "level"
        elif c["bodies"]:
            c["class30"] = "body"
        else:
            c["class30"] = "none"
    return out


def lot_mode(ws, mission, seed_name, contacts=False, raw=False):
    lf = F / "workspaces" / ws / ".level_factory"
    name = "%s.laser_tag_evaluate.candidate.%s" % (mission, seed_name)
    seed = _seed(lf / "jobs" / name / "1" / "job.log")
    dst = F / "_scratch" / ("enemy_trace_%s_%s" % (mission, seed_name))
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(lf / "staging" / name, dst)
    shutil.rmtree(dst / "addons" / "laser_tag_tool")
    shutil.copytree(LT_ADDON, dst / "addons" / "laser_tag_tool")
    b = dst / BRAIN
    raw = b.read_bytes()
    eol = b"\r\n" if b"\r\n" in raw else b"\n"
    text = raw.decode("utf-8").replace("\r\n", "\n")
    b.write_bytes(_traced(text).encode("utf-8").replace(b"\n", eol))
    subprocess.run([GODOT, "--headless", "--path", str(dst), "--import"], cwd=str(dst), capture_output=True,
                   text=True, timeout=900, stdin=subprocess.DEVNULL)
    reports, outs = [], []
    for k in (1, 2):
        out = dst / ("report_%d.json" % k)
        r = subprocess.run([GODOT, "--headless", "--fixed-fps", "60", "--path", str(dst), "-s",
                            "res://addons/laser_tag_tool/runners/run_map_eval.gd", "--", "--bake-nav",
                            "--map", "res://level.tscn", "--scenario", "res://mission_scenario.tres",
                            "--runs", "25", "--seed", seed, "--output", str(out)],
                           cwd=str(dst), capture_output=True, text=True, timeout=1800, stdin=subprocess.DEVNULL)
        if not out.exists():
            print("%s %s: NO REPORT (exit %d)" % (mission, seed_name, r.returncode))
            return 1
        reports.append(json.loads(out.read_text(encoding="utf-8")))
        outs.append(r.stdout)
    a, b2 = reports
    same = a["summary"] == b2["summary"] and _stuck(a) == _stuck(b2) and a["grade"] == b2["grade"]
    classes = _classify(outs[0])
    counts = {}
    for c in classes:
        counts[c["class"]] = counts.get(c["class"], 0) + 1
    print("%s %s (seed %s, %s): %s %s, enemy stuck %d, traced %d: %s%s" % (
        mission, seed_name, seed, ws, a["grade"], a["overall_score"], a["summary"]["enemy_stuck_events"],
        len(classes), json.dumps(dict(sorted(counts.items()))),
        "" if same else "   CONTROL FAILED: the two runs differ"))
    if contacts:
        c30 = {}
        for c in classes:
            c30[c["class30"]] = c30.get(c["class30"], 0) + 1
        print("  as 0.30.0 asks (the floor left out): %s; blocked in the report %s" % (
            json.dumps(dict(sorted(c30.items()))), a["summary"].get("enemy_blocked_events", "(no field)")))
        for c in classes:
            print("  %-12s at (%7.2f, %5.2f, %7.2f)  %-10s  %s" % (
                c["who"], c["at"][0], c["at"][1], c["at"][2], c["class30"],
                "; ".join(["%s n (%.2f, %.2f, %.2f)" % ("/".join(p.split("/")[-2:]), n[0], n[1], n[2])
                           for p, _at, n in c["level"]]
                          + ["%s (a body)" % p.rsplit("/", 1)[-1] for p, _at, _n in c["bodies"]]) or "-"))
    if raw:
        for line in outs[0].splitlines():
            if line.startswith("[enemy trace]"):
                print(line)
    if same:
        shutil.rmtree(dst)
    return 0 if same else 1


def main():
    if "--lot" in sys.argv:
        contacts, raw = "--contacts" in sys.argv, "--raw" in sys.argv
        args = [a for a in sys.argv[sys.argv.index("--lot") + 1:] if a not in ("--contacts", "--raw")]
        if len(args) % 3 != 0 or not args:
            sys.exit("usage: --lot [--contacts] [--raw] <workspace> <mission> <seed> [<workspace> <mission> <seed> ...]")
        worst = 0
        for i in range(0, len(args), 3):
            worst = max(worst, lot_mode(*args[i:i + 3], contacts=contacts, raw=raw))
        return worst
    seed = _seed(JOB / "job.log")
    job = json.loads((JOB / "out" / "lasertag.report.json").read_text(encoding="utf-8"))
    if DST.exists():
        shutil.rmtree(DST)
    shutil.copytree(SRC, DST)
    b = DST / BRAIN
    raw = b.read_bytes()
    eol = b"\r\n" if b"\r\n" in raw else b"\n"
    text = raw.decode("utf-8").replace("\r\n", "\n")
    b.write_bytes(_traced(text).encode("utf-8").replace(b"\n", eol))
    out = DST / "report.json"
    subprocess.run([GODOT, "--headless", "--path", str(DST), "--import"], cwd=str(DST), capture_output=True,
                   text=True, timeout=900, stdin=subprocess.DEVNULL)
    r = subprocess.run([GODOT, "--headless", "--fixed-fps", "60", "--path", str(DST), "-s",
                        "res://addons/laser_tag_tool/runners/run_map_eval.gd", "--", "--bake-nav",
                        "--map", "res://level.tscn", "--scenario", "res://mission_scenario.tres",
                        "--runs", "25", "--seed", seed, "--output", str(out)],
                       cwd=str(DST), capture_output=True, text=True, timeout=1800, stdin=subprocess.DEVNULL)
    if not out.exists():
        sys.exit("NO REPORT (exit %d)" % r.returncode)
    copy = json.loads(out.read_text(encoding="utf-8"))
    moved = sorted(k for k in set(job["summary"]) | set(copy["summary"])
                   if job["summary"].get(k) != copy["summary"].get(k))
    print("seed %s; job: %s %s, copy: %s %s" % (seed, job["grade"], job["overall_score"],
                                                 copy["grade"], copy["overall_score"]))
    if moved or _stuck(job) != _stuck(copy) or job["grade"] != copy["grade"]:
        print("CONTROL FAILED: the copy is not the job (summary fields moved: %s; job stuck %s, copy stuck %s)"
              % (", ".join(moved) or "none", _stuck(job), _stuck(copy)))
        return 1
    print("CONTROL HELD: the copy's summary and its EnemyStuck events are the job's: %s" % (_stuck(job),))
    for line in r.stdout.splitlines():
        if line.startswith("[enemy trace]"):
            print(line)
    shutil.rmtree(DST)
    return 0


if __name__ == "__main__":
    sys.exit(main())
