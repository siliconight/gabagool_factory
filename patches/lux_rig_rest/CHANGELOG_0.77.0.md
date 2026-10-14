## [0.77.0] - a rig at rest before its scene is packed

**The factory's roadmap 247.** Two cold runs of one command built Lux's applied scene with eleven lights' energies
apart. Measured in the factory (`docs/findings/roofprops_bytes/lux_energy_pairs.py`: urban_row_001's
`presentation/lux.applied.tscn` over cold runs 9295 to 9300, Godot's per-save ids masked):
- the same ten lights' `light_energy` differ in every pair, by about one part in 10,000: seven flickering
  `Spawned_pendant_*` fluoros, and three streetlights (`site_pole_43`, `site_pole_53`, `site_lamp_78`);
- a failing tube, `Spawned_fluorescent_038_dup2`, reads 2.618 in four runs and 3.7 in two.

**Why.** The fluorescent and streetlight rigs animate a failing or flickering lamp from their own clocks (`_fail_t`,
`_flicker_phase`) whenever they process, and the stage light cycles its colours on `_t`. The factory's Lux apply
(`run_lux_apply.gd`) awaits seven frames before it packs the scene, each with a wall-clock `delta`. So the clocks
reach a different moment every run, and `pack()` saves the lamps there. The values are already apart in the Lux
apply job's own output, before the light bake touches the scene.

**What changes:**
- **`rest()` on `LuxFluorescentRig`, `LuxStreetlightRig` and `LuxStageLightRig`.**
  - Every lamp goes back to what its rebuild gave it: `rig.energy * energy_scale`, `rig.energy`, or the colour a
    cycle starts in.
  - A failing lens goes back to its own glow while the fixtures are powered.
  - Every clock goes to zero.
- **Nothing here calls it; the packer does.** The factory's Level Factory 0.208.0 rests every rig in
  `lux_light_rig` before it packs. At run time the rigs animate from zero, as they always did.
- **A dark dusk-to-dawn rig stays dark.** Its switch is `visible` and its lenses' dark copies, which `rest()` does
  not touch.
- **`tools/rig_rest_selftest.gd`:** fails on 0.76.1 on its four `rest()` checks -- the failing tube, the flickering row, the cycling pole and the cycling stage light each answers none -- while its driven cases pass there: the tube in a drop at 0.61 of its energy, the pole in its cycle's dark at 15.0 of 30, the stage lamp turned half way to its next colour. All 24 checks pass on 0.77.0. Headless, after an import pass.
- **The other self-tests:** the other 24 in `tools/` exit 0 on 0.76.1 and on 0.77.0 alike, each run as its docstring says (`streetlight_shadow_selftest.gd` windowed on GL Compatibility, the rest headless), on copies of the repo after an import pass.
