"""A stair rail's opening must have floor under it.

WALKED 2026-09-23, on cold run 9072's package: "this stair case has some
unexpected openings allowing for gaps to step off of the side of a stair case
which we don't want, and the back is exposed".

MEASURED, and the number is exact. `stair_guards` leaves each long-edge rail
open by `landing_open = 0.8 + min_door_width()` = 2.050 m at the arrival end,
so a body can get onto the flight sideways -- walling the full length once
sealed the upstairs objective off (nav gate, 0.126.0 candidate, twin_a01's
both stairs `no_path`), and that decision stands.

What nothing checked is whether the opening has FLOOR under it. The solid at
the arrival end is the landing plus the discharge plate:

    landing    land_d   = step_d + 0.7 * step_d
    discharge  d_depth  = WALKOFF_CLEAR - 0.7 * step_d
                        -----------------------------
    solid                = step_d + WALKOFF_CLEAR      ~ 1.07 m

Measured in the package: landing x 7.93..8.39 (0.46 m), discharge x 8.39..9.00
(0.61 m), total 1.07 m, against an opening of 2.05 m -- so 0.98 m of the
opening hung over the shaft. `tools/walkable_edge.gd` found the fall
independently, by physics: 121 unguarded cells at that stairwell, the floor-
level ones reading x 7.35..8.10, y 0.00, drop 2.90 m -- a full storey.

IT STILL LETS A BODY ON. The clipped opening is ~1.07 m against the nav bake's
requirement of 2 x agent_radius = 0.80 m, and a rail is GUARD_THICK (0.1 m)
deep, so it is a threshold rather than a corridor -- `min_corridor_width`
(1.10) is the test for a length of passage, not for a gap in a rail. Beyond
the reserved rectangle's edge there is ordinary floor and no rail at all, so
the walk-on is the clipped stretch PLUS everything outside the rectangle.

ONLY THE RAIL IS CLIPPED. A `side` stands on the storey BELOW and its opening
is at the entry end, where the floor is that storey's slab -- solid all the
way across. Clipping it would wall a flight in for no reason.

Anchored: every anchor must match exactly once or this refuses to write.
"""
from pathlib import Path

TARGET = Path(__file__).resolve().parent.parent / "deli_counter" / \
    "stairwell.py"

# ---------------------------------------------------------------- anchor 1
A1 = '''#: Air left between a flight's tread ends and its side wall, so the two never
#: share a plane.
SIDE_GAP = 0.005
'''

N1 = '''#: Air left between a flight's tread ends and its side wall, so the two never
#: share a plane.
SIDE_GAP = 0.005
#: The walk-off depth past the top landing, along the flight's TRAVEL axis.
#: `flight_rect` reserves it so a body has somewhere to arrive, and the
#: builder's discharge plate floors it (`deli_counter._stairs`).
#:
#: NOT `hole_span`'s `clear`, which is 0.8 as well and is a LATERAL pad on the
#: hole's width. Two quantities, one value, and merging them because the
#: literals match would be the mistake this note exists to prevent -- they
#: move for different reasons.
WALKOFF_CLEAR = 0.8
'''

# ---------------------------------------------------------------- anchor 2
A2 = '''    x_off = 0.0 if st.style == "straight" else st.width / 2
    clear = 0.8                          # walk-off depth past the landing
'''

N2 = '''    x_off = 0.0 if st.style == "straight" else st.width / 2
    clear = WALKOFF_CLEAR                # walk-off depth past the landing
'''

# ---------------------------------------------------------------- anchor 3
A3 = '''            open_ = landing_open
            if st.style == "scissor":
                side_span = (t_lo + open_, t_hi - open_)
                rail_span = side_span
            elif arrive_hi:
                side_span = (t_lo + open_, t_hi)
                rail_span = (t_lo, t_hi - open_)
            else:
                side_span = (t_lo, t_hi - open_)
                rail_span = (t_lo + open_, t_hi)
'''

N3 = '''            open_ = landing_open
            # A RAIL'S OPENING MUST HAVE FLOOR UNDER IT, and until 0.143.0 it
            # did not. The walker, cold run 9072: "gaps to step off of the
            # side of a stair case which we don't want, and the back is
            # exposed". `landing_open` (2.050 m) is the gap a body needs to
            # get on sideways and it stays; what was missing is that the gap
            # ran 0.98 m past the last solid plate and over the open shaft.
            #
            # The solid at the arrival end is the landing plus the discharge:
            # `land_d` is step_d + 0.7 * step_d and `d_depth` is
            # WALKOFF_CLEAR - 0.7 * step_d, so together they are exactly
            # step_d + WALKOFF_CLEAR -- the 0.7 * step_d split moves where the
            # two meet and not how far they reach. Measured in the shipped
            # package: 0.46 + 0.61 = 1.07 m against an opening of 2.05.
            #
            # A SIDE IS NOT CLIPPED. It stands on the storey BELOW, and its
            # opening is at the entry end where that storey's slab is solid
            # across the whole rectangle.
            step_d = st.run / float(_step_count(st, H))
            open_rail = min(open_, step_d + WALKOFF_CLEAR)
            if st.style == "scissor":
                side_span = (t_lo + open_, t_hi - open_)
                rail_span = (t_lo + open_rail, t_hi - open_rail)
            elif arrive_hi:
                side_span = (t_lo + open_, t_hi)
                rail_span = (t_lo, t_hi - open_rail)
            else:
                side_span = (t_lo, t_hi - open_)
                rail_span = (t_lo + open_rail, t_hi)
'''

EDITS = ((A1, N1), (A2, N2), (A3, N3))


def main() -> None:
    data = TARGET.read_bytes()
    if b"\r\n" in data:
        raise SystemExit("REFUSED: expected LF, found CRLF")
    text = data.decode("utf-8")
    before = len(data)
    for i, (old, new) in enumerate(EDITS, 1):
        hits = text.count(old)
        if hits != 1:
            raise SystemExit(f"REFUSED: anchor {i} matched {hits} times")
        text = text.replace(old, new)
    out = text.encode("utf-8")
    if b"\r\n" in out:
        raise SystemExit("REFUSED: would write CRLF")
    TARGET.write_bytes(out)
    print(f"{TARGET.name}: {before} -> {len(out)} bytes (+{len(out) - before})")


if __name__ == "__main__":
    main()
