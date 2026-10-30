# The slice's look: gaps and fixes, newest first

Judged by `RUBRIC.md`. The slice is `docs/vertical_slice/` (Delco Ave: a gas station, a bank and the library's draw).

## AT A GLANCE (for the walker, kept current)

**Shipped to the slice, each built, shot and priced; every one free or near it in draw calls:**

| Step | What changed on the street | Tools |
|---|---|---|
| 1 | A gas station and one bank on the avenue | Level Factory 0.268.0 |
| 2 | Parapets stand on their walls, flush with the facade | Deli Counter 0.292.0 |
| 3 | Duplicate trim stacked on 76 of 158 buildings removed | Patina 0.33.1 |
| 4 | Debris gathers at walls and kerbs; open asphalt mostly clean (4,547 -> 811 pieces) | Patina 0.34.0 |
| 5 | No gutter under a parapet: a scupper and a conductor head instead | Patina 0.34.0, Zoo 1.147.0 |
| 6 | A cream stone band at every floor line | Patina 0.35.0, Zoo 1.148.0 |
| 7 | A cornice band under the parapet; every band wraps the corners | Patina 0.36.0 |
| 8 | Sidewalk debris at the kerb and the building line, the middle clear | Patina 0.37.0 |
| 9 | A soda machine, crates and a news box beside each shop's door | Lot 0.137.0 |
| 10 | The gas station's canopy built: brand fascia and stripe, light soffit, columns on yellow guards | Zoo 1.149.0, Deli Counter 0.293.0 |
| 11 | Quoins: dressed stone blocks up the bank's corners | Patina 0.38.0 |
| 12 | Utility-cut patches of newer asphalt across the avenue, two a building | Lot 0.138.0 |
| 13 | Quoins lifted above a standing body's height (nothing proud where a body walks) | Patina 0.38.1 |
| 14 | Stone pilasters on a civic building's long walls, solid, at the bays its windows imply | Zoo 1.150.0, Deli Counter 0.294.0 |
| 15 | The evening's fill: the sky in the bake lifted, street frames about 45 % brighter, still dusk | Lux 0.81.0 |

**In flight (the walker, 2026-10-30: "try the card-based trees and lift the evening fill"):** the evening's fill
-- Blue Hour's sky in the bake lifted (Lux), slice 12; leaf-card street trees on a leaf cutout -- Pixelcoat and Zoo,
slice 13. **Pilasters, why that shape:** the bank's long blank flank divided
into bays. **Carving them into the wall modules does not work, kept:** a carved pier can stand only on a module
seam, and Deli Counter tiles each storey round its own openings -- on the bank's east side the ground storey's seams
fall at ..., -0.85, 1.15, 3.15 and the upper storey's at ..., -0.70, 1.30, 3.30; the only seams both share are at
-8.85 and -6.85, and the bay line the openings imply is 0. A pier would jog at the floor line. (A Zoo clone was
written to the carved design and dropped unshipped.) The shape that fits: a pilaster as its own solid, full height
at the chosen line, a hand proud of the wall WITH a collider -- a Zoo species and a Deli Counter volume, the canopy
column's pattern. The price harness reads a
heading's steady draw count, not a stray frame (Level Factory 0.269.0).

**Waiting on you** (section FOR THE WALKER below): the street trees, the evening's darkness, rowhome gutters under
parapets, the train yard on Delco Ave, and whether downspouts may stand proud at body height.

**Open and not yet solved:** the slice is over the 2,000-draw budget at two headings in every build (2,312-2,393,
from the rail yard looking back down the avenue); a draw-attribution probe disagrees with the harness about that view
(3,540 objects against 2,320) and is not yet trusted.

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
5. **Proud trim at body height.** The standing rule is no dressing in walkable space: a wall's collider ends at its
   face, so anything proud of the face within a body's height is geometry a body walks into. Panel fields and
   pilasters were withdrawn for it. Patina 0.38.0's quoins broke it from the ground and 0.38.1 lifts them above the
   lowest band clear of a 1.8 m body. But downspouts (7 cm proud, gutter to the ground, no collision) have shipped
   since Patina 0.25.0 down every face with an opening -- the same shape at the same height. Exempt small trim (and
   say how small), give downspouts a collider, or stop them above body height?

## 2026-10-30 -- slice 12: the evening's fill -- SHIPPED

The walker, 2026-10-30: "lift the evening fill". At the brief's `evening` (Level Factory maps it to Lux's Blue Hour)
every facade and the ground were close to black. `ambient_energy` was not the lever: a baked surface takes its fill
from the sky in the bake (Level Factory 0.164.0), and Blue Hour's sky gave it little -- `sky_energy` 0.7 over a
`ground_color` of (0.10, 0.11, 0.16). Lux 0.81.0 (3603c2d, `patches/patch_lux_evening_fill.py`) lifts them to 1.5
and (0.20, 0.19, 0.22); sun, exposure, fixtures and sky colours unchanged. **Measured** (mean of the frame, 0-255, in
the level's light; the chain prints it): ave_east 30.7 -> 45.5, ave_west 23.1 -> 35.8, the bank oblique 33.9 ->
49.9, the gas front 40.0 -> 60.4, the sidewalk 25.5 -> 39.1; the interior objective 40.4 -> 40.8. **Verdict: reads
better** (`crops_s11_s12_evening_fill.png`): the road's paint, the cars, kerbs and sidewalks and the bank's bands,
quoins and pilasters read; still dusk -- the lit windows, the canopy and the pylon are still the brightest things.
The facades are still on the dark side: room for one more step. **Price** (`perf_s12_*`, slice 11 the control):
**draws +0 exactly (floor 0)** -- the fill lives in the lightmap. The printed FAIL is frame time read while Deli
Counter 0.294.0's commit hook ran (controls 1.88 ms apart; camera_socket_1 yaw 90, 11.16 ms at 1,554 draws).

## 2026-10-30 -- slice 11: stone pilasters on a civic building's long walls -- SHIPPING

The bank's east flank was 22 m of blank stucco between its corners. Zoo 1.150.0 (034dc9a,
`patches/patch_zoo_wall_pilaster.py`) adds `wall_pilaster` -- a plinth, a shaft set back from it, a cap, in the stone
trim, one collider over the slot -- and Deli Counter 0.294.0 (`patches/patch_dc_pilasters.py`, `pilasters.py`) stands
it on every civic building that is not an Empty: bay lines laid between anchors (the wall's ends and each pooled
opening's centre), one pier midway between two openings, no bay longer than 6.5 m, none within 1.2 m of a corner or
0.4 m of an opening; 0.6 m wide, 8 cm proud, grade to the top storey's wall top. 17 civic buildings carry them; the
slice's bank, eight, one midway along the east flank. Solid where a body walks, so the walkable-space rule holds: the
slice walked clean. **Why this shape, kept:** a proud Patina pilaster was withdrawn for having no collider, and a pier
carved into the wall modules cannot follow a bay line -- the storeys share almost no module seams (above). **Verdict:
reads correctly, modestly** (`crops_s10_s11_pilasters.png`): a vertical rhythm on the flank and the front, nothing
reads as a grid; at street distance a 0.6 m pier 8 cm proud in a stone near the stucco's value is faint -- a wider,
deeper, more contrasting pier would read more, and costs another gate and slice. **Price** (`perf_s11_*`, slice 10
the control): **draws median +2, largest +34 (floor 0)** -- each pier is its own module, so a view that sees the
bank's eight pays for eight; extraction_12 yaw 90 1,457 -> 1,491, longest_sightline (already over) +12. **Open:**
merge a building's pilasters by material, as its covers are, which would make them free. p95 median +0.052 ms, inside
a 1.165 ms floor.

## 2026-10-30 -- slice 10: no quoin within a standing body's height -- SHIPPED

A rule check on slice 8's own change. A quoin stands 6 cm proud of the wall with no collider, and a wall's collider
ends at its face, so every block within a body's height was geometry a body walks into -- the rule panel fields and
pilasters were withdrawn for (Level Factory's Patina adapter; Zoo's `arch.relief_parts`). Patina 0.38.0 laid them
from the ground. Patina 0.38.1 (2861623, `patches/patch_patina_quoin_body.py`) starts the quoined body just above
the lowest band clear of a standing body -- `BODY_CLEAR_M` 1.85, Deli Counter's agent contract's 1.8 m player and a
hand -- a quoined upper body over a plain base storey; a civic building with no band that high gets none. **Verdict:
reads as intended** (`crops_s9b_s10_quoins.png`): stone quoins on the upper storey from the first string course
up, the ground storey plain. **Price** (`perf_s10_*`, slice 9b the control): **draws median +0, largest +0, the
controls' floor 0** -- the first price since the harness read the window's p95, and its draw floor is exact. The
verdict printed FAIL on frame time, and that is the machine: Zoo's two suites ran beside the price, the controls read
10.3 ms apart, and the heading named, attacker_spawn_10 yaw 270, draws 853 against a 2,000 budget. A quiet re-price
is owed. Downspouts stand in the same place the same way and have since Patina 0.25.0: FOR THE WALKER, item 5.

## 2026-10-29 -- slices 9 and 9b: where the street was dug up -- SHIPPED (9b)

The avenue is the largest surface in every street frame and was one even field of the road pack. Lot 0.138.0
(7b2e08e, `patches/patch_lot_utility_cuts.py`) cuts a patch of newer asphalt where each building's services were
trenched in: from past the main under the centre line to the kerb on the building's side, 36 in along the road (a
24 in trench and its T-cut), two for a wide frontage (water and sewer), across the lines along the road, clear of
every other marking, the drains and the junctions -- 8 on the slice. **Slice 9, retracted, kept**
(`crops_s8_s9_patches_retracted.png`): a 0.62 tint with a 4 in band of black sealant round each patch; the body
could not be told from the road at the street's stations, and the sealant, under a pixel tall at 20 m and more,
broke into dashed black lines -- read as skid marks or a fault. **Slice 9b**: no sealant line, a 0.42 tint (a fresh
cap is near black against weathered grey). **Verdict: reads correctly, modestly** -- solid dark strips across the
near lanes, one cutting the centre line's dash as a real repair does; no station sees one close. **Price**
(`perf_s9b_*`, slice 8 the control): **draws median +0, largest +4**; p95 median -0.011 ms.

