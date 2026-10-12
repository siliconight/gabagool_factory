"""Does Blender's own `bmesh.ops.create_uvsphere` lay its faces in the same order every process?
No Zoo code: a fresh bmesh, the sphere the pendant bulb asks for (u 10, v 6), then the same with
`bmesh.ops.bisect_plane` keeping the upper half as Zoo's hemisphere helper does, its geometry given
in storage order. Prints a digest of the vertices and of the faces' corner sequences, in storage
order and sorted. Run it in several Blender processes and compare the lines:

    blender --background --python docs/findings/grader_speed/uvsphere_order_probe.py
"""
import hashlib

import bmesh


def digest(bm):
    bm.verts.index_update()
    verts = [tuple(round(c, 6) for c in v.co) for v in bm.verts]
    faces = [tuple(v.index for v in f.verts) for f in bm.faces]
    h = lambda x: hashlib.sha256(repr(x).encode()).hexdigest()[:12]
    return "verts %s faces in order %s faces sorted %s (%d verts, %d faces)" % (
        h(verts), h(faces), h(sorted(faces)), len(verts), len(faces))


bm = bmesh.new()
bmesh.ops.create_uvsphere(bm, u_segments=10, v_segments=6, radius=1.0)
print("UVSPHERE_ORDER uvsphere", digest(bm))
bm.free()

bm = bmesh.new()
ret = bmesh.ops.create_uvsphere(bm, u_segments=20, v_segments=10, radius=1.0)
geom = list(bm.verts) + list(bm.edges) + list(bm.faces)
bmesh.ops.bisect_plane(bm, geom=geom, dist=1e-5, plane_co=(0, 0, 0), plane_no=(0, 0, 1), clear_inner=True)
print("UVSPHERE_ORDER hemisphere_storage_order", digest(bm))
bm.free()


def capped(sort_rim):
    """The dome's glass: the hemisphere, its rim closed by `holes_fill`, the rim's edges given in
    the bmesh's order or sorted by their vertices. Returns the cap's corners as made."""
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=20, v_segments=10, radius=1.0)
    bm.verts.index_update()
    geom = (list(bm.verts) + sorted(bm.edges, key=lambda e: sorted(v.index for v in e.verts))
            + sorted(bm.faces, key=lambda f: [v.index for v in f.verts]))
    bmesh.ops.bisect_plane(bm, geom=geom, dist=1e-5, plane_co=(0, 0, 0), plane_no=(0, 0, 1),
                           clear_inner=True)
    bm.verts.index_update()
    rim = [e for e in bm.edges if e.is_boundary]
    if sort_rim:
        rim.sort(key=lambda e: sorted(v.index for v in e.verts))
    bmesh.ops.holes_fill(bm, edges=rim, sides=0)
    cap = [f for f in bm.faces if len(f.verts) > 4]
    out = [v.index for v in cap[0].verts] if cap else None
    bm.free()
    return out


for sort_rim in (False, True):
    corners = capped(sort_rim)
    print("UVSPHERE_ORDER cap_rim_%s starts at %s, %d corners, digest %s" % (
        "sorted" if sort_rim else "storage", corners[0] if corners else None,
        len(corners or []), hashlib.sha256(repr(corners).encode()).hexdigest()[:12]))
