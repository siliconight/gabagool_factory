"""Land the stair ramp on the floor it starts from.

`deli_counter.py` builds a flight's collision as one smooth incline rather than
a box per step, and the comment above it says exactly why:

    Boxy per-step colliders catch a CharacterBody3D on every riser (you stick /
    have to jump); a flush incline at the flight's pitch lets any controller
    walk straight up with no step logic. Visual stays stepped. Sat half a step
    proud so its surface rides the step nosings.

That is right, and along the run it works. The problem is the last clause. The
slab is raised `step_h / 2` so its surface rides the nosings, so at the FOOT of
the flight its surface begins that far above the floor it is supposed to meet --
plus half the slab's own 0.25 thickness, measured vertically through the tilt:

    lead = step_h / 2 + (thickness / 2) / cos(pitch)

For a 3.40 m rise over a 4.16 m run at ten steps that is 0.33 m. Measured on
walkup_siege the floor jumps 0.492 m in 0.018 m of travel at this exact spot,
and the walktest walker parks against it with a HORIZONTAL contact normal. A
capsule walks up radius * (1 - cos(floor_max_angle)) = 0.146 unassisted. So the
fix for "you stick on every riser" built one riser, at the first step, and it
is four times too tall to walk up.

It survived because nothing tests it. There are eight stair test modules in this
repo and not one of them mentions the ramp collider.

THE FIX. Extend the ramp downhill until its top surface reaches floor level at
the foot, and shift its centre by half that so the HEAD of the flight does not
move -- the top must still meet the landing exactly. Along the incline:

    extra = lead / sin(pitch)          # lengthen by this
    back  = extra / 2 * cos(pitch)     # move the centre this far downhill
    drop  = extra / 2 * sin(pitch)     # and this far down

The wedge this adds below the old start is buried in the slab; what surfaces
above the floor is the ramp at its own pitch, which is what a stair's bottom
nosing does in the first place.

Three emission sites share the defect: the straight/switchback/scissor flight,
and both legs of an L. Leg B starts from the corner landing rather than a floor
slab, so its riser is off the landing -- same geometry, same fix.

Containment is unaffected: `containment_findings` is a spec-level check against
`st.run` and lateral partitions, and the N/S mouths are explicitly never
required to be guarded (test_stair_containment.py). This changes emitted
geometry, not the spec.

The math lands in `stairwell.py` because it imports only `math` and `tactical`,
so the new test can import it without Blender -- `deli_counter.py` does
`import bpy` at module scope and cannot be tested directly.

Asserts every target before writing, and is idempotent.
"""
import pathlib
import py_compile

ROOT = pathlib.Path(r"C:\Projects\gabagool_studios\gabagool_factory")
DC = ROOT / "deli_counter" / "deli_counter.py"
SW = ROOT / "deli_counter" / "stairwell.py"
TEST = ROOT / "deli_counter" / "test_stair_ramp_foot.py"

HELPER = '''

def ramp_foot_extension(pitch_rad, step_rise, thickness=0.25):
    """How far a stair's collision ramp must extend past the foot of its run.

    The ramp is set half a step proud of the flight so its surface rides the
    step nosings. That is correct along the run and wrong where the run meets
    the floor: the surface starts `step_rise / 2` above it, plus half the
    slab's own thickness measured vertically through the tilt. The result is a
    riser at the first step -- the exact thing a smooth ramp exists to remove.

    A capsule only walks up `radius * (1 - cos(floor_max_angle))`, which is
    0.146 m for the contract body. Anything taller needs step-up code the
    shipped level cannot assume, so the ramp has to reach the floor rather
    than hover above it.

    Returns `(extra_length, back, drop)`: lengthen the ramp by `extra_length`
    along its own incline, move its centre `back` downhill in plan and `drop`
    downward, and the HEAD of the flight stays exactly where it was.
    """
    if pitch_rad <= 0.0:
        return 0.0, 0.0, 0.0
    lead = step_rise / 2.0 + (thickness / 2.0) / math.cos(pitch_rad)
    extra = lead / math.sin(pitch_rad)
    return extra, extra / 2.0 * math.cos(pitch_rad), extra / 2.0 * math.sin(pitch_rad)
'''

