# The walker's walk of cold run 9386, 2026-10-23

The walker played `_runs/walk_9386_restaurant_row_001` (Deli Counter 0.264.0, Level Factory 0.237.0; restaurant_row_001
at seed 9003). Their words and the overlay's figures, as they reported them; each is investigated in its own section
as it is measured. Screenshots are the walker's, kept beside this (`NN_*.webp`).

| # | the walker | where (overlay) | state |
|---|---|---|---|
| 1 | "still doensn't look irght to have 2 signs on top of each other like this and not centered... in real life this would be 1 sign" | pos -7.1, 1.6, 17.6; bldg b1 pharmacy_a01 | filed, not investigated |
| 2 | "textures have visible seams and it doesn't look as continous as it could be" (lines marked on the frame) | pos -8.0, 1.6, -0.1; pharmacy_a01, GreyboxBase; look ext_col_0_N_open0_BREACHPANEL 10.49 m | filed, not investigated |
| 3 | "drop safe looks like a brown box, needs more retopology or multiple texture/colors to see it better imo" | pos 9.4, 1.6, -4.6; bldg b1 pharmacy_a01; look DropSafe 2.75 m | filed, not investigated |
| 4 | "non collision rod on the stair case that shouldn't be there" | pos 54.6, 2.2, 1.6; bldg office, GreyboxBase; look slab_col_2 13.07 m | filed, not investigated |
| 5 | "screens should have the same effect as the tvs in the strip club that give them that little movement/\"shimmer\" to show \"life\"" | pos 47.0, 8.8, -7.3; bldg b2 office; a cubicle's monitor | filed, not investigated |
| 6 | "something about the doulbe stairs still needs some work to not look so odd...mainly the walling/railing doesn't loook natural yet" | pos 55.7, 5.2, -6.0; bldg office, GreyboxBase; look stair_guard_rail_4_col 8.37 m | filed, not investigated |
| 7 | "this empty space goes against the doc i sent you about the value of urban land and how it would be filled in with things...careful how we solve this one....but it should be not the norm to have these wide empty spaces without talking about it" | pos 70.7, 1.7, 15.8 (cover_155) and 99.4, 1.6, -21.0 (Site) | filed, not investigated |
| 8 | "garbage cans are usually up against walls inside buildings" | pos -51.6, 1.6, -2.6; deli_a03, GreyboxBase; look litter_bin_r2f2d413e_11 3.26 m | filed, not investigated |
| 9 | "good collision, but not sure what this large boring wood block is...." | pos -35.0, 1.6, -10.1; bldg b0 deli_a03; look Prop 2.55 m | named: `loading_pallet_stack` |
| 10 | "bus stop sign is for cars/buses so there is no parking ther...so it sohuld be closer to the road" | pos 19.8, 1.7, -2.6; look nothing within 60 m | filed, not investigated |
| 11 | "traffic lights done change?" | pos 7.9, 1.7, 16.7; the intersection's signal heads | filed, not investigated |
| 12 | "where are the traffic lights for this side of the road?" | approaching the same junction from the other side (near gs_empty_rowhome_h) | filed, not investigated |
| 13 | "many of the rowhome doors dont have doorknobs?" | pos 15.6, 1.6, 24.4; bldg blocker_15 gs_empty_rowhome_j | filed, not investigated |

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

## 5. Office monitors are still pictures

`05_office_screen_static.webp`: the office's cubicle monitors show a fixed screen ("READY", and the neighbour's
desktop) with no movement, where the strip club's TVs carry the screen effect that gives them life (the moving-screens
work, `levels-feel-static-make-them-alive`). The walker: every screen the same. To find: which rule decides which
screen species carry the effect, and why a monitor is outside it; then the effect on every screen, priced -- an office
floor holds many monitors, so a per-screen cost is multiplied (`CLAUDE.md`: per-frame work that scales with prop count
is a shape already refused; a shader-only effect, no script, would not scale that way).

## 6. The office's double stair: walling and railing look unnatural

`06_double_stair_walls.webp` (the walker's mark round the upper flight's side): the office's switchback stair -- a
flight up beside the opening of the flight down -- reads as solid slabs: the up-flight's side is a full-height plain
block (marked), the down-flight's opening ringed by a dark wood guard wall and a slab-edged stair head. The overlay
names `stair_guard_rail_4_col`, a Deli Counter stair guard. The walker: the walling and railing do not look natural
yet. Related and recent: Deli Counter 0.262.0 builds every library stair solid underneath, which is what stands the
side and back guards; a real stair of this shape has a half-height balustrade or a rail on posts over an open string,
a wall only where it meets a real wall. To read before changing: which guard kinds stand here (side, back, rail), at
what heights, and what the real-world forms are.

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

## 13. Rowhome doors without knobs

`13_rowhome_door_no_knob.webp`: gs_empty_rowhome_j's front door (an Empty, `empties-get-dark-interiors`: its doors
shut by design) -- a flat grey slab in its frame at the top of the stoop, no knob, no handle, no panels. The walker:
many of the rowhome doors. To find: which door species the Empties' shut doors build as (Zoo's door leaf, or a greybox
panel the Empty's merge stands in), and whether the hardware the library's working doors carry exists for them; then
every door a player can see, shut or open, with its hardware.
