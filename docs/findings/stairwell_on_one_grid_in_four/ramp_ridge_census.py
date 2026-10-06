"""How far does each stair's collision ramp stand above the floor it delivers
to? Read from every library GLB's own collider geometry, node transforms
applied (translation, rotation, scale). Measures; names no cause.

    python ramp_ridge_census.py [--only a,b]

A ramp is a node named `stair<N>ramp_<story>` (an L-stair's legs:
`stair<N>aramp_` and `bramp_`); its top is the highest vertex.
The floor it delivers to is the top of the slab collider of the storey above
the ramp's own (`slab_col_<story+1>`). Frame: the building's own Godot frame,
metres, y up.

Why: Laser Tag's player bodies stuck 3,148 times at the head of deli_a03's
up-stair in cold run 9186 (seed_9003), at the top edge of that ramp, which
stands 0.2 m above the floor. A capsule walks up about 0.10 m unassisted
(agent_contract `unassisted_step_max_m`); the navmesh climbs 0.15 and Lot's
walkers step 0.5, so neither of those instruments saw it.
"""
import glob
import json
import os
import re
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BUILD = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(HERE))), "deli_counter", "build")


def _load(path):
    b = open(path, "rb").read()
    n = struct.unpack_from("<I", b, 12)[0]
    return b, json.loads(b[20:20 + n]), 20 + n + 8


def _verts(b, gl, binoff, mesh_i):
    out = []
    for prim in gl["meshes"][mesh_i]["primitives"]:
        a = gl["accessors"][prim["attributes"]["POSITION"]]
        v = gl["bufferViews"][a["bufferView"]]
        off = binoff + v.get("byteOffset", 0) + a.get("byteOffset", 0)
        stride = v.get("byteStride", 12)
        for i in range(a["count"]):
            out.append(struct.unpack_from("<3f", b, off + i * stride))
    return out


def _qrot(q, v):
    x, y, z, w = q
    vx, vy, vz = v
    cx, cy, cz = y * vz - z * vy, z * vx - x * vz, x * vy - y * vx
    dx, dy, dz = y * cz - z * cy, z * cx - x * cz, x * cy - y * cx
    return (vx + 2 * (w * cx + dx), vy + 2 * (w * cy + dy), vz + 2 * (w * cz + dz))


def _world(b, gl, binoff, nd):
    t = nd.get("translation", [0, 0, 0])
    q = nd.get("rotation", [0, 0, 0, 1])
    s = nd.get("scale", [1, 1, 1])
    return [tuple(a + c for a, c in zip(_qrot(q, (x * s[0], y * s[1], z * s[2])), t))
            for x, y, z in _verts(b, gl, binoff, nd["mesh"])]


def main():
    only = None
    if "--only" in sys.argv:
        only = set(sys.argv[sys.argv.index("--only") + 1].split(","))
    rows = []
    for path in sorted(glob.glob(os.path.join(BUILD, "*.glb"))):
        name = os.path.basename(path)[:-4]
        if name.startswith("lf_") or (only and name not in only):
            continue
        b, gl, binoff = _load(path)
        slabs, ramps = {}, []
        for nd in gl.get("nodes", []):
            nm = nd.get("name", "")
            if "mesh" not in nd:
                continue
            m = re.match(r"slab_col_(-?\d+)", nm)
            if m:
                slabs[int(m.group(1))] = max(v[1] for v in _world(b, gl, binoff, nd))
            m = re.match(r"stair(\d+)[ab]?ramp_(-?\d+)", nm)
            if m:
                ramps.append((nm, int(m.group(2)), max(v[1] for v in _world(b, gl, binoff, nd))))
        for nm, story, top in ramps:
            floor = slabs.get(story + 1)
            if floor is None:
                continue
            rows.append((name, nm, round(top, 3), round(floor, 3), round(top - floor, 3)))
    rows.sort(key=lambda r: -r[4])
    above = [r for r in rows if r[4] > 0.005]
    print("ramps measured: %d in %d shells; standing above the floor they deliver to: %d"
          % (len(rows), len({r[0] for r in rows}), len(above)))
    buckets = {}
    for r in rows:
        k = round(r[4], 2)
        buckets[k] = buckets.get(k, 0) + 1
    print("overshoot (m) -> ramps:", dict(sorted(buckets.items())))
    for r in rows[:25]:
        print("  %-30s %-22s ramp top %.3f  floor %.3f  above by %.3f" % r)


if __name__ == "__main__":
    main()
