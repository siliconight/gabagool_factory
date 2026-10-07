"""Deli Counter 0.202.0: a wall piece needs a wall behind it.

    python patch_dc_wall_backing.py

`level_design.py` as read 2026-10-07 (261,708 bytes, LF); every anchor
asserted once, nothing written on a miss.

MEASURED FIRST (the factory's docs/findings/wall_pieces_without_walls/): 155 of
the library's 4,086 furnished wall pieces, in 18 shells, stand against a room
edge with no built wall behind them. `_wall_slots` offered every edge of a
room: an exterior edge it checked for openings and glazing, an interior edge
it took for a wall and never asked. Where two rooms meet across open floor
-- deli_a01's customer floor and its deli counter room, at y -3.0 -- an ATM
and two paper lottery boards stood with their backs against nothing, in front
of the deli case.

THE RULE: a slot is offered only where a wall the builder stands
(`layout_lint.built_walls`, the walls L25 measures) lies on the edge -- its
centreline within `_EDGE_WALL_TOL` -- and holds the piece's whole run along
it. Every slot is drawn and shuffled as before and the unheld ones dropped
after the shuffle, so the held slots keep their order and the random stream
is untouched.

REFUTED, KEPT: the first draft dropped an unheld slot before the shuffle.
That changed the length of the list the room shuffles, and a room with one
open edge re-rolled whole: its dry run moved 33 specs, where 18 held a piece
against nothing.
"""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
LD = ROOT / "deli_counter" / "level_design.py"

AIR = '''#: Air between a wall-slotted piece's back and the wall's face.
_WALL_PIECE_AIR = 0.01
'''
AIR_NEW = '''#: Air between a wall-slotted piece's back and the wall's face.
_WALL_PIECE_AIR = 0.01

#: A WALL PIECE NEEDS A WALL BEHIND IT (0.202.0). How close a built wall's
#: centreline must lie to a room edge to stand on it: a room's bound lies on
#: its wall's centreline, and 0.10 m is the census's (the factory's
#: docs/findings/wall_pieces_without_walls/), under which 3,931 of the
#: library's 4,086 furnished wall pieces found their wall.
_EDGE_WALL_TOL = 0.10
#: Every spec field the builder's walls are drawn from (`layout_lint.built_walls`
#: and the stair voids it asks): furnish adds volumes, never these, so the
#: walls are measured once a spec and kept.
_WALL_MODEL_KEYS = ("footprint_x", "footprint_y", "wall_thick", "n_stories", "has_basement",
                    "auto_exterior", "story_height", "partitions", "ext_walls", "stairs",
                    "ramps", "slab_holes", "setbacks")
_WALLS_SEEN = {}


def _built_walls(spec):
    """`layout_lint.built_walls`, kept by the fields it reads: furnish asks
    `_wall_slots` for every size of every piece in every room."""
    import json
    import layout_lint
    key = json.dumps([spec.get(k) for k in _WALL_MODEL_KEYS], sort_keys=True, default=str)
    got = _WALLS_SEEN.get(key)
    if got is None:
        if len(_WALLS_SEEN) > 512:
            _WALLS_SEEN.clear()
        got = _WALLS_SEEN[key] = layout_lint.built_walls(spec)
    return got


def _edge_backing(spec, story, n, line):
    """The stretches of a room edge a built wall stands on, merged: every wall
    on ``story`` whose faces look along axis ``n`` (0: x, a wall running along
    y) with its centreline within `_EDGE_WALL_TOL` of ``line``."""
    spans = sorted(s for _label, ws, wn, plane, _half, sp in _built_walls(spec)
                   if ws == story and wn == n and abs(plane - line) <= _EDGE_WALL_TOL
                   for s in sp)
    out = []
    for s0, s1 in spans:
        if out and s0 <= out[-1][1] + 1e-6:
            out[-1] = (out[-1][0], max(out[-1][1], s1))
        else:
            out.append((s0, s1))
    return out


def _held(backing, a, b):
    """Does one stretch of wall hold the run ``a``..``b`` whole?"""
    return any(s0 - 1e-6 <= a and b <= s1 + 1e-6 for s0, s1 in backing)
'''

DOC = '''    ``with_front`` appends the compass bearing the piece's front must face
    (away from its wall), so the caller can turn a piece the emitter will
    not turn -- `_front_turn` -- rather than trust `rot_z`, which is right
    only for a piece longer than it is deep.
    """
    x0, y0, x1, y1 = room["bounds"]
'''
DOC_NEW = '''    ``with_front`` appends the compass bearing the piece's front must face
    (away from its wall), so the caller can turn a piece the emitter will
    not turn -- `_front_turn` -- rather than trust `rot_z`, which is right
    only for a piece longer than it is deep.

    A WALL BEHIND IT (0.202.0). An edge is offered only where a wall the
    builder stands lies on it and holds the piece's whole run
    (`_edge_backing`, `_held`). Until then an interior edge was taken for a
    wall: where two rooms meet across open floor, 155 of the library's 4,086
    wall pieces stood with their backs against nothing -- deli_a01's ATM and
    two paper lottery boards among them, in front of its deli case. Every
    slot is drawn and shuffled as before and the unheld ones dropped after,
    so the held ones keep their order and only a piece that stood against
    nothing moves.
    """
    x0, y0, x1, y1 = room["bounds"]
    story = int(room.get("story", 0) or 0)
'''

