"""Zoo 1.100.0: a fixture's same-material parts are one mesh, inside it and never across two (roadmap 233).

Anchored edits: `zoo_keeper/bpylayer/merge.py` (`pack_by_material` takes ``units``, each part's
placement: a part merges only inside its own, and a unit's parts must share one transform, which
the merged mesh takes), `zoo_keeper/bpylayer/export.py` (`export_glb` hands ``units`` to the
merge), `zoo_keeper/bpylayer/build.py` (`build_fixtures` records each part's placement and exports
merged by it, `merge_parts` the control, the merge's stats in the index), `tools/zoo_cli.py`
(`--no-merge-parts` reaches the fixtures), and a new `tests/test_fixture_merge.py`. Each file
pinned by hash and each anchor asserted once, nothing written on a miss; the files' own line
endings kept. Applies on Zoo 1.99.1. CHANGELOG and VERSION from
`zoo_fixture_merge/CHANGELOG_1.100.0.md`; `--results-pending` leaves the RESULT_ keys to `--fill`.

    python patches/patch_zoo_fixture_merge.py --results-pending && cd zoo && python -m pytest -q
    python patches/patch_zoo_fixture_merge.py --fill
    ZOO_ROOT=<copy> python patches/patch_zoo_fixture_merge.py --draft
"""
import hashlib
import os
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
ZOO = pathlib.Path(os.environ.get("ZOO_ROOT") or HERE.parent / "zoo")
SRC = HERE / "zoo_fixture_merge"
DRAFT = "--draft" in sys.argv
PENDING = "--results-pending" in sys.argv
FILL = "--fill" in sys.argv
RESULTS = {"RESULT_SUITE": "result_suite.txt", "RESULT_BPY": "result_bpy.txt",
           "RESULT_LAYER": "result_layer.txt"}
VERSION_WAS, VERSION = b"1.99.1", b"1.100.0"
CHANGELOG_HEAD = "## [1.99.1] - a hemisphere is the upper half it names, and every cap stands on its body\n"
MERGE = "zoo_keeper/bpylayer/merge.py"
EXPORT = "zoo_keeper/bpylayer/export.py"
BUILD = "zoo_keeper/bpylayer/build.py"
CLI = "tools/zoo_cli.py"
TEST = "tests/test_fixture_merge.py"
SHA = {MERGE: "35a9d9ea1a251457", EXPORT: "99c627a19bfaaafd", BUILD: "c0aa0e86dc145daa",
       CLI: "257c8b90c7ea7579"}

# --- merge.py -------------------------------------------------------------------------------
M_DOC_OLD = ("granularity. Merging ACROSS modules would cost exactly that, and is\n"
             "deliberately not done here.\n")
M_DOC_NEW = (M_DOC_OLD +
             "\n"
             "A LAYER MERGES BY ITS UNITS (1.100.0). A building's fixtures ship as one\n"
             "GLB of many placements -- a layer, not a module -- and merging across them\n"
             "would cost exactly that culling. ``units`` names each part's placement and\n"
             "the merge groups by it: one placement's parts that share a material become\n"
             "one mesh, and no two placements ever share one. A placement's parts are\n"
             "moved together (`build.build_fixtures` sets one matrix on them all), so\n"
             "inside a unit the identity rule becomes ONE TRANSFORM: the parts merge in\n"
             "the frame they share and the merged object takes it. Measured on 1.99.0's\n"
             "fixture species at their default corner: a streetlight is a pole, a base\n"
             "and a head in one metal, three meshes where one carries them; a pendant a\n"
             "cord and a socket; a wall pack an arm and a body; a sign box its arms and\n"
             "its cabinet (`docs/findings/fixture_merge/` in the factory).\n")
M_SIG_OLD = ("def pack_by_material(collection):\n"
             "    \"\"\"Build the merged export set for ``collection``. Never mutates it.\n"
             "\n"
             "    Returns a `Packed`, or None when there is nothing worth merging (every\n"
             "    group of size one would just rename parts for no gain).\n"
             "    \"\"\"\n")
