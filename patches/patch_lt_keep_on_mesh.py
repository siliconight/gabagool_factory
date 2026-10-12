"""Laser Tag 0.28.0: the bot keeps to the mesh it plans on, so it stops meeting the corners it is routed
round (factory roadmap 242; docs/findings/route_snag/).

Anchored edits, each asserted once, nothing written until all of them matched:
  addons/laser_tag_tool/scripts/player/LT_BotPlayerController.gd
      `MESH_TOLERANCE_M` and `MESH_LEVEL_M` after the step constants; `_advance_route` reads its
      `delta` and moves at `_velocity_on_mesh`'s velocity; `_velocity_on_mesh` before the route-walked
      rule
  addons/laser_tag_tool/runners/tests/test_bot_keeps_to_the_mesh.gd   NEW
CHANGELOG and VERSION from `lt_keep_on_mesh/CHANGELOG_0.28.0.md`; `--results-pending` leaves the
RESULT_ keys to `--fill`.

Read before it was written: `_advance_route` (the movement at its end, the `_delta` it never read),
`_next_path_point`, `_align_agent_to_mesh` (the agent's arrival radius, `path_height_offset` a cell),
`run_map_eval.gd`'s bake (the contract's NAV_* numbers), and `test_step_up_is_the_contracts.gd` (the
test's shape: the real pill over real colliders). Laser Tag's `project.godot` is not tracked, so a
draft copy needs the repository's own beside it, and an editor scan to know the classes.

    python patches/patch_lt_keep_on_mesh.py --results-pending
    for t in lasertag/addons/laser_tag_tool/runners/tests/*.gd; do godot --headless --path lasertag -s res://${t#lasertag/}; done
    python patches/patch_lt_keep_on_mesh.py --fill
    LT_ROOT=<copy> python patches/patch_lt_keep_on_mesh.py --draft
"""
import hashlib
import os
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
LT = pathlib.Path(os.environ.get("LT_ROOT") or HERE.parent / "lasertag")
SRC = HERE / "lt_keep_on_mesh"
DRAFT = "--draft" in sys.argv
PENDING = "--results-pending" in sys.argv
FILL = "--fill" in sys.argv
RESULTS = {"RESULT_MEASURED": "result_measured.txt", "RESULT_TESTS": "result_tests.txt",
           "RESULT_SUITE": "result_suite.txt"}
VERSION_WAS, VERSION = b"Laser Tag 0.27.0", b"Laser Tag 0.28.0"
CHANGELOG_HEAD = ("# Changelog\n\n## [0.27.0] - the navigation map updates on the evaluation's thread, so "
                  "the clock need not wait\n")
BOT = "addons/laser_tag_tool/scripts/player/LT_BotPlayerController.gd"
TEST = "addons/laser_tag_tool/runners/tests/test_bot_keeps_to_the_mesh.gd"
SHA = {BOT: "ce35a0c24574ddc8"}

CONST_OLD = ("## How squarely the wall must face the walk (cos of 72.5 deg). A wall the bot\n"
             "## slides along at a shallower angle is not in its way.\n"
             "const STEP_FACING_DOT: float = 0.3\n")
CONST_NEW = (CONST_OLD +
             "\n"
             "## THE BODY KEEPS TO THE MESH IT PLANS ON (0.28.0, factory roadmap 242).\n"
             "## How far the end of a step may sit from the mesh before it is turned back\n"
             "## onto it: a centimetre, against the 5 cm the contract's bake (0.4 m) leaves\n"
             "## the 0.35 m body. A tolerance for the closest-point query's own rounding,\n"
             "## not a clearance.\n"
             "const MESH_TOLERANCE_M: float = 0.01\n"
             "## A nearest mesh point more than this above or below the step's end is on\n"
             "## another level -- a floor above, a ramp's far side -- and not the step's to\n"
             "## judge: the contract's step (`player_max_step_up_m`, 0.5).\n"
             "const MESH_LEVEL_M: float = 0.5\n")

SIG_OLD = "func _advance_route(_delta: float) -> void:\n"
SIG_NEW = "func _advance_route(delta: float) -> void:\n"

