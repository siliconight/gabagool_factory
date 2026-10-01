# Cold run 9121 -- the pumps drawn

Zoo 1.36.0 (the pump: a 1997 two-sided mechanical dispenser, three grade
panels a face, lit price wheels and a lit FLAPPHAS header, two draws). Same
brief, same seed, same lot as 9120. Zero interventions, one observation (the
look shots).

The art leg before export: 0 blockers, 63 findings -- identical to 9120's by
code (none moved). Export closure clean (0 issues over 53 resources).

## The pumps (`01`-`05`, night, sky wired)

Given stations, Godot metres; gas_station_a02's pumps stand at x 103 / 97,
z 16 / 10 / 4, the lanes between the islands at z 7, 13, 19.

* `05_pump_back` (103, 1.45, 19.6) -> (103, 1.15, 16): the pump from its
  outer lane, in the canopy's light -- the silver, red and gold panels, the
  holstered nozzles and hoses, the price wheels and FLAPPHAS. Frame mean 11.5.
* `04_pump_face` (103, 1.45, 12.4) -> (103, 1.15, 16): the same pump's other
  face, from the inner lane. Square to the camera, so the faces are on the
  lanes as the planner intends; the face stands in shadow and only the glow
  reads. Mean 11.2. This is walk finding 4 (the forecourt is dark), not the
  pump.
* `03_lane` (110, 1.6, 13) -> (94, 1.3, 13): down the lane between the
  islands to the store. Mean 9.9.
* `02_pumps`, `01_street_approach`: 9120's stations. 9.9 -> 12.8 at the pumps
  (their glow), 9.9 -> 10.1 from the street.

From the street (`01`) the pylon and the pumps say the same name and the same
prices (variant 0, both).

## Still open from the FLAPPHAS walk

2. The lit box over the door is blank -- visible in `01` and `03`. Attributed
   this run, and 9120's attribution was WRONG: it named Lux. Lux turns its own
   preview quad off at fixture markers (`lux_fixture_spawner.gd`); the blank
   panel is Zoo's `sign_box`, which painted a face only from a Pixelcoat sign
   pack, and no theme ships one. Every derived sign in the library -- 102 --
   is blank, all three on this site. Next.
3. Stone inside.
4. The forecourt is dark (`04`).

`wire_sky.py` printed "identical to 9111's wiring: False" on this copy; the
sky rendered (stars in every frame). Not investigated.
