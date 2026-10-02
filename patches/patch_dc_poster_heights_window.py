"""Deli Counter 0.170.0: poster runs hang at varied heights; a store tapes a pair in its window.

The poster pass the walker queued 2026-09-30 ("we can make them better later
right?"), its two placement halves. The colour half is Zoo 1.41.0.

  * VARIED HEIGHTS. Every wall run hung with its centre on the camera's eye,
    1.6 m, on every wall of every building -- the placement guide's
    "identical spacing, height, rotation, or mounting pattern on every wall".
    A piece may now carry `lift_steps`, offsets from its `lift`; a run takes
    one by its place in its room, and `_place_fixture` clears and builds it there.
    Club one-sheets step 10 cm either way (framed, hung level), a store's
    sale posters down to 20 under and never over (a higher one clears an
    ATM's top and hangs over it), a bar's gig bills from 15 under to 15
    over (pinned up by whoever was closing).
  * THE WINDOW. `migrate_window_poster.py` (new, in the repo) tapes one
    `window_poster` -- Zoo's `poster_wall`, `store` family, two sheets --
    inside each convenience store's glass, facing the street. This patch
    routes the name to the species and to paper, and keeps paper on a wall
    out of a room's furniture count (it stands on no floor).

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


LEVEL = [
    ('''           rooms=None, distinct=False, solo=False):
    return {"name": name, "sizes": tuple(sizes), "where": where,''',
     '''           rooms=None, distinct=False, solo=False, lift_steps=None):
    return {"name": name, "sizes": tuple(sizes), "where": where,'''),
    ('''            "distinct": distinct, "solo": solo}
''', '''            "distinct": distinct, "solo": solo,
            # offsets from `lift`, one taken by a placement's own name
            # (0.170.0, `_lift_step`); None hangs every one at `lift`
            "lift_steps": tuple(lift_steps) if lift_steps else None}
'''),
    ('''           variants=4, form="club", most=3, most_big=(150.0, 5),
           lift=_eye_height(), collision="none", distinct=True),''',
     '''           variants=4, form="club", most=3, most_big=(150.0, 5),
           lift=_eye_height(), collision="none", distinct=True,
           lift_steps=(-0.1, 0.0, 0.1)),'''),
    ('''           variants=4, form="bar", most=2, most_big=(80.0, 3),
           lift=_eye_height(), collision="none", distinct=True,
           rooms=("bar", "taproom", "tavern", "pub", "social")),''',
     '''           variants=4, form="bar", most=2, most_big=(80.0, 3),
           lift=_eye_height(), collision="none", distinct=True,
           lift_steps=(-0.15, -0.05, 0.0, 0.15),
           rooms=("bar", "taproom", "tavern", "pub", "social")),'''),
    ('''           variants=4, form="store", most=2, most_big=(150.0, 3),
           lift=_eye_height(), collision="none", distinct=True, off_glass=True,''',
     '''           variants=4, form="store", most=2, most_big=(150.0, 3),
           lift=_eye_height(), collision="none", distinct=True, off_glass=True,
           # never ABOVE the eye: 0.15 up, a run's foot (1.45) cleared an ATM's
           # top and hung over it (pharmacy_a02, `test_store_atms`)
           lift_steps=(-0.2, -0.1, 0.0),'''),
    ('''    # GLASS: a run hung inside a storefront faces the shop, so the street
    # sees its back; a store's window posters face out, and that is a rule
    # of its own (the window sign's), not this one.
''', '''    # GLASS: a run hung inside a storefront faces the shop, so the street
    # sees its back; a store's window posters face out, and that is a rule
    # of its own (the window sign's), not this one -- `window_poster`,
    # `migrate_window_poster.py`, 0.170.0.
    #
    # NOT ALL AT ONE HEIGHT (0.170.0). Until now every run's centre was on
    # the eye, on every wall of every building -- the placement guide's
    # "identical ... height ... on every wall". `lift_steps` are offsets from
    # `lift`; a run takes one by its place in its room (`_lift_step`). A club's
    # one-sheets are framed and hung near level, a store's sale posters step
    # a little more, a bar's bills were pinned up by whoever was closing.
'''),
    ('''def _eye_height():''', '''def _lift_step(p, key, rtag, k):
    """The offset from its `lift` that a room's ``k``-th ``key`` hangs at
    (0.170.0): one of the piece's `lift_steps`, by the crc32 of the three,
    or 0.0 for a piece with none.

    BY ITS ORDINAL IN THE ROOM, NOT ITS NAME. The first cut keyed the step
    on the volume's name, which carries the room's next free sequence
    number -- and a run that found no wall at its step was retried by the
    next pass under a new number, drew a new step, and fitted: the library
    stopped being a fixed point of the fixture pass (strip_club_a03 grew a
    run on the second pass). `k` is the same on every pass."""
    steps = p["lift_steps"]
    if not steps:
        return 0.0
    import zlib
    return float(steps[(zlib.crc32(f"{key}|{rtag}|{k}".encode("utf-8")) & 0xFFFFFFFF) % len(steps)])


def _eye_height():'''),
    ('''        half = max(w, d) / 2.0
        lift = _piece_lift(spec, p, h)
        hung = lift is not None
        above = (lift - h / 2.0) if hung else None
        below = (lift + h / 2.0) if hung else None
        # A PIECE HUNG OVER THE FLOOR IS SOMETHING A BODY WALKS UNDER. The''',
     '''        half = max(w, d) / 2.0
        lift = _piece_lift(spec, p, h)
        hung = lift is not None
        # its own step off the piece's height (0.170.0), by its ordinal in
        # the room: cleared here at the height it is built at
        if hung and p["lift_steps"]:
            lift = round(lift + _lift_step(p, key, rtag, k), 3)
        above = (lift - h / 2.0) if hung else None
        below = (lift + h / 2.0) if hung else None
        # A PIECE HUNG OVER THE FLOOR IS SOMETHING A BODY WALKS UNDER. The'''),
    ('''        vol = _make_volume(spec, key, f"{key}_{rtag}_{seq}", qx, qy, sx, sy, h, rot,
                           story, sh, building)
        if p["distinct"] and not _distinct_variant(spec, key, rtag, vol, variant_count(p)):''',
     '''        vol = _make_volume(spec, key, f"{key}_{rtag}_{seq}", qx, qy, sx, sy, h, rot,
                           story, sh, building,
                           lift=lift if p["lift_steps"] else None)
        if p["distinct"] and not _distinct_variant(spec, key, rtag, vol, variant_count(p)):'''),
    ('''    (("poster_wall",), "paper"),
    (("poster",), "metal_bare"),''', '''    (("poster_wall", "window_poster"), "paper"),
    (("poster",), "metal_bare"),'''),
    ('''        bottom = v.get("z", 0) - v.get("size_z", 0) / 2
        if (v.get("collision") == "none"
                and bottom - story * sh >= headroom - 1e-9):
            continue
''', '''        bottom = v.get("z", 0) - v.get("size_z", 0) / 2
        if (v.get("collision") == "none"
                and bottom - story * sh >= headroom - 1e-9):
            continue
        # PAPER ON A WALL stands on no floor either (0.170.0): the store's
        # `window_poster` is taped to the glass at the eye, under the
        # headroom line the rule above draws, and counted it would cost the
        # sales floor a piece of furniture -- the window sign's defect again
        if v.get("collision") == "none" and v.get("material") == "paper":
            continue
'''),
]

SPECIES = [
    ('''    (("poster_wall",), "poster_wall"),
''', '''    # `window_poster` (0.170.0): the pair of sale sheets a store tapes in its
    # glass, the same species; it must sit above `poster` for the same reason
    (("poster_wall", "window_poster"), "poster_wall"),
'''),
]

T_WALLS = [
    ('''    assert p["lift"] == agent_contract.eye_height()
''', '''    assert p["lift"] == agent_contract.eye_height()
    # 0.170.0: a run hangs a step off the eye, never more than 0.25 m, and
    # level is one of the steps
    assert p["lift_steps"] and 0.0 in p["lift_steps"]
    assert all(abs(s) <= 0.25 for s in p["lift_steps"])
'''),
    ('''            fam = PIECES[_stem(v)]
            story = round((v["z"] - agent_contract.eye_height()) / sh)
            assert v["z"] == round(story * sh + agent_contract.eye_height(), 3), v["name"]
''', '''            fam = PIECES[_stem(v)]
            story = round((v["z"] - agent_contract.eye_height()) / sh)
            # 0.170.0: at the eye plus the run's OWN step -- its room's k-th
            # run of its kind, in the order the pass numbered them
            p = level_design._PIECES[_stem(v)]
            rtag, seq = v["name"][len(_stem(v)) + 1:].rsplit("_", 1)
            k = sorted(int(u["name"].rsplit("_", 1)[1]) for u in _runs(d)
                       if u["name"].startswith(f"{_stem(v)}_{rtag}_")).index(int(seq))
            want = agent_contract.eye_height() + level_design._lift_step(p, _stem(v), rtag, k)
            assert v["z"] == round(story * sh + round(want, 3), 3), v["name"]
'''),
    ('''def test_a_store_s_runs_are_off_the_glass():''', '''def test_the_runs_do_not_all_hang_at_one_height():
    """0.170.0, the placement guide: "identical spacing, height, rotation,
    or mounting pattern on every wall" is the tell. Across the library each
    family's runs take every one of its steps."""
    seen = {}
    for d in _library():
        sh = level_design._story_height(d)
        for v in _runs(d):
            story = round((v["z"] - agent_contract.eye_height()) / sh)
            seen.setdefault(_stem(v), set()).add(round(v["z"] - story * sh - agent_contract.eye_height(), 3))
    for key in PIECES:
        steps = set(level_design._PIECES[key]["lift_steps"])
        # more than one height, and none that is not a step (the library has
        # eight bar runs: too few to promise every step is drawn)
        assert seen[key] <= steps and len(seen[key]) >= 2, (key, seen[key])


