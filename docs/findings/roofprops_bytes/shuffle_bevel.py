"""Inside Blender: does Zoo's bevel make one sphere one way, whatever order its faces were laid in (roadmap 247)?

    blender -b --factory-startup --python docs/findings/roofprops_bytes/shuffle_bevel.py [-- <zoo root>]

One process. Six times: the satellite dish's bowl as `recipes/satellite_dish` asks for it (`geometry.add_ellipsoid`,
radii (0.3, 0.066, 0.3), 12 by 6 -- flat enough front to back that the bevel takes its rim), its faces laid in a
shuffled order (`BMElemSeq.sort` by a seeded permutation, what a fresh process does to `create_uvsphere`'s faces),
then `geometry.bm_to_object` with a 1 cm bevel. Three ways:

  as_laid          the bevel takes the faces as shuffled
  sorted_first     the faces put back in `in_one_order`'s order before the bevel
  restarted_after  every face remade to start at its lowest vertex just after the bevel (`start_at_lowest`)

Prints, per way, each build's vertex digest, face digest (each face's vertex indices as stored, in stored order) and
counts. The counts say whether the bevel ran at all: 62 vertices and 72 faces are the sphere unbevelled, and a first
version of this check, which scaled the vertices by hand and left the face normals stale, never bevelled and read
"one way" for nothing. Prints what it measured; it names no cause.
"""
import hashlib
import os
import random
import sys

F = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
ZOO = sys.argv[sys.argv.index("--") + 1] if "--" in sys.argv and len(sys.argv) > sys.argv.index("--") + 1 \
    else os.path.join(F, "zoo")
sys.path.insert(0, ZOO)

import bmesh  # noqa: E402
import bpy  # noqa: E402

from zoo_keeper.bpylayer import geometry  # noqa: E402

RADII = (0.3, 0.066, 0.3)
_bevel = geometry.bevel_edges


def _h(x):
    return hashlib.sha256(repr(x).encode()).hexdigest()[:8]


def build(seed, way):
    bm = bmesh.new()
    geometry.add_ellipsoid(bm, (0.0, 0.0, 0.0), RADII, u_seg=12, v_seg=6)
    bm.faces.index_update()
    order = list(range(len(bm.faces)))
    random.Random(seed).shuffle(order)
    bm.faces.sort(key=lambda f: order[f.index])
    if way == "sorted_first":
        bm.faces.index_update()
        rank = [0] * len(bm.faces)
        for i, f in enumerate(geometry.in_one_order(bm, list(bm.faces))):
            rank[f.index] = i
        bm.faces.sort(key=lambda f: rank[f.index])
    if way == "restarted_after":
        def bevel_then_restart(bm_, offset, *a, **k):
            _bevel(bm_, offset, *a, **k)
            geometry.start_at_lowest(bm_, list(bm_.faces))
        geometry.bevel_edges = bevel_then_restart
    try:
        col = bpy.data.collections.new("shuffle_%s_%d" % (way, seed))
        me = geometry.bm_to_object(bm, "Bowl_%s_%d" % (way, seed), col, bevel=0.01, texel=1.0).data
    finally:
        geometry.bevel_edges = _bevel
    verts = [tuple(round(c, 6) for c in v.co) for v in me.vertices]
    faces = [tuple(p.vertices) for p in me.polygons]
    return "%s/%s %dv %df" % (_h(verts), _h(faces), len(verts), len(faces))


for way in ("as_laid", "sorted_first", "restarted_after"):
    made = [build(seed, way) for seed in range(6)]
    print("SHUFFLE_BEVEL %-16s %d way(s): %s" % (way, len(set(made)), "  ".join(made)))
