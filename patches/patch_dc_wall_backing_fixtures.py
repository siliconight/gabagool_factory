"""Deli Counter 0.202.0: the furnish and club probes stand their rooms in walls.

    python patch_dc_wall_backing_fixtures.py

Three test files as read 2026-10-07 (all LF): `test_furnish.py` (39,336 bytes),
`test_club_rooms.py` (35,571), `test_club_fixtures.py` (14,358). Every anchor
asserted once, nothing written on a miss.

WHY. The probes stood a room 2 m INSIDE a larger footprint "so its walls are
interior": edges with no partition on them, which furnish took for walls. From
0.202.0 a wall piece needs a wall behind it (`level_design._wall_slots`), so a
room floating in its footprint gets no wall piece at all -- 18 of these tests
failed on the rule for that reason alone, not for what each asks. The room
becomes the shell, its walls the building's own, which is what furnish stands
wall pieces against. The reasoning the footprint carried dated from 0.122.0,
which banned exterior walls; that ban was lifted the release after.

Two more probes put a room on storey -1 in a building that declared no
basement; the builder stands no walls on a storey it does not build, so they
declare one. One vending probe floated its room inside a 44 x 34 footprint; it
becomes 40 x 30, the room.

Run FIRST, before the rule: every changed test passes on 0.201.0 too, so the
fixtures change what the probes stand in, not what they test.
"""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
DC = ROOT / "deli_counter"

FURNISH = [
    ('''def _spec(w=12.0, d=10.0, role="office", **kw):
    # The footprint is deliberately LARGER than the room: wall furniture
    # stands against interior walls only, because `_seed_clear` knows about
    # partitions and nothing here knows where the openings in an outside
    # wall are. A probe room that WAS the whole building would have four
    # exterior walls and no shelf would ever be placed.
    s = {"name": "furnish_probe", "seed": 1997, "story_height": 3.0,
         "footprint_x": w + 4.0, "footprint_y": d + 4.0, "n_stories": 1,
''', '''def _spec(w=12.0, d=10.0, role="office", **kw):
    # THE ROOM IS THE SHELL (0.202.0): its walls are the building's own,
    # which furnish stands wall pieces against, clear of their openings
    # (`_ext_openings`). Until 0.202.0 the footprint was 4 m LARGER than the
    # room so that its walls were "interior" -- edges with no partition on
    # them, which furnish took for walls and no longer does: a wall piece
    # needs a wall behind it. That reasoning dated from 0.122.0, which banned
    # exterior walls; the ban was lifted the release after.
    s = {"name": "furnish_probe", "seed": 1997, "story_height": 3.0,
         "footprint_x": w, "footprint_y": d, "n_stories": 1,
'''),
    ('''    s = _spec(30.0, 24.0, role="connector")
    s["rooms"][0].update(id="storage_basement", story=-1)
''', '''    # a room on storey -1 stands in a basement the building declares: the
    # builder stands no walls on a storey it does not build (0.202.0)
    s = _spec(30.0, 24.0, role="connector", has_basement=True)
    s["rooms"][0].update(id="storage_basement", story=-1)
'''),
    ('''        s = _spec(20.0, 16.0, role="utility", story_height=sh)
        s["rooms"][0].update(id="boiler_room", story=-1)
''', '''        # in a basement the building declares (0.202.0)
        s = _spec(20.0, 16.0, role="utility", story_height=sh, has_basement=True)
        s["rooms"][0].update(id="boiler_room", story=-1)
'''),
]

CLUB_ROOMS = [
    ('''    """A strip club with one room; the footprint is larger than the room so
    its walls are interior (the furnish probe's reasoning)."""
    s = {"name": name, "seed": 1997, "story_height": 3.6, "wall_thick": 0.3,
         "footprint_x": w + 4.0, "footprint_y": d + 4.0, "n_stories": 1,
''', '''    """A strip club with one room, which is the whole shell: its walls are
    the building's own (0.202.0, the furnish probe's reasoning -- a wall
    piece needs a wall behind it, and a room floating 2 m inside its
    footprint had none)."""
    s = {"name": name, "seed": 1997, "story_height": 3.6, "wall_thick": 0.3,
         "footprint_x": w, "footprint_y": d, "n_stories": 1,
'''),
    ('''             "footprint_x": 44.0, "footprint_y": 34.0, "n_stories": 1,
             "rooms": [{"id": "upper_hall", "story": 0, "role": "connector",
''', '''             # the room is the shell (0.202.0): a wall piece needs a wall
             "footprint_x": 40.0, "footprint_y": 30.0, "n_stories": 1,
             "rooms": [{"id": "upper_hall", "story": 0, "role": "connector",
'''),
]

CLUB_FIXTURES = [
    ('''def _club(w=20.0, d=12.0, rid="main_floor", name="strip_club_probe", **kw):
    s = {"name": name, "seed": 1997, "story_height": 3.6, "wall_thick": 0.3,
         "footprint_x": w + 4.0, "footprint_y": d + 4.0, "n_stories": 1,
''', '''def _club(w=20.0, d=12.0, rid="main_floor", name="strip_club_probe", **kw):
    # the room is the shell, its walls the building's own (0.202.0): a wall
    # piece needs a wall behind it, and a room inside a larger footprint had
    # none
    s = {"name": name, "seed": 1997, "story_height": 3.6, "wall_thick": 0.3,
         "footprint_x": w, "footprint_y": d, "n_stories": 1,
'''),
]


def _apply(path, size, edits):
    data = path.read_bytes()
    assert len(data) == size, "%s is %d bytes, not the %d read; refusing" % (path.name, len(data), size)
    assert b"\r\n" not in data, "CRLF in %s; refusing" % path.name
    text = data.decode("utf-8")
    for old, _new in edits:
        n = text.count(old)
        assert n == 1, "%s: anchor found %d times, not once: %r" % (path.name, n, old[:60])
    for old, new in edits:
        text = text.replace(old, new)
    return text


def main():
    out = [(DC / "test_furnish.py", _apply(DC / "test_furnish.py", 39336, FURNISH)),
           (DC / "test_club_rooms.py", _apply(DC / "test_club_rooms.py", 35571, CLUB_ROOMS)),
           (DC / "test_club_fixtures.py", _apply(DC / "test_club_fixtures.py", 14358, CLUB_FIXTURES))]
    for p, text in out:
        p.write_bytes(text.encode("utf-8"))
        print("%s: %d bytes" % (p.name, len(p.read_bytes())))


if __name__ == "__main__":
    main()
