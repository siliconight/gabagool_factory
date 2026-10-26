"""Lot 0.131.0 on a CLONE (<repo>): no parking where the bus pulls in (the walker's walk of cold run 9386, finding 10:
"bus stop sign is for cars/buses so there is no parking ther"). Anchored; refuses on a miss.

    python edit_lot_bus_zone.py <repo>
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


edit("site_streets.py", [
    ("""    gaps: list = field(default_factory=list)

    @property
    def centre(self):""",
     """    gaps: list = field(default_factory=list)
    #: Stretches of a kerb's parking lane no car may use (0.131.0): ``(side, t0,
    #: t1)``, a bus stop's zone (`site_furniture.BUS_ZONE_M`). Set by
    #: `plan_furniture` as it stands a stop, and by `roads` from the spec's
    #: ``bus_zones`` after it, so every reader of `bays` sees the same lane.
    no_parking: list = field(default_factory=list)

    @property
    def centre(self):"""),
    ("""    \"\"\"Every parking bay on ``road``: dicts of side, index, t0, t1 (along)
    and offset (across, to the lane's centre). Bays step from the road's
    start; a stretch within `CROSSING_SETBACK` of a centre-line crossing, or
    over a kerb cut, holds none.\"\"\"""",
     """    \"\"\"Every parking bay on ``road``: dicts of side, index, t0, t1 (along)
    and offset (across, to the lane's centre). Bays step from the road's
    start; a stretch within `CROSSING_SETBACK` of a centre-line crossing, or
    over a kerb cut, holds none -- nor one a ``road.no_parking`` zone
    overlaps on its side (0.131.0, a bus stop): no car, no meter, no paint.\"\"\""""),
    ("""            if any(not (t1 <= a or t0 >= b) for a, b in keep_out + cuts):
                continue
            out.append({"side": kerb.side, "index": i, "t0": t0, "t1": t1,""",
     """            if any(not (t1 <= a or t0 >= b) for a, b in keep_out + cuts):
                continue
            if any(side == kerb.side and not (t1 <= a or t0 >= b)
                   for side, a, b in road.no_parking):
                continue
            out.append({"side": kerb.side, "index": i, "t0": t0, "t1": t1,"""),
    ("""        out.append(road)
    for road in out:""",
     """        # a bus stop's zone, as `plan_furniture` stood it (0.131.0)
        road.no_parking = [(z["side"], float(z["t0"]), float(z["t1"]))
                           for z in site_spec.get("bus_zones", []) or [] if z.get("road") == i]
        out.append(road)
    for road in out:"""),
])

edit("site_furniture.py", [
    ("""def _bus_stop(road, kerb, placed, n, markers=()):""",
     """#: NO PARKING WHERE THE BUS PULLS IN (0.131.0). The walker, walking cold run
#: 9386, of the stop's flag: "bus stop sign is for cars/buses so there is no
#: parking ther". NACTO's minimum length for a 40 ft bus's curbside stop,
#: midblock -- the bus and its merge in and out -- is 120 ft; Lot stands a stop
#: at the middle of a kerb's longest free stretch, so midblock
#: (`docs/STREET_RULES.md`, "Bus stops", at the factory root). The zone is
#: centred on the shelter, and no bay it overlaps holds a car, a meter or paint.
BUS_ZONE_M = round(120 * 0.3048, 4)


def bus_zones(roads_list) -> list:
    \"\"\"The stops' zones `plan_furniture` stood on ``roads_list``, as the spec
    keeps them: ``{"road", "side", "t0", "t1"}``.\"\"\"
    return [{"road": r.index, "side": s, "t0": round(a, 3), "t1": round(b, 3)}
            for r in roads_list for s, a, b in r.no_parking]


def _bus_stop(road, kerb, placed, n, markers=()):"""),
    ("""                placed.extend(stop)
                out.extend(_stop_corner(road, kerb, stop, placed, markers))""",
     """                placed.extend(stop)
                out.extend(_stop_corner(road, kerb, stop, placed, markers))
                # its zone, before the poles and the meters read the bays
                if stop:
                    t = stop[0]["t"]
                    road.no_parking.append((kerb.side, t - BUS_ZONE_M / 2.0,
                                            t + BUS_ZONE_M / 2.0))"""),
])

