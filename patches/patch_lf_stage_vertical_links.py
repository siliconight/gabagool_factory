"""Level Factory 0.216.1: the Dispatch staging carries VERTICAL LINKS, so a declared drop's off-mesh link ships.

FOUND BY 0.216.0'S OWN GATE ON ITS FIRST EXPORT. Cold run 9320 (urban_row_001, seed 9104, on Deli Counter
0.226.0 + Lot 0.125.0 + Dispatch 0.5.3 + Level Factory 0.216.0) STOPPED at the export: the drop-edge census
refused the package on 20 undeclared rows at deli_a01's floor hole -- "0 at a declared drop" -- though the chain
was built, the session before, to declare exactly that hole. Traced rather than guessed, hop by hop:

    deli_counter/build/deli_a01.gameplay.json         vertical_links: a floor_hole's and a hatch's nav_link  OK
    lot_assemble .../seed_9104/1/out/site.site.gameplay.json   the same, nav_link in site space (Lot 0.125.0)  OK
    .../temp/urban_row_001/dispatch_inputs/lot/lot.gameplay.json   no `vertical_links` KEY AT ALL
    .../dispatch_handoff/1/out/navigation_hints.json   links: the two ladders' only

`stage_dispatch_inputs` projects each gameplay manifest into a literal dict whose keys are `schema, license,
up_axis, anchors, props, interactives, ladders`; Dispatch 0.5.3's two importers read `up_axis, anchors, props,
interactives, ladders, vertical_links` (`dispatch/importers/lot.py`, `deli_counter.py`, read for this patch).
`vertical_links` is the one they read that the staging never wrote. It is the ladders' failure one record over
-- claimed end to end and stopped here, twice, on cold runs 9075 and 9076 (`patch_lf_stage_ladders.py`, roadmap
172) -- and it was claimed a third time in the factory's 02c1b06 ("the declared set now ships in the package")
without a package that showed it.

What it changes (anchored; refuses on a miss; LF-safe and CRLF-safe):
  * packages/staging/dispatch_inputs.py -- `vertical_links` verbatim on the deli_counter side and the lot side,
    beside `ladders`, by the ladders' rule (re-projecting geometry here is how a nav link and a route node end up
    disagreeing about where one thing is).
  * tests/unit/test_drop_links_staged.py (new) -- both sides carry the deli's three vertical links verbatim (the
    floor hole's and the hatch's nav links, the descriptive stair link with them), a site that carries its
    buildings stages none from the generated shell, and both staged manifests carry every key Dispatch 0.5.3
    reads (the contract, written down where the next silent drop would be caught).
  * VERSION 0.216.0 -> 0.216.1, CHANGELOG.

    python patches/patch_lf_stage_vertical_links.py --tests   # the test file only (prove it fails first)
    python patches/patch_lf_stage_vertical_links.py           # everything
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
LF = ROOT / "level_factory"


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


DELI_OLD = '''        "ladders": list(dc_gp.get("ladders", []) or []),
    }, indent=2), encoding="utf-8")
    (deli_dir / "shell.nav_hints.json").write_text(
'''
DELI_NEW = '''        "ladders": list(dc_gp.get("ladders", []) or []),
        # VERTICAL LINKS, by the same rule (0.216.1, factory roadmap 173): a
        # floor_hole / hatch vertical link carries a one-way off-mesh
        # `nav_link` (Deli Counter 0.226.0), and Dispatch 0.5.3's importer
        # reads it off this record as it reads a ladder's.
        "vertical_links": list(dc_gp.get("vertical_links", []) or []),
    }, indent=2), encoding="utf-8")
    (deli_dir / "shell.nav_hints.json").write_text(
'''

LOT_OLD = '''        "ladders": list(lot_gp.get("ladders", []) or []),
    }, indent=2), encoding="utf-8")
    (lot_dir / "lot.layout.json").write_text(json.dumps({
'''
LOT_NEW = '''        "ladders": list(lot_gp.get("ladders", []) or []),
        # VERTICAL LINKS, the same line one record over (0.216.1, factory
        # roadmap 173). Deli Counter 0.226.0 files a one-way off-mesh
        # `nav_link` on every floor_hole / hatch vertical link, Lot 0.125.0
        # moves it into site space, Dispatch 0.5.3's Lot importer reads it --
        # and cold run 9320 shipped the two ladders' links and neither drop's,
        # because this whitelist did not name the key. Found by the export's
        # drop-edge gate, which refused that package on the deli's 20
        # undeclared floor-hole rows.
        "vertical_links": list(lot_gp.get("vertical_links", []) or []),
    }, indent=2), encoding="utf-8")
    (lot_dir / "lot.layout.json").write_text(json.dumps({
'''

TEST = '''"""0.216.1 -- the staging carries VERTICAL LINKS, so a declared drop's off-mesh link reaches Dispatch (factory
roadmap 173).

