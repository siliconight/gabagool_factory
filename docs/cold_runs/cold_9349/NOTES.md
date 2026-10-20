# Cold run 9349 -- 0 interventions; restaurant_row_001, seed 9003: the first package with its buildings merged

**What it was for.** Level Factory 0.223.0 (the factory's roadmap 266, `docs/findings/interior_merge_266/`) merges each
enterable building's static modules per room cell and material in the export, after the Empties' merge and before the
light bake. It was priced on copies of cold run 9347's package; this run is the same level made cold through the new
export, and the price of what it shipped against the same workspace exported again with `--no-merge-buildings`.

**Tools:** Level Factory 0.223.0 (4174d64), Deli Counter 0.238.0, Zoo 1.114.1, Lot 0.125.0, Lux 0.78.0. Staged from
9347; seed 9003 named.

**Every leg ran, `INTERVENTIONS: 0`** (journal 0, unattributed files 0), read after `cold_run.py --end`; 8 min.
- **Shell:** 0 blockers of 79 findings; seed_9003 placed deli_a03, office and pharmacy_a01 with the terrace's twelve
  Empties, as 9347.
- **Art:** 0 blockers of 108 findings. **Findings 108 -> 108** against 9347.
- **Export:** the Empties merged as before (12 scenes, 1,744 surfaces -> 172 meshes); **the buildings merged: 3 scenes,
  880 slots, 1,643 surfaces -> 789 meshes, 830 colliders kept**; 197 module GLBs no file named any longer removed, 9.0
  MB. The light bake 2,880 users. The drop-edge gate reached 55,638 of 69,746 standable cells -- 9347's very count:
  the merge copies every collider whole, and the gate measures colliders.

## The price (`_runs/perf_inner/run.py`, 53 station-headings; `price_a.out.txt`, `price_b.out.txt`)

The shipped package against the same workspace exported again with `--no-merge-buildings` (the bake 3,524 users),
each priced twice; the shipped package restored byte for byte after the control's export.

| | control A | control B | merged A | merged B |
|---|---|---|---|---|
| draws, all headings | 38,938 | 38,938 | 34,531 | 34,439 |
| p95, mean a heading | 3.962 ms | 4.064 ms | 3.832 ms | 4.169 ms |
| the worst heading | 9.95 ms, attacker_spawn_5 yaw 90, 2,115 draws | 10.33 ms, the same | 9.13 ms, the same, 1,799 draws | 9.96 ms, longest_sightline yaw 270, 1,650 draws |
| mesh instances | 3,597 | 3,597 | 2,953 | 2,953 |
| video memory | 130.5 MiB | 130.5 MiB | 134.7 MiB | 134.7 MiB |
| meshes over the 8-light cap, paired | 9 | 9 | 9 | 9 |

- **The draws fell by 83 to 85 a heading (11 %), 418 at the most**, the same both times.
- **The frame time did not move outside this machine's noise:** merged minus the controls' mean is -0.181 ms a
  heading in one run and +0.156 in the other, against 0.131 between the two controls. At the seven headings drawing
  over 1,500, the merged runs' mean is 0.233 ms under the controls' (median 0.442), and the two merged runs differ by
  0.712 there. At 4 ms a frame on this desktop GPU, submissions are not what the frame waits on; the merge buys its
  time where they are -- the low-end target this repo ships for -- and that is not measured here.
- **The cost:** a 2048 x 1024 lightmap where the control's is 1024 x 1024, and 4.2 MiB of video memory.

## Level Factory 0.224.0 on a copy of this package (`docs/findings/interior_merge_266/`)

The same workspace's control against copies of this package re-merged by 0.224.0 and re-baked by Level Factory's own
bake. 0.224.0's first cut, the fixtures' housings merged too, drew 94 to 97 fewer a heading and was refused by the
light cap, two room cells pairing 10 lights and the meshes over it 9 -> 11. As shipped, the fixtures whole and a
`_Face` lit face a mesh of its own per instance: 6 lit faces split (deli_a03 4, office 2), 2,953 mesh instances as
0.223.0's, draws -84.9 and -81.4 a heading, p95 -0.242 and -0.183 ms against the controls' 0.131 floor, the meshes
over the cap the control's 9.
