"""Stop the walker eating the waypoint that steers it round a corner.

MEASURED on warehouse_district. The navmesh's own path from the stuck point:

    0  (83.00, 0.25, -52.70)
    1  (83.15, 0.25, -52.70)     0.15 m from 0
    2  (83.45, 0.25, -52.40)     0.42 m from 1
    3  (83.60, 0.25, -35.50)    16.90 m from 2   <- clear for a body

Every leg of that path is clear when swept with the walker's own capsule. The
route is walkable. Points 1 and 2 are the corner: they shift the body 0.45 m
EAST before the long run north, and from point 2 the 16.9 m is unobstructed.

The walker stands at (83.00, -52.40) -- 0.45 m west of point 2 -- and from there
a straight line north goes into `ext_col_0_N_seg27`, the building's north wall.
Four walkers park against it on two sites, `on_wall` with a horizontal normal.

WHY IT IS THERE. Waypoints are consumed by proximity alone, against a hardcoded
0.6 m:

    if hd < 0.6 and (vd < 1.6 or hd < 0.1):
        pi += 1

From where the walker stands, points 0, 1 and 2 are 0.30, 0.34 and 0.45 m away.
All three are inside 0.6, so all three are marked reached in a single frame
without the body ever moving to them, and it then steers at point 3 from the
wrong side of the corner. The tolerance meant to decide "I got there" is wider
than the correction the path was asking for.

`ARRIVE_DIST` (DC_QA_ARRIVE, 1.5) is NOT this number -- it decides when a leg
TARGET is reached. Setting DC_QA_ARRIVE=0.4 changed nothing, which is how this
constant was found: the knob that looked responsible had no effect, so the real
one was somewhere else and hardcoded.

THE FIX, in two parts, because a smaller radius alone is not enough.

  * The radius has to be small, and how small is arithmetic rather than taste.
    The wall segment ends at x 83.00 (read from the .glb: ext_col_0_N_seg27,
    glTF +27.56 wide 0.88, in a building placed at [55, 35]). A 0.28 m body
    must reach x >= 83.28 before turning north. The corner waypoint is at
    83.45. So the path offers 0.17 m of margin, and any consume radius above
    that spends it. Simulated against that geometry: 0.60 hits the wall (the
    shipped behaviour, and it reproduces the observed stall to 2 cm), 0.30
    still hits it, 0.15 clears at x 83.51. The first version of this patch used
    AGENT_RADIUS * 0.75 = 0.30 and would not have worked.

    Where the 0.17 comes from is worth keeping: the funnel offsets a corner by
    the radius the map was BAKED for (0.4, ceiled to 0.45 by the voxel grid),
    while the body only needs its own 0.28. The margin IS that difference. Widen
    the walker to the bake radius and it goes to zero -- no consume radius would
    work, and `passed` would be carrying the whole fix.

  * Proximity is the wrong test anyway. What matters is whether the body has
    gone PAST a waypoint on its way to the next one, which is a direction
    question, not a distance one. A corner waypoint 0.45 m away is near while
    the body is still on the wrong side of the corner. Checking "passed"
    consumes waypoints the body genuinely left behind and keeps the ones it
    has not rounded yet, at any distance.

Both are needed, and the simulation shows why in both directions: a radius
alone cannot tell "near" from "behind" and clips the corner, while `passed`
alone STALLS -- at the first waypoint the body is exactly abreast of the leg
leaving it, the projection is zero rather than positive, and nothing ever
advances. Each covers the other's failure.

Adds DC_QA_WP so the radius is testable from the shell like every other walker
constant, instead of being the one that was not.

Asserts every target before writing, and is idempotent.
"""
import pathlib
import shutil

ROOT = pathlib.Path(r"C:\Projects\gabagool_studios\gabagool_factory")
DIR_GD = ROOT / "lot" / "godot" / "addons" / "heist_nav_qa" / "nav_qa_director.gd"

OLD_KNOB = '''var ARRIVE_DIST := _envf("DC_QA_ARRIVE", 1.5)
'''

