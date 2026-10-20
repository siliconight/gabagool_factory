---
name: light-tools-breakdown-and-check
description: "tools/light_breakdown.py (what a frame is lit by), tools/light_check.py (rooms + street held to named floors, day and night via re-bake), tools/lux_rebake.py (exact re-bake under any preset/field); club_block_014 midnight: moon carries outside, fills carry rooms"
metadata:
  node_type: memory
  type: reference
  originSessionId: 27f14f8b-7ce5-44c0-a704-178a824035d7
  modified: 2026-10-09T20:13:03.787Z
---

Built 2026-10-09 at the walker's asks: "build that light breakdown
instrument" and "a tool that can make sure levels look good in both
interiors and exteriors for both day and night lighting".

**The tools, all at the factory root:**
- **`tools/light_breakdown.py`:** each light source switched off in turn,
  via look_shots' `--switch-off` (lightmap, live, sun, ambient, probes,
  emission, sky, fog).
  - `--also a+b` switches several together.
  - `--fills` re-bakes with the room fills on and off.
- **`tools/light_check.py`:** one station a room (the night census's
  derivation) plus the street and facade cameras, held to named floors:
  - a ROW room p50 >= 10, a MOODY room 5 (provisional), a DEN exempt;
  - the street p50 > 1 and near-clip <= 5%;
  - a facade's p95 >= 10;
  - by day, the street over the shop.
  - Other slots are re-baked.
- **`tools/lux_rebake.py`:** Level Factory's own bake on a copy, under any
  preset (`--preset`), any preset field (`--set street_lamps_lit=true`) or
  no fills. **It reproduces a shipped bake exactly**, 0.0 at every camera.
  - `--bake-environment scene` bakes with the sky. Level Factory's own is
    `0`, no sky; see [[lighting-spec-filed]].
- **`docs/findings/lighting_spec_vs_lux/compare_checks.py`:** two or more
  light-check reports of one level, station by station.

**What the first runs found** (cold run 9213, club_block_014, midnight):
- **Outside, the moon (`LuxSun`) carries the facades:** 17.4 to 1.6 without
  it.
- **The environment's ambient moves nothing on baked surfaces.**
- **Lit rooms are mostly the bake-only fills** (25.2 of a room's 26.0).
  Lamp-less concrete rooms bake black.
- **The light check:** at midnight the airport terminal's check-in hall
  fails (p50 8) and the north facade warns; the afternoon re-bake passes.
- Findings: `docs/findings/light_breakdown/`, `docs/findings/light_check/`.

**How to apply:**
- **A drop is not a share.** Every number is luma after the tonemap and
  post, so a source's drop says how much darker the frame got, not how much
  of the light it gave. Rankings and "black without it" hold. The README
  carries the correction (2026-10-09, from [[lighting-spec-filed]]).
- **`-lightmap` alone is a trap.** Clearing the lightmap lets real-time
  ambient and probes in, and rooms got BRIGHTER. Isolate the bake with
  `-ambient+probes` less `-lightmap+ambient+probes`.
- **Judge an elevation by its whole frame's p95.** Its centre third is sky.
- **A re-bake uses the package's vendored Lux,** so test a Lux change with
  a fresh export, not a re-bake of an old package.

See [[street-lamps-dark-by-day]], [[interiors-must-read-at-night]] and
[[levels-have-five-times-of-day]].
