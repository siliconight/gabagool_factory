"""Deli Counter 0.221.0: a switchback's second flight stands on the floor under it (the walker's walk of cold runs
9305-9307, findings 7-9: the factory's `docs/findings/walk_2026-10-14/`; the walker's call, 2026-10-14, "fill the
stairs to the ground").

Anchored edits, each asserted exactly once and each file's sha16 pinned, nothing written until all matched:
  stairwell.py           `flight_solid_base` after `flight_solid_under`; `stair_guards` gives the second run a back
                         on the lowest storey; the SCOPE comment says the channel is filled
  deli_counter.py        `_stairs` stands each tread's column and collider on `flight_solid_base`'s floor
  test_stair_back.py     the two tests that pinned 0.134.0's walkway change with it; the docstring says why
  test_stair_fill_to_ground.py   NEW (`dc_fill_to_ground/test_stair_fill_to_ground.py.txt`)
CHANGELOG and VERSION from `dc_fill_to_ground/CHANGELOG_0.221.0.md`; `--results-pending` leaves RESULT_ keys to
`--fill`. The shells are built after (`build.py --all`, since `stairwell.py` and `deli_counter.py` move).

Read before it was written, in this session: `stairwell.py` -- `flight_rect`, `flight_run_lateral`,
`flight_solid_end`, `flight_solid_rect`, `single_run`, `hole_span` (471-605), `stair_guards` from its docstring
through its filters (755-1113), `slab_openings` (1293-1320) and `flight_solid_under` (1987-2003);
`deli_counter.py`'s `_stair_guards` and `_stairs` (1832-2105); `test_stair_underside.py` whole and
`test_stair_back.py` (1-120, 228-387); `spec_types` `SlabHole`, `LevelSpec.story_height` / `has_basement` /
`slab_holes`; docs/COMMANDS.md on Deli Counter (prove before `build.py --all`; the freshness hook). Every file LF.

For every leg on its own storey the builder's new expressions reduce to 0.220.0's floats exactly: `z - base_z` is
0.0 there, `0.0 + x` is `x`, and the collider's `under > 1e-9` is `i >= 1`.

    python patches/patch_dc_fill_to_ground.py --results-pending
    (python -m pytest -q in deli_counter; then python build.py --all --blender C:/blender/blender.exe)
    python patches/patch_dc_fill_to_ground.py --fill
"""
import hashlib
import os
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
DC = pathlib.Path(os.environ.get("DC_ROOT") or HERE.parent / "deli_counter")
SRC = HERE / "dc_fill_to_ground"
PENDING = "--results-pending" in sys.argv
FILL = "--fill" in sys.argv
RESULTS = {"RESULT_FAILING": "result_failing.txt", "RESULT_SUITE": "result_suite.txt",
           "RESULT_BUILD": "result_build.txt"}
VERSION_WAS, VERSION = b"Deli Counter 0.220.0", b"Deli Counter 0.221.0"
CHANGELOG_HEAD = "## [0.220.0] - a walk-up stands a fire escape on its front, a storey a slot\n"
SHA = {"stairwell.py": "27800e602d962ed1", "deli_counter.py": "e85f909cbdbf3694",
       "test_stair_back.py": "ff72cbbb352aa6a7"}
NEW = {"test_stair_fill_to_ground.py": "test_stair_fill_to_ground.py.txt"}

BASE_OLD = '''    leg = s - min(st.from_story, st.to_story)
    by_style = ((st.style == "straight" and leg == 0) or
                (st.style == "switchback" and leg < 2))
    return by_style and stair_underside(spec, st) == "solid"


def derive(spec, pieces=None):
'''
BASE_NEW = '''    leg = s - min(st.from_story, st.to_story)
    by_style = ((st.style == "straight" and leg == 0) or
                (st.style == "switchback" and leg < 2))
    return by_style and stair_underside(spec, st) == "solid"


def flight_solid_base(spec, st, s):
    """The storey whose floor the solid fill of the leg climbing storey `s`
    stands on (0.221.0). THE rule `Builder._stairs` builds and `stair_guards`
    fills beside, so the two cannot drift.

    `flight_solid_under` fills a switchback's first two legs "to that storey's
    floor", on the premise that only the first leg of each run stands on one.
    With `cut_slabs`, leg 1's own storey floor is the slab its stair cut across
    both runs (`hole_span`), so its fill hung with a level bottom a storey over
    the floor below. The walker, at cold run 9310's office: "bottom of this
    stair should come down all the way to the ground" (the factory's
    `docs/findings/walk_2026-10-14/`, findings 7-9; 17 legs in 14 library
    specs). Under leg 1's run on the stair's lowest storey nothing of the stair
    stands but the turn plates above, so leg 1 stands on that floor -- the
    walker's call of 2026-10-14, "fill the stairs to the ground", over the
    walkway 0.134.0 kept open there. Unless something else opens that floor
    under the leg's run (`slab_openings`): then it keeps its own storey rather
    than stand on a hole. Every other leg stands on its own storey, as before.
    """
    lo = min(st.from_story, st.to_story)
    if (st.style != "switchback" or single_run(st)
            or not getattr(st, "cut_slabs", True) or s - lo != 1
            or not flight_solid_under(spec, st, s)):
        return s
    x0, y0, x1, y1 = flight_solid_rect(st, spec.story_height, s)
    for a0, b0, a1, b1 in slab_openings(spec).get(lo, ()):
        if (min(x1, a1) - max(x0, a0) > 1e-6
                and min(y1, b1) - max(y0, b0) > 1e-6):
            return s
    return lo


def derive(spec, pieces=None):
'''

