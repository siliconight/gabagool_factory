"""Lux 0.64.0: the streetlight's lamp hangs below its mount. The walker,
2026-10-03: "we still have quite a few street lamps that aren't putting
their light down" / "this one far away is working but the one closer isn't".
Twelve of the gas station lot's seventeen poles drew nothing: the shadow
budget had given them shadow maps, and each lamp sat exactly on its own
shaft's top cap, where the first centimetres of shaft fill the whole shadow
frustum. `LuxStreetlightRig` now hangs the lamp `LAMP_HANG_M` (0.10) below
the mount, with the derivation and the measurements on the constant; the
loader solves the pole's energy for where the lamp is.

Anchored edits (every anchor once; refuses on a miss):
`rigs/lux_streetlight_rig.gd` -- the constant after `_CONE_SHADER`, the
lamp's position in `_rebuild`; `lux_light_loader.gd` -- `pole_h` in the
`"streetlight"` branch. `tools/streetlight_shadow_selftest.gd` and
`tools/self_shadow_census.gd` copied from `lux_streetlight_hang/`;
CHANGELOG and VERSION from `lux_streetlight_hang/CHANGELOG_0.64.0.md`.

    python patch_lux_streetlight_hang.py
    LUX_ROOT=<copy> python patch_lux_streetlight_hang.py
"""
import os
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
LUX = pathlib.Path(os.environ.get("LUX_ROOT") or HERE.parent / "lux")
SRC = HERE / "lux_streetlight_hang"

HANG = '''
## THE LAMP HANGS BELOW ITS MOUNT (0.64.0). The mount is where the anchor
## puts the rig: for a Lot pole it is the lens point, 0.175 m under the
## module's top (Lot's `STREETLIGHT_LENS_DROP`), and in Zoo's recipe that
## is 5 mm above the shaft's top cap. A spot's shadow map is a perspective
## camera at the light's origin, and a disc of radius r at depth d in front
## of it subtends atan(r / d): the 0.06 m cap 5 mm under the lamp subtends
## 85 degrees, the whole 55-degree cone, and every pixel under the pole
## compares as shadowed. At or below the cap the disc is behind the camera.
## (The first reading was the shaft's SIDES filling the frustum from a
## camera on the axis; a clean cylinder with the lamp on its cap lit the
## ground fully and refuted it.)
##
## MEASURED on cold run 9139's gas station lot (survey, every other light
## off, the ground's luminance 9 m from the foot), the pole's own lamp
## against a fresh unshadowed spot on its transform:
##
##     at the lens point, shadowed   0.001     (12 of 17 poles shipped so)
##     fresh, unshadowed             0.305
##     0.02 m lower, shadowed        0.282
##     0.05 m lower, shadowed        0.239
##     0.10 m lower, shadowed        0.282     (the unshadowed figure: 0.286)
##
## And with Zoo's shapes in this project (`tools/streetlight_shadow_
## selftest.gd`): 5 mm over the cap 0.002; at or under it 0.742 whatever
## the body's cull mode; the shaft hidden 0.745; the head or the lens
## hidden, no change. The figure stops moving at 0.02; 0.10 keeps the cap
## a hand's width behind the camera. The five poles the shadow budget had
## not reached were the ones the walker saw working.
const LAMP_HANG_M := 0.10
'''


def main():
    v = (LUX / "VERSION").read_text(encoding="utf-8").strip()
    assert v == "Lux 0.63.0", v
    rig = LUX / "addons" / "lux" / "runtime" / "rigs" / "lux_streetlight_rig.gd"
    s = rig.read_text(encoding="utf-8")
    assert "\r" not in s and "LAMP_HANG_M" not in s, "already applied, or CRLF"
    a1 = 'const _CONE_SHADER := preload("res://addons/lux/shaders/spatial/lux_light_cone.gdshader")\n'
    assert s.count(a1) == 1
    s = s.replace(a1, a1 + HANG)
    a2 = "\t\tlamp.position = Vector3(start + i * r.spacing, r.mount_height, 0.0)\n"
    assert s.count(a2) == 1
    s = s.replace(a2, "\t\tlamp.position = Vector3(start + i * r.spacing, r.mount_height - LAMP_HANG_M, 0.0)\n")
    rig.write_text(s, encoding="utf-8", newline="\n")
    loader = LUX / "addons" / "lux" / "runtime" / "lux_light_loader.gd"
    t = loader.read_text(encoding="utf-8")
    assert "\r" not in t and "LAMP_HANG_M" not in t
    a3 = '\t\t\t\tpole_h = maxf(float(a.get("pos")[2]), 0.5)\n'
    assert t.count(a3) == 1
    t = t.replace(a3, '\t\t\t\t# the lamp hangs LAMP_HANG_M under the lens (0.64.0): solve for where it is\n'
                      '\t\t\t\tpole_h = maxf(float(a.get("pos")[2]) - LuxStreetlightRig.LAMP_HANG_M, 0.5)\n')
    loader.write_text(t, encoding="utf-8", newline="\n")
    for name in ("streetlight_shadow_selftest.gd", "self_shadow_census.gd"):
        (LUX / "tools" / name).write_bytes((SRC / name).read_bytes())
    entry = (SRC / "CHANGELOG_0.64.0.md").read_text(encoding="utf-8").replace("\r\n", "\n")
    cl = LUX / "CHANGELOG.md"
    d = cl.read_bytes()
    assert b"## [0.64.0]" not in d
    head = b"# Changelog\n\n"
    assert d.startswith(head)
    cl.write_bytes(head + entry.encode("utf-8") + d[len(head):])
    (LUX / "VERSION").write_bytes(b"Lux 0.64.0")
    print("0.63.0 -> 0.64.0")


if __name__ == "__main__":
    main()
