"""Level Factory 0.162.0: each responder arrival names the car it brings
(roadmap 212).

Lot 0.101.0's themed assembly copies the cruiser Zoo's site kit built into
`cover/` beside its scene and names it in `responders.json`.
`write_responder_arrivals` takes the themed site's directory and gives each
arrival `vehicle_scene`, matched by stop -- null, with the reason in
`vehicle_findings`, when no car is named or the file is not in the package.
`responder_arrivals.json` schema v3.

Anchored edits (every anchor once; refuses on a miss; nothing is written
until every anchor in every file matched):
- `packages/exporting/export.py`: `write_responder_arrivals` and its call.
- `tests/unit/test_responder_arrivals_in_package.py`: v3, and two tests.
CHANGELOG and VERSION from `lf_responder_vehicle/CHANGELOG_0.162.0.md`.

    python patch_lf_responder_vehicle.py
    LF_ROOT=<copy> python patch_lf_responder_vehicle.py
"""
import os
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
LF = pathlib.Path(os.environ.get("LF_ROOT") or HERE.parent / "level_factory")
SRC = HERE / "lf_responder_vehicle"
CHANGELOG_HEAD = "## [0.161.0] - The package ships a responder's lane as Lot steered it\n"

EXPORT = [
    ("""def write_responder_arrivals(export_dir: Path, lot_gameplay) -> dict | None:
""",
     """def write_responder_arrivals(export_dir: Path, lot_gameplay,
                             themed_site_dir: Path | None = None) -> dict | None:
"""),
    ("""    round. A lane from Lot 0.99 is its one `lane_box`, shipped as the only
    box, at shift 0.
""",
     """    round. A lane from Lot 0.99 is its one `lane_box`, shipped as the only
    box, at shift 0.

    THE CAR EACH BRINGS (0.162.0, schema v3). Lot 0.101.0's themed assembly
    copies the cruiser Zoo's site kit built beside its scene -- into
    `cover/`, a sibling this package carries -- stands it nowhere, and names
    it in `responders.json`. Each arrival here gets `vehicle_scene`, the
    car's `res://` path, matched by its stop. It is null when the themed
    site names no car for that stop, or names a file the package does not
    hold, and `vehicle_findings` says which. This file is one of
    `closure._METADATA_FILES`, so the closure gate does not read the path:
    the file's presence is checked here. Lot from before 0.101.0 writes no
    `responders.json`, and every arrival's car is null with that said once.
"""),
    ("""    from packages.staging.dispatch_inputs import site_marker_anchor_pairs
    arrivals = []
""",
     """    from packages.staging.dispatch_inputs import site_marker_anchor_pairs

    def stop_key(p):
        return (round(float(p[0]), 3), round(float(p[1]), 3))

    cars, said = {}, []
    named = Path(themed_site_dir) / "responders.json" if themed_site_dir else None
    if named is not None and named.is_file():
        rv = json.loads(named.read_text(encoding="utf-8"))
        for v in rv.get("vehicles") or []:
            cars[stop_key(v["stop"])] = v["scene"]
        if rv.get("missing"):
            said.append("the themed site built no car for arrival(s) %s" % rv["missing"])
    else:
        said.append("the themed site names no responder car (no responders.json: "
                    "Lot before 0.101.0, or no themed site)")
    arrivals = []
"""),
    ("""        lane = a["lane_boxes"] if "lane_boxes" in a else [a["lane_box"]]
""",
     """        lane = a["lane_boxes"] if "lane_boxes" in a else [a["lane_box"]]
        scene = cars.get(stop_key(a["stop"]))
        if scene is not None and not (export_dir / scene).is_file():
            said.append("%s is named for the stop at %s and is not in the package"
                        % (scene, list(a["stop"][:2])))
            scene = None
        elif scene is None and cars:
            said.append("the themed site names no car for the stop at %s" % list(a["stop"][:2]))
"""),
    ("""            "lane_shift_m": a.get("lane_shift", 0.0),
""",
     """            "lane_shift_m": a.get("lane_shift", 0.0),
            "vehicle_scene": ("res://" + scene) if scene else None,
"""),
    ("""    doc = {"schema": "level_factory.responder_arrivals.v2",
""",
     """    doc = {"schema": "level_factory.responder_arrivals.v3",
"""),
    ("""           "arrivals": arrivals}
    (export_dir / RESPONDER_ARRIVALS_NAME).write_text(pretty_dumps(doc), encoding="utf-8")
""",
     """           "arrivals": arrivals, "vehicle_findings": said}
    (export_dir / RESPONDER_ARRIVALS_NAME).write_text(pretty_dumps(doc), encoding="utf-8")
"""),
    ("""    arrivals_doc = write_responder_arrivals(export_dir, lot_gameplay)
""",
     """    arrivals_doc = write_responder_arrivals(export_dir, lot_gameplay, themed_site_dir)
"""),
]

