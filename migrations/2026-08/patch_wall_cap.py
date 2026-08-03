"""Walls stop under the slab that caps them. Reverts the inset; fixes both families.

WHY THE INSET WAS THE WRONG SHAPE, measured rather than argued. Insetting the
slab took cr_deli from 363 visible fights to 151 -- and the remainder broke down
as:

    93   int_*_segN  <->  slab_N     INTERIOR partitions
    16   parapet corners
     4   stair discharge, ext-vs-int

Interior walls stand in the middle of the building, so shrinking the slab at its
perimeter cannot reach them. The inset fixed the defect where it was VISIBLE
from where the level was being walked, not where it IS. It clears 58% and
structurally cannot clear the rest.

THE ACTUAL RULE. Every wall, exterior or interior, spans [sH, (s+1)H]. Every
slab spans [sH - ft, sH], because its top face is the floor of storey s -- the
coordinate contract fixes that and it should not move. So the wall's top face
and the slab-above's top face both land on (s+1)H, both pointing up,
interpenetrating through the slab's whole thickness. That is one defect with two
emitters, and it repeats at every storey boundary of every building.

Cap the wall at the slab's underside -- [sH, (s+1)H - ft] -- and the wall top
meets the slab bottom. Abutting, which zfight_gate ignores by design ("mere
contact is how geometry normally meets"), and which is how a floor actually
bears on a wall.

THE INSET MUST COME OUT, or the two fixes miss each other: shortened walls plus
an inset slab leaves a band at the perimeter between (s+1)H - ft and (s+1)H with
neither wall nor floor in it. A hole. This patch reverts it in the same run so
the tree is never in that state.

INSTANCING IS PRESERVED, which is the constraint that decided the shape. The
change is UNIFORM -- every wall loses the same ft -- so segments stay identical
to each other and still link one mesh datablock. A 66-tile wall remains one mesh
with 66 transforms; the VRAM win is untouched, and so is the resolver's
one-import-per-slot.

ONE EDGE, named rather than discovered. ft is `roof_thick or floor_thick` for
the topmost slab and floor_thick elsewhere, so a spec that sets roof_thick gives
its top-storey walls a different height from the rest: two mesh datablocks
instead of one, in that building only. Bounded, and visible in Blender's
Outliner -> Blender File -> Meshes as a user count that splits.

THE RULE LIVES IN ONE PLACE. _cap_thick() is a method rather than the same
expression written twice, because two copies of a rule drift and this file's own
comments say so.

WHAT THIS DOES NOT FIX, and should not be expected to: parapet corners (16) and
the stair discharge (4). Different geometry, separate decisions, much smaller.
Expect cr_deli to land near 20, not 0.

Asserts every target, refuses on a miss, idempotent, byte-compiles.
"""
import pathlib
import py_compile
import shutil

ROOT = pathlib.Path(r"C:\Projects\gabagool_studios\gabagool_factory")
DC = ROOT / "deli_counter" / "deli_counter.py"

# ---- 1. revert the inset ---------------------------------------------------
INSET_OLD = '''            # THE SLAB STOPS AT THE WALL'S INNER FACE. A wall for storey s
            # spans [sH, (s+1)H] and the slab above spans [(s+1)H - ft,
            # (s+1)H], so at full footprint BOTH top faces landed on (s+1)H,
            # both facing up, interpenetrating through the whole slab. That is
            # a z-fight by definition, it repeated at every storey boundary
            # around every building, and zfight_gate found 363 of them in
            # cr_deli with 103 of 103 buildings affected.
            #
            # Insetting the slab rather than shortening the wall is deliberate:
            # wall height feeds the modular slot dims Zoo builds against and the
            # vertical placement of openings, and neither should move for a
            # rendering defect. Inset, the two top faces are edge-to-edge, and
            # the gate only flags real interpenetration.
            inset = 2.0 * self.s.wall_thick
            sx = max(self.s.footprint_x - inset, self.s.wall_thick)
            sy = max(self.s.footprint_y - inset, self.s.wall_thick)
            if not (is_roof and self.s.roof == "open"):
                self._box(f"slab_{s}", (0, 0, z - ft / 2),
                          (sx, sy, ft),
                          self.VISUAL, role=role)
'''

INSET_NEW = '''            # Full footprint. The slab is NOT inset: an earlier attempt shrank
            # it by a wall thickness to dodge the coincident top faces, which
            # reached only the perimeter walls and left every interior
            # partition fighting. Walls are capped under the slab instead --
            # see _cap_thick -- and an inset slab under a shortened wall would
            # leave a band at the perimeter with neither in it.
            if not (is_roof and self.s.roof == "open"):
                self._box(f"slab_{s}", (0, 0, z - ft / 2),
                          (self.s.footprint_x, self.s.footprint_y, ft),
                          self.VISUAL, role=role)
'''

COL_OLD = '''            # Collision follows the visual, or a body would stand on floor that
            # is not there -- and check_steps would not see it, because it reads
            # the built scene rather than comparing the two meshes.
            self._col_box(f"slab_col_{s}", (0, 0, z - ft / 2),
                          (sx, sy, ft),
                          mode="trimesh")
'''

COL_NEW = '''            self._col_box(f"slab_col_{s}", (0, 0, z - ft / 2),
                          (self.s.footprint_x, self.s.footprint_y, ft),
                          mode="trimesh")
'''

# ---- 2. the rule, in one place --------------------------------------------
HELPER_OLD = '''    def _exterior(self):
'''

