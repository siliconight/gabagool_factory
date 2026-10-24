"""Zoo 1.122.0 on a CLONE (<repo>): no rim across a hole where two rooms' skins meet (the walker's walk of cold run
9386, finding 4: "non collision rod on the stair case that shouldn't be there"). Anchored; refuses on a miss.

    python edit_zoo_plate_rim.py <repo>
"""
import pathlib
import sys

R = pathlib.Path(sys.argv[1])


def edit(rel, pairs):
    p = R / rel
    b = p.read_bytes()
    crlf = b"\r\n" in b
    t = b.decode("utf-8").replace("\r\n", "\n")
    for o, n in pairs:
        assert t.count(o) == 1, (rel, o[:70])
        t = t.replace(o, n)
    p.write_bytes((t.replace("\n", "\r\n") if crlf else t).encode("utf-8"))


edit("zoo_keeper/core/arch.py", [
    ('''#: A plate's voids are inset from its edges by this much so the union's outer
#: bbox still equals the authored (w, d, h). Same law as the jambs in
#: :func:`void_for` -- fit-to-exact-dims has to pass by construction, and a
#: stairwell cut hard against a wall would otherwise shrink the plate. Two
#: centimetres of rim at the lip of a hole is invisible from below and carries
#: no collision.
PLATE_RIM = 0.02''',
     '''#: A plate's voids are inset from an edge by this much WHERE THEY WOULD TAKE
#: THAT WHOLE EDGE, so the union's outer bbox still equals the authored
#: (w, d, h). Same law as the jambs in :func:`void_for` -- fit-to-exact-dims has
#: to pass by construction, and a stairwell cut hard against a wall the whole
#: plate's depth would otherwise shrink it.
#:
#: REFUTED AND KEPT: "Two centimetres of rim at the lip of a hole is invisible
#: from below." It was inset from EVERY edge a void reached. Where a stairwell
#: crosses the line between two rooms, each room's ceiling skin kept its 2 cm
#: rim straight across the hole, and the two met back to back as a pale bar
#: spanning the stairwell with no collision -- the walker, walking cold run
#: 9386: "non collision rod on the stair case that shouldn't be there" (the
#: office's two storey-0 ceilings, found by hiding them: the factory's
#: `docs/findings/walk_2026-10-23_9386/`). A void reaching an edge along PART of
#: it leaves the rest of that edge standing, which holds the bbox already, so
#: it is cut to the edge (1.122.0).
PLATE_RIM = 0.02'''),
    ('''def plate_voids(w: float, d: float, voids, rim: float = PLATE_RIM):
    """Clip rectangular voids to a centered w x d plate, dropping degenerates.

    ``voids`` are dicts with x0/y0/x1/y1 in the plate's own centered coords.
    Returns a normalised list, sorted, so the tiling below is deterministic.
    """
    hw, hd = w / 2.0, d / 2.0
    lo_x, hi_x = -hw + rim, hw - rim
    lo_y, hi_y = -hd + rim, hd - rim
    out = []
    for v in voids or ():
        x0 = _clamp(min(float(v["x0"]), float(v["x1"])), lo_x, hi_x)
        x1 = _clamp(max(float(v["x0"]), float(v["x1"])), lo_x, hi_x)
        y0 = _clamp(min(float(v["y0"]), float(v["y1"])), lo_y, hi_y)
        y1 = _clamp(max(float(v["y0"]), float(v["y1"])), lo_y, hi_y)
        if x1 - x0 <= _EPS or y1 - y0 <= _EPS:
            continue          # entirely outside the plate, or a sliver
        out.append({"x0": round(x0, 6), "y0": round(y0, 6),
                    "x1": round(x1, 6), "y1": round(y1, 6)})
    return sorted(out, key=lambda v: (v["x0"], v["y0"], v["x1"], v["y1"]))''',
     '''def _covers(spans, lo: float, hi: float) -> bool:
    """Does the union of ``spans`` ((a, b) intervals) cover [lo, hi]?"""
    at = lo
    for a, b in sorted(spans):
        if a > at + _EPS:
            return False
        at = max(at, b)
    return at >= hi - _EPS


def plate_voids(w: float, d: float, voids, rim: float = PLATE_RIM):
    """Clip rectangular voids to a centered w x d plate, dropping degenerates.

    ``voids`` are dicts with x0/y0/x1/y1 in the plate's own centered coords.
    Each is cut to the plate's edge, except on a side the voids touching it
    would take END TO END: there each keeps ``rim`` from that edge, so some of
    the plate still stands on every side and its bbox is the authored one
    (`PLATE_RIM`, 1.122.0). Returns a normalised list, sorted, so the tiling
    below is deterministic.
    """
    hw, hd = w / 2.0, d / 2.0
    cut = []
    for v in voids or ():
        x0 = _clamp(min(float(v["x0"]), float(v["x1"])), -hw, hw)
        x1 = _clamp(max(float(v["x0"]), float(v["x1"])), -hw, hw)
        y0 = _clamp(min(float(v["y0"]), float(v["y1"])), -hd, hd)
        y1 = _clamp(max(float(v["y0"]), float(v["y1"])), -hd, hd)
        if x1 - x0 <= _EPS or y1 - y0 <= _EPS:
            continue          # entirely outside the plate, or a sliver
        cut.append([x0, y0, x1, y1])
    # the sides the voids would take whole, asked of the cut voids, not the rimmed
    lo_x = _covers([(v[1], v[3]) for v in cut if v[0] <= -hw + _EPS], -hd, hd)
    hi_x = _covers([(v[1], v[3]) for v in cut if v[2] >= hw - _EPS], -hd, hd)
    lo_y = _covers([(v[0], v[2]) for v in cut if v[1] <= -hd + _EPS], -hw, hw)
    hi_y = _covers([(v[0], v[2]) for v in cut if v[3] >= hd - _EPS], -hw, hw)
    out = []
    for x0, y0, x1, y1 in cut:
        if lo_x and x0 <= -hw + _EPS:
            x0 = -hw + rim
        if hi_x and x1 >= hw - _EPS:
            x1 = hw - rim
        if lo_y and y0 <= -hd + _EPS:
            y0 = -hd + rim
        if hi_y and y1 >= hd - _EPS:
            y1 = hd - rim
        if x1 - x0 <= _EPS or y1 - y0 <= _EPS:
            continue
        out.append({"x0": round(x0, 6), "y0": round(y0, 6),
                    "x1": round(x1, 6), "y1": round(y1, 6)})
    return sorted(out, key=lambda v: (v["x0"], v["y0"], v["x1"], v["y1"]))'''),
])
edit("tests/test_plate.py", [
    ('''def test_two_holes():''',
     '''def test_a_hole_crossing_part_of_an_edge_keeps_no_rim_across_it():
    """1.122.0, the walker walking cold run 9386: "non collision rod on the stair case that shouldn't be there". The
    office's stairwell crosses the line between two rooms, and each room's ceiling skin kept a 2 cm rim across the
    hole at that line. Here the ground bullpen's: 34 x 12, its void x -2..2 running past its +y edge. No part stands
    over the hole, the hole takes its whole area, and the bbox is still the authored one. FAILS ON 1.121.0."""
    w, d = 34.0, 12.0
    p = arch.plate_parts(w, d, 0.02, [{"x0": -2.0, "y0": 3.35, "x1": 2.0, "y1": 9.15}])
    over = [(n, c, s) for n, c, s in p
            if c[0] - s[0] / 2.0 < 2.0 - 1e-9 and c[0] + s[0] / 2.0 > -2.0 + 1e-9
            and c[1] + s[1] / 2.0 > 3.35 + 1e-9]
    assert not over, over
    assert abs(_area(p) - (w * d - 4.0 * (6.0 - 3.35))) < 1e-6
    lo, hi = arch.parts_bbox(p)
    assert (round(lo[0], 6), round(hi[0], 6), round(lo[1], 6), round(hi[1], 6)) == (-17.0, 17.0, -6.0, 6.0)


def test_a_hole_taking_a_whole_edge_keeps_its_rim_on_that_side_only():
    """The rim is for the side a void would take end to end -- here +x, the void running the plate's whole depth --
    and nowhere else: the +y and -y edges keep standing beside the void, so it is cut to them."""
    vs = arch.plate_voids(10.0, 8.0, [{"x0": 3.0, "y0": -9.0, "x1": 9.0, "y1": 9.0}])
    assert vs == [{"x0": 3.0, "y0": -4.0, "x1": round(5.0 - arch.PLATE_RIM, 6), "y1": 4.0}], vs


def test_two_holes():'''),
])
print("arch.plate_voids: a rim only on a side a void takes whole; tests")
