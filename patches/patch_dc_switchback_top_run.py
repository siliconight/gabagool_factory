"""Deli Counter 0.225.0: a multi-storey switchback's top leg cuts only its own run, and its seam is guarded.

Cold run 9317's office, read by the drop-edge instrument (roadmap 173, docs/findings/drop_edges_173/): the
stair's top leg arrives at storey 2 in the west run; the east run holds leg 0, which tops out a storey below,
and the slab cut at storey 2 spanned both runs -- so the east half of the cut was a pit 6.67 m deep onto leg
0's foot, open on three edges: the discharge plate's edge over the east run, the east rail's sideways opening,
and the seam between the runs along the whole of leg 1 (12 unguarded edges, 1.3-6.67 m). `single_run` already
stops a one-leg switchback cutting the run it does not use (cold run 9050); this is that rule one storey up.

What it changes (anchored; refuses on a miss; CRLF-safe), each after-text copied byte for byte from the tree
that shipped (this file was regenerated from it by the session's gen_patch_dc_0225.py and proven in a worktree
of 0.224.1):
  * stairwell.hole_span(st, s=None) -- per leg: the top leg of a multi-storey switchback is its own run plus
    its outer margin, meeting the other run at the seam with no margin. flight_rect and the builder's _stairs
    (the cut and the discharge plate) pass `s`; intermediate legs and turn landings keep both runs.
  * stairwell._seam_pieces + stair_guards -- on the top leg's seam side: a thin side wall (GUARD_THICK at
    SIDE_GAP from the treads) from the rectangle's far end to the turn landing, no sideways opening, its
    UNDERSIDE a body's height above the floor (`z_lo`); the rail above stands at the seam on the slab that now
    covers the other run. The underside is the nav gate's measurement on cbp_town_finale_midbalanced (see the
    CHANGELOG entry): a floor-level bottom cut the lower flight, a stepped one did not help, a lifted one passed.
  * deli_counter._stair_guards honours `z_lo`: the box's bottom lifts, its top stays at the slab underside.
  * test_switchback_top_run.py, VERSION 0.225.0, CHANGELOG.

    python patches/patch_dc_switchback_top_run.py --tests   # the test file only (prove it fails first)
    python patches/patch_dc_switchback_top_run.py           # everything
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
DC = ROOT / "deli_counter"


def _apply(path, old, new, count=1):
    raw = path.read_bytes()
    crlf = raw.count(b"\r\n")
    lf = raw.count(b"\n") - crlf
    assert crlf == 0 or lf == 0, f"{path.name}: mixed endings ({crlf} CRLF, {lf} LF)"
    eol = "\r\n" if crlf else "\n"
    text = raw.decode("utf-8")
    o, n = old.replace("\n", eol), new.replace("\n", eol)
    assert text.count(o) == count, f"{path.name}: anchor found {text.count(o)} times, wanted {count}: {old[:70]!r}"
    path.write_bytes(text.replace(o, n).encode("utf-8"))


HOLE_SPAN_OLD = '''def hole_span(st):
    """``(local centre x, width)`` of a straight / switchback / scissor stair's
    slab cut across its runs, in the stair's own unrotated frame. THE single
    source for the builder's `_stairs` and for `flight_rect`."""
    clear = 0.8
    x_off = 0.0 if st.style == "straight" else st.width / 2
    if single_run(st):
        return st.x + x_off, st.width + clear
    return st.x, st.width + 2 * x_off + clear
