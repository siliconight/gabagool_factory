"""Level Factory 0.219.0: the drop-edge lattice is laid off the round coordinates, so a rounding gap is not a hole
(roadmap 173).

FOUND BY THE BREADTH SWEEP OF 2026-10-19. Cold run 9333 (restaurant_row_001) STOPPED at the export with 0
interventions: `UNDECLARED_DROP_INDOORS: 3 unguarded edge(s)`, a 3.3 m drop from deli_a03's storey-1 floor at site x
-64.25..-64.0, z -9.5..-8.75 -- the west edge of its up-stair's discharge plate. Attributed in the engine on a copy of
the package (`docs/findings/breadth_sweep_2026-10-19/`):

  * the slab collider's cut and the plate's collider are authored flush at deli_a03's local x -13.0, site x -64.0;
  * `probe_at.gd` (roadmap 173's) found every "drop" column cast at exactly x -64.0;
  * rays at x -64.02, -64.01 meet `slab_col_1` at 3.3, at -63.99, -63.98 `stair1col_discharge_0` at 3.3, and at
    -64.00 exactly NEITHER: `slab_col_0`, the ground, at 0.0.

REFUTED, KEPT: "a ray exactly on the line where two flush colliders meet reports neither". They are not flush in the
engine. `seam_floats.py` read the GLB: the slab's cut vertices are stored at x -13.000000953674316, one float32 step
west of -13, and the plate's body sits at local x -11.800000190734863 with a hull 1.2000000476837158 across each way.
`seam_ulps.gd` read the engine: composed with the building's -51, the plate's body lands at site x -62.799999237
(float32 near 63 steps 3.8 um), so its west face is at -63.999999285 and the slab's cut at -64.000000954 -- a 1.7 um
gap straddling x -64.0. A ray there falls through it; rays at the float32 values either side (-64.000007629,
-63.999996185) meet the slab and the plate.

`walkable_edge.gd` casts one ray straight down each cell's lattice point, and the gate's 0.5 m lattice
(`drop_edges.CELL_M`, its extent snapped to it) lands on the round coordinates where Deli Counter's pieces meet --
exactly where float32 rounding opens such gaps. A body is 0.4 m across and cannot fall through 1.7 um. Roadmap 173
had filed the lattice's fragility (its README's "lattice sweep") after one centimetre of grid offset lost a landing.

THE FIX: the lattice itself is laid `SEAM_NUDGE_X` / `SEAM_NUDGE_Z` (3.1 mm, 2.3 mm) off the round coordinates -- one
offset on the grid's origin, after the extent is snapped, so every query the instrument makes asks the moved points:
the column rays and the capsules stood on them, the barrier ray, the block capsule, the sky ray (which decides
indoors, and would read a gap in a roof as open sky), the seed's cell and each link's. Neither offset is a multiple of
0.5 mm, so no query lands on a coordinate a half-millimetre grid holds -- every line of the gate's snapped lattice,
and the round coordinates generated pieces are authored at. Each is more than 35 times the float32 step anywhere
within 1 km of the origin (61 um at most), so a rounding gap at such a coordinate cannot reach a query, and each is
under 2 % of the standing probe's radius (0.20 m), so a cell still asks its own ground. The rows are reported to
0.01 m, where 3 mm does not show; the report records the offset (`lattice_offset_m`).

WHY THE WHOLE LATTICE, AND NOT THE COLUMN RAYS ALONE (the first build of this patch, kept as evidence:
`docs/findings/breadth_sweep_2026-10-19/gate_ab_columns_only/`). The gate's own measure, classify and assert, run on
copies of the sweep's six packages through both instruments (`gate_ab.py`; the old arm reproduced every export's own
scan exactly, the control), changed 38 edge rows. Each was attributed cell by cell (`edge_cells.gd`) to one of four
things a query on a round coordinate does, none of them about the geometry:

  * a rounding gap between colliders authored flush -- the seam, 9333's three undeclared rows and two beside them;
  * a ray lying in a face's plane, which reads that collider or misses it as rounding falls -- a ramp's side read a
    cell east or west (9333, 9332), rail and guard tops stood on because a ray grazed their faces (9333, 9330);
  * a capsule exactly touching a face its own radius from a lattice line, which Godot calls an overlap (there is no
    epsilon) -- two flight sides hidden and a guard's top occupied on 9328's precinct;
  * a hit read a few millimetres along a slope -- the same edge a centimetre apart once rounded (9332, 9333, 9334),
    and one drop of 0.501 against 0.500 (9330), a threshold toss.

The third reached the block capsule and the barrier ray, which the first build left on the lattice; moving the
origin takes every query off it at once. Measured the same way, this build's every count and row equals the first
build's on all six packages (`gate_ab/`, `ab_table.out.txt`): the barrier ray and the block capsule moved and changed
nothing measurable there. 684 of 685 "steep surfaces" on 9333's package were a fifth artefact that
changed no row: zero-normal hits on sidewalk boxes wherever a lattice line runs along a box's side (`steep_hits.gd`).
Read off Godot's box code, not measured: a ray starting inside a box exactly on its side is outside to the box's
strict point test, so the box reports a hit at the ray's start with no normal. (First written "a quarter-turned
sidewalk box"; sidewalk_0R_0, unturned, carries 12 of them -- corrected, the docstring only.) The other
packages' steep counts fell the same way (9328 1,815 to 5, 9330 36 to 0, 9331 48 to 0, 9334 36 to 0; 9332 6 and 6)
and were not probed one by one.

What it changes (anchored; the file pinned by hash; nothing written on a miss; LF-safe):
  * assets/godot/walkable_edge.gd -- the two constants, and the grid's origin moved by them in `_run`.
  * tests/unit/test_edge_seam.py (new, 1; fails on 0.218.2, Godot-required): deli_a03's seam rebuilt from its own
    floats over a ground plane -- a trimesh slab whose cut is stored at -13.000000953674316 and a convex plate whose
    body sits at -11.800000190734863, both under a building at -51 -- reads no drop along the seam, and the plate's
    far rim, which the flood reaches only across the seam, is still found.
  * VERSION 0.218.2 -> 0.219.0, CHANGELOG.

The factory root's `tools/walkable_edge.gd`, identical to this file before the change, takes the same edit in the
root's commit, so the instrument and the gate stay one file.

    python patches/patch_lf_edge_seam.py --tests   # the test file only (prove it fails first)
    python patches/patch_lf_edge_seam.py           # everything; the test again when it is this patch's
"""
import hashlib
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
LF = ROOT / "level_factory"
EDGE = LF / "assets" / "godot" / "walkable_edge.gd"
EDGE_SHA = "878f755daa9521ae"

