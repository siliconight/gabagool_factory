"""Zoo 1.109.0: a bevelled mesh is one mesh every build -- each face restarts at its lowest vertex after the bevel
(factory roadmap 247, the roof props' bytes).

Anchored edits, each asserted exactly once and each file's sha16 pinned, nothing written until all matched:
  zoo_keeper/bpylayer/geometry.py   `_corner_layers`, `_corner_value`, `_set_corner_value` before `start_at_lowest`;
                                    `start_at_lowest` carries corner data where it refused it; `bevel_edges`
                                    restarts every face after `bmesh.ops.bevel`
  tests/test_faces_in_order.py      the refusal's test retired, a comment in its place
  tests/test_bevelled_faces_in_order.py   NEW (`zoo_bevel_restart/test_bevelled_faces_in_order.py.txt`)
CHANGELOG and VERSION from `zoo_bevel_restart/CHANGELOG_1.109.0.md`; `--results-pending` leaves RESULT_ keys to
`--fill`. `ZOO_ROOT=<copy>` applies it to a draft.

Read before it was written, in this session: `start_at_lowest`, `in_one_order`, `bevel_edges`, `bm_to_object` (the
1.103.0 face sort and its stated premise, "the vertices' order holds"), `add_ellipsoid`, `add_hemisphere`,
`weight_normals`, `wear_colors` (a byte colour layer, one random draw a vertex in storage order); `prim_mesh`, which
gives a turning part UVMap and Pivot corner layers before `bm_to_object` bevels it; `export.export_glb` (weighted
normals, then the merge); `tests/test_faces_in_order.py` whole; Blender 5.1's loop-layer API, probed (kinds bool,
color, float, float_color, float_vector, int, string, uv; a UV is `uv` and `pin_uv`; a colour a `Vector`). The
measurements: docs/findings/roofprops_bytes/stage_runs.py, shuffle_bevel.py, census_1108.out.txt. Every file LF.

    ZOO_ROOT=<copy> python patches/patch_zoo_bevel_restart.py --results-pending
    python patches/patch_zoo_bevel_restart.py --results-pending
    python patches/patch_zoo_bevel_restart.py --fill
"""
import hashlib
import os
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
ZOO = pathlib.Path(os.environ.get("ZOO_ROOT") or HERE.parent / "zoo")
SRC = HERE / "zoo_bevel_restart"
PENDING = "--results-pending" in sys.argv
FILL = "--fill" in sys.argv
RESULTS = {"RESULT_CHURN": "result_churn.txt", "RESULT_FAILING": "result_failing.txt",
           "RESULT_CENSUS": "result_census.txt", "RESULT_SUITE": "result_suite.txt"}
VERSION_WAS, VERSION = b"1.108.0", b"1.109.0"
CHANGELOG_HEAD = "## [1.108.0] - a corner shop's canvas awning, `shop_awning`\n"
GEOMETRY = "zoo_keeper/bpylayer/geometry.py"
OLD_TEST = "tests/test_faces_in_order.py"
SHA = {GEOMETRY: "de22382f2836f024", OLD_TEST: "593453c33edbe964"}
NEW = {"tests/test_bevelled_faces_in_order.py": "test_bevelled_faces_in_order.py.txt"}

