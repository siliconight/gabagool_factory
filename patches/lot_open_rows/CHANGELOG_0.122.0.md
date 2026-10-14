## 0.122.0 - a row the fences leave open shuts nothing: enemies may stand behind the urban street's near side

**Factory roadmap 241, the urban street's near side.** `plan_fences` leaves an Empty row open, unfenced, when a
mission marker stands in the band behind its front line, rather than strand a spawn, objective or enemy nobody
can reach. `site_spawns.place_enemies` kept every enemy out of every row's band all the same
(`shut_band_rects`, 0.97.3): a shut band that nothing shut.

- **On a strip level it never mattered.** Of the 276 `lot_assemble` job logs on the factory's disk, a row was
  left open in 3, all of them cold run 9289's.
- **On the urban street it is the near side.** Level Factory 0.201.0 stands Empties between the mission's
  buildings. Each is a row of its own (`site_fences.rows`), and its band runs from its front line to the
  plate's edge, across the plate's whole width.
  - **The measurement:** the factory's `docs/findings/urban_street/spawn_filters.py` reran each of 9289's
    three jobs with `place_enemies` watched, and reproduced their enemies.
  - **seed_9205:** the near block's band and the far row's left only the street, open and inside the opening
    range of the crew's path. All six enemies were dropped (LOT_ENEMY_SPAWN_UNPLACEABLE), and Laser Tag
    refused the map.
  - **seed_9104:** all six stood in the street.
  - **seed_9003:** the near row's front was judged to be its far side, so its band covered the street and the
    crew's whole route.
  - **The fences had left all three rows open.**
- **One question, asked once.** `site_fences.markers_behind(band, members, markers)` returns the markers
  inside a row's band and in none of its houses.
  - `plan_fences` asks it, in place of its own copy.
  - `shut_bands(..., markers=())` leaves out a row that has any.
  - `site_spawns.shut_band_rects(..., markers=())` passes the markers through.
  - `place_enemies` passes its spawn, objective and extraction: the points `plan_fences` is handed, besides
    the enemies placed here.
  - Without markers every row is shut, as before.
- **The result:** cold run 9289's three candidates rerun on 0.122.0 (the factory's `docs/findings/urban_street/spawn_filters_0122.out.txt`, beside `spawn_filters.out.txt` on 0.121.0, whose rerun reproduced each job's enemies): seed_9205 places all six enemies, between b0 and b1, where none stood; seed_9104's six stand between the mission's buildings rather than in the street, found after 1 to 80 spots each against 133 to 1,357; seed_9003 moves three of its six (enemies 0, 1 and 4) onto ground its near row's band had shut. No spot on any of them is refused for a shut band alone.
- **Strip levels:** the picked `lot_assemble` jobs of cold runs 9278 to 9287 replayed from their own `job.log` on 0.121.0 and on 0.122.0 (the factory's `docs/findings/urban_street/lot_replay.py`): 10 jobs, 420 files, 0 differ.
- **Carried: a comment.** `site_cover.min_passable_gap`'s docstring said the contract's
  `clearances.derivation` "still evaluates the formula" at the refuted 0.15 m cell. Since Deli Counter 0.214.0
  it works the formula at the 0.1 m cell (1.00 m), and the walker kept the door at 1.25. No number or
  behaviour depends on it.
- **`tests/test_open_rows_are_not_shut.py`** has 5 checks, run on two fixtures:
  - 9289 seed_9205's site as `place_enemies` read it (`tests/fixtures/urban_row_001_seed_9205.place_enemies.json`);
  - the strip's fixture.

  4 of the 5 fail on 0.121.0; the fixture's own check passes on both. The suite: `python -m pytest -q`: 840 passed (0.121.0's 835 and the 5 here).