CONST_OLD = "const MAX_ROWS := 200000\n"
CONST_NEW = (
    "const MAX_ROWS := 200000\n"
    "#: TWO PIECES AUTHORED FLUSH ARE NOT FLUSH IN FLOAT32 (Level Factory 0.219.0,\n"
    "#: the factory's roadmap 173). deli_a03's stair cut and its discharge plate\n"
    "#: meet at local x -13.0, a line of the gate's 0.5 m lattice; the cut is\n"
    "#: stored one float32 step west of it and the plate's body composes a step\n"
    "#: east, a 1.7 um gap straddling x -64.0. A ray cast there falls through to\n"
    "#: the floor below, and cold run 9333's export refused three such \"drops\"\n"
    "#: (rays a float32 step either side meet the slab and the plate). The\n"
    "#: lattice is laid these offsets off the round coordinates (in `_run`), so\n"
    "#: no query -- ray or capsule -- lands where pieces meet: not multiples of\n"
    "#: 0.5 mm; over 35 float32 steps within 1 km of the origin; and a body is\n"
    "#: wider than a gap.\n"
    "const SEAM_NUDGE_X := 0.0031\n"
    "const SEAM_NUDGE_Z := 0.0023\n"
)

BOX_OLD = (
    "\t\tbox = AABB(Vector3(x0, box.position.y, z0), Vector3(x1 - x0, box.size.y, z1 - z0))\n"
    "\n"
    "\tvar space: PhysicsDirectSpaceState3D = root.world_3d.direct_space_state\n"
)
BOX_NEW = (
    "\t\tbox = AABB(Vector3(x0, box.position.y, z0), Vector3(x1 - x0, box.size.y, z1 - z0))\n"
    "\t# THE LATTICE IS LAID OFF THE ROUND COORDINATES (0.219.0; SEAM_NUDGE\n"
    "\t# above), bounded or not: every query below -- the column rays and the\n"
    "\t# capsules stood on them, the barrier ray, the block capsule, the sky ray,\n"
    "\t# the seed's cell and each link's -- asks points this far off the lines\n"
    "\t# pieces meet on. The first build moved the column and sky rays alone, and\n"
    "\t# a capsule standing exactly its radius from a face on a lattice line still\n"
    "\t# touched it, which Godot calls an overlap. Rows are reported to 0.01 m,\n"
    "\t# where the offset does not show.\n"
    "\tbox.position += Vector3(SEAM_NUDGE_X, 0.0, SEAM_NUDGE_Z)\n"
    "\treport[\"lattice_offset_m\"] = [SEAM_NUDGE_X, SEAM_NUDGE_Z]\n"
    "\n"
    "\tvar space: PhysicsDirectSpaceState3D = root.world_3d.direct_space_state\n"
)

