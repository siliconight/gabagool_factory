"""How much of each drop hole a Deli Counter's hole slots draw greybox over, in the hole's own slab, over the library.

A probe: prints what it measured and stops. Reads `hole_causes.hole_slots` in either shape -- 0.236.0's
``(slot, entry, center, size)``, one box a slot, and 0.236.1's ``(slot, entry, boxes)`` -- and, for every box whose
height range meets the slab a hole is cut in, the plan area it covers inside the hole's rect (m2).

    python greybox_over_holes.py <deli_counter repo>
"""
import glob
import json
import os
import sys

REPO = os.path.abspath(sys.argv[1])
sys.path.insert(0, REPO)
import hole_causes as HC  # noqa: E402

total, holes_hit, n_holes = 0.0, 0, 0
for p in sorted(glob.glob(os.path.join(REPO, "specs", "*.json"))):
    if os.path.basename(p).startswith("lf_"):
        continue
    spec = json.load(open(p, encoding="utf-8"))
    links = HC.drop_links(spec)
    if not links:
        continue
    sh = float(spec.get("story_height") or 3.5)
    thick = float(spec.get("floor_thick") or 0.3)
    slots, _n = HC.hole_slots(spec, lambda m: 1)
    boxes = []
    for x in slots:
        if len(x) == 4:
            boxes.append((x[0]["slot_id"], x[2], x[3]))
        else:
            boxes += list(x[2])
    for v in links:
        if HC.cause_for(spec, v) in (None, HC.STAIR):
            continue
        n_holes += 1
        h = HC._rect(v)
        z0, z1 = int(v["story"]) * sh - thick - HC.SKIN, int(v["story"]) * sh + HC.SKIN + 0.05
        cover = 0.0
        for name, c, z in boxes:
            if c[2] + z[2] / 2.0 < z0 or c[2] - z[2] / 2.0 > z1:
                continue
            ox = min(c[0] + z[0] / 2.0, h[2]) - max(c[0] - z[0] / 2.0, h[0])
            oy = min(c[1] + z[1] / 2.0, h[3]) - max(c[1] - z[1] / 2.0, h[1])
            if ox > 1e-6 and oy > 1e-6:
                cover += ox * oy
        if cover > 0.0:
            holes_hit += 1
            print("  %-24s story %d hole %.2f x %.2f m: %.2f m2 of greybox over it" % (
                os.path.basename(p)[:-5], v["story"], h[2] - h[0], h[3] - h[1], cover))
        total += cover
print("[greybox over holes] %d caused holes, %d with greybox over them, %.2f m2 in all" % (n_holes, holes_hit, total))
