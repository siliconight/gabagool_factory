"""Where seed_9104's crew member stands frozen, and which way its path points, read off Laser Tag's own
bot (roadmap 242).

    python docs/findings/route_snag/snag_trace.py [run]

Cold run 9263's Laser Tag job read 72 player-stuck events on restaurant_row_001 seed_9104, 64 of them
at ONE point to fifteen digits -- Godot (-66.35009, 0.00094, 4.94045), plan (-66.35, -4.94), inside
the deli (b0) on its ground floor, one body radius (0.35 m) west of the front register counter's
west end and level with its south face. A body that never moves, not a body wedged anew each time.

This copies the job's staged project (`staging/...laser_tag_evaluate.candidate.seed_9104`) to
`_scratch/snag_trace/`, changes the COPY's harness only -- its trace snapshots at 60, 66, 70, 71.5
and 73 s of the first run instead of 0.5 to 20 s, and each bot's line followed by the first points
of its current navigation path and the index it is on -- and runs the job's own command for one run
(`--runs 1 --seed 9104`: run i seeds with 9104 + i, so this is the job's run 1, which held the first
of the 64 at t 72.0).

THE CONTROL: the copy must reproduce the job's own first stuck event -- LT_Player_04 at t 72.0 at
the same position to the digits the report keeps. If it does not, the copy is not the job and its
trace says nothing about the job; the probe says so and stops. It prints what it measured and stops.
"""
import json
import pathlib
import shutil
import subprocess
import sys

F = pathlib.Path(__file__).resolve().parents[3]
WS = F / "workspaces" / "cold-9263-ws" / ".level_factory"
SRC = WS / "staging" / "restaurant_row_001.laser_tag_evaluate.candidate.seed_9104"
JOB_REPORT = WS / "jobs" / "restaurant_row_001.laser_tag_evaluate.candidate.seed_9104" / "1" / "out" / "lasertag.report.json"
DST = F / "_scratch" / "snag_trace"
GODOT = "C:/Godot/4.7/Godot_v4.7-stable_win64_console.exe"
HARNESS = "addons/laser_tag_tool/scripts/core/LT_MapEvalHarness.gd"

