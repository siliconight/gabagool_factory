## 0.98.0 - the getaway van at the spawn: the crew starts at it and the job ends at it

The walker, 2026-10-07:
- "the default is they have to leave the building and return to the
  'getaway' car or vehicle to leave the scene";
- the vehicle "a Box Truck. Like a Chevrolet P30 ... Matte Black" -- Zoo's
  `step_van`, 1.82.0 to 1.85.0;
- "location of the getaway vehicle should be the same as the missions spawn
  point. you spawn, do the job, then return to the car".

2026-10-08: "go ahead, place it at the spawn". Roadmap 206, phase 2.

### `site_getaway`: where the van stands and where the crew does

**The van.** It parks in two adjacent parking bays, because a van is longer
than one 6.0 m bay. The pair is chosen on a kerb that a door of the spawn
building faces, as the one that puts the van's own door nearest that door,
within `MAX_REACH` (30 m).
- It faces the way its lane travels, as `site_parking`'s cars do, so its
  kerb side -- Zoo's -X, with the crew's door -- is against the kerb.
- Its body stands `KERB_GAP` (0.20 m) off the kerb line, so the slot, which
  runs out to the mirror heads, stops just short of it.
- It is a cover record (`source: getaway_van`, Zoo's genome dims
  2.6 x 6.8 x 3.05), so the site kit builds it, the walk scene's navmesh
  carves it, and every planner after it stands round it.

**The crew's point.** One point on the sidewalk outside the van's kerb-side
door:
- `DOOR_AHEAD` (1.65 m, pinned from Zoo's `van_forms.layout` because Lot does
  not import Zoo) toward the nose, and `SPAWN_OFF_KERB` (1.2 m) in from the
  kerb;
- it is both the site's `crew_spawn` marker and its `extraction` marker, the
  latter carrying `getaway: step_van`;
- `_walk_positions` takes a site-level marker over a building's own, so the
  crew leaves from it and the job ends at it.

**What gets no van, and says why** (`LOT_GETAWAY_NONE`):
- a site that is not a heist;
- a spawn building not on the site;
- a site that already declares its own start or exit -- a designer's
  site-level marker stands;
- no pair of free bays within reach of a door facing a road.

Without a van the spawn and the extraction are what they always were.

**No enemy stands in it**, by arithmetic rather than a rule. Every point of the
van lies within `site_spawns.MIN_STANDOFF` (8.0 m) of its door's spawn --
6.35 m at the far corner -- and `place_enemies` keeps every enemy that far
out.

### `assemble`

The van is planned before anything reads where the crew stands: after the
collision reading, before `_walk_positions`. It joins `cover` and its markers
join `site_markers`, which `merge_gameplay` copies only when the spec carried
the key, so both lists are kept. The plan travels in the gameplay JSON as
`getaway_plan`, and `LOT_GETAWAY_PLACED` says where the van went.
`COVER_MATERIALS["step_van"]` is `paint_matte`, Zoo's one option for it.

On the kerb probe the van takes bays L7-8 at (-62.0, 3.65), with the crew at
(-63.65, 6.2). That is 23.9 m from the garage's south door, which stands well
back from its road. The pair nearest the door's line lay inside a crossing's
setback.

### The enemies along one leg

With the van the extraction is the crew's spawn, and the route goes there and
back. `place_enemies` spread its samples over spawn -> objective ->
extraction, and the return leg is the outbound one backwards. Measured on an
open field:
- two enemies landed mirrored at one point;
- one was pushed 43.5 m off the route;
- three crowded the middle.

A route whose extraction stands within `THERE_AND_BACK` (3.0 m) of its spawn
now spreads the enemies along its one leg. All six land within 6.5 m of it,
and the crew passes them going in and coming out.

### The audit

- **`S_BACKTRACK`** ("the exfil rewinds the entry") fired at 0 m and 0
  degrees on every level built the walker's way. When the extraction marker
  names a getaway van it is `S_GETAWAY_AT_SPAWN`, INFO: the second half of
  the heist is the walk back to the van, by design. Without the van's mark,
  the same geometry is still `S_BACKTRACK`.
- **Two anchors at one point are judged once.** `S_RESPONDER_CAMP` and
  `S_NAKED_ANCHOR` checked the crew spawn and the extraction separately, and
  reported one problem twice when the two are one point.

### Tests

**`tests/test_site_getaway.py`: 9.** They cover:
- the kerb the spawn building faces, and a pair of free adjacent bays;
- one point as spawn and extraction, at the door, clear of the slot;
- no enemy inside the van;
- every refusal saying why;
- determinism;
- `assemble` writing the van as a `paint_matte` slot, with the markers in the
  drawn spec and every parked car outside it;
- the audit's INFO, and its single camp line;
- the enemies along one leg. With `THERE_AND_BACK` 0 this test FAILS, on the
  enemy 43.5 m off the route.

**Suite:** 678 passed (669 and the 9).

