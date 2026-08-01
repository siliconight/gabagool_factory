"""The kerb goes under the step ceiling, and the whole slab stack lies flat.

WHAT THE PROBE MEASURED. coldrun_kerb_probe put six paths across one road at
90, 75, 60, 45, 30 and 20 degrees. Two results:

  1. The angle-aware kerb cut is CORRECT. Predicted (w + d*|cos t|)/sin t gave
     13.196 m at 30 deg and 19.938 m at 20 deg; Lot reported 13.2 and 19.9, at
     two independent crossings each. Nothing to fix there -- a shallow crossing
     genuinely has to eat that much kerb, and LOT_KERB_CROSSED_SHALLOW already
     says so and tells you to re-route.

  2. LOT_STEP_NEEDS_ASSIST fired on ground -> sidewalk: 0.16 m against a
     0.1025 m ceiling. A stock CharacterBody3D meets a kerb as a WALL.

THE SECOND ONE IS THE DEFECT, AND IT INVERTED ITS OWN INTENT. SIDEWALK_H was a
picked 0.16 carrying the comment "a kerb is MEANT to be a wall". But
lot_player.gd implements step-up, so the kerb never walled OUR player. It walled
a stock controller -- which is exactly what every recipient of a site pack has.
The wall only ever stopped the person we ship to, which is the opposite of the
standalone contract the whole toolchain is written against.

THE STACK COLLAPSES ONCE THE KERB IS MOUNTABLE. The old band existed because a
0.16 kerb needed a half-step: slabs had to sit in [SIDEWALK_H - step, step], so
paths stood 0.08 proud of the ground with roads and courtyards 1.6 cm either
side. Put the kerb under STEP_MAX and bare ground mounts it directly, so slabs
stop being a step to anything and can lie flat.

    before                              after
      kerb        0.1600                  0.0974   = STEP_MAX * 0.95
      courtyard   0.0958                  0.0140
      path        0.0800                  0.0120
      road        0.0643                  0.0100
      ground      0.0000                  0.0000

Every adjacent pair now clears the ceiling with room: ground->kerb 0.0974,
kerb->path 0.0854, path->road 0.0020. The 1.6 cm path-over-road lip that no
traversal gate could see is gone, and so is the reason a recipient needs custom
step-up code.

WHY NOT EXACTLY ZERO. Two coplanar faces z-fight where a path crosses a road.
The 2 mm tiers exist to separate them and for no other reason. Against a 103 mm
step ceiling that is not a step, and check_steps will not see it.

WHY 95% AND NOT 100%. A rise exactly equal to STEP_MAX puts the contact normal
exactly on floor_max_angle. Shipping physics that sits on a boundary is how a
thing works on one machine and not the next.

THE GUARD IS RE-AIMED, NOT DELETED. LOT_SURFACE_STACK_IMPOSSIBLE tested
SLAB_LO > SLAB_HI, which SIDEWALK_H <= STEP_MAX makes unreachable -- and a check
that cannot fail is indistinguishable from one that passed. It becomes
LOT_KERB_ABOVE_STEP, testing the invariant this file now actually rests on.

EXPECT THE LIBRARY TO MOVE. Every site's kerbs and surfaces change height, so
re-run the sweep and check_steps before believing anything. LOT_STEP_NEEDS_ASSIST
should disappear across the board; if a site gains a new step finding, read it
rather than assuming this patch is fine.

Asserts every target, refuses on a miss, idempotent, byte-compiles.
"""
import pathlib
import py_compile
import shutil

ROOT = pathlib.Path(r"C:\Projects\gabagool_studios\gabagool_factory")
LOT = ROOT / "lot" / "lot.py"

