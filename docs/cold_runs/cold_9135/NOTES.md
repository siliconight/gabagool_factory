# Cold run 9135 -- the real look in a level, on a brief that keeps its gas station

gas_block_001, a NEW brief anchored on `gas_station`, on Zoo 1.46.0 (the
video poker, the ATM and both registers rebuilt with smooth type, painted
shading and broken corners). Zero interventions (journal 0, unattributed
files 0), no observations.

## Why a new brief

9134 lost its gas station when the library grew (`pick_lot` pops by
`next(rng) % len(pool)`, so one more building family reshuffles every
seed). A brief's `archetype` anchors one building; this one anchors the gas
station, so the store with the ATM, the poker cabinet and the tills is in
every candidate whatever the library does to the other two.

All three candidates drew a gas station:

| seed | buildings | major findings |
|---|---|---|
| 9080 | bank_tower_a02, freight_terminal_a01, gas_station_a03 | 1 |
| 9181 | arena_a03, gas_station_a02, marina_a02 | 2 |
| 9282 | airport_terminal_a02, funeral_home_a02, gas_station_a02 | 1 |

`pick_candidate.py` took 9080: nav walktest ok, no major
`LT_ROUTE_NEVER_COMPLETED` or `LT_MAP_ENEMY_PATHING_BROKEN`.

## Seen in the level (`frames/`)

A probe found each prop by the material it wears, waited out the shader
warm-up (248 frames, `scaling_3d_scale` back at 1.0) and stood a camera in
front of it:

* `atm0_full`, `atm0_close`, `atm1_*` -- two ATMs, one in the store and one
  in the bank tower. Smooth sign, brushed fascia, the sticker, the keypad.
* `poker0_full`, `poker0_close` -- one cabinet in the store, a hand dealt.
* `till0_counter`, `till0_customer`, `till0_clerk` -- the service counter's
  two tills: putty body, dot-segment display, lettered keys at the clerk's
  end.

What the frames also show, and nothing measured: the machines now sit among
props that still have the pixel look (the lottery dispensers are flat red
boxes, the cooler's bottles are pixel art). The two looks are side by side
in one room for the first time.

## Priced (`perf_9135.json`)

**RETRACTED AS A FRAME-TIME FIGURE, 2026-10-02, kept above what replaced
it.** The table below was not measured on an idle machine. The same lot at
the same draw counts reads 9.3 to 9.7 ms at `highest_vantage` yaw 90 (16.70
here) and 7.8 to 8.1 ms at `longest_sightline` yaw 90 (14.39 here) in four
passes with nothing else running: `docs/findings/real_look_trial/
AB_IN_LEVEL.md`. The DRAW counts below hold; the milliseconds and "6 of 14
over" do not.

The fixed-station harness on a fresh copy of the package, GL Compatibility.
Budget 2000 draws and 11.0 ms p95 (provisional). 6 of 14 stations over:

| station | p95 ms | draws |
|---|---|---|
| highest_vantage | 16.70 | 2160 |
| extraction_14 | 15.69 | 2726 |
| longest_sightline | 14.39 | 1884 |
| extraction_3 | 12.99 | 2148 |
| attacker_spawn_2 | 12.96 | 2239 |
| attacker_spawn_1 | 12.51 | 2196 |

THIS IS A BASELINE AND NOT A PRICE. The lot is new, so no earlier run is
comparable, and the same lot was not built on Zoo 1.45.0. What the real look
costs is held by the scratch-project measurement (Zoo 1.46.0's changelog:
draws unchanged on three props, one more on a service counter, texture
memory up 1 to 3.6 MiB a prop uncompressed) and by nothing measured in a
level. Runs on this brief from here on can be compared with this one.

## Findings

51, none comparable with an earlier run. `PRESENTATION_ZFIGHT` reports 96
coplanar pairs, worst `base:stair0_0_* / floor_banking_hall` -- the bank
tower's stairs, not a prop this run changed. `LT_MAP_PLAYER_STUCK` 2156 and
263, `LT_MAP_TRAVERSAL` 86 % and 65 % of the route walked.

## Open

* The extra draw on a service counter: keep it, or build the one-material
  version (an emission mask over one image).
* The display flicker has never reached a counter's tills (Level Factory
  matches `M_Register_*_Face`; a counter's is `M_Counter_VFD_*_Face`).
  Measured in a scratch project with it switched on: a 5.2 % swing in the
  display's green, one more draw a counter.
* Frame time and texture memory of the real look in a level, A against B.
* Godot's import compression against the new atlases.