Found by 0.216.0's own drop-edge gate on its first export (the factory's cold run 9320): it refused the package
on 20 undeclared rows at deli_a01's floor hole. The chain, traced:

    deli_counter/build/deli_a01.gameplay.json        vertical_links: a floor_hole's and a hatch's nav_link
    lot_assemble .../out/site.site.gameplay.json     the same, the nav links in site space (Lot 0.125.0)
    dispatch_inputs/lot/lot.gameplay.json            no `vertical_links` key at all
    navigation_hints.json                            links: the two ladders' only

`stage_dispatch_inputs` projects each gameplay manifest into a whitelist of keys, and a key the whitelist does
not name is dropped exactly as if upstream never sent it -- the ladders' failure twice (roadmap 172, cold runs
9075 and 9076), one record over.

Run: python -m pytest -q tests/unit/test_drop_links_staged.py
"""
import json

from packages.staging.dispatch_inputs import stage_dispatch_inputs

#: What Dispatch 0.5.3's two importers read off a gameplay manifest (`dispatch/importers/lot.py`,
#: `dispatch/importers/deli_counter.py`). A key Dispatch learns to read and this staging does not write is the
#: next silent drop, so the list is the contract: change it when Dispatch's importers change.
DISPATCH_READS = {"up_axis", "anchors", "props", "interactives", "ladders", "vertical_links"}

#: deli_a01's three vertical links as Lot 0.125.0 wrote them into cold run 9320's site (seed 9104): a
#: descriptive stair link, and a floor hole's and a hatch's, each with its one-way nav link in site space.
VERTICAL_LINKS = [
    {"kind": "stair", "role": "main_internal_rotation", "from_story": -1, "to_story": 2, "story": None,
     "x": None, "y": None, "breachable": None, "building": "b0"},
    {"kind": "floor_hole", "role": "vertical_attack_angle", "from_story": None, "to_story": None, "story": 1,
     "x": 8.0, "y": -4.0, "breachable": None, "building": "b0",
     "nav_link": {"id": "deli_a01_floor_hole_1_8_-4_navlink", "start_position": [-43.0, -1.49, 3.3],
                  "end_position": [-43.0, -1.49, 0.0], "bidirectional": False, "cost": 4.0,
                  "agent_types": ["player", "ai_humanoid"], "required_capability": "drop",
                  "access_state": "open", "reservation_state": "free",
                  "hole": [[-44.1, -2.59], [-41.9, -0.39]]}},
    {"kind": "hatch", "role": "roof_drop_to_stair", "from_story": None, "to_story": None, "story": 1,
     "x": -12.0, "y": 8.0, "breachable": True, "building": "b0",
     "nav_link": {"id": "deli_a01_hatch_1_-12_8_navlink", "start_position": [-63.0, 10.51, 3.3],
                  "end_position": [-63.0, 10.51, 0.0], "bidirectional": False, "cost": 4.0,
                  "agent_types": ["player", "ai_humanoid"], "required_capability": "drop",
                  "access_state": "open", "reservation_state": "free",
                  "hole": [[-63.7, 9.81], [-62.3, 11.21]]}},
]
MARKERS = [{"id": "MAIN_W", "type": "door", "building": "b0", "x": -2.4, "y": -13.0, "z": 0.0}]


def _stage(tmp_path, dc, lot):
    deli = tmp_path / "shell.gameplay.json"
    deli.write_text(json.dumps(dc), encoding="utf-8")
    gp = tmp_path / "site.site.gameplay.json"
    gp.write_text(json.dumps(lot), encoding="utf-8")
    stage = tmp_path / "stage"
    stage_dispatch_inputs(stage, deli_gameplay=deli, shell_glb=tmp_path / "shell.glb",
                          lot_gameplay=gp, mission_id="m")
    read = lambda p: json.loads((stage / p).read_text(encoding="utf-8"))  # noqa: E731
    return read("deli_counter/shell.gameplay.json"), read("lot/lot.gameplay.json")


def test_the_sites_vertical_links_reach_dispatchs_lot_input(tmp_path):
    _dc, lot = _stage(tmp_path, {"up_axis": "z"},
                      {"up_axis": "z", "markers": MARKERS, "vertical_links": VERTICAL_LINKS})
    assert lot["vertical_links"] == VERTICAL_LINKS
    drops = [v["nav_link"]["id"] for v in lot["vertical_links"] if "nav_link" in v]
    assert drops == ["deli_a01_floor_hole_1_8_-4_navlink", "deli_a01_hatch_1_-12_8_navlink"]


def test_a_lone_shells_vertical_links_reach_dispatchs_deli_input(tmp_path):
    # a site with no markers to stand in for the shell: the shell side is staged, and its links with it
    dc, _lot = _stage(tmp_path, {"up_axis": "z", "vertical_links": VERTICAL_LINKS}, {"up_axis": "z"})
    assert dc["vertical_links"] == VERTICAL_LINKS


def test_a_site_that_carries_its_buildings_stages_none_from_the_generated_shell(tmp_path):
    # the anchors' rule (0.158.0): the shell's records, in the shell's own frame, would duplicate the site's
    dc, lot = _stage(tmp_path, {"up_axis": "z", "vertical_links": VERTICAL_LINKS},
                     {"up_axis": "z", "markers": MARKERS, "vertical_links": VERTICAL_LINKS})
    assert dc["vertical_links"] == [] and lot["vertical_links"] == VERTICAL_LINKS


def test_the_staged_manifests_carry_every_key_dispatch_reads(tmp_path):
    dc, lot = _stage(tmp_path, {"up_axis": "z"}, {"up_axis": "z", "markers": MARKERS})
    assert DISPATCH_READS <= set(dc), sorted(DISPATCH_READS - set(dc))
    assert DISPATCH_READS <= set(lot), sorted(DISPATCH_READS - set(lot))
'''

CHANGELOG = '''## [0.216.1] - the declared drops reach Dispatch: the staging carries vertical links

**Found by 0.216.0's own gate on its first export** (the factory's cold run 9320). The drop-edge census refused
the package on 20 undeclared rows at deli_a01's floor hole, "0 at a declared drop", though Deli Counter 0.226.0
records that hole's one-way nav link and Lot 0.125.0 moves it into site space. Lot's `site.site.gameplay.json`
carried it. `packages/staging/dispatch_inputs.py` writes Dispatch's inputs from a whitelist of keys that did
not name `vertical_links`, so Dispatch 0.5.3's importers, which read them, found none. The package's
`navigation_hints.json` carried the two ladders' links and neither drop's. It is the seam the ladders crossed
twice (cold runs 9075 and 9076, factory roadmap 172), one record over.

### Fixed
- `stage_dispatch_inputs` carries `vertical_links` verbatim on the deli_counter side and the lot side, beside
  `ladders`.
- `tests/unit/test_drop_links_staged.py` (4, all fail on 0.216.0): both sides carry the deli's three vertical
  links verbatim; a site that carries its buildings stages none from the generated shell; and both staged
  manifests carry every key Dispatch 0.5.3's importers read, written down as the contract.

'''


def write_tests():
    (LF / "tests" / "unit" / "test_drop_links_staged.py").write_text(TEST, encoding="utf-8", newline="\n")
    print("wrote level_factory/tests/unit/test_drop_links_staged.py")


def main(argv):
    if "--tests" in argv:
        write_tests()
        return 0
    st = LF / "packages" / "staging" / "dispatch_inputs.py"
    _apply(st, DELI_OLD, DELI_NEW)
    _apply(st, LOT_OLD, LOT_NEW)
    v = LF / "VERSION"
    assert v.read_text(encoding="utf-8").strip() == "0.216.0", v.read_text(encoding="utf-8")
    v.write_text("0.216.1", encoding="utf-8")
    cl = LF / "CHANGELOG.md"
    rawc = cl.read_bytes()
    eol = "\r\n" if rawc.count(b"\r\n") else "\n"
    text = rawc.decode("utf-8")
    assert text.startswith("## [0.216.0]"), text[:40]
    cl.write_bytes((CHANGELOG.replace("\n", eol) + text).encode("utf-8"))
    write_tests()
    print("Level Factory 0.216.1 applied: vertical_links staged on both sides, test, VERSION, CHANGELOG")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