'''

HOLE_SPAN_NEW = '''def hole_span(st, s=None):
    """``(local centre x, width)`` of a straight / switchback / scissor stair's
    slab cut across its runs, in the stair's own unrotated frame. THE single
    source for the builder's `_stairs` and for `flight_rect`.

    PER LEG when `s` is given: THE TOP LEG OF A MULTI-STOREY SWITCHBACK CUTS
    ONLY ITS OWN RUN. Cold run 9317's office, read by the drop-edge instrument
    (the factory's docs/findings/drop_edges_173/): leg 1 arrives at storey 2 in
    the west run; the east run holds leg 0, which tops out a storey below, and
    the cut at storey 2 spanned both runs -- so the east half of it was a pit
    6.67 m deep onto leg 0's foot, open on three edges (the discharge plate's
    edge over the east run, the east rail's sideways opening, the seam between
    the runs along the whole of leg 1): 12 unguarded edges, 1.3-6.67 m. The
    run keeps its outer margin (`clear / 2`) and meets the other run at the
    seam with none, so the slab covers the other run to the flight's edge and
    `stair_guards` stands a rail at the seam on it. `single_run` is this rule
    for a one-leg switchback (cold run 9050); this is the same rule a storey
    up. Intermediate legs keep both runs: their turn landings bridge them.
    """
    clear = 0.8
    x_off = 0.0 if st.style == "straight" else st.width / 2
    if single_run(st):
        return st.x + x_off, st.width + clear
    if (s is not None and st.style == "switchback"
            and s == max(st.from_story, st.to_story) - 1):
        lo = min(st.from_story, st.to_story)
        sign = 1 if ((s - lo) % 2 == 0) else -1
        half = st.width + clear / 2.0
        return st.x + sign * half / 2.0, half
    return st.x, st.width + 2 * x_off + clear
'''

FLIGHT_RECT_OLD = '''    hole_cx, hole_w = hole_span(st)
'''
FLIGHT_RECT_NEW = '''    hole_cx, hole_w = hole_span(st, s)
'''

HELPER_ANCHOR = '''RAIL_OPEN_MIN = 1.4


def stair_guards(spec):'''

HELPER_NEW = '''RAIL_OPEN_MIN = 1.4


def _seam_pieces(st, H, s, sid, travel, pos, span):
    """The seam wall of a multi-storey switchback's top leg: ONE box, its
    underside a body's height above the storey's floor.

    The seam between the two runs has no margin, so a wall there stands over
    the lower run's edge, and the lower flight passes under it. Measured on
    `cbp_town_finale_midbalanced` (0.225.0), one shell of 157 and the only one
    with a volume leaning over the run from the other side: with the wall's
    bottom at the storey's floor the nav bake lost the lower flight 2.25 m up
    (its lower and upper endpoints on islands of 101 and 612 polygons), and
    with the bottom lifted a metre it connected again; the mirror stair, with
    nothing leaning on it, passed either way. REFUTED on the same shell: an
    underside stepped along the flight below at a body's height plus a riser
    over it, rising only from 4 m along -- same cut, same 101 polygons, so the
    bake's objection is not the headroom model that stepping assumed. The
    rule shipped is the one that measured clean, derived rather than one
    metre: the bottom at the floor plus `agent_contract.body_height` (the
    bake's agent height), so the flight below keeps a body's headroom under
    the wall all the way to the turn landing, where its surface is a riser
    under the floor. The body ON the top leg is still held: the gap under the
    wall is a body's height minus the leg's own rise, less than a body from
    the first riser on, and at the very foot it is a doorway onto the lower
    flight's top step, a step a review reads as a step."""
    z_lo = s * H + agent_contract.body_height()
    return [{"stair": sid, "story": s, "kind": "side", "axis": travel,
             "pos": pos, "lo": span[0], "hi": span[1], "z_lo": round(z_lo, 4)}]


def stair_guards(spec):'''

GUARDS_OLD = '''            narrow = st.width < agent_contract.min_corridor_width() - 1e-9
            fill = SIDE_MARGIN - SIDE_GAP
            for side, rect_edge in ((-1, l_lo), (+1, l_hi)):
                pos_rail = rect_edge + side * T / 2.0
                pos_side = (pos_rail if narrow
                            else rect_edge - side * fill / 2.0)
                if solid and side_span[1] - side_span[0] > T:
                    piece = {"stair": sid, "story": s, "kind": "side",
                             "axis": travel, "pos": pos_side,
                             "lo": side_span[0], "hi": side_span[1]}
                    if not narrow:
                        piece["thick"] = fill
                    raw.append(piece)
                if rail_span[1] - rail_span[0] > T:
                    raw.append({"stair": sid, "story": s + 1, "kind": "rail",
                                "axis": travel, "pos": pos_rail,
                                "lo": rail_span[0], "hi": rail_span[1]})