MOVE_OLD = ("\tif flat.length() > 0.05:\n"
            "\t\tvar direction := flat.normalized()\n"
            "\t\tbody.velocity.x = direction.x * move_speed\n"
            "\t\tbody.velocity.z = direction.z * move_speed\n"
            "\t\t_face_point(body.global_position + direction)\n"
            "\telse:\n"
            "\t\t_stop_horizontal()\n"
            "\n"
            "## A ROUTE IS WALKED WHEN EVERY POINT ON IT WAS REACHED (0.25.0, roadmap\n")
MOVE_NEW = ("\tif flat.length() > 0.05:\n"
            "\t\tvar direction := flat.normalized()\n"
            "\t\tvar v: Vector3 = _velocity_on_mesh(direction * move_speed, delta)\n"
            "\t\tbody.velocity.x = v.x\n"
            "\t\tbody.velocity.z = v.z\n"
            "\t\t_face_point(body.global_position + direction)\n"
            "\telse:\n"
            "\t\t_stop_horizontal()\n"
            "\n"
            "## THE BODY KEEPS TO THE MESH IT PLANS ON (0.28.0, factory roadmap 242).\n"
            "## The bot turns toward its next path point once within its arrival radius,\n"
            "## about 0.44 m (`LT_Const.arrival_radius`), and the straight line from there\n"
            "## to a point round a corner cuts the corner: off the mesh, into the 0.4 m the\n"
            "## contract's bake keeps from every collider, where the 0.35 m body has 5 cm.\n"
            "## Measured in the factory (`docs/findings/route_snag/`): on restaurant_row_001\n"
            "## 64 of a candidate's 72 player-stuck events stood at one deli counter's\n"
            "## corner, pinned by Godot Physics; across sixteen lots Jolt pinned bodies at\n"
            "## other corners. So a step whose end leaves the mesh is turned toward the\n"
            "## mesh's nearest point to that end, at no more than the speed it had: the\n"
            "## body slides along the mesh's edge round the corner at the bake's clearance.\n"
            "## `velocity` is horizontal; what comes back is too.\n"
            "func _velocity_on_mesh(velocity: Vector3, delta: float) -> Vector3:\n"
            "\tif not use_navigation or nav_agent == null or delta <= 0.0:\n"
            "\t\treturn velocity\n"
            "\tvar map: RID = nav_agent.get_navigation_map()\n"
            "\tif not map.is_valid() or NavigationServer3D.map_get_iteration_id(map) == 0:\n"
            "\t\treturn velocity\n"
            "\tvar here: Vector3 = body.global_position\n"
            "\tvar want: Vector3 = here + Vector3(velocity.x, 0.0, velocity.z) * delta\n"
            "\t# the mesh sits a cell above the floor the feet stand on (`path_height_offset`)\n"
            "\tvar lift: float = NavigationServer3D.map_get_cell_height(map)\n"
            "\tvar on: Vector3 = NavigationServer3D.map_get_closest_point(map, want + Vector3.UP * lift)\n"
            "\tif absf(on.y - lift - want.y) > MESH_LEVEL_M:\n"
            "\t\treturn velocity\n"
            "\tif Vector2(on.x - want.x, on.z - want.z).length() <= MESH_TOLERANCE_M:\n"
            "\t\treturn velocity\n"
            "\tvar to_mesh: Vector3 = Vector3(on.x - here.x, 0.0, on.z - here.z) / delta\n"
            "\tvar speed: float = Vector2(velocity.x, velocity.z).length()\n"
            "\tif to_mesh.length() > speed:\n"
            "\t\tto_mesh = to_mesh.normalized() * speed\n"
            "\treturn to_mesh\n"
            "\n"
            "## A ROUTE IS WALKED WHEN EVERY POINT ON IT WAS REACHED (0.25.0, roadmap\n")


def _eol(raw, rel):
    crlf = raw.count(b"\r\n")
    lf = raw.count(b"\n")
    assert crlf in (0, lf), (rel, "mixed line endings", crlf, lf)
    return b"\r\n" if crlf else b"\n"


def _src(name):
    return (SRC / name).read_bytes().decode("utf-8").replace("\r\n", "\n")


