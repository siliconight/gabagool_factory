## 0.101.0 - the responders' car is built and shipped, and stood nowhere

**Roadmap 212.** Responders arrive on the way back; spawning them is the
gameplay layer's, and the factory makes "thee assets" (the walker,
2026-10-08). Zoo 1.86.0 draws the cruiser and Lot 0.100 plans where it
arrives. Nothing built it for a level, so no package carried it.

**The car is a list of its own.** `assemble` writes
`site_spec["responders"]`, one record per arrival
(`site_responders.vehicle_record`): the species, `VEHICLE`'s slot, the stop,
and the yaw it drove in at.
- **It is not cover.** So no planner stands round it, and the audit does
  not grade it as cover.

**The site kit builds it.** `write_site_slots` gives each record a slot,
`responder_<i>`:
- the cruiser at its slot, at the stop, facing the way it came, with convex
  collision for when the game spawns it;
- `coverage` counts them as `prop/site_responders`;
- `COVER_MATERIALS` names `cruiser` `metal_painted`, its genome's one
  option.

The kit builds one module for them all, because the slots are identical.

**The themed assembly ships it and stands nothing.**
`cover_module_refs(..., key="responders")` resolves the car the way it
resolves a cover piece: the kit's verdict read, the module copied beside the
scene into `cover/` with the textures it names.
- **Not in the scene.** Its declarations are left out of `site.tscn`, since
  a resource a scene declares, it loads.
- **Named instead.** `write_responder_vehicles` writes `responders.json`
  beside the scene: each car's file, its stop, its yaw and its slot.
- **A car with no module** is listed under `missing`, not dropped. The
  candidate's greybox assembly, which has no kit yet, lists every car
  there.

**Level Factory 0.162.0** reads `responders.json` and names each arrival's
car in `responder_arrivals.json`.

**Tests.** `tests/test_site_responders.py` has 17 tests, 4 of them new:
- each arrival gets a kit slot for its car;
- the car is copied with the texture it names and named for the package;
- the probe, assembled against a kit holding the cruiser, stands no car
  and names it for both arrivals;
- with no kit, every car is missing, not dropped.

All four fail on 0.100.1.

**Suite:** 710 passed (706 + 4), `python -m pytest -q`.
