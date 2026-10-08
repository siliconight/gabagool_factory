"""Lot 0.100.0: the responders' cruiser is Zoo's, and its lane steers round
what stands in it (roadmap 212).

Zoo 1.86.0 built the cruiser the walker asked for, so `site_responders`
pins its slot (2.196 x 5.545 x 1.578: mirror heads, push bar to rear
bumper, light bar) and measures a stop's door room from its body and a
lane from its mirrors. Alone that widens the lane box from 3.0 to 3.196 m
and makes cold run 9204's lost arrival worse: the getaway van's mirrors
stood 0.45 m into road 0's eastern lane, and a rigid lane cannot pass
them. So the lane now steers: `STATION_STEP` slices, each shifted toward
and across the centre line as far as it must, tapered at the MUTCD
shifting-taper rate, back in its own half by the stop, written as
`lane_boxes`. Level Factory 0.161.0 ships them; an older Level Factory
cannot read this Lot's arrivals.

Anchored edits (every anchor once; refuses on a miss; nothing is written
until every anchor in every file matched):
- `site_responders.py`: the vehicle, `MIRROR_OUT`, the steering constants,
  `shift_limit`, `_needs`, `steer`, `_lane`; `_best_stop`, `plan`,
  `keep_out` and `blocked` read the lane as boxes.
- `tests/test_site_responders.py`: the lane as boxes, the control moved to
  cold run 9204's car, and four tests more.
New file from `lot_responder_lane/`: `tests/fixtures/club_block_014_seed_9181.site.json`,
cold run 9204's input site with its cover as drawn.
CHANGELOG and VERSION from `lot_responder_lane/CHANGELOG_0.100.0.md`.

    python patch_lot_responder_lane.py
    LOT_ROOT=<copy> python patch_lot_responder_lane.py
"""
import os
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
LOT = pathlib.Path(os.environ.get("LOT_ROOT") or HERE.parent / "lot")
SRC = HERE / "lot_responder_lane"

NEW = {
    pathlib.Path("tests") / "fixtures" / "club_block_014_seed_9181.site.json":
        "club_block_014_seed_9181.site.json",
}

