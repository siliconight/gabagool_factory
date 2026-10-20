---
name: detail-lives-in-generator-logic
description: "Walker 2026-10-06 -- the detail put into the strip club and the Flappahs convenience store must live in the logic any level runs when it calls for a gas station, convenience store or strip club, not only in particular spec instances"
metadata:
  node_type: memory
  type: feedback
  originSessionId: 27f14f8b-7ce5-44c0-a704-178a824035d7
  modified: 2026-10-06T14:15:52.710Z
---

The walker, 2026-10-06: "I also want to make sure that the care and detail
we put into the strip club and flappahs convient store don't just get lost to
the next phase of level creation. That level of detail should be in the logic
that is called when a level calls for a Gas Station, Convient Store, or a
strip club."

Then: "yes, a03 as convenience store; Flappahs store always Flappahs".
- My stated reading, not contradicted: a gas station's fascia also says
  FLAPPAHS, one brand a site.
- Zoo builds the pumps, pylon, coffee island and slush machine in the brand.

- **Flappahs** is the invented convenience-store brand. See
  `pixelcoat/profiles/signs/marks/flappahs_red.svg` and
  `docs/proposals/GAS_STATION_SHOP.md`.

**Why:** some of that detail went in by migrating specific spec JSON files.
`deli_counter/migrate_cooler_wall.py` is one. A level that draws a different
instance, or generates a fresh building from the archetype, can silently miss
it. As of LF 0.145.0 the library path is the default, so the path that
builds these types changed.

**How to apply:**
- Put new building-type detail in the generator: Deli Counter presets and
  room programs (`level_design.py`), Zoo species keyed on room kind, Lux
  presets, Pixelcoat sign profiles.
- A migration of existing specs is fine only alongside a generator change.
- When checking a type, check the generated path AND every library spec of
  the family.

**Shipped 2026-10-06** (gas station and convenience store):
- DC 0.188.0: the `convenience_store` recipe; a03 renamed
  `convenience_store_a01`; generated stores get the window sign, posters and
  a `preset` key.
- Zoo 1.75.0: FLAPPAHS spelling; `convenience` opens the door sign.
- Pixelcoat 0.58.0: FLAPPAHS is the only name in the gas and convenience
  families.
- LF 0.146.0:
  - the brief words for all three types;
  - the fascia reads the resolved preset;
  - a fascia is never the fuel price board.
- Cold run 9181 is the never-seen one-building convenience store.

**Still open:**
- Strip club identity: RESOLVED by LF 0.147.0, "a band names a shop".
  A club gets no band, so its neon and door, which share one name, name it.
  Zoo 1.76.0 stopped a retail strip's door from reading as a club.
  Still open: a windowless club gets no door box.
- `corner_store` and `nightclub` stay refused as brief words, by decision
  (`deli`, `night_deli` and `stop_n_go` resolve since LF 0.150.0).
- Deli detail: DONE 2026-10-07, generated and drawn alike. The case is off
  its wall (DC 0.199.0); it is Zoo 1.81.0's `deli_case`, routed by DC
  0.200.0; the window has a beer neon over taped posters (DC 0.201.0);
  `deli`, `delicatessen`, `night_deli` and `stop_n_go` resolve (LF 0.150.0).
  Proven in cold runs 9190 and 9191, 0 interventions each.
  Open: furnish's wall pieces on open edges (roadmap 196); the generated
  deli's enemies jam at its rear door (197); the neon reads faint.
- `fuel_stop_heist` has no video poker.
- (Fixed in LF 0.147.0: `gs_corner_station`, `stop_n_go` and the
  `fuel_stop_heist` specs now wear FLAPPAHS.)

Related: [[store-dressing-queue]], [[strip-club-comp-lou-turks]],
[[store-at-night-work-queue]], [[pa-skill-games-queue]],
[[breadth-sweep-ten-missions]].
