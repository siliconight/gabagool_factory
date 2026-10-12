"""An arm for `spec_arm.sh`: the live sun with no specular term.

    python docs/findings/lux_tiers/sun_nospec.py <a copy of a package>

A lightmap holds diffuse light only, so a baked sun has no specular term where a live one has Godot's
default (`light_specular`, which Lux never sets). This writes `sun.light_specular = 0.0` into the copy's
vendored `runtime/lux/runtime/lux_lighting.gd`, right after Lux sets the sun's energy, through
`sun_variants._edit` (exactly one match or nothing written). Never run it on a package itself.
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import sun_variants as SV   # noqa: E402

OLD = "\tsun.light_energy = preset.sun_energy\n"
NEW = OLD + "\tsun.light_specular = 0.0  # an arm: docs/findings/lux_tiers/spec_arm.sh\n"


def main():
    project = pathlib.Path(sys.argv[1])
    if "_scratch" not in project.resolve().parts:
        sys.exit("refusing: %s is not a copy under _scratch" % project)
    SV._edit(project / SV.LIGHTING, OLD, NEW)
    print("lux_lighting.gd: the sun's specular 0")


if __name__ == "__main__":
    main()
