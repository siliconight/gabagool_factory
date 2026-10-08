"""Zoo 1.84.0: the ghost is the getaway van's own (roadmap 206). The walker,
2026-10-08, on 1.83.0's frames: "make the ghost the default, patchy
version". Every step van carries SKEEVY'S WOODER ICE, peeled and patched;
the plain van and the variant that chose between them are gone, and the
paint material, always the art under the `Wear` colour, keeps its plain name.

Anchored edits (every anchor once; refuses on a miss) to
`core/van_forms.py`, `recipes/step_van.py`, `genome/species/step_van.json`
and `tests/test_step_van.py`; CHANGELOG and VERSION from
`zoo_ghost_default_184/CHANGELOG_1.84.0.md`.

    python patch_zoo_ghost_default_184.py                 # source and release
    python patch_zoo_ghost_default_184.py --source-only   # the edits alone
    ZOO_ROOT=<copy> python patch_zoo_ghost_default_184.py
"""
import os
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
ZOO = pathlib.Path(os.environ.get("ZOO_ROOT") or HERE.parent / "zoo")
SRC = HERE / "zoo_ghost_default_184"

EDITS = [
    ("zoo_keeper/core/van_forms.py",
     "# --- the ghost (1.83.0, variant 1) --------------------------------------------------\n",
     "# --- the ghost (1.83.0; every step van's since 1.84.0) ------------------------------\n"),
    ("zoo_keeper/core/van_forms.py",
     "#: THE GHOST, variant 1 -- the walker's to judge (2026-10-08: \"show me\n"
     "#: this\"). The van ran as a water-ice truck, SKEEVY'S WOODER ICE, its name in\n",
     "#: THE GHOST. The walker, 2026-10-08: \"show me this\" (1.83.0, variant 1),\n"
     "#: then \"make the ghost the default, patchy version\" (1.84.0) -- so every\n"
     "#: step van carries it. The van ran as a water-ice truck, SKEEVY'S WOODER\n"
     "#: ICE, its name in\n"),
    ("zoo_keeper/core/van_forms.py",
     "#: one somebody peeled off (2026-10-08).\n"
     "GHOST_PATCH = 0.30\n",
     "#: one somebody peeled off (2026-10-08). The walker chose these over the\n"
     "#: even ones: \"patchy version\".\n"
     "GHOST_PATCH = 0.30\n"),
    ("zoo_keeper/recipes/step_van.py",
     "THE GHOST (1.83.0, variant 1, the walker's to judge): the van's old life as\n",
     "THE GHOST (1.83.0; every step van's since 1.84.0 -- the walker: \"make the\n"
     "ghost the default, patchy version\"): the van's old life as\n"),
    ("zoo_keeper/recipes/step_van.py",
     "    ghost = int(plan[\"params\"].get(\"variant\", 0) or 0) == 1\n",
     ""),
    ("zoo_keeper/recipes/step_van.py",
     "    art = None\n"
     "    if ghost:\n"
     "        art = van_forms.ghost_art()\n"
     "        paint = materials.make_wear_textured_material(\n"
     "            \"M_Van_paint_ghost\", materials.image_from_png(art[\"name\"], art[\"png\"]), plan[\"material\"])\n"
     "    else:\n"
     "        paint = materials.make_material(\"M_Van_paint\", [1.0, 1.0, 1.0], plan[\"material\"])\n",
     "    art = van_forms.ghost_art()\n"
     "    paint = materials.make_wear_textured_material(\n"
     "        \"M_Van_paint\", materials.image_from_png(art[\"name\"], art[\"png\"]), plan[\"material\"])\n"),
    ("zoo_keeper/recipes/step_van.py",
     "            if art is not None:\n"
     "                uv = ((lambda co, n: van_forms.ghost_uv(co, n, lay)) if key == \"paint\"\n"
     "                      else (lambda co, n: van_forms.GHOST_OUTSIDE))\n"
     "                if not geometry.set_uv_by(obj, uv):\n"
     "                    raise RuntimeError(f\"step_van: {obj.name} has no UV layer, so the ghost would not land\")\n",
     "            uv = ((lambda co, n: van_forms.ghost_uv(co, n, lay)) if key == \"paint\"\n"
     "                  else (lambda co, n: van_forms.GHOST_OUTSIDE))\n"
     "            if not geometry.set_uv_by(obj, uv):\n"
     "                raise RuntimeError(f\"step_van: {obj.name} has no UV layer, so the ghost would not land\")\n"),
    ("zoo_keeper/recipes/step_van.py",
     "          f\"ghost={art['name'] if art else 'none'} \"\n",
     "          f\"ghost={art['name']} \"\n"),
    ("zoo_keeper/genome/species/step_van.json",
     "  \"module_variants\": 2,\n",
     ""),
    ("tests/test_step_van.py",
     "the ghost of SKEEVY'S WOODER ICE (variant 1) keeps a white margin, reads the\n"
     "right way round on both sides and stays off the primer patch. Built half\n",
     "the ghost of SKEEVY'S WOODER ICE keeps a white margin, reads the right way\n"
     "round on both sides and stays off the primer patch -- every step van's\n"
     "since 1.84.0 (\"make the ghost the default, patchy version\"). Built half\n"),
    ("tests/test_step_van.py",
     "    assert g[\"module_variants\"] == 2      # 0 the plain van, 1 the ghost\n",
     "    assert g.get(\"module_variants\", 1) == 1    # one van: the ghost is its own (1.84.0)\n"),
    ("tests/test_step_van.py",
     "    genome inert). The ghost swaps the paint for the same kind under one\n"
     "    image; it adds no material.\"\"\"\n",
     "    genome inert). The paint carries the ghost's one image under the same\n"
     "    kind; it adds no material.\"\"\"\n"),
    ("tests/test_step_van.py",
     "    assert sorted(n for _f, n in made) == [\"M_Van_interior\", \"M_Van_paint\",\n"
     "                                          \"M_Van_painted\", \"M_Van_rubber\"], made\n",
     "    assert sorted(n for _f, n in made) == [\"M_Van_interior\", \"M_Van_painted\",\n"
     "                                          \"M_Van_rubber\"], made\n"),
    ("tests/test_step_van.py",
     "    assert re.search(r'make_wear_textured_material\\(\\s*\"M_Van_paint_ghost\"', src)\n",
     "    assert re.search(r'make_wear_textured_material\\(\\s*\"M_Van_paint\"', src)\n"),
    ("tests/test_step_van.py",
     "def _build(tmp_path, dims, variant=None):\n",
     "def _build(tmp_path, dims):\n"),
    ("tests/test_step_van.py",
     "    if variant:\n"
     "        slot[\"variant\"] = variant\n",
     ""),
    ("tests/test_step_van.py",
     "    assert not doc.get(\"images\")\n",
     "    assert \"baseColorTexture\" in pbr      # the ghost's art, every build (1.84.0)\n"),
    ("tests/test_step_van.py",
     "    \"\"\"Variant 1: the same five submissions, the paint one image richer; the\n",
     "    \"\"\"Every build (1.84.0): five submissions, the paint one image richer; the\n"),
    ("tests/test_step_van.py",
     "    res, _objs = _build(tmp_path, (2.6, 6.8, 3.05), variant=1)\n",
     "    res, _objs = _build(tmp_path, (2.6, 6.8, 3.05))\n"),
    ("tests/test_step_van.py",
     "    assert sorted(mats) == [\"M_Van_glass\", \"M_Van_interior\", \"M_Van_paint_ghost\",\n"
     "                            \"M_Van_painted\", \"M_Van_rubber\"], sorted(mats)\n"
     "    assert \"baseColorTexture\" in mats[\"M_Van_paint_ghost\"][\"pbrMetallicRoughness\"]\n",
     "    assert sorted(mats) == [\"M_Van_glass\", \"M_Van_interior\", \"M_Van_paint\",\n"
     "                            \"M_Van_painted\", \"M_Van_rubber\"], sorted(mats)\n"
     "    assert \"baseColorTexture\" in mats[\"M_Van_paint\"][\"pbrMetallicRoughness\"]\n"),
    ("tests/test_step_van.py",
     "    prim = [p for m in visual for p in m[\"primitives\"] if names[p[\"material\"]] == \"M_Van_paint_ghost\"]\n",
     "    prim = [p for m in visual for p in m[\"primitives\"] if names[p[\"material\"]] == \"M_Van_paint\"]\n"),
    ("tests/test_step_van.py",
     "@pytest.mark.parametrize(\"variant\", (None, 1))\n"
     "def test_bpy_the_same_file_every_build(tmp_path, variant):\n",
     "def test_bpy_the_same_file_every_build(tmp_path):\n"),
    ("tests/test_step_van.py",
     "        res, _o = _build(out, (2.6, 6.8, 3.05), variant=variant)\n",
     "        res, _o = _build(out, (2.6, 6.8, 3.05))\n"),
]


