"""Zoo 1.83.0: the getaway van after the walker's first look (roadmap 206).
The walker, 2026-10-08, on 1.82.0's frames: "Looks great, the windows in the
front feel proportionally a little too tall?", the ghost lettering -- "show
me this" -- and "flesh out the bottom of the truck a bit...like giving it a
driveshaft and rear differential". A deeper header, a chassis under the
body, and the ghost of SKEEVY'S WOODER ICE as variant 1.

Whole files from `zoo_van_183/`, each replacing the 1.82.0 file whose sha256
it asserts first: `core/van_forms.py`, `recipes/step_van.py`,
`genome/species/step_van.json`, `tests/test_step_van.py`. Anchored edits
(every anchor once; refuses on a miss): `bpylayer/geometry.py`
(`set_uv_by`), `bpylayer/materials.py` (`make_wear_textured_material`),
`core/prims.py` (`rod`'s `phase`), `tests/test_coincident_faces.py` (the
census note). CHANGELOG and VERSION from `zoo_van_183/CHANGELOG_1.83.0.md`.

    python patch_zoo_van_183.py
    ZOO_ROOT=<copy> python patch_zoo_van_183.py
"""
import hashlib
import os
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
ZOO = pathlib.Path(os.environ.get("ZOO_ROOT") or HERE.parent / "zoo")
SRC = HERE / "zoo_van_183"

#: the 1.82.0 files (e346bf0) these replace, by sha256
WHOLE = {
    "zoo_keeper/core/van_forms.py": ("van_forms.py",
                                     "af9da2c3563c9fba5b553bcd34f92f9546f78a7708753dab1580ee50306b259e"),
    "zoo_keeper/recipes/step_van.py": ("step_van.py",
                                       "9146afe1d9d091a6c0b2189e28fcdd50aac2156ffbd9c0dbd8b48a69fba54ee7"),
    "zoo_keeper/genome/species/step_van.json": ("step_van.json",
                                                "b738c5355bdb785076b252f06deca4142837c9907c81705e87d58abb14df4eec"),
    "tests/test_step_van.py": ("test_step_van.py",
                               "2e2ed7efe51a56ea586567217112c45e406f28288c1830bbcfeda0a3430498f5"),
}


def _edit(path, old, new):
    d = path.read_bytes()
    crlf = b"\r\n" in d
    s = d.decode("utf-8").replace("\r\n", "\n")
    assert s.count(old) == 1, (path.name, s.count(old), old[:60])
    s = s.replace(old, new)
    path.write_bytes((s.replace("\n", "\r\n") if crlf else s).encode("utf-8"))


SET_UV_BY = '''

def set_uv_by(obj, fn):
    """Write every corner's UV from ``fn(co, normal)`` (Zoo 1.83.0): ``co``
    the corner's vertex in the mesh's own space, ``normal`` its face's. The
    getaway van's ghost lettering maps the box's sides by their (y, z) and
    sends every other face past the art's clamped corner; the cube
    projection `bm_to_object` wrote is replaced, not blended.

    Returns the number of corners written; 0 when the object has no UV
    layer, which a caller should treat as the art not landing."""
    mesh = obj.data
    layer = mesh.uv_layers.active
    if layer is None:
        return 0
    verts, loops = mesh.vertices, mesh.loops
    n = 0
    for poly in mesh.polygons:
        nrm = (poly.normal[0], poly.normal[1], poly.normal[2])
        for li in poly.loop_indices:
            v = verts[loops[li].vertex_index].co
            layer.data[li].uv = fn((v[0], v[1], v[2]), nrm)
            n += 1
    return n
'''

WEAR_TEXTURED = '''def make_wear_textured_material(name, image, material_kind):
    """A kind's flat material with ``image`` under its `Wear` colour (Zoo
    1.83.0: the getaway van's ghost lettering). Base Color is the image
    times the colour attribute, so a part painted per corner keeps every
    corner's colour and the image only scales it -- white leaves the paint
    as it was. Roughness and metallic are the kind's, as `make_material`'s
    flat path sets them.

    The multiply is `_wear_multiply`, the same node the skinned path uses,
    and it is load-bearing for the export: a material that reads no vertex
    colour ships COLOR_0 white (the module docstring). Linear filtering,
    clamped: the art is one picture, and a face sent past its corner reads
    its white margin."""
    mat = bpy.data.materials.get(name)
    if mat:
        return mat
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    tree = mat.node_tree
    bsdf = next(n for n in tree.nodes if n.type == "BSDF_PRINCIPLED")
    bsdf.inputs["Roughness"].default_value = ROUGHNESS.get(base_kind(material_kind), 0.6)
    bsdf.inputs["Metallic"].default_value = METALLIC.get(base_kind(material_kind), 0.0)
    tex = tree.nodes.new("ShaderNodeTexImage")
    tex.image = image
    tex.interpolation = "Linear"
    tex.extension = "EXTEND"
    tree.links.new(_wear_multiply(tree, tex.outputs["Color"], name), bsdf.inputs["Base Color"])
    return mat


'''


