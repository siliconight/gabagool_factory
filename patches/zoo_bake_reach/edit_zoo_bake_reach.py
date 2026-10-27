"""Edit a Zoo clone for 1.134.0: a light row's `bake_reach` (Deli Counter >= 0.279.0) rides every lamp of the row, and
the marker carries it as `lux_bake_reach` for Lux >= 0.80.0, only where a row has one. Run from the clone's root.
Asserts every anchor once; refuses on a miss."""
from pathlib import Path


def edit(path, pairs):
    p = Path(path)
    raw = p.read_bytes()
    crlf = b"\r\n" in raw
    t = raw.decode("utf-8").replace("\r\n", "\n")
    for old, new in pairs:
        assert t.count(old) == 1, (path, old[:70], t.count(old))
        t = t.replace(old, new)
    if crlf:
        t = t.replace("\n", "\r\n")
    p.write_bytes(t.encode("utf-8"))
    print(path, "edited", len(pairs), "anchors", "CRLF" if crlf else "LF")


edit("zoo_keeper/core/fixtures.py", [
('''                "reach": float(a.get("reach", 0.0) or 0.0),
                "seed_offset": _seed_offset(aid, j),''',
'''                "reach": float(a.get("reach", 0.0) or 0.0),
                # 1.134.0: a row Deli Counter (>= 0.279.0) asks to bake
                # further than it lights live carries `bake_reach`, the
                # horizontal metres its lightmap must reach; Lux >= 0.80.0
                # lends the lamp that range only while a lightmap bakes. 0.0
                # everywhere else, and then no marker carries it.
                "bake_reach": float(a.get("bake_reach", 0.0) or 0.0),
                "seed_offset": _seed_offset(aid, j),'''),
])

edit("zoo_keeper/bpylayer/build.py", [
('''        if float(p.get("reach", 0.0)) > 0.0:
            mk["lux_reach"] = float(p["reach"])
''',
'''        if float(p.get("reach", 0.0)) > 0.0:
            mk["lux_reach"] = float(p["reach"])
        # 1.134.0: the same, for the reach a row's lightmap bakes to
        if float(p.get("bake_reach", 0.0)) > 0.0:
            mk["lux_bake_reach"] = float(p["bake_reach"])
'''),
])

edit("tests/test_fixtures.py", [
('''    assert reach == {"sales_floor_ceiling": [6.0, 6.0, 6.0],
                     "stockroom_ceiling": [0.0, 0.0]}
''',
'''    assert reach == {"sales_floor_ceiling": [6.0, 6.0, 6.0],
                     "stockroom_ceiling": [0.0, 0.0]}


def test_bake_reach_rides_every_lamp_of_its_row_and_no_other():
    # 1.134.0: Deli Counter stamps `bake_reach` on a supermarket's rows
    p = fixtures.plan(_manifest([
        {"id": "sales_floor_ceiling", "type": "fluorescent", "pos": [0, 0, 4.1],
         "row": {"count": 3, "spacing": 5.5}, "drop": 4.1, "bake_reach": 5.5},
        {"id": "stockroom_ceiling", "type": "fluorescent", "pos": [0, 9, 3.8],
         "row": {"count": 2, "spacing": 4.0}, "drop": 3.8, "reach": 6.0}]))
    got = {}
    for pl in p["placements"]:
        got.setdefault(pl["anchor_id"], []).append((pl["bake_reach"], pl["reach"]))
    assert got == {"sales_floor_ceiling": [(5.5, 0.0)] * 3,
                   "stockroom_ceiling": [(0.0, 6.0)] * 2}
'''),
('''    got = sorted((m["lux_anchor_id"], m.get("lux_reach")) for m in marks)
    assert got == [("sales_floor_ceiling", 6.0), ("sales_floor_ceiling", 6.0),
                   ("stockroom_ceiling", None)], got
''',
'''    got = sorted((m["lux_anchor_id"], m.get("lux_reach")) for m in marks)
    assert got == [("sales_floor_ceiling", 6.0), ("sales_floor_ceiling", 6.0),
                   ("stockroom_ceiling", None)], got


def test_bpy_a_row_marks_its_bake_reach_and_no_other_row_does(tmp_path):
    # 1.134.0: as the reach, for Lux's bake -- absent on the control
    pytest.importorskip("bpy")
    import json
    import os
    from zoo_keeper.bpylayer import build
    manifest = {"light_manifest_version": "1.2.0", "building_id": "bake_reach_bpy",
                "space": "Blender Z-up, meters", "anchors": [
                    {"id": "sales_floor_ceiling", "type": "fluorescent", "pos": [0.0, 0.0, 4.1],
                     "rot_y": 0.0, "row": {"count": 2, "spacing": 5.5}, "drop": 4.1, "bake_reach": 5.5},
                    {"id": "stockroom_ceiling", "type": "fluorescent", "pos": [0.0, 9.0, 3.8],
                     "rot_y": 0.0, "row": {"count": 1, "spacing": 0.0}, "drop": 3.8}]}
    build.build_fixtures(manifest, str(tmp_path), theme="delco", options={"save_blend": False})
    with open(os.path.join(str(tmp_path), "bake_reach_bpy_fixtures.built.json"), encoding="utf-8") as fh:
        index = json.load(fh)
    j = _gltf(os.path.join(str(tmp_path), index["files"]["glb"]))
    marks = [n.get("extras", {}) for n in j["nodes"] if n["name"].startswith("LuxEmit")]
    got = sorted((m["lux_anchor_id"], m.get("lux_bake_reach")) for m in marks)
    assert got == [("sales_floor_ceiling", 5.5), ("sales_floor_ceiling", 5.5),
                   ("stockroom_ceiling", None)], got
'''),
])
