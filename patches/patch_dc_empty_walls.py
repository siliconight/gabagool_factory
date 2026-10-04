"""Deli Counter 0.175.2: an Empty's walls run the full storey.

0.175.0 removed an Empty's floor slabs, and `_cap_thick` still stopped every
wall 0.3 m short of each storey line to sit under a slab that was no longer
there. Measured on `gs_empty_rowhome_f.slots.json`: storey 0 walls end at
2.80 and storey 1 begins at 3.10; 5.90 to 6.20 the same. Cold run 9147's
frames show it as a dark band through every Empty at every storey line.

Anchored edits (every anchor once; refuses on a miss):
  deli_counter.py  `_cap_thick` answers 0 on an Empty below its roof
Writes `test_empty_walls.py`; CHANGELOG and VERSION. `deli_counter.py`
changes, so `python build.py --all` follows (build freshness).

    python patch_dc_empty_walls.py
"""
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
DC = HERE.parent / "deli_counter"
SRC = HERE / "dc_empty_walls"


def _edit(path, pairs):
    s = path.read_text(encoding="utf-8")
    assert "\r" not in s, path
    for old, new in pairs:
        assert s.count(old) == 1, (path.name, old[:70])
        s = s.replace(old, new)
    path.write_text(s, encoding="utf-8", newline="\n")


CAP_OLD = '''        a z-fight at every storey boundary of every building. One rule, one
        place, because both wall emitters need it and two copies drift.
        """
        return ((self.s.roof_thick or self.s.floor_thick)
                if story + 1 == top else self.s.floor_thick)
'''
CAP_NEW = '''        a z-fight at every storey boundary of every building. One rule, one
        place, because both wall emitters need it and two copies drift.

        AN EMPTY HAS NO SLAB BETWEEN ITS STOREYS (0.175.0), so nothing caps
        its wall there and it runs the full storey (0.175.2). Stopping short
        under a slab that was no longer emitted left a 0.3 m slot through
        every Empty at every storey line -- a dark band across each house in
        cold run 9147's frames. Under the roof, the one slab it keeps, it
        still stops.
        """
        if getattr(self.s, "facade", False) and story + 1 != top:
            return 0.0
        return ((self.s.roof_thick or self.s.floor_thick)
                if story + 1 == top else self.s.floor_thick)
'''


def main():
    assert (DC / "VERSION").read_text(encoding="utf-8").strip() == "Deli Counter 0.175.1"
    _edit(DC / "deli_counter.py", [(CAP_OLD, CAP_NEW)])
    (DC / "test_empty_walls.py").write_bytes((SRC / "test_empty_walls.py").read_bytes())
    ch = DC / "CHANGELOG.md"
    s = ch.read_text(encoding="utf-8")
    ch.write_text((SRC / "CHANGELOG_0.175.2.md").read_text(encoding="utf-8").rstrip("\n") + "\n\n" + s,
                  encoding="utf-8", newline="\n")
    (DC / "VERSION").write_text("Deli Counter 0.175.2", encoding="utf-8", newline="\n")
    print("applied Deli Counter 0.175.2")


if __name__ == "__main__":
    main()
