# The slice's look: gaps and fixes, newest first

Judged by `RUBRIC.md`. The slice is `docs/vertical_slice/` (Delco Ave: a gas station, a bank and the library's draw).

## 2026-10-29 -- slice 3: a string course at every floor line -- FIRST ATTEMPT NOT SHIPPED

Under the studio light the bank's flank showed a dark groove at its floor line: Deli Counter stops a storey's walls
under the slab above and the slab stops at the walls' centreline, so every floor of every building that is not an
Empty carries the slab's edge recessed half a wall -- the parapet's defect one storey down. A string course covers
it: Patina orders a band at each floor line, Zoo builds it 6 cm proud. `workspaces/slice-3-ws`: the bank 64 bands,
the card shop 38 (12 refused at its openings). Priced against slice 2 (`perf_s3_*`): **draws median +0, largest +0;
p95 median -0.013 ms, largest +0.272 ms (floor 0.391 ms)** -- free.

**Verdict: worse in one way, invisible in another, so not shipped** (`sheet_s2_s3_inspect.png`; the bank flank at full
resolution). The continuous groove became a DASHED line: one band a 2 m slot, each band's ends bevelled, and the
recessed edge showed through every joint. And the band, in the covers' concrete, vanished into a concrete wall --
no colour contrast, which the walker named. Second attempt (slice 3b): Patina joins the bands into runs, split only
where an opening refuses a slot; Zoo builds them in the stone trim the Empties' lintels and sills use, a cream band.

## 2026-10-29 -- the draw budget: what the over-budget view submits (MEASURED, not yet acted on)

Slice 2's price put two headings over the 2,000-draw budget in both arms, both from the train yard looking back down
the avenue (`extraction_11` at (92, 1.6, 22.41) and `longest_sightline`, yaw 90). `station_draws.gd` (beside this
file; level_factory's `station_census.gd` method, attribution by subtraction, at a given eye and yaw) on a copy of
slice 2's package, `station_draws_s2_ex11*.json`:

- **Its total does not match the harness's** -- 3,555 draws where the price reported 2,370 at that station and yaw.
  The eye or the settling differs (the harness places its camera at a station's position plus `EYE_H`; this probe
  at the reported position). **Only the SHARES below are evidence until the totals agree.**
- **A noise floor of ~100 draws**: hiding almost any small group -- the warm-up, the occluders, one ground tile set
  -- drops 97-114. Rows under ~150 are not contributions.
- Under `Bake/Site`: the four buildings 1,664; the far-side terrace (`blocker_*`: the 12 Empty rowhomes, three
  instances each, 36) 1,061 -- **about 27 draws an Empty, at 50-100 m**; the street props (`cover_*`, 193) 1,063,
  about 5 each; `LuxClub` 609 -- Lux's neon, room-ambient and club rigs, whose cost in GL Compatibility is the extra
  light pass each lit mesh takes. Control: everything hidden, 50 draws.

**Levers, owners, not yet priced**: distance detail on the Empties' small parts (visibility ranges; Level Factory's
export or Zoo's module), the reach of Lux's rigs from the street (Lux), and the street props' material count (Zoo).
Next step: make the probe's total agree with the harness, then price one lever at a time. Tried and retracted
(both kept in `station_draws.gd`'s header): settling 30 frames, and taking the maximum over a 60-frame window as the
harness does -- the total stayed 3,555, so occlusion settling is not the difference; nor is the scene (the price tool
copies the same export package). Why the totals differ is still open.

## 2026-10-29 -- slice 2: debris where it gathers, a roof that drains through its parapet -- SHIPPED

`workspaces/slice-2-ws`: slice 1's batch and seed with Patina and Zoo pointed at the changes' clones (the same lot,
the same candidate). Shipped as Patina 0.34.0 (67470dd, `patches/patch_patina_scupper_debris.py`) and Zoo 1.147.0
(7abde5e, `patches/patch_zoo_scupper.py`).

- **Debris** (`scatter_probe.py` on slice 2's manifest): open ground 4,547 -> 811 pieces, 11.1 -> 2.0 per 100 m2;
  plate-wide Clark-Evans R 0.72 -> 0.51; sidewalks and wall bases unchanged. Within 2 m of an edge 605 -> 413,
  beyond 10 m 1,585 -> 92. **Verdict: reads better** in the street frames -- the road and the lots are no longer
  sprinkled, and what is left sits at kerbs and walls -- though at street distance a single frame shows it less than
  the numbers do.
- **Scupper**: the bank's gutters 64 -> 0, 10 headed downspouts; the white line 1.4 m below the bank's top is gone and
  a conductor head shows at the parapet (`sheet_s1_s2_inspect.png`, bank_front). **Verdict: reads better**, small.
- **Price** (`perf_s2b_*`, A / subject / A, slice 1 the control): **WATCH over 53 headings -- draws median +0,
  largest +1 (control floor 21); p95 median +0.034 ms, largest +0.640 ms (floor 0.977 ms).** The change is free;
  the WATCH is two headings that stand near and over budget in BOTH arms at identical counts: extraction_11 yaw 90
  (2,312 draws, 10.77 ms p95) and longest_sightline yaw 90 (2,370 draws, 10.89 ms). The first price (`perf_s2_*`)
  is kept: its controls disagreed by 60 draws and 2.48 ms and it said so; this one was taken on a quiet machine.
- **New gap from the price: the slice itself is over the 2,000-draw budget at two headings.** Pre-existing in
  slice 1. Owner to find (the long sightline down the avenue is the obvious suspect: every building, the far-side
  terrace and the backdrop in one view). Ranked with the looks; a slice that does not hold its frame is not done.

## 2026-10-29 -- slice 1, the first build, judged

**What was built.** `workspaces/slice-1-ws`, Level Factory 0.268.0's `D01_delco_avenue` from its clone, Deli Counter
0.292.0's flush parapet from its clone, everything else at HEAD: seed 9003, candidate seed 9104 picked; the lot drew
gas_station_a02, bank_branch_a02, card_shop_a01 and train_yard_a01 (`docs/vertical_slice/`). Frames:
`frames/s1_level`, `frames/s1_inspect` (look_shots' derived cameras), `frames/s1_street_*` (`shoot_street.py`).
**Retracted, kept:** the first street stations stood at Godot z 0, behind every building; the avenue is at z 30.6
(the candidate's `site.markings.json`). Those frames were the buildings' backs and are re-shot. The re-shoot from the avenue (`frames/s1_street_*`, stations re-derived): mean brightness 22-40 of 255 in the
level's light, 57-84 under the studio light.

**The gaps, ranked by the rubric** (a defect before a missing detail; then share of frame x frames x cost):

1. **The open ground reads generated -- MEASURED.** `scatter_probe.py` on the surface-dressing manifest: 4,547 of
   6,111 pieces lay on 41,051 m2 of open ground (11.1 per 100 m2, Clark-Evans R 0.77, flat out to 10+ m from any
   edge), the wall bases where a street's debris collects held 64 (a near-grid, R 2.48), and weeds and rubble were
   drawn in equal shares in the middle of the asphalt. Owner: Patina's planner. FIX IN FLIGHT (below).
2. **The evening is black.** At the brief's `evening`, facades, ground and the far side go to near-black (several
   street frames under 5 of 255 mean); only the canopy, a few windows and the sky read. Legibility is a defect by the
   rubric, but the time of day and its mood are the walker's: **left for the walker**, with the studio-lit frames
   beside them to show what is there.
3. **Blank walls.** The bank's flank and the card shop's back are 20-30 m planes with one or two openings. Owner:
   Zoo / Deli Counter (facade layering). Next after the debris.
4. **Texture scale -- RETRACTED, measured from source.** "The gas station's stone reads at about twice real size"
   was a read of one frame, not a measurement. Pixelcoat's `fieldstone_delco` is 2.5 m a tile at 6 aggregate cells,
   about 0.42 m a stone, and Zoo maps it by `meters_per_tile` (`bpylayer/materials.py`); a fieldstone wall's stones
   run about 0.15-0.45 m. Not a defect.
5. **The white gutter line under the parapet.** FIX IN FLIGHT (below).
7. **The street trees read as generated -- seen from the corrected stations.** In seven of nine street frames a
   tree stands in the foreground or mid-ground as a silhouette of flat plates on a bare trunk. Of everything on the
   avenue it is the single most "computer made" shape, and it is in nearly every view. Owner: Zoo (the street
   tree species). Ranked second after the debris, before the facades, because of how many frames it is in; a
   redraw is a large change and is planned, not rushed.
6. **A train yard on Delco Ave.** The seeded draw's fourth building; plausible as "random", odd beside a bank.
   **Left for the walker** (a candidate pick, or a fabric list for D01).

## Fixes in flight, to be proven on slice 2

- **Debris gathers at edges** (Patina 0.34.0, `_scratch/patina-scupper`): on open ground (`ground` in a
  `play_space`) a candidate survives with probability max(0.06, exp(-d / 2.5 m)), d the distance to the nearest
  building, wall base or kerb; weeds and rubble only within 2 m of one; `very_high` zones (Lot's perimeter) and
  gameplay paths untouched. Re-planned on slice 1's own inputs: open ground 4,547 -> 811 pieces (11.1 -> 2.0 per
  100 m2), plate-wide R 0.72 -> 0.51; within 2 m of an edge 605 -> 413, beyond 10 m 1,585 -> 92.
  Tests: tests/test_debris_edges.py; suite 408 passed, 11 skipped.
- **No gutter under a parapet** (Patina 0.34.0 + Zoo 1.147.0, `_scratch/zoo-scupper`): a scupper, conductor head
  and downspout instead, on buildings that are not Empties.

## 2026-10-29 -- slice 6: what stands outside a shop's door -- SHIPPED

Lot 0.137.0 (5e93b6d, `patches/patch_lot_frontage.py`), the first set dressing placed by cause rather than by
spacing: against a shop's street face beside its way in, a soda machine, a stack of milk crates and a news box,
stepped clear of the door's approach point, the paths and everything standing. On the slice: the gas station's shop
and the card shop (b0, b2); the bank and the rail yard keep clear fronts. **Verdict: reads better**
(`crops_s5_s6_inspect.png`): the card shop's door now has the blue machine and the red crates and box beside it --
the first saturated accents at street level, and a reason for them. **Price** (`perf_s6_*`, slice 5 the control):
**draws median +0, largest +24 (control floor 0); p95 median -0.008 ms, largest +0.776 ms (floor 0.830 ms)** -- six
props, explained; `camera_socket_0` yaw 270 newly near budget at 1,804 draws. **Retracted, kept:** the first slice-6
build placed nothing -- the draft read a building's `id`, which is the site's `b0` -- and its unit tests passed
because they named buildings by archetype; the tests now hold Lot's own record shape.

## 2026-10-29 -- slice 5: a sidewalk's debris at its kerb and its building line -- SHIPPED

Patina 0.37.0 (f5975c4, `patches/patch_patina_sidewalk_edges.py`). Slice 4's sidewalks were the densest dressing on
the level, 1,500 pieces on 3,315 m2 laid evenly across the walking surface. Now thinned by distance to the strip's
nearer long edge: 1,500 -> 469, within 0.4 m of an edge 18 % -> 39 %, the middle band 322 -> 48. **Verdict: reads
better, modestly** (`crops_s4_s5_inspect.png`): the walking surface is clear and what is left sits where it would.
**Price** (`perf_s5_*`, slice 4 the control): **draws median +0, largest +0** (control floor 87); p95 median -0.370
ms against a control disagreement of 2.151 ms -- a weak frame-time read, and the draws say free.

## 2026-10-29 -- slice 4: a band at the roof line, and the bands round their corners -- SHIPPED

Patina 0.36.0 (3a8ccb7, `patches/patch_patina_roof_line.py`). With the parapet flush on its wall, a facade ran from
the ground to the coping with nothing marking the roof; a band at the parapet's foot over the roof slab's depth now
does. Writing it found that 0.35.0's bands stopped a wall short of every outside corner (Deli Counter's N and S wall
runs stop at the side walls' inner faces); they now wrap the corner by the coping's rule. **Verdict: reads better**
(`crops_s3b_s4_inspect.png`): the bank and the card shop read base, middle and top. **Price** (`perf_s4_*`, slice 3b
the control): **draws median +0, largest +11 (control floor 21); p95 median +0.031 ms, largest +0.315 ms** -- the
controls disagreed by 1.013 ms, so the frame-time read is weak, and the draws say free.

## 2026-10-29 -- slice 3b: the string course, joined and in stone -- SHIPPED

Patina 0.35.0 (b279773, `patches/patch_patina_string_courses.py`) joins each floor line's surviving bands into runs;
Zoo 1.148.0 (248f864, `patches/patch_zoo_string_course.py`) builds them in the stone trim. `workspaces/slice-3b-ws`,
rebuilt after the failed bake below. **Verdict: reads better** (`crops_s2_s3b_inspect.png`, `sheet_s2_s3b_inspect.png`):
the bank's flank groove is a continuous cream band at its floor line; the card shop has a stone band between its
brick and its storefront, the way a commercial front is built. **Price** (`perf_s3b_*`, slice 2 the control):
**WATCH over 53 headings -- draws median +3, largest +10.5 (control floor 21); p95 median +0.014 ms, largest +0.186
ms (floor 0.552 ms)** -- the stone is a second material on sides that had only concrete; the WATCH is the two
headings over budget in every build of the slice.

## 2026-10-29 -- a failed light bake priced as the change's cost (RETRACTED price, guard added)

Slice 3b's first build ran while the disk filled: its light bake failed (`light_bake.json` `ok: false`, no
`bake.exr`), Level Factory shipped the package unbaked as it is written to (`exporting/export.py`, "ships the package
unbaked, saying which in light_bake.json"), and `make` exited 0. Priced against slice 2, it read **FAIL: draws median
+1,521, largest +3,588; 30 headings over budget** (`perf_s3b_nobake_*`) -- the cost of unbaked light, not of the
string course. Kept, renamed, and not evidence about the change. `tools/price_batch.py` now refuses a control and a
subject whose bake states differ. Still open, and Level Factory's: a failed bake is a `problem` row in the panel
(`service/exporting.py`) and nothing else; a package that costs ~1,500 draws more in every view probably should not
leave `make` with exit 0.

## 2026-10-29 -- the disk filled; what was removed to continue

Slice 3b's shoot stopped on a full disk (0 MB free on C:). With the walker away, only scratch this session created and
no longer needs was removed: the clones of tool changes already shipped (`_scratch/zoo-coping`, `zoo-scupper`,
`zoo-window-frame`, `zoo-strings-try`, `patina-coping`, `patina-planes`, `patina-scupper`, `patina-strings-try`,
`patina-strings-try2`, `dc-parapet-flush`, `lf-slice-cluster`), the price tool's and the probe's package copies
(`_scratch/price_perf_{coping,flush,frame,linear,linear2,s2,s2b,s3}`, `_scratch/probe_slice2`), and the build
workspaces whose findings are committed (`workspaces/{frame,coping,flush,flush2}-9082-ws`, `workspaces/slice-3-ws`,
the rejected first string-course build). 5.9 GB free after. Nothing outside this session's own scratch was touched;
`_scratch/price_perf_deposit` was left because its origin is not this session's.

## FOR THE WALKER -- decisions this work found and did not take alone

1. **The street trees.** In seven of nine street frames a tree stands in the foreground as a silhouette of flat
   plates on a bare trunk -- the most "computer made" shape on the avenue. It is that way on purpose: Zoo's
   `street_tree` was kept low-poly retro on your call of 2026-09-13 ("the mario64 trees looked nice in their own retro
   way"), before the realism direction. Options: (a) keep it; (b) its existing alpha-card crown (`params.crown =
   "cards"`, judged not ready on cold run 9032), finished and priced -- card foliage is how the 360-era target does
   trees, at the cost of alpha overdraw; (c) a redraw of the volume crown with many more, smaller, smoothed leaf
   masses. Each would be shot on the slice and priced before it ships.
2. **The evening.** At the brief's `evening` the facades and the ground are close to black (street frames 22-40 of
   255 mean brightness in the level's light, 57-84 under the studio light). The sky, the lit windows, the gas canopy
   and the signs read; nothing else does. Keep the mood and lift the fill, change the slice's time of day, or leave
   it.
3. **Rowhome gutters under their parapets.** Patina 0.34.0 drains a commercial roof through its parapet; the Empties
   keep the gutters you asked for on 2026-10-04. Should a rowhome with a parapet drain through it too?
4. **A train yard on Delco Ave.** The seeded draw's fourth building. Pick another candidate, or give the avenue a
   fabric list (Level Factory's `D01_delco_avenue`)?

## 2026-10-29 -- what the walker's comps show that our levels do not

The walker sent three comps of 2000s-era shooter levels (a desert city street from above, a ruined downtown
intersection at sunset, a civic bank on a plaza from above) and asked, "without copying these comps, what can you
see in these maps/levels that we aren't achieving today?" Read against seed 9082's bank block (the frames in
`docs/findings/parapet_flush/`), the gaps, as principles and not as things to copy, each with the tool that owns it:

1. **Massing that steps and overhangs** (Deli Counter). Their buildings are not extruded footprints: storeys set
   back, upper floors overhang the street, bays and balconies project, rooftops carry penthouses, stair towers,
   tanks and masts, and neighbours differ in height. Ours are boxes of similar height with flat tops; the skyline is
   one line.
2. **Facades in several planes** (Zoo). Deep reveals, shutters, awnings over each opening, cornices and string
   courses, pilasters and columns, recessed entries with steps -- every facade has three or four depths that throw
   shadow. Ours are one plane with holes in it, now with frames and sills.
3. **Weathering that tells where water runs** (Pixelcoat, Patina). Darker bases, streaks under sills and copings,
   patched render, stains, rust bleeding from metal -- value variation across one wall that follows cause. Ours are a
   uniform skin per wall.
4. **Light with a direction and a colour** (Lux). A low warm sun against cool shadow, long cast shadows, and
   atmospheric haze that pushes distance back in layers. Our level light is overcast or night: soft, even, grey.
   (The slice's time of day and weather are the walker's call; the brief says evening, clear.)
5. **Colour contrast by accent** (Pixelcoat, Zoo, Lot). A restrained base -- tan stone, grey concrete -- against a
   few saturated accents: a red truck, red paving, a lit sign, warning stripes, banners. Ours is close to one value
   everywhere with few accents beyond the signs.
6. **A ground plane with hierarchy** (Lot). Kerbs with gutters, paving bands at a frontage, a plaza in a different
   material, cracks, patches, manholes, stains and markings. Ours is road, sidewalk, lot.
7. **Clutter in groups that tell a story** (Lot, Zoo). Roadwork barricades with cones around a hole, wrecks pushed
   against a fence, a security perimeter of vans -- props clustered around a cause, not one every N metres.
8. **An overhead layer** (Lot). Wires across the street, hanging signals and lamps, banners: the top third of the
   street frame is full. Ours carries the pole line on one side and little across.
9. **A hero piece per view** (Zoo, Lot). Each frame has one thing it is about -- a neon blade sign, a columned bank
   portico on steps, a beacon mast, a palm -- larger, brighter or more detailed than its surroundings.
10. **Roofscapes worth seeing from above** (Zoo, Patina). Copings, tar patches, skylights, plant, parapets that
    differ by building -- because these levels are seen from rooftops. Ours are flat plates with a few units.
11. **An architectural language per building type** (Deli Counter, Zoo). The bank reads as a bank from 50 m:
    rusticated stone base, arched windows, columns and pediment, a name band. Ours reads as a box with a sign.

**Proposed order** (biggest change to the frame first, cheapest first among equals, every step priced):
weathering and value variation (3), facade layering on the common walls (2), the ground plane (6), clustered
dressing (7), the hero piece -- the bank's portico and the gas station's canopy (9, 11), massing and roofscape
(1, 10), the overhead layer (8). Light (4) and colour (5) touch the walker's taste and are proposed, not changed
alone.

## Fixes in flight

- **No gutter under a parapet** (Patina 0.34.0 + Zoo 1.147.0, clones `_scratch/patina-scupper`,
  `_scratch/zoo-scupper`): a non-Empty building's roof drains through a scupper in its parapet into a conductor head
  and a downspout; the white gutter line 1.4 m below the bank's top goes. Empties keep their gutters (the walker's
  call, 2026-10-04) -- **left for the walker**: should a rowhome with a parapet drain through it too?
