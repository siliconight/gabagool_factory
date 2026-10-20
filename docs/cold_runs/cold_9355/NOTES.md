# Cold run 9355 -- 0 interventions; restaurant_row_001, seed 9003: the booth's marks are small, and mostly weather

**What it was for.** The walker's look review, 2026-10-20 (the factory's roadmap 210), on cold run 9351's booths:
"more subtle graffiti/weathering....a large shapie squigle doesn't look like anything". Zoo 1.117.0 marks every
booth -- the plain look too -- with what hands and weather leave inside one: small tags in words, keyed initials, rain
run down from the roof's seam, scuffs, scratches, the paper of a torn-off sticker, and a tag the phone company painted
over. This is cold run 9351's level made cold through it.

**Tools:** Zoo 1.117.0 (48fdc71), Lot 0.126.0 (49dcf8d), Level Factory 0.226.0 (7a83a9a), Deli Counter 0.240.0
(557717da), Lux 0.79.0 (9132d32). Staged from 9351; seed 9003 named; the brief's evening kept.

**Every leg ran, `INTERVENTIONS: 0`** (journal 0, unattributed files 0), read after `cold_run.py --end`; 8.6 min.
Shell 0 blockers of 79 findings; art 0 of 108; **findings 108 -> 108** against 9351.

## What else moved between 9351 and 9355 (`module_diff.py`, `scene_diff.py`)

Five tool versions moved between the two runs, so before reading anything off this one, every file that differs
between the two packages (their walk copies, `_scratch/review/walk_9351` and `walk_9355`) was attributed
(`module_diff.out.txt`, `scene_diff.out.txt`). Of 1,790 files:

- **The booths, as Zoo 1.117.0 says:** the two street looks' paint atlases (`cover/_tex/Payphone_256x1182_*` ->
  `Payphone_256x1360_*`) and their GLBs, which name them; the office's indoor wall unit's atlas (256 x 1326 -> 256 x
  1504); and the office room mesh the unit's paint merges into (`lot/office/merged/r210.res`, Level Factory 0.223.0's
  merge, its lit face kept apart by 0.224.0).
- **The bake's pixels** (`bake.exr`, `bake.lmbake`): the booths' albedo is in it. `bake.tscn` is otherwise the same
  scene, so the lightmap's users did not change.
- **Lux 0.79.0's two day presets** (`runtime/lux/presets/delco_morning.tres`, `delco_high_noon.tres`), shipped with
  every package and unused at evening.
- **Nothing, once Godot's own save ids are set aside:** 15 buildings' `site.tscn` (deli_a03, the office,
  pharmacy_a01 and twelve Empties) and `presentation/lux.applied.tscn` differ only in each node's `unique_id` and the
  random resource ids a save draws.

No building's modules or scenes differ, so Deli Counter 0.239.0's roof hatches and 0.240.0's two mappings changed
nothing in this level, and only the booths could move its price.

## The phones (`phones_9351_vs_9355.jpg`, `phones_close_crop.jpg`; `phone_frames.sh`)

Each phone shot from 9351's own stations (`docs/cold_runs/cold_9351/stop_stations.py`, derived again off 9355's drawn
site and checked equal to 9351's: every phone where it stood, facing as it faced, in the same look), from 4 m toward
its road and from 1.5 m, into the booth's mouth, in the level's evening light; 9351 shot again beside 9355 from its
walk copy.

- **From 4 m**, 9351's booths carry their marker waves readable from the street: black on the back panel's top, purple
  and black down the sides. 9355's read clean at that distance; the marks are for somebody who walks up.
- **From 1.5 m** (`phones_close_crop.jpg`, payphone_1L3 in the plain look and payphone_2R3 in look 1, 9351 left,
  9355 right): where 9351 drew the waves, 9355 shows writing -- ARDY in a faded red over JABRONI, keyed initials under
  them, WOODER and JEET on the right side panel; on look 1, YOUSE beside the instrument and the same panel's words in
  another hand. Both match their looks' contact sheet (`patches/zoo_booth_marks/marks_1160_vs_1170.jpg`).
- **Seen, not changed:** the hood lamp washes the booth's inside nearly white at 1.5 m in the evening, so the faint
  marks read fainter there than on the contact sheet, and the weather -- the runs, the scuffs -- barely at all. That is
  the lamp's look (Zoo 1.89.0 hung it behind the header to halve its hot spot), and the walker's eye on it.

