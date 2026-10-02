# Cold run 9131 -- the poster pass, the pinched bag, the porch light

Five releases since 9130, one run: Zoo 1.41.0 (plain poster stock, one or two
loud sheets a cluster) and 1.42.0 (a bag pinched at its seals), Deli Counter
0.169.0 (a home's door takes a porch light, not a lit sign) and 0.170.0
(poster runs at varied heights; a window poster pair in each store), Lot
0.87.0 (alley runs at varied heights). Same brief, same seed, same lot as
9130. Zero interventions, no observations.

The art leg before export: 0 blockers, 63 findings -- identical to 9130's by
code.

## What the frames show

* `window_poster_from_street.png`: the gas station's pair of sale sheets
  (ATM INSIDE, HOAGIES) in the glass left of its door, at the eye, reading
  the right way round from the forecourt. One on white, one on yellow: the
  stock rule.
* `window_poster_from_inside.png`: from the sales floor the same sheets
  show their print REVERSED. Deli Counter 0.170.0's changelog left this
  unlooked-at; this is the look. Paper against lit glass does show through,
  but this is the full print at full strength, not a ghost of it.
* `bags_pinched.png`: the chip aisle with Zoo 1.42.0's bag -- thin at the
  seals, fat in the belly. The same station as 9130's
  `gas_cakes_and_chips.png`.
* `poles_plain_stock.png`: two papered poles by the bus shelter. Cream and
  white sheets, one green: one loud bill a pole.

## What this run could not show

* THE PORCH LIGHT. The lot drew three buildings -- airport_terminal_a02,
  gas_station_a02, strip_club_a01 -- and none is a home. Deli Counter
  0.169.0 is held by its tests and its built library (8 homes, 0 signs), not
  by a frame.
* THE ALLEY RUNS' HEIGHTS. The site's six wall runs are at 1.69 and 1.30 m
  where every one was 1.60 (`site.slots.json`); the one frame aimed at one
  was black, an unlit back wall at night. Read from the manifest, not seen.
* THE INDOOR RUNS' HEIGHTS: gas_station_a02's sales-floor run is at 1.40.
  Not framed.

## Priced (`perf_9131.json`, against 9130's)

53 headings: 61,545 draws -> 61,510. Five headings moved: +1 at three and
+2 at one, which is the window poster where the storefront is in view (one
mesh more in the census, 4,493 -> 4,494) -- and -40 at defender_spawn_22
yaw 180. That last is not explained. The same heading moved by 40 the other
way in an earlier run on a change that added no draw; it is recorded as
measured and no cause is claimed. Worst heading 2,648 both. Lights 113,
meshes over the cap 44, both unchanged.