M_SIG_NEW = ("def pack_by_material(collection, units=None):\n"
             "    \"\"\"Build the merged export set for ``collection``. Never mutates it.\n"
             "\n"
             "    Returns a `Packed`, or None when there is nothing worth merging (every\n"
             "    group of size one would just rename parts for no gain).\n"
             "\n"
             "    ``units`` (1.100.0): ``{object name: unit key}`` for a layer of many\n"
             "    placements, the keys sortable. Given, a part merges only with parts of\n"
             "    its own unit, a part with no unit is kept as itself, and a unit's parts\n"
             "    must share one transform, which the merged mesh takes. None is a\n"
             "    module: one unit, every part at identity.\n"
             "    \"\"\"\n")
M_LOOP_OLD = ("    for obj in collection.objects:\n"
              "        if obj.type != \"MESH\" or not partnames.is_mergeable(obj.name):\n"
              "            keep.append(obj)\n"
              "            continue\n"
              "        why = _unsupported(obj.data)\n"
              "        if why is None and not _identity(obj):\n"
              "            why = \"unapplied transform\"\n")
M_LOOP_NEW = ("    #: unit key -> the transform every part of that unit carries (1.100.0)\n"
              "    frames = {}\n"
              "    for obj in collection.objects:\n"
              "        if obj.type != \"MESH\" or not partnames.is_mergeable(obj.name):\n"
              "            keep.append(obj)\n"
              "            continue\n"
              "        if units is not None and obj.name not in units:\n"
              "            keep.append(obj)\n"
              "            continue\n"
              "        why = _unsupported(obj.data)\n"
              "        if why is None and units is None and not _identity(obj):\n"
              "            why = \"unapplied transform\"\n"
              "        if why is None and units is not None:\n"
              "            frame = frames.setdefault(units[obj.name], obj.matrix_world.copy())\n"
              "            if not _same_matrix(obj.matrix_world, frame):\n"
              "                why = \"transform differs from its unit's\"\n")
M_GROUP_OLD = ("    groups = partnames.group_parts(\n"
               "        ((name, mat or None, sig) for (name, mat, sig) in by_desc),\n"
               "        taken={o.name for o in collection.objects})\n")
M_GROUP_NEW = ("    if units is None:\n"
               "        groups = partnames.group_parts(\n"
               "            ((name, mat or None, sig) for (name, mat, sig) in by_desc),\n"
               "            taken={o.name for o in collection.objects})\n"
               "    else:\n"
               "        # One plan a unit, in unit order, each naming around every name\n"
               "        # taken before it, so the same layer builds the same names.\n"
               "        groups = []\n"
               "        used = {o.name for o in collection.objects}\n"
               "        for unit in sorted({units[name] for (name, _m, _s) in by_desc}):\n"
               "            planned = partnames.group_parts(\n"
               "                ((name, mat or None, sig) for (name, mat, sig) in by_desc\n"
               "                 if units[name] == unit), taken=used)\n"
               "            used.update(merged for merged, _k, _s in planned)\n"
               "            groups.extend(planned)\n")
M_OBJ_OLD = "        obj = bpy.data.objects.new(name, me)\n"
M_OBJ_NEW = ("        obj = bpy.data.objects.new(name, me)\n"
             "        if units is not None:\n"
             "            obj.matrix_world = frames[units[sources[0][0].name]]\n")
M_STATS_OLD = "        \"triangles\": before_tris,\n    }\n"
M_STATS_NEW = ("        \"triangles\": before_tris,\n"
               "        \"units\": len(frames) if units is not None else None,\n"
               "    }\n")
M_IDENT_OLD = "def _slots_used(me):\n"
M_IDENT_NEW = ("def _same_matrix(a, b):\n"
               "    \"\"\"Two transforms equal to 1e-6 in every element (1.100.0): the parts of\n"
               "    one placement, which `build.build_fixtures` moves with one matrix.\"\"\"\n"
               "    return all(abs(a[r][c] - b[r][c]) <= 1e-6\n"
               "               for r in range(4) for c in range(4))\n"
               "\n"
               "\n"
               "def _slots_used(me):\n")

# --- export.py ------------------------------------------------------------------------------
E_SIG_OLD = ("def export_glb(filepath, collection, merge_parts=True, share_textures=True,\n"
             "               weighted_normals=True):\n")
E_SIG_NEW = ("def export_glb(filepath, collection, merge_parts=True, share_textures=True,\n"
             "               weighted_normals=True, units=None):\n")
