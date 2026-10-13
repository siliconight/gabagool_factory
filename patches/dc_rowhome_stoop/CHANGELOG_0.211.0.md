## [0.211.0] - a rowhome Empty stands three steps up, on a stoop

**Factory roadmap 240's rowhouse front.** The walker's comps, a Philadelphia rowhouse street: "three or
four steps up to each door, with iron railings; the first floor stands above the sidewalk" (the
factory's `docs/reference/PHILLY_STREET_COMPS.md`). Philadelphia's own guide says it without a number,
"Most existing rowhouses are a few steps up from the street" (City Planning Commission, *Philadelphia
Rowhouse Manual*, 2008, p. 13); the residential code fills the blank, a riser at most 7 3/4 in and a
tread at least 10 in (IRC R311.7.5). The design: the factory's `docs/proposals/ROWHOUSE_STOOP.md`.

- **`stoop.py`** (new, pure): the stoop in front of the front door. Three risers of 7 in on 11 in
  treads (0.1778 m, 0.2794 m), a 0.9 m landing, 1.5 m across. **The contract decides its collision:**
  a 7 in riser is 1.7 times `unassisted_step_max_m`, so a collider a step is a wall to the contract
  body. As the stairs do, the stoop is walked on ONE ramp whose top face is the nosing line -- through
  the landing's front edge and each tread's, meeting grade a tread past the bottom riser, its head
  ending on the landing's edge -- at 32.5 deg. A block stands under each tread but the lowest, one
  riser short of it. 1.74 m deep, ramp included, inside Level Factory's 2.0 m terrace frontage; four
  risers would not fit with this landing (2.02 m).
- **`empty_rowhome(stoop=3)`**: the ground storey's front door and window rise together, so the door's
  threshold (the slab's top plus its sill) is three risers above grade -- a 0.3834 m sill on the 0.3 m
  slab. `stoop` names the stoop for the build, and the palette declares the concrete it is made of. 0
  is the house as it was. All twelve rowhomes take three (the comps' "each door"), written once
  after `EMPTY_ROWHOMES`; their specs are the presets' output again.
- **`_stoop`**, in the facade build after the exterior: the landing and treads as visuals recorded as
  `prop` slots in concrete (the art pass dresses them as it does a volume, `fit.collision` none), and
  the landing, the blocks and the ramp as convex colliders. The spec type and the schema carry `stoop`.

**Built:** build.py --all, 146 shells. Each of the twelve rowhomes, read off its GLB: `stoop_landing`, `stoop_tread_1` and `stoop_tread_2` (visual, three `prop` slots in concrete) and `stoop_landing_col`, `stoop_under_1_col` and `stoop_ramp` (convex); on gs_empty_rowhome_a the ramp is 32.47 deg and 0.9936 m long, its top face's head on the landing's front edge (0.5334 m up, 0.900 m out of the front face) and its foot at grade 1.738 m out; every front door keeps its leaf and its collider, a sill now under it; the manifests move their build time and the twelve's spec hash

**Suite:** 1,407 passed; `test_stoop.py`, 9 checks, 8 of them failing on 0.210.0's houses with `stoop.py` beside them (the ninth holds only the code's limits). The suite caught `test_empty_door_leaf._doors` reading a sill as a window -- the raised front door has one -- and it now takes a door as an opening with a lintel and no pane (`patches/patch_dc_door_leaf_raised.py`)