def main():
    v = (ZOO / "VERSION").read_text(encoding="utf-8").strip()
    assert v == "1.82.0", v
    for rel, (name, sha) in WHOLE.items():
        got = hashlib.sha256((ZOO / rel).read_bytes()).hexdigest()
        assert got == sha, (rel, "is not the 1.82.0 file", got)
    zk = ZOO / "zoo_keeper"
    _edit(zk / "bpylayer" / "geometry.py",
          "            attr.data[li].color = (c[0] * r, c[1] * g, c[2] * b, c[3])\n"
          "            n += 1\n"
          "    return n\n",
          "            attr.data[li].color = (c[0] * r, c[1] * g, c[2] * b, c[3])\n"
          "            n += 1\n"
          "    return n\n" + SET_UV_BY)
    _edit(zk / "bpylayer" / "materials.py",
          "def make_painted_material(name, image, roughness, tile=False, smooth=False):\n",
          WEAR_TEXTURED + "def make_painted_material(name, image, roughness, tile=False, smooth=False):\n")
    _edit(zk / "core" / "prims.py",
          'def rod(part, mat, p0, p1, r0, r1=None, segments=8, bevel=False):\n'
          '    """A faceted frustum from point ``p0`` (radius r0) to ``p1`` (r1), for a\n'
          '    cue, a pipe or a leg that is not vertical."""\n',
          'def rod(part, mat, p0, p1, r0, r1=None, segments=8, bevel=False, phase=0.0):\n'
          '    """A faceted frustum from point ``p0`` (radius r0) to ``p1`` (r1), for a\n'
          '    cue, a pipe or a leg that is not vertical.\n'
          '\n'
          '    ``phase`` turns the rings in radians, as `cyl`\'s does (Zoo 1.83.0). At 0\n'
          '    a vertex sits on the ring\'s first axis, and a rod of 6 or 10 sides laid\n'
          '    level then carries a facet flat on top and one flat underneath, which two\n'
          '    such pipes meeting at an elbow share; ``pi / (2 * segments)`` leaves no\n'
          '    facet square to any axis at 6, 8, 10 or 12 sides."""\n')
    _edit(zk / "core" / "prims.py",
          "            t = 2.0 * math.pi * k / n\n",
          "            t = 2.0 * math.pi * k / n + phase\n")
    _edit(ZOO / "tests" / "test_coincident_faces.py",
          "#: along its own 45-degree facet (`van_forms.CAB_ROOF_INSET`).\n"
          "CENSUS_BUILDS = 363\n",
          "#: along its own 45-degree facet (`van_forms.CAB_ROOF_INSET`).\n"
          "#: 1.83.0: `step_van` redrawn -- a deeper header, a chassis under the\n"
          "#: body -- the same three builds, same tool, Blender 5.1.1: \"3 builds, 0\n"
          "#: with coincident pairs, 0 that did not build\" (5,152 / 5,372 / 5,592\n"
          "#: tris). Corners alone missed three pairs BETWEEN them; the species'\n"
          "#: own test sweeps its chassis at every centimetre of height.\n"
          "CENSUS_BUILDS = 363\n")
    for rel, (name, _sha) in WHOLE.items():
        (ZOO / rel).write_bytes((SRC / name).read_bytes())
    entry = (SRC / "CHANGELOG_1.83.0.md").read_text(encoding="utf-8").replace("\r\n", "\n")
    cl = ZOO / "CHANGELOG.md"
    d = cl.read_bytes()
    assert b"## [1.83.0]" not in d and d.startswith(b"## [1.82.0]")
    crlf = b"\r\n" in d
    cl.write_bytes((entry.replace("\n", "\r\n") if crlf else entry).encode("utf-8") + d)
    (ZOO / "VERSION").write_bytes(b"1.83.0")
    print("1.82.0 -> 1.83.0")


if __name__ == "__main__":
    main()
