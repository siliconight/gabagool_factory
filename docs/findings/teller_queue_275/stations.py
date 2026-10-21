"""Look-shot stations given in a building's own frame, turned into the site's frame of one package.

    python docs/findings/teller_queue_275/stations.py <walk or package dir> <building id> NAME:ex,ey,eh,tx,ty,th [...]

Each station is an eye and a target in the BUILDING's frame as Deli Counter writes a spec: x east, y north, h the
height above the ground floor, metres. The package's `site.tscn` places the building's scene (`lot/<id>/site.tscn`)
with a `Transform3D` read the way Godot reads it -- the basis's ROWS, then the origin (`tools/godot_transform.py`) --
and the building's own scene is glTF's Y-up turn of the spec's frame: (x, h, -y). Prints one `--station` argument a
station, ready for `tools/look_shots.py`, and the placement it used, and stops.
"""
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2] / "tools"))
import godot_transform  # noqa: E402

pkg, building = pathlib.Path(sys.argv[1]), sys.argv[2]
site = (pkg / "site.tscn").read_text(encoding="utf-8")
res = re.search(r'\[ext_resource type="PackedScene" path="lot/%s/site.tscn" id="([^"]+)"\]' % re.escape(building), site)
if not res:
    raise SystemExit("FAIL: %s/site.tscn instances no lot/%s/site.tscn" % (pkg, building))
node = re.search(r'\[node name="[^"]+" parent="\." instance=ExtResource\("%s"\)\]\ntransform = (Transform3D\([^)]*\))'
                 % re.escape(res.group(1)), site)
if not node:
    raise SystemExit("FAIL: no placed node instances %s's scene" % building)
m = godot_transform.matrix(godot_transform.floats(node.group(1)))
print("# %s placed by %s" % (building, node.group(1)))
args = []
for st in sys.argv[3:]:
    name, nums = st.split(":", 1)
    ex, ey, eh, tx, ty, th = (float(v) for v in nums.split(","))
    e = godot_transform.apply(m, (ex, eh, -ey))
    t = godot_transform.apply(m, (tx, th, -ty))
    args.append("--station %s:%s" % (name, ",".join("%.3f" % v for v in e + t)))
print(" ".join(args))