MARKS_OLD = "_trace_marks = [0.5, 2.0, 5.0, 10.0, 20.0]"
MARKS_NEW = "_trace_marks = [60.0, 66.0, 70.0, 71.5, 73.0]"
LINE_OLD = '\t\t\tprint("[LT trace]   " + bot.debug_status())\n'
LINE_NEW = ('\t\t\tprint("[LT trace]   " + bot.debug_status())\n'
            '\t\t\tvar agent: NavigationAgent3D = bot.get("nav_agent")\n'
            '\t\t\tif agent != null:\n'
            '\t\t\t\tvar path: PackedVector3Array = agent.get_current_navigation_path()\n'
            '\t\t\t\tvar shown: PackedStringArray = PackedStringArray()\n'
            '\t\t\t\tfor k in range(mini(path.size(), 8)):\n'
            '\t\t\t\t\tshown.append("(%.2f,%.2f,%.2f)" % [path[k].x, path[k].y, path[k].z])\n'
            '\t\t\t\tprint("[LT trace]     path index %d of %d, target %s: %s" % [\n'
            '\t\t\t\t\tagent.get_current_navigation_path_index(), path.size(),\n'
            '\t\t\t\t\tstr(agent.target_position), " ".join(shown)])\n'
            '\t\t\tvar body: CharacterBody3D = bot.get("body")\n'
            '\t\t\tif body != null and body.velocity.length() > 0.1:\n'
            '\t\t\t\tvar dir: Vector3 = Vector3(body.velocity.x, 0.0, body.velocity.z).normalized()\n'
            '\t\t\t\tprint("[LT trace]     on floor %s, floor normal %s, wall %s" % [\n'
            '\t\t\t\t\tstr(body.is_on_floor()), str(body.get_floor_normal()), str(body.is_on_wall())])\n'
            '\t\t\t\tvar slab: Node = get_tree().root.get_node_or_null("site_walk/Nav/Site/b0/slab_col_0")\n'
            '\t\t\t\tif slab != null and String(body.name) == "LT_Player_04":\n'
            '\t\t\t\t\tfor cs in slab.find_children("*", "CollisionShape3D", true, false):\n'
            '\t\t\t\t\t\tvar shp: Shape3D = (cs as CollisionShape3D).shape\n'
            '\t\t\t\t\t\tvar xf: Transform3D = (cs as Node3D).global_transform\n'
            '\t\t\t\t\t\tprint("[LT trace]     slab_col_0 shape %s, %s" % [shp.get_class(), str(xf.origin)])\n'
            '\t\t\t\t\t\tif shp is ConcavePolygonShape3D:\n'
            '\t\t\t\t\t\t\tvar faces: PackedVector3Array = (shp as ConcavePolygonShape3D).get_faces()\n'
            '\t\t\t\t\t\t\tvar p: Vector3 = body.global_position\n'
            '\t\t\t\t\t\t\tvar shown_t: int = 0\n'
            '\t\t\t\t\t\t\tfor t in range(0, faces.size(), 3):\n'
            '\t\t\t\t\t\t\t\tvar a: Vector3 = xf * faces[t]\n'
            '\t\t\t\t\t\t\t\tvar b: Vector3 = xf * faces[t + 1]\n'
            '\t\t\t\t\t\t\t\tvar c: Vector3 = xf * faces[t + 2]\n'
            '\t\t\t\t\t\t\t\tvar cen: Vector3 = (a + b + c) / 3.0\n'
            '\t\t\t\t\t\t\t\tvar lo: Vector2 = Vector2(minf(a.x, minf(b.x, c.x)), minf(a.z, minf(b.z, c.z)))\n'
            '\t\t\t\t\t\t\t\tvar hi: Vector2 = Vector2(maxf(a.x, maxf(b.x, c.x)), maxf(a.z, maxf(b.z, c.z)))\n'
            '\t\t\t\t\t\t\t\tif p.x > lo.x - 0.6 and p.x < hi.x + 0.6 and p.z > lo.y - 0.6 and p.z < hi.y + 0.6:\n'
            '\t\t\t\t\t\t\t\t\tshown_t += 1\n'
            '\t\t\t\t\t\t\t\t\tif shown_t <= 24:\n'
            '\t\t\t\t\t\t\t\t\t\tprint("[LT trace]       tri %s %s %s" % [str(a), str(b), str(c)])\n'
            '\t\t\t\t\t\t\tprint("[LT trace]     slab_col_0: %d triangles, %d within 0.6 m of the body" % [faces.size() / 3, shown_t])\n'
            '\t\t\t\tif String(body.name) == "LT_Player_04":\n'
            '\t\t\t\t\tvar q := PhysicsShapeQueryParameters3D.new()\n'
            '\t\t\t\t\tvar bx := BoxShape3D.new()\n'
            '\t\t\t\t\tbx.size = Vector3(1.6, 0.06, 1.6)\n'
            '\t\t\t\t\tq.shape = bx\n'
            '\t\t\t\t\tq.transform = Transform3D(Basis(), body.global_position)\n'
            '\t\t\t\t\tq.exclude = [body.get_rid()]\n'
            '\t\t\t\t\tfor hit_d in body.get_world_3d().direct_space_state.intersect_shape(q, 32):\n'
            '\t\t\t\t\t\tvar hc: Object = hit_d["collider"]\n'
            '\t\t\t\t\t\tprint("[LT trace]     at the feet (1.6 x 0.06 x 1.6 m): %s shape %d" % [\n'
            '\t\t\t\t\t\t\tstr(hc.get_path()) if hc is Node else str(hc), int(hit_d["shape"])])\n'
            '\t\t\t\tfor lift in [0.002, 0.005, 0.01, 0.02, 0.05, 0.15]:\n'
            '\t\t\t\t\tvar params := PhysicsTestMotionParameters3D.new()\n'
            '\t\t\t\t\tparams.from = body.global_transform.translated(Vector3(0.0, float(lift), 0.0))\n'
            '\t\t\t\t\tparams.motion = dir * 0.3\n'
            '\t\t\t\t\tparams.max_collisions = 4\n'
            '\t\t\t\t\tvar res := PhysicsTestMotionResult3D.new()\n'
            '\t\t\t\t\tvar hit_any: bool = PhysicsServer3D.body_test_motion(body.get_rid(), params, res)\n'
            '\t\t\t\t\tif not hit_any:\n'
            '\t\t\t\t\t\tprint("[LT trace]     lifted %.2f m, 0.3 m along %s: free" % [float(lift), str(dir)])\n'
            '\t\t\t\t\t\tcontinue\n'
            '\t\t\t\t\tfor c in range(res.get_collision_count()):\n'
            '\t\t\t\t\t\tvar hit: Object = res.get_collider(c)\n'
            '\t\t\t\t\t\tvar hit_name: String = str(hit.get_path()) if hit is Node else str(hit)\n'
            '\t\t\t\t\t\tprint("[LT trace]     lifted %.2f m, 0.3 m along %s: hits %s at %s normal %s after %.3f m" % [\n'
            '\t\t\t\t\t\t\tfloat(lift), str(dir), hit_name, str(res.get_collision_point(c)),\n'
            '\t\t\t\t\t\t\tstr(res.get_collision_normal(c)), res.get_travel().length()])\n')


