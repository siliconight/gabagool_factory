"""Roadmap batch 37, 2026-09-12: the walker's two questions on the 9012 bank
-- 18 REPLACE (old kept; the census's refutation of finding (1) is
retracted) and 151 filed and closed (APPEND: outdoor clutter on interior
floors). Asserts every anchor.
"""
import io
import sys

P = "PIPELINE_ROADMAP.md"

OLD_18 = """*STATUS: NARROWED 2026-09-11 (evening) -- THE RE-WALK COPY IS BUILT FROM A
COLD EXPORT, THE FIXES ARE MEASURED ON IT, AND A CONFOUND IN THE DAY'S OWN
MEASUREMENTS IS NAMED."""

NEW_18 = """*STATUS: NARROWED 2026-09-12 (late) -- THE WALKER WAS RIGHT ABOUT THE
ROTATED PIECES, THE CENSUS WAS BLIND TO THEM, AND A GATE HAD BEEN SAYING SO
IN EVERY COLD PACKAGE SINCE 9001. Two questions on cold run 9012's bank
frames. (1) "this rotation looks wrong? (opening in the building)" -- a
narrow panel standing out from the wall beside a doorway. MEASURED off the
composed scene, not the frame: `int_0_1_seg1`, a `wallEnd` remainder on a
wall that runs along Y (slot rot_y 90, scale [1.875, 0.3, 3.3]), placed
with a scale-only basis -- 1.875 m along X, ACROSS its wall -- while every
full segment beside it carried the turn; 18 such pieces in the bank, 237
of 777 wallEnd nodes across the cold packages on disk (9001-9012), every
one on a turned wall. THE REFUTATION RETRACTED: the 2026-09-11 status
below records finding (1), "pieces that looked rotated", as NOT REPRODUCED
by `module_pose_census` (443 of 443 judged correct on 9005). The census
compared the SORTED horizontal extents -- "module-local, so the rotation
does not matter to the set" -- and a remainder across its wall has the
same sorted extents as one along it. The walker saw it on 9005 and again
on 9012; the instrument could not. It now judges the footprint in world
axes and reports the pose as `across` (18 on the 9012 bank, where the
sorted version said 0). Fixed at the source, DC 0.120.0: `godot_basis`
applied a remainder's scale in world axes after the rotation while
`_volumes` emits it in the module's frame, and `_fit_rotation` fitted the
unscaled unit cube, which ties at every angle and answers 0 -- two seams
that cancel at 0 degrees and stack at 90. Recomposed: 0 across. THE THIRD
SHAPE: Deli Counter's `verify_placement` NAMED those eighteen slots in
9012's compose manifest, the driver printed `placement gate [MISMATCH]:
224/242` and returned 0 (9005: 400 of 430), the adapter filed a moderate
advisory in the validation file, and the run was counted a zero -- item
133's z-fight shape again, an instrument that fired and nothing read it.
LF 0.74.0: the finding blocks and names the slots; on DC 0.120.0 the three
9012 shells pass 242/242, 212/212, 158/158. (2) "are these grey blobs the
surface dressing?" -- they were; item 151. THE INSTRUMENT SCORE, revised:
of the 2026-09-11 walk's eight findings, one that was scored "refuted by
an instrument" was real and had been reported by a different instrument
nobody read. Previously: THE RE-WALK COPY IS BUILT FROM A
COLD EXPORT, THE FIXES ARE MEASURED ON IT, AND A CONFOUND IN THE DAY'S OWN
MEASUREMENTS IS NAMED."""

APPEND = """
*STATUS: CLOSED 2026-09-12 (late) -- LOT 0.56.0 DECLARES THE SEAM AS A BAND
AND THE FLOOR PLAN AS AN EXCLUSION; 185 PIECES OF OUTDOOR CLUTTER ON THE
BANK'S CARPET ACCOUNTED FOR, ZONE BY ZONE, AND NONE OF THEM ALLOWED NOW*

**151. Outdoor ground clutter was scattered on interior floors, because
nothing had said a floor plan is not ground.** The walker, on cold run
9012's bank lobby: "are these grey blobs the surface dressing?" They were:
Patina's `surface_dressing` (item 110's layer, connected 2026-09-11)
placed 185 of its 3,643 pieces -- pebbles, litter scraps, rubble, weed
tufts -- inside `bank_branch_a03`'s footprint at z = 0, on the carpet, and
every one was allowed by a zone Lot declared. ATTRIBUTED, every item:
159 from `wall_base_b0`, which was `grow(footprint, band)` -- the whole
30 x 22 m plan plus one agent radius, called a seam; 17 from
`open_ground`, the plate remainder, which is the whole plate; 9 from the
`path_b0_b1` corridor, whose first box is centred on the objective marker
-- the building's centre. The only exclusions were the spawn and objective
circles. Lot's `site_surfaces` is the owner (it declares, Patina only
honours). Lot 0.56.0: the wall base is the four strips of the grown box
MINUS the plan (`_annulus_strips`, the shape the perimeter already used),
`wall_base_<id>_0..3`, and no square metre of a plan is in any of them;
`exclusions()` emits one `building` box per footprinted building, which
Patina's `excluded()` already honoured for `aabb` entries, so nothing
downstream changed; the schema gains the tag (LF 0.74.0). Interiors are
Deli Counter's layer, dressed at the shell's request. Tests hold both
shapes against the pawn-job fixture (399 pass). What this does not do:
say what a bank lobby SHOULD have on its floor -- that is item 44's set
dressing, and the answer is not pebbles.
"""


def main() -> int:
    raw = io.open(P, "rb").read()
    if b"\r\n" in raw:
        print("roadmap has CRLF endings -- stop", file=sys.stderr)
        return 1
    text = raw.decode("utf-8")
    if text.count(OLD_18) != 1:
        print(f"18 anchor matched {text.count(OLD_18)} times; refusing", file=sys.stderr)
        return 1
    if "\n**151. " in text:
        print("item 151 already present", file=sys.stderr)
        return 1
    text = text.replace(OLD_18, NEW_18, 1)
    text = text.rstrip("\n") + "\n" + APPEND.rstrip("\n") + "\n"
    out = text.encode("utf-8")
    io.open(P, "wb").write(out)
    print(f"wrote {len(out)} bytes ({len(raw)} before); 18 updated, 151 filed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
