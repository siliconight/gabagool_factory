"""A rail's opening may hang past its plate by less than a body's radius.

THE DEFECT IS 0.143.0'S, AND 0.143.0 IS THIS RELEASE'S PREDECESSOR. That change
clipped a stair rail's opening to the solid plate beneath it,
`step_d + WALKOFF_CLEAR`. It was right about the floor and silent about whether
what remained still connected. On `foundry_heist_vertical` it did not: the
basement baked as a disjoint island of 339 polygons against 1,286 for
ground-to-roof, and the switchback stair, a 12 m ramp declared at 30 deg and a
ladder all failed to carry.

ATTRIBUTED, NOT GUESSED. `build/*.manifest.json` is tracked and carries
`outputs_sha256_16`: c600f22e9178d52e before 0.143.0, 8f2b4ae3a33c8567 at and
since it. Building with `stairwell.py` from HEAD~1 returns the old hash and
both stairs gate `ok`; at HEAD the new hash returns and `stair_0` is `no_path`.

THE THRESHOLD, measured by forcing `open_rail` to a constant and rebuilding
this shell at each value -- nine distinct glb hashes, monotone, the 2.05
control reproducing the pre-0.143.0 glb exactly:

    1.0778 FAIL  1.2 FAIL  1.25 FAIL  1.3 FAIL  1.35 FAIL
    1.4 PASS     1.6 PASS  1.8 PASS   2.05 PASS

So the bake wants an opening of about 1.4 against a plate of 1.0778. The
opening must be WIDER than the floor under it, and 0.143.0's premise --
opening <= floor -- has no solution.

A FIX THAT WAS TRIED AND REFUTED, recorded because it looks obviously right.
Raising `WALKOFF_CLEAR` from 0.8 to 1.25 to deepen the plate DID NOT WORK: the
walk-off also sizes `flight_rect`'s reserved rectangle and the builder's hole,
and the opening is measured from that rectangle's edge. Growing it moved `t_lo`
out by exactly as much as the opening grew, so the rail's absolute position
never changed. Rebuilt, gated: `no_path`, glb 2a371e974f9f852d. The opening
equals the plate at any scale -- the two are one quantity, and that is why the
premise is unsatisfiable rather than merely tight.

THE ACTUAL QUESTION, once the shape is right. The hazard the walker reported on
cold run 9072 -- "gaps to step off of the side of a stair case" -- is not a hole
to fall through. It is an UNGUARDED EDGE of length `overhang` along the travel
axis, between where the plate ends and where the rail begins, with the shaft
beside it. A body reaches that void only if it can get its capsule centre over
it, and the rail stops the capsule `radius` short of its own face. So the void
window a centre can occupy is `overhang - radius`, and it is EMPTY while

    overhang < characters.player.radius_m

which is 0.35 m. That is a derivation from the contract rather than a margin
chosen here, and it explains all three states at once:

    before 0.143.0  overhang 0.9722  > 0.35   a body gets over the void
    0.143.0         overhang 0.0000            safe, and disconnected
    here            overhang 0.3500  = 0.35   the rail holds the capsule back
                                              and the opening reaches 1.4278

WHAT IS THIN ABOUT IT, said plainly rather than discovered later. 1.4278 clears
a threshold measured between 1.35 and 1.40 by 28 mm, and that threshold was
measured on ONE shell at one bake setting (radius 0.40, cell 0.10, climb 0.15,
slope 55). It is not a contract clearance -- `min_corridor_width` 1.10 and
`min_door_width` 1.25 were both tried and both FAIL. If the bake's radius or
cell size moves, re-measure it. `test_rail_opening.py` asserts the inequality
over every flight in the library so the margin cannot silently go negative.

ALSO FIXED HERE, and it is a real latent defect rather than tidying:
`deli_counter._stairs` carried its own literal `0.8` for the walk-off while
`stairwell.WALKOFF_CLEAR` governed the guards and the reserved rectangle. Two
spellings of one quantity, so turning the named one would have moved the guards
and left the hole and the discharge plate behind -- the knob-with-no-effect
shape CLAUDE.md records. It reads the constant now. `WALKOFF_CLEAR` itself does
not move.

NOT TOUCHED: `hole_span`'s own `clear`, also 0.8, a LATERAL pad on the hole's
width. `WALKOFF_CLEAR`'s note says in as many words that merging them because
the literals match is the mistake to avoid.

Anchored: every anchor must match exactly once or this refuses to write.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
AC = ROOT / "deli_counter" / "agent_contract.py"
SW = ROOT / "deli_counter" / "stairwell.py"
DC = ROOT / "deli_counter" / "deli_counter.py"

# ------------------------------------------------------- agent_contract.py
AC_OLD = '''def min_corridor_width():
    return float(contract()["clearances"]["min_corridor_width_m"])
'''

AC_NEW = '''def min_corridor_width():
    return float(contract()["clearances"]["min_corridor_width_m"])


def body_radius():
    """The player capsule's radius, in metres.

    NOT `nav_bake.agent_radius_m`, and the difference has cost this repo two
    defects. That one is 0.40 -- the fattest navigating character plus 0.05 --
    and is what a BAKE is given so a 0.35 body has somewhere to stand. This is
    the body itself, and it is what to reach for when the question is "can a
    body get here", "does a body fit" or "how far short of a wall does a
    capsule stop".

    First caller: `stairwell.stair_guards`, deciding how far a rail's opening
    may hang past the floor under it. A capsule cannot put its centre over a
    void window narrower than the distance the rail holds it back, which is
    exactly this.
    """
    return float(contract()["characters"]["player"]["radius_m"])
'''

# ------------------------------------------------------------ stairwell.py
SW_OLD = '''            step_d = st.run / float(_step_count(st, H))
            open_rail = min(open_, step_d + WALKOFF_CLEAR)
'''

SW_NEW = '''            step_d = st.run / float(_step_count(st, H))
            # AND IT MAY HANG PAST THAT FLOOR BY LESS THAN A BODY'S RADIUS,
            # because clipping it to the floor exactly disconnects the landing.
            # 0.143.0 clipped it exactly and `foundry_heist_vertical`'s
            # basement stopped baking as part of the building: 339 polygons
            # against 1,286, with the stair, a 30 deg ramp and a ladder all
            # failing to carry. Measured by forcing this value and rebuilding
            # that shell -- FAIL at 1.0778, 1.2, 1.25, 1.3, 1.35; PASS at 1.4,
            # 1.6, 1.8, 2.05, nine distinct glb hashes with the 2.05 control
            # reproducing the pre-0.143.0 file exactly -- the bake wants about
            # 1.4 where the plate is 1.0778. The opening has to be WIDER than
            # the floor under it, so "opening <= floor" has no solution.
            #
            # WHY A BODY RADIUS AND NOT A CHOSEN MARGIN. The hazard is an
            # unguarded EDGE of length `overhang`, not a hole: a body reaches
            # the void only by getting its capsule centre over it, and the rail
            # holds the capsule `radius` short of its own face. The window a
            # centre can occupy is `overhang - radius`, empty while the
            # overhang stays under a radius. Before 0.143.0 the overhang was
            # 0.9722 against a 0.35 radius, which is why the walker could step
            # off the side of a staircase (cold run 9072).
            #
            # REFUTED, so nobody tries it again: deepening the plate by raising
            # WALKOFF_CLEAR does nothing. The walk-off also sizes
            # `flight_rect`'s reserved rectangle, which is what `t_lo` above
            # comes from, so the opening and its reference edge move together
            # and the rail lands in the same place. Rebuilt at 1.25 and gated:
            # still `no_path`, glb 2a371e974f9f852d.
            #
            # THIN, AND KNOWN TO BE: 1.4278 clears a threshold measured between
            # 1.35 and 1.40 by 28 mm, on one shell at one bake setting.
            # `test_rail_opening.py` asserts it over every flight in the
            # library so the margin cannot go negative unnoticed.
            open_rail = min(open_, step_d + WALKOFF_CLEAR
                            + agent_contract.body_radius())
'''

# --------------------------------------------------------- deli_counter.py
DC_OLD = '''                clear = 0.8                  # walk-off depth past the landing
'''

DC_NEW = '''                # ONE SOURCE for the walk-off, because there were two. This
                # read a literal while `stairwell.WALKOFF_CLEAR` governed the
                # guards and `flight_rect`'s reserved rectangle, so moving the
                # named constant would have moved two of the four quantities it
                # names and left the hole and the discharge plate behind.
                clear = stairwell.WALKOFF_CLEAR   # walk-off past the landing
'''

EDITS = ((AC, AC_OLD, AC_NEW), (SW, SW_OLD, SW_NEW), (DC, DC_OLD, DC_NEW))


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
