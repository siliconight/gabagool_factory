## 0.118.1 - a line starts clear of the kerb's own cut span, and a signal keeps its arms' box: the corner pole stands

**Factory roadmap 240, found in its first cold run.** Cold run 9262 stood
0.118.0's line on restaurant_row_001's picked lot and its west side street
carried 2 poles where its run asked for 3: no pole at the T where it meets the
main road, so the line's first pole stood 35.7 m from the main road's nearest
-- past the reach a junction's wires will take. Re-planned from the run's own
drawn spec, step by step, two things refused it:

- **The run began inside the cut's clearance.** A cut stands on its kerb as
  its width and `site_streets.CUT_MARGIN` either side (`split_span`): the
  10 m crossing at station 0 is the span 0.0 to 5.6, and
  `site_furniture._clear_of_cuts` reads the span. `_runs` trimmed from the
  width alone, so the first station, 6.45, stood 0.6 m inside the clearance
  and was refused as a cut -- on every run of every street, behind every
  crossing, whenever the station was not stepped clear by something else.
- **A signal's 5 m circle refused every step off it.** `Signal_1L_0` stands at
  station 8.40 on the furniture line, 7.55 m from the road's centre line
  against the pole line's 5.61, and the circle refused 6.56 to 12.45. Its
  arms are a box -- 8 m along its yaw, 0.62 m across, at 6 to 6.5 m up (Zoo
  `traffic_signal`) -- and a pole on its line stands 1.63 m clear of it.

**What changed.** `_runs` breaks a line at the kerb's own span for each road
crossing; `_room` asks a signal's box, grown by the pole's radius and the gap,
in the signal's frame. REFUTED, KEPT in the comment: the 5 m circle,
`SIGNAL_CLEAR`. And the line reads every piece planned so far, every
road's, not its own kerb's alone (`site_furniture.plan_furniture`): a
corner pole stands where two roads' furniture meet, and `_room` reads plan
boxes, right across roads.

**Measured:** On cold run 9262's drawn spec the west side street stands 3 poles where 0.118.0 stood 2, the first at its run's start, 7.05 from the crossing; the east one's corner pole stands there too, where 0.118.0 had stepped it to 7.45 off the cut's clearance. On the four stored site fixtures 8, 9, 9 and 9 poles become 9, 10, 9 and 9 -- a corner pole back on bank_block_001 seed 9256 and club_block_014 seed 9080 -- with 3 cans each as before (the factory's `docs/findings/pole_line/pole_census.py`)

**Tests:** `test_every_line_stands_its_corner_poles_beside_a_signal`, on cold
run 9262's roads: every station of every line stands a pole, no run starts
inside a cut's clearance, and no pole stands in a signal's box. On 0.118.0 the new test fails as cold run 9262 did: the west side street stands 2 poles for its 3 stations

**Suite:** 809 passed, where 0.118.0 passed 808: the new test
