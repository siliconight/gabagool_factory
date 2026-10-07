"""Deli Counter 0.202.0 tests: furnish keeps off an authored hole in its own floor.

    python patch_dc_hole_clear_tests.py

Appends to `deli_counter/test_stale_pieces.py` (6,175 bytes, LF, as read
2026-10-07), anchored on its last test. Run BEFORE `patch_dc_hole_clear.py`:
the hole test fails on 0.201.0; the storey-below guard passes either side.

WHY NOW. Layout_lint L23's second cause, "UNSEEN": furnish clears the stairs
(`_stair_reserved_rects`) and never an authored `slab_holes` opening, so
apartment_walkup_a01's dining set stood over its 2 x 2 m drop hole. 0.202.0's
refurnish (the wall rule) re-rolled that room and rowhouse_raid's, and both
dining sets landed over their holes -- rowhouse_raid's for the first time.
cbp_town_finale's and final_stand's furnished pieces stand inside atrium holes
of 28 x 22 m and 10 x 8 m, which nothing fills: floating furniture.
"""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
TEST = ROOT / "deli_counter" / "test_stale_pieces.py"

OLD_TAIL = '''def test_stale_baseline_has_not_gone_stale():
    lib = _library()
    gone = {k: [n for n in v if n not in lib.get(k, [])] for k, v in _frozen().items()}
    assert not {k: v for k, v in gone.items() if v}, gone
'''

NEW_TAIL = OLD_TAIL + '''

# ------------------------------------------- an authored hole (0.202.0)
# L23's second cause, "UNSEEN": furnish cleared the stairs and never an
# authored `slab_holes` opening. apartment_walkup_a01's dining set stood over
# its 2 x 2 m drop hole; cbp_town_finale's and final_stand's furnished pieces
# inside atrium holes nothing fills.

def _holed(story=1):
    """Two storeys, one 20 x 14 m room each, an authored 4 x 4 m hole in the
    floor of `story`'s room."""
    s = {"name": "holed", "seed": 7, "footprint_x": 20.0, "footprint_y": 14.0,
         "story_height": 3.0, "n_stories": 2, "wall_thick": 0.3, "stairs": [],
         "slab_holes": [{"story": story, "x": 0.0, "y": 0.0, "size_x": 4.0, "size_y": 4.0}],
         "rooms": [{"id": "lower_hall", "story": 0, "role": "connector",
                    "bounds": [-10.0, -7.0, 10.0, 7.0]},
                   {"id": "upper_hall", "story": 1, "role": "connector",
                    "bounds": [-10.0, -7.0, 10.0, 7.0]}],
         "volumes": [], "partitions": [], "ext_walls": [], "markers": []}
    return s


def _over(v, x0, y0, x1, y1):
    return (v["x"] + v["size_x"] / 2 > x0 and v["x"] - v["size_x"] / 2 < x1
            and v["y"] + v["size_y"] / 2 > y0 and v["y"] - v["size_y"] / 2 < y1)


def test_furnish_keeps_off_an_authored_hole_in_its_own_floor():
    for seed in range(8):
        s = _holed()
        s["seed"] = seed
        level_design.furnish(s)
        upper = [v for v in s["volumes"] if layout_lint.piece_story(s, v) == 1]
        assert upper, "nothing furnished upstairs (seed %d)" % seed
        assert layout_lint.stale_pieces(s) == [], (seed, layout_lint.stale_pieces(s))


def test_the_storey_below_a_hole_may_stand_under_it():
    """A guard: a hole in storey 1's floor is a ceiling over storey 0, not a
    floor; the room below is furnished as it was."""
    a, b = _holed(), _holed()
    b["slab_holes"] = []
    level_design.furnish(a)
    level_design.furnish(b)
    lower = lambda s: sorted((v["name"], v["x"], v["y"]) for v in s["volumes"]
                             if layout_lint.piece_story(s, v) == 0)
    assert lower(a) == lower(b)
'''


def main():
    data = TEST.read_bytes()
    assert len(data) == 6175, "test_stale_pieces.py is %d bytes, not the 6,175 read" % len(data)
    assert b"\r\n" not in data
    text = data.decode("utf-8")
    assert text.endswith(OLD_TAIL), "test_stale_pieces.py no longer ends as read; refusing"
    TEST.write_bytes((text[:-len(OLD_TAIL)] + NEW_TAIL).encode("utf-8"))
    print("test_stale_pieces.py: 2 tests appended")


if __name__ == "__main__":
    main()
