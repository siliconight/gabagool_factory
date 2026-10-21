# Cold run 9365 -- 0 interventions; bank_block_001, seed 9082: Zoo 1.120.0's parked-car histories, on most cars

**What it was for.** Roadmap 44, the walker's look review of 2026-10-19 on the parked cars: "some of the cars need some
patina and wear...rusting....ect....bumper stickers....". Zoo 1.120.0 (0c51827) draws each car a history -- kept,
driven or beater -- and paints and lays it: sun and road in the body's `Wear`, rust, primer and peeled clear coat as
pieces of the painted material, bumper stickers from one sheet. Cold run 9364's level again -- same brief, same seed,
staged from it -- so Zoo is the only tool that moved and the 35 parked cars are the same eight modules in the same
bays.

**Tools** (`before.json`, every repo clean at `--begin`): Zoo 1.120.0 (0c51827); the rest as 9364 -- Deli Counter
0.245.0, Level Factory 0.228.0, Lot 0.126.0, Lux 0.79.0, Dispatch 0.5.3, Patina 0.32.0, Laser Tag 0.32.0, Pipeline
0.6.0, Pixelcoat 0.62.0.

**Every leg ran, `INTERVENTIONS: 0`** (journal 0, unattributed files 0, retries 0); 7.3 min (03:58:52 to 04:06:11).
Shell 0 blockers of 79 findings; art 0 of 110; **findings 110 -> 110 against 9364**, the same level, no code moving.
The export: its bake 2,240 users against 9364's 2,213.

**The cars, read from the package** (`docs/findings/car_wear_44/car_surfaces.py`, `car_surfaces_9364_9365_9366.out.txt`):
the eight car modules' visual surfaces times the instances the site places -- 140 at 9364, 167 here. Every one of the
27 more is the sticker material: seven of the eight modules drew a sticker, 27 of the 35 cars; the rust, primer and
peel pieces packed into each car's painted mesh and added none. The bake's 27 more users are the same 27 stickers.
The walker asked for "some of the cars"; 27 of 35 is most of them, and the stickers are the whole cost, so Zoo 1.120.1
makes a sticker a chance per history -- cold run 9366.
