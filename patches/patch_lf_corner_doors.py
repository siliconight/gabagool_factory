"""A building beside the cross street gets a door onto it.

THE MEASUREMENT. `tools/level_recipe_census.py`, after Lot 0.77.0 taught the
site graph about streets:

    street_members  {0: ['b0', 'b1', 'b2'], 1: []}

Every generated site, including the first crossroads ever built
(`crossroads_9600`, where Lot drew a genuine four-approach X): not one building
has a door onto the cross street. `_spurs` derives every door from the FRONT
road's y and nothing else, so the side street is a road through empty ground.

WHY IT MATTERS BEYOND TIDINESS. The level recipe asks for
`approaches: min 3` and no site has ever exceeded 2, because three buildings on
one street afford two directions to come from. The cross street is the obvious
third, and it has no addresses to approach from. The walker's own archetype
list says the same thing about what a crossroads IS -- "four corners become
natural anchors" -- and a junction with nothing on its corners is a junction,
not a corner.

WHAT A CORNER BUILDING IS, and the test is the same one the front door uses. A
building fronts the cross street when its nearer LATERAL face is close enough
to that street's band to have a door onto it: within `FRONTAGE`, the same
2.0 m stoop-and-meter-strip the front door is given, measured from the band's
outer edge. That is the existing rule applied on the other axis rather than a
new number.

THE DOOR STOPS ON THE SIDEWALK, for the reason the front door does and which
cost a cold run to learn: a path reaching the road's centre line is read by
Lot's `kerb_crossings` as a street crossing, and cold run 9048 shipped every
door dropped-kerbed, crosswalked and signed. `SPUR_INTO_WALK` is the same
fraction, off the same walk depth.

ONLY WHERE THERE IS ROOM. The front door is skipped when the gap between the
face and the walk is under 0.3 m, because a path shorter than that is a seam
rather than a route. The same guard applies here, on the lateral axis.

NOT A PLACEMENT CHANGE. This does not move a single building; it declares a
door that the geometry already affords. Moving buildings to suit the road --
the road graph first, buildings hung off it -- is the inversion `road_grammar`'s
own docstring defers, and doing it in the same change as this would make the
before-and-after unreadable.

Anchored: every anchor must match exactly once or this refuses to write.
"""
from pathlib import Path

TARGET = Path(__file__).resolve().parent.parent / "level_factory" / \
    "packages" / "pipeline" / "road_grammar.py"

# ---------------------------------------------------------------- anchor 1
A1 = '''        south = face if south is None else min(south, face)
    return south, faces, edges
'''

N1 = '''        south = face if south is None else min(south, face)
        spans.append((x - float(ext_x) / 2.0, x + float(ext_x) / 2.0,
                      float(b["at"][1]) - float(ext_y) / 2.0,
                      float(b["at"][1]) + float(ext_y) / 2.0))
    return south, faces, edges


def _lateral_spurs(spans, x_cross, y_road, span_y):
    """A door from each building whose SIDE faces the cross street.

    `_spurs` derives every door from the front road, so until this existed the
    cross street had no addresses at all -- measured across every generated
    site, `street_members` read `{0: [b0, b1, b2], 1: []}`, including on the
    first crossroads ever built.

    A building fronts the cross street when its nearer lateral face is within
    `FRONTAGE` of that street's band -- the same 2.0 m the front door is given,
    applied on the other axis rather than a number chosen here. The door stops
    on the sidewalk for the reason the front one does: a path that reaches the
    centre line is read as a street crossing, and cold run 9048 shipped every
    door dropped-kerbed, crosswalked and signed.

    Skipped where a building sits across the street's line: a door needs a
    face outside the band to start from.
    """
    band = ROAD_WIDTH / 2.0 + SIDEWALK_WIDTH
    walk_in = band - SIDEWALK_WIDTH * SPUR_INTO_WALK
    out = []
    for x0, x1, y0, y1 in spans:
        # the building's own stretch of the cross street, and its mid-point;
        # a door is put where the building actually is, not at its centre if
        # that centre lies off the street's run
        y_mid = max(min((y0 + y1) / 2.0, span_y / 2.0 - ROAD_MARGIN),
                    y_road)
        if x1 <= x_cross:                       # building lies WEST of it
            face, sign = x1, +1
        elif x0 >= x_cross:                     # EAST of it
            face, sign = x0, -1
        else:
            continue                            # straddles the line: no face
        gap = abs(x_cross - face) - band
        if gap < 0.0 or gap > FRONTAGE:
            continue                            # too far to be a corner
        end = x_cross - sign * walk_in
        if abs(end - (face + sign * 1.0)) <= 0.3:
            continue                            # a seam, not a route
        out.append({"a": [face + sign * 1.0, y_mid], "b": [end, y_mid],
                    "width": SPUR_WIDTH})
    return out
'''

# ---------------------------------------------------------------- anchor 2
A2 = '''    south, faces, edges = None, [], []
'''
N2 = '''    south, faces, edges, spans = None, [], [], []
'''

# ---------------------------------------------------------------- anchor 3
A3 = '''    """(southernmost front face, per-building [(x, face)], per-building x span).
'''
N3 = '''    """(southernmost front face, per-building [(x, face)], per-building x span,
    per-building (x0, x1, y0, y1) box).
'''

# ---------------------------------------------------------------- anchor 4
A4 = '''    south, faces, edges = _south_face(buildings, footprints)
'''
N4 = '''    south, faces, edges, spans = _south_face(buildings, footprints)
'''

# ---------------------------------------------------------------- anchor 5
A5 = '''    return [road, cross], _spurs(faces, y_road), span_x, span_y
'''
N5 = '''    # THE CROSS STREET GETS ITS ADDRESSES. Without these it is a road through
    # empty ground: `street_members` read `{0: [b0, b1, b2], 1: []}` on every
    # site ever generated, so the junction added approaches nobody could use.
    doors = _spurs(faces, y_road) + _lateral_spurs(spans, x_cross, y_road,
                                                   span_y)
    return [road, cross], doors, span_x, span_y
'''

EDITS = ((A3, N3), (A2, N2), (A1, N1), (A4, N4), (A5, N5))


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
