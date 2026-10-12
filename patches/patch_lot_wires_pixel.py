"""Lot 0.119.1: a far wire is a faint line, not a dotted one -- drawn a pixel wide at least and faded
by what it covers (factory roadmap 240, build 3, seen in cold run 9263's frames).

Anchored edits, each asserted once, nothing written until all of them matched:
  site_poles.py              the wires' header gains ONE PIXEL; `WIRE_MIN_PX` and `WIRE_SHADER` after
                             `WIRE_COLOUR`; `wire_meshes` writes each vertex's drawn radius as its u,
                             winds every face outward, and shares a ShaderMaterial
  tests/test_site_wires.py   the material test reads the shader material and counts the `vt`s; three
                             tests appended (`lot_wires_pixel/tests_new.py.txt`)
CHANGELOG and VERSION from `lot_wires_pixel/CHANGELOG_0.119.1.md`; `--results-pending` leaves the
RESULT_ keys to `--fill`.

Read before it was written: `_tube` (its quads run round the ring AGAINST the normals: 16 of 16
faces on a three-point wire, measured), `wire_meshes`, `write_godot_scene` (it counts sub_resources
by their `[sub_resource` header element and writes every element as given), Lux's emissive binder
(it casts a surface material `as BaseMaterial3D` and skips the rest) and the package's `warmup.gd`.

    python patches/patch_lot_wires_pixel.py --results-pending && cd lot && python -m pytest -q
    python patches/patch_lot_wires_pixel.py --fill
    LOT_ROOT=<copy> python patches/patch_lot_wires_pixel.py --draft
"""
import hashlib
import os
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
LOT = pathlib.Path(os.environ.get("LOT_ROOT") or HERE.parent / "lot")
SRC = HERE / "lot_wires_pixel"
DRAFT = "--draft" in sys.argv
PENDING = "--results-pending" in sys.argv
FILL = "--fill" in sys.argv
RESULTS = {"RESULT_MEASURED": "result_measured.txt", "RESULT_TESTS": "result_tests.txt",
           "RESULT_SUITE": "result_suite.txt"}
VERSION_WAS, VERSION = b"Lot 0.119.0", b"Lot 0.119.1"
CHANGELOG_HEAD = ("## 0.119.0 - the pole line's wires: the full set along every line and across each "
                  "junction, with the art only\n")
POLES = "site_poles.py"
TEST = "tests/test_site_wires.py"
SHA = {POLES: "18e08350894ea3a3", TEST: "0729c7b0ed36a283"}

HEAD_OLD = ("# (GL Compatibility draws a lit mesh once more for every light that reaches\n"
            "# it). No collision: nothing walks a wire.\n"
            "\n"
            "#: Sag at mid-span, a fraction of the span's length: conductors a few percent,\n")
HEAD_NEW = ("# (GL Compatibility draws a lit mesh once more for every light that reaches\n"
            "# it). No collision: nothing walks a wire.\n"
            "#\n"
            "# ONE PIXEL (0.119.1). A tube a few centimetres across is under a pixel\n"
            "# from about 15 m (a primary) to 30 m (a cable) at the player's camera and\n"
            "# 900 lines, and the rasteriser keeps or drops it pixel by pixel: cold run\n"
            "# 9263's far wires drew as dotted lines. Each vertex carries its wire's\n"
            "# drawn radius as its UV's u, and `WIRE_SHADER` finds the wire's centre from\n"
            "# it, widens a wire thinner than `WIRE_MIN_PX` pixel to that, and fades it\n"
            "# by the share of the widened line the wire really covers: a far wire is a\n"
            "# faint continuous line, as in a photograph, and a near one looks as it did.\n"
            "\n"
            "#: Sag at mid-span, a fraction of the span's length: conductors a few percent,\n")

CONST_OLD = ("WIRE_CELL_M = 32.0\n"
             "WIRE_COLOUR = (0.07, 0.07, 0.07)\n")
