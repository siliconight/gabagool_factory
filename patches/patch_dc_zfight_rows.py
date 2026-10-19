"""Deli Counter 0.230.0: the z-fight gate reads a scene's transforms as Godot does -- roadmap 177's last two pairs.

THE DEFECT. `zfight_gate._scene_module_boxes` built each composed module's box from its `.tscn` `Transform3D`
reading the nine basis numbers as COLUMNS. Godot 4.7 writes and parses them as ROWS, measured three times:
this repo off the engine on cold run 9013 (`tscn_export.godot_basis`'s docstring, 0.120.1); Lot's `str_to_var`
on 2026-09-13 (`lot/site_furniture.plate_facing`); and the factory's `tools/module_pose_census.py` on cold run
9324's deli_a01, 2026-10-19 (`docs/findings/zfight_rows_177/`). A pure turn reads the same either way for a box
about its own centre; a turned, non-uniformly scaled module does not. deli_a01's east-wall end piece
`ext_0_E_seg10` -- 0.6 m along its wall, 0.35 m through it, on a wall that runs along Godot Z -- came out the
other way round, and so shared both side planes of partition 1's end piece `int_0_1_seg18`, 0.9 m2 each: the
last two pairs the gate reported (cold runs 9322 to 9324). The engine stands the piece as written: x
18.825..19.175, z -6.300..-5.700, no face on either plane.

MEASURED BEFORE WRITING (`docs/findings/zfight_rows_177/rows_vs_columns.py`, the gate's own code with only the
matrix swapped, over cold run 9324's 16 composed buildings): 2 visible pairs read as columns, both deli_a01's
junction, 0 read as rows; no pair appears under rows that columns hid. Buried pairs (reported, never gated on)
move: deli_a01 213 -> 220, pharmacy_a01 29 -> 27.

What it changes (anchored; the file pinned by hash; nothing written on a miss; LF-safe):
  * zfight_gate.py -- `instance_matrix(f)`: a node's 3x4 world matrix from the twelve numbers as written, the
    basis rows then the origin, with the refutation kept in its docstring; `_scene_module_boxes` uses it.
  * test_zfight_rows.py (new, 3; all fail on 0.229.0): the end piece's box against the engine's numbers; a pure
    turn unchanged; the junction itself, end to end through `check_package` on a synthetic package.
  * VERSION 0.229.0 -> 0.230.0, CHANGELOG.

No rebuild: zfight_gate.py is a reader, in `build_freshness.NOT_BAKED` since 0.229.0.

    python patches/patch_dc_zfight_rows.py --tests   # the test file only (prove it fails first)
    python patches/patch_dc_zfight_rows.py           # everything; the test again when it is this patch's
"""
import hashlib
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
DC = ROOT / "deli_counter"
ZG = DC / "zfight_gate.py"
ZG_SHA = "c7fe3d2ce6b8c8fc"

APPLY_OLD = '''def _apply(m, p):
    return tuple(m[i][0] * p[0] + m[i][1] * p[1] + m[i][2] * p[2] + m[i][3]
                 for i in range(3))
'''
APPLY_NEW = '''def _apply(m, p):
    return tuple(m[i][0] * p[0] + m[i][1] * p[1] + m[i][2] * p[2] + m[i][3]
                 for i in range(3))


def instance_matrix(f):
    """The 3x4 world matrix of a `.tscn` node's ``Transform3D(...)``, its
    twelve numbers in the order written: the basis's three ROWS, then the
    origin (0.230.0, the factory's roadmap 177).

    Godot 4.7 writes and parses the nine basis numbers as rows. Measured three
    times: this repo off the engine on cold run 9013 (`tscn_export.
    godot_basis` says so), Lot's `str_to_var` on 2026-09-13 (`lot/
    site_furniture.plate_facing`), and the factory's `tools/
    module_pose_census.py` on cold run 9324's deli_a01, where `ext_0_E_seg10`
    stands 0.35 m through its wall and 0.6 m along it.

    REFUTED, KEPT: until 0.229.0 this gate read them as COLUMNS -- the
    transpose. A pure turn reads the same either way for a box about its own
    centre; a turned AND non-uniformly scaled module, a wall remainder on a
    wall that runs along Godot Z, came out with its length and thickness
    swapped. deli_a01's east-wall end piece then shared both of partition 1's
    side planes, 0.9 m2 each, and the gate reported them as the last two
    z-fight pairs of cold runs 9322 to 9324: an instrument defect, no
    geometry. Read as rows, 9324's 16 composed buildings count 0."""
    return [[f[0], f[1], f[2], f[9]],
            [f[3], f[4], f[5], f[10]],
            [f[6], f[7], f[8], f[11]]]
'''

MATRIX_OLD = '''        m = [[f[0], f[3], f[6], f[9]],
             [f[1], f[4], f[7], f[10]],
             [f[2], f[5], f[8], f[11]]]
'''
MATRIX_NEW = '''        m = instance_matrix(f)
'''

