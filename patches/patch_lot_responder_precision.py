"""Lot 0.100.1: the responder planner checks the boxes it records (roadmap 212).

Cold run 9206 brought back the arrival cold run 9204 lost, and carried one
new major finding: on seed_9080, LOT_RESPONDER_BLOCKED, "step_van at
(-9.0, -26.9) stands in responder arrival 0's lane". It does not. 0.100.0
steered the lane 1e-6 m clear of the van, and the record rounded the
box's edge onto the van's: -28.22 against `cover_rects`' -26.92 - 1.3 =
-28.220000000000002. The read-back, which checks the recorded boxes,
found 3.6e-15 m of overlap. So the planner rounds each box once, to the
record's `RECORD_DIGITS`, checks that box, and records it, and a steered
lane clears what it passes by `RECORD_PRECISION`.

Anchored edits (every anchor once; refuses on a miss; nothing is written
until every anchor in every file matched):
- `site_responders.py`: `RECORD_DIGITS`, `RECORD_PRECISION`, `_recorded`;
  `_needs`, `_best_stop`, `_lane` and `plan` use them.
- `tests/test_site_responders.py`: seed_9080's fixture and a test that the
  read-back finds clear what the planner kept; the 9204 test's shift is
  the need plus the record's precision.
New file from `lot_responder_precision/`:
`tests/fixtures/club_block_014_seed_9080.site.json`, cold run 9206's input
site with the getaway van as placed.
CHANGELOG and VERSION from `lot_responder_precision/CHANGELOG_0.100.1.md`.

    python patch_lot_responder_precision.py
    LOT_ROOT=<copy> python patch_lot_responder_precision.py
"""
import os
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
LOT = pathlib.Path(os.environ.get("LOT_ROOT") or HERE.parent / "lot")
SRC = HERE / "lot_responder_precision"

NEW = {
    pathlib.Path("tests") / "fixtures" / "club_block_014_seed_9080.site.json":
        "club_block_014_seed_9080.site.json",
}

RESPONDERS = [
    ("""SHIFT_SPEED_MPH = 25.0
SHIFT_RATE = 120.0 / SHIFT_SPEED_MPH ** 2
""",
     """SHIFT_SPEED_MPH = 25.0
SHIFT_RATE = 120.0 / SHIFT_SPEED_MPH ** 2
#: THE PLANNER CHECKS THE BOXES IT RECORDS (0.100.1). `plan` writes a stop's
#: and a lane's boxes to `RECORD_DIGITS` decimals, and the read-back
#: (`blocked`) checks those -- so the planner rounds each box once, here,
#: and checks the rounded one, and a steered lane clears what it passes by
#: `RECORD_PRECISION`, which rounding cannot undo.
#: 0.100.0 checked unrounded boxes and cleared an edge by 1e-6 m. On cold
#: run 9206's seed_9080 the record rounded a box's edge onto the getaway
#: van's: -28.22 against `cover_rects`' -26.92 - 1.3 = -28.220000000000002.
#: The read-back reported the van in the lane, LOT_RESPONDER_BLOCKED, major,
#: by 3.6e-15 m.
RECORD_DIGITS = 3
RECORD_PRECISION = 10.0 ** -RECORD_DIGITS
"""),
    ("""def _interval(rect, road, axis) -> tuple:
""",
     """def _recorded(box) -> tuple:
    \"\"\"``box`` as the record writes it, to `RECORD_DIGITS` decimals: the value
    the planner checks, so the value the read-back checks is the same one.\"\"\"
    return tuple(round(v, RECORD_DIGITS) for v in box)


def _interval(rect, road, axis) -> tuple:
"""),
    ("""                if lo < s < hi:
                    s = hi + 1e-6
                    moved = True
""",
     """                if lo < s < hi:
                    s = hi + RECORD_PRECISION
                    moved = True
"""),
    ("""        stop = _box(road, t, off, d, body + 2.0 * DOOR_ROOM)
""",
     """        stop = _recorded(_box(road, t, off, d, body + 2.0 * DOOR_ROOM))
"""),
    ("""        boxes.append(_box(road, (a + b) / 2.0, off - sign * shifts[i], abs(b - a), lane_w))
""",
     """        boxes.append(_recorded(_box(road, (a + b) / 2.0, off - sign * shifts[i], abs(b - a), lane_w)))
"""),
    ("""            "stop_box": [round(v, 3) for v in stop],
            "lane_boxes": [[round(v, 3) for v in box] for box in lane],
""",
     """            "stop_box": list(stop),
            "lane_boxes": [list(box) for box in lane],
"""),
]

