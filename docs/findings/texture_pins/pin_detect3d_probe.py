"""`pin_bake_import_probe.py` with one more pin: `detect_3d/compress_to=0` on the shared textures.

The baseline (`pin_bake_import_probe.out.txt`): the light bake's first `--import`, whose job is to
re-import the 476 models `mark_imports` moved to static lightmaps, imported textures 1,843 times --
the same shared texture again and again, several in flight at once -- and 64 of 415 `_tex/`
sidecars came out with Godot's defaults. Every one of those sidecars still carries
`detect_3d/compress_to=1`, the engine's rule for re-importing a texture when a 3D scene uses it, a
rule the pins already contradict (they choose the compression themselves). This runs the same
reproduction with that rule turned off in the pin table, so the difference between the two runs is
that one key. It measures and prints.

    python docs/findings/texture_pins/pin_detect3d_probe.py <package dir>
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pin_bake_import_probe as P  # noqa: E402

P.E.SHARED_TEX_PINS["detect_3d/compress_to"] = "0"
print("pins:", P.E.SHARED_TEX_PINS, flush=True)
P.X = os.path.join(P.F, "_scratch", "texture_pins", "bake_import_detect3d_off")

if __name__ == "__main__":
    P.main()
