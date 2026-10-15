"""Roadmap 170, step 1, second cut: the roof hatch through the two compose gates -- Zoo 1.113.1 + Deli Counter 0.224.1.

Cold run 9315 (precinct_yard_001, the first with the hatch) stopped at the art pass on two blockers from
`presentation_compose`, both on the buildings that carry a roof hatch (courthouse_a02, airport_terminal_a01):

- **The placement gate** (`portable_building.verify_placement`, tolerance 0.25 m) measures a module's WHOLE
  visual footprint against its greybox slot. The open lid, 100 degrees on its hinge and leaning out past the
  curb, read `placed [1.668, 1.835, 1.987]` against `greybox [1.66, 0.2, 1.66]`: 0.33 m outside. The fix is the
  species': the lid stands vertical (90 degrees) on a hinge set 4 cm inside the back wall, its edges 5 mm inside
  the curb's planes, so the open module's footprint is the curb's and no face of the lid lies on a curb plane.
- **The circulation gate** (`circulation.check_shell`) found the hatch's own greybox box 0.2 m inside
  `ladder:ladder_0`'s climb volume. It is inside by construction -- the climber comes up THROUGH the hatch -- as a
  stair's guard stands at its own hole's edge, which the gate already excuses (0.191.0). The hatch gets the same
  excusal for ladder volumes, listed as excused; in a doorway or a stair's column it is a prop like any other.

Also: `roof_hatch.py` joins `build_freshness.GEOMETRY_SOURCES` (it emits slots, so editing it must demand a
rebuild). Every anchor is asserted once and every touched file is pinned by sha16.

    python patches/patch_roof_hatch_gates.py
    (cd zoo && blender -b --python tools/coplanar_census.py -- --species roof_hatch bollard)   then the suites
"""
import hashlib
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
ZOO = ROOT / "zoo"
DC = ROOT / "deli_counter"

SHA = {
    ZOO / "zoo_keeper/recipes/roof_hatch.py": "14b132b3691b031f",
    ZOO / "zoo_keeper/genome/species/roof_hatch.json": "a1419c36a25c04ee",
    ZOO / "CHANGELOG.md": "e54f8da6bbc39690",
    ZOO / "VERSION": "a459f7b477630473",
    DC / "circulation.py": "66ffd747e1c7eae8",
    DC / "build_freshness.py": "98d2a62503ab7be5",
    DC / "test_circulation.py": "8fd0408222499757",
    DC / "CHANGELOG.md": "f90de91685b049ed",
    DC / "VERSION": "1cad70001bfbf4c2",
}

ZOO_CHANGELOG = """## [1.113.1] - the lid stands vertical, inside the curb's footprint

**Cold run 9315, the first with a roof hatch, stopped at the art pass** on Deli Counter's placement gate: it
measures a module's whole visual footprint against its greybox slot (`verify_placement`, 0.25 m), and the lid
at 100 degrees -- past vertical, leaning out over the curb's back -- read `placed [1.668, 1.835, 1.987]` against
`greybox [1.66, 0.2, 1.66]` on courthouse_a02, 0.33 m outside.

### Changed
- **`roof_hatch`'s open lid stands at 90 degrees**, the way a hold-open arm holds a scuttle lid, on a hinge set
  `HINGE_IN` 4 cm inside the back wall's outer face; the plate's edges stop `LIP` 5 mm inside the curb's outer
  planes. So the open module's footprint is the curb's (the hinge rod's 1.8 cm radius is all that passes it,
  inside the gate's tolerance), and no face of the lid, open or closed, lies on a plane of the curb: standing,
  its faces sit 5 mm and 20 mm off the curb's back wall's; closed, its edges are 5 mm inside the curb's rim.
  The census re-run is recorded in `tests/test_coincident_faces.py`.

"""

DC_CHANGELOG = """## [0.224.1] - the hatch is its ladder's own furniture

**Cold run 9315, the first with a roof hatch, stopped at the art pass** on the circulation gate: the hatch's own
greybox box stood 0.2 m inside `ladder:ladder_0`'s climb volume on courthouse_a02 and airport_terminal_a01
(`circulation_check`, shell arm). It stands there by construction -- the climber comes up THROUGH the hatch --
as a stair's guard stands at its own hole's edge, which the gate has excused since 0.191.0.

### Changed
- **`circulation.check_shell` excuses a `roof_hatch_*` prop in a ladder's climb volume** (`HATCH_PREFIX`), and
  lists it as excused so a reader sees what was not counted; in a doorway or a stair's column it is a prop like
  any other. The two excusals are one function now, `excused_own_furniture`, and `test_circulation.py` pins
  it: the hatch in its ladder's volume and the guard in its stair's are excused, the same hatch in a doorway and
  a crate in the ladder's volume are not.
- **`roof_hatch.py` is a geometry source** (`build_freshness.GEOMETRY_SOURCES`): it emits slots, so editing it
  demands the rebuild the freshness gate exists to demand.

The placement gate's finding on the same buildings -- the open lid's footprint 0.33 m past the slot -- is Zoo
1.113.1's.

"""

