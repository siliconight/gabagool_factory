"""`RAIL_OPEN_MIN` gets a name, a measurement and a gate.

The overhang rule derives HOW FAR a rail's opening may hang past its plate
(a body radius). It does not say how wide the opening must END UP, and that is
the quantity the bake actually cares about. Naming it here lets
`test_rail_opening.py` assert the inequality over every flight in the library,
so the 28 mm of margin this release ships on cannot go negative unnoticed --
which is how the same defect went five weeks without being seen.

Anchored: the anchor must match exactly once or this refuses to write.
"""
from pathlib import Path

TARGET = Path(__file__).resolve().parent.parent / "deli_counter" / \
    "stairwell.py"

OLD = "WALKOFF_CLEAR = 0.8\n"

NEW = '''WALKOFF_CLEAR = 0.8
#: The narrowest opening a stair rail can leave and still have the bake connect
#: the landing to the floor beside it.
#:
#: MEASURED, NOT DERIVED, and that is a limitation rather than a shrug. Forcing
#: `open_rail` to a constant and rebuilding `foundry_heist_vertical` at each
#: value gave FAIL at 1.0778, 1.2, 1.25, 1.3 and 1.35 and PASS at 1.4, 1.6, 1.8
#: and 2.05 -- nine distinct glb hashes, monotone, with the 2.05 control
#: reproducing the pre-0.143.0 glb exactly, so the knob reached the geometry and
#: the instrument could see a difference. At bake radius 0.40, cell 0.10,
#: climb 0.15, slope 55 (`agent_contract.nav_bake`).
#:
#: TWO CONTRACT CONSTANTS WERE CANDIDATES AND BOTH FAIL: `min_corridor_width`
#: 1.10 and `min_door_width` 1.25. So this is not a clearance in the contract's
#: sense -- it is what Recast needs to join two regions through a gap, and it
#: moves when the bake's radius or cell size moves. Re-measure it then.
#:
#: NOTHING BUILDS TO THIS. It is a floor that `test_rail_opening.py` checks the
#: library against; the geometry is decided by the overhang rule in
#: `stair_guards`. A constant that is asserted rather than used is deliberate
#: here -- the alternative is a number in a comment, which rots.
RAIL_OPEN_MIN = 1.4
'''


def main() -> None:
    data = TARGET.read_bytes()
    if b"\r\n" in data:
        raise SystemExit("REFUSED: expected LF, found CRLF")
    text = data.decode("utf-8")
    before = len(data)
    if "RAIL_OPEN_MIN" in text:
        raise SystemExit("REFUSED: RAIL_OPEN_MIN already present")
    hits = text.count(OLD)
    if hits != 1:
        raise SystemExit(f"REFUSED: anchor matched {hits} times")
    out = text.replace(OLD, NEW).encode("utf-8")
    if b"\r\n" in out:
        raise SystemExit("REFUSED: would write CRLF")
    TARGET.write_bytes(out)
    print(f"{TARGET.name}: {before} -> {len(out)} bytes (+{len(out) - before})")


if __name__ == "__main__":
    main()
