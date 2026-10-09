"""Zoo 1.87.0: weighted normals -- every part's corner normals weighed by face
area at export (roadmap 214, trial 1).

A bevelled box at the default 50-degree smoothing shipped with every corner of
its big faces pulled toward the chamfer beside it: 28.89 degrees off flat on
all 36 big-face corners of a 0.6 x 0.4 x 0.5 m crate, read out of the GLB
(`docs/findings/weighted_normals/`). Weighed by area, 2.40 degrees mean, with
the same 48 vertices.

Anchored edits (an anchor matches the count given, 1 unless stated; refuses on
a miss; nothing is written until every anchor in every file matched):
- `zoo_keeper/bpylayer/geometry.py`: `weight_normals`, and its import.
- `zoo_keeper/bpylayer/export.py`: `export_glb(..., weighted_normals=True)`.
- `zoo_keeper/bpylayer/merge.py`: the merge carries each part's corner
  normals when any part has custom ones.
- `zoo_keeper/bpylayer/build.py`: `DEFAULT_OPTIONS["weighted_normals"]`, and
  every export passes it (3 + 2 calls).
- `zoo_keeper/bpylayer/ingest.py`: an import keeps its author's normals.
- `tools/zoo_cli.py`: `--no-weighted-normals`, into all 4 option dicts.
- `tools/preview_specimen.py`: `--no-weighted-normals`, into all 3 builds.
New, refused if present: `zoo_keeper/core/normals.py`,
`tests/test_weighted_normals.py`.
CHANGELOG and VERSION from `zoo_weighted_normals/CHANGELOG_1.87.0.md`.

    python patch_zoo_weighted_normals.py
    ZOO_ROOT=<copy> python patch_zoo_weighted_normals.py
"""
import os
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
ZOO = pathlib.Path(os.environ.get("ZOO_ROOT") or HERE.parent / "zoo")
SRC = HERE / "zoo_weighted_normals"

CHANGELOG_HEAD = ("## [1.86.0] - the responders' cruiser: a 1990s Crown Victoria lettered "
                  "for the DELCO COUNTY POLICE\n")

GEOMETRY = [
    ("""from ..core import arch
""",
     """from ..core import arch
from ..core import normals as core_normals
""", 1),
    ('''        e.smooth = faces[0].normal.dot(faces[1].normal) >= limit


def taper_z(''',
     '''        e.smooth = faces[0].normal.dot(faces[1].normal) >= limit


def weight_normals(me):
    """Set ``me``'s custom normals by face area (1.87.0, roadmap 214).

    `core.normals.weighted_corner_normals` computes them from the faces, their
    smoothing and the sharp edges -- the fans `shade_by_angle` decided -- in
    the order the mesh stores its corners. A big face keeps its own normal
    and a chamfer rolls between its neighbours, where the default normal
    shades a bevelled box as a dome (see `core/normals.py`). Called by
    `export.export_glb`, after everything that moves a vertex. Returns the
    corners written; a mesh with no faces is left alone.
    """
    polys = me.polygons
    if not len(polys):
        return 0
    sharp = {frozenset(e.vertices) for e in me.edges if e.use_edge_sharp}
    out = core_normals.weighted_corner_normals(
        [list(p.vertices) for p in polys], [tuple(p.normal) for p in polys],
        [p.area for p in polys], [p.use_smooth for p in polys], sharp)
    me.normals_split_custom_set(out)
    return len(out)


def taper_z(''', 1),
]

EXPORT = [
    ("""def export_glb(filepath, collection, merge_parts=True, share_textures=True):
""",
     """def export_glb(filepath, collection, merge_parts=True, share_textures=True,
               weighted_normals=True):
""", 1),
    ('''    The merged objects are torn down before this returns, so the scene
    `save_blend` writes is the one the recipe built either way.
    """
    packed = merge.pack_by_material(collection) if merge_parts else None
''',
     '''    ``weighted_normals`` weighs every visual part's corner normals by face
    area first (`geometry.weight_normals`, 1.87.0): a big face keeps its own
    normal and a chamfer rolls between its neighbours, where the default
    normal shaded a bevelled box as a dome. Done HERE, after everything that
    moves a vertex, so the normals are computed from the geometry that ships;
    the merge then carries them. Same vertices, triangles and draw calls.
    A keyword for the same reason as the two above: `tools/zoo_cli.py
    --no-weighted-normals` is the one-build control. Ingest passes False,
    because an imported mesh carries the normals its author made.

    The merged objects are torn down before this returns, so the scene
    `save_blend` writes is the one the recipe built either way, its parts'
    normals weighted when they were.
    """
    if weighted_normals:
        for obj in collection.objects:
            if (obj.type == "MESH"
                    and not obj.name.endswith(partnames.COL_SUFFIXES)):
                geometry.weight_normals(obj.data)
    packed = merge.pack_by_material(collection) if merge_parts else None
''', 1),
]

