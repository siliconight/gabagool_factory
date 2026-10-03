# Small things that move -- design, 2026-10-02

Item 3 of the "alive" queue the walker approved on 2026-10-02 (screens that
run: done, Zoo 1.45.0 / LF 0.127.0; light that is not steady: done, Lux
0.62.0). Shown before anything was built; the walker: "start with the
roller grill, and i want some motion on the slurpee stuff too".

**Status.** Steps 1 and 2 SHIPPED as Zoo 1.55.0 and Level Factory 0.129.0
(`docs/findings/moving_parts/NOTES.md` has the frames and the price).
Steps 3 and 4 (the wind: trees and flyers; pennants, banners, hangers) are
not started; their design is `WIND_DESIGN.md` beside this file. One lesson from step 1 belongs here because step 3 will meet
it: a pivot written into the vertex data at build time is stale by
whatever moves the vertices afterwards -- Zoo re-centres every module --
so the layer rides with the vertices and is converted to the engine's axes
only at export, and the test compares the pivots with the SHIPPED
vertices, not with the numbers the recipe meant.

## The rule everything below follows

**A thing moves because something drives it, and the driver is visible or
known.** The authorship guide's test: cause and specificity over uniform
polish. Two drivers exist in a level, and each thing that moves names its:

- **A motor.** The store's machines run because they are on. Their motion is
  constant, each at its own rate, and it never stops while the building has
  power (a power cut stops it: the same `fixtures_powered()` Lux 0.62.0 asks).
- **The wind.** Outside, one wind for the whole level: a direction, a
  strength, and gusts that TRAVEL across the lot. A tree, a strip of pennants
  and the loose corner of a flyer answer the same gust a moment apart,
  because it reaches them a moment apart. That shared cause is what makes it
  read as weather rather than as props jiggling.

Indoors there is no wind. A hung thing indoors moves only if the building's
air moves it, and that is a slow 1-degree drift, not a sway.

## The mechanism, and why this one

**Vertex shaders, clocked by TIME, installed at import by the worldskin,
the way the screens and shutters already are.** No node moves, no script
ticks, no AnimationPlayer, no light. The CPU cost is zero per prop, which is
the performance rule's hard line (per-frame CPU scaling with prop count is
on its refused list).

- Zoo writes WHAT MOVES AND ABOUT WHAT into the mesh: a second UV set
  (UV2) carrying the pivot or the weight, exactly as the shutters carry
  their schedule in UV and UV2 today (`core/shutters.py`, LF 0.127.0). The
  shader never guesses geometry from the vertex position; a roller knows
  its own axle and a pennant's tip knows it is a tip because Zoo said so.
  TEXCOORD_1 is proven to survive Zoo's glTF export and Godot's import
  (the shutters depend on it).
