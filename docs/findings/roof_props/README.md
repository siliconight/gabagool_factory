# Roof props: the merge, measured on one roof (roadmap 181)

**Question.** Zoo 1.101.0 exports a roof's props merged (each prop's placement
baked into its vertices, then `pack_by_material`'s module rule). The merge
groups a module's parts by part FAMILY and material -- the name before the
first underscore (`Hvac_Cabinet`, `Hvac_Cabinet.001` ...) -- so what does one
roof's layer cost in submissions, merged against unmerged?

**Instrument.** `tools/zoo_cli.py --roof-props <slots> --out <dir> --theme
delco --no-blend`, once as shipped and once with `--no-merge-parts` (the
one-build control), on a copy of `deli_a01.slots.json` as the 0.208.0 library
shipped it (38 x 28 m roof, top at 6.6 m, one hatch hole, no `keep_out` yet:
the 0.209.0 rebuild had not run). Flat materials (no skin library). Blender
5.1.1, 2026-10-11. `docs/findings/fixture_merge/layer_count.py` reads each
GLB's visual mesh nodes; the `.built.json` indexes carry the merge's own
stats. Logs: `build_merged.txt`, `build_unmerged.txt`; counts:
`layer_count_*.txt`; indexes: `deli_a01_roofprops.*.built.json`.

**Result.**

    scatter: 17 props -- hvac_unit 4, vent_stack 6, exhaust_fan 3, skylight 2,
             satellite_dish 2; no water tank (the roof is 6.6 m, the gate 12);
             forbidden rects 1 (the hatch's hole, grown by VOID_CLEAR)
    unmerged: 59 visual mesh nodes, 59 submissions
    merged:   59 parts in -> 6 meshes out (one a species family), 15 kept
              (the collider proxies, never merged), 4,392 triangles both ways

**What is evidence of what.** The counts are the two GLBs', read by the same
script that read the fixture merge. The draw-call figure is a submission
count, not a frame time: cold run 9245 prices it on the level. The scatter
differs from 1.100.0's for every seed (the yaw is drawn first), and no level
has had a roof prop, so nothing shipped moved.

**Not measured here.** Keep-out against a landing (the slots had none yet);
the look (the walker's eye on 9245's frames); the bake's lightmap users for
six merged meshes against 59.

`test_roofprops_new.py` is the test module as it was run against 1.100.0
first (8 of 13 failing) before the patch existed.
