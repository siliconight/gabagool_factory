"""Prototype: a building's scout MODEL (roadmap 295) -- the scout view's signals as a GLB a player turns all the way round.

One mesh a storey (so a viewer can lift the storeys apart), one material, colour in COLOR_0 (one draw a storey).
Built from the same layout readers the scout drawing uses: `floorplan.storey_walls` + `wall_split`,
`axonometric._slab_holes`, `stairwell.ascent_surfaces`, `setbacks.storey_extent`. Pure Python, no Blender.

    python scout_model.py <deli_counter> <spec name> <out.glb> [palette]
"""
import json
import math
import struct
import sys

DC = sys.argv[1]
sys.path.insert(0, DC)
import axonometric as AX  # noqa: E402
import floorplan as FP  # noqa: E402
import spec_loader  # noqa: E402
import stairwell as SW  # noqa: E402

CUT = 1.2            # walls stand to the plan cut, as the drawing's
CAP = 0.04           # the cut's dark cap on top of every wall
THRESH = 0.08        # a door's floor strip


def palettes():
    return {
        # an architect's card model: warm white walls, pale floors, inked cuts, brass stairs, red entries
        "model": {"slab": (0.70, 0.68, 0.64), "slab_side": (0.50, 0.48, 0.45), "wall": (0.95, 0.94, 0.91),
                  "cap": (0.16, 0.17, 0.19), "glass": (0.55, 0.74, 0.86), "door": (0.30, 0.33, 0.37),
                  "entry": (0.80, 0.22, 0.18), "tread": (0.78, 0.60, 0.30), "ladder": (0.15, 0.55, 0.55),
                  "hole_rim": (0.80, 0.22, 0.18), "bg": (0.13, 0.14, 0.16)},
        # a night blueprint: deep blue slabs, pale cyan walls, white cuts, amber stairs
        "blueprint": {"slab": (0.10, 0.20, 0.38), "slab_side": (0.07, 0.14, 0.28), "wall": (0.62, 0.82, 0.95),
                      "cap": (0.95, 0.98, 1.00), "glass": (0.35, 0.95, 0.95), "door": (0.85, 0.92, 1.00),
                      "entry": (1.00, 0.45, 0.25), "tread": (1.00, 0.75, 0.25), "ladder": (0.40, 1.00, 0.70),
                      "hole_rim": (1.00, 0.45, 0.25), "bg": (0.03, 0.06, 0.12)},
        # a heist dossier: paper and ink, one red for what matters
        "dossier": {"slab": (0.90, 0.87, 0.78), "slab_side": (0.70, 0.66, 0.56), "wall": (0.30, 0.29, 0.27),
                    "cap": (0.12, 0.11, 0.10), "glass": (0.60, 0.66, 0.66), "door": (0.45, 0.42, 0.38),
                    "entry": (0.75, 0.10, 0.10), "tread": (0.55, 0.50, 0.42), "ladder": (0.75, 0.10, 0.10),
                    "hole_rim": (0.75, 0.10, 0.10), "bg": (0.82, 0.79, 0.70)},
    }


class Mesh:
    def __init__(self):
        self.pos, self.nrm, self.col, self.idx = [], [], [], []

    def quad(self, a, b, c, d, n, col):
        base = len(self.pos)
        for p in (a, b, c, d):
            # spec metres (x east, y north, z up) to glTF (x, y up, z south)
            self.pos.append((p[0], p[2], -p[1]))
            self.nrm.append((n[0], n[2], -n[1]))
            # the palette is written as on screen (sRGB); glTF's COLOR_0 is linear
            self.col.append(tuple(((c / 12.92) if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4) for c in col)
                            + (1.0,))
        self.idx += [base, base + 1, base + 2, base, base + 2, base + 3]

    def box(self, x0, y0, z0, x1, y1, z1, col, side=None, top=None, sides="snwe"):
        side = side or col
        top = top or col
        q = self.quad
        q((x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1), (0, 0, 1), top)
        q((x0, y1, z0), (x1, y1, z0), (x1, y0, z0), (x0, y0, z0), (0, 0, -1), side)
        if "s" in sides:
            q((x0, y0, z0), (x1, y0, z0), (x1, y0, z1), (x0, y0, z1), (0, -1, 0), side)
        if "n" in sides:
            q((x1, y1, z0), (x0, y1, z0), (x0, y1, z1), (x1, y1, z1), (0, 1, 0), side)
        if "w" in sides:
            q((x0, y1, z0), (x0, y0, z0), (x0, y0, z1), (x0, y1, z1), (-1, 0, 0), side)
        if "e" in sides:
            q((x1, y0, z0), (x1, y1, z0), (x1, y1, z1), (x1, y0, z1), (1, 0, 0), side)