E_DOC_OLD = "    The merged objects are torn down before this returns, so the scene\n"
E_DOC_NEW = ("    ``units`` (1.100.0) goes to the merge: a layer of many placements names\n"
             "    each part's placement, and a part merges only inside its own\n"
             "    (`merge.pack_by_material`). None merges the collection as one module.\n"
             "\n" + E_DOC_OLD)
E_CALL_OLD = "    packed = merge.pack_by_material(collection) if merge_parts else None\n"
E_CALL_NEW = ("    packed = (merge.pack_by_material(collection, units=units)\n"
              "              if merge_parts else None)\n")

# --- build.py -------------------------------------------------------------------------------
B_INIT_OLD = ("    built = 0\n"
              "    markerless = 0\n"
              "    for i, p in enumerate(plan[\"placements\"]):\n")
B_INIT_NEW = ("    built = 0\n"
              "    markerless = 0\n"
              "    #: each visual part's placement (1.100.0), so the export merges a\n"
              "    #: fixture's same-material parts inside it and never across two\n"
              "    units = {}\n"
              "    for i, p in enumerate(plan[\"placements\"]):\n")
B_NEW_OLD = ("        new_objs = [o for o in coll.objects if o not in before]\n"
             "\n"
             "        # Recipes build centered. Mount 'above': bottom (-h/2) at the anchor\n")
B_NEW_NEW = ("        new_objs = [o for o in coll.objects if o not in before]\n"
             "        for obj in new_objs:\n"
             "            if obj.type == \"MESH\":\n"
             "                units[obj.name] = i\n"
             "\n"
             "        # Recipes build centered. Mount 'above': bottom (-h/2) at the anchor\n")
B_EXPORT_OLD = ("    # hardware. A layer, not a module. See the note in `build_dressing`.\n"
                "    export.export_glb(base + \".glb\", coll, merge_parts=False,\n"
                "                      weighted_normals=opts[\"weighted_normals\"])\n")
B_EXPORT_NEW = ("    # hardware. A layer, not a module. See the note in `build_dressing`.\n"
                "    # 1.100.0: MERGED BY PLACEMENT. A fixture's parts that share a material\n"
                "    # become one mesh and no two fixtures share one, so each stays its own\n"
                "    # culling unit and sheds the submissions its extra parts cost (roadmap\n"
                "    # 233); a streetlight's pole, base and head were three. `merge_parts`\n"
                "    # False is the one-build control, as it is for a module.\n"
                "    merge_stats = export.export_glb(base + \".glb\", coll,\n"
                "                                    merge_parts=opts[\"merge_parts\"],\n"
                "                                    weighted_normals=opts[\"weighted_normals\"],\n"
                "                                    units=units)\n")
B_INDEX_OLD = ("             \"skipped\": plan[\"skipped\"], \"placements\": plan[\"placements\"],\n"
               "             \"files\": files}\n")
B_INDEX_NEW = ("             \"skipped\": plan[\"skipped\"], \"placements\": plan[\"placements\"],\n"
               "             \"files\": files}\n"
               "    if merge_stats is not None:\n"
               "        index[\"merge\"] = merge_stats\n")

# --- zoo_cli.py -----------------------------------------------------------------------------
C_OLD = "                 \"seed\": args.seed, \"types\": types,\n"
C_NEW = ("                 \"seed\": args.seed, \"types\": types,\n"
         "                 # 1.100.0: a fixture's parts merge inside it; this is the control\n"
         "                 \"merge_parts\": not args.no_merge_parts,\n")


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
    p = ZOO / rel
    raw = p.read_bytes()
    got = hashlib.sha256(raw.replace(b"\r\n", b"\n")).hexdigest()[:16]
    assert got == SHA[rel], (rel, "is not the file this patch read", got)
    return p, _eol(raw, rel), raw.decode("utf-8").replace("\r\n", "\n")


def _write(p, eol, text):
    p.write_bytes(text.replace("\n", eol.decode()).encode("utf-8"))