BAND_OLD = '''# The walkable slab thicknesses are DERIVED, not picked. A capsule walks up a
# step only while the contact normal stays inside floor_max_angle, which for the
# contract player is clearances.unassisted_step_max_m. Every adjacent pair of
# outdoor surfaces has to clear that in BOTH directions, and the sidewalk is on
# the other side of each slab:
#
#     ground 0.00  -> slab                    slab <= step
#     slab         -> sidewalk SIDEWALK_H     SIDEWALK_H - slab <= step
#
# so a walkable slab is squeezed into [SIDEWALK_H - step, step]. The picked
# values had drifted out of it: COURT_THICK was 0.12 against a step limit of
# 0.1025, which walled the courtyard edge on ballpark_block's own circulation,
# and PATH_THICK 0.10 was inside by 2.5 mm. Fixed fractions of the band keep the
# surfaces ordered and visually distinct and move them together when the
# gameplay team picks a different body.
GROUND_THICK = 0.5
WALL_THICK = 0.3
COVER = (1.0, 1.0, 1.0)
ROAD_COLOR = (0.13, 0.13, 0.14)        # asphalt
SIDEWALK_H = 0.16                      # a kerb is MEANT to be a wall
SIDEWALK_COLOR = (0.55, 0.55, 0.57)    # concrete, raised curb

#: The tallest step the contract player walks up with no step-up code.
STEP_MAX = float(_agent()["clearances"]["unassisted_step_max_m"])
#: Legal band for a slab walkable from the ground AND onto the sidewalk beside
#: it. Empty when the kerb is taller than two steps -- _outdoor_nodes says so
#: out loud rather than emitting a wall and letting play discover it.
SLAB_LO = SIDEWALK_H - STEP_MAX
SLAB_HI = STEP_MAX


def _slab(frac):
    """A walkable slab thickness at `frac` across the legal band."""
    if SLAB_LO > SLAB_HI:
        return round(SLAB_HI * 0.8, 4)
    return round(SLAB_LO + (SLAB_HI - SLAB_LO) * frac, 4)


ROAD_THICK = _slab(0.15)
PATH_THICK = _slab(0.50)
COURT_THICK = _slab(0.85)
'''

BAND_NEW = '''# Outdoor surface heights are DERIVED, and the derivation changed once the kerb
# probe measured what the previous one cost.
#
# THE OLD SHAPE. SIDEWALK_H was a picked 0.16 carrying the comment "a kerb is
# MEANT to be a wall". A capsule walks up a step only while the contact normal
# stays inside floor_max_angle, so it clears STEP_MAX and no more -- 0.16 sits
# above that, making the kerb unclimbable from bare ground by design. Slabs then
# had to live in [SIDEWALK_H - step, step] so they could serve as a half-step
# onto it, which is why paths stood 0.08 proud of the ground with roads and
# courtyards 1.6 cm either side.
#
# WHY THAT WAS WRONG, measured rather than argued. lot_player.gd implements
# step-up, so the kerb never walled OUR player. It walled a stock
# CharacterBody3D -- which is what every recipient of a site pack has. The wall
# only ever stopped the person we ship to. coldrun_kerb_probe made it explicit:
# LOT_STEP_NEEDS_ASSIST on ground -> sidewalk, 0.16 m against a 0.1025 m
# ceiling, on a level that walks perfectly inside this repo.
#
# THE NEW SHAPE. Put the kerb under the step ceiling and the stack collapses:
# bare ground mounts the kerb, so slabs stop being a half-step to anything and
# can lie flat. Every outdoor surface becomes reachable by a stock controller
# with no step-up code -- which is what the standalone contract needs -- and
# every lip on the site goes, including the 1.6 cm path-over-road lip that no
# traversal gate could see.
GROUND_THICK = 0.5
WALL_THICK = 0.3
COVER = (1.0, 1.0, 1.0)
ROAD_COLOR = (0.13, 0.13, 0.14)        # asphalt
SIDEWALK_COLOR = (0.55, 0.55, 0.57)    # concrete, raised curb

#: The tallest step the contract player walks up with no step-up code.
STEP_MAX = float(_agent()["clearances"]["unassisted_step_max_m"])

#: A kerb the contract body mounts from bare ground, with margin rather than at
#: the limit: a rise exactly equal to STEP_MAX puts the contact normal exactly
#: on floor_max_angle, and shipping physics that sits on a boundary is how a
#: thing works on one machine and not the next.
KERB_FRACTION = 0.95
SIDEWALK_H = round(STEP_MAX * KERB_FRACTION, 4)

#: Flush -- but not zero. Two coplanar faces z-fight where a path crosses a
#: road, so these tiers exist to separate them and for no other reason. 2 mm
#: against a ~103 mm step ceiling is not a step, and check_steps will not see
#: it. The ordering (road lowest, courtyard highest) is kept so overlaps
#: resolve the way a reader expects.
SURFACE_BASE = 0.010
SURFACE_TIER = 0.002
ROAD_THICK = SURFACE_BASE
PATH_THICK = SURFACE_BASE + SURFACE_TIER
COURT_THICK = SURFACE_BASE + 2 * SURFACE_TIER
'''

