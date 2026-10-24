"""Lot 0.127.0 on a CLONE (<repo>): a bus stop's flag stands at the curb (the walker's walk of cold run 9386,
finding 10: "bus stop sign is for cars/buses so there is no parking ther...so it sohuld be closer to the road").
Anchored; refuses on a miss.

    python edit_lot_bus_flag.py <repo>
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
    ('''SIGN_BEFORE_SHELTER = 1.0
''',
     '''SIGN_BEFORE_SHELTER = 1.0
#: A SIGN ON A CURBED STREET STANDS 2 FT FROM THE CURB FACE to its nearest edge:
#: PennDOT LTAP Tech Sheet 181, the urban lateral offset (1 ft where space is
#: limited), the MUTCD's curbed-street minimum. A bus stop's flag speaks to the
#: bus and to whoever would park there, so it stands at the curb and not at the
#: back of the walk (0.127.0; the walker, walking cold run 9386: "it sohuld be
#: closer to the road"). The stop signs answer the walker's 6 ft rule
#: (`STOP_LATERAL_MIN`) instead, which `docs/STREET_RULES.md` records.
CURB_SIGN_OFFSET = 2 * 0.3048
'''),
    ('''    """The stop as a set -- shelter, bench inside it, sign before it -- at
    the midpoint of the longest free stretch of ``kerb`` that holds it clear
    of the cuts and of what already stands; nudged along in 3 m steps when
    a lamp or a tree is in the way. Returns the pieces (possibly none)."""
    sw, sd, _sh = SPECIES["bus_shelter"]
    sign_w, sign_d, _ = SPECIES["sign_post"]
    outer = kerb.offset + kerb.sign * (road.sidewalk / 2.0 - BAND_INSET)
''',
     '''    """The stop as a set -- shelter, bench inside it, its flag before it at
    the curb -- at the midpoint of the longest free stretch of ``kerb`` that
    holds it clear of the cuts and of what already stands; nudged along in 3
    m steps when a lamp or a tree is in the way. Returns the pieces (possibly
    none).

    THE FLAG AT THE CURB (0.127.0): turned to face along the road, its
    plate's width runs across the walk, so its post stands
    `CURB_SIGN_OFFSET` plus half that width in from the curb face. It stood
    `BAND_INSET` in from the band's BACK edge until then, beside the
    buildings' walls and doors."""
    sw, sd, _sh = SPECIES["bus_shelter"]
    sign_w, sign_d, _ = SPECIES["sign_post"]
    flag_off = kerb.offset - kerb.sign * (road.sidewalk / 2.0 - CURB_SIGN_OFFSET
                                          - BLADE_DIMS[BLADE_AT_BUS_STOP][0] / 2.0)
'''),
    ('''                      _piece(f"StopFlag_{n + 2}", "sign_post", road, kerb, sign_t,
                             outer, 90.0, breaks=tag, blade=BLADE_AT_BUS_STOP)]''',
     '''                      _piece(f"StopFlag_{n + 2}", "sign_post", road, kerb, sign_t,
                             flag_off, 90.0, breaks=tag, blade=BLADE_AT_BUS_STOP)]'''),
])
edit("tests/test_site_furniture.py", [
    ('''    # without buildings there is no facing kerb and no stop
    assert not [p for p in site_furniture.plan_furniture(roads) if p["species"] == "bus_shelter"]
''',
     '''    # without buildings there is no facing kerb and no stop
    assert not [p for p in site_furniture.plan_furniture(roads) if p["species"] == "bus_shelter"]


def test_the_bus_stop_flag_stands_at_the_curb():
    """The flag's plate, turned to face along the road, has its near edge `CURB_SIGN_OFFSET` (2 ft, PennDOT TS 181)
    from the curb face -- the walker, walking cold run 9386: "it sohuld be closer to the road" -- and stands nearer
    the road than the shelter."""
    assert abs(site_furniture.CURB_SIGN_OFFSET - 0.6096) < 1e-9
    spec = _probe()
    roads = site_streets.roads(spec)
    pieces = site_furniture.plan_furniture(roads, spec["buildings"])
    (flag,) = [p for p in pieces if p["species"] == "sign_post" and p["breaks"].startswith("stop@")]
    (shelter,) = [p for p in pieces if p["species"] == "bus_shelter"]
    road = roads[0]
    plate_w = site_furniture.BLADE_DIMS[site_furniture.BLADE_AT_BUS_STOP][0]
    curb = road.width / 2.0
    near_edge = abs(flag["at"][1]) - plate_w / 2.0 - curb
    assert abs(near_edge - site_furniture.CURB_SIGN_OFFSET) < 1e-3, (flag["at"], curb)
    assert abs(flag["at"][1]) < abs(shelter["at"][1])
'''),
])
(R / "VERSION").write_bytes(b"Lot 0.127.0")
print("site_furniture: the bus stop flag at the curb; test; VERSION")
