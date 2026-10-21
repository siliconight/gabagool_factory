"""Does a changed floorplan.py draw every plan of the library as the shipped one does? (argv: the Deli Counter checkout
whose specs and other modules are read, the directory holding the changed floorplan.py, an output .txt.) Each module
is loaded under its own name from its own file; every spec's every storey is rendered by both and compared as
strings. Prints and writes the counts and the first differences. Read-only on both checkouts."""
import glob
import importlib.util
import os
import sys

dc, new_dir, out_path = sys.argv[1], sys.argv[2], sys.argv[3]
sys.path.insert(0, dc)
import spec_loader  # noqa: E402


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


old = load("floorplan_shipped", os.path.join(dc, "floorplan.py"))
new = load("floorplan_changed", os.path.join(new_dir, "floorplan.py"))
specs = plans = same = 0
diffs = []
for p in sorted(glob.glob(os.path.join(dc, "specs", "*.json"))):
    name = os.path.basename(p)[:-5]
    if name.startswith("lf_"):
        continue
    s = spec_loader.load_spec(p)
    specs += 1
    for story in old.stories_in(s):
        a, b = old.render_story(s, story), new.render_story(s, story)
        plans += 1
        if a == b:
            same += 1
        else:
            al, bl = a.splitlines(), b.splitlines()
            first = next((i for i, (x, y) in enumerate(zip(al, bl)) if x != y), min(len(al), len(bl)))
            diffs.append((name, story, len(al), len(bl), first,
                          al[first][:110] if first < len(al) else "", bl[first][:110] if first < len(bl) else ""))
lines = ["== every library plan, the shipped floorplan.py against %s" % new_dir,
         "specs %d, plans %d, identical %d, different %d" % (specs, plans, same, plans - same)]
for d in diffs[:12]:
    lines.append("  %s storey %s: %d lines -> %d, first difference at line %d" % d[:5])
    lines.append("    - " + d[5])
    lines.append("    + " + d[6])
txt = "\n".join(lines) + "\n"
open(out_path, "w", encoding="utf-8", newline="\n").write(txt)
print(txt)
