"""Where cold run 9315's roof hatch stands in the package, and two cameras to see it with.

The precinct's spec puts the hatch at (13, -9) on the roof (storey 2, 3.6 m storeys: the slab's top is z 7.2,
the slot's centre 7.3) in Deli Counter's frame -- x east, y north, z up. The building's GLB reaches Godot Y-up
as (x, z, -y), and the site stands the building at its own transform in `site.tscn`. This reads that transform
off the exported package, applies it to the slot's point, and prints `--station` arguments for
`tools/look_shots.py` (eye and target in Godot metres, Y up): one from the hinge side, one from the climber's.
It prints what it computed and stops.

    python hatch_station.py <package_dir> [<building id fragment> [x y z]]

The exported site stands library archetypes, not the generated precinct shell (9316's seed_9203: courthouse_a02,
clinic_a01, convenience_store_a01, airport_terminal_a01), so the hatch to frame is courthouse_a02's at
(-16, 12) on a 2 x 5.0 m building -- slot centre (-16, 12, 10.1) -- given on the command line.
"""
import pathlib
import re
import sys

SLOT_DC = (13.0, -9.0, 7.3)          # the precinct spec's hatch; the command line overrides it
LOCAL = None
EYE_OFFSETS = {"hatch_hinge_side": (3.5, 2.2, 4.5), "hatch_climber_side": (-3.5, 2.2, -4.5),
               "hatch_from_above": (0.5, 6.0, 0.5)}


def main(argv):
    pkg = pathlib.Path(argv[1])
    frag = argv[2] if len(argv) > 2 else "precinct"
    slot = tuple(float(v) for v in argv[3:6]) if len(argv) >= 6 else SLOT_DC
    local = (slot[0], slot[2], -slot[1])            # Godot, Y up
    text = (pkg / "site.tscn").read_text(encoding="utf-8")
    ext = {}
    for m in re.finditer(r'\[ext_resource type="PackedScene"[^\]]*path="([^"]+)"[^\]]*id="([^"]+)"', text):
        ext[m.group(2)] = m.group(1)
    nodes = re.split(r"\n(?=\[node )", text)
    found = []
    for n in nodes:
        head = n.split("\n", 1)[0]
        inst = re.search(r'instance=ExtResource\("([^"]+)"\)', head)
        if not inst:
            continue
        path = ext.get(inst.group(1), "")
        if frag not in path:
            continue
        name = re.search(r'name="([^"]+)"', head).group(1)
        t = re.search(r"transform = Transform3D\(([^)]+)\)", n)
        vals = [float(v) for v in t.group(1).split(",")] if t else [1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0]
        found.append((name, path, vals))
    if not found:
        print(f"no instanced node whose scene path contains {frag!r}; ext resources: {sorted(set(ext.values()))[:12]}")
        return 1
    for name, path, v in found:
        b = [[v[0], v[3], v[6]], [v[1], v[4], v[7]], [v[2], v[5], v[8]]]   # Godot stores basis columns
        o = (v[9], v[10], v[11])
        lx, ly, lz = local
        wx = b[0][0] * lx + b[0][1] * ly + b[0][2] * lz + o[0]
        wy = b[1][0] * lx + b[1][1] * ly + b[1][2] * lz + o[1]
        wz = b[2][0] * lx + b[2][1] * ly + b[2][2] * lz + o[2]
        print(f"node {name}  scene {path}")
        print(f"  building origin {o}  basis rows {b}")
        print(f"  hatch slot: spec {slot} -> local Godot {local} -> world ({wx:.2f}, {wy:.2f}, {wz:.2f})")
        for label, (dx, dy, dz) in EYE_OFFSETS.items():
            # the eye offsets are in the building's frame too, so the hinge side is the hinge side
            ex = b[0][0] * dx + b[0][1] * dy + b[0][2] * dz
            ey = b[1][0] * dx + b[1][1] * dy + b[1][2] * dz
            ez = b[2][0] * dx + b[2][1] * dy + b[2][2] * dz
            print(f"  --station {label}:{wx + ex:.2f},{wy + ey:.2f},{wz + ez:.2f},{wx:.2f},{wy:.2f},{wz:.2f}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
