"""Lot 0.115.0: the plate tile follows the bake, and the paint is cut into cells (roadmap 231,
the second lever and the first lever's own gate).

Anchored edits in `lot.py` (`MESH_TILE_BAKED` and `mesh_tile(site_spec)` beside `MESH_TILE`;
`_mesh_child_lines`, `_box_node` and `_yaw_box_node` take `tile`; `_outdoor_nodes` reads the
site's tile and passes it to the plate families; `_marking_meshes` writes one mesh per paint
colour PER `PAINT_CELL_M` CELL, the colour's one material shared -- cold run 9236's paired
census put each level-wide paint mesh under 21 live lights against the cap of 8; the caller-less
`_yaw_quad_node` and the `uv_offset` only it passed to `_mat_sub` are removed), four edits to
`tests/test_marking_meshes.py` (the cells) and a new `tests/test_mesh_tile_render.py`; each file
pinned by hash and each anchor asserted once, nothing written on a miss; the file's own line
endings kept. Applies on Lot 0.114.0. CHANGELOG and VERSION from
`lot_mesh_tile/CHANGELOG_0.115.0.md`; `--suite-pending` leaves RESULT_SUITE to `--fill`.

    python patches/patch_lot_mesh_tile.py --suite-pending && cd lot && python -m pytest -q
    python patches/patch_lot_mesh_tile.py --fill
    LOT_ROOT=<copy> python patches/patch_lot_mesh_tile.py --draft
"""
import hashlib
import os
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
LOT = pathlib.Path(os.environ.get("LOT_ROOT") or HERE.parent / "lot")
SRC = HERE / "lot_mesh_tile"
DRAFT = "--draft" in sys.argv
PENDING = "--suite-pending" in sys.argv
FILL = "--fill" in sys.argv
VERSION_WAS, VERSION = b"Lot 0.114.0", b"Lot 0.115.0"
CHANGELOG_HEAD = "## 0.114.0 - the road paint as one mesh per colour, beside the scene\n"
SHA = {"lot.py": "0e2a98543ab0ec79",
       "tests/test_marking_meshes.py": "a1a400ca4e5b0c5e"}
NEW_TEST = "tests/test_mesh_tile_render.py"

TILE_OLD = "MESH_TILE = 8.0\n\n\ndef _mesh_tiles(sx, sz, tile=MESH_TILE):\n"
TILE_NEW = '''MESH_TILE = 8.0

#: The tile where the package BAKES its lights (0.115.0, roadmap 231), taken
#: when the site spec says so (`mesh_tile`). Godot 4.7's culler pairs no
#: BAKE_STATIC light with a mesh that has a lightmap
#: (servers/rendering/renderer_scene_cull.cpp, `_scene_cull`; Level Factory
#: 0.159.0's paired census), so under the bake the per-mesh cap binds only
#: through the lights left live -- the failing tubes, the cycling poles and
#: the spots: cold run 9233 left 29 rigs of 235 live, and its paired census
#: read 2,895 of 3,966 lightmapped meshes under no light at all, 915 under
#: one, the worst plate under nine. The 8 m tile above was priced against
#: LIVE lights and cost that level 521 of its 795 boxes. 32 m is a quarter of
#: a 128 m plate side; the first package built with it is its proof (the
#: paired census: no mesh over 8 live lights), and the number moves if the
#: census says so. Only the PLATE FAMILIES take it -- the ground, the slabs,
#: the bands, the fields, the pads, the walls; a cover or a blocker is under
#: 8 m anyway. Zoo's `PLATE_TILE` and Deli Counter's `SLAB_TILE` are the
#: same law for interiors and have not moved: each is its own decision.
MESH_TILE_BAKED = 32.0

#: The cell the road paint is cut into, a mesh a colour a cell (0.115.0,
#: roadmap 231): the same per-mesh cap, measured on the first lever. Cold run
#: 9236 shipped 0.114.0's one mesh a colour, and its paired census put each
#: under 21 live lights against the cap of 8 -- a mesh whose box is the whole
#: plate reaches the failing tube behind every storefront, and the engine
#: binds the first 8 it finds, so a pole left live over a crosswalk could be
#: one of the 13 it drops. A cell of the baked tile's size keeps each piece
#: under the lights within its reach; its proof is the same census on the
#: first package built with it.
PAINT_CELL_M = 32.0


def mesh_tile(site_spec) -> float:
    """The tile the site's plate families are cut to: `render.mesh_tile_m`
    when the spec names one, else MESH_TILE_BAKED when `render.lights_baked`
    is true (Level Factory 0.178.0 writes it from its export's own default),
    else MESH_TILE -- a spec that says nothing draws as before, byte for
    byte. A tile under a metre, or not a number, is refused rather than
    drawn: a sliver law is a defect, not a setting."""
    r = (site_spec or {}).get("render") or {}
    if r.get("mesh_tile_m") is not None:
        t = float(r["mesh_tile_m"])
        if not t >= 1.0:
            raise ValueError(f"render.mesh_tile_m must be >= 1 m, got {r['mesh_tile_m']!r}")
        return t
    return MESH_TILE_BAKED if r.get("lights_baked") else MESH_TILE


def _mesh_tiles(sx, sz, tile=MESH_TILE):
'''

