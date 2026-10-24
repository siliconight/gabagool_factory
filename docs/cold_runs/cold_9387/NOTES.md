# Cold run 9387 -- 0 interventions; restaurant_row_001, seed 9003: the walker's walk of 9386, four findings in the tools

**What it was for.** Staged from 9386, after the walker's walk of it (`docs/findings/walk_2026-10-23_9386/`). Moved
since, all committed before the run began: Deli Counter 0.265.0 (acb3e6ec, the root is the builder) and 0.266.0
(ecac8dc6, finding 8: litter bins against walls); Lot 0.127.0 (0db5bee, finding 10: the bus stop's flag at the curb)
and 0.128.0 (ab8bcfe, finding 12: a far-side signal for every approach); Zoo 1.121.0 (1859226, the signal's `right`
form).

**Every leg ran, `INTERVENTIONS: 0`.** The light check: FAIL 3, PASS 33, REPORT 1 -- the same three dark rooms as 9385
and 9386, every opening passing.

**The signals, measured** (`signal_faces.out.txt`, the finding's `signal_faces.gd` on this walk copy): six, three a
junction, where 9386 had two. NOTE ON THE PROBE: it prints local +Z as the face, which is the plain module's; the
`right` form's heads face local -Z, so each line's true facing is the opposite of `face_plan`. Read so, at the east
junction: `cover_1` north of the main road on its west side, arm south over the lanes, heads facing east to the
westbound driver; `cover_20` south of it on the east side, heads facing west to the eastbound driver; `cover_22` on
the main road's far (south) kerb, heads facing north up the side street. The west junction the same. The scene names
the `_fright` module, so Zoo's form resolved.

**Frames** (`signal_*_inspect.webp`, `tools/look_shots.py --inspect studio`, the inspection light -- geometry, not the look):
`westbound` (eye 36,1.7,19.5 -> 16.6,5.0,20.3): the far-side mast arm back over the lanes from the right-hand pole,
both heads facing the camera; `side_street` (22.5,1.7,3 -> 23.6,5.0,27.63): the signal across the main road on the
driver's right facing up the street; `eastbound` the same for its approach. The same stations shot as shipped
(blue hour) were too dark at that range to read a head and are not kept. A frame of deli_a03's moved bin was dropped: a gondola
hid it from the station chosen. The bins are proven by the census and `tests/test_bins_on_walls.py`, not by a
frame.

The walk copy `_runs/walk_9387_restaurant_row_001`.