edit("lot.py", [
    ("""    site_spec.setdefault("cover", []).extend(furniture)
""",
     """    site_spec.setdefault("cover", []).extend(furniture)
    # NO PARKING WHERE THE BUS PULLS IN (0.131.0): the stops' zones go into the
    # spec, so the parking and the paint, which read the roads afresh, keep the
    # same lanes clear (`site_furniture.BUS_ZONE_M`)
    site_spec["bus_zones"] = site_furniture.bus_zones(_furniture_roads)
    if site_spec["bus_zones"]:
        print(f"[lot] LOT_BUS_ZONES: {len(site_spec['bus_zones'])} stop(s), "
              f"{site_furniture.BUS_ZONE_M} m of kerb each kept clear of parking")
    # the getaway van was stood before the stops: say so if it stands in a zone
    if getaway is not None:
        _van = getaway["van"]
        for _z in site_spec["bus_zones"]:
            _r = _furniture_roads[_z["road"]]
            _t = ((_van["at"][0] - _r.a[0]) * _r.along[0] + (_van["at"][1] - _r.a[1]) * _r.along[1])
            _s = (_van["at"][0] - _r.a[0]) * _r.perp[0] + (_van["at"][1] - _r.a[1]) * _r.perp[1]
            if _z["t0"] <= _t <= _z["t1"] and (_s > 0) == (_z["side"] == "L") \\
                    and abs(_s) <= _r.width / 2.0 + 1e-6:
                print(f"[lot] LOT_GETAWAY_IN_BUS_ZONE: the getaway van stands in road "
                      f"{_z['road']}'s stop zone ({_z['side']} {_z['t0']}..{_z['t1']})")
"""),
])

TEST = '''"""No parking where the bus pulls in (0.131.0): a stop's zone, `BUS_ZONE_M` of kerb centred on its shelter, holds no
bay -- so no car, no meter, no paint -- on its side only. The walker, walking cold run 9386: "bus stop sign is for
cars/buses so there is no parking ther". FAILS ON 0.130.0."""
import site_furniture
import site_streets


def _street():
    return {"roads": [{"a": [-60.0, 0.0], "b": [60.0, 0.0], "width": 10.0, "sidewalk": 3.0}], "buildings": [],
            "paths": []}


def test_a_zone_empties_the_bays_it_overlaps_on_its_side_only():
    spec = _street()
    road = site_streets.roads(spec)[0]
    before = site_streets.bays(road)
    assert before, "the probe street has no bays: not a test"
    spec["bus_zones"] = [{"road": 0, "side": "L", "t0": 40.0, "t1": 40.0 + site_furniture.BUS_ZONE_M}]
    road = site_streets.roads(spec)[0]
    after = site_streets.bays(road)
    gone = [b for b in before if b not in after]
    assert gone and all(b["side"] == "L" and b["t1"] > 40.0 and b["t0"] < 40.0 + site_furniture.BUS_ZONE_M
                        for b in gone), gone
    assert [b for b in before if b["side"] == "R"] == [b for b in after if b["side"] == "R"]


def test_the_zone_is_nactos_midblock_length():
    assert abs(site_furniture.BUS_ZONE_M - 36.576) < 1e-9


def test_furniture_records_a_stops_zone_and_stands_no_meter_in_it():
    spec = _street()
    spec["buildings"] = [{"id": "b0", "at": [0.0, 20.0], "rot": 0, "footprint": [30.0, 20.0]}]
    roads = site_streets.roads(spec)
    pieces = site_furniture.plan_furniture(roads, spec["buildings"])
    shelters = [p for p in pieces if p["species"] == "bus_shelter"]
    zones = site_furniture.bus_zones(roads)
    assert len(shelters) == len(zones) >= 1, (shelters, zones)
    z = zones[0]
    assert abs((z["t0"] + z["t1"]) / 2.0 - shelters[0]["t"]) < 1e-3
    meters = [p for p in pieces if p["species"] == "parking_meter" and p["kerb"] == z["side"]]
    assert not [m for m in meters if z["t0"] <= m["t"] <= z["t1"]], meters
'''
(R / "tests" / "test_bus_zone.py").write_text(TEST, encoding="utf-8", newline="\n")
print("bus stop zones: site_streets.no_parking, site_furniture.BUS_ZONE_M / bus_zones, lot.py; tests/test_bus_zone.py")
