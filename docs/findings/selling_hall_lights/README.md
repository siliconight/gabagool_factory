# A selling room's lamps, and what they cost

The walker, 2026-10-26, walking seed 9205's supermarket ("far too dark in teh super market"), and the comps that
followed, filed in [`docs/reference/GROCERY_STORE_COMPS.md`](../../reference/GROCERY_STORE_COMPS.md): "shiny floor,
bright lights, isles, glowing freezer section, stacked high".

## The census (`census.py`)

`census.py`, run from a Deli Counter checkout, reads each shell's `build/<shell>.lights.json` against its spec. It
lists every room whose id sells (`floors.floor_by_use` == "tile") with:
- its floor area;
- its fluorescent lamp count;
- the area per lamp.

- `census_0272.out.txt`: the live library on 2026-10-26, with Deli Counter 0.273.0's `build.py --all` output in
  its working tree. Lamp counts are unchanged by 0.273.0, which touches ramps.
  - 41 selling rooms of 150 m2 or more.
  - 20 of them at the 12-lamp room cap (`lights._MAX_LAMPS_ROOM`).
  - Their density falls with size:
    - shops under 340 m2: 13.5 to 34 m2 a lamp;
    - the three supermarkets: 73 to 92;
    - the three market halls: 89 to 104.
- The first run, on a 0.272.0 clone whose `build/` was the committed one, listed 30 rooms, 11 at the cap: the
  committed `build/` carried fewer shells' manifests than a full rebuild writes. Quote the live file.

The density Deli Counter 0.274.0 keeps, 25 m2 a lamp (`lights._SELLING_M2_PER_LAMP`), is what the capped selling
rooms of 250 to 300 m2 already had:
- the delis' `market_aisles`: 25.0;
- gas_station_a02: 23.0;
- convenience_store_a01: 21.1;
- pharmacy_a01: 26.4.

## The price

Pending. The subject arm is a copy of the walker's workspace (`levels/restaurant_row`, seed 9205) whose
`tools.local.json` points `deli_counter` at a 0.272.0 clone carrying both 0.274.0 (the lamps) and 0.275.0 (the
supermarket's dressing). The control is the walker's own package, built on 0.272.0.
