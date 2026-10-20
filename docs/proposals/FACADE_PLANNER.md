# The facade planner: one face, every storey, decided before an opening is placed (proposal, 2026-10-20)

**Status: steps 1 and 3 SHIPPED** (Deli Counter 0.238.0, `patches/dc_facade_stack/`; proven by cold run 9348,
`docs/cold_runs/cold_9348/`); steps 2 and 4-6 planned. Roadmap 79, with 74 and 76 inside it. Mapped read-only against Deli Counter 0.237.0,
Zoo 1.114.1 and Level Factory 0.222.0 on 2026-10-20. Re-read every cited line before patching (CLAUDE.md,
grounding). It serves the "good" gate (roadmap 18), not interventions-per-level: every level the pipeline makes today
already ships without a hand on it, and none of this changes that number.

## What was measured (`docs/findings/facade_census_79/`)

On the 102 buildings a themed lot can draw (Level Factory's own themed report), read off their built slots:

- **The storeys do not stack.** Of the 169 first-storey openings in the 52 multi-storey buildings, 28 stand over a
  ground-floor opening. The Empties, whose presets lay every storey on one list of bays, read 92.9 % through the same
  instrument, so it can see stacking where there is any. Along one storey the rhythm is already regular (43 of 62
  runs with three or more openings space them evenly), so the problem is between storeys.
- **The entrance is marked by width alone.** 31 of the 39 tagged main or front doors are wider than every other
  exterior door. Above the 23 that have a storey over them, 2 have an opening.
- **Widths nobody chose:** 8.2 % of solid wall is tiling remainder, in 69 distinct widths. The Empties carry 35.4 %
  and still compose, because their preset chose those widths. A remainder is only unchosen when nothing upstream
  sized it.
- **In delco the joints are not what shows.** The delco wall draws no relief (Zoo 0.51.0, `reveal` 0), so a module
  joint is at most a faint 3 mm bevel line. What a person reads on a delco facade is where its openings are.

## Why the emitter cannot do it, and how far the upper storeys can

`_exterior` (`deli_counter.py:1494`) emits each side of each storey separately. `_emit_wall_run` (`:1085`) gets one
run, and its openings arrive already placed as fractions of that run (`_opening_to_hole`, `:511`). Nothing in the
emitter could align storeys, because it never sees two.

Moving the upper storeys alone goes part of the way, and the measurement says exactly how far (`predict.py`). Five
candidate grammars were tried, each moving only the 170 upper windows that carry no gameplay tag, with the ground
floor fixed. The table settles one thing first: **the upper storeys were authored to one rule and the ground floors
to another.** Upstairs, 167 of 177 openings are mirrored about their face's centre. At grade, 135 of 321 are, because
doors, breaches and display windows stand where the rooms behind them need them. While the ground floor holds,
stacking and that symmetry trade against each other:

- Moving each upper window onto the opening below it, within a bay (3.2 m), stacks 99 of 169. It moves 71 windows a
  median 2.0 m, none into another room, and costs 44 upstairs openings their mirrored partner.
- The same move made only in mirrored pairs (`over sym`) stacks 74 of 169. It moves 46 windows in 22 buildings, none
  into another room, and keeps all 167 mirrored openings.
- Centring the upper storeys on equal 3.2 m bays keeps the symmetry and stacks almost nothing (5), because the ground
  floor's openings are on no regular grid.
- The best grid through the ground floor's own openings stacks 139. Reaching it moves windows up to 22 m, 8 into
  another room, and breaks most of the symmetry (64 left).

*Refuted and kept:* this section's first version tried the move onto the opening below at half a bay only, found 17
windows could move, and concluded that the upper storeys could not be moved toward a composition at all.

**So a face that is both stacked and symmetric, where its use allows, needs its ground floor laid out with the grid --
where openings are first chosen: the spec's authoring.** The Empties prove the point from the other side.
`empty_midrise` (`presets.py:3304`) divides its front into `round(width / MIDRISE_BAY)` bays (`MIDRISE_BAY` 3.2,
`:3295`), puts the door in the bay nearest `lobby`, and gives every storey the same positions. `empty_rowhome`
(`:3121`) does the same with two bays. That is a facade planner, written inline once per family, and it is the only
composition in the library.

## The mechanism (what this proposal builds)

- **`facade_plan.py` in Deli Counter, pure data and no Blender.** `plan_face(width, storeys, row, fixed=...)`
  returns a plan with:
  - the face's bay lines (positions along the face);
  - each bay's role (primary, regular, end);
  - per storey, which openings land in which bay.

  `fixed` carries openings that gameplay pins, which the plan must keep or must place a bay around.
- **The grammar is a table, not code.** One row per family names a bay width, which storeys share the grid, where
  the primary bay goes, and what a ground floor may do differently. Each row names its source. Deli Counter owns the
  table; the walker owns what goes in it.
- **The presets ask the planner** instead of writing fractions by hand. The specs stay what they are today:
  `ext_walls` with `pos` fractions. The planner decides those fractions before anything downstream reads them, so the
  emitter, the furnish pass, the gameplay records and every gate keep reading the spec as they do now.
- **`_emit_wall_run` stays the executor.** A later step lets the plan size the piers between openings, so `_wall_span`
  lays a chosen pier instead of leaving a remainder. That is item 74's "a vocabulary that grows with the span", made a
  composition decision rather than a tiling accident.

## The grammar's first rows, and where each comes from

Not invented here. Roadmap 79 forbids that and is right to. The rows come from the walker's own references:

- *"Align repeated architecture where construction would align it; vary the parts that would actually vary"*
  (`docs/reference/HUMAN_AUTHORSHIP_GUIDE.md`): windows stack on bays because the structure between them carries down.
- `docs/reference/EMPTIES_COMPS.md`, agreed 2026-10-04:
  - the rowhome: "Two windows per storey, stacked on the same bays";
  - the loft: brick piers between regular bays, one window per bay per storey;
  - the main-street storefront: shop below, one or two floors above, a sign band.
- *"Establish the rule, then break it with a reason"* (the guide, 9.7). An exception, such as a bricked-up bay or a
  boarded window, carries a cause. It is never noise.
- Primary identity goes "where a person approaches or looks for the entrance". The plan marks the primary bay. What
  dresses it (a sign band, a canopy, door glass, a window over it) is Zoo's and Pixelcoat's to build and the walker's
  to choose.

## Steps, each reversible

1. **The module, proven against the composition that already exists.** `facade_plan.py` plus the two Empty families'
   rows, with `empty_rowhome` and `empty_midrise` routed through it. Proof: every Empty spec byte-identical and the
   built records identical except build time. No look changes; the mechanism exists and its first user changes
   nothing.
2. **The census as a Deli Counter report.** The stacking, entrance and remainder figures go into a build's findings,
   advisory, so the next building is measured as it is built.
3. **`over sym` across the library: the first step that composes, moving nothing gameplay placed.** 46 upper
   windows in 22 buildings move onto the mirrored openings below them, within a bay and within their room. Stacking
   goes from 28 to 74 of 169 and no symmetry is lost. A migration through the planner, then:
   - refurnish the 22 (a moved window moves fixtures), rebuild, and run every gate;
   - a cold run on a mission that draws one of them;
   - frames before and after;
   - price it: draw calls and frame time at fixed stations, against the same Level Factory version.
4. **One enterable family re-planned whole, as a trial (the walker's choice of family).** Its faces share one grid on
   every storey. Its ground-floor openings move within their own rooms, to land on the grid. Then:
   - refurnish (a moved opening moves fixtures), rebuild, and run every gate;
   - a cold run on a mission that draws the family;
   - frames before and after;
   - price it: draw calls and frame time at fixed stations, against the same Level Factory version.
5. **Piers chosen, not left.** The plan sizes the solid between openings, so the remainder figure falls by
   construction (74).
6. **The primary bay and the corners as designed conditions**, after step 4's frames, with the walker. 79 asks for
   both. 74's caveat holds: any second layer of articulation is subtractive or texture, never proud of the wall
   (`zoo_keeper/core/arch.py`, `relief_parts`).

## How to measure

- `census.py` before and after every step, the Empties as its control. `predict.py` is kept to price a candidate row
  before it is built: how many windows move, how far, and how many into another room.
- Step 1: byte-identical specs and build records. Steps 3 and 4: interventions on a cold run of a mission that
  draws a moved building, the nav gate, Laser Tag's routes, the light check, and the price. A moved opening is a
  gameplay change: doors and windows are entries, sockets and interactives (`_record_openings`, `:1551`).

## What is the walker's

- The grammar: the bay, which family first, and whether a ground floor's openings may move within their rooms to
  land on a grid.
- What marks the entrance.
- Whether a composed facade reads better at all, judged from step 3's frames, and whether symmetry or stacking
  wins where a face cannot have both (`over sym` keeps the symmetry; a plain `over` at a bay's reach stacks 25 more
  and loses it on 44 openings).