TEST = r'''"""The z-fight gate reads a `.tscn` Transform3D as Godot does: the basis's rows, then the origin (0.230.0, the
factory's roadmap 177).

Until 0.229.0 the gate built the transpose. A turned, non-uniformly scaled wall module -- deli_a01's east-wall end
piece `ext_0_E_seg10`, 0.6 m long and 0.35 m thick on a wall that runs along Godot Z -- came out 0.6 m through the
wall and 0.35 m along it, sharing both side planes of partition 1's end piece `int_0_1_seg18`: the last two pairs
the gate reported in cold runs 9322 to 9324. The engine stands it 0.35 m through and 0.6 m along (the factory's
`tools/module_pose_census.py` on cold run 9324's package: x 18.825..19.175, z -6.300..-5.700). These use the two
nodes' transforms exactly as cold run 9324 wrote them, on a unit-cube module, as the wall-end modules are.

Run: python -m pytest -q test_zfight_rows.py
"""
import struct

import pytest

import zfight_gate

# exactly as cold run 9324's lot/deli_a01/site.tscn writes them
EXT_SEG10 = "0.0, 0.0, -0.35, 0.0, 3.0, 0.0, 0.6, 0.0, 0.0, 19.0, 1.496, -6.0"
INT_SEG18 = "0.375, 0.0, -0.0, 0.0, 3.0, 0.0, 0.0, 0.0, 0.35, 18.8125, 1.496, -6.0"
EXT_SEG9 = "0.0, 0.0, -1.0, 0.0, 1.0, 0.0, 1.0, 0.0, 0.0, 19.0, 1.496, -4.7"


def _box(xf_text, half=0.5):
    m = zfight_gate.instance_matrix([float(v) for v in xf_text.split(",")])
    pts = [zfight_gate._apply(m, (x, y, z))
           for x in (-half, half) for y in (-half, half) for z in (-half, half)]
    return [min(p[i] for p in pts) for i in range(3)], [max(p[i] for p in pts) for i in range(3)]


def test_the_end_piece_stands_as_the_engine_measured_it():
    lo, hi = _box(EXT_SEG10)
    assert lo[0] == pytest.approx(18.825) and hi[0] == pytest.approx(19.175)   # 0.35 m through the wall
    assert lo[2] == pytest.approx(-6.3) and hi[2] == pytest.approx(-5.7)       # 0.6 m along it
    assert lo[1] == pytest.approx(-0.004) and hi[1] == pytest.approx(2.996)


def test_a_pure_turn_reads_as_it_always_did():
    lo, hi = _box(EXT_SEG9)
    assert hi[0] - lo[0] == pytest.approx(1.0) and hi[2] - lo[2] == pytest.approx(1.0)
    assert (lo[0] + hi[0]) / 2 == pytest.approx(19.0) and (lo[2] + hi[2]) / 2 == pytest.approx(-4.7)


def _unit_cube_glb(path):
    """A one-mesh glTF whose POSITION accessor spans the unit cube about the origin -- all the gate reads."""
    from pygltflib import GLTF2, Accessor, Attributes, Buffer, BufferView, Mesh, Node, Primitive, Scene
    blob = b"".join(struct.pack("<3f", x, y, z) for x in (-0.5, 0.5) for y in (-0.5, 0.5) for z in (-0.5, 0.5))
    g = GLTF2(scene=0, scenes=[Scene(nodes=[0])], nodes=[Node(mesh=0, name="WallEnd_Panel")],
              meshes=[Mesh(primitives=[Primitive(attributes=Attributes(POSITION=0))])],
              accessors=[Accessor(bufferView=0, componentType=5126, count=8, type="VEC3",
                                  min=[-0.5, -0.5, -0.5], max=[0.5, 0.5, 0.5])],
              bufferViews=[BufferView(buffer=0, byteOffset=0, byteLength=len(blob))],
              buffers=[Buffer(byteLength=len(blob))])
    g.set_binary_blob(blob)
    g.save_binary(str(path))


# The storey's slabs, as the building stands them: the walls are sunk 4 mm (`SLAB_CAP_SINK`) into the floor, their
# caps 4 mm under the slab above. Both pieces span the same height, so their tops and bottoms share planes; matter
# within the gate's outward gap buries those, as it does in the building. Without the slabs this would be asking
# about faces no building leaves open.
FLOOR = "2.0, 0.0, 0.0, 0.0, 0.3, 0.0, 0.0, 0.0, 2.0, 18.8, -0.15, -6.0"
CEILING = "2.0, 0.0, 0.0, 0.0, 0.3, 0.0, 0.0, 0.0, 2.0, 18.8, 3.15, -6.0"


def _instance(name, xf):
    return '[node name="%s" parent="." instance=ExtResource("1_cube")]\ntransform = Transform3D(%s)\n\n' % (name, xf)


def test_the_junction_holds_no_pair(tmp_path):
    pkg = tmp_path / "pkg"
    (pkg / "art" / "zoo").mkdir(parents=True)
    _unit_cube_glb(pkg / "art" / "zoo" / "cube.glb")
    (pkg / "site.tscn").write_text(
        '[gd_scene format=3]\n\n'
        '[ext_resource type="PackedScene" path="res://art/zoo/cube.glb" id="1_cube"]\n\n'
        '[node name="Site" type="Node3D"]\n\n'
        + _instance("ext_0_E_seg10", EXT_SEG10) + _instance("int_0_1_seg18", INT_SEG18)
        + _instance("floor_0", FLOOR) + _instance("ceiling_1", CEILING), encoding="utf-8")
    r = zfight_gate.check_package(str(pkg), "site.tscn")
    assert r["solids"] == 4, r
    assert r["pairs"] == 0 and r["ok"], r["findings"]
'''

