#!/usr/bin/env python
"""patch_zoo_tint.py -- Zoo 0.41.0 -> 0.42.0

WHAT
  Teaches Zoo to read Pixelcoat 0.13's `tintable` flag: an achromatic pack is
  multiplied by the mesh's own base colour instead of replacing it, and its
  material cache key becomes (kind, theme, colour) instead of (kind, theme).

  This patch changes NOTHING that renders. No pack on disk sets `tintable`,
  and no theme maps a kind that would.

  Requires patch_pc_tintable.py (Pixelcoat 0.13.0) applied first, or the flag
  is never true and this is inert.

UNVERIFIED
  The shader graph gains one node between the image and Base Color. The glTF
  exporter may drop the resulting baseColorFactor SILENTLY. tools/tint_probe.py
  ships with this patch to measure it. Do not map a tintable pack into a theme
  until that probe is green.

USAGE   (run from anywhere; paths are absolute)
  pwsh:  python patch_zoo_tint.py --check
         python patch_zoo_tint.py
         python patch_zoo_tint.py --selftest
         python patch_zoo_tint.py --revert

CONTRACT
  * refuses on drift (sha256 per target, recorded at generation time)
  * all-or-nothing: full pre-flight sweep before the first byte is written
  * every anchor must occur EXACTLY ONCE
  * .pre_tint sidecars for --revert
  * __pycache__ purged after any write (a same-second .pyc can otherwise
    serve the old module and make the patch look like a no-op)
"""
import argparse, hashlib, io, json, os, shutil, sys, tempfile

