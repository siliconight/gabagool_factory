"""Laser Tag 0.28.0: a bot standing to fight is not stuck (factory roadmap 242; `docs/findings/route_snag/`,
"the stuck detector counts fights").

Anchored edits, each asserted once, nothing written until all of them matched:
  addons/laser_tag_tool/scripts/player/LT_BotPlayerController.gd
      `_physics_process` passes `enemy != null and not advance_while_engaging` to `_update_stuck`;
      `_update_stuck` restarts its window on a frame the bot stands to fight
  addons/laser_tag_tool/runners/tests/test_a_fight_is_not_stuck.gd   NEW
CHANGELOG and VERSION from `lt_fight_not_stuck/CHANGELOG_0.28.0.md`; `--results-pending` leaves the
RESULT_ keys to `--fill`. (The held keep-on-mesh draft, `patch_lt_keep_on_mesh.py`, also called itself
0.28.0; it is renumbered when it is revived.)

Read before it was written: `_physics_process` (`enemy` is the function's, so it is in scope at the
`_update_stuck` call; the stand-and-fight branch calls `_stop_horizontal`), `_update_stuck` (the window,
the anchor, the instant's enemy question, the route point it skips), `_score_traversal` (10 points for
any player-stuck event), `start_route`, `_set_destination` and `_nav_finished` with `use_navigation` off
(the test's bot), and `test_stuck_is_per_body.gd` (the tests' shape). Laser Tag's `project.godot` is not
tracked, so a draft copy needs the repository's own beside it.

    python patches/patch_lt_fight_not_stuck.py --results-pending
    for t in lasertag/addons/laser_tag_tool/runners/tests/*.gd; do godot --headless --path lasertag -s res://${t#lasertag/}; done
    python patches/patch_lt_fight_not_stuck.py --fill
    LT_ROOT=<copy> python patches/patch_lt_fight_not_stuck.py --draft
"""
import hashlib
import os
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
LT = pathlib.Path(os.environ.get("LT_ROOT") or HERE.parent / "lasertag")
SRC = HERE / "lt_fight_not_stuck"
DRAFT = "--draft" in sys.argv
PENDING = "--results-pending" in sys.argv
FILL = "--fill" in sys.argv
RESULTS = {"RESULT_TEST": "result_test.txt", "RESULT_SUITE": "result_suite.txt",
           "RESULT_MEASURED": "result_measured.txt"}
VERSION_WAS, VERSION = b"Laser Tag 0.27.0", b"Laser Tag 0.28.0"
CHANGELOG_HEAD = ("# Changelog\n\n## [0.27.0] - the navigation map updates on the evaluation's thread, so "
                  "the clock need not wait\n")
BOT = "addons/laser_tag_tool/scripts/player/LT_BotPlayerController.gd"
TEST = "addons/laser_tag_tool/runners/tests/test_a_fight_is_not_stuck.gd"
SHA = {BOT: "ce35a0c24574ddc8"}

CALL_OLD = "\t_try_step_up(intended)\n\t_update_stuck(delta)\n"
CALL_NEW = ("\t_try_step_up(intended)\n"
            "\t# a stand to fight restarts the stuck window (0.28.0): see `_update_stuck`\n"
            "\t_update_stuck(delta, enemy != null and not advance_while_engaging)\n")

FUNC_OLD = ("func _update_stuck(delta: float) -> void:\n"
            "\tif _completed or _dead or route_points.is_empty():\n"
            "\t\treturn\n"
            "\t_stuck_timer += delta\n")
FUNC_NEW = ("## A STAND TO FIGHT RESTARTS THE STUCK WINDOW (0.28.0, factory roadmap 242).\n"
            "## The window asked about an enemy only as it closed, so a bot that stood to\n"
            "## fight all window (`advance_while_engaging` off: it stops) and lost sight of\n"
            "## its enemy at that instant read as stuck -- 10 traversal points and a\n"
            "## skipped route point. Measured in the factory (`docs/findings/route_snag/`):\n"
            "## 18 of the 21 stuck events a draft added on five lots were such windows, an\n"
            "## enemy in sight in 59 or 60 of their 60 frames. So a frame the bot stands to\n"
            "## fight restarts the window: stuck means four seconds with no stand to fight\n"
            "## in which the body moved less than `stuck_distance_threshold`. A bot\n"
            "## advancing while engaging is trying to move; its window runs on as before.\n"
            "## (`LT_EnemyMovement._update_stuck` restarts a guard's window whenever it is\n"
            "## not trying to move; here only a stand to fight does, so a bot hung on a\n"
            "## path point under its own feet is still counted.)\n"
            "func _update_stuck(delta: float, standing_to_fight: bool = false) -> void:\n"
            "\tif _completed or _dead or route_points.is_empty():\n"
            "\t\treturn\n"
            "\tif standing_to_fight:\n"
            "\t\t_stuck_timer = 0.0\n"
            "\t\t_stuck_anchor = body.global_position\n"
            "\t\treturn\n"
            "\t_stuck_timer += delta\n")


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


def main():
    if FILL:
        return fill()
    if DRAFT and not os.environ.get("LT_ROOT"):
        sys.exit("refusing: --draft is for an LT_ROOT copy, never the repo")
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
    text = _once(text, CALL_OLD, CALL_NEW, "the call in _physics_process")
    text = _once(text, FUNC_OLD, FUNC_NEW, "_update_stuck")
    test = _src("test_a_fight_is_not_stuck.gd.txt")
    cl = LT / "CHANGELOG.md"
    cl_raw = cl.read_bytes()
    cl_eol = _eol(cl_raw, "CHANGELOG.md")
    cl_text = cl_raw.decode("utf-8").replace("\r\n", "\n")
    assert cl_text.startswith(CHANGELOG_HEAD), cl_text[:200]
    cl_new = "# Changelog\n\n" + entry.rstrip("\n") + "\n\n" + cl_text[len("# Changelog\n\n"):]
    # every anchor matched: now write
    p.write_bytes(text.encode("utf-8").replace(b"\n", eol))
    (LT / TEST).write_bytes(test.encode("utf-8"))
    cl.write_bytes(cl_new.encode("utf-8").replace(b"\n", cl_eol))
    (LT / "VERSION").write_bytes(VERSION + b"\n" if (LT / "VERSION").read_bytes().endswith(b"\n") else VERSION)
    print("Laser Tag 0.27.0 -> 0.28.0" + (" (DRAFT)" if DRAFT else ""))


if __name__ == "__main__":
    main()
