# The brief's pacing never reached Lot (roadmap 200)

2026-10-07. Asked while drafting the fix for roadmap 200: if Level Factory
wrote the brief's mode and target window into the site spec, what would Lot
say about every level already on disk -- and would the heist gate that the
mode switches on fail any of them?

## What the dial looked like

Three disconnections on one dial, each read in the code on 2026-10-07:

1. **The window.** Level Factory writes `target_minutes` at the site spec's
   top level (`apps/cli/commands/__init__.py`, `_write_site_spec`). Lot's
   `site_pacing._cfg` reads `site_spec["pacing"]["target_minutes"]`.
2. **The mode.** The site spec carries no `mode`. `site_pacing._critical_legs`
   builds travel legs only for `heist`, `assault` or `survival`, so the
   estimate counted no travel. The brief has no mode field either, so every
   mission is a heist (`getattr(model, "mode", None) or "heist"`, Deli
   Counter's spec).
3. **The verdict.** `adapters/lot/__init__.py::normalize_validation` raised
   `LOT_PACING_OUTSIDE_TARGET` only for a status containing "outside target".
   Lot writes four statuses (`site_pacing.estimate_pacing`); only the straddle
   case, "partly outside target (range straddles the window)", contains it.
   "likely TOO SHORT vs target" and "likely TOO LONG vs target" never
   surfaced. Level Factory's fake Lot (`tests/fixtures/repos/lot/lot.py`)
   writes only the straddle status, so no test could see it.

Switching the mode on also switches on `site_tactical.gate`, which RAISES --
Lot prints `BUILD FAILED` -- unless spawn -> objective -> extraction are joined
by declared paths or a shared street. The standard's v1.1 records Lot's
tactical gates as off for generated sites for exactly this reason (no mode).

## The instrument

`heist_gate_census.py` reads every candidate `site.json` under
`workspaces/*/.level_factory/temp/`, injects `mode: heist` and the brief's
window into a copy, and calls Lot's own `site_tactical.gate`,
`site_tactical.analyze` and `site_pacing.estimate_pacing`. Nothing is written.
Run it with `python -B` while a cold run is in flight, so importing Lot's
modules writes no bytecode into a hashed repo (the snapshot skips
`__pycache__` anyway).

What it does not read: the merged gameplay that holds each building's real
objective and loot markers is a Lot output, so the census counts ONE objective
marker (Lot's floor) and no loot. Distances are building origin to building
origin on the plan, not walked routes.

## What it measured (`census_2026-10-07.txt`)

- **144 candidate specs** (themed copies skipped): 8 one-building sites, 3
  two-, 123 three-, 6 four-, 4 five-building. None carries a `mode` or a
  `pacing` block.
- **The heist gate passes on all 144.** No isolated building.
- **Every spec is judged against Lot's 7-15 min default today.** The briefs
  ask for 25-35 on 125 of them (and 177 of 181 cold-run briefs on disk).
- **With the mode and the window:** expected 2.5-3.6 min (median 2.8), of
  which travel is 0-63 s (median 16). Every one reads "likely TOO SHORT vs
  target". The estimate's phases are travel, setup, objective work, loot trips
  and (survival only) a holdout; none counts fighting.
- **The extraction is the objective building on 43 of the 136 multi-building
  specs**, so the second half of those heists has no leg at all. Separately,
  **spawn == objective on 43** -- roadmap 201's defect, in specs written
  before Level Factory 0.152.0. Cold run 9194's three bank_block_001
  candidates, written by 0.152.0, read objective b0 (a bank every time),
  spawn and extraction each another building.

## Two brief facts found on the way

- **Six brief fields build nothing:** `route_shape`, `objective_hypotheses`,
  `extraction_relationship`, `verticality`, `landmark` and `seed_policy`
  (searched every repo, 2026-10-07). The first five are read only by
  `MissionBrief.functional_signature`, the functional lock's hash: changing
  one re-locks a mission and changes no geometry. `seed_policy` is read by
  nothing. Of 181 cold-run briefs, every one sets the first five and none sets
  `seed_policy`.
- **The level standard's Appendix A was wrong about `target_minutes`:** it
  read "Laser Tag's scenario timing, BUILT". Nothing in Laser Tag or in Level
  Factory's Laser Tag path reads it; it reached nothing at all.
- **159 of 181 briefs ask for `extraction_relationship:
  "crew_start_backtrack"`** -- an exit back at the crew's start -- which is the
  shape Lot's `site_audit` warns against as `S_BACKTRACK` ("the exfil rewinds
  the entry"). Neither the brief's wish nor the audit's rule builds anything:
  the extraction is a seeded draw among the buildings that are not the spawn.

## What it led to

Level Factory 0.153.0 (`patches/patch_lf_brief_pacing_tests.py`, then
`patches/patch_lf_brief_pacing.py`): the site spec carries `mode` and
`pacing.target_minutes`; the adapter names every status Lot writes and reports
an unknown one, or a missing block, as `LOT_PACING_UNREAD`; `batch create`
names the brief fields nothing builds from. Expect one new non-blocking
`LOT_PACING_OUTSIDE_TARGET` on nearly every level: the estimate and the window
measure different things until the walker decides what `target_minutes`
means -- a session, which the estimate would need a combat term to reach, or
the structural route, which today's 25-35 overstates by about ten times.