TEST = r'''"""A seam is not a hole: the drop-edge lattice is laid off the round coordinates (0.219.0, the factory's roadmap 173).

Cold run 9333's export refused three "drops" on deli_a03's storey-1 floor. Its slab's cut and its stair's discharge
plate are authored flush on the gate's 0.5 m lattice, site x -64.0, and are not flush in float32: the cut is stored at
local x -13.000000953674316, and the plate's body, at local -11.800000190734863 under the building's -51, composes to
-62.799999237, so a 1.7 um gap straddles x -64.0 and a ray cast exactly there fell through it to the ground (the
factory's docs/findings/breadth_sweep_2026-10-19/seam_ulps.gd). This rebuilds that seam from those floats -- a trimesh
slab and a convex plate, as the GLB's -colonly and -convcolonly nodes import -- over a ground plane, and runs the real
instrument through a real Godot at the gate's own cell: nothing may drop along the seam, and the plate's far rim,
which the flood reaches only across the seam, must still be found.

Skipped where no Godot is installed (`LF_GODOT`, then `DC_GODOT`, then `LOT_GODOT`, then the usual Windows path).
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from packages.exporting import drop_edges as D  # noqa: E402

EDGE = D.EDGE_SCRIPT  # the very file the export's gate runs, at its cell
NEAR = D.CELL_M / 2 + 0.01  # an edge row sits at the midpoint of two cells, so within half a cell of its line

# deli_a03's own floats, as its GLB stores them (glTF frame, metres; site x = building x + local x)
BUILDING_X = -51.0
SLAB_Y = 3.1500000953674316
SLAB_HALF_Y = 0.15000000596046448
SLAB_CUT_X = -13.000000953674316
SLAB_FAR_X = -18.9  # deli_a03's slab runs on to -19.0; this end is kept off the lattice so only the seam is on it
PLATE_X = -11.800000190734863
PLATE_Y = 3.1968750953674316
PLATE_HALF_X = 1.2000000476837158
PLATE_HALF_Y = 0.10312499850988388
HALF_Z = 4.9  # both 9.8 m along the seam, their ends off the lattice
SEAM_X = BUILDING_X - 13.0  # -64.0, a lattice line: the grid starts at the ground's corner, x -80
PLATE_FAR_X = BUILDING_X + PLATE_X + PLATE_HALF_X  # -61.6, the plate's east rim


def _godot() -> str | None:
    for env in ("LF_GODOT", "DC_GODOT", "LOT_GODOT"):
        p = os.environ.get(env)
        if p and Path(p).is_file():
            return p
    usual = Path("C:/Godot/4.7/Godot_v4.7-stable_win64_console.exe")
    if usual.is_file():
        return str(usual)
    return shutil.which("godot")


godot_required = pytest.mark.skipif(_godot() is None, reason="no Godot binary; this runs the real instrument")

PROJECT = """config_version=5

[application]
config/name="edge_seam"
run/main_scene="res://main.tscn"
config/features=PackedStringArray("4.7")
"""


def _box_soup(x0, x1, y0, y1, z0, z1):
    """A box as a ConcavePolygonShape3D's triangles, each front-facing outward by Godot's rule: a face's normal is
    (a - c) x (a - b), and a ray meets a trimesh face only from its front."""
    def corner(i, j, k):
        return ((x0, x1)[i], (y0, y1)[j], (z0, z1)[k])
    faces = (  # each face's corners in order round it, and its outward axis
        (((0, 1, 0), (1, 1, 0), (1, 1, 1), (0, 1, 1)), (0, 1, 0)),
        (((0, 0, 0), (1, 0, 0), (1, 0, 1), (0, 0, 1)), (0, -1, 0)),
        (((0, 0, 0), (1, 0, 0), (1, 1, 0), (0, 1, 0)), (0, 0, -1)),
        (((0, 0, 1), (1, 0, 1), (1, 1, 1), (0, 1, 1)), (0, 0, 1)),
        (((0, 0, 0), (0, 1, 0), (0, 1, 1), (0, 0, 1)), (-1, 0, 0)),
        (((1, 0, 0), (1, 1, 0), (1, 1, 1), (1, 0, 1)), (1, 0, 0)),
    )
    out = []
    for quad, outward in faces:
        pts = [corner(*q) for q in quad]
        for a, b, c in ((pts[0], pts[1], pts[2]), (pts[0], pts[2], pts[3])):
            u = [a[i] - c[i] for i in range(3)]
            v = [a[i] - b[i] for i in range(3)]
            n = (u[1] * v[2] - u[2] * v[1], u[2] * v[0] - u[0] * v[2], u[0] * v[1] - u[1] * v[0])
            if sum(n[i] * outward[i] for i in range(3)) < 0:
                b, c = c, b
            out.extend(a + b + c)
    return out


def _floats(vals) -> str:
    return ", ".join(repr(float(v)) for v in vals)


def _main_scene() -> str:
    slab = _box_soup(SLAB_FAR_X, SLAB_CUT_X, -SLAB_HALF_Y, SLAB_HALF_Y, -HALF_Z, HALF_Z)
    plate = [c for x in (-PLATE_HALF_X, PLATE_HALF_X) for y in (-PLATE_HALF_Y, PLATE_HALF_Y)
             for z in (-HALF_Z, HALF_Z) for c in (x, y, z)]
    slab_w = SLAB_CUT_X - SLAB_FAR_X
    return f"""[gd_scene load_steps=7 format=3]

[sub_resource type="BoxShape3D" id="ground"]
size = Vector3(40, 0.2, 30)

[sub_resource type="BoxMesh" id="ground_mesh"]
size = Vector3(40, 0.2, 30)

[sub_resource type="ConcavePolygonShape3D" id="slab"]
data = PackedVector3Array({_floats(slab)})

[sub_resource type="BoxMesh" id="slab_mesh"]
size = Vector3({slab_w!r}, {2 * SLAB_HALF_Y!r}, {2 * HALF_Z!r})

[sub_resource type="ConvexPolygonShape3D" id="plate"]
points = PackedVector3Array({_floats(plate)})

[sub_resource type="BoxMesh" id="plate_mesh"]
size = Vector3({2 * PLATE_HALF_X!r}, {2 * PLATE_HALF_Y!r}, {2 * HALF_Z!r})

[node name="Main" type="Node3D"]

[node name="Ground" type="StaticBody3D" parent="."]
transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, -60, -0.1, 0)

[node name="col" type="CollisionShape3D" parent="Ground"]
shape = SubResource("ground")

[node name="mesh" type="MeshInstance3D" parent="Ground"]
mesh = SubResource("ground_mesh")

[node name="Building" type="Node3D" parent="."]
transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, {BUILDING_X!r}, 0, 0)

[node name="slab_col_1" type="StaticBody3D" parent="Building"]
transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, 0, {SLAB_Y!r}, 0)

[node name="col" type="CollisionShape3D" parent="Building/slab_col_1"]
shape = SubResource("slab")

[node name="mesh" type="MeshInstance3D" parent="Building/slab_col_1"]
transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, {(SLAB_FAR_X + SLAB_CUT_X) / 2!r}, 0, 0)
mesh = SubResource("slab_mesh")

[node name="stair1col_discharge_0" type="StaticBody3D" parent="Building"]
transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, {PLATE_X!r}, {PLATE_Y!r}, 0)

[node name="col" type="CollisionShape3D" parent="Building/stair1col_discharge_0"]
shape = SubResource("plate")

[node name="mesh" type="MeshInstance3D" parent="Building/stair1col_discharge_0"]
mesh = SubResource("plate_mesh")
"""


@godot_required
def test_a_seam_on_the_lattice_is_not_a_drop(tmp_path):
    proj = tmp_path / "pkg"
    proj.mkdir()
    (proj / "project.godot").write_text(PROJECT, encoding="utf-8")
    (proj / "main.tscn").write_text(_main_scene(), encoding="utf-8")
    (proj / "walkable_edge.gd").write_text(EDGE.read_text(encoding="utf-8"), encoding="utf-8")
    out = tmp_path / "edges.json"
    run = subprocess.run([_godot(), "--headless", "--path", str(proj), "--script", "res://walkable_edge.gd",
                          "--", str(out), str(D.CELL_M), "-67.0,3.3,0.1"],
                         capture_output=True, text=True, timeout=300)
    assert out.is_file(), run.stdout + run.stderr
    report = json.loads(out.read_text(encoding="utf-8"))
    assert report["ok"], report["error"]
    upper = [e for e in report["edges"] if e["y"] > 2.0]
    # along the seam's interior (its ends are the slabs' own corners): a body cannot fall through 1.7 um
    seam = [(e["x"], e["z"], e["drop_m"]) for e in upper if abs(e["x"] - SEAM_X) <= NEAR and abs(e["z"]) < 4.6]
    assert seam == [], seam[:20]
    # the plate's east rim is a real 3.3 m drop, and the flood reaches the plate only across the seam
    assert any(abs(e["x"] - PLATE_FAR_X) <= NEAR and abs(e["z"]) < 4.6 for e in upper), \
        sorted({e["x"] for e in upper})[:40]
'''