## The price

`_runs/perf_inner/run.py`, 53 station-headings; every table beside this file.

**The first read was wrong three ways, and none of them was the booths.** Against 9351's two runs of 12:37 and 12:42
(`price_a.out.txt`, `price_b.out.txt`, `price_c.out.txt`), 9355 read 184 fewer draws in all, +0.67 to +0.99 ms a
heading at p95, and 14 MiB less video memory -- where bigger atlases could only add. Two instruments disagreeing, one
of them is wrong; so the session was priced against itself, each arm in turn and alone:

| arm | report written | draws, all | extraction_16 / player_start_19, yaw 90 | texture memory | buffer memory |
|---|---|---:|---:|---:|---:|
| 9351, its own two runs | 12:37, 12:42 | 34,731 | 1,316 / 1,331 | 79,959,321 | 61,614,416 |
| 9351's bytes, rebuilt (`make_hybrid.py`) | 16:15 | 34,547 | 1,224 / 1,239 | 79,959,321 | 46,703,072 |
| the control: 9355 with 1.116.0's booths put back | 16:09 | 34,547 | 1,224 / 1,239 | 79,959,321 | 46,703,072 |
| 9355, four runs | 15:55-16:12 | 34,547 / 34,547 / 34,489 / 34,547 | 1,224 / 1,239 | 80,049,489 | 44.6-48.8 M |
| 9353's morning package, unchanged since its 14:08 and 14:12 runs | 16:01 | 23,609, as at 14:08 | -- | 79,959,321 | 61.6 M then, 48.8 M now |

"9351's bytes, rebuilt" is 9355's package with 9351's booths, office room mesh and bake put back and Lux 0.79.0's two
unused presets taken out: against 9351's walk copy it differs only in records, import uids and the scenes' save ids
(`make_hybrid.out.txt`).

- **What the booths cost: 90,168 bytes of texture memory**, the three paint atlases 178 px taller after the import's
  S3TC compression, and nothing else this machine can see. Against the control, priced in the same session, the draws
  are equal at all 53 headings and p95 is +0.030 ms a heading (median -0.050) against the controls' 0.151 ms floor
  (`price_vs_control.out.txt`, `draw_flicker_control.out.txt`).
- **The draws: the session's.** 9351's own bytes, priced now, read 9355's draws at every heading -- 92 fewer at the
  two headings looking west from the van than they read at 12:37 (`draw_flicker_bytes.out.txt`, `drift_9351_bytes.out.txt`).
  Between 9355's own runs one heading flickers (objective_2 / 180, 547 or 489); 9350's two runs of one package flickered
  at attacker_spawn_4 the same way (`draw_flicker.out.txt`).
- **The frame time: the session's.** The morning package, byte for byte what was priced at 14:08, now reads +0.612 ms
  a heading at p95 against its own 0.099 ms floor (`drift_9353.out.txt`) -- most of the +0.67 and +0.72 that 9355's
  runs B and C read against 9351's runs of 12:37 and 12:42.
- **The video memory: the buffers, which move on their own.** Texture memory is the same on the same bytes in
  every run today. Buffer memory is not: 9351's and the morning package's runs before 14:15 read 61,614,416 each, the
  noon package's two runs at 14:10 and 14:14 read 57.4 and 59.5 MB, and every run since 15:55 44.6 to 48.8 MB, moving
  between runs of one package. The harness's "video memory" is the two summed, so read texture memory to price a
  package's memory.
- **And one run spoiled by this session's own work:** run A was measuring while `module_diff.py` hashed the two walk
  copies, and read the worst of the four (+0.99 ms). A price runs alone; kept as the record that it did not.

Not attributed, and not guessed at: what changed between 12:42 and 15:55 that moves an evening heading's draws, the
frame time and the buffers on identical bytes -- the window, the display, a lamp's shadow allocation and the machine's
other use since the walker came back at 14:56 are all candidates, and none was measured. The copies were deleted once
their JSON existed (`_runs/perf_inner/c9355_*.json`, `c9353_now.json`, `c9355_hyb1116.json`, `c9351_bytes_now.json`).
