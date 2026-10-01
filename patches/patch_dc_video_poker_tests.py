"""Deli Counter 0.168.0, the tests that name what a club room and a piece may be.

Seven tests failed when the video-poker cabinets were placed, every one a
register of what is allowed, each extended here with the reason:

  * `CLUB_SPECIES` (test_club_rooms, test_preset_strip_club): a club room may
    now carry `video_poker` -- the walker asked for them in strip clubs.
  * `_ZOO_RANGES` (test_furnish): Zoo 1.39.0's `video_poker` genome ranges.
  * the 2.2 m spread between HOSTS (test_club_rooms): a cabinet stands at a
    wall with its own stool, and the reference rows stand side by side; it is
    not a piece a group gathers round, which is what the spread is between.
  * a stool's host (test_club_rooms): a stool is named for its host's
    sequence number, which is unique in its room, and the host is now a
    counter OR a cabinet.
  * the fixture pass moves nothing (test_club_fixtures): the cabinets and
    their own stools are fixtures; the stools named for a cabinet are read
    off the cabinets, not off a prefix every bar stool shares.

Every edit asserts its anchor once and refuses to write on a miss.
"""
from __future__ import annotations

import pathlib

DC = pathlib.Path(__file__).resolve().parents[1] / "deli_counter"


def _edit(rel, pairs):
    p = DC / rel
    raw = p.read_bytes()
    assert b"\r\n" not in raw, f"{rel}: CRLF in an LF file"
    s = raw.decode("utf-8")
    for old, new in pairs:
        n = s.count(old)
        assert n == 1, f"{rel}: anchor found {n} times: {old[:60]!r}"
        s = s.replace(old, new)
    p.write_bytes(s.encode("utf-8"))
    print("patched", rel)


ROOMS = [
    ('''                "back_bar"}
_GEN = re.compile''', '''                "back_bar",
                # the video-poker cabinets (0.168.0, Zoo 1.39.0)
                "video_poker"}
_GEN = re.compile'''),
    ('''                                           # not a second host (0.163.0)
                                           "poster_wall_"))]''',
     '''                                           # not a second host (0.163.0)
                                           "poster_wall_",
                                           # a video-poker cabinet stands at a
                                           # wall with its own stool, and the
                                           # reference rows stand side by side:
                                           # nothing gathers round it (0.168.0)
                                           "video_poker_"))]'''),
    ('''    counters = {v["name"].rsplit("_", 1)[1]: v for v in s["volumes"]
                if v["name"].startswith("counter_club_")}
    stools = [v for v in s["volumes"] if v["name"].startswith("bar_stool_")]
    assert stools and len(counters) == 2            # 300 m2: the second bar
    for v in stools:
        host = counters[v["name"].split("_")[3]]''',
     '''    counters = {v["name"].rsplit("_", 1)[1]: v for v in s["volumes"]
                if v["name"].startswith("counter_club_")}
    # a stool is named for its host's sequence number, unique in the room;
    # since 0.168.0 the host is a counter or a video-poker cabinet
    cabinets = {v["name"].rsplit("_", 1)[1]: v for v in s["volumes"]
                if v["name"].startswith("video_poker_")}
    stools = [v for v in s["volumes"] if v["name"].startswith("bar_stool_")]
    assert stools and len(counters) == 2            # 300 m2: the second bar
    for v in stools:
        seq = v["name"].split("_")[3]
        host = counters.get(seq) or cabinets[seq]'''),
]

PRESET = [('''                # 0.137.0: the lit wall unit behind every bar counter, and
                # the plain counter that returns the bar to the wall
                "back_bar"}''', '''                # 0.137.0: the lit wall unit behind every bar counter, and
                # the plain counter that returns the bar to the wall
                "back_bar",
                # the video-poker cabinets (0.168.0, Zoo 1.39.0)
                "video_poker"}''')]

FURNISH = [('''    "atm": ((0.5, 0.75), (0.4, 0.7), (1.2, 1.65)),''',
            '''    "atm": ((0.5, 0.75), (0.4, 0.7), (1.2, 1.65)),
    # Zoo 1.39.0's genome (0.168.0)
    "video_poker": ((0.55, 0.8), (0.5, 0.8), (1.55, 1.95)),''')]

FIXTURES = [('''    fixtures = [v for v in s["volumes"]
                if v["name"].startswith(("dartboard_", "cigarettes_", "poster_wall_"))]
    assert fixtures''', '''    fixtures = [v for v in s["volumes"]
                if v["name"].startswith(("dartboard_", "cigarettes_", "poster_wall_",
                                         "video_poker_"))]
    # ...and a cabinet's own stool (0.168.0), named for the cabinet: read off
    # the cabinets, not off the `bar_stool_` prefix every bar stool shares
    own = {"bar_stool_" + v["name"].split("_", 3)[3] + "_1" for v in fixtures
           if v["name"].startswith("video_poker_bar_")}
    fixtures += [v for v in s["volumes"] if v["name"] in own]
    assert fixtures''')]


def main():
    _edit("test_club_rooms.py", ROOMS)
    _edit("test_preset_strip_club.py", PRESET)
    _edit("test_furnish.py", FURNISH)
    _edit("test_club_fixtures.py", FIXTURES)


if __name__ == "__main__":
    main()
