"""SUPERSEDED, KEPT (2026-10-06): applied, rebuilt, and REVERTED before release.
Sinking the whole ramp by its head overshoot landed the head flush -- the ramp census read
0.000 on all 174 ramps and a capsule walked deli_a03's stair both ways -- but it put the
ramp a riser under the nosings, so every visual tread stood above it, and the nav bake,
which reads the visual meshes too, saw 0.206 m risers against a 0.15 climb: the swept gate
failed stair traversal on 94 of 144 shells, where 0.189.0 passed all 144. Replaced by
patch_dc_ramp_head_trim.py, which trims the head instead and keeps the ramp on the nosings.

Deli Counter 0.190.0: a stair's collision ramp lands its HEAD on the
landing, as `ramp_foot_extension` (2026-07-21) landed its foot on the floor.

Found 2026-10-06 (roadmap 189, cold run 9186 seed_9003). Laser Tag's player
bodies stuck 3,148 times at the head of deli_a03's up-stair, and finished its
route in 0 of 25 runs.
- **Measured over the whole library** (`ramp_ridge_census.py` at the factory
  root's `docs/findings/stairwell_on_one_grid_in_four/`): every one of 174
  ramps in 98 shells tops out 0.19 to 0.21 m above the floor it delivers to.
  That is the top face's end corner, at `step_rise/2 + (thickness/2) *
  cos(pitch)` over the landing: the half-step-proud offset that makes the
  surface ride the nosings, plus half the slab's thickness through the tilt.
  The foot fix said, correctly, that it "leaves the head of the flight
  untouched".
- **Walked** (`stair_head_walk.gd`): a capsule of Laser Tag's size (r 0.35,
  h 1.8, no step-up, floor_max_angle 45) on deli_a03's up-stair.
  - Ramp as built: DOWN stuck on the landing for the full 8 s; UP arrived,
    topping out at 3.47 over a 3.30 landing.
  - Ramp lowered one riser (the control): DOWN arrived in 2.4 s, UP in 3.8 s.
- Going up, a body rises over the ridge and drops onto the landing. Coming
  down, it meets a 0.2 m step, about twice what a capsule walks up
  unassisted. The navmesh climbs 0.15 and Lot's walkers step 0.5, so neither
  saw it.

`stairwell.ramp_head_drop` gives the overshoot. All three ramp constructions
(a flight's ramp, and an L-stair's two legs) sink their centre by it. The head
then meets the landing flush, and the foot -- already extended to the floor
-- goes a little under it.

    python patch_dc_ramp_head.py
"""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
DC = ROOT / "deli_counter"
SW = DC / "stairwell.py"
BUILDER = DC / "deli_counter.py"

HELPER_OLD = '''    lead = step_rise / 2.0 + (thickness / 2.0) / math.cos(pitch_rad)
    extra = lead / math.sin(pitch_rad)
    return extra, extra / 2.0 * math.cos(pitch_rad), extra / 2.0 * math.sin(pitch_rad)
'''
HELPER_NEW = '''    lead = step_rise / 2.0 + (thickness / 2.0) / math.cos(pitch_rad)
    extra = lead / math.sin(pitch_rad)
    return extra, extra / 2.0 * math.cos(pitch_rad), extra / 2.0 * math.sin(pitch_rad)


def ramp_head_drop(pitch_rad, step_rise, thickness=0.25):
    """How far a stair's collision ramp must sink so its HEAD meets the
    landing it delivers to (0.190.0).

    The half-step-proud offset that makes the surface ride the nosings, plus
    half the slab's thickness through the tilt, leaves the top face's end
    corner `step_rise / 2 + (thickness / 2) * cos(pitch)` above the landing.
    Measured over the library: 0.19 to 0.21 m on all 174 ramps. Going up a
    body rides over it and drops onto the landing; coming DOWN it meets that
    as a step, and a capsule walks up about 0.10 m unassisted
    (`unassisted_step_max_m`). On deli_a03 a body of Laser Tag's size stood
    on the landing for 8 s and never started down; sunk one riser, it was at
    the foot in 2.4.

    Sinking the whole ramp by this lands the head flush. The foot, already
    extended to the floor by `ramp_foot_extension`, goes the same distance
    under the floor, which a body never meets.
    """
    if pitch_rad <= 0.0:
        return 0.0
    return step_rise / 2.0 + (thickness / 2.0) * math.cos(pitch_rad)
'''

MAIN_OLD = '''                    _ext, _back, _drop = stairwell.ramp_foot_extension(
                        angle, step_h)
                    wx, wy = self._stair_pt(st, sx, st.y - sign * _back)
                    ramp = self._box(
                        f"stair{si}{ch}ramp_{s}" + self.col_suffix["convex"],
                        (wx, wy, z + H / 2 + step_h / 2 - _drop),
'''
MAIN_NEW = '''                    _ext, _back, _drop = stairwell.ramp_foot_extension(
                        angle, step_h)
                    # THE HEAD, TOO (0.190.0): sunk so its top corner meets the
                    # landing instead of standing 0.2 m over it -- a step a
                    # body coming DOWN cannot climb (stairwell.ramp_head_drop).
                    _head = stairwell.ramp_head_drop(angle, step_h)
                    wx, wy = self._stair_pt(st, sx, st.y - sign * _back)
                    ramp = self._box(
                        f"stair{si}{ch}ramp_{s}" + self.col_suffix["convex"],
                        (wx, wy, z + H / 2 + step_h / 2 - _drop - _head),
'''

A_OLD = '''                             (wx, wy, z + riseA / 2 + step_h / 2 - _dropA),
'''
A_NEW = '''                             (wx, wy, z + riseA / 2 + step_h / 2 - _dropA
                              - stairwell.ramp_head_drop(angA, step_h)),
'''

B_OLD = '''                             (wx, wy, z + riseA + riseB / 2 + step_h / 2
                              - _dropB),
'''
B_NEW = '''                             (wx, wy, z + riseA + riseB / 2 + step_h / 2
                              - _dropB - stairwell.ramp_head_drop(angB, step_h)),
'''

EDITS = {SW: [(HELPER_OLD, HELPER_NEW)],
         BUILDER: [(MAIN_OLD, MAIN_NEW), (A_OLD, A_NEW), (B_OLD, B_NEW)]}


def main():
    staged = {}
    for path, pairs in EDITS.items():
        data = path.read_bytes()
        crlf = data.count(b"\r\n")
        assert crlf in (0, data.count(b"\n")), f"{path}: mixed line endings"
        eol = "\r\n" if crlf else "\n"
        text = data.decode("utf-8")
        for old, new in pairs:
            old, new = old.replace("\n", eol), new.replace("\n", eol)
            n = text.count(old)
            assert n == 1, f"{path.name}: anchor matched {n} times: {old[:70]!r}"
            text = text.replace(old, new)
        staged[path] = text
    for path, text in staged.items():
        path.write_bytes(text.encode("utf-8"))
        print("patched", path.relative_to(ROOT))


if __name__ == "__main__":
    main()
