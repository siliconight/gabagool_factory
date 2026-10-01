"""Deli Counter 0.168.0: video-poker cabinets, with a stool, in stores, bars and clubs.

The walker, 2026-09-30: "'PA Skill Games' ... into the level. We would see
them in convenient stores, bars, and strip clubs. High stool to play" -- the
1997 period version agreed; Zoo 1.39.0 draws the `video_poker` cabinet.

  * `prop_species`: `video_poker` routes to the species, IMMEDIATELY AHEAD of
    the counter row, whose `bar_` would claim `video_poker_bar_*` first.
  * Two fixture pieces of the one species, because a fixture's `rooms` gate
    is one token set for every recipe that lists it and the store's and the
    bar's are different: `video_poker_store` (the ATM's selling rooms, at
    most 2) on `shop_floor`; `video_poker_bar` (a tavern's bar rooms and the
    strip club's, 2, and 3 past 80 m2) on `club` and `strip_club`. 0.65 x
    0.65 x 1.75, standing, collision, four brand variants.
  * `_place_fixture` honours a piece's `seats` (until now only the
    furnishing pass did): a cabinet takes one `bar_stool` in front of its
    face, through the same `_seed_clear` and nested-room test as the cabinet,
    turned to face it -- and a spot whose stool does not fit is not a spot.

Every edit asserts its anchor once and refuses to write on a miss.
"""
from __future__ import annotations

import pathlib

DC = pathlib.Path(__file__).resolve().parents[1] / "deli_counter"


def _edit(rel, pairs):
    p = DC / rel
    raw = p.read_bytes().replace(b"\r\n", b"\n")
    s = raw.decode("utf-8")
    for old, new in pairs:
        n = s.count(old)
        assert n == 1, f"{rel}: anchor found {n} times: {old[:60]!r}"
        s = s.replace(old, new)
    p.write_bytes(s.encode("utf-8"))
    print("patched", rel)


SPECIES_OLD = '''    (("counter", "reception", "station", "island", "cage", "bar_",
      "workbench", "tool_bench"), "counter"),'''
SPECIES_NEW = '''    # THE VIDEO-POKER CABINET (Zoo 1.39.0; placed 0.168.0). Above the
    # counter row, whose `bar_` would claim every `video_poker_bar_*`.
    (("video_poker",), "video_poker"),
''' + SPECIES_OLD

PIECE_OLD = '''    _piece("payphone", ((0.75, 0.5, 2.3),), "wall", front=True, most=1),'''
PIECE_NEW = '''    # THE VIDEO-POKER CABINET (0.168.0). The walker, 2026-09-30: "PA Skill
    # Games ... in convenient stores, bars, and strip clubs. High stool to
    # play", the 1997 version -- Zoo 1.39.0's `video_poker`, a "for
    # amusement only" upright with a CRT, four invented brands by variant.
    # TWO PIECES, ONE SPECIES: a fixture's `rooms` gate is one token set for
    # every recipe that lists it, and `floor` -- which a strip club's main
    # floor needs -- would put a store's machines on every warehouse floor.
    # Each brings ONE stool in front of its face (`seats`, which
    # `_place_fixture` honours since this release). Standing, collision.
    _piece("video_poker_store", ((0.65, 0.65, 1.75),), "wall", front=True, most=2,
           variants=4, seats=("stool", 1, 1),
           rooms=("sales", "retail", "shop", "customer", "market", "showroom", "stall")),
    _piece("video_poker_bar", ((0.65, 0.65, 1.75),), "wall", front=True, most=2,
           most_big=(80.0, 3), variants=4, seats=("stool", 1, 1),
           rooms=("bar", "taproom", "tavern", "pub", "social", "club", "lounge", "vip",
                  "cabaret", "stage", "dance", "main", "floor")),
''' + PIECE_OLD

RECIPE_CLUB_OLD = '''             "clusters": (), "fixtures": ("cigarettes", "poster_wall_bar")},'''
RECIPE_CLUB_NEW = '''             "clusters": (), "fixtures": ("cigarettes", "poster_wall_bar",
                                          "video_poker_bar")},'''
