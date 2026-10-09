## [0.70.0] - the payphone's hood lamp

Roadmap 210. Cold run 9212 stood Zoo 1.88.0's booth at a bus stop, and at
midnight it read as a silhouette: no light reached the card, the keys or the
stickers. The walker, 2026-10-09, on a backlit header and a hood lamp: "yes
light it". Zoo 1.89.0 is the other half. It hangs a tube's diffuser under the
roof, just behind the header, and `LuxEmit_payphone_hood` under it, carrying
`lux_type` and `lux_drop`, the lamp's height above the ground.

**A `payphone_hood` row** (`lux_light_loader.gd`). Without it, the marker
spawns nothing and the spawner skips it.
- **The lamp:** one cool fluorescent downlight, on the fluorescent rig's
  machinery, the way the counter accent and the heat lamp use it. A power cut
  kills it with every spawned light.
- **Its range** is a ceiling lamp's for the marker's drop:
  `fluorescent_range`, 4.0 m in a 2.3 m booth.
- **Its energy** puts `PAYPHONE_HOOD_LEVEL` on the ground under it, at any
  drop. A taller booth is no dimmer.
- **A marker with no drop** hangs at the default booth's, 2.211 m
  (`PAYPHONE_DEFAULT_DROP`).
- **Not preset scaled.** It is a street fixture, like the pole and the
  canopy, and not named "fluorescent". The night preset's
  `fluorescent_energy_scale` leaves it alone.

**`PAYPHONE_HOOD_LEVEL` = `REFERENCE_POOL` x 0.75, set from frames.**
- **The probe.** A lamp was stood live in cold run 9212's package, at
  midnight, where Zoo 1.89.0 hangs it: drop 2.211, range 4.0
  (`docs/findings/payphone_light/` at the factory root).
- **The reading.** The caller's view of the instrument, the mean luma of the
  frame's middle third:

  | level, x `REFERENCE_POOL` | the lamp mid-hood | behind the header |
  |---|---|---|
  | 0, the control | 20.6 | |
  | 0.375 | | 68.5 |
  | 0.75 | 89.2 | 94.8 |
  | 1.5 | 118.4 | 123.9 |
  | 3.0 | 146.7 | |
  | 6.0 | 170.4 | |

  - Nothing clipped at any level.
  - At 0.75 every word on the instrument reads, and the back panel's top, a
    hand's width from the tube, is pale.
  - From 1.5 the panel washes toward white, while the instrument gains less
    with each doubling.
- **So 0.75.** The pavement under a booth's tube reads as the road under a
  streetlight. That is `STREETLIGHT_LEVEL`'s ratio, reached by a different
  road. It is a separate constant, so tuning one does not move the other.
- **What the probe could not show.** Its lamp was live and unshadowed. This
  one bakes, so the booth's own parts shadow it and its walls bounce it.
  Cold run 9213 measures the residue.

**Tests.** `tools/payphone_hood_selftest.gd`:
- **the row:**
  - its range and the ground value at two drops;
  - the probe's energy, 3.0508;
  - the default drop;
  - no preset scaling;
  - the colour;
- **the marker path:** the payload in `extras`, as Zoo ships it, and a
  deduped name with no payload;
- **the power cut;**
- **the heat lamp,** untouched.

- **On 0.69.0 the new selftest fails at its first case,** "a payphone_hood
  anchor builds a rig", and exits 1.
- **All 19 selftests pass:** 18 headless, and
  `streetlight_shadow_selftest.gd` windowed, as it documents.
- **gdcheck** passes the loader and the new selftest.
