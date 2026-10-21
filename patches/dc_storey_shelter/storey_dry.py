"""In memory, with the dc_storey clone's code: (1) is every library spec still a fixed point of furnish; (2) what does
`seed_cover` add to each library spec now (it is additive and idempotent, so a re-run adds only where a room reads bare
or shelterless by the new storey test); (3) after that seeding and a refurnish, the combat audit's COVER/KILLBOX/
NAKED/HOLDOUT findings against the shipped code's audit of the shipped specs. Writes nothing. Run from the clone with
the real deli_counter's path as argv[1]."""
import collections
import glob
import json
import os
import subprocess
import sys

real = sys.argv[1]
sys.path.insert(0, os.getcwd())
import level_design as L  # noqa: E402
import migrate_furnish_recipes as M  # noqa: E402
import combat_audit as CA  # noqa: E402
from spec_loader import spec_from_dict  # noqa: E402

CODES = ("COVER_ALL_LOW", "KILLBOX", "C_NAKED_ROOM", "H_NO_HOLDOUT")


def findings(d, name):
    res = CA.audit(spec_from_dict(d), name=name)
    return sorted("%s %s" % (f[1], f[2].split("'")[1] if "'" in f[2] else "") for f in res["findings"] if f[1] in CODES)


# the shipped audit, run by the REAL repo's code in a subprocess, on the shipped specs
shipped = json.loads(subprocess.run([sys.executable, "-B", "-c", r'''
import glob, json, os, sys
sys.path.insert(0, os.getcwd())
import combat_audit as CA
from spec_loader import spec_from_dict
CODES = ("COVER_ALL_LOW", "KILLBOX", "C_NAKED_ROOM", "H_NO_HOLDOUT")
out = {}
for p in sorted(glob.glob("specs/*.json")):
    n = os.path.basename(p)[:-5]
    if n.startswith("lf_"):
        continue
    d = json.load(open(p, encoding="utf-8"))
    res = CA.audit(spec_from_dict(d), name=n)
    out[n] = sorted("%s %s" % (f[1], f[2].split("'")[1] if "'" in f[2] else "") for f in res["findings"] if f[1] in CODES)
print(json.dumps(out))
'''], cwd=real, capture_output=True, text=True, check=True).stdout)

not_fixed = []
added = collections.Counter()
rooms_added = []
after = {}
for p in sorted(glob.glob(os.path.join(real, "specs", "*.json"))):
    name = os.path.basename(p)[:-5]
    if name.startswith("lf_"):
        continue
    d0 = json.load(open(p, encoding="utf-8"))
    if d0.get("rooms"):
        d1 = json.loads(json.dumps(d0))
        M.migrate(d1)
        if json.dumps(d1, sort_keys=True) != json.dumps(d0, sort_keys=True):
            not_fixed.append(name)
    d = json.loads(json.dumps(d0))
    before = {v["name"] for v in d.get("volumes") or []}
    n = L.seed_cover(d) if d.get("rooms") else 0
    if n:
        new = [v for v in d["volumes"] if v["name"] not in before]
        for v in new:
            kind = "shelter" if v["name"].endswith("_shelter") else "bare-room piece"
            added[kind] += 1
            rooms_added.append("%s: %s (%.2f x %.2f x %.2f)" % (name, v["name"], v["size_x"], v["size_y"], v["size_z"]))
        M.migrate(d)
    after[name] = findings(d, name)

print("specs no longer a fixed point of furnish under the new code (before any seeding):", not_fixed)
print("seed_cover now adds:", dict(added))
for r in rooms_added:
    print("  +", r)
came = collections.Counter(); gone = collections.Counter()
for name in shipped:
    a, b = collections.Counter(shipped[name]), collections.Counter(after.get(name, []))
    for k in b - a:
        came[k.split()[0]] += 1
        print("  audit +", name, k)
    for k in a - b:
        gone[k.split()[0]] += 1
        print("  audit -", name, k)
print("audit findings that appear:", dict(came), " vanish:", dict(gone))
print("shipped totals:", dict(collections.Counter(k.split()[0] for v in shipped.values() for k in v)),
      " after:", dict(collections.Counter(k.split()[0] for v in after.values() for k in v)))
