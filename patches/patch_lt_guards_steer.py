"""Laser Tag 0.31.0: the guards walk as the crew does -- they keep to the mesh and step up (factory roadmap 242;
the 23 events 0.30.0 still counted, placed in the factory's `docs/findings/stoop_breadth/`).

Anchored edits, each asserted exactly once and every file's sha16 pinned, nothing written until all of them
matched:
  addons/laser_tag_tool/scripts/core/LT_Steering.gd            NEW: the crew bot's keep-to-the-mesh and
                                                                step-up, moved as static functions
  addons/laser_tag_tool/scripts/player/LT_BotPlayerController.gd   three spans, each pinned by its own sha16,
                                                                become calls into LT_Steering: the constants,
                                                                `_try_step_up` with `_body_radius` (its one
                                                                caller), `_velocity_on_mesh`
  addons/laser_tag_tool/scripts/enemy/LT_EnemyMovement.gd      `max_step_up`, `keep_to_mesh`, `steps_taken`;
                                                                `_physics_process` keeps the step on the mesh
                                                                and steps up after the slide; 0.30.0's "73 of
                                                                75" corrected
  addons/laser_tag_tool/scripts/core/LT_MapEvalHarness.gd      `_apply_body` gives a guard the scenario's step
  addons/laser_tag_tool/runners/tests/test_guards_walk_as_the_crew.gd   NEW
CHANGELOG and VERSION from `lt_guards_steer/CHANGELOG_0.31.0.md`; `--results-pending` leaves the RESULT_ keys
to `--fill`.

Read before it was written, in this session: `LT_BotPlayerController.gd`'s step-up block (constants,
`_physics_process`, `_try_step_up`, `_body_radius` and its one caller), `_advance_route` and
`_velocity_on_mesh`; `LT_EnemyMovement.gd` whole; `LT_MapEvalHarness.gd`'s `_apply_body` and
`_configure_player`; `LT_TestScenario.gd`'s body fields; `LT_EnemyPill.tscn`; `LT_Const.gd`'s head and
`synchronous_navigation`; the crew's `test_bot_keeps_to_the_mesh.gd` and `test_step_up_is_the_contracts.gd`;
`agent_contract.json`'s `characters` (npc_standard: "share player metrics until a distinct class ships").
Every file LF.

    python patches/patch_lt_guards_steer.py --results-pending
    (every runners/tests script headless in lasertag; the breadth)
    python patches/patch_lt_guards_steer.py --fill
"""
import hashlib
import os
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
LT = pathlib.Path(os.environ.get("LT_ROOT") or HERE.parent / "lasertag")
SRC = HERE / "lt_guards_steer"
PENDING = "--results-pending" in sys.argv
FILL = "--fill" in sys.argv
RESULTS = {"RESULT_TESTS": "result_tests.txt", "RESULT_BREADTH": "result_breadth.txt"}
VERSION_WAS, VERSION = b"Laser Tag 0.30.0", b"Laser Tag 0.31.0"
#: the changelog keeps a title above its entries; the new entry goes under it
CHANGELOG_TITLE = "# Changelog\n\n"
CHANGELOG_HEAD = CHANGELOG_TITLE + "## [0.30.0] - a guard held by another bot is blocked, not stuck"
BOT = "addons/laser_tag_tool/scripts/player/LT_BotPlayerController.gd"
MOVE = "addons/laser_tag_tool/scripts/enemy/LT_EnemyMovement.gd"
HARNESS = "addons/laser_tag_tool/scripts/core/LT_MapEvalHarness.gd"
SHA = {BOT: "8e9356ff5e712389", MOVE: "d21cabdafb71aaec", HARNESS: "74ab96a5614e41d6"}
NEW = {"addons/laser_tag_tool/scripts/core/LT_Steering.gd": "LT_Steering.gd.txt",
       "addons/laser_tag_tool/runners/tests/test_guards_walk_as_the_crew.gd": "test_guards_walk_as_the_crew.gd.txt"}

