"""Deli Counter 0.204.0, the code: an indoor payphone asks for Zoo's `wall`
form (roadmap 210).

`level_design._piece("payphone", ..., "wall")` stands a payphone against a
wall and asked for no form, so Zoo's `auto` built a booth on a post in front
of the wall -- cold run 9212 shipped two, the airport terminal's and the
funeral home's. Zoo 1.88.0's `wall` unit is what a lobby carries.

- `level_design.py`: the payphone piece asks `form="wall"`.
- `test_payphone_wall_form.py` (new, refused if present): the piece asks;
  every payphone the piece placed carries it in its spec and in the
  `slots.json` Zoo reads; the form moved no size. Its first three cases fail
  on 0.203.0.

The refurnish (`migrate_furnish_recipes.py`) and `build.py --all` follow
this, and `patch_dc_0204_release.py` writes VERSION and the CHANGELOG with
what they measured.

    python patch_dc_payphone_wall.py
"""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
DC = ROOT / "deli_counter"
SRC = pathlib.Path(__file__).resolve().parent / "dc_payphone_wall"

OLD = """    _piece("payphone", ((0.75, 0.5, 2.3),), "wall", front=True, most=1),
"""
NEW = """    # THE PAYPHONE ON A WALL IS A WALL UNIT (0.204.0, roadmap 210): Zoo
    # 1.88.0's `wall` form -- no post, a conduit down the wall, a phone book
    # under the shelf. Asked for nothing, Zoo's `auto` stood a booth on a post
    # in front of the wall.
    _piece("payphone", ((0.75, 0.5, 2.3),), "wall", front=True, form="wall", most=1),
"""


def main():
    v = (DC / "VERSION").read_bytes().strip()
    assert v == b"Deli Counter 0.203.0", v
    p = DC / "level_design.py"
    d = p.read_bytes()
    assert b"\r\n" not in d, "level_design.py is LF; it has CRLF now"
    t = d.decode("utf-8")
    assert t.count(OLD) == 1, t.count(OLD)
    test = DC / "test_payphone_wall_form.py"
    assert not test.exists(), test
    src = (SRC / "test_payphone_wall_form.py").read_bytes().replace(b"\r\n", b"\n")
    # every check passed: now write
    p.write_bytes(t.replace(OLD, NEW).encode("utf-8"))
    test.write_bytes(src)
    print("level_design: the payphone asks form='wall'; test_payphone_wall_form.py written")


if __name__ == "__main__":
    main()
