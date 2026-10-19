"""Simulate a call before making it: the store's video poker cabinet may stand against the PARTITION it backs onto.

`_seed_clear` keeps every piece's centre 1.0 m off every partition's line, which refuses every slot a held
partition wall offers (a cabinet backed against one stands its centre about half a metre off it) -- `why_rule.py`
beside this attributes 25 to 48 of each short store's candidates to that rule. The door rule
(`_seed_clear_doors`, 1.5 m plus the piece's half from every partition opening) is separate and stays.

This writes a scratch copy of the working tree's `level_design.py` with one dial, `backs_on_partitions`, on for
`video_poker_store` alone: such a piece placed by `_place_fixture` against a wall skips the partition-line rule for
the one partition whose centreline IS the room edge it backs onto; every other partition, the door rule and every
other rule still apply. It then strips and refurnishes copies of every library spec with the scratch copy
(`migrate_furnish_recipes.migrate`, in memory) and compares each building with the library as it stands. Writes
nothing in the repo. A probe: prints and stops (roadmap 196).

    python partition_sim.py <deli_counter dir> <scratch dir>
"""
import collections
import glob
import json
import os
import re
import shutil
import sys

dc = os.path.abspath(sys.argv[1])
scratch = os.path.abspath(sys.argv[2])
os.makedirs(scratch, exist_ok=True)
src = open(os.path.join(dc, "level_design.py"), encoding="utf-8").read()

EDITS = [
    # the dial on the piece
    ('''           displaces=None, most_building=None):
    return {"name": name, "sizes": tuple(sizes), "where": where,
''', '''           displaces=None, most_building=None, backs_on_partitions=False):
    return {"name": name, "sizes": tuple(sizes), "where": where,
            "backs_on_partitions": backs_on_partitions,
'''),
    ('''           displaces=("cabinet_file", "vending"), most_building=2),
''', '''           displaces=("cabinet_file", "vending"), most_building=2,
           backs_on_partitions=True),
'''),
    # _seed_clear learns which partition the piece backs onto
    ('''def _seed_clear(spec, room, px, py, placed, half=0.0, above=None,
                below=None, over_openings=False, corridor=False):
''', '''def _seed_clear(spec, room, px, py, placed, half=0.0, above=None,
                below=None, over_openings=False, corridor=False, backed_on=None):
'''),
    ('''        if p.get("story", 0) != story:
            continue
        if p["axis"] == "Y":
            cy = max(p["start"], min(py, p["end"]))
''', '''        if p.get("story", 0) != story:
            continue
        if backed_on is not None and p["axis"] == backed_on[0] \\
                and abs(float(p["pos"]) - backed_on[1]) < 0.05:
            continue
        if p["axis"] == "Y":
            cy = max(p["start"], min(py, p["end"]))
'''),
    # _place_fixture passes it for a piece with the dial, from the slot's bearing
    ('''        if not _seed_clear(spec, room, qx, qy, [], half=half, above=above,
                           below=below,
                           over_openings=hangs_over_openings(spec, story,
                                                             above)):
            continue
''', '''        backed_on = None
        if p.get("backs_on_partitions") and front is not None:
            bx0, by0, bx1, by1 = room["bounds"]
            backed_on = {0.0: ("X", by0), 180.0: ("X", by1),
                         90.0: ("Y", bx0), 270.0: ("Y", bx1)}.get(float(front))
        if not _seed_clear(spec, room, qx, qy, [], half=half, above=above,
                           below=below,
                           over_openings=hangs_over_openings(spec, story,
                                                             above),
                           backed_on=backed_on):
            continue
'''),
]
for old, new in EDITS:
    if src.count(old) != 1:
        raise SystemExit("UNKNOWN SHAPE: an anchor is not in level_design.py once: %r" % old[:70])
    src = src.replace(old, new)
open(os.path.join(scratch, "level_design.py"), "w", encoding="utf-8", newline="\n").write(src)
shutil.copy(os.path.join(dc, "migrate_furnish_recipes.py"), scratch)

sys.path.insert(0, dc)
sys.path.insert(0, scratch)
os.chdir(dc)
import level_design as L  # noqa: E402  -- the scratch copy
import migrate_furnish_recipes as M  # noqa: E402
assert os.path.dirname(os.path.abspath(L.__file__)) == scratch, L.__file__

KEY = "video_poker_store"
stem = re.compile(r"_r[0-9a-f]{8}_\d+(_\d+)?$")


def census(spec):
    return collections.Counter(stem.sub("", str(v.get("name", ""))) for v in spec.get("volumes") or [])


moved = 0
held = collections.Counter()
rows = []
for path in sorted(glob.glob("specs/*.json")):
    name = os.path.basename(path)[:-5]
    if name.startswith("lf_"):
        continue
    now = json.load(open(path, encoding="utf-8"))
    if not now.get("rooms"):
        continue
    sim = json.loads(json.dumps(now))
    M.migrate(sim)
    if json.dumps(sim, sort_keys=True) == json.dumps(now, sort_keys=True):
        continue
    moved += 1
    a, b = census(now), census(sim)
    d = {k: b[k] - a[k] for k in set(a) | set(b) if a[k] != b[k]}
    rows.append((name, a[KEY], b[KEY], d))
print("specs the dial changes: %d" % moved)
for name, a, b, d in rows:
    print("  %-28s cabinets %d -> %d   %s" % (name, a, b, ", ".join("%+d %s" % (n, k) for k, n in sorted(d.items(), key=lambda kv: kv[1])) or "(moved, same counts)"))
