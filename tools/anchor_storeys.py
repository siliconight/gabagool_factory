"""Which plane does each dressing anchor measure from -- the storey, or the building?

WHAT THIS IS FOR. Patina's anchor pass emits the four dressing families the
walkthrough kept flagging as "dressing all over in a way that doesn't look
good":

    roofline        -> Cover_edge_strip     "along the top edge of each wall"
    wall_base       -> Cover_base_course    "along the foot of each wall"
    exterior_light  -> Cover_conduit_run    "above exterior doors"
    ground_edge     -> Cover_curb           "where walls meet the ground"

Every one of those phrases names a reference plane, and none of them is checked
anywhere. This prints the segment extents the pass derives and the anchor
heights that fall out of them, side by side with the building's actual floor
planes, so the question "measured from what?" has an instrument.

    python tools\\anchor_storeys.py <shell.glb> [<shell.glb> ...]

RETRACTED FIRST DRAFT, kept because the wrong number was believable. The first
version omitted ``scene.bake_visual_transforms()``. Patina's Scene holds each
node's world matrix on ``Mesh.transform`` and leaves ``Primitive.positions`` in
LOCAL space until that call folds it in; ``cli.py:75`` makes the call before any
pass runs. Without it every module reads at its own origin -- slab_-1, slab_0,
slab_1 and slab_2 all reported the same AABB -- and the building collapsed from
44 x 13 x 32 m to 44 x 4 x 32 m, which looked exactly like a dropped-transform
bug in the pipeline. It was the instrument. This version matches the CLI's
ordering: load, bake, detect up axis, classify, then measure.

WHAT IT MEASURES, AND IN WHAT FRAME. Anchor math is written Z-up; the pass
permutes a Y-up DC export into that canonical frame, computes, and permutes
back (``anchors._up_to_z`` / ``_z_to_up``). This reads the canonical Z-up view,
which is the frame the placement decisions are actually made in -- reading the
output frame instead would show you where anchors ended up but not what they
were measured against.

HOW TO READ THE SEGMENT TABLE. One row is one exterior-wall segment as
``_wall_segments`` buckets them: by wall plane, keyed ``(axis, side,
round(fixed, 1))``. Every storey of one facade shares that plane. So a row whose
``z_lo``..``z_hi`` spans more than one storey height is the finding: it means
"the foot of the wall" and "the top of the wall" are the bottom and top of the
WHOLE BUILDING, and `wall_base`, `ground_edge` and `exterior_light` are all
being placed against a plane no player will ever stand on.

Compare the printed anchor heights against the FLOOR planes below them. A curb
belongs at the storey the street is on; a base course belongs at the foot of a
storey you can see.

WHAT A NONZERO EXIT MEANS. A file could not be read or carried no exterior-wall
faces. An empty result is never reported as "no anchors needed".
"""
import sys

import numpy as np

from patina import anchors, gltf_io, slots, surfaces
from patina.mesh import SurfaceRole


def floor_planes(scene):
    """Every FLOOR face's height in the canonical Z-up view, deduped to cm."""
    zs = []
    for m in scene.visual_meshes():
        for p in m.primitives:
            if p.face_roles is None:
                continue
            tris = p.positions[p.indices]
            for t, r in enumerate(p.face_roles):
                if r == SurfaceRole.FLOOR:
                    zs.append(float(tris[t][:, 2].mean()))
    return sorted({round(z, 2) for z in zs}), len(zs)


def report(path):
    scene = gltf_io.load_glb(path)
    scene.bake_visual_transforms()          # cli.py:75 -- world-space metres
    up = slots.detect_up_axis(scene)
    surfaces.classify(scene, up_axis=up)

    print("=" * 72)
    print("%s   up_axis=%s" % (path.replace("\\", "/").split("/")[-1], "XYZ"[up]))
    print("roles:", surfaces.role_counts(scene))

    saved = [(p, p.positions)
             for m in scene.visual_meshes() for p in m.primitives]
    for p, _pos in saved:
        p.positions = anchors._up_to_z(p.positions, up)
    try:
        segs = list(anchors._wall_segments(scene))
        planes, nfaces = floor_planes(scene)
        found = anchors._generate_zup(scene, anchors.AnchorOptions(), seed=1999)
    finally:
        for p, pos in saved:
            p.positions = pos

    if not segs:
        print("NO exterior-wall segments -- nothing measured, not 'nothing to do'")
        return False

    print()
    print("EXTERIOR WALL SEGMENTS (canonical Z-up), %d found" % len(segs))
    print("%5s %8s %9s %9s %9s %9s %9s"
          % ("axis", "plane", "a_min", "a_max", "z_lo", "z_hi", "z_span"))
    for s in sorted(segs, key=lambda s: (s["axis"], s["fixed"])):
        print("%5d %8.2f %9.2f %9.2f %9.2f %9.2f %9.2f"
              % (s["axis"], s["fixed"], s["a_min"], s["a_max"],
                 s["z_lo"], s["z_hi"], s["z_hi"] - s["z_lo"]))

    print()
    if planes:
        # Deliberately NOT estimating a storey height from the gaps between
        # floor planes: the nuance pass densifies floors, so consecutive gaps
        # measure triangle size, not architecture (852 faces at 63 distinct
        # heights on a 4-storey shell). The floor-plane RANGE needs no such
        # guess -- it is the vertical extent of every walkable surface in the
        # building, and a wall segment covering it covers every storey at once.
        span = planes[-1] - planes[0]
        print("FLOOR planes (%d faces, %d distinct): %s%s"
              % (nfaces, len(planes), planes[:10],
                 " ..." if len(planes) > 10 else ""))
        print("lowest %.2f   highest %.2f   full range %.2f"
              % (planes[0], planes[-1], span))
        tall = [s for s in segs if span > 0 and s["z_hi"] - s["z_lo"] >= span]
        if tall:
            print()
            print("%d of %d segments span the whole floor range. For those, "
                  "'the foot of the\nwall' and 'the top of the wall' are the "
                  "bottom and top of the BUILDING --\nevery storey's dressing "
                  "is measured against a plane only one storey has."
                  % (len(tall), len(segs)))
    else:
        print("FLOOR planes: none classified -- no walkable extent to compare")

    print()
    print("%-16s %5s %9s %9s   %s" % ("anchor kind", "n", "z_min", "z_max",
                                      "placed at"))
    where = {"roofline": "seg z_hi", "wall_base": "seg z_lo",
             "ground_edge": "seg z_lo",
             "exterior_light": "z_lo + 0.75*(z_hi-z_lo)"}
    for kind in anchors.ANCHOR_KINDS:
        zs = [a.pos[2] for a in found if a.kind == kind]
        if zs:
            print("%-16s %5d %9.2f %9.2f   %s"
                  % (kind, len(zs), min(zs), max(zs), where.get(kind, "?")))
    return True


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv:
        sys.stderr.write(__doc__.splitlines()[0] + "\n"
                         "usage: anchor_storeys.py <shell.glb> [...]\n")
        return 2
    ok = 0
    for path in argv:
        try:
            ok += bool(report(path))
        except (OSError, ValueError, KeyError) as exc:
            sys.stderr.write("unreadable: %s: %s\n" % (path, exc))
    return 0 if ok else 2


if __name__ == "__main__":
    sys.exit(main())
