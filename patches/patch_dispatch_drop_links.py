"""Dispatch 0.5.3: a declared drop's off-mesh link reaches the package (factory roadmap 173, step 3).

Deli Counter 0.226.0 files a one-way `nav_link` on every `floor_hole` / `hatch` vertical link, and Lot 0.125.0
moves it into site space. Both importers here carried a LADDER's link (0.5.0, 0.5.1: cold run 9075 found the
Lot importer had not been taught) and read nothing off a vertical link, so `navigation_hints.json` `links[]`
held the climbs and none of the drops. Now both importers read `vertical_links[].nav_link` exactly as they read
`ladders[].nav_link`: `NavGraph.add_off_mesh_link` namespaces and converts it, the payload rides verbatim
(`required_capability` "drop", `bidirectional` false, `hole`).

What it changes (anchored; refuses on a miss; CRLF-safe):
  * importers/deli_counter.py and importers/lot.py: the vertical-link loop after the ladder loop.
  * tests/test_drop_links.py, VERSION 0.5.3, dispatch/__init__.py __version__, CHANGELOG.

    python patches/patch_dispatch_drop_links.py --tests   # the test file only
    python patches/patch_dispatch_drop_links.py           # everything
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
DP = ROOT / "dispatch"


def _apply(path, old, new, count=1):
    raw = path.read_bytes()
    crlf = raw.count(b"\r\n")
    lf = raw.count(b"\n") - crlf
    assert crlf == 0 or lf == 0, f"{path.name}: mixed endings ({crlf} CRLF, {lf} LF)"
    eol = "\r\n" if crlf else "\n"
    text = raw.decode("utf-8")
    o, n = old.replace("\n", eol), new.replace("\n", eol)
    assert text.count(o) == count, f"{path.name}: anchor found {text.count(o)} times, wanted {count}: {old[:70]!r}"
    path.write_bytes(text.replace(o, n).encode("utf-8"))


DC_OLD = '''    for _lad in gp.get("ladders", []) or []:
        _link = _lad.get("nav_link")
        if _link:
            imp.nav.add_off_mesh_link(_link, "deli_counter", _up)
'''
DC_NEW = '''    for _lad in gp.get("ladders", []) or []:
        _link = _lad.get("nav_link")
        if _link:
            imp.nav.add_off_mesh_link(_link, "deli_counter", _up)
    # DECLARED DROPS (Deli Counter 0.226.0): a floor_hole / hatch vertical link
    # files a one-way nav link the same way a ladder does, so the AI's
    # off-mesh set and a drop-edge gate's declared set are one list (factory
    # roadmap 173). Read off the same record, converted by the same call.
    for _vl in gp.get("vertical_links", []) or []:
        _link = _vl.get("nav_link")
        if _link:
            imp.nav.add_off_mesh_link(_link, "deli_counter", _up)
'''
LOT_OLD = '''    for _lad in gp.get("ladders", []) or []:
        _link = _lad.get("nav_link")
        if _link:
            imp.nav.add_off_mesh_link(_link, "lot", _up)
'''
LOT_NEW = '''    for _lad in gp.get("ladders", []) or []:
        _link = _lad.get("nav_link")
        if _link:
            imp.nav.add_off_mesh_link(_link, "lot", _up)
    # DECLARED DROPS (Deli Counter 0.226.0, moved into site space by Lot
    # 0.125.0): read off the vertical links as the ladders' are, in THIS
    # importer too -- the one a site mission runs (0.5.1's lesson).
    for _vl in gp.get("vertical_links", []) or []:
        _link = _vl.get("nav_link")
        if _link:
            imp.nav.add_off_mesh_link(_link, "lot", _up)
'''

TEST = '''"""A declared drop's off-mesh link reaches the package, from both importers (0.5.3, factory roadmap 173).