# --- the three emission sites ------------------------------------------------

OLD_1 = '''                    wx, wy = self._stair_pt(st, sx, st.y)
                    ramp = self._box(
                        f"stair{si}{ch}ramp_{s}" + self.col_suffix["convex"],
                        (wx, wy, z + H / 2 + step_h / 2),
                        self._stair_sz(st, st.width, length3d, 0.25),
                        self.COLLISION)
                    ramp.rotation_euler = self._stair_tilt(st, sign, angle)
'''

NEW_1 = '''                    # reach the floor at the foot: the half-step proud offset
                    # that makes the surface ride the nosings also starts it
                    # that far ABOVE the slab, which is a riser no capsule
                    # walks up. Extending downhill lands it; shifting the
                    # centre by half leaves the head of the flight untouched.
                    _ext, _back, _drop = stairwell.ramp_foot_extension(
                        angle, step_h)
                    wx, wy = self._stair_pt(st, sx, st.y - sign * _back)
                    ramp = self._box(
                        f"stair{si}{ch}ramp_{s}" + self.col_suffix["convex"],
                        (wx, wy, z + H / 2 + step_h / 2 - _drop),
                        self._stair_sz(st, st.width, length3d + _ext, 0.25),
                        self.COLLISION)
                    ramp.rotation_euler = self._stair_tilt(st, sign, angle)
'''

OLD_2 = '''            wx, wy = self._stair_pt(st, st.x, st.y)
            ramp = self._box(f"stair{si}aramp_{s}" + self.col_suffix["convex"],
                             (wx, wy, z + riseA / 2 + step_h / 2),
                             self._stair_sz(st, w, lenA, 0.25), self.COLLISION)
            ramp.rotation_euler = self._stair_tilt(st, 1, angA)
'''

NEW_2 = '''            _extA, _backA, _dropA = stairwell.ramp_foot_extension(angA, step_h)
            wx, wy = self._stair_pt(st, st.x, st.y - _backA)
            ramp = self._box(f"stair{si}aramp_{s}" + self.col_suffix["convex"],
                             (wx, wy, z + riseA / 2 + step_h / 2 - _dropA),
                             self._stair_sz(st, w, lenA + _extA, 0.25),
                             self.COLLISION)
            ramp.rotation_euler = self._stair_tilt(st, 1, angA)
'''

OLD_3 = '''            wx, wy = self._stair_pt(st, st.x + w / 2 + st.run / 2, yB)
            ramp = self._box(f"stair{si}bramp_{s}" + self.col_suffix["convex"],
                             (wx, wy, z + riseA + riseB / 2 + step_h / 2),
                             self._stair_sz(st, lenB, w, 0.25), self.COLLISION)
            ramp.rotation_euler = self._stair_tilt_x(st, angB)
'''

NEW_3 = '''            # leg B leaves the corner landing rather than a floor slab, but
            # the riser is the same one and so is the remedy
            _extB, _backB, _dropB = stairwell.ramp_foot_extension(angB, step_h)
            wx, wy = self._stair_pt(
                st, st.x + w / 2 + st.run / 2 - _backB, yB)
            ramp = self._box(f"stair{si}bramp_{s}" + self.col_suffix["convex"],
                             (wx, wy, z + riseA + riseB / 2 + step_h / 2
                              - _dropB),
                             self._stair_sz(st, lenB + _extB, w, 0.25),
                             self.COLLISION)
            ramp.rotation_euler = self._stair_tilt_x(st, angB)
'''

IMPORT_ANCHOR = "import ladder_geom\n"
IMPORT_NEW = "import ladder_geom\nimport stairwell\n"