TESTS = [
    ("""FIXTURE_9204 = os.path.join(HERE, "fixtures", "club_block_014_seed_9181.site.json")
SPAWN_9204 = (73.85, -17.95, 0.0)
OBJECTIVE_9204 = (-50.0, 5.0, 0.0)
""",
     """FIXTURE_9204 = os.path.join(HERE, "fixtures", "club_block_014_seed_9181.site.json")
SPAWN_9204 = (73.85, -17.95, 0.0)
OBJECTIVE_9204 = (-50.0, 5.0, 0.0)
#: Cold run 9206's seed_9080: the input site and the getaway van as placed,
#: and the crew's points from the job's `site_walk.tscn` (0.100.1).
FIXTURE_9080 = os.path.join(HERE, "fixtures", "club_block_014_seed_9080.site.json")
SPAWN_9080 = (-10.65, -24.37, 0.0)
OBJECTIVE_9080 = (-47.0, -9.42, -3.3)
"""),
    ("""    # the van's edge nearest the centre line, and the shift that clears it
    v0, v1 = across(van)
    near = v0 if off > 0 else v1
    need = abs(off) + w / 2.0 - abs(near)
    assert a["lane_shift"] == pytest.approx(need, abs=1e-3)
    assert 0.6 < need < 0.7                        # 0.648 m: 0.45 + the mirror and margin growth
""",
     """    # the van's edge nearest the centre line, and the shift that clears it
    # by the record's precision (0.100.1)
    v0, v1 = across(van)
    near = v0 if off > 0 else v1
    need = abs(off) + w / 2.0 - abs(near)
    assert a["lane_shift"] == pytest.approx(need + site_responders.RECORD_PRECISION, abs=1e-6)
    assert 0.6 < need < 0.7                        # 0.648 m: 0.45 + the mirror and margin growth
"""),
    ("""def test_a_shift_ramps_up_before_and_down_after():
""",
     """def test_what_the_planner_keeps_the_read_back_finds_clear():
    \"\"\"Cold run 9206's seed_9080: a lane steered round the getaway van. 0.100.0
    cleared the van by 1e-6 m and rounded the record's box onto the van's
    edge, and `blocked` reported the van in the lane -- LOT_RESPONDER_BLOCKED,
    major -- by 3.6e-15 m. The planner now checks the boxes it records, and
    a steered lane clears what it passes by the record's precision.\"\"\"
    spec = json.load(open(FIXTURE_9080, encoding="utf-8"))
    findings = []
    arrivals = site_responders.plan(spec, {"spawn": SPAWN_9080, "extraction": SPAWN_9080,
                                           "objective": OBJECTIVE_9080}, findings)
    assert len(arrivals) == 3 and findings == []
    assert site_responders.blocked(arrivals, spec["cover"]) == []
    steered = [a for a in arrivals if a["lane_shift"] > 0]
    assert len(steered) == 1
    van = _slot(spec["cover"][0])
    for box in steered[0]["lane_boxes"]:
        if box[0] < van[2] and van[0] < box[2]:       # beside the van along the road
            gap = max(van[1] - box[3], box[1] - van[3])
            assert gap >= site_responders.RECORD_PRECISION / 2.0, (box, van, gap)
    # every box in a record is already at the record's precision
    for a in arrivals:
        for _part, box in _boxes(a):
            assert list(site_responders._recorded(box)) == list(box)


def test_a_shift_ramps_up_before_and_down_after():
"""),
]


EDITS = {
    "site_responders.py": RESPONDERS,
    str(pathlib.Path("tests") / "test_site_responders.py"): TESTS,
}


def main():
    v = LOT / "VERSION"
    assert v.read_bytes() == b"Lot 0.100.0", v.read_bytes()
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
    entry = (SRC / "CHANGELOG_0.100.1.md").read_text(encoding="utf-8").replace("\r\n", "\n")
    assert "RESULT_" not in entry, "the changelog still carries an unfilled result"
    cl = LOT / "CHANGELOG.md"
    data = cl.read_bytes()
    assert b"\r\n" not in data
    text = data.decode("utf-8")
    assert text.startswith("## 0.100.0 - the responders' cruiser is Zoo's"), text[:60]
    # Every anchor matched: now write.
    for p, raw in staged.items():
        p.write_bytes(raw)
    for rel, src in NEW.items():
        (LOT / rel).parent.mkdir(parents=True, exist_ok=True)
        (LOT / rel).write_bytes((SRC / src).read_bytes())
    cl.write_bytes((entry + text).encode("utf-8"))
    v.write_bytes(b"Lot 0.100.1")
    print("Lot 0.100.0 -> 0.100.1")


if __name__ == "__main__":
    main()
