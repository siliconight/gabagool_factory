---
name: lighting-spec-filed
description: "Walker's Godot 4.7 natural+artificial lighting spec, filed 2026-10-09 in docs/reference; compared to Lux in docs/findings/lighting_spec_vs_lux/: the bake has no sky (environment_mode 0), night boosts fluorescents (scale 1.0 day, 6.0 night), luma isn't additive"
metadata:
  node_type: memory
  type: reference
  originSessionId: 27f14f8b-7ce5-44c0-a704-178a824035d7
  modified: 2026-10-09T20:46:55.101Z
---

The walker handed over a lighting spec on 2026-10-09 ("this could help Lux
and you?"). It is filed verbatim at
`docs/reference/Godot_4_7_Natural_and_Artificial_Lighting_Spec.md`, 41,663
bytes. The comparison with the code is `docs/findings/lighting_spec_vs_lux/`.

**Its core claim:** a lamp's output stays fixed. Its prominence changes
because the light around it changes and the camera adapts. The model is
`E = sun + sky + bounce + lamps`, added before display mapping.

**What it matched in the code:**
- **A dusk-to-dawn sensor is a legitimate schedule.** That is Lux 0.71.0.
- **A baked light does not follow the sun.** We bake per slot.
- **On Compatibility, the tool set is** lightmap, probes and authored fills.
- **Every fixture row uses attenuation 2.** The exceptions are the fills (0,
  flat by design) and the heat lamp (0.6).

**What it showed:**
1. **Level Factory bakes with no sky.** `light_bake.py:113` sets
   `environment_mode = 0`, which came with 0.131.0 and no recorded reason,
   and a lightmapped surface takes no ambient. Test it with
   `tools/lux_rebake.py --bake-environment scene`. Under Heavy Rain (cold run
   9214) the sky added +0.3 to +2.3 outdoors and 0 indoors.
2. **Fluorescent rigs scale with the slot:** 1.0 in Delco Summer Afternoon,
   1.7 in SoF PC2000, 3.7 at Blue Hour, 4.3 in Heavy Rain, 5.0 in Mission
   Goes Hot, 5.7 at the Gas Station, 6.0 at night.
   - The spec calls brightening lamps as the sun dims a "don't".
   - Bulbs are exempt by the walker's call of 2026-09-28
     (`lux_fluorescent_rig.gd`, `scales_with_preset`).
   - Street lamps, wall packs and the payphone hood do not scale.
   - Whether the boost should live in the lamps at all is the walker's call.
3. **The light breakdown's drops are not shares.** Luma is measured after
   the tonemap and post. Its README carries the correction.

**Measured on 9214's level** (roadmap 217):
- **The sky in the bake.**
  - On a clear afternoon the street rises +15 to +21, and shade goes from
    near black to daylight.
  - Under Heavy Rain it adds +0.3 to +2.3, at Blue Hour +0.5 to +3.7, and at
    night +3.3 and +4.4 on two facades.
  - Rooms move 1.2 or less in every slot, and the bake time does not move.
  - Recommended to the walker.
- **Heavy Rain's rooms outshine the street** (12 of 16). The cause is its
  sun, which casts no shadow.
  - That was Lux 0.38.0's recorded trade on price (`lux_preset.gd`): +3.2
    to +8.1 ms, measured on cold run 9054.
  - With the shadow on, the rooms fall 5.6 to 31.6.
  - The free lever, a cull-mask split, is unbuilt.
  - The fluorescent boost is not the cause.

**How to apply:**
- **Before calling a look a defect, grep the preset's own comments.** The
  Heavy Rain leak was written down a month ago.
- **Re-price old perf refusals.** The bake and the merges have since cut
  what a shadow pass re-draws.

See [[light-tools-breakdown-and-check]] and [[street-lamps-dark-by-day]].
