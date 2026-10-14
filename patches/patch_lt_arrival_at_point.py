"""Laser Tag 0.32.0: an arrival is at the point, not at the end of a path that stops short of it (factory roadmap 246).

`_advance_route` counted a route point reached at `_nav_finished()`, the end of the path the navigation server
returned -- for a point the network does not reach, the closest point it does. Traced on cold run 9185's
restaurant_row_001 seed_9003 (`docs/findings/lt_arrival/arrival_trace.py`): every crew bot "arrived" at an objective
standing on a navmesh island 61.2 m away, and the route read 1.00 completed.

Anchored edits, each asserted exactly once and the file's sha16 pinned, nothing written until all of them matched:
  addons/laser_tag_tool/scripts/player/LT_BotPlayerController.gd   `path_reaches_point` (static) before
                                                                    `walked_whole_route`; `_advance_route` counts
                                                                    `_route_reached` only where the path's end
                                                                    reaches the point, and says
                                                                    `RoutePointUnreachable` where it does not
  addons/laser_tag_tool/runners/tests/test_an_arrival_is_at_the_point.gd   NEW
CHANGELOG and VERSION from `lt_arrival_at_point/CHANGELOG_0.32.0.md`; `--results-pending` leaves the RESULT_ keys
to `--fill`.

Read before it was written, in this session: `LT_BotPlayerController.gd`'s `_nav_finished`, `_advance_route`'s arrival
block (the cover-seeking return, `_route_index`, `_route_reached`, `RouteProgress`, the end of the route and
`route_walked`), `_route_reached`'s note (real arrivals only), `route_walked`, `walked_whole_route`,
`_align_agent_to_mesh` (`path_desired_distance` from the body; `target_desired_distance` left at Godot's 1.0);
`LT_MetricsCollector.record_event` (an unmatched event is logged with its `position`); the trace's arrivals;
`runners/tests/test_a_skipped_route_is_not_walked.gd`, the model. Every file LF.

    python patches/patch_lt_arrival_at_point.py --results-pending
    (every runners/tests script headless in lasertag; docs/findings/lt_arrival/arrival_breadth.py)
    python patches/patch_lt_arrival_at_point.py --fill
"""
import hashlib
import os
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
LT = pathlib.Path(os.environ.get("LT_ROOT") or HERE.parent / "lasertag")
SRC = HERE / "lt_arrival_at_point"
PENDING = "--results-pending" in sys.argv
FILL = "--fill" in sys.argv
RESULTS = {"RESULT_TESTS": "result_tests.txt", "RESULT_BREADTH": "result_breadth.txt"}
VERSION_WAS, VERSION = b"Laser Tag 0.31.0", b"Laser Tag 0.32.0"
CHANGELOG_TITLE = "# Changelog\n\n"
CHANGELOG_HEAD = CHANGELOG_TITLE + "## [0.31.0] - the guards walk as the crew does: they keep to the mesh and step up"
BOT = "addons/laser_tag_tool/scripts/player/LT_BotPlayerController.gd"
SHA = {BOT: "10a9035a500e7f34"}
NEW = {"addons/laser_tag_tool/runners/tests/test_an_arrival_is_at_the_point.gd": "test_an_arrival_is_at_the_point.gd.txt"}

ARRIVE_OLD = ("\t\t_route_index += 1\n"
              "\t\t_route_reached += 1\n"
              "\t\t# a route point reached restarts the stuck window (0.28.1)\n")
ARRIVE_NEW = ("\t\t# AN ARRIVAL IS AT THE POINT, NOT AT THE END OF A PATH THAT STOPS SHORT\n"
              "\t\t# OF IT (0.32.0, factory roadmap 246). `_nav_finished()` is the end of the\n"
              "\t\t# path the navigation server returned, which for a route point the\n"
              "\t\t# network does not reach is the closest point it does. Counted as an\n"
              "\t\t# arrival, cold run 9185's restaurant_row_001 seed_9003 read route\n"
              "\t\t# completion 1.00 in every run while its objective stood on a navmesh\n"
              "\t\t# island: traced, every crew bot \"arrived\" 61.2 m from it, 2.5 m from\n"
              "\t\t# its spawn. A point whose path stops short is passed as a jammed one is\n"
              "\t\t# (`_update_stuck`): the index moves on, the arrival is not counted, and\n"
              "\t\t# the run's log says where.\n"
              "\t\tvar arrived: bool = true\n"
              "\t\tif use_navigation and nav_agent != null:\n"
              "\t\t\tarrived = path_reaches_point(nav_agent.get_final_position(),\n"
              "\t\t\t\tnav_agent.target_position, nav_agent.target_desired_distance)\n"
              "\t\t_route_index += 1\n"
              "\t\tif arrived:\n"
              "\t\t\t_route_reached += 1\n"
              "\t\telse:\n"
              "\t\t\tvar short_end: Vector3 = nav_agent.get_final_position()\n"
              "\t\t\tget_tree().call_group(LT_Const.GROUP_METRICS, \"record_event\",\n"
              "\t\t\t\t\"RoutePointUnreachable\", {\"source\": body.name, \"index\": _route_index - 1,\n"
              "\t\t\t\t\t\"short_m\": snappedf(short_end.distance_to(nav_agent.target_position), 0.01),\n"
              "\t\t\t\t\t\"position\": [short_end.x, short_end.y, short_end.z]})\n"
              "\t\t# a route point reached restarts the stuck window (0.28.1)\n")

