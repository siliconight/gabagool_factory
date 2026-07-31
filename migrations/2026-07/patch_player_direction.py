"""The step-up reads where the body ENDED UP, not where it is trying to go.

REPORTED FROM PLAY, after the floor_max_angle fix landed: "no problem walking
over kerbs from certain directions, still stopped from others."

THE CAUSE, in the function that fix edited. _move_with_steps runs move_and_slide()
and then decides which way the body is pushing by reading velocity:

    move_and_slide()
    ...
    var horiz := Vector3(velocity.x, 0.0, velocity.z)
    if horiz.length() < 0.05:
        return
    var into := horiz.normalized()

move_and_slide has ALREADY rewritten velocity to the post-slide result. So at the
exact moment the step-up is needed:

  * head-on into the kerb, the component into the face is removed and horizontal
    velocity is near zero -- the length test returns early;
  * at an angle, the velocity becomes tangential, running ALONG the kerb -- so
    into.dot(-normal) is near zero and the > 0.3 test fails.

It fires only in the narrow band where enough velocity survives still pointing
into the face, which is exactly "some approach directions work and others do not".

THE FIX. Use the INPUT direction. _physics_process already computes it one line
above the call and then discards it:

    var dir := (transform.basis * Vector3(input_dir.x, 0, input_dir.y)).normalized()
    velocity.x = dir.x * spd
    velocity.z = dir.z * spd
    _move_with_steps(delta)

`dir` is where the player is steering, is unaffected by the collision response,
and is the same on every approach angle. Passing it in makes the step-up
direction-agnostic: a dot of ~1 head-on, ~0.71 at 45 degrees, and still above the
0.3 threshold out to about 72 degrees off-normal -- past which you genuinely are
sliding along the kerb rather than trying to mount it, and refusing is correct.

This is the same defect shape as the rest of this pass: a cheap observable read
after the fact (resulting velocity) standing in for the expensive truth (intent),
with nothing recording the substitution.

A SECOND FIX in the same function. The forward probe distance is pinned:

    var ahead := into * 0.4

0.4 is "just past the body surface" only for a body narrower than 0.4. The
contract player is 0.35, so it works today by luck; a wider body would probe
inside itself and find its own floor. Taken from the capsule the scene actually
carries, cached at ready.

Asserts every target, refuses on a miss, idempotent, and runs gdcheck.
"""
import pathlib
import shutil
import subprocess
import sys

ROOT = pathlib.Path(r"C:\Projects\gabagool_studios\gabagool_factory")
GD = ROOT / "lot" / "godot" / "addons" / "lot" / "lot_player.gd"

# --- 1. cache the body radius ------------------------------------------------

READY_OLD = '''var _cam: Camera3D
var _yaw := 0.0
var _pitch := 0.0
'''

READY_NEW = '''var _cam: Camera3D
var _yaw := 0.0
var _pitch := 0.0
## Capsule radius, taken from the collision shape this scene actually carries so
## the step-up's forward probe clears the body instead of landing inside it.
var _radius := 0.35


func _find_radius() -> float:
	for c in get_children():
		if c is CollisionShape3D:
			var s := (c as CollisionShape3D).shape
			if s is CapsuleShape3D:
				return (s as CapsuleShape3D).radius
			if s is CylinderShape3D:
				return (s as CylinderShape3D).radius
	return 0.35
'''

READY_CALL_OLD = '''func _ready() -> void:
	_cam = get_node_or_null("Camera") as Camera3D
'''

READY_CALL_NEW = '''func _ready() -> void:
	_radius = _find_radius()
	_cam = get_node_or_null("Camera") as Camera3D
'''

# --- 2. pass the input direction --------------------------------------------

CALL_OLD = '''	velocity.x = dir.x * spd
	velocity.z = dir.z * spd
	_move_with_steps(delta)
'''

CALL_NEW = '''	velocity.x = dir.x * spd
	velocity.z = dir.z * spd
	# `dir` is where the player is STEERING. Pass it: move_and_slide rewrites
	# velocity to the post-slide result, so reading velocity afterwards tells you
	# where the body ended up, which at a kerb is either nowhere (head-on, the
	# component into the face removed) or sideways (angled, sliding along it).
	_move_with_steps(delta, dir)
'''

SIG_OLD = '''func _move_with_steps(delta: float) -> void:
	# Normal move first. If grounded and walking into a short near-vertical
	# obstacle (curb, ledge, steep stair nose), lift onto it and continue --
	# CharacterBody3D has no built-in step handling.
	move_and_slide()
	if not is_on_floor():
		return
	var horiz := Vector3(velocity.x, 0.0, velocity.z)
	if horiz.length() < 0.05:
		return
	var into := horiz.normalized()
'''

