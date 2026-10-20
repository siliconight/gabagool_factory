# The facade planner: one face, every storey, decided before an opening is placed (proposal, 2026-10-20)

**Status: PLANNED, not built.** Roadmap 79, with 74 and 76 inside it. Mapped read-only against Deli Counter 0.237.0,
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

## Why the emitter cannot do it, and the upper storeys cannot either

`_exterior` (`deli_counter.py:1494`) emits each side of each storey separately. `_emit_wall_run` (`:1085`) gets one
run, and its openings arrive already placed as fractions of that run (`_opening_to_hole`, `:511`). Nothing in the
emitter could align storeys, because it never sees two.

Moving the upper storeys alone does not fix it either (`predict.py`). Four candidate grammars were tried, each moving
only the 170 upper windows that carry no gameplay tag, with the ground floor fixed:

- Centring the upper storeys on equal 3.2 m bays moves them a median 0.86 m. Stacking over the ground floor *falls*,
  from 28 to 5.
- The best grid through the ground floor's own openings exists for most faces: 283 of 321 ground openings stand on
  one. Reaching it lifts stacking to 139, but moves windows a median 2.5 m and up to 22 m, 8 of them into another
  room.
- Moving each upper window onto the opening below it reaches only 17 of the 170. The other 124 have no opening below
  within half a bay.

**So the grid has to be chosen together with the ground floor's openings, where openings are first chosen: the
spec's authoring.** The Empties prove the point from the other side. `empty_midrise` (`presets.py:3304`) divides its
front into `round(width / MIDRISE_BAY)` bays (`MIDRISE_BAY` 3.2, `:3295`), puts the door in the bay nearest `lobby`,
and gives every storey the same positions. `empty_rowhome` (`:3121`) does the same with two bays. That is a facade
planner, written inline once per family, and it is the only composition in the library.

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
- **The presets ask the planner** instead of writing fractions by hand. The specs stay what they are today: `ext_walls`
  with `pos` fractions. The planner decides those fractions before anything downstream reads them, so the emitter,
  the furnish pass, the gameplay records and every gate keep reading the spec as they do now.
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
   built records identical except build time. No look changes; the mechanism exists and its first user changes nothing.
2. **The census as a Deli Counter report.** The stacking, entrance and remainder figures go into a build's findings,
   advisory, so the next building is measured as it is built.
3. **One enterable family, as a trial (the walker's choice of family).** Re-plan its faces so the storeys share one
   grid. Its ground-floor openings move within their own rooms, to land on the grid. Then:
   - refurnish (a moved opening moves fixtures), rebuild, and run every gate;
   - a cold run on a mission that draws the family;
   - frames before and after;
   - price it: draw calls and frame time at fixed stations, against the same Level Factory version.
4. **Piers chosen, not left.** The plan sizes the solid between openings, so the remainder figure falls by
   construction (74).
5. **The primary bay and the corners as designed conditions**, after step 3's frames, with the walker. 79 asks for
   both. 74's caveat holds: any second layer of articulation is subtractive or texture, never proud of the wall
   (`zoo_keeper/core/arch.py`, `relief_parts`).

## How to measure

- `census.py` before and after every step, the Empties as its control. `predict.py` is kept to price a candidate row
  before it is built: how many windows move, how far, and how many into another room.
- Step 1: byte-identical specs and build records. Step 3: interventions on a cold run of a mission that draws the
  family, the nav gate, Laser Tag's routes, the light check, and the price. A moved opening is a gameplay change:
  doors and windows are entries, sockets and interactives (`_record_openings`, `:1551`).

## What is the walker's

- The grammar: the bay, which family first, and whether a ground floor's openings may move within their rooms to
  land on a grid.
- What marks the entrance.
- Whether a composed facade reads better at all, judged from step 3's frames.
