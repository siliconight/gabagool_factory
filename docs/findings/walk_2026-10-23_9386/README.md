# The walker's walk of cold run 9386, 2026-10-23

The walker played `_runs/walk_9386_restaurant_row_001` (Deli Counter 0.264.0, Level Factory 0.237.0; restaurant_row_001
at seed 9003). Their words and the overlay's figures, as they reported them; each is investigated in its own section
as it is measured. Screenshots are the walker's, kept beside this (`NN_*.webp`).

| # | the walker | where (overlay) | state |
|---|---|---|---|
| 1 | "still doensn't look irght to have 2 signs on top of each other like this and not centered... in real life this would be 1 sign" | pos -7.1, 1.6, 17.6; bldg b1 pharmacy_a01 | SHIPPED Zoo 1.123.0, Lot 0.129.0, Level Factory 0.241.0; proven, cold run 9391 |
| 2 | "textures have visible seams and it doesn't look as continous as it could be" (lines marked on the frame) | pos -8.0, 1.6, -0.1; pharmacy_a01, GreyboxBase; look ext_col_0_N_open0_BREACHPANEL 10.49 m | cause measured (an interactive opening's own lightmap rect, 8 of 10 marks); casings Zoo 1.126.0, proven 9391; 2 marks over the bookshelf open |
| 3 | "drop safe looks like a brown box, needs more retopology or multiple texture/colors to see it better imo" | pos 9.4, 1.6, -4.6; bldg b1 pharmacy_a01; look DropSafe 2.75 m | SHIPPED Zoo 1.125.0, Deli Counter 0.267.0; proven, cold run 9391 |
| 4 | "non collision rod on the stair case that shouldn't be there" | pos 54.6, 2.2, 1.6; bldg office, GreyboxBase; look slab_col_2 13.07 m | SHIPPED Zoo 1.122.0; proven, cold run 9389 |
| 5 | "screens should have the same effect as the tvs in the strip club that give them that little movement/\"shimmer\" to show \"life\"" | pos 47.0, 8.8, -7.3; bldg b2 office; a cubicle's monitor | SHIPPED Level Factory 0.239.0; proven, cold run 9388 |
| 6 | "something about the doulbe stairs still needs some work to not look so odd...mainly the walling/railing doesn't loook natural yet" | pos 55.7, 5.2, -6.0; bldg office, GreyboxBase; look stair_guard_rail_4_col 8.37 m | the walker picked the compact U; step 1, rails as balustrades (Zoo 1.128.0, Deli Counter 0.268.0), in progress; step 2, the seam wall, open |
| 7 | "this empty space goes against the doc i sent you about the value of urban land and how it would be filled in with things...careful how we solve this one....but it should be not the norm to have these wide empty spaces without talking about it" | pos 70.7, 1.7, 15.8 (cover_155) and 99.4, 1.6, -21.0 (Site) | open |
| 8 | "garbage cans are usually up against walls inside buildings" | pos -51.6, 1.6, -2.6; deli_a03, GreyboxBase; look litter_bin_r2f2d413e_11 3.26 m | SHIPPED Deli Counter 0.266.0; proven, cold run 9387 |
| 9 | "good collision, but not sure what this large boring wood block is...." | pos -35.0, 1.6, -10.1; bldg b0 deli_a03; look Prop 2.55 m | SHIPPED Deli Counter 0.267.0; proven, cold run 9391 |
| 10 | "bus stop sign is for cars/buses so there is no parking ther...so it sohuld be closer to the road" | pos 19.8, 1.7, -2.6; look nothing within 60 m | SHIPPED Lot 0.127.0, proven 9387; no parking at the stop, Lot 0.131.0, unproven |
| 11 | "traffic lights done change?" | pos 7.9, 1.7, 16.7; the intersection's signal heads | SHIPPED Level Factory 0.238.0; proven, cold run 9388 |
| 12 | "where are the traffic lights for this side of the road?" | approaching the same junction from the other side (near gs_empty_rowhome_h) | SHIPPED Lot 0.128.0, Zoo 1.121.0; proven, cold run 9387 |
| 13 | "many of the rowhome doors dont have doorknobs?" | pos 15.6, 1.6, 24.4; bldg blocker_15 gs_empty_rowhome_j | SHIPPED Zoo 1.124.0, proven 9391; its hardware in the railing's iron, Zoo 1.127.0, for the draws, unproven |

## 1. Two signs on one shop front

`01_pharmacy_two_signs.webp`: pharmacy_a01's street face carries the band "DOC'S DISCOUNT DRUGS" along its parapet and,
under it at its west end, a blue box "PHARMACY" over the door, off the band's centre. Earlier context: roadmap 187 (the
walker, 2026-10-06, option A) made the band (Lot hangs it; Level Factory deals it from Pixelcoat) and the door box
(Deli Counter places it; Zoo names it) read from one name list -- two signs agreeing, still two signs. The walker now:
one sign.