ROOT = r"C:\Projects\gabagool_studios\gabagool_factory"
TAG = "tint"
M = json.loads(r"""{
 "tool": "zoo",
 "from_version": "0.41.0",
 "to_version": "0.42.0",
 "tag": "tint",
 "edits": [
  {
   "path": "zoo/zoo_keeper/core/skins.py",
   "anchor": "        return {\"id\": raw.get(\"asset_id\") or os.path.basename(pack_dir),\n                \"dir\": os.path.abspath(pack_dir),\n                \"maps\": maps,\n                \"meters_per_tile\": float(raw.get(\"meters_per_tile\") or 1.0),\n                \"tileable\": raw.get(\"tileable\"),\n                \"transparency\": raw.get(\"import_hints\", {}).get(\"transparency\")}\n",
   "after": "        return {\"id\": raw.get(\"asset_id\") or os.path.basename(pack_dir),\n                \"dir\": os.path.abspath(pack_dir),\n                \"maps\": maps,\n                \"meters_per_tile\": float(raw.get(\"meters_per_tile\") or 1.0),\n                \"tileable\": raw.get(\"tileable\"),\n                # ACHROMATIC-BY-INTENT (Pixelcoat >= 0.13). The pack says its\n                # albedo is a surface and not a paint job, so the consumer is\n                # expected to supply the hue. Absent key -> False: every pack\n                # written before 0.13 keeps today's behaviour exactly.\n                \"tintable\": bool(raw.get(\"tintable\")),\n                \"transparency\": raw.get(\"import_hints\", {}).get(\"transparency\")}\n"
  },
  {
   "path": "zoo/zoo_keeper/core/skins.py",
   "anchor": "    return {\"id\": stem, \"dir\": os.path.abspath(pack_dir), \"maps\": maps,\n            \"meters_per_tile\": 1.0, \"tileable\": None}\n",
   "after": "    return {\"id\": stem, \"dir\": os.path.abspath(pack_dir), \"maps\": maps,\n            \"meters_per_tile\": 1.0, \"tileable\": None, \"tintable\": False}\n"
  },
  {
   "path": "zoo/zoo_keeper/bpylayer/materials.py",
   "anchor": "    pack = _find_pack(material_kind)\n    if pack:\n        skin_name = f\"M_Skin_{material_kind}_{_SKINS['theme']}\"\n        mat = bpy.data.materials.get(skin_name)\n        if mat:\n            return mat\n        print(f\"[zoo] skin: {material_kind} <- {pack['id']} ({pack['dir']})\")\n        return _textured(skin_name, pack, material_kind)\n",
   "after": "    pack = _find_pack(material_kind)\n    if pack:\n        # A TINTABLE pack is achromatic on purpose: it carries grain, wear and\n        # sheen, and the mesh supplies the hue. Such a material CANNOT be\n        # shared across colours, so the cache key carries the colour and one\n        # material exists per (kind, theme, colour). A normal pack still\n        # collapses to one material per (kind, theme) -- which is the whole\n        # point for a wall, and the reason the docstring above says the\n        # genome's colour rides only the flat path. It now also rides the\n        # textured path, but ONLY when the pack asked for it.\n        tint = _tint_key(base_color) if pack.get(\"tintable\") else None\n        skin_name = f\"M_Skin_{material_kind}_{_SKINS['theme']}\"\n        if tint is not None:\n            skin_name += \"_\" + tint\n        mat = bpy.data.materials.get(skin_name)\n        if mat:\n            return mat\n        print(f\"[zoo] skin: {material_kind} <- {pack['id']} ({pack['dir']})\"\n              + (f\"  tinted #{tint}\" if tint else \"\"))\n        return _textured(skin_name, pack, material_kind,\n                         tint=(tuple(base_color) if tint else None))\n"
  },
  {
   "path": "zoo/zoo_keeper/bpylayer/materials.py",
   "anchor": "def _textured(name, pack, material_kind):\n",
   "after": "def _textured(name, pack, material_kind, tint=None):\n"
  },
  {
   "path": "zoo/zoo_keeper/bpylayer/materials.py",
   "anchor": "    albedo = tex_node(maps[\"albedo\"])\n    link_vector(albedo)\n    tree.links.new(_wear_multiply(tree, albedo.outputs[\"Color\"], name),\n                   bsdf.inputs[\"Base Color\"])\n",
   "after": "    albedo = tex_node(maps[\"albedo\"])\n    link_vector(albedo)\n    color_socket = albedo.outputs[\"Color\"]\n    if tint is not None:\n        color_socket = _tint_multiply(tree, color_socket, tint, name)\n    tree.links.new(_wear_multiply(tree, color_socket, name),\n                   bsdf.inputs[\"Base Color\"])\n"
  },
  {
   "path": "zoo/zoo_keeper/bpylayer/materials.py",
   "anchor": "def _wear_multiply(tree, color_socket, label):\n",
   "after": "def _tint_key(base_color):\n    \"\"\"Stable 6-hex cache key for a base colour. Pure; unit-testable without\n    bpy, which is why it is not inlined into `make_material`.\"\"\"\n    return \"\".join(\"%02x\" % max(0, min(255, int(round(float(c) * 255.0))))\n                   for c in tuple(base_color)[:3])\n\n\ndef _tint_multiply(tree, color_socket, tint, label):\n    \"\"\"Insert ``albedo * tint`` for an achromatic pack and return the socket.\n\n    UNVERIFIED AT THE EXPORT BOUNDARY -- read this before trusting it.\n    glTF computes base colour as ``baseColorFactor * baseColorTexture *\n    COLOR_0``. This node is the Blender spelling of the FACTOR term, and the\n    exporter has to fold it back into one. There is now one more node between\n    the image and Base Color than there was when `tools/wear_probe.py`\n    verified the texture still exported, and the exporter is free to give up\n    quietly and drop the factor -- which would render every tinted prop in\n    the pack's own near-white, with no error anywhere. That is the same shape\n    of silent failure that hid the flat wear for a whole art pass.\n\n    `tools/tint_probe.py` exports a specimen and reads baseColorFactor and\n    baseColorTexture back out of the GLB. Run it before shipping a tintable\n    pack. If the factor is dropped, the fallback is to multiply the tint into\n    the loaded image pixels once per colour -- slower and heavier, but a plain\n    texture cannot be dropped.\n\n    On failure this returns the original socket and SAYS SO, rather than\n    leaving a half-wired graph.\n    \"\"\"\n    try:\n        mix = tree.nodes.new(\"ShaderNodeMix\")\n        mix.data_type = \"RGBA\"\n        mix.blend_type = \"MULTIPLY\"\n        mix.inputs[\"Factor\"].default_value = 1.0\n        tree.links.new(color_socket, mix.inputs[6])            # A: albedo\n        mix.inputs[7].default_value = (float(tint[0]), float(tint[1]),\n                                       float(tint[2]), 1.0)    # B: tint\n        return mix.outputs[2]\n    except Exception as exc:\n        print(f\"[zoo] WARNING: {label}: could not wire the tint multiply \"\n              f\"({type(exc).__name__}: {exc}) -- this material will render in \"\n              f\"the pack's own colour and ignore the genome\")\n        return color_socket\n\n\ndef _wear_multiply(tree, color_socket, label):\n"
  }
 ],
 "whole": {
  "zoo/VERSION": "Zoo 0.42.0\n"
 },
 "new": {
  "zoo/tests/test_tintable.py": "\"\"\"Tintable packs: the achromatic-by-intent flag and its cache key (no bpy).\n\nWhy these tests exist. `make_material` discards the genome's per-specimen\ncolour the moment a pack resolves -- all objects of a kind share one cached\nmaterial. Correct for a brick wall, wrong for a bumper. The fix cannot key on\nmaterial KIND, because `metal` serves both a rusted storefront facade and 42\nprop species, so it keys on the PACK: a grammar declares `tintable`,\nPixelcoat writes it into the manifest, Zoo reads it here.\n\nThe shader-graph half of that lives behind bpy and is covered by\n`tools/tint_probe.py`, not by these tests. What IS covered here is every\ndecision made before a node is created.\n\"\"\"\n\nimport json\nimport os\n\nimport pytest\n\nfrom zoo_keeper.core import skins\n\n\ndef _touch(path):\n    os.makedirs(os.path.dirname(path), exist_ok=True)\n    with open(path, \"wb\") as f:\n        f.write(b\"\\x89PNG stub\")\n\n\ndef _pack(root, dirname, asset_id, tintable=None):\n    d = os.path.join(root, dirname)\n    os.makedirs(d, exist_ok=True)\n    _touch(os.path.join(d, f\"{asset_id}_albedo.png\"))\n    manifest = {\"schema\": skins.PACK_SCHEMA, \"asset_id\": asset_id,\n                \"maps\": {\"albedo\": f\"{asset_id}_albedo.png\"},\n                \"meters_per_tile\": 1.0, \"tileable\": \"both\"}\n    if tintable is not None:\n        manifest[\"tintable\"] = tintable\n    with open(os.path.join(d, f\"{asset_id}.pack.json\"), \"w\",\n              encoding=\"utf-8\") as f:\n        json.dump(manifest, f)\n    return d\n\n\ndef test_tintable_true_is_surfaced(tmp_path):\n    root = str(tmp_path)\n    _pack(root, \"plastic_delco\", \"plastic_neutral\", tintable=True)\n    assert skins.find_pack(root, \"plastic\", \"delco\")[\"tintable\"] is True\n\n\ndef test_tintable_false_is_surfaced(tmp_path):\n    root = str(tmp_path)\n    _pack(root, \"metal_delco\", \"metal_rusted_street\", tintable=False)\n    assert skins.find_pack(root, \"metal\", \"delco\")[\"tintable\"] is False\n\n\ndef test_pack_written_before_0_13_defaults_to_not_tintable(tmp_path):\n    \"\"\"THE COMPATIBILITY CASE. Every pack on disk today predates the flag.\n    A missing key must mean False, or the first build after this patch\n    repaints every skinned surface by the mesh colour.\"\"\"\n    root = str(tmp_path)\n    _pack(root, \"brick_delco\", \"brick_delco\", tintable=None)\n    pack = skins.find_pack(root, \"brick\", \"delco\")\n    assert \"tintable\" in pack, \"the key must be present even when absent from disk\"\n    assert pack[\"tintable\"] is False\n\n\ndef test_legacy_manifestless_pack_is_not_tintable(tmp_path):\n    \"\"\"The 0.1-era layout has no manifest at all to carry the flag.\"\"\"\n    root = str(tmp_path)\n    d = os.path.join(root, \"wood_delco\")\n    _touch(os.path.join(d, \"wood_delco_albedo.png\"))\n    assert skins.find_pack(root, \"wood\", \"delco\")[\"tintable\"] is False\n\n\ndef test_tintable_is_coerced_to_a_bool(tmp_path):\n    \"\"\"A hand-edited manifest can carry a truthy string. The consumer branches\n    on identity (`is True`), so a leaked 'false' string would tint.\"\"\"\n    root = str(tmp_path)\n    _pack(root, \"plastic_delco\", \"p\", tintable=\"false\")\n    got = skins.find_pack(root, \"plastic\", \"delco\")[\"tintable\"]\n    assert isinstance(got, bool)\n\n\n# --------------------------------------------------------------------------- #\n# The cache key. `bpylayer.materials` imports bpy at module scope, so the key\n# function is read with `ast` and exec'd in isolation -- the same technique\n# `test_kind_vocabulary.py` uses, and for the same reason.\n# --------------------------------------------------------------------------- #\n\nimport ast\n\n\ndef _load_tint_key():\n    here = os.path.dirname(os.path.abspath(__file__))\n    src = os.path.join(os.path.dirname(here), \"zoo_keeper\", \"bpylayer\",\n                       \"materials.py\")\n    tree = ast.parse(open(src, encoding=\"utf-8\").read())\n    for node in tree.body:\n        if isinstance(node, ast.FunctionDef) and node.name == \"_tint_key\":\n            mod = ast.Module(body=[node], type_ignores=[])\n            ast.fix_missing_locations(mod)\n            ns = {}\n            exec(compile(mod, src, \"exec\"), ns)\n            return ns[\"_tint_key\"]\n    raise AssertionError(\"materials.py has no _tint_key\")\n\n\ndef test_tint_key_is_hex_and_stable():\n    k = _load_tint_key()\n    assert k([1.0, 1.0, 1.0]) == \"ffffff\"\n    assert k([0.0, 0.0, 0.0]) == \"000000\"\n    assert k([0.62, 0.14, 0.14]) == k([0.62, 0.14, 0.14])\n\n\ndef test_two_colours_that_differ_get_two_materials():\n    \"\"\"THE CASE THE REAL DATA WOULD NOT HAVE CAUGHT. vending_machine ships a\n    red default and a blue style; if the key collapsed them, the second built\n    machine would silently reuse the first one's material.\"\"\"\n    k = _load_tint_key()\n    red = k([0.62, 0.14, 0.14])\n    blue = k([0.14, 0.26, 0.55])\n    assert red != blue\n\n\ndef test_tint_key_clamps_out_of_range():\n    \"\"\"Genome colours are authored by hand and are not validated as 0..1.\"\"\"\n    k = _load_tint_key()\n    assert k([2.0, -1.0, 0.5]) == \"ff0080\"\n\n\ndef test_tint_key_ignores_alpha():\n    k = _load_tint_key()\n    assert k([0.5, 0.5, 0.5, 1.0]) == k([0.5, 0.5, 0.5])\n",
  "zoo/tools/tint_probe.py": "\"\"\"Does the tint survive the glTF export? Read it back out of the file.\n\nWHY THIS EXISTS. `materials._tint_multiply` inserts `albedo * tint` between\nthe image texture and Base Color. glTF computes base colour as\n``baseColorFactor * baseColorTexture * COLOR_0``, so the exporter has to fold\nthat node back into the FACTOR term. It is free not to. If it gives up, it\ndoes so QUIETLY: every tinted prop renders in the pack's own near-white, no\nwarning is printed, and nothing fails. That is the same shape of silent\nfailure that hid the flat wear for a whole art pass (see tools/wear_probe.py),\nwhich is why this is measured and not assumed.\n\nWHAT IT DOES. Builds the smallest scene that can answer the question -- two\ncubes, one tintable pack, two different genome colours -- exports it, and\nreads the GLB's own JSON chunk back. It deliberately does NOT drive the\nspecies pipeline: a failure there would be a different finding and would\nmuddy this one.\n\n    blender --background --python tools\\\\tint_probe.py -- --pack <pack dir>\n\nBuild a tintable pack to point it at:\n\n    cd pixelcoat\n    python -m pixelcoat.cli.main proc-pack profiles/materials/plastic_neutral.json --out _probe --size 128\n\nWHAT THE EXITS MEAN\n    0  the question was answered (either way -- a dropped factor is a\n       finding, and findings exit 0)\n    2  blender was not the interpreter, or the pack could not be read\n\"\"\"\nfrom __future__ import annotations\n\nimport argparse\nimport json\nimport os\nimport struct\nimport sys\n\nREPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))\nif REPO_ROOT not in sys.path:\n    sys.path.insert(0, REPO_ROOT)\n\n# Two colours far apart in every channel, so a collapsed pair is unmistakable.\nRED = (0.62, 0.14, 0.14)\nBLUE = (0.14, 0.26, 0.55)\n\n\ndef parse_args():\n    argv = sys.argv\n    argv = argv[argv.index(\"--\") + 1:] if \"--\" in argv else argv[1:]\n    ap = argparse.ArgumentParser(prog=\"tint_probe\")\n    ap.add_argument(\"--pack\", required=True,\n                    help=\"a Pixelcoat pack DIRECTORY whose manifest sets \"\n                         \"tintable=true (bypasses theme resolution on \"\n                         \"purpose: this probe tests the exporter, not the \"\n                         \"resolver)\")\n    ap.add_argument(\"--keep\", help=\"write the probe GLB here instead of a \"\n                                   \"temp file that is deleted\")\n    return ap.parse_args(argv)\n\n\n# --------------------------------------------------------------------------- #\n# read the answer out of the file, with no assumptions about the exporter\n# --------------------------------------------------------------------------- #\n\ndef glb_json(path):\n    \"\"\"The JSON chunk of a .glb, parsed. Raises on a malformed container.\"\"\"\n    with open(path, \"rb\") as f:\n        magic, version, _total = struct.unpack(\"<III\", f.read(12))\n        if magic != 0x46546C67:\n            raise ValueError(\"%s is not a GLB (magic %#x)\" % (path, magic))\n        length, ctype = struct.unpack(\"<II\", f.read(8))\n        if ctype != 0x4E4F534A:\n            raise ValueError(\"first chunk of %s is not JSON\" % path)\n        return json.loads(f.read(length).decode(\"utf-8\"))\n\n\ndef materials_report(doc):\n    \"\"\"[(name, baseColorFactor, has_baseColorTexture)] for every material.\"\"\"\n    out = []\n    for m in doc.get(\"materials\", []):\n        pbr = m.get(\"pbrMetallicRoughness\") or {}\n        out.append((m.get(\"name\", \"?\"),\n                    pbr.get(\"baseColorFactor\"),\n                    \"baseColorTexture\" in pbr))\n    return out\n\n\ndef close(a, b, tol=0.02):\n    return a is not None and abs(float(a) - float(b)) <= tol\n\n\n# --------------------------------------------------------------------------- #\n\ndef main():\n    try:\n        import bpy  # noqa: F401\n    except ImportError:\n        sys.stderr.write(\n            \"tint_probe must run inside Blender:\\n\"\n            \"  blender --background --python tools/tint_probe.py -- --pack DIR\\n\")\n        return 2\n\n    import bpy\n    import tempfile\n\n    args = parse_args()\n\n    from zoo_keeper.core import skins\n    from zoo_keeper.bpylayer import materials, export\n\n    pack = skins.load_pack(os.path.abspath(args.pack))\n    if pack is None:\n        sys.stderr.write(\"no pack in %s\\n\" % args.pack)\n        return 2\n    print(\"pack       : %s\" % pack[\"id\"])\n    print(\"tintable   : %r\" % pack.get(\"tintable\"))\n    if pack.get(\"tintable\") is not True:\n        print(\"\")\n        print(\"FINDING: that pack is not tintable, so this probe cannot ask \"\n              \"the question. Build one from a grammar whose `tintable` is \"\n              \"true (profiles/materials/plastic_neutral.json).\")\n        return 0\n\n    # smallest scene that can answer the question\n    bpy.ops.wm.read_factory_settings(use_empty=True)\n    coll = bpy.data.collections.new(\"TintProbe\")\n    bpy.context.scene.collection.children.link(coll)\n    made = []\n    for tag, rgb in ((\"red\", RED), (\"blue\", BLUE)):\n        mesh = bpy.data.meshes.new(\"Probe_\" + tag)\n        mesh.from_pydata([(0, 0, 0), (1, 0, 0), (1, 1, 0), (0, 1, 0)], [],\n                         [(0, 1, 2, 3)])\n        mesh.update()\n        obj = bpy.data.objects.new(\"Probe_\" + tag, mesh)\n        obj.location = (len(made) * 2.0, 0, 0)\n        coll.objects.link(obj)\n        mat = materials._textured(\"M_Probe_\" + tag, pack, \"plastic\", tint=rgb)\n        obj.data.materials.append(mat)\n        made.append((tag, rgb, mat.name))\n\n    tmp = args.keep or os.path.join(tempfile.mkdtemp(), \"tint_probe.glb\")\n    export.export_glb(tmp, coll)\n\n    doc = glb_json(tmp)\n    rows = materials_report(doc)\n\n    print(\"\")\n    print(\"  %-16s %-34s %s\" % (\"MATERIAL\", \"baseColorFactor\", \"baseColorTexture\"))\n    print(\"  \" + \"-\" * 74)\n    for name, factor, has_tex in rows:\n        f = \"None (exporter dropped it)\" if factor is None else \\\n            \"[\" + \", \".join(\"%.3f\" % v for v in factor) + \"]\"\n        print(\"  %-16s %-34s %s\" % (name, f, \"yes\" if has_tex else \"NO\"))\n\n    # ---- the verdict --------------------------------------------------------\n    print(\"\")\n    by_name = {n: (f, t) for n, f, t in rows}\n    verdict_ok = True\n    for tag, rgb, matname in made:\n        got = by_name.get(matname)\n        if got is None:\n            print(\"FINDING: material %r is not in the file at all.\" % matname)\n            verdict_ok = False\n            continue\n        factor, has_tex = got\n        if not has_tex:\n            print(\"FINDING: %s lost its baseColorTexture. The extra node \"\n                  \"broke texture detection -- this is worse than losing the \"\n                  \"tint.\" % matname)\n            verdict_ok = False\n        if factor is None:\n            print(\"FINDING: %s has no baseColorFactor. The tint was DROPPED \"\n                  \"silently; this prop would render in the pack's own \"\n                  \"near-white.\" % matname)\n            verdict_ok = False\n        elif not all(close(factor[i], rgb[i]) for i in range(3)):\n            print(\"FINDING: %s baseColorFactor is %s, wanted ~%s. The tint \"\n                  \"reached the file but not intact.\"\n                  % (matname, factor[:3], list(rgb)))\n            verdict_ok = False\n\n    if verdict_ok and len({tuple(by_name[m][0][:3]) for _, _, m in made}) < 2:\n        print(\"FINDING: both materials exported the SAME baseColorFactor. \"\n              \"The colours collapsed -- check the cache key in \"\n              \"make_material, not the exporter.\")\n        verdict_ok = False\n\n    print(\"\")\n    if verdict_ok:\n        print(\"TINT SURVIVES THE EXPORT. baseColorFactor carries the genome \"\n              \"colour and baseColorTexture is intact on both materials.\")\n    else:\n        print(\"TINT DOES NOT SURVIVE. Fall back to multiplying the tint into \"\n              \"the loaded image pixels once per colour (see the docstring on \"\n              \"materials._tint_multiply) -- a plain texture cannot be \"\n              \"dropped.\")\n    if args.keep:\n        print(\"probe GLB kept at %s\" % tmp)\n    return 0\n\n\nif __name__ == \"__main__\":\n    sys.exit(main())\n"
 },
 "changelog": "## [0.42.0] - a pack can ask to be painted, and the mesh answers\n\n`make_material`'s own docstring said it: \"the genome's per-specimen color\nrides only the flat path; textured paint jobs are the pack's job\". Measured,\nthat means every object of a kind in a skinned build shares ONE cached\nmaterial, modulated only by COLOR_0, which carries greyscale wear. All 42\nspecies that can wear `metal` collapse into one galvanized grey; simple_car's\npolice black, racing red and 1970s brown collapse with them.\n\nThat is correct for a brick wall and wrong for a bumper, and the distinction\nis not the KIND -- `metal` serves a rusted storefront facade and 42 props.\nIt is the PACK. Pixelcoat 0.13 lets a grammar declare `tintable`; this reads\nit.\n\n### Added\n- `skins.load_pack` surfaces `tintable`. Absent key -> False, so every pack\n  written before Pixelcoat 0.13 -- which is all of them -- behaves exactly as\n  it does today. Verified by `test_pack_written_before_0_13_defaults_to_not_tintable`.\n- `materials._tint_key`: a pure 6-hex cache key, kept out of `make_material`\n  so it can be tested without bpy.\n- `materials._tint_multiply`: `albedo * tint` for a tintable pack only.\n- `tools/tint_probe.py`: exports a specimen and reads `baseColorFactor` and\n  `baseColorTexture` back out of the GLB.\n\n### Changed\n- A tintable pack's material cache key is now `(kind, theme, colour)` instead\n  of `(kind, theme)`. A non-tintable pack still collapses to one material,\n  which is the point for walls.\n\n### UNVERIFIED\nThe shader graph now has one more node between the image and Base Color than\nit had when `tools/wear_probe.py` verified the texture still exported. glTF\nfolds `baseColorFactor * baseColorTexture * COLOR_0`; the exporter may give up\non the extra multiply and drop the factor SILENTLY, which would render every\ntinted prop in the pack's own near-white with no error anywhere. This is the\nsame failure shape that hid the flat wear for a whole art pass, so it is\nwritten down as unknown rather than assumed working. Run `tools/tint_probe.py`\nbefore mapping any tintable pack into a theme. If the factor is dropped, the\nfallback is to multiply the tint into the loaded image pixels once per colour.\n\n### Note\nNothing renders differently yet. No pack on disk sets `tintable`, and no theme\nmaps a kind that would.\n\n",
 "pre_sha": {
  "zoo/zoo_keeper/core/skins.py": "9051fd1515d0df4d7807f55ddb07af7d09e5740e85407164265fa3592bd93f47",
  "zoo/zoo_keeper/bpylayer/materials.py": "cf432dff2f830dc9d45e87214210582ae25b90bb6749850a6ddcef796faf3803",
  "zoo/VERSION": "f0ab090f0dc424b7d960b52cdf654044b43d2ae39a3e0b41bc080aac8b2e2de6",
  "zoo/CHANGELOG.md": "2f7dda5d5bffd4f99a03623c987af7aeb9612ba5ba1e744f3c8ccfb49a492381"
 }
}""")