#: site_responders.py, as applied by the scratch edit and tested there.
RESPONDERS = [
    # --- the module docstring: the lane steers ---------------------------------------
    ("""- **The lane:** the inbound driving lane from the entry to the stop -- the
  half of the carriageway a driver arriving from that end keeps to
  (`site_streets.KEEP_RIGHT`), the vehicle's width and `LANE_MARGIN` either
  side. No cover may stand in it.
""",
     """- **The lane:** the inbound driving lane from the entry to the stop -- the
  half of the carriageway a driver arriving from that end keeps to
  (`site_streets.KEEP_RIGHT`), the vehicle's width to its mirrors and
  `LANE_MARGIN` either side. Where something stands in it, the lane steers
  toward and across the centre line to pass, as a driver does, tapered by
  `SHIFT_RATE`, and is back in its own half by the stop (0.100.0). It is
  `STATION_STEP` slices, written as the boxes they make. No cover may stand
  in it.
"""),
    # --- the vehicle and the steering constants ----------------------------------------
    ("""#: A 1990s police cruiser's slot: width to the mirrors, length bumper to
#: bumper, height. The Ford Crown Victoria Police Interceptor and the
#: Chevrolet Caprice 9C1 were 1.99-2.0 m wide and 5.39-5.44 m long. STATED,
#: not derived: Zoo has no cruiser species yet (roadmap 212).
VEHICLE = ("cruiser", 2.0, 5.4, 1.5)
#: Room for a door to open, each side. A 1990s sedan's front door is about
#: 1.1 m long; opened to 60 degrees it stands 0.95 m out.
DOOR_ROOM = 1.0
#: Clear road either side of the vehicle in its lane, from entry to stop.
LANE_MARGIN = 0.5
""",
     """#: The responders' cruiser's slot: Zoo 1.86.0's `cruiser` genome defaults --
#: width to the mirror heads, length from the push bar to the rear bumper,
#: height to the light bar's top. Pinned, because Lot does not import Zoo;
#: `tests/test_site_responders.py` reads the genome when Zoo stands beside
#: this repo and fails when the two disagree.
#: 0.99.0 STATED 2.0 x 5.4 x 1.5 before Zoo had a cruiser, and called the
#: 2.0 m a width "to the mirrors": the published 1.99-2.0 m it cited is a
#: Crown Victoria's body, without them.
VEHICLE = ("cruiser", 2.196, 5.545, 1.578)
#: How far a mirror head stands outside the body (Zoo `car_forms.CRUISER`'s
#: `mirror_out`). A door opens from the body, so the stop's door room is
#: measured from it (`VEHICLE`'s width less two of these); the lane, which
#: the mirrors pass along, from the mirror heads.
MIRROR_OUT = 0.105
#: Room for a door to open, each side. A 1990s sedan's front door is about
#: 1.1 m long; opened to 60 degrees it stands 0.95 m out.
DOOR_ROOM = 1.0
#: Clear road either side of the vehicle in its lane, from entry to stop.
LANE_MARGIN = 0.5
#: THE LANE STEERS (0.100.0). A driver meeting a van parked out of its bay
#: moves over toward the centre line, and across it, rather than stopping.
#: 0.99.0's lane was a rigid box at the lane's centre. On cold run 9204 the
#: getaway van's mirrors stood 0.45 m into it and closed road 0's east end
#: (`docs/findings/responder_entry_no_stop/` at the factory root).
#: A shift is tapered, as a driver's is: MUTCD (2009) section 6C.08 puts a
#: shifting taper at L/2, with L = W * S^2 / 60 for speeds of 40 mph or
#: less (W the shift, S the speed in mph, L in W's units). A shift of W so
#: takes W * S^2 / 120 along the road: a rate of 120 / S^2 across per metre
#: along. `SHIFT_SPEED_MPH` is STATED, a residential street's posted speed.
SHIFT_SPEED_MPH = 25.0
SHIFT_RATE = 120.0 / SHIFT_SPEED_MPH ** 2
"""),
    # --- the helpers: the shift a slice needs, and the taper -----------------------------
    ("""def entries(roads_list) -> list:
""",
     """def _interval(rect, road, axis) -> tuple:
    \"\"\"(lo, hi): plan ``rect``'s extent along ``axis`` (the road's `along`
    or `perp`), measured from `road.a` -- its four corners projected, exact.\"\"\"
    vals = [(x - road.a[0]) * axis[0] + (y - road.a[1]) * axis[1]
            for x in (rect[0], rect[2]) for y in (rect[1], rect[3])]
    return min(vals), max(vals)


def shift_limit(road, off: float, width: float) -> float:
    \"\"\"How far a lane of ``width`` centred at ``off`` may shift toward and
    across the centre line: until its far edge meets the oncoming driving
    half's outer edge. The parking lane beyond is the far kerb's, where cars
    stand.\"\"\"
    parking = site_streets.LANE_DEPTH if site_streets.has_parking(road) else 0.0
    return abs(off) + (road.width / 2.0 - parking) - width / 2.0


def _needs(road, travel, off, width, slices, blocking, limit) -> list:
    \"\"\"For each slice ``(t0, t1)``: the least shift toward the centre line at
    which a box ``width`` across, centred ``off`` less that shift, overlaps
    no rect in ``blocking`` -- or None where no shift up to ``limit`` does.

    Each rect beside the slice forbids an open interval of shifts, the ones
    at which the box's across extent overlaps the rect's; the least allowed
    shift is 0, or the top of the chain of intervals that holds it.\"\"\"
    sign = 1.0 if off > 0 else -1.0
    near = [(_interval(r, road, road.along), _interval(r, road, road.perp)) for r in blocking]
    out = []
    for t0, t1 in slices:
        a0, a1 = min(t0, t1), max(t0, t1)
        banned = []
        for (b0, b1), (p0, p1) in near:
            if b1 <= a0 or b0 >= a1:
                continue
            if sign > 0:
                banned.append((off - p1 - width / 2.0, off - p0 + width / 2.0))
            else:
                banned.append((p0 - width / 2.0 - off, p1 + width / 2.0 - off))
        s = 0.0
        moved = True
        while moved:
            moved = False
            for lo, hi in banned:
                if lo < s < hi:
                    s = hi + 1e-6
                    moved = True
        out.append(s if s <= limit else None)
    return out


def steer(needs, rate: float, steps) -> list:
    \"\"\"The shift each slice takes: at least what it needs, and at least what
    any other slice needs less the taper between them, so a shift ramps up
    before what it passes and back down after it, at ``rate`` across per
    metre along. ``steps`` is each slice's length. Then back to 0 at the
    lane's end, where the stop stands in its own half: None when a slice
    must stand further over than the taper from there allows.\"\"\"
    s = list(needs)
    for i in range(1, len(s)):
        s[i] = max(s[i], s[i - 1] - rate * steps[i - 1])
    for i in range(len(s) - 2, -1, -1):
        s[i] = max(s[i], s[i + 1] - rate * steps[i])
    room = 0.0
    for i in range(len(s) - 1, -1, -1):
        if s[i] > room + 1e-9:
            return None
        room += rate * steps[i]
    return s


def entries(roads_list) -> list:
"""),
    # --- _best_stop: the stop from the body, the lane steered -------------------------------
    ("""    _name, w, d, _h = VEHICLE
    off = lane_offset(road, travel)
    lo, hi = road.slab
    junctions = _junctions(road)
    best = None
    t = t_entry + travel * (ENTRY_RUN + d / 2.0)
    while lo + d / 2.0 - 1e-9 <= t <= hi - d / 2.0 + 1e-9:
        rear, front = t - d / 2.0, t + d / 2.0
        stop = _box(road, t, off, d, w + 2.0 * DOOR_ROOM)
        centre = road.point(t, off)
        ok = (not any(not (front <= j0 or rear >= j1) for j0, j1 in junctions)
              and all(math.dist(centre, a) >= site_audit.CAMP_RADIUS for a in anchors)
              and not any(_overlaps(stop, r)
                          for r in list(standing) + list(taken_stops) + list(taken_lanes)))
        if ok:
            t_lane = t - travel * d / 2.0
            lane = _box(road, (t_entry + t_lane) / 2.0, off, abs(t_lane - t_entry),
                        w + 2.0 * LANE_MARGIN)
            if not any(_overlaps(lane, r) for r in list(standing) + list(taken_stops)):
                dist, toward = _to_segment(centre, *way_back)
                key = (round(dist, 6), abs(t - t_entry))
                if best is None or key < best[0]:
                    best = (key, t, centre, stop, lane, dist, toward)
        t += travel * STATION_STEP
    return best
""",
     """    _name, w, d, _h = VEHICLE
    body = w - 2.0 * MIRROR_OUT
    lane_w = w + 2.0 * LANE_MARGIN
    off = lane_offset(road, travel)
    sign = 1.0 if off > 0 else -1.0
    lo, hi = road.slab
    junctions = _junctions(road)
    blocking = list(standing) + list(taken_stops)
    limit = shift_limit(road, off, lane_w)
    # the lane's slices, entry outward, and what each needs -- once for every
    # stop this entry is tried at, each lane being the first of them
    end = hi if travel > 0 else lo
    count = int(math.ceil(abs(end - t_entry) / STATION_STEP - 1e-9))
    grid = [(t_entry + travel * k * STATION_STEP,
             t_entry + travel * min((k + 1) * STATION_STEP, abs(end - t_entry)))
            for k in range(count)]
    needs = _needs(road, travel, off, lane_w, grid, blocking, limit)
    best = None
    t = t_entry + travel * (ENTRY_RUN + d / 2.0)
    while lo + d / 2.0 - 1e-9 <= t <= hi - d / 2.0 + 1e-9:
        rear, front = t - d / 2.0, t + d / 2.0
        stop = _box(road, t, off, d, body + 2.0 * DOOR_ROOM)
        centre = road.point(t, off)
        ok = (not any(not (front <= j0 or rear >= j1) for j0, j1 in junctions)
              and all(math.dist(centre, a) >= site_audit.CAMP_RADIUS for a in anchors)
              and not any(_overlaps(stop, r)
                          for r in list(standing) + list(taken_stops) + list(taken_lanes)))
        lane = _lane(road, t_entry, travel, off, sign, lane_w, t - travel * d / 2.0,
                     grid, needs, blocking) if ok else None
        if lane is not None:
            dist, toward = _to_segment(centre, *way_back)
            key = (round(dist, 6), abs(t - t_entry))
            if best is None or key < best[0]:
                best = (key, t, centre, stop, lane, dist, toward)
        t += travel * STATION_STEP
    return best


def _lane(road, t_entry, travel, off, sign, lane_w, t_lane, grid, needs, blocking):
    \"\"\"The lane from ``t_entry`` to ``t_lane`` (the stop's rear): ``(boxes,
    the largest shift)``, each box a run of slices at one shift -- or None
    when a slice can clear what stands in it at no shift the taper and the
    carriageway allow. Every box is read back against ``blocking``.\"\"\"
    run = abs(t_lane - t_entry)
    slices, need = [], []
    for (t0, t1), n in zip(grid, needs):
        if abs(t0 - t_entry) >= run - 1e-9:
            break
        if n is None:
            return None
        t1 = t_entry + travel * min(abs(t1 - t_entry), run)
        slices.append((t0, t1))
        need.append(n)
    if not slices:
        return None
    shifts = steer(need, SHIFT_RATE, [abs(t1 - t0) for t0, t1 in slices])
    if shifts is None:
        return None
    boxes = []
    i = 0
    while i < len(slices):
        j = i
        while j + 1 < len(slices) and abs(shifts[j + 1] - shifts[i]) < 1e-9:
            j += 1
        a, b = slices[i][0], slices[j][1]
        boxes.append(_box(road, (a + b) / 2.0, off - sign * shifts[i], abs(b - a), lane_w))
        i = j + 1
    if any(_overlaps(box, r) for box in boxes for r in blocking):
        return None
    return boxes, max(shifts)
"""),
    # --- plan(): taken lanes are boxes now, and the record carries them -------------------------
    ("""        _key, t, centre, stop, lane, dist, toward = best
        stops.append(stop)
        lanes.append(lane)
""",
     """        _key, t, centre, stop, (lane, shift), dist, toward = best
        stops.append(stop)
        lanes.extend(lane)
"""),
    ("""            "vehicle": [w, d, h],
            "stop_box": [round(v, 3) for v in stop],
            "lane_box": [round(v, 3) for v in lane],
""",
     """            "vehicle": [w, d, h],
            "stop_box": [round(v, 3) for v in stop],
            "lane_boxes": [[round(v, 3) for v in box] for box in lane],
            "lane_shift": round(shift, 3),
"""),
    # --- keep_out() and blocked() read every lane box ----------------------------------------------
    ("""    return [tuple(a["stop_box"]) for a in arrivals] + [tuple(a["lane_box"]) for a in arrivals]
""",
     """    return ([tuple(a["stop_box"]) for a in arrivals]
            + [tuple(box) for a in arrivals for box in a["lane_boxes"]])
"""),
    ("""    for i, a in enumerate(arrivals):
        for part in ("stop_box", "lane_box"):
            box = tuple(a[part])
            for cv, rect in zip(named, pieces):
                if _overlaps(rect, box):
                    what = cv.get("species") or cv.get("source") or cv.get("name") or "a piece"
                    out.append({
                        "code": "LOT_RESPONDER_BLOCKED", "severity": "major", "category": "spawn",
                        "message": (f"{what} at ({cv['at'][0]:.1f}, {cv['at'][1]:.1f}) stands in "
                                    f"responder arrival {i}'s {part.split('_')[0]} on road "
                                    f"{a['road']}: the lane and the stop were reserved before it "
                                    f"was planned, and a vehicle arriving there would meet it")})
    return out
""",
     """    for i, a in enumerate(arrivals):
        parts = [("stop", a["stop_box"])] + [("lane", box) for box in a["lane_boxes"]]
        for cv, rect in zip(named, pieces):
            for part in ("stop", "lane"):
                if any(_overlaps(rect, tuple(box)) for name, box in parts if name == part):
                    what = cv.get("species") or cv.get("source") or cv.get("name") or "a piece"
                    out.append({
                        "code": "LOT_RESPONDER_BLOCKED", "severity": "major", "category": "spawn",
                        "message": (f"{what} at ({cv['at'][0]:.1f}, {cv['at'][1]:.1f}) stands in "
                                    f"responder arrival {i}'s {part} on road "
                                    f"{a['road']}: the lane and the stop were reserved before it "
                                    f"was planned, and a vehicle arriving there would meet it")})
    return out
"""),
]

