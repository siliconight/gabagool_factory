# The walker's walk of cold runs 9305-9307, 2026-10-14

The walker walked the three newest levels before a stakeholder demo at 21:00 and sent frames from the debug walk
(`walker_*.png`, `walker_*.webp`, theirs, F3 overlay on). Each finding below: where, what it is, whose, and what is
known. "Traced" means read off the tool's own spec or code; "seen" means only the frame.

**The demo plan changed at 17:31.** The walker: "we can also ditch these in favor of fresh runs that address all my
callouts". The contained findings were fixed in the tools and run fresh before 21:00 (cold runs 9308 urban, 9309
gas, 9310 restaurant). The copies walked here were moved, not copied, to `_runs/demo_fallback_2026-10-14/` as the
fallback. The structural findings (5, 6, 7-9) are design work and come after the demo.

| # | fixed in | how |
|---|---|---|
| 1 | Zoo 1.111.0 (9176f8d) | the room behind the goods glows at `ROOM_GLOW` 90/255 of its paint; `EMISSION` stays 2.2 |
| 2 | Level Factory 0.211.0 (5c67868) | one dark plane under the backdrop, 30 m past it, 0.10 m under the plate |
| 3 | Zoo 1.111.0 (9176f8d) | each bay's stock turned to the side its drawers face |
| 4 | Zoo 1.112.0 (8d1e2a4) | a door under its building's band says the trade; the walker chose it |

**Seen, 9305 against 9308 at the walker's own spots** (`fixes_9305_9308.png`, `fixes_1_3_9305_9308.png`, the
stations in each frame's caption):
- **2:** the blue void beyond the east fence is dark ground under the backdrop's houses.
- **4:** the box over the pharmacy's door reads PHARMACY under the DOC'S DISCOUNT DRUGS band. Its colours are the
  trade sign's own colourway, cream on navy, where the door had worn the band's yellow on black -- the walker's
  call whether it should match. The deli's door paints DELI and the gas station's OPEN 24 HOURS, cream on green
  (read off the painted textures in 9308's and 9309's packages).
- **1:** the grocery's backdrop no longer clips to white; the shelves and the coloured goods read. It is still a
  flat painting up close.
- **3: seen fixed in the inspection light** (`cubicles_9305_9308_inspect.png`). In the level's own night light a
  CRT's screen and its back read alike, and a brightened crop did not settle it. So `tools/look_shots.py` gained
  `--inspect studio` at the walker's ask, "a tool to make the area brighter for checking things": a shadowless
  work light over the camera's shoulder, every frame named INSPECT_ so none is read as the level's look. At the
  same two stations, every CRT in 9305 shows its black back to the aisle with its keyboard hidden against the
  panel; in 9308 every screen and keyboard faces the aisle, where the chair is, on both banks.

| # | level | finding | whose | status |
|---|---|---|---|---|
| 1 | urban_row_001 | the corner grocery's window reads as bars and dots up close | Zoo `shop_panes` | traced |
| 2 | urban_row_001 | at the fence, the ground ends and the backdrop stands on nothing | Level Factory backdrop | traced, seen |
| 3 | urban_row_001 | the cubicles' computers face the panel | Zoo `cubicle_forms` | traced, a bug |
| 4 | urban_row_001 | the pharmacy's name twice, band and door box | Lot / Deli Counter / Zoo | traced, a taste call |
| 5 | urban_row_001 | the deli's basement wall stops in a big opening | Deli Counter | open |
| 6 | urban_row_001 | a hole in the deli's ground-floor ceiling | Deli Counter (authored) | traced, by design, undressed |
| 7 | restaurant_row_001 | a big gap in the office's stair enclosure | Deli Counter stairs | open |
| 8 | restaurant_row_001 | the office's stair core "looks wrong in general" | Deli Counter stairs | open |
| 9 | restaurant_row_001 | the upper flight's underside stops in mid-air; it "should come down all the way to the ground" | Deli Counter stairs | open |

## 1. The corner grocery's window (`walker_69..71`, one of them)

`gs_cornershop_d`, the green-awning corner, at about 3 m from its glass. Its ground-floor bays are Zoo's
`shop_panes` painted atlas in the `shop_grocery` cell, lit from inside (Deli Counter 0.218.0; Zoo 1.107.0). There
is no interior: the corner blocks are facades. `shop_panes.EMISSION` is 2.2, brighter than a home's window (1.6) on
purpose, and at night the pale shelf backing blows out to near-white, so the painted goods read as dots on bars.
Already queued as "the cool shops glow nearly white".
- **Proposed, cheapest first:** the glow to about 1.2-1.4 and warmer; a darker backing in the painting; a redrawn
  pane with depth (aisle, counter, sign); a shallow real interior (draws, priced first).

## 2. The plate's edge (`walker_71`/`72`; `edge_9305_sheet.png`)

