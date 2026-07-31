"""Don't try to step up a slope. Steps have walkable tops; ramps do not.

REPORTED FROM PLAY, after the floor_max_angle fix: "now I can run into it and it
tries to get up but fails and falls down."

MEASURED, from the geometry and the code. A stair ramp is a CONTINUOUS incline, so
the forward probe always finds a surface higher than the body by

    probe_distance * tan(pitch)   =   0.4 * tan(50 deg)   =   0.48 m

which is inside max_step_height (0.5), so the step-up fires. It then lifts the
body 0.48 m while advancing it only `speed * delta * 0.6`, about 0.05 m at 60 fps.
The body ends up in mid-air above the ramp, is_on_floor() goes false, the step-up
stops running, and it slides back down. Next frame it fires again. The lift height
is set by the PROBE DISTANCE, not by the geometry, so the cycle never converges --
juddering up a staircase and falling off it.

MY REGRESSION, introduced tonight. The old gate was `absf(n.y) < 0.2`, which never
fired on a slope at all, so a too-steep flight simply stopped the body. Changing it
to cos(floor_max_angle) -- correct for the KERB case it was written for -- also
opened it to every slope steeper than the floor angle, where it cannot help and
now actively throws the body around. Stopping dead is a better failure than being
launched and dropped.

THE FIX is one condition, and the information is already in hand. The probe ray
returns the surface NORMAL along with the position, and the code discards it. A
step has a walkable top; a ramp does not. So: only lift onto something the engine
would call a floor.

    if hit.get("normal", Vector3.UP).y < cos(floor_max_angle):
        return

That keeps every kerb working -- a kerb top is flat, its normal is straight up --
and refuses the futile lift on a slope, which correctly leaves a too-steep flight
as a wall until the geometry is fixed.

WHAT THIS DOES NOT FIX. The stairs. 20 of 38 buildings emit flights at 45-51
degrees against a controller that stands on 45, and no step-up rescues a
continuous slope steeper than the floor angle -- that is what this measurement
establishes. The flights need a shallower pitch; this only stops the controller
pretending it can help.

Asserts its target, refuses on a miss, idempotent, and runs gdcheck.
"""
import pathlib
import shutil
import subprocess
import sys

ROOT = pathlib.Path(r"C:\Projects\gabagool_studios\gabagool_factory")
GD = ROOT / "lot" / "godot" / "addons" / "lot" / "lot_player.gd"

OLD = '''	var step_top: float = hit["position"].y
	var rise := step_top - global_position.y
	if rise <= 0.02 or rise > max_step_height:
		return
'''

NEW = '''	var step_top: float = hit["position"].y
	var rise := step_top - global_position.y
	if rise <= 0.02 or rise > max_step_height:
		return

	# Is the thing we would stand on actually a FLOOR? A step has a walkable top;
	# a ramp does not, and on a continuous incline this probe ALWAYS finds a
	# surface `ahead * tan(pitch)` higher -- 0.48 m on a 50 degree flight, inside
	# max_step_height, so it fires. It then lifts the body by that much while
	# advancing it about 0.05 m, leaving it in mid-air above the ramp; is_on_floor
	# goes false, this stops running, the body slides back down, and next frame it
	# fires again. The lift is set by the probe distance rather than by the
	# geometry, so it never converges: reported from play as "it tries to get up
	# but fails and falls down".
	#
	# The old `absf(n.y) < 0.2` gate never fired on a slope, so a too-steep flight
	# simply stopped the body. Widening the gate to cos(floor_max_angle) -- right
	# for the kerb it was written for -- also opened it to slopes it cannot climb.
	# Stopping dead is a better failure than being launched and dropped.
	#
	# The probe already returns the surface normal and it was being discarded.
	if hit.get("normal", Vector3.UP).y < cos(floor_max_angle):
		return
'''


def main() -> int:
    if not GD.exists():
        raise SystemExit(f"missing {GD}. Nothing written.")
    src = GD.read_text(encoding="utf-8")
    if 'hit.get("normal"' in src:
        print("lot_player.gd: step-up already refuses a non-walkable top")
        return 0
    if "var floor_cos := cos(floor_max_angle)" not in src:
        raise SystemExit("lot_player.gd: run patch_player_step.py first. "
                         "NOTHING WRITTEN.")
    if src.count(OLD) != 1:
        raise SystemExit(f"lot_player.gd: the probe result block appears "
                         f"{src.count(OLD)} time(s), expected exactly 1. "
                         f"NOTHING WRITTEN.")
    backup = GD.with_suffix(".gd.pre_slope")
    if not backup.exists():
        shutil.copy2(GD, backup)
    GD.write_text(src.replace(OLD, NEW), encoding="utf-8")
    print("  lot_player.gd: step-up only lifts onto a surface the engine would "
          "call floor")
    print(f"  previous file kept at {backup.name}")

    print("\n=========== gdcheck ===========")
    checker = ROOT / "gdcheck.py"
    if checker.exists():
        r = subprocess.run([sys.executable, str(checker), str(GD)],
                           capture_output=True, text=True, cwd=str(ROOT))
        print((r.stdout or "").rstrip() or (r.stderr or "").rstrip()[-500:])
        if r.returncode != 0:
            return r.returncode
    print("\n  Expected after repackaging: kerbs unchanged (a kerb top is flat, "
          "so its\n  normal is straight up and it still lifts), and a too-steep "
          "flight stops the\n  body cleanly instead of throwing it. The flight "
          "is still not climbable --\n  that needs the pitch capped in "
          "deli_counter.\n")
    print("    cd lot")
    print("    python package.py specs\\ballpark_block\\ballpark_block_site.json "
          "--walkable \\")
    print('      --check "C:\\Godot\\4.7\\Godot_v4.7-stable_win64_console.exe"')
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
