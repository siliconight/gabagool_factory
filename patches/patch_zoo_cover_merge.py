"""Zoo 1.68.0: a building's covers merge, one side at a time.

Every Patina cover reached the level as its own mesh, one draw call each;
hiding them all on cold run 9154's package took the worst view from 8,690
draws / 27.33 ms p95 to 5,571 / 17.74 ms (roadmap 180). See
`zoo_cover_merge/CHANGELOG_1.68.0.md`.

Anchored edits (every anchor once; refuses on a miss):
  zoo_keeper/core/dressing.py        SIDES, footprint, cover_side; a side
                                     on every plan, a count a side
  zoo_keeper/recipes/dress_cover.py  a cover is named Cover<side>_<kind>
  zoo_keeper/bpylayer/build.py       covers built in place, merged per
                                     side per material; stats in the index
  tools/zoo_cli.py                   --no-merge-parts reaches --dress; the
                                     merge is printed
Copies the test; CHANGELOG and VERSION.

    python patch_zoo_cover_merge.py
"""
import pathlib
import shutil

HERE = pathlib.Path(__file__).resolve().parent
ZOO = HERE.parent / "zoo"
SRC = HERE / "zoo_cover_merge"


def _edit(path, pairs):
    s = path.read_text(encoding="utf-8")
    assert "\r" not in s, path
    for old, new in pairs:
        assert s.count(old) == 1, (path.name, old[:70])
        s = s.replace(old, new)
    path.write_text(s, encoding="utf-8", newline="\n")


# --- core/dressing.py -------------------------------------------------------

SIDE_ANCHOR = '''def plan_dressing(manifest: dict, genome: dict, theme: str,
                  tool_version: str) -> dict:
'''
SIDE_NEW = '''#: THE SIDES A BUILDING'S COVERS MERGE BY (1.68.0), in Deli Counter's facings
#: -- N = +y, E = +x, S = -y, W = -x, the letters its `ext_<storey>_<facing>_*`
#: slot ids carry, read against their own orders' normals on cold run 9154.
#: A side is the unit that enters and leaves view together, which is what a
#: merged mesh has to be: the export culls by occlusion, and one mesh holding
#: a building's front and back covers keeps the back drawn whenever the front
#: is seen.
SIDES = ("N", "E", "S", "W")


def footprint(points):
    """``(cx, cy, hx, hy)``: the box the covers stand in, seen from above --
    its centre and half-sizes in x and y. The building as its covers see it."""
    xs = [float(p[0]) for p in points]
    ys = [float(p[1]) for p in points]
    if not xs:
        return (0.0, 0.0, 0.0, 0.0)
    return ((min(xs) + max(xs)) / 2.0, (min(ys) + max(ys)) / 2.0,
            (max(xs) - min(xs)) / 2.0, (max(ys) - min(ys)) / 2.0)


def cover_side(normal, pos, box):
    """Which of `SIDES` a cover belongs to.

    A WALL-FACING cover is on the side its normal leaves. An UP-FACING one --
    a curb at the wall's foot, an edge strip on the roof, 60 of a rowhome's
    103 covers -- has no side of its own and takes the one it stands nearest,
    measured in units of the footprint's half-size so a long building's end
    curbs go to its end and not its flank. Grouped by normal alone, every curb
    and roof edge of a building would be one mesh the size of the building.
    Ties go to x, then to the negative side: deterministic, not meaningful.
    """
    nx, ny, nz = (float(v) for v in normal)
    side = max(abs(nx), abs(ny))
    if side > 1e-6 and side >= abs(nz):
        if abs(nx) >= abs(ny):
            return "E" if nx > 0 else "W"
        return "N" if ny > 0 else "S"
    cx, cy, hx, hy = box
    dx = (float(pos[0]) - cx) / max(hx, 1e-6)
    dy = (float(pos[1]) - cy) / max(hy, 1e-6)
    if abs(dx) >= abs(dy):
        return "E" if dx > 0 else "W"
    return "N" if dy > 0 else "S"


def plan_dressing(manifest: dict, genome: dict, theme: str,
                  tool_version: str) -> dict:
'''

