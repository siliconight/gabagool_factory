## [0.66.0] - a baked level's lightmap follows the level's state

Roadmap item 31's probe baked the gas station lot's steady lights with
Godot 4.7's LightmapGI and priced it on a quiet machine: -0.8 ms median
frame (-16 %), -0.45 ms GPU, controls 0.04-0.10 ms, the heaviest views ~3 ms
faster (`docs/findings/light_bake/NOTES.md`). A baked light's effect on the
level is fixed in the lightmap, and a static light no longer lights the
lightmapped surfaces in real time, so two things Lux offers at runtime
would draw a wrong picture over a lightmap. This release keeps both
honest.

THE POWER CUT. `set_fixtures_powered(false)` hides every rig lamp; the
lightmap now goes off with them and comes back when the power does.
Measured on the baked lot in GL Compatibility: lightmap off and lamps
hidden read 0.120 overhead (2,401 draws) against 0.154 lit.

A PRESET OTHER THAN THE BAKED ONE falls back to real time:
`LuxLighting.set_baked_lighting(false)` clears the lightmap, turns every
static rig light dynamic, and re-adds each (hidden and shown again).
Measured: 3,253 draws and the never-baked build's luminance at three
stations, against that build's 3,252. Clearing the lightmap alone, or
flipping the bake mode alone, left the static lights excluded from the
surfaces the lightmap had covered -- 2,614 draws and a darker level -- so
the re-add is the step that works, and is written down where it is done.
"Other" is by identity: the preset in force when the lightmap was bound is
the baked one; weather, time of day and a mission phase build new presets
and fall back; a quality change re-applies the same one and does not.

`LuxRoot` binds every LightmapGI with data in the level's scene, deferred
after ready, and prints how many. `LuxRoot.baked_lighting()` and
`set_baked_lighting(on)` are public, and `LuxRuntimeAPI.baked_lighting(tree,
on)` is the consumer's call; turning baked lighting on under a preset other
than the baked one is refused with a warning. A level with no lightmap is
untouched.

`tools/lightmap_switch_selftest.gd` (headless) holds the states: bound after
ready; the cut and the restore; real time and back; a cut in real time; a
foreign preset falls back and refuses the switch; a level with no lightmap.
What the states look like is measured on the baked lot, not here.

