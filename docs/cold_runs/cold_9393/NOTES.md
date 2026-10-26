# Cold run 9393 -- 0 interventions; restaurant_row_001, seed 9003: the door hardware merges with the railing

**What it was for.** Level Factory 0.242.0 (3561b73): a door's hardware keeps its own UVs on a kit module. Cold run
9392 had shown the knob's iron colour in the package but no merge, because the knob was world-projected in its
`doorway_` module and the stoop railing, a `prop_`, was not (`docs/cold_runs/cold_9392/NOTES.md`).

**Every leg ran, `INTERVENTIONS: 0`.** The light check: FAIL 3, PASS 33, REPORT 1, as 9391 and 9392. The walk copy
`_runs/walk_9393_restaurant_row_001`; the workspace `workspaces/cold-9393-ws`.

## The merge -- PROVEN

- **`blocker_0`** (`meshes_blocker0_9393.out.txt`, from `docs/cold_runs/cold_9392/meshes_under.gd`): one iron mesh
  on the street side where 9392 had two, keyed `uv1_scale (0.833, 0.833, 1.0) triplanar false`, the railing's key.
  The back door's knob keeps its own mesh, which is now on the same key. 26 -> 25 meshes.
- **Every Empty** (`count_by_site_child_diff.out.txt`): 26 children -1 each, nothing else moved; the site 3,038 ->
  3,012 meshes.

## The price (`price.py`, `price_compare.out.txt`; 9392's walk copy twice as the control, one session)

| arm - ctrl | draws | median ms, mean of headings | median of the differences | worst heading |
|---|---|---|---|---|
| ctrl2 (9392 again) | +0 | -0.032 | +0.031 | +0.170 |
| lf0242 (9393) | **-449** (-28 to 0 a heading) | +0.046 | +0.040 | +1.327 |

- **Draws: -449.** The brass knob's cost in 9391 was +582 against 9389; the street side's half of it is paid back.
  The back doors keep one mesh each, as Zoo 1.127.0 said they would.
- **Frame time: inside the instrument's spread.** The worst heading's +1.327 ms is a single p95-shaped spike.
- **The budget verdicts are frame-time spikes, not draws**, and land in a different arm each time:
  - 9392 (ctrl): `camera_socket_0`, MS, 16.12 ms p95;
  - 9393: `attacker_spawn_5`, MS, 15.24 ms p95 at 1,949 draws;
  - 9392 again (ctrl2): every station inside budget.

  The draw overrun at `attacker_spawn_5` that 9391 showed is gone in all three arms. Its worst heading, yaw 90:
  9391 2,004 draws, 9392 1,977 (the bus zones had moved six cars out of that view), 9393 1,949.

## For the walker

Nothing new to see beyond 9392: the knob looks the same and costs less.
