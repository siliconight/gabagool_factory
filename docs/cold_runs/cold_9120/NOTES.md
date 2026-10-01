# Cold run 9120 -- an ATM in every store, half the poles papered, and the FLAPPHAS walk

Zoo 1.35.0 (the ATM redrawn: a 1990s surcharge unit, lit topper and CRT, two
draws), Deli Counter 0.164.0 (one ATM in every building that sells) and Lot
0.86.1 (a third of the poles papered; the walker's "tune it down 50%"). Same
brief, same seed, same lot. Zero interventions, one observation (the walk).

The art leg before export: 0 blockers, 63 findings -- 9119's 64 less one
`ZOO_PARTIAL_BUILD` (2 -> 1). The one that went is the airport's lobby ATM
(`prop_atm_delco_1997_05_w60_d55_h145_mmetal`), which failed exact fit in
every recent run on the old recipe (its sign 1.57 m over a 1.45 slot, its
keypad 0.58 past 0.55) and now passes; the one left is the flat-top grill.
gas_station_a02's own ATM built and passed. Export closure clean.

Pole posters: 11 poles papered (8 pair, 3 stack) against 9119's 22.

## The ATM (`atm_gas_station.png`)

On the sales floor against the storefront glass, 1.3 m from a door, facing
the room: CASH JAWN on its lit topper, the green CRT, the yellow sticker.

## The FLAPPHAS walk (`walk_a.png`, `walk_b.png`)

The walker asked for "a proper walk of the gas station/convenient store combo"
after ATMs. Seventeen stations from the street to the office, at night.
What reads: the storefront through its glass (the WOODER ICE window neon,
aisles, the cooler wall's lit section signs); the aisles with shelf tags; the
cooler wall; the FROZEN JAWN slush machine and the roller grill; the coffee
station under its FLAPPHAS COFFEE sign; the ATM.

What does not, each named to the job that makes it:

1. THE PUMPS ARE BOXES. `pump_1`-`pump_6` route to Zoo's `pump`, whose recipe
   is the placeholder `tools/new_species.py` minted on 2026-09-12 -- "NOT yet
   a pump: this file is where the drawing goes". A gas station's most
   recognisable object is the one still greybox.
2. THE LIT BOX OVER THE DOOR IS BLANK. Deli Counter's light manifest derives
   a "sign" anchor over the entrance (`lights.py`, the sign derivation), and
   Lux draws it as a lit panel with no art on it: a white rectangle where
   the store's name would go.
3. STONE INSIDE. The interior faces of the exterior walls wear the exterior
   material (`stone_ext`) -- behind the register, in the stockroom and the
   office -- where a store's inside is painted block or drywall.
4. THE FORECOURT IS DARK. From the street the canopy is a row of lights and
   the pumps and columns are lost (frame mean 9.9 of 255); under the canopy,
   the pump stands in shadow beside a lit patch (11.5).

Not a finding: `03_canopy_to_store` is black because the station put the
camera inside canopy column 2 -- the station was wrong, not the level.