HELPER_NEW = '''    def _cap_thick(self, story, top):
        """Thickness of the slab that caps `story` -- the one whose top face is
        the floor of story+1, so the wall below must stop at its underside.

        A wall spanning the full storey height puts its top face on the same
        plane as that slab's top face, both pointing up and interpenetrating:
        a z-fight at every storey boundary of every building. One rule, one
        place, because both wall emitters need it and two copies drift.
        """
        return ((self.s.roof_thick or self.s.floor_thick)
                if story + 1 == top else self.s.floor_thick)

    def _exterior(self):
'''

# ---- 3. exterior walls -----------------------------------------------------
EXT_OLD = '''        for s in range(base, top):
            z = s * H
            cz = z + H / 2
            wall_geo = {
                "N": ((0, hy, cz), (self.s.footprint_x, wt, H), 0),
                "S": ((0, -hy, cz), (self.s.footprint_x, wt, H), 0),
                "E": ((hx, 0, cz), (wt, self.s.footprint_y, H), 1),
                "W": ((-hx, 0, cz), (wt, self.s.footprint_y, H), 1),
            }
'''

EXT_NEW = '''        for s in range(base, top):
            z = s * H
            # Stop under the slab above, not at the storey line. Uniform across
            # every segment, so identical tiles still share one mesh datablock.
            wh = H - self._cap_thick(s, top)
            cz = z + wh / 2
            wall_geo = {
                "N": ((0, hy, cz), (self.s.footprint_x, wt, wh), 0),
                "S": ((0, -hy, cz), (self.s.footprint_x, wt, wh), 0),
                "E": ((hx, 0, cz), (wt, self.s.footprint_y, wh), 1),
                "W": ((-hx, 0, cz), (wt, self.s.footprint_y, wh), 1),
            }
'''

# ---- 4. interior partitions ------------------------------------------------
INT_OLD = '''    def _partitions(self):
        H, wt = self.s.story_height, self.s.wall_thick
        for i, p in enumerate(self.s.partitions):
            z = p.story * H
            cz = z + H / 2
'''

INT_NEW = '''    def _partitions(self):
        H, wt = self.s.story_height, self.s.wall_thick
        _base, _top = self._story_range()
        for i, p in enumerate(self.s.partitions):
            z = p.story * H
            # Same cap as the exterior: an interior wall reaching the storey
            # line puts its top face on the slab's, and 93 of cr_deli's
            # remaining 151 fights were exactly this pair.
            wh = H - self._cap_thick(p.story, _top)
            cz = z + wh / 2
'''

SIZE_OLD = '''            if p.axis == "Y":
                c = (p.pos, mid, cz)
                size = (wt, length, H)
                axis = 1
            else:
                c = (mid, p.pos, cz)
                size = (length, wt, H)
                axis = 0
'''

SIZE_NEW = '''            if p.axis == "Y":
                c = (p.pos, mid, cz)
                size = (wt, length, wh)
                axis = 1
            else:
                c = (mid, p.pos, cz)
                size = (length, wt, wh)
                axis = 0
'''

EDITS = [
    (INSET_OLD, INSET_NEW, "slab visual back to full footprint"),
    (COL_OLD, COL_NEW, "slab collision back to full footprint"),
    (HELPER_OLD, HELPER_NEW, "_cap_thick, the rule in one place"),
    (EXT_OLD, EXT_NEW, "exterior walls stop under the slab"),
    (INT_OLD, INT_NEW, "interior partitions get the same cap"),
    (SIZE_OLD, SIZE_NEW, "partition boxes use the capped height"),
]


def main() -> int:
    if not DC.exists():
        raise SystemExit(f"missing {DC}. Nothing written.")
    src = DC.read_text(encoding="utf-8")
    if "_cap_thick" in src:
        print("deli_counter.py: walls already stop under the slab")
        return 0
    if "inset = 2.0 * self.s.wall_thick" not in src:
        raise SystemExit("deli_counter.py has no slab inset to revert -- run "
                         "patch_slab_inset.py first, or this is not the file "
                         "this patch was written against. NOTHING WRITTEN.")
    done = []
    for old, new, label in EDITS:
        n = src.count(old)
        if n != 1:
            raise SystemExit(f"{label}: target appears {n} time(s), expected 1. "
                             f"NOTHING WRITTEN -- the file is untouched.")
        src = src.replace(old, new)
        done.append(label)
    for dead in ("inset = 2.0", "(sx, sy, ft)"):
        if dead in src:
            raise SystemExit(f"`{dead}` survives the revert, so the inset is "
                             f"only half removed. NOTHING WRITTEN.")

    backup = DC.with_suffix(".py.pre_cap")
    if not backup.exists():
        shutil.copy2(DC, backup)
    DC.write_text(src, encoding="utf-8")
    py_compile.compile(str(DC), doraise=True)
    print("applied:")
    for d in done:
        print(f"  deli_counter.py: {d}")
    print(f"  compiles; previous file kept at {backup.name}")
    print("\n  cr_deli: 363 before anything, 151 after the inset. Expect about "
          "20 now --\n  the parapet corners and the stair discharge, which this "
          "does not touch.\n")
    print("    python build.py specs\\cr_deli.json")
    print('    python -c "import zfight_gate as z; b=z._node_world_boxes('
          "r'build\\cr_deli.glb'); v,s=z.visible_fights(b); "
          "print(len(v),'visible',len(s),'entombed')\"")
    print("\n  Then the two things that could have broken quietly:")
    print("    - slots: cr_deli emitted 320 before; the count should hold and "
          "every\n      height should be lower by one slab thickness.")
    print("    - openings: nothing should now extend past the top of its wall.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
