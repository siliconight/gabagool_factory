"""Plan of one storey of a building, in the BUILDING frame: the bake's navmesh
polygons coloured by island, every mesh node standing in the body's height
band as an outline, and the gameplay stair footprints and landings dashed.
Draws what was measured; names no cause.

    python stairwell_plan.py <sweep.json> <site.site.drawn.json> <archetype> <glb> <out.png>
        --region x0 x1 y0 y1 --floor h [--band 0.4] [--islands 0,9]

Navmesh heights are polygon heights in metres; `--floor` picks the storey's
navmesh height (0.25 for deli_a01's ground floor). Obstacles are nodes whose
box overlaps z 0.15..1.8 above the storey's slab top (z = floor - 0.25),
excluding slabs: 0.15 is the bake's agent_max_climb, 1.8 its agent_height.
"""
import json
import os
import sys

from PIL import Image, ImageDraw  # noqa: E402

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))   # glb_region_nodes beside it
from glb_region_nodes import boxes  # noqa: E402


def opt(argv, name, n=1, default=None):
    if name not in argv:
        return default
    i = argv.index(name)
    return argv[i + 1:i + 1 + n] if n > 1 else argv[i + 1]


def main():
    argv = sys.argv[1:]
    sweep, drawn, arch, glb, out = argv[:5]
    x0, x1, y0, y1 = [float(v) for v in opt(argv, "--region", 4)]
    hz = float(opt(argv, "--floor"))
    band = float(opt(argv, "--band", default="0.4"))
    named = [int(v) for v in opt(argv, "--islands", default="0,9").split(",")]
    spec = json.load(open(drawn, encoding="utf-8"))
    bld = [b for b in spec["buildings"] if b.get("archetype") == arch]
    assert len(bld) == 1 and float(bld[0].get("rot", 0) or 0) == 0.0, "one building at rot 0 only"
    bld = bld[0]
    ax, ay = bld["at"]
    g = json.load(open(bld["gameplay"], encoding="utf-8"))
    dump = json.load(open(sweep, encoding="utf-8"))
    b = dump["bakes"][0]
    v = b["verts"]
    colours = {named[0]: (74, 127, 212), named[1]: (232, 137, 58)} if len(named) > 1 else {named[0]: (74, 127, 212)}
    S = 60                                   # pixels per metre
    W, H = int((x1 - x0) * S), int((y1 - y0) * S)
    img = Image.new("RGB", (W, H + 40), "white")
    d = ImageDraw.Draw(img, "RGBA")

    def px(x, y):                            # building frame -> image (y up)
        return ((x - x0) * S, (y1 - y) * S)

    for gx in range(int(x0), int(x1) + 1):
        d.line([px(gx, y0), px(gx, y1)], fill=(220, 220, 220), width=1)
    for gy in range(int(y0), int(y1) + 1):
        d.line([px(x0, gy), px(x1, gy)], fill=(220, 220, 220), width=1)
    counts = {}
    for k, idx in b["polys_list"]:
        p = [v[i] for i in idx]
        h = sum(q[1] for q in p) / len(p)
        if abs(h - hz) > band:
            continue
        pts = [(q[0] - ax, -q[2] - ay) for q in p]
        cx = sum(q[0] for q in pts) / len(pts)
        cy = sum(q[1] for q in pts) / len(pts)
        if not (x0 <= cx <= x1 and y0 <= cy <= y1):
            continue
        counts[k] = counts.get(k, 0) + 1
        c = colours.get(k, (187, 187, 187))
        d.polygon([px(*q) for q in pts], fill=c + (190,), outline=(255, 255, 255, 255))
    slab_top = hz - 0.25
    for name, (lo, hi) in boxes(glb).items():
        if name.startswith("slab"):
            continue
        if hi[0] < x0 or lo[0] > x1 or hi[1] < y0 or lo[1] > y1:
            continue
        if hi[2] < slab_top + 0.15 or lo[2] > slab_top + 1.8:
            continue
        col = (20, 20, 20) if "colonly" not in name else (200, 40, 40)
        (ax0, ay1), (ax1, ay0) = px(lo[0], lo[1]), px(hi[0], hi[1])
        d.rectangle([ax0, ay0, ax1, ay1], outline=col, width=2 if "colonly" not in name else 1)
        if "colonly" not in name and (hi[0] - lo[0]) * (hi[1] - lo[1]) > 0.05:
            d.text(((ax0 + ax1) / 2 - 30, (ay0 + ay1) / 2 - 5), name[:22], fill=(0, 0, 0))
    for st in g.get("stair_systems", []):
        fp = st.get("footprint_polygon") or []
        if fp:
            d.polygon([px(*q) for q in fp], outline=(42, 157, 74))
            d.text(px(fp[0][0], fp[0][1] - 0.1), st["id"], fill=(42, 157, 74))
        for L in st.get("landings", []):
            r = L.get("rect")
            if r and abs(L.get("story", 0) * 3.3 - slab_top) < 1.0:
                (lx0, ly1), (lx1, ly0) = px(r[0], r[1]), px(r[2], r[3])
                d.rectangle([lx0, ly0, lx1, ly1], outline=(42, 157, 74), width=3)
    d.text((6, H + 4), "%s navmesh h %.2f +- %.2f: island %s blue, island %s orange, others grey. Black = visual node, red = collision-only, green = stair footprint / landing (thick). Grid 1 m; x %.1f..%.1f, y %.1f..%.1f (building frame)"
           % (arch, hz, band, named[0], named[1] if len(named) > 1 else "-", x0, x1, y0, y1), fill=(0, 0, 0))
    img.save(out)
    print("polygons drawn by island:", dict(sorted(counts.items())))
    print("wrote", out)


if __name__ == "__main__":
    main()
