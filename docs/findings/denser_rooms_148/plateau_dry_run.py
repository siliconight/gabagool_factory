"""REFUTED, KEPT: "more pieces" as the answer to roadmap 148's "Too sparse". Refurnish every library spec in memory
under the shipped `_furnish_target` and under a candidate without its 160 to 400 m2 plateau (one piece per
`_FURNISH_PER_AREA` to `_FURNISH_HALL_MAX`), and print per room kind the pieces furnish wrote, the median floor share
under standing volumes and the rooms short of their target. Writes nothing. Run from a Deli Counter checkout's own
directory; `plateau_dry_run_0245.out.txt` is 0.245.0's.

What it showed: 7,777 -> 12,665 pieces across the library (+63 %) and deli_a03's market aisles 5.7 -> 6.8 % of the
floor covered, because what a higher count adds is cartons and cabinets. Not built; the rows were.
"""
import collections, copy, glob, json, os, sys, statistics
sys.path.insert(0, os.getcwd())
import level_design as LD
import migrate_furnish_recipes as M

SHIPPED = LD._furnish_target


def candidate(area, per_area=None):
    if per_area:
        return min(max(1, int(round(area / per_area))), LD._FURNISH_HALL_MAX)
    return min(max(1, int(round(area / LD._FURNISH_PER_AREA))), LD._FURNISH_HALL_MAX)


def room_stats(spec, room):
    x0, y0, x1, y1 = room["bounds"]
    sh = LD._story_height(spec)
    st = room.get("story", 0)
    area = (x1 - x0) * (y1 - y0)
    foot = 0.0
    n = 0
    tag = LD._room_tag(room)
    for v in spec["volumes"]:
        if not (x0 <= v.get("x", 1e9) <= x1 and y0 <= v.get("y", 1e9) <= y1):
            continue
        z, h = v.get("z", 0), v.get("size_z", 0)
        if not (st * sh - 0.5 <= z - h / 2 < (st + 1) * sh - 0.5):
            continue
        if v.get("collision") == "none" or v.get("visual") is False:
            continue
        foot += v["size_x"] * v["size_y"]
        if ("_%s_" % tag) in v.get("name", ""):
            n += 1
    return area, foot / area, n


def run(rule):
    LD._furnish_target = rule
    out = []
    for path in sorted(glob.glob("specs/*.json")):
        name = os.path.basename(path)[:-5]
        if name.startswith("lf_"):
            continue
        d = json.load(open(path, encoding="utf-8"))
        if not d.get("rooms"):
            continue
        M.migrate(d)
        b = LD.club_building_id(d)
        for room in d["rooms"]:
            x0, y0, x1, y1 = room["bounds"]
            if (x1 - x0) * (y1 - y0) < LD._FURNISH_MIN_AREA:
                continue
            kind = LD._room_kind(room, b)
            area, share, n = room_stats(d, room)
            recipe = LD._RECIPES[kind]
            tgt = rule(area, recipe.get("per_area"))
            have = LD._room_volume_count(d, room)
            out.append((name, room["id"], kind, area, share, n, tgt, have))
    LD._furnish_target = SHIPPED
    return out


a = run(SHIPPED)
b = run(candidate)
by = collections.defaultdict(lambda: [[], []])
for ra, rb in zip(a, b):
    assert ra[:4] == rb[:4]
    by[ra[2]][0].append(ra)
    by[ra[2]][1].append(rb)
print("%-13s %5s %8s | %7s %7s | %7s %7s | %6s %6s" % ("kind", "rooms", "area_med", "pcs_a", "pcs_b", "share_a", "share_b", "shortA", "shortB"))
tot = [0, 0]
for k in sorted(by, key=lambda k: -len(by[k][0])):
    A, B = by[k]
    pa = sum(r[5] for r in A); pb = sum(r[5] for r in B)
    tot[0] += pa; tot[1] += pb
    sa = statistics.median(r[4] for r in A); sb = statistics.median(r[4] for r in B)
    shA = sum(1 for r in A if r[7] < r[6]); shB = sum(1 for r in B if r[7] < r[6])
    print("%-13s %5d %8.0f | %7d %7d | %6.1f%% %6.1f%% | %6d %6d" % (k, len(A), statistics.median(r[3] for r in A), pa, pb, 100 * sa, 100 * sb, shA, shB))
print("furnished volumes", tot)
for name, rid in (("deli_a03", "market_aisles"), ("deli_a03", "kitchen"), ("deli_a03", "stockroom_loading"), ("office", "ground_bullpen"), ("office", "lobby"), ("pharmacy_a01", "retail_floor"), ("pharmacy_a01", "rx_counter"), ("pharmacy_a01", "rx_vault")):
    for ra, rb in zip(a, b):
        if ra[0] == name and ra[1] == rid:
            print("  %s/%s %.0f m2: pieces %d -> %d, share %.1f%% -> %.1f%%, target %d -> %d, holds %d -> %d" % (name, rid, ra[3], ra[5], rb[5], 100 * ra[4], 100 * rb[4], ra[6], rb[6], ra[7], rb[7]))
