"""Level Factory 0.161.0: the package ships a responder's lane as Lot
steered it (roadmap 212).

Lot 0.100.0 steers an arrival's lane round what stands in it and writes it
as `lane_boxes` with `lane_shift`; one box drawn round a steered lane would
cover the van the lane goes round. `write_responder_arrivals` ships every
box in Lot's order, and the largest shift, as `responder_arrivals.json`
schema v2; a Lot 0.99 arrival's one `lane_box` ships as its only box.

Anchored edits (every anchor once; refuses on a miss; nothing is written
until every anchor in every file matched):
- `packages/exporting/export.py`: `write_responder_arrivals`.
- `tests/unit/test_responder_arrivals_in_package.py`: v2, the 0.99 lane as
  one box, and a steered lane's nine boxes, verbatim from Lot 0.100.0.
CHANGELOG and VERSION from `lf_lane_boxes/CHANGELOG_0.161.0.md`.

    python patch_lf_lane_boxes.py
    LF_ROOT=<copy> python patch_lf_lane_boxes.py
"""
import os
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
LF = pathlib.Path(os.environ.get("LF_ROOT") or HERE.parent / "level_factory")
SRC = HERE / "lf_lane_boxes"
CHANGELOG_HEAD = "## [0.160.0] - The light bake keeps a cycling rig live\n"

EXPORT = [
    ("""    anchor holds a position and tags, so the rest is here, keyed by that
    anchor's id: the road end a vehicle appears at, the stop, which way it
    faces arriving, the lane and stop boxes nothing else stands in, and the
    point of the crew's way back the stop was chosen for.
""",
     """    anchor holds a position and tags, so the rest is here, keyed by that
    anchor's id: the road end a vehicle appears at, the stop, which way it
    faces arriving, the lane and stop boxes nothing else stands in, and the
    point of the crew's way back the stop was chosen for.

    THE LANE IS BOXES (0.161.0, schema v2). Lot 0.100.0 steers a lane round
    what stands in it -- toward and across the centre line, tapered, back in
    its own half by the stop -- and writes it as `lane_boxes`, one box a run
    of slices at one shift, with `lane_shift` the largest. One box could not
    say that: drawn round a steered lane it covers the van the lane goes
    round. A lane from Lot 0.99 is its one `lane_box`, shipped as the only
    box, at shift 0.
"""),
    ("""        boxes = {}
        for key in ("stop_box", "lane_box"):
            x0, y0, x1, y1 = a[key]
            boxes[key] = {"min": _package_xz(x0, y1), "max": _package_xz(x1, y0)}
        arrivals.append({
            "anchor": anchor["id"],
            "entry": [ex, 0.0, ez], "stop": [sx, 0.0, sz],
            "forward": [dx / n, 0.0, dz / n],
            "vehicle_m": list(a.get("vehicle") or []),
            "stop_box": boxes["stop_box"], "lane_box": boxes["lane_box"],
            "toward": [tx, 0.0, tz],
            "to_way_back_m": a.get("to_way_back"), "run_m": a.get("run"),
        })
    doc = {"schema": "level_factory.responder_arrivals.v1",
""",
     """        def box(rect):
            x0, y0, x1, y1 = rect
            return {"min": _package_xz(x0, y1), "max": _package_xz(x1, y0)}

        lane = a["lane_boxes"] if "lane_boxes" in a else [a["lane_box"]]
        arrivals.append({
            "anchor": anchor["id"],
            "entry": [ex, 0.0, ez], "stop": [sx, 0.0, sz],
            "forward": [dx / n, 0.0, dz / n],
            "vehicle_m": list(a.get("vehicle") or []),
            "stop_box": box(a["stop_box"]),
            "lane_boxes": [box(r) for r in lane],
            "lane_shift_m": a.get("lane_shift", 0.0),
            "toward": [tx, 0.0, tz],
            "to_way_back_m": a.get("to_way_back"), "run_m": a.get("run"),
        })
    doc = {"schema": "level_factory.responder_arrivals.v2",
"""),
]

