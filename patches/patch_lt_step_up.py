"""Laser Tag 0.24.0: the crew takes the contract's step-up (roadmap 203).

    python patch_lt_step_up.py            # apply
    python patch_lt_step_up.py --check    # verify every anchor, write nothing

`deli_counter/agent_contract.json` gives the player `max_step_up_m` 0.5 and
says a transition above `clearances.unassisted_step_max_m` (0.1025) requires
the consumer's step-up. LT_BotPlayerController had none, and the navmesh routes
over anything up to `agent_max_climb_m` (0.15): cold run 9194's
bank_branch_a04 crew wedged against a stair ramp's open side 0.118 m high
(route completion 8% and 0%).

  - LT_BotPlayerController: `max_step_up` (0.5) and `_try_step_up`, after the
    slide, onto a TOP the body can stand on -- probed straight down a
    body-width ahead, normal within `floor_max_angle`, lift and move both
    clear. Never a slope. `steps_taken` counts them.
  - LT_TestScenario: `player_max_step_up_m` (0.5), the contract's field.
  - LT_MapEvalHarness._apply_body: hands it to the bot.

Anchored on, as read 2026-10-07:
  lasertag/addons/laser_tag_tool/scripts/player/LT_BotPlayerController.gd  16,345 bytes, LF
  lasertag/addons/laser_tag_tool/resources/LT_TestScenario.gd               6,631 bytes, CRLF
  lasertag/addons/laser_tag_tool/scripts/core/LT_MapEvalHarness.gd         42,165 bytes, LF
A CRLF file is matched with its endings normalised and written back CRLF; a
mixed file is refused. Every anchor must match once; nothing is written until
every file matched.
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
LT = ROOT / "lasertag" / "addons" / "laser_tag_tool"

BOT = [
    ("@export var stuck_distance_threshold: float = 0.5\n",
     "@export var stuck_distance_threshold: float = 0.5\n"
     "\n"
     "## THE CONTRACT'S STEP-UP (0.24.0, roadmap 203). `characters.player.\n"
     "## max_step_up_m` in `deli_counter/agent_contract.json` is 0.5: the player's\n"
     "## controller lifts itself over a step that tall, and a transition above\n"
     "## `clearances.unassisted_step_max_m` (0.1025, what a stock capsule walks over)\n"
     "## \"requires the consumer to have implemented step-up\". This bot implemented\n"
     "## none, and the navmesh routes over anything up to `agent_max_climb_m` (0.15),\n"
     "## so it stopped where the contract's player walks on. Measured on cold run\n"
     "## 9194: bank_branch_a04's crew wedged against a stair ramp's open side 0.118 m\n"
     "## high -- 1,302 of 1,306 stuck events in one 2 m cell, route completion 8% --\n"
     "## while the walktest's walker, which steps, walked past it. The harness sets\n"
     "## this from the scenario (`player_max_step_up_m`), which Level Factory fills\n"
     "## from the contract. 0 turns step-up off.\n"
     "@export var max_step_up: float = 0.5\n"
     "## Step-ups taken: what the step-up did, for a reader of a run.\n"
     "var steps_taken: int = 0\n"
     "\n"
     "## How far past the body the step probe looks, and how far above the limit it\n"
     "## starts, so a top exactly at `max_step_up` is found. A tolerance, not a\n"
     "## derivation: a top narrower than this is not one a body can stand on.\n"
     "const STEP_PROBE_MARGIN: float = 0.05\n"
     "## A rise below this is the floor's own unevenness, not a step.\n"
     "const STEP_MIN_RISE: float = 0.01\n"
     "## How squarely the wall must face the walk (cos of 72.5 deg). A wall the bot\n"
     "## slides along at a shallower angle is not in its way.\n"
     "const STEP_FACING_DOT: float = 0.3\n"),
    ("\tbody.move_and_slide()\n"
     "\t_update_stuck(delta)\n",
     "\t# The way the bot MEANT to go, before the slide turns it along whatever\n"
     "\t# it hit: the step-up asks about that wall, not about the slide.\n"
     "\tvar intended := Vector3(body.velocity.x, 0.0, body.velocity.z)\n"
     "\tbody.move_and_slide()\n"
     "\t_try_step_up(intended)\n"
     "\t_update_stuck(delta)\n"),
    ("func _fire_at(enemy: Node3D) -> void:\n",
     "## A STEP, NEVER A SLOPE (0.24.0, roadmap 203).\n"
     "##\n"
     "## The lift is the height of a TOP the body can stand on: a surface found\n"
     "## straight down, a body-width ahead, whose normal is within the body's own\n"
     "## `floor_max_angle`. On a continuous incline a probe ahead always finds a\n"
     "## higher surface, so a lift sized by the probe would throw the body up a ramp\n"
     "## it cannot stand on (CLAUDE.md, \"Step-up cannot rescue a slope\"). The step is\n"
     "## taken only when the lift and the move onto the top both clear the world.\n"
     "func _try_step_up(intended: Vector3) -> bool:\n"
     "\tif max_step_up <= 0.0 or not body.is_on_floor() or not body.is_on_wall():\n"
     "\t\treturn false\n"
     "\tif intended.length() < 0.1:\n"
     "\t\treturn false\n"
     "\tvar fwd: Vector3 = intended.normalized()\n"
     "\tif body.get_wall_normal().dot(fwd) > -STEP_FACING_DOT:\n"
     "\t\treturn false\n"
     "\tvar reach: float = _body_radius() + STEP_PROBE_MARGIN\n"
     "\tvar feet: Vector3 = body.global_position\n"
     "\tvar probe: Vector3 = feet + fwd * reach\n"
     "\tvar excl: Array[RID] = [body.get_rid()]\n"
     "\tvar query := PhysicsRayQueryParameters3D.create(\n"
     "\t\tprobe + Vector3.UP * (max_step_up + STEP_PROBE_MARGIN),\n"
     "\t\tprobe + Vector3.DOWN * STEP_PROBE_MARGIN, LT_Const.LAYER_WORLD, excl)\n"
     "\tvar hit: Dictionary = body.get_world_3d().direct_space_state.intersect_ray(query)\n"
     "\tif hit.is_empty():\n"
     "\t\treturn false\n"
     "\tvar top: Vector3 = hit[\"position\"]\n"
     "\tvar normal: Vector3 = hit[\"normal\"]\n"
     "\tvar rise: float = top.y - feet.y\n"
     "\tif rise <= STEP_MIN_RISE or rise > max_step_up:\n"
     "\t\treturn false\n"
     "\tif normal.angle_to(Vector3.UP) > body.floor_max_angle:\n"
     "\t\treturn false\n"
     "\tvar lift: Vector3 = Vector3.UP * (rise + STEP_PROBE_MARGIN)\n"
     "\tif body.test_move(body.global_transform, lift):\n"
     "\t\treturn false\n"
     "\tif body.test_move(body.global_transform.translated(lift), fwd * reach):\n"
     "\t\treturn false\n"
     "\tbody.global_position = feet + lift + fwd * reach\n"
     "\tbody.velocity.y = 0.0\n"
     "\tsteps_taken += 1\n"
     "\treturn true\n"
     "\n"
     "\n"
     "func _body_radius() -> float:\n"
     "\tvar shape_node := body.get_node_or_null(\"CollisionShape3D\") as CollisionShape3D\n"
     "\tif shape_node != null and shape_node.shape is CapsuleShape3D:\n"
     "\t\treturn (shape_node.shape as CapsuleShape3D).radius\n"
     "\treturn nav_agent.radius if nav_agent != null else 0.35\n"
     "\n"
     "\n"
     "func _fire_at(enemy: Node3D) -> void:\n"),
]

SCENARIO = [
    ("@export var player_walk_speed_mps: float = 4.0\n",
     "@export var player_walk_speed_mps: float = 4.0\n"
     "## The contract's `characters.player.max_step_up_m`: how tall a step the\n"
     "## player's controller lifts itself over. The crew bot steps up to this,\n"
     "## onto a top it can stand on (0.24.0, roadmap 203). 0 turns step-up off.\n"
     "@export var player_max_step_up_m: float = 0.5\n"),
]

HARNESS = [
    ("\tif bot_c != null:\n"
     "\t\tbot_c.move_speed = scenario.player_walk_speed_mps\n",
     "\tif bot_c != null:\n"
     "\t\tbot_c.move_speed = scenario.player_walk_speed_mps\n"
     "\t\t# THE CONTRACT'S STEP-UP (0.24.0, roadmap 203): the bot lifts itself over\n"
     "\t\t# what the contract's player does, onto a top it can stand on.\n"
     "\t\tbot_c.max_step_up = scenario.player_max_step_up_m\n"),
]

FILES = [
    (LT / "scripts" / "player" / "LT_BotPlayerController.gd", 16345, BOT),
    (LT / "resources" / "LT_TestScenario.gd", 6631, SCENARIO),
    (LT / "scripts" / "core" / "LT_MapEvalHarness.gd", 42165, HARNESS),
]


def _load(path, size):
    data = path.read_bytes()
    assert len(data) == size, "%s is %d bytes, read at %d" % (path.name, len(data), size)
    crlf, lf = data.count(b"\r\n"), data.count(b"\n")
    assert crlf in (0, lf), "%s mixes endings (%d CRLF of %d lines); refused" % (path.name, crlf, lf)
    text = data.decode("utf-8")
    return data, text.replace("\r\n", "\n"), crlf == lf and lf > 0


def main():
    check = "--check" in sys.argv[1:]
    staged = []
    for path, size, edits in FILES:
        data, text, is_crlf = _load(path, size)
        for old, new in edits:
            assert text.count(old) == 1, "%s: anchor found %d times: %r" % (path.name, text.count(old), old[:70])
            text = text.replace(old, new)
        out = (text.replace("\n", "\r\n") if is_crlf else text).encode("utf-8")
        staged.append((path, data, out, is_crlf))
    for path, data, out, is_crlf in staged:
        tag = "CRLF" if is_crlf else "LF"
        if check:
            print("%s: every anchor matched once (%d -> %d bytes, %s, not written)" % (path.name, len(data), len(out), tag))
            continue
        path.write_bytes(out)
        print("%s: %d -> %d bytes (%s)" % (path.name, len(data), len(out), tag))


if __name__ == "__main__":
    main()
