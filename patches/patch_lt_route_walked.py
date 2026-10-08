"""Laser Tag 0.25.0: a route that ended on a skip is not a route walked
(roadmap 206). With the getaway van at the crew's spawn (Lot 0.98.0) the route
ends where it starts, and a bot jammed in its first seconds was skipped "back
to the van" it stood beside and recorded a finished heist.

New file from `lt_route_walked/`:
`runners/tests/test_a_skipped_route_is_not_walked.gd`. Anchored edits (every
anchor once; refuses on a miss): `scripts/player/LT_BotPlayerController.gd`
(`route_walked`, `walked_whole_route`, `ObjectiveReached` only for a walked
route, `RouteEndedShort` otherwise), `scripts/core/LT_MapEvalHarness.gd` (the
route end arrives with its bot; OBJECTIVE only for a walked route). CHANGELOG
and VERSION from `lt_route_walked/CHANGELOG_0.25.0.md`.

    python patch_lt_route_walked.py
    LT_ROOT=<copy> python patch_lt_route_walked.py

Run the test:  godot --headless --path lasertag -s res://addons/laser_tag_tool/runners/tests/test_a_skipped_route_is_not_walked.gd
"""
import os
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
LT_ROOT = pathlib.Path(os.environ.get("LT_ROOT") or HERE.parent / "lasertag")
LT = LT_ROOT / "addons" / "laser_tag_tool" / "scripts"
SRC = HERE / "lt_route_walked"
TEST = LT_ROOT / "addons" / "laser_tag_tool" / "runners" / "tests" / "test_a_skipped_route_is_not_walked.gd"
CHANGELOG_HEAD = "# Changelog\n\n## [0.24.0] - the crew takes the contract's step-up\n"

T = "\t"

EDITS = {
    "player/LT_BotPlayerController.gd": [
        (T * 3 + "get_tree().call_group(LT_Const.GROUP_METRICS, \"record_event\",\n"
         + T * 4 + "\"ObjectiveReached\", {\"source\": body.name})\n"
         + T * 3 + "route_completed.emit()\n"
         + T * 3 + "return\n",
         T * 3 + "# A ROUTE ENDED ON A SKIP IS NOT A ROUTE WALKED (0.25.0, roadmap\n"
         + T * 3 + "# 206): `route_walked` asks the arrivals, not the index. Said as\n"
         + T * 3 + "# `RouteEndedShort` so the run's log shows where it fell short.\n"
         + T * 3 + "if route_walked(_route_reached, route_points.size()):\n"
         + T * 4 + "get_tree().call_group(LT_Const.GROUP_METRICS, \"record_event\",\n"
         + T * 5 + "\"ObjectiveReached\", {\"source\": body.name})\n"
         + T * 3 + "else:\n"
         + T * 4 + "get_tree().call_group(LT_Const.GROUP_METRICS, \"record_event\",\n"
         + T * 5 + "\"RouteEndedShort\", {\"source\": body.name,\n"
         + T * 6 + "\"reached\": _route_reached, \"total\": route_points.size()})\n"
         + T * 3 + "route_completed.emit()\n"
         + T * 3 + "return\n"),
        ("func _go_to_current_route_point() -> void:\n",
         "## A ROUTE IS WALKED WHEN EVERY POINT ON IT WAS REACHED (0.25.0, roadmap\n"
         "## 206). `_update_stuck` advances `_route_index` past a point the bot is\n"
         "## jammed on, so an index that runs off the end says the route ENDED, not\n"
         "## that it was walked -- and `ObjectiveReached`, which is all\n"
         "## `route_completion_rate` reads, used to fire on the index. With the\n"
         "## getaway van the route ends where it starts (spawn, objective, the van at\n"
         "## the spawn), and a bot jammed in its first seconds was skipped to \"back\n"
         "## at the van\" while standing beside it: a finished heist, recorded for a\n"
         "## crew that never left. `_route_reached` counts real arrivals only\n"
         "## (roadmap 128); this asks it.\n"
         "static func route_walked(reached: int, total: int) -> bool:\n"
         + T + "return total > 0 and reached >= total\n"
         "\n"
         "\n"
         "## True once this bot's route has ended with every point reached.\n"
         "func walked_whole_route() -> bool:\n"
         + T + "return _completed and route_walked(_route_reached, route_points.size())\n"
         "\n"
         "\n"
         "func _go_to_current_route_point() -> void:\n"),
    ],
    "core/LT_MapEvalHarness.gd": [
        (T * 2 + "bot_controller.route_completed.connect(_on_route_walked)\n",
         T * 2 + "bot_controller.route_completed.connect(_on_route_walked.bind(bot_controller))\n"),
        ("func _on_route_walked() -> void:\n"
         + T + "_route_walked = true\n"
         + T + "if _enemies_cleared:\n"
         + T * 2 + "run_state.end_run(LT_RunState.EndReason.OBJECTIVE)\n",
         "##\n"
         "## A route that ENDED ON A SKIP was not walked (0.25.0, roadmap 206): the\n"
         "## walk is over, so nothing waits on it, but with the guards down the run\n"
         "## ends as ENEMIES_CLEARED -- what happened -- and not as OBJECTIVE.\n"
         "func _on_route_walked(bot: LT_BotPlayerController) -> void:\n"
         + T + "_route_walked = true\n"
         + T + "if _enemies_cleared:\n"
         + T * 2 + "run_state.end_run(LT_RunState.EndReason.OBJECTIVE if bot.walked_whole_route()\n"
         + T * 3 + "else LT_RunState.EndReason.ENEMIES_CLEARED)\n"),
    ],
}


def main():
    v = (LT_ROOT / "VERSION").read_bytes()
    assert v == b"Laser Tag 0.24.0", repr(v)
    assert not TEST.exists(), "already applied"
    for name, edits in EDITS.items():
        p = LT / name
        d = p.read_bytes()
        assert b"\r\n" not in d, name
        t = d.decode("utf-8")
        for old, new in edits:
            n = t.count(old)
            assert n == 1, (name, n, old[:70])
            t = t.replace(old, new)
        p.write_bytes(t.encode("utf-8"))
    TEST.write_bytes((SRC / "test_a_skipped_route_is_not_walked.gd").read_bytes())
    c = (LT_ROOT / "CHANGELOG.md").read_bytes()
    assert b"\r\n" not in c
    text = c.decode("utf-8")
    assert text.startswith(CHANGELOG_HEAD) and text.count(CHANGELOG_HEAD) == 1
    entry = (SRC / "CHANGELOG_0.25.0.md").read_text(encoding="utf-8").replace("\r\n", "\n")
    title = "# Changelog\n\n"
    (LT_ROOT / "CHANGELOG.md").write_bytes((title + entry + text[len(title):]).encode("utf-8"))
    (LT_ROOT / "VERSION").write_bytes(b"Laser Tag 0.25.0")
    print("Laser Tag 0.24.0 -> 0.25.0")


if __name__ == "__main__":
    main()