CONST_NEW = ("WIRE_CELL_M = 32.0\n"
             "WIRE_COLOUR = (0.07, 0.07, 0.07)\n"
             "#: The narrowest a wire is drawn, in pixels (0.119.1): a thinner one is\n"
             "#: widened to this and faded by the share of it the wire covers.\n"
             "WIRE_MIN_PX = 1.0\n"
             "#: The wires' material (0.119.1). A vertex stands at its wire's centre plus\n"
             "#: NORMAL times the wire's drawn radius, which its u carries, so the vertex\n"
             "#: shader can find the centre and widen the tube about it. Half a pixel at a\n"
             "#: vertex is the clip's w over the projection's y scale and the frame's\n"
             "#: height -- w is the depth in a perspective view and 1 in an orthographic\n"
             "#: one, so the elevated shots hold too -- and a four-sided tube is sqrt(2)\n"
             "#: narrower across a face than across its corners, so the clamp is that much\n"
             "#: wider. Unshaded: no light adds a pass. Written into the scene as a string,\n"
             "#: so no double quote and no backslash.\n"
             'WIRE_SHADER = """shader_type spatial;\n'
             "render_mode unshaded, cull_back;\n"
             "\n"
             "// Lot's overhead wires (site_poles.py, 0.119.1): a wire thinner than min_px\n"
             "// pixels is drawn that wide and faded by the share of it the wire covers.\n"
             "uniform vec4 colour : source_color = vec4(0.07, 0.07, 0.07, 1.0);\n"
             "uniform float min_px = 1.0;\n"
             "varying float coverage;\n"
             "\n"
             "void vertex() {\n"
             "    float r = UV.x;\n"
             "    vec3 centre = VERTEX - NORMAL * r;\n"
             "    vec4 clip = PROJECTION_MATRIX * (MODELVIEW_MATRIX * vec4(centre, 1.0));\n"
             "    float half_px = abs(clip.w) / (abs(PROJECTION_MATRIX[1][1]) * VIEWPORT_SIZE.y);\n"
             "    float drawn = max(r, 1.41421356 * half_px * min_px);\n"
             "    coverage = r / drawn;\n"
             "    VERTEX = centre + NORMAL * drawn;\n"
             "}\n"
             "\n"
             "void fragment() {\n"
             "    ALBEDO = colour.rgb;\n"
             "    ALPHA = colour.a * coverage;\n"
             "}\n"
             '"""\n')

DOC_OLD = ("    beside the scene (``files``: name -> text) stood by a MeshInstance3D that\n"
           "    casts no shadow, takes no GI and shares one unshaded material. ``base`` is\n")
DOC_NEW = ("    beside the scene (``files``: name -> text) stood by a MeshInstance3D that\n"
           "    casts no shadow, takes no GI and shares one unshaded material, which holds\n"
           "    a wire to a pixel (`WIRE_SHADER`, 0.119.1). ``base`` is\n")

LOOP_OLD = ("        verts, norms, faces = [], [], []\n"
            "        for a, b in cells[cell]:\n"
            "            for wire in sorted(WIRES):\n"
            "                v, nrm, q = _tube(wire_path(a, b, wire, base), WIRE_R[_kind(wire)])\n"
            "                o = len(verts)\n"
            "                verts += v\n"
            "                norms += nrm\n"
            "                faces += [(o + i0 + 1, o + i1 + 1, o + i2 + 1, o + i3 + 1) for i0, i1, i2, i3 in q]\n")
LOOP_NEW = ("        verts, norms, radii, faces = [], [], [], []\n"
            "        for a, b in cells[cell]:\n"
            "            for wire in sorted(WIRES):\n"
            "                r = WIRE_R[_kind(wire)]\n"
            "                v, nrm, q = _tube(wire_path(a, b, wire, base), r)\n"
            "                o = len(verts)\n"
            "                verts += v\n"
            "                norms += nrm\n"
            "                radii += [r] * len(v)\n"
            "                faces += [(o + i0 + 1, o + i1 + 1, o + i2 + 1, o + i3 + 1) for i0, i1, i2, i3 in q]\n")

LINES_OLD = ("        # Godot's frame: plan (x, y, z up) is (x, z, -y)\n"
             '        lines += [f"v {x:.4f} {z:.4f} {-y:.4f}" for x, y, z in verts]\n'
             '        lines += [f"vn {x:.4f} {z:.4f} {-y:.4f}" for x, y, z in norms]\n'
             "        for f0, f1, f2, f3 in faces:\n"
             '            lines.append(f"f {f0}//{f0} {f1}//{f1} {f2}//{f2}")\n'
             '            lines.append(f"f {f0}//{f0} {f2}//{f2} {f3}//{f3}")\n')
