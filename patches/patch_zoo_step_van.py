"""Zoo 1.82.0: the crew's getaway van (roadmap 206). The walker, 2026-10-07:
"a Box Truck. Like a Chevrolet P30. Matte Black....faded, with patina, like
a worn in truck...that's been on many jobs.... Our very own 'millenial
falcon'", and "location of the getaway vehicle should be the same as the
missions spawn point. you spawn, do the job, then return to the car". A new
species, `step_van`: a P30-style step van whose paint is its history, on
one material, five submissions.

New files copied from `zoo_step_van/`: `core/van_forms.py`,
`recipes/step_van.py`, `genome/species/step_van.json`,
`tests/test_step_van.py`. Anchored edits (every anchor once; refuses on a
miss): `bpylayer/geometry.py` (`tint_wear_by`), `bpylayer/materials.py`
and `core/skins.py` (the `paint_matte` kind), `tests/test_genome.py` (the
hand-authored species set), and the two audits that count species by a
literal on purpose (`tests/test_coincident_faces.py`,
`tests/test_theme_style_resolution.py`), and `.gitignore` (the probe's
default output). CHANGELOG and VERSION from
`zoo_step_van/CHANGELOG_1.82.0.md`.

    python patch_zoo_step_van.py
    ZOO_ROOT=<copy> python patch_zoo_step_van.py
"""
import os
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
ZOO = pathlib.Path(os.environ.get("ZOO_ROOT") or HERE.parent / "zoo")
SRC = HERE / "zoo_step_van"


def _edit(path, old, new):
    d = path.read_bytes()
    crlf = b"\r\n" in d
    s = d.decode("utf-8").replace("\r\n", "\n")
    assert s.count(old) == 1, (path.name, s.count(old), old[:60])
    s = s.replace(old, new)
    path.write_bytes((s.replace("\n", "\r\n") if crlf else s).encode("utf-8"))


TINT_WEAR_BY = '''def tint_wear_by(obj, fn):
    """`tint_wear` with a colour that varies over the part (Zoo 1.82.0).

    ``fn(co, normal)`` returns the RGB for one corner: ``co`` its vertex's
    position in the mesh's own space, ``normal`` its face's normal. The
    getaway van's paint -- sun-chalked up high, dusty low down, rust at the
    arches -- rides ONE material this way rather than one material a colour,
    the cargo container's pattern the draw-call rule forbids. Multiplied into
    `Wear` like `tint_wear`, so the crease darkening `wear_colors` wrote
    stays under it.

    Returns the number of corners tinted; 0 when the object carries no
    `Wear` layer, which a caller should treat as the tint not landing."""
    mesh = obj.data
    try:
        attr = mesh.color_attributes[WEAR_LAYER]
    except (KeyError, AttributeError):
        return 0
    verts, loops = mesh.vertices, mesh.loops
    n = 0
    for poly in mesh.polygons:
        nrm = (poly.normal[0], poly.normal[1], poly.normal[2])
        for li in poly.loop_indices:
            v = verts[loops[li].vertex_index].co
            r, g, b = fn((v[0], v[1], v[2]), nrm)
            c = attr.data[li].color
            attr.data[li].color = (c[0] * r, c[1] * g, c[2] * b, c[3])
            n += 1
    return n
'''


