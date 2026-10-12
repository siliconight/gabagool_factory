"""Where the backdrop stands, read from the scene file (roadmap 243, 2026-10-12).

    python docs/findings/lux_tiers/backdrop_casters.py [<package>]

`sun_casters.gd` cannot place a MultiMesh's instances headless (see its docstring); the package's
`site_backdrop.tscn` writes every instance's transform in its MultiMesh's `buffer` (transform_format 1:
twelve floats an instance, three rows of basis and origin). This reads them and prints, for each side
the backdrop's MultiMeshes are named by (`__N`, `__E`, `__S`, `__W`), the instance count, the range of
their origins (Godot's x and z, metres) and their heights (the `_h<cm>` in the species' name, which
`sun_casters.gd` read off the meshes as the same 8.0-11.0 and 40.0 m), and whether the side stands
toward the sun of cold run 9264's `blue_hour` (toward it (-0.937, 0.070, -0.341), from `sun_casters.gd`):
a side whose outward direction points at the sun stands between it and the level. A buffer whose
length is not twelve an instance, or a transform format other than 1, stops it. It measures and prints.
"""
import collections
import pathlib
import re
import sys

F = pathlib.Path(__file__).resolve().parents[3]
PKG = F / "workspaces" / "cold-9264-ws" / ".level_factory" / "exports" / "LF_restaurant_row_001.portable-godot"
TO_SUN = (-0.937, -0.341)   # (x, z) toward the sun, `sun_casters.gd` on 9264's package
OUTWARD = {"N": (0.0, -1.0), "S": (0.0, 1.0), "E": (1.0, 0.0), "W": (-1.0, 0.0)}
MM = re.compile(r'\[sub_resource type="MultiMesh" id="MM_([^"]+)"\]\n(.*?)\n\n', re.S)


def main():
    pkg = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else PKG
    text = (pkg / "site_backdrop.tscn").read_bytes().decode("utf-8").replace("\r\n", "\n")
    sides = collections.defaultdict(list)
    for m in MM.finditer(text + "\n\n"):
        name, body = m.group(1), m.group(2)
        fmt = re.search(r"^transform_format = (\d+)$", body, re.M)
        if fmt is None or fmt.group(1) != "1":
            sys.exit("UNKNOWN SHAPE: transform format %r in %s" % (fmt and fmt.group(1), name))
        n = int(re.search(r"^instance_count = (\d+)$", body, re.M).group(1))
        buf = [float(x) for x in re.search(r"^buffer = PackedFloat32Array\(([^)]*)\)$", body, re.M).group(1).split(",")]
        if len(buf) != 12 * n:
            sys.exit("UNKNOWN SHAPE: %d floats for %d instances in %s" % (len(buf), n, name))
        h = int(re.search(r"_h(\d+)__", name).group(1)) / 100.0
        side = name.rsplit("__", 1)[1]
        kind = name.split("_delco")[0]
        for i in range(n):
            b = buf[12 * i:12 * i + 12]
            sides[side].append((b[3], b[11], h, kind))
    if not sides:
        sys.exit("UNKNOWN SHAPE: no MultiMesh in site_backdrop.tscn")
    total = sum(len(v) for v in sides.values())
    print("site_backdrop.tscn: %d instances" % total)
    for side in sorted(sides):
        v = sides[side]
        xs, zs, hs = [p[0] for p in v], [p[1] for p in v], [p[2] for p in v]
        o = OUTWARD.get(side)
        facing = "?" if o is None else ("toward the sun" if o[0] * TO_SUN[0] + o[1] * TO_SUN[1] > 0 else "away from it")
        print("  %s: %3d instances, x %7.1f..%7.1f, z %7.1f..%7.1f, %4.1f..%4.1f m high, %s (%s)" % (
            side, len(v), min(xs), max(xs), min(zs), max(zs), min(hs), max(hs), facing,
            ", ".join(sorted({p[3] for p in v}))))


if __name__ == "__main__":
    main()
