"""Lot 0.128.0 on a CLONE (<repo>): a signalised junction faces every approach (the walker's walk of cold run 9386,
finding 12: "where are the traffic lights for this side of the road?"). Anchored; refuses on a miss.

    python edit_lot_far_signals.py <repo>
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


edit("site_furniture.py", [
    ('''#: Where the 1990s kit stands, and why.
#:   traffic_signal: on the corner of a signalised junction (a yielding
#:                   road meets an arterial, `site_streets.approaches`),
#:                   pole on the yielding leg's right-hand kerb, mast arm
#:                   over the road it meets''',
     '''#: Where the 1990s kit stands, and why.
#:   traffic_signal: ONE PER APPROACH of a signalised junction (a yielding
#:                   road meets an arterial, `site_streets.approaches`), on
#:                   the FAR side: its pole beyond the junction on the
#:                   approach's right, its arm back over the approach's lanes,
#:                   both heads facing the driver (0.128.0, `_far_signal`)'''),
    ('''SIGNAL_SETBACK = 0.4
''',
     '''SIGNAL_SETBACK = 0.4
#: A SIGNALISED APPROACH SEES TWO FACES BEYOND THE JUNCTION (0.128.0). MUTCD
#: 2009 4D.14 (quoted in the Delaware Administrative Code's copy; FHWA
#: interpretation 4-358): at least two primary faces for an approach's through
#: movement, at least 8 ft apart, at least one of them no less than 40 ft and
#: no more than 180 ft beyond the stop line. Zoo's `traffic_signal` carries
#: two heads 4.3 m apart, the arm's and the pole's, so one far-side signal an
#: approach is the rule; nearer than this to the stop line is said.
SIGNAL_MIN_BEYOND = 40 * 0.3048
'''),
    ('''def plan_traffic_control(road, roads_list, markers=(), findings=None,
                         placed=()) -> list:
    """The signal or the stop signs on every approach ``road`` makes to a
    junction (`site_streets.approaches`). ``placed`` are pieces already
    standing, which a stop sign keeps clear of; ``findings`` (a list of
    strings) hears about an approach whose control could not be stood by
    the rules."""''',
     '''def _far_signal(road, ap, roads_list, name, findings):
    """THE FAR-SIDE SIGNAL for approach ``ap`` (0.128.0), or None (and a
    finding).

    The walker, walking cold run 9386: "where are the traffic lights for this
    side of the road?" Until this a signal stood only on a junction's
    yielding leg, its pole at the leg's mouth and its heads facing ACROSS
    the leg -- one direction of the road it meets was served, the yielding
    driver and the other direction were not (measured on 9386's walk copy:
    both signals' heads faced west).

    Every approach now gets its own, by `SIGNAL_MIN_BEYOND`'s rule: the pole
    beyond the junction box on the approach's RIGHT, `CURB_SIGN_OFFSET` plus
    the pole's half off the curb face, its arm turned back over the
    approach's lanes and its heads facing the driver -- Zoo's `right` form,
    whose heads face the arm turned counter-clockwise. Where the road runs
    on past the box the pole stands on its own right band; where it ends on
    the road it meets (a T's stem) it stands on THAT road's far band, in
    line with the approach's right kerb. On a four-way each corner is the
    far-right corner of one approach, so one post a corner holds."""
    import site_streets
    by = {r.index: r for r in roads_list}
    crosser = by.get(ap.crosser)
    cut = next((c for c in road.crossings if c.kind == "road" and c.crosser == ap.crosser
                and abs(c.t - ap.station) < 1e-6), None)
    if crosser is None or cut is None:
        return None
    lo, hi = site_streets.crossing_box(cut)
    far = (hi if ap.travel > 0 else lo) + ap.travel * SIGNAL_SETBACK
    tx, ty = ap.travel * road.along[0], ap.travel * road.along[1]
    arm = (-ty, tx)                   # the driver's left: back over the lanes
    inset = CURB_SIGN_OFFSET + FOOTPRINT["traffic_signal"][0] / 2.0
    who = (f"road {road.index}'s {'+t' if ap.travel > 0 else '-t'} approach to "
           f"road {ap.crosser}")
    if road.sidewalk and road.slab[0] + 0.5 < far < road.slab[1] - 0.5:
        host = road
        kerb = road.kerb(site_streets.right_side(ap.travel))
        t = far
    else:
        if not crosser.sidewalk:
            _say(findings,
                 f"LOT_SIGNAL_NO_FAR_BAND: {who} ends on road {ap.crosser}, which has no "
                 f"sidewalk band beyond it to stand its signal on; nothing is placed.")
            return None
        px, py = road.point(ap.station)
        s0 = (px - crosser.a[0]) * crosser.along[0] + (py - crosser.a[1]) * crosser.along[1]
        right = (ty, -tx)
        t = s0 + (road.width / 2.0 + inset) * (right[0] * crosser.along[0] + right[1] * crosser.along[1])
        across = tx * crosser.perp[0] + ty * crosser.perp[1]
        host = crosser
        kerb = crosser.kerb("L" if across > 0 else "R")
        if not (crosser.slab[0] + 0.5 < t < crosser.slab[1] - 0.5):
            _say(findings,
                 f"LOT_SIGNAL_NO_FAR_BAND: {who}'s far-side signal would stand at "
                 f"{t:.2f} m along road {ap.crosser}, off its slab; nothing is placed.")
            return None
    offset = kerb.offset - kerb.sign * (host.sidewalk / 2.0 - inset)
    yaw_extra = math.degrees(math.atan2(arm[1], arm[0])) - host.angle_deg
    piece = _piece(name, "traffic_signal", host, kerb, t, offset, yaw_extra,
                   breaks=f"junction@{ap.station:.1f}")
    piece["form"] = "right"
    sx, sy = road.point(ap.line)
    beyond = (piece["at"][0] - sx) * tx + (piece["at"][1] - sy) * ty
    if beyond < SIGNAL_MIN_BEYOND - 1e-6:
        _say(findings,
             f"LOT_SIGNAL_NEAR_STOP_LINE: {who}'s signal stands {beyond:.2f} m beyond "
             f"its stop line, under the {SIGNAL_MIN_BEYOND:.2f} m (40 ft) the MUTCD asks "
             f"of one of its two faces.")
    return piece


def plan_traffic_control(road, roads_list, markers=(), findings=None,
                         placed=()) -> list:
    """The signal or the stop signs on every approach ``road`` makes to a
    junction (`site_streets.approaches`). ``placed`` are pieces already
    standing, which a stop sign keeps clear of; ``findings`` (a list of
    strings) hears about an approach whose control could not be stood by
    the rules. A signal may stand on ANOTHER road's band (`_far_signal`: a
    T's stem is faced from the road it ends on), and says so in its own
    ``road`` and ``kerb``."""'''),
    ('''        if ap.control == "through" or (ap.control == "signal" and not ap.minor):
            # the through road keeps its right of way; at a signal, the
            # pole on the yielding leg's corner carries the arm over it
            continue''',
     '''        if ap.control == "through":
            # the through road of a stop-controlled junction keeps its right
            # of way; at a signal every approach is faced (0.128.0)
            continue'''),
    ('''        kerb = road.kerb(side)
        if ap.control == "signal":
            # the pole on the corner, the mast arm reaching over the road
            # it meets -- which is the direction of the mouth
            pole_t = ap.mouth - ap.travel * SIGNAL_SETBACK
            offset = kerb.offset + kerb.sign * (road.sidewalk / 2.0 - BAND_INSET)
            yaw_extra = 0.0 if ap.travel > 0 else 180.0
            piece = _piece(f"Signal_{road.index}{side}{tag}", "traffic_signal", road,
                           kerb, pole_t, offset, yaw_extra,
                           breaks=f"junction@{ap.station:.1f}")
            if _clear_of_markers(piece, markers):
                out.append(piece)
            continue''',
     '''        if ap.control == "signal":
            piece = _far_signal(road, ap, roads_list, f"Signal_{road.index}{side}{tag}",
                                findings)
            if piece is not None and _clear_of_markers(piece, markers):
                out.append(piece)
            continue
        kerb = road.kerb(side)'''),
    ('''    controls, every_control = {}, []
    for road in roads_list:
        controls[road.index] = plan_traffic_control(road, roads_list, markers,
                                                    findings, every_control)
        every_control.extend(controls[road.index])
    for road in roads_list:
        for p in controls[road.index]:
            station = _junction_station(road, p)
            if station is not None:
                corner_posts.add(corner_key(road, station, p["at"]))''',
     '''    controls, every_control = {}, []
    for road in roads_list:
        every_control.extend(plan_traffic_control(road, roads_list, markers,
                                                  findings, every_control))
    # BY THE ROAD EACH STANDS ON, not the road that asked for it: a T's stem
    # is faced by a signal on the road it ends on (0.128.0, `_far_signal`)
    for road in roads_list:
        controls[road.index] = [p for p in every_control if p["road"] == road.index]
    for road in roads_list:
        for p in controls[road.index]:
            station = _junction_station(road, p)
            if station is not None:
                corner_posts.add(corner_key(road, station, p["at"]))'''),
])
edit("tests/test_site_furniture.py", [
    ('''    through, side = site_streets.roads(tee)
    control = site_furniture.plan_traffic_control(side, [through, side])
    assert [p["species"] for p in control] == ["traffic_signal"]
    (sig,) = control
    # the pole stands back up the leg from its mouth, on the band
    assert sig["at"][0] != 0.0 or sig["at"][1] > 0
    assert abs(sig["at"][1] - (site_furniture.SIGNAL_SETBACK + 8.0)) < 1e-6
    assert sig["size"] == [0.7, 6.5, 0.7]          # the box is the pole
    assert sig["dims"] == [8.0, 0.62, 6.5]         # the slot is the reach''',
     '''    through, side = site_streets.roads(tee)
    control = site_furniture.plan_traffic_control(side, [through, side])
    assert [p["species"] for p in control] == ["traffic_signal"]
    (sig,) = control
    # the stem is faced from the FAR side (0.128.0): on the through road's band
    # beyond the junction, in line with the stem's right kerb
    assert sig["road"] == through.index and sig["at"][1] < 0
    assert sig["size"] == [0.7, 6.5, 0.7]          # the box is the pole
    assert sig["dims"] == [8.0, 0.62, 6.5]         # the slot is the reach'''),
    ('''    # the through road ends on nothing, so it carries no control
    assert site_furniture.plan_traffic_control(through, [through, side]) == []''',
     '''    # the through road's two approaches are faced too (0.128.0), each beyond the box on its right
    both = site_furniture.plan_traffic_control(through, [through, side])
    assert [p["species"] for p in both] == ["traffic_signal"] * 2
    assert all(p["road"] == through.index for p in both)'''),
    ('''def test_the_bus_stop_flag_stands_at_the_curb():''',
     '''def _tee():
    return {"name": "tee", "ground": {"size_x": 140, "size_y": 120}, "buildings": [],
            "roads": [{"a": [-60, 0], "b": [60, 0], "width": 10, "sidewalk": 3},
                      {"a": [0, 0], "b": [0, 50], "width": 10, "sidewalk": 3}]}


def test_every_approach_of_a_signalised_junction_is_faced_from_its_far_right():
    """The walker, walking cold run 9386: "where are the traffic lights for this side of the road?" -- a signal
    stood only on the yielding leg, facing across it. Every approach of the tee's signalised junction -- the stem and
    both directions of the through road -- now has a signal whose heads face its driver (Zoo's `right` form: the arm
    along the yaw, the face the arm turned counter-clockwise), standing on the driver's right, beyond the junction,
    at least 40 ft past the stop line (MUTCD 4D.14). FAILS ON 0.127.0: one signal, facing across the stem."""
    import math
    import site_streets
    roads = site_streets.roads(_tee())
    findings = []
    signals = [p for r in roads for p in site_furniture.plan_traffic_control(r, roads, findings=findings)
               if p["species"] == "traffic_signal"]
    aps = [a for a in site_streets.approaches(roads) if a.control == "signal"]
    assert len(aps) == 3 and len(signals) == 3, (len(aps), [s["name"] for s in signals])
    assert not [f for f in findings if "NEAR_STOP_LINE" in f], findings
    by = {r.index: r for r in roads}
    for ap in aps:
        road = by[ap.road]
        t = (ap.travel * road.along[0], ap.travel * road.along[1])
        stop = road.point(ap.line)
        faced = []
        for s in signals:
            assert s["form"] == "right"
            yaw = math.radians(s["yaw"])
            arm = (math.cos(yaw), math.sin(yaw))
            face = (-arm[1], arm[0])                  # the right form: the arm turned counter-clockwise
            rel = (s["at"][0] - stop[0], s["at"][1] - stop[1])
            beyond = rel[0] * t[0] + rel[1] * t[1]
            right_of = rel[0] * t[1] - rel[1] * t[0]  # > 0 on the driver's right
            if face[0] * t[0] + face[1] * t[1] < -0.99 and right_of > 0 and beyond > 0:
                faced.append((s["name"], round(beyond, 2)))
        assert len(faced) == 1, (ap, faced)
        assert faced[0][1] >= site_furniture.SIGNAL_MIN_BEYOND, (ap, faced)


def test_the_bus_stop_flag_stands_at_the_curb():'''),
])
edit("tests/test_street_rules.py", [
    ('''    assert not [p for p in pieces if p["species"] == "stop_sign"]
    assert [p["species"] for p in pieces if p["species"] == "traffic_signal"] == ["traffic_signal"]''',
     '''    assert not [p for p in pieces if p["species"] == "stop_sign"]
    # a T under a signal: one far-side signal for each of its three approaches (0.128.0)
    assert [p["species"] for p in pieces if p["species"] == "traffic_signal"] == ["traffic_signal"] * 3'''),
])
edit("tests/test_urban_street_trees.py", [
    ('''    for kerb in roads[0].kerbs:
        row = [p["t"] for p in trees if p["kerb"] == kerb.side]
        stations = site_furniture.urban_tree_stations(roads[0], kerb)
        assert row == [round(s, 3) for s in stations], (kerb.side, row, stations)   # `_piece` keeps t to 3 places''',
     '''    for kerb in roads[0].kerbs:
        row = [p["t"] for p in trees if p["kerb"] == kerb.side]
        stations = site_furniture.urban_tree_stations(roads[0], kerb)
        # every tree on its station, or one `NUDGES` step off it clear of a junction's far-side signal pole
        # (0.128.0: a pole beyond the box stands 1.1 m from the station at 172.296 here, so that tree steps -2 m)
        signals = [p["t"] for p in urban if p["species"] == "traffic_signal" and p["road"] == roads[0].index
                   and p["kerb"] == kerb.side]
        assert len(row) == len(stations), (kerb.side, row, stations)
        for got, want in zip(row, stations):
            want = round(want, 3)                  # `_piece` keeps t to 3 places
            if got != want:
                assert round(abs(got - want), 3) in site_furniture.NUDGES, (kerb.side, got, want)
                assert any(abs(s - want) < 2.0 for s in signals), (kerb.side, got, want, signals)'''),
])
(R / "VERSION").write_bytes(b"Lot 0.128.0")
print("site_furniture: a far-side signal for every approach; tests; VERSION")