NEW_KNOB = '''var ARRIVE_DIST := _envf("DC_QA_ARRIVE", 1.5)
#: How close counts as HAVING REACHED a path waypoint. Not ARRIVE_DIST -- that
#: one is for leg targets. This was a hardcoded 0.6, which is wider than the
#: lateral correction a funnelled path asks for at a corner: on
#: warehouse_district the corner waypoint sat 0.45 m away, inside 0.6, so it was
#: consumed while the body was still on the wrong side of the corner and the
#: body then steered at the far waypoint straight into a wall. Bounded by the
#: body instead of chosen. The margin available is exactly
#: (nav agent radius after voxel ceiling) - (this body's radius): the funnel
#: offsets a corner waypoint by the radius the map was BAKED for, and the body
#: only needs its own. On warehouse_district that is 0.45 - 0.28 = 0.17, so a
#: consume radius above 0.17 eats the clearance and the body clips the corner.
#: Simulated against the real wall from the .glb: 0.60 hits it (which is the
#: shipped behaviour and the observed failure), 0.30 still hits it, 0.15 clears.
#: NOTE this margin VANISHES if the walker is widened to the bake radius --
#: see clearances in agent_contract.json before raising the body.
var WP_RADIUS := _envf("DC_QA_WP", 0.15)
'''

OLD_CONSUME = '''		if hd < 0.6 and (vd < 1.6 or hd < 0.1):
			pi += 1
		else:
			break
'''

NEW_CONSUME = '''		if hd < WP_RADIUS and (vd < 1.6 or hd < 0.1):
			pi += 1
		elif pi + 1 < path.size() and _passed(body.global_position, wp,
				path[pi + 1]):
			# Not near, but behind: the body has rounded this waypoint and is
			# on its way to the next. Distance alone cannot tell those apart,
			# which is the whole defect this replaces.
			pi += 1
		else:
			break
'''

PASSED = '''

static func _passed(pos: Vector3, wp: Vector3, nxt: Vector3) -> bool:
	## Has the body gone PAST this waypoint on its way to the next one?
	##
	## Proximity cannot answer this. A corner waypoint 0.45 m away is near while
	## the body is still on the wrong side of the corner, so a radius test marks
	## it reached and the body steers at whatever comes after it -- on
	## warehouse_district, through the wall the corner existed to avoid. This
	## asks the direction question instead: project the body onto the leg
	## leaving the waypoint, and call it consumed only once it is on the far
	## side. Horizontal only, for the same reason the proximity test is: the
	## capsule centre rides about half its height above the nav surface, and a
	## 3D test folds that constant offset into every comparison.
	var leg := Vector2(nxt.x - wp.x, nxt.z - wp.z)
	if leg.length() < 0.01:
		return true
	var rel := Vector2(pos.x - wp.x, pos.z - wp.z)
	return rel.dot(leg.normalized()) > 0.0
'''

ANCHOR = "func _drive(w: Dictionary, delta: float) -> void:"


def main() -> int:
    src = DIR_GD.read_text(encoding="utf-8")
    if "WP_RADIUS" in src:
        print("nav_qa_director.gd: already patched")
        return 0

    for label, block in (("the ARRIVE_DIST knob", OLD_KNOB),
                         ("the waypoint-consume test", OLD_CONSUME)):
        if src.count(block) != 1:
            raise SystemExit(
                f"nav_qa_director.gd: {label} appears {src.count(block)} "
                f"time(s), expected exactly 1. Nothing written -- read the file "
                f"and re-aim this patch.")
    if src.count(ANCHOR) != 1:
        raise SystemExit("nav_qa_director.gd: cannot find _drive. "
                         "Nothing written.")

    backup = DIR_GD.with_suffix(".gd.pre_wp")
    if not backup.exists():
        shutil.copy2(DIR_GD, backup)

    src = src.replace(OLD_KNOB, NEW_KNOB)
    src = src.replace(OLD_CONSUME, NEW_CONSUME)
    at = src.index(ANCHOR)
    src = src[:at] + PASSED.lstrip("\n") + "\n\n" + src[at:]
    DIR_GD.write_text(src, encoding="utf-8")

    print(f"nav_qa_director.gd: waypoint consume is now WP_RADIUS + passed()")
    print(f"nav_qa_director.gd: previous file kept at {backup.name}")
    print("\n  the corner that was being eaten, on warehouse_district:")
    print("    wall ext_col_0_N_seg27 ends at x 83.00; a 0.28 m body needs")
    print("    x >= 83.28 before turning north; the corner waypoint is at 83.45,")
    print("    so the path offers 0.17 m of margin.")
    print("    simulated against that geometry:")
    for r, what in ((0.60, "hits the wall at (83.01, -52.20)  <- shipped"),
                    (0.30, "hits the wall at (83.19, -52.32)"),
                    (0.15, "clears north at x 83.51           <- default")):
        print(f"      consume radius {r:.2f} + passed()  ->  {what}")
    print("    passed() with no radius at all stalls on waypoint 0, so both")
    print("    tests are load-bearing. Override the radius with DC_QA_WP.")
    print("\n  run it, then re-walk the two sites that failed on this:")
    print("    python library_walk.py --only warehouse_district central_vault")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
