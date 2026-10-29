"""Print the plane clusters `anchors._plane_keys` (Patina >= 0.33.1) merges on a shell: every cluster of face planes
within PLANE_TOL whose members `round(_, 1)` used to send to different buckets, with each member's face count and z
range. Runs Patina's CLI from the checkout given, with `_exterior_wall_faces` wrapped. Measures only; metres,
Patina's canonical Z-up view.

    python docs/findings/parapet_flush/merge_probe.py <patina checkout> <shell.glb>
"""
import collections
import os
import sys
import tempfile

sys.path.insert(0, os.path.abspath(sys.argv[1]))
import numpy as np  # noqa: E402

from patina import anchors, cli  # noqa: E402

seen = []
_orig = anchors._exterior_wall_faces


def _wrapped(scene, mirrored=False):
    for item in _orig(scene, mirrored):
        seen.append(item)
        yield item


anchors._exterior_wall_faces = _wrapped
with tempfile.TemporaryDirectory() as tmp:
    try:
        cli.main([os.path.abspath(sys.argv[2]), "--mode", "vertex-color", "--out", tmp + "/x.patina.glb",
                  "--dressing", "--anchors"])
    except SystemExit:
        pass
faces = collections.defaultdict(list)
for c, n, (zlo, zhi) in seen:
    horiz = np.array([n[0], n[1]])
    if np.linalg.norm(horiz) < 1e-6:
        continue
    horiz = horiz / np.linalg.norm(horiz)
    axis = int(np.argmax(np.abs(horiz)))
    side = "hi" if horiz[axis] > 0 else "lo"
    faces[(axis, side, float(c[axis]))].append((float(zlo), float(zhi)))
keys = anchors._plane_keys([(a, s, p) for a, s, p in faces])
clusters = collections.defaultdict(list)
for (a, s, p), k in keys.items():
    clusters[(a, s, k)].append(p)
n = 0
for (a, s, k), ps in sorted(clusters.items()):
    old = {round(p, 1) for p in ps}
    if len(old) < 2:
        continue
    n += 1
    print("axis", a, s, "bucket", k, "was", sorted(old))
    for p in sorted(ps):
        zs = faces[(a, s, p)]
        print("   ", repr(p), "faces", len(zs), "z", round(min(z[0] for z in zs), 3), round(max(z[1] for z in zs), 3))
print("merged clusters", n)
