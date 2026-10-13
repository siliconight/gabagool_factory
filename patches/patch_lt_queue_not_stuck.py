"""Laser Tag 0.30.0: a guard held by another bot is blocked, not stuck (factory roadmap 242; traced in the factory's
`docs/findings/stoop_breadth/`).

Anchored edits, each asserted exactly once and every file's sha16 pinned, nothing written until all of them
matched:
  addons/laser_tag_tool/scripts/enemy/LT_EnemyMovement.gd      `blocked_detected`; `_update_stuck` asks
                                                                `_held_by_a_body` as a window closes held
  addons/laser_tag_tool/scripts/enemy/LT_EnemyBrain.gd         `_on_blocked`; `_on_stuck` and it share
                                                                `_held`, the event's name the only difference
  addons/laser_tag_tool/scripts/metrics/LT_MetricsCollector.gd `enemy_blocked_events`, counted and summed
  addons/laser_tag_tool/runners/tests/test_a_queue_is_not_stuck.gd   NEW
CHANGELOG and VERSION from `lt_queue_not_stuck/CHANGELOG_0.30.0.md`; `--results-pending` leaves the RESULT_
keys to `--fill`.

Read before it was written, in this session: `LT_EnemyMovement.gd` whole (the window, `_physics_process`'s
`move_and_slide` then `_update_stuck`), `LT_EnemyBrain.gd`'s `_ready` and `_physics_process` (SEEK re-sets the
destination every frame) and `_on_stuck` (state, record, jitter), `LT_MetricsCollector.gd`'s run fields,
`record_event` and summary, `LT_ScoreCalculator._score_pathing` (reads `enemy_stuck_events` and the per-enemy
rate only), `LT_Const` (`GROUP_ENEMY`, `GROUP_PLAYER`), and 0.28.0's `test_a_fight_is_not_stuck.gd` and its
entry. Every file LF.

    python patches/patch_lt_queue_not_stuck.py --results-pending
    (every runners/tests script headless in lasertag; the breadth)
    python patches/patch_lt_queue_not_stuck.py --fill
"""
import hashlib
import os
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
LT = pathlib.Path(os.environ.get("LT_ROOT") or HERE.parent / "lasertag")
SRC = HERE / "lt_queue_not_stuck"
PENDING = "--results-pending" in sys.argv
FILL = "--fill" in sys.argv
RESULTS = {"RESULT_TESTS": "result_tests.txt", "RESULT_BREADTH": "result_breadth.txt"}
VERSION_WAS, VERSION = b"Laser Tag 0.29.0", b"Laser Tag 0.30.0"
#: the changelog keeps a title above its entries; the new entry goes under it
CHANGELOG_TITLE = "# Changelog\n\n"
CHANGELOG_HEAD = CHANGELOG_TITLE + "## [0.29.0] - the bot keeps to the mesh it plans on"
MOVE = "addons/laser_tag_tool/scripts/enemy/LT_EnemyMovement.gd"
BRAIN = "addons/laser_tag_tool/scripts/enemy/LT_EnemyBrain.gd"
METRICS = "addons/laser_tag_tool/scripts/metrics/LT_MetricsCollector.gd"
SHA = {MOVE: "05f260fb1437135d", BRAIN: "0670ba8fd9ccb8d3", METRICS: "d03de47626dac35e"}
NEW = {"addons/laser_tag_tool/runners/tests/test_a_queue_is_not_stuck.gd": "test_a_queue_is_not_stuck.gd.txt"}

