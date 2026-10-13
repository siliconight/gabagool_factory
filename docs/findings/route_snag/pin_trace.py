"""Where a lot's crew bodies pin, and what holds them there, on any staged Laser Tag evaluation (roadmap
242; written for Laser Tag 0.28.0's draft, whose bank_block_001 lot pinned where 0.27.0 had not).

    python docs/findings/route_snag/pin_trace.py census <workspace> <mission> <seed_N> [--addon DIR] [--jolt]
    python docs/findings/route_snag/pin_trace.py trace  <workspace> <mission> <seed_N> --run R --who NAME \\
        --at X,Y,Z [--addon DIR] [--jolt]

`snag_trace.py` answered one counter on one lot with its paths written in. This takes the lot as
arguments. Both modes copy the job's staged project to `_scratch/pin_trace/`, drop in a Laser Tag addon
(the repository's, or `--addon`: the draft's), name Jolt if asked, import, and run the job's command.

  census   the job's 25 runs from its seed: the report's summary, then every player-stuck place to a
           millimetre (the report's full-precision `metadata.position`) with its count, runs, first
           times and bodies; a PIN is a place recurring in two or more runs (`engine_breadth.py`'s
           count). The report is kept beside the copies for `trace`'s control.
  census --why   the same 25 runs with every bot counting, since its stuck window last closed, its
           frames and those it had an enemy in sight -- `_update_stuck` asks about an enemy only as
           the window closes, so a bot that stood to fight (`advance_while_engaging` off: it stops)
           and lost sight of its enemy at that instant reads as stuck. Each stuck event is printed
           beside that count. THE CONTROL: the instrumented run's stuck events must be the plain
           census's, time, body and position, or the prints moved the run and it says so.
  trace    ONE run, R, of the same command (`--runs 1 --seed N+R-1`: the job's run R, as snag_trace.py
           found run i seeds with N + i - 1), its bot controller instrumented in the COPY only: while
           body NAME stands within 5 cm of X,Y,Z, up to six frames of `move_and_slide` -- position
           and velocity before and after, floor and wall, each slide's collider, point, normal and
           travel -- and on the first, the navigation path ahead, the colliders within a 1.2 m box at
           the body's height, and (0.28.0's `_velocity_on_mesh`, if the addon has it) the step it
           asked for, the mesh's nearest point and the velocity it returned. `--wide M`: also,
           every third tick while the body is within M metres of X,Y,Z (400 lines at most), its
           position, velocity, path index and next point (read off the path, never
           `get_next_path_position`, which advances it), target, route point, cover and enemy.
           THE CONTROL: the copy's first stuck event must be the census's first stuck event of run R
           -- time, body and position as the report keeps them. If not, the trace is not the job's
           and it says so.

It prints what it measured and stops. Copies are removed; the census report is kept until the next
census of the same lot.
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
SCR = F / "_scratch" / "pin_trace"
BOT = "addons/laser_tag_tool/scripts/player/LT_BotPlayerController.gd"
SLIDE_OLD = ("\tvar intended := Vector3(body.velocity.x, 0.0, body.velocity.z)\n"
             "\tbody.move_and_slide()\n"
             "\t_try_step_up(intended)\n")
SLIDE_NEW = """\tvar intended := Vector3(body.velocity.x, 0.0, body.velocity.z)
\tvar dbg_before: Vector3 = body.global_position
\tvar dbg_vel: Vector3 = body.velocity
\tvar dbg_here: bool = String(body.name) == "__WHO__" and dbg_before.distance_to(__AT__) < 0.05
\tvar dbg_n: int = int(get_meta("dbg_n", 0))
\tif dbg_here and dbg_n == 0:
\t\tvar path: PackedVector3Array = nav_agent.get_current_navigation_path() if nav_agent != null else PackedVector3Array()
\t\tvar idx: int = nav_agent.get_current_navigation_path_index() if nav_agent != null else -1
\t\tvar shown: PackedStringArray = PackedStringArray()
\t\tfor k in range(maxi(idx - 1, 0), mini(path.size(), idx + 6)):
\t\t\tshown.append("%d(%.3f,%.3f,%.3f)" % [k, path[k].x, path[k].y, path[k].z])
\t\tprint("[LT pin] path index %d of %d, target %s: %s" % [idx, path.size(),
\t\t\tstr(nav_agent.target_position) if nav_agent != null else "?", " ".join(shown)])
\t\tvar q := PhysicsShapeQueryParameters3D.new()
\t\tvar bx := BoxShape3D.new()
\t\tbx.size = Vector3(1.2, 1.2, 1.2)
\t\tq.shape = bx
\t\tq.transform = Transform3D(Basis(), dbg_before + Vector3(0.0, 0.9, 0.0))
\t\tq.exclude = [body.get_rid()]
\t\tfor hit_d in body.get_world_3d().direct_space_state.intersect_shape(q, 32):
\t\t\tvar hc: Object = hit_d["collider"]
\t\t\tprint("[LT pin] within 1.2 m at body height: %s shape %d" % [
\t\t\t\tstr(hc.get_path()) if hc is Node else str(hc), int(hit_d["shape"])])
\tbody.move_and_slide()
\tif dbg_here and dbg_n < 6:
\t\tset_meta("dbg_n", dbg_n + 1)
\t\tprint("[LT pin] tick %d before %s vel %s -> after %s real %s floor %s wall %s slides %d" % [
\t\t\tEngine.get_physics_frames(), str(dbg_before), str(dbg_vel), str(body.global_position),
\t\t\tstr(body.get_real_velocity()), str(body.is_on_floor()), str(body.is_on_wall()),
\t\t\tbody.get_slide_collision_count()])
\t\tfor k in range(body.get_slide_collision_count()):
\t\t\tvar sc: KinematicCollision3D = body.get_slide_collision(k)
\t\t\tvar sco: Object = sc.get_collider()
\t\t\tprint("[LT pin]   %s at %s normal %s travel %s" % [
\t\t\t\tstr(sco.get_path()) if sco is Node else str(sco), str(sc.get_position()),
\t\t\t\tstr(sc.get_normal()), str(sc.get_travel())])
\tif __WIDE__ > 0.0 and String(body.name) == "__WHO__" and body.global_position.distance_to(__AT__) < __WIDE__ \\
\t\t\tand int(get_meta("dbg_w", 0)) < 400 and Engine.get_physics_frames() % 3 == 0:
\t\tset_meta("dbg_w", int(get_meta("dbg_w", 0)) + 1)
\t\tvar wp: PackedVector3Array = nav_agent.get_current_navigation_path() if nav_agent != null else PackedVector3Array()
\t\tvar wi: int = nav_agent.get_current_navigation_path_index() if nav_agent != null else -1
\t\tvar nxt: String = "-"
\t\tif wi >= 0 and wi < wp.size():
\t\t\tnxt = "(%.2f,%.2f,%.2f)" % [wp[wi].x, wp[wi].y, wp[wi].z]
\t\tvar gp: Vector3 = body.global_position
\t\tprint("[LT wide] tick %d pos (%.2f,%.2f,%.2f) vel (%.2f,%.2f) path %d/%d next %s target %s route %d cover %s enemy %s" % [
\t\t\tEngine.get_physics_frames(), gp.x, gp.y, gp.z, body.velocity.x, body.velocity.z, wi, wp.size(), nxt,
\t\t\tstr(nav_agent.target_position) if nav_agent != null else "-", _route_index, str(_seeking_cover),
\t\t\tstr(enemy != null)])
\t_try_step_up(intended)
"""
#: `census --why`: every bot counts its frames and the frames it had an enemy in sight since its stuck
#: window last closed, and says so when the window closes as a stuck event -- the detector asks about
#: an enemy only at that instant (`_update_stuck`), so a bot that stood to fight all window and lost
#: sight of its enemy as the window closed reads as stuck. Prints only; the report must not move.
ENEMY_OLD = "\tvar enemy := _find_visible_enemy()\n"
ENEMY_NEW = ENEMY_OLD + ("\tset_meta(\"dbg_frames\", int(get_meta(\"dbg_frames\", 0)) + 1)\n"
                         "\tif enemy != null:\n"
                         "\t\tset_meta(\"dbg_eng\", int(get_meta(\"dbg_eng\", 0)) + 1)\n")
STUCK_OLD = "\t\tvar moved := body.global_position.distance_to(_stuck_anchor)\n"
STUCK_NEW = STUCK_OLD + (
    "\t\tif moved < stuck_distance_threshold and _find_visible_enemy() == null:\n"
    "\t\t\tprint(\"[LT stuck] %s (%.2f, %.2f, %.2f) moved %.3f m, an enemy in sight %d of %d frames\" % [\n"
    "\t\t\t\tbody.name, body.global_position.x, body.global_position.y, body.global_position.z, moved,\n"
    "\t\t\t\tint(get_meta(\"dbg_eng\", 0)), int(get_meta(\"dbg_frames\", 0))])\n")
#: the window's close, anchored on the line before it: Laser Tag 0.28.0's restart (below) has the same
#: two lines, and an anchor that matched both would be refused
RESET_OLD = ("\t\t\t_go_to_current_route_point()\n"
             "\t\t_stuck_timer = 0.0\n\t\t_stuck_anchor = body.global_position\n")
RESET_NEW = RESET_OLD + "\t\tset_meta(\"dbg_eng\", 0)\n\t\tset_meta(\"dbg_frames\", 0)\n"
#: 0.28.0's restart on a stand to fight, when the addon has it: the counters restart with the window
RESTART_OLD = ("\tif standing_to_fight:\n\t\t_stuck_timer = 0.0\n"
               "\t\t_stuck_anchor = body.global_position\n\t\treturn\n")
RESTART_NEW = ("\tif standing_to_fight:\n\t\t_stuck_timer = 0.0\n"
               "\t\t_stuck_anchor = body.global_position\n"
               "\t\tset_meta(\"dbg_eng\", 0)\n\t\tset_meta(\"dbg_frames\", 0)\n\t\treturn\n")
#: 0.28.1's one restart, `_restart_stuck_window`, which a stand to fight and an arrival both call
RESTART2_OLD = "func _restart_stuck_window() -> void:\n\t_stuck_timer = 0.0\n\t_stuck_anchor = body.global_position\n"
RESTART2_NEW = RESTART2_OLD + "\tset_meta(\"dbg_eng\", 0)\n\tset_meta(\"dbg_frames\", 0)\n"
MESH_OLD = "\tvar to_mesh: Vector3 = Vector3(on.x - here.x, 0.0, on.z - here.z) / delta\n"
MESH_NEW = MESH_OLD + """\tif String(body.name) == "__WHO__" and here.distance_to(__AT__) < 0.05 and int(get_meta("dbg_m", 0)) < 6:
\t\tset_meta("dbg_m", int(get_meta("dbg_m", 0)) + 1)
\t\tprint("[LT mesh] asked %s from %s: want %s, the mesh's nearest %s (lift %.3f), returns toward it %s" % [
\t\t\tstr(velocity), str(here), str(want), str(on), lift, str(to_mesh)])
"""


def _args():
    a = sys.argv[1:]
    if len(a) < 4 or a[0] not in ("census", "trace"):
        sys.exit(__doc__)
    opts = {"mode": a[0], "ws": a[1], "mission": a[2], "seed": a[3], "addon": None, "jolt": "--jolt" in a,
            "why": "--why" in a}
    for flag in ("--addon", "--run", "--who", "--at", "--wide"):
        if flag in a:
            opts[flag[2:]] = a[a.index(flag) + 1]
    if opts["mode"] == "trace" and not all(opts.get(k) for k in ("run", "who", "at")):
        sys.exit("trace needs --run, --who and --at")
    return opts


def _job_seed(job_log):
    first = job_log.read_text(encoding="utf-8", errors="replace").splitlines()[0]
    m = re.search(r"--seed (\d+)", first)
    if not m:
        sys.exit("UNKNOWN SHAPE: no --seed in %s" % job_log)
    return int(m.group(1))


def _stage(o, name, src):
    addon = pathlib.Path(o["addon"]) if o["addon"] else F / "lasertag" / "addons" / "laser_tag_tool"
    if not (addon / "runners" / "run_map_eval.gd").exists():
        sys.exit("no Laser Tag addon at %s" % addon)
    version = addon.parent.parent / "VERSION"
    print("Laser Tag addon: %s (%s)%s" % (addon, version.read_text().strip() if version.exists() else "?",
                                          ", Jolt Physics" if o["jolt"] else ""), flush=True)
    dst = SCR / name
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst)
    shutil.rmtree(dst / "addons" / "laser_tag_tool")
    shutil.copytree(addon, dst / "addons" / "laser_tag_tool")
    if o["jolt"]:
        pg = dst / "project.godot"
        text = pg.read_text(encoding="utf-8")
        if "3d/physics_engine" in text:
            sys.exit("UNKNOWN SHAPE: %s already names a physics engine" % pg)
        pg.write_text(text.rstrip("\n") + '\n\n[physics]\n\n3d/physics_engine="Jolt Physics"\n',
                      encoding="utf-8", newline="\n")
    return dst


def _run(dst, runs, seed, out, trace=False):
    subprocess.run([GODOT, "--headless", "--path", str(dst), "--import"], cwd=str(dst), capture_output=True,
                   text=True, timeout=900, stdin=subprocess.DEVNULL)
    cmd = [GODOT, "--headless", "--fixed-fps", "60", "--path", str(dst), "-s",
           "res://addons/laser_tag_tool/runners/run_map_eval.gd", "--", "--bake-nav",
           "--map", "res://level.tscn", "--scenario", "res://mission_scenario.tres",
           "--runs", str(runs), "--seed", str(seed), "--output", str(out)]
    return subprocess.run(cmd, cwd=str(dst), capture_output=True, text=True, timeout=1800,
                          stdin=subprocess.DEVNULL)


def _places(report):
    at = collections.defaultdict(list)
    for e in report["events"]:
        if e["event"] != "PlayerStuck":
            continue
        full = e.get("metadata", {}).get("position")
        if full is None:
            sys.exit("UNKNOWN SHAPE: a PlayerStuck event without metadata.position: %r" % sorted(e))
        at[tuple(round(v, 3) for v in full)].append(e)
    return at


def _why(dst):
    b = dst / BOT
    raw = b.read_bytes()
    eol = b"\r\n" if b"\r\n" in raw else b"\n"
    text = raw.decode("utf-8").replace("\r\n", "\n")
    for old, new in ((ENEMY_OLD, ENEMY_NEW), (STUCK_OLD, STUCK_NEW), (RESET_OLD, RESET_NEW)):
        if text.count(old) != 1:
            sys.exit("UNKNOWN SHAPE: %d of %r in the copy's bot controller" % (text.count(old), old[:40]))
        text = text.replace(old, new)
    for old, new in ((RESTART_OLD, RESTART_NEW), (RESTART2_OLD, RESTART2_NEW)):
        if text.count(old) > 1:
            sys.exit("UNKNOWN SHAPE: %d of a window restart %r" % (text.count(old), old[:30]))
        text = text.replace(old, new)
    b.write_bytes(text.encode("utf-8").replace(b"\n", eol))


def census(o, name, src, n):
    tag = "%s_%s%s" % (name, "jolt" if o["jolt"] else "godot", "_addon" if o["addon"] else "")
    dst = _stage(o, tag + ("_why" if o["why"] else ""), src)
    if o["why"]:
        _why(dst)
    out = SCR / (tag + (".why" if o["why"] else "") + ".census.json")
    proc = _run(dst, 25, n, out)
    shutil.rmtree(dst)
    if not out.exists():
        print("NOT MEASURED: no report (exit %d)" % proc.returncode)
        return 2
    r = json.loads(out.read_text(encoding="utf-8"))
    if o["why"]:
        return _why_report(r, proc.stdout, SCR / (tag + ".census.json"))
    s = r["summary"]
    print("%s, 25 runs from seed %d: %s %s, route %s, player stuck %s, enemy stuck %s, deaths %s" % (
        name, n, r["grade"], r["overall_score"], s["route_completion_rate"], s["player_stuck_events"],
        s["enemy_stuck_events"], s["player_deaths"]))
    at = _places(r)
    for pos, es in sorted(at.items(), key=lambda kv: -len(kv[1])):
        runs = sorted({e["run_id"] for e in es})
        print("  %s (%.3f, %.3f, %.3f): %d events in runs %s, first at t %s by %s" % (
            "PIN  " if len(runs) >= 2 else "once ", pos[0], pos[1], pos[2], len(es), runs,
            ", ".join("%s r%d" % (e["time"], e["run_id"]) for e in es[:3]),
            ", ".join(sorted({e["source"] for e in es}))))
    print("census report kept: %s" % out)
    return 0


def _why_report(r, stdout, plain):
    """Each stuck event beside what its bot saw in the window that closed on it."""
    said = [ln for ln in stdout.splitlines() if ln.startswith("[LT stuck] ")]
    events = [e for e in r["events"] if e["event"] == "PlayerStuck"]
    if len(said) != len(events):
        print("UNKNOWN SHAPE: %d stuck lines printed for %d stuck events" % (len(said), len(events)))
        return 2
    if plain.exists():
        p = [(e["time"], e["source"], e["position"]) for e in json.loads(plain.read_text(encoding="utf-8"))["events"]
             if e["event"] == "PlayerStuck"]
        held = p == [(e["time"], e["source"], e["position"]) for e in events]
        print("the control: the instrumented census's stuck events %s the plain census's (%d against %d)" % (
            "ARE" if held else "ARE NOT", len(events), len(p)))
        if not held:
            return 1
    else:
        print("no plain census to hold this one against at %s: run census without --why first" % plain)
        return 2
    fought = 0
    for e, ln in zip(events, said):
        m = re.search(r"^\[LT stuck\] (\S+) \(([-\d.]+), ([-\d.]+), ([-\d.]+)\) moved ([\d.]+) m, "
                      r"an enemy in sight (\d+) of (\d+) frames$", ln)
        if m is None or m.group(1) != e["source"]:
            print("UNKNOWN SHAPE: %r against the event %r" % (ln, e))
            return 2
        seen, frames = int(m.group(6)), int(m.group(7))
        fought += seen * 2 >= frames
        print("  run %2d t %5.1f %s at (%s, %s, %s): moved %s m, an enemy in sight %d of %d frames" % (
            e["run_id"], e["time"], e["source"], m.group(2), m.group(3), m.group(4), m.group(5), seen, frames))
    print("%d stuck events; %d of them closed a window the bot spent at least half in sight of an enemy" % (
        len(events), fought))
    return 0


def trace(o, name, src, n):
    tag = "%s_%s%s" % (name, "jolt" if o["jolt"] else "godot", "_addon" if o["addon"] else "")
    kept = SCR / (tag + ".census.json")
    if not kept.exists():
        sys.exit("no census for this lot and arm at %s: run census first" % kept)
    run = int(o["run"])
    at = "Vector3(%s)" % o["at"]
    dst = _stage(o, tag + "_trace", src)
    b = dst / BOT
    raw = b.read_bytes()
    eol = b"\r\n" if b"\r\n" in raw else b"\n"
    text = raw.decode("utf-8").replace("\r\n", "\n")
    if text.count(SLIDE_OLD) != 1:
        sys.exit("UNKNOWN SHAPE: %d of the slide in the copy's bot controller" % text.count(SLIDE_OLD))
    text = text.replace(SLIDE_OLD, SLIDE_NEW.replace("__WHO__", o["who"]).replace("__AT__", at)
                        .replace("__WIDE__", "%.3f" % float(o.get("wide") or 0.0)))
    if text.count(MESH_OLD) == 1:
        text = text.replace(MESH_OLD, MESH_NEW.replace("__WHO__", o["who"]).replace("__AT__", at))
        print("instrumented: the slide and _velocity_on_mesh")
    elif (dst / "addons/laser_tag_tool/scripts/core/LT_Steering.gd").exists():
        # Laser Tag 0.31.0 moved the step's body into `LT_Steering`, a static function with no node of its
        # own to ask `get_meta`, so the mesh step is not instrumented there
        print("instrumented: the slide (this addon's _velocity_on_mesh calls LT_Steering, not instrumented)")
    else:
        print("instrumented: the slide (this addon has no _velocity_on_mesh)")
    b.write_bytes(text.encode("utf-8").replace(b"\n", eol))
    out = dst / "report.json"
    proc = _run(dst, 1, n + run - 1, out)
    for line in proc.stdout.splitlines():
        if line.startswith("[LT pin]") or line.startswith("[LT mesh]") or line.startswith("[LT wide]"):
            print(line)
    if not out.exists():
        print("NOT MEASURED: no report (exit %d)" % proc.returncode)
        shutil.rmtree(dst)
        return 2
    mine = [e for e in json.loads(out.read_text(encoding="utf-8"))["events"] if e["event"] == "PlayerStuck"]
    theirs = [e for e in json.loads(kept.read_text(encoding="utf-8"))["events"]
              if e["event"] == "PlayerStuck" and e["run_id"] == run]
    first = lambda es: (es[0]["time"], es[0]["source"], es[0]["position"]) if es else None
    print("stuck events, run %d: this copy %d, the census %d" % (run, len(mine), len(theirs)))
    print("  first here:      %s" % (first(mine),))
    print("  first in census: %s" % (first(theirs),))
    shutil.rmtree(dst)
    if first(mine) != first(theirs):
        print("CONTROL FAILED: the copy did not reproduce the census's run %d; its trace is not the census's" % run)
        return 1
    print("control held: the copy reproduces the census's run %d" % run)
    return 0


def main():
    o = _args()
    lf = F / "workspaces" / o["ws"] / ".level_factory"
    name = "%s.laser_tag_evaluate.candidate.%s" % (o["mission"], o["seed"])
    src = lf / "staging" / name
    if not src.is_dir():
        sys.exit("no staged project at %s" % src)
    n = _job_seed(lf / "jobs" / name / "1" / "job.log")
    short = "%s_%s" % (o["mission"], o["seed"])
    SCR.mkdir(parents=True, exist_ok=True)
    return census(o, short, src, n) if o["mode"] == "census" else trace(o, short, src, n)


if __name__ == "__main__":
    sys.exit(main())
