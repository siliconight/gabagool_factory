"""Roadmap item 180: every Patina cover is its own draw call, measured.

Cold run 9154 (`docs/cold_runs/cold_9154/NOTES.md`). Appended after item
179, the status line directly above the heading (the `roadmap_status.py`
convention); the generated index is NOT touched here --
`roadmap_status.py --write` regenerates it.

    python patch_roadmap_180_cover_draws.py <roadmap path>
"""
import pathlib
import sys

ANCHOR = ("    ride Patina's surface dressing they ride its MultiMesh: cold run 9146's\n"
          "    export packed 4,241 dressing instances into 4 draw calls.\n")

ITEM = r"""
*STATUS: OPEN 2026-10-05 -- MEASURED on cold run 9154's package: hiding every cover takes the worst view from 8,690 draws / 27.33 ms p95 to 5,571 / 17.74 ms, and the median view 850 draws / 2.06 ms lighter; control 0 draws / +0.05 ms. Nothing merges them.*

**180. Every Patina cover is its own draw call, and the covers are a third of
the worst view.** Patina's facade dressing -- the curbs, edge strips, base
courses, conduit, gutters and downspouts around every building -- reaches the
level as one MeshInstance3D per cover, each with one surface.

**WHERE IT COMES FROM.** Zoo's `build_dressing`
(`zoo_keeper/bpylayer/build.py`) exports a building's covers with
`merge_parts=False`. Its comment says Level Factory's `extract_meshes.gd`
merges them downstream "per visible chunk". It does not:
  * `extract_meshes.gd` belongs to the surface-clutter layer;
  * the only Level Factory code naming `_dressing.glb` is the worldskin's
    tiling list;
  * the census on cold run 9147 showed every `Dressing/Cover_*` as its own
    MeshInstance3D.
The comment's own worry -- welding opposite faces into one bounding box --
is real, and is why the unit below is a face.

**HOW MANY, COUNTED THREE WAYS (9152 -> 9154).**
  * 1,080 -> 1,323 cover meshes in the nine dressing GLBs.
  * 2,783 -> 3,370 cover instances in the level. The six rowhome Empty
    variants are placed 26 times.
  * The export's lightmap users 7,676 -> 8,263, and the perf harness's mesh
    census 7,730 -> 8,317.
All three moved by exactly 587, the gutters and downspouts of Patina
0.25.0/0.25.1 and Zoo 1.67.0.

**WHAT THEY COST.** Fixed stations, 53 station x heading pairs, with
`_runs/perf_inner/run.py` and `patches/lf_empties/compare_price.py`.
  * **The gutters alone** (A = 9152, B = 9154, A2 = 9152): draws median
    +137, mean +160, up to +418 a view. The median frame is +0.274 ms
    (mean +0.367, up to +1.255); control +0.018. Every one of the 53 views
    got slower.
  * **Every cover hidden** (A = 9154; B = the same with each building's
    `Dressing` node `visible = false` by `patches/lf_empties/make_nocov.py`;
    A2 = 9154): draws median -850, mean -1,021, up to -3,119 a view. The
    median frame is -2.062 ms (mean -2.515, up to -9.334); control +0.054.
  * Stations over the provisional budget: 13 of 14 as shipped, 11 of 14
    with the covers hidden. The covers are not the whole of the overrun.

Hiding is a ceiling, not a design: the level loses its trim. A merge keeps
a few meshes a building where there are about 100 today. It recovers most
of the ceiling, by an amount not yet measured.

**THE UNIT TO MERGE IS ONE FACE OF ONE BUILDING, PER MATERIAL.** The
export culls by occlusion: `use_occlusion_culling=true`, and 1,407 box
occluders in `occluders.tscn`.
  * Merging a whole building per material would keep its back-side covers
    drawn whenever any of it is visible -- the trade `CLAUDE.md`'s merge
    rule forbids.
  * A face's covers enter and leave view together. Grouping by the cover
    normal's dominant axis and sign, times the materials in use today (the
    concrete skin and `metal_painted`), is at most 12 meshes a building.

**RE-READ AFTER A MERGE, NOT ASSUMED.**
  * **The lights-per-object census.** 46 meshes are over the cap of 8 in
    every report so far. A merged face is touched by more lights than one
    cover, and a dropped light darkens it.
  * **The lightmap.** Bake time is 88.5 s today, and the texel density of
    the freight terminal's merged 54.3 m face is not that of a 0.875 m
    gutter section.
  * **The worldskin.** It names `_dressing.glb` in its tiling list, so a
    merged face must still project.
  * **The price, the same way:** A = as shipped, B = merged, A2 = as
    shipped, at the same stations.

**WHAT KIND OF WORK THIS IS.** It moves no intervention count. It is the
frame budget (`CLAUDE.md`, "Every frame is spent on somebody else's
machine"), and every Empty detail still queued -- window air conditioners,
bars, lintels and sills -- adds covers to multiply by placements.
"""


def main():
    p = pathlib.Path(sys.argv[1])
    d = p.read_bytes()
    assert b"\r\n" not in d, "the roadmap is LF; a CRLF means something changed"
    s = d.decode("utf-8")
    assert s.count(ANCHOR) == 1, "anchor not found exactly once"
    assert s.endswith(ANCHOR), "item 179 is no longer the last thing in the file"
    assert "**180." not in s, "item 180 already exists"
    p.write_bytes((s + ITEM).encode("utf-8"))
    print("appended item 180 to", p)


if __name__ == "__main__":
    main()