TEST_SRC = '''"""Pure tests for the stair ramp reaching the floor (no bpy).

deli_counter.py builds a flight's collision as one smooth incline set half a
step proud so its surface rides the step nosings. Correct along the run; at the
foot it means the surface starts above the floor it is supposed to meet, and
that gap is a riser. Measured on walkup_siege at 0.492 m against a capsule that
walks up 0.146 -- the walker parks against it with a horizontal contact normal
and the site fails its walktest.

Eight stair test modules existed and none of them mentioned the ramp collider,
which is why the defect shipped. Run: python3 test_stair_ramp_foot.py
"""
import math

import stairwell as S

THICK = 0.25


def _run(fn):
    fn()
    print(f"[ok] {fn.__name__}")


def _foot_height(pitch, rise, step_rise, length3d, extra, drop, thickness=THICK):
    """Top surface of the ramp at its lower end, relative to the flight base.

    Mirrors deli_counter.py's own placement: the slab's centre sits
    `rise/2 + step_rise/2 - drop` above the base plane, and its lower end is
    half the (extended) length downhill of that. The walkable surface is half
    the thickness above the mid-plane, measured VERTICALLY through the tilt.

    The `rise/2` term is not optional. Leaving it out cancels wrongly and the
    helper reports `-rise/2` for a ramp that lands perfectly -- which is what
    it did on first run, and is why this docstring names it."""
    centre = rise / 2.0 + step_rise / 2.0 - drop
    mid_at_foot = centre - (length3d + extra) / 2.0 * math.sin(pitch)
    return mid_at_foot + (thickness / 2.0) / math.cos(pitch)


# --- the defect, stated as the number it produced ----------------------------

def test_unextended_ramp_hovers_above_the_floor():
    """What shipped: no extension, and the surface starts a third of a metre up."""
    rise, run, n = 3.40, 4.16, 10
    pitch = math.atan2(rise, run)
    length3d = math.hypot(run, rise)
    hover = _foot_height(pitch, rise, rise / n, length3d, 0.0, 0.0)
    assert hover > 0.3, hover
    assert hover > 0.146, "this is the whole point: a capsule cannot walk it"


def test_extension_lands_the_surface_on_the_floor():
    rise, run, n = 3.40, 4.16, 10
    pitch = math.atan2(rise, run)
    length3d = math.hypot(run, rise)
    extra, back, drop = S.ramp_foot_extension(pitch, rise / n)
    assert abs(_foot_height(pitch, rise, rise / n, length3d, extra,
                              drop)) < 1e-9


def test_it_lands_across_every_plausible_flight():
    for rise in (2.8, 3.2, 3.4, 4.0):
        for run in (3.0, 4.16, 5.5):
            for n in (8, 10, 12, 16):
                pitch = math.atan2(rise, run)
                length3d = math.hypot(run, rise)
                extra, back, drop = S.ramp_foot_extension(pitch, rise / n)
                got = _foot_height(pitch, rise, rise / n, length3d,
                                   extra, drop)
                assert abs(got) < 1e-9, (rise, run, n, got)


# --- what must NOT move ------------------------------------------------------

def test_the_head_of_the_flight_does_not_move():
    """The top has to keep meeting the landing. Extending downhill and shifting
    the centre by half the extension leaves the upper end exactly where it was."""
    for rise, run, n in ((3.4, 4.16, 10), (2.8, 3.0, 8), (4.0, 5.5, 16)):
        pitch = math.atan2(rise, run)
        length3d = math.hypot(run, rise)
        extra, back, drop = S.ramp_foot_extension(pitch, rise / n)
        head_before = length3d / 2.0 * math.sin(pitch)
        head_after = -drop + (length3d + extra) / 2.0 * math.sin(pitch)
        assert abs(head_after - head_before) < 1e-9, (rise, run, n)


def test_the_plan_shift_matches_the_drop_at_the_pitch():
    pitch = math.atan2(3.4, 4.16)
    extra, back, drop = S.ramp_foot_extension(pitch, 0.34)
    assert abs(back - extra / 2.0 * math.cos(pitch)) < 1e-12
    assert abs(drop - extra / 2.0 * math.sin(pitch)) < 1e-12
    assert abs(math.hypot(back, drop) - extra / 2.0) < 1e-12


def test_a_steeper_flight_needs_less_extension():
    """Steeper means the surface loses height faster, so it reaches the floor
    sooner. A check that moved the other way would be measuring nothing."""
    shallow = S.ramp_foot_extension(math.radians(30), 0.34)[0]
    steep = S.ramp_foot_extension(math.radians(50), 0.34)[0]
    assert steep < shallow


def test_a_flat_flight_is_not_divided_by_zero():
    assert S.ramp_foot_extension(0.0, 0.34) == (0.0, 0.0, 0.0)


ALL = [v for k, v in sorted(globals().items()) if k.startswith("test_")]

if __name__ == "__main__":
    for fn in ALL:
        _run(fn)
    print(f"\\n{len(ALL)} ramp-foot tests passed.")
'''


