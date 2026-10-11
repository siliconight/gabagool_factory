# A hidden interactive state and its collider (roadmap 175)

**The question.** Roadmap 175 (2026-09-23) measured, on cold run 9070's
package, that every hidden `_breached` sibling of a breach wall carried a
live collider, and that a ray at two of six sampled walls hit `Breach`
rather than the brick a player sees. The item still reads OPEN. Is it?

**What the code says.** Deli Counter 0.144.0 (`319f25c2`, "a hidden
interactive state keeps its collision off") made `themed_tscn.write_themed_tscn`
write, for every hidden state whose contract says it is not solid
(`interactives._DEFAULTS`' `collision_per_state`: a breach wall's `breached`,
a door's `open`, a window's `broken`), an editable override on the instance
that sets each collision body's `collision_layer` and `collision_mask` to 0.

**What ships.** Cold run 9239's package: `lot/deli_a01/site.tscn` -- the
scene `presentation/lux.applied.tscn` instances, which `bake.tscn` instances,
which `mission.tscn` loads -- carries 9 `_breached` nodes and 9 overrides,
each `[node name="Breach" parent="<wall>_breached"]` with `collision_layer = 0`
and `collision_mask = 0`.

**What the engine says** (`breach_ray_probe.gd`, `breach_ray_9241.txt`). Run headless on the
imported copy of cold run 9241's package (the price harness's), on the same deli scene: 9
hidden `_breached` states, each `visible=false` with one collision body, `Breach`, at layer 0
and mask 0; a full-mask ray through each one's origin from 1.5 m off either side, 18 rays,
meets the visible `Wall` of the same opening or the greybox's lintel collider -- **0 of 18 hit
a hidden state.** 175 was fixed by Deli Counter 0.144.0 and nobody closed it. The closure
rests on this probe, which re-creates the measurement the item was found with -- a ray
through each hidden state's origin -- because that probe was never filed.

Not measured here: a navmesh baked from physics geometry (the item's second cost). A body at
layer 0 is invisible to any query whose mask has a bit set, which is every query the probe
could make, but the bake's own parse of the scene was not read.

## Instruments

- `breach_ray_probe.gd`: loads a building scene headless, and for every
  `_breached` node prints its visibility, the layer and mask of each
  collision body under it, and what a full-mask ray through the node's
  origin hits from either side. Needs an imported copy of a package (a
  package as exported carries no `.godot` import cache, and every GLB then
  reads as missing); the price harness's copies are imported.
