---
name: street-lamps-dark-by-day
description: "Walker 2026-10-09: street lamps aren't on by day -> Lux 0.71.0 (poles + wall packs dark under day presets, lens too); PROVEN in cold 9214: a hidden lamp is not baked; at stations lamps add <=0.2, close up a wall pack +16-22"
metadata:
  node_type: memory
  type: project
  originSessionId: 27f14f8b-7ce5-44c0-a704-178a824035d7
  modified: 2026-10-09T20:12:29.657Z
---

The walker, 2026-10-09, on the light check's afternoon frames: "a good call
out is that street lamps aren't usually on during the day".

**Shipped: Lux 0.71.0.**
- **`LuxPreset.street_lamps_lit`** is false on the four day presets: Delco
  Summer Afternoon, Delco Arcade, SoF PC2000, and Heavy Rain, "an overcast
  DAY".
- **`LuxLightRig.dusk_to_dawn`** is set by the `streetlight` and `wall_pack`
  rows. A wall pack on a home is its porch light.
- **`LuxStreetlightRig.set_lamps_lit`** hides the rig and darkens its lens.
- `tools/street_lamps_selftest.gd`.

**Proven in cold run 9214** (0 interventions, 1 retry), bank_block_001. Its
brief is afternoon with rain, so it ships under Heavy Rain.
- **A hidden lamp is not baked.** Wall pack 002 is a baked rig, and its
  light is absent from the shipped lightmap: wall 32.5 against 48.0, sidewalk
  62.3 against 84.2 with the lamps forced on.
- **At the light check's 23 stations the lamps change nothing,** 0.2 or
  less. A daylit street hides a lamp, as the lighting spec says.
- **A pole's head** reads 75.4 against 98.2.
- Sheet: `docs/cold_runs/cold_9214/street_lamps_by_day.png`, sent to the
  walker.

**How to apply:**
- **What stays lit by day is my call, and the walker can move it:** a fuel
  canopy (many stand lit around the clock), lit signs, store glass, the
  payphone, every room.
- **Every wall pack is outside over an exterior door:** 389 of 389, all
  derived (`docs/findings/lighting_spec_vs_lux/wall_pack_census.py`). So the
  spec's warning, that a day switch must spare lamps in shade or indoors,
  does not bite.
- **Morning and noon still fall through to Gas Station Fluorescent,** a dim
  preset whose lamps stay lit. That is LEVEL_STANDARD section 17's gap.

See [[light-tools-breakdown-and-check]], [[lighting-spec-filed]] and
[[levels-have-five-times-of-day]].
