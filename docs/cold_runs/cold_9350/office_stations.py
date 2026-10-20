"""look_shots stations at the office's desks and cubicle banks, from where a person working at them would be.

    python docs/cold_runs/cold_9350/office_stations.py <package or walk copy> [--building office]

Reads where the site stands the building (`site.tscn`: the node instancing `lot/<id>/site.tscn`, its Transform3D read
by `tools/godot_transform.py`, rows) and its desks and cubicle banks off Deli Counter's built slots
(`deli_counter/build/<id>.slots.json`). A desk's sitter is at its local -Y (Zoo's `recipes/desk.py`: "user sits at
-Y"), so the station for a desk with office stock stands 2.2 m out on that side at a person's 1.6 m over its floor,
looking at the middle of the top 0.95 m up, where its monitor stands. A cubicle bank is seen over its 1.2 m
partitions: 2 m out from its -Y side at 2.4 m, looking at its middle 0.9 m up (4.5 m out stood the east banks'
stations outside the office's south wall). `--only a,b` keeps the named slots. A slot's `rot_y` turns its local
frame about the up axis CLOCKWISE from above. REFUTED, KEPT: the first version turned it counter-clockwise, as
Blender's Z does, and its stations at the three desks turned 90 and 270 looked at the monitors' backs while the one
turned 180 -- where the two senses agree -- saw the screen. Deli Counter's frame is Blender Z-up and
Godot's Y-up: a building's local Godot (x, y, z) is Deli Counter's (x, z, -y). Prints `--station NAME:ex,ey,ez,tx,ty,tz`
for each, look_shots' own; prints what it derived and stops.
"""
import json
import math
import os
import re
import sys

F = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, os.path.join(F, "tools"))
import godot_transform as gt  # noqa: E402

pkg = sys.argv[1]
bid = sys.argv[sys.argv.index("--building") + 1] if "--building" in sys.argv else "office"
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
slots = json.load(open(os.path.join(F, "deli_counter", "build", bid + ".slots.json"), encoding="utf-8"))["slots"]


def godot(p):
    """Deli Counter local (x, y, z-up) -> the package's world frame."""
    return gt.apply(m, (p[0], p[2], -p[1]))


only = set(sys.argv[sys.argv.index("--only") + 1].split(",")) if "--only" in sys.argv else None
out = []
for s in slots:
    if only is not None and s["slot_id"] not in only:
        continue
    sp, stock = s.get("species"), s.get("stock")
    if sp == "desk" and stock == "office":
        back, eye_h, tgt_h = 2.2, 1.6, 0.95
    elif sp == "cubicle_bank":
        back, eye_h, tgt_h = 2.0, 2.4, 0.9
    else:
        continue
    (x, y, z), rot = s["transform"]["translation"], math.radians(float(s["transform"].get("rot_y") or 0.0))
    floor = z - float(s["fit"]["dims"][2]) / 2.0
    # the sitter's side, local -Y, turned clockwise by rot_y (measured: see the docstring)
    fx, fy = -math.sin(rot), -math.cos(rot)
    if sp == "cubicle_bank":
        back += float(s["fit"]["dims"][1]) / 2.0
    eye = godot((x + fx * back, y + fy * back, floor + eye_h))
    tgt = godot((x, y, floor + tgt_h))
    print("# %s %s at (%.2f, %.2f) floor %.2f rot %s: sitter's side (%.2f, %.2f)"
          % (s["slot_id"], sp, x, y, floor, s["transform"].get("rot_y"), fx, fy), file=sys.stderr)
    out.append("--station %s:%s" % (s["slot_id"], ",".join("%.3f" % v for v in tuple(eye) + tuple(tgt))))
print(" ".join(out))