PLAN_OLD = '''    plans = [dress_plan(o, genome, theme, space, tool_version) for o in orders]
    counts: dict[str, int] = {}
    for p in plans:
        k = p["order"]["cover"]
        counts[k] = counts.get(k, 0) + 1
    return {
        "building_id": manifest.get("building_id"),
        "trim_sheet": manifest.get("trim_sheet"),
        "space": space,
        "theme": theme,
        "plans": plans,
        "counts": dict(sorted(counts.items())),
        "cover_count": len(plans),
    }
'''
PLAN_NEW = '''    plans = [dress_plan(o, genome, theme, space, tool_version) for o in orders]
    # every cover's side (1.68.0), against the footprint of ALL of them, in
    # the Blender frame `dress_plan` has already put them in
    box = footprint([p["order"]["pos"] for p in plans])
    counts: dict[str, int] = {}
    sides: dict[str, int] = {}
    for p in plans:
        k = p["order"]["cover"]
        counts[k] = counts.get(k, 0) + 1
        p["side"] = cover_side(p["order"]["normal"], p["order"]["pos"], box)
        sides[p["side"]] = sides.get(p["side"], 0) + 1
    return {
        "building_id": manifest.get("building_id"),
        "trim_sheet": manifest.get("trim_sheet"),
        "space": space,
        "theme": theme,
        "plans": plans,
        "counts": dict(sorted(counts.items())),
        "sides": dict(sorted(sides.items())),
        "cover_count": len(plans),
    }
'''

# --- recipes/dress_cover.py -------------------------------------------------

RECIPE_OLD = '''    obj = geometry.bm_to_object(
        bm, f"Cover_{cover}", collection,
'''
RECIPE_NEW = '''    # THE NAME IS THE MERGE GROUP (1.68.0): `partnames.family` is everything
    # before the first underscore, so `CoverN_gutter_run` merges with the rest
    # of the north side in its material and nothing else. A plan with no side
    # (the prompt/DNA path) keeps the old `Cover_<kind>`.
    obj = geometry.bm_to_object(
        bm, f"Cover{plan.get('side') or ''}_{cover}", collection,
'''

# --- bpylayer/build.py ------------------------------------------------------

DOC_OLD = '''    Reads Patina v0.11 ``<building>.dressing.json`` (via ``core.dressing``),
    builds one thin cover mesh per order at its anchor pos/orientation, and
    writes them into a single ``<building>_dressing.glb`` plus a
    ``<building>_dressing.built.json`` index. Never emits collision: covers are
    visual only, so the DC greybox collision stays authoritative.
    """
'''
DOC_NEW = '''    Reads Patina v0.11 ``<building>.dressing.json`` (via ``core.dressing``),
    builds one thin cover mesh per order at its anchor pos/orientation, and
    writes them into a single ``<building>_dressing.glb`` plus a
    ``<building>_dressing.built.json`` index. Never emits collision: covers are
    visual only, so the DC greybox collision stays authoritative.

    The covers are merged at export (1.68.0), one mesh per SIDE of the
    building per material -- see the comment at the export below.
    """
'''

PLACE_OLD = '''        # place: orient by the anchor normal, then translate to its position.
        rot = _orient_matrix(order["normal"], order.get("tangent"))
        trans = mathutils.Matrix.Translation(mathutils.Vector(order["pos"]))
        m = trans @ rot
        for obj in result["objects"]:
            obj.matrix_world = m @ obj.matrix_world
'''
PLACE_NEW = '''        # place: orient by the anchor normal, then translate to its position.
        rot = _orient_matrix(order["normal"], order.get("tangent"))
        trans = mathutils.Matrix.Translation(mathutils.Vector(order["pos"]))
        m = trans @ rot
        for obj in result["objects"]:
            # BUILT IN PLACE (1.68.0): the placement goes into the vertices and
            # the object stays at identity, as every Zoo part is built. The
            # merge reads raw coordinates and leaves an object with a
            # transform unmerged (`merge._identity`), so a cover placed by its
            # matrix could never join its side. A yaw and a translation: the
            # UVs, colours and shading edges written before this are untouched.
            if obj.data.users != 1:
                raise AssertionError(
                    "dressing: cover %r shares its mesh; baking its placement "
                    "would move the other user too" % obj.name)
            obj.data.transform(m @ obj.matrix_world)
            obj.matrix_world = mathutils.Matrix.Identity(4)
'''

EXPORT_OLD = '''    # NOT MERGED, AND THIS IS THE LINE THAT SAYS SO. This collection is a
    # whole BUILDING's covers, each already transformed to its own anchor --
    # not one module. Packing them by material would weld geometry from
    # opposite faces of the building into one mesh, which is a single
    # bounding box that is never off-screen: it trades every cover's culling
    # for the draw calls, and the covers are the one layer already handled
    # downstream (`level_factory/assets/godot/extract_meshes.gd` merges them
    # with the placement baked in, per visible chunk).
    export.export_glb(base + ".glb", coll, merge_parts=False)
'''
EXPORT_NEW = '''    # MERGED ONE SIDE OF THE BUILDING PER MATERIAL (1.68.0). Until this
    # version the covers were exported unmerged, on the claim that Level
    # Factory's `extract_meshes.gd` merged them downstream "per visible
    # chunk". It does not: that script is the surface-clutter layer's, and
    # every `Dressing/Cover_*` reached the level as its own MeshInstance3D --
    # 3,370 of them in cold run 9154's gas_block_001, and hiding them took the
    # worst view from 8,690 draws / 27.33 ms p95 to 5,571 / 17.74 ms
    # (roadmap 180).
    #
    # The worry that comment carried was right, and it sets the unit: packing
    # a whole building by material welds its opposite faces into one bounding
    # box, and with the export's occlusion culling that keeps a building's
    # back covers drawn whenever its front is seen. A SIDE enters and leaves
    # view together. Each cover is named for its side (`dress_cover`,
    # `core.dressing.cover_side`), so the family `merge.pack_by_material`
    # groups by IS the side, and the merge's own guarantees -- triangle count
    # asserted, vertices unwelded, one surface per material -- come with it.
    stats = export.export_glb(base + ".glb", coll, merge_parts=opts["merge_parts"])
'''

