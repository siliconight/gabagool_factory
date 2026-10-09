# The light check, first run: club_block_014 at midnight and in the afternoon (cold run 9213)

**Question.** The walker, 2026-10-09: "a tool that can make sure levels look
good in both interiors and exteriors for both day and night lighting".
`tools/light_check.py` is that tool. This is its first run, on cold run
9213's walk copy, as shipped (Delco Night) and re-baked under the afternoon's
preset.

**What it holds.** The floor under "looks good" that a number can hold:
- a room a person can read;
- a street that has not collapsed to black;
- a frame that has not blown to white;
- by day, the street outshining the shop.

It does not judge whether a level looks designed (roadmap 18). The targets,
each with its source, are in the tool's docstring. Two are PROVISIONAL: the
moody rooms' floor and the day's interior floor.

**Stations.**
- **Inside, one a room:** the night census's derivation, from Deli
  Counter's room lists. 11 rooms in 3 buildings.
- **Dens of sin:** the strip club is one, read from its tinted room probes:
  orange on the main floor, pink in the VIP wing.
- **Outside:** look_shots' derived cameras. The objective stands inside the
  club, so it is judged as a den.
- **Not judged:** the rowhome Empties have no room list. They are shut and
  dark by design.

## What it found

| | midnight, as shipped | afternoon, re-baked |
|---|---|---|
| FAIL | 1 | 0 |
| WARN | 1 | 0 |
| PASS | 12 | 14 |
| EXEMPT (dens) | 4 | 4 |
| the street's median | 38.3 | 101.7 |

**At midnight:**
- **FAIL: the airport terminal's check-in hall,** a fluorescent room, p50 8
  against the floor of 10. A 54 x 21.6 m hall with a dark carpet, its far
  doorway the brightest thing in frame (`sheets/midnight_as_shipped.png`).
- **WARN: the north elevation.** Nothing on it reaches the floor: p95 3, a
  row of facades black but for a few lit windows. The light breakdown
  measured what carries the others: the moon lights the south and west
  facades, and nothing replaces it on the far side. The environment's
  ambient reaches no baked surface (`docs/findings/light_breakdown/`).
- **Every other room reads,** p50 12 to 48, and so do the street cameras,
  22 and 24.

**In the afternoon** (Delco Summer Afternoon, re-baked: 172 fills, 82 s in
the editor):
- **every room passes,** p50 38 to 62;
- **every room is under the street's median,** so the day's inversion holds;
- **nothing is blown:** near-clip 0.28% at most, the crematory wing;
- **the dens read at 17 to 24 by day.** Exempt either way.

**Not verdicts, for the eye** (`sheets/afternoon_rebaked.png`):
- the afternoon's rooms light an even grey;
- the east elevation's sky has a bright streak.

## Retracted, kept: the first facade rule

The first version judged a facade by its frame's centre p50, and all four
elevations warned. An elevation frames the street orthographically, with the
buildings along the bottom, so its centre third is sky: centre p95 3 on all
four. The whole frame's p95 tells them apart: north 3, east 17, south 92,
west 85. The rule is now "nothing on the facade reaches the ROW floor", and
only the north one warns.

## Records beside this README

- **The run:**
  - `light_check.txt` (the verdicts as printed), `light_check.json` and
    `light_check.log`;
  - `own.json` and `afternoon.json`: look_shots' manifests. Their PNG paths
    point into `_runs/`, which is not kept.
- **Sheets:** `sheets/midnight_as_shipped.png` and
  `sheets/afternoon_rebaked.png`, every station's frame labelled with its
  verdict.

The command, as run (its default slots: own, night, afternoon; night is the
level's own preset, so it is the shipped bake):

    python tools/light_check.py _runs/walk_export_club_block_014 --out _runs/light_check_9213
