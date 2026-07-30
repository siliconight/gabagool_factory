"""Fix the step-up in the shipped player: it climbs tall steps and fails on curbs.

MEASURED, from the code and the capsule geometry. lot_player.gd DOES implement
step-up -- max_step_height 0.45, a raycast probe after move_and_slide with a
direction test and a head-clearance test. It is gated on this:

    if absf(col.get_normal().y) < 0.2 and into.dot(-col.get_normal()) > 0.3:
        blocked = true

A capsule does not meet a low step on a flat face. Contact lands on the bottom
hemisphere, so the contact normal is SLOPED, and the lower the step the more
vertical that normal gets: n.y = (R - h) / R. Requiring n.y < 0.2 therefore
requires

    (R - h) / R < 0.2   ->   h > 0.8 * R   ->   h > 0.28 m for the 0.35 m body

so nothing shorter than 0.28 m ever sets `blocked`, and the step-up never runs on
it. The step-up is backwards: it lifts the body over tall obstacles and leaves it
stuck against curbs. Between the tallest step a capsule WALKS up
(R * (1 - cos(floor_max_angle)) = 0.1025 m) and 0.28 m there is a dead band where
the body simply stops.

SIDEWALK_H is 0.16. COURT_THICK was 0.12. Both sat inside that band, which is why
"walking from a spawn toward the street stops dead and needs a jump" was reported
from play despite a controller that nominally climbs 0.45 m.

THE FIX IS THE ENGINE'S OWN THRESHOLD. floor_max_angle is what CharacterBody3D
uses to decide whether a contact counts as floor at all. Gating the step-up on
cos(floor_max_angle) puts its lower bound exactly where walking stops working:

    n.y < cos(45 deg) = 0.7071   ->   h > 0.2929 * R = 0.1025 m for R = 0.35

which is unassisted_step_max_m to four decimals. Walking covers 0 to 0.1025,
step-up covers 0.1025 to max_step_height, no gap and no overlap, and both bounds
fall out of one constant instead of a picked 0.2. It also scales: change the body
and the two thresholds still meet.

TWO SMALLER DEFECTS in the same function.

The head-clearance ray runs from step_top + 0.05 to step_top + 1.7 against a body
1.8 m tall, so it clears 1.65 m and under-checks by 0.15 m -- the body can be
lifted into geometry its own head occupies. Now driven by the body height.

max_step_height is 0.45 while the contract's characters.player.max_step_up_m says
0.5, and the export's own comment says "keep under ~0.5 m". Two numbers for one
quantity. The walk scene now sets both properties from the contract, the same way
PlayerCol already does, so the pack ships one set of body metrics rather than
three.

Touches lot/godot/addons/lot/lot_player.gd and lot/lot.py. Asserts every target,
refuses on a miss, idempotent, byte-compiles the Python, and runs gdparse on the
GDScript if gdtoolkit is present.
"""
import json
import math
import pathlib
import py_compile
import shutil
import subprocess
import sys

ROOT = pathlib.Path(r"C:\Projects\gabagool_studios\gabagool_factory")
GD = ROOT / "lot" / "godot" / "addons" / "lot" / "lot_player.gd"
LOT_PY = ROOT / "lot" / "lot.py"
CONTRACT = ROOT / "deli_counter" / "agent_contract.json"

# --- 1. the export block ----------------------------------------------------

EXPORT_OLD = '''## Max height the body auto-steps up in one move: curbs/sidewalks, ledges, and
## steep stair noses the capsule would otherwise catch on. Keep under ~0.5 m so
## you don't climb things you shouldn't. This is a raycast-probe step-up with a
## valid-direction + head-clearance check (after move_and_slide), adapted from
## the standard FPS step-climbing approach.
@export var max_step_height := 0.45
'''

EXPORT_NEW = '''## Max height the body auto-steps up in one move: curbs/sidewalks, ledges, and
## steep stair noses the capsule would otherwise catch on. This is a
## raycast-probe step-up with a valid-direction + head-clearance check (after
## move_and_slide), adapted from the standard FPS step-climbing approach.
##
## The walk scene sets this from the agent contract
## (characters.player.max_step_up_m), because a default here and a number in the
## contract are two values for one quantity and they had already diverged -- 0.45
## against 0.5.
@export var max_step_height := 0.45
## Full body height, including both capsule hemispheres. Used for the step-up's
## head-clearance probe: a hardcoded 1.7 m there cleared only 1.65 m against a
## 1.8 m body, so the body could be lifted into geometry its own head occupies.
## Also set from the contract by the walk scene.
@export var body_height := 1.8
'''

# --- 2. the gate ------------------------------------------------------------

