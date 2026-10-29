"""Print the plane buckets Patina's anchor pass forms on a shell: per (axis, side, rounded plane) key -- the key
`anchors._wall_segments` groups by -- the faces' exact plane coordinates (repr) and their z range. Runs Patina's own
CLI (--dressing --anchors) on the shell into a temporary folder with `_exterior_wall_faces` wrapped to record what it
yields. Measures only; metres, Patina's canonical Z-up view.

    python docs/findings/parapet_flush/bucket_probe.py <shell.glb> [axis]
"""
import collections
import sys
import tempfile

sys.path.insert(0, r"C:\Projects\gabagool_studios\gabagool_factory\patina")
import numpy as np  # noqa: E402

from patina import anchors, cli  # noqa: E402

glb = sys.argv[1]
want_axis = int(sys.argv[2]) if len(sys.argv) > 2 else None
seen = []
_orig = anchors._exterior_wall_faces


def _wrapped(scene, mirrored=False):
    for item in _orig(scene, mirrored):
        seen.append(item)
        yield item


anchors._exterior_wall_faces = _wrapped
with tempfile.TemporaryDirectory() as tmp:
    try:
        cli.main([glb, "--mode", "vertex-color", "--out", tmp + "/x.patina.glb", "--dressing", "--anchors"])
    except SystemExit:
        pass
rows = collections.defaultdict(list)
for c, n, (zlo, zhi) in seen:
    horiz = np.array([n[0], n[1]])
    if np.linalg.norm(horiz) < 1e-6:
        continue
    horiz = horiz / np.linalg.norm(horiz)
    axis = int(np.argmax(np.abs(horiz)))
    if want_axis is not None and axis != want_axis:
        continue
    side = "hi" if horiz[axis] > 0 else "lo"
    rows[(axis, side, round(float(c[axis]), 1))].append((float(c[axis]), float(zlo), float(zhi)))
for key in sorted(rows):
    planes = collections.Counter(repr(p) for p, _a, _b in rows[key])
    print(key, "faces", len(rows[key]), "z", round(min(r[1] for r in rows[key]), 3),
          round(max(r[2] for r in rows[key]), 3), "planes", planes.most_common(4))
