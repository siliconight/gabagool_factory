"""Laser Tag 0.28.1: a bot that reaches where it was going is not stuck (factory roadmap 242;
`docs/findings/route_snag/`, the stuck detector's second false positive).

Anchored edits, each asserted once, nothing written until all of them matched:
  addons/laser_tag_tool/scripts/player/LT_BotPlayerController.gd
      `_restart_stuck_window` before `_stop_horizontal`; `_update_stuck`'s stand-to-fight restart calls
      it; `_advance_route` calls it on a cover point reached and on a route point reached
  addons/laser_tag_tool/runners/tests/test_an_arrival_is_not_stuck.gd   NEW
CHANGELOG and VERSION from `lt_arrival_not_stuck/CHANGELOG_0.28.1.md`; `--results-pending` leaves the
RESULT_ keys to `--fill`. (The held keep-on-mesh draft, `patch_lt_keep_on_mesh.py`, pins 0.28.0's
file; it is rebased onto this one when it is revived.)

Read before it was written: `_advance_route` (the cover arrival returns before the route arrival;
`_route_reached` counts real arrivals only), `_update_stuck` as 0.28.0 left it, `_nav_finished` without
navigation (1.2 m), and `test_a_fight_is_not_stuck.gd` (the shape, and that it reaches no route point,
so it reads the same on both).

    python patches/patch_lt_arrival_not_stuck.py --results-pending
    for t in lasertag/addons/laser_tag_tool/runners/tests/*.gd; do godot --headless --path lasertag -s res://${t#lasertag/}; done
    python patches/patch_lt_arrival_not_stuck.py --fill
    LT_ROOT=<copy> python patches/patch_lt_arrival_not_stuck.py --draft
"""
import hashlib
import os
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
LT = pathlib.Path(os.environ.get("LT_ROOT") or HERE.parent / "lasertag")
SRC = HERE / "lt_arrival_not_stuck"
DRAFT = "--draft" in sys.argv
PENDING = "--results-pending" in sys.argv
FILL = "--fill" in sys.argv
RESULTS = {"RESULT_TEST": "result_test.txt", "RESULT_SUITE": "result_suite.txt",
           "RESULT_MEASURED": "result_measured.txt"}
VERSION_WAS, VERSION = b"Laser Tag 0.28.0", b"Laser Tag 0.28.1"
CHANGELOG_HEAD = "# Changelog\n\n## [0.28.0] - a bot standing to fight is not stuck\n"
BOT = "addons/laser_tag_tool/scripts/player/LT_BotPlayerController.gd"
TEST = "addons/laser_tag_tool/runners/tests/test_an_arrival_is_not_stuck.gd"
SHA = {BOT: "c3b0e61df6063849"}

COVER_OLD = ("\t\tif _seeking_cover:\n"
             "\t\t\t_seeking_cover = false\n"
             "\t\t\t_go_to_current_route_point()\n"
             "\t\t\treturn\n")
COVER_NEW = ("\t\tif _seeking_cover:\n"
             "\t\t\t_seeking_cover = false\n"
             "\t\t\t# a cover point reached restarts the stuck window (0.28.1)\n"
             "\t\t\t_restart_stuck_window()\n"
             "\t\t\t_go_to_current_route_point()\n"
             "\t\t\treturn\n")
ARRIVE_OLD = "\t\t_route_index += 1\n\t\t_route_reached += 1\n"
ARRIVE_NEW = ("\t\t_route_index += 1\n\t\t_route_reached += 1\n"
              "\t\t# a route point reached restarts the stuck window (0.28.1)\n"
              "\t\t_restart_stuck_window()\n")
FIGHT_OLD = ("\tif standing_to_fight:\n"
             "\t\t_stuck_timer = 0.0\n"
             "\t\t_stuck_anchor = body.global_position\n"
             "\t\treturn\n")
FIGHT_NEW = ("\tif standing_to_fight:\n"
             "\t\t_restart_stuck_window()\n"
             "\t\treturn\n")
HELPER_OLD = "func _stop_horizontal() -> void:\n"
HELPER_NEW = ("## RESTART THE STUCK WINDOW where the body stands: on a stand to fight\n"
              "## (0.28.0) and on reaching a destination, a route point or a cover point\n"
              "## (0.28.1, factory roadmap 242). The window measures NET displacement, so a\n"
              "## body that walked out to a route point and back inside one window -- an\n"
              "## objective down a short corridor -- ended near where the window began and\n"
              "## read as stuck. Measured in the factory (`docs/findings/route_snag/`): every\n"
              "## stuck event 0.28.0 added over its sixteen lots was such a round trip, the\n"
              "## route point reached halfway through the window. An arrival is progress; a\n"
              "## jam after it still counts, a window later.\n"
              "func _restart_stuck_window() -> void:\n"
              "\t_stuck_timer = 0.0\n"
              "\t_stuck_anchor = body.global_position\n"
              "\n" + HELPER_OLD)


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
    for path, rel in [(LT / "CHANGELOG.md", "CHANGELOG.md"), (SRC / "CHANGELOG_0.28.1.md", "the entry")]:
        raw = path.read_bytes()
        eol = _eol(raw, rel)
        text = raw.decode("utf-8").replace("\r\n", "\n")
        for key, value in results.items():
            assert text.count(key) == 1, (rel, key, text.count(key))
            text = text.replace(key, value)
        writes[path] = text.encode("utf-8").replace(b"\n", eol)
    for path, data in writes.items():
        path.write_bytes(data)
    print("Laser Tag 0.28.1: results filled")


def main():
    if FILL:
        return fill()
    if DRAFT and not os.environ.get("LT_ROOT"):
        sys.exit("refusing: --draft is for an LT_ROOT copy, never the repo")
    assert (LT / "VERSION").read_bytes().strip() == VERSION_WAS, (LT / "VERSION").read_bytes()
    entry = _src("CHANGELOG_0.28.1.md")
    assert entry.startswith("## [0.28.1] - "), entry[:40]
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
    text = _once(text, COVER_OLD, COVER_NEW, "the cover arrival")
    text = _once(text, ARRIVE_OLD, ARRIVE_NEW, "the route arrival")
    text = _once(text, FIGHT_OLD, FIGHT_NEW, "0.28.0's restart")
    text = _once(text, HELPER_OLD, HELPER_NEW, "the helper's place")
    test = _src("test_an_arrival_is_not_stuck.gd.txt")
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
    (LT / "VERSION").write_bytes(VERSION)
    print("Laser Tag 0.28.0 -> 0.28.1" + (" (DRAFT)" if DRAFT else ""))


if __name__ == "__main__":
    main()