MCL_DEF_OLD = "def _mesh_child_lines(name, size, color, skin=None):\n"
MCL_DEF_NEW = "def _mesh_child_lines(name, size, color, skin=None, tile=None):\n"
MCL_DOC_OLD = "    StaticBody3D, tiled to MESH_TILE. Shared by `_box_node` and\n"
MCL_DOC_NEW = ("    StaticBody3D, tiled to ``tile`` -- the site's `mesh_tile` (0.115.0), None\n"
               "    meaning MESH_TILE. Shared by `_box_node` and\n")
MCL_TILES_OLD = "    for suffix, dx, dz, tx, tz in _mesh_tiles(sx, sz):\n"
MCL_TILES_NEW = "    for suffix, dx, dz, tx, tz in _mesh_tiles(sx, sz, tile or MESH_TILE):\n"

BOX_DEF_OLD = "def _box_node(name, size, at_xyz, color=None, skin=None, visual=True):\n"
BOX_DEF_NEW = "def _box_node(name, size, at_xyz, color=None, skin=None, visual=True, tile=None):\n"
BOX_CALL_OLD = "    mesh_body, mesh_sub = _mesh_child_lines(name, size, color, skin) if visual else ([], [])\n"
BOX_CALL_NEW = ("    mesh_body, mesh_sub = (_mesh_child_lines(name, size, color, skin, tile=tile)\n"
                "                           if visual else ([], []))\n")
YAW_DEF_OLD = "def _yaw_box_node(name, size, center_godot, yaw_deg, color=None, skin=None):\n"
YAW_DEF_NEW = "def _yaw_box_node(name, size, center_godot, yaw_deg, color=None, skin=None, tile=None):\n"
YAW_CALL_OLD = "    mesh_body, mesh_sub = _mesh_child_lines(name, size, color, skin)\n"
YAW_CALL_NEW = "    mesh_body, mesh_sub = _mesh_child_lines(name, size, color, skin, tile=tile)\n"

QUAD_RE = re.compile(r"def _yaw_quad_node\(.*?\n\n\n(?=def _mat_sub\()", re.S)
MAT_DEF_OLD = "def _mat_sub(name, color, skin=None, tint=None, uv_offset=None, triplanar=True):\n"
MAT_DEF_NEW = "def _mat_sub(name, color, skin=None, tint=None, triplanar=True):\n"
MAT_OFF_OLD = ("        if uv_offset is not None:\n"
               "            u, v, w = uv_offset\n"
               "            lines.append(f'uv1_offset = Vector3({u:.6g}, {v:.6g}, {w:.6g})')\n")