## 2. Seams down the walls

`02_wall_seams.webp`, `02_wall_seams_marked.webp` (the walker's lines): pharmacy_a01's back room, its walls in
vertical bands -- brightness and the plaster's grain stepping at intervals along the back and side walls. Two candidate
causes, not yet told apart: each wall piece starting its texture over (UVs per piece), or each piece's own rect in the
light bake not matching its neighbour's at the joint (lightmap seams). To tell them apart: the same view shot with the
bake and without it.

**Measured 2026-10-24, NOT YET DECIDED** (`seams/`): the walker's eye (overlay: -8.0, 1.6, -0.1, facing the north
wall) on cold run 9388's walk copy, three ways (`tools/look_shots.py`): as shipped; the inspection light with the bake
on; the inspection light with the bake switched off (`--switch-off lightmap`: 1 lightmap cleared, 209 static lamps
hidden). With the bake off the plaster's grain runs continuously across the wall -- the texture is world-projected
and has no joint to show. As shipped, a contrast-stretched crop shows two thin vertical lines
(`wall_crops_autocontrast.webp`). Measured at those columns, 1600x900, the line's dip against the 4 px either side is
0.2 and 1.5 grey codes as shipped, 0.6 and 0.5 bake on, 0.6 and -0.4 bake off (`seam_profile.out.txt`) -- under what
this instrument separates from the grain. Along the whole wall the largest column-to-column step is 9.6 % of the mean
as shipped, 8.1 % bake on, 5.1 % bake off. Leaning: the bake (lightmap rects meeting at a joint), not the texture --
but a lean is not a finding; the next instrument reads the lightmap's own rects at the wall's piece joints.

**The walker, 2026-10-24: "i think we want the look of baking but where we try to not get those bands".**

**REFUTED, 2026-10-24, the same day -- kept above the reasoning it overturns.** Level Factory 0.240.0 made the wall
one lightmap chart (a welded proxy unwrapped, UV2 carried back) and cold run 9390 measured it against 9389 from the
walker's eye, same instrument, one session (`seams/joints_9389_vs_9390.out.txt`): the wall IS one continuous row of
the lightmap in 9390 (`wall_islands_9390.out.txt`) and the joint-to-mid-module step went 2.0x -> 3.0x, not down. So the
bands are NOT separate lightmap charts meeting at the joints; the correlation below with the joints stands, the cause
read into it does not. 0.240.0 reverted as 0.240.1 (bake 36.0 -> 52.7 s, for nothing the walker asked for). Still
open, untested: the per-module `wear` Zoo bakes into each wall module's own vertex colours (a module-to-module step
that would show with the bake off too -- the bake-off frame's largest step was 5.1 %, not zero), the texel grid at
0.2 m against the 2 m module (a joint every tenth texel), and the bake's denoiser at quality Low.