def _once(text, old, new, what):
    assert text.count(old) == 1, (what, text.count(old))
    return text.replace(old, new)


def fill():
    assert (LT / "VERSION").read_bytes().strip() == VERSION, (LT / "VERSION").read_bytes()
    results = {}
    for key, name in RESULTS.items():
        value = (SRC / name).read_text(encoding="utf-8").strip()
        assert value and "RESULT_" not in value and not value.endswith("."), (name, value[-40:])
        results[key] = value
    writes = {}
    for path, rel in [(LT / "CHANGELOG.md", "CHANGELOG.md"), (SRC / "CHANGELOG_0.28.0.md", "the entry")]:
        raw = path.read_bytes()
        eol = _eol(raw, rel)
        text = raw.decode("utf-8").replace("\r\n", "\n")
        for key, value in results.items():
            assert text.count(key) == 1, (rel, key, text.count(key))
            text = text.replace(key, value)
        writes[path] = text.encode("utf-8").replace(b"\n", eol)
    for path, data in writes.items():
        path.write_bytes(data)
    print("Laser Tag 0.28.0: results filled")


#: HELD 2026-10-12 (`docs/findings/route_snag/README.md`, "Laser Tag 0.28.0, drafted and HELD"): over 16
#: lots the draft cut player-stuck 108 -> 45 under Godot Physics and 60 -> 44 under Jolt, and made
#: bank_block_001 seed_9256 pin 7 times under each and three deli and gas lots score 10 lower. It writes
#: the repository only once those are attributed and this line is removed; a draft copy is always fine.
HELD = True


def main():
    if FILL:
        return fill()
    if DRAFT and not os.environ.get("LT_ROOT"):
        sys.exit("refusing: --draft is for an LT_ROOT copy, never the repo")
    if HELD and not DRAFT:
        sys.exit("refusing: Laser Tag 0.28.0 is HELD (see HELD above); LT_ROOT=<copy> ... --draft only")
    assert (LT / "VERSION").read_bytes().strip() == VERSION_WAS, (LT / "VERSION").read_bytes()
    entry = _src("CHANGELOG_0.28.0.md")
    assert entry.startswith("## [0.28.0] - "), entry[:40]
    if not DRAFT:
        left = entry
        for key in RESULTS if PENDING else ():
            left = left.replace(key, "")
        assert "RESULT_" not in left, "the changelog still carries an unfilled result"
    assert not (LT / TEST).exists(), "already applied"
    p = LT / BOT
    raw = p.read_bytes()
    got = hashlib.sha256(raw.replace(b"\r\n", b"\n")).hexdigest()[:16]
    assert got == SHA[BOT], (BOT, "is not the file this patch read", got)
    eol = _eol(raw, BOT)
    text = raw.decode("utf-8").replace("\r\n", "\n")
    text = _once(text, CONST_OLD, CONST_NEW, "the step constants")
    text = _once(text, SIG_OLD, SIG_NEW, "_advance_route's signature")
    text = _once(text, MOVE_OLD, MOVE_NEW, "the movement at _advance_route's end")
    test = _src("test_bot_keeps_to_the_mesh.gd.txt")
    cl = LT / "CHANGELOG.md"
    cl_raw = cl.read_bytes()
    cl_eol = _eol(cl_raw, "CHANGELOG.md")
    cl_text = cl_raw.decode("utf-8").replace("\r\n", "\n")
    assert cl_text.startswith(CHANGELOG_HEAD), cl_text[:160]
    cl_new = "# Changelog\n\n" + entry.rstrip("\n") + "\n\n" + cl_text[len("# Changelog\n\n"):]
    # every anchor matched: now write
    p.write_bytes(text.replace("\n", eol.decode()).encode("utf-8"))
    (LT / TEST).write_bytes(test.encode("utf-8"))
    cl.write_bytes(cl_new.replace("\n", cl_eol.decode()).encode("utf-8"))
    (LT / "VERSION").write_bytes(VERSION)
    print("Laser Tag 0.27.0 -> 0.28.0" + (" (DRAFT)" if DRAFT else ""))


if __name__ == "__main__":
    main()
