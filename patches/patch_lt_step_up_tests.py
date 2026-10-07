"""Laser Tag 0.24.0's test, written first: a step the contract's player takes,
the crew takes (roadmap 203).

    python patch_lt_step_up_tests.py

Writes `lasertag/addons/laser_tag_tool/runners/tests/test_step_up_is_the_contracts.gd`
(new, LF; refuses if it exists). On 0.23.2 it must FAIL: the bot has no
`max_step_up` and no `steps_taken`, so the script errors before any case; and
the OFF half of every case is the 0.23.2 bot's own behaviour.

Run:  godot --headless --path lasertag -s res://addons/laser_tag_tool/runners/tests/test_step_up_is_the_contracts.gd
"""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
TEST = ROOT / "lasertag" / "addons" / "laser_tag_tool" / "runners" / "tests" / "test_step_up_is_the_contracts.gd"

SRC = '''extends SceneTree
## A step the contract's player takes, the crew takes (0.24.0, roadmap 203).
##
## `deli_counter/agent_contract.json` gives the player `max_step_up_m` 0.5:
## its controller lifts itself over a step that tall, and a transition above
## `clearances.unassisted_step_max_m` -- 0.1025, what a stock capsule of radius
## 0.35 walks over at a 45 degree floor -- "requires the consumer to have
## implemented step-up". LT_BotPlayerController implemented none, and the
## navmesh routes over anything up to `nav_bake.agent_max_climb_m` (0.15). So
## the crew stopped where the contract's player walks on: cold run 9194's
## bank_branch_a04 crew wedged against a stair ramp's open side 0.118 m high,
## 1,302 of 1,306 stuck events in one 2 m cell, route completion 8% and 0% on
## the two candidates that drew that bank.
##
## Each case walks the real LT_PlayerPill over real colliders, with step-up OFF
## (the bot before this release) and ON (the contract's 0.5 m):
##   [1] a 0.08 m step, under the unassisted line: walked either way, and no
##       step is taken. The CONTROL -- the body is the contract's capsule and
##       the scene can see a pass.
##   [2] a 0.118 m step, the height the wedge stood at: OFF stops, ON steps.
##   [3] a 37.9 degree ramp met from its open side, as on the bank's stair:
##       OFF stops, ON steps onto the ramp.
##   [4] a 0.6 m box, over the limit: no climb, and no step taken.
##   [5] a 50 degree slope, steeper than the floor: no climb, and no step
##       taken -- step-up must not try to rescue a slope (CLAUDE.md).
##
## Run:  godot --headless --path lasertag -s res://addons/laser_tag_tool/runners/tests/test_step_up_is_the_contracts.gd

const RADIUS: float = 0.35
const HEIGHT: float = 1.8
const FRAMES: int = 360

var failures: int = 0


func check(condition: bool, label: String) -> void:
	if condition:
		print("  ok: " + label)
	else:
		failures += 1
		print("  FAIL: " + label)


func _solid(shape: Shape3D, at: Vector3) -> StaticBody3D:
	var sb := StaticBody3D.new()
	sb.collision_layer = LT_Const.LAYER_WORLD
	sb.collision_mask = 0
	var cs := CollisionShape3D.new()
	cs.shape = shape
	sb.add_child(cs)
	sb.position = at
	return sb


func _box(size: Vector3, at: Vector3) -> StaticBody3D:
	var b := BoxShape3D.new()
	b.size = size
	return _solid(b, at)


## A wedge rising along +X from height 0 at x = 0 to `rise` at x = `run`,
## `width` deep in Z from z = 0, placed at `at`: a flight's smooth ramp.
func _wedge(run: float, rise: float, width: float, at: Vector3) -> StaticBody3D:
	var w := ConvexPolygonShape3D.new()
	w.points = PackedVector3Array([
		Vector3(0.0, 0.0, 0.0), Vector3(run, 0.0, 0.0), Vector3(run, rise, 0.0),
		Vector3(0.0, 0.0, width), Vector3(run, 0.0, width), Vector3(run, rise, width)])
	return _solid(w, at)


## Walk the real pill from `start` toward `target` for FRAMES physics frames,
## with `step` as its step-up limit. Returns [position, completed, steps].
func _walk(obstacle: StaticBody3D, start: Vector3, target: Vector3,
		step: float) -> Array:
	var world := Node3D.new()
	get_root().add_child(world)
	world.add_child(_box(Vector3(40.0, 0.2, 40.0), Vector3(0.0, -0.1, 0.0)))
	world.add_child(obstacle)
	var pill_scene: PackedScene = load(
		"res://addons/laser_tag_tool/scenes/LT_PlayerPill.tscn")
	var pill: CharacterBody3D = pill_scene.instantiate()
	world.add_child(pill)
	# The contract's capsule, as the harness builds it: origin at the feet.
	var shape_node: CollisionShape3D = pill.get_node("CollisionShape3D")
	var cap: CapsuleShape3D = (shape_node.shape as CapsuleShape3D).duplicate()
	cap.radius = RADIUS
	cap.height = HEIGHT
	shape_node.shape = cap
	shape_node.position.y = HEIGHT * 0.5
	var manual: Node = pill.get_node("LT_PlayerController")
	manual.set_physics_process(false)
	manual.set_process_unhandled_input(false)
	var bot: LT_BotPlayerController = pill.get_node("LT_BotPlayerController")
	bot.use_navigation = false
	bot.move_speed = 4.0
	bot.max_step_up = step
	pill.global_position = start
	await physics_frame
	var route: Array[Vector3] = [target]
	bot.start_route(route)
	for i in FRAMES:
		await physics_frame
	var out: Array = [pill.global_position, bot._completed, bot.steps_taken]
	world.queue_free()
	await process_frame
	return out


func _report(label: String, r: Array) -> void:
	var p: Vector3 = r[0]
	print("     %s: at (%.2f, %.3f, %.2f), completed %s, steps %d"
		% [label, p.x, p.y, p.z, str(r[1]), int(r[2])])


func _init() -> void:
	LT_Const.ensure_input_actions()

	print("[1] a 0.08 m step, under the unassisted line (the control)")
	var a_off: Array = await _walk(_box(Vector3(4.0, 0.08, 4.0), Vector3(3.0, 0.04, 0.0)),
		Vector3(0.0, 0.02, 0.0), Vector3(4.0, 0.08, 0.0), 0.0)
	var a_on: Array = await _walk(_box(Vector3(4.0, 0.08, 4.0), Vector3(3.0, 0.04, 0.0)),
		Vector3(0.0, 0.02, 0.0), Vector3(4.0, 0.08, 0.0), 0.5)
	_report("off", a_off)
	_report("on ", a_on)
	check(bool(a_off[1]) and (a_off[0] as Vector3).y > 0.05,
		"with no step-up the capsule walks onto 0.08 m: the body and the scene are sound")
	check(bool(a_on[1]) and int(a_on[2]) == 0,
		"and with step-up on it walks it too, taking no step it does not need")

	print("[2] a 0.118 m step, the height the bank's crew wedged at")
	var b_off: Array = await _walk(_box(Vector3(4.0, 0.118, 4.0), Vector3(3.0, 0.059, 0.0)),
		Vector3(0.0, 0.02, 0.0), Vector3(4.0, 0.118, 0.0), 0.0)
	var b_on: Array = await _walk(_box(Vector3(4.0, 0.118, 4.0), Vector3(3.0, 0.059, 0.0)),
		Vector3(0.0, 0.02, 0.0), Vector3(4.0, 0.118, 0.0), 0.5)
	_report("off", b_off)
	_report("on ", b_on)
	check(not bool(b_off[1]) and (b_off[0] as Vector3).y < 0.05,
		"with no step-up the crew stops at it -- the 0.23.2 bot")
	check(bool(b_on[1]) and (b_on[0] as Vector3).y > 0.1 and int(b_on[2]) >= 1,
		"with the contract's step-up it steps up and finishes the route")

	print("[3] a 37.9 degree ramp met from its open side, as on the bank's stair")
	# 4.2 m over 5.4 m, the bank's flight; met across its width at x = 0.25,
	# where its top stands 0.195 m.
	var c_off: Array = await _walk(_wedge(5.4, 4.2, 1.6, Vector3.ZERO),
		Vector3(0.25, 0.02, -2.0), Vector3(0.25, 0.195, 1.4), 0.0)
	var c_on: Array = await _walk(_wedge(5.4, 4.2, 1.6, Vector3.ZERO),
		Vector3(0.25, 0.02, -2.0), Vector3(0.25, 0.195, 1.4), 0.5)
	_report("off", c_off)
	_report("on ", c_on)
	check(not bool(c_off[1]) and (c_off[0] as Vector3).z < 0.0,
		"with no step-up the crew stops at the ramp's side")
	check(bool(c_on[1]) and (c_on[0] as Vector3).y > 0.1 and int(c_on[2]) >= 1,
		"with it the crew steps onto the ramp and finishes")

	print("[4] a 0.6 m box, over the contract's 0.5")
	var d_on: Array = await _walk(_box(Vector3(4.0, 0.6, 4.0), Vector3(3.0, 0.3, 0.0)),
		Vector3(0.0, 0.02, 0.0), Vector3(4.0, 0.6, 0.0), 0.5)
	_report("on ", d_on)
	check(not bool(d_on[1]) and (d_on[0] as Vector3).y < 0.05 and int(d_on[2]) == 0,
		"too tall to step: not climbed, and no step taken")

	print("[5] a 50 degree slope, steeper than the floor")
	var e_on: Array = await _walk(_wedge(2.0, 2.0 * tan(deg_to_rad(50.0)), 4.0,
		Vector3(1.0, 0.0, -2.0)), Vector3(0.0, 0.02, 0.0), Vector3(2.5, 1.8, 0.0), 0.5)
	_report("on ", e_on)
	check(not bool(e_on[1]) and int(e_on[2]) == 0,
		"a slope is not a step: no step taken, the route not finished")
	check((e_on[0] as Vector3).y < 0.6, "and the body was not thrown up the slope")

	print("")
	if failures == 0:
		print("test_step_up_is_the_contracts: PASS")
	else:
		print("test_step_up_is_the_contracts: %d FAILURE(S)" % failures)
	quit(1 if failures > 0 else 0)
'''


def main():
    assert not TEST.exists(), "%s exists; this patch writes it new" % TEST
    TEST.write_bytes(SRC.encode("utf-8"))
    print("wrote %s (%d bytes)" % (TEST.relative_to(ROOT), len(SRC.encode("utf-8"))))


if __name__ == "__main__":
    main()
