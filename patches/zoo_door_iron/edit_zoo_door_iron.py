"""Zoo 1.127.0 on a CLONE (<repo>): a door's hardware is the stoop railing's black iron, so it merges with the railing
(cold run 9391's price of 1.124.0's brass: +2 meshes an Empty). Anchored; refuses on a miss.

    python edit_zoo_door_iron.py <repo>
"""
import pathlib
import sys

R = pathlib.Path(sys.argv[1])


def edit(rel, pairs):
    p = R / rel
    b = p.read_bytes()
    crlf = b"\r\n" in b
    t = b.decode("utf-8").replace("\r\n", "\n")
    for o, n in pairs:
        assert t.count(o) == 1, (rel, o[:70])
        t = t.replace(o, n)
    p.write_bytes((t.replace("\n", "\r\n") if crlf else t).encode("utf-8"))


edit("zoo_keeper/core/doors.py", [
    ("""#: and a knob on an escutcheon plate at the latch edge at handle height, in one
#: shared brass (`HARDWARE`: one material for every door in a build, so the
#: Empties' per-side merge carries it as one more mesh a front at most). Each""",
     """#: and a knob on an escutcheon plate at the latch edge at handle height, in
#: `HARDWARE`. Each"""),
    ("""HARDWARE = ("M_Door_hardware_brass", (0.71, 0.55, 0.24), "metal_painted")""",
     """#: THE HARDWARE IS THE RAILING'S BLACK IRON (1.127.0). 1.124.0 drew it in
#: brass, one more colour of `metal_painted`, which Level Factory makes one more
#: material -- and the Empties' per-side merge one more mesh on EVERY side with
#: a door: cold run 9391 counted +2 meshes on each of its 26 Empties against
#: 9389 (front and back), +582 draws over the package's 53 headings, up to +45
#: at one; frame time inside the controls' spread (the factory's
#: `docs/cold_runs/cold_9391/`). A colour-only variation as a new material is
#: the defect `CLAUDE.md` names first. In the stoop railing's own colour and
#: kind (`genome/species/stoop_railing.json`, every style), the knob is the
#: railing's material and merges into its mesh on a side with a stoop -- every
#: front; a back door with no railing keeps one. Black iron with black iron
#: railings is a South Philly front, a call made 2026-10-24 and meant to be
#: changed: brass back is this colour, at one draw a side.
IRON = (0.06, 0.06, 0.065)
HARDWARE = ("M_Door_hardware_iron", IRON, "metal_painted")"""),
])

TEST_ADD = '''

def test_the_hardware_is_the_stoop_railings_own_iron():
    """1.127.0: the knob shares the railing's material, so a front with a stoop merges it (FAILS ON 1.126.0)."""
    import json
    import os
    g = json.load(open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "zoo_keeper",
                                    "genome", "species", "stoop_railing.json"), encoding="utf-8"))
    name, colour, kind = A.HARDWARE
    assert kind == g["materials"]["default"] == "metal_painted"
    assert {tuple(s["color"]) for s in g["styles"].values()} == {tuple(colour)}, (colour, g["styles"])
'''
p = R / "tests" / "test_door_hardware.py"
t = p.read_bytes().decode("utf-8")
assert "test_the_hardware_is_the_stoop_railings_own_iron" not in t and "\r\n" not in t
p.write_bytes((t.rstrip("\n") + "\n" + TEST_ADD).encode("utf-8"))
print("doors.IRON, HARDWARE in the railing's iron; tests/test_door_hardware.py")