**CAUSE MEASURED, 2026-10-24** (`seams/wall_islands.gd`, `wall_islands.out.txt`, `joints_in_frame.out.txt`, on 9389's
walk copy): the back room's north wall is one merged mesh, `b1/MergedR_1`, and its lightmap UV2 is ONE ISLAND PER 2 m
WALL MODULE (x -10.85..-8.85, -8.85..-6.85, ... two triangles each) -- the merge (`merge_buildings.gd`) unwraps each
cell's mesh with `lightmap_unwrap` at 0.2 m a texel, and adjacent modules share no vertices, so each is its own chart
of about 10 texels across. Some neighbours sit side by side in the atlas (-4.85..-2.85 and -2.85..-0.85 share
u = 0.1474), others in different rows (-8.85..-6.85 at u 0.53, -6.85..-4.85 at u 0.24). Projected into the shipped
frame through the same camera, the brightness step across a joint against one mid-module: joints mean 3.0 grey codes
(n 8; the joint behind the bookshelf left out), mid-module 1.5 (n 6; one at the room's corner left out) -- and the two
lines first picked out by eye, columns 1335 and 1415, are the joints at x 0.30 and 1.70, the door opening's edges.
So the bands are lightmap islands meeting at module joints. The cure the walker's call points to: one chart per
wall plane inside a cell (unwrap a position-and-normal-welded proxy and carry its UV2 back), keeping the bake --
priced before it ships (lightmap size, bake time, frames from the walker's eye).

**THE JOINTS REFUTED, 2026-10-24, later the same day -- kept below the two readings it overturns, both of which rest
on it.** The "joints step twice as much as mid-module" figure was the control's placement, not the joints:

- **What the modules carry was read first and is no cause** (`seams/joint_attrs.gd`, `joint_attrs_9389.out.txt`, on
  9389's walk copy). Every module of the wall is one quad with the same four corner colours, so `Wear` (Zoo's
  `geometry.wear_colors`, seeded noise per vertex) DOES step at every joint -- 0.686/0.820 bottom/top on a module's
  right edge against 0.973/0.663 on the next one's left. But nothing draws it: the merged wall's material reads
  `vertex_color_use_as_albedo false` at run time (the worldskin keeps a tiled kit's vertex colour off, for this
  reason). Its UV1 restarts per module, and the material is `uv1_world_triplanar true`, so it never reads UV1. The
  normals are identical either side, (0, 0, 1) to four decimals.
- **Which light carries the steps** (`seams/light_sources.sh`, `light_sources_9389.out.txt`; three arms from the
  walker's eye on 9389, one session): shipped joints 3.19 / mid-module 1.45 grey codes (n 7 / 6, the corner and the
  bookshelf left out as above), reproducing the first frame to 0.5; lightmap only 3.46 / 1.40; lightmap off 0.66 /
  0.38 -- a wall at 11-20 grey, too dark for this instrument to say anything either way. The lightmap carries them.
- **But the lightmap itself is smooth across the joints** (`seams/lm_wall_profile.gd`, which reads the bake's own
  EXR, since headless holds no texture pixels: `lm_wall_profile_9389.out.txt`, `_9390.out.txt`). At y 1.6 every
  5 cm, consecutive texels run on without a step at any joint, in both runs (at -8.85: 0.682, 0.654, 0.594). The
  curve is the ceiling lamps' pools on the wall -- peaks near -9.5, -3.25, 0.05 and 3.0, troughs near -7.3 and
  -1.5, rising 0.10 -> 0.70 over about 1.5 m -- at a texel of about 0.18 m in 9389 and 0.35 m in 9390 (whose one
  chart gave the wall half the texels; the coarser texel is a likely reading of 0.240.0's worse ratio).
- **The control was on the pools' extremes.** The lamps sit on the modules' grid, so the mid-module positions fell
  on peaks and troughs, where the light is flat, and the joints on the slopes. Measured at every 0.1 m of the wall
  in the lightmap-only frame (`seams/step_vs_slope.py`, `step_vs_slope_9389.out.txt`): joints mean |step| 2.25
  (n 5), mid-modules 1.74 (n 6), every other position 3.73 (n 116); inside the joints' own slope range, joints 2.25
  (n 5) against 1.99 for 53 positions that are not joints. A joint steps as much as anywhere else on a slope.
- **Two refutations on the way:** bicubic lightmap sampling (Mach bands at the kinks of a bilinear gradient) is
  ALREADY ON -- `rendering/lightmapping/lightmap_gi/use_bicubic_filter = true` in the walk copy, and Godot 4.7's
  Compatibility scene shader carries the `LIGHTMAP_BICUBIC_FILTER` variant. And the wall modules' buried end faces
  (`seams/joint_caps.gd`, `joint_caps_9389.out.txt`: two back to back at every joint, 0.30 m deep, z -6.64..-6.34)
  lie behind the face the bake's rays leave from, and the texels show no dip there.

**What IS a seam, measured:** the breach panel's edges, x 0.30 and 1.70 (an earlier line here called it a door
opening; it is `ext_0_N_open0`, the BREACHPANEL the walker's crosshair was on). There the merged wall meets
`ext_0_N_open0/Wall_Panel`, the panel's own piece, a separate mesh with its own rect
in the atlas (slice 12 against the wall's slice 7), and the bake does not agree across the cut: above the door at
y 2.6 the wall reads 0.601 and the panel 0.526 at x 0.30 (-12 %), the panel 0.410 and the wall 0.364 at 1.70
(+13 %) (`lm_door_b1_MergedR_1_9389.out.txt`, `lm_door_ext_0_N_open0_Wall_Panel_9389.out.txt`). Inside one merged
mesh, 9389's separate per-module islands bake smooth; between two meshes, they do not.

**Still open:** whether the walker's bands are those two door seams, the lamp pools themselves (a wall lit in
scallops reads as stripes), or both. The next instrument: the walker's frame marked against these positions. The
cure for the door seams, if they are it, is the opening's piece baked as part of the wall's merged mesh, to be
found in Level Factory's merge and priced; the pools are the lighting's look, Lux's to answer if the walker wants
them softer.

**THE STATION WAS NOT THE WALKER'S VIEW, 2026-10-24 -- every frame measurement above it stands, about a different
view of the same wall.** The station `seams:-8.0,1.6,-0.1,-6.0,2.07,-10.5` faced the north wall square on; the
walker faced east-north-east, their crosshair on the breach panel at 10.49 m (`ext_col_0_N_open0_BREACHPANEL`; from
their position (0.4, 2.07, -6.34) is 10.5 m off). Re-shot from `walker:-8.0,1.6,-0.1,0.4,2.07,-6.34` it matches their
frame: the north wall on the left (bookshelf and all), the east wall ahead with its door.

**The walker's ten marks, placed** (their 2000 px frame scaled to 1600, cast through that camera; about +/-0.3 m,
the view being reconstructed rather than theirs) against the meshes each wall face is made of
(`seams/wall_pieces.gd`, `wall_pieces_x_9389.out.txt`, `wall_pieces_z_9389.out.txt`):

| wall | marks | a piece the merge left out (`merge_buildings.gd`, `_mergeable`: `*_open<n>` and interactive slots stay whole) |
|---|---|---|
| north, z -6.34 | x 0.17, 2.31 | the breach panel `ext_0_N_open0`, x 0.30..1.70 |
| east, x 4.85 | z -3.89, -3.48, -2.86, -2.20 | the doorway `int_0_1_open1`, z -3.615..-2.365 |
| east | z -1.00, -0.52 | the breach panel `int_0_1_open0/Wall_Panel`, z -0.69..0.71 (first read here as a filled opening) |
| north, above the bookshelf | x -7.00, -6.44 | none: one merged mesh there (its module joint at -6.85) -- unexplained |

Eight of the ten sit at an edge where an opening's own mesh, with its own rect in the lightmap, meets the room's
merged wall -- the seam the breach panel's texels measure at -12 % and +13 %. The cure this points at is Level
Factory's: bake an opening's opaque wall surfaces as part of the cell's merged wall, where nothing about the opening
needs them apart (a filled opening's panel, a doorway's jambs and head); a breach panel and a door leaf change state
and stay their own. To be built, then proven and priced in a cold run, from the walker's view.

**THE MERGE CURE REFUTED BEFORE IT WAS BUILT, 2026-10-24** (`seams/open_slots.gd`, `open_slots_b1_9389.out.txt`):
every piece behind those eight marks is INTERACTIVE -- `ext_0_N_open0` and `int_0_1_open0` are breach panels
(`interactive_id`, each with a `_breached` twin it swaps to), `int_0_1_open1` a doorway -- and an interactive slot
changes state, so it has to stay its own mesh. Of pharmacy_a01's 11 opening slots, none is both untagged and free of
glass. What is left, each a change to what a player sees:

- **A casing at the edge.** A real doorway's casing covers exactly this joint, and a trim strip reads as built rather
  than as a fault: a few triangles inside the interactive slot, no draw added. For a doorway this is plainly right.
- **For a breach panel it is a gameplay call, queued for the walker:** a frame round a breach panel tells a player
  where the wall will open. Left unframed, its seam is the lightmap's.
  **THE WALKER, 2026-10-24: "Yes hide the seam for breaches, we still don't know how they would work in the game
  but its' really cool we are building it in for potential use".** Doorways and breach panels both get the casing.
- **Matched texel density**, as a partial cure: the panel's rect is about 0.05 m a texel (30 texels across 1.4 m)
  against the merged wall's 0.18 m, two very different bakes meeting. It cannot remove the step on its own -- at
  x 0.30 the two disagree by 0.075 where the wall's own slope across 0.2 m is about 0.02 -- but it may narrow it.

**THE MOTTLE, 2026-10-25: the plaster's own, not the bake's** (`docs/findings/bake_quality/`, "The wall's blotches";
roadmap 224). Square on the wall, soft dark patches a metre or two across. Re-baked with twice the texels and with the
denoiser off, the wall reads blotchier, not smoother (index 0.293 -> 0.338 and 0.329); with the bake switched off under
the inspection light the same patches stand in the same places. They are Pixelcoat's concrete skin -- its grime and
stains, world-projected, so continuous across every joint -- and at that contrast read as patches. Queued for the
walker: the skin's stain scale or contrast is a look call.

## 3. The drop safe reads as a brown box

`03_drop_safe.webp`: pharmacy_a01's `DropSafe`, a wood-brown cube with a faint dial, under its spot -- the same
colour as the floor and the crates, nothing on it a player reads as a safe. The walker: more shape (retopology) or more
than one material and colour. The owner of the species is Zoo; whether a steel-grey body, a door seam, a handle and a
lit keypad are inside the modern low-poly standard's budget (`modern-low-poly-standard`) is to be priced.

## 4. A rod across the office's stairwell

`04_rod_over_stair.webp`: looking down the office's stair from its head, a thin pale horizontal bar spans the
stairwell at about head height over the flight, which the walker walked through (no collision). Not yet named: a
handrail or guard rail laid across the flight rather than along it, or a light rig's pole. First step: name the node
from the walk copy (every visible instance crossing that span, as `hole_column.gd` did for finding 1 of 9383's walk).

**Measured 2026-10-23, NOT YET NAMED.** The building is `b2`, spec `office` (placed at Godot 54, 0, -0.49;
`buildings.json`). The overlay's `pos` is the EYE (`debug_overlay.gd:443`): local (0.6, 2.2, 2.09), at the foot of
flight 0 of the office's switchback (`office_stair_0`: flight 0 at local x 0..1.6 rising toward -z to the landing at
y 3.4-3.6, flight 1 at x -1.6..0 rising back). Its centre ray hits `slab_col_2` 13.07 m off at y 6.90, so the walker
was looking UP the flight, through the slab hole. Ruled out, each by measurement, instruments beside this README:

  * a spec volume: `specs/office.json` holds no volume with two sides under 0.2 m within 8 m;
  * a rod-shaped node anywhere in the walk scene (`thin_rods.gd`, two sides under 0.1, one over 1.0 m:
    nine found, all sign posts and two merged shop-front mullions, none near) or in the office's
    `site_base.glb`, dressing or fixtures (`glb_rods.py`);
  * Deli Counter's slab: `build/office.glb`'s `slab_1_t2_3` is a frame round the hole, x -2..2, and no bottom
    face covers a point over the flight;
  * the ceiling skins: both storey-0 panels void the hole (`office.slots.json`, voids x -2..2, y -2.65..3.15) and
    hold nothing but ceiling tile (`glb_faces_in_rect.py` on the themed assembly's panels);
  * a fixture over the hole below 10.4 m (`fixtures_in_stairwell.out.txt`).

**Refuted and kept:** `faces_in_box.gd` found a 6 mm concrete island at y 3.294-3.300 in `b2/MergedR_250`, and it
was read as a plate across the hole. `merged_plate.gd` then showed that mesh is the flight's two full-height guards
(`stair_guard_side_2`, `stair_guard_back_10`, Zoo props `w40_d375_h330` and `w160_d106_h330`) and the island their
L-shaped tops: its bounds spanned the hole, its triangles did not.

Next: shoot the walker's view from the eye with the camera's own basis and pick the rod's pixels by hiding
candidates, rather than by bounds -- every bounds-based instrument above has been answered.

**NAMED, 2026-10-24: the two storey-0 ceiling skins' rims.** Done as above. `tools/look_shots.py` gained a
`hide:<node name>` switch (wildcards allowed) to attribute a frame's pixels; the walker's view reproduced from their
eye under the inspection light (`walker:54.6,2.2,1.6 -> 54.6,5.8,-7.73`) shows the bar at row 382. Hidden by family,
then by digit, the bar's band (rows 379-386, columns 660-1040, 0-255 grey) against the ceiling above it (rows
360-370):

    as shipped                         bar 131.7   above 54.2
    every MergedR_* hidden             bar  34.6   above 34.0      the bar goes
    MergedR_2* hidden                  bar  54.5   above 54.2      the bar goes
    MergedR_27* alone / MergedR_278    bar 125.0   above 54.2      dimmed, not gone
    MergedR_251 alone                  bar 131.7   above 54.2
    MergedR_251 + MergedR_278          bar  54.5   above 54.2      the bar goes

`b2/MergedR_278` is the lobby's ceiling skin and `b2/MergedR_251` the ground bullpen's (2 cm at y 3.28-3.30, meeting
at z -0.49, the line between the two rooms). Zoo's `arch.plate_voids` inset every void `PLATE_RIM` (2 cm) from every
edge it reached, "invisible from below": the stairwell crosses that room line, so each ceiling kept a 2 cm rim across
the hole there, back to back -- the bar. **Fixed in Zoo 1.122.0** (`patches/patch_zoo_plate_rim.py`): the rim only on
a side a void would take end to end.

**Refuted and kept, a second time:** `rod_pick.gd` (a `--script` probe hiding meshes and diffing the band) scored
against a BLACK frame -- it replaces the main loop, so the walk copy's warm-up never finished; every candidate "moved
the band" the same 0.34 and its leader (`MergedR_182`, the storey-1 wood rails) meant nothing
(`rod_pick_black_frame_REFUTED.out.txt`). It now refuses a black first frame, and did, which is why the work moved to
`look_shots`, which waits for the warm-ups.

## 5. Office monitors are still pictures

`05_office_screen_static.webp`: the office's cubicle monitors show a fixed screen ("READY", and the neighbour's
desktop) with no movement, where the strip club's TVs carry the screen effect that gives them life (the moving-screens
work, `levels-feel-static-make-them-alive`). The walker: every screen the same. To find: which rule decides which
screen species carry the effect, and why a monitor is outside it; then the effect on every screen, priced -- an office
floor holds many monitors, so a per-screen cost is multiplied (`CLAUDE.md`: per-frame work that scales with prop count
is a shape already refused; a shader-only effect, no script, would not scale that way).

