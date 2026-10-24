"""Lot 0.129.0 on a CLONE (<repo>): a building with a band carries no lit door box (the walker's walk of cold run 9386,
finding 1: "in real life this would be 1 sign"). Anchored; refuses on a miss.

    python edit_lot_one_sign.py <repo>
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


edit("lot.py", [
    ('''def merge_lights(site_spec, base_dir):
    """Merge every building's <name>.lights.json into one site-level lighting
    manifest: each anchor offset to world space and id-namespaced by building
    (mirrors merge_gameplay), plus the exterior streetlights Lot derives.
    Deterministic. Consumed by Lux's light-anchor loader."""''',
     '''def merge_lights(site_spec, base_dir):
    """Merge every building's <name>.lights.json into one site-level lighting
    manifest: each anchor offset to world space and id-namespaced by building
    (mirrors merge_gameplay), plus the exterior streetlights Lot derives.
    Deterministic. Consumed by Lux's light-anchor loader.

    ONE SIGN A BUILDING (0.129.0). The walker, walking cold run 9386, of a
    pharmacy with its band along the parapet and a lit box over its door: "in
    real life this would be 1 sign". A building the spec deals a band
    (`signs`, which `sign_placement` hangs on any building with a footprint)
    keeps the band, centred on its street face, and its door box's lamp -- a
    `sign` anchor -- is left out here; Level Factory 0.241.0 builds that shell's
    fixtures without the box. A building with no band keeps its box as its one
    sign. Counted in ``door_signs_dropped``."""'''),
    ('''    merged_versions = []
    for b in site_spec["buildings"]:
        bid = b["id"]''',
     '''    merged_versions = []
    banded = set((site_spec.get("signs") or {}).keys())
    site["door_signs_dropped"] = []
    for b in site_spec["buildings"]:
        bid = b["id"]'''),
    ('''        for a in lm.get("anchors", []):
            wa = dict(a)
            wa["id"] = f"{bid}/{a.get('id', 'light')}"''',
     '''        for a in lm.get("anchors", []):
            if bid in banded and a.get("type") == "sign":
                site["door_signs_dropped"].append(f"{bid}/{a.get('id', 'light')}")
                continue
            wa = dict(a)
            wa["id"] = f"{bid}/{a.get('id', 'light')}"'''),
])

TEST = '''"""One sign a building (0.129.0). The walker, walking cold run 9386, of a pharmacy with its band along the parapet
and a lit box over its door: "in real life this would be 1 sign". A building the spec deals a band loses its door
box's lamp (a `sign` anchor) from the site's lights; a building with no band keeps its box. FAILS ON 0.128.0."""
import json

import lot


def _site(tmp_path, signs):
    lights = {"light_manifest_version": "1.1.0", "anchors": [
        {"id": "ext_0_S_sign", "type": "sign", "pos": [-3.5, -9.35, 2.55], "rot_y": 270.0},
        {"id": "ceiling_0", "type": "fluorescent", "pos": [0.0, 0.0, 3.0]}]}
    for name in ("shop", "office"):
        (tmp_path / (name + ".lights.json")).write_text(json.dumps(lights), encoding="utf-8")
    return {"name": "t", "buildings": [
        {"id": "b0", "at": [0.0, 0.0], "rot": 0, "lights": "shop.lights.json"},
        {"id": "b1", "at": [40.0, 0.0], "rot": 0, "lights": "office.lights.json"}],
        "roads": [], "signs": signs}


def test_a_banded_building_loses_its_door_box_lamp_and_an_unbanded_one_keeps_it(tmp_path):
    site = lot.merge_lights(_site(tmp_path, {"b0": "packs/sign_x"}), str(tmp_path))
    ids = {a["id"] for a in site["anchors"]}
    assert "b0/ext_0_S_sign" not in ids and "b0/ceiling_0" in ids
    assert "b1/ext_0_S_sign" in ids and "b1/ceiling_0" in ids
    assert site["door_signs_dropped"] == ["b0/ext_0_S_sign"]


def test_no_bands_drops_nothing(tmp_path):
    site = lot.merge_lights(_site(tmp_path, {}), str(tmp_path))
    assert {"b0/ext_0_S_sign", "b1/ext_0_S_sign"} <= {a["id"] for a in site["anchors"]}
    assert site["door_signs_dropped"] == []
'''
(R / "tests" / "test_one_sign.py").write_text(TEST, encoding="utf-8", newline="\n")
(R / "VERSION").write_bytes(b"Lot 0.129.0")
print("lot.merge_lights: one sign a building; tests/test_one_sign.py; VERSION")