def _minus(rect, holes):
    """`rect` less every hole, as rectangles: a grid on every hole edge, each cell kept unless a hole covers it."""
    x0, y0, x1, y1 = rect
    xs = sorted({x0, x1} | {min(max(h[i], x0), x1) for h in holes for i in (0, 2)})
    ys = sorted({y0, y1} | {min(max(h[i], y0), y1) for h in holes for i in (1, 3)})
    out = []
    for a, b in zip(xs, xs[1:]):
        for c, d in zip(ys, ys[1:]):
            if b - a < 1e-6 or d - c < 1e-6:
                continue
            mx, my = (a + b) / 2, (c + d) / 2
            if not any(h[0] <= mx <= h[2] and h[1] <= my <= h[3] for h in holes):
                out.append((a, c, b, d))
    return out


def build(spec, pal):
    sh = FP._story_height(spec)
    t_floor = getattr(spec, "floor_thick", 0.3) or 0.3
    holes = AX._slab_holes(spec)
    try:
        import setbacks
        extent = {s: setbacks.storey_extent(spec, s) for s in FP.stories_in(spec)}
    except Exception:
        hx, hy = spec.footprint_x / 2, spec.footprint_y / 2
        extent = {s: (-hx, -hy, hx, hy) for s in FP.stories_in(spec)}
    bound = {"x": spec.footprint_x / 2, "y": spec.footprint_y / 2}
    storeys = {}
    for s in FP.stories_in(spec):
        m = Mesh()
        ex = extent[s]
        hs = [r for r, _k in holes.get(s, [])]
        cells = _minus(ex, hs)
        for r in cells:
            # a side only where no cell of the same slab sits against it: the outer edge and a hole's edge
            def against(x0, y0, x1, y1):
                return any(abs(c[0] - x0) < 1e-6 and abs(c[2] - x1) < 1e-6 and abs(c[1] - y0) < 1e-6
                           and abs(c[3] - y1) < 1e-6 for c in cells)
            sides = "".join(k for k, nb in (("s", (r[0], None, r[2], r[1])), ("n", (r[0], r[3], r[2], None)),
                                            ("w", (None, r[1], r[0], r[3])), ("e", (r[2], r[1], None, r[3])))
                            if not any((nb[1] is None and abs(c[1] - r[3]) < 1e-6 or
                                        nb[3] is None and abs(c[3] - r[1]) < 1e-6 or
                                        nb[0] is None and abs(c[0] - r[2]) < 1e-6 or
                                        nb[2] is None and abs(c[2] - r[0]) < 1e-6)
                                       and (abs(c[0] - r[0]) < 1e-6 and abs(c[2] - r[2]) < 1e-6
                                            if k in "sn" else abs(c[1] - r[1]) < 1e-6 and abs(c[3] - r[3]) < 1e-6)
                                       for c in cells))
            m.box(r[0], r[1], -t_floor, r[2], r[3], 0.0, pal["slab"], side=pal["slab_side"], sides=sides)
        for r, kind in holes.get(s, []):   # a hole's rim, so it reads as an opening from any side
            w = 0.06
            for rr in ((r[0], r[1] - w, r[2], r[1]), (r[0], r[3], r[2], r[3] + w),
                       (r[0] - w, r[1], r[0], r[3]), (r[2], r[1], r[2] + w, r[3])):
                m.box(rr[0], rr[1], 0.0, rr[2], rr[3], 0.02, pal["hole_rim" if kind != "stair" else "tread"])
        for wall in FP.storey_walls(spec, s):
            t = wall["t"]
            ops = []
            for op in wall["openings"]:
                try:
                    res = op.resolved()
                except Exception:
                    res = {"sill": getattr(op, "sill", 0.0) or 0.0}
                if float(res.get("sill") or 0.0) < CUT:
                    ops.append((op, float(res.get("sill") or 0.0)))
            fixed, lo, hi, segs, gaps = FP.wall_split(wall["p0"], wall["p1"], wall["axis"], [o for o, _ in ops],
                                                      bound[wall["axis"]])
            sills = {id(o): sl for o, sl in ops}
            exterior = wall["name"].startswith("ext")

            def rect(a, b, axis=wall["axis"], fixed=fixed, t=t):
                return (a, fixed - t / 2, b, fixed + t / 2) if axis == "x" else (fixed - t / 2, a, fixed + t / 2, b)
            for a, b in segs:
                r = rect(a, b)
                m.box(r[0], r[1], 0.0, r[2], r[3], CUT - CAP, pal["wall"])
                m.box(r[0], r[1], CUT - CAP, r[2], r[3], CUT, pal["cap"])
            for glo, ghi, op, c, w in gaps:
                if c < lo or c > hi:
                    continue
                glo, ghi = max(glo, lo), min(ghi, hi)
                r = rect(glo, ghi)
                sill = sills.get(id(op), 0.0)
                if sill > 1e-6:      # a window: its sill wall, then glass to the cut
                    m.box(r[0], r[1], 0.0, r[2], r[3], sill, pal["wall"])
                    m.box(r[0], r[1], sill, r[2], r[3], CUT, pal["glass"])
                else:                # a door: a strip across the floor, red where it lets you in from outside
                    m.box(r[0], r[1], 0.0, r[2], r[3], THRESH, pal["entry"] if exterior else pal["door"])
        for i, st in enumerate(getattr(spec, "stairs", []) or []):
            surfaces = [u for u in SW.ascent_surfaces(spec, st) if u[0] == s]
            if not surfaces:
                continue
            riser = sh / SW._step_count(st, sh)
            solid = SW.flight_solid_under(spec, st, s)
            for (_s, tx, ty, ztop, ssx, ssy) in surfaces:
                z1 = ztop - s * sh
                z0 = 0.0 if solid else max(0.0, z1 - riser)
                m.box(tx - ssx / 2, ty - ssy / 2, z0, tx + ssx / 2, ty + ssy / 2, z1, pal["tread"])
        for ld in getattr(spec, "ladders", []) or []:
            a, b = sorted((ld.from_story, ld.to_story))
            if a <= s < b:           # rails from this floor up to the next
                for dx in (-0.22, 0.22):
                    m.box(ld.x + dx - 0.03, ld.y - 0.03, 0.0, ld.x + dx + 0.03, ld.y + 0.03, sh, pal["ladder"])
                k = 0.3
                while k < sh:
                    m.box(ld.x - 0.22, ld.y - 0.02, k, ld.x + 0.22, ld.y + 0.02, k + 0.03, pal["ladder"])
                    k += 0.3
        storeys[s] = m
    return storeys, sh