DOC_OLD = ("    roadmap 231): ONE mesh per paint colour, every marking a flat quad in it\n"
           "    on the paint's top face, written as an OBJ beside the scene (``files``:\n"
           "    file name -> text) and stood by one MeshInstance3D with one material.\n")
DOC_NEW = ("    roadmap 231): ONE mesh per paint colour PER CELL -- a `PAINT_CELL_M` square\n"
           "    of the plan, by each marking's centre (0.115.0) -- every marking a flat\n"
           "    quad in it on the paint's top face, written as an OBJ beside the scene\n"
           "    (``files``: file name -> text), each stood by a MeshInstance3D sharing\n"
           "    the colour's one material.\n"
           "\n"
           "    WHY A CELL. Cold run 9236 shipped one mesh a colour and its paired light\n"
           "    census (Level Factory 0.159.0's) put each under 21 live lights against\n"
           "    the engine's cap of 8 a mesh: a mesh whose box is the plate reaches every\n"
           "    failing tube behind every storefront, and the engine binds the first 8.\n"
           "    A cell keeps each piece under the lights within its reach, and culls as\n"
           "    a piece; the draws it adds are the cells in view, a dozen where 227 were.\n")
LOOP_OLD = ("    groups = {}\n"
            "    for m in marks:\n"
            "        groups.setdefault(tuple(float(v) for v in m[\"color\"]), []).append(m)\n"
            "    body, sub, files = [], [], {}\n"
            "    for color in sorted(groups):\n"
            "        name = f\"site_marks_{_colour_slug(color)}\"\n"
            "        verts, uvs, faces = [], [], []\n"
            "        for m in groups[color]:\n")
LOOP_NEW = ("    groups = {}\n"
            "    for m in marks:\n"
            "        cell = (int(math.floor(float(m[\"at\"][0]) / PAINT_CELL_M)),\n"
            "                int(math.floor(float(m[\"at\"][1]) / PAINT_CELL_M)))\n"
            "        groups.setdefault((tuple(float(v) for v in m[\"color\"]),) + cell, []).append(m)\n"
            "    body, sub, files = [], [], {}\n"
            "    done = set()\n"
            "    for key in sorted(groups):\n"
            "        color, cx, cy = key\n"
            "        slug = _colour_slug(color)\n"
            "        # the cell in the name, offset so a westerly or southerly cell\n"
            "        # carries no sign: c500_500 holds the origin\n"
            "        name = f\"site_marks_{slug}_c{cx + 500:03d}_{cy + 500:03d}\"\n"
            "        verts, uvs, faces = [], [], []\n"
            "        for m in groups[key]:\n")
LINES_OLD = ("        lines = [f\"# Lot: the site's road paint, colour {_colour_slug(color)}, \"\n"
             "                 f\"{len(groups[color])} marking(s), a quad each\", f\"o {name}\"]\n")
LINES_NEW = ("        lines = [f\"# Lot: the site's road paint, colour {slug}, cell ({cx}, {cy}) of \"\n"
             "                 f\"{PAINT_CELL_M:g} m, {len(groups[key])} marking(s), a quad each\",\n"
             "                 f\"o {name}\"]\n")
TAIL_OLD = ("        body += [f'[node name=\"{name}\" type=\"MeshInstance3D\" parent=\".\"]',\n"
            "                 f'mesh = ExtResource(\"{name}\")',\n"
            "                 f'material_override = SubResource(\"Mat_{name}\")', '']\n"
            "        mat = _mat_sub(name, color, paint, tint=color if paint else None, triplanar=False)\n"
            "        mat.insert(len(mat) - 1, 'cull_mode = 2')\n"
            "        sub += mat\n"
            "    return body, sub, files\n")
