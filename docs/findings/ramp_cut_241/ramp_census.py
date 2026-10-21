"""Every library ramp that cuts a slab: the cut 0.240.0 makes, the cut the headroom rule would make, and the
partitions on the storey the cut opens that run within reach of either -- read before any edit.

    python ramp_census.py <deli_counter root>

The rule measured here: the cut ends at the ramp's head and begins where the clearance between the slab's underside
and the ramp's top face falls to the agent contract's min_headroom_m. Prints what it measured and stops.
"""
import glob
import json
import math
import os
import sys

root = sys.argv[1]
sys.path.insert(0, root)
import agent_contract  # noqa: E402
import spec_loader  # noqa: E402
import stairwell  # noqa: E402

HEAD = json.load(open(os.path.join(root, "agent_contract.json"), encoding="utf-8"))["clearances"]["min_headroom_m"]
print("min_headroom_m", HEAD)
for path in sorted(glob.glob(os.path.join(root, "specs", "*.json"))):
    try:
        spec = spec_loader.load_spec(path)
    except Exception as exc:          # a spec the loader refuses is not this census's subject
        continue
    for i, rp in enumerate(getattr(spec, "ramps", ()) or ()):
        if not (rp.cut_slabs and rp.to_story > rp.from_story):
            continue
        H, ft = spec.story_height, spec.floor_thick
        dz, z_low = (rp.to_story - rp.from_story) * H, rp.from_story * H
        ang = math.atan2(dz, rp.run)
        top_off = (rp.thickness / 2.0) / math.cos(ang)
        tc = rp.y if rp.axis == "Y" else rp.x
        t_low, t_head = tc - rp.run / 2.0, tc + rp.run / 2.0
        z_under = rp.to_story * H - ft
        t0 = t_low + (z_under - HEAD - z_low - top_off) * rp.run / dz
        t0 = min(max(t0, t_low), t_head)
        cx, cy, sx, sy = stairwell.ramp_hole(rp)
        old = (cx - sx / 2, cy - sy / 2, cx + sx / 2, cy + sy / 2)
        o_lo, o_hi = (old[1], old[3]) if rp.axis == "Y" else (old[0], old[2])
        head_at_old_start = z_under - (z_low + (max(o_lo, t_low) - t_low) * dz / rp.run + top_off)
        print("\n%s ramp %d: axis %s, run %.1f, width %.1f, storeys %d->%d, H %.1f, slab %.2f, thickness %.2f"
              % (os.path.basename(path), i, rp.axis, rp.run, rp.width, rp.from_story, rp.to_story, H, ft,
                 rp.thickness))
        print("  ramp body along %s: %.2f .. %.2f (head %.2f)" % (rp.axis, t_low, t_head, t_head))
        print("  0.240.0 cut along %s: %.2f .. %.2f -- past the head by %.2f; headroom at its start %.2f m"
              % (rp.axis, o_lo, o_hi, o_hi - t_head, head_at_old_start))
        print("  the rule's cut: %.2f .. %.2f (%.2f m), the slab edge's drop at its start %.2f m"
              % (t0, t_head, t_head - t0, ft + HEAD))
        lat_c = rp.x if rp.axis == "Y" else rp.y
        half = (rp.width + 0.4) / 2.0
        near = []
        for p in getattr(spec, "partitions", ()) or ():
            if p.story != rp.to_story:
                continue
            lo, hi = min(p.start, p.end), max(p.start, p.end)
            # a partition runs along `axis` at `pos`; ask whether it crosses or skirts the cut's window
            if p.axis == rp.axis:          # runs along the ascent: a candidate side
                if abs(p.pos - lat_c) <= half + 1.0 and hi > min(o_lo, t0) - 1 and lo < max(o_hi, t_head) + 1:
                    near.append(("along", p.axis, p.pos, lo, hi))
            else:                          # runs across the ascent
                if min(o_lo, t0) - 1 <= p.pos <= max(o_hi, t_head) + 4 and hi > lat_c - half and lo < lat_c + half:
                    near.append(("across", p.axis, p.pos, lo, hi))
        print("  partitions on storey %d near either cut: %s" % (rp.to_story, near or "none"))
