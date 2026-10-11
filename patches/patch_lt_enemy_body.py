"""Laser Tag 0.26.0: an enemy is the contract's body too -- built from the scenario's body and
steered with the arrival radius the crew has derived since 0.18.0 (roadmap 197).

Anchored edits: `scripts/core/LT_Const.gd` (`arrival_radius`, the 0.18.0 formula, one definition
for every body), `scripts/player/LT_BotPlayerController.gd` (the crew's `_align_agent_to_mesh`
calls it; the same number), `scripts/enemy/LT_EnemyMovement.gd` (`_align_agent_to_mesh` on the
first destination: the path height offset and the arrival radius from the body and the map),
`scripts/core/LT_MapEvalHarness.gd` (`_configure_enemy` applies `_apply_body`), and a new
`runners/tests/test_enemy_is_the_contracts.gd` from `lt_enemy_body/test_enemy_is_the_contracts.gd.txt`.
Each file pinned by hash and each anchor asserted once, nothing written on a miss; the files' own
line endings kept. Applies on 0.25.0. CHANGELOG and VERSION from `lt_enemy_body/CHANGELOG_0.26.0.md`;
`--results-pending` leaves the RESULT_ keys to `--fill`.

    python patches/patch_lt_enemy_body.py --results-pending
    python patches/patch_lt_enemy_body.py --fill
    LT_ROOT=<a copy, or a staged project's root> python patches/patch_lt_enemy_body.py --draft
"""
import hashlib
import os
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
LT = pathlib.Path(os.environ.get("LT_ROOT") or HERE.parent / "lasertag")
SRC = HERE / "lt_enemy_body"
DRAFT = "--draft" in sys.argv
PENDING = "--results-pending" in sys.argv
FILL = "--fill" in sys.argv
RESULTS = {"RESULT_AB": "result_ab.txt", "RESULT_TESTS": "result_tests.txt"}
VERSION_WAS, VERSION = b"Laser Tag 0.25.0", b"Laser Tag 0.26.0"
CHANGELOG_HEAD = "# Changelog\n\n## [0.25.0] - a route that ended on a skip is not a route walked\n"
A = "addons/laser_tag_tool/"
CONST = A + "scripts/core/LT_Const.gd"
BOT = A + "scripts/player/LT_BotPlayerController.gd"
MOVE = A + "scripts/enemy/LT_EnemyMovement.gd"
HARNESS = A + "scripts/core/LT_MapEvalHarness.gd"
TEST = A + "runners/tests/test_enemy_is_the_contracts.gd"
SHA = {CONST: "8809bc007c6dd56d", BOT: "45f0ecd403e8cee6", MOVE: "d152be0d8bf06a4e",
       HARNESS: "cc6418b56da9d64d"}

C_OLD = ("\treturn Vector3(cos(angle) * radius, 0.0, sin(angle) * radius)\n"
         "\n"
         "static func _ensure_key(action: StringName, keycode: Key) -> void:\n")
C_NEW = ("\treturn Vector3(cos(angle) * radius, 0.0, sin(angle) * radius)\n"
         "\n"
         "## How near a waypoint must be before a body counts it reached -- ONE\n"
         "## definition for every body (0.26.0). Three terms, combined in 3D because\n"
         "## Godot measures `path_desired_distance` that way: the body's radius (a\n"
         "## waypoint inside its own footprint IS reached), one physics tick of travel\n"
         "## (below it the body steps over the threshold between two samples), and half\n"
         "## a cell height (what `path_height_offset` cannot remove). The crew's\n"
         "## controller derived this inline from 0.18.0; the enemy took the pill\n"
         "## scene's 0.8 until 0.26.0 -- the value 0.18.0 measured cutting corners.\n"
         "static func arrival_radius(radius: float, speed: float, ticks: float,\n"
         "\t\tcell_height: float) -> float:\n"
         "\tvar horizontal: float = maxf(0.05, radius) + speed / maxf(1.0, ticks)\n"
         "\tvar vertical: float = cell_height * 0.5\n"
         "\treturn sqrt(horizontal * horizontal + vertical * vertical)\n"
         "\n"
         "static func _ensure_key(action: StringName, keycode: Key) -> void:\n")