TEST = [
    ("""def test_the_package_says_how_each_responder_arrives(tmp_path):
    result = _export(tmp_path, _gameplay(tmp_path))
    doc = json.loads((result.export_dir / RESPONDER_ARRIVALS_NAME).read_text(encoding="utf-8"))
    assert doc["schema"] == "level_factory.responder_arrivals.v1"
""",
     """def test_the_package_says_how_each_responder_arrives(tmp_path):
    result = _export(tmp_path, _gameplay(tmp_path))
    doc = json.loads((result.export_dir / RESPONDER_ARRIVALS_NAME).read_text(encoding="utf-8"))
    assert doc["schema"] == "level_factory.responder_arrivals.v2"
"""),
    ("""        x0, y0, x1, y1 = a["stop_box"]
        assert got["stop_box"] == {"min": [x0, -y1], "max": [x1, -y0]}
        assert got["vehicle_m"] == a["vehicle"]
""",
     """        x0, y0, x1, y1 = a["stop_box"]
        assert got["stop_box"] == {"min": [x0, -y1], "max": [x1, -y0]}
        assert got["vehicle_m"] == a["vehicle"]
        # a Lot 0.99 lane: its one box, the only one, at shift 0
        x0, y0, x1, y1 = a["lane_box"]
        assert got["lane_boxes"] == [{"min": [x0, -y1], "max": [x1, -y0]}]
        assert got["lane_shift_m"] == 0.0
        assert "lane_box" not in got


#: Lot 0.100.0's arrival for cold run 9204's road 0 east end, the one a
#: rigid lane lost to the getaway van, verbatim from `site_responders.plan`
#: on Lot's `club_block_014_seed_9181` fixture: its lane steered 0.648 m round
#: the van, nine boxes (plan rects, site frame) in order from the entry, the
#: shift ramping 0.192 a metre up and back down.
STEERED = {
    "road": 0, "travel": -1, "entry": [92.5, -22.75], "stop": [62.637, -22.75], "yaw": 270.0,
    "vehicle": [2.196, 5.545, 1.578], "stop_box": [59.865, -24.743, 65.41, -20.757],
    "lane_boxes": [[82.5, -24.348, 92.5, -21.152], [81.5, -24.42, 82.5, -21.224],
                   [80.5, -24.612, 81.5, -21.416], [79.5, -24.804, 80.5, -21.608],
                   [71.5, -24.996, 79.5, -21.8], [70.5, -24.804, 71.5, -21.608],
                   [69.5, -24.612, 70.5, -21.416], [68.5, -24.42, 69.5, -21.224],
                   [65.41, -24.348, 68.5, -21.152]],
    "lane_shift": 0.648, "toward": [63.87, -16.101], "to_way_back": 6.763, "run": 29.863,
}


def test_a_steered_lane_ships_every_box_in_order(tmp_path):
    \"\"\"Lot 0.100.0's `lane_boxes`, each turned to the package's frame, in the
    order Lot wrote them, with the lane's largest shift.\"\"\"
    gp = {"up_axis": "z", "markers": [],
          "site_markers": [{"type": "crew_spawn", "at": VAN, "source": "getaway_van"},
                           {"type": "responder_spawn", "at": STEERED["stop"],
                            "source": "responder_arrival", "arrival": STEERED}],
          "responder_plan": {"arrivals": [STEERED], "findings": []}}
    path = tmp_path / "site.site.gameplay.json"
    path.write_text(json.dumps(gp), encoding="utf-8")
    result = _export(tmp_path, path)
    doc = json.loads((result.export_dir / RESPONDER_ARRIVALS_NAME).read_text(encoding="utf-8"))
    (got,) = doc["arrivals"]
    assert got["lane_boxes"] == [{"min": [x0, -y1], "max": [x1, -y0]}
                                 for x0, y0, x1, y1 in STEERED["lane_boxes"]]
    assert got["lane_shift_m"] == 0.648
    assert got["vehicle_m"] == [2.196, 5.545, 1.578]
"""),
]


EDITS = {
    str(pathlib.Path("packages") / "exporting" / "export.py"): EXPORT,
    str(pathlib.Path("tests") / "unit" / "test_responder_arrivals_in_package.py"): TEST,
}


def main():
    v = (LF / "VERSION").read_bytes()
    assert v == b"0.160.0", repr(v)
    staged = {}
    for name, edits in EDITS.items():
        p = LF / name
        d = p.read_bytes()
        crlf, lf = d.count(b"\r\n"), d.count(b"\n")
        assert crlf in (0, lf), (name, "mixed endings")
        t = d.decode("utf-8").replace("\r\n", "\n")
        for old, new in edits:
            n = t.count(old)
            assert n == 1, (name, n, old[:70])
            t = t.replace(old, new)
        staged[p] = (t.replace("\n", "\r\n") if crlf else t).encode("utf-8")
    entry = (SRC / "CHANGELOG_0.161.0.md").read_text(encoding="utf-8").replace("\r\n", "\n")
    assert "RESULT_" not in entry, "the changelog still carries an unfilled result"
    c = (LF / "CHANGELOG.md").read_bytes()
    assert b"\r\n" not in c
    text = c.decode("utf-8")
    assert text.startswith(CHANGELOG_HEAD) and text.count(CHANGELOG_HEAD) == 1, text[:80]
    # Every anchor matched: now write.
    for p, raw in staged.items():
        p.write_bytes(raw)
    (LF / "CHANGELOG.md").write_bytes((entry + text).encode("utf-8"))
    (LF / "VERSION").write_bytes(b"0.161.0")
    print("Level Factory 0.160.0 -> 0.161.0")


if __name__ == "__main__":
    main()
