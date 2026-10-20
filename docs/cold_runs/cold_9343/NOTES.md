# Cold run 9343 -- 0 interventions; precinct_yard_001, seed 9708, shipped: the fire escape skinned, a broken floor and a floor hatch in a package

**What it was for.** 9342's brief and seed again, on Level Factory 0.220.0 (aa217f7), which gives Deli Counter's
legacy fire escape and its vehicle ramp a worldskin pass (`patches/patch_lf_fire_escape_ramp.py`;
`docs/findings/base_greybox_owners/`). Two questions: does the package ship, and do apartment_walkup_a01's `broken`
hole and floor hatch -- roadmap 265's two causes not yet seen in a package -- read in it.

**Tools:** Deli Counter 0.236.1, Level Factory 0.220.0, Zoo 1.114.0, Lot 0.125.0, Lux 0.78.0. Staged from 9342
(`stage_batch.py`), seed 9708 named.

**Every leg ran, `INTERVENTIONS: 0`** (journal 0, unattributed files 0), read after `cold_run.py --end`.
- **Shell:** 3 candidates, all distinct; 0 blockers of 74 findings; seed_9708's lot 9342's -- airport_terminal_a01,
  apartment_walkup_a01 (b2), freight_terminal_a01, large_warehouse_a03 and the 12 Empties.
- **Art:** 0 blockers of 104 findings.
- **Export:** exit 0. `greybox skin: 0 surface(s) on a greybox material (none), 0 of them slabs; any one is refused`
  -- 9342 refused on 2. The light bake as 9342's: 379 models and 149 primitive meshes, 4,632 users, 75.3 s.
- **Findings 104 -> 104** against 9342, no code moving.

**The two passes, off the package's import log:** apartment_walkup_a01's base `fire escapes: 2 surface(s) skinned on 2
mesh(es), 0 mesh(es) left flat; darkest tinted metal M_Skin_metal_painted_delco_050505 (0.143)` -- the metal its
ladders' rails wear, as predicted; the other 15 bases `no fire escape in this base`. `ramps:` no vehicle ramp in any
of the 16 bases, as the census said (this lot draws no garage).

## Frames (`holes_9343.jpg`)

The level's light and the inspection light (`look_shots.py --inspect studio`), from a walk copy of the package
(`tools/walk_export.py`). Godot frame for b2: x = building x + 52, y = building z, z = -(building y) - 30
(`site.tscn`: b2 at `Transform3D(1,0,0, 0,1,0, -0,0,1, 52,0,-30)`); rooms off the build's `gameplay.json`.

- **The broken hole, from the bedroom** (`hole_from_bedroom_n`, from the hole's north side under the ceiling): a torn
  ring of floor and framing round the 2 x 2 m drop, jagged all the way round, the kitchen's table seen through it.
  Still square in plan -- the teeth stand round a square cut -- which the walker's "some reason other than a
  perfectly cut square" may or may not accept: for the walker.
- **From the kitchen** (`hole_from_kitchen`): the drop ceiling broken back round a dark opening, shards hanging into
  it.
- **The spoil** (`spoil_from_kitchen`): planks with the bedroom's tile on them, bars and fragments on the kitchen
  floor -- sparse at play distance, as 9340's.
- **The floor hatch, from the office** (`hatch_from_office_e`, side-on from the east): a square opening in the
  carpet, the lid standing open on its north edge, the garage bay's floor below. **The frame reads dark brown, not
  safety yellow.** Measured, not guessed: the shipped module (`prop_roof_hatch_delco_04_w166_d166_h3_ffloor.glb`)
  carries the yellow in its frame's vertex colours, (0.863, 0.638, 0.040) on the 3 cm ring, and the worldskin draws
  them (`2 material(s) draw vertex colour`); but the theme's skin puts the frame and lid on `M_Skin_metal_delco`,
  whose texture is `metal_rusted_street_albedo`, mean sRGB (0.451, 0.315, 0.208) -- yellow times rust is about
  (0.39, 0.20, 0.01). Zoo's floor form assumed the white base it paints with. The hinge, on `metal_bare`, takes the
  neutral texture (mean 0.94). Left as roadmap 265's next step.
- **From the garage bay** (`hatch_from_garage_s`): a clean rectangular opening in the ceiling grid.
- **The fire escape, from the yard** (`fire_escape_from_yard`): a dark painted steel deck and guard over the rear door
  with its drop ladder to the ground; a slab, not a grating -- the legacy fire escape's boxes, now skinned.

Two first stations were blocked and are kept out of the sheet: from the bedroom's east side a carton stack stands
between the camera and the hole, and from the office's south side two carton stacks 0.69 and 0.89 m south of the
hatch hide it; no prop stands over either opening (the slots, checked).

## The price, inferred

Not priced in the engine: 9342 shipped nothing to compare against. Off the modules (`docs/findings/hole_causes_265/
glb_draws.out.txt`): the broken hole is 5 submissions (the framed edge 2, the spoil with its tile 3), the floor hatch
2, so a station that sees all three adds 7 draws -- about 0.03 ms at 9062's 3.5 us a draw, against the cut hole's +9
measured inside the 0.05 ms floor on 9341. An inference from a measured neighbour, not a measurement.
