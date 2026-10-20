# What a facade is made of, measured (roadmap 79, with 74 and 76), 2026-10-20

**What was asked.** Roadmap 79 says nothing in the pipeline represents a facade: `_emit_wall_run` sees one face of one
storey, so the storeys cannot align, the entrance is one opening in a list, and every width that was not a module is
a remainder. It quotes a critique of a walk and gives each bullet a line number, and no number. This counts each
bullet that placement can answer, on the library a themed lot draws from, before a planner is proposed
(`docs/proposals/FACADE_PLANNER.md`). It serves the "good" gate (roadmap 18), not interventions-per-level.

**What was read.** Deli Counter 0.237.0's built library (`deli_counter/build/<id>.slots.json`, the slot records the
art pass swaps, and `<id>.gameplay.json` for the openings' tags), its specs through `spec_loader.load_spec`, and Level
Factory 0.222.0's own `building_library.index` and `themed_report` for the themed pool: 102 of the 127 indexed
buildings, all enterable. The Empties (27, `facade` true) are drawn by their own rows, not the pool, and are reported
apart. Frame: building-local, Blender Z-up, metres; a face is one side over every storey at or above grade; along a
face `u` is the slot's own x (N, S) or y (E, W). `TOL` 0.05 m: openings stand on the spec's 0.5 m grid, so two
centres within it are the same grid point.

## The census (`census.py`; `census.out.txt`, `census.json`)

| group | buildings | multi-storey | stacked, ground -> first | stacked, above | joints continuing | remainder |
|---|---|---|---|---|---|---|
| themed pool (enterable) | 102 | 52 | **28 of 169 (16.6 %)** | 3 of 3 (office only) | 41.4 % | 8.2 % |
| Empties (their presets compose bays) | 27 | 27 | 92.9 % | 100 % | 96.9 % | 35.4 % |
| outside the pool, enterable | 29 | 11 | 22.8 % | - | 33.9 % | 12.1 % |

- **Stacking:** of the first storey's openings, the share with a ground-floor opening under it. In the pool 28 of
  169. **The Empties are the instrument's control:** `empty_rowhome` and `empty_midrise` lay every storey on one
  list of bay positions (`presets.py`, `MIDRISE_BAY` 3.2), and the census reads them at 92.9 % -- it can see
  stacking where it is. The 7 % it misses there is the twelve rowhomes' rear faces, where the preset puts the back
  door in one of the house's two bays and the window above in the other (`back = [dict(win, pos=-door)]`): both on
  the bays, not over each other.
  An example of what 16.6 % looks like: bank_branch_a04's south face has a centred 2.2 m main door between windows at
  -12 and +12 m, and upstairs two windows at -10 and +10.
- **Within a storey the rhythm is already regular:** 43 of the 62 runs with three or more openings space them with
  a coefficient of variation under 0.05 (median 0.00). The irregularity is between storeys, and between the
  openings and their face, not along a run.
- **Joints:** of the joints between pieces on a storey, the share that continue a joint on the storey below. **What
  this describes is not what delco shows.** The delco wall style draws no relief (`zoo/zoo_keeper/genome/species/
  wall.json`, `"relief": {"reveal": 0.0}`, Zoo 0.51.0), so its modules are flush panels with world-space UVs and a
  3 mm bevel, and a joint is a faint line at most. A theme with relief draws a pier at every joint. In delco what
  reads is where the openings are.
- **Remainder:** the share of solid wall that is a tiling remainder (`size_mod` "end", corner posts left out; a last
  module that absorbed a sliver counts only its excess). 8.2 % in the pool, in **69 distinct widths**, the
  commonest 1.700 m (61), 0.150 (44), 0.225 (42), 1.725 (39), 1.150 (39). The Empties' 35.4 % is a warning about the
  number itself: their piers are remainders to the tiler and chosen widths to the preset, the same on every storey.
  A remainder is only unchosen when nothing upstream sized it.
- **The entrance:** 63 of the 102 tag no door `main...` or `front...` (their doors are `entry_w`, `crew_n`,
  `service_entry` and the like); of the 39 that do, **31 make it wider than every other exterior door**, 11 stand it
  on its face's centre (within 5 % of the face), and of the 23 with a storey above it, **2 put an opening over it**
  (deli_a01 and deli_a03). Width marks the entrance; nothing else in the composition answers it.
- **Corners:** a post (`_emit_wall_run(corners=True)`, N and S own them), in every building of the pool (102 of 102;
  146 of the 158 built). Unchanged since roadmap 58; not counted further.

## Can it be composed after the openings are placed? (`predict.py`; `predict.out.txt`)

Four candidate grammars, each moving only upper-storey windows with no gameplay tag -- the ground floor, every door,
breach, garage and vault, and every tagged window stay where gameplay put them -- and keeping each storey's count,
kind and size. A target is turned down when the window would leave the run, come within 0.3 m of another opening, or
cross a partition's junction with the exterior wall (a room wall standing in the window); the window then tries the
next target. 170 such windows in the pool's 52 multi-storey buildings; 28 of 169 first-storey openings stacked as
built.

| grammar | moved | into another room | median / max move | stacked, ground -> first | buildings touched |
|---|---|---|---|---|---|
| over: onto the opening below, within half a bay | 17 (124 have none within 1.6 m) | 0 | 1.50 / 1.50 m | 45 of 169 | 13 |
| centred: n = round(L / 3.2) equal bays | 160 | 0 | 0.86 / 3.30 m | **5 of 169** | 51 |
| entrance: centred, phased on the primary door | 156 | 0 | 0.88 / 3.38 m | 20 of 169 | 51 |
| fit: the best grid through the ground's own openings, stacking first | 147 | 8 | **2.50 / 22.00 m** | 139 of 169 | 51 |

- **A regular grid is cheap to reach and composes against nothing:** centring the upper storeys on equal bays moves
  windows under a metre and drops stacking over the ground floor from 28 to 5, because the ground floor's
  openings are not on any such grid.
- **A grid through the ground floor exists** -- 283 of 321 ground openings stand on the best 2.4-4.0 m grid their
  own face admits (the search is generous: 17 widths and a phase per opening, so some of that fit is the search's
  freedom) -- **but reaching it from the upper storeys means relocating windows**, a median 2.5 m and up to 22 m,
  8 of them into another room.
- **So the ground floor and the upper storeys were laid out independently**, and no re-placement of one against the
  other fixed recovers a composition at a small move. The grid has to be chosen where the openings are first
  chosen -- with the ground floor's -- which is the spec's authoring, not the emitter. That is where the proposal
  puts the planner.

What `predict.py` cannot see: stairs, fixtures and lights against a wall (every touched building needs a refurnish,
counted, not simulated), and how any of it looks.

## What is left

- The proposal: `docs/proposals/FACADE_PLANNER.md`.
- A ruler for appearance (roadmap 78) still does not exist; this one reads placement.
