# The backdrop kit, built (roadmap 228, step C; Zoo 1.95.0)

**What was built.** Zoo 1.95.0's two backdrop species, from `backdrop_slots.json`
(a three-slot manifest in Lot's slot shape: two rowhomes at different dims and
a water tower), through `zoo_cli.py --build-kit` inside Blender 5.1.1, theme
delco, style 1.

| module | status | tris | materials | primitives |
|---|---|---|---|---|
| `prop_backdrop_rowhome_delco_01_w600_d1200_h950` | PASS | 48 of 120 | 1 (`M_BackdropRowhome_..._Face`) | 1 |
| `prop_backdrop_rowhome_delco_01_w550_d1200_h800` | PASS | 48 of 120 | 1 | 1 |
| `prop_water_tower_delco_01_w1400_d1400_h4000` | PASS | 372 of 400 | 2 (`M_WaterTower_metal_painted`, `M_WaterTower_Beacon_Lens`) | 2 |

One primitive a rowhome is the point: a band of them is one MultiMesh and one
draw a side.

**The facade,** `facades_x6.png` (the two rowhomes' albedo and emission,
96 x 128 each, enlarged six times): brick with its courses, the cornice band,
the door bottom-left, five windows. The first house's pattern lights one
warm and one TV-blue pane, in the emission alone; the second's lights none.
The brick strip (sides and back) and the tar strip (roof, cornice, stoop)
stand to the right of each facade.

**The first build failed, kept.** All three modules failed `fit_width`,
`fit_depth` and `fit_height`: the rowhome's cornice, stoop and chimney and the
tower's wider cap and beacon stood outside the slot's dims, and Zoo's exact
fit (roadmap 44) holds a module's extents to the slot. `backdrop_forms.body_dims`
now shrinks the body by the cornice's overhang, the stoop's depth and the
chimney's height, and `tower_parts` keeps the cap at the tank's radius and
puts the beacon's top at the slot's top; `test_the_rowhome_stands_exactly_its_dims`
holds it at four dims.

**Not yet seen in a level.** These are species; Lot's bands (step D) place
them and Level Factory composes them (step E). The look at the menu's
stations, and the price, come with those.

## The second kit: the tree and the warehouse (Zoo 1.96.0)

The other recipes' species, from `backdrop_slots_2.json` through the same
build on a draft of 1.96.0, theme delco, style 1:

| module | status | tris | materials | primitives |
|---|---|---|---|---|
| `prop_backdrop_tree_delco_01_w700_d700_h1000` | PASS | 132 of 180 | 2 (bark, vegetation) | 2 |
| `prop_backdrop_tree_delco_01_w400_d400_h600` | PASS | 132 of 180 | 2 | 2 |
| `prop_backdrop_warehouse_delco_01_w3000_d1600_h800` | PASS | 48 of 120 | 1 (`M_BackdropWarehouse_..._Face`) | 1 |

- **The tree** is a trunk box and a twelve-by-six faceted crown; twelve
  around because a fourteen-gon's extents are not its radius (the rooftop
  `water_tank` learned that at exact fit). Two materials, so a belt is two
  draws a module a side.
- **The warehouse,** `warehouse_x6.png`: siding with its seams, the dark
  roll-up door in the left third, the strip of high windows along the top,
  two of the six lit cool white in the emission for this stem. In this sheet
  the lit panes' daytime colour is the rowhome's warm brown; 1.96.0 ships
  them in the cool white's own tint, the one change after the sheet.
- **The census** found no coincident pair on the first run (6 builds): the
  trunk ends inside the crown, and the monitors stand INSET into the roof
  from the start, the lesson the first kit paid for.

## The tree redrawn (Zoo 1.97.0, roadmap 228 step F)

The walker, on cold run 9227's parkland: "those trees in the distance are
a little lazy imo (giant lolipops vs. trees)". `tree_forms_1_97_0.png` is
the redraw rendered by `tools/preview_specimen.py` at four slots: a trunk
that flares at the foot and forks into three limbs under ten overlapping
lobes, the form by the slot's proportions -- a low oak at 8 x 8 x 8 and
11 x 11 x 12, a round maple at 7 x 7 x 10, a narrow elm at 4 x 4 x 9 --
548 triangles of 800, bark and vegetation still two materials.

**The first draft was refuted by its own render, kept here in words:** four
lobes at the limb tips plus three low fillers read as balloons on sticks,
the limbs visible between them. The second draft pulls the limb lobes a
tenth toward the axis, adds fillers at their height and a lower ring under
them (so the limbs vanish into the crown and its foot keeps daylight above
the fork), and displaces each lobe by a sixth of its radius; that reads as
a crown. The second kit rebuilt PASS and census-clean (`result_*.txt` in
`patches/zoo_backdrop_3/`); Lot 0.110.0 lays the belt in clusters of mixed
forms. The walker's eye on a level is the gate that remains.

## Instruments

- `backdrop_slots.json`: the manifest.
- `backdrop_test_kit.built.json`: the build's index, as Zoo wrote it.
- `facades_x6.png`, `facade_*_albedo.png`, `facade_*_emission.png`: the paint.
- The build command, from a Zoo checkout:
  `blender --background --python tools/zoo_cli.py -- --build-kit docs/findings/backdrop_kit/backdrop_slots.json --theme delco --style 1 --out <dir> --no-blend`.