TAIL_NEW = ("        body += [f'[node name=\"{name}\" type=\"MeshInstance3D\" parent=\".\"]',\n"
            "                 f'mesh = ExtResource(\"{name}\")',\n"
            "                 f'material_override = SubResource(\"Mat_site_marks_{slug}\")', '']\n"
            "        if slug not in done:\n"
            "            # one material a colour, shared by its cells\n"
            "            done.add(slug)\n"
            "            mat = _mat_sub(f\"site_marks_{slug}\", color, paint,\n"
            "                           tint=color if paint else None, triplanar=False)\n"
            "            mat.insert(len(mat) - 1, 'cull_mode = 2')\n"
            "            sub += mat\n"
            "    return body, sub, files\n")

# tests/test_marking_meshes.py: the cells
T_IMP_OLD = "import json\nimport os\nimport sys\n"
T_IMP_NEW = "import json\nimport math\nimport os\nimport re\nimport sys\n"
T_FILES_OLD = "    assert len(files) == len(colours) >= 2\n"
T_FILES_NEW = ("    assert len(files) >= len(colours) >= 2\n"
               "    assert all(re.fullmatch(r\"site_marks_\\d{3}_\\d{3}_\\d{3}_c\\d{3}_\\d{3}\\.obj\", f)\n"
               "               for f in files), sorted(files)\n")
T_MAT_OLD = ("        assert f'mesh = ExtResource(\"{n}\")' in txt and "
             "f'material_override = SubResource(\"Mat_{n}\")' in txt\n")
T_MAT_NEW = ("        assert f'mesh = ExtResource(\"{n}\")' in txt\n"
             "        assert f'material_override = SubResource(\"Mat_{n[:n.index(\"_c\")]}\")' in txt\n")
T_COUNT_OLD = "    assert len(mats) == len(files)\n"
T_COUNT_NEW = "    assert len(mats) == len(colours)            # one material a colour, shared by its cells\n"
T_CELLS = '''

def test_the_paint_is_cut_into_cells_by_each_markings_centre():
    """0.115.0: cold run 9236's paired census put one level-wide paint mesh under
    21 live lights against the engine's cap of 8 -- a mesh whose box is the
    plate reaches every failing tube behind every storefront. A cell of
    `PAINT_CELL_M` a colour keeps each piece under the lights within its reach,
    and the colour's one material is shared by its cells."""
    spec = _spec()
    files = {}
    body, _sub = lot._outdoor_nodes(spec, files=files)
    cell = lot.PAINT_CELL_M
    for fname, text in files.items():
        m = re.fullmatch(r"site_marks_(\\d{3}_\\d{3}_\\d{3})_c(\\d{3})_(\\d{3})\\.obj", fname)
        assert m, fname
        cx, cy = int(m.group(2)) - 500, int(m.group(3)) - 500
        for verts, _uv in _quads(text):
            px = sum(x for x, _y, _z in verts) / 4.0
            py = -sum(z for _x, _y, z in verts) / 4.0
            assert (math.floor(px / cell), math.floor(py / cell)) == (cx, cy), (fname, px, py)
    colours = {f.split("_c")[0] for f in files}
    assert len(files) > len(colours)                 # the probe's streets span several cells
    nodes = [l for l in body if l.startswith('[node name="site_marks_')]
    assert len(nodes) == len(files)
'''

OUT_OLD = ("    floors = set() if self_flooring is None else set(self_flooring)\n"
           "\n"
           "    import site_extent\n")
OUT_NEW = ("    floors = set() if self_flooring is None else set(self_flooring)\n"
           "    # THE PLATE TILE (0.115.0, roadmap 231): read off the spec's `render`,\n"
           "    # MESH_TILE_BAKED where the package bakes its lights, MESH_TILE otherwise.\n"
           "    tile = mesh_tile(site_spec)\n"
           "    if tile != MESH_TILE:\n"
           "        print(f\"[lot] plate tile {tile:g} m: the site spec's render says the \"\n"
           "              f\"lights bake (MESH_TILE {MESH_TILE:g} m under live lights)\")\n"
           "\n"
           "    import site_extent\n")