#: tests/test_site_responders.py, the same.
TESTS = [
    ("""Two sites:
- the kerb probe, assembled end to end -- one road with both ends open, and
  the getaway van on its north kerb;
- cold run 9198's seed_9256 as Lot drew it, with its cover cut back to the
  van, which is what stood when the arrivals were planned.

THE INSTRUMENTS ARE THE TESTS' OWN. A stop is read from its marker, the
lane's half from the road's own frame, and a piece's slot from its record's
`size` ([plan x, height, plan y]). The two controls at the end show the
reservation doing something: a car 9198 parked in a stop, parked again
without it and kept out with it; and a cover piece refused a kept-out spot
without the spot hiding anything.
""",
     """Three sites:
- the kerb probe, assembled end to end -- one road with both ends open, and
  the getaway van on its north kerb;
- cold run 9198's seed_9256 as Lot drew it, with its cover cut back to the
  van, which is what stood when the arrivals were planned;
- cold run 9204's club_block_014 seed_9181, the same way: the input site and
  the cover as drawn (0.100.0). Its getaway van stood 0.45 m into road 0's
  eastern lane and closed it; the lane steers round it now.

THE INSTRUMENTS ARE THE TESTS' OWN. A stop is read from its marker, the
lane's half from the road's own frame, and a piece's slot from its record's
`size` ([plan x, height, plan y]). The two controls at the end show the
reservation doing something: a car 9204 parked in what is now a stop,
parked again without it and kept out with it; and a cover piece refused a
kept-out spot without the spot hiding anything.
"""),
    ("""#: seed_9256's van door (the crew's spawn and extraction) and its objective,
#: as cold run 9198's scene wrote them (site frame).
SPAWN = (18.812, -1.8, 0.0)
OBJECTIVE = (-46.0, 9.25, -3.9)
""",
     """#: seed_9256's van door (the crew's spawn and extraction) and its objective,
#: as cold run 9198's scene wrote them (site frame).
SPAWN = (18.812, -1.8, 0.0)
OBJECTIVE = (-46.0, 9.25, -3.9)
#: Cold run 9204's seed_9181: the input site with the cover as drawn, and the
#: crew's points from the job's `site_walk.tscn` (Godot turned to site).
FIXTURE_9204 = os.path.join(HERE, "fixtures", "club_block_014_seed_9181.site.json")
SPAWN_9204 = (73.85, -17.95, 0.0)
OBJECTIVE_9204 = (-50.0, 5.0, 0.0)
#: Zoo, where the factory keeps it beside this repo.
ZOO = os.path.join(os.path.dirname(os.path.dirname(HERE)), "zoo")
"""),
    ("""def _in_the_way(drawn):
    return [(cv.get("species") or cv.get("source"), part)
            for m in _arrivals(drawn["site_markers"]) for part in ("stop_box", "lane_box")
            for cv in drawn["cover"] if cv.get("size") and _overlaps(_slot(cv), m["arrival"][part])]
""",
     """def _boxes(a):
    \"\"\"An arrival's reserved ground: (part, rect) for its stop and every box
    of its lane.\"\"\"
    return [("stop", a["stop_box"])] + [("lane", box) for box in a["lane_boxes"]]


def _in_the_way(drawn):
    return [(cv.get("species") or cv.get("source"), part)
            for m in _arrivals(drawn["site_markers"]) for part, box in _boxes(m["arrival"])
            for cv in drawn["cover"] if cv.get("size") and _overlaps(_slot(cv), box)]


def _plan_9204():
    full = json.load(open(FIXTURE_9204, encoding="utf-8"))
    spec = dict(full, cover=[cv for cv in full["cover"] if cv.get("source") == "getaway_van"])
    findings = []
    arrivals = site_responders.plan(spec, {"spawn": SPAWN_9204, "extraction": SPAWN_9204,
                                           "objective": OBJECTIVE_9204}, findings)
    return full, spec, arrivals, findings
"""),
    ("""    van = _slot(spec["cover"][0])
    for i, a in enumerate(arrivals):
        assert not _overlaps(a["stop_box"], van) and not _overlaps(a["lane_box"], van)
        assert math.dist(a["stop"], SPAWN[:2]) >= site_audit.CAMP_RADIUS
        for b in arrivals[i + 1:]:
            assert not _overlaps(a["stop_box"], b["stop_box"])
            assert not _overlaps(a["stop_box"], b["lane_box"])
            assert not _overlaps(b["stop_box"], a["lane_box"])
""",
     """    van = _slot(spec["cover"][0])
    for i, a in enumerate(arrivals):
        assert not any(_overlaps(box, van) for _part, box in _boxes(a))
        assert math.dist(a["stop"], SPAWN[:2]) >= site_audit.CAMP_RADIUS
        for b in arrivals[i + 1:]:
            assert not _overlaps(a["stop_box"], b["stop_box"])
            assert not any(_overlaps(a["stop_box"], box) for box in b["lane_boxes"])
            assert not any(_overlaps(b["stop_box"], box) for box in a["lane_boxes"])
"""),
    ("""def test_without_the_reservation_a_car_parks_in_a_stop():
    \"\"\"The control, on real ground. On the probe nothing lands in a lane or a
    stop even unreserved -- its stops sit where the way back crosses the
    road, which keeps its bays empty anyway -- so the probe alone cannot
    show the reservation doing anything.

    Cold run 9198 planned seed_9256 with no reservation and parked a car in
    bay L6 on road 1, at (21.112, 14.85): in what is now arrival 0's stop.
    `plan_parking` parks there again given no reservation, and given the
    reservation keeps every car out of every stop and lane -- and the
    read-back names 9198's car.\"\"\"
    full = json.load(open(FIXTURE, encoding="utf-8"))
    spec = dict(full, cover=[cv for cv in full["cover"] if cv.get("source") == "getaway_van"])
    arrivals = site_responders.plan(spec, {"spawn": SPAWN, "extraction": SPAWN,
                                           "objective": OBJECTIVE})
    shipped = site_responders.blocked(arrivals, full["cover"])
    assert len(shipped) == 1 and "(21.1, 14.8)" in shipped[0]["message"], shipped
    roads, van = site_streets.roads(spec), [_slot(spec["cover"][0])]

    def parked_in(keep):
        cars = site_parking.plan_parking(roads, van + list(keep), [SPAWN[:2], OBJECTIVE[:2]])
        return [tuple(cv["at"]) for cv in cars
                if any(_overlaps(_slot(cv), a[part])
                       for a in arrivals for part in ("stop_box", "lane_box"))]

    assert parked_in([]) == [(21.112, 14.85)]
    assert parked_in(site_responders.keep_out(arrivals)) == []
""",
     """def test_without_the_reservation_a_car_parks_in_a_stop():
    \"\"\"The control, on real ground. On the probe nothing lands in a lane or a
    stop even unreserved -- its stops sit where the way back crosses the
    road, which keeps its bays empty anyway -- so the probe alone cannot
    show the reservation doing anything.

    Cold run 9204 planned seed_9181 before the lane could steer: road 0's
    east end had no arrival, and `plan_parking` parked a car at (66.5,
    -20.25) -- in what is now arrival 1's stop, where the steered lane comes
    back into its half. `plan_parking` parks there again given no
    reservation, and given the reservation keeps every car out of every
    stop and lane -- and the read-back names 9204's car.

    *Through 0.99.1* this was cold run 9198's car at (21.112, 14.85) on
    seed_9256, in arrival 0's stop. The cruiser's 5.545 m length and its
    station grid moved that stop 0.36 m, and the car's slot now misses it by
    about 4 cm: an instance lost, not a reservation that stopped working.\"\"\"
    full, spec, arrivals, _findings = _plan_9204()
    shipped = site_responders.blocked(arrivals, full["cover"])
    assert len(shipped) == 1 and "(66.5, -20.2)" in shipped[0]["message"], shipped
    assert "arrival 1's stop" in shipped[0]["message"]
    roads, van = site_streets.roads(spec), [_slot(spec["cover"][0])]

    def parked_in(keep):
        cars = site_parking.plan_parking(roads, van + list(keep), [SPAWN_9204[:2], OBJECTIVE_9204[:2]])
        return [tuple(cv["at"]) for cv in cars
                if any(_overlaps(_slot(cv), box) for a in arrivals for _part, box in _boxes(a))]

    assert parked_in([]) == [(66.5, -20.25)]
    assert parked_in(site_responders.keep_out(arrivals)) == []


# --------------------------------------------------------------------------- #
# 0.100.0: the cruiser's size, and a lane that steers
# --------------------------------------------------------------------------- #

def test_the_lane_steers_round_the_van_on_9204():
    \"\"\"Cold run 9204's seed_9181, as its assemble planned it: three arrivals
    where 0.99.1 found two and `LOT_RESPONDER_ENTRY_NO_STOP` for road 0's
    east end. That end's lane moves toward the centre line by exactly what
    the van's slot needs, tapered, clears the van, and is back in its own
    half by the stop.\"\"\"
    _full, spec, arrivals, findings = _plan_9204()
    assert [f["code"] for f in findings] == []
    assert len(arrivals) == 3
    (road0,) = [r for r in site_streets.roads(spec) if r.index == 0]
    east = [a for a in arrivals if a["road"] == 0 and a["travel"] == -1]
    assert len(east) == 1, arrivals
    a = east[0]
    van = _slot(spec["cover"][0])
    w = site_responders.VEHICLE[1] + 2.0 * site_responders.LANE_MARGIN
    off = site_responders.lane_offset(road0, -1)

    def across(rect):
        vals = [(x - road0.a[0]) * road0.perp[0] + (y - road0.a[1]) * road0.perp[1]
                for x in (rect[0], rect[2]) for y in (rect[1], rect[3])]
        return min(vals), max(vals)

    # the van's edge nearest the centre line, and the shift that clears it
    v0, v1 = across(van)
    near = v0 if off > 0 else v1
    need = abs(off) + w / 2.0 - abs(near)
    assert a["lane_shift"] == pytest.approx(need, abs=1e-3)
    assert 0.6 < need < 0.7                        # 0.648 m: 0.45 + the mirror and margin growth
    boxes = a["lane_boxes"]
    assert not any(_overlaps(box, van) for box in boxes)
    # tapered: neighbouring boxes' centres step by no more than the rate allows
    centres = [sum(across(b)) / 2.0 for b in boxes]
    shifts = [abs(off) - abs(c) for c in centres]
    for s0, s1 in zip(shifts, shifts[1:]):
        assert abs(s1 - s0) <= site_responders.SHIFT_RATE * site_responders.STATION_STEP + 1e-6
    # back in its own half by the stop; every box on the carriageway
    assert shifts[-1] == pytest.approx(0.0, abs=1e-9)
    limit = site_responders.shift_limit(road0, off, w)
    assert max(shifts) <= limit


def test_a_shift_ramps_up_before_and_down_after():
    \"\"\"`steer`: a 0.6 m need at slices 4-5 of twelve, 1 m slices, at the
    MUTCD rate for 25 mph (0.192 across per metre along).\"\"\"
    rate = site_responders.SHIFT_RATE
    assert rate == pytest.approx(120.0 / 25.0 ** 2)
    need = [0.0] * 4 + [0.6, 0.6] + [0.0] * 6
    s = site_responders.steer(need, rate, [1.0] * 12)
    assert s[4] == s[5] == 0.6
    assert s[3] == pytest.approx(0.6 - rate) and s[6] == pytest.approx(0.6 - rate)
    assert s[0] == 0.0 and s[-1] == 0.0
    # the same need two slices from the stop cannot get back in time
    assert site_responders.steer([0.0] * 8 + [0.6, 0.6, 0.0, 0.0], rate, [1.0] * 12) is None


def test_a_lane_nothing_can_pass_is_refused():
    \"\"\"Ground standing across the whole carriageway leaves no shift that
    clears it: the slice needs None, and the entry gets no stop.\"\"\"
    _full, spec, _arrivals, _findings = _plan_9204()
    (road0,) = [r for r in site_streets.roads(spec) if r.index == 0]
    van = _slot(spec["cover"][0])
    stations = [(x - road0.a[0]) * road0.along[0] + (y - road0.a[1]) * road0.along[1]
                for x in (van[0], van[2]) for y in (van[1], van[3])]
    t = (min(stations) + max(stations)) / 2.0          # the van's station, from the road's frame
    corners = [road0.point(t + dt, side * road0.width) for dt in (-0.5, 0.5) for side in (-1.0, 1.0)]
    wall = (min(c[0] for c in corners), min(c[1] for c in corners),
            max(c[0] for c in corners), max(c[1] for c in corners))
    off = site_responders.lane_offset(road0, -1)
    w = site_responders.VEHICLE[1] + 2.0 * site_responders.LANE_MARGIN
    limit = site_responders.shift_limit(road0, off, w)
    assert site_responders._needs(road0, -1, off, w, [(t + 0.5, t - 0.5)], [wall], limit) == [None]
    # and the van alone, at the same slice, needs the shift that clears it
    assert site_responders._needs(road0, -1, off, w, [(t + 0.5, t - 0.5)], [van], limit)[0] > 0.6


def test_the_vehicle_is_zoos_cruiser():
    \"\"\"Lot does not import Zoo, so `VEHICLE` and `MIRROR_OUT` are pinned:
    read Zoo's `cruiser` genome and its `car_forms.CRUISER` row when Zoo
    stands beside this repo, and fail when they disagree.\"\"\"
    genome = os.path.join(ZOO, "zoo_keeper", "genome", "species", "cruiser.json")
    if not os.path.exists(genome):
        pytest.skip("Zoo is not beside this repo")
    dims = json.load(open(genome, encoding="utf-8"))["dimensions"]
    want = tuple(dims[k]["default"] for k in ("width", "depth", "height"))
    assert site_responders.VEHICLE == ("cruiser",) + want
    forms = open(os.path.join(ZOO, "zoo_keeper", "core", "car_forms.py"), encoding="utf-8").read()
    row = forms[forms.index("CRUISER = {"):forms.index("FORMS[\\"cruiser\\"] = CRUISER")]
    assert '"mirror_out": %r' % site_responders.MIRROR_OUT in row
"""),
]


