"""Wire SkyCycle into a fresh walk copy's `_walk.tscn`, as cold run 9111's was.

    python tools/cold_drive/wire_sky.py _runs/walk_export_<mission>
"""
import pathlib
import shutil

import sys
W = pathlib.Path(sys.argv[1])
#: The walk copy's sky cycle: the same bytes the kept 9111 walk copy carried.
SKY = pathlib.Path(__file__).resolve().parents[1] / "walk_sky_cycle.gd"

t = W / "_walk.tscn"
d = t.read_bytes()
eol = b"\r\n" if b"\r\n" in d else b"\n"
s = d.decode("utf-8")
n = eol.decode()
assert "sky_cycle" not in s, "already wired"
head = "[gd_scene load_steps=7 format=3]"
assert s.count(head) == 1, s[:60]
s = s.replace(head, "[gd_scene load_steps=8 format=3]", 1)
fl = '[ext_resource type="Script" path="res://_walk_flashlight.gd" id="walk_flashlight"]'
assert s.count(fl) == 1
s = s.replace(fl, fl + n + '[ext_resource type="Script" path="res://_sky_cycle.gd" id="sky_cycle"]', 1)
node = '[node name="WalkFlashlight" type="Node" parent="."]' + n + 'script = ExtResource("walk_flashlight")' + n
assert s.count(node) == 1
s = s.replace(node, node + n + '[node name="SkyCycle" type="Node" parent="."]' + n
              + 'script = ExtResource("sky_cycle")' + n, 1)
t.write_bytes(s.encode("utf-8"))
if not (W / "_sky_cycle.gd").exists():
    shutil.copy(SKY, W / "_sky_cycle.gd")
# STRUCTURE, NOT A KEPT COPY. This compared the whole scene with a walk copy
# kept from cold run 9111 in a session scratchpad; it printed False on every
# run from 9147 on and nobody read it. What matters is that the node and its
# script are there, and the script is the one in tools/.
got = s.replace("\r\n", "\n")
assert got.count('[node name="SkyCycle" type="Node" parent="."]') == 1
assert got.count('path="res://_sky_cycle.gd"') == 1
assert (W / "_sky_cycle.gd").read_bytes() == SKY.read_bytes()
print("wired: SkyCycle node and script, the same bytes as tools/walk_sky_cycle.gd")
