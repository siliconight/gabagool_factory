"""Every seed_cover piece in the built library: is it stale (today's
`_seed_clear` refuses where it stands), and does it leave a SLOT -- a gap
narrower than a body -- to a wall face, a stair's reserve or another piece?
Measures; names no cause.

    python seeded_slots_census.py [--list]

Plan frame, metres, the spec's own (x, y). A piece is its volume's plan box.
GAP is the clear distance between two plan boxes (0 when they touch or
overlap); a SLOT is 0.05 < gap < min_corridor_width (agent_contract, 1.1 m:
2 x the bake radius + 0.3). Walls are solid along their whole run, openings
included -- doors keep seeded pieces 1.5 m off already (`_seed_clear_doors`),
so this over-reports only beside breach panels and windows, and the listing
names the obstacle so that can be read off.

Exterior walls stand on the footprint edge, `wall_thick` thick, centred; a
partition `wall_thick` thick centred on its `pos`. Stair reserves are
`level_design._stair_reserved_rects` (flights, landings, guard bands), all
storeys, as `_seed_clear` reads them.
"""
import glob
import json
import os
import sys

DC = r"C:\Projects\gabagool_studios\gabagool_factory\deli_counter"
sys.path.insert(0, DC)
import agent_contract   # noqa: E402
import layout_lint      # noqa: E402
import level_design as LD   # noqa: E402

CORRIDOR = agent_contract.min_corridor_width()
TOUCH = 0.05


def gap(a, b):
    dx = max(b[0] - a[2], a[0] - b[2], 0.0)
    dy = max(b[1] - a[3], a[1] - b[3], 0.0)
    return (dx * dx + dy * dy) ** 0.5


def obstacles(spec, story, skip):
    hx, hy = spec["footprint_x"] / 2.0, spec["footprint_y"] / 2.0
    t = float(spec.get("wall_thick", 0.3))
    out = [("ext N", (-hx, hy - t / 2, hx, hy + t / 2)), ("ext S", (-hx, -hy - t / 2, hx, -hy + t / 2)),
           ("ext E", (hx - t / 2, -hy, hx + t / 2, hy)), ("ext W", (-hx - t / 2, -hy, -hx + t / 2, hy))]
    for i, p in enumerate(spec.get("partitions", [])):
        if p.get("story", 0) != story:
            continue
        s, e = sorted((p.get("start", -hy if p["axis"] == "Y" else -hx), p.get("end", hy if p["axis"] == "Y" else hx)))
        if p["axis"] == "Y":
            out.append(("partition %d" % i, (p["pos"] - t / 2, s, p["pos"] + t / 2, e)))
        else:
            out.append(("partition %d" % i, (s, p["pos"] - t / 2, e, p["pos"] + t / 2)))
    for k, r in enumerate(LD._stair_reserved_rects(spec)):
        out.append(("stair reserve %d" % k, tuple(r)))
    for v in spec.get("volumes", []):
        if v is skip or layout_lint.piece_story(spec, v) != story:
            continue
        hx_, hy_ = float(v.get("size_x", 0)) / 2, float(v.get("size_y", 0)) / 2
        out.append(("volume " + str(v.get("name")), (v["x"] - hx_, v["y"] - hy_, v["x"] + hx_, v["y"] + hy_)))
    return out


def main():
    rows = []
    n_specs = n_seeded = 0
    for m in sorted(glob.glob(os.path.join(DC, "build", "*.manifest.json"))):
        name = os.path.basename(m)[:-len(".manifest.json")]
        p = os.path.join(DC, "specs", name + ".json")
        if name.startswith("lf_") or not os.path.exists(p):
            continue
        spec = json.load(open(p, encoding="utf-8"))
        if not spec.get("rooms"):
            continue
        n_specs += 1
        vols = spec.get("volumes") or []
        for v in vols:
            story = layout_lint.piece_story(spec, v)
            if story is None:
                continue
            room = LD._room_for_point(spec, float(v["x"]), float(v["y"]), story)
            if not LD._seeded_cover(v, room):
                continue
            n_seeded += 1
            without = dict(spec)
            without["volumes"] = [o for o in vols if o is not v]
            placed = [(float(o["x"]), float(o["y"])) for o in vols if o is not v and LD._seeded_cover(o, room)]
            half = max(float(v["size_x"]), float(v["size_y"])) / 2.0
            stale = not LD._seed_clear(without, room, float(v["x"]), float(v["y"]), placed, half=half)
            box = (v["x"] - v["size_x"] / 2, v["y"] - v["size_y"] / 2, v["x"] + v["size_x"] / 2, v["y"] + v["size_y"] / 2)
            slots = [(nm, round(gap(box, r), 2)) for nm, r in obstacles(spec, story, v)
                     if TOUCH < gap(box, r) < CORRIDOR]
            rows.append((name, room["id"], v["name"], stale, slots))
    st = [r for r in rows if r[3]]
    sl = [r for r in rows if r[4]]
    both = [r for r in rows if r[3] and r[4]]
    print("corridor %.2f m (agent_contract.min_corridor_width); %d specs, %d seeded pieces"
          % (CORRIDOR, n_specs, n_seeded))
    print("  stale (today's _seed_clear refuses): %d pieces in %d shells" % (len(st), len({r[0] for r in st})))
    print("  leaving a slot < %.2f m: %d pieces in %d shells" % (CORRIDOR, len(sl), len({r[0] for r in sl})))
    print("  both: %d" % len(both))
    kinds = {}
    for r in sl:
        for nm, _g in r[4]:
            k = nm.split(" ")[0] if not nm.startswith("stair") else "stair reserve"
            kinds[k] = kinds.get(k, 0) + 1
    print("  slots by obstacle kind:", kinds)
    if "--list" in sys.argv:
        for r in rows:
            if r[3] or r[4]:
                print("   %-30s %-22s %-34s stale=%-5s %s" % (r[0], r[1], r[2], r[3], r[4][:4]))


if __name__ == "__main__":
    main()