def test_a_store_s_runs_are_off_the_glass():'''),
]

TEST_WINDOW = '''"""A store tapes a pair of sale posters in its window (0.170.0).

The walker, 2026-09-29, choosing where posters go: "store windows and walls".
The walls were 0.163.0; this is the window, by the window sign's rule: inside
the sales floor's glass, beside an entrance, facing the street, clear of
every opening and of the sign, at the eye. And it costs the sales floor no
furniture: paper on a wall stands on no floor.
"""
import copy
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import agent_contract  # noqa: E402
import level_design  # noqa: E402
import migrate_slush_machine  # noqa: E402
import migrate_window_poster as M  # noqa: E402
import migrate_window_sign as SIGN  # noqa: E402
import prop_species  # noqa: E402
import test_window_sign  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
STORES = test_window_sign.STORES


def _spec(name):
    return json.load(open(os.path.join(HERE, "specs", name + ".json"), encoding="utf-8"))


def _poster(spec):
    (v,) = [v for v in spec["volumes"] if v["name"] == M.NAME]
    return v


def test_the_name_routes_to_the_poster_wall_on_paper():
    assert prop_species.species_for_name(M.NAME) == "poster_wall"
    assert level_design._prop_material({"materials": []}, M.NAME) == "paper"
    # and the runs on the walls still route as they did
    assert prop_species.species_for_name("poster_wall_store_r0123abcd_4") == "poster_wall"