# the plate families: each call's closing line gains the tile
CALLS = [
    ('                               GROUND_COLOR, skin=skins.get("ground"))\n',
     '                               GROUND_COLOR, skin=skins.get("ground"), tile=tile)\n'),
    ('                               PATH_COLOR, skin=skins.get("path"))\n',
     '                               PATH_COLOR, skin=skins.get("path"), tile=tile)\n'),
    ('                           COURT_COLOR, skin=skins.get("courtyard"))\n',
     '                           COURT_COLOR, skin=skins.get("courtyard"), tile=tile)\n'),
    ('                               FIELD_COLOR, skin=skins.get("parking"))\n',
     '                               FIELD_COLOR, skin=skins.get("parking"), tile=tile)\n'),
    ('                           YARD_COLOR, skin=skins.get("yard"))\n',
     '                           YARD_COLOR, skin=skins.get("yard"), tile=tile)\n'),
    ('            bl, sr = _box_node(name, size, at_xyz, PERIM_COLOR, visual=seen)\n',
     '            bl, sr = _box_node(name, size, at_xyz, PERIM_COLOR, visual=seen, tile=tile)\n'),
    ('            skin=skins.get("sidewalk" if s["family"] == "sidewalk" else "road"))\n',
     '            skin=skins.get("sidewalk" if s["family"] == "sidewalk" else "road"),\n'
     '            tile=tile)\n'),
    ('                               SIDEWALK_COLOR, skin=skins.get("sidewalk"))\n',
     '                               SIDEWALK_COLOR, skin=skins.get("sidewalk"), tile=tile)\n'),
]


def _eol(raw, rel):
    crlf = raw.count(b"\r\n")
    lf = raw.count(b"\n")
    assert crlf in (0, lf), (rel, "mixed line endings", crlf, lf)
    return b"\r\n" if crlf else b"\n"


def _src(name):
    return (SRC / name).read_bytes().replace(b"\r\n", b"\n").decode("utf-8")


def _once(text, old, new, what):
    assert text.count(old) == 1, (what, text.count(old))
    return text.replace(old, new)


def _read(rel):
    p = LOT / rel
    raw = p.read_bytes()
    got = hashlib.sha256(raw.replace(b"\r\n", b"\n")).hexdigest()[:16]
    assert got == SHA[rel], (rel, "is not the file this patch read", got)
    return p, _eol(raw, rel), raw.decode("utf-8").replace("\r\n", "\n")


def _fill():
    cl = LOT / "CHANGELOG.md"
    raw = cl.read_bytes()
    eol = _eol(raw, "CHANGELOG.md")
    text = raw.decode("utf-8").replace("\r\n", "\n")
    value = (SRC / "result_suite.txt").read_bytes().decode("utf-8").replace("\r\n", "\n").strip()
    assert value and not value.endswith("."), "result_suite.txt must be one sentence without its final stop"
    text = _once(text, "RESULT_SUITE", value, "RESULT_SUITE")
    cl.write_bytes(text.replace("\n", eol.decode()).encode("utf-8"))
    print("Lot 0.115.0's changelog filled")