BOT = "addons/laser_tag_tool/scripts/player/LT_BotPlayerController.gd"
SLIDE_OLD = ("\tvar intended := Vector3(body.velocity.x, 0.0, body.velocity.z)\n"
             "\tbody.move_and_slide()\n"
             "\t_try_step_up(intended)\n")
SLIDE_NEW = ("\tvar intended := Vector3(body.velocity.x, 0.0, body.velocity.z)\n"
             "\tvar dbg_before: Vector3 = body.global_position\n"
             "\tvar dbg_vel: Vector3 = body.velocity\n"
             "\tbody.move_and_slide()\n"
             "\tif String(body.name) == \"LT_Player_04\" and dbg_before.distance_to(Vector3(-66.35, 0.0, 4.94)) < 0.05 \\\n"
             "\t\t\tand int(get_meta(\"dbg_n\", 0)) < 5:\n"
             "\t\tset_meta(\"dbg_n\", int(get_meta(\"dbg_n\", 0)) + 1)\n"
             "\t\tprint(\"[LT slide] tick %d before %s vel %s -> after %s real %s floor %s wall %s slides %d\" % [\n"
             "\t\t\tEngine.get_physics_frames(), str(dbg_before), str(dbg_vel), str(body.global_position),\n"
             "\t\t\tstr(body.get_real_velocity()), str(body.is_on_floor()), str(body.is_on_wall()),\n"
             "\t\t\tbody.get_slide_collision_count()])\n"
             "\t\tfor k in range(body.get_slide_collision_count()):\n"
             "\t\t\tvar sc: KinematicCollision3D = body.get_slide_collision(k)\n"
             "\t\t\tvar sco: Object = sc.get_collider()\n"
             "\t\t\tprint(\"[LT slide]   %s at %s normal %s travel %s remainder %s\" % [\n"
             "\t\t\t\tstr(sco.get_path()) if sco is Node else str(sco), str(sc.get_position()),\n"
             "\t\t\t\tstr(sc.get_normal()), str(sc.get_travel()), str(sc.get_remainder())])\n"
             "\t_try_step_up(intended)\n")
