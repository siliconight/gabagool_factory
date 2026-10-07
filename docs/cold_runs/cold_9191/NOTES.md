# Cold run 9191 -- 0 interventions; a brief that asks for a "deli" gets a dressed deli

A never-seen one-building brief, `deli_001`, whose archetype is the plain
word `deli`. That word was refused until Level Factory 0.150.0. One building
means no lot library, so the deli is GENERATED from Deli Counter's
`corner_deli` recipe through `presets.make`. It is the first cold run of a
generated corner deli.

**Every leg ran, `INTERVENTIONS: 0`, and the package exported.**
- **Plan:** `deli` resolved to `corner_deli` and nothing refused.
- **Shell:** three distinct candidates. All three were "out" on Laser Tag's
  `LT_MAP_ENEMY_PATHING_BROKEN`, so the driver took the fewest major
  findings, seed_9191. That is an automated choice, not an intervention, and
  is reported below.
- **Findings: 58** on deli_001. The driver's "0 -> 58" diffs against 9190's
  different mission, so it is a count, not a change.
- **Bake:** 1,855 users, 49.6 s.

## The generated deli, in the package

Read in the `presentation_compose` job's composed shell
(`out/presentation/site.tscn`). `art.log` carries no `ZOO_PARTIAL_BUILD`.
- **The case:** `deli_case_cover` instances
  `prop_deli_case_delco_1997_03_w582_d110_h130_mglass` at x -11.0925.
  `presets.make` trimmed the recipe's 7.0 m case off its own wall (Deli
  Counter 0.199.0), and it builds as Zoo 1.81.0's species (0.200.0).
- **The window** (Deli Counter 0.201.0):
  - `window_sign` is `prop_neon_sign_delco_1997_06_w120_d6_h60_fwindow_n1` at
    (0, 1.95, 13.755);
  - `window_poster` is `prop_poster_wall_delco_1997_07_w100_d1_h60_fstore` at
    (-0.25, 1.25, 13.79).
  - Both are in the S wall's window, building frame, Godot axes.

**Frames** (`tools/look_shots.py` on this run's walk copy,
`_runs/walk_export_deli_001`). Its shell scene is byte-identical to the
export. The shell stands at site (6, 0, 0), unturned.

| frame | station (eye -> target) | mean luminance (/255) |
|---|---|---|
| `frame_9191_window_street.jpg` | (6.0, 1.6, 21.0) -> (6.0, 1.5, 14.0) | 53.6 |
| `frame_9191_front_three_quarter.jpg` | (-1.0, 1.7, 23.0) -> (2.5, 1.6, 14.0) | 43.0 |
| `frame_9191_case_front.jpg` | (-5.09, 1.6, 4.6) -> (-5.09, 0.85, 1.2) | 15.0 |

**What they show.**
- **From the street:** the band and the door box both say WOODER ICE &
  HOAGIES, dealt from Pixelcoat's deli family, one business a shell (Level
  Factory 0.148.0). In the window, the JAWN LITE neon hangs high and two
  sale posters are taped low, shifted toward the door.
  - **The neon reads faint behind the pane.** Whether it should glow
    brighter is the walker's to judge.
- **Inside:** the case's deck glows on the customer floor.
  - A store poster board hangs in mid-air at the frame's edge. That is the
    defect in `docs/findings/wall_pieces_without_walls/`: furnish stands wall
    pieces against open room edges. The generated recipe does it too.

## Laser Tag: enemies jam behind the deli

All three candidates fail `ENEMY_PATHING_BROKEN`.
- **seed_9191:** WARN 70, route completion 1.0, 19 timeouts in 25 runs.
  177 enemy-stuck events, 1.18 per enemy per run.
- **seed_9292:** WARN 70, 20 timeouts, 192 stuck.

**Where.** 165 of seed_9191's 177 stuck events stand at one spot, site
(18-20, 0, -15). In the building's frame that is x 12-14, y +15 (spec axes):
1 m outside the north wall, at and just east of the recipe's
`rear_staff_entry` door (pos 0.32, x 12.0 as cut, **1.1 m wide**).
- All six enemies jam there, the first at t 6.07 s.
- The site stands only `path_2` there, the walk Lot lays to that door.

**Refuted, kept.** A first look found a floor safe (`safe_floor_r365b5162_1`)
flush against the north wall inside the door's span. It belongs to the
**basement** vault (storey -1). The filter took pieces by plan position
without asking their storey. Nothing stands inside the door on the ground
floor.

**Not established: why they jam.** Measured, not explained:
- The door is 1.1 m against the contract's 1.25 m (`min_door_width`).
- Library deli_a01 has no rear door, and 0 enemy-stuck events in 9190.
- 9190's deli_a03, whose rear door is 1.4 m, had 36.

The navmesh through that door is the next thing to read.

## Open, after this run

1. **The generated deli's rear door, where enemies jam.** Bake the walk
   copy's site and read the navmesh through the door before changing the
   recipe.
2. **Furnish's wall pieces on open edges**, in the generated deli as in the
   library (155 pieces in 18 shells).
3. The window neon's brightness: the walker's call.
