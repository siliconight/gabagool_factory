"""Rewrite a walk copy's site_backdrop.tscn with a Level Factory clone's `with_ground`: the old ground taken out, the
new laid from the drawn spec. Prints what it wrote.

    python _scratch/reground.py <lf clone> <walk copy> <drawn spec>
"""
import json
import re
import sys
from pathlib import Path

lf, walk, drawn_path = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
sys.path.insert(0, str(lf))
from packages.exporting import backdrop_layer as B  # noqa: E402

p = walk / "site_backdrop.tscn"
raw = p.read_bytes()
assert b"\r\n" not in raw
t = raw.decode("utf-8")
sub = re.compile(r'\[sub_resource type="PlaneMesh" id="BackdropGround_mesh"\]\n.*?\n\n'
                 r'\[sub_resource type="StandardMaterial3D" id="BackdropGround_mat"\]\n.*?\n\n', re.S)
assert len(sub.findall(t)) == 1
t = sub.sub("", t)
node = re.compile(r'\n\[node name="BackdropGround" type="MeshInstance3D" parent="\."\]\n(?:[^\[\n].*\n)*')
assert len(node.findall(t)) == 1
t = node.sub("\n", t)
t = re.sub(r"load_steps=(\d+)", lambda m: "load_steps=%d" % (int(m.group(1)) - 2), t, count=1)
drawn = json.loads(drawn_path.read_text(encoding="utf-8"))
orders = B.manifest_from_drawn(drawn)["orders"]
t, ground = B.with_ground(t, orders, keep_out=B.plate_bound(drawn))
p.write_text(t, encoding="utf-8", newline="\n")
print(json.dumps(ground))
