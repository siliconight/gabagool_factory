# Which base geometry has no skin: the library's greybox read against its owners (2026-10-20)

**Found by cold run 9342** (precinct_yard_001, seed 9708, 0 interventions; `docs/cold_runs/cold_9342/`), stopped
at the export. Level Factory's greybox census refused the themed package on two surfaces:

    Bake/Site/b2/GreyboxBase/FIREESCAPE_REAR_FIRE_ESCAPE_1       on gb_floor   7.63 m2
    Bake/Site/b2/GreyboxBase/FIREESCAPE_REAR_FIRE_ESCAPE_1_RAIL  on gb_floor   5.07 m2

`b2` is apartment_walkup_a01, and the two are its legacy exterior fire escape: Deli Counter's `_fire_escapes` (ladder
spec s9) builds a deck a served storey, its outer guard and a stub down to the deck below as boxes in the floor role,
with their own colliders. No kit module stands in for one and no worldskin pass dressed one.

**It is not new, and it is not the floor-hole change the run was there to prove.** Cold run 9172 shipped apartment_walkup_a01
on 2026-10-06 and its export log reads `greybox skin: 2 surface(s) on a greybox material (gb_floor 2); slabs 0` -- the
census refused on slabs only then, and reported these. Level Factory 0.218.0 made it refuse any greybox surface, on
the claim that every class it had reported had an owner; the evidence was the packages exported since 2026-10-10, and
no lot in that window drew a shell carrying one. 9342 was the first package since to draw apartment_walkup_a01.

## The census: every base at once

A cold run finds an unowned kind only in the buildings its lot happens to draw. `census.py` reads every built base in
Deli Counter's library (`deli_counter/build/<spec>.glb` and `.slots.json`) node by node: a node with a primitive on a
`gb_*` material is a collider, a slot's own node (`themed_tscn.owns_node`, the question the base strip and the
composer ask), or one of the worldskin passes' name tests mirrored from `zoo_worldskin.gd` -- whose prefixes it reads
from that file, failing on one that is not there -- or else UNOWNED.

**The control** (`census.py --spec` on 9342's four buildings): UNOWNED exactly the two surfaces above, on
apartment_walkup_a01, and nothing on airport_terminal_a01, freight_terminal_a01 or large_warehouse_a03 -- the engine's
census, to the surface.

**Where the two instruments disagree, and why the census can over-report but not miss.** Its owned counts run high:
airport_terminal_a01's build GLB carries 144 slab nodes and 20 ladder rails and rungs, the package's `site_base.glb`
72 and 19, and the engine's log skins 72 and 19. The package's base strip also drops, by geometry, every visual node
inside a themed roof's box (`portable_building.roof_covered_nodes`): there, the top slab's 72 `gb_ceiling` tiles and
the ladder's top rung, `ladder0_rung_0_17`, which stands at 5.25 m inside the roof slab's 5.20-5.50 m. The census
asks only the slot-name question, so a node dropped that way can only make it report a surface the package does not
carry, never hide one it does. What it cannot
see is a kit gap: it assumes every slot resolves to a themed module, so a slot left on its greybox fallback is not in
it. The engine's census still refuses one.

**The library** (`census_library.out.txt`, `census_library.json`; 158 specs, Deli Counter 0.236.1): 480 surfaces in
17 specs own nothing. Read against Level Factory's own themed pool (`building_library.themed_report`: 102 of the 127
indexed shells fit):

| kind | where | can a themed lot draw it? |
|---|---|---|
| `FIREESCAPE_*` deck, guard (`gb_floor`) | apartment_walkup_a01; rowhouse_raid | apartment_walkup_a01 yes; rowhouse_raid no (empty slot coverage) |
| `ramp<n>` (`gb_ramp`), Deli Counter's `_ramps` | cr_garage, parking_garage, parking_garage_a01, parking_garage_a02 (two); cbp_town_finale, foundry_heist_vertical | the four garages yes -- five ramps; the other two no |
| whole-wall `ext_<n>_<side>`, `int_<n>_<n>`, `parapet_*` (`gb_wall`) | 12 older specs | no: ten have an empty slot coverage, two are demos the library does not index |
| `PLATFORM_MAIN_CATWALK` and its rails (`gb_floor`) | warehouse | no (empty slot coverage) |

**The garages were the next refusal.** Cold runs 9168 and 9177 shipped cr_garage and 9174 parking_garage_a01, each with
`greybox skin: ... gb_ramp 1` -- reported, before 0.218.0. Any of the four would have been refused the next time a
lot drew it.

## What answered it

Level Factory 0.220.0 (`patches/patch_lf_fire_escape_ramp.py`, its records in `patches/lf_fire_escape_ramp/`): two
worldskin passes on the slab pass's shape. What each wears is a call, made 2026-10-20 and meant to be changed:

- **A fire escape** takes the darkest tinted metal in the building's `prop_` modules -- the walk-ups' fire escapes are
  Zoo's `fire_escape`, black painted steel -- and the theme's rust only when no tinted metal is there. On 9342's
  apartment_walkup_a01 that is `M_Skin_metal_painted_delco_050505`, the metal its ladders' rails wear; its packs carry
  no rust.
- **A ramp** takes the floor family the slabs' reveal takes, the roof as the fallback: a ramp is a floor, as a tread
  is. The name test is exact (`ramp` and an index).

Neither changes a draw: each greybox box is one mesh of one surface before and after, and the texture it borrows is
already resident. After the release the census reports the two kinds as owned (`census_after_0220.out.txt`).

## Not measured

- A kit gap (above).
- How either looks in a level, and what it costs there: the re-run of 9342's brief and seed on 0.220.0 is that
  measurement.
- Level Factory's own `lf_` buildings: none was built into `deli_counter/build` when this ran.