RECIPE_STRIP_OLD = '''                   "fixtures": ("dartboard", "cigarettes", "poster_wall_club")},'''
RECIPE_STRIP_NEW = '''                   "fixtures": ("dartboard", "cigarettes", "poster_wall_club",
                                "video_poker_bar")},'''
RECIPE_SHOP_OLD = '''                   "fixtures": ("atm_store", "poster_wall_store")},'''
RECIPE_SHOP_NEW = '''                   "fixtures": ("atm_store", "video_poker_store", "poster_wall_store")},'''

PLACE_OLD = '''        vol = _make_volume(spec, key, f"{key}_{rtag}_{seq}", qx, qy, sx, sy, h, rot,
                           story, sh, building)
        if p["distinct"] and not _distinct_variant(spec, key, rtag, vol, variant_count(p)):
            continue
        spec.setdefault("volumes", []).append(vol)
        return vol
    return None'''
PLACE_NEW = '''        # A FIXTURE'S SEAT (0.168.0): a piece with `seats` brings them, one
        # stool in front of a video-poker cabinet's face -- through the same
        # room edge, nested-room and `_seed_clear` tests as the cabinet, so
        # a spot whose stool does not fit is not a spot. The furnishing pass
        # has always seated its hosts (`_seats`); this pass never had.
        seat = None
        if p["seats"] and front is not None:
            how, _lo, _hi = p["seats"]
            seat_key = _SEAT_PIECES.get(how)
            if seat_key:
                s_w, s_d, s_h = _PIECES[seat_key]["sizes"][0]
                f = math.radians(front)
                ux, uy = round(math.sin(f)), round(math.cos(f))
                depth = sy if uy else sx
                out = depth / 2.0 + s_d / 2.0 + _FIXTURE_SEAT_GAP
                cx, cy = qx + ux * out, qy + uy * out
                s_half = max(s_w, s_d) / 2.0
                rx0, ry0, rx1, ry1 = room["bounds"]
                edge = 0.15 + s_half
                if not (rx0 + edge < cx < rx1 - edge and ry0 + edge < cy < ry1 - edge):
                    continue
                if _over_rects(inner, cx, cy, s_half, s_half):
                    continue
                if not _seed_clear(spec, room, cx, cy, [], half=s_half):
                    continue
                if _over_rects(lanes, cx, cy, s_half, s_half):
                    continue
                # facing the cabinet: a seat's front is its local -Y and a
                # slot turns +Y onto its bearing, so the host's own front
                # bearing points the seat back at the host (`_seats`)
                s_rot = float(int(round(front / 90.0)) * 90 % 360)
                seat = _make_volume(spec, seat_key, f"{seat_key}_{rtag}_{seq}_1", cx, cy,
                                    s_w, s_d, s_h, s_rot, story, sh, building)
        vol = _make_volume(spec, key, f"{key}_{rtag}_{seq}", qx, qy, sx, sy, h, rot,
                           story, sh, building)
        if p["distinct"] and not _distinct_variant(spec, key, rtag, vol, variant_count(p)):
            continue
        spec.setdefault("volumes", []).append(vol)
        if seat is not None:
            spec["volumes"].append(seat)
        return vol
    return None'''

GAP_OLD = '''_FIXTURE_ROUNDS = 6
'''
GAP_NEW = '''_FIXTURE_ROUNDS = 6
#: A fixture's stool stands this far off its host's face: knees under the
#: button deck's lip, a hand's width of floor between (0.168.0).
_FIXTURE_SEAT_GAP = 0.12
'''