SCOPE_OLD = '''            #   switchback fills its leg's OWN run and leaves the other one
            #   end to end: `flight_run_lateral` says which half is which.
'''
SCOPE_NEW = '''            #   switchback fills its leg's OWN run and leaves the other one
            #   end to end: `flight_run_lateral` says which half is which.
            #
            #   FILLED 0.221.0, the walker's call (cold run 9310's office,
            #   2026-10-14, "fill the stairs to the ground"): a cut switchback's
            #   leg 1 stands on this storey's floor (`flight_solid_base`), so
            #   the channel is no passage, and the other run's stretch past
            #   leg 1's foot gets its own back below.
'''

BACK_OLD = '''                if t_b - t_a > T and b_hi - b_lo > T:
                    backs.append({"stair": sid, "story": s, "kind": "back",
                                  "axis": lateral, "pos": (t_a + t_b) / 2.0,
                                  "thick": t_b - t_a,
                                  "lo": b_lo, "hi": b_hi})
    # AFTER every side and rail, so each of those keeps its index -- and so
'''
BACK_NEW = '''                if t_b - t_a > T and b_hi - b_lo > T:
                    backs.append({"stair": sid, "story": s, "kind": "back",
                                  "axis": lateral, "pos": (t_a + t_b) / 2.0,
                                  "thick": t_b - t_a,
                                  "lo": b_lo, "hi": b_hi})
            # THE OTHER RUN'S BACK, WHERE ITS LEG STANDS ON THIS FLOOR (0.221.0).
            # Leg 1 of a cut switchback stands on the lowest storey's floor
            # (`flight_solid_base`), so the other run there is the dead end
            # this rule fills, not 0.134.0's passage: from leg 1's foot to the
            # rectangle's arrival edge -- the gap the walker looked through at
            # cold run 9310's office (walker_75) -- between the side wall's
            # inner face and the run boundary, floor to slab underside, beside
            # the leg's own back above.
            if (multi_sb and s == lo_s
                    and flight_solid_base(spec, st, s + 1) == s
                    and any(q["kind"] == "side" and q["stair"] == sid
                            and q["story"] == s for q in raw)):
                inner = 0.0 if narrow else fill
                fx0, fy0, fx1, fy1 = flight_solid_rect(st, H, s + 1)
                f_lo, f_hi = (fy0, fy1) if travel == "Y" else (fx0, fx1)
                t_a, t_b = ((f_hi + SIDE_GAP, t_hi) if arrive_hi
                            else (t_lo, f_lo - SIDE_GAP))
                r_lo, r_hi = flight_run_lateral(st, s + 1)
                if r_lo + r_hi > l_lo + l_hi:   # the next leg's run, high side
                    b_lo, b_hi = r_lo, l_hi - inner
                else:
                    b_lo, b_hi = l_lo + inner, r_hi
                if t_b - t_a > T and b_hi - b_lo > T:
                    backs.append({"stair": sid, "story": s, "kind": "back",
                                  "axis": lateral, "pos": (t_a + t_b) / 2.0,
                                  "thick": t_b - t_a,
                                  "lo": b_lo, "hi": b_hi})
    # AFTER every side and rail, so each of those keeps its index -- and so
'''

BUILD_BASE_OLD = '''                solid_under = stairwell.flight_solid_under(self.s, st, s)
'''
BUILD_BASE_NEW = '''                solid_under = stairwell.flight_solid_under(self.s, st, s)
                # AND THE FLOOR IT STANDS ON (0.221.0): a cut switchback's second
                # leg stands on the stair's lowest floor, not on the slab its own
                # stair removed (`stairwell.flight_solid_base`; the walker, cold
                # run 9310: "bottom of this stair should come down all the way to
                # the ground"). Every other leg stands on its own storey, z.
                base_z = stairwell.flight_solid_base(self.s, st, s) * H
'''