B_OLD = ("\tvar ticks: float = maxf(1.0, float(Engine.physics_ticks_per_second))\n"
         "\tvar per_frame: float = move_speed / ticks\n"
         "\tvar horizontal: float = maxf(0.05, nav_agent.radius) + per_frame\n"
         "\tvar vertical: float = cell_height * 0.5\n"
         "\tnav_agent.path_desired_distance = sqrt(\n"
         "\t\thorizontal * horizontal + vertical * vertical)\n")
B_NEW = ("\t#\n"
         "\t# ONE DEFINITION FOR EVERY BODY since 0.26.0 (`LT_Const.arrival_radius`):\n"
         "\t# the enemy derives its own from the same terms, where it used to keep the\n"
         "\t# pill scene's 0.8. The same number here as before, to the bit.\n"
         "\tnav_agent.path_desired_distance = LT_Const.arrival_radius(\n"
         "\t\tnav_agent.radius, move_speed,\n"
         "\t\tfloat(Engine.physics_ticks_per_second), cell_height)\n")

M_VAR_OLD = "var _stuck_reported: bool = false\n"
M_VAR_NEW = ("var _stuck_reported: bool = false\n"
             "## Set once the agent has its arrival radius and path height offset (0.26.0).\n"
             "var _aligned: bool = false\n")
M_SET_OLD = ("func set_destination(destination: Vector3) -> void:\n"
             "\t_wants_to_move = true\n"
             "\tif use_navigation and nav_agent != null:\n"
             "\t\tnav_agent.target_position = destination\n")
M_SET_NEW = ("func set_destination(destination: Vector3) -> void:\n"
             "\t_wants_to_move = true\n"
             "\tif use_navigation and nav_agent != null:\n"
             "\t\t_align_agent_to_mesh()\n"
             "\t\tnav_agent.target_position = destination\n")
M_STOP_OLD = "func stop() -> void:\n"
M_STOP_NEW = ("## Steer the enemy as the crew is steered (0.26.0, roadmap 197): the arrival\n"
              "## radius from the body and the bake, and every returned path point lowered\n"
              "## by the bake's cell height to the feet that walk to it -- what\n"
              "## `LT_BotPlayerController._align_agent_to_mesh` has done for the crew since\n"
              "## 0.18.0. The pill scene's `path_desired_distance` 0.8 counts a waypoint\n"
              "## reached from 0.8 m away, so at a door the body turns for the next one\n"
              "## before it is through and walks into the jamb; 0.18.0 measured exactly\n"
              "## that for the crew. Read from the MAP once one is known, so a different\n"
              "## bake stays right without an edit here; `nav_agent.radius` is the body's,\n"
              "## set by the harness from the scenario.\n"
              "func _align_agent_to_mesh() -> void:\n"
              "\tif _aligned or nav_agent == null:\n"
              "\t\treturn\n"
              "\tvar map: RID = nav_agent.get_navigation_map()\n"
              "\tif not map.is_valid():\n"
              "\t\treturn\n"
              "\tvar cell_height: float = NavigationServer3D.map_get_cell_height(map)\n"
              "\tnav_agent.path_height_offset = cell_height\n"
              "\tnav_agent.path_desired_distance = LT_Const.arrival_radius(\n"
              "\t\tnav_agent.radius, move_speed,\n"
              "\t\tfloat(Engine.physics_ticks_per_second), cell_height)\n"
              "\t_aligned = true\n"
              "\n"
              "func stop() -> void:\n")

H_OLD = ("func _configure_enemy(pill: Node) -> void:\n"
         "\tvar health: LT_Health = pill.get_node(\"LT_Health\")\n"
         "\thealth.max_health = scenario.enemy_health\n")
H_NEW = ("func _configure_enemy(pill: Node) -> void:\n"
         "\t# THE ENEMY'S BODY IS THE CONTRACT'S (0.26.0, roadmap 197). `_apply_body`\n"
         "\t# built only the crew, and every enemy kept `LT_EnemyPill.tscn`'s capsule\n"
         "\t# of radius 0.40 -- the BAKE's agent radius, which agent_contract.json says\n"
         "\t# \"is NOT a body radius and nothing should be built from it\" -- so it met\n"
         "\t# every corner the navmesh rounds by 0.40 with no clearance at all.\n"
         "\t# npc_standard shares the player's metrics until a distinct class ships\n"
         "\t# (the reason the eye below reads one field), so the crew's fields build it;\n"
         "\t# the camera and controller parts of `_apply_body` find nothing on an enemy.\n"
         "\t_apply_body(pill)\n"
         "\tvar health: LT_Health = pill.get_node(\"LT_Health\")\n"
         "\thealth.max_health = scenario.enemy_health\n")


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


