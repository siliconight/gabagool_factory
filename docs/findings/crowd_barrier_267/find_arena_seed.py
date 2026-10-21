"""Which seeds of a brief draw a given building? Level Factory's own `lot_for_brief`, themed as the art leg draws.

    python docs/findings/crowd_barrier_267/find_arena_seed.py <brief.json> <building id> <seed lo> <seed hi>

Prints each seed whose candidate lot holds the building, and how many did. Draws nothing, builds nothing.
"""
import json
import pathlib
import sys
import types

F = pathlib.Path(r"C:\Projects\gabagool_studios\gabagool_factory")
sys.path.insert(0, str(F / "level_factory"))
from packages.pipeline.building_library import lot_for_brief  # noqa: E402

brief = json.loads(pathlib.Path(sys.argv[1]).read_text(encoding="utf-8"))
want, lo, hi = sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
model = types.SimpleNamespace(**brief)
hits = 0
for seed in range(lo, hi):
    cid = "%s.candidate.seed_%d" % (brief["mission_id"], seed)
    lot, _inc = lot_for_brief(model, cid, themed=True)
    ids = [e.get("id") for e in lot]
    if want in ids:
        hits += 1
        print(seed, ids)
print("%d of %d seeds draw %s" % (hits, hi - lo, want))