BUILD_COL_OLD = '''                        if solid_under:
                            # the tread as a column to the storey floor
                            col_h = step_h * (i + 1)
                            self._box(f"stair{si}{ch}_{s}_{i}",
                                      (wx, wy, z + col_h / 2),
                                      self._stair_sz(st, st.width, step_d,
                                                     col_h),
                                      self.VISUAL, role="stair")
                            # and solid to a body, but stopping ONE RISER
                            # below the tread, so the smooth ramp riding the
                            # nosings is still the only surface a foot meets
                            if i >= 1:
                                self._col_box(
                                    f"stair{si}{ch}col_under_{s}_{i}",
                                    (wx, wy, z + step_h * i / 2),
                                    self._stair_sz(st, st.width, step_d,
                                                   step_h * i))
'''
BUILD_COL_NEW = '''                        if solid_under:
                            # the tread as a column to the floor it stands on
                            col_h = (z - base_z) + step_h * (i + 1)
                            self._box(f"stair{si}{ch}_{s}_{i}",
                                      (wx, wy, base_z + col_h / 2),
                                      self._stair_sz(st, st.width, step_d,
                                                     col_h),
                                      self.VISUAL, role="stair")
                            # and solid to a body, but stopping ONE RISER
                            # below the tread, so the smooth ramp riding the
                            # nosings is still the only surface a foot meets
                            under = (z - base_z) + step_h * i
                            if under > 1e-9:
                                self._col_box(
                                    f"stair{si}{ch}col_under_{s}_{i}",
                                    (wx, wy, base_z + under / 2),
                                    self._stair_sz(st, st.width, step_d,
                                                   under))
'''

DOC_OLD = '''a leg that ends in a TURN LANDING is a step deeper than `run / 2` says,
because that leg is built one tread shorter.
"""
'''
DOC_NEW = '''a leg that ends in a TURN LANDING is a step deeper than `run / 2` says,
because that leg is built one tread shorter.

0.221.0 -- THE WALKWAY FILLED. The walker, cold run 9310's office (the
factory's `docs/findings/walk_2026-10-14/`): the second flight's fill hung a
storey over the walkway, whose north mouth was "a big gap", and asked, chose
"fill the stairs to the ground". A cut switchback's leg 1 now stands on the
lowest storey's floor (`flight_solid_base`) and the walkway's mouth gets a
back, so the two tests below that pinned the walkway change with it.
"""
'''

OWN_RUN_OLD = '''def test_the_walkers_stair_gets_a_back_in_its_own_run_only():
    """`office_stepped`, cold run 9060. Leg 0 climbs storey 0 in the run
    x 0.000..1.600 and its top tread ends at y 2.089; the slot behind it runs
    to the rectangle's arrival edge at y 3.150 and out to the east side wall's
    inner face at x 1.605. The run at x -1.600..0.000 is the walkway and keeps
    every metre of it."""
    sp = _load("office_stepped")
    st = sp.stairs[0]
    backs = [p for p in S.stair_guards(sp) if p["kind"] == "back"]
    assert [p["story"] for p in backs] == [0], backs
    b = backs[0]
'''
OWN_RUN_NEW = '''def test_the_walkers_stair_gets_a_back_in_each_run():
    """`office_stepped`, cold run 9060. Leg 0 climbs storey 0 in the run
    x 0.000..1.600 and its top tread ends at y 2.089; the slot behind it runs
    to the rectangle's arrival edge at y 3.150 and out to the east side wall's
    inner face at x 1.605. Until 0.221.0 the run at x -1.600..0.000 was the
    walkway and kept every metre of it; since, leg 1 stands on storey 0's floor
    (`flight_solid_base`), and the stretch from its foot at y 2.350 to the
    arrival edge is filled too, out to the west side wall's inner face."""
    sp = _load("office_stepped")
    st = sp.stairs[0]
    backs = sorted((p for p in S.stair_guards(sp) if p["kind"] == "back"),
                   key=lambda p: p["lo"])
    assert [p["story"] for p in backs] == [0, 0], backs
    west, b = backs
    wx0, wy0, wx1, wy1 = _rect(west)
    assert abs(wx0 - -1.605) < 1e-9 and abs(wx1 - 0.0) < 1e-9, west
    assert abs(wy0 - (st.y + st.run / 2.0 + S.SIDE_GAP)) < 1e-9, west
    assert abs(wy1 - 3.15) < 1e-9, west
'''

