"""Does the lightmapper bake a light marked `editor_only`?

    python fixture_control_editor_only.py <dir> [--godot EXE]

fixture_control.py's floor and two lamps, plus `Lamp_editor_only`: a static
omni at (0, 2.5, 0), energy 1.0, range 3.0, `editor_only = true` -- a light
Godot hides at runtime. Shot baked and unbaked the same way. Unbaked, the
floor under it must read 0 (the runtime hides it: the instrument's control).
Baked, a pool under it means the lightmapper took it.
"""
import sys

import fixture_control as FC

FC.SCENE = FC.SCENE.replace(
    '[node name="Lightmap" type="LightmapGI" parent="."]',
    '[node name="Lamp_editor_only" type="OmniLight3D" parent="."]\n'
    'transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 2.5, 0)\n'
    'editor_only = true\n'
    'light_bake_mode = 1\n'
    'omni_range = 3.0\n\n'
    '[node name="Lightmap" type="LightmapGI" parent="."]')
assert "Lamp_editor_only" in FC.SCENE

if __name__ == "__main__":
    FC.main(sys.argv[1:])