NS = """        span = (x1 - x0) - long_side - 0.6
        if span <= 0:
            continue
        for _ in range(4):
            px = x0 + 0.3 + long_side / 2.0 + rng.random() * span
            if not over_openings and ext and not _clear_of_openings(
                    openings, ext, px, long_side / 2.0):
                continue
            # against the S wall (inset +1) the front must face N; against
            # the N wall, S. Long axis along x, so no long-axis turn is added.
            out.append((px, wy + inset * (short_side / 2.0 + back),
                        long_side, short_side, 180.0 if inset > 0 else 0.0,
                        0.0 if inset > 0 else 180.0))
"""
NS_NEW = """        span = (x1 - x0) - long_side - 0.6
        if span <= 0:
            continue
        backing = _edge_backing(spec, story, 1, wy)
        for _ in range(4):
            px = x0 + 0.3 + long_side / 2.0 + rng.random() * span
            if not over_openings and ext and not _clear_of_openings(
                    openings, ext, px, long_side / 2.0):
                continue
            # against the S wall (inset +1) the front must face N; against
            # the N wall, S. Long axis along x, so no long-axis turn is added.
            out.append(((px, wy + inset * (short_side / 2.0 + back),
                         long_side, short_side, 180.0 if inset > 0 else 0.0,
                         0.0 if inset > 0 else 180.0),
                        _held(backing, px - long_side / 2.0, px + long_side / 2.0)))
"""

EW = """        span = (y1 - y0) - long_side - 0.6
        if span <= 0:
            continue
        for _ in range(4):
            py = y0 + 0.3 + long_side / 2.0 + rng.random() * span
            if not over_openings and ext and not _clear_of_openings(
                    openings, ext, py, long_side / 2.0):
                continue
            # against the W wall the front must face E; against the E wall,
            # W. `long_axis_first` already turns this piece 90, so the front
            # sits at 90 + rot_z + 180: 180 here gives E, 0 gives W.
            out.append((wx + inset * (short_side / 2.0 + back), py,
                        short_side, long_side, 180.0 if inset > 0 else 0.0,
                        90.0 if inset > 0 else 270.0))
    rng.shuffle(out)
    return out if with_front else [o[:5] for o in out]
"""
EW_NEW = """        span = (y1 - y0) - long_side - 0.6
        if span <= 0:
            continue
        backing = _edge_backing(spec, story, 0, wx)
        for _ in range(4):
            py = y0 + 0.3 + long_side / 2.0 + rng.random() * span
            if not over_openings and ext and not _clear_of_openings(
                    openings, ext, py, long_side / 2.0):
                continue
            # against the W wall the front must face E; against the E wall,
            # W. `long_axis_first` already turns this piece 90, so the front
            # sits at 90 + rot_z + 180: 180 here gives E, 0 gives W.
            out.append(((wx + inset * (short_side / 2.0 + back), py,
                         short_side, long_side, 180.0 if inset > 0 else 0.0,
                         90.0 if inset > 0 else 270.0),
                        _held(backing, py - long_side / 2.0, py + long_side / 2.0)))
    # THE SHUFFLE FIRST, THEN THE WALL (0.202.0): shuffled with every slot in
    # it, as it always was, so the held slots keep the order they had and the
    # stream every later draw reads is untouched; then the slots no wall holds
    # go. Filtered before the shuffle, a room with one open edge re-rolled
    # whole -- 33 specs moved where 18 held a piece against nothing.
    rng.shuffle(out)
    out = [o for o, held in out if held]
    return out if with_front else [o[:5] for o in out]
"""


def main():
    data = LD.read_bytes()
    assert len(data) == 261708, "level_design.py is %d bytes, not the 261,708 read; refusing" % len(data)
    assert b"\r\n" not in data, "CRLF in level_design.py; refusing"
    text = data.decode("utf-8")
    edits = [(AIR, AIR_NEW), (DOC, DOC_NEW), (NS, NS_NEW), (EW, EW_NEW)]
    for old, _new in edits:
        n = text.count(old)
        assert n == 1, "anchor found %d times, not once: %r" % (n, old[:70])
    for old, new in edits:
        text = text.replace(old, new)
    LD.write_bytes(text.encode("utf-8"))
    print("level_design.py: %d -> %d bytes" % (len(data), len(LD.read_bytes())))


if __name__ == "__main__":
    main()