WALKWAY_OLD = '''def test_the_walkway_under_the_next_leg_keeps_both_its_mouths():
    """The run the NEXT leg flies over carries no fill on any storey, in any
    multi-storey switchback in the library -- that is the channel 0.134.0
    protected and the reason this rule is per-run and not per-rectangle."""
    n = 0
    for path in _library_specs():
        sp = spec_loader.load_spec(path)
        guards = S.stair_guards(sp)
        for i, st in enumerate(sp.stairs or ()):
            if st.style != "switchback" or S.single_run(st):
                continue
            sid = S.stair_ident(st, i)
            lo = min(st.from_story, st.to_story)
            hi = max(st.from_story, st.to_story)
            for s in range(lo, hi):
                n += 1
                _own, other = _runs(st, s)
                for b in [p for p in guards if p["stair"] == sid
                          and p["story"] == s and p["kind"] == "back"]:
                    assert min(b["hi"], other[1]) - max(b["lo"], other[0]) \\
                        < 1e-9, (path, sid, s, b, other)
    assert n == 41, n
'''
WALKWAY_NEW = (SRC / "test_walkway_filled.txt").read_text(encoding="utf-8") if (SRC / "test_walkway_filled.txt").exists() else None

EDITS = {
    "stairwell.py": [(BASE_OLD, BASE_NEW), (SCOPE_OLD, SCOPE_NEW), (BACK_OLD, BACK_NEW)],
    "deli_counter.py": [(BUILD_BASE_OLD, BUILD_BASE_NEW), (BUILD_COL_OLD, BUILD_COL_NEW)],
    "test_stair_back.py": [(DOC_OLD, DOC_NEW), (OWN_RUN_OLD, OWN_RUN_NEW), (WALKWAY_OLD, WALKWAY_NEW)],
}


def _eol(raw, rel):
    crlf = raw.count(b"\r\n")
    lf = raw.count(b"\n")
    assert crlf in (0, lf), (rel, "mixed line endings", crlf, lf)
    return b"\r\n" if crlf else b"\n"


def fill():
    assert (DC / "VERSION").read_bytes().strip() == VERSION, (DC / "VERSION").read_bytes()
    results = {}
    for key, name in RESULTS.items():
        value = (SRC / name).read_text(encoding="utf-8").strip()
        assert value and "RESULT_" not in value and not value.endswith("."), (name, value[-40:])
        results[key] = value
    writes = {}
    for path, rel in [(DC / "CHANGELOG.md", "CHANGELOG.md"), (SRC / "CHANGELOG_0.221.0.md", "the entry")]:
        raw = path.read_bytes()
        eol = _eol(raw, rel)
        text = raw.decode("utf-8").replace("\r\n", "\n")
        for key, value in results.items():
            assert text.count(key) == 1, (rel, key, text.count(key))
            text = text.replace(key, value)
        writes[path] = text.encode("utf-8").replace(b"\n", eol)
    for path, data in writes.items():
        path.write_bytes(data)
    print("Deli Counter 0.221.0: results filled")


def main():
    if FILL:
        return fill()
    assert WALKWAY_NEW is not None, "dc_fill_to_ground/test_walkway_filled.txt is not written yet"
    vraw = (DC / "VERSION").read_bytes()
    assert vraw.strip() == VERSION_WAS, vraw
    entry = (SRC / "CHANGELOG_0.221.0.md").read_bytes().decode("utf-8").replace("\r\n", "\n")
    assert entry.startswith("## [0.221.0] - "), entry[:40]
    left = entry
    for key in RESULTS if PENDING else ():
        left = left.replace(key, "")
    assert "RESULT_" not in left, "the changelog still carries an unfilled result"
    writes = {}
    for rel in SHA:
        p = DC / rel
        raw = p.read_bytes()
        got = hashlib.sha256(raw.replace(b"\r\n", b"\n")).hexdigest()[:16]
        assert got == SHA[rel], (rel, "is not the file this patch read", got)
        eol = _eol(raw, rel)
        text = raw.decode("utf-8").replace("\r\n", "\n")
        for old, new in EDITS[rel]:
            assert text.count(old) == 1, (rel, "anchor", text.count(old), old[:80])
            text = text.replace(old, new)
        writes[p] = text.encode("utf-8").replace(b"\n", eol)
    for rel, name in NEW.items():
        p = DC / rel
        assert not p.exists(), (rel, "already exists")
        writes[p] = (SRC / name).read_bytes().replace(b"\r\n", b"\n")
    cl = DC / "CHANGELOG.md"
    cl_raw = cl.read_bytes()
    cl_eol = _eol(cl_raw, "CHANGELOG.md")
    cl_text = cl_raw.decode("utf-8").replace("\r\n", "\n")
    assert cl_text.startswith(CHANGELOG_HEAD), cl_text[:120]
    for p, data in writes.items():
        p.write_bytes(data)
    cl.write_bytes((entry.rstrip("\n") + "\n\n" + cl_text).encode("utf-8").replace(b"\n", cl_eol))
    (DC / "VERSION").write_bytes(vraw.replace(VERSION_WAS, VERSION))
    print("Deli Counter 0.220.0 -> 0.221.0")


if __name__ == "__main__":
    main()
