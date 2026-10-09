## [0.71.0] - street lamps are dark by day

The walker, 2026-10-09, on the light check's afternoon frames: "a good call
out is that street lamps aren't usually on during the day".

**What was there.**
- **The streetlight row had no time of day.** At an afternoon level every
  pole was baked on, and every third one cycled live, in full sun. So was
  every wall pack, which on a home is its porch light.
- **88 kept briefs are set in the afternoon,** bank_block_001 among them.
- **Nothing measured it.** At noon a sodium pool vanishes into the sunlight,
  so the light check passed those frames. It was real light, baked where
  none belongs.

**A street pole and a wall pack switch on a photocell in the world, and now
here.**
- **`LuxPreset.street_lamps_lit`** says whether a preset's sky lights them.
  It is false on the four day presets: Delco Summer Afternoon, Delco Arcade,
  SoF PC2000, and Heavy Rain, which Level Factory's `_preset_for` calls "an
  overcast DAY". It is true on dusk and night.
- **`LuxLightRig.dusk_to_dawn`:** the loader's `streetlight` and `wall_pack`
  rows set it.
- **`LuxStreetlightRig.set_lamps_lit`:** a dusk-to-dawn rig under a day
  preset is hidden, so its lamps neither draw nor bake. The lens nearest
  each lamp takes a dark copy of its material, so a dark lamp does not glow
  at noon; the material itself is untouched. A night preset relights the
  rig and puts the lens's material back.
- **`LuxLighting`** hands the preset's value to every lamp's rig when a
  preset is applied and when a lamp registers.
  - A power cut and its restore show and hide lamps, not rigs, so they
    cannot relight a dark pole.
  - `LuxRoot._lerp_preset`, exhaustive by contract, snaps the switch at a
    blend's middle.

**Where it is read.** LuxRoot applies its preset in the editor too, so the
export, the editor's bake and a re-bake under another slot all see it. A day
level bakes no street lamp.

**What stays lit by day,** as calls the walker can move: a fuel canopy (many
stand lit around the clock), a lit sign, a store's glass, a payphone, and
every room.

**Not changed:** morning and noon still fall through to Gas Station
Fluorescent, a dim forecourt whose lamps stay lit. That is LEVEL_STANDARD
section 17's gap.

**Tests.** `tools/street_lamps_selftest.gd`:
- **the presets:** the four day presets dark, the six dusk and night ones
  lit;
- **the loader:** a pole and a wall pack are dusk to dawn; a canopy wash and
  a payphone are not;
- **a day preset:** the pole and the wall pack dark, and the pole's lens
  dark through a copy, its own material unchanged. The canopy and the
  payphone stay lit;
- **a power cut and its restore** do not relight a dark pole;
- **a night preset** relights both and gives the lens its own material
  back;
- **a blend** snaps the switch at its middle.

On 0.70.0 it fails at its first case: no preset has the field.

All 20 selftests pass: 19 headless, and `streetlight_shadow_selftest.gd`
windowed, which builds the pole rig this changes. gdcheck passes all seven
changed files.