EDITS = {
    MOVE: [
        ("signal stuck_detected(position: Vector3)\n",
         "signal stuck_detected(position: Vector3)\n"
         "## Held by another bot's body and by nothing of the level (0.30.0, factory roadmap 242). Every guard\n"
         "## in SEEK paths to the same crew member through the same corners and none steers round another,\n"
         "## so a guard behind a guard stood still and was `stuck_detected` -- 73 of 75 such events traced on\n"
         "## the factory's lots -- and NPC Pathing charged the map for the bots' own crowding.\n"
         "signal blocked_detected(position: Vector3)\n"),
        ("\t\tif moved < stuck_distance_threshold and not _stuck_reported:\n"
         "\t\t\t_stuck_reported = true\n"
         "\t\t\tstuck_detected.emit(body.global_position)\n",
         "\t\tif moved < stuck_distance_threshold and not _stuck_reported:\n"
         "\t\t\t_stuck_reported = true\n"
         "\t\t\tif _held_by_a_body():\n"
         "\t\t\t\tblocked_detected.emit(body.global_position)\n"
         "\t\t\telse:\n"
         "\t\t\t\tstuck_detected.emit(body.global_position)\n"),
        ("\t\t_stuck_anchor = body.global_position\n"
         "\t\tif moved >= stuck_distance_threshold:\n"
         "\t\t\t_stuck_reported = false\n",
         "\t\t_stuck_anchor = body.global_position\n"
         "\t\tif moved >= stuck_distance_threshold:\n"
         "\t\t\t_stuck_reported = false\n"
         "\n"
         "## Whether this frame's move was held by another bot's body and by nothing of the level (0.30.0).\n"
         "## `_update_stuck` runs right after `move_and_slide`, so these are the closing frame's contacts. A\n"
         "## contact under the feet is the floor, not a hold; any other contact that is not a body -- a wall,\n"
         "## a prop -- is the level's, and the guard is stuck as before.\n"
         "func _held_by_a_body() -> bool:\n"
         "\tvar by_body := false\n"
         "\tfor i in range(body.get_slide_collision_count()):\n"
         "\t\tvar c: KinematicCollision3D = body.get_slide_collision(i)\n"
         "\t\tif c.get_normal().angle_to(Vector3.UP) <= body.floor_max_angle:\n"
         "\t\t\tcontinue\n"
         "\t\tif c.get_collider() is CharacterBody3D:\n"
         "\t\t\tby_body = true\n"
         "\t\telse:\n"
         "\t\t\treturn false\n"
         "\treturn by_body\n"),
    ],
    BRAIN: [
        ("\tif movement != null:\n"
         "\t\tmovement.stuck_detected.connect(_on_stuck)\n",
         "\tif movement != null:\n"
         "\t\tmovement.stuck_detected.connect(_on_stuck)\n"
         "\t\tmovement.blocked_detected.connect(_on_blocked)\n"),
        ("func _on_stuck(position: Vector3) -> void:\n"
         "\tstuck_count += 1\n"
         "\tstate = State.STUCK\n"
         "\tget_tree().call_group(LT_Const.GROUP_METRICS, \"record_event\", \"EnemyStuck\", {\n",
         "func _on_stuck(position: Vector3) -> void:\n"
         "\t_held(position, \"EnemyStuck\")\n"
         "\n"
         "## Held by another bot's body, not by the level (0.30.0, factory roadmap 242). Handled as a stuck\n"
         "## guard is -- the same state, the same jitter, the same random draws, so every fight plays as it\n"
         "## did -- and recorded as `EnemyBlocked`, which NPC Pathing does not charge to the map.\n"
         "func _on_blocked(position: Vector3) -> void:\n"
         "\t_held(position, \"EnemyBlocked\")\n"
         "\n"
         "func _held(position: Vector3, event_name: String) -> void:\n"
         "\tstuck_count += 1\n"
         "\tstate = State.STUCK\n"
         "\tget_tree().call_group(LT_Const.GROUP_METRICS, \"record_event\", event_name, {\n"),
    ],
    METRICS: [
        ("\t\t\"player_stuck_events\": 0,\n"
         "\t\t\"enemy_stuck_events\": 0,\n"
         "\t\t\"time_to_first_contact\": -1.0,\n",
         "\t\t\"player_stuck_events\": 0,\n"
         "\t\t\"enemy_stuck_events\": 0,\n"
         "\t\t# a guard held by another bot's body (0.30.0): reported, not scored\n"
         "\t\t\"enemy_blocked_events\": 0,\n"
         "\t\t\"time_to_first_contact\": -1.0,\n"),
        ("\t\t\"EnemyStuck\":\n"
         "\t\t\tcurrent[\"enemy_stuck_events\"] += 1\n",
         "\t\t\"EnemyStuck\":\n"
         "\t\t\tcurrent[\"enemy_stuck_events\"] += 1\n"
         "\t\t\"EnemyBlocked\":\n"
         "\t\t\tcurrent[\"enemy_blocked_events\"] += 1\n"),
        ("\t\t\"enemy_stuck_events\": _sum(runs, \"enemy_stuck_events\"),\n",
         "\t\t\"enemy_stuck_events\": _sum(runs, \"enemy_stuck_events\"),\n"
         "\t\t# a guard held by another bot's body (0.30.0): reported, never scored\n"
         "\t\t\"enemy_blocked_events\": _sum(runs, \"enemy_blocked_events\"),\n"),
    ],
}


def _eol(raw, rel):
    crlf = raw.count(b"\r\n")
    lf = raw.count(b"\n")
    assert crlf in (0, lf), (rel, "mixed line endings", crlf, lf)
    return b"\r\n" if crlf else b"\n"


def fill():
    assert (LT / "VERSION").read_bytes().strip() == VERSION, (LT / "VERSION").read_bytes()
    results = {}
    for key, name in RESULTS.items():
        value = (SRC / name).read_text(encoding="utf-8").strip()
        assert value and "RESULT_" not in value and not value.endswith("."), (name, value[-40:])
        results[key] = value
    writes = {}
    for path, rel in [(LT / "CHANGELOG.md", "CHANGELOG.md"), (SRC / "CHANGELOG_0.30.0.md", "the entry")]:
        raw = path.read_bytes()
        eol = _eol(raw, rel)
        text = raw.decode("utf-8").replace("\r\n", "\n")
        for key, value in results.items():
            assert text.count(key) == 1, (rel, key, text.count(key))
            text = text.replace(key, value)
        writes[path] = text.encode("utf-8").replace(b"\n", eol)
    for path, data in writes.items():
        path.write_bytes(data)
    print("Laser Tag 0.30.0: results filled")


def main():
    if FILL:
        return fill()
    assert (LT / "VERSION").read_bytes().strip() == VERSION_WAS, (LT / "VERSION").read_bytes()
    entry = (SRC / "CHANGELOG_0.30.0.md").read_bytes().decode("utf-8").replace("\r\n", "\n")
    assert entry.startswith("## [0.30.0] - "), entry[:40]
    left = entry
    for key in RESULTS if PENDING else ():
        left = left.replace(key, "")
    assert "RESULT_" not in left, "the changelog still carries an unfilled result"
    for rel in NEW:
        assert not (LT / rel).exists(), ("already applied", rel)
    writes = {}
    for rel, pairs in EDITS.items():
        p = LT / rel
        raw = p.read_bytes()
        got = hashlib.sha256(raw.replace(b"\r\n", b"\n")).hexdigest()[:16]
        assert got == SHA[rel], (rel, "is not the file this patch read", got)
        eol = _eol(raw, rel)
        text = raw.decode("utf-8").replace("\r\n", "\n")
        for old, new in pairs:
            assert text.count(old) == 1, (rel, "anchor", text.count(old), old[:80])
            text = text.replace(old, new)
        writes[p] = text.encode("utf-8").replace(b"\n", eol)
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
    print("Laser Tag 0.29.0 -> 0.30.0")


if __name__ == "__main__":
    main()