CHANGELOG = '''## [0.219.0] - the drop-edge lattice is laid off the round coordinates, so a rounding gap is not a hole

**Found by the factory's breadth sweep of 2026-10-19 (roadmap 173).** Cold run 9333, restaurant_row_001, stopped at the
export with 0 interventions on three "undeclared drops", 3.3 m from deli_a03's storey-1 floor at the west edge of its
up-stair's discharge plate. The slab's cut and the plate are authored flush on the gate's 0.5 m lattice, site x -64.0,
and are not flush in float32: the cut is stored at local x -13.000000953674316, one float32 step west, and the plate's
body composes with the building's -51 to -62.799999237, its west face 0.7 um east of -64.0 -- a 1.7 um gap
straddling the line (the factory's docs/findings/breadth_sweep_2026-10-19/, read off the GLB and the engine). A ray at
exactly -64.0 fell through it to the ground; rays a float32 step either side meet the slab and the plate.
`walkable_edge.gd` cast one ray down each cell's lattice point, and the lattice lands on the round coordinates where
pieces meet. A body is 0.4 m across and cannot fall through 1.7 um. Roadmap 173 had filed the lattice's fragility
after one centimetre of offset lost a landing.

### Fixed
- The lattice is laid `SEAM_NUDGE_X` / `SEAM_NUDGE_Z` (3.1 mm, 2.3 mm) off the round coordinates -- one offset on the
  grid's origin, bounded or not -- so every query asks the moved points: the column rays and their capsules, the
  barrier ray, the block capsule, the sky ray, the seed's cell and each link's. Not multiples of 0.5 mm, so no query
  lands where pieces meet; more than 35 float32 steps anywhere within 1 km of the origin; under 2 % of the standing
  probe's radius. Rows are reported to 0.01 m, where 3 mm does not show; the report gains `lattice_offset_m`.
- Measured through the gate on the sweep's six packages, on 0.218.2 and on both builds of this release, the old arm
  reproducing each export's own scan: 9333 refuses on 0.218.2 and passes here, and no other verdict moves. 38 edge
  rows change, each attributed cell by cell to what a query on a round coordinate does -- a rounding gap, a ray in a
  face's plane, a capsule touching a face its radius away (Godot has no epsilon), a hit a few millimetres along a
  slope -- and the factory's findings keep the tables. A first build moved the column and sky rays alone; this one's
  every count and row equals it on all six packages, so moving the barrier ray and the block capsule changed nothing
  measurable there. They move because the capsule kind was measured on the standing capsule, not because a row
  needed it.

### Refuted, kept
- "A ray exactly on the line where two flush colliders meet reports neither." They were never flush: the floats
  above, and rays at the float32 values either side of -64.0 each meet a collider.

### Added
- `tests/unit/test_edge_seam.py` (1, fails on 0.218.2; runs the real instrument through a real Godot): deli_a03's seam
  rebuilt from its own floats -- a trimesh slab and a convex plate under a building at -51 -- reads no drop along the
  seam, and the plate's far rim, which the flood reaches only across the seam, is still found.

'''