def fill():
    assert (ZOO / "VERSION").read_bytes().strip() == VERSION, (ZOO / "VERSION").read_bytes()
    results = {}
    for key, name in RESULTS.items():
        value = (SRC / name).read_text(encoding="utf-8").strip()
        assert value and "RESULT_" not in value and not value.endswith("."), (name, value[-40:])
        results[key] = value
    writes = {}
    for path, rel in [(ZOO / "CHANGELOG.md", "CHANGELOG.md"),
                      (SRC / "CHANGELOG_1.100.0.md", "the entry")]:
        raw = path.read_bytes()
        eol = _eol(raw, rel)
        text = raw.decode("utf-8").replace("\r\n", "\n")
        for key, value in results.items():
            assert text.count(key) == 1, (rel, key, text.count(key))
            text = text.replace(key, value)
        writes[path] = text.encode("utf-8").replace(b"\n", eol)
    for path, data in writes.items():
        path.write_bytes(data)
    print("Zoo 1.100.0: results filled")


def main():
    if FILL:
        return fill()
    if DRAFT and not os.environ.get("ZOO_ROOT"):
        sys.exit("refusing: --draft is for a ZOO_ROOT copy, never the repo")
    assert (ZOO / "VERSION").read_bytes().strip() == VERSION_WAS, (ZOO / "VERSION").read_bytes()
    entry = _src("CHANGELOG_1.100.0.md")
    assert entry.startswith("## [1.100.0] - "), entry[:40]
    if not DRAFT:
        left = entry
        if PENDING:
            for key in RESULTS:
                left = left.replace(key, "")
        assert "RESULT_" not in left, "the changelog still carries an unfilled result"
    test_text = _src("test_fixture_merge.py.txt")
    assert not (ZOO / TEST).exists(), "already applied"

    mp, m_eol, mer = _read(MERGE)
    assert "_same_matrix" not in mer, "already applied"
    mer = _once(mer, M_DOC_OLD, M_DOC_NEW, "merge's chunk paragraph")
    mer = _once(mer, M_SIG_OLD, M_SIG_NEW, "pack_by_material's signature")
    mer = _once(mer, M_LOOP_OLD, M_LOOP_NEW, "the pooling loop")
    mer = _once(mer, M_GROUP_OLD, M_GROUP_NEW, "the grouping")
    mer = _once(mer, M_OBJ_OLD, M_OBJ_NEW, "the merged object")
    mer = _once(mer, M_STATS_OLD, M_STATS_NEW, "the stats")
    mer = _once(mer, M_IDENT_OLD, M_IDENT_NEW, "the matrix helper")

    ep, e_eol, exp = _read(EXPORT)
    exp = _once(exp, E_SIG_OLD, E_SIG_NEW, "export_glb's signature")
    exp = _once(exp, E_DOC_OLD, E_DOC_NEW, "export_glb's docstring")
    exp = _once(exp, E_CALL_OLD, E_CALL_NEW, "the merge call")

    bp, b_eol, bld = _read(BUILD)
    bld = _once(bld, B_INIT_OLD, B_INIT_NEW, "the placement loop")
    bld = _once(bld, B_NEW_OLD, B_NEW_NEW, "each placement's parts")
    bld = _once(bld, B_EXPORT_OLD, B_EXPORT_NEW, "the fixtures export")
    bld = _once(bld, B_INDEX_OLD, B_INDEX_NEW, "the index")

    cp, c_eol, cli = _read(CLI)
    cli = _once(cli, C_OLD, C_NEW, "the fixtures options")

    cl = ZOO / "CHANGELOG.md"
    cl_raw = cl.read_bytes()
    cl_eol = _eol(cl_raw, "CHANGELOG.md")
    cl_text = cl_raw.decode("utf-8").replace("\r\n", "\n")
    assert cl_text.startswith(CHANGELOG_HEAD) and cl_text.count(CHANGELOG_HEAD) == 1, cl_text[:120]
    # every anchor matched: now write
    _write(mp, m_eol, mer)
    _write(ep, e_eol, exp)
    _write(bp, b_eol, bld)
    _write(cp, c_eol, cli)
    (ZOO / TEST).write_bytes(test_text.encode("utf-8"))
    _write(cl, cl_eol, entry.rstrip("\n") + "\n\n" + cl_text)
    (ZOO / "VERSION").write_bytes(VERSION)
    print("Zoo 1.99.1 -> 1.100.0" + (" (DRAFT)" if DRAFT else ""))


if __name__ == "__main__":
    main()
