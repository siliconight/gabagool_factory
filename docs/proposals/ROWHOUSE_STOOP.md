# The rowhouse stoop: a raised first floor and a few steps up (proposal, 2026-10-12)

**Status: PLANNED, not built.** Roadmap 240's rowhouse front, its first part. Mapped read-only against
Deli Counter, Level Factory, Lot and the contract on 2026-10-12 night. Re-read every cited line
before patching (CLAUDE.md, grounding).

## What the comps and the sources ask for

- **The comps** (`docs/reference/PHILLY_STREET_COMPS.md`, frame 3): "three or four steps up to each
  door, with iron railings; the first floor stands above the sidewalk". Every residential frame in the
  set has them.
- **Philadelphia's own guide** (City Planning Commission, *Philadelphia Rowhouse Manual*, 2008;
  read from phila.gov on 2026-10-12, not stored):
  - "Most existing rowhouses are a few steps up from the street" (p. 13);
  - houses with front porches are "usually set a few feet above the sidewalk" (p. 13);
  - a stair has "a well-anchored handrail" on at least one side (p. 27).

  It gives no dimensions.
- **The code fills that blank** (IRC 2018 R311.7.5, as reproduced by local building departments):
  - a riser at most 7 3/4 in (196 mm), a tread at least 10 in (254 mm);
  - Baltimore's local amendment allows 8 1/4 in and 9 in.

  A house built before any of these may be steeper; the factory takes the code's numbers as the
  ceiling. The working pair below is 7 in (0.178 m) and 11 in (0.279 m).

## What decides the form: the contract

- **A real riser is a wall to the contract body.** `clearances.unassisted_step_max_m` is 0.1025 m:
  `R * (1 - cos 45 deg)` for the 0.35 m body (`deli_counter/agent_contract.json`). A 7 in riser is
  1.7 times that. Per-step colliders would make a stoop a wall.
- **Deli Counter's stairs already answer this.** One smooth collision ramp rides the nosings, under
  stepped visuals:
  - its foot is extended to the floor (`stairwell.ramp_foot_extension`);
  - its head is trimmed flush with the landing (`stairwell.ramp_head_trim`, 0.190.0: trimmed, not
    sunk, because the nav bake reads the visual treads).
- **The pitch is comfortable.** At 7 in over 11 in it is atan(0.178 / 0.279) = 32.5 deg, under the
  body's 45 deg `floor_max_angle` and the bake's 55 deg (`nav_bake.agent_max_slope_deg`, cell 0.1
  m, which carries 56.3 deg).

**So a stoop is a short exterior flight built by the stairs' own helpers, not a box.** A volume's
convex collider would be a 0.5 m block; a hull of the steps keeps a 0.178 m riser at its foot.

## Where it stands: a 2.0 m strip, by construction

Level Factory's terrace (`level_factory/packages/pipeline/empties.py`) stands every Empty's front
`FRONTAGE` = 2.0 m behind the far sidewalk's back edge, the near side's own frontage
(`road_grammar.FRONTAGE`). Measured on cold run 9270's lot: the far row's fronts at plan y -31.665,
the sidewalk's back edge at -29.665.

A stoop and its ramp's foot must fit in that strip. With the nosing line through the landing's front
edge, the foot lands one tread beyond the bottom riser: the landing depth plus `n` treads from the
facade.

    risers   rise      visual depth (0.9 m landing)   the ramp's foot    fits 2.0 m
    3        0.534 m   0.9 + 2 x 0.279 = 1.46 m        ~1.74 m            yes, 0.26 m to spare
    4        0.712 m   0.9 + 3 x 0.279 = 1.74 m        ~2.02 m            no (0.8 m landing: 1.92)

**Three risers by default** -- the comps' "three or four" and the strip's answer. Four only where a
deeper strip allows. A test should hold the terrace's `FRONTAGE` against the stoop's depth, so a
narrower terrace cannot silently push a ramp onto the sidewalk.

## Who owns what

- **Deli Counter:**
  - `empty_rowhome(stoop=3)` raises the front door's sill and the ground storey's front windows by
    the stoop's rise. The storey grid is kept: a 0.534 m rise puts a 1.6 m window's head at 2.98 m
    in a 3.1 m storey, so either the window shortens or the building gains a base course. The draft
    decides which, by what the wall builder accepts.
  - A `_stoops` step builds the flight with the stairs' helpers -- visual tread columns, one
    collision ramp (foot extended, head trimmed), the landing -- and records slots so the art pass
    can see it.
  - The door is a panel on an Empty (`empty_panes`, no carve), so nothing behind it changes.
- **Zoo:** the iron railing, and later the stoop's art (treads, cheek walls) as a species owning
  its visual only. The collision stays Deli Counter's, as the stairs' does.
- **Level Factory and Lot:** nothing, while the terrace keeps 2.0 m. Lot's frontage slab is the
  ground the stoop stands on.

## Gameplay and price

- **A stoop is a height step and cover:** a 0.53 m landing behind railings. The graded lots carry
  the Empties (every `lot_assemble.candidate.*` job builds the `gs_empty_rowhome_*` GLBs), so stoops
  change what Laser Tag and the walk test grade. Price them on the graders' breadth
  (`docs/findings/route_snag/engine_breadth.py`, 16 lots, both engines) before shipping -- roadmap
  242's lesson.
- **Draws:** the stoop's pieces join each Empty's per-side merge (Level Factory 0.143.0; 9270:
  1,061 meshes of 1,660 surfaces became 148). They add at most a material a side (the treads) and the
  railing's iron. Priced like the drains: fixed stations, two controls.

## The build, in order

1. **A Deli Counter draft** in a scratch copy:
   - raise the door and windows (a spec change), and add `_stoops` (greybox);
   - build one Empty and read its manifest and collision;
   - check the ramp against the contract with Deli Counter's own stair gates.
2. **The patch:** suite, `build.py --all`, a cold run, frames at the far row, and the graders'
   breadth. Built as Deli Counter 0.211.0/0.211.1 and Level Factory 0.195.0/0.196.0 (cold runs 9271
   and 9272). **The graders' breadth was not run before shipping**, for the stoops or the railings:
   `engine_breadth.py` stages lots that predate both (its newest are cold run 9264's). It was run
   afterwards, on 2026-10-13 (`docs/findings/stoop_breadth/`). On the 8 of its lots with rowhomes,
   the same Deli Counter with and without stoops was swapped in, and the controls held:
   - the walk test is unchanged on all eight;
   - no Laser Tag stuck event falls within 10.9 m of a stoop (229 events);
   - the fights move both ways.
3. **Zoo's railing**, then a cold run and frames. Built as Zoo 1.105.0's `stoop_railing`, Deli
   Counter 0.212.0 and Level Factory 0.197.0 (cold run 9273): one railing each side, in two sections,
   5 cm inside the stoop's side; its colliders Deli Counter's.
4. **The walker's eye:** `docs/cold_runs/cold_9273/railings.png`.

## Taste calls, answered

The walker, 2026-10-13: "3 risers, concrete, railings both sides -- build the railings".

- Three risers or four (the strip says three unless the landing shrinks): **three**.
- The treads: concrete as on the twin, marble, or brick. No source here says which Philadelphia's
  were: **concrete**.
- A railing on one side or both (the manual asks at least one): **both**.