EDITS = {
    "site_responders.py": RESPONDERS,
    str(pathlib.Path("tests") / "test_site_responders.py"): TESTS + [
        ("import os\nimport sys\n", "import os\nimport sys\n\nimport pytest\n"),
    ],
}


def main():
    v = LOT / "VERSION"
    assert v.read_bytes() == b"Lot 0.99.1", v.read_bytes()
    for rel in NEW:
        assert not (LOT / rel).exists(), ("already applied", rel)
    staged = {}
    for name, edits in EDITS.items():
        p = LOT / name
        d = p.read_bytes()
        crlf = b"\r\n" in d
        assert not (crlf and d.replace(b"\r\n", b"").count(b"\n")), (name, "mixed endings")
        t = d.decode("utf-8").replace("\r\n", "\n")
        for old, new in edits:
            n = t.count(old)
            assert n == 1, (name, n, old[:70])
            t = t.replace(old, new)
        staged[p] = (t.replace("\n", "\r\n") if crlf else t).encode("utf-8")
    entry = (SRC / "CHANGELOG_0.100.0.md").read_text(encoding="utf-8").replace("\r\n", "\n")
    assert "RESULT_" not in entry, "the changelog still carries an unfilled result"
    cl = LOT / "CHANGELOG.md"
    data = cl.read_bytes()
    assert b"\r\n" not in data
    text = data.decode("utf-8")
    assert text.startswith("## 0.99.1 - a stage light's aim moves with its club"), text[:60]
    # Every anchor matched: now write.
    for p, raw in staged.items():
        p.write_bytes(raw)
    for rel, src in NEW.items():
        (LOT / rel).parent.mkdir(parents=True, exist_ok=True)
        (LOT / rel).write_bytes((SRC / src).read_bytes())
    cl.write_bytes((entry + text).encode("utf-8"))
    v.write_bytes(b"Lot 0.100.0")
    print("Lot 0.99.1 -> 0.100.0")


if __name__ == "__main__":
    main()
