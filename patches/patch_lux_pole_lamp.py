"""Lux 0.65.0: the streetlight's lamp sits beside its pole, under the lens.

Lux 0.64.0 hung the lamp 0.10 m below the mount to get it out of its own
shadow map. The mount is 5 mm above the shaft's cap, so that put the lamp
9.5 cm INSIDE the steel shaft. A shadow map culls the shaft's inside faces
and drew the pool; the light bake ray-traces, and a lamp sealed in a tube
baked 0 lit texels (the light-bake probe, roadmap item 31:
`docs/findings/light_bake/NOTES.md`). Every steady pole's pool vanished
from the baked lot.

The pole's lamp now sits `POLE_LAMP_ALONG_M` (0.2) along the head from the
pole's axis -- the rig turns with its pole, so local x is the head's length
-- and `POLE_LAMP_DROP_M` (0.01) under the lens: in the air, under the lit
lens, beside the shaft. A rig-node property, `lamp_offset`, carries it, and
defaults to 0.64.0's (0, -LAMP_HANG_M, 0) so a wall pack -- the same rig, its
own hardware -- does not move; the loader's `streetlight` branch sets the
pole's.

Anchored edits (every anchor once; refuses on a miss): `rigs/
lux_streetlight_rig.gd` (the constants after `LAMP_HANG_M`, the property,
the lamp's and the cone's position), `lux_light_loader.gd` (the streetlight
branch sets the offset, and solves energy for the lamp's height);
`tools/streetlight_shadow_selftest.gd` replaced from `lux_pole_lamp/`;
CHANGELOG and VERSION from `lux_pole_lamp/CHANGELOG_0.65.0.md`.

    python patch_lux_pole_lamp.py
    LUX_ROOT=<copy> python patch_lux_pole_lamp.py
"""
import os
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
LUX = pathlib.Path(os.environ.get("LUX_ROOT") or HERE.parent / "lux")
SRC = HERE / "lux_pole_lamp"

CONSTS = '''
## THE POLE'S LAMP SITS BESIDE THE POLE (0.65.0), and `LAMP_HANG_M` above
## is a wall pack's now. 0.64.0 hung a pole's lamp 0.10 below its mount to
## clear its own shadow map; the mount is 5 mm above the shaft's cap, so the
## lamp sat 9.5 cm INSIDE the steel. A shadow map culls the shaft's inside
## faces and drew the pool. The light bake ray-traces, and measured on one
## closed 6 m pole and one static spot (`patches/lightbake_probe/
## make_pole_control.py`, Godot 4.7's lightmapper, quality Low):
##
##     lamp inside the shaft (0.64.0)             0 lit texels   max 0.005
##     on the axis at the lens point (to 0.63.0)  2,815          max 0.039
##     0.2 m along the head, 1 cm under the lens  5,581          max 20.9
##     no pole at all                             5,605          max 3.0
##
## So the lamp sits POLE_LAMP_ALONG_M along the head from the pole's axis,
## and POLE_LAMP_DROP_M under the lens: clear of the 0.06 m shaft by 0.14,
## under the lens at the genome's narrowest head (0.5 m wide, a 0.4 m lens,
## so 0.2 is its end), and above nothing but the ground. The pole now
## shadows a wedge of its own pool -- 2 atan(0.06 / 0.2), 33 degrees, on
## the far side -- which a real pole does.
const POLE_LAMP_ALONG_M := 0.2
const POLE_LAMP_DROP_M := 0.01
## AND ITS SHADOW BIAS (0.65.0). A shadowed pole's lamp reads lit for about
## 30 frames, then the renderer moves it to a smaller slot of the 16-bit
## positional atlas and, at the engine's 0.03, the ground shadows itself
## (acne). Measured on the gas station lot's side-street pole, settled,
## every other light off, the ground under it (unshadowed 0.201):
##
##     bias 0.03 (default)   0.085      normal bias 2    0.157
##     bias 0.1              0.183      normal bias 4    0.178
##     bias 0.3              0.183      24-bit atlas     0.183
##
## 0.1 is where it stops moving; a 6 m pole's shadow detaches by a few cm.
## Every steady pole on the lot lit after a 90-frame settle at 0.1; one of
## 17 was dark at the default.
const POLE_SHADOW_BIAS := 0.1
'''