'''

GUARDS_NEW = '''            narrow = st.width < agent_contract.min_corridor_width() - 1e-9
            fill = SIDE_MARGIN - SIDE_GAP
            # THE TOP LEG OF A MULTI-STOREY SWITCHBACK HAS A SEAM, NOT A
            # MARGIN, on the side toward the other run: its rectangle is one
            # run wide there (`hole_span`), so the rectangle's edge IS the
            # flight's edge. The guard there is thin, SIDE_GAP off the treads
            # like a narrow flight's; the side wall runs from the rectangle's
            # far end to the turn landing the leg departs from, with no
            # sideways opening -- the only thing beside it is the other run's
            # air, and a body on this leg stood 1.3-5.9 m over the leg below
            # along its whole length (cold run 9317's office, seven unguarded
            # edges). The rail above it stands on the slab that now covers the
            # other run, with the usual opening at the arrival end, which is
            # over this leg's own top treads and its plate.
            top_leg = (st.style == "switchback" and not single_run(st)
                       and s == hi_s - 1)
            r_lo, r_hi = flight_run_lateral(st, s)
            land_t = None
            if top_leg:
                prev_end = flight_solid_end(st, H, s - 1)
                land_t = prev_end[1] if travel == "Y" else prev_end[0]
            for side, rect_edge in ((-1, l_lo), (+1, l_hi)):
                seam = top_leg and abs(
                    rect_edge - (r_lo if side < 0 else r_hi)) < 1e-6
                pos_rail = rect_edge + side * (
                    (SIDE_GAP + T / 2.0) if seam else T / 2.0)
                pos_side = (pos_rail if (narrow or seam)
                            else rect_edge - side * fill / 2.0)
                s_span = side_span
                if seam:
                    s_span = ((land_t + SIDE_GAP, t_hi) if arrive_hi
                              else (t_lo, land_t - SIDE_GAP))
                if solid and seam and s_span[1] - s_span[0] > T:
                    raw += _seam_pieces(st, H, s, sid, travel, pos_side,
                                        s_span)
                elif solid and s_span[1] - s_span[0] > T:
                    piece = {"stair": sid, "story": s, "kind": "side",
                             "axis": travel, "pos": pos_side,
                             "lo": s_span[0], "hi": s_span[1]}
                    if not narrow:
                        piece["thick"] = fill
                    raw.append(piece)
                if rail_span[1] - rail_span[0] > T:
                    raw.append({"stair": sid, "story": s + 1, "kind": "rail",
                                "axis": travel, "pos": pos_rail,
                                "lo": rail_span[0], "hi": rail_span[1]})
'''

BUILDER_OLD = '''                # ONE SOURCE for the cut's width and centre: a single-storey
                # switchback cuts only the run its one leg climbs in
                # (`stairwell.hole_span`; cold run 9050's open unused run).
                hole_cx, hole_w = stairwell.hole_span(st)
'''

BUILDER_NEW = '''                # ONE SOURCE for the cut's width and centre: a single-storey
                # switchback cuts only the run its one leg climbs in
                # (`stairwell.hole_span`; cold run 9050's open unused run), and
                # so does the top leg of a multi-storey one (0.225.0: cold run
                # 9317's office, the other run's half of the cut a 6.67 m pit).
                hole_cx, hole_w = stairwell.hole_span(st, s)
'''

Z_OLD = '''            z0 = g["story"] * H
            # a `back` fills the slot behind a flight, flush with the side
            # walls either side of it: same height, same wall material
            if g["kind"] in ("side", "back"):
                h = H - self._cap_thick(g["story"], top)
                mat = None
            else:
                h = stairwell.GUARD_HEIGHT
                mat = "wood" if "wood" in have else None
