# Phase 2 -- Core Library: CLOSED (2026-07-21)

**Targets hit exactly: 40 configurations / 16 families / 6 missions.**
27 new configs across 11 new families, all PASSING both engine building
gates on Godot 4.7 (27/27 nav, 27/27 import). All 3 new missions FULL
green -- path proofs + physical walkers + 4-player mp_smoke -- including
the MSN_WAREHOUSE_DISTRICT_01 hero (4 players x 14/14 targets, ~770 m,
202 s spine-scaled sim): the first hero to fully pass the physical
walktest. Three Zoo visual themes (delco / center_city / industrial_flats)
across all 46 species genomes; theme distribution recorded per config.
Certified set: **factory 1.3.0** (DC 0.81.0, Lot 0.21.0, Zoo 0.31.0,
pipeline 0.3.0).

## Narrative slate
The writer's 33-heist slate is mapped (NARRATIVE_SLATE.md): Phase 2 ships
the Wawa chassis (GAS_STATION), CVS (PHARMACY), Angelos (STRIP_RETAIL A01),
Jewelers Row (STRIP_RETAIL A02 + strip_mall mission), market chassis
(SUPERMARKET), and the shipping-port ancestor (LARGE_WAREHOUSE A03 hero).
Design updates recorded: 20/30/40-min mission tiers; SEPTA train heist
flagged for level_factory design work.

## Engine-round findings (all fixed)
1. find_godot --version probe flakes on loaded machines -> explicit
   DC_GODOT trusted unprobed.
2. Walker floor_max_angle (45 deg default) < bake slope (55) -> tall-story
   basement ramps read as walls; walkers now read DC_NAV_SLOPE.
3. Tall-story (4.2 m+) switchback basement flights fragile in tight rooms ->
   straight-with-clearance is the proven pattern (encoded in p2 rules).
4. Building-level nav islands from exterior volumes (gas forecourt) are
   site-scale artifacts -> recorded as open_issue, not defect.

## Open (carried to Phase 3)
- Visual scoring (score >=4 / hero >=4.5) still null on all records --
  configs stay candidate until the art pass (Pixelcoat/Patina/Lux leg).
- Phase 1 backlog items (multi-story switchback self-connect; story1-deli
  descent at site scale; central_vault hero physical walk -- NOTE: the
  slope fix likely cures it; re-run when convenient).
- Phase 3 scope: 28 families / 75 configs / 12 missions / 4 heroes; the
  structurally novel families (rail station=SEPTA, freight terminal,
  courthouse, self-storage) + slate families (strip club, funeral home,
  construction site, marina, brewery, mansion, museum).
