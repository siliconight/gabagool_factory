"""Copy a walk project with one live lamp standing where a payphone's hood lamp
will, or re-set that lamp's energy in a copy already made.

    python make_probe_copy.py make <project> <copy> --at X,Y,Z --energy E
    python make_probe_copy.py energy <copy> --energy E

WHAT IT STANDS. A plain `SpotLight3D` appended under `presentation/
lux.applied.tscn`'s root (`Site`, which `bake.tscn` instances at the identity,
so the numbers are Godot world metres, Y up), pointing straight down, with the
numbers Lux's fluorescent rig gives a `_make_downlight` lamp: spot_angle 89,
spot_angle_attenuation 0.125, attenuation 2, no shadow. Its colour is
`LuxColorTemp.cool_fluorescent()` worked by hand from `lux_color_temp.gd`
(4,100 K by the Tanner Helland fit, then the 0.07 green cast): (0.965, 0.874,
0.646). Its range is `LuxLightLoader.fluorescent_range(drop)`, passed in.

WHAT IT DOES NOT DO. It does not re-bake. Godot's default `light_bake_mode`
is DYNAMIC, so on a lightmapped surface the lamp adds its direct light live
and nothing else: a frame of the copy is the package's own bake plus this
lamp's direct light. The shipped lamp will be BAKED, ray-traced, with the
booth's own parts casting shadows and a bounce; that is the residue between
this probe and the cold run.

Refuses: a copy that exists (make), a copy without exactly one probe node
(energy), a scene with no `[node name="Site"` root. Prints what it wrote and
stops.
"""
import argparse
import pathlib
import re
import shutil

SCENE = pathlib.Path("presentation") / "lux.applied.tscn"
NAME = "PayphoneHoodProbe"
UNIQUE_ID = 1975310261
COLOR = (0.965, 0.874, 0.646)


def _read(path):
    data = path.read_bytes()
    eol = "\r\n" if b"\r\n" in data else "\n"
    return data.decode("utf-8").replace("\r\n", "\n"), eol


def _write(path, text, eol):
    path.write_bytes(text.replace("\n", eol).encode("utf-8"))


def node_text(at, energy, light_range):
    x, y, z = at
    # rows of the basis, as Godot writes them: X turned -90 degrees, so the
    # lamp's -Z (its forward) is world -Y, straight down
    return (f'\n[node name="{NAME}" type="SpotLight3D" parent="." unique_id={UNIQUE_ID}]\n'
            f"transform = Transform3D(1, 0, 0, 0, 0, 1, 0, -1, 0, {x!r}, {y!r}, {z!r})\n"
            f"light_color = Color({COLOR[0]}, {COLOR[1]}, {COLOR[2]}, 1)\n"
            f"light_energy = {energy!r}\n"
            f"spot_range = {light_range!r}\n"
            f"spot_attenuation = 2.0\n"
            f"spot_angle = 89.0\n"
            f"spot_angle_attenuation = 0.125\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=("make", "energy"))
    ap.add_argument("paths", nargs="+")
    ap.add_argument("--at")
    ap.add_argument("--energy", type=float, required=True)
    ap.add_argument("--range", type=float, default=4.0)
    a = ap.parse_args()
    if a.mode == "make":
        src, dst = pathlib.Path(a.paths[0]), pathlib.Path(a.paths[1])
        if dst.exists():
            raise SystemExit(f"{dst} exists; refusing to write over it")
        if not (src / SCENE).is_file():
            raise SystemExit(f"{src / SCENE} not found")
        at = tuple(float(v) for v in a.at.split(","))
        assert len(at) == 3, a.at
        text, eol = _read(src / SCENE)
        if text.count('\n[node name="Site"') + text.startswith('[node name="Site"') != 1:
            raise SystemExit("the scene's root is not one `Site` node")
        if f"unique_id={UNIQUE_ID}" in text or f'name="{NAME}"' in text:
            raise SystemExit("the source already carries the probe")
        shutil.copytree(src, dst)
        out = text.rstrip("\n") + "\n" + node_text(at, a.energy, a.range)
        _write(dst / SCENE, out, eol)
        print(f"{dst / SCENE}: {NAME} at {at}, energy {a.energy!r}, range {a.range!r}")
    else:
        dst = pathlib.Path(a.paths[0])
        text, eol = _read(dst / SCENE)
        if text.count(f'[node name="{NAME}"') != 1:
            raise SystemExit("not exactly one probe node")
        head, tail = text.split(f'[node name="{NAME}"', 1)
        new_tail, n = re.subn(r"^light_energy = [0-9.eE+-]+$", f"light_energy = {a.energy!r}", tail,
                              count=1, flags=re.M)
        if n != 1:
            raise SystemExit("the probe node carries no energy line")
        old = re.search(r"^light_energy = ([0-9.eE+-]+)$", tail, flags=re.M).group(1)
        _write(dst / SCENE, head + f'[node name="{NAME}"' + new_tail, eol)
        print(f"{dst / SCENE}: {NAME} energy {old} -> {a.energy!r}")


if __name__ == "__main__":
    main()
