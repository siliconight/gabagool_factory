"""Copy a club project with its stage rigs switched live, the dial that works.

    python make_live_copy.py <project> <copy> [--energy-scale K]

THE DIAL IS THE RESOURCE. `lux_stage_light_rig.gd`'s `_rebuild()` frees every
saved lamp at load and makes it again from the rig's `LuxLightRig` resource,
so an edit to a saved SpotLight3D never runs (cold run 9204's NOTES keep the
on/off that learned this). This edits the resource: in
`presentation/lux.applied.tscn`, every sub_resource whose `rig_name` is
"Stage Light (baked)" gets `bake_mode = 0` -- `apply_bake_mode` then leaves
the lamp at Godot's default, BAKE_DYNAMIC, and `_cycles()` lets the colour
cycle run -- and, with `--energy-scale`, its `energy` multiplied by K.

What it does NOT change: the lightmap. The copy keeps the bake it was given,
which holds the stage lamps' light, so a frame of the copy shows the baked
wash plus the live lamps.

Refuses: a copy that already exists, a scene with no stage rig resource, a
stage rig resource without exactly one `bake_mode = 1` and one `energy` line.
Prints what it changed and stops.
"""
import argparse
import pathlib
import re
import shutil

SCENE = pathlib.Path("presentation") / "lux.applied.tscn"
STAGE = 'rig_name = &"Stage Light (baked)"'

ap = argparse.ArgumentParser()
ap.add_argument("project")
ap.add_argument("copy")
ap.add_argument("--energy-scale", type=float, default=1.0)
a = ap.parse_args()

src, dst = pathlib.Path(a.project), pathlib.Path(a.copy)
if dst.exists():
    raise SystemExit(f"{dst} exists; refusing to write over it")
if not (src / SCENE).is_file():
    raise SystemExit(f"{src / SCENE} not found")
shutil.copytree(src, dst)
path = dst / SCENE
data = path.read_bytes()
eol = b"\r\n" if b"\r\n" in data else b"\n"
text = data.decode("utf-8").replace("\r\n", "\n")
blocks = re.split(r"(?=^\[)", text, flags=re.M)
changed = []
for i, b in enumerate(blocks):
    if not b.startswith('[sub_resource type="Resource"') or STAGE not in b:
        continue
    rid = re.match(r'\[sub_resource type="Resource" id="([^"]+)"\]', b).group(1)
    if len(re.findall(r"^bake_mode = 1$", b, flags=re.M)) != 1:
        raise SystemExit(f"{rid}: not exactly one 'bake_mode = 1'")
    energies = re.findall(r"^energy = ([0-9.eE+-]+)$", b, flags=re.M)
    if len(energies) != 1:
        raise SystemExit(f"{rid}: not exactly one 'energy' line")
    e0 = float(energies[0])
    b = re.sub(r"^bake_mode = 1$", "bake_mode = 0", b, flags=re.M)
    b = re.sub(r"^energy = [0-9.eE+-]+$", f"energy = {e0 * a.energy_scale!r}", b, flags=re.M)
    blocks[i] = b
    changed.append((rid, e0, e0 * a.energy_scale))
if not changed:
    raise SystemExit(f"{path}: no {STAGE} resource")
out = "".join(blocks)
path.write_bytes(out.replace("\n", eol.decode()).encode("utf-8"))
for rid, e0, e1 in changed:
    print(f"{rid}: bake_mode 1 -> 0, energy {e0:.4f} -> {e1:.4f}")
print(f"{len(changed)} stage rig resource(s) live in {path}")