TEST = '''"""Video-poker cabinets with a stool, in stores, bars and clubs (0.168.0).

The walker, 2026-09-30: "PA Skill Games ... in convenient stores, bars, and
strip clubs. High stool to play" -- Zoo 1.39.0's `video_poker`. Held, on the
library as the specs carry it: cabinets stand only in selling rooms, bar
rooms and strip-club rooms, at most the pieces allow; each routes to the
species, stands on its floor against a wall with collision and a variant;
each has ONE stool in front of its face, facing it, clear of the cabinet;
and the fixture pass stays idempotent.
"""
import collections
import glob
import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import level_design  # noqa: E402
import prop_species  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))


def _library():
    for p in sorted(glob.glob(os.path.join(HERE, "specs", "*.json"))):
        if os.path.basename(p).startswith("lf_"):
            continue
        with open(p, encoding="utf-8") as f:
            d = json.load(f)
        if d.get("rooms"):
            yield d


def _cabinets(d):
    return [v for v in d.get("volumes") or [] if str(v.get("name", "")).startswith("video_poker_")]


def test_the_names_route_to_the_species_and_the_stool_to_the_stool():
    for n in ("video_poker_store_r0a1b2c3d_4", "video_poker_bar_r0a1b2c3d_2"):
        assert prop_species.species_for_name(n) == "video_poker", n
    assert prop_species.species_for_name("bar_stool_r0a1b2c3d_2_1") == "bar_stool"


def test_cabinets_stand_where_they_belong_at_most_the_pieces_allow():
    per_room = collections.Counter()
    total = 0
    for d in _library():
        building = level_design.club_building_id(d)
        rooms = {level_design._room_tag(r): r for r in d["rooms"]}
        for v in _cabinets(d):
            total += 1
            tag = next(t for t in rooms if f"_{t}_" in v["name"])
            room = rooms[tag]
            key = v["name"].rsplit("_" + tag, 1)[0]
            kind = level_design._room_kind(room, building)
            assert key in level_design._RECIPES[kind].get("fixtures", ()), (d["name"], v["name"], kind)
            toks = set(str(room["id"]).lower().replace("-", "_").split("_"))
            assert toks & level_design._PIECES[key]["rooms"], (d["name"], room["id"])
            per_room[(d["name"], tag, key)] += 1
    assert total >= 30, total
    for (name, tag, key), n in per_room.items():
        assert n <= max(level_design._PIECES[key]["most"] or 1,
                        (level_design._PIECES[key]["most_big"] or (0, 0))[1]), (name, tag, key, n)


def test_each_cabinet_stands_against_a_wall_with_one_stool_facing_it():
    seen = 0
    for d in _library():
        sh = level_design._story_height(d)
        vols = {v["name"]: v for v in d.get("volumes") or []}
        for v in _cabinets(d):
            seen += 1
            assert prop_species.species_for_name(v["name"]) == "video_poker"
            assert v["collision"] == "convex"
            assert 0 <= int(v.get("variant", 0) or 0) < 4
            # the stool is named for its cabinet: `bar_stool_<roomtag>_<seq>_1`
            key = next(k for k in ("video_poker_store", "video_poker_bar")
                       if v["name"].startswith(k + "_"))
            stools = [vols[n] for n in ("bar_stool_" + v["name"][len(key) + 1:] + "_1",) if n in vols]
            assert len(stools) == 1, (d["name"], v["name"])
            s = stools[0]
            # in front of the face, off the cabinet, facing it
            dx, dy = s["x"] - v["x"], s["y"] - v["y"]
            assert math.hypot(dx, dy) > 0.5, (d["name"], v["name"])
            assert abs(dx) < 1e-6 or abs(dy) < 1e-6, (dx, dy)
            assert s["z"] < v["z"]                       # a stool, under the cabinet's centre
    assert seen >= 30


def test_the_fixture_pass_is_idempotent_on_the_library():
    import copy
    for d in _library():
        e = copy.deepcopy(d)
        assert level_design.place_fixtures(e) == 0, d["name"]
'''


def main():
    t = DC / "test_video_poker.py"
    assert not t.exists(), "already applied"
    _edit("prop_species.py", [(SPECIES_OLD, SPECIES_NEW)])
    _edit("level_design.py", [(PIECE_OLD, PIECE_NEW), (RECIPE_CLUB_OLD, RECIPE_CLUB_NEW),
                              (RECIPE_STRIP_OLD, RECIPE_STRIP_NEW), (RECIPE_SHOP_OLD, RECIPE_SHOP_NEW),
                              (PLACE_OLD, PLACE_NEW), (GAP_OLD, GAP_NEW)])
    t.write_bytes(TEST.encode("utf-8"))
    print("wrote test_video_poker.py")


if __name__ == "__main__":
    main()