GATE_OLD = '''	# Only step if we're pushing INTO a near-vertical face, not sliding along it.
	var blocked := false
	for i in get_slide_collision_count():
		var col := get_slide_collision(i)
		if absf(col.get_normal().y) < 0.2 and into.dot(-col.get_normal()) > 0.3:
			blocked = true
			break
	if not blocked:
		return
'''

GATE_NEW = '''	# Only step if we're pushing INTO something the engine does NOT count as
	# floor, and not merely sliding along it.
	#
	# This threshold was a fixed 0.2, and that made the step-up backwards. A
	# capsule meets a LOW step on its bottom hemisphere, so the contact normal is
	# sloped, not vertical: n.y = (R - h) / R. Demanding n.y < 0.2 demands
	# h > 0.8 * R -- 0.28 m for a 0.35 m body -- so nothing shorter ever set
	# `blocked` and nothing shorter was ever stepped. Tall obstacles got climbed
	# and curbs did not. Between the tallest step the capsule WALKS up (0.1025 m)
	# and 0.28 m the body just stopped, and SIDEWALK_H at 0.16 m sat in that band.
	#
	# floor_max_angle is the same threshold the engine uses to decide whether a
	# contact is floor, so cos(floor_max_angle) puts this lower bound exactly
	# where walking stops working: n.y < cos(45 deg) means h > 0.2929 * R, which
	# is R * (1 - cos(floor_max_angle)) -- clearances.unassisted_step_max_m. The
	# two ranges meet with no gap, and they keep meeting if the body changes.
	var floor_cos := cos(floor_max_angle)
	var blocked := false
	for i in get_slide_collision_count():
		var col := get_slide_collision(i)
		if absf(col.get_normal().y) < floor_cos and into.dot(-col.get_normal()) > 0.3:
			blocked = true
			break
	if not blocked:
		return
'''

# --- 3. the head-clearance probe -------------------------------------------

HEAD_OLD = '''	# Head clearance: don't climb into a low ceiling / under geometry.
	var hp: Vector3 = hit["position"]
	var head := PhysicsRayQueryParameters3D.create(
		Vector3(hp.x, step_top + 0.05, hp.z), Vector3(hp.x, step_top + 1.7, hp.z))
'''

HEAD_NEW = '''	# Head clearance: don't climb into a low ceiling / under geometry. The upper
	# end was a hardcoded 1.7, which clears 1.65 m from the step surface against
	# a body 1.8 m tall -- 0.15 m short, so the body could be lifted into
	# geometry its own head occupies.
	var hp: Vector3 = hit["position"]
	var head := PhysicsRayQueryParameters3D.create(
		Vector3(hp.x, step_top + 0.05, hp.z),
		Vector3(hp.x, step_top + body_height, hp.z))
'''

# --- 4. the walk scene sets both from the contract --------------------------

WALK_OLD = """        '[node name="Player" type="CharacterBody3D" parent="."]',
        f'transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, {player_godot})',
        'script = ExtResource("player")', '',
        '[node name="col" type="CollisionShape3D" parent="Player"]',
        'transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0.9, 0)',
        'shape = SubResource("PlayerCol")', '',
        '[node name="Camera" type="Camera3D" parent="Player"]',
        'transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 1.6, 0)', '',
"""

WALK_NEW = """        # Every body metric on this node comes from the contract. The capsule
        # already did; the step-up ceiling, the head-clearance height, the
        # collision offset and the eye height were literals, and lot_player.gd's
        # own default step height (0.45) had already drifted from the contract's
        # max_step_up_m (0.5). The collision shape sits half the body height up
        # because the node origin is at the FEET.
        '[node name="Player" type="CharacterBody3D" parent="."]',
        f'transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, {player_godot})',
        'script = ExtResource("player")',
        f'max_step_height = {_player_metric("max_step_up_m", 0.5)}',
        f'body_height = {_player_metric("height_m", 1.8)}', '',
        '[node name="col" type="CollisionShape3D" parent="Player"]',
        f'transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, 0, '
        f'{_player_metric("height_m", 1.8) / 2.0}, 0)',
        'shape = SubResource("PlayerCol")', '',
        '[node name="Camera" type="Camera3D" parent="Player"]',
        f'transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, 0, '
        f'{_player_metric("eye_height_m", 1.6)}, 0)', '',
"""

HELPER_ANCHOR = '''def write_walk_scene(site_spec, merged, walk_out, site_tscn_base,'''

