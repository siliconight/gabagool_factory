# The asset wishlist, read against what the factory builds (2026-10-19)

**The ask.** The walker, handing over `docs/reference/PA_1999_Heist_Game_Asset_Wishlist_FINAL_GO_AHEAD.md` (v2.1, 224
asset families with taste rules): "interesting document that may help us make assets we don't know we need to make our
levels feel more alive as we make them (ignore the animation, sound, and anything else that isn't part of the level
factory pipeline, but of what to make and add if it helps make things look great)".

**Read in full, all 779 lines.** In scope by the walker's terms: families A (architecture), B (streets), C (interiors
and services), D (retail and food), E (workshops and transport), F (signs and print), G (materials), H (landscape),
I12 (vehicle parts), J (specialist destinations) and the physical half of K (safes, cameras, alarms, loot) -- the things
a level is built from. Out: L people, M weapons, N animation, O effects (the factory owns FX hooks only, roadmap 235),
P sound, Q interface. The document names one real person, Robin-Yann Storm, as the author of a public article it cites
(R1); it names no real brand.

## What the generator already asks for and Zoo cannot build

The strongest evidence of an asset "we don't know we need" is one the pipeline already places. `box_slots.py` reads
Deli Counter's built slot manifests: **1,486 of the tracked library's 10,048 prop slots (14.8 %), in 142 names, name no
species, so Zoo builds each as a plain box at the slot's size** (`box_slots_library.out.txt`). Some are boxes on
purpose -- `prop_species.PROP_SPECIES` maps crates, columns, pillars, carts, planters, canopies, kiosks and vaults to
None -- and some only because no word reaches a species that exists. By count:

