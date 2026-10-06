"""Deli Counter 0.190.0: a stair's collision ramp is trimmed at its HEAD so it
meets its landing flush, as `ramp_foot_extension` (2026-07-21) landed its
foot on the floor -- without leaving the nosings.

Found 2026-10-06 (roadmap 189, cold run 9186 seed_9003). Laser Tag's player
bodies stuck 3,148 times at the head of deli_a03's up-stair.
- **Measured** (the factory root's `docs/findings/stairwell_on_one_grid_in_four/`):
  all 174 library ramps stood 0.19 to 0.21 m over the floor they deliver to.
  That is the top face's end corner, `step_rise/2 + (thickness/2) *
  cos(pitch)` above the landing.
- **Walked:** a capsule of Laser Tag's size could not walk DOWN onto the
  flight; up it could.

**Refuted first, kept** (`patch_dc_ramp_head.py`, applied, rebuilt,
reverted): sinking the whole ramp by that overshoot.
- The census read 0.000 and the capsule walked both ways.
- But the ramp then ran a riser under the nosings, so every visual tread
  stood above it.
- The nav bake reads visual meshes too, and saw 0.206 m risers against a
  0.15 climb. The swept gate failed stair traversal on 94 of 144 shells.

**Now the head is TRIMMED, and the ramp stays on the nosings.**
- `stairwell.ramp_head_trim` shortens the ramp along its incline by
  `overshoot / sin(pitch)` and keeps the foot where it was. The corner then
  meets the landing at the top tread's front edge, where the nosing line
  reaches the landing.
- The strip it leaves is less than one tread deep. The visual top tread
  already covers it for the nav bake.
- A final leg's discharge collider now reaches back over it, for a body. A
  landing already reaches back over its top tread.

**Scope.**
- Scissor channels keep their ramps: they deliver at both ends with no
  plate to extend.
- The L-stair builder is untouched.
- Neither style stands in the library: 77 switchback and 72 straight
  stairs.

    python patch_dc_ramp_head_trim.py
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


def ramp_head_trim(pitch_rad, step_rise, thickness=0.25):
    """How much of a stair's collision ramp to cut from its HEAD so the head
    meets the landing flush (0.190.0).

    The half-step-proud offset that makes the surface ride the nosings, plus
    half the slab's thickness through the tilt, leaves the top face's end
    corner `step_rise / 2 + (thickness / 2) * cos(pitch)` above the landing:
    0.19 to 0.21 m on all 174 library ramps. Going up a body rides over it;
    coming DOWN it meets a step about twice what a capsule walks up
    unassisted, and on deli_a03 a body of Laser Tag's size never started down.

    TRIMMED, NOT SUNK. Sinking the ramp by the same amount lands the head too,
    and was built and reverted: it puts the ramp under the nosings, every
    visual tread stands above it, and the nav bake -- which reads visual meshes
    -- saw 0.206 m risers against a 0.15 climb on 94 of 144 shells. Cutting
    `overshoot / sin(pitch)` from the head along the incline keeps the surface
    on the nosings and puts the corner where the nosing line reaches the
    landing: the top tread's front edge. The strip left behind is less than one
    tread deep, which the visual top tread fills.

    Returns `(trim, back, drop)`: shorten the ramp by `trim` along its own
    incline, move its centre `back` downhill in plan and `drop` downward, and
    the FOOT stays exactly where it was.
    """
    if pitch_rad <= 0.0:
        return 0.0, 0.0, 0.0
    over = step_rise / 2.0 + (thickness / 2.0) * math.cos(pitch_rad)
    trim = over / math.sin(pitch_rad)
    return trim, trim / 2.0 * math.cos(pitch_rad), trim / 2.0 * math.sin(pitch_rad)
'''

MAIN_OLD = '''                    _ext, _back, _drop = stairwell.ramp_foot_extension(
                        angle, step_h)
                    wx, wy = self._stair_pt(st, sx, st.y - sign * _back)
                    ramp = self._box(
                        f"stair{si}{ch}ramp_{s}" + self.col_suffix["convex"],
                        (wx, wy, z + H / 2 + step_h / 2 - _drop),
                        self._stair_sz(st, st.width, length3d + _ext, 0.25),
                        self.COLLISION)
'''
MAIN_NEW = '''                    _ext, _back, _drop = stairwell.ramp_foot_extension(
                        angle, step_h)
                    # THE HEAD, TOO (0.190.0): trimmed so its corner meets the
                    # landing instead of standing 0.2 m over it -- a step a
                    # body coming DOWN cannot climb (stairwell.ramp_head_trim).
                    # A scissor channel delivers at both ends with no plate to
                    # reach back over the cut, so it keeps its full ramp.
                    _trim, _tback, _tdrop = ((0.0, 0.0, 0.0)
                                             if st.style == "scissor" else
                                             stairwell.ramp_head_trim(angle,
                                                                      step_h))
                    wx, wy = self._stair_pt(st, sx,
                                            st.y - sign * (_back + _tback))
                    ramp = self._box(
                        f"stair{si}{ch}ramp_{s}" + self.col_suffix["convex"],
                        (wx, wy, z + H / 2 + step_h / 2 - _drop - _tdrop),
                        self._stair_sz(st, st.width,
                                       length3d + _ext - _trim, 0.25),
                        self.COLLISION)
'''

DISCH_OLD = '''                            self._col_box(f"stair{si}col_discharge_{s}",
                                          (wx, wy, dz),
                                          self._stair_sz(st, hole_w, d_depth,
                                                         step_h))
'''
DISCH_NEW = '''                            # THE COLLIDER REACHES BACK over the strip the
                            # ramp's head trim leaves on the top tread (0.190.0),
                            # so a body walks from plate to ramp on one surface.
                            # A landing already reaches back over its top tread.
                            c_back = (0.0 if has_landing else
                                      stairwell.ramp_head_trim(angle, step_h)[0]
                                      * _m.cos(angle))
                            c_depth = d_depth + c_back
                            c_y = st.y + sign * (st.run / 2 + d_near - c_back
                                                 + c_depth / 2)
                            cwx, cwy = self._stair_pt(st, hole_cx, c_y)
                            self._col_box(f"stair{si}col_discharge_{s}",
                                          (cwx, cwy, dz),
                                          self._stair_sz(st, hole_w, c_depth,
                                                         step_h))
'''

EDITS = {SW: [(HELPER_OLD, HELPER_NEW)],
         BUILDER: [(MAIN_OLD, MAIN_NEW), (DISCH_OLD, DISCH_NEW)]}


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
