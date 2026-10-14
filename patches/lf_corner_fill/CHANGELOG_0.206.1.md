## [0.206.1] - A spent bag is not a closed run: the corner wall's fill deals afresh before it stops

**Factory roadmap 241, the corner shop.** Cold run 9295's seed_9003 closed its urban wall 12.70 m short of the
run's end, where 9294's stopped 3.70 m short, so its closing corner shop did not stand at the corner.

- **Traced** (the factory root's `patches/lf_corner_fill/replay_9003.py`, whose replay stood the run's wall block
  for block): the fill stopped at x 55.50 with 18.70 m to fill before the closing corner's room. The one block
  left on the bag was `gs_midrise_f`, at 19.8 m.
- **The cause.** 0.206.0's `_cornered` stopped when nothing LEFT ON THE BAG fit. That is the condition `infill`
  met on the near side and answered in 0.203.0 with a fresh deal behind the remainder.
- **The fix.** Where nothing on the bag fits before the closing corner's room and some design does, a fresh deal
  now goes behind what is left. Without heights, the fill takes the next dealt block that fits, as `infill`
  does.
- **Measured before it was written** (`patches/lf_corner_fill/measure_remainder.py`): 600 walls at the
  factory's thirteen built widths, on the three candidates' plates, with no action and four, seeds 1-40.

      shortfall      median   90th      worst     over 6.6 m (the narrowest design)
      0.206.0        4.70 m   12.70 m   14.20 m   171 of 600
      0.206.1        0.60 m    2.60 m    4.10 m     0

  Every wall opens and closes on a corner on both, and neither puts one mid-wall.
- **The cost: a narrow block can stand beside itself,** only where no other design fits that room.
  - That is `_by_height`'s rule, and `infill`'s. It happens on 20 of the 600 walls: `gs_midrise_i` 12
    times, `h` 5 and `g` 3.
  - Stopping instead would leave 4 walls more than 6.6 m short, the worst 12.70 m.
  - The test file's neighbours' check asserted no repeat at all, which 0.206.0 met by stopping short. It now
    asserts the rule.
- **Without a corner row, every wall is still 0.205.0's** (the control digest).
- **`tests/unit/test_urban_corner_shops.py`:** 10 checks. Against 0.206.0, `test_a_run_closes_within_the_narrowest_design_of_its_end` alone fails, first on a 171 m plate with no action, seed 12, 9.30 m short; the other nine pass, the corrected neighbours' rule among them. Replayed on cold run 9295's three candidates (the factory root's `patches/lf_corner_fill/replay_candidates.py`, whose control is the run's own walls stood again on 0.206.0): seed_9003 12.70 -> 1.90 m short, seed_9205 4.70 -> 2.60, and seed_9104, the pick, block for block as it stood.
- **The suite:** `python -m pytest -q`: exit 0, 2,400 passed (0.206.0's 2,399 and the new check), 14 skipped (the real-tool smoke), 1 xfail, counted off the progress marks, in 6 min 34 s.
