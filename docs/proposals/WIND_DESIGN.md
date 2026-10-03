# The wind -- design, 2026-10-03

Steps 3 and 4 of `MOVING_PARTS_DESIGN.md` (small things that move), after
steps 1 and 2 shipped as Zoo 1.55.0 / Level Factory 0.129.0. Shown before
anything was built; the walker: "start with the crowns".

**Status.** Step 3a (the crowns) SHIPPED as Zoo 1.56.0 and Level Factory
0.130.0 (`docs/findings/wind/NOTES.md`: invisible at rest within 15 pixels
of 746,496; the lean shown in a storm frame; draws identical in 53 views).
Steps 3b and 4 are not started. The amplitudes below are the shipped
starting values; the walker's eye on the frames sets them.

## What is in the level, read off cold run 9139's package

    London plane trees   14 instances (one GLB scene each; not a MultiMesh)
    red maple             1
    pole flyer sleeves    3
    pennant rows, banners, ceiling hangers   0 (other briefs place them)

A tree is three surfaces: the grate (iron), the wood (trunk, branches,
twigs; 1,951 vertices, a textured skin with a normal map) and the CROWN
(every leaf cluster in one object, 1,891 vertices, `M_Skin_vegetation_*`:
an albedo texture and a metallic-roughness texture, no normal map, no
alpha). A flyer sleeve is one object on one painted material, every sheet a
strip of arc facets from its foot `z0` to its head `z1`. A pennant is a
triangular prism pinned at its hoist band, tip down, one material per team
colour. A banner is straps, a rod, a cloth, an art quad and a hem bar; a
hanger a board on a chain.

## The rule, carried over

A thing moves because something drives it. Here the driver is THE WIND:
one wind for the whole level, a direction and a strength from the brief's
weather, and gusts that travel across the lot so a tree, a flyer and a
pennant answer the same gust a moment apart. Indoors there is no wind: a
hung thing indoors drifts on the building's air, a degree, slowly. Which
of the two a species answers is decided by the species (a tree is outside,
a banner is inside), never by where a placement happened to land.

## The mechanism, and how it differs from the turn

Vertex shaders on the shader clock, installed at import by the worldskin,
as the turning parts are. Two differences, both learned on step 1:

1. **A WEIGHT, not a pivot.** Each vertex carries how much it moves
   (0 where the thing is attached, 1 at its free end) in UV2.x, and a
   phase of its own in UV2.y so two leaf clusters do not flap in step. A
   weight is a scalar: re-centring, fitting and merging leave it alone, so
   the trap the pivots fell into (0.7 m stale after `recentre`) cannot
   bite -- but the TEST is still against the shipped file: weight 0 at the
   vertex nearest the attachment, the largest weight at the vertex farthest
   from it, read off POSITION and TEXCOORD_1 of the GLB.
