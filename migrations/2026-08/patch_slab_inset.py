"""Slabs stop at the wall's inner face, so their top faces stop coinciding.

THE DEFECT, measured by this repo's own gate rather than argued.

    python -c "import zfight_gate as z; b=z._node_world_boxes('build/cr_deli.glb'); ..."
    458 solids -> 363 VISIBLE fights, 38 suppressed as entombed
    slab_0 <-> ext_-1_N_seg0  axis 1 max area 0.35     (and 362 more like it)

Across the built library: **103 of 103 buildings, none clean**, 410 in the worst.

THE ARITHMETIC, from deli_counter.py itself:

    slab_{s}    centre z - ft/2, height ft   ->  spans [sH - ft, sH]
    ext_{s}_*   cz = z + H/2,    height H    ->  spans [sH, (s+1)H]

So the wall for storey s and the slab for storey s+1 BOTH end at (s+1)H, both
top faces, both pointing up, interpenetrating through the full slab thickness
wherever the wall sits inside the footprint. Two coincident visible surfaces is
what a z-fight IS. It repeats at every storey boundary, all the way round.

It is also exactly where it was seen in play: the flicker is at the floor-to-
wall junction, because that is where the two surfaces are.

WHY THE GATE NEVER CAUGHT IT. zfight_gate.check_package() walks a COMPOSED
package and only inspects refs under art/zoo/ -- it gates the art path. A raw
Deli Counter greybox build never passes through it. The gate is correct, it is
unit-tested, and it had never been pointed at the buildings it would fail.

WHY INSET THE SLAB RATHER THAN SHORTEN THE WALL. Both remove the coincidence.
Shortening the wall to (s+1)H - ft is closer to how real construction reads, but
wall height feeds two contracts: the modular slot dimensions Zoo builds modules
against, and the vertical placement of openings. Changing it would invalidate
every kit module and risk clipping a door near the top of a wall. The slab
stopping at the wall's inner face changes neither -- the two top faces become
edge-to-edge instead of overlapping, and the gate only ever flags real
interpenetration ("mere contact is how geometry normally meets").

WHAT THIS DOES NOT ADDRESS, said out loud rather than discovered later:

  * `_record_roof_slots` derives its slots from self.s.footprint, so the roof's
    swap-slots still describe the full footprint while the roof mesh is now
    inset by a wall thickness. A perimeter band the wall already occupies. Worth
    reconciling when the Zoo roof pass is next touched; not worth a second edit
    in the same patch.
  * Stair, ramp and hatch holes are boolean-cut against the slab. They are
    interior by construction, so an inset of one wall thickness should not reach
    them -- but "should not" is why the gate gets re-run per building rather
    than trusted.

VERIFY ON ONE BUILDING BEFORE THE LIBRARY. cr_deli is the reference: 363 visible
fights today. Rebuild it and re-run the gate. If it does not fall to zero, read
what is left before rebuilding anything else -- a remainder means there is a
second source of coincident faces this patch does not touch.

Asserts every target, refuses on a miss, idempotent, byte-compiles.
"""
import pathlib
import py_compile
import shutil

ROOT = pathlib.Path(r"C:\Projects\gabagool_studios\gabagool_factory")
DC = ROOT / "deli_counter" / "deli_counter.py"

VIS_OLD = '''            if not (is_roof and self.s.roof == "open"):
                self._box(f"slab_{s}", (0, 0, z - ft / 2),
                          (self.s.footprint_x, self.s.footprint_y, ft),
                          self.VISUAL, role=role)
'''

VIS_NEW = '''            # THE SLAB STOPS AT THE WALL'S INNER FACE. A wall for storey s
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

COL_OLD = '''            self._col_box(f"slab_col_{s}", (0, 0, z - ft / 2),
                          (self.s.footprint_x, self.s.footprint_y, ft),
                          mode="trimesh")
'''

COL_NEW = '''            # Collision follows the visual, or a body would stand on floor that
            # is not there -- and check_steps would not see it, because it reads
            # the built scene rather than comparing the two meshes.
            self._col_box(f"slab_col_{s}", (0, 0, z - ft / 2),
                          (sx, sy, ft),
                          mode="trimesh")
'''


def main() -> int:
    if not DC.exists():
        raise SystemExit(f"missing {DC}. Nothing written.")
    src = DC.read_text(encoding="utf-8")
    if "inset = 2.0 * self.s.wall_thick" in src:
        print("deli_counter.py: slabs already inset by the wall thickness")
        return 0
    for probe in ('self._box(f"slab_{s}"', 'self._col_box(f"slab_col_{s}"'):
        if probe not in src:
            raise SystemExit(f"deli_counter.py has no `{probe}` -- this is not "
                             f"the file this patch was written against. "
                             f"NOTHING WRITTEN.")
    done = []
    for old, new, label in ((VIS_OLD, VIS_NEW, "the visual slab is inset"),
                            (COL_OLD, COL_NEW, "the collision slab follows it")):
        n = src.count(old)
        if n != 1:
            raise SystemExit(f"{label}: target appears {n} time(s), expected 1. "
                             f"NOTHING WRITTEN -- the file is untouched.")
        src = src.replace(old, new)
        done.append(label)

    backup = DC.with_suffix(".py.pre_inset")
    if not backup.exists():
        shutil.copy2(DC, backup)
    DC.write_text(src, encoding="utf-8")
    py_compile.compile(str(DC), doraise=True)
    print("applied:")
    for d in done:
        print(f"  deli_counter.py: {d}")
    print(f"  compiles; previous file kept at {backup.name}")
    print("\n  ONE BUILDING FIRST. cr_deli is the reference at 363 visible "
          "fights:\n")
    print("    python build.py specs\\cr_deli.json")
    print('    python -c "import zfight_gate as z; b=z._node_world_boxes('
          "r'build\\cr_deli.glb'); v,s=z.visible_fights(b); "
          "print(len(v),'visible',len(s),'entombed')\"")
    print("\n  Expect 0 visible. A remainder is a SECOND source of coincident "
          "faces that\n  this patch does not touch -- read it before rebuilding "
          "anything else.\n")
    print("  Then walk it. The flicker was at the floor-to-wall junction, which "
          "is\n  exactly the geometry this moves, so the eye is the other half "
          "of the check.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
