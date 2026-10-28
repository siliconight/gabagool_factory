"""Bank Block on Level Factory 0.266.0 / Lot 0.136.0 / Dispatch 0.7.0, events off and on, against 0.265.1's.

Prints what it measured: anchor counts, which carry events, the extraction zone's block, whether ids and records
match the earlier build, and the van's distance from the zone's centre (plan metres).
"""
import glob
import json
import math

PKG = "workspaces/%s/.level_factory/exports/LF_bank_block_001.portable-godot/gameplay_anchors.json"


def anchors(ws):
    d = json.load(open(PKG % ws, encoding="utf-8"))
    return {a["shell_id"]: a for a in d["anchors"]}


old_off, old_on = anchors("events-off-02651-ws"), anchors("events-on-02651-ws")
off, on = anchors("zone-off-02660-ws"), anchors("zone-on-02660-ws")
print("anchors  0.265.1 off/on:", len(old_off), len(old_on), "  0.266.0 off/on:", len(off), len(on))
print("off ids == 0.265.1 off ids:", set(off) == set(old_off), " on ids == 0.265.1 on ids:", set(on) == set(old_on))
diff_off = sorted(k for k in off if k in old_off and off[k] != old_off[k])
print("off records differing from 0.265.1 off:", diff_off)
diff_on = sorted(k for k in on if k in old_on and on[k] != old_on[k])
print("on records differing from 0.265.1 on:", diff_on)
for k in diff_on:
    a, b = old_on[k], on[k]
    print("  ", k, {f: (a.get(f), b.get(f)) for f in set(a) | set(b) if a.get(f) != b.get(f)})
events = {k: a["event"]["event"] for k, a in on.items() if a.get("event")}
print("events on:", sorted(events.values()))
zones = [a for a in on.values() if a.get("event", {}).get("event", "").startswith("zone.")]
for z in zones:
    print("zone:", z["shell_id"], z["anchor_type"], json.dumps(z["event"]), "tags", z.get("tags"))

gp = glob.glob("workspaces/zone-on-02660-ws/.level_factory/**/*.site.gameplay.json", recursive=True)
print("lot gameplay files:", len(gp))
for g in gp[:1]:
    d = json.load(open(g, encoding="utf-8"))
    placed = (d.get("getaway_plan") or {}).get("placed")
    ext = [m for m in d.get("site_markers", []) if m.get("type") == "extraction"]
    print("site extraction markers:", ext)
    if placed:
        sx, _h, sy = placed["van"]["size"]
        x, y = placed["van"]["at"]
        for m in ext:
            px, py = m["at"]
            gap = math.hypot(max(x - sx / 2 - px, 0, px - x - sx / 2), max(y - sy / 2 - py, 0, py - y - sy / 2))
            print("  van slot edge from the zone centre: %.3f m  (zone_radius %s)" % (gap, m.get("zone_radius")))
