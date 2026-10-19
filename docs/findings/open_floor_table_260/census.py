"""L12 / L24 / L26 and tactical's graph edges for every library spec, against the DC checkout given as argv[1]."""
import glob, json, os, sys
DC = sys.argv[1]
sys.path.insert(0, DC)
os.chdir(DC)
import layout_lint, tactical, spec_loader
out = {}
for path in sorted(glob.glob(os.path.join(DC, "specs", "*.json"))):
    name = os.path.basename(path)[:-5]
    if name.startswith("lf_"):
        continue
    d = json.load(open(path, encoding="utf-8"))
    if not d.get("rooms"):
        continue
    reach = layout_lint._reach_from_ext(d)
    walk = layout_lint._reach_from_ext(d, walk_only=True)
    rooms = [r["id"] for r in d["rooms"]]
    try:
        adj = tactical.build_graph(spec_loader.spec_from_dict(d))
        edges = sorted("%s|%s" % tuple(sorted((a, b))) for a, ns in adj.items() for b in ns if a < b)
    except Exception as e:
        edges = ["ERROR %s" % e]
    out[name] = {"L12": sorted(r for r in rooms if r not in reach), "L24": sorted(r for r in rooms if r not in walk),
                 "L26": sorted("%s|%s" % (f["a"], f["b"]) for f in layout_lint.open_floors(d)), "graph": edges}
json.dump(out, open(sys.argv[2], "w", encoding="utf-8"), indent=1, sort_keys=True)
print(len(out), "specs with rooms;", sum(len(v["L26"]) for v in out.values()), "open floors;",
      sum(len(v["L12"]) for v in out.values()), "L12;", sum(len(v["L24"]) for v in out.values()), "L24")