LINES_NEW = ("        # Godot's frame: plan (x, y, z up) is (x, z, -y), a rotation, so a\n"
             "        # face's winding survives it. Each vertex's u is its wire's drawn\n"
             "        # radius, which `WIRE_SHADER` reads (0.119.1).\n"
             '        lines += [f"v {x:.4f} {z:.4f} {-y:.4f}" for x, y, z in verts]\n'
             '        lines += [f"vt {r:.4f} 0" for r in radii]\n'
             '        lines += [f"vn {x:.4f} {z:.4f} {-y:.4f}" for x, y, z in norms]\n'
             "        # `_tube`'s quads run round the ring against the normals; reversed, a\n"
             "        # face is counter-clockwise about its outward normal (OBJ's front) and\n"
             "        # the material culls the back, so one layer of a wire draws and its\n"
             "        # fade is its coverage (0.119.1; 0.119.0 drew both sides)\n"
             "        for f0, f1, f2, f3 in faces:\n"
             '            lines.append(f"f {f0}/{f0}/{f0} {f2}/{f2}/{f2} {f1}/{f1}/{f1}")\n'
             '            lines.append(f"f {f0}/{f0}/{f0} {f3}/{f3}/{f3} {f2}/{f2}/{f2}")\n')

MAT_OLD = ("    if cells:\n"
           "        r, g, b = WIRE_COLOUR\n"
           "        sub += ['[sub_resource type=\"StandardMaterial3D\" id=\"Mat_site_wires\"]',\n"
           "                \"shading_mode = 0\",\n"
           "                f\"albedo_color = Color({r:g}, {g:g}, {b:g}, 1)\",\n"
           "                \"cull_mode = 2\", \"\"]\n"
           "    return body, sub, files\n")
MAT_NEW = ("    if cells:\n"
           "        cr, cg, cb = WIRE_COLOUR\n"
           "        sub += ['[sub_resource type=\"Shader\" id=\"Shader_site_wires\"]',\n"
           "                f'code = \"{WIRE_SHADER}\"', \"\",\n"
           "                '[sub_resource type=\"ShaderMaterial\" id=\"Mat_site_wires\"]',\n"
           "                'shader = SubResource(\"Shader_site_wires\")',\n"
           "                f\"shader_parameter/colour = Color({cr:g}, {cg:g}, {cb:g}, 1)\",\n"
           "                f\"shader_parameter/min_px = {WIRE_MIN_PX:g}\", \"\"]\n"
           "    return body, sub, files\n")

TEST_OLD = ("    assert sub[0] == '[sub_resource type=\"StandardMaterial3D\" id=\"Mat_site_wires\"]'\n"
            "    assert \"shading_mode = 0\" in sub\n"
            "    ring = site_poles.WIRE_SIDES * (site_poles.WIRE_SEGMENTS + 1)\n"
            "    verts = sum(t.count(\"\\nv \") for t in files.values())\n"
            "    norms = sum(t.count(\"\\nvn \") for t in files.values())\n"
            "    faces = sum(t.count(\"\\nf \") for t in files.values())\n"
            "    assert verts == norms == ring * len(site_poles.WIRES) * len(spans)\n")
TEST_NEW = ("    # the material holds a wire to a pixel (0.119.1): a shader, unshaded\n"
            "    assert sub[0] == '[sub_resource type=\"Shader\" id=\"Shader_site_wires\"]'\n"
            "    assert '[sub_resource type=\"ShaderMaterial\" id=\"Mat_site_wires\"]' in sub\n"
            "    assert \"render_mode unshaded, cull_back;\" in site_poles.WIRE_SHADER\n"
            "    ring = site_poles.WIRE_SIDES * (site_poles.WIRE_SEGMENTS + 1)\n"
            "    verts = sum(t.count(\"\\nv \") for t in files.values())\n"
            "    uvs = sum(t.count(\"\\nvt \") for t in files.values())\n"
            "    norms = sum(t.count(\"\\nvn \") for t in files.values())\n"
            "    faces = sum(t.count(\"\\nf \") for t in files.values())\n"
            "    assert verts == uvs == norms == ring * len(site_poles.WIRES) * len(spans)\n")


