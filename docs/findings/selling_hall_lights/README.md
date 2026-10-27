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

## The price (`price.py`, `price.out.txt`, `compare.out.txt`, `perf_*.json`)

**The arms.**
- Subject: a copy of the walker's workspace (`levels/restaurant_row`, seed 9205) rebuilt against a Deli Counter
  clone that carries both 0.274.0 (the lamps) and 0.275.0 (the supermarket's dressing), so it prices the two
  together.
- Control: the walker's own package (Deli Counter 0.272.0, Level Factory 0.257.0), measured twice in the same
  session, the subject between the two passes.
- The harness: Level Factory's fixed-station harness, 14 stations from the package's anchors, 53 headings.

**Refuted on the way, and kept here.** The first subject rebuild repointed only `tools.local.json`. Lot draws its
buildings from the brief's `lot_library`, which still named the live `deli_counter/build`:
- the supermarket's art came back `cache`;
- the garage took an in-flight 0.273.0 build.

That arm measured nothing and was discarded. The second arm repointed both; its export was then refused by its own
guard ("collision_fingerprint changed after art pass", correctly: the aisles and the cooler wall change the
supermarket's collision), and it was built after re-locking the shell, as the panel's walk does.

| | draws, subject - controls' mean | p95 ms, subject - controls' mean |
|---|---|---|
| median over 53 headings | +0.0 | +0.041 |
| mean | +12.6 | +0.095 |
| largest | +87 (`player_start_18` facing the supermarket, 1,577 -> 1,664) | +0.416 |
| the controls' own a - b | median 0, largest 102 | median -0.003, largest 0.779 |

- Worst heading, `camera_socket_1` at yaw 90: 2,150 draws in both controls -> 2,209 in the subject; p95 10.75 /
  11.53 -> 11.19 ms.
- Every heading where draws rose looks at the supermarket or through it: `objective_4` +76, `extraction_13`
  +69, `longest_sightline` +62.
- Frame time moved within the controls' own spread everywhere.

So the lamps and the dressing cost up to about 90 draws in a view of the store, about 5 %, and no frame time the
instrument can tell from its floor.

## What it looks like (`frames/`, `frames_arms*.out.json`)

Walk copies shot with `look_shots` at three stations:

| station | control mean / p50 | subject mean / p50 |
|---|---|---|
| the walker's view down the sales floor (24.4, 1.6, -6.8) | 44.4 / 42 | 77.4 / 74 |
| from the checkout toward the cooler wall | 28.2 / 35 | 37.8 / 42 |
| `room_stations`' `sales_floor`, which faces a gondola at arm's length | 31.4 / 30 | 26.5 / 17 |

- The third is darker: the gondola faces beside that eye stand between the new rows. That is one close view, and
  the claim is not that every view gains.
- The cooler wall reads as lit glass at the far end (`02_toward_cooler_before_after.png`).
- The views from the store's centre (`frames_arms.out.json`'s `c_*`) were shot from among the gondola ends and
  frame nothing; they are kept for the numbers only.
