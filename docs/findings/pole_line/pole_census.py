"""Census of the street furniture Lot plans on the stored site fixtures of cold runs
(`lot/tests/fixtures/*.site.json`): steel lamps, utility poles, cans, street lights, trees,
hydrants and pieces, each fixture re-planned by the Lot checkout given (its `cover` dropped
first), so two checkouts on the same specs compare planner against planner. It measures and
prints.

    python docs/findings/pole_line/pole_census.py <lot checkout>
"""
import collections, glob, json, os, sys
root = sys.argv[1]
sys.path.insert(0, root)
import site_furniture, site_streets, lot
for p in sorted(glob.glob(os.path.join(root, "tests", "fixtures", "*.site.json"))):
    spec = json.load(open(p, encoding="utf-8"))
    spec = {k: v for k, v in spec.items() if k != "cover"}
    roads = site_streets.roads(spec)
    pieces = site_furniture.plan_furniture(roads, spec.get("buildings") or [])
    c = collections.Counter(q["species"] for q in pieces)
    trees = sum(v for k, v in c.items() if k in site_furniture.TREES or k == "street_tree")
    cans = sum(1 for q in pieces if q.get("form") == "transformer")
    spec["cover"] = pieces
    lights = [a for a in lot.merge_lights(spec, os.path.join(root, "specs"))["anchors"] if a["type"] == "streetlight"]
    print("%-42s lamps %2d poles %2d cans %d lights %2d trees %2d hydrants %d pieces %d" % (
        os.path.basename(p), c["streetlight"], c["utility_pole"], cans, len(lights), trees, c["fire_hydrant"], len(pieces)))
