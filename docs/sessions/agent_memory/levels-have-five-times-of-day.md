---
name: levels-have-five-times-of-day
description: "Walker 2026-10-07: every level is set at one of five times (morning, high noon, afternoon, evening, midnight); the sky and the light levels should follow that slot"
metadata:
  node_type: memory
  type: project
  originSessionId: 27f14f8b-7ce5-44c0-a704-178a824035d7
  modified: 2026-10-07T12:35:23.790Z
---

The walker, 2026-10-07, mid-way through the night-interiors work: "levels will
either be at morning, high noon, afternoon, evening, midnight...so we can
start to associate the skybox (sun/moon cycle) with the intensity of the
lighting?"

**Why:** a level never changes its time of day, so one bake per level can be
baked for its slot, and every light level can be a property of the slot.

**What existed on 2026-10-07:**
- `MissionBrief.time_of_day` picks the Lux preset in Level Factory's
  `_preset_for` (apps/cli/commands): night -> Delco Night, evening -> Blue
  Hour, afternoon -> Delco Summer Afternoon. Anything else, morning and noon
  included, falls through to Gas Station Fluorescent. Rain overrides all of
  them with Heavy Rain.
- The preset owns the sun, the sky, the skybox (sky provider), the ambient and
  `fluorescent_energy_scale` (Blue Hour 3.7, Delco Night 6.0).
- **Window light has no dial.** Every window spot ships at energy 3.0 in all
  29 retained walk copies, midnight ones included.
- The walk copy's N key cycles skyboxes only. It moves no light.

**How to apply:** treat a level's light levels as a function of its slot.
Interior floor, window light and fixture strength live on the preset, and
the bake is baked for that slot. Dens of sin keep their own dim, coloured look
at every slot ([[interiors-must-read-at-night]]). Price every new look
([[performance-beats-graphics]]).