START_OLD = '''def start_at_lowest(bm, faces):
    """Each of ``faces`` remade to start at its lowest-index vertex, its
    winding and its material kept (1.103.0). Returns the faces as they stand.

    An operator that makes a face (`holes_fill`, `contextual_create`) starts
    it at a corner of its own choosing, and the choice changes from one
    process to the next even with its input in one order: across four builds
    of the deli's fixtures, each dome's 20-cornered cap started at one of two
    neighbouring corners, dome by dome. A GLB triangulates a face from its
    first corner, so the two starts are two sets of triangles and two
    lightmap charts. Remade before the face carries corner data -- refused if
    the bmesh has any, rather than losing it.
    """
    layers = bm.loops.layers
    for kind in ("uv", "color", "float_color", "float", "int"):
        if len(getattr(layers, kind, ())):
            raise ValueError("start_at_lowest: the bmesh carries %s corner data" % kind)
    bm.verts.index_update()
    out = []
    for f in faces:
        vs = list(f.verts)
        k = min(range(len(vs)), key=lambda i: vs[i].index)
        if k == 0:
            out.append(f)
            continue
        mat, smooth = f.material_index, f.smooth
        bm.faces.remove(f)
        nf = bm.faces.new(vs[k:] + vs[:k])
        nf.material_index, nf.smooth = mat, smooth
        out.append(nf)
    return out
'''
START_NEW = '''def _corner_layers(bm):
    """``[(kind, layer)]``: every loop layer ``bm`` carries, of every kind
    this Blender's BMesh has -- read off the API rather than listed (5.1:
    bool, color, float, float_color, float_vector, int, string, uv), so a
    kind added later is carried, or refused loudly, never dropped."""
    acc = bm.loops.layers
    out = []
    for kind in sorted(dir(acc)):
        coll = None if kind.startswith("_") else getattr(acc, kind, None)
        if isinstance(coll, bmesh.types.BMLayerCollection):
            out += [(kind, layer) for layer in coll.values()]
    return out


def _corner_value(loop, kind, layer):
    """A corner's value on one layer, held apart from the corner: a UV by
    its `uv` and its pin, a vector copied, anything else as read."""
    value = loop[layer]
    if kind == "uv":
        return (value.uv.copy(), value.pin_uv)
    return value.copy() if hasattr(value, "copy") else value


def _set_corner_value(loop, kind, layer, value):
    if kind == "uv":
        loop[layer].uv, loop[layer].pin_uv = value
    else:
        loop[layer] = value


def start_at_lowest(bm, faces):
    """Each of ``faces`` remade to start at its lowest-index vertex, its
    winding, its material and its corner data kept (1.103.0; the corner data
    since 1.109.0). Returns the faces as they stand.

    An operator that makes a face (`holes_fill`, `contextual_create`, the
    bevel in `bevel_edges`) starts it at a corner of its own choosing, and the
    choice changes from one process to the next even with its input in one
    order: across four builds of the deli's fixtures, each dome's 20-cornered
    cap started at one of two neighbouring corners, dome by dome. A GLB
    triangulates a face from its first corner, so the two starts are two sets
    of triangles and two lightmap charts.

    THE CORNER DATA GOES ROUND WITH ITS CORNERS (1.109.0). Until then a bmesh
    carrying any was refused, rather than have it lost; but `bevel_edges`
    restarts every face it leaves, and a turning part reaches it carrying its
    UVMap and Pivot layers (`prim_mesh`). Each corner's value on every layer
    (`_corner_layers`) is read before the face is remade and written back to
    the corner on the same vertex.
    """
    layers = _corner_layers(bm)
    bm.verts.index_update()
    out = []
    for f in faces:
        vs = list(f.verts)
        k = min(range(len(vs)), key=lambda i: vs[i].index)
        if k == 0:
            out.append(f)
            continue
        held = [[_corner_value(lp, kind, layer) for lp in f.loops] for kind, layer in layers]
        mat, smooth = f.material_index, f.smooth
        bm.faces.remove(f)
        nf = bm.faces.new(vs[k:] + vs[:k])
        nf.material_index, nf.smooth = mat, smooth
        for (kind, layer), values in zip(layers, held):
            for lp, value in zip(nf.loops, values[k:] + values[:k]):
                _set_corner_value(lp, kind, layer, value)
        out.append(nf)
    return out
'''

BEVEL_OLD = '''    if edges:
        bmesh.ops.bevel(bm, geom=edges, offset=offset, segments=segments,
                        profile=0.7, affect="EDGES", clamp_overlap=True)
'''
BEVEL_NEW = '''    if edges:
        bmesh.ops.bevel(bm, geom=edges, offset=offset, segments=segments,
                        profile=0.7, affect="EDGES", clamp_overlap=True)
        # EVERY FACE FROM ITS LOWEST CORNER (1.109.0, factory roadmap 247).
        # The bevel starts the faces it makes and remakes at corners of its
        # own choosing, and the choice moves with the bmesh's face order and
        # with the process. The satellite dish's bowl -- a `create_uvsphere`,
        # whose faces come in an order that changes from process to process
        # -- built six times in fresh processes from one command, left four
        # ways, its triangles from other corners and in other orders. One
        # process laying its faces in six orders bevelled them four to six
        # ways, and six ways with the faces sorted back into one order first.
        # Restarted at their lowest vertex just after the bevel, the six were
        # one mesh, the same in two processes (the factory's
        # docs/findings/roofprops_bytes/: stage_runs.py, shuffle_bevel.py).
        # `bm_to_object` sorts the faces by their corners next, so where a
        # face starts is its sort key.
        start_at_lowest(bm, list(bm.faces))
'''