**Owner found, 2026-10-23.** The shimmer is Level Factory's import pass (`assets/godot/zoo_worldskin.gd`, CRT MOTION,
0.89.0): a darkening overlay hung off a lit screen material's `next_pass`, phased per node from
`NODE_POSITION_WORLD`, safe through Lux's power cut. It takes a material only by name -- `M_*CRT_Screen*_Face`
(`_is_crt_face`) -- and Zoo 1.115.0 names a desk monitor's lit screen `M_StockScreen_<atlas>_Face`
(`recipes/_card_atlas.build_art`, from `bpylayer/prim_mesh.build_stock`), so no monitor was ever given it. The fix is
one more mark in `_is_crt_face`. **Its price is owed first** (`CLAUDE.md`): each overlay is a `next_pass`, one more
draw for every screen in view -- the club's handful of TVs measured below the noise floor, an office floor of twenty
desks is twenty more submissions. Measure draw calls and frame time at the office's stations, pass on and off, with a
control, before it ships.

**Fixed in Level Factory 0.239.0** (`patches/patch_lf_desk_screens.py`), priced first (`patches/lf_desk_screens/`):
the desk screens live in the export's merged lit meshes (`LitR_*`, 20 in the office, 3 in deli_a03, one atlas
material -- `screen_holders.gd`). Three arms of 9387's raw package: the twelve stations 0-19 draws more and a p95
move inside the control's spread; the office bullpen facing the desks 91 -> 110 draws, 1.98 ms against controls 1.82
and 1.85.