#: THE SLAB ARM (`--swap`): after five pinned frames, slab_col_0's trimesh is swapped for a box of the
#: slab's bounds with the same top (38 x 0.3 x 28 m about the shape's own origin, top at y 0), and the
#: next seven frames are logged. If the body walks off, the trimesh pinned it.
SWAP_BLOCK = ("\tvar dbg_k: int = int(get_meta(\"dbg_n\", 0))\n"
              "\tif String(body.name) == \"LT_Player_04\" and dbg_k >= 5 and dbg_k < 12:\n"
              "\t\tif dbg_k == 5:\n"
              "\t\t\tvar slab: Node = get_tree().root.get_node_or_null(\"site_walk/Nav/Site/b0/slab_col_0\")\n"
              "\t\t\tfor cs in slab.find_children(\"*\", \"CollisionShape3D\", true, false):\n"
              "\t\t\t\tvar bx := BoxShape3D.new()\n"
              "\t\t\t\tbx.size = Vector3(38.0, 0.3, 28.0)\n"
              "\t\t\t\t(cs as CollisionShape3D).shape = bx\n"
              "\t\t\tprint(\"[LT slide] SWAPPED slab_col_0's trimesh for a 38 x 0.3 x 28 box, the same top\")\n"
              "\t\tset_meta(\"dbg_n\", dbg_k + 1)\n"
              "\t\tprint(\"[LT slide] after the swap, tick %d: before %s -> after %s, real %s\" % [\n"
              "\t\t\tEngine.get_physics_frames(), str(dbg_before), str(body.global_position),\n"
              "\t\t\tstr(body.get_real_velocity())])\n")
#: THE COUNTER ARM (`--counter`): after five pinned frames the front register counter's collision is
#: disabled, and the next seven frames are logged with their slide collisions. If the body walks off,
#: the counter's corner held it.
COUNTER_BLOCK = ("\tvar dbg_c: int = int(get_meta(\"dbg_n\", 0))\n"
                 "\tif String(body.name) == \"LT_Player_04\" and dbg_c >= 5 and dbg_c < 12:\n"
                 "\t\tif dbg_c == 5:\n"
                 "\t\t\tvar ctr: Node = get_tree().root.get_node_or_null(\"site_walk/Nav/Site/b0/front_register_counter_col\")\n"
                 "\t\t\tfor cs in ctr.find_children(\"*\", \"CollisionShape3D\", true, false):\n"
                 "\t\t\t\t(cs as CollisionShape3D).disabled = true\n"
                 "\t\t\t\tprint(\"[LT slide] DISABLED %s, a %s at %s\" % [str(cs.get_path()),\n"
                 "\t\t\t\t\t(cs as CollisionShape3D).shape.get_class(), str((cs as Node3D).global_transform.origin)])\n"
                 "\t\tset_meta(\"dbg_n\", dbg_c + 1)\n"
                 "\t\tprint(\"[LT slide] counter off, tick %d: before %s -> after %s, real %s, slides %d\" % [\n"
                 "\t\t\tEngine.get_physics_frames(), str(dbg_before), str(body.global_position),\n"
                 "\t\t\tstr(body.get_real_velocity()), body.get_slide_collision_count()])\n"
                 "\t\tfor k in range(body.get_slide_collision_count()):\n"
                 "\t\t\tvar sc2: KinematicCollision3D = body.get_slide_collision(k)\n"
                 "\t\t\tvar sco2: Object = sc2.get_collider()\n"
                 "\t\t\tprint(\"[LT slide]   %s normal %s travel %s\" % [\n"
                 "\t\t\t\tstr(sco2.get_path()) if sco2 is Node else str(sco2), str(sc2.get_normal()),\n"
                 "\t\t\t\tstr(sc2.get_travel())])\n")