def main():
    if DRAFT and not os.environ.get("LOT_ROOT"):
        sys.exit("refusing: --draft is for a LOT_ROOT copy, never the repo")
    if FILL:
        _fill()
        return
    assert (LOT / "VERSION").read_bytes().strip() == VERSION_WAS, (LOT / "VERSION").read_bytes()
    entry = _src("CHANGELOG_0.115.0.md")
    assert entry.startswith("## 0.115.0 - "), entry[:40]
    if not DRAFT and not PENDING:
        assert "RESULT_" not in entry, "the changelog still carries an unfilled result"
    assert not (LOT / NEW_TEST).exists(), f"{NEW_TEST} already exists"

    lp, l_eol, lot = _read("lot.py")
    assert "MESH_TILE_BAKED" not in lot, "already applied"
    lot = _once(lot, TILE_OLD, TILE_NEW, "MESH_TILE")
    lot = _once(lot, MCL_DEF_OLD, MCL_DEF_NEW, "_mesh_child_lines def")
    lot = _once(lot, MCL_DOC_OLD, MCL_DOC_NEW, "_mesh_child_lines doc")
    lot = _once(lot, MCL_TILES_OLD, MCL_TILES_NEW, "_mesh_child_lines tiles")
    lot = _once(lot, BOX_DEF_OLD, BOX_DEF_NEW, "_box_node def")
    lot = _once(lot, BOX_CALL_OLD, BOX_CALL_NEW, "_box_node call")
    lot = _once(lot, YAW_DEF_OLD, YAW_DEF_NEW, "_yaw_box_node def")
    lot = _once(lot, YAW_CALL_OLD, YAW_CALL_NEW, "_yaw_box_node call")
    quads = QUAD_RE.findall(lot)
    assert len(quads) == 1 and quads[0].count("\ndef ") == 0, ("_yaw_quad_node", len(quads))
    lot = QUAD_RE.sub("", lot, count=1)
    assert "_yaw_quad_node" not in lot, "a caller of _yaw_quad_node is left"
    lot = _once(lot, MAT_DEF_OLD, MAT_DEF_NEW, "_mat_sub def")
    lot = _once(lot, MAT_OFF_OLD, "", "_mat_sub uv_offset")
    assert "uv_offset" not in lot, "uv_offset is still read somewhere"
    lot = _once(lot, OUT_OLD, OUT_NEW, "_outdoor_nodes tile")
    for old, new in CALLS:
        lot = _once(lot, old, new, old.strip()[:40])
    lot = _once(lot, DOC_OLD, DOC_NEW, "_marking_meshes doc")
    lot = _once(lot, LOOP_OLD, LOOP_NEW, "_marking_meshes loop")
    lot = _once(lot, LINES_OLD, LINES_NEW, "_marking_meshes header")
    lot = _once(lot, TAIL_OLD, TAIL_NEW, "_marking_meshes tail")

    mp, m_eol, mtests = _read("tests/test_marking_meshes.py")
    assert mtests.endswith("\n")
    mtests = _once(mtests, T_IMP_OLD, T_IMP_NEW, "marking tests imports")
    mtests = _once(mtests, T_FILES_OLD, T_FILES_NEW, "marking tests files")
    mtests = _once(mtests, T_MAT_OLD, T_MAT_NEW, "marking tests material")
    mtests = _once(mtests, T_COUNT_OLD, T_COUNT_NEW, "marking tests count")
    mtests = mtests.rstrip("\n") + "\n" + T_CELLS

    cl = LOT / "CHANGELOG.md"
    cl_raw = cl.read_bytes()
    cl_eol = _eol(cl_raw, "CHANGELOG.md")
    cl_text = cl_raw.decode("utf-8").replace("\r\n", "\n")
    assert cl_text.startswith(CHANGELOG_HEAD) and cl_text.count(CHANGELOG_HEAD) == 1, cl_text[:120]
    test = _src("test_mesh_tile_render.py")
    # Every pin and anchor matched: now write.
    lp.write_bytes(lot.replace("\n", l_eol.decode()).encode("utf-8"))
    mp.write_bytes(mtests.replace("\n", m_eol.decode()).encode("utf-8"))
    (LOT / NEW_TEST).write_bytes(test.replace("\n", l_eol.decode()).encode("utf-8"))
    cl.write_bytes((entry.rstrip("\n") + "\n\n" + cl_text).replace("\n", cl_eol.decode()).encode("utf-8"))
    (LOT / "VERSION").write_bytes(VERSION)
    print("Lot 0.114.0 -> 0.115.0" + (" (DRAFT)" if DRAFT else ""))


if __name__ == "__main__":
    main()