HELPER_NEW = '''def _player_metric(key, fallback):
    """One body metric from the contract, for the walk scene's Player node.

    Exists so the walk scene cannot carry a second opinion about the body. Each
    of these was a literal in the emitted .tscn, and lot_player.gd carried a
    third copy of the step height as an export default.
    """
    try:
        return float(_agent()["characters"]["player"][key])
    except (KeyError, TypeError, ValueError):
        return fallback


def write_walk_scene(site_spec, merged, walk_out, site_tscn_base,'''


def _swap(src, old, new, label):
    n = src.count(old)
    if n != 1:
        raise SystemExit(f"{label}: target appears {n} time(s), expected exactly "
                         f"1. Read the file rather than forcing this. "
                         f"NOTHING WRITTEN.")
    return src.replace(old, new)


def main() -> int:
    for p in (GD, LOT_PY, CONTRACT):
        if not p.exists():
            raise SystemExit(f"missing {p}. Nothing written.")

    done = []

    gd = GD.read_text(encoding="utf-8")
    if "var floor_cos := cos(floor_max_angle)" in gd:
        done.append("lot_player.gd: already uses the floor threshold")
    else:
        gd = _swap(gd, EXPORT_OLD, EXPORT_NEW,
                   "lot_player.gd: exports")
        gd = _swap(gd, GATE_OLD, GATE_NEW,
                   "lot_player.gd: step-up gate")
        gd = _swap(gd, HEAD_OLD, HEAD_NEW,
                   "lot_player.gd: head-clearance probe")
        done.append("lot_player.gd: step-up gated on cos(floor_max_angle), "
                    "head clearance uses the body height, both metrics exported")

    src = LOT_PY.read_text(encoding="utf-8")
    if "def _player_metric(" in src:
        done.append("lot.py: walk scene already sets the body metrics")
    else:
        src = _swap(src, HELPER_ANCHOR, HELPER_NEW, "lot.py: _player_metric")
        src = _swap(src, WALK_OLD, WALK_NEW, "lot.py: walk scene Player node")
        done.append("lot.py: walk scene sets max_step_height, body_height, "
                    "collision offset and eye height from the contract")

    for path, text, suffix in ((GD, gd, ".gd.pre_step"),
                               (LOT_PY, src, ".py.pre_step")):
        backup = path.with_suffix(suffix)
        if not backup.exists():
            shutil.copy2(path, backup)
        path.write_text(text, encoding="utf-8")
    py_compile.compile(str(LOT_PY), doraise=True)

    print("applied:")
    for line in done:
        print(f"  {line}")
    print("  lot.py compiles; previous copies kept as *.pre_step")

    # GDScript has to be checked before it reaches a machine that loads it
    print("\n=========== gdcheck ===========")
    checker = ROOT / "gdcheck.py"
    if checker.exists():
        r = subprocess.run([sys.executable, str(checker), str(GD)],
                           capture_output=True, text=True, cwd=str(ROOT))
        print((r.stdout or "").rstrip() or (r.stderr or "").rstrip()[-800:])
    else:
        print("  gdcheck.py not found at the factory root -- run it manually:")
        print(f"    python gdcheck.py {GD}")

    # the arithmetic, stated out loud
    c = json.loads(CONTRACT.read_text(encoding="utf-8"))
    pl = c["characters"]["player"]
    r = float(pl["radius_m"])
    ceiling = float(pl["max_step_up_m"])
    walk = r * (1.0 - math.cos(math.radians(45.0)))
    old_band_lo, old_band_hi = walk, 0.8 * r
    print("\n=========== the two ranges, for this body ===========")
    print(f"  body radius {r} m, floor angle 45 deg")
    print(f"    walking handles          0.0000 .. {walk:.4f} m")
    print(f"    step-up now handles      {walk:.4f} .. {ceiling:.4f} m")
    print(f"    step-up BEFORE handled   {old_band_hi:.4f} .. {ceiling:.4f} m")
    print(f"    dead band removed        {old_band_lo:.4f} .. {old_band_hi:.4f} m")
    print()
    for name, h in (("road", 0.0643), ("path", 0.0800), ("courtyard", 0.0958),
                    ("sidewalk / kerb", 0.16), ("old courtyard", 0.12)):
        if h <= walk:
            verdict = "walks"
        elif h <= ceiling:
            was = "was STUCK" if h < old_band_hi else "stepped before too"
            verdict = f"steps up   ({was})"
        else:
            verdict = "too tall for either"
        print(f"    {name:<18}{h:.4f}   {verdict}")
    print("\n  Derived, not tested in engine. The experiment is: package a site, "
          "walk\n  into a kerb, see whether you rise onto it.\n")
    print("    python lot\\package.py lot\\specs\\ballpark_block\\"
          "ballpark_block_site.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