def _edit(path, old, new):
    d = path.read_bytes()
    crlf = b"\r\n" in d
    s = d.decode("utf-8").replace("\r\n", "\n")
    assert s.count(old) == 1, (path.name, s.count(old), old[:70])
    s = s.replace(old, new)
    path.write_bytes((s.replace("\n", "\r\n") if crlf else s).encode("utf-8"))


def main():
    source_only = "--source-only" in sys.argv[1:]
    v = (ZOO / "VERSION").read_text(encoding="utf-8").strip()
    assert v == "1.83.0", v
    for rel, old, new in EDITS:
        _edit(ZOO / rel, old, new)
    if source_only:
        print("1.84.0's edits applied; VERSION and CHANGELOG left at 1.83.0")
        return
    entry = (SRC / "CHANGELOG_1.84.0.md").read_text(encoding="utf-8").replace("\r\n", "\n")
    cl = ZOO / "CHANGELOG.md"
    d = cl.read_bytes()
    assert b"## [1.84.0]" not in d and d.startswith(b"## [1.83.0]")
    crlf = b"\r\n" in d
    cl.write_bytes((entry.replace("\n", "\r\n") if crlf else entry).encode("utf-8") + d)
    (ZOO / "VERSION").write_bytes(b"1.84.0")
    print("1.83.0 -> 1.84.0")


if __name__ == "__main__":
    main()