#: the crew bot's blocks that move to LT_Steering: (first line, last line, the block's sha16, what replaces it).
#: Pinned by hash rather than quoted, as the blocks are long; the file's own sha16 above pins the whole of it.
SPANS = {
    BOT: [
        ("## How far past the body the step probe looks, and how far above the limit it\n",
         "const MESH_LEVEL_M: float = 0.5\n", "14f1ac6554e8474e",
         "## The step-up's and the mesh's tolerances live with the code that reads them,\n"
         "## `LT_Steering` (0.31.0), which the guards share.\n"),
        ("## A STEP, NEVER A SLOPE (0.24.0, roadmap 203).\n",
         "\treturn nav_agent.radius if nav_agent != null else 0.35\n", "d8859d9fc8cdb477",
         "## A STEP, NEVER A SLOPE (0.24.0, roadmap 203): `LT_Steering.try_step_up`, which\n"
         "## the guards share since 0.31.0.\n"
         "func _try_step_up(intended: Vector3) -> bool:\n"
         "\tif not LT_Steering.try_step_up(body, nav_agent, intended, max_step_up):\n"
         "\t\treturn false\n"
         "\tsteps_taken += 1\n"
         "\treturn true\n"),
        ("## THE BODY KEEPS TO THE MESH IT PLANS ON (0.29.0, factory roadmap 242).\n## The bot turns toward",
         "\treturn to_mesh\n", "cb9b04f886af3c22",
         "## THE BODY KEEPS TO THE MESH IT PLANS ON (0.29.0, factory roadmap 242):\n"
         "## `LT_Steering.velocity_on_mesh`, which the guards share since 0.31.0. A bot\n"
         "## walking without navigation is left be.\n"
         "func _velocity_on_mesh(velocity: Vector3, delta: float) -> Vector3:\n"
         "\tif not use_navigation:\n"
         "\t\treturn velocity\n"
         "\treturn LT_Steering.velocity_on_mesh(body, nav_agent, velocity, delta)\n"),
    ],
}

EDITS = {
    MOVE: [
        ("## so a guard behind a guard stood still and was `stuck_detected` -- 73 of 75 such events traced on\n"
         "## the factory's lots -- and NPC Pathing charged the map for the bots' own crowding.\n",
         "## so a guard behind a guard stood still and was `stuck_detected` -- 74 of 75 such events traced on\n"
         "## the factory's lots had another body among their contacts -- and NPC Pathing charged the map for\n"
         "## the bots' own crowding.\n"),
        ("@export var use_navigation: bool = true\n",
         "@export var use_navigation: bool = true\n"
         "\n"
         "## THE GUARD WALKS AS THE CREW DOES (0.31.0, factory roadmap 242): `LT_Steering`, the crew bot's\n"
         "## own copy. `agent_contract.json` says npc_standard shares the player's metrics until a distinct\n"
         "## class ships, so the harness sets this from the scenario's `player_max_step_up_m` (0.5), as it\n"
         "## sets the crew's. 0 turns step-up off.\n"
         "@export var max_step_up: float = 0.5\n"
         "## Keep each step on the mesh the guard plans on, as the crew has since 0.29.0. Off, the guard steers\n"
         "## straight at its next path point, as it did before 0.31.0.\n"
         "@export var keep_to_mesh: bool = true\n"
         "## Step-ups taken: what the step-up did, for a reader of a run.\n"
         "var steps_taken: int = 0\n"),
        ("\t\tif flat.length() > 0.05:\n"
         "\t\t\tvar direction := flat.normalized()\n"
         "\t\t\tbody.velocity.x = direction.x * move_speed\n"
         "\t\t\tbody.velocity.z = direction.z * move_speed\n"
         "\t\t\t_face(direction)\n",
         "\t\tif flat.length() > 0.05:\n"
         "\t\t\tvar direction := flat.normalized()\n"
         "\t\t\tvar v: Vector3 = direction * move_speed\n"
         "\t\t\tif keep_to_mesh and use_navigation:\n"
         "\t\t\t\tv = LT_Steering.velocity_on_mesh(body, nav_agent, v, delta)\n"
         "\t\t\tbody.velocity.x = v.x\n"
         "\t\t\tbody.velocity.z = v.z\n"
         "\t\t\t_face(direction)\n"),
        ("\tbody.move_and_slide()\n"
         "\t_update_stuck(delta)\n",
         "\t# the way the guard MEANT to go, before the slide turns it along whatever it hit: the step-up\n"
         "\t# asks about that wall, not about the slide (0.31.0, the crew's since 0.24.0)\n"
         "\tvar intended := Vector3(body.velocity.x, 0.0, body.velocity.z)\n"
         "\tbody.move_and_slide()\n"
         "\tif LT_Steering.try_step_up(body, nav_agent, intended, max_step_up):\n"
         "\t\tsteps_taken += 1\n"
         "\t_update_stuck(delta)\n"),
    ],
    HARNESS: [
        ("\t\tbot_c.max_step_up = scenario.player_max_step_up_m\n"
         "\n"
         "\tvar agent: NavigationAgent3D = pill.get_node_or_null(\"NavigationAgent3D\")\n",
         "\t\tbot_c.max_step_up = scenario.player_max_step_up_m\n"
         "\n"
         "\t# THE GUARD'S STEP-UP (0.31.0, roadmap 242): npc_standard shares the player's\n"
         "\t# metrics until a distinct class ships (`agent_contract.json`), so a guard\n"
         "\t# lifts itself over what the crew does.\n"
         "\tvar guard: LT_EnemyMovement = pill.get_node_or_null(\"LT_EnemyMovement\")\n"
         "\tif guard != null:\n"
         "\t\tguard.max_step_up = scenario.player_max_step_up_m\n"
         "\n"
         "\tvar agent: NavigationAgent3D = pill.get_node_or_null(\"NavigationAgent3D\")\n"),
    ],
}


