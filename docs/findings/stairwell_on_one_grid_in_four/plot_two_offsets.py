"""Draw deli_a03's ground-floor navmesh around its stairwell for the two bakes
in sweep_dump2.json (grid offsets [0, 0, 0] and [0.075, 0, 0]), coloured by
island. Writes deli_a03_stairwell_two_offsets.png.

    python run_bake_sweep.py <staged project> res://buildings/deli_a03.glb pts_bldg.json sweep2.json --label dump2 --dump
    python plot_two_offsets.py

Frame: the building's own Godot frame (x, z = -DC y), metres. Lines are taken
from deli_a03.gameplay.json: red = interior walls int_0_1 (DC y 6) and int_0_0
(DC x -8), green = office_stair_door (x -15, 1.25 m), magenta = deli_stair_up's
axis, cyan = deli_stair_down's axis.
"""
import json
import os

from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
X0, X1, Z0, Z1, S = -20.5, -5.5, -15.5, 5.0, 40  # metres, pixels per metre


def px(x, z):
    return ((x - X0) * S, (z - Z0) * S)


def main():
    d = json.load(open(os.path.join(HERE, "sweep_dump2.json")))
    w, h = int((X1 - X0) * S), int((Z1 - Z0) * S)
    tiles = []
    for b in d["bakes"]:
        im = Image.new("RGB", (w, h + 30), "white")
        dr = ImageDraw.Draw(im)
        vs = b["verts"]
        main_isl = b["points"]["kitchen"][0]
        stair_isl = b["points"]["stair_lo"][0]
        for isl, poly in b["polys_list"]:
            pts = [vs[i] for i in poly]
            mean_y = sum(p[1] for p in pts) / len(pts)
            if not (-0.6 < mean_y < 1.6):  # ground floor only
                continue
            col = ((74, 127, 212) if isl == main_isl
                   else (240, 138, 36) if isl == stair_isl else (160, 160, 160))
            dr.polygon([px(p[0], p[2]) for p in pts], fill=col, outline=(0, 0, 0))
        dr.line([px(-19, -6), px(19, -6)], fill=(220, 0, 0), width=2)
        dr.line([px(-8, -14), px(-8, 14)], fill=(220, 0, 0), width=2)
        dr.line([px(-15.625, -6), px(-14.375, -6)], fill=(0, 220, 0), width=6)
        dr.line([px(-11.8, -11.6), px(-11.8, -5.6)], fill=(200, 0, 200), width=3)
        dr.line([px(-15.8, -11.6), px(-15.8, -5.6)], fill=(0, 200, 200), width=3)
        for gx in range(-20, -5):
            dr.text(px(gx, 4.4), str(gx), fill=(0, 0, 0))
        dr.text((5, h + 8), "grid offset %s: blue = street island, orange = "
                "stair island, green = 1.25 m door" % b["offset"], fill=(0, 0, 0))
        tiles.append(im)
    out = Image.new("RGB", (w * 2 + 20, h + 30), "white")
    out.paste(tiles[0], (0, 0))
    out.paste(tiles[1], (w + 20, 0))
    out.save(os.path.join(HERE, "deli_a03_stairwell_two_offsets.png"))


if __name__ == "__main__":
    main()