**The controls' draw floor** read 87 on slice 9 and 21 on 9b, against about 0 before. Investigated in
`docs/findings/price_draw_flicker/`: the harness reported each heading's draws as its window's maximum, and at two
headings the scene now and then submits one frame higher than it holds. Level Factory 0.269.0 (3c1baaf) reports the
p95 and keeps the maximum as `draws_max`; three runs over one package agree at all 53 headings. The prices above
were read with the maximum; every pass disagreement on record sat at the same two headings, so their medians are
unaffected, and a "largest" delta could carry one stray frame -- not re-priced.

## 2026-10-29 -- slice 8: quoins up the bank's corners -- SHIPPED

After slice 4 the bank read base, middle and top, and its corners were plain stucco between the bands: the stone
stopped where two walls met. Patina 0.38.0 (af5f19e, `patches/patch_patina_quoins.py`) stands dressed blocks up each
outside corner of a civic building that is not an Empty -- a bank, a credit union, a courthouse, a library, a post
office -- alternately long (0.62 m) and short (0.36 m) on each face, 0.32 m courses with a 3 cm joint, wrapped by the
bands' corner rule, a course left out where it would meet a band, a pair dropped whole where either half meets an
opening or a downspout; Zoo builds them as it builds the string courses, in the same stone trim. On the slice:
bank_branch_a02 136 blocks over 17 courses, the card shop (not civic) none. **Verdict: reads better**
(`crops_s7_s8_inspect.png`): the bank's corners read as laid stone under the studio light, and at evening still as a
toothed edge against the sky. **Price** (`perf_s8_*`, slice 7 the control): **draws median +0, largest +2 (floor 0)**
-- the blocks merge into each side's string-course mesh. **The frame time is not evidence**: Deli Counter 0.293.0's
commit hook was rebuilding the whole library during the price, the controls read 1.501 ms apart, and the p95 median
+0.077 ms lies inside that. Slice 7, the control, was cleared for slice 9's disk before a quiet re-price could run;
the draw count, which machine load does not move, is the number this ships on.

