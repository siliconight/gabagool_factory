"""Isolated mid-floor pieces across specs/*.json.

DEFINITION (stated, cheap, a proxy):
  floor piece  = a volume whose foot is on some storey's floor (+-0.05 m), not hung
                 (`level_design._hung`), size_z >= 0.6, visual (not visual:false),
                 its centre inside a room of that storey (innermost room).
  off-wall     = its axis-aligned footprint (size_x, size_y as recorded) is more than
                 0.6 m from all four edges of its room's bounds. Room bounds stand in
                 for walls: an open-plan edge with no wall counts as a wall here, which
                 UNDER-counts isolated pieces near such an edge.
  isolated     = off-wall AND no other floor piece of the storey within 1.0 m
                 edge-to-edge (box gap, the diagonal at corners). Chairs count as
                 companions, so a table with its chairs is NOT isolated.
Producer by name: seed_cover `<stem>_<room>_<n>` / `_shelter`; furnish
`<stem>_r<crc>_<n>` split by the stem's `where`; anything else 'authored/other'.
Prints counts; draws no conclusion.
"""
import glob, json, os, re, sys, collections
sys.path.insert(0, r"C:\Projects\gabagool_studios\gabagool_factory\deli_counter")
import level_design as ld

SPECS = r"C:\Projects\gabagool_studios\gabagool_factory\deli_counter\specs"
FURN = re.compile(r"^(?P<stem>[a-z_]+?)_r[0-9a-f]{8}_\d+(_\d+)?$")
tot = collections.Counter(); iso = collections.Counter()
by_kind = collections.Counter(); by_kind_iso = collections.Counter()
examples = collections.defaultdict(list)
nspec = 0
for path in sorted(glob.glob(os.path.join(SPECS, "*.json"))):
    try:
        d = json.load(open(path, encoding="utf-8"))
    except Exception:
        continue
    if not isinstance(d, dict) or not d.get("rooms") or not d.get("volumes"):
        continue
    nspec += 1
    sh = float(d.get("story_height") or 3.0)
    building = ld.club_building_id(d)
    roomids = [r["id"] for r in d["rooms"]]
    seedpat = re.compile(r"_(%s)_(\d+)$" % "|".join(map(re.escape, roomids)))
    pieces = []
    for v in d["volumes"]:
        if v.get("visual") is False or float(v.get("size_z", 0)) < 0.6:
            continue
        z, h = float(v.get("z", 0)), float(v.get("size_z", 0))
        k = round((z - h / 2) / sh)
        if abs((z - h / 2) - k * sh) > 0.05:
            continue
        if ld._hung(v, k * sh):
            continue
        cands = [r for r in d["rooms"] if int(r.get("story", 0)) == k and r.get("bounds")
                 and r["bounds"][0] <= v["x"] <= r["bounds"][2]
                 and r["bounds"][1] <= v["y"] <= r["bounds"][3]]
        if not cands:
            continue
        r = min(cands, key=lambda r: (r["bounds"][2]-r["bounds"][0])*(r["bounds"][3]-r["bounds"][1]))
        ax, ay = float(v.get("size_x", 0)) / 2, float(v.get("size_y", 0)) / 2
        box = (v["x"] - ax, v["y"] - ay, v["x"] + ax, v["y"] + ay)
        pieces.append((v, r, k, box))
    for v, r, k, box in pieces:
        name = v.get("name", "")
        if name.startswith("chair_set_") or name.startswith("stair") or name.startswith("guard"):
            continue
        m = FURN.match(name)
        if m and m.group("stem") in ld._PIECES:
            prod = "furnish:" + ld._PIECES[m.group("stem")]["where"]
        elif name.endswith("_shelter"):
            prod = "seed_cover:shelter"
        elif seedpat.search(name):
            prod = "seed_cover:archetype"
        else:
            prod = "authored/other"
        kind = ld._room_kind(r, building)
        b = r["bounds"]
        off = min(box[0] - b[0], box[1] - b[1], b[2] - box[2], b[3] - box[3]) > 0.6
        lone = off and not any(o is not v and kk == k and ld._box_gap(box, ob) < 1.0
                               for o, _r, kk, ob in pieces)
        tot[prod] += 1; by_kind[kind] += 1
        if lone:
            iso[prod] += 1; by_kind_iso[kind] += 1
            if len(examples[prod]) < 6:
                examples[prod].append("%s/%s/%s" % (os.path.basename(path)[:-5], r["id"], name))
print("specs read", nspec)
print("BY PRODUCER: isolated / floor pieces")
for p in sorted(tot, key=lambda p: -iso[p]):
    print("  %-22s %4d / %5d  (%.0f%%)" % (p, iso[p], tot[p], 100.0 * iso[p] / tot[p]))
print("BY ROOM KIND: isolated / floor pieces")
for kd in sorted(by_kind, key=lambda kd: -by_kind_iso[kd]):
    print("  %-14s %4d / %5d" % (kd, by_kind_iso[kd], by_kind[kd]))
for p, ex in examples.items():
    print("e.g.", p, ex)