STATIC_OLD = "## True once this bot's route has ended with every point reached.\n"
STATIC_NEW = ("## AN ARRIVAL IS AT THE POINT (0.32.0, factory roadmap 246): the path the\n"
              "## navigation server returned ends within ``tolerance`` of the route point.\n"
              "## `is_navigation_finished()` is true at the end of that path, and for a\n"
              "## point the network does not reach the path ends at the closest point it\n"
              "## does. Godot asks the same of `get_final_position()` and\n"
              "## `target_desired_distance` as `is_target_reachable()`; static here so it\n"
              "## is tested without a scene.\n"
              "static func path_reaches_point(path_end: Vector3, point: Vector3, tolerance: float) -> bool:\n"
              "\treturn path_end.distance_to(point) <= tolerance\n"
              "\n"
              "\n"
              "## True once this bot's route has ended with every point reached.\n")

EDITS = {BOT: [(ARRIVE_OLD, ARRIVE_NEW), (STATIC_OLD, STATIC_NEW)]}


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
        assert value and "RESULT_" not in value, (name, value[-40:])
        results[key] = value
    writes = {}
    for path, rel in [(LT / "CHANGELOG.md", "CHANGELOG.md"), (SRC / "CHANGELOG_0.32.0.md", "the entry")]:
        raw = path.read_bytes()
        eol = _eol(raw, rel)
        text = raw.decode("utf-8").replace("\r\n", "\n")
        for key, value in results.items():
            assert text.count(key) == 1, (rel, key, text.count(key))
            text = text.replace(key, value)
        writes[path] = text.encode("utf-8").replace(b"\n", eol)
    for path, data in writes.items():
        path.write_bytes(data)
    print("Laser Tag 0.32.0: results filled")


def main():
    if FILL:
        return fill()
    assert (LT / "VERSION").read_bytes().strip() == VERSION_WAS, (LT / "VERSION").read_bytes()
    entry = (SRC / "CHANGELOG_0.32.0.md").read_bytes().decode("utf-8").replace("\r\n", "\n")
    assert entry.startswith("## [0.32.0] - "), entry[:40]
    left = entry
    for key in RESULTS if PENDING else ():
        left = left.replace(key, "")
    assert "RESULT_" not in left, "the changelog still carries an unfilled result"
    for rel in NEW:
        assert not (LT / rel).exists(), ("already applied", rel)
    writes = {}
    for rel, edits in EDITS.items():
        raw = (LT / rel).read_bytes()
        got = hashlib.sha256(raw.replace(b"\r\n", b"\n")).hexdigest()[:16]
        assert got == SHA[rel], (rel, "is not the file this patch read", got)
        eol = _eol(raw, rel)
        text = raw.decode("utf-8").replace("\r\n", "\n")
        for old, new in edits:
            assert text.count(old) == 1, (rel, "anchor", text.count(old), old[:60])
            text = text.replace(old, new)
        writes[rel] = (text, eol)
    news = {r: (SRC / s).read_bytes().replace(b"\r\n", b"\n") for r, s in NEW.items()}
    cl = LT / "CHANGELOG.md"
    cl_raw = cl.read_bytes()
    cl_eol = _eol(cl_raw, "CHANGELOG.md")
    cl_text = cl_raw.decode("utf-8").replace("\r\n", "\n")
    assert cl_text.startswith(CHANGELOG_HEAD), cl_text[:120]
    # every anchor matched: now write
    for rel, (body, e) in writes.items():
        (LT / rel).write_bytes(body.encode("utf-8").replace(b"\n", e))
    for r, data in news.items():
        (LT / r).write_bytes(data)
    cl.write_bytes((CHANGELOG_TITLE + entry.rstrip("\n") + "\n\n" + cl_text[len(CHANGELOG_TITLE):])
                   .encode("utf-8").replace(b"\n", cl_eol))
    (LT / "VERSION").write_bytes(VERSION)
    print("Laser Tag 0.31.0 -> 0.32.0")


if __name__ == "__main__":
    main()