MERGE = [
    ("""`Wear` colour attribute, per-face smoothing, per-edge sharpness and seams --
and the triangle count, which is ASSERTED against the pre-merge total rather
than assumed.
""",
     """`Wear` colour attribute, per-face smoothing, per-edge sharpness and seams --
and the triangle count, which is ASSERTED against the pre-merge total rather
than assumed.

CORNER NORMALS, when any part carries custom ones (1.87.0). `export_glb`
weighs every part's normals by face area before this runs. A new mesh's
normals are recomputed from its edges, which reproduces each part's DEFAULT
normals exactly -- nothing welds -- and cannot reproduce custom ones, so the
merged mesh is given each part's corner normals, copied with its faces.
""", 1),
    ('''def _copy_faces(dst, me, slot, dst_layers):
    """Append the faces of ``me`` with material_index ``slot`` into ``dst``.
''',
     '''def _copy_faces(dst, me, slot, dst_layers, corner=None):
    """Append the faces of ``me`` with material_index ``slot`` into ``dst``.

    ``corner``, when a list, gets the copied faces' corner normals appended
    in the order the new faces' corners are made (1.87.0).
''', 1),
    ("""    vmap = {}
    for face in src.faces:
        if face.material_index != slot:
            continue
""",
     """    vmap = {}
    # from_mesh keeps the mesh's face order and each face's corner order, so
    # face `fi`'s corner k is the mesh's corner loop_start + k
    src_normals = me.corner_normals if corner is not None else None
    for fi, face in enumerate(src.faces):
        if face.material_index != slot:
            continue
""", 1),
    ("""            for name, layer in src_fcol.items():
                dl[dst_layers["fcol"][name]] = sl[layer]
""",
     """            for name, layer in src_fcol.items():
                dl[dst_layers["fcol"][name]] = sl[layer]
        if corner is not None:
            start = me.polygons[fi].loop_start
            corner.extend(tuple(src_normals[start + k].vector)
                          for k in range(len(face.loops)))
""", 1),
    ("""    for obj, slot in sources:
        _copy_faces(dst, obj.data, slot, layers)
    me = bpy.data.meshes.new(name)
    dst.to_mesh(me)
    dst.free()
""",
     """    # each part's corner normals, when any part has custom ones (1.87.0)
    corner = ([] if any(obj.data.has_custom_normals for obj, _ in sources)
              else None)
    for obj, slot in sources:
        _copy_faces(dst, obj.data, slot, layers, corner)
    me = bpy.data.meshes.new(name)
    dst.to_mesh(me)
    dst.free()
    if corner is not None:
        me.normals_split_custom_set(corner)
""", 1),
]

BUILD = [
    ("""    "merge_parts": True,
}
""",
     """    "merge_parts": True,
    # Weigh every part's corner normals by face area at export
    # (`core.normals`, 1.87.0). Off is the control for the look, as
    # `merge_parts` is for the draw calls.
    "weighted_normals": True,
}
""", 1),
    ("""export.export_glb(base + ".glb", coll, merge_parts=opts["merge_parts"])""",
     """export.export_glb(base + ".glb", coll, merge_parts=opts["merge_parts"],
                      weighted_normals=opts["weighted_normals"])""", 3),
    ("""export.export_glb(base + ".glb", coll, merge_parts=False)""",
     """export.export_glb(base + ".glb", coll, merge_parts=False,
                      weighted_normals=opts["weighted_normals"])""", 2),
]

INGEST = [
    ("""    _export.export_glb(glb_path, coll)
""",
     """    # AN AUTHOR'S NORMALS STAY (1.87.0): the glTF importer sets a file's
    # normals as custom normals, and weighing them by area would overwrite
    # that work. The merge carries them through.
    _export.export_glb(glb_path, coll, weighted_normals=False)
""", 1),
]