TEST = [
    ("""from packages.staging.dispatch_inputs import stage_dispatch_inputs  # noqa: E402
""",
     """from packages.staging.dispatch_inputs import stage_dispatch_inputs  # noqa: E402
from tests.unit.glb_fixture import stub_glb  # noqa: E402
"""),
    ("""    assert doc["schema"] == "level_factory.responder_arrivals.v2"
""",
     """    assert doc["schema"] == "level_factory.responder_arrivals.v3"
    # no themed site: no car named, and said once
    assert all(a["vehicle_scene"] is None for a in doc["arrivals"])
    assert len(doc["vehicle_findings"]) == 1 and "no responders.json" in doc["vehicle_findings"][0]
"""),
    ("""def test_the_manifest_lists_it(tmp_path):
""",
     """#: The cruiser module Zoo's site kit builds for a responder slot at the
#: genome's default size, as Lot 0.101.0's themed assembly names it.
CAR = "cover/prop_cruiser_delco_1997_01_w220_d554_h158.glb"


def _themed(tmp_path, scene_present=True):
    \"\"\"A themed site dir as Lot 0.101.0 leaves one: the scene, the car in
    `cover/` (or not), and `responders.json` naming it for STEERED's stop.\"\"\"
    themed = tmp_path / "themed"
    themed.mkdir()
    (themed / "site.tscn").write_text("[gd_scene]\\n", encoding="utf-8")
    if scene_present:
        stub_glb(themed / CAR, "cruiser")
    (themed / "responders.json").write_text(json.dumps({
        "schema": "lot.responder_vehicles.v1",
        "vehicles": [{"arrival": 0, "species": "cruiser", "scene": CAR,
                      "stop": STEERED["stop"], "yaw": 270.0,
                      "dims": STEERED["vehicle"]}],
        "missing": []}), encoding="utf-8")
    return themed


def _export_themed(tmp_path, themed):
    gp = {"up_axis": "z", "markers": [],
          "site_markers": [{"type": "crew_spawn", "at": VAN, "source": "getaway_van"},
                           {"type": "responder_spawn", "at": STEERED["stop"],
                            "source": "responder_arrival", "arrival": STEERED}],
          "responder_plan": {"arrivals": [STEERED], "findings": []}}
    path = tmp_path / "site.site.gameplay.json"
    path.write_text(json.dumps(gp), encoding="utf-8")
    handoff = tmp_path / "handoff"
    handoff.mkdir()
    (handoff / "mission.tscn").write_text("[gd_scene]\\n", encoding="utf-8")
    (handoff / "site.tscn").write_text("[gd_scene]\\n", encoding="utf-8")
    result = export_mission(mission_id="m1", handoff_dir=handoff, presentation_dir=None,
                            source_dir=None, profile=ExportProfile(), tool_versions={},
                            out_root=tmp_path / "exports", lot_gameplay=path,
                            themed_site_dir=themed)
    return result, json.loads((result.export_dir / RESPONDER_ARRIVALS_NAME).read_text(encoding="utf-8"))


def test_each_arrival_names_the_car_it_brings(tmp_path):
    \"\"\"Lot 0.101.0's themed site names the cruiser for the stop; the car is
    in the package's `cover/`, and the arrival names its `res://` path.\"\"\"
    result, doc = _export_themed(tmp_path, _themed(tmp_path))
    (got,) = doc["arrivals"]
    assert got["vehicle_scene"] == "res://" + CAR
    assert (result.export_dir / CAR).is_file()
    assert doc["vehicle_findings"] == []


def test_a_car_named_but_not_in_the_package_is_null_and_said(tmp_path):
    \"\"\"A path the package does not hold is not shipped as if it did.\"\"\"
    _result, doc = _export_themed(tmp_path, _themed(tmp_path, scene_present=False))
    (got,) = doc["arrivals"]
    assert got["vehicle_scene"] is None
    assert any("not in the package" in s for s in doc["vehicle_findings"])


def test_the_manifest_lists_it(tmp_path):
"""),
]


def _stage(root, edits):
    """{path: bytes}: every file's new content, every anchor matched once,
    endings kept; raises before anything is written."""
    staged = {}
    for rel, pairs in edits.items():
        p = root / rel
        d = p.read_bytes()
        crlf, lf = d.count(b"\r\n"), d.count(b"\n")
        assert crlf in (0, lf), (rel, "mixed endings")
        t = d.decode("utf-8").replace("\r\n", "\n")
        for old, new in pairs:
            n = t.count(old)
            assert n == 1, (rel, n, old[:70])
            t = t.replace(old, new)
        staged[p] = (t.replace("\n", "\r\n") if crlf else t).encode("utf-8")
    return staged


EDITS = {
    str(pathlib.Path("packages") / "exporting" / "export.py"): EXPORT,
    str(pathlib.Path("tests") / "unit" / "test_responder_arrivals_in_package.py"): TEST,
}


def main():
    v = (LF / "VERSION").read_bytes()
    assert v == b"0.161.0", repr(v)
    staged = _stage(LF, EDITS)
    entry = (SRC / "CHANGELOG_0.162.0.md").read_text(encoding="utf-8").replace("\r\n", "\n")
    assert "RESULT_" not in entry, "the changelog still carries an unfilled result"
    c = (LF / "CHANGELOG.md").read_bytes()
    assert b"\r\n" not in c
    text = c.decode("utf-8")
    assert text.startswith(CHANGELOG_HEAD) and text.count(CHANGELOG_HEAD) == 1, text[:80]
    # Every anchor matched: now write.
    for p, raw in staged.items():
        p.write_bytes(raw)
    (LF / "CHANGELOG.md").write_bytes((entry + text).encode("utf-8"))
    (LF / "VERSION").write_bytes(b"0.162.0")
    print("Level Factory 0.161.0 -> 0.162.0")


if __name__ == "__main__":
    main()
