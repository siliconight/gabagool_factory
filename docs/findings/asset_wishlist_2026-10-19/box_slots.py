"""Which of Deli Counter's prop slots Zoo builds only as a plain box -- no species named -- by name, over built manifests.

A probe: prints what it measured and stops. A prop slot whose `species` is empty is built by Zoo as the plain box at
the slot's size (`prop_species.PROP_SPECIES` maps a piece's name to a species, or to None on purpose for columns,
crates, carts, planters, kiosks and the like); a slot naming a species Zoo has no genome for is counted apart. Names
are the slot ids with their trailing indices and compass suffixes taken off.

    python docs/findings/asset_wishlist_2026-10-19/box_slots.py [<folder of *.slots.json>] [--with-lf]

The folder defaults to deli_counter/build/ (the tracked library's builds); `lf_*` manifests are left out unless
--with-lf. A level's own buildings (`lf_*`) are built by Level Factory in its workspace, not there.
"""
import collections
import glob
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
FACTORY = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
args = [a for a in sys.argv[1:] if not a.startswith("--")]
folder = args[0] if args else os.path.join(FACTORY, "deli_counter", "build")
with_lf = "--with-lf" in sys.argv
zoo = {os.path.basename(p)[:-5] for p in glob.glob(os.path.join(FACTORY, "zoo", "zoo_keeper", "genome", "species",
                                                                   "*.json"))}
boxes, unknown, where = collections.Counter(), collections.Counter(), collections.defaultdict(set)
props = files = 0
for p in sorted(glob.glob(os.path.join(folder, "*.slots.json"))):
    name = os.path.basename(p)[:-len(".slots.json")]
    if name.startswith("lf_") and not with_lf:
        continue
    files += 1
    d = json.load(open(p, encoding="utf-8"))
    for s in d.get("slots", []):
        if s.get("role") != "prop":
            continue
        props += 1
        base = re.sub(r"(_\d+)+$", "", s.get("slot_id", ""))
        base = re.sub(r"_[nsew]$|_\d+_\d+$", "", base)
        sp = s.get("species")
        if not sp:
            boxes[base] += 1
            where[base].add(name)
        elif sp not in zoo:
            unknown[sp] += 1
print("%d manifests, %d prop slots; plain boxes %d (%.1f %%) in %d names; species with no genome %d" % (
    files, props, sum(boxes.values()), 100.0 * sum(boxes.values()) / max(1, props), len(boxes),
    sum(unknown.values())))
for k, v in boxes.most_common():
    print("  %5d  %-36s %3d specs" % (v, k, len(where[k])))
for k, v in unknown.most_common():
    print("  no genome: %s x%d" % (k, v))
