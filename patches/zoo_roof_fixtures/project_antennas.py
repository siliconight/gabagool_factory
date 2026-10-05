"""Where every placed TV antenna lands in a frame, in pixels.

    python project_antennas.py <run> <png> <cam x y z> <target x y z> [fov_v]

Rebuilds each antenna's parts (Zoo's own `antenna_parts`, from the run's
Patina order: `pos`, `tangent`, `size2`) in its building's frame, places the
building where the drawn site put it (`blockers[]`: `at`, `rot`; Lot turns a
building by (x c - y s, x s + y c)), takes plan (x, y) and height h to Godot
(x, h, -y), and projects through a Godot camera at <cam> looking at
<target> with a vertical field of view of <fov_v> degrees (default 65, the
frame script's). Prints, per antenna: its house, the bounding box of its
projected parts in the PNG's pixels, and the mast's top. Frame: Godot world,
metres; pixels from the PNG's top-left.
"""
import json
import math
import pathlib
import struct
import sys

F = pathlib.Path(r"C:\Projects\gabagool_studios\gabagool_factory")
sys.path.insert(0, str(F / "zoo"))
from zoo_keeper.core.dressing import antenna_parts  # noqa: E402

run, png = sys.argv[1], pathlib.Path(sys.argv[2])
eye = [float(v) for v in sys.argv[3:6]]
tgt = [float(v) for v in sys.argv[6:9]]
fov = float(sys.argv[9]) if len(sys.argv) > 9 else 65.0
raw = png.read_bytes()
assert raw[:8] == b"\x89PNG\r\n\x1a\n"
W, H = struct.unpack(">II", raw[16:24])
WS = F / "workspaces" / f"cold-{run}-ws" / ".level_factory" / "jobs"


def sub(a, b):
    return [a[i] - b[i] for i in range(3)]


def dot(a, b):
    return sum(a[i] * b[i] for i in range(3))


def cross(a, b):
    return [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]]


def unit(a):
    n = math.sqrt(dot(a, a))
    return [x / n for x in a]


fwd = unit(sub(tgt, eye))
right = unit(cross(fwd, [0.0, 1.0, 0.0]))
up = cross(right, fwd)
focal = (H / 2.0) / math.tan(math.radians(fov) / 2.0)


def project(p):
    v = sub(p, eye)
    z = dot(v, fwd)
    if z <= 0.05:
        return None
    return (W / 2.0 + focal * dot(v, right) / z, H / 2.0 - focal * dot(v, up) / z)


site = json.loads((WS / "gas_block_001.lot_assemble.candidate.seed_9080" / "out" / "site.site.drawn.json")
                  .read_text(encoding="utf-8"))
print(f"frame {W}x{H}, eye {eye}, target {tgt}, fov_v {fov}")
for b in site["blockers"]:
    if not b.get("empty"):
        continue
    bid = b["archetype"]
    man = WS / f"gas_block_001.patina_dressing.{bid}" / "out" / f"{bid}.patina.dressing.json"
    for o in json.loads(man.read_text(encoding="utf-8"))["orders"]:
        if o["cover"] != "tv_antenna":
            continue
        tx, ty = o["tangent"][0], o["tangent"][1]
        yaw = math.atan2(ty, tx)
        c, s = math.cos(yaw), math.sin(yaw)
        r = math.radians(float(b["rot"]))
        rc, rs = math.cos(r), math.sin(r)
        pts, top = [], None
        for k, ((cx, cy, cz), (sx, sy, sz)) in enumerate(antenna_parts(*o["size2"])):
            for dx in (-sx / 2, sx / 2):
                for dy in (-sy / 2, sy / 2):
                    for dz in (-sz / 2, sz / 2):
                        lx, ly, lz = cx + dx, cy + dy, cz + dz
                        bx = o["pos"][0] + lx * c - ly * s          # the building's frame
                        by = o["pos"][1] + lx * s + ly * c
                        bz = o["pos"][2] + lz
                        px = b["at"][0] + bx * rc - by * rs          # the plan
                        py = b["at"][1] + bx * rs + by * rc
                        q = project([px, bz, -py])                   # Godot
                        if q:
                            pts.append(q)
                            if k == 1 and dz > 0:
                                top = q
        if pts:
            xs, ys = [p[0] for p in pts], [p[1] for p in pts]
            on = min(xs) < W and max(xs) > 0 and min(ys) < H and max(ys) > 0
            print(f"  {b['id']:>4} {bid}: x {min(xs):7.0f}..{max(xs):7.0f}  y {min(ys):6.0f}..{max(ys):6.0f}"
                  f"  mast top {('%.0f,%.0f' % top) if top else '-'}  {'IN FRAME' if on else ''}")