## 6. The office's double stair: walling and railing look unnatural

`06_double_stair_walls.webp` (the walker's mark round the upper flight's side): the office's switchback stair -- a
flight up beside the opening of the flight down -- reads as solid slabs: the up-flight's side is a full-height plain
block (marked), the down-flight's opening ringed by a dark wood guard wall and a slab-edged stair head. The overlay
names `stair_guard_rail_4_col`, a Deli Counter stair guard. The walker: the walling and railing do not look natural
yet. Related and recent: Deli Counter 0.262.0 builds every library stair solid underneath, which is what stands the
side and back guards; a real stair of this shape has a half-height balustrade or a rail on posts over an open string,
a wall only where it meets a real wall. To read before changing: which guard kinds stand here (side, back, rail), at
what heights, and what the real-world forms are.

**The walker's pick, 2026-10-23: the compact U-shaped staircase** (`stair_refs/ref_4_compact_u_rcc_section.png`, of five
references they sent, all in `stair_refs/`). Its form, as the drawing gives it: two parallel flights of about 900 mm
clear width side by side in a well about 2.1 m wide and 3.5 m long; a half landing the well's full width and about
900 mm deep at the turn; a waist slab (150 mm) under each flight; masonry walls enclosing the well's outer sides;
risers about 164 mm, treads about 280 mm, 3.0 m floor to floor. So walls are right where they ENCLOSE the well; the
edge between the two flights is the one that should read open, with a rail. The other four references (open treads
with cable or glass guards, a concrete well, a masonry dog-leg) are kept as the range, not the target.