'''

Z_NEW = '''            z0 = g["story"] * H
            # a `back` fills the slot behind a flight, flush with the side
            # walls either side of it: same height, same wall material
            if g["kind"] in ("side", "back"):
                h = H - self._cap_thick(g["story"], top)
                mat = None
            else:
                h = stairwell.GUARD_HEIGHT
                mat = "wood" if "wood" in have else None
            # A SEAM PIECE'S UNDERSIDE FOLLOWS THE FLIGHT BELOW (0.225.0):
            # `z_lo` lifts the box's bottom off the storey floor and the top
            # stays at the slab underside (`stairwell._seam_pieces`).
            if "z_lo" in g:
                lift = max(0.0, float(g["z_lo"]) - z0)
                z0 += lift
                h -= lift
                if h <= T:
                    continue
'''

TEST = '''"""A multi-storey switchback's top leg cuts only its own run, and its seam is guarded (0.225.0).

Cold run 9317's office, read by the drop-edge instrument (roadmap 173): the top leg arrives at storey 2 in the
west run; the east run holds leg 0, which tops out a storey below, and the cut at storey 2 spanned both runs --
a pit 6.67 m deep onto leg 0's foot, open on the plate's edge, the east rail's sideways opening and the seam
between the runs. Fails on 0.224.1 (the cut 4.0 m wide at storey 2; no seam guard).

Run: pytest -q test_switchback_top_run.py
"""
import stairwell as S
from spec_types import LevelSpec, Stairwell


def _switchback(to_story=2, facing="N", width=1.6):
    st = Stairwell(x=0.0, y=0.0, from_story=0, to_story=to_story, id="sb", width=width,
                   run=4.7, style="switchback", facing=facing)
    return LevelSpec(name="sb", n_stories=to_story + 1, story_height=3.6,
                     footprint_x=34, footprint_y=24, stairs=[st])


def _lateral(rect, facing):
    x0, y0, x1, y1 = rect
    return (x0, x1) if facing in ("N", "S") else (y0, y1)


def test_top_leg_cuts_only_its_run():
    sp = _switchback()
    st = sp.stairs[0]
    holes = S.slab_openings(sp)
    (r1,) = holes[1]
    assert abs(r1[0] + 2.0) < 1e-6 and abs(r1[2] - 2.0) < 1e-6      # storey 1: both runs and both margins
    (r2,) = holes[2]
    assert abs(r2[0] + 2.0) < 1e-6 and abs(r2[2] - 0.0) < 1e-6      # storey 2: the west run, its outer margin, the seam
    r_lo, r_hi = S.flight_run_lateral(st, 1)
    assert abs(r_hi - r2[2]) < 1e-6                                 # the rectangle meets the other run at the flight's edge
    assert abs(r2[3] - r2[1] - (4.7 + 0.3 + 0.8)) < 1e-6            # the travel extent is what it was


def test_three_legs_top_leg_in_the_east_run():
    sp = _switchback(to_story=3)
    holes = S.slab_openings(sp)
    (r3,) = holes[3]
    assert abs(r3[0] - 0.0) < 1e-6 and abs(r3[2] - 2.0) < 1e-6      # leg 2 climbs in the east run
    (r2,) = holes[2]
    assert abs(r2[0] + 2.0) < 1e-6 and abs(r2[2] - 2.0) < 1e-6      # an intermediate leg keeps both runs


def test_facing_east_turns_the_seam_with_the_stair():
    sp = _switchback(facing="E")
    (r2,) = S.slab_openings(sp)[2]
    lo, hi = _lateral(r2, "E")
    assert abs(hi - lo - 2.0) < 1e-6
    assert min(abs(lo), abs(hi)) < 1e-6                             # one lateral edge is the seam at the stair's own line


