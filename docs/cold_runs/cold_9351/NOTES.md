# Cold run 9351 -- 0 interventions; restaurant_row_001, seed 9003: the street phones face the sidewalk

**What it was for.** The walker's look review, 2026-10-19 (the factory's roadmap 210): a street phone should "Always
face the sidewalk" -- this level's faced the storefront behind it -- and the booths' graffiti was "too
similar/uniform". Lot 0.126.0 turns every piece at a bus stop toward the road from either kerb and gives each payphone
the look its place picks; Zoo 1.116.0 draws the payphone in four looks. This is cold run 9350's level made cold
through both.

**Tools:** Lot 0.126.0 (49dcf8d), Zoo 1.116.0 (3e811ec), Level Factory 0.224.0, Deli Counter 0.238.0, Lux 0.78.0.
Staged from 9350; seed 9003 named.

**Every leg ran, `INTERVENTIONS: 0`** (journal 0, unattributed files 0), read after `cold_run.py --end`; 8.5 min.
Shell 0 blockers of 79 findings; art 0 of 108; **findings 108 -> 108** against 9350.

## The stop corners (`site.site.drawn.json`, 9350 against 9351)

| piece | kerb | 9350 yaw | 9351 yaw | 9351 look |
|---|---|---|---|---|
| payphone_0L3 | L of road 0 | 180, its face to the storefront | **0** | 1 |
| mailbox_0L0, newspaper_box_0L1, _0L2 | L of road 0 | 0 | 0 | -- |
| payphone_1L3 | L of road 1 | 270, its face to the wall | **90** | 0, the plain booth |
| mailbox_1L0, newspaper_box_1L1, _1L2 | L of road 1 | 90 | 90 | -- |
| payphone_2R3 | R of road 2 | 270 | 270 | 1 |
| mailbox_2R0, newspaper_box_2R1, _2R2 | R of road 2 | 90, their faces to the wall | **270** | -- |

Each change is the kerb that was wrong for that piece, and nothing else on the site moved. Two of the three phones
drew look 1 (`cover_variant` is a hash of where a phone stands; four looks over three phones can repeat). The export
ships the plain module and `_n1`.

## The phones (`phones_9350_vs_9351.jpg`; `stop_stations.py`)

Each phone from 4 m toward its road, at 1.7 m, the level's evening light; 9350 left, 9351 right. On roads 0 and 1,
9350 shows the booth's dark back and 9351 the lit booth facing the street -- its header, the instrument, the tags --
with the hood lamp's pool on the sidewalk in front of it rather than against the wall. On road 2, which faced the
street already, the booth wears look 1's marks where 9350's wore the plain booth's.

## The price (`_runs/perf_inner/run.py`, 53 station-headings; `price_a.out.txt`, `price_b.out.txt`)

9350's package and this one priced in turn, twice each.

| | 9350 A | 9350 B | 9351 A | 9351 B |
|---|---|---|---|---|
| draws, all headings | 34,733 | 34,547 | 34,731 | 34,731 |
| p95, mean a heading | 3.772 ms | 3.988 ms | 3.949 ms | 3.777 ms |
| mesh instances | 2,971 | 2,971 | 2,971 | 2,971 |
| video memory | 134.7 MiB | 134.7 MiB | 135.0 MiB | 135.0 MiB |
| meshes over the 8-light cap, paired | 9 | 9 | 9 | 9 |

- **Nothing moved that this machine can see:** the draws inside the two 9350 runs' own spread (186 between them),
  the frame time +0.069 and -0.103 ms a heading against their 0.297 ms floor, the same mesh instances and lightmap
  users (2,898).
- **The cost is the second booth's atlas:** 0.3 MiB of video memory. Zoo 1.116.0 priced a look at about 1.2 MB as
  an uncompressed texture; the package's import measured less.