def _eol(raw, rel):
    crlf = raw.count(b"\r\n")
    lf = raw.count(b"\n")
    assert crlf in (0, lf), (rel, "mixed line endings", crlf, lf)
    return b"\r\n" if crlf else b"\n"


def _span(text, rel, first, last, sha, new):
    assert text.count(first) == 1, (rel, "span start", text.count(first), first[:60])
    i = text.index(first)
    j = text.find(last, i)
    assert j > i and text.count(last) == 1, (rel, "span end", text.count(last), last[:60])
    j += len(last)
    got = hashlib.sha256(text[i:j].encode("utf-8")).hexdigest()[:16]
    assert got == sha, (rel, "the span is not the block this patch read", first[:60], got)
    return text[:i] + new + text[j:]


def fill():
    assert (LT / "VERSION").read_bytes().strip() == VERSION, (LT / "VERSION").read_bytes()
    results = {}
    for key, name in RESULTS.items():
        value = (SRC / name).read_text(encoding="utf-8").strip()
        assert value and "RESULT_" not in value and not value.endswith("."), (name, value[-40:])
        results[key] = value
    writes = {}
    for path, rel in [(LT / "CHANGELOG.md", "CHANGELOG.md"), (SRC / "CHANGELOG_0.31.0.md", "the entry")]:
        raw = path.read_bytes()
        eol = _eol(raw, rel)
        text = raw.decode("utf-8").replace("\r\n", "\n")
        for key, value in results.items():
            assert text.count(key) == 1, (rel, key, text.count(key))
            text = text.replace(key, value)
        writes[path] = text.encode("utf-8").replace(b"\n", eol)
    for path, data in writes.items():
        path.write_bytes(data)
    print("Laser Tag 0.31.0: results filled")


def main():
    if FILL:
        return fill()
    assert (LT / "VERSION").read_bytes().strip() == VERSION_WAS, (LT / "VERSION").read_bytes()
    entry = (SRC / "CHANGELOG_0.31.0.md").read_bytes().decode("utf-8").replace("\r\n", "\n")
    assert entry.startswith("## [0.31.0] - "), entry[:40]
    left = entry
    for key in RESULTS if PENDING else ():
        left = left.replace(key, "")
    assert "RESULT_" not in left, "the changelog still carries an unfilled result"
    for rel in NEW:
        assert not (LT / rel).exists(), ("already applied", rel)
    writes = {}
    for rel in sorted(set(EDITS) | set(SPANS)):
        p = LT / rel
        raw = p.read_bytes()
        got = hashlib.sha256(raw.replace(b"\r\n", b"\n")).hexdigest()[:16]
        assert got == SHA[rel], (rel, "is not the file this patch read", got)
        eol = _eol(raw, rel)
        text = raw.decode("utf-8").replace("\r\n", "\n")
        for first, last, sha, new in SPANS.get(rel, ()):
            text = _span(text, rel, first, last, sha, new)
        for old, new in EDITS.get(rel, ()):
            assert text.count(old) == 1, (rel, "anchor", text.count(old), old[:80])
            text = text.replace(old, new)
        writes[p] = text.encode("utf-8").replace(b"\n", eol)
    # nothing the crew bot moved may be left behind, and nothing it reads may have gone with it
    bot = writes[LT / BOT].decode("utf-8")
    for gone in ("STEP_PROBE_MARGIN", "STEP_MIN_RISE", "STEP_FACING_DOT", "MESH_TOLERANCE_M", "MESH_LEVEL_M",
                 "_body_radius"):
        assert gone not in bot, ("the crew bot still names", gone)
    news = {rel: (SRC / src).read_bytes().replace(b"\r\n", b"\n") for rel, src in NEW.items()}
    cl = LT / "CHANGELOG.md"
    cl_raw = cl.read_bytes()
    cl_eol = _eol(cl_raw, "CHANGELOG.md")
    cl_text = cl_raw.decode("utf-8").replace("\r\n", "\n")
    assert cl_text.startswith(CHANGELOG_HEAD), cl_text[:120]
    # every anchor matched: now write
    for p, data in writes.items():
        p.write_bytes(data)
    for rel, data in news.items():
        (LT / rel).write_bytes(data)
    cl.write_bytes((CHANGELOG_TITLE + entry.rstrip("\n") + "\n\n" + cl_text[len(CHANGELOG_TITLE):])
                   .encode("utf-8").replace(b"\n", cl_eol))
    (LT / "VERSION").write_bytes(VERSION)
    print("Laser Tag 0.30.0 -> 0.31.0")


if __name__ == "__main__":
    main()