SIG_NEW = '''func _move_with_steps(delta: float, wish: Vector3) -> void:
	# Normal move first. If grounded and walking into a short near-vertical
	# obstacle (curb, ledge, steep stair nose), lift onto it and continue --
	# CharacterBody3D has no built-in step handling.
	move_and_slide()
	if not is_on_floor():
		return
	# Where the body is TRYING to go, not where it ended up. This read velocity
	# AFTER move_and_slide, which rewrites it to the post-slide result: head-on
	# into a kerb the horizontal velocity is ~0 and the length test returned
	# early, and at an angle the velocity runs ALONG the kerb so the dot test
	# below failed. Between them the step-up fired only for a narrow band of
	# approach angles -- reported from play as kerbs that work from some
	# directions and not others. `wish` is the input direction, identical on
	# every approach and unaffected by the collision response.
	var into := Vector3(wish.x, 0.0, wish.z)
	if into.length() < 0.05:
		return
	into = into.normalized()
'''

# --- 3. probe past the body's own surface -----------------------------------

AHEAD_OLD = '''	# Probe straight down from step height, just ahead, for the surface top.
	var space := get_world_3d().direct_space_state
	var ahead := into * 0.4
'''

AHEAD_NEW = '''	# Probe straight down from step height, just past the body's own surface, for
	# the step's top. The distance was pinned at 0.4, which clears a 0.35 m
	# capsule by 0.05 and would land INSIDE anything wider -- finding the body's
	# own floor instead of the step in front of it.
	var space := get_world_3d().direct_space_state
	var ahead := into * (_radius + 0.05)
'''


def _swap(src, old, new, label):
    n = src.count(old)
    if n != 1:
        raise SystemExit(f"lot_player.gd: {label} appears {n} time(s), expected "
                         f"exactly 1. Read the file rather than forcing this. "
                         f"NOTHING WRITTEN.")
    return src.replace(old, new)


def main() -> int:
    if not GD.exists():
        raise SystemExit(f"missing {GD}. Nothing written.")
    src = GD.read_text(encoding="utf-8")
    if "_move_with_steps(delta: float, wish: Vector3)" in src:
        print("lot_player.gd: step-up already uses the input direction")
        return 0
    if "var floor_cos := cos(floor_max_angle)" not in src:
        raise SystemExit("lot_player.gd: the floor_max_angle fix is not applied. "
                         "Run patch_player_step.py first. NOTHING WRITTEN.")

    src = _swap(src, READY_OLD, READY_NEW, "the state block")
    src = _swap(src, READY_CALL_OLD, READY_CALL_NEW, "_ready")
    src = _swap(src, CALL_OLD, CALL_NEW, "the _move_with_steps call")
    src = _swap(src, SIG_OLD, SIG_NEW, "the _move_with_steps signature")
    src = _swap(src, AHEAD_OLD, AHEAD_NEW, "the forward probe")

    backup = GD.with_suffix(".gd.pre_dir")
    if not backup.exists():
        shutil.copy2(GD, backup)
    GD.write_text(src, encoding="utf-8")
    print("  lot_player.gd: step-up steers on the INPUT direction, not the "
          "post-slide velocity")
    print("  lot_player.gd: forward probe derived from the capsule radius")
    print(f"  previous file kept at {backup.name}")

    print("\n=========== gdcheck ===========")
    checker = ROOT / "gdcheck.py"
    if checker.exists():
        r = subprocess.run([sys.executable, str(checker), str(GD)],
                           capture_output=True, text=True, cwd=str(ROOT))
        print((r.stdout or "").rstrip() or (r.stderr or "").rstrip()[-600:])
        if r.returncode != 0:
            print(f"\n  gdcheck exit {r.returncode} -- do NOT repackage until "
                  f"this is clean.")
            return r.returncode
    else:
        print("  gdcheck.py missing at the factory root")

    print("\n  The pack carries its own copy of this script, so repackage "
          "before walking:\n")
    print("    cd lot")
    print("    python package.py specs\\ballpark_block\\ballpark_block_site.json "
          "--walkable \\")
    print('      --check "C:\\Godot\\4.7\\Godot_v4.7-stable_win64_console.exe"')
    print("\n  Then approach the same kerb from several angles, including along "
          "it.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