## 7. Wide empty ground

`07_empty_ground_a.webp` (from beside cover_155 toward the east fence) and `07_empty_ground_b.webp` (down the street
past the warehouse): broad dark ground between the buildings and the fence, nothing standing on it but scattered
litter and a tree. The walker, against the land-use guide (`land-use-guide-informs-lot`): urban land is valuable and
would be filled; a wide empty space should not be the norm without being talked about -- and "careful how we solve
this one". Where it stands: Lot's land-use work shipped doors to the street, dumpster pads and parking fields
(2026-10-03) and left the site's remainder -- ground no use claims -- at 55-64 % against the design's under-15 %
band; one building line, verges and vacant lots were next and not started. The care: that ground is also where fights
are fought, so any fill is measured on fight space (the gunfight-first rule, `game-is-a-series-of-shooting-galleries`)
as well as on the remainder, and a large open space that stays should be a named, deliberate use (a lot, a yard, a
park), never the leftover.

**MEASURED 2026-10-24, cold run 9391's site** (`landuse/remainder_map.py`, which keeps the census's own grid --
`tools/landuse_census.measure`, shares checked equal to the census row; maps `landuse/remainder_9391*.webp`, red the
remainder). **First, the instrument was wrong:** the census paints `buildings` only, and a street's Empties are the
spec's `blockers` -- 26 rowhomes along the south street here -- so their footprints read as remainder. Counted as built
land: buildings 12.5 % -> 23.1 %, remainder 58.4 % -> 47.7 % (`remainder_9391_with_blockers.out.txt`). Every land-use
figure since 2026-10-03 overstates the remainder on a level with an Empty row; the fix is Lot's (`site_landuse`).
**What is left, 9,160 m2 in two pieces:** one of 7,910 m2 that reaches the plate's edge -- the strip north of the north
road across the plate's width (no facing row there), the ground east and north of the office the walker's two frames
look over, and the verges at the plate's west and east ends -- and one of 1,252 m2 inside the block, behind deli_a03
and the pharmacy, between them and the north road (the back of the block).