def _test_plan():
    p = LF / "tests" / "unit" / "test_edge_seam.py"
    if p.exists():
        assert p.read_bytes() == TEST.encode("utf-8"), f"{p.name} exists and is not this patch's"
    return p


def write_tests(p=None):
    p = p or _test_plan()
    p.write_text(TEST, encoding="utf-8", newline="\n")
    print("wrote level_factory/tests/unit/test_edge_seam.py")


def _once(text, old, new, what):
    assert text.count(old) == 1, (what, text.count(old))
    return text.replace(old, new)


def main(argv):
    if "--tests" in argv:
        write_tests()
        return 0
    raw = EDGE.read_bytes()
    assert b"\r\n" not in raw, "walkable_edge.gd is LF"
    got = hashlib.sha256(raw).hexdigest()[:16]
    assert got == EDGE_SHA, ("walkable_edge.gd is not the file this patch read", got)
    text = raw.decode("utf-8")
    assert "SEAM_NUDGE" not in text, "already applied"
    text = _once(text, CONST_OLD, CONST_NEW, "the constants")
    text = _once(text, BOX_OLD, BOX_NEW, "the grid's origin")
    v = LF / "VERSION"
    assert v.read_text(encoding="utf-8").strip() == "0.218.2", v.read_text(encoding="utf-8")
    cl = LF / "CHANGELOG.md"
    rawc = cl.read_bytes()
    eol = "\r\n" if rawc.count(b"\r\n") else "\n"
    ctext = rawc.decode("utf-8")
    assert ctext.startswith("## [0.218.2]"), ctext[:40]
    plan = _test_plan()
    EDGE.write_bytes(text.encode("utf-8"))
    v.write_text("0.219.0", encoding="utf-8")
    cl.write_bytes((CHANGELOG.replace("\n", eol) + ctext).encode("utf-8"))
    write_tests(plan)
    print("Level Factory 0.219.0 applied: walkable_edge.gd's lattice off the round coordinates, the test, VERSION, "
          "CHANGELOG -- "
          "now the suite, gdcheck, and the gate on the sweep's packages")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
