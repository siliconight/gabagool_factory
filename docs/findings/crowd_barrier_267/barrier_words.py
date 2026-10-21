"""What would the word `barrier` claim in Deli Counter's library? Every authored volume and every built slot whose name
holds it, with its size long side first (as `prop_species.long_axis_first` turns a hinted volume) and the species the
name routes to today.

    python docs/findings/crowd_barrier_267/barrier_words.py [word]

Reads `deli_counter/specs/*.json` (the library's own specs; `lf_*` are Level Factory's per-candidate writes and are
skipped, as Deli Counter's one-word test skips them) and `deli_counter/build/*.slots.json`. Prints what it counted and
stops.
"""
import glob
import json
import os
import pathlib
import sys

F = pathlib.Path(__file__).resolve().parents[3]
DC = F / "deli_counter"
sys.path.insert(0, str(DC))
import prop_species  # noqa: E402

word = (sys.argv[1] if len(sys.argv) > 1 else "barrier").lower()
print("authored volumes naming %r:" % word)
n = 0
for path in sorted(glob.glob(str(DC / "specs" / "*.json"))):
    if os.path.basename(path).startswith("lf_"):
        continue
    spec = json.load(open(path, encoding="utf-8"))
    for v in spec.get("volumes") or []:
        name = (v.get("name") or "")
        if word in name.lower():
            n += 1
            dims = sorted((float(v["size_x"]), float(v["size_y"])), reverse=True) + [float(v["size_z"])]
            print("   %-24s %-20s %s routes to %r" % (os.path.basename(path)[:-5], name, dims,
                                                    prop_species.species_for_name(name)))
print("   %d" % n)
print("built slots naming %r:" % word)
n = 0
for path in sorted(glob.glob(str(DC / "build" / "*.slots.json"))):
    d = json.load(open(path, encoding="utf-8"))
    for s in d.get("slots") or []:
        sid = str(s.get("slot_id", ""))
        if word in sid.lower():
            n += 1
            print("   %-24s %-20s role %s species %r dims %s rot_y %s" % (
                d.get("building_id"), sid, s.get("role"), s.get("species"), (s.get("fit") or {}).get("dims"),
                (s.get("transform") or {}).get("rot_y")))
print("   %d" % n)