PROP = '''
## Where each lamp sits from its row point at the mount, in the rig's frame
## (x along the head, y up). The default is 0.64.0's, which a wall pack
## keeps; the loader's `streetlight` branch puts a pole's lamp beside the
## pole (`POLE_LAMP_ALONG_M`, `POLE_LAMP_DROP_M`).
@export var lamp_offset: Vector3 = Vector3(0.0, -LAMP_HANG_M, 0.0):
	set(value):
		lamp_offset = value
		if is_inside_tree():
			_rebuild()
## Each lamp's shadow bias; negative leaves the engine's. The loader's
## `streetlight` branch sets `POLE_SHADOW_BIAS`.
@export var lamp_shadow_bias: float = -1.0
'''


def _edit(path, pairs):
    s = path.read_text(encoding="utf-8")
    assert "\r" not in s, path
    for old, new in pairs:
        assert s.count(old) == 1, (path.name, old[:70])
        s = s.replace(old, new)
    path.write_text(s, encoding="utf-8", newline="\n")


def main():
    v = (LUX / "VERSION").read_text(encoding="utf-8").strip()
    assert v == "Lux 0.64.0", v
    rig = LUX / "addons" / "lux" / "runtime" / "rigs" / "lux_streetlight_rig.gd"
    _edit(rig, [
        ("const LAMP_HANG_M := 0.10\n", "const LAMP_HANG_M := 0.10\n" + CONSTS + PROP),
        ("\t\tlamp.position = Vector3(start + i * r.spacing, r.mount_height - LAMP_HANG_M, 0.0)\n",
         "\t\tlamp.position = Vector3(start + i * r.spacing, r.mount_height, 0.0) + lamp_offset\n"),
        ("\t\tlamp.shadow_enabled = r.shadows_enabled\n",
         "\t\tlamp.shadow_enabled = r.shadows_enabled\n\t\tif lamp_shadow_bias >= 0.0:\n\t\t\tlamp.shadow_bias = lamp_shadow_bias\n"),
        ("\tmi.position = Vector3(start + index * r.spacing, r.mount_height * 0.5, 0.0)\n",
         "\tmi.position = Vector3(start + index * r.spacing + lamp_offset.x, r.mount_height * 0.5, lamp_offset.z)\n"),
    ])
    loader = LUX / "addons" / "lux" / "runtime" / "lux_light_loader.gd"
    _edit(loader, [
        ('\t\t\tvar s := LuxStreetlightRig.new()\n\t\t\ts.name = String(a.get("id", "streetlight"))\n',
         '\t\t\tvar s := LuxStreetlightRig.new()\n\t\t\ts.name = String(a.get("id", "streetlight"))\n'
         '\t\t\t# beside the pole, under the lens (0.65.0): see POLE_LAMP_ALONG_M\n'
         '\t\t\ts.lamp_offset = Vector3(LuxStreetlightRig.POLE_LAMP_ALONG_M,\n'
         '\t\t\t\t-LuxStreetlightRig.POLE_LAMP_DROP_M, 0.0)\n'
         '\t\t\ts.lamp_shadow_bias = LuxStreetlightRig.POLE_SHADOW_BIAS\n'),
        ('\t\t\t\t# the lamp hangs LAMP_HANG_M under the lens (0.64.0): solve for where it is\n'
         '\t\t\t\tpole_h = maxf(float(a.get("pos")[2]) - LuxStreetlightRig.LAMP_HANG_M, 0.5)\n',
         '\t\t\t\t# the lamp sits POLE_LAMP_DROP_M under the lens (0.65.0): solve for where it is\n'
         '\t\t\t\tpole_h = maxf(float(a.get("pos")[2]) - LuxStreetlightRig.POLE_LAMP_DROP_M, 0.5)\n'),
    ])
    (LUX / "tools" / "streetlight_shadow_selftest.gd").write_bytes((SRC / "streetlight_shadow_selftest.gd").read_bytes())
    entry = (SRC / "CHANGELOG_0.65.0.md").read_text(encoding="utf-8").replace("\r\n", "\n")
    cl = LUX / "CHANGELOG.md"
    d = cl.read_bytes()
    assert b"## [0.65.0]" not in d
    head = b"# Changelog\n\n"
    assert d.startswith(head)
    cl.write_bytes(head + entry.encode("utf-8") + d[len(head):])
    (LUX / "VERSION").write_bytes(b"Lux 0.65.0")
    print("0.64.0 -> 0.65.0")


if __name__ == "__main__":
    main()
