"""Deli Counter 0.190.0: VERSION and CHANGELOG for `patch_dc_ramp_head_trim.py`
(after the superseded `patch_dc_ramp_head.py`), `patch_dc_stair_flight_width.py`,
`patch_dc_stair_flight_width_all.py` and `patch_dc_grid_baseline_0190.py`.

    python patch_dc_0190_release.py
"""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
DC = ROOT / "deli_counter"

ENTRY = '''## [0.190.0] - stairs a body can walk: no ledge at the head, no flight narrower than a corridor

Both were found 2026-10-06, measuring roadmap 189 at the factory root
(`docs/findings/stairwell_on_one_grid_in_four/`).

### Every stair's head stood a riser over its landing

**Cold run 9186.** With deli_a03's stairwell fixed (0.189.0), Laser Tag's bots
reached its upstairs objective. They then stuck 3,148 times at the head of
its up-stair, all in one 2 m cell, and finished 0 runs of 25.

**The census** (`ramp_ridge_census.py`): every stair collision ramp in the
library topped out 0.19 to 0.21 m above the floor it delivers to. That is 174
ramps in 98 shells.
- It is the top face's end corner, at `step_rise/2 + (thickness/2) *
  cos(pitch)` over the landing.
- It comes from the half-step-proud offset that makes the surface ride the
  nosings.
- `ramp_foot_extension` (2026-07-21) landed the foot, and said it left the
  head untouched.

**The walk** (`stair_head_walk.gd`): a capsule of Laser Tag's size (r 0.35,
h 1.8, no step-up, floor_max_angle 45) on deli_a03's up-stair.
- As built: DOWN stuck on the landing for 8 s; UP arrived.
- The control, with the ramp lowered one riser: down in 2.4 s, up in 3.8 s.
- A ledge is a drop going up and a riser coming down. The navmesh climbs
  0.15 and Lot's walkers step 0.5, so neither had seen it.

**Refuted first, kept** (`patch_dc_ramp_head.py`): SINKING every ramp by the
overshoot.
- Built, it read 0.000 on the census and walked both ways.
- The swept nav gate then failed stair traversal on **94 of 144** shells.
- The ramp ran a riser under the nosings, so every visual tread stood above
  it, and the bake, which reads visual meshes, saw 0.206 m risers against a
  0.15 climb.
- Reverted before release. The census and the walk measured collision only.

**`stairwell.ramp_head_trim`** TRIMS the head instead.
- It cuts `overshoot / sin(pitch)` along the incline and keeps the foot, so
  the corner meets the landing where the nosing line does, at the top
  tread's front edge.
- The ramp still rides the nosings. A new test,
  `test_no_tread_stands_above_the_ramp`, holds that.
- A final leg's discharge collider reaches back over the strip left; a
  landing already reached back over its top tread.
- Scissor channels keep their ramps, since they have no plate to reach back.
  The L-stair builder is untouched. Neither style stands in the library:
  77 switchback and 72 straight stairs.

**Rebuilt and measured:**
- census, 0.000 m over the landing on all 174 ramps;
- walk, down 2.4 s and up 3.8 s. The over-lowered control now fails going
  up, so the instrument sees both directions;
- swept gate, **144 of 144** shells traverse, as on 0.189.0.

### No generator draws a flight narrower than a corridor

**twin_a01's 0.9 m flights traversed at 7 of 8 grid origins.**
- The route-walking neck finder put the tear on the flight itself: one cell
  after erosion.
- **Refuted first, kept:** moving the fridge, which stood nearest the tear.
  Built in scratch, it was still 7 of 8.
- At 1.2 m, furniture untouched, 8 of 8, gate and census.

**`presets.STAIR_FLIGHT_WIDTH`** is the contract's corridor minimum
(`min_corridor_width_m`, 1.1: 2 x the bake radius + 0.3) and one bake cell:
1.2.
- `twin` and `rowhome` drew 0.9 m flights, and `pawn_shop` and
  `suburban_safehouse` drew 1.0 m. All four draw it now.
- twin_a01's frozen spec stands on it, with the reason on each stair's
  `meta` as `width_why`, and is still a fixed point of furnish.
- The library's 1.0 m and 1.1 m flights (cr_pawn, night_pawn, card_shop_a01)
  connect at 8 of 8 as built and keep their specs.

### The baseline

`grid_fragile` 7 -> 6:
- twin_a01 leaves.
- primos_pizza's list gains `patrol_point_PAT_CLUB`, which the trimmed
  ramps' base bake now reaches, at 6 of 8 like its stair.

Level Factory's themed-lot fitness, measured with its own `themed_fitness`:
101 -> **102** of 127. twin_a01 and deli_a03 are both fit again.

### Tests

- **`test_stair_ramp_head.py`, 7:**
  - the defect as a number, 0.1995 m on deli_a03's flight;
  - the trim lands the head and keeps the foot, across legal stairs;
  - no tread stands above the ramp;
  - the strip left is the top tread and at most a cell's sliver;
  - a level ramp needs no trim;
  - the builder trims and reaches back (read as source).
  - Six fail on 0.189.0. The defect statement passes both sides by design.
  - The first draft's grid held 0.56 m risers, where both properties fail
    for any ramp; it was cut to legal stairs.
- **`test_stair_flight_width.py`, 3:** the width is derived from the
  contract; no preset draws narrower than a corridor; twin_a01 stands on the
  width. All three fail on 0.189.0.
- **`test_navgate_population.py`:** `test_grid_baseline_has_not_gone_stale`
  failed on twin_a01 until the baseline let it go.

**Suite:** 1,250 passed, 2 skipped. That is 0.189.0's 1,240 and these 10.

'''


def main():
    v = DC / "VERSION"
    assert v.read_bytes() == b"Deli Counter 0.189.0", v.read_bytes()
    cl = DC / "CHANGELOG.md"
    data = cl.read_bytes()
    assert b"\r\n" not in data
    text = data.decode("utf-8")
    assert text.startswith("## [0.189.0] - the nav gate bakes"), text[:60]
    cl.write_bytes((ENTRY + text).encode("utf-8"))
    v.write_bytes(b"Deli Counter 0.190.0")
    print("Deli Counter 0.190.0: VERSION and CHANGELOG")


if __name__ == "__main__":
    main()