def _read(rel):
    p = LT / rel
    raw = p.read_bytes()
    got = hashlib.sha256(raw.replace(b"\r\n", b"\n")).hexdigest()[:16]
    assert got == SHA[rel], (rel, "is not the file this patch read", got)
    return p, _eol(raw, rel), raw.decode("utf-8").replace("\r\n", "\n")


def _write(p, eol, text):
    p.write_bytes(text.replace("\n", eol.decode()).encode("utf-8"))


def fill():
    assert (LT / "VERSION").read_bytes().strip() == VERSION, (LT / "VERSION").read_bytes()
    results = {}
    for key, name in RESULTS.items():
        value = (SRC / name).read_text(encoding="utf-8").strip()
        assert value and "RESULT_" not in value and not value.endswith("."), (name, value[-40:])
        results[key] = value
    writes = {}
    for path, rel in [(LT / "CHANGELOG.md", "CHANGELOG.md"), (SRC / "CHANGELOG_0.26.0.md", "the entry")]:
        raw = path.read_bytes()
        eol = _eol(raw, rel)
        text = raw.decode("utf-8").replace("\r\n", "\n")
        for key, value in results.items():
            assert text.count(key) == 1, (rel, key, text.count(key))
            text = text.replace(key, value)
        writes[path] = text.encode("utf-8").replace(b"\n", eol)
    for path, data in writes.items():
        path.write_bytes(data)
    print("Laser Tag 0.26.0: results filled")


def main():
    if FILL:
        return fill()
    if DRAFT and not os.environ.get("LT_ROOT"):
        sys.exit("refusing: --draft is for an LT_ROOT copy, never the repo")
    test_text = _src("test_enemy_is_the_contracts.gd.txt")
    assert not (LT / TEST).exists(), "already applied"

    cp, c_eol, const = _read(CONST)
    assert "func arrival_radius" not in const, "already applied"
    const = _once(const, C_OLD, C_NEW, "LT_Const: the helper before _ensure_key")
    bp, b_eol, bot = _read(BOT)
    bot = _once(bot, B_OLD, B_NEW, "the crew's derivation")
    mp, m_eol, move = _read(MOVE)
    move = _once(move, M_VAR_OLD, M_VAR_NEW, "the movement's state")
    move = _once(move, M_SET_OLD, M_SET_NEW, "set_destination")
    move = _once(move, M_STOP_OLD, M_STOP_NEW, "the align function before stop")
    hp, h_eol, harness = _read(HARNESS)
    harness = _once(harness, H_OLD, H_NEW, "_configure_enemy")

    # A staged project carries the addon and not the repository's CHANGELOG or VERSION: a draft
    # there is the code change alone, which is what an A/B on a staged level needs.
    staged = DRAFT and not (LT / "CHANGELOG.md").exists()
    if not staged:
        assert (LT / "VERSION").read_bytes().strip() == VERSION_WAS, (LT / "VERSION").read_bytes()
        entry = _src("CHANGELOG_0.26.0.md")
        assert entry.startswith("## [0.26.0] - "), entry[:40]
        if not DRAFT:
            left = entry
            if PENDING:
                for key in RESULTS:
                    left = left.replace(key, "")
            assert "RESULT_" not in left, "the changelog still carries an unfilled result"
        cl = LT / "CHANGELOG.md"
        cl_raw = cl.read_bytes()
        cl_eol = _eol(cl_raw, "CHANGELOG.md")
        cl_text = cl_raw.decode("utf-8").replace("\r\n", "\n")
        assert cl_text.startswith(CHANGELOG_HEAD) and cl_text.count(CHANGELOG_HEAD) == 1, cl_text[:120]
    # every anchor matched: now write
    _write(cp, c_eol, const)
    _write(bp, b_eol, bot)
    _write(mp, m_eol, move)
    _write(hp, h_eol, harness)
    (LT / TEST).write_bytes(test_text.encode("utf-8"))
    if not staged:
        head = "# Changelog\n\n"
        _write(cl, cl_eol, head + entry.rstrip("\n") + "\n\n" + cl_text[len(head):])
        (LT / "VERSION").write_bytes(VERSION)
    print("Laser Tag 0.25.0 -> 0.26.0" + (" (DRAFT" + (", code only, staged project)" if staged else ")") if DRAFT else ""))


if __name__ == "__main__":
    main()