**The walker, 2026-10-24: "my caution is around its ok for levels to have open areas but it should be with intention and to support gameplay not just because we forgot to put something there".** So the rule the options are judged by: every open area a NAMED use with a gameplay reason the site records, and drawn as that use; ground with no reason is filled.

**Options, to be talked through as the walker asked, none built:** (a) a facing row of Empties along the north road,
as the urban type already stands on its far side (roadmap 241) -- streets read as streets, and the remainder falls
most; (b) the back of the block as yards and an alley -- fenced back yards, a service lane, the dumpsters' pads --
where a heist approach can still come in; (c) the east ground as one NAMED open use -- a parking lot, a vacant lot
behind a fence with rubble and weeds, or a pocket park -- kept open because a fight wants it, and drawn as that use;
(d) the plate-end verges as grass and sidewalk to the fence. Every one is measured twice: the remainder, and the
fight space (`game-is-a-series-of-shooting-galleries`) -- Laser Tag's sightlines and cover on the same seed before and
after.

**A PROPOSAL, DRAWN, nothing placed (roadmap 306 step 1; `landuse/classify_remainder.py`, `roles_9391.webp`,
`roles_9391.out.txt`).** Each remainder cell takes the first role whose test holds: fight space within 12 m of the
mission's legs or the encounter's 23 markers and cover; rear yards and alley behind a building or Empty, within 25 m of
its back face; street frontage with no row; verge within 8 m of the plate's edge; open. Of 9,143 m2: fight 864 (9 %),
rear 2,164 (24 %), frontage 3,575 (39 %), verge 1,244 (14 %), open 1,297 (14 %) -- the open being mostly the ground
east and north of the office the walker's frames look over. A first draft read the markers in a shape they do not have
and called 94 m2 fight space; kept in the script's comment.

## 8. A garbage can mid-floor

`08_litter_bin_mid_floor.webp`: deli_a03's `litter_bin_r2f2d413e_11` -- furnish's (its `_r<crc>_` name) -- stands
alone in the floor at the end of an aisle. The walker: inside a building a can stands against a wall. Owner: Deli
Counter's furnish recipes, several of which list `litter_bin` as a floor cluster (`(("litter_bin",), 1, 1)` in the
shop floor's, the lobby's, the gallery hall's) rather than a wall piece. The rule a fix states: an indoor litter bin is
a wall piece, in every recipe. The arrangement census (`arrangement.py`) already reads such a bin as loose.

## 9. A large plain wood block in the stockroom

`09_pallet_stack_block.webp`: in deli_a03's `stockroom_loading` (spec x 16, y 7.6 from the walker's position, b0 at
world -51, 0, -2.51), the piece 4.7 m off is the spec's authored `loading_pallet_stack` -- 4.5 x 2.5 x 1.5 m at (12, 10)
-- rendered as one wood-textured block. Named from the spec by position (no other piece over 1.5 m2 within 5 m but a
kitchen counter); not yet confirmed against the walk copy's node. Same root as finding 3: the Zoo species a piece of
this kind builds reads as a box -- pallets, wrapped goods, the gaps between them are what would make it a pallet
stack. The walker: collision good.

## 10. The bus stop sign stands back from the road

`10_bus_stop_sign.webp`: a BUS STOP sign on its post at the back of the sidewalk, beside a building's wall and door,
not at the curb. The walker: it speaks to drivers -- no parking, the bus pulls in here -- so it belongs at the road's
edge. Owner: Lot's street furniture. The rule to check it against: `docs/STREET_RULES.md` (the MUTCD's curbside
placement the stop signs already follow, `stop-sign-placement-follows-mutcd`); a bus stop sign stands at the curb, set
back from the travelled way as a sign is, beside where the bus stops.

**Fixed in Lot 0.127.0** (`patches/patch_lot_bus_flag.py`): `_bus_stop` stood the flag `BAND_INSET` in from the
band's BACK edge; it now stands with its plate's near edge 2 ft from the curb face (PennDOT LTAP TS 181, the urban
curbed-street offset; `docs/STREET_RULES.md`, "Bus stops"). On Lot's probe street the flag moves from 7.55 m off the
centre line to 5.76 m, the curb at 5.0. **Open, the second half of the walker's reason:** parking bays still run past
the stop -- `site_streets.bays(road)` is computed from the road alone by five modules while the stop is placed later
against what already stands, so keeping the stop's length free of parked cars is its own change.

