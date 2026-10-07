"""Deli Counter 0.198.0 tests: a z-fight pair is judged by the side its faces face.

    python patch_dc_zfight_facing_tests.py

Appends to `deli_counter/test_zfight_gate.py`, anchored on its last test. Run
BEFORE `patch_dc_zfight_facing.py`: five must fail; the three guards (marked)
pass either side of the change, so the new rule cannot hide too much.
"""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
TEST = ROOT / "deli_counter" / "test_zfight_gate.py"

OLD_TAIL = '''    vis, buried = visible_fights([part, slab, segA, segB])
    end = [f for f in buried if f["axis"] == 2]
    assert end, "jointly covered end face must be suppressed"
    assert not [f for f in vis if f["axis"] == 2]
'''

NEW_TAIL = OLD_TAIL + '''

# ------------------------------------------- the side the faces face (0.198.0)
# A same-facing pair can be seen only from the side its two faces FACE. The
# gate buried a pair only inside a solid with matter on BOTH sides of the
# plane, so a chair and the floor module it stands in -- both bottoms on the
# slab, facing down into it -- read as flicker. Measured on cold run 9189's
# composed buildings: deli_a01 198 pairs, office 121, rail_station_a02 117;
# judged by what each face faces, 2, 2 and 1.

def test_bottoms_pressed_on_a_slab_are_hidden():
    slab = ("slab_0", _box((-10, -0.3, -10), (10, 0.0, 10)))
    floor = ("floor_room", _box((-5, 0.0, -5), (5, 0.02, 5)))
    chair = ("chair", _box((0, 0.0, 0), (0.6, 0.9, 0.6)))
    vis, buried = visible_fights([slab, floor, chair])
    assert not [f for f in vis if f["axis"] == 1 and f["side"] == "min"], vis
    assert any(f.get("buried_in") == "slab_0" for f in buried)


def test_the_same_bottoms_with_nothing_under_them_are_seen():
    """A guard: with no slab beneath, the same pair is visible."""
    floor = ("floor_room", _box((-5, 0.0, -5), (5, 0.02, 5)))
    chair = ("chair", _box((0, 0.0, 0), (0.6, 0.9, 0.6)))
    vis, _buried = visible_fights([floor, chair])
    assert any(f["axis"] == 1 and f["side"] == "min" for f in vis)


def test_a_rug_on_the_floor_still_fights():
    """A guard: both tops face the room, and nothing above shuts them."""
    slab = ("slab_0", _box((-10, -0.3, -10), (10, 0.0, 10)))
    rug = ("rug", _box((0, -0.01, 0), (2, 0.0, 3)))
    vis, _buried = visible_fights([slab, rug])
    assert any(f["axis"] == 1 and f["side"] == "max" for f in vis)


def test_float32_seams_between_tiles_still_shut_a_face():
    # 9189's deli_a01: slab tiles meet at -9.333000183 and -9.332999944
    t1 = ("slab_t1", _box((-14.25, -0.3, -14.0), (-9.5, 0.0, -9.333000183)))
    t2 = ("slab_t2", _box((-14.25, -0.3, -9.332999944), (-9.5, 0.0, -4.67)))
    tread = ("stair1_0_6", _box((-12.6, 0.0, -9.5), (-11.0, 0.62, -9.25)))
    floor = ("floor_stairwell", _box((-14.0, 0.0, -14.0), (-9.6, 0.02, -4.7)))
    vis, buried = visible_fights([t1, t2, tread, floor])
    assert not [f for f in vis if f["axis"] == 1 and f["side"] == "min"], vis
    assert any(f.get("buried_in") == "(joint cover)" for f in buried)


def test_a_two_by_two_corner_of_tiles_shuts_a_face():
    tiles = [("t%d%d" % (i, j), _box((-1 + i, -0.3, -1 + j), (i, 0.0, j)))
             for i in (0, 1) for j in (0, 1)]
    desk = ("desk", _box((-0.4, 0.0, -0.4), (0.4, 0.75, 0.4)))
    floor = ("floor_room", _box((-1, 0.0, -1), (1, 0.02, 1)))
    vis, _buried = visible_fights(tiles + [desk, floor])
    assert not [f for f in vis if f["axis"] == 1 and f["side"] == "min"], vis


def test_caps_sunk_under_the_next_slab_are_hidden():
    # two crossing walls, sunk SLAB_CAP_SINK (4 mm) under the slab above them
    a = ("int_a", _box((-1, 0.0, -0.175), (1, 2.996, 0.175)))
    b = ("int_b", _box((-0.175, 0.0, -1), (0.175, 2.996, 1)))
    above = ("slab_1", _box((-10, 3.0, -10), (10, 3.3, 10)))
    vis, _buried = visible_fights([a, b, above])
    assert not [f for f in vis if f["axis"] == 1 and f["side"] == "max"], vis


def test_the_gap_is_the_composers_sink_and_the_tolerance():
    import themed_tscn
    import zfight_gate
    assert zfight_gate.SLAB_CAP_SINK == themed_tscn.SLAB_CAP_SINK
    assert abs(zfight_gate.OUTWARD_GAP - (themed_tscn.SLAB_CAP_SINK + TOL)) < 1e-12


def test_a_desk_flush_with_the_ledge_under_it_fights():
    """A guard: office's reception desk, its sides flush with the greybox
    ledge it stands on, both facing the open room."""
    ledge = ("base:VAULTLEDGE_0", _box((-2.5, 0.0, -0.5), (2.5, 0.3, 0.5)))
    desk = ("reception_desk", _box((-2.5, 0.0, -0.4), (2.5, 1.1, 0.4)))
    vis, _buried = visible_fights([ledge, desk])
    assert any(f["axis"] == 0 for f in vis), vis
'''


def main():
    data = TEST.read_bytes()
    assert b"\r\n" not in data
    text = data.decode("utf-8")
    assert text.endswith(OLD_TAIL), "test_zfight_gate.py no longer ends as read; refusing"
    assert "OUTWARD_GAP" not in text
    TEST.write_bytes((text[:-len(OLD_TAIL)] + NEW_TAIL).encode("utf-8"))
    print("test_zfight_gate.py: 8 tests appended")


if __name__ == "__main__":
    main()