def write_glb(storeys, sh, path, name):
    bin_ = bytearray()
    views, accs, meshes, nodes = [], [], [], []

    def add(data, target, comp, typ, count, mn=None, mx=None):
        while len(bin_) % 4:
            bin_.append(0)
        views.append({"buffer": 0, "byteOffset": len(bin_), "byteLength": len(data), "target": target})
        bin_.extend(data)
        a = {"bufferView": len(views) - 1, "componentType": comp, "count": count, "type": typ}
        if mn is not None:
            a["min"], a["max"] = mn, mx
        accs.append(a)
        return len(accs) - 1

    for s in sorted(storeys):
        m = storeys[s]
        if not m.idx:
            continue
        p = add(b"".join(struct.pack("<3f", *v) for v in m.pos), 34962, 5126, "VEC3", len(m.pos),
                [min(v[i] for v in m.pos) for i in range(3)], [max(v[i] for v in m.pos) for i in range(3)])
        n = add(b"".join(struct.pack("<3f", *v) for v in m.nrm), 34962, 5126, "VEC3", len(m.nrm))
        c = add(b"".join(struct.pack("<4f", *v) for v in m.col), 34962, 5126, "VEC4", len(m.col))
        i = add(b"".join(struct.pack("<I", v) for v in m.idx), 34963, 5125, "SCALAR", len(m.idx))
        meshes.append({"name": "storey_%d" % s, "primitives": [
            {"attributes": {"POSITION": p, "NORMAL": n, "COLOR_0": c}, "indices": i, "material": 0}]})
        nodes.append({"name": "storey_%d" % s, "mesh": len(meshes) - 1, "translation": [0.0, s * sh, 0.0],
                      "extras": {"storey": s, "elevation": s * sh}})
    gltf = {"asset": {"version": "2.0", "generator": "deli_counter scout_model prototype"},
            "scene": 0, "scenes": [{"name": name, "nodes": list(range(len(nodes)))}], "nodes": nodes,
            "meshes": meshes, "materials": [{"name": "scout", "pbrMetallicRoughness": {
                "baseColorFactor": [1, 1, 1, 1], "metallicFactor": 0.0, "roughnessFactor": 0.85}}],
            "accessors": accs, "bufferViews": views, "buffers": [{"byteLength": len(bin_)}]}
    js = json.dumps(gltf, separators=(",", ":")).encode()
    js += b" " * ((4 - len(js) % 4) % 4)
    while len(bin_) % 4:
        bin_.append(0)
    out = struct.pack("<III", 0x46546C67, 2, 12 + 8 + len(js) + 8 + len(bin_))
    out += struct.pack("<II", len(js), 0x4E4F534A) + js + struct.pack("<II", len(bin_), 0x004E4942) + bytes(bin_)
    with open(path, "wb") as f:
        f.write(out)
    tris = sum(len(storeys[s].idx) // 3 for s in storeys)
    return len(out), tris, len(meshes)


if __name__ == "__main__":
    import os
    spec = spec_loader.load_spec(os.path.join(DC, "specs", sys.argv[2] + ".json"))
    pal = palettes()[sys.argv[4] if len(sys.argv) > 4 else "model"]
    st, sh = build(spec, pal)
    size, tris, n = write_glb(st, sh, sys.argv[3], spec.name)
    print("%s: %d bytes, %d triangles, %d storey meshes, storey height %.2f m" % (sys.argv[3], size, tris, n, sh))
