"""A look_shots station square on one building's face, in a package's world frame.

    python docs/cold_runs/cold_9348/front_station.py <package or walk copy> <building id> [--face S] [--back M]

Reads where the site stands the building (`site.tscn`: the node instancing `lot/<id>/site.tscn`, its Transform3D read
by `tools/godot_transform.py`, rows) and its footprint off Deli Counter's spec. The eye stands `--back` metres out
from the face's centre at a person's 1.7 m, looking at the face's centre 4.5 m up, so a ground floor and a first storey
are both in frame. Deli Counter's frame is Blender Z-up and Godot's Y-up: a building's local Godot (x, y, z) is
Deli Counter's (x, z, -y), so its S face, at Deli Counter y = -half the footprint, is at local Godot z = +half.
Prints `NAME:ex,ey,ez,tx,ty,tz`, look_shots' `--station`.
"""
import json
import os
import re
import sys

F = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, os.path.join(F, "tools"))
import godot_transform as gt  # noqa: E402

pkg, bid = sys.argv[1], sys.argv[2]
face = sys.argv[sys.argv.index("--face") + 1] if "--face" in sys.argv else "S"
back = float(sys.argv[sys.argv.index("--back") + 1]) if "--back" in sys.argv else 14.0
site = open(os.path.join(pkg, "site.tscn"), encoding="utf-8").read()
rid = re.search(r'\[ext_resource type="PackedScene" path="(?:res://)?lot/%s/site\.tscn" id="([^"]+)"\]' % re.escape(bid),
                site)
if not rid:
    raise SystemExit("%s: no ext_resource for lot/%s/site.tscn" % (pkg, bid))
node = re.search(r'\[node name="[^"]+" parent="\." instance=ExtResource\("%s"\)\]\ntransform = (Transform3D\([^)]*\))'
                 % re.escape(rid.group(1)), site)
if not node:
    raise SystemExit("%s: no placed node instances lot/%s/site.tscn with a transform" % (pkg, bid))
m = gt.matrix(gt.floats(node.group(1)))
spec = json.load(open(os.path.join(F, "deli_counter", "specs", bid + ".json"), encoding="utf-8"))
hx, hy = float(spec["footprint_x"]) / 2.0, float(spec["footprint_y"]) / 2.0
# the face's centre and its outward normal, in the building's local Godot frame
centre, out = {"S": ((0.0, 0.0, hy), (0, 0, 1)), "N": ((0.0, 0.0, -hy), (0, 0, -1)),
               "E": ((hx, 0.0, 0.0), (1, 0, 0)), "W": ((-hx, 0.0, 0.0), (-1, 0, 0))}[face]
eye = gt.apply(m, (centre[0] + out[0] * back, 1.7, centre[2] + out[2] * back))
tgt = gt.apply(m, (centre[0], 4.5, centre[2]))
print("%s_%s:%s" % (bid, face, ",".join("%.3f" % v for v in tuple(eye) + tuple(tgt))))
