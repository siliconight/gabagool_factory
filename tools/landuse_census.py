"""Land-use census over every assembled site on disk (`lot/site_landuse.py`):
what share of each plate is building, road, sidewalk, frontage, walk,
courtyard, service pad, parking field, or REMAINDER (ground with no role), the largest piece of
remainder, building separation, and per road the building line's spread,
frontage occupancy and whether fronting buildings have a door facing it.

    python tools/landuse_census.py                    every lot on disk, distinct lots once
    python tools/landuse_census.py <ws> <mission> <seed>   one lot, in full (JSON)

Reads a site spec and its merged gameplay, resolves the walks on a COPY
(`site_paths.snap_to_doors`, as `assemble` does), measures, writes nothing.
Prints what it measured.
"""
import copy
import glob
import json
import pathlib
import statistics
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "lot"))
import site_landuse  # noqa: E402
import site_paths  # noqa: E402


def pair(ws, mission, seed):
    spec = ws / ".level_factory" / "temp" / mission / f"candidate_seed_{seed}" / "site.json"
    gp = ws / ".level_factory" / "jobs" / f"{mission}.lot_assemble.candidate.seed_{seed}" / "out" / "site.site.gameplay.json"
    return spec, gp


def measure(spec_p, gp_p):
    spec = json.loads(spec_p.read_text(encoding="utf-8"))
    merged = json.loads(gp_p.read_text(encoding="utf-8"))
    s = copy.deepcopy(spec)
    # the spec on disk is the authored one; resolve its walks as assemble does
    s["paths"] = [p for p in s.get("paths", []) if not p.get("landing_of") and "leg_of" not in p]
    for p in s["paths"]:
        if "from" in p:
            for k in ("a", "b", "snapped", "route_width", "drawn"):
                p.pop(k, None)
    for b in s.get("buildings", []):
        mb = next((m for m in merged.get("buildings", []) if m.get("id") == b["id"]), None)
        if mb and mb.get("footprint") and not b.get("footprint") and not b.get("_footprint"):
            b["_footprint"] = mb["footprint"]
    site_paths.snap_to_doors(s, merged)
    # what assemble planned onto the ground and recorded in the gameplay
    # (Lot 0.93.0): the service pads; absent on an older build, so none
    s["yards"] = list(s.get("yards") or []) + list((merged.get("yard_plan") or {}).get("placed") or [])
    # ...and the parking fields and their driveways (Lot 0.94.0)
    s["fields"] = list((merged.get("field_plan") or {}).get("placed") or [])
    s["driveways"] = [f["driveway"] for f in s["fields"]]
    return site_landuse.census(s, merged)


def main():
    if len(sys.argv) == 4:
        spec_p, gp_p = pair(pathlib.Path(sys.argv[1]), sys.argv[2], sys.argv[3])
        print(json.dumps(measure(spec_p, gp_p), indent=1))
        return
    seen, rows = set(), []
    for gp in sorted(glob.glob(str(ROOT / "workspaces" / "*" / ".level_factory" / "jobs" / "*.lot_assemble.candidate.seed_*" / "out" / "site.site.gameplay.json"))):
        gp_p = pathlib.Path(gp)
        mission, seed = gp_p.parents[1].name.split(".lot_assemble.candidate.seed_")
        ws = gp_p.parents[4]
        spec_p, _ = pair(ws, mission, seed)
        if not spec_p.exists():
            continue
        spec = json.loads(spec_p.read_text(encoding="utf-8"))
        key = (mission, seed, tuple((b["id"], str(b.get("glb")), b.get("rot", 0), tuple(b["at"])) for b in spec.get("buildings", [])))
        if key in seen:
            continue
        seen.add(key)
        try:
            c = measure(spec_p, gp_p)
        except Exception as e:  # said, not skipped
            print("CANNOT MEASURE %s %s %s: %r" % (ws.name, mission, seed, e))
            continue
        if not c.get("ok"):
            print("NO PLATE %s %s %s" % (ws.name, mission, seed))
            continue
        rows.append((ws.name, mission, seed, c))
    print("%-34s %5s %6s %6s %6s %6s %6s %6s %7s %7s %6s %s" % ("lot", "bldg", "road", "walk*", "front", "path", "remain", "blob", "gapmin", "line+-", "occ", "door->street"))
    for ws, mission, seed, c in rows:
        sh = c["shares"]
        walk = sh["sidewalk"] + sh["kerbcut"]
        gaps = [g for g in c["nearest_building_gap"].values() if g is not None]
        spreads = [r["setback_spread"] for r in c["roads"] if len(r["fronting"]) > 1]
        occs = [v for r in c["roads"] for v in r["frontage_occupancy"].values() if v]
        fr = [f for r in c["roads"] for f in r["fronting"]]
        faced = sum(1 for f in fr if f["door_faces_road"])
        print("%-34s %5.2f %6.2f %6.2f %6.2f %6.2f %6.2f %6.0f %7.1f %7.1f %6.2f %d/%d" % (
            f"{mission} s{seed}"[:34], sh["building"], sh["road"], walk, sh["frontage"], sh["path"], sh["remainder"],
            c["remainder_largest_blob"], min(gaps) if gaps else -1, max(spreads) if spreads else 0.0,
            max(occs) if occs else 0.0, faced, len(fr)))
    if rows:
        rem = [c["shares"]["remainder"] for _w, _m, _s, c in rows]
        cov = [c["shares"]["building"] for _w, _m, _s, c in rows]
        fr = [f for _w, _m, _s, c in rows for r in c["roads"] for f in r["fronting"]]
        print()
        print("distinct lots %d; remainder share median %.2f (min %.2f max %.2f); coverage median %.2f" % (
            len(rows), statistics.median(rem), min(rem), max(rem), statistics.median(cov)))
        print("building-road frontings %d; a ground door facing the road on %d" % (
            len(fr), sum(1 for f in fr if f["door_faces_road"])))
        unknown = sorted({u for _w, _m, _s, c in rows for u in c["unknown_families"]})
        if unknown:
            print("UNKNOWN surface families (not counted as a use; counted as remainder):", unknown)


if __name__ == "__main__":
    main()
