## [1.67.0] - a gutter that reads as a gutter, a downspout, painted metal

The walker, 2026-10-04: "also we need rain gutters". Patina has ordered a
`gutter_run` under every roofline since its 0.18. Zoo built each one as a
solid box, 10 cm proud by 14 cm tall, centred ON the wall face -- so half of
it stood inside the wall -- in the concrete every other cover wears. From the
street that is a ledge, not a gutter. Patina 0.25.0 adds `downspout` orders,
which nothing built.

- **The gutter is an open trough off the wall face** (`gutter_parts`):
  - a back on the wall;
  - a floor;
  - a front a little lower than the back (`GUTTER_FRONT`);
  - a rolled bead along the front's top.

  Nothing spans the mouth, so street level sees a lip and its shadow. Every
  part runs the full span, so sections butt at module seams.
- **The downspout** (`downspout_parts`, `_COVER["downspout"]`):
  - a 3 x 2 inch leader on a 2 cm standoff;
  - two straps;
  - a cast boot at the ground, where a Philadelphia rowhouse's leader goes
    into the sewer.

  The boot also means no elbow kicking out across the sidewalk: non-collision
  geometry in walkable space is what panel fields were removed for.
  `strip_size` runs it up the wall like a conduit.
- **Both are painted metal** (`METAL_COVERS`): `dress_plan` gives them
  `metal_painted` when the `dress_cover` genome offers it, which it now does.
  `delco_1997` maps that kind to Pixelcoat's `metal_painted_neutral`. A
  genome that does not offer it keeps its default.
- **The metal split, for `dress_cover`.** `test_material_options_closed`
  holds that a species offering a split kind offers no raw `metal` and no
  style names it: raw `metal` resolves the theme's own pack (delco_1997's is
  rusted street metal) and ignores the genome colour. So:
  - `dress_cover` offers `concrete`, `plaster` and `metal_painted`, and is
    declared in that test's `PAINTED`;
  - the two styles whose every cover was raw `metal`, `center_city` and
    `industrial_flats`, move to `metal_painted`, since a metal facade trim is
    painted flashing.

  That is a look change in those two themes; `delco` and `delco_1997` covers
  stay concrete.

Both new shapes are pure part lists, as `frame_strips` is, tested without
Blender. Every other cover is built exactly as before.

**Cost.** The painted metal is a second cover material per building.
Level Factory merges covers per visible chunk and per material, so it can add
a draw per chunk that holds gutters. It is priced on the cold run that ships
it, against the run before.

`tests/test_gutters.py`:
- a gutter is an open trough standing off the wall (fails on 1.66.0);
- a downspout stands off the wall into a boot at the ground;
- `strip_size` runs it up the wall;
- gutters and downspouts are painted metal, and the rest are not;
- the control: a genome without the metal keeps its default.
