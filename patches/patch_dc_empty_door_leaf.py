"""Deli Counter 0.186.0: an Empty's door is shut to a ray as well as a body
(roadmap 183). See `dc_empty_door_leaf/CHANGELOG_0.186.0.md`.

Anchored edits (every anchor once; refuses on a miss):
  deli_counter.py   _opening_piece fills a facade's door full-thickness
Copies the test; CHANGELOG and VERSION. Rebuild after: `python build.py --all`.

    python patch_dc_empty_door_leaf.py
"""
import pathlib
import shutil

HERE = pathlib.Path(__file__).resolve().parent
DC = HERE.parent / "deli_counter"
SRC = HERE / "dc_empty_door_leaf"


def _edit(path, pairs):
    s = path.read_text(encoding="utf-8")
    assert "\r" not in s, path
    for old, new in pairs:
        assert s.count(old) == 1, (path.name, old[:70])
        s = s.replace(old, new)
    path.write_text(s, encoding="utf-8", newline="\n")


LEAF_OLD = '''            self._seg_box(f"{vb}_pane", f"{cb}_pane", center, size, axis,
                          u, w, (open_bottom + open_top) / 2.0, hh,
                          role="window", material=material, record_slot=False)
        elif kind == "breach":
'''
LEAF_NEW = '''            self._seg_box(f"{vb}_pane", f"{cb}_pane", center, size, axis,
                          u, w, (open_bottom + open_top) / 2.0, hh,
                          role="window", material=material, record_slot=False)
        elif kind == "door" and getattr(self.s, "facade", False):
            # AN EMPTY'S DOOR IS SHUT (0.186.0, roadmap 183). A door on a facade
            # shell leads nowhere -- the shell is sealed and hollow -- so its
            # aperture is filled full-thickness, as a window's is. Left a
            # walkable void, the 0.7 m between the door module's jambs stopped
            # the 0.8 m walk capsule but not a shot: rays passed 10 m into
            # gs_empty_rowhome_f through its front door (cold run 9162). The
            # art pass's door module still draws the leaf; this is its
            # collision.
            self._seg_box(f"{vb}_leaf", f"{cb}_leaf", center, size, axis,
                          u, w, (open_bottom + open_top) / 2.0, hh,
                          role="doorway", material=material, record_slot=False)
        elif kind == "breach":
'''


def main():
    assert (DC / "VERSION").read_text(encoding="utf-8").strip() == "Deli Counter 0.185.0"
    _edit(DC / "deli_counter.py", [(LEAF_OLD, LEAF_NEW)])
    shutil.copyfile(SRC / "test_empty_door_leaf.py", DC / "test_empty_door_leaf.py")
    ch = DC / "CHANGELOG.md"
    s = ch.read_text(encoding="utf-8")
    ch.write_text((SRC / "CHANGELOG_0.186.0.md").read_text(encoding="utf-8").rstrip("\n") + "\n\n" + s,
                  encoding="utf-8", newline="\n")
    (DC / "VERSION").write_text("Deli Counter 0.186.0", encoding="utf-8", newline="\n")
    print("applied Deli Counter 0.186.0 -- now rebuild: python build.py --all")


if __name__ == "__main__":
    main()