The walker at (91.1, 1.6, -20.4) facing east, the fence (`cover_173`, Zoo's chain link, 101 m long) at x 94.75.
- **Traced:** `site_backdrop.tscn` holds the backdrop's rowhomes and its water tower, 25 MultiMeshes, and no
  ground. The plate's thirteen `Ground_*` pieces stand at x -84 to 82 on a 171 x 102 m plate.
- **Seen** (`edge_9305_sheet.png`, shot on 9305's workspace package): from 26 m up the plate's ground ends in a
  straight line and the rowhomes beyond stand on nothing, the sky and fog colour below and between them. From the
  road the fence and the buildings hide it ("fine from a distance"); at the fence, one looks over it.
- **Proposed:** Level Factory's backdrop (roadmap 228, step E) lays a ground under itself from the plate's edge out
  past its last row: one mesh, one draw, outside the bake like the rest of the backdrop.

## 3. The cubicles' computers (`walker_73`)

The office's `CubicleBank` (Zoo). The recipe's docstring promises stock "facing that band's sitter", and
`_surface_stock.plan_surface` defines `facing` 0 as "they stand at -Y". `cubicle_forms` puts a band's surface on
the `-out` side of its spine -- its drawer fronts face that way, correctly -- and hands the stock
`3.141592653589793 if out > 0 else 0.0`, which turns every item's front toward the spine, on both sides of every
bank.
- **Proposed:** `0.0 if out > 0 else math.pi`, with a test that reads each region's facing against its drawer
  fronts; a test already pinning the inverted value would change with it.

## 4. The pharmacy's name twice (`walker_69..71`, one of them)

`pharmacy_a01` at (4, 0, 2.51). Lot's band sign (`sign_b1`, at 3.6 m, the big board) and Deli Counter's door box
(named by Zoo's `storefront_names`, the small lit sign over the door) both read DOC'S DISCOUNT DRUGS. That is the
walker's own 2026-10-06 choice (roadmap 187, option A: "one name list on both signs"), now seen on a one-storey
front where the two stack.
- **Proposed, the walker's call:** where the band names the shop, the door box carries the trade or a hours/OPEN
  sign instead (PHARMACY, Rx, DELI, OPEN).

## 5. The deli's basement wall (`walker_74`)

`deli_a01`, story -1, the walker at (-68.8, -1.7, 1.1). The basement's two partitions each carry a 1.25 m door and a
1.4 m `breach` opening. Not yet traced: whether what the walker saw is a breach and how one is built.

**Traced, 2026-10-14 19:30: not the breach. The partition stops 7 m short of the outside wall at both ends.**
The spec, in its own metres (`deli_counter/specs/deli_a01.json`):
- The basement is 38 x 28 m, x -19..19. Four rooms divide it: `basement_corridor` and `cold_storage` west of x 1.0,
  `utility_room` and `basement_vault` east of it, one pair either side of y 1.0.
- So the wall along X at y 1.0 divides rooms that meet across the full width, x -19..19. It is built x -12..12.
- That leaves 7.00 m open at each end. On the west, `basement_corridor` opens into `cold_storage`. On the east,
  `utility_room` opens into `basement_vault`, the objective room, marked `fortifiable`, beside the 1.4 m
  `vault_side_breach` that was meant to be its way in.
- 9308's `site.tscn` stands the deli at Godot (-51, 0, -2.51), unrotated. So the walker at (-68.8, -1.7, 1.1)
  stood at plan (-17.8, -3.6), in `basement_corridor`, 4.6 m south of the partition with its west end 5.8 m to
  the east. That is the west gap. The door they outlined fits the corridor door, at x -8.4, 3.6 m along the wall
  from its end.

**Authored so from the first version:** Deli Counter 0.80.0 (f54ebfee, 2026-07-19, the pvp_heist configs) wrote this
partition at -12..12. The other basement partition overshot the footprint at -16..16 and was clamped by 0.83.3
(1c344a8d, "clamp interior partitions to footprint"). Nothing extended this one.

**How far it reaches** (`partition_gaps.py`, `partition_gaps.out.txt`): open stretches over 1 m, where two rooms meet
past a partition's end, number 59 in 31 of the 446 specs.
- The same two 7 m gaps stand in every deli: deli_a01, a02, a03, cr_deli, night_deli, corner_deli_heist_01, and
  Level Factory's per-candidate copies.
- Others read as designed openness and are for a person to sort: the parking garages' decks, the warehouses'
  north aisles, office's executive lobby.
- The census names no cause.

- **Proposed, Deli Counter's:**
  - Run the deli family's partition to the walls, so the vault is entered by its door and its breach.
  - Add a check that refuses a partition stopping short of where its rooms meet, unless the spec names the gap as an
    opening. That is the part that generalises.
  - Both move the navmesh and the fights, so they go out through the graders with the moved fields read.
- **The walker's call first:** whether the deli basement was meant to be open at its ends.

## 6. The hole in the deli's ceiling (frame with the taskbar at 17:25)

`deli_a01`, the walker at (-43, 1.6, 3.6) looking up. Authored: `vertical_links` carries a `floor_hole` on story 1 at
(8.0, -4.0), 2.2 x 2.2 m, role `vertical_attack_angle` (Deli Counter 0.80.0, 2026-07-19, the heist configs) -- a
sightline to shoot down through. It is built as a bare cut through the drop ceiling and the slab, so it reads as
missing geometry.
- **Proposed, a design call:** dress it as deliberate (trim and a guard rail upstairs) or as damage (broken tiles,
  a ragged edge); the gameplay role stays.

## 7, 8 and 9. The office's stair core (`walker_75`, `walker_76`; the third frame was not kept on disk)

`office` in restaurant_row_001: one switchback stair at the shell's centre (0, 0), story 0 to 2, 3.6 m storeys,
`cut_slabs`, run 4.7. From beside it a tall gap in the enclosure shows the flight's sawtooth underside
(`stair0col_under_0_15`); from inside, partial walls, solid wedges under the flights, a handrail across the void and
raw slab cuts. From below at (56.6, 1.6, 2.7) the second flight's solid underside (`stair0col_under_1_11`, its top
at 3.60) ends in a level bottom edge in mid-air, over open floor -- the walker: "bottom of this stair should come
down all the way to the ground". Not yet traced. The three read as one finding: a stair core built from per-step
boxes, with no enclosure, soffit or rail a person would expect.

## The work light, L (the walker's ask, 20:10)

After the inspection light settled finding 3 in frames (`tools/look_shots.py --inspect studio`), the walker asked for
the same thing while walking: "yes add a work light key to the walk copies".
- **`tools/walk_work_light.gd`:** L toggles it, off at start. A shadowless key light over the camera's shoulder and a
  flat white ambient, the same constants as `--inspect studio`. The level's fog, glow, colour adjustment and
  tonemap are set aside and Lux's grade layer is hidden; the debug overlay and the HUD stay. A banner across the top
  says nothing on screen is the level's look. L again puts back every value it touched. Debug builds only.
- **`tools/walk_export.py`** copies it into every walk copy it assembles. The scene's `load_steps` is now counted off
  the scene by `_walk_scene`; it had been typed, under a comment saying "4 ext + 1 sub" while the scene loaded five.
- **`tools/walk_add_work_light.py <walk copy> ...`** adds it to a copy assembled before, in place, with no new
  import.

**Proven:**
- `tools/walk_work_light_selftest.gd`, headless: 31 checks on a night-graded environment, every value back on the
  second L (`work_light_selftest.out.txt`). A mutant that forgets one value fails exactly that check, exit 1
  (`work_light_selftest_mutant.out.txt`).
- `tools/test_walk_export_work_light.py`: 6 fail on the walk_export.py committed before, 6 pass
  (`work_light_wiring_prove.out.txt`).
- In a real level (`work_light_probe.gd`, `work_light_probe_9308.out.txt`): a scratch walk copy of 9308's package,
  headless, with the probe autoloaded into the scratch copy only. The light rode `/root/_walk/Player/Camera`, and
  the level's one Environment went fog, glow and adjustment off, ACES at 1.05 to linear at 1.0, sky ambient at 0.9
  to white at 0.5. The second L restored every value exactly. No engine error.

**Found on the way:** `tools/cold_drive/wire_sky.py`, which the cold drive runs on every fresh walk copy, asserted
the scene's head read `load_steps=7` and wrote 8. The work light made a fresh copy's 8, so it refused every copy --
silently, since the drive pipes it through `tail`. It refused the scratch copy above, whose probe therefore ran
without the sky cycle. It now counts too. `tools/test_walk_add_work_light.py` fails on the committed wire_sky.py
with that assertion and passes on the patched one (`work_light_wire_sky_prove.out.txt`).

**Not yet in tonight's copies, by design:** the demo's three walk copies and their fallbacks were not touched before
the demo. After it: `python tools/walk_add_work_light.py _runs/walk_export_urban_row_001
_runs/walk_export_gas_block_001 _runs/walk_export_restaurant_row_001`, then a headless load of each. Not seen in a
window yet: the light's look on screen and the banner's place in the frame.

## Kept for what is left

The demo's three levels are what findings 5-9 and roadmap 252's price are worked against. They are named here so
the retire keeps them while this finding is open:
- `workspaces/cold-9308-ws`, urban_row_001: the deli's basement (5) and ceiling (6), and the ground under the
  backdrop (252);
- `workspaces/cold-9309-ws`, gas_block_001;
- `workspaces/cold-9310-ws`, restaurant_row_001: the office's stair core (7-9).

Roadmap 250 carries the open findings, with 251 and 252 beside it.