def test_seam_guards():
    sp = _switchback()
    st = sp.stairs[0]
    g = S.stair_guards(sp)
    seam_pos = S.SIDE_GAP + S.GUARD_THICK / 2.0
    sides = [p for p in g if p["kind"] == "side" and p["story"] == 1 and abs(p["pos"] - seam_pos) < 1e-6]
    assert len(sides) == 1, [p for p in g if p["story"] == 1]
    p = sides[0]
    assert "thick" not in p                                          # thin, like a narrow flight's guard
    land = S.flight_solid_end(st, sp.story_height, 0)[1]
    assert abs(p["lo"] + 3.15) < 1e-6                                # from the rectangle's far end
    assert abs(p["hi"] - (land - S.SIDE_GAP)) < 1e-6                 # to the turn landing: no sideways opening
    # ITS UNDERSIDE IS A BODY'S HEIGHT ABOVE THE FLOOR, so the flight below keeps its headroom under it
    import agent_contract
    H = sp.story_height
    assert abs(p["z_lo"] - (H + agent_contract.body_height())) < 1e-6
    assert p["z_lo"] < 2 * H                                           # and there is wall left under the slab
    rails = [p for p in g if p["kind"] == "rail" and p["story"] == 2 and abs(p["pos"] - seam_pos) < 1e-6]
    assert len(rails) == 1
    assert not [p for p in g if p["story"] == 2 and p["axis"] == "Y" and p["pos"] > 0.2]   # nothing over the other run
    end = [p for p in g if p["kind"] == "rail" and p["story"] == 2 and p["axis"] == "X"]
    assert len(end) == 1 and abs(end[0]["lo"] + 2.1) < 1e-6 and abs(end[0]["hi"] - 0.1) < 1e-6
    outer = [p for p in g if p["kind"] == "side" and p["story"] == 1 and p["pos"] < -1.0]
    assert len(outer) == 1 and abs(outer[0]["thick"] - (S.SIDE_MARGIN - S.SIDE_GAP)) < 1e-6   # the outer wall as before


def test_single_run_and_straight_unchanged():
    one = _switchback(to_story=1).stairs[0]
    assert S.hole_span(one, 0) == S.hole_span(one)
    straight = Stairwell(x=0.0, y=0.0, from_story=0, to_story=3, id="st", width=1.2, run=4.0, style="straight")
    for s in range(3):
        assert S.hole_span(straight, s) == S.hole_span(straight)
    g = S.stair_guards(_switchback(to_story=1))
    assert all(abs(abs(p["pos"]) - (S.SIDE_GAP + S.GUARD_THICK / 2.0)) > 1e-6 for p in g)   # no seam piece
'''

CHANGELOG_ENTRY = '''## [0.225.0] - a switchback's top leg cuts only its own run

**Cold run 9317's office, read by the drop-edge instrument (roadmap 173, the factory's
`docs/findings/drop_edges_173/`):** the stair's top leg arrives at storey 2 in the west run; the east run holds
leg 0, which tops out a storey below, and the slab cut at storey 2 spanned both runs -- so the east half of the
cut was a pit 6.67 m deep onto leg 0's foot, open on three edges: the discharge plate's edge over the east run
(five unguarded edges), the east rail's sideways opening (one of them), and the seam between the runs along the
whole of leg 1 (seven, 1.3-5.9 m down onto leg 0). The guards derived for it on 0.224.1 said why: `rail` leaves
the arrival end open across the whole reserved rectangle, which is two runs wide, and `side` stands only on the
rectangle's outer edges, so a wall even hung over the east run's margin at storey 1 while nothing stood at the
seam. `single_run` already stops a one-leg switchback cutting the run it does not use (cold run 9050); this is
the same rule one storey up.

### Changed
- **`stairwell.hole_span(st, s)` is per leg**: the top leg of a multi-storey switchback cuts its own run plus
  its outer margin, meeting the other run at the seam with no margin, so the slab covers the other run to the
  flight's edge. `flight_rect` and the builder's `_stairs` (the cut and the discharge plate) pass `s`; an
  intermediate leg and its turn landing keep both runs. Every other caller of `flight_rect` passed `s` already.
