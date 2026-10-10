## [1.93.0] - trash_bags: a heap of filled garbage bags

### What the walker asked for
Roadmap 219 note 11, from the walk of club_block_014 on 2026-10-09: "need
filled black garbage bags stacked near the garbage bins". Lot stands a
dumpster at the back or side of each building (Zoo 1.58.0, Lot 0.90.0). This
is what sits beside it, and Lot 0.104.0 places it there.

### `trash_bags`: a heap of filled bags
`recipes/trash_bags.py`, every decision from `core/trash_bag_forms.py`,
which is pure.
- **A filled bag is a sack that has slumped.** Each bag is an ellipsoid
  pushed out of shape (`shape`):
  - pressed flat where it sits;
  - spread at the belly;
  - lumpy where what is in it pushes out;
  - gathered at the top into a neck, with a knot and two ears of its own
    plastic tied on top.
- **A heap is a row and a top** (`heap`). Two to five bags stand on the
  ground across the slot's width, and one or two more are thrown into the
  gaps. The top bags rest into the row, not on it. Every bag has its own
  size, yaw and lean.
- **Four heaps** (`module_variants: 4`). A slot's `variant` picks one.
- **Mostly black.** One bag in twelve is a white kitchen bag and one a green
  contractor bag (`COLOURS`), because nobody buys one kind.
- **One object and one material, so one draw a heap.**
  - The material is the genome's plastic in the style's colour, which is
    white. Each bag's own colour rides in `Wear`.
  - Under a skin library, the delco plastic pack is tintable and near white
    (0.93 mean albedo, Pixelcoat 0.61.0). The `Wear` multiply is wired on
    the textured path too, so the black stays black.
- **The slot is exact.** After the lumps and leans, one affine map fits the
  heap to the slot's box, so its outermost faces are the slot's faces.
- **Collision is the slot's box.** A heap of bags is soft, but a body still
  does not walk through it.
- **Measured:** 1,536 triangles at the default 1.4 x 0.8 x 0.75 slot and at
  the smallest, and 2,304 at the largest, 2.0 x 1.2 x 1.0. The genome's
  budget is 2,800, a regression detector and not a frame cost.

### Tests
- **`tests/test_trash_bags.py`.**
  - The pure checks:
    - discovered, and the genome validates;
    - four heaps, one a variant;
    - a row on the ground and more on top, at three slots and every
      variant, with every bag inside the slot;
    - no two flat bottoms on one plane;
    - mostly black;
    - a bag pressed flat, spread and gathered;
    - the same bag every time.
  - The bpy half: an exact fit with one part and one material at three
    slots, and no two faces sharing a plane at all four variants.
- **The counts a new species moves:**
  - `PROP_SPECIES` gains `trash_bags`;
  - `CENSUS_BUILDS` goes from 369 to 372, with the census's own line;
  - the style-resolution count goes from 96 to 97.
- **Run inside Blender 5.1.1:** the species' file, 16 passed. The coplanar
  census, `tools/coplanar_census.py --species trash_bags`: "3 builds, 0 with
  coincident pairs, 0 that did not build" (1,536 / 1,536 / 2,304 tris).
- **Found while building it, and fixed before the tests passed:**
  - **Blades.** The first build took `bm.verts[n0:]` after each ellipsoid as
    the vertices just made. After the helper's operators that sequence is
    not in creation order, so the shaping moved the wrong vertices. The heap
    grew half-metre blades, and the fit to the slot shrank every bag to pay
    for them. Each piece's vertices now come from the list `add_ellipsoid`
    returns.
  - **One coincident pair.** On the first heap, the coplanar probe found a
    bag's bottom clamped onto one plane, which folded two of its triangles
    back to back. `shape` squeezes the bottom now rather than clamping it:
    about 7 mm of dome on a full-size bag.
  - **The genome.** The recipe first passed its material as a literal, and
    `test_recipe_reads_its_genome` would have failed it. It reads the
    genome's material and colour now, as `window_drape` does.

Suite: 4,094 passed, 421 skipped, 1 xfailed (1.92.0: 4,081, 414 and 1). The
species adds 13 passes and 7 Blender skips: 9 and 7 in its own file, and 4
in the sweeps every species joins -- its materials closed three ways, and
`test_recipe_reads_its_genome`. Its own file, run inside Blender 5.1.1: 16
passed.
