---
name: extraction-is-the-getaway-vehicle
description: "Walker 2026-10-07/08 -- the getaway vehicle is a matte-black, faded Chevy P30-style step van parked AT the spawn; a HERO PROP reused across missions; Zoo 1.85.0; PLACED and PROVEN (Lot 0.98.0/0.98.1, cold 9198/9199); priced 5 draws / ~0.04 ms where seen; package anchor still missing (204)"
metadata:
  node_type: memory
  type: project
  originSessionId: 27f14f8b-7ce5-44c0-a704-178a824035d7
  modified: 2026-10-08T17:06:56.175Z
---

The walker, 2026-10-07, in three steps:
1. "the default is they have to leave the building and return to the
   'getaway' car or vehicle to leave the scene."
2. "For the getaway car, I want a Box Truck. Like a Chevrolet P30. Matte
   Black....faded, with patina, like a worn in truck...that's been on many
   jobs.... Our very own 'millenial falcon'." Four reference photos: a
   white P30 step van, a Philly water-ice step van, and two dark, weathered
   food-truck step vans.
3. "location of the getaway vehicle should be the same as the missions
   spawn point. you spawn, do the job, then return to the car."

Then, 2026-10-08, on 1.82.0's frames: "Looks great"; glass too tall (fixed:
header); "show me" the ghost lettering; "flesh out the bottom ... driveshaft
and rear differential" (fixed: chassis). And: **"this van is also going to
be the foundation of a hero prop that get's reused in multiple missions, so
we can afford to really make it look good."**

**Why:** measured 2026-10-07, the extraction was a seeded draw among the
buildings that are not the spawn, so it landed on the objective building on
43 of 136 multi-building site specs and on 2 of 3 candidates in cold run
9195 -- no second half to the heist. 159 of 181 cold-run briefs already said
`extraction_relationship: "crew_start_backtrack"`.

**Status, 2026-10-08:** Zoo 1.82.0 (e346bf0), 1.83.0 (492d654): header
0.28 m, 28-part chassis on the body's material (5 submissions); 1.84.0
(9cb7249): the ghost of SKEEVY'S WOODER ICE on EVERY build -- the walker:
"make the ghost the default, patchy version" (peeled vinyl = darker,
unevenly faded letters on the chalked side). 1.85.0 (7852cb2): the HERO
PASS -- 28-segment grooved tyres, nested steel wheels, wipers hung from the
header, West Coast mirrors, step, markers, tail lamps, hinges, corner caps,
mud flaps: 13,792 tris (budget 16,000), still 5 draw calls. PHASE 2 GO
(walker 2026-10-08: "go ahead, place it at the spawn"): Lot 0.98.0 d12d559
(site_getaway: two kerb bays nearest the spawn building's street door; one
point = crew_spawn + extraction(getaway) on the sidewalk at its door;
enemies along one leg; S_GETAWAY_AT_SPAWN), Level Factory 0.155.0 a5f6f30
(extraction = spawn, draw kept), Laser Tag 0.25.0 d676dc6 (completion only
when every route point is REACHED -- stricter for all routes). Cold run 9198
(0 interventions) proved it: van 4.0/4.5/6.1 m from the door on its 3
candidates; frames sent (night+rain level: silhouette reads, ghost/patina
do NOT -- a daylight look needs the times-of-day work). 9198 found a crew
member INSIDE the van (crew_spawns ignored cover; seed_9256 never played):
Lot 0.98.1 c45c6e2 (`cover_rects`), proven by cold 9199 (0 interventions).
PRICED (findings/getaway_van_price): 5 draws where seen (17 of 53
headings), ~0.04 ms there; root 600b8e6. PACKAGE FIXED by LF 0.156.0 (cold
9201): the van's crew spawn is the package's player_start (mission_start)
and its extraction the mission's; before, the start was synthesized at the
centroid of all Lot anchors -- and tools/walk_export.py stands the walker
at the package's player_start, so walks now start at the van. The walk back was empty with
the one-leg enemy spread (crew deaths 48->1, 19->0; but 49->41 where enemies
flanked) -> the walker chose responders on the way back:
[[responders-arrive-on-the-way-back]], roadmap 212. Still open: a painted
finish texture, best judged in a level; Lot 0.98.1's place_enemies comment
overstates "single file" (fix with roadmap 211).

**How to apply (phase 2):**
- One vehicle per level: spawn and extraction are the same place, the truck
  at the curb, spawn on the sidewalk by its kerb-side door (inside its box =
  Laser Tag SPAWN_IN_COLLISION). Never the objective building.
- Lot's `site_audit` S_BACKTRACK fires at 0 m / 0 deg on every level under
  this model; it must recognise the getaway van. S_RESPONDER_CAMP would
  double-report. Level Factory's `site_placements` keeps its extraction draw
  so no later number moves. Roadmap 206 lists every touched reference.
- The package must mark it as the mission's start and extraction (roadmap
  204). Related: [[level-excellence-standard-doc]], [[authorship-guide]].