CLI = [
    ("""                         "bpylayer/merge.py). Costs ~5.8x the draw calls.")
""",
     """                         "bpylayer/merge.py). Costs ~5.8x the draw calls.")
    ap.add_argument("--no-weighted-normals", dest="no_weighted_normals",
                    action="store_true",
                    help="export the default corner normals instead of "
                         "weighing them by face area -- the pre-1.87.0 "
                         "shading, kept as the control for the look (see "
                         "core/normals.py). Same vertices, triangles and "
                         "draw calls either way.")
""", 1),
    # habitat, kit and dressing builds, at one indent...
    ("""                 "merge_parts": not args.no_merge_parts})
""",
     """                 "merge_parts": not args.no_merge_parts,
                 "weighted_normals": not args.no_weighted_normals})
""", 3),
    # ...and the full build's opts, at another
    ("""            "merge_parts": not args.no_merge_parts}
""",
     """            "merge_parts": not args.no_merge_parts,
            "weighted_normals": not args.no_weighted_normals}
""", 1),
]

PREVIEW = [
    ("""    no_ground = _flag("--no-ground")
""",
     """    no_ground = _flag("--no-ground")
    # The control for Zoo 1.87.0's weighted normals: the same build with the
    # default corner normals, so a before/after is two renders of one piece.
    weighted = not _flag("--no-weighted-normals")
""", 1),
    # the kit-path module first: its options share a line with `style`...
    ("""                                 style=style, options={"save_blend": False})
""",
     """                                 style=style,
                                 options={"save_blend": False,
                                          "weighted_normals": weighted})
""", 1),
    # ...then the slot-path module, whose options have a line of their own
    ("""                                 options={"save_blend": False})
""",
     """                                 options={"save_blend": False,
                                          "weighted_normals": weighted})
""", 1),
    ("""                     "save_blend": False, "clear_scene": True})
""",
     """                     "save_blend": False, "clear_scene": True,
                     "weighted_normals": weighted})
""", 1),
]

EDITS = {
    "zoo_keeper/bpylayer/geometry.py": GEOMETRY,
    "zoo_keeper/bpylayer/export.py": EXPORT,
    "zoo_keeper/bpylayer/merge.py": MERGE,
    "zoo_keeper/bpylayer/build.py": BUILD,
    "zoo_keeper/bpylayer/ingest.py": INGEST,
    "tools/zoo_cli.py": CLI,
    "tools/preview_specimen.py": PREVIEW,
}

NEW = {
    "zoo_keeper/core/normals.py": "normals.py",
    "tests/test_weighted_normals.py": "test_weighted_normals.py",
}


def _stage(root, edits):
    """{path: bytes}: every file's new content, every anchor matched exactly
    as often as stated, endings kept; raises before anything is written."""
    staged = {}
    for rel, triples in edits.items():
        p = root / rel
        d = p.read_bytes()
        crlf, lf = d.count(b"\r\n"), d.count(b"\n")
        assert crlf in (0, lf), (rel, "mixed endings")
        t = d.decode("utf-8").replace("\r\n", "\n")
        for old, new, want in triples:
            n = t.count(old)
            assert n == want, (rel, n, want, old[:70])
            t = t.replace(old, new)
        staged[p] = (t.replace("\n", "\r\n") if crlf else t).encode("utf-8")
    return staged


def main():
    v = (ZOO / "VERSION").read_bytes().strip()
    assert v == b"1.86.0", repr(v)
    staged = _stage(ZOO, EDITS)
    new = {}
    for rel, name in NEW.items():
        dst = ZOO / rel
        assert not dst.exists(), dst
        new[dst] = (SRC / name).read_bytes()
    entry = (SRC / "CHANGELOG_1.87.0.md").read_text(encoding="utf-8").replace("\r\n", "\n")
    assert "RESULT_" not in entry, "the changelog still carries an unfilled result"
    cl = ZOO / "CHANGELOG.md"
    data = cl.read_bytes()
    crlf, lf = data.count(b"\r\n"), data.count(b"\n")
    assert crlf in (0, lf), "CHANGELOG.md has mixed endings"
    text = data.decode("utf-8").replace("\r\n", "\n")
    assert text.startswith(CHANGELOG_HEAD) and text.count(CHANGELOG_HEAD) == 1, text[:90]
    # Every anchor matched: now write.
    for p, raw in staged.items():
        p.write_bytes(raw)
    for p, raw in new.items():
        p.write_bytes(raw)
    out = entry + text
    cl.write_bytes((out.replace("\n", "\r\n") if crlf else out).encode("utf-8"))
    vfile = ZOO / "VERSION"
    vraw = vfile.read_bytes()
    vfile.write_bytes(vraw.replace(b"1.86.0", b"1.87.0"))
    print("Zoo 1.86.0 -> 1.87.0")


if __name__ == "__main__":
    main()
