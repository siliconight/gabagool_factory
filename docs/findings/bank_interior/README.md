# A bank interior that reads as the walker's comps (roadmap 321, the bank first)

The walker, 2026-10-27: "we need to prioritize a great looking bank interior next", with twelve comps read in
`docs/reference/BANK_INTERIOR_COMPS.md`.

## The baseline: MEASURED, 2026-10-27

`bank_block_001` at seed 9082, the level cold runs 9364-9366 made. It was made fresh on the day's tools
(`workspaces/bank-look-1027-ws`, `batch.json` here; `level_factory make`, not a cold run): Level Factory 0.261.0,
Deli Counter 0.279.0, Zoo 1.134.0, Lux 0.80.0, Pixelcoat 0.63.0. Its bank is `bank_branch_a02`, building b0 at Godot
(-60, 0, 6.97), unrotated, so plan (x, y) -> Godot (-60 + x, h, 6.97 - y). `shoot.sh` walks it and shoots six stations
twice: in the level's own light (`frames/01_*`) and under `look_shots --inspect studio` (`frames/02_*`).

| station | the level's light, mean / p50 | inspection light |
|---|---|---|
| lobby_entry (the door, facing the teller line) | 37.2 / 33 | 76.1 / 67 |
| lobby_wide | 33.7 / 27 | 59.7 / 54 |
| behind_line (staff side, facing out) | 46.4 / 42 | 80.0 / 70 |
| manager_office | 80.5 / 76 | 117.0 / 105 |
| vault (storey -1) | 39.9 / 39 | 108.3 / 118 |
| vault_west (storey -1) | 29.9 / 30 | 87.8 / 75 |

For scale, the supermarket's aisles read 87.8 and 91.1 the same day, after roadmap 319.

What the frames show, against the comps:

- **The lobby is dark and bare.**
  - It has 10 lamps over 390 m2, one per 39 m2 (`build/bank_branch_a02.lights.json`). The ceiling grid reads dark grey
    and the walls are raw concrete.
  - On the floor: a few stanchions, a low bench, two bins.
  - No check desk, no planters, no poster stands, no date clock. The recipe stands vending and a cigarette fixture
    there (`level_design._RECIPES["lobby"]`).
- **The lobby floor is maroon carpet** (inspection frame). `floors.FLOOR_BY_ROLE["public_entry"]` is carpet, and
  0.271.0's note keeps it on purpose: "right for a lobby, a banking hall or a parlour". The comps say otherwise for a
  bank: terrazzo or pale tile in public in 1, 2, 4, 6 and 7, carpet only behind the line (3, 5).
