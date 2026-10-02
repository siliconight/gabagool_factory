# Cold run 9134 -- screens that run, and a lot that is not the one expected

club_block_014, 9131's brief and seed, on Zoo 1.45.0 and Level Factory
0.127.0 (shutters on the ATM's and the video poker's CRTs, a flicker on the
register's display). Zero interventions, no observations.

## THE LOT CHANGED, and the batch's prediction was wrong

The batch said "Expected: the same lot". It is not. Seed 9181 of this brief
drew `gas_station_a02`, `airport_terminal_a02` and `strip_club_a01` in every
run through 9131; in this run it drew `arena_a03`, `mansion_a02` and
`strip_club_a01`.

What is different between 9131 and this run that the draw reads: Deli
Counter 0.171.0 added `video_store_a01` to the library. `pick_lot`
(`level_factory/packages/pipeline/building_library.py`) draws each non-anchor
building as `pool.pop(next(rng) % len(pool))`, and its own comment says
adding to the pool "reshuffles every existing draw". The pool is one family
longer, so the same seed lands on other buildings. That is the mechanism the
code states; it was not isolated by re-running with the video store removed.

What it costs:

* THE GAS STATION IS NOT IN THIS LEVEL. The run was meant to show the ATM,
  the poker cabinet and the register in the store the walker walked in 9131.
  It shows the strip club's cabinets instead. No ATM and no register is in
  this lot, so their screens are held by the scratch-project frames
  (docs/findings/screens_that_run/) and by nothing in a level.
* THE BASELINE IS GONE. Every draw and finding comparison since 9121 was
  against this brief and seed drawing the same three buildings. 63 findings
  -> 60 here is two different lots, not a change.
* `_runs/walk_export_club_block_014` now holds this lot. The 9131 gas-station
  walk copy was overwritten by it.

A brief whose archetype is `gas_station` anchors one in every candidate, as
`video_block_001` anchors the video store. That is the brief to walk the
machines in, and to keep as a baseline that a growing library cannot move.

## The screens (`poker_three_moments.png`, `club_cabinets.png`)

* Three frames of one cabinet in the club's back room, taken a few seconds
  apart in one run: the hand, the hand, a cleared screen. The deal runs in a
  level.
* The club's back wall: three cabinets in one frame. PIKE DRAW shows its
  hand; the two DOWN THE SHORE DRAW cabinets show theirs -- at this instant
  all three happen to be holding (a hand is held for 64% of the period), so
  this frame does not show them out of step.

## Priced (`perf_9134.json`)

53 headings, 61,574 draws, worst heading 2,465, median 1,021; 106 lights,
4,527 meshes, 23 over the 8-light cap. NOTHING TO SUBTRACT IT FROM: 9131's
61,510 was another lot. The shutters' cost is one draw a cabinet where it is
seen -- six cabinets in this level -- and that is counted, not measured: a
shutter's placeholder is alpha-masked, so switching the import pass off
would not remove the draw, and the on/off this needs is a package built by
Zoo 1.44.0 from the same lot.