def main():
    if DST.exists():
        shutil.rmtree(DST)
    shutil.copytree(SRC, DST)
    b = DST / BOT
    braw = b.read_bytes()
    beol = b"\r\n" if b"\r\n" in braw else b"\n"
    btext = braw.decode("utf-8").replace("\r\n", "\n")
    if btext.count(SLIDE_OLD) != 1:
        sys.exit("UNKNOWN SHAPE: %d of the slide in the copy's bot controller" % btext.count(SLIDE_OLD))
    new = SLIDE_NEW
    if "--swap" in sys.argv:
        new = SLIDE_NEW.replace("\t_try_step_up(intended)\n", SWAP_BLOCK + "\t_try_step_up(intended)\n")
        print("THE SLAB ARM: slab_col_0's trimesh swapped for a box after five pinned frames")
    if "--counter" in sys.argv:
        new = SLIDE_NEW.replace("\t_try_step_up(intended)\n", COUNTER_BLOCK + "\t_try_step_up(intended)\n")
        print("THE COUNTER ARM: the front register counter's collision disabled after five pinned frames")
    if "--jolt" in sys.argv:
        # THE ENGINE ARM: the copy's project runs Jolt, Godot 4.7's other 3D physics engine; nothing
        # else changes. The staged project names no engine, so it runs the default, Godot Physics.
        pg = DST / "project.godot"
        ptext = pg.read_text(encoding="utf-8")
        if "3d/physics_engine" in ptext:
            sys.exit("UNKNOWN SHAPE: the staged project already names a physics engine")
        pg.write_text(ptext.rstrip("\n") + '\n\n[physics]\n\n3d/physics_engine="Jolt Physics"\n',
                      encoding="utf-8", newline="\n")
        print("THE ENGINE ARM: the copy runs Jolt Physics")
    b.write_bytes(btext.replace(SLIDE_OLD, new).encode("utf-8").replace(b"\n", beol))
    h = DST / HARNESS
    raw = h.read_bytes()
    eol = b"\r\n" if b"\r\n" in raw else b"\n"
    text = raw.decode("utf-8").replace("\r\n", "\n")
    for old, new in ((MARKS_OLD, MARKS_NEW), (LINE_OLD, LINE_NEW)):
        if text.count(old) != 1:
            sys.exit("UNKNOWN SHAPE: %d of %r in the copy's harness" % (text.count(old), old[:50]))
        text = text.replace(old, new)
    h.write_bytes(text.encode("utf-8").replace(b"\n", eol))
    out = DST / "report.json"
    cmd = [GODOT, "--headless", "--fixed-fps", "60", "--path", str(DST), "-s",
           "res://addons/laser_tag_tool/runners/run_map_eval.gd", "--", "--bake-nav",
           "--map", "res://level.tscn", "--scenario", "res://mission_scenario.tres",
           "--runs", "1", "--seed", "9104", "--trace", "--output", str(out)]
    proc = subprocess.run(cmd, cwd=str(DST), capture_output=True, text=True, timeout=900,
                          stdin=subprocess.DEVNULL)
    for line in proc.stdout.splitlines():
        # (the first version kept only `[LT trace]` lines and so hid its own `[LT slide]` ones)
        if line.startswith("[LT trace]") or line.startswith("[LT slide]") or line.startswith("[LT] run "):
            print(line)
    if not out.exists():
        print("NOT MEASURED: no report (exit %d)" % proc.returncode)
        return 2
    got = json.loads(out.read_text(encoding="utf-8"))
    job = json.loads(JOB_REPORT.read_text(encoding="utf-8"))
    mine = [e for e in got["events"] if e["event"] == "PlayerStuck"]
    theirs = [e for e in job["events"] if e["event"] == "PlayerStuck" and e["run_id"] == 1]
    print("stuck events, run 1: this copy %d, the job %d" % (len(mine), len(theirs)))
    first = lambda es: (es[0]["time"], es[0]["source"], es[0]["position"]) if es else None
    print("  first here:   %s" % (first(mine),))
    print("  first in job: %s" % (first(theirs),))
    if "--swap" in sys.argv or "--counter" in sys.argv or "--jolt" in sys.argv:
        print("THIS ARM changes the run after its change, so it is not the job's from there; the control "
              "is the plain run's")
        return 0
    if first(mine) != first(theirs):
        print("CONTROL FAILED: the copy did not reproduce the job's first stuck event; its trace is not the job's")
        return 1
    print("control held: the copy reproduces the job's first stuck event")
    return 0


if __name__ == "__main__":
    sys.exit(main())