TEST_OLD = '''def test_bpy_it_refuses_a_face_that_carries_corner_data():
    pytest.importorskip("bpy")
    import bmesh
    from zoo_keeper.bpylayer import geometry
    bm = bmesh.new()
    try:
        vs = [bm.verts.new((x, y, 0.0)) for x, y in ((0, 0), (1, 0), (1, 1))]
        f = bm.faces.new([vs[1], vs[2], vs[0]])
        bm.loops.layers.uv.new("UVMap")
        with pytest.raises(ValueError):
            geometry.start_at_lowest(bm, [f])
    finally:
        bm.free()
'''
TEST_NEW = '''# `test_bpy_it_refuses_a_face_that_carries_corner_data` stood here until 1.109.0, when
# `start_at_lowest` came to carry a face's corner data round with its corners rather than refuse
# it: tests/test_bevelled_faces_in_order.py reads the data back, corner by corner.
'''


def _eol(raw, rel):
    crlf = raw.count(b"\r\n")
    lf = raw.count(b"\n")
    assert crlf in (0, lf), (rel, "mixed line endings", crlf, lf)
    return b"\r\n" if crlf else b"\n"


def _read(rel):
    raw = (ZOO / rel).read_bytes()
    got = hashlib.sha256(raw.replace(b"\r\n", b"\n")).hexdigest()[:16]
    assert got == SHA[rel], (rel, "is not the file this patch read", got)
    return _eol(raw, rel), raw.decode("utf-8").replace("\r\n", "\n")


def fill():
    assert (ZOO / "VERSION").read_bytes().strip() == VERSION, (ZOO / "VERSION").read_bytes()
    results = {}
    for key, name in RESULTS.items():
        value = (SRC / name).read_text(encoding="utf-8").strip()
        assert value and "RESULT_" not in value, (name, value[-40:])
        results[key] = value
    writes = {}
    for path, rel in [(ZOO / "CHANGELOG.md", "CHANGELOG.md"), (SRC / "CHANGELOG_1.109.0.md", "the entry")]:
        raw = path.read_bytes()
        eol = _eol(raw, rel)
        text = raw.decode("utf-8").replace("\r\n", "\n")
        for key, value in results.items():
            assert text.count(key) == 1, (rel, key, text.count(key))
            text = text.replace(key, value)
        writes[path] = text.encode("utf-8").replace(b"\n", eol)
    for path, data in writes.items():
        path.write_bytes(data)
    print("Zoo 1.109.0: results filled")


def main():
    if FILL:
        return fill()
    assert (ZOO / "VERSION").read_bytes().strip() == VERSION_WAS, (ZOO / "VERSION").read_bytes()
    entry = (SRC / "CHANGELOG_1.109.0.md").read_bytes().decode("utf-8").replace("\r\n", "\n")
    assert entry.startswith("## [1.109.0] - "), entry[:40]
    left = entry
    for key in RESULTS if PENDING else ():
        left = left.replace(key, "")
    assert "RESULT_" not in left, "the changelog still carries an unfilled result"
    for rel in NEW:
        assert not (ZOO / rel).exists(), ("already applied", rel)
    geo_eol, geo = _read(GEOMETRY)
    test_eol, test = _read(OLD_TEST)
    for text, old, new, what in ((geo, START_OLD, START_NEW, "start_at_lowest"),
                                 (geo, BEVEL_OLD, BEVEL_NEW, "bevel_edges"),
                                 (test, TEST_OLD, TEST_NEW, "the refusal's test")):
        assert text.count(old) == 1, (what, "anchor", text.count(old))
    geo = geo.replace(START_OLD, START_NEW).replace(BEVEL_OLD, BEVEL_NEW)
    test = test.replace(TEST_OLD, TEST_NEW)
    compile(geo, GEOMETRY, "exec")
    compile(test, OLD_TEST, "exec")
    news = {r: (SRC / s).read_bytes().replace(b"\r\n", b"\n") for r, s in NEW.items()}
    for r, data in news.items():
        compile(data.decode("utf-8"), r, "exec")
    cl = ZOO / "CHANGELOG.md"
    cl_raw = cl.read_bytes()
    cl_eol = _eol(cl_raw, "CHANGELOG.md")
    cl_text = cl_raw.decode("utf-8").replace("\r\n", "\n")
    assert cl_text.startswith(CHANGELOG_HEAD) and cl_text.count(CHANGELOG_HEAD) == 1, cl_text[:120]
    # every anchor matched: now write
    (ZOO / GEOMETRY).write_bytes(geo.encode("utf-8").replace(b"\n", geo_eol))
    (ZOO / OLD_TEST).write_bytes(test.encode("utf-8").replace(b"\n", test_eol))
    for r, data in news.items():
        (ZOO / r).write_bytes(data)
    cl.write_bytes((entry.rstrip("\n") + "\n\n" + cl_text).encode("utf-8").replace(b"\n", cl_eol))
    (ZOO / "VERSION").write_bytes(VERSION)
    print("Zoo 1.108.0 -> 1.109.0")


if __name__ == "__main__":
    main()
