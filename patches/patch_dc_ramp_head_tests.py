"""SUPERSEDED, KEPT (2026-10-06): applied, rebuilt, and REVERTED before release.
Sinking the whole ramp by its head overshoot landed the head flush -- the ramp census read
0.000 on all 174 ramps and a capsule walked deli_a03's stair both ways -- but it put the
ramp a riser under the nosings, so every visual tread stood above it, and the nav bake,
which reads the visual meshes too, saw 0.206 m risers against a 0.15 climb: the swept gate
failed stair traversal on 94 of 144 shells, where 0.189.0 passed all 144. Replaced by
patch_dc_ramp_head_trim.py, which trims the head instead and keeps the ramp on the nosings.

Deli Counter 0.190.0, the tests for `patch_dc_ramp_head.py`, applied first
so they are seen failing on 0.189.0.

    python patch_dc_ramp_head_tests.py
"""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
TEST = ROOT / "deli_counter" / "test_stair_ramp_head.py"

BODY = '''"""Pure tests for the stair ramp meeting its landing (no bpy) -- the head's
half of what `test_stair_ramp_foot.py` proves for the foot (0.190.0).

Measured 2026-10-06 (roadmap 189 at the factory root): every one of the
library's 174 ramps topped out 0.19 to 0.21 m over the floor it delivers to.
A capsule of Laser Tag's size stood on deli_a03's upper landing for 8 s and
never started down; with the ramp sunk one riser it was at the foot in 2.4.
Going UP the step is a drop and nothing notices it; coming DOWN it is a
riser, which is why the foot fix of 2026-07-21 left it behind.
"""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import agent_contract                # noqa: E402
import stairwell as S                # noqa: E402

THICK = 0.25


def _head_corner(pitch, rise, step_rise, length3d, extra, drop, head,
                 thickness=THICK):
    """The top face's end corner at the head, relative to the flight's base.

    Mirrors deli_counter.py: the slab's centre sits `rise/2 + step_rise/2 -
    drop - head` up, its upper end half the extended length along the incline
    from there, and the top face's corner half the thickness along the face
    normal, whose vertical component is cos(pitch)."""
    centre = rise / 2.0 + step_rise / 2.0 - drop - head
    mid_end = centre + (length3d + extra) / 2.0 * math.sin(pitch)
    return mid_end + (thickness / 2.0) * math.cos(pitch)


def _foot_surface(pitch, rise, step_rise, length3d, extra, drop, head,
                  thickness=THICK):
    """The walkable surface at the foot, measured as test_stair_ramp_foot
    measures it: vertically through the tilt."""
    centre = rise / 2.0 + step_rise / 2.0 - drop - head
    mid_at_foot = centre - (length3d + extra) / 2.0 * math.sin(pitch)
    return mid_at_foot + (thickness / 2.0) / math.cos(pitch)


def _flight(rise, run, n):
    pitch = math.atan2(rise, run)
    extra, _back, drop = S.ramp_foot_extension(pitch, rise / n)
    return pitch, math.hypot(run, rise), extra, drop


def test_without_the_drop_the_head_stands_a_riser_proud():
    """What shipped, on deli_a03's up-stair: 16 risers over 3.3 m, a 4.0 m
    run. 0.1995 m against the 0.2 the library census measured, and well over
    what a capsule walks up."""
    rise, run, n = 3.3, 4.0, 16
    pitch, length3d, extra, drop = _flight(rise, run, n)
    proud = _head_corner(pitch, rise, rise / n, length3d, extra, drop, 0.0) - rise
    assert abs(proud - 0.1995) < 0.001, proud
    step_max = agent_contract.contract()["clearances"]["unassisted_step_max_m"]
    assert proud > step_max, (proud, step_max)


def test_the_drop_lands_the_head_on_the_landing():
    for rise in (2.8, 2.9, 3.3, 3.4, 4.0, 4.5):
        for run in (3.0, 3.8, 4.0, 5.5):
            for n in (8, 10, 12, 16):
                pitch, length3d, extra, drop = _flight(rise, run, n)
                head = S.ramp_head_drop(pitch, rise / n)
                got = _head_corner(pitch, rise, rise / n, length3d, extra,
                                   drop, head)
                assert abs(got - rise) < 1e-9, (rise, run, n, got)


def test_the_foot_stays_on_or_under_the_floor():
    for rise, run, n in ((3.3, 4.0, 16), (2.9, 3.8, 14), (4.5, 5.5, 22)):
        pitch, length3d, extra, drop = _flight(rise, run, n)
        head = S.ramp_head_drop(pitch, rise / n)
        assert _foot_surface(pitch, rise, rise / n, length3d, extra, drop,
                             head) <= 1e-9


def test_a_level_ramp_needs_no_drop():
    assert S.ramp_head_drop(0.0, 0.2) == 0.0


def test_the_builder_sinks_every_ramp():
    """deli_counter.py is Blender-bound, so it is read as source: each of the
    three ramp constructions -- a flight's, and an L-stair's two legs --
    subtracts the head drop from its centre."""
    src = open(os.path.join(HERE, "deli_counter.py"), encoding="utf-8").read()
    assert src.count("stairwell.ramp_head_drop(") == 3, src.count("stairwell.ramp_head_drop(")
    assert "- _drop - _head)" in src
'''


def main():
    assert not TEST.exists(), TEST
    TEST.write_bytes(BODY.encode("utf-8"))
    print("wrote", TEST.relative_to(ROOT))


if __name__ == "__main__":
    main()