2. **The material under it is TEXTURED.** A roller is flat chrome, so the
   turn shader reproduces a flat material. A crown wears a skin. The sway
   shader reproduces exactly what Zoo's textured skins use and nothing
   more: the albedo texture (nearest filter, its UV1 scale), the
   metallic-roughness texture (glTF's G = roughness, B = metallic), the
   vertex colour where the surface is tinted, the roughness and metallic
   factors, alpha scissor where the skin is a cutout. A material carrying
   anything outside that set -- a normal map, an emission, a blend -- is
   REFUSED: left still and reported by name, never drawn wrong. The wood
   has a normal map and does not move, so nothing in this level is refused;
   the rule exists for the next skin. Before any motion is added, the
   crown is shot before and after with the wind at zero and compared pixel
   for pixel: the replacement must be invisible at rest.

**The wind reaches the shader as one global uniform**, `lf_wind` (a
vector: direction times metres a second), declared in the shipped
`project.godot`'s `[shader_globals]` by the export and set from the brief's
weather word:

    clear       1.5 m/s   a breath: leaves move, nothing else does
    rain        4.0
    storm       9.0
    hurricane  15.0, and every amplitude below is capped

Gusts are computed in the shader from TIME and the vertex's world
position: a slow swell (period about 7 s) over a slower one, phased by the
distance downwind (`dot(world, dir) / 10 m/s`), so the front walks across
the lot; plus a per-node offset so two trees in the same place still
differ. No CPU. Lux owns weather; its `LuxWeatherProfile` is the right home
for a wind field and `set_weather` the right place to move the global at
runtime. The first cut reads the brief's word at export; Lux grows the
field when a level changes weather while it runs.

## What moves, in build order

### 3a. The crown of a tree (outside; 15 in this level)

Weight = the vertex's height above the crown's base, squared, over the
crown's height: the top of the crown sways, the branch tips barely. Tip
displacement = weight x 0.02 m per m/s of wind (3 cm in a breath, 18 cm in
a storm), along the wind, with the lee lean a real crown has (it does not
swing back past upright); a small flutter on each cluster's facets at
about 2 Hz, a centimetre, phased by UV2.y. The wood and the grate do not
move: a crown moving against a fixed trunk is what a tree does. Normals
are left alone; the displacement is small against a faceted blob. The
shadow pass runs the same vertex stage, so the shadow sways with it.
Cost: zero draws (the crown is already one surface); a vertex stage on
1,891 vertices a tree, 28,000 a frame for the fifteen.

### 3b. The flyers on the poles (outside; 3 sleeves here)

A flyer is stapled at its head and loose at its foot. Weight = how far
down the sheet the vertex is, cubed, so only the lower corners lift: a
centimetre and a half out from the pole on a gust, with a flutter at 3 Hz.
The sleeve stays one object on one material. Cost: zero draws.

### 4a. Pennant rows (inside; card shops, car lots)

Pinned at the hoist, free at the tip: weight = distance below the hoist
over the length. Inside there is no wind, so the driver is the shop's own
air -- a 3 cm tip sway and a slow 0.5 Hz flutter -- and in a level that
places them outside (a car lot's strip) they take `lf_wind` instead: the
species says which with a flag the genome carries. Cost: zero draws.

### 4b. Banners and ceiling hangers (inside)

A pendulum from the hang point: every part -- straps, rod, cloth, art,
hem; chain and board -- displaced sideways in proportion to its height
below the hang point, a degree at most, on a period of 4 to 6 s with a
phase per node. The whole thing moves as one, so no material is split and
no draw is added. The shop's air, never `lf_wind`.

## What does NOT move, and why

- **The wood.** A trunk and its branches move so little in a breeze that
  drawing it would read as the whole tree sliding. The crown moves against
  it.
- **The grass tufts, the litter.** `weed_tuft` and `litter_scrap` are
  Lot's surface dressing: MultiMesh instances, where a node position is
  the MultiMesh's and not the instance's, and the dressing extractor bakes
  the placement into the vertices. Both are solvable (INSTANCE_ID for the
  phase, the weight is invariant) and both are deferred: a tuft is a
  hand's width and the eye reads the trees.
- **Awnings, signs on brackets, power lines.** No species builds one yet.

## How it is priced and proven

- The pixel-identical check first: crown before and after, wind zero.
- A probe on the shipped walk copy, nothing respawned: three frames half a
  second apart of a crown against the sky, of a flyer sleeve, and of a
  still control, the pixel difference printed. Frames shown.
- The harness A/B on one package, before and after, with a same-session
  control pass. Expected: zero draws moved; frame time within the spread.
- GL Compatibility runs vertex shaders and global uniforms; the probe runs
  on it.
- The gust front: two trees twenty metres apart along the wind, the time
  of their peaks read off the frames, must differ by about two seconds.

## Risks named now

- The textured reproduction. The sway shader's support set is fixed and
  small; the refusal path is tested with a material that carries a normal
  map (the wood), which must be left still and named in the import log.
- The `_vertex_colour_albedo` pass runs AFTER the replacement and only on
  standard materials, so the sway shader decides for itself whether to
  multiply the vertex colour, from the same all-white test, at replace
  time.
- Occluders: the occluder bake covers modules' meshes; whether a crown is
  in it is read before the crown moves. A crown's edge moving a few
  centimetres against a static occluder cannot show, but the number is
  looked at rather than assumed.
- A sway that is too large reads as a toy. The amplitudes above are
  starting values with their derivation written down; the walker's eye on
  the first frames sets them.
