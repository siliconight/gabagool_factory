"""Level Factory 0.211.0: a ground under the backdrop (the walker's walk of cold runs 9305-9307, 2026-10-14, finding
2: the factory's `docs/findings/walk_2026-10-14/`).

`backdrop_layer.ship_backdrop` wrote the backdrop's rowhomes and water tower as MultiMeshes and nothing under them, so
past the plate's edge they stood on nothing: at urban_row_001's east fence the walker saw "the bottom of the level
just disappears" (`edge_9305_sheet.png` there: from 26 m up the plate's ground ends in a straight line and the
rowhomes stand over the sky and the fog). `with_ground` lays one dark `PlaneMesh` under the whole backdrop,
`GROUND_MARGIN` past its pieces and `GROUND_Y` under the plate: 9305's `Ground_*` pieces reach x +-99 while its
fences stand at +-94.75, so a ground that began at any edge would lie on the plate's.

Anchored edits, each asserted exactly once and the file's sha16 pinned, nothing written until all matched:
  packages/exporting/backdrop_layer.py  the docstring's THE GROUND UNDER IT; `import re`; `GROUND_*`;
                                        `with_ground`; `ship_backdrop` lays it and reports it under `ground`
  tests/unit/test_backdrop_ground.py    new, from `lf_backdrop_ground/test_backdrop_ground.py.txt`
CHANGELOG and VERSION from `lf_backdrop_ground/CHANGELOG_0.211.0.md`; `--results-pending` leaves RESULT_SUITE to
`--fill`.

Read before it was written, in this session: `backdrop_layer.py` whole; `dressing_scene.py`'s axis note (site
(x, y, z) -> Godot (x, z, -y)) and `scene_text`'s signature; `tests/unit/test_backdrop_layer.py` (it counts
`MultiMeshInstance3D` and the manifest's `draw_calls`, neither of which a `MeshInstance3D` ground moves); 9305's
`site_backdrop.tscn` (its header, resources and nodes) and its drawn spec's `backdrop` (267 pieces, x -181..181,
y -137..141). Every file LF.

    python patches/patch_lf_backdrop_ground.py --results-pending
    (python -m pytest -q in level_factory)
    python patches/patch_lf_backdrop_ground.py --fill
"""
import hashlib
import os
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
LF = pathlib.Path(os.environ.get("LF_ROOT") or HERE.parent / "level_factory")
SRC = HERE / "lf_backdrop_ground"
PENDING = "--results-pending" in sys.argv
FILL = "--fill" in sys.argv
RESULTS = {"RESULT_SUITE": "result_suite.txt"}
VERSION_WAS, VERSION = b"0.210.0", b"0.211.0"
CHANGELOG_HEAD = "## [0.210.0] - The kit modules only merged slots instanced leave the package"
NEW_TEST = ("tests/unit/test_backdrop_ground.py", "test_backdrop_ground.py.txt")
SHA = {"packages/exporting/backdrop_layer.py": "a2be4df923ecaa0a"}

WITH_GROUND = '''

def with_ground(text: str, orders) -> tuple:
    """The backdrop scene with one ground plane under it, and what was laid (`None` with no orders).

    0.211.0, the walker at urban_row_001's east fence: "the bottom of the level just disappears". The plane spans
    the pieces' extent and `GROUND_MARGIN` past it, at `GROUND_Y`, the spec's (x, y) Godot's (x, -z) as
    `dressing_scene` maps it. Two resources and one node; `load_steps` counts the two."""
    if not orders:
        return text, None
    xs = [float(o["pos"][0]) for o in orders]
    ys = [float(o["pos"][1]) for o in orders]
    x0, x1 = min(xs) - GROUND_MARGIN, max(xs) + GROUND_MARGIN
    y0, y1 = min(ys) - GROUND_MARGIN, max(ys) + GROUND_MARGIN
    w, d = round(x1 - x0, 3), round(y1 - y0, 3)
    cx, cy = round((x0 + x1) / 2.0, 3), round((y0 + y1) / 2.0, 3)
    subs = ('[sub_resource type="PlaneMesh" id="BackdropGround_mesh"]\\nsize = Vector2(%s, %s)\\n\\n'
            '[sub_resource type="StandardMaterial3D" id="BackdropGround_mat"]\\n'
            'albedo_color = Color(%s, %s, %s, 1)\\nroughness = 1.0\\n\\n') % (w, d, *GROUND_RGB)
    node = ('\\n[node name="BackdropGround" type="MeshInstance3D" parent="."]\\n'
            'transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, %s, %s, %s)\\n'
            'mesh = SubResource("BackdropGround_mesh")\\n'
            'material_override = SubResource("BackdropGround_mat")\\n'
            'cast_shadow = 0\\n') % (cx, GROUND_Y, -cy)
    first = text.index("\\n[node ")
    text = text[:first + 1] + subs + text[first + 1:]
    text = re.sub(r"load_steps=(\\d+)", lambda m: "load_steps=%d" % (int(m.group(1)) + 2), text, count=1)
    return text.rstrip("\\n") + "\\n" + node, {"size": [w, d], "y": GROUND_Y, "centre": [cx, cy], "draw_calls": 1}
'''

