"""Deli Counter 0.167.0: the canopy's washes hang over the lanes.

Cold run 9120's FLAPPHAS walk, finding 4: the forecourt is dark -- "under the
canopy, the pump stands in shadow beside a lit patch". `_canopy_anchors`
spread its washes evenly along the deck's long axis, so on gas_station_a02's
22 x 13 m deck the three washes stood at x -7.33, 0 and 7.33 -- within 1.33 m
of the three islands at -6, 0 and 6. A downward spot over an island lights the
island and the pump's top and grazes the pump's faces, and the faces are what
a driver and a player look at: they face the LANES, which fell between pools.
Cold run 9121 photographed one face square on at frame mean 11.2 of 255.

With pump islands under the deck, the washes now hang over the lanes: the
gaps between islands, and between the outer islands and the deck's edge, that
are at least `_CANOPY_LANE_MIN` wide (a car's width), along the islands' long
axis, one wash a lane, to `_CANOPY_WASH_MAX`. Each owns its lane's pool (the
lane's width by the deck's depth). A deck with no islands under it keeps the
even spread, so every canopy without pumps is unchanged. gas_station_a02:
four washes at x -8.9, -3, 3, 8.9 where there were three -- one light more,
priced on the cold run that ships it.

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


CONST_OLD = '''#: The lamp grid hangs this far below the soffit.'''
CONST_NEW = '''#: THE LANES (0.167.0). Pump islands are the volumes named this, and a gap
#: between them -- or between the outer island and the deck's edge -- is a
#: lane when it is at least this wide: a car's width and a door's swing. A
#: wash hangs over each lane, because the pumps' faces face the lanes.
_PUMP_ISLAND = "pump_island"
_CANOPY_LANE_MIN = 2.4
#: The lamp grid hangs this far below the soffit.'''

WASH_OLD = '''        # THE LIGHT. A few washes, along the deck's long axis, inset so the
        # pools land on the tarmac rather than past the drip line.
        n = _CANOPY_WASH_BASE + int((sx * sy) // _CANOPY_WASH_PER_AREA)
        n = max(_CANOPY_WASH_BASE, min(_CANOPY_WASH_MAX, n))
        span, across = (sx, True) if sx >= sy else (sy, False)
        step = span / float(n)
        for i in range(n):
            off = -span / 2.0 + step * (i + 0.5)
            x = cx + off if across else cx
            y = cy if across else cy + off
            out.append({'''
WASH_NEW = '''        # THE LIGHT. Over the LANES when pump islands stand under the deck
        # (0.167.0, `_canopy_lanes`): a pump's faces face its lanes, and a
        # wash over an island grazes them. Otherwise a few washes, along the
        # deck's long axis, inset so the pools land on the tarmac rather
        # than past the drip line.
        lanes = _canopy_lanes(deck, volumes)
        if lanes:
            spots = lanes
        else:
            n = _CANOPY_WASH_BASE + int((sx * sy) // _CANOPY_WASH_PER_AREA)
            n = max(_CANOPY_WASH_BASE, min(_CANOPY_WASH_MAX, n))
            span, across = (sx, True) if sx >= sy else (sy, False)
            step = span / float(n)
            spots = []
            for i in range(n):
                off = -span / 2.0 + step * (i + 0.5)
                spots.append((cx + off if across else cx, cy if across else cy + off,
                              [round(step, 3), round(min(sx, sy), 3)]))
        for i, (x, y, pool) in enumerate(spots):
            out.append({'''

POOL_OLD = '''                # the pool this wash owns, so Lux need not divide the deck
                # itself and two canopies of different sizes light alike
                "size": [round(step, 3), round(min(sx, sy), 3)],'''
POOL_NEW = '''                # the pool this wash owns, so Lux need not divide the deck
                # itself and two canopies of different sizes light alike
                "size": pool,'''

FUNC_OLD = '''def _canopy_anchors(volumes):'''
FUNC_NEW = '''def _canopy_lanes(deck, volumes):
    """``[(x, y, pool)]``, one per LANE under ``deck``, or [] when no pump
    island stands under it.

    The islands' long axis is the lanes' direction; the lanes are the gaps
    ACROSS it -- between neighbouring islands, and between the outer islands
    and the deck's edge -- at least `_CANOPY_LANE_MIN` wide. A wash stands
    over each lane's centre, half way along the deck, and owns the lane's
    width by the deck's length that way. More lanes than `_CANOPY_WASH_MAX`
    keep the outermost two and the evenly spread rest, so the light budget on
    the forecourt ground holds whatever the deck."""
    cx, cy = float(deck.get("x", 0.0)), float(deck.get("y", 0.0))
    sx, sy = float(deck.get("size_x", 0.0)), float(deck.get("size_y", 0.0))
    isl = []
    for v in volumes or ():
        if not str(v.get("name", "")).startswith(_PUMP_ISLAND):
            continue
        vx, vy = float(v.get("x", 0.0)), float(v.get("y", 0.0))
        if abs(vx - cx) > sx / 2.0 or abs(vy - cy) > sy / 2.0:
            continue          # another forecourt's island
        isl.append(v)
    if not isl:
        return []
    # the islands run along y when they are longer in y: the lanes do too,
    # and are spaced across x
    along_y = sum(float(v.get("size_y", 0.0)) - float(v.get("size_x", 0.0)) for v in isl) >= 0
    if along_y:
        lo, hi, c_al, len_al = cx - sx / 2.0, cx + sx / 2.0, cy, sy
        spans = sorted((float(v["x"]) - float(v.get("size_x", 0.0)) / 2.0,
                        float(v["x"]) + float(v.get("size_x", 0.0)) / 2.0) for v in isl)
    else:
        lo, hi, c_al, len_al = cy - sy / 2.0, cy + sy / 2.0, cx, sx
        spans = sorted((float(v["y"]) - float(v.get("size_y", 0.0)) / 2.0,
                        float(v["y"]) + float(v.get("size_y", 0.0)) / 2.0) for v in isl)
    edges = [lo] + [e for a, b in spans for e in (a, b)] + [hi]
    gaps = [(edges[k], edges[k + 1]) for k in range(0, len(edges), 2)]
    gaps = [(a, b) for a, b in gaps if b - a >= _CANOPY_LANE_MIN]
    if len(gaps) > _CANOPY_WASH_MAX:
        keep = [round(k * (len(gaps) - 1) / (_CANOPY_WASH_MAX - 1.0))
                for k in range(_CANOPY_WASH_MAX)]
        gaps = [gaps[k] for k in sorted(set(keep))]
    out = []
    for a, b in gaps:
        mid, w = (a + b) / 2.0, b - a
        if along_y:
            out.append((mid, c_al, [round(w, 3), round(len_al, 3)]))
        else:
            out.append((c_al, mid, [round(len_al, 3), round(w, 3)]))
    return out


def _canopy_anchors(volumes):'''

TEST = '''"""The canopy's washes hang over the lanes (0.167.0).