def main():
    v = (ZOO / "VERSION").read_text(encoding="utf-8").strip()
    assert v == "1.81.0", v
    zk = ZOO / "zoo_keeper"
    assert not (zk / "core" / "van_forms.py").exists(), "already applied"
    for name, dst in (("van_forms.py", zk / "core" / "van_forms.py"),
                      ("step_van.py", zk / "recipes" / "step_van.py"),
                      ("step_van.json", zk / "genome" / "species" / "step_van.json"),
                      ("test_step_van.py", ZOO / "tests" / "test_step_van.py")):
        dst.write_bytes((SRC / name).read_bytes())
    _edit(zk / "bpylayer" / "geometry.py",
          '    return len(attr.data)\n\n# --- object plumbing',
          '    return len(attr.data)\n\n\n' + TINT_WEAR_BY + '\n# --- object plumbing')
    _edit(zk / "bpylayer" / "materials.py",
          '             "wood_panel": 0.52, "slatwall": 0.55}\n',
          '             "wood_panel": 0.52, "slatwall": 0.55,\n'
          "             # THE GETAWAY VAN'S PAINT (1.82.0, roadmap 206): flat black gone\n"
          '             # chalky. Object-owned like the prop metals, and with no skin\n'
          "             # pack in any theme on purpose -- the colour is the van's own,\n"
          '             # painted per corner (`geometry.tint_wear_by`). Between `cloth`\n'
          '             # (0.85) and sun-faded block paint (0.88): matte, never gloss,\n'
          '             # where `metal_painted` is semi-gloss enamel at 0.45.\n'
          '             "paint_matte": 0.86}\n')
    _edit(zk / "bpylayer" / "materials.py",
          '            "metal_painted": 0.0, "metal_bare": 0.90,\n',
          '            "metal_painted": 0.0, "metal_bare": 0.90,\n'
          '            # paint is a dielectric however flat it dries (1.82.0)\n'
          '            "paint_matte": 0.0,\n')
    _edit(zk / "core" / "skins.py",
          '               "wood_panel", "slatwall")\n',
          '               "wood_panel", "slatwall",\n'
          "               # THE GETAWAY VAN'S PAINT (1.82.0, roadmap 206): flat black,\n"
          '               # object-owned, and deliberately without a pack in any theme --\n'
          '               # the van carries its own colour per corner, so a theme pack\n'
          '               # would only repaint it.\n'
          '               "paint_matte")\n')
    _edit(ZOO / "tests" / "test_genome.py",
          '                # lit deck of pans and cards, logs cut to the glass\n'
          '                "deli_case"}\n',
          '                # lit deck of pans and cards, logs cut to the glass\n'
          '                "deli_case",\n'
          "                # the crew's getaway van (1.82.0, roadmap 206): a P30-style\n"
          '                # step van, matte black gone chalky, parked at the spawn\n'
          '                "step_van"}\n')
    # the two audits that count species by a literal on purpose
    _edit(ZOO / "tests" / "test_coincident_faces.py",
          'CENSUS_BUILDS = 360\n',
          '#: 1.82.0: `step_van`, three builds more, same tool, Blender 5.1.1: "3\n'
          '#: builds, 0 with coincident pairs, 0 that did not build" (4,640 / 4,860 /\n'
          '#: 5,080 tris). The probe found 10-12 pairs a build first, every one fixed\n'
          "#: at its source: seat backs flush with their bases, the engine cover's and\n"
          "#: the dash's bottoms on one plane, the grille bars and the rear seams 2 mm\n"
          '#: off what they stood on (the window is <= 2.0 mm, so a 2 mm fix still\n'
          '#: read), the B-pillar 2 mm off the rear door seam, and the cab roof shifted\n'
          '#: along its own 45-degree facet (`van_forms.CAB_ROOF_INSET`).\n'
          'CENSUS_BUILDS = 363\n')
    _edit(ZOO / "tests" / "test_theme_style_resolution.py",
          '    assert len(_genomes()) == 93 + len(_minted), len(_genomes())\n',
          "    # 1.82.0: 94, + step_van, its `delco` row a copy of its `default`: the\n"
          "    # crew's van is the same van in every theme.\n"
          '    assert len(_genomes()) == 94 + len(_minted), len(_genomes())\n')
    _edit(ZOO / ".gitignore",
          '_preview/\n_census/\n',
          '_preview/\n_census/\n'
          '# tools/coplanar_probe.py --species writes its builds to ./_coplanar unless\n'
          '# given --out (2026-10-07: three GLBs and their meta stood loose after the\n'
          "# van's probes)\n"
          '_coplanar/\n')
    entry = (SRC / "CHANGELOG_1.82.0.md").read_text(encoding="utf-8").replace("\r\n", "\n")
    cl = ZOO / "CHANGELOG.md"
    d = cl.read_bytes()
    assert b"## [1.82.0]" not in d and d.startswith(b"## [1.81.0]")
    crlf = b"\r\n" in d
    cl.write_bytes((entry.replace("\n", "\r\n") if crlf else entry).encode("utf-8") + d)
    (ZOO / "VERSION").write_bytes(b"1.82.0")
    print("1.81.0 -> 1.82.0")


if __name__ == "__main__":
    main()