**Fixed in Lot 0.131.0** (`patches/patch_lot_bus_zone.py`): a stop's zone, 120 ft centred on its shelter (NACTO's
midblock length for a 40 ft bus, `docs/STREET_RULES.md`), holds no bay -- no car, no meter, no paint. On cold run
9391's themed site assembled both ways: 3 stops, 6 cars, 12 meters and 14 bay ticks in the zones -> none
(`patches/lot_bus_zone/zone_check.out.txt`).

## 11. The traffic lights never change

`11_traffic_lights_static.webp`: the intersection's signal heads hold one state, never cycling. The walker's ask
belongs with the levels-feel-static work (`levels-feel-static-make-them-alive`: screens, unsteady light, moving parts
shipped). What a fix states: the intersection's heads on ONE shared clock, the crossing directions in opposition (green
and amber one way while the other is red), a real green-amber-red cycle with an all-red gap -- driven by a shader or
one timer for the junction, never a script per lamp (`CLAUDE.md`: per-frame work that scales with prop count is
refused). Owner to find: which tool builds the signal heads (Zoo's species, Lot's placement) and which lights them
(Lux).

## 12. No signal facing this approach

`12_no_signal_this_approach.webp`: approaching the junction from the other direction, no signal head faces the driver
-- the mast arm's heads face the opposite approach. With finding 11 one system: a signalled junction has a head (or a
mast-arm head and a near-side head) facing every approach, the crossing directions on one clock in opposition. To
find: whether the site draws a signal for one approach only, or each assembly is placed and oriented for one
direction; then a junction-level rule from Lot, checked against the MUTCD's signal-face placement the street rules
draw on (`docs/STREET_RULES.md`).

**Owner found, 2026-10-23 (findings 11 and 12 together).** Lot's `site_furniture.plan_traffic_control` stands a signal
ONLY on a signalised junction's yielding (minor) approach: `ap.control == "signal" and not ap.minor` is skipped. Its
pole stands on that leg's right kerb at the mouth, yawed along the leg's travel, and Zoo's `traffic_signal` hangs its
two heads facing local -y off an arm along local +x -- so the heads face ACROSS the yielding road, serving one
direction of the road it meets. Nothing faces the yielding driver, and on a T the far direction of the major road is
served by nothing: the walker's finding 12 on both counts.

**The rule a fix builds to** (MUTCD 2009 4D.14, quoted in the Delaware Administrative Code's copy; FHWA
interpretation 4-358): at least TWO primary faces for each approach's through movement, at least 8 ft apart, at least
one of them no less than 40 ft and no more than 180 ft beyond the stop line. Zoo's signal already carries two heads
about 4.3 m apart (the arm's and the pole's), so ONE FAR-SIDE SIGNAL PER APPROACH answers it: its pole beyond the
junction on the approach's right, its arm reaching back over the approach's lanes, both heads facing the approaching
driver. On a four-way each corner is the far-right corner of exactly one approach, so Lot's one post a corner holds.

**Finding 11 on top of it:** the lenses already wear one material per colour (`M_TrafficSignal_Lens_Red/Amber/
Green`, Zoo's recipe says gameplay or a Lux row would drive which is lit). A cycle costs no per-frame CPU as a shader
on those three materials driven by TIME, the junction's two directions in opposition by a phase each signal carries --
priced on/off at stations before it ships (`CLAUDE.md`), and kept out of the light bake, which would freeze one state.

**Correction, 2026-10-24: the cycle already existed.** Level Factory 0.165.0 gives each lens a lit shader on one 60 s
clock (green 33, amber 4, red 23 s), and both 9386's and 9387's packages carry it (`lens_materials.gd`,
`lens_materials_938[67].out.txt`) -- the lights DID change, once a minute, which a passer-by reads as never. And on
one clock, Lot 0.128.0's far-side signals put every head at a junction on green together (9387's frame).
**Fixed in Level Factory 0.238.0** (`patches/patch_lf_signal_opposition.py`): a head's facing picks its half of a 48 s
cycle (green 18, amber 4, red 26 with a 2 s all-red), so a junction's two directions take turns; measured on a
re-imported copy of 9387 (`patches/lf_signal_opposition/heads_shipped_over_trial.png`).

## 13. Rowhome doors without knobs

`13_rowhome_door_no_knob.webp`: gs_empty_rowhome_j's front door (an Empty, `empties-get-dark-interiors`: its doors
shut by design) -- a flat grey slab in its frame at the top of the stoop, no knob, no handle, no panels. The walker:
many of the rowhome doors. To find: which door species the Empties' shut doors build as (Zoo's door leaf, or a greybox
panel the Empty's merge stands in), and whether the hardware the library's working doors carry exists for them; then
every door a player can see, shut or open, with its hardware.
