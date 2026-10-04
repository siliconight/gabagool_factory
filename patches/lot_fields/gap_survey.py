"""What room a parking field would have: per candidate, along each road with
a sidewalk, the gaps between the buildings that front it (and from the
plate's end to the first and last), with each gap's width along the road and
the depth clear behind the back of walk. Reads the specs and gameplay a
build wrote; changes nothing. Plan metres.

    python gap_survey.py <workspace> <mission> [<workspace> <mission> ...]
"""
import copy
import glob
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "lot"))
sys.path.insert(0, str(ROOT / "tools"))
import landuse_census  # noqa: E402
import site_extent  # noqa: E402
import site_landuse  # noqa: E402
import site_streets  # noqa: E402


def survey(ws, mission):
    for j in sorted(glob.glob(str(ws / ".level_factory" / "jobs" / f"{mission}.lot_assemble.candidate.seed_*"))):
        seed = j.rsplit("seed_", 1)[1]
        spec_p, gp_p = landuse_census.pair(ws, mission, seed)
        spec = json.loads(spec_p.read_text(encoding="utf-8"))
        merged = json.loads(gp_p.read_text(encoding="utf-8"))
        s = copy.deepcopy(spec)
        for b in s.get("buildings", []):
            mb = next((m for m in merged.get("buildings", []) if m.get("id") == b["id"]), None)
            if mb and mb.get("footprint") and not b.get("_footprint"):
                b["_footprint"] = mb["footprint"]
        c = site_landuse.census(s, merged)
        ext = site_extent.resolve(s).rect
        rl = site_streets.roads(s)
        print(f"{mission} seed {seed}: plate x {ext[0]:.1f}..{ext[2]:.1f} y {ext[1]:.1f}..{ext[3]:.1f}")
        for road, r in zip(rl, c["roads"]):
            if not road.sidewalk:
                continue
            for side in (1, -1):
                fr = sorted((f for f in r["fronting"] if f["side"] == side), key=lambda f: f["along"][0])
                if not fr:
                    continue
                spans = [tuple(f["along"]) for f in fr]
                # other roads' bands, along this road
                bands = []
                for o in rl:
                    if o is road:
                        continue
                    for end in (o.a, o.b):
                        pass
                    half = o.width / 2.0 + o.sidewalk
                    ts = [((x - road.a[0]) * road.along[0] + (y - road.a[1]) * road.along[1])
                          for x, y in (o.point(0, half), o.point(0, -half), o.point(o.length, half), o.point(o.length, -half))]
                    bands.append((min(ts), max(ts)))
                lo = max(road.slab[0], 0.0)
                hi = min(road.slab[1], road.length)
                edges = [lo] + [v for sp in spans for v in sp] + [hi]
                gaps = []
                prev = lo
                for a0, a1 in spans:
                    gaps.append((prev, a0))
                    prev = max(prev, a1)
                gaps.append((prev, hi))
                desc = []
                for g0, g1 in gaps:
                    cut = [b for b in bands if not (b[1] <= g0 or b[0] >= g1)]
                    desc.append(f"[{g0:6.1f},{g1:6.1f}] {g1 - g0:5.1f} m" + (f" (a road in it {[(round(b[0],1), round(b[1],1)) for b in cut]})" if cut else ""))
                print(f"  road {road.index} side {'+' if side > 0 else '-'}: buildings {[(f['building'], f['along']) for f in fr]}")
                for d in desc:
                    print("     gap " + d)


if __name__ == "__main__":
    a = sys.argv[1:]
    for i in range(0, len(a), 2):
        survey(pathlib.Path(a[i]), a[i + 1])