- **`stairwell.stair_guards` guards the seam**: on the top leg's seam side a thin side wall (`GUARD_THICK` at
  `SIDE_GAP` from the treads, as a narrow flight's) runs from the rectangle's far end to the turn landing the
  leg departs from, with no sideways opening, and ITS UNDERSIDE IS A BODY'S HEIGHT ABOVE THE FLOOR
  (`_seam_pieces`, `z_lo`; the builder's `_stair_guards` lifts the box and keeps its top at the slab
  underside). The rail above stands at the seam on the slab that now covers the other run, with the usual
  opening at the arrival end, which is over the leg's own top treads and plate. The wall that stood over the
  other run's outer margin at the top storey goes with the margin.
- `test_switchback_top_run.py`: the cut at the top storey is one run wide and meets the other run at the
  flight's edge (two and three legs, facing N and E), an intermediate storey keeps both runs, the seam wall and
  rail exist with those spans and that underside and nothing stands over the other run, a single-storey
  switchback and a straight flight are unchanged. Fails on 0.224.1.

### Measured
- The seam wall's underside, on the nav gate (Godot's own bake, `nav_gate.py`), one shell of 157:
  `cbp_town_finale_midbalanced`'s stair 0, whose lower run a console volume already leans over from the other
  side (`STAIR_VOLUME_INVADED`). With the wall's bottom at the storey floor the bake lost the lower flight
  2.25 m up (endpoints on islands of 101 and 612 polygons; the mirror stair, with nothing leaning on it,
  passed); with no seam wall it connected; with the bottom lifted a metre it connected. REFUTED on the same
  shell: an underside stepped along the flight below at a body's height plus a riser over it -- the same cut,
  the same 101 polygons -- so the bake's objection is not that headroom model. Shipped: the bottom at the floor
  plus the contract's body height, which passed; the gap under it is a body's height minus the leg's own rise,
  so the top leg is held from its first riser on.
- Before, on cold run 9317 (DC 0.224.1): the office, walked by the factory's `tools/walkable_edge.gd` seeded
  from the crew spawn, had 59 unguarded edges, 12 of them this pit. The after is the next cold run's, in
  roadmap 173.

'''


def write_tests():
    (DC / "test_switchback_top_run.py").write_text(TEST, encoding="utf-8")
    print("wrote deli_counter/test_switchback_top_run.py")


def main(argv):
    if "--tests" in argv:
        write_tests()
        return 0
    sw = DC / "stairwell.py"
    _apply(sw, HOLE_SPAN_OLD, HOLE_SPAN_NEW)
    _apply(sw, FLIGHT_RECT_OLD, FLIGHT_RECT_NEW)
    _apply(sw, HELPER_ANCHOR, HELPER_NEW)
    _apply(sw, GUARDS_OLD, GUARDS_NEW)
    dc = DC / "deli_counter.py"
    _apply(dc, BUILDER_OLD, BUILDER_NEW)
    _apply(dc, Z_OLD, Z_NEW)
    v = DC / "VERSION"
    assert v.read_text(encoding="utf-8").strip() == "Deli Counter 0.224.1", v.read_text(encoding="utf-8")
    v.write_text("Deli Counter 0.225.0", encoding="utf-8")
    cl = DC / "CHANGELOG.md"
    raw = cl.read_bytes()
    eol = "\r\n" if raw.count(b"\r\n") else "\n"
    text = raw.decode("utf-8")
    assert text.startswith("## [0.224.1]"), text[:40]
    cl.write_bytes((CHANGELOG_ENTRY.replace("\n", eol) + text).encode("utf-8"))
    write_tests()
    print("Deli Counter 0.225.0 applied: hole_span per leg, the seam guarded with a lifted underside, test, VERSION, CHANGELOG")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