def test_every_store_tapes_one_and_the_migration_is_done():
    for name in STORES:
        spec = _spec(name)
        v = _poster(spec)
        assert v["form"] == "store" and v["collision"] == "none" and v["material"] == "paper"
        assert 0 <= v["variant"] < M.VARIANTS
        assert any(m.get("id") == "paper" for m in spec["materials"]), name
        assert M.migrate(copy.deepcopy(spec)) == (False, None), name


def test_it_is_on_the_sales_floors_glass_at_the_eye_facing_out_clear_of_the_sign():
    for name in STORES:
        spec = _spec(name)
        v = _poster(spec)
        room = next(r for r in spec["rooms"] if r["id"] == SIGN.ROOM)
        x0, y0, x1, y1 = room["bounds"]
        assert x0 <= v["x"] <= x1 and y0 <= v["y"] <= y1, name
        assert v["z"] == agent_contract.eye_height(), name
        wt = float(spec.get("wall_thick") or 0.3)
        hx, hy = spec["footprint_x"] / 2.0, spec["footprint_y"] / 2.0
        fx, fy = migrate_slush_machine._front(v)
        # its front points out through the wall it is taped inside, and that
        # wall is storefront glass
        if fx:
            wall = "E" if fx > 0 else "W"
            gap = hx - abs(v["x"])
        else:
            wall = "N" if fy > 0 else "S"
            gap = hy - abs(v["y"])
        assert (v["x"] * fx > 0) or (v["y"] * fy > 0), (name, v)
        assert abs(gap - (wt / 2.0 + M.INSET + M.SIZE[1] / 2.0)) < 1e-6, (name, gap)
        mats = {w["wall"]: w.get("material") for w in spec["ext_walls"] if not w.get("story")}
        assert mats[wall] == SIGN.STOREFRONT, (name, wall)
        # clear of the window sign along the wall
        sign = next(s for s in spec["volumes"] if s["name"] == SIGN.NAME)
        u, su = (v["x"], sign["x"]) if fy else (v["y"], sign["y"])
        assert abs(u - su) >= (M.SIZE[0] + SIGN.SIZE[0]) / 2.0 + M.GAP - 1e-6, (name, u, su)


def test_paper_on_a_wall_takes_no_share_of_the_rooms_furniture():
    spec = _spec("gas_station_a02")
    room = next(r for r in spec["rooms"] if r["id"] == SIGN.ROOM)
    with_it = level_design._room_volume_count(spec, room)
    bare = copy.deepcopy(spec)
    bare["volumes"] = [v for v in bare["volumes"] if v["name"] != M.NAME]
    assert level_design._room_volume_count(bare, room) == with_it
    # the control: a solid thing in the same place does count
    solid = copy.deepcopy(spec)
    _poster(solid).update(collision="convex", material="metal_painted")
    assert level_design._room_volume_count(solid, room) == with_it + 1
'''


def main():
    t = DC / "test_window_poster.py"
    assert not t.exists(), "already applied"
    assert (DC / "migrate_window_poster.py").exists(), "the migration is not in the repo"
    _edit("level_design.py", LEVEL)
    _edit("prop_species.py", SPECIES)
    _edit("test_poster_walls.py", T_WALLS)
    t.write_bytes(TEST_WINDOW.encode("utf-8"))
    print("wrote test_window_poster.py")


if __name__ == "__main__":
    main()