CHANGELOG = '''## [0.230.0] - the z-fight gate reads a scene's transforms as Godot does

**The factory's roadmap 177, its last two pairs.** The gate built each composed module's box from its `.tscn`
`Transform3D`, reading the nine basis numbers as columns. Godot 4.7 writes and parses them as rows, measured three
times: by this repo on cold run 9013 (`tscn_export.godot_basis`), by Lot on 2026-09-13, and on cold run 9324's
deli_a01 with the factory's `tools/module_pose_census.py`. A pure turn reads the same either way for a box about its
own centre; a turned, non-uniformly scaled module does not. deli_a01's east-wall end piece `ext_0_E_seg10`, 0.6 m
along its wall and 0.35 m through it, came out the other way round, sharing both side planes of partition 1's end
piece: the two 0.9 m2 pairs cold runs 9322 to 9324 reported. The engine stands it as written, x 18.825..19.175 and
z -6.300..-5.700, with no face on either plane.

### Fixed
- `instance_matrix(f)`: a node's 3x4 world matrix from the twelve numbers as written, the basis rows then the
  origin; `_scene_module_boxes` builds every instance box with it. The column reading is kept, refuted, in its
  docstring.

### Measured
- Cold run 9324's 16 composed buildings, the gate's own code with only the matrix differing (the factory's
  `docs/findings/zfight_rows_177/`): 2 visible pairs read as columns, both deli_a01's junction, and 0 read as rows;
  no pair appears under rows that columns hid. Buried pairs, reported and never gated on, move: deli_a01 213 -> 220,
  pharmacy_a01 29 -> 27.

### Added
- `test_zfight_rows.py` (3), on the two nodes' transforms exactly as cold run 9324 wrote them; all fail on 0.229.0.

No rebuild: `zfight_gate.py` is a reader, in `build_freshness.NOT_BAKED`. Other readers outside this repo hold the
same belief -- Level Factory's `ground_contact`, and three of the factory's tools -- and are the roadmap's, not this
release's.

'''


def _once(text, old, new, what):
    assert text.count(old) == 1, (what, text.count(old))
    return text.replace(old, new)


def _test_plan():
    p = DC / "test_zfight_rows.py"
    if p.exists():
        assert p.read_bytes() == TEST.encode("utf-8"), f"{p.name} exists and is not this patch's"
    return p


def write_tests(p=None):
    p = p or _test_plan()
    p.write_text(TEST, encoding="utf-8", newline="\n")
    print("wrote deli_counter/test_zfight_rows.py")


def main(argv):
    if "--tests" in argv:
        write_tests()
        return 0
    raw = ZG.read_bytes()
    assert b"\r\n" not in raw, "zfight_gate.py is LF"
    got = hashlib.sha256(raw).hexdigest()[:16]
    assert got == ZG_SHA, ("zfight_gate.py is not the file this patch read", got)
    text = raw.decode("utf-8")
    assert "def instance_matrix" not in text, "already applied"
    text = _once(text, APPLY_OLD, APPLY_NEW, "_apply")
    text = _once(text, MATRIX_OLD, MATRIX_NEW, "the instance matrix")
    v = DC / "VERSION"
    assert v.read_text(encoding="utf-8").strip() == "Deli Counter 0.229.0", v.read_text(encoding="utf-8")
    cl = DC / "CHANGELOG.md"
    rawc = cl.read_bytes()
    eol = "\r\n" if rawc.count(b"\r\n") else "\n"
    ctext = rawc.decode("utf-8")
    assert ctext.startswith("## [0.229.0]"), ctext[:40]
    plan = _test_plan()
    ZG.write_bytes(text.encode("utf-8"))
    v.write_text("Deli Counter 0.230.0", encoding="utf-8")
    cl.write_bytes((CHANGELOG.replace("\n", eol) + ctext).encode("utf-8"))
    write_tests(plan)
    print("Deli Counter 0.230.0 applied: instance_matrix reads rows, test_zfight_rows.py, VERSION, CHANGELOG -- "
          "no rebuild (a reader); the suite, then commit")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