def main() -> int:
    sw = SW.read_text(encoding="utf-8")
    if "ramp_foot_extension" in sw:
        print("stairwell.py: already has ramp_foot_extension")
    else:
        if "\nimport math\n" not in sw:
            raise SystemExit("stairwell.py does not import math. Nothing written.")
        SW.write_text(sw.rstrip("\n") + "\n" + HELPER, encoding="utf-8")
        py_compile.compile(str(SW), doraise=True)
        print("stairwell.py: + ramp_foot_extension(), and it compiles")

    dc = DC.read_text(encoding="utf-8")
    if "ramp_foot_extension" in dc:
        print("deli_counter.py: already patched")
    else:
        for label, old in (("straight/switchback/scissor", OLD_1),
                           ("L leg A", OLD_2), ("L leg B", OLD_3)):
            if dc.count(old) != 1:
                raise SystemExit(
                    f"deli_counter.py: the {label} ramp block appears "
                    f"{dc.count(old)} time(s), expected exactly 1. Nothing "
                    f"written -- read the file and re-aim this patch.")
        if dc.count(IMPORT_ANCHOR) != 1:
            raise SystemExit("deli_counter.py: cannot find the import anchor. "
                             "Nothing written.")
        dc = dc.replace(IMPORT_ANCHOR, IMPORT_NEW)
        dc = dc.replace(OLD_1, NEW_1).replace(OLD_2, NEW_2).replace(OLD_3, NEW_3)
        DC.write_text(dc, encoding="utf-8")
        py_compile.compile(str(DC), doraise=True)
        print("deli_counter.py: 3 ramp sites land on their floor, and it compiles")

    if TEST.exists():
        print(f"{TEST.name}: already there")
    else:
        TEST.write_text(TEST_SRC, encoding="utf-8")
        print(f"{TEST.name}: written")

    print("\n=========== what the flight looked like before and after ===========")
    import math
    import subprocess
    import sys
    for rise, run, n in ((3.40, 4.16, 10), (3.20, 4.00, 12), (2.80, 3.00, 8)):
        pitch = math.atan2(rise, run)
        step_h = rise / n
        lead = step_h / 2.0 + (0.25 / 2.0) / math.cos(pitch)
        extra = lead / math.sin(pitch)
        print(f"  rise {rise:.2f} run {run:.2f} n={n:>2}  pitch "
              f"{math.degrees(pitch):.1f} deg   riser was {lead:.3f} m "
              f"-> ramp extends {extra:.3f} m downhill, riser 0.000")
    print("\n  a capsule walks up 0.146; every 'was' above is a wall")

    print("\n=========== the new tests ===========")
    r = subprocess.run([sys.executable, str(TEST)], capture_output=True,
                       text=True, cwd=str(DC.parent))
    print((r.stdout or "").rstrip())
    if r.returncode != 0:
        print((r.stderr or "").rstrip()[-1200:])
    return r.returncode


if __name__ == "__main__":
    raise SystemExit(main())
