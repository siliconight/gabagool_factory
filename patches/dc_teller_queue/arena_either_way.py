"""Whether arena_a02's queue depends on the order the migration fits it in: 0.243.0 fitted it round the spec's
furniture and refurnished after; 0.244.0's `migrate_ticket_queue.migrate` sets the furnished pieces aside, fits, and
refurnishes. Both run from 0.242.0's arena_a02 (the factory's docs/findings/ticket_queue_267/arena_a02_0242.json) with
its barricades and `metal_bare` taken off, as 0.243.0 did, and the whole spec compared with the library's
arena_a02.json, key by key.

    python patches/dc_teller_queue/arena_either_way.py <deli_counter dir>

Prints what it compared and stops.
"""
import copy
import json
import os
import sys

dc = os.path.abspath(sys.argv[1])
sys.path.insert(0, dc)
os.chdir(dc)
import migrate_ticket_queue  # noqa: E402

F = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
src = json.load(open(os.path.join(F, "docs", "findings", "ticket_queue_267", "arena_a02_0242.json"), encoding="utf-8"))
src["volumes"] = [v for v in src["volumes"] if not v["name"].startswith("barrier_")]
src["materials"] = [m for m in src["materials"] if m["id"] != "metal_bare"]
d = copy.deepcopy(src)
report = migrate_ticket_queue.migrate(d)
print("0.244.0's migration on 0.242.0's arena_a02, barricades off:", [(r["room"], r["queued"], r["why"]) for r in report])
lib = json.load(open(os.path.join(dc, "specs", "arena_a02.json"), encoding="utf-8"))
keys = sorted(set(d) | set(lib))
moved = [k for k in keys if d.get(k) != lib.get(k)]
print("keys that differ from the library's arena_a02.json: %s" % (moved or "none"))
for k in moved:
    if isinstance(d.get(k), list) and isinstance(lib.get(k), list):
        a = {json.dumps(x, sort_keys=True) for x in d[k]}
        b = {json.dumps(x, sort_keys=True) for x in lib[k]}
        print("   %s: %d entries here, %d in the library; %d only here, %d only there; same set: %s" % (
            k, len(d[k]), len(lib[k]), len(a - b), len(b - a), a == b))
print("the same spec, byte for byte as the migration writes it:",
      json.dumps(d, indent=1) + "\n" == open(os.path.join(dc, "specs", "arena_a02.json"), encoding="utf-8").read())