- **The teller line reads.** A wood front, glass windows at pitch, an enclosed staff side
  (`enclose_teller_lines`, the walker's ask on cold run 9048). It is the room's strongest shape, as in the comps,
  standing in the dark.
- **The manager's office** is bright and plain: concrete walls, bare desks and cabinets.
- **The vault floor** has count tables with cash, safes, a cage wall and a round vault door: the bones are right.
  - It is lit by bare-bulb pendants (`lights.py`'s moody rule): 6 lamps over 330 m2, one per 55 m2, a mean of 30-40.
  - The comps light money rooms with bare tubes on steel (10, 11), and show safe-deposit boxes (12) and cash carts and
    hampers (10, 11). The vault floor has none of them.

## Step 1 shipped: Deli Counter 0.280.0 (fef9d2f9), light and floor

A bank's public room is lit at a selling room's density with the bake-only reach, and floored in tile. Its rooms below
grade and over the take are lit by tubes, not moody bulbs. A split row's one-lamp runs keep the row's `bake_reach`.

The same mission and seed, made on 0.280.0 with every other tool the same (`workspaces/bank-look-0280-ws`,
`after_0280.sh`), shot at the same stations (`frames/03_*`, `frames/04_*`):

| station | before, mean / p50 | 0.280.0 | inspection light, before -> after |
|---|---|---|---|
| lobby_entry | 37.2 / 33 | 101.1 / 98 | 76.1 -> 159.0 |
| lobby_wide | 33.7 / 27 | 94.2 / 96 | 59.7 -> 138.1 |
| behind_line | 46.4 / 42 | 62.0 / 54 | 80.0 -> 94.3 |
| manager_office | 80.5 / 76 | 80.8 / 76 | unchanged (the control: no rule names it) |
| vault | 39.9 / 39 | 72.2 / 70 | 108.3 -> 129.9 |
| vault_west | 29.9 / 30 | 49.0 / 47 | 87.8 -> 103.2 |

**Priced** (`price.py`, `compare.py`, `compare.out.txt`; control twice and the subject, one session, nothing else
running), 53 headings at the package's own stations:

- **Draws:** subject minus the controls' mean, median +0, largest +34. The controls agree to the draw.
- **p95:** median +0.151 ms. The controls' own a - b is median -0.173 and largest 0.662, so the median is inside the
  instrument's floor.
- **ONE HEADING PAST THE FLOOR, UNEXPLAINED:** `attacker_spawn_2` at yaw 270 reads 8.77 ms against 7.40 and 7.47
  (+1.33), with +10 draws. It is outside the bank, and nothing here says why it moved. Not re-measured.

What the frames show now: a bright, even lobby on a pale tile floor, the teller line reading across it, the vault lit by
tubes. And what they show is still missing:

- an EMPTY lobby (a bench, two bins and stanchions on the floor);
- raw concrete walls in every room;
- the manager's office and the staff side on concrete.

Steps 2 to 4 follow.

## Steps 2 and 3 shipped: Zoo 1.135.0 (7c8489c) and Deli Counter 0.281.0 (cc301ed1), the lobby's furniture and the carts

- **Zoo 1.135.0** draws `check_desk` (a standing-height island, a dark top, brass slip pockets, comp 1's date block)
  and `cash_cart` (a steel cage cart on casters, its load the variant).
- **Deli Counter 0.281.0** furnishes a bank's public room as `bank_lobby`: the check desk its anchor, waiting chairs,
  an ATM, a queue, and none of the general lobby's vending, cigarettes, payphone or sofa. A bank's vault is
  `bank_vault`, with a cash cart beside its count table.

The same level on both (`workspaces/bank-look-0281-ws`, `after_0281.sh`; `frames/05_*`, `frames/06_*`): the check
desk stands mid-floor before the teller line, the vending and cigarettes are gone, and carts stand in the vaults. Light
moved only where a piece now stands (lobby_entry 101.1 -> 101.8, vault_west 49.0 -> 51.9).

**Priced** against the 0.280.0 package (`price_0281.py`, `compare.py perf_0281_`, `compare_0281.out.txt`), 53
headings:

- **Draws:** median +0, from -27 to +5. The lobby's dropped pieces outweigh the desk and the carts.
- **p95:** median +0.011 ms, inside the controls' own floor of 0.850.

**0.280.0'S OUTLIER DID NOT REPRODUCE.** `attacker_spawn_2` yaw 270 read 8.77 ms on the 0.280.0 package in the first
session. The same package reads 7.21 and 7.16 there in this one: session drift (roadmap 271), not the change.

**Two first applies stopped in their gates**, both before any commit, and are kept here:

- **Zoo's:** the species were unreachable by prompt (underscored keywords; the spaced names added).
- **Deli Counter's:** five tests pinned the old bank lobby, and only the furnish tests had been run on the clone.
- The first build of 0.281.0 also put a cash cart in every `vault`-kind room, 44 specs including a deli's back safe.
  `bank_vault` scopes it to banks.

Left: the cart reads brown, the theme's `metal` skin; and every wall is raw concrete -- step 4.

## Step 4 shipped: Zoo 1.136.0 (06ab3b8) and Deli Counter 0.282.0 (ab4e4279), the walls, the cameras, the plants and the clock

The walker, shown 0.281.0's lobby: "fix it before we rush to the release", then "were there cctv cameras in the 90s?"
and "cameras first" (the reference's researched section: the Bank Protection Act of 1968, time-lapse VCRs).

- **Zoo 1.136.0** draws `planter` (a square commercial pot, the variant the plant) and `wall_clock`.
- **Deli Counter 0.282.0** plasters a bank's concrete walls inside above grade (below grade the money rooms stay
  concrete), hangs `security_camera` in the lobby and every vault, and stands the lobby's plants and clock.

The same level on both (`workspaces/bank-look-0282-ws`, `_scratch/bank_0282_after.sh`; `frames/07_*`, `frames/08_*`):
the lobby and the offices read as painted plaster where every earlier frame showed raw concrete, and cameras hang on
the lobby's and the vault's walls. The level frames' mean luminance barely moved: lobby_entry 101.8 -> 101.9,
vault_west 51.9 -> 51.9; manager_office reads 82.5 and vault 72.5.

**The plants and the clock are in the level and in no frame.** The package's merged `assets/lot.glb` carries
`potted_plant_rcce455f7_3`, `_5` and `wall_clock_rcce455f7_14`, and the job built
`prop_planter_..._w50_d50_h120_n2_mwood`, `prop_planter_..._w70_d70_h180_mwood` and `prop_wall_clock_..._w36_d6_h36`.
They stand at the lobby's east and west ends (plan x 14.5 and -14.6) and the clock on its east wall, and no station
looks there. The next shoot adds one that does.

**Priced** against the 0.281.0 package (`price_0282.py`, `compare.py perf_0282_`, `compare_0282.out.txt`), 53 headings:

- **Draws:** median +0, from +0 to +30; 26 headings gained some (cameras, plants, the clock).
- **p95:** median +0.055 ms. Three headings are past the controls' own floor of 0.258, by at most 0.08 ms:
  extraction_11 yaw 270 +0.342 (+9 draws), extraction_12 yaw 90 +0.311 (+30), objective_5 yaw 270 +0.266 (+6).
- 0.280.0's `attacker_spawn_2` yaw 270 reads 6.88 against the controls' 6.75 and 6.84.

**A first reader of these reports found 0 headings**: it guessed the schema (`stations` / `results`) where the file
writes `rows`. `compare.py`'s own loader asserts the shape and was the one used.

## Step 5 shipped: Zoo 1.137.0 (48e8da9) and Deli Counter 0.283.0 (f1d1bfa9), the offers and the name over the line

The walker's list: the rate board and posters, then the bank's name over the line and a number on every window.

- **Zoo 1.137.0** paints `poster_wall` form `bank` and `teller_line` form `bank`.
  - The posters are twelve offers and the rate board; the bank family is a fifth family on the club's poster system
    (its run, layout, stocks and readability tests).
  - The teller line carries a nameboard, its sixteen variants the door sign's name and colours.
- **Deli Counter 0.283.0** hangs `poster_wall_bank` in every bank lobby (two or three runs, 5 cm height steps) and
  dresses every library teller line form `bank` in `bank_teller_variant`: bank_branch_a02 11, a03 5, a04 2, bank_job
  14, credit_union_a01 8, bank 2.

The same level on both (`workspaces/bank-look-0283-ws`, `_scratch/bank_0283_after.sh`; `frames/09_*`, `frames/10_*`).
Two stations were added because frames 07 and 08 showed none of the lobby's side walls: `lobby_east` and `lobby_west`.
- The teller line reads YOUSE CREDIT CO-OP across its nameboard from the door (lobby_entry); at that distance the
  window numbers are small.
- lobby_east shows two offer runs on the east wall, the plant and the clock beside them; lobby_west shows a run by the
  ATM and the other plant. The sheets are 0.46 x 0.62 m in a 30 m lobby and read small from mid-floor.

**Priced** against the 0.282.0 package (`price_0283.py`, `compare.py perf_0283_`, `compare_0283.out.txt`), 53 headings:

- **Draws:** median +0, largest +3.
- **p95:** median +0.001 ms, largest +0.388, the controls' own floor 0.386.

**Two first builds stopped in their gates**, both before any commit:
- Zoo's poster family failed its own tests four ways: a copy line on the denylist, a figure panel too pale to step
  off its paper, a rate board whose ground ignored the stock, and an unknown stock not refused. Fixing them found the
  board losing every rate at the shipped 118 px while those tests passed; a test now holds every line.
- Deli Counter's first build hung every bank run at one height, and `test_poster_walls` refused it on the clone's
  full suite (the placement guide's tell).

## Step 6 shipped: the outside -- Zoo 1.138.0 (bbc02c7), Lot 0.132.0-0.134.0, Level Factory 0.262.0 (fbec345)

The walker's list ended outside: the drive-up, the night drop, the time-and-temperature sign; then "do the drive-up lane
next".

- **Zoo 1.138.0** draws all four pieces, each with one name and one colour a bank:
  - `price_pylon` form `bank`: the gas pylon's frame, the bank's name, the time over the temperature in amber lamps,
    MEMBER FDIC;
  - `night_drop`;
  - `drive_up_tube`;
  - `drive_up_canopy`, its fascia the bank's colour.
- **Lot** places them:
  - 0.132.0 (b71d895): the sign at the bank's frontage by the gas pylon's planner, its stations reaching past the
    building's ends; `site_driveup`, the served lane, island and passing lane against a side wall, the island on the
    driver's left, the lane stopping short of the wall's first door;
  - 0.133.0 (430c074): `site_night_drop`, hung beside the storefront door;
  - 0.134.0 (141656f): the pieces' material rows.
- **Level Factory 0.262.0** deals a bank's band the name Zoo's other faces give it.

**The first build** (`workspaces/bank-look-out-ws`, `_scratch/bank_out_after.sh`; `frames/11_*`, `frames/12_*`) found
two defects by looking:

- The drive-up stood as two green greybox boxes. Zoo built both modules and they passed, but Lot asked for
  `metal_painted` where neither species has it, so Zoo built `_mmetal_painted` stems and Lot's resolver, asking the
  untagged names, said `LOT_COVER_MODULE_MISSING ... the box stays`. Fixed by Lot 0.134.0.
- The band said MATTRESS MONEY TRUST over a sign and a line saying YOUSE CREDIT CO-OP. Level Factory's deal keyed its
  own hash; Deli Counter, Lot and Zoo key `storefront_names`' crc32. Fixed by Level Factory 0.262.0.

**The second build** (`workspaces/bank-look-out2-ws`, `_scratch/bank_out2_after.sh`; `frames/13_*`, `frames/14_*`):
- The canopy and the station are their modules, the band, the sign and the line one bank. The night drop hung
  (`LOT_NIGHT_DROP: b0 on its S facade at +1.60 m from its door`), too small to read in `bank_front`.
- **Reads wrong, not yet fixed:**
  - the canopy's fascia reads near black rather than the variant's navy;
  - the station's cabinet reads brown, the theme's `metal` skin (the cash cart's complaint);
  - the lanes are the lot's own asphalt with no marking, so the drive-up reads as a canopy in a parking lot rather
    than a lane.

**Priced:**
- The first build against 0.283.0's package (`price_out.py`, `compare_out.out.txt`): draws median +0, largest +3;
  p95 median -0.012 ms against the controls' 0.758.
- The second against the first (`price_out2.py`, `compare_out2.out.txt`): draws median +0, largest +2; p95 median
  +0.002 ms against the controls' 0.342.

**Gates that stopped a first build, before any commit:**
- Zoo 1.138.0's census count read 441 where 148 species make 444: the canopy came after the count.
- Lot's `site_driveup` first refused both ends of the bank, each crossing its side door's landing. The finding now
  names the refusing test for each end, and a lane stops short of the landing instead.
- The bank's sign found no station: all thirteen of the gas pylon's +/-12 m stations met the bank's footprint, grown
  0.5 m.

## Step 7 shipped: the three fixed -- Zoo 1.139.0 (d2c9112), Lot 0.135.0 (4a39612), Deli Counter 0.284.0 (925054d8)

The walker: "fix those three, then cut the release", then "do some more research, make it look better". The
canopy, station and clearance bar on painted steel, the night drop and cash cart on bare (Zoo 1.139.0); the lane's
clearance bar, bollards, yellow island and arrows (Lot 0.135.0); every placed piece asking Zoo for a kind its species
is made of, about 2,800 library slots that asked for rust or wood (Deli Counter 0.284.0).

**The build** (`workspaces/bank-look-final-ws`, `_scratch/bank_final_after.sh`; `frames/15_*`, `frames/16_*`):
- The drive-up reads as a lane: the clearance bar and its CLEARANCE 9 FT plate across the entry, the island yellow,
  an arrow each lane, DRIVE-UP on the canopy's board. The band, the sign and the line one bank.
- The lobby is 0.283.0's: plaster floor to ceiling, the glass front a wall of dark bars, the deposit wall a grid. The
  walker then asked "do the interiors look really good?" -- no -- and "hold the release, do the interior pass first";
  that pass is Zoo 1.140.0 and Deli Counter 0.285.0, below.

**The first walk failed, and the cause is not proven.** Level Factory's buildings' merge timed out at its 1,800 s
limit (`_scratch/bank_final_walk.log`) while clone builds, Blender and a 10-minute Zoo suite ran on the same machine.
Re-run with the machine to itself the whole walk, the merge included, took 4 min 21 s (`bank_final_walk2.log`).
Contention fits; a 7x slowdown is more than contention has shown here before, and nothing else was measured. The rule
it breaks is the price's: nothing heavy runs beside a level build either.

**Priced** (`price_final.py`, `compare_final.out.txt`), against 0.283.0's second outside build: draws median +1,
largest +16; p95 median +0.009 ms, largest +0.265, against the controls' own 0.609.

## Step 8 shipped: the interior pass -- Deli Counter 0.285.0 (93f0d394), Zoo 1.140.0 (cf9797b), Zoo 1.141.0 (5134b5c)

The walker: "do the interiors look really good?" (no: plaster floor to ceiling, the front a wall of dark bars, the
deposit wall a bare grid), "hold the release, do the interior pass first", and, mid-pass, "they had these pens attached
with a little chain at banks" and "also longer chain".
- Deli Counter 0.285.0: a bank's public room panelled below a chair rail (`_dados`; wood_panel sheet 6 mm proud, a
  rail 9 mm proud, its top 0.9 m); a bank's `glass` front before its public room a storefront (`bank_front`); a vault
  door's and a deposit wall's slot on its own steel where it took its wall's concrete (`FIXTURE_OPENINGS`).
- Zoo 1.140.0: the deposit wall as comp 12 -- numbered steel doors with brass locks, large boxes low, a few drawn, the
  doors nearly flush, bare steel, and its 884 coincident pairs gone.
- Zoo 1.141.0: a pen on a slack ball chain each side of the check desk.

**What the frames found while it was built** (Zoo previews in the clones, not filed): the first lock layout put the
locks on the doors' left as a person faces them (+x is the viewer's left from +y); the first frame stood 9 cm proud and
read as pigeonholes; crossing bars' chamfers drew a dark dot at each crossing; a 1 mm rail setback left 7 coincident
pairs inside the census's 2 mm. All fixed before shipping.

**The build** (`workspaces/bank-interior-ws`, `_scratch/bank_interior_chain.sh`; `frames/17_*`, `frames/18_*`):
- The lobby's wood band runs round its west, east and north walls; the front is glass onto the street, mullions and
  all, and from outside the lobby glows through it at night.
- The deposit wall reads as boxes with its drawn cells; under the level's light its steel reads darker than comp 12's.
- The pens are too small to read at these stations.

**Priced** (`price_interior.py`, `compare_interior.out.txt`), against step 7's build: draws median +0, largest +13;
p95 median -0.004 ms, largest +0.432, against the controls' own 0.491.

**Reads wrong, not yet fixed:** the lobby is still sparse for its 390 m2 (officers' desks on the floor are the next
Deli Counter step); the deposit wall's steel is dark; the storefront's mullions read as dark stripes from inside.

## The plan, each step priced and shown

1. **Light and floor** (Deli Counter): a bank's public rooms take a selling room's lamp density and the bake-only
   reach (roadmap 319's `room_caps` and `bake_reach`), and a hard floor. The money rooms take fluorescent rows, not
   pendants.
2. **The lobby's furniture** (Deli Counter recipe, Zoo species): a check desk island, planters, poster stands, a date
   clock; no vending or cigarettes in a bank.
3. **The money rooms** (Zoo species): a bank of safe-deposit boxes, some drawn open; cash carts and canvas hampers.
4. **Surfaces** (Pixelcoat and the theme): terrazzo underfoot in public (`profiles/materials/terrazzo.json` exists,
   used by the rockay and casino themes), painted walls and wood panelling for the concrete.
