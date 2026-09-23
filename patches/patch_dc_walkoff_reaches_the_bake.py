"""The walk-off past a landing is deep enough for the bake to connect it.

THE DEFECT, and it is 0.143.0's -- this release's own. That change clipped a
stair rail's opening to the solid floor beneath it, `step_d + WALKOFF_CLEAR`,
which was right about the floor and silent about whether what remained still
connected. On `foundry_heist_vertical` it did not: the basement baked as a
disjoint island of 339 polygons against 1,286 for ground-to-roof, and three
separate ways up -- the switchback stair, a 12 m ramp declared at 30 deg, and a
ladder -- all failed to carry.

HOW IT WAS ATTRIBUTED, because the first two answers were wrong.
`build/*.manifest.json` is tracked and carries `outputs_sha256_16`:

    2026-09-16  pre-0.143.0  c600f22e9178d52e
    2026-09-23  0.143.0      8f2b4ae3a33c8567   and unchanged since

Confirmed by building the shell with `stairwell.py` from HEAD~1 (hash returns,
both stairs `ok`) and at HEAD (hash returns, `stair_0` `no_path`), restoring the
file byte-for-byte each time. Two earlier hypotheses were refuted first: that
the spec's `to_story == n_stories` was out of range (ten specs use that
roof-access convention and only this one fails), and that the arrival sat one
`cell_height` above the ground floor (the glb says landing, discharge and
ground slab all top out at y = 0.0000; the 0.20/0.35 in the island report are
Recast voxel tops on the bake's own grid, a rounded artefact).

THE MEASUREMENT. Forcing `open_rail` to a constant and rebuilding this shell at
each value, nine distinct glb hashes, monotone, with the 2.05 control
reproducing the pre-0.143.0 glb EXACTLY -- so the knob reached the geometry and
the instrument can see a difference:

    1.0778 FAIL  1.2 FAIL  1.25 FAIL  1.3 FAIL  1.35 FAIL
    1.4 PASS     1.6 PASS  1.8 PASS   2.05 PASS

So the bake needs an opening between 1.35 and 1.40 m, while the plate under it
was 0.2778 + 0.8 = 1.0778 m. THE PREMISE WAS UNSATISFIABLE: the opening must be
wider than the floor, and no clip value gives both. The fix is to size the
FLOOR to the opening rather than the opening to the floor.

WHY A CONSTANT AND NOT A PER-STAIR DERIVATION. `step_d + WALKOFF_CLEAR` is the
quantity that must clear `RAIL_OPEN_MIN`, and the honest per-stair form would
be `max(WALKOFF_CLEAR, RAIL_OPEN_MIN - step_d)`. But `step_d` needs the storey
height, and `flight_rect` -- which reserves this same ground for the layout
passes, in six files and twelve call sites -- takes only `(st, s)`. A version
of the walk-off that `flight_rect` could not see would reserve one rectangle
while the builder cut a different hole, and furniture would be placed over a
void. So the constant is sized for the SHALLOWEST step the authored library
builds, measured across all 133 specs and 149 flights:

    min step_d 0.1667 (apartment_walkup_a01, deli_a01 and six more:
                       3.00 m run over 18 steps)
    max step_d 0.3095 (cbp_town_finale_midbalanced)
    1.40 - 0.1667 = 1.2333  ->  WALKOFF_CLEAR = 1.25

which puts every flight's plate between 1.4167 and 1.5595 m. The cost is 0.45 m
of extra floor past every landing, and the same 0.45 m added to the hole and to
`flight_rect`'s reserved rectangle -- they move together, which is the point.

THE CONSTANT CANNOT GO STALE SILENTLY. `test_rail_opening.py` asserts the
inequality for every stair in the library, so authoring a shallower step fails
a test instead of disconnecting a basement five weeks later. A constant
measured against a population needs a gate on that population or it is a guess
with a date on it.

ALSO FIXED HERE: `deli_counter._stairs` carried its own literal `0.8` for the
same quantity. 0.143.0 introduced `WALKOFF_CLEAR` in `stairwell` and left the
builder's copy behind, so the named constant governed the guards and the
reserved rectangle while a literal governed the hole and the plate. Turning the
knob would have moved two of the four. It now reads the constant.

NOT TOUCHED: `hole_span`'s own `clear`, which is also 0.8 and is a LATERAL pad
on the hole's width. `WALKOFF_CLEAR`'s note says in as many words that merging
them because the literals match is the mistake to avoid -- they move for
different reasons, and only one of them moves here.

Anchored: every anchor must match exactly once or this refuses to write.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SW = ROOT / "deli_counter" / "stairwell.py"
DC = ROOT / "deli_counter" / "deli_counter.py"

# ------------------------------------------------------------ stairwell.py
SW_OLD = '''#: The walk-off depth past the top landing, along the flight's TRAVEL axis.
#: `flight_rect` reserves it so a body has somewhere to arrive, and the
#: builder's discharge plate floors it (`deli_counter._stairs`).
#:
#: NOT `hole_span`'s `clear`, which is 0.8 as well and is a LATERAL pad on the
#: hole's width. Two quantities, one value, and merging them because the
#: literals match would be the mistake this note exists to prevent -- they
#: move for different reasons.
WALKOFF_CLEAR = 0.8
'''

SW_NEW = '''#: The narrowest opening a stair rail can leave and still have the bake connect
#: the landing to the floor beside it.
#:
#: MEASURED, NOT DERIVED, and that is a limitation rather than a shrug. Forcing
#: `open_rail` to a constant and rebuilding `foundry_heist_vertical` at each
#: value gave FAIL at 1.0778, 1.2, 1.25, 1.3 and 1.35 and PASS at 1.4, 1.6, 1.8
#: and 2.05 -- nine distinct glb hashes, monotone, with the 2.05 control
#: reproducing the pre-0.143.0 glb exactly, so the knob reached the geometry.
#: At bake radius 0.40, cell 0.10, climb 0.15, slope 55 (`agent_contract`).
#:
#: Two contract constants were candidates and both FAIL: `min_corridor_width`
#: 1.10 and `min_door_width` 1.25. So this is not a clearance in the contract's
#: sense; it is what Recast needs to join two regions through a gap, and it
#: will move if the bake's radius or cell size moves. Re-measure it then.
RAIL_OPEN_MIN = 1.4
#: The walk-off depth past the top landing, along the flight's TRAVEL axis.
#: `flight_rect` reserves it so a body has somewhere to arrive, and the
#: builder's discharge plate floors it (`deli_counter._stairs`).
#:
#: NOT `hole_span`'s `clear`, which is 0.8 and is a LATERAL pad on the hole's
#: width. Two quantities, and merging them because the literals once matched
#: would be the mistake this note exists to prevent -- they move for different
#: reasons, and only this one moved in 0.144.0.
#:
#: WAS 0.8, AND THAT DISCONNECTED A BASEMENT. 0.143.0 clipped a rail's opening
#: to the plate beneath it, `step_d + WALKOFF_CLEAR`; on
#: `foundry_heist_vertical` that is 0.2778 + 0.8 = 1.0778 m against a
#: `RAIL_OPEN_MIN` of 1.4, so the opening could not be both floored and
#: passable and the bake split the shell into disjoint islands. The floor is
#: sized to the opening now, not the opening to the floor.
#:
#: DERIVED FROM THE SHALLOWEST STEP THE LIBRARY BUILDS, because the quantity
#: that must clear `RAIL_OPEN_MIN` is `step_d + WALKOFF_CLEAR` and `step_d`
#: needs the storey height, which `flight_rect` -- twelve call sites in six
#: files, signature `(st, s)` -- does not have. A walk-off `flight_rect` could
#: not see would reserve one rectangle while the builder cut a different hole.
#: Measured over all 133 authored specs, 149 flights: step_d runs 0.1667
#: (apartment_walkup_a01 and seven more, 3.00 m over 18 steps) to 0.3095
#: (cbp_town_finale_midbalanced). 1.40 - 0.1667 = 1.2333, rounded up:
WALKOFF_CLEAR = 1.25
'''

# --------------------------------------------------------- deli_counter.py
DC_OLD = '''                clear = 0.8                  # walk-off depth past the landing
'''

DC_NEW = '''                # ONE SOURCE for the walk-off, because there were two. This
                # read a literal 0.8 while `stairwell.WALKOFF_CLEAR` governed
                # the guards and `flight_rect`'s reserved rectangle, so 0.143.0
                # moved the named constant and left the hole and the discharge
                # plate on the old value. A knob that moves two of the four
                # quantities it names is the defect CLAUDE.md calls a knob with
                # no effect.
                clear = stairwell.WALKOFF_CLEAR   # walk-off past the landing
'''

EDITS = ((SW, SW_OLD, SW_NEW), (DC, DC_OLD, DC_NEW))


def main() -> None:
    staged = []
    for path, old, new in EDITS:
        data = path.read_bytes()
        if b"\r\n" in data:
            raise SystemExit(f"REFUSED: {path.name} is CRLF; expected LF")
        text = data.decode("utf-8")
        hits = text.count(old)
        if hits != 1:
            raise SystemExit(f"REFUSED: {path.name} anchor matched {hits} times")
        out = text.replace(old, new).encode("utf-8")
        if b"\r\n" in out:
            raise SystemExit(f"REFUSED: would write CRLF into {path.name}")
        staged.append((path, len(data), out))
    for path, before, out in staged:
        path.write_bytes(out)
        print(f"{path.name}: {before} -> {len(out)} bytes (+{len(out) - before})")


if __name__ == "__main__":
    main()