EDITS = {
    "packages/exporting/backdrop_layer.py": [
        ("WHAT IS NOT HERE. No collision",
         "THE GROUND UNDER IT (0.211.0). One dark plane under the whole backdrop, `GROUND_MARGIN` past its pieces and\n"
         "`GROUND_Y` under the plate, which covers it wherever both stand: without it the pieces stood on nothing, and\n"
         "the walker at urban_row_001's east fence saw \"the bottom of the level just disappears\". One draw.\n"
         "\n"
         "WHAT IS NOT HERE. No collision"),
        ("import json\nimport math\nimport shutil\n",
         "import json\nimport math\nimport re\nimport shutil\n"),
        ("SIDES = (\"N\", \"S\", \"E\", \"W\")\n",
         "SIDES = (\"N\", \"S\", \"E\", \"W\")\n"
         "#: The ground under the backdrop (0.211.0): a tenth of a metre under the plate, so the plate covers it\n"
         "#: wherever both stand -- cold run 9305's plate reaches x +-99 past fences at +-94.75 -- and this far past\n"
         "#: the pieces.\n"
         "GROUND_Y = -0.10\n"
         "GROUND_MARGIN = 30.0\n"
         "GROUND_RGB = (0.045, 0.045, 0.05)\n"),
        ("\n\ndef ship_backdrop(export_dir: Path, drawn_path, godot_executable, *,\n",
         WITH_GROUND + "\n\ndef ship_backdrop(export_dir: Path, drawn_path, godot_executable, *,\n"),
        ("    scene_name = f\"{site_id}_backdrop.tscn\"\n"
         "    (export_dir / scene_name).write_text(text, encoding=\"utf-8\", newline=\"\\n\")\n",
         "    scene_name = f\"{site_id}_backdrop.tscn\"\n"
         "    text, ground = with_ground(text, manifest[\"orders\"])\n"
         "    (export_dir / scene_name).write_text(text, encoding=\"utf-8\", newline=\"\\n\")\n"),
        ("        \"towers\": sum(1 for o in manifest[\"orders\"] if o[\"species\"] == \"water_tower\"),\n"
         "    })\n",
         "        \"towers\": sum(1 for o in manifest[\"orders\"] if o[\"species\"] == \"water_tower\"),\n"
         "        \"ground\": ground,\n"
         "    })\n"),
    ],
}


def _eol(raw, rel):
    crlf = raw.count(b"\r\n")
    lf = raw.count(b"\n")
    assert crlf in (0, lf), (rel, "mixed line endings", crlf, lf)
    return b"\r\n" if crlf else b"\n"


def fill():
    assert (LF / "VERSION").read_bytes().strip() == VERSION, (LF / "VERSION").read_bytes()
    results = {}
    for key, name in RESULTS.items():
        value = (SRC / name).read_text(encoding="utf-8").strip()
        assert value and "RESULT_" not in value and not value.endswith("."), (name, value[-40:])
        results[key] = value
    writes = {}
    for path, rel in [(LF / "CHANGELOG.md", "CHANGELOG.md"), (SRC / "CHANGELOG_0.211.0.md", "the entry")]:
        raw = path.read_bytes()
        eol = _eol(raw, rel)
        text = raw.decode("utf-8").replace("\r\n", "\n")
        for key, value in results.items():
            assert text.count(key) == 1, (rel, key, text.count(key))
            text = text.replace(key, value)
        writes[path] = text.encode("utf-8").replace(b"\n", eol)
    for path, data in writes.items():
        path.write_bytes(data)
    print("Level Factory 0.211.0: results filled")


def main():
    if FILL:
        return fill()
    assert (LF / "VERSION").read_bytes().strip() == VERSION_WAS, (LF / "VERSION").read_bytes()
    entry = (SRC / "CHANGELOG_0.211.0.md").read_bytes().decode("utf-8").replace("\r\n", "\n")
    assert entry.startswith("## [0.211.0] - "), entry[:40]
    left = entry
    for key in RESULTS if PENDING else ():
        left = left.replace(key, "")
    assert "RESULT_" not in left, "the changelog still carries an unfilled result"
    test_dst = LF / NEW_TEST[0]
    assert not test_dst.exists(), (test_dst, "already exists")
    test_src = (SRC / NEW_TEST[1]).read_bytes().replace(b"\r\n", b"\n")
    writes = {}
    for rel, pairs in EDITS.items():
        p = LF / rel
        raw = p.read_bytes()
        got = hashlib.sha256(raw.replace(b"\r\n", b"\n")).hexdigest()[:16]
        assert got == SHA[rel], (rel, "is not the file this patch read", got)
        eol = _eol(raw, rel)
        text = raw.decode("utf-8").replace("\r\n", "\n")
        for old, new in pairs:
            assert text.count(old) == 1, (rel, "anchor", text.count(old), old[:80])
            text = text.replace(old, new)
        writes[p] = text.encode("utf-8").replace(b"\n", eol)
    cl = LF / "CHANGELOG.md"
    cl_raw = cl.read_bytes()
    cl_eol = _eol(cl_raw, "CHANGELOG.md")
    cl_text = cl_raw.decode("utf-8").replace("\r\n", "\n")
    assert cl_text.startswith(CHANGELOG_HEAD), cl_text[:120]
    for p, data in writes.items():
        p.write_bytes(data)
    test_dst.write_bytes(test_src)
    cl.write_bytes((entry.rstrip("\n") + "\n\n" + cl_text).encode("utf-8").replace(b"\n", cl_eol))
    (LF / "VERSION").write_bytes(VERSION)
    print("Level Factory 0.210.0 -> 0.211.0")


if __name__ == "__main__":
    main()