Cold run 9120, finding 4: under the canopy the pump stood in shadow beside a
lit patch. The washes were spread evenly along the deck and on
gas_station_a02 landed within 1.33 m of the islands; a pump's faces face its
lanes. Held: with islands under the deck, one wash a lane, over the lane's
centre and never over an island; the gaps too narrow to drive are not lanes;
the islands' long axis decides which way the lanes run; too many lanes are
capped; another forecourt's islands do not count; and with no islands the
even spread is unchanged.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import lights  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
DECK = {"name": "canopy_roof", "x": 0.0, "y": -22.0, "z": 5.0, "size_x": 22.0, "size_y": 13.0,
        "size_z": 0.4}
COLS = [{"name": "canopy_col_%d" % i, "x": x, "y": y, "z": 2.5, "size_x": 0.5, "size_y": 0.5,
         "size_z": 5.0} for i, (x, y) in enumerate(((-8, -27), (0, -27), (8, -27), (-8, -17),
                                                    (0, -17), (8, -17)))]
ISLANDS = [{"name": "pump_island_%d" % i, "x": x, "y": -22.0, "z": 0.15, "size_x": 1.6,
            "size_y": 8.0, "size_z": 0.3} for i, x in enumerate((-6.0, 0.0, 6.0), 1)]


def _washes(vols):
    return [a for a in lights._canopy_anchors(vols) if a["type"] == "canopy_wash"]