| Name (slots, specs) | Wishlist family | What it is today | What it could be |
| --- | --- | --- | --- |
| `stair_guard_rail` / `_side` / `_back` (1,025 in 98) | A07, A17 rails | a stair's own guards, plain boxes | a guard species: posts, a rail, a kick plate |
| `col`, `canopy_col`, `column`, `pillar` (146 in 14) | A09, A13 | boxes | steel columns, pipe columns, brick piers |
| `stoop_tread`, `stoop_landing` (37 in 13) | A04 | boxes | boxes are right for treads; nothing to do |
| `pump_island` (21 in 7) | B07 | a box | a painted concrete island with its bollards |
| `crate_stack_*`, `crate`, `crate_row`, `stash_crates` (44 in 17) | E01 | boxes on purpose | cover that reads as goods: a supplier's cartons |
| `slots`, `slots_b` (13 in 3, the casinos) | D11 | boxes | a slot machine (`video_poker`'s neighbour) |
| `stall`, `stall_b` (13 in 3, the market halls) | D16 | boxes | a market stall: awning, counter, crates of produce |
| `lift` (8 in 4, the auto shops) | E06 | a box | the auto shop's vehicle lift, its centrepiece |
| `planter_box_*`, `planter` (15 in 7, deli_a01-a03 among them) | H03 | boxes on purpose | "a shopkeeper's cared-for pots" |
| `kiosk*` (13 in 6) | B/J | boxes on purpose | a ticket or concession kiosk |
| `pizza_oven`, `dough_mixer` (4 in 2) | D07 | boxes | the pizza shop's oven frontage |
| `jukebox` (2), `keg_stack` (2), `club_bar` (2) | D10, D11 | boxes | a jukebox; kegs; the club's bar |
| `forklift_bay` (2), `roof_ac` (1) | E04, C23 | boxes | a forklift; `roof_ac` should reach `hvac_unit` |

Two other ways a piece is less than it says, read off the same table: a `locker` is built as a `filing_cabinet` and
a `workbench`, `tool_bench` or `cage` as a `counter` -- stand-ins, each a visible lie in the room it furnishes
(C11, E05). And `roof_ac` and `club_bar` miss species Zoo already has (`hvac_unit`, `back_bar`): a word in
`PROP_SPECIES`, not a new asset. Not measured here: the share in Level Factory's own buildings (`lf_*`, built in a
level's workspace, not in `deli_counter/build/`); a cold run's package answers it.

## What nobody places yet

Families the wishlist calls foundation (P0) or core (P1) that no Deli Counter recipe places and no Zoo species
builds. Each is small, repeats across a block, and says the place is used -- the document's "Use" and "History" tests:

- **B08 building service clusters** -- gas and electric meters, disconnects, a cabinet: on every rowhouse front and
  store rear, what makes a wall a building's.
- **C12 window air conditioners and radiators** -- the window unit on a 1999 rowhouse or walk-up facade; a radiator
  under a window inside.
- **K08 the alarm bell box** over a storefront, and its panel inside; **C15** an extinguisher, an exit sign, a pull
  station -- grounding objects the document asks for in every working building.
- **C08 washroom fixtures** -- basin, mirror, stall panels: the tracked library has one restroom, gs_corner_station's,
  and a water heater is all that stands in it.
- **B13 a temporary job** -- cones, a road plate, a barricade, a work light, a contractor's sign: "one temporary job
  changes the route". The floor-hole kit (roadmap 265) is the first of these indoors.
- **E02 hand trucks and stock carts** -- a delivery half-done at the rear door: the first mission's own story.
- **C07 / C09 the upper room** -- a bed, a wardrobe, a sofa, a domestic kitchen: the delis' apartment above the
  shop and the walk-ups' bedrooms. "The upper room with its own life" is one of the document's twenty signature
  builds.
- **C17-C19 the office and the stereo** -- a computer, a phone and fax, a component stereo: the cash office and the
  safehouse corner.

## The rules that map onto the pipeline

- **"Put the visual budget where somebody put their money"** (3.1): one hero purchase per owner -- the bar's taps,
  the shop's cooler, the auto shop's lift -- and the rest plain. The factory furnishes by room kind; nothing chooses an
  owner's one investment. That is a furnish rule, and it is the authorship guide's "specificity over uniform polish"
  (`docs/AUTHORSHIP_GUIDE_APPLIED.md`) made concrete.
- **The room dressing order** (section 9): purpose, construction, arrangement, composition, personal choices, *current
  task*, surface history, play review. A "current task" -- a delivery mid-unload, a meal being made, a repair open
  on a bench -- is the step the factory's furnish recipes were not checked for here; the floor hole's kit is one.
- **"Every object needs support; wires, pipes, ducts need destinations"**: already the factory's floater rule
  (roadmap 234) and the pole line's service drops (240).
- **"Make objects connect the world"** (section 9): the same supplier on the cartons, the truck and the bar's stock.
  Whether the factory's invented brands carry across props was not checked here.
- **The taste test and the five questions** (sections 2 and 11) -- form, use, desire, history, play; "what would I
  remember about this room tomorrow?" -- are candidate wording for roadmap 18's missing gate, beside the authorship
  guide's rubric.

## Tensions for the walker, not decided here

- **Brand tone.** The document: "Avoid making every brand a sex joke". The walker's standing call: invented Delco
  brands, "funny and crass", PG-13. The walker's taste stands; the document is noted.
- **Vehicles and rights.** The document: "Removing a badge from an otherwise recognizable product ... does not
  establish clearance". The getaway van is drawn from a real step-van chassis (the P30, `GETAWAY_VAN_COMPS.md`); the
  document's own crew van is "a compact, boxy cargo body in deep navy, cream steel wheels". A rights review is not the
  factory's call.
- **What the stair guards should look like.** 1,025 boxes in 98 specs is the largest count above, and nobody has
  looked at one in a frame to say whether a box reads wrong as a guard rail.

## What is not proven

Nothing above was seen in a level: the counts are of slot manifests. Whether a plain box reads as a placeholder at
play distance -- the claim that makes the table a to-do list -- is the walker's eye, one frame each.