- The worldskin matches the material BY NAME (`_shutters`, `_crt_motion`
  are the pattern), replaces it with a ShaderMaterial that reproduces the
  flat kind material (albedo colour times vertex colour, roughness,
  metallic, the glow's emission where there is one) and adds the vertex
  stage. Replacement, not `next_pass`: a second pass cannot move the first.
- Per-prop phase from `NODE_POSITION_WORLD`, as the shutters and the CRT
  pass do, so two grills side by side are not in step.
- The wind is ONE global shader uniform (`lf_wind`: direction times
  strength), set once per level from the brief's weather, plus a gust
  formula every wind shader computes from TIME and its world position, so
  the gust front moves across the lot with no CPU behind it.

**Draw cost.** A part that turns separately from its body needs its own
surface, because `merge.pack_by_material` packs a kind into one mesh and
one mesh is one draw: ONE added surface per moving kind per prop. A part
whose whole mesh moves (a tree, a pennant strip, a banner) adds none.

## What moves, in the order to build it

### 1. The roller grill: the rollers turn and the dogs ride them (motor)

Both grills in the gas station have them (2 in 9139's store). Today the
rollers are `metal_bare` packed with the body, the dogs `metal_painted`
with their colour in `Wear`. They become `M_Roller_metal_bare_turn` and
`M_Roller_metal_painted_turn`, each vertex's axle (y, z) in UV2 and the
axis along x fixed by the kind. The rollers spin at a slow motor rate; a
dog turns because the rollers under it turn, so its angular speed is the
rollers' times `ROLLER_R / dog_r` -- derived, not chosen -- and in the
other sense. Cost: +2 draws a grill (+4 in this level). Priced first because
it proves the whole path: Zoo UV2 -> glTF -> worldskin -> a part turning in
a shipped level, measured by a probe that shoots three frames half a second
apart and reports the roller's silhouette moving.

### 2. The frozen drink station: the slush churns (motor)

Two in this store. The churn is already a painted tile on the barrel's glow
image, seamless left to right (`_churn`), wrapped once round the side rings
with u by segment. The shader scrolls u within that tile's rect: UV2 =
(tile u0, tile width) on the churn facets, (0, 0) everywhere else, so the
rest of the image stays put. Each flavour at its own rate, the red and the
blue not in step. Cost: zero draws, zero geometry.

### 3. The wind, outside: trees and the flyers on the poles

Both are in this level (one London plane species on the lot; three flyer
sleeves). The tree's leaf clusters sway with the gust, weighted by height
(UV2.x = the cluster's height over the trunk base, written by the tree
builder), with a small faster flutter on the cluster facets; the trunk and
branches do not move, so the crown moves against a fixed trunk, which is
what a tree does. A flyer's free lower corners lift a centimetre on a gust
(UV2.x = flap weight, 1 at the loose corner, 0 at the staple). Cost: zero
draws. The wind's direction and strength come from the brief's weather
(Lux already reads rain from it); calm briefs get a breath, not a wind.

### 4. The wind, where a level has them: pennants, banners, hangers

`pennant_row` (tips flutter, hoist pinned: weight = distance below the
hoist over the length), `hanging_banner` and `ceiling_hanger` (indoors: a
slow 1-degree pendulum from the chain top, pivot in UV2). None are in the
gas station; they ship with the species and are measured on the first
brief that places them. Cost: zero draws.

## What does NOT move, and why

- **Roof fans.** `exhaust_fan` is a mushroom (curb, drum, dome) and
  `hvac_unit` a cowl: neither has a visible blade, so spinning them shows
  nothing. A visible blade behind a louvre is a species change, and a
  separate call.
- **Security cameras, traffic signals, cars.** Item 4 (a world that changes
  on its own) and gameplay-adjacent; designs shown separately.
- **The cooler doors, the register drawer, the ATM.** They move when a
  player uses them or never; idle motion on them would be noise.
- **Item 2's residue.** "Light that is not steady" shipped as failing
  fixtures; the neon letter that drops out and the pump price's shimmer
  from the same item are NOT done and are not in this design either. They
  belong to the sign and the pylon as surface motion, and are queued behind
  this.

## How it is priced and proven

- The harness A/B on one package, before and after, with a same-bytes
  control pass, in one session (the lesson of cold run 9139: the instrument
  wanders 0.3-0.5 ms between sessions). Draws per view, median and p95.
- A probe on the shipped walk copy, nothing respawned: three frames half a
  second apart of each moving thing, and the pixel difference between them
  printed, so motion in the level is a number rather than a claim.
- GL Compatibility is the target and runs vertex shaders and global
  uniforms; the probe runs on it.
- Each step ships on its own Zoo version with its own frames shown before
  the next starts.

## Risks named now

- `merge.pack_by_material` refuses to pack parts whose UV layers differ, so
  every part of a moving kind carries UV2 or the kind splits into more
  draws than counted. The census test (`tests/`) holds the count.
- A swaying crown against a baked occluder: trees are collision at the
  trunk only; whether the occluder bake includes the crown is checked before
  the tree moves, not after.
- The replacement shader must reproduce the kind material exactly; the
  first frame pair (before/after, no motion) is compared pixel-for-pixel
  before any motion is added.