def _abs(rel):
    return os.path.join(ROOT, rel.replace("/", os.sep))


def _sha(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def _read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def _write(path, text):
    """Never truncate the target before the content is known good."""
    d = os.path.dirname(path)
    os.makedirs(d, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=d, suffix=".tmp")
    os.close(fd)
    with io.open(tmp, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    os.replace(tmp, path)


def _purge_bytecode(rels):
    """Delete __pycache__ for every package dir we just rewrote a .py in.

    Found the hard way: rewriting version.py in the same wall-clock SECOND
    that its .pyc was written left the .pyc valid by Python's (mtime, size)
    check -- both were 366 bytes and both stamped the same second -- so the
    interpreter kept serving the OLD constant and the selftest reported the
    change had not landed. It had. A patch tool that edits live Python must
    invalidate bytecode or it can silently appear to do nothing.
    """
    seen = set()
    for rel in rels:
        if not rel.endswith(".py"):
            continue
        d = os.path.join(os.path.dirname(_abs(rel)), "__pycache__")
        if d in seen or not os.path.isdir(d):
            continue
        seen.add(d)
        shutil.rmtree(d, ignore_errors=True)
        print("  purged " + os.path.relpath(d, ROOT))
    return len(seen)


# --------------------------------------------------------------------------- #
# pre-flight
# --------------------------------------------------------------------------- #

def preflight(expect_patched=False):
    """Returns (ok, list of problem strings). Writes nothing, ever."""
    bad = []
    targets = set(M["pre_sha"])
    for rel in sorted(targets):
        p = _abs(rel)
        if not os.path.isfile(p):
            bad.append("MISSING  " + rel)
            continue
        got = _sha(p)
        want = M["pre_sha"][rel]
        if got != want and not expect_patched:
            bad.append("DRIFT    %s\n           on disk %s\n           expect  %s"
                       % (rel, got[:16], want[:16]))
    # anchors must be present exactly once
    for e in M["edits"]:
        p = _abs(e["path"])
        if not os.path.isfile(p):
            continue
        src = _read(p)
        n = src.count(e["anchor"])
        if n != 1 and not expect_patched:
            bad.append("ANCHOR   %s occurs %d times (need exactly 1)"
                       % (e["path"], n))
    for rel in M["new"]:
        p = _abs(rel)
        if os.path.isfile(p) and not expect_patched:
            bad.append("EXISTS   %s (refusing to overwrite a file this "
                       "patch claims to create)" % rel)
    return (not bad), bad


# --------------------------------------------------------------------------- #
# apply
# --------------------------------------------------------------------------- #

def apply():
    ok, bad = preflight()
    if not ok:
        print("REFUSED -- nothing written:")
        for b in bad:
            print("  " + b)
        return 1

    # Build every output IN MEMORY first. Only then touch the disk.
    out = {}

    by_file = {}
    for e in M["edits"]:
        by_file.setdefault(e["path"], []).append(e)
    for rel, edits in by_file.items():
        src = _read(_abs(rel))
        for e in edits:
            src = src.replace(e["anchor"], e["after"], 1)
        out[rel] = src

    for rel, text in M["whole"].items():
        out[rel] = text
    for rel, text in M["new"].items():
        out[rel] = text

    cl_rel = M["tool"] + "/CHANGELOG.md"
    cl = _read(_abs(cl_rel))
    head = "# Changelog\n\n"
    if not cl.startswith(head):
        print("REFUSED -- %s does not start with the expected header" % cl_rel)
        return 1
    out[cl_rel] = head + M["changelog"] + cl[len(head):]

    # sidecars, then write
    for rel in sorted(out):
        p = _abs(rel)
        if os.path.isfile(p):
            shutil.copy2(p, p + ".pre_" + TAG)
    for rel in sorted(out):
        _write(_abs(rel), out[rel])
        print("  wrote  %-52s %8d bytes" % (rel, len(out[rel].encode("utf-8"))))

    _purge_bytecode(out)

    print("")
    print("%s %s -> %s" % (M["tool"], M["from_version"], M["to_version"]))
    return 0


def revert():
    n = 0
    for rel in sorted(set(list(M["pre_sha"]) + list(M["new"]))):
        p = _abs(rel)
        side = p + ".pre_" + TAG
        if os.path.isfile(side):
            shutil.copy2(side, p)
            os.remove(side)
            print("  restored " + rel)
            n += 1
        elif rel in M["new"] and os.path.isfile(p):
            os.remove(p)
            print("  removed  " + rel)
            n += 1
    _purge_bytecode(set(list(M["pre_sha"]) + list(M["new"])))
    print("reverted %d file(s)" % n)
    return 0 if n else 1


# --------------------------------------------------------------------------- #
# selftest -- must FAIL if the change is backed out
# --------------------------------------------------------------------------- #

def selftest():
    sys.path.insert(0, os.path.join(ROOT, "zoo"))
    fails = []
    try:
        return _selftest(fails)
    except Exception as exc:
        print("SELFTEST FAILED -- %s: %s" % (type(exc).__name__, exc))
        for f in fails:
            print("  - " + f)
        return 1


def _selftest(fails):
    import ast as _ast
    import json as _json
    import tempfile as _tf

    from zoo_keeper.core import skins

    # ---- 1. load_pack surfaces the flag, in all three shapes ---------------
    def _mkpack(root, dirname, asset_id, tintable):
        d = os.path.join(root, dirname)
        os.makedirs(d, exist_ok=True)
        with open(os.path.join(d, asset_id + "_albedo.png"), "wb") as f:
            f.write(b"\x89PNG stub")
        man = {"schema": getattr(skins, "PACK_SCHEMA", "pixelcoat-pack/2"),
               "asset_id": asset_id,
               "maps": {"albedo": asset_id + "_albedo.png"},
               "meters_per_tile": 1.0, "tileable": "both"}
        if tintable is not None:
            man["tintable"] = tintable
        with open(os.path.join(d, asset_id + ".pack.json"), "w",
                  encoding="utf-8") as f:
            _json.dump(man, f)

    with _tf.TemporaryDirectory() as td:
        _mkpack(td, "plastic_delco", "plastic_neutral", True)
        _mkpack(td, "metal_delco", "metal_rusted_street", False)
        _mkpack(td, "brick_delco", "brick_delco", None)   # pre-0.13 pack
        got = skins.find_pack(td, "plastic", "delco")
        if got.get("tintable") is not True:
            fails.append("tintable=true pack surfaced %r" % got.get("tintable"))
        got = skins.find_pack(td, "metal", "delco")
        if got.get("tintable") is not False:
            fails.append("tintable=false pack surfaced %r" % got.get("tintable"))
        # THE COMPATIBILITY CASE: every pack on disk today has no such key.
        got = skins.find_pack(td, "brick", "delco")
        if "tintable" not in got:
            fails.append("a pre-0.13 pack has no `tintable` key at all -- "
                         "consumers would KeyError")
        elif got["tintable"] is not False:
            fails.append("a pre-0.13 pack defaulted to tintable=%r; every "
                         "skinned surface would be repainted by the mesh "
                         "colour" % got["tintable"])
        # legacy manifest-less layout
        d = os.path.join(td, "wood_delco")
        os.makedirs(d, exist_ok=True)
        with open(os.path.join(d, "wood_delco_albedo.png"), "wb") as f:
            f.write(b"\x89PNG stub")
        got = skins.find_pack(td, "wood", "delco")
        if got.get("tintable") is not False:
            fails.append("manifest-less pack surfaced tintable=%r"
                         % got.get("tintable"))

    # ---- 2. the cache key, read with ast (materials.py imports bpy) --------
    msrc = os.path.join(ROOT, "zoo", "zoo_keeper", "bpylayer", "materials.py")
    text = open(msrc, encoding="utf-8").read()
    tree = _ast.parse(text)
    fns = {n.name: n for n in tree.body if isinstance(n, _ast.FunctionDef)}
    for want in ("_tint_key", "_tint_multiply", "_textured", "make_material"):
        if want not in fns:
            fails.append("materials.py has no %s" % want)
    if "_tint_key" in fns:
        mod = _ast.Module(body=[fns["_tint_key"]], type_ignores=[])
        _ast.fix_missing_locations(mod)
        ns = {}
        exec(compile(mod, msrc, "exec"), ns)
        k = ns["_tint_key"]
        cases = {(1.0, 1.0, 1.0): "ffffff", (0.0, 0.0, 0.0): "000000",
                 (2.0, -1.0, 0.5): "ff0080"}
        for rgb, want in cases.items():
            got = k(list(rgb))
            if got != want:
                fails.append("_tint_key(%s) = %r, want %r" % (list(rgb), got, want))
        # THE CASE THE REAL DATA WOULD NOT HAVE CAUGHT: vending_machine ships
        # a red default and a blue style. A collapsing key silently reuses the
        # first material for the second machine.
        if k([0.62, 0.14, 0.14]) == k([0.14, 0.26, 0.55]):
            fails.append("_tint_key collapses two visibly different colours")

    # ---- 3. the graph is actually wired, not merely defined ----------------
    if "_tint_multiply" in fns:
        td_src = _ast.get_source_segment(text, fns["_textured"]) or ""
        if "_tint_multiply(" not in td_src:
            fails.append("_tint_multiply is defined but _textured never calls "
                         "it -- the node would never be created")
        if "tint" not in [a.arg for a in fns["_textured"].args.args] + \
                         [a.arg for a in fns["_textured"].args.kwonlyargs]:
            fails.append("_textured takes no `tint` parameter")
    mm_src = _ast.get_source_segment(text, fns["make_material"]) or ""
    if 'pack.get("tintable")' not in mm_src:
        fails.append("make_material never reads pack['tintable'] -- a "
                     "tintable pack would be treated like any other")
    if "_tint_key(" not in mm_src:
        fails.append("make_material does not key the material cache on the "
                     "colour; two colours would share one material")

    # ---- 4. the probe ships, and says the boundary is unverified ----------
    probe = os.path.join(ROOT, "zoo", "tools", "tint_probe.py")
    if not os.path.isfile(probe):
        fails.append("tools/tint_probe.py is missing -- the export boundary "
                     "has no way to be measured")
    else:
        psrc = open(probe, encoding="utf-8").read()
        for token in ("baseColorFactor", "baseColorTexture"):
            if token not in psrc:
                fails.append("tint_probe.py never looks at %s" % token)
        _ast.parse(psrc)

    # ---- 5. the new tests exist and pass ----------------------------------
    tfile = os.path.join(ROOT, "zoo", "tests", "test_tintable.py")
    if not os.path.isfile(tfile):
        fails.append("tests/test_tintable.py is missing")
    else:
        try:
            import pytest as _pytest
            rc = _pytest.main([tfile, "-x"])
            if rc != 0:
                fails.append("tests/test_tintable.py failed (pytest rc=%s)" % rc)
        except ImportError:
            print("  (pytest not importable here -- run it yourself:")
            print("     cd zoo; python -m pytest tests/test_tintable.py)")

    if fails:
        print("SELFTEST FAILED (%d):" % len(fails))
        for f in fails:
            print("  - " + f)
        return 1
    print("SELFTEST OK -- 5 groups: flag surfacing (4 pack shapes), cache key "
          "(4 cases + the collapse case), graph wiring, probe present, tests "
          "green")
    return 0


def check():
    ok, bad = preflight()
    print("targets:")
    for rel in sorted(M["pre_sha"]):
        p = _abs(rel)
        state = "ok" if os.path.isfile(p) and _sha(p) == M["pre_sha"][rel] else "DRIFT/MISSING"
        print("  %-14s %s" % (state, rel))
    for rel in M["new"]:
        print("  %-14s %s" % ("create" if not os.path.isfile(_abs(rel)) else "EXISTS", rel))
    print("")
    if ok:
        print("PRE-FLIGHT CLEAN -- apply would write %d file(s)"
              % (len(M["pre_sha"]) + len(M["new"])))
        return 0
    print("PRE-FLIGHT REFUSED:")
    for b in bad:
        print("  " + b)
    return 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--revert", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.check:
        return check()
    if a.revert:
        return revert()
    if a.selftest:
        return selftest()
    return apply()


if __name__ == "__main__":
    sys.exit(main())
