# The fire escape: steel on brick, on the urban street's walk-ups (roadmaps 156 and 241)

**The ask.** The walker, 2026-09-13, with a photo of a brick walk-up: "this is something i'd like to see in our
toolset, fireescape stairs brick, uneven architecture" (roadmap 156; `docs/SET_DRESSING_REFERENCES.md`, "The
walker's fire escape photo"). The photo: a steel fire escape on red brick, one landing per floor with a slatted deck
and railings on three sides, a switchback flight between landings, a drop ladder below the lowest.

**Why now.** Roadmap 241's urban street stands rows of brick mid-rise Empties at the sidewalk line, touching; until
it, no generated block had brick walk-ups at all. Its own list of what is left names the detail a mid-rise front
lacks.

## What exists, read 2026-10-14

- **Deli Counter:** `FireEscape` (`spec_types.py`) and `_fire_escapes` (`deli_counter.py`) build, per served floor, a
  0.12 m deck box, one rail on the outer edge, and a 0.6 x 0.6 m visual-only column where the stair should be. No
  slot is recorded, so no art reaches it. `ladder_place.fire_escape_proposal` exists and nothing calls it.
- **Zoo:** `ladder`, `stair_rail`, `stoop_railing`; no landing, flight or drop-ladder species.
- **The mid-rise Empties** (`presets.empty_midrise`): 3.1 m storeys, windows in bays about 3.2 m apart front and back,
  a lobby door at grade, party walls at the sides. Their fronts are what the street sees.
- **The pattern to follow:** the corner shop's awning (Zoo 1.108.0, Deli Counter 0.219.0). Deli Counter computes
  where a part hangs and records a `prop` slot; Zoo draws the species from the slot's box alone; Level Factory's
  per-side merge folds an Empty's parts into one mesh a material a side.

## The first cut, in order

1. **Zoo: `fire_escape`, drawn per storey** from a slot's box, so a fire escape of any width, projection or storey
   height is drawn without Zoo knowing the building. Black-painted steel, one material, no collision.
   - `flight_a`, `flight_b`: one storey's bay. A landing at the box's bottom -- a slatted deck in a frame, railings
     on its three open sides -- and a flight rising along its outer edge to the box's top, `a` toward +X, `b`
     toward -X, so a stack alternates and switches back.
   - `top`: the top landing alone, its railings.
   - `drop`: the drop ladder, hanging from the lowest landing, raised.
2. **Deli Counter: where it stands.** A walk-up Empty -- six storeys or fewer, the walk-up's height before a
  building needs a lift, CHOSEN and not read from a code -- stands one on its front, centred on the end bay farthest
  from its lobby door: a flight bay for each floor from the second to the one under the top, the top landing, and
  the drop below the lowest, its foot about 2.3 m over the sidewalk. Each part is a `prop` slot with no collision:
  the lowest landing stands a storey up, and Level Factory reads an Empty's street edge off its colliders.
   - Not on the corner blocks in this cut: their awning runs the front, where the drop would hang into it.
3. **Level Factory:** nothing new. The per-side merge carries it.

## As built, 2026-10-14

- **Step 1, Zoo 1.110.0 (c173a8a).** `fire_escape` as listed, with these settled on the way:
  - `top` became `top_a` and `top_b`, the top landing's hatch at whichever end the last flight comes up.
  - `auto` is listed first in the genome, because a list's first option is a plan's default and the coplanar
    census names no form.
  - The flight is 22 in wide, its risers at most 8 in (2012 IEBC 405.4, as a code forum quotes it); guards 36 in.
  - The stringers are 8 in, so the treads stay 4 in deep.
  - The treads stop a step short of the stringers' end, and the handrail springs from the front rail with no foot
    post: the coplanar census found a face on another at both, in the first drafts.
- **Step 2, Deli Counter 0.220.0 (827038a4).** As listed. The drop's foot is 2.2 m over the ground floor, not 2.3
  over the sidewalk, and the width a bay's spacing less 0.2 m either side, at most 2.8 m.
- **Step 3 was wrong.** The per-side merge does not carry it: `merge_empties.gd` takes slots by name, and
  `fire_escape_*` gives no side, so each storey draws on its own (`docs/findings/fire_escape/`, "Refuted").
- **Proven: cold run 9303,** 0 interventions, nothing the graders read moved. Six walk-ups stand one on the picked
  candidate, seen in `docs/findings/fire_escape/walkups_9303_sheet.png`.
- **Found there:** Patina moved each walk-up front's coping, base course and curbs onto the stack's greybox boxes
  (roadmap 248).

## Costs to price before it ships

One more material on a walk-up's front, so one more draw a front after the merge. Thin bars are lightmap users with
little to light: read the bake's users and atlas against the run before. Triangles are not the budget here.

**Priced, cold run 9303 against 9302:**
- +3.3 draws a heading on the mean and +26 at the worst, unmerged.
- p95 frame time inside a floor of 0.38 ms.
- Lightmap users +28 and models +16; `bake.exr` +1.75 MB (65.4 -> 67.1 MB).

## Later

- **Walkable**, on an enterable walk-up: Deli Counter's `_fire_escapes` rebuilt as landings and flights with
  collision, guarded edges and slots, which is what closes 156 ("a body can climb from the drop ladder to the top
  landing").
- **The light well** of the walker's photo: a recessed facade segment in Deli Counter.

## Open for the walker

- Front or back. The street sees the front; the walker's photo shows a light well.
- Which buildings: the six-storey cut, and whether a corner block takes one on its side.
- The steel's colour: black is the default; Philadelphia's are often black, sometimes rust or silver.