Run: python -m pytest tests/test_drop_links.py -q
"""
import json
from types import SimpleNamespace

from dispatch.importers import deli_counter as dc_imp
from dispatch.importers import lot as lot_imp
from dispatch.navgraph import NavGraph

#: The link Deli Counter 0.226.0 files on deli_a01's floor hole, verbatim (building frame, z up).
DROP = {
    "id": "deli_a01_floor_hole_1_8_-4_navlink",
    "start_position": [8.0, -4.0, 3.3],
    "end_position": [8.0, -4.0, 0.0],
    "bidirectional": False,
    "cost": 4.0,
    "agent_types": ["player", "ai_humanoid"],
    "required_capability": "drop",
    "access_state": "open",
    "reservation_state": "free",
    "hole": [[7.25, -4.75], [8.75, -3.25]],
}


def test_the_payload_survives_verbatim_and_is_one_way():
    g = NavGraph()
    g.add_off_mesh_link(dict(DROP), "deli_counter", "z")
    got = g.links[0]
    assert got["id"] == "deli_counter:deli_a01_floor_hole_1_8_-4_navlink"
    assert got["bidirectional"] is False and got["required_capability"] == "drop"
    assert got["hole"] == DROP["hole"]
    assert got["start_position"][1] - got["end_position"][1] == 3.3     # z up became y up: the fall is 3.3 m


def _files(tmp_path, prefix, gp, extra):
    (tmp_path / f"{prefix}.gameplay.json").write_text(json.dumps(gp), encoding="utf-8")
    (tmp_path / f"{prefix}.nav_hints.json").write_text(json.dumps({"up_axis": "z", "nodes": [], "links": []}), encoding="utf-8")
    (tmp_path / f"{prefix}.glb").write_bytes(b"")
    files = {f"{prefix}.gameplay.json": tmp_path / f"{prefix}.gameplay.json",
             f"{prefix}.nav_hints.json": tmp_path / f"{prefix}.nav_hints.json",
             f"{prefix}.glb": tmp_path / f"{prefix}.glb"}
    files.update(extra)
    return files


def test_the_deli_counter_importer_reads_a_drop(tmp_path):
    gp = {"up_axis": "z", "anchors": [], "props": [], "ladders": [],
          "vertical_links": [{"kind": "stair"}, {"kind": "floor_hole", "story": 1, "x": 8.0, "y": -4.0, "nav_link": dict(DROP)}]}
    rt = SimpleNamespace(files=_files(tmp_path, "shell", gp, {}), manifest=gp, schema="deli_counter.gameplay.v1")
    imp = dc_imp.load(rt)
    ids = [l["id"] for l in imp.nav.links]
    assert ids == ["deli_counter:deli_a01_floor_hole_1_8_-4_navlink"], ids


def test_the_lot_importer_reads_a_drop(tmp_path):
    gp = {"up_axis": "z", "anchors": [], "props": [], "interactives": [], "ladders": [],
          "vertical_links": [{"kind": "hatch", "story": 1, "x": -12.0, "y": 8.0, "building": "deli_a01",
                              "nav_link": dict(DROP, id="deli_a01_hatch_1_-12_8_navlink")}]}
    layout = {"up_axis": "z"}
    (tmp_path / "lot.layout.json").write_text(json.dumps(layout), encoding="utf-8")
    files = _files(tmp_path, "lot", gp, {"lot.layout.json": tmp_path / "lot.layout.json"})
    rt = SimpleNamespace(files=files, manifest=layout, schema="lot.layout.v1")
    imp = lot_imp.load(rt)
    ids = [l["id"] for l in imp.nav.links]
    assert ids == ["lot:deli_a01_hatch_1_-12_8_navlink"], ids
    assert imp.nav.links[0]["source"] == "lot"
'''

CHANGELOG = '''## v0.5.3 — 2026-10-16

**A declared drop's off-mesh link reaches the package.** Deli Counter 0.226.0 files a one-way `nav_link` on
every `floor_hole` / `hatch` vertical link (factory roadmap 173: "a drop is either guarded or declared"), and
Lot 0.125.0 moves it into site space. Both importers here carried a ladder's link and read nothing off a
vertical link, so `navigation_hints.json` `links[]` held the climbs and none of the drops -- cold run 9317's
package: 2 links, both ladders, while its deli declares a floor hole and a hatch. Now both importers read
`vertical_links[].nav_link` as they read `ladders[].nav_link`; `NavGraph.add_off_mesh_link` namespaces and
converts it and the payload rides verbatim (`required_capability` "drop", `bidirectional` false, `hole`: the
cut's rect, for a gate that asks which rim is declared). `tests/test_drop_links.py` runs both importers on a
minimal package.

'''


def write_tests():
    (DP / "tests" / "test_drop_links.py").write_text(TEST, encoding="utf-8")
    print("wrote dispatch/tests/test_drop_links.py")


def main(argv):
    if "--tests" in argv:
        write_tests()
        return 0
    _apply(DP / "dispatch" / "importers" / "deli_counter.py", DC_OLD, DC_NEW)
    _apply(DP / "dispatch" / "importers" / "lot.py", LOT_OLD, LOT_NEW)
    v = DP / "VERSION"
    assert v.read_text(encoding="utf-8").strip() == "0.5.2", v.read_text(encoding="utf-8")
    v.write_bytes(b"0.5.3" + bytes([10]))      # LF, as the file was; write_text would give CRLF on Windows
    _apply(DP / "dispatch" / "__init__.py", '__version__ = "0.5.2"\n', '__version__ = "0.5.3"\n')
    cl = DP / "CHANGELOG.md"
    raw = cl.read_bytes()
    eol = "\r\n" if raw.count(b"\r\n") else "\n"
    text = raw.decode("utf-8")
    head = "# Changelog\n\n".replace("\n", eol)
    assert text.startswith(head), text[:30]
    cl.write_bytes((head + CHANGELOG.replace("\n", eol) + text[len(head):]).encode("utf-8"))
    write_tests()
    print("Dispatch 0.5.3 applied: both importers read a declared drop's nav link, test, VERSION, CHANGELOG")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