GUARD_OLD = '''    if SLAB_LO > SLAB_HI:
        # No slab thickness is walkable in both directions. Emitting anyway and
        # staying quiet is how a wall reaches play; four defects in this pass
        # were a check going silent.
        print(f"[lot] LOT_SURFACE_STACK_IMPOSSIBLE: climbing a {SIDEWALK_H} m "
              f"kerb from the ground needs two steps of {STEP_MAX:.4f} m, so no "
              f"slab thickness clears both. Lower SIDEWALK_H below "
              f"{2 * STEP_MAX:.3f} m, or the body has to get wider.")
'''

GUARD_NEW = '''    if SIDEWALK_H > STEP_MAX:
        # RE-AIMED, not deleted. The old test asked whether the half-step band
        # had collapsed, which a kerb under the step ceiling makes unreachable
        # -- and a check that cannot fail is indistinguishable from one that
        # passed. This is the invariant
        # the flat surfaces above actually rest on: if the kerb ever climbs back
        # over the step ceiling, they become unreachable and nothing else here
        # would notice.
        print(f"[lot] LOT_KERB_ABOVE_STEP: the {SIDEWALK_H:.4f} m kerb is taller "
              f"than the {STEP_MAX:.4f} m a contract body walks up unassisted, "
              f"so a stock CharacterBody3D cannot leave the road except at a "
              f"crossing. The flat surfaces assume it can. Lower SIDEWALK_H, or "
              f"put the slabs back on a half-step band.")
'''


def main() -> int:
    if not LOT.exists():
        raise SystemExit(f"missing {LOT}. Nothing written.")
    src = LOT.read_text(encoding="utf-8")
    if "KERB_FRACTION" in src:
        print("lot.py: the kerb already sits under the step ceiling")
        return 0
    for name in ("SLAB_LO", "_slab(", "SIDEWALK_H = 0.16"):
        if name not in src:
            raise SystemExit(f"lot.py has no `{name}` -- this is not the file "
                             f"this patch was written against. NOTHING WRITTEN.")
    done = []
    for old, new, label in ((BAND_OLD, BAND_NEW, "flat surfaces, kerb under the step ceiling"),
                            (GUARD_OLD, GUARD_NEW, "the guard re-aimed at SIDEWALK_H > STEP_MAX")):
        n = src.count(old)
        if n != 1:
            raise SystemExit(f"{label}: target appears {n} time(s), expected 1. "
                             f"NOTHING WRITTEN.")
        src = src.replace(old, new)
        done.append(label)

    for dead in ("SLAB_LO", "SLAB_HI", "_slab("):
        if dead in src:
            raise SystemExit(
                f"`{dead}` still appears after the rewrite, so something else "
                f"reads it and would now be undefined. NOTHING WRITTEN -- the "
                f"file on disk is untouched.")

    backup = LOT.with_suffix(".py.pre_flat")
    if not backup.exists():
        shutil.copy2(LOT, backup)
    LOT.write_text(src, encoding="utf-8")
    py_compile.compile(str(LOT), doraise=True)
    print("applied:")
    for d in done:
        print(f"  lot.py: {d}")
    print(f"  compiles; previous file kept at {backup.name}")
    print("\n  Every site's kerbs and surfaces change height, so nothing is "
          "believable until\n  the geometry is rebuilt. Smallest honest check "
          "first -- the probe itself:\n")
    print("    cd lot")
    print("    python cater.py specs\\coldrun_kerb_probe.json "
          "\"..\\_runs\\kerb_probe_flat\"")
    print("\n  LOT_STEP_NEEDS_ASSIST should be gone. LOT_KERB_CROSSED_SHALLOW "
          "should NOT be --\n  the cut is angle-driven and this changes only "
          "heights. Then the library:\n")
    print("    python tools\\library_walk.py --timeout 1800")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