def test_one_wash_a_lane_over_the_lane_and_never_over_an_island():
    w = _washes([DECK] + COLS + ISLANDS)
    xs = sorted(a["pos"][0] for a in w)
    assert xs == [-8.9, -3.0, 3.0, 8.9], xs
    for a in w:
        assert a["pos"][1] == -22.0
        for i in ISLANDS:                       # clear of every island
            assert abs(a["pos"][0] - i["x"]) >= i["size_x"] / 2.0 + lights._CANOPY_LANE_MIN / 2.0 - 1e-9
    assert {tuple(a["size"]) for a in w} == {(4.2, 13.0), (4.4, 13.0)}


def test_a_gap_too_narrow_to_drive_is_not_a_lane():
    tight = [dict(i, x=x) for i, x in zip(ISLANDS, (-2.0, 0.0, 6.0))]   # 0.4 m between two
    xs = sorted(a["pos"][0] for a in _washes([DECK] + COLS + tight))
    assert all(not (-1.2 < x < -0.8) for x in xs), xs


def test_islands_along_x_put_the_lanes_along_x():
    deck = dict(DECK, size_x=13.0, size_y=22.0, y=0.0)
    isl = [dict(i, x=0.0, y=y, size_x=8.0, size_y=1.6) for i, y in zip(ISLANDS, (-6.0, 0.0, 6.0))]
    w = _washes([deck] + isl)
    assert sorted(a["pos"][1] for a in w) == [-8.9, -3.0, 3.0, 8.9]
    assert {a["pos"][0] for a in w} == {0.0}


def test_too_many_lanes_are_capped():
    deck = dict(DECK, size_x=60.0)
    isl = [dict(ISLANDS[0], name="pump_island_%d" % k, x=x)
           for k, x in enumerate((-24.0, -16.0, -8.0, 0.0, 8.0, 16.0, 24.0))]
    w = _washes([deck] + isl)
    assert len(w) == lights._CANOPY_WASH_MAX
    xs = sorted(a["pos"][0] for a in w)
    assert xs[0] < -24 and xs[-1] > 24            # the outermost lanes are kept


def test_another_forecourt_s_islands_do_not_count():
    far = [dict(i, x=i["x"] + 200.0) for i in ISLANDS]
    assert len(_washes([DECK] + COLS + far)) == len(_washes([DECK] + COLS))


def test_no_islands_keeps_the_even_spread():
    xs = sorted(a["pos"][0] for a in _washes([DECK] + COLS))
    n = len(xs)
    step = DECK["size_x"] / n
    assert xs == [round(-DECK["size_x"] / 2 + step * (k + 0.5), 3) for k in range(n)] or \\
        all(abs(a - b) < 1e-6 for a, b in zip(xs, [-DECK["size_x"] / 2 + step * (k + 0.5)
                                                   for k in range(n)]))


def test_the_gas_station_s_washes_are_over_its_lanes():
    spec = json.load(open(os.path.join(HERE, "specs", "gas_station_a02.json"), encoding="utf-8"))
    vols = spec.get("volumes") or []
    w = _washes(vols)
    islands = [v for v in vols if str(v["name"]).startswith("pump_island")]
    assert len(w) == 4 and len(islands) == 3
    for a in w:
        for i in islands:
            assert abs(a["pos"][0] - i["x"]) > i["size_x"] / 2.0, (a["pos"], i["name"])
'''


def main():
    t = DC / "test_canopy_lanes.py"
    assert not t.exists(), "already applied"
    _edit("lights.py", [(CONST_OLD, CONST_NEW), (WASH_OLD, WASH_NEW), (POOL_OLD, POOL_NEW),
                        (FUNC_OLD, FUNC_NEW)])
    t.write_bytes(TEST.encode("utf-8"))
    print("wrote test_canopy_lanes.py")


if __name__ == "__main__":
    main()
