"""Deli Counter 0.177.0: a parapet is a wall the art pass dresses.

No pass skinned a parapet: 324 `gb_wall` surfaces in cold run 9148's
package, all `parapet_*` -- 260 on the Empties, 64 on two real buildings.
Each visual tile becomes a wall slot named as the tile, in the material of
the top storey's wall on its side, so Zoo builds it and the composer strips
the greybox tile like any wall. See `dc_parapet_slots/CHANGELOG_0.177.0.md`.

Anchored edits (every anchor once; refuses on a miss):
  deli_counter.py  `_parapets` records a slot per tile when modular;
                   `_record_parapet_slot`
Copies the test; CHANGELOG and VERSION. `python build.py --all` follows.

    python patch_dc_parapet_slots.py
"""
import pathlib
import shutil

HERE = pathlib.Path(__file__).resolve().parent
DC = HERE.parent / "deli_counter"
SRC = HERE / "dc_parapet_slots"


def _edit(path, pairs):
    s = path.read_text(encoding="utf-8")
    assert "\r" not in s, path
    for old, new in pairs:
        assert s.count(old) == 1, (path.name, old[:70])
        s = s.replace(old, new)
    path.write_text(s, encoding="utf-8", newline="\n")


TILE_OLD = '''                for suffix, (dx, dy), (tx, ty) in floors.slab_tiles(
                        size[0], size[1]):
                    self._box(f"parapet_{n}{suffix}",
                              (c[0] + dx, c[1] + dy, c[2]),
                              (tx, ty, size[2]), self.VISUAL, role="wall")
                self._col_box(f"parapet_{n}_col", c, size)
'''
TILE_NEW = '''                for suffix, (dx, dy), (tx, ty) in floors.slab_tiles(
                        size[0], size[1]):
                    self._box(f"parapet_{n}{suffix}",
                              (c[0] + dx, c[1] + dy, c[2]),
                              (tx, ty, size[2]), self.VISUAL, role="wall")
                    # A PARAPET IS THE WALL BELOW IT, CARRIED PAST THE ROOF
                    # (0.177.0): a slot per tile, so the art pass dresses it
                    # as that wall. Nothing skinned one before -- 324 grey
                    # surfaces in cold run 9148, the cornice of every Empty.
                    if self._modular_on():
                        self._record_parapet_slot(
                            f"parapet_{n}{suffix}", (c[0] + dx, c[1] + dy, c[2]),
                            (tx, ty, size[2]), n, p.story)
                self._col_box(f"parapet_{n}_col", c, size)
'''

REC_ANCHOR = '''    def _record_opening_slot(self, vb, center, size, axis, h, ref=None,
                             material=None):
'''
REC_NEW = '''    def _record_parapet_slot(self, vname, c, sz, side, story):
        """One wall slot for one parapet tile (0.177.0), named as the tile so
        the composer strips exactly that greybox piece.

        The material is the TOP STOREY'S wall on the same side -- an explicit
        `ext_walls` entry when there is one, else the default -- because the
        parapet is that wall carried past the roof. Its inner face looks onto
        the roof, not a room, so `_material_in` gives it none (`wall` is not
        an `ext_` name). Its height can share a width with a storey wall; the
        manifest's `mark_height_keys` (0.176.0) keeps the two names apart.
        """
        below = {(w.wall, w.story): w for w in self.s.ext_walls}.get((side, story - 1))
        mat = (getattr(below, "material", None) if below else None) or self.s.default_material
        self._record_wall_slot(vname, c, sz, 0 if side in ("N", "S") else 1,
                               "wall", "full", material=mat)
        sl = self.slots[-1]
        sl.update(wall=f"parapet_{side}", story=story, facing=side,
                  transform=dict(sl["transform"],
                                 rot_y={"N": 0, "E": 90, "S": 180, "W": 270}[side]))

    def _record_opening_slot(self, vb, center, size, axis, h, ref=None,
                             material=None):
'''


# FOLLOW-UPS found by the library-wide name check once parapets were slots:
# parapet runs cut by `floors.slab_tiles` (millimetre-snapped) gave equal tiles
# 1 mm apart -- one module at any resolution a name carries -- so both the
# check and the marker ask at whole centimetres; and `themed_tscn.py` joins
# the freshness sources, because the manifest's marking is decided there.
KEYTEST_OLD = """            g[stem].add(tuple(round(float(v), 4) for v in s["fit"]["dims"][:3]))"""
KEYTEST_NEW = """            # AT THE NAME'S OWN RESOLUTION, whole centimetres (0.177.0): a
            # parapet run cut by `floors.slab_tiles` snaps its interior cuts
            # to millimetres, so equal tiles differ by up to 1 mm (4.666 and
            # 4.667 m) and are one module at any resolution a name can carry.
            g[stem].add(tuple(int(round(float(v) * 100)) for v in s["fit"]["dims"][:3]))"""
MARK_OLD = """        h = round(float(s["fit"]["dims"][2]), 4)
        groups.setdefault(stem, {}).setdefault(h, []).append(i)"""
MARK_NEW = """        # whole centimetres, the resolution `_h<cm>` can carry (0.177.0): two
        # heights a millimetre apart would be marked and still share a name
        h = int(round(float(s["fit"]["dims"][2]) * 100))
        groups.setdefault(stem, {}).setdefault(h, []).append(i)"""
FRESH_OLD = """    "spec_loader.py",
    "build.py",
)
"""
FRESH_NEW = """    "spec_loader.py",
    "build.py",
    # the slot manifest's `fit.key_height` is decided here as it is written
    # (`mark_height_keys`, 0.176.0) -- a change to it moves every slots.json
    "themed_tscn.py",
)
"""


def main():
    assert (DC / "VERSION").read_text(encoding="utf-8").strip() == "Deli Counter 0.176.0"
    _edit(DC / "deli_counter.py", [(TILE_OLD, TILE_NEW), (REC_ANCHOR, REC_NEW)])
    _edit(DC / "test_key_height.py", [(KEYTEST_OLD, KEYTEST_NEW)])
    _edit(DC / "themed_tscn.py", [(MARK_OLD, MARK_NEW)])
    _edit(DC / "build_freshness.py", [(FRESH_OLD, FRESH_NEW)])
    shutil.copyfile(SRC / "test_parapet_slots.py", DC / "test_parapet_slots.py")
    ch = DC / "CHANGELOG.md"
    s = ch.read_text(encoding="utf-8")
    ch.write_text((SRC / "CHANGELOG_0.177.0.md").read_text(encoding="utf-8").rstrip("\n") + "\n\n" + s,
                  encoding="utf-8", newline="\n")
    (DC / "VERSION").write_text("Deli Counter 0.177.0", encoding="utf-8", newline="\n")
    print("applied Deli Counter 0.177.0")


if __name__ == "__main__":
    main()