def _eol(raw, rel):
    crlf = raw.count(b"\r\n")
    lf = raw.count(b"\n")
    assert crlf in (0, lf), (rel, "mixed line endings", crlf, lf)
    return b"\r\n" if crlf else b"\n"


def _src(name):
    return (SRC / name).read_bytes().decode("utf-8").replace("\r\n", "\n")


def _read(rel):
    p = LOT / rel
    raw = p.read_bytes()
    got = hashlib.sha256(raw.replace(b"\r\n", b"\n")).hexdigest()[:16]
    assert got == SHA[rel], (rel, "is not the file this patch read", got)
    return p, _eol(raw, rel), raw.decode("utf-8").replace("\r\n", "\n")


def _once(text, old, new, what):
    assert text.count(old) == 1, (what, text.count(old))
    return text.replace(old, new)


def fill():
    assert (LOT / "VERSION").read_bytes().strip() == VERSION, (LOT / "VERSION").read_bytes()
    results = {}
    for key, name in RESULTS.items():
        value = (SRC / name).read_text(encoding="utf-8").strip()
        assert value and "RESULT_" not in value and not value.endswith("."), (name, value[-40:])
        results[key] = value
    writes = {}
    for path, rel in [(LOT / "CHANGELOG.md", "CHANGELOG.md"), (SRC / "CHANGELOG_0.119.1.md", "the entry")]:
        raw = path.read_bytes()
        eol = _eol(raw, rel)
        text = raw.decode("utf-8").replace("\r\n", "\n")
        for key, value in results.items():
            assert text.count(key) == 1, (rel, key, text.count(key))
            text = text.replace(key, value)
        writes[path] = text.encode("utf-8").replace(b"\n", eol)
    for path, data in writes.items():
        path.write_bytes(data)
    print("Lot 0.119.1: results filled")


def main():
    if FILL:
        return fill()
    if DRAFT and not os.environ.get("LOT_ROOT"):
        sys.exit("refusing: --draft is for a LOT_ROOT copy, never the repo")
    assert (LOT / "VERSION").read_bytes().strip() == VERSION_WAS, (LOT / "VERSION").read_bytes()
    entry = _src("CHANGELOG_0.119.1.md")
    assert entry.startswith("## 0.119.1 - "), entry[:40]
    if not DRAFT:
        left = entry
        if PENDING:
            for key in RESULTS:
                left = left.replace(key, "")
        assert "RESULT_" not in left, "the changelog still carries an unfilled result"
    pp, p_eol, poles = _read(POLES)
    assert "WIRE_SHADER" not in poles, "already applied"
    poles = _once(poles, HEAD_OLD, HEAD_NEW, "the wires' header")
    poles = _once(poles, CONST_OLD, CONST_NEW, "the wire constants")
    poles = _once(poles, DOC_OLD, DOC_NEW, "wire_meshes' docstring")
    poles = _once(poles, LOOP_OLD, LOOP_NEW, "wire_meshes' tubes")
    poles = _once(poles, LINES_OLD, LINES_NEW, "wire_meshes' OBJ lines")
    poles = _once(poles, MAT_OLD, MAT_NEW, "wire_meshes' material")
    tp, t_eol, test = _read(TEST)
    test = _once(test, TEST_OLD, TEST_NEW, "the material test")
    test = test.rstrip("\n") + "\n" + _src("tests_new.py.txt")
    cl = LOT / "CHANGELOG.md"
    cl_raw = cl.read_bytes()
    cl_eol = _eol(cl_raw, "CHANGELOG.md")
    cl_text = cl_raw.decode("utf-8").replace("\r\n", "\n")
    assert cl_text.startswith(CHANGELOG_HEAD) and cl_text.count(CHANGELOG_HEAD) == 1, cl_text[:160]
    # every anchor matched: now write
    pp.write_bytes(poles.replace("\n", p_eol.decode()).encode("utf-8"))
    tp.write_bytes(test.replace("\n", t_eol.decode()).encode("utf-8"))
    cl.write_bytes((entry.rstrip("\n") + "\n\n" + cl_text).replace("\n", cl_eol.decode()).encode("utf-8"))
    (LOT / "VERSION").write_bytes(VERSION)
    print("Lot 0.119.0 -> 0.119.1" + (" (DRAFT)" if DRAFT else ""))


if __name__ == "__main__":
    main()