EDITS = [
    # --- Zoo: the recipe ----------------------------------------------------------------------------------
    (ZOO / "zoo_keeper/recipes/roof_hatch.py",
     "OPEN_DEG = 100.0     # the lid's angle from flat when open: past vertical, leaning out\n"
     "HINGE_R = 0.018      # m; the hinge rod\n",
     "OPEN_DEG = 90.0      # the lid's angle from flat when open: vertical, inside the curb's footprint\n"
     "HINGE_R = 0.018      # m; the hinge rod\n"
     "HINGE_IN = 0.04      # m; the hinge line sits this far inside the back wall's outer face\n"
     "LIP = 0.005          # m; the lid's edges stop this short of the curb's outer planes\n"),
    (ZOO / "zoo_keeper/recipes/roof_hatch.py",
     "- `open`: the lid stands on its hinge at OPEN_DEG, past vertical and leaning away from the opening,\n"
     "  the way a hold-open arm keeps a real scuttle lid. The climber comes up through the hole and steps\n",
     "- `open`: the lid stands vertical on its hinge (OPEN_DEG 90), the way a hold-open arm holds a real\n"
     "  scuttle lid, INSIDE the curb's footprint: Deli Counter's placement gate measures a module's whole\n"
     "  footprint against its slot (0.25 m), and a lid leaning 10 degrees past vertical stood 0.33 m\n"
     "  outside it on cold run 9315. The climber comes up through the hole and steps\n"),
    (ZOO / "zoo_keeper/recipes/roof_hatch.py",
     "    # THE LID: a plate the curb's own size, resting on the curb's top -- sunk SKIRT into it, the\n"
     "    # way a Zoo floater rests (core.floaters), so no face of it is coincident with the curb's --\n"
     "    # and hinged along the back top edge. Closed, it stands LID_T above the slot: art above the\n"
     "    # curb, which is the fit.\n"
     "    lid_w, lid_d = w, d\n"
     "    lid_z = h / 2.0 - SKIRT + LID_T / 2.0                     # the plate's centre, closed\n"
     "    hinge = (0.0, -d / 2.0, h / 2.0 - SKIRT)                 # the hinge line, along local X\n"
     "    bm = geometry.new_bm()\n"
     "    verts = geometry.add_box(bm, (0.0, 0.0, lid_z), (lid_w, lid_d, LID_T))\n"
     "    if state == \"open\":\n"
     "        # swing the plate about the hinge line by OPEN_DEG: its far (+Y) edge rises and, past\n"
     "        # 90 degrees, leans back over the curb's outside, clear of the opening\n",
     "    # THE LID: a plate across the curb's top, resting on it -- sunk SKIRT into it, the way a Zoo\n"
     "    # floater rests (core.floaters) -- hinged along a line HINGE_IN inside the back wall's outer\n"
     "    # face, its edges LIP inside the curb's outer planes. So no face of it lies on a plane of the\n"
     "    # curb, closed or standing, and standing it stays inside the curb's footprint, which is what\n"
     "    # Deli Counter's placement gate measures. Closed, it stands LID_T above the slot: art above\n"
     "    # the curb, which is the fit.\n"
     "    lid_w = w - 2 * LIP\n"
     "    y_back, y_front = -d / 2.0 + HINGE_IN, d / 2.0 - LIP\n"
     "    lid_d = y_front - y_back\n"
     "    lid_z = h / 2.0 - SKIRT + LID_T / 2.0                     # the plate's centre, closed\n"
     "    hinge = (0.0, y_back, h / 2.0 - SKIRT)                   # the hinge line, along local X\n"
     "    bm = geometry.new_bm()\n"
     "    verts = geometry.add_box(bm, (0.0, (y_back + y_front) / 2.0, lid_z), (lid_w, lid_d, LID_T))\n"
     "    if state == \"open\":\n"
     "        # swing the plate about the hinge line by OPEN_DEG: its far (+Y) edge rises until the\n"
     "        # plate stands on the hinge, its thickness over the back wall, clear of the opening\n"),
    (ZOO / "zoo_keeper/recipes/roof_hatch.py",
     "    else:\n"
     "        lid_box = ((-lid_w / 2.0, -lid_d / 2.0, lid_z - LID_T / 2.0),\n"
     "                   (lid_w / 2.0, lid_d / 2.0, lid_z + LID_T / 2.0))\n",
     "    else:\n"
     "        lid_box = ((-lid_w / 2.0, y_back, lid_z - LID_T / 2.0),\n"
     "                   (lid_w / 2.0, y_front, lid_z + LID_T / 2.0))\n"),
    (ZOO / "zoo_keeper/genome/species/roof_hatch.json",
     "`open` (the default) stands it up past vertical on its back hinge, clear of the climber",
     "`open` (the default) stands it up vertical on its back hinge, inside the curb's footprint and clear of "
     "the climber"),
    # Applied by hand after the census ran (the figures are the census's), same text:
    (ZOO / "tests/test_coincident_faces.py",
     "#: record is the factory's `patches/roof_hatch/census.log`.\nCENSUS_BUILDS = 402",
     "#: record is the factory's `patches/roof_hatch/census.log`. 1.113.1 stood the\n"
     "#: lid vertical on a hinge 4 cm inside the back wall, its edges 5 mm inside the\n"
     "#: curb's planes (the placement gate's footprint): re-run the same way, the\n"
     "#: same 260 / 260 / 260 tris and 0 pairs, the bollard its 2 / 2 / 1\n"
     "#: (`patches/roof_hatch/census_1131.log`).\nCENSUS_BUILDS = 402"),
    (ZOO / "VERSION", "1.113.0", "1.113.1"),
    (ZOO / "CHANGELOG.md", "## [1.113.0] - a roof hatch: the curb and lid around a ladder's opening",
     ZOO_CHANGELOG + "## [1.113.0] - a roof hatch: the curb and lid around a ladder's opening"),
    # --- Deli Counter -------------------------------------------------------------------------------------
    (DC / "circulation.py",
     "GUARD_PREFIX = \"stair_guard_\"\n",
     "GUARD_PREFIX = \"stair_guard_\"\n"
     "\n"
     "#: `roof_hatch.py` (0.224.0) stands a ``roof_hatch_{x}_{y}`` prop -- the curb and lid\n"
     "#: around a roof ladder's opening -- on the ladder's own hatch, inside its climb\n"
     "#: volume by construction: the climber comes up THROUGH it. Cold run 9315's compose\n"
     "#: read it 0.2 m inside `ladder:ladder_0` on both buildings that carry one. It is\n"
     "#: EXCUSED from ladder volumes and listed as such (0.224.1); in a doorway or a\n"
     "#: stair's column it is a prop like any other. Not linked to its own ladder, as the\n"
     "#: guard is not to its stair.\n"
     "HATCH_PREFIX = \"roof_hatch_\"\n"),
    (DC / "circulation.py",
     "    props = shell_prop_boxes(shell_glb, gameplay)\n"
     "    vols = circulation_volumes(slots_manifest, gameplay)\n"
     "    found = prop_conflicts(props, vols)\n"
     "    # A stair's guard at its own hole's edge (`GUARD_PREFIX`): excused from\n"
     "    # stair volumes, and returned, so a reader sees what was not counted.\n"
     "    excused = [c for c in found if c[\"prop\"].startswith(GUARD_PREFIX)\n"
     "               and c[\"volume\"].startswith(\"stair:\")]\n"
     "    conflicts = [c for c in found if c not in excused]\n",
     "    props = shell_prop_boxes(shell_glb, gameplay)\n"
     "    vols = circulation_volumes(slots_manifest, gameplay)\n"
     "    found = prop_conflicts(props, vols)\n"
     "    excused, conflicts = excused_own_furniture(found)\n"),
    (DC / "circulation.py",
     "def check_shell(shell_glb, slots_manifest, gameplay):\n",
     "def excused_own_furniture(found):\n"
     "    \"\"\"``(excused, conflicts)``: the conflicts that are a volume's own furniture, and the rest.\n"
     "\n"
     "    A stair's guard at its own hole's edge (`GUARD_PREFIX`) is excused from stair\n"
     "    volumes; a roof hatch's curb and lid (`HATCH_PREFIX`) from ladder volumes. Both are\n"
     "    returned, so a reader sees what was not counted. Order is `found`'s.\n"
     "    \"\"\"\n"
     "    excused = [c for c in found\n"
     "               if (c[\"prop\"].startswith(GUARD_PREFIX) and c[\"volume\"].startswith(\"stair:\"))\n"
     "               or (c[\"prop\"].startswith(HATCH_PREFIX) and c[\"volume\"].startswith(\"ladder:\"))]\n"
     "    return excused, [c for c in found if c not in excused]\n"
     "\n"
     "\n"
     "def check_shell(shell_glb, slots_manifest, gameplay):\n"),
    (DC / "build_freshness.py",
     "    # where a walk-up's fire escape stands, a storey a slot (0.220.0)\n"
     "    \"fire_escape_stack.py\",\n",
     "    # where a walk-up's fire escape stands, a storey a slot (0.220.0)\n"
     "    \"fire_escape_stack.py\",\n"
     "    # the roof hatch slot and its interactive, one per hatch link on the roof (0.224.0)\n"
     "    \"roof_hatch.py\",\n"),
    (DC / "test_circulation.py",
     "def test_a_stair_without_endpoints_keeps_the_full_column():\n"
     "    assert C.stair_column(_stair(floors_served=[0, 1])) == (-1e6, 1e6)\n"
     "    vols = dict(C.circulation_volumes({}, {\"stair_systems\": [_stair()]}))\n"
     "    assert vols[\"stair:stair_0\"][1][2] == 1e6\n",
     "def test_a_stair_without_endpoints_keeps_the_full_column():\n"
     "    assert C.stair_column(_stair(floors_served=[0, 1])) == (-1e6, 1e6)\n"
     "    vols = dict(C.circulation_volumes({}, {\"stair_systems\": [_stair()]}))\n"
     "    assert vols[\"stair:stair_0\"][1][2] == 1e6\n"
     "\n"
     "\n"
     "# ---- a roof hatch stands in its own ladder's climb volume (0.224.1) ---------\n"
     "#\n"
     "# `roof_hatch.py` stands the curb and lid on the ladder's own hatch; the climber\n"
     "# comes up through it. Cold run 9315's compose read it 0.2 m inside\n"
     "# `ladder:ladder_0` on both buildings that carry one. Excused from LADDER\n"
     "# volumes and said to be, as the guard is from its stair's; anywhere else a\n"
     "# prop like any other.\n"
     "\n"
     "def test_a_roof_hatch_in_its_ladders_volume_is_excused_and_said():\n"
     "    found = [{\"prop\": \"roof_hatch_13_-9\", \"volume\": \"ladder:ladder_0\", \"penetration\": 0.2},\n"
     "             {\"prop\": \"roof_hatch_13_-9\", \"volume\": \"doorway:w_open0\", \"penetration\": 0.3},\n"
     "             {\"prop\": \"crate_stack_2\", \"volume\": \"ladder:ladder_0\", \"penetration\": 0.4},\n"
     "             {\"prop\": \"stair_guard_back_1\", \"volume\": \"stair:s0\", \"penetration\": 0.26},\n"
     "             {\"prop\": \"stair_guard_back_1\", \"volume\": \"ladder:ladder_0\", \"penetration\": 0.1}]\n"
     "    excused, conflicts = C.excused_own_furniture(found)\n"
     "    assert [(c[\"prop\"], c[\"volume\"]) for c in excused] == [\n"
     "        (\"roof_hatch_13_-9\", \"ladder:ladder_0\"), (\"stair_guard_back_1\", \"stair:s0\")]\n"
     "    assert [(c[\"prop\"], c[\"volume\"]) for c in conflicts] == [\n"
     "        (\"roof_hatch_13_-9\", \"doorway:w_open0\"), (\"crate_stack_2\", \"ladder:ladder_0\"),\n"
     "        (\"stair_guard_back_1\", \"ladder:ladder_0\")]\n"
     "\n"
     "\n"
     "def test_the_hatch_prefix_is_the_builders():\n"
     "    import roof_hatch\n"
     "    from spec_types import LevelSpec, VerticalLink\n"
     "    s = LevelSpec(name=\"t\", n_stories=2, story_height=3.2)\n"
     "    s.vertical_links = [VerticalLink(kind=\"hatch\", story=2, x=13.0, y=-9.0)]\n"
     "    (slot, _e, _c, _z), = roof_hatch.roof_hatches(s)\n"
     "    assert slot[\"slot_id\"].startswith(C.HATCH_PREFIX)\n"),
    (DC / "VERSION", "Deli Counter 0.224.0", "Deli Counter 0.224.1"),
    (DC / "CHANGELOG.md", "## [0.224.0] - a lid on every roof hatch",
     DC_CHANGELOG + "## [0.224.0] - a lid on every roof hatch"),
]


def sha16(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()[:16]


def main():
    for p, want in SHA.items():
        assert b"\r\n" not in p.read_bytes(), f"{p} is CRLF; the patch assumes LF"
        got = sha16(p)
        assert got == want, f"{p}: sha16 {got} != {want}; re-ground before applying"
    texts = {}
    for p, old, new in EDITS:
        t = texts.get(p) or p.read_text(encoding="utf-8")
        assert t.count(old) == 1, (p.name, old[:70])
        texts[p] = t.replace(old, new)
    for p, t in texts.items():
        p.write_text(t, encoding="utf-8", newline="\n")
    print("roof hatch gates applied: Zoo 1.113.1 + Deli Counter 0.224.1; now the census and both suites")


if __name__ == "__main__":
    sys.exit(main())
