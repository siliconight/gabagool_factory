"""Two cold runs' shipped surface dressing, side by side: pieces by the zone
family that owns the ground they stand on (Lot's precedence, read from the
run's own zones), pieces placed on another family's ground, and pieces a
square metre on the parking fields (from the run's own `field_plan`).
Prints what it measured.

    python dressing_compare.py <workspace A> <workspace B> [mission]
"""
import collections
import json
import pathlib
import sys


def family(z):
    for t in z.get("tags") or ():
        if t.startswith("zone_family:"):
            return t.split(":", 1)[1]
    return z["surface_zone_id"]


def read(ws, m):
    j = pathlib.Path(ws) / ".level_factory" / "jobs"
    d = json.loads((j / f"{m}.patina_surface_dressing" / "out" / f"{m}.surface_dressing.json").read_text(encoding="utf-8"))
    g = json.loads((j / f"{m}.themed_site_assemble" / "out" / "site.site.gameplay.json").read_text(encoding="utf-8"))
    return d, [f["rect"] for f in (g.get("field_plan") or {}).get("placed") or []]


def measure(d, fields):
    zl = d["zones"]
    by_id = {z["surface_zone_id"]: z for z in zl}

    def owner(x, y):
        for z in zl:
            a = z["aabb"]
            if a[0] <= x <= a[3] and a[1] <= y <= a[4]:
                return z
        return None
    by_owner, foreign = collections.Counter(), 0
    on_fields = 0
    for o in d["orders"]:
        x, y = o["pos"][0], o["pos"][1]
        ow = owner(x, y)
        fam = family(ow) if ow else "none"
        by_owner[fam] += 1
        if ow is None or fam != family(by_id[o["surface_zone_id"]]):
            foreign += 1
        if any(r[0] <= x <= r[2] and r[1] <= y <= r[3] for r in fields):
            on_fields += 1
    area = sum((r[2] - r[0]) * (r[3] - r[1]) for r in fields)
    walk_zones = sum(1 for z in zl if family(z) == "path")
    return {"orders": len(d["orders"]), "by_owner": dict(sorted(by_owner.items())), "foreign": foreign,
            "on_fields": on_fields, "field_m2": round(area, 1),
            "per_m2_fields": round(on_fields / area, 3) if area else None,
            "walk_zones": walk_zones, "counts": d.get("counts")}


def main():
    m = sys.argv[3] if len(sys.argv) > 3 else "gas_block_001"
    for ws in sys.argv[1:3]:
        d, fields = read(ws, m)
        r = measure(d, fields)
        print(pathlib.Path(ws).name)
        for k, v in r.items():
            print("   %-14s %s" % (k, v))


if __name__ == "__main__":
    main()
