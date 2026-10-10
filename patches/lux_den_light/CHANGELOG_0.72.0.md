## [0.72.0] - a den is lit at its walls, and in its own colour

The walker, 2026-10-09, walking club_block_014's strip club at midnight
(cold run 9213): "strip club is still a tad too dark... still be dark and
moody, but lit enough for a player to see and experience it". Their comps,
read for format only:
- a VtMB bar, the Asylum's hall and a KOTOR 2 cantina;
- a median luma of 15 to 39, with 19 to 40% of each frame under 10.

The club measured a median of 1, with 98% of the frame under 10.

**Why it was dark,** measured on cold run 9217's walk copy (the factory
root's `docs/findings/club_light_trials/`):
- **The club's light was almost all baked:** the main floor's frame mean is
  3.7, and 1.6 with the bake switched off. 0.68.2 lays no fill in a den.
- **Its carpet's albedo is 0.036 linear,** so the washes' pools land on
  black.
- **Its ceiling is the office tile, at 0.545.** So anything that throws
  light up lights the ceiling. The stage lip's and the back bar's omnis made
  the only bright pools in the room, overhead.
- **Neither lever alone got there.** A white den fill at the bulb share
  reached a median of 3. The washes' stored energies at x3 reached 1.

**What the comps do, and what a den's bake now does:** coloured washes on
the walls, and a room whose ceiling and floor carry its colour. Both are laid
by `add_bake_fills` and freed with the room fills before the save, so a level
carries nothing of them at run time: no node, no per-mesh light.
- **Washers on every wall** of a tinted den room (`_lay_den_washers`):
  - about every `DEN_WASH_PITCH_M` (3 m), 0.8 m in from the wall and 0.25 m
    under the ceiling;
  - each aimed at the wall 1.0 m over the floor;
  - each in the colour of the nearest club wash in the room;
  - each putting `DEN_WASH_LEVEL` (2.34) x `REFERENCE_POOL` on the wall at
    its aim point.
- **A fill in the room's own colour**, at `DEN_FILL_SHARE` (2.0) of the
  preset's room fill. A white fill was tried first and refused on the
  frames: it turned the office tile overhead into a grey grid, and the club
  read as a hall.
- **The den's untinted back rooms are filled white** at `DEN_BACK_SHARE`,
  the bulb rooms' 0.5. At a full share, 0.68.0 made strip_club_a02's back
  rooms the brightest room in a level (52.3), and the walker kept dens dark
  after it.

**The trials** were re-bakes of 9217's walk copy, measured at light_check's
room stations (mean / p50, luma of 255, Delco Night). The "washers" figure
is what one washer puts on the wall, in units of `REFERENCE_POOL`:

| variant | main floor | VIP wing | cash office | objective |
|---|---|---|---|---|
| 0.71.0 | 3.7 / 1 | 2.2 / 0 | 2.6 / 1 | 1.2 / 0 |
| white fill 0.5, no washers | 7.5 / 3 | 4.6 / 1 | 6.7 / 3 | 4.7 / 2 |
| washers 1.56 | 6.9 / 2 | 7.9 / 2 | 2.7 / 1 | 1.7 / 1 |
| washers 3.12 | 9.4 / 3 | 12.6 / 4 | 2.8 / 1 | 2.2 / 1 |
| washers 1.56, white fill 2 | 24.9 / 11 | 21.3 / 8 | 23.1 / 20 | 21.4 / 22 |
| washers 1.56, tinted fill 2 | 13.2 / 7 | 10.5 / 5 | 23.0 / 20 | 21.2 / 21 |
| washers 2.34, tinted fill 2 | 14.5 / 8 | 13.0 / 7 | 23.1 / 20 | 21.5 / 22 |
| washers 2.34, tinted fill 4 | 21.3 / 10 | 15.2 / 9 | 41.3 / 40 | 38.5 / 42 |
| **0.72.0, this loader baked** | **14.5 / 8** | **13.0 / 7** | **6.9 / 3** | **5.7 / 3** |

- **The back rooms in the trials** were filled white at the same share as
  the club floor. 0.72.0 gives them 0.5.
- **0.72.0's own row** is the release's loader, vendored into a copy of the
  walk project and baked by Level Factory's own bake
  (`club_light_trials/loader_trial.py`).
- **Chosen:** washers 2.34 with a tinted fill at 2, against the frames. The
  club reads as coloured walls over dark furniture, with an amber or pink
  ceiling.
- **The fill at 4** is brighter (main floor p50 10) and shows more of the
  office grid overhead. It is the walker's call; the frames are in the
  findings.
- **RETRACTED, kept: the trials' "wall level".** It took the cosine of
  incidence as the ray's vertical share, which is 2.56x too large. Their
  energies were exact. The levels above are re-derived with the cosine the
  wall's normal gives, and `_lay_den_washers` solves that way.

**Still open, and not this release's:**
- the club's ceiling is the office tile, which Deli Counter's
  `dress_club_rooms` never sets;
- the washers have no hardware over them;
- `light_check` exempts DEN rooms. Its floor is the walker's call.

**Tests.** `tools/den_light_selftest.gd`, new:
- the constants;
- a den's tinted room filled 2 x 2 in its own colour at `DEN_FILL_SHARE`;
- its back room filled once, white, at the bulb share;
- an ordinary building beside it filled at share 1;
- 14 washers on a 12 x 9 m room and none in the back room or the office.
  Every washer is inside the room under its ceiling, static, owned, and
  aimed down at the wall it stands in from;
- each wall's washers take their nearest wash's colour, red and cyan;
- a washer puts `DEN_WASH_LEVEL x REFERENCE_POOL` on the wall by the closed
  form;
- a second call replaces the first.

On 0.71.0 it fails at its first case: the loader has no `DEN_WASH_LEVEL`.

`tools/bake_fill_selftest.gd` now holds a den filled: its four checks of
"none" became 4, 2 and 23.

**The suite:** 20 of 21 selftests pass, `den_light_selftest` among them.
- **The 21st fails, and not because of this release.** The windowed
  `streetlight_shadow_selftest` fails its on-axis control, "the cap blacks
  the pool: false".
- **0.71.0 fails it the same way,** run alone with the GPU idle on
  2026-10-10. Its other control, a slab under the lamp, passes, so shadows
  draw.
- **0.71.0's own record has all 20 passing.** So the machine's environment
  moved, not this code, which touches neither the pole nor shadows.
- It is filed as roadmap 222.

gdcheck passes the three changed files.
