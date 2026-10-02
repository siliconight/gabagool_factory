"""Deli Counter 0.172.0: the video store, revised from the walker's photographs.

0.171.0 laid the store out "from the era". Cold run 9132 put it in a level
and the walker sent ten photographs (docs/SET_DRESSING_REFERENCES.md, "The
walker's video store references"): a cult store's tall painted aisles of
spines, and a chain store's new-release wall and counter. Zoo 1.44.0 redrew
the rack; this is the floor plan's half.

  * THE ISLANDS ARE AISLES: 1.9 m, full height, where they were 1.4 m racks
    a body sees over. The four rows are corridors now.
  * A NEW-RELEASE WALL: the east wall's two runs nearest the storefront are
    Zoo's `display` form -- black racks of faced-out boxes -- and the third
    stays spines.
  * TWO ARMCHAIRS by the shop window, facing the floor (the photographs'
    pair of orange velvet chairs; Zoo's `club_chair`, in what colour it
    comes).
  * NO SALE POSTERS: the recipe's `poster_wall_store` hung the convenience
    store's SCRATCH & WIN and HOT DOGS 2/$1 on a video store's wall (cold
    run 9132). A video store's posters are film one-sheets, which nothing
    draws yet; until something does, the wall is bare.

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


PRESETS = [
    ('''    # the EAST wall, door to back: three runs, facing the room (-x)
    for k, y in enumerate((-4.2, -4.2 + step, -4.2 + 2 * step)):
        racks.append(_rack(f"tape_wall_e{k + 1}", hx - off, y, "y", "wall", 2 + k))''',
     '''    # the EAST wall, door to back: three runs, facing the room (-x). The two
    # nearest the storefront are THE NEW-RELEASE WALL (0.172.0, the
    # photographs' chain store): Zoo's `display` form, boxes faced out.
    for k, y in enumerate((-4.2, -4.2 + step, -4.2 + 2 * step)):
        racks.append(_rack(f"tape_wall_e{k + 1}", hx - off, y, "y",
                           "display" if k < 2 else "wall", 2 + k))'''),
    ('''    # FOUR ROWS OF ISLANDS, two runs a row, low enough to see the back wall
    # over. The aisles between rows are 1.7 to 2.6 m and the one along the
    # back wall is 1.4: every one is over `min_corridor_width` 1.1.
    for c, x in enumerate((-3.5, 0.0, 3.0, 6.0)):
        for k, y in enumerate((-2.82, -2.82 + step)):
            racks.append(_rack(f"tape_island_{c + 1}{'ab'[k]}", x, y, "y", "island",
                               (c * 2 + k) % 6, d=0.9, h=1.4))''',
     '''    # FOUR ROWS OF ISLANDS, two runs a row. FULL HEIGHT (0.172.0): the
    # photographs' floor units are 1.9 m double-sided shelving in long rows
    # -- aisles, with nothing to see over -- where 0.171.0's were 1.4 m. The
    # aisles between rows are 1.7 to 2.6 m and the one along the back wall
    # is 1.4: every one is over `min_corridor_width` 1.1.
    for c, x in enumerate((-3.5, 0.0, 3.0, 6.0)):
        for k, y in enumerate((-2.82, -2.82 + step)):
            racks.append(_rack(f"tape_island_{c + 1}{'ab'[k]}", x, y, "y", "island",
                               (c * 2 + k) % 6, d=0.9, h=1.9))'''),
    ('''    # ...and the store's floor safe, the objective.
    safe = (-8.2, 6.2, 0.2)''', '''    # TWO ARMCHAIRS by the shop window, facing the floor (0.172.0): the
    # photographs' pair of velvet chairs in a corner of the stacks.
    chairs = [{"name": f"club_chair_window_{k + 1}", "x": x, "y": -6.2, "z": 0.39,
               "size_x": 0.78, "size_y": 0.75, "size_z": 0.78, "rot_z": 180.0,
               "collision": "convex", "material": "wood", "variant": k}
              for k, x in enumerate((1.6, 2.8))]
    # ...and the store's floor safe, the objective.
    safe = (-8.2, 6.2, 0.2)'''),
    ('''        counter,
    ] + racks
''', '''        counter,
    ] + racks + chairs
'''),
]

LEVEL = [
    ('''                    "one_cluster": True,
                    "fixtures": ("poster_wall_store",)},''',
     '''                    "one_cluster": True,
                    # NO SALE POSTERS (0.172.0): `poster_wall_store` is the
                    # convenience store's copy, and cold run 9132 hung SCRATCH
                    # & WIN and HOT DOGS 2/$1 in a video store. Its posters are
                    # film one-sheets, which nothing draws yet.
                    "fixtures": ()},'''),
]

TESTS = [
    ('''ZOO_FORMS = ("wall", "island", "adult")''', '''ZOO_FORMS = ("wall", "island", "adult", "display")'''),
    ('''    assert forms.count("wall") == 8 and forms.count("island") == 8 and forms.count("adult") == 3''',
     '''    # 0.172.0: the east wall's two front runs are the new-release display
    assert (forms.count("wall"), forms.count("display"), forms.count("island"),
            forms.count("adult")) == (6, 2, 8, 3)
    # ...and the islands are aisles, not racks a body sees over
    assert {v["size_z"] for v in racks if v["form"] == "island"} == {1.9}
    assert {v["size_z"] for v in racks if v["form"] != "island"} == {2.0}'''),
    ('''    posters = [v for v in done["volumes"] if v["name"].startswith("poster_wall_store_")]
    assert len(posters) >= 1
''', '''    # 0.172.0: no convenience-store sale posters on a video store's wall
    assert not [v for v in done["volumes"] if v["name"].startswith("poster_wall_")]
'''),
    ('''def test_the_back_room_has_two_ways_in():''', '''def test_two_armchairs_stand_by_the_window_facing_the_floor():
    spec = _store(enrich=False)
    chairs = [v for v in spec["volumes"] if v["name"].startswith("club_chair_window_")]
    assert len(chairs) == 2
    hy = spec["footprint_y"] / 2.0
    aisle = agent_contract.min_corridor_width()
    for v in chairs:
        assert prop_species.species_for_name(v["name"]) == "club_chair"
        assert _room_of(spec, v)["id"] == "sales_floor"
        assert v["y"] < -hy + 1.5 and float(v["rot_z"]) == 180.0      # at the glass, facing in
        for r in _racks(spec):
            x0, y0, x1, y1 = _rect(r)
            cx0, cy0, cx1, cy1 = _rect(v)
            gx = max(x0 - cx1, cx0 - x1, 0.0)
            gy = max(y0 - cy1, cy0 - y1, 0.0)
            assert (gx * gx + gy * gy) ** 0.5 >= aisle, (v["name"], r["name"])


def test_the_back_room_has_two_ways_in():'''),
]


def main():
    s = (DC / "presets.py").read_text(encoding="utf-8")
    assert "club_chair_window_" not in s, "already applied"
    _edit("presets.py", PRESETS)
    _edit("level_design.py", LEVEL)
    _edit("test_video_store.py", TESTS)


if __name__ == "__main__":
    main()
