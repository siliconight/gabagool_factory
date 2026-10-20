# Cold run 9342 -- 0 interventions; precinct_yard_001, seed 9708, stopped at the export on a fire escape nothing skins

**What it was for.** Roadmap 265's `broken` and `hatch` floor-hole causes in a shipped package: cold runs 9340 and
9341 proved the `cut` cause on deli_a03, and only apartment_walkup_a01 carries a `broken` hole (bedroom over kitchen)
beside a floor hatch in a building a themed lot can draw. `docs/findings/hole_causes_265/lot_replay.py` replays Level
Factory's own `building_library.lot_for_brief` offline (its `--check 9328` reproduces all three of 9328's graded lots)
and found precinct_yard_001's seed 9708 placing it. Staged from 9328 with `seed_base` 9708; the seed named.

**Tools:** Deli Counter 0.236.1, Level Factory 0.219.0, Zoo 1.114.0, Lot 0.125.0, Lux 0.78.0.

**The legs** (`driver.log`):
- **Shell:** 3 candidates, all distinct; 0 blockers of 74 findings. seed_9708 placed airport_terminal_a01,
  apartment_walkup_a01, freight_terminal_a01 and large_warehouse_a03 with the 12 Empties, as the replay said.
- **Art:** 0 blockers of 104 findings.
- **Export: STOPPED, exit 5** (`export.log`), the greybox census refusing the themed package:

      GREYBOX_IN_A_THEMED_PACKAGE: 2 surface(s) still carry a greybox material (gb_floor 2)
        Bake/Site/b2/GreyboxBase/FIREESCAPE_REAR_FIRE_ESCAPE_1  on gb_floor
        Bake/Site/b2/GreyboxBase/FIREESCAPE_REAR_FIRE_ESCAPE_1_RAIL  on gb_floor

  Everything before it held: no missing glb reference; the light bake 379 models and 149 primitive meshes, 4,632
  users, 75.1 s.

**`INTERVENTIONS: 0`** (journal 0, unattributed files 0), read after `cold_run.py --end`.

## Attributed before anything was changed

- **`b2` is apartment_walkup_a01**: the package's `greybox_skin_scan.json` names the two nodes (7.63 and 5.07 m2), and
  the spec's one `fire_escapes` row is `rear_fire_escape` on the N wall serving storey 1, its drop ladder the
  termination. Deli Counter's `_fire_escapes` (ladder spec s9) builds the deck and its outer guard as boxes in the
  floor role with their own colliders; no kit module stands in for them and no worldskin pass dressed them.
- **Not the hole change, and not new.** Cold run 9172 shipped apartment_walkup_a01 on 2026-10-06 and its export log
  reads `2 surface(s) on a greybox material (gb_floor 2); slabs 0` -- reported, because the census refused on slabs
  only then. Level Factory 0.218.0 made any greybox surface refuse, on the claim that every class the census had
  reported had an owner, judged on the packages exported since 2026-10-10; no lot in that window drew this building.
- **One cold run finds one such kind; the library census found the next one.**
  `docs/findings/base_greybox_owners/census.py` read every base in the library against the passes' name tests -- on
  this run's four buildings it reproduces the engine's census to the surface -- and found one more kind in shells a
  themed lot can draw: the vehicle ramp (`ramp<n>`, `gb_ramp`), five of them in cr_garage, parking_garage,
  parking_garage_a01 and parking_garage_a02, which cold runs 9168, 9174 and 9177 had each shipped one of.

## What answered it

Level Factory 0.220.0 (`patches/patch_lf_fire_escape_ramp.py`): a worldskin pass for each kind -- the fire escape the
darkest tinted metal in the building's props (here `M_Skin_metal_painted_delco_050505`, its ladders' rail), a ramp
the floor family. The re-run of this brief and seed on it is cold run 9343.

## The floor holes

Not reached: the package was refused before frames. apartment_walkup_a01's `broken` hole and floor hatch go to 9343.