## 2026-10-29 -- slice 7: the gas station's canopy and columns, built -- SHIPPED

The forecourt's landmark had no species: Deli Counter's specs author it as `canopy_roof` on six `canopy_col`, and the
box row of `prop_species` held both to greybox -- a grey slab on grey posts. Zoo 1.149.0 (d8a0935,
`patches/patch_zoo_fuel_canopy.py`) mints and shapes `fuel_canopy` -- a fascia in the store's colour with a stripe in
its rule colour (the FLAPPAHS pylon's colourway, so canopy and sign are one brand), a light soffit on the plane the
canopy lights hang from, a roof cap -- and `canopy_column`, a steel shaft on a safety-yellow guard; one material each,
0 coincident pairs at every genome corner. Deli Counter 0.293.0 (`patches/patch_dc_canopy_species.py`) routes the
volumes to them. **Verdict: reads better** (`crops_s6_s7_inspect.png`): a branded canopy where a grey slab stood, the
column guards the forecourt's first yellow. The fascia's green is the brand's dark field colour; at evening it reads
dark -- the pylon's palette, not a new choice. **Price** (`perf_s7_*`, slice 6 the control): **draws median +0,
largest +21 (floor 0)** -- the deck and its six columns now their own modules; **p95 median -0.010 ms**, and
extraction_11 yaw 90, already over the draw budget, +0.764 ms against a 0.480 ms floor.

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

## (history) Fixes that were in flight before slice 2 -- since shipped

- **Debris gathers at edges** (Patina 0.34.0, `_scratch/patina-scupper`): on open ground (`ground` in a
  `play_space`) a candidate survives with probability max(0.06, exp(-d / 2.5 m)), d the distance to the nearest
  building, wall base or kerb; weeds and rubble only within 2 m of one; `very_high` zones (Lot's perimeter) and
  gameplay paths untouched. Re-planned on slice 1's own inputs: open ground 4,547 -> 811 pieces (11.1 -> 2.0 per
  100 m2), plate-wide R 0.72 -> 0.51; within 2 m of an edge 605 -> 413, beyond 10 m 1,585 -> 92.
  Tests: tests/test_debris_edges.py; suite 408 passed, 11 skipped.
- **No gutter under a parapet** (Patina 0.34.0 + Zoo 1.147.0, `_scratch/zoo-scupper`): a scupper, conductor head
  and downspout instead, on buildings that are not Empties.

## (history) The first fixes in flight -- since shipped

- **No gutter under a parapet** (Patina 0.34.0 + Zoo 1.147.0, clones `_scratch/patina-scupper`,
  `_scratch/zoo-scupper`): a non-Empty building's roof drains through a scupper in its parapet into a conductor head
  and a downspout; the white gutter line 1.4 m below the bank's top goes. Empties keep their gutters (the walker's
  call, 2026-10-04) -- **left for the walker**: should a rowhome with a parapet drain through it too?
