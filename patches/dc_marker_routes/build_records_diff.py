"""Which built records moved beyond their build time: every changed file under deli_counter/build/ against HEAD, a
JSON file compared with `built_utc` (and any key ending `_utc`) set aside; a GLB counted apart. Prints what it found.
Copied from `patches/dc_reserved_routes/build_records_diff.py` unchanged."""
import collections
import json
import subprocess
import sys

DC = r"C:\Projects\gabagool_studios\gabagool_factory\deli_counter"


def strip(o):
    if isinstance(o, dict):
        return {k: strip(v) for k, v in o.items() if not k.endswith("_utc")}
    if isinstance(o, list):
        return [strip(v) for v in o]
    return o


names = subprocess.run(["git", "-C", DC, "diff", "--name-only", "--", "build/"], capture_output=True, text=True,
                       check=True).stdout.split()
moved, same, glbs, other = collections.defaultdict(list), 0, [], []
for n in names:
    if n.endswith(".glb"):
        glbs.append(n)
        continue
    if not n.endswith(".json"):
        other.append(n)
        continue
    old = subprocess.run(["git", "-C", DC, "show", "HEAD:" + n], capture_output=True, check=True).stdout
    new = open(DC + "\\" + n.replace("/", "\\"), "rb").read()
    if strip(json.loads(old)) == strip(json.loads(new)):
        same += 1
    else:
        spec = n.split("/")[-1].split(".")[0]
        moved[spec].append(n.split("/")[-1][len(spec) + 1:])
print("changed files under build/:", len(names), "| JSON the same but for build time:", same,
      "| GLBs:", len(glbs), "| other:", other)
print("records that moved:", len(moved), "specs")
for spec in sorted(moved):
    print("  %-34s %s" % (spec, ", ".join(sorted(moved[spec]))))
print("GLBs:", ", ".join(sorted(g.split("/")[-1] for g in glbs)))
