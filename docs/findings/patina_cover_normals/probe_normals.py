"""Roadmap 221, step 1: does Patina's anchor pass derive wall normals that point OUT of the shell?

    python docs/findings/patina_cover_normals/probe_normals.py deli_counter/build/strip_club_a01.glb

Loads the shell the way `patina.cli.run` does -- `gltf_io.load_glb`, then
`bake_visual_transforms`, `slots.detect_up_axis`, `nuance.densify` at its defaults and
`surfaces.classify`; the bevel is a bpy bridge and is skipped -- permutes its primitives into
the anchor pass's Z-up view exactly as `anchors.generate` does, and lists
`anchors._wall_segments`.

RETRACTED, kept: the first run skipped `bake_visual_transforms`. Patina keeps each primitive in
its node's local frame until that bake, so the run measured strip_club_a01 as 7 x 3.3 x 4.8 m
-- one slab tile's frame, not the building -- and its four 'wall segments' were that tile's.
Its verdict, every normal pointing in, was about the wrong geometry and is not evidence. For each segment it prints the derived
horizontal normal and the direction from the shell's horizontal centre to the segment, and their
dot product. That test needs no frame: whatever the axes are called, an exterior wall's outward
normal points away from the building's middle, so the dot is positive.

A second column recomputes each normal with the triangle's winding taken in the file's own frame
(no permutation), then permuted as a VECTOR, so the two derivations can be compared.

It prints what it measured and stops.
"""
import os
import sys

import numpy as np

F = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, os.path.join(F, "patina"))
from patina import anchors, gltf_io, nuance, slots, surfaces  # noqa: E402
from patina.surfaces import SurfaceRole  # noqa: E402


def main(path):
    scene = gltf_io.load_glb(path)
    scene.bake_visual_transforms()
    up = slots.detect_up_axis(scene)
    opts = nuance.NuanceOptions()
    if opts.densify:
        nuance.densify(scene, opts)
    surfaces.classify(scene, up)
    print("shell %s, up axis %s" % (os.path.basename(path), "XYZ"[up]))
    vlo, vhi = anchors._visual_aabb(scene)
    print("visual AABB, file frame: %s to %s" % (np.round(vlo, 2), np.round(vhi, 2)))
    # the anchor pass's own view: positions permuted, as anchors.generate does
    saved = []
    for mesh in scene.visual_meshes():
        for prim in mesh.primitives:
            saved.append((prim, prim.positions))
            prim.positions = anchors._up_to_z(prim.positions, up)
    try:
        lo, hi = anchors._visual_aabb(scene)
        centre = (lo + hi) / 2.0
        segs = list(anchors._wall_segments(scene))
        # the same faces' normals with the winding taken BEFORE the permutation
        alt = []
        for prim, orig in saved:
            if prim.face_roles is None:
                continue
            tris = orig[prim.indices]
            fn = np.cross(tris[:, 1] - tris[:, 0], tris[:, 2] - tris[:, 0])
            ln = np.linalg.norm(fn, axis=1, keepdims=True)
            fn = np.divide(fn, ln, out=np.zeros_like(fn), where=ln > 1e-9)
            fn = anchors._up_to_z(fn, up)                 # the vector, permuted afterwards
            cen = anchors._up_to_z(tris.mean(axis=1), up)
            for t, role in enumerate(prim.face_roles):
                if role == SurfaceRole.EXTERIOR_WALL:
                    alt.append((cen[t], fn[t]))
    finally:
        for prim, pos in saved:
            prim.positions = pos
    print("centre (anchor frame, x y): %.3f %.3f; %d wall segments" % (centre[0], centre[1], len(segs)))
    out_n = in_n = 0
    print("%4s %5s %9s %17s %17s %7s %17s" % ("axis", "along", "fixed", "derived normal", "centre->wall",
                                             "dot", "winding first"))
    for s in segs:
        mid = np.zeros(2)
        mid[s["axis"]] = s["fixed"]
        mid[s["along"]] = (s["a_min"] + s["a_max"]) / 2.0
        d = mid - centre[:2]
        d = d / max(np.linalg.norm(d), 1e-9)
        n = np.asarray(s["normal"], dtype=float)
        dot = float(n @ d)
        # the alternative normal for the faces nearest this segment's plane
        near = [f for c, f in alt if abs(c[s["axis"]] - s["fixed"]) < 0.06
                and s["a_min"] - 0.06 <= c[s["along"]] <= s["a_max"] + 0.06]
        if near:
            m = np.mean([f[:2] for f in near], axis=0)
            m = m / max(np.linalg.norm(m), 1e-9)
            alt_s = "(%+.2f, %+.2f)" % (m[0], m[1])
        else:
            alt_s = "none near"
        if dot > 0:
            out_n += 1
        else:
            in_n += 1
        print("%4s %5s %9.3f   (%+.2f, %+.2f)   (%+.2f, %+.2f) %7.2f   %s"
              % ("xy"[s["axis"]], "xy"[s["along"]], s["fixed"], n[0], n[1], d[0], d[1], dot, alt_s))
    print("segments whose derived normal points away from the centre: %d; toward it: %d" % (out_n, in_n))


if __name__ == "__main__":
    main(sys.argv[1])