INDEX_OLD = '''        "cover_count": plan["cover_count"],
        "counts": plan["counts"],
        "files": files,
    }
    index_file = f"{stem}.built.json"
'''
INDEX_NEW = '''        "cover_count": plan["cover_count"],
        "counts": plan["counts"],
        "sides": plan["sides"],
        # what the merge did (1.68.0): None when it was off or found nothing
        # to merge; `refused` names every cover left as its own mesh, and why
        "merge": stats,
        "files": files,
    }
    index_file = f"{stem}.built.json"
'''

RETURN_OLD = '''            "covers_built": built, "files": files, "index_file": index_file}
'''
RETURN_NEW = '''            "covers_built": built, "files": files, "index_file": index_file,
            "merge": stats}
'''

# --- tools/zoo_cli.py -------------------------------------------------------

CLI_OLD = '''    # No `merge_parts`: a dressing layer is a whole building's covers, never
    # one module, and `build_dressing` does not merge at all. Passing the
    # flag here would be a knob with no effect.
    res = build.build_dressing(
        manifest, os.path.abspath(args.out), theme=args.theme,
        options={"save_blend": not args.no_blend, "clear_scene": True})
'''
CLI_NEW = '''    # `merge_parts` reaches the dressing (1.68.0): `build_dressing` merges a
    # building's covers one side per material, and --no-merge-parts is the
    # one-build control, as it is for a kit.
    res = build.build_dressing(
        manifest, os.path.abspath(args.out), theme=args.theme,
        options={"save_blend": not args.no_blend, "clear_scene": True,
                 "merge_parts": not args.no_merge_parts})
'''

PRINT_OLD = '''    print(f"[zoo]   {res['covers_built']} covers ({summary}); collision: none")
'''
PRINT_NEW = '''    print(f"[zoo]   {res['covers_built']} covers ({summary}); collision: none")
    st = res.get("merge")
    if st:
        print(f"[zoo]   merged: {st['parts_in']} covers -> {st['meshes_out']} meshes "
              f"(a side of the building per material); refused {len(st['refused'])}")
        for name, why in st["refused"][:5]:
            print(f"[zoo]     refused {name}: {why}")
    else:
        print("[zoo]   merged: nothing (off, or every group a single cover)")
'''


def main():
    assert (ZOO / "VERSION").read_text(encoding="utf-8").strip() == "1.67.0"
    _edit(ZOO / "zoo_keeper" / "core" / "dressing.py",
          [(SIDE_ANCHOR, SIDE_NEW), (PLAN_OLD, PLAN_NEW)])
    _edit(ZOO / "zoo_keeper" / "recipes" / "dress_cover.py", [(RECIPE_OLD, RECIPE_NEW)])
    _edit(ZOO / "zoo_keeper" / "bpylayer" / "build.py",
          [(DOC_OLD, DOC_NEW), (PLACE_OLD, PLACE_NEW), (EXPORT_OLD, EXPORT_NEW),
           (INDEX_OLD, INDEX_NEW), (RETURN_OLD, RETURN_NEW)])
    _edit(ZOO / "tools" / "zoo_cli.py", [(CLI_OLD, CLI_NEW), (PRINT_OLD, PRINT_NEW)])
    shutil.copyfile(SRC / "test_cover_sides.py", ZOO / "tests" / "test_cover_sides.py")
    ch = ZOO / "CHANGELOG.md"
    s = ch.read_text(encoding="utf-8")
    ch.write_text((SRC / "CHANGELOG_1.68.0.md").read_text(encoding="utf-8").rstrip("\n") + "\n\n" + s,
                  encoding="utf-8", newline="\n")
    (ZOO / "VERSION").write_text("1.68.0", encoding="utf-8", newline="\n")
    print("applied Zoo 1.68.0")


if __name__ == "__main__":
    main()
