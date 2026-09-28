# Placing the price pylon (proposal, 2026-09-28)

**Status: PLANNED, not built.** Zoo 1.19.0 grew the `price_pylon` species
(2.4 x 0.5 x 6.5 m default, ranges w 1.6-3.4, d 0.3-0.8, h 4.5-9.0; faces at
Blender +/-Y = Godot local +/-Z, width along local X; collision is the whole
slot box). Nothing in a level asks for it yet. This is the Lot change that
will, mapped read-only against Lot's source and cold run 9101's package on
2026-09-28. Re-read every cited line before patching (CLAUDE.md, grounding).

## What the map found, and three corrections

- **The fascia sign is not the model.** `sign_placement` (lot.py ~1240-1274)
  picks a facade by nearest road and `_sign_node` emits a can with no
  collision and no Zoo module. The shipped plan->Godot conversion is
  `sign_facing(yaw) = (yaw + 90) % 360` (lot.py ~1277-1301); the
  `r = -(t + 90)` quoted in PIPELINE_ROADMAP.md ~15985 is 0.69.2's, which was
  itself wrong on E/W facades. `tests/test_site_signs.py` reads the basis by
  ROWS (numbers 2, 5, 8 are local +Z).
- **Lot never placed canopy lights.** Deli Counter derives a `canopy_lights`
  anchor from a volume named `canopy_roof` (`lights.py` `_CANOPY_DECK`,
  `_canopy_anchors`), Zoo builds it into the building's fixtures GLB, and Lot
  only merges the anchors (`merge_lights`). GAS_STATION_SHOP.md's "Lot 0.79.0"
  attribution for `canopy_lights` is wrong; Lot 0.79.0 is the streetlight fix.
- **The path to follow is Lot's kerb-line furniture.** `site_furniture`
  pieces go into `site_spec["cover"]` (lot.py ~3092-3097), `write_site_slots`
  writes them as `prop` slots with `species` (lot.py ~1470-1525), Level
  Factory's `zoo_kit_build.site` job builds them with `--build-kit`, and
  `cover_module_refs` resolves the GLB (lot.py ~1551-1654); `_outdoor_nodes`
  instances it, or a StaticBody box if nothing resolved.

## gas_station_a02 as shipped (cold run 9101, seed 9181)

Building b2 at plan (70, -10), rot 90, footprint x 59..81, y -26..6. Road 0
runs y = -43 (width 10, sidewalk 3): its north (L) band is y -38..-35, the
frontage. The storefront (local S) faces plan EAST, onto the forecourt; the
face toward the road is the stone side wall, which carries the fascia band
(`sign_b2`, wearing Pixelcoat's `sign_fuel_price`). The forecourt is on the
spec itself: pad x 56..102 / y -33..13, canopy at (92, -10) 22 x 13, islands
at (92, -16/-10/-4), PUMPS marker at (83, -10). At the frontage today: lamps,
trees, meters, parked cars in bays L26 and L29-L34 -- and no kerb cut,
driveway or apron (Lot has no vehicle route concept).

## The change (Lot)

1. `site_furniture.py`: `SPECIES["price_pylon"] = (2.4, 0.5, 6.5)`,
   `PYLON_SETBACK = 0.3`, and `plan_pylons(roads, forecourts, markers,
   standing, keep_out, findings)`: for each forecourt, the nearest road with
   a sidewalk to the canopy centre (the clamp projection `sign_placement`
   uses), the kerb on the canopy's side (`_facing_kerb`'s test), station `t0`
   = the canopy centre projected on the road, offset BEHIND the band's back
   edge by `PYLON_SETBACK + w/2` -- a 2.4 m face across a 3 m band leaves
   0.6 m, under `min_passable_gap` 1.2 -- and `yaw_extra = 90` so both faces
   point along the road. `_piece` hardcodes `base: "sidewalk"`; set
   `base: "plate"`. Try `t0 + 0, +/-2 ... +/-12`; accept the first clear of
   cuts (`_clear_of_cuts`), path corridors and building footprints
   (`keep_out`), `standing` (+ `PIECE_GAP`) and markers; else
   `LOT_PYLON_NO_ROOM` (`LOT_PYLON_NO_FRONTAGE` with no band).
2. `lot.py`: `forecourts(site_spec, base_dir)` reads each building's
   `canopy_lights` anchors from its lights.json (`_lights_ref_for`,
   `_place_point`, swap size when `(anchor rot + b.rot) % 180 == 90`) --
   Deli Counter's own gas-station test, and deterministic JSON, unlike the
   GLB solids, which the greybox and themed runs read differently (906 vs
   1742 colliders). Call `plan_pylons` in `assemble` after the furniture
   (~3096) and before `standing` (~3102); extend `cover` and the
   furniture plan. `COVER_MATERIALS["price_pylon"] = "metal_painted"` (the
   genome default, so no `_m` suffix). The slot then flows unchanged and
   resolves `prop_price_pylon_delco_1997_01_w240_d50_h650.glb`.
3. Expected on a02: road 0, L kerb, centre about (92, -33.5), clear of the
   band, the lamps, the trees, the door path and the pumps.
4. Tests in `lot/tests/test_site_furniture.py`: one pylon per canopy; faces
   along the road (`|plate_facing(yaw) . road.along| > 0.99`); wholly behind
   the band; clear of cuts and a door corridor; `base == "plate"`; genome
   dims match Zoo's; an `assemble` test that the slot and its Transform3D
   come out as above.

## Traps the map found

- `LOT_STEP_BLOCKS_A_ROUTE` cannot fire on a prop (it reads walkable
  prefixes and spec paths only), so a pylon across a door path would pass
  silently: the path check has to be explicit in `plan_pylons`.
- Nothing constrains height near roads (no sight triangle, no vehicle route).
- Optional later: the price board would read better on the pylon than on the
  fascia; Level Factory could then give the fascia a brand pack.
