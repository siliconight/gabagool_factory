"""How Lot's `tests/fixtures/club_block_014_seed_9181.site.json` was made:
cold run 9204's club_block_014 seed_9181, the candidate's input `site.json`
with its cover as the job drew it -- the getaway van among it, the very
record `site_getaway` placed. The tests cut the cover back to the van, which
is what stood when `site_responders.plan` ran; the rest is there for the
read-back control. Also prints the crew's points from the job's
`site_walk.tscn` (Godot x, y up, z turned to site x, y).

    python make_fixture_9204.py <out.json>

Needs `workspaces/cold-9204-ws` at the factory root. Prints what it wrote.
"""
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
WS = ROOT / "workspaces" / "cold-9204-ws" / ".level_factory"
SPEC = WS / "temp" / "club_block_014" / "candidate_seed_9181" / "site.json"
JOB = WS / "jobs" / "club_block_014.lot_assemble.candidate.seed_9181" / "1" / "out"

spec = json.loads(SPEC.read_text(encoding="utf-8"))
drawn = json.loads((JOB / "site.site.drawn.json").read_text(encoding="utf-8"))
placed = json.loads((JOB / "site.site.gameplay.json").read_text(encoding="utf-8"))["getaway_plan"]["placed"]["van"]
vans = [cv for cv in drawn["cover"] if cv.get("source") == "getaway_van"]
assert len(vans) == 1 and vans[0] == placed, "the drawn van is not the placed van"
assert not spec.get("cover"), "the input site already carries cover"
spec["cover"] = drawn["cover"]
out = pathlib.Path(sys.argv[1])
out.write_text(json.dumps(spec, indent=1, sort_keys=True) + "\n", encoding="utf-8")
print("wrote %s: %d bytes, %d cover pieces" % (out, out.stat().st_size, len(spec["cover"])))
walk = (JOB / "site_walk.tscn").read_text(encoding="utf-8")
for name in ("spawn_pos", "objective_pos", "extraction_pos"):
    m = re.search(r"^%s = Vector3\(([^,]+), ([^,]+), ([^)]+)\)$" % name, walk, flags=re.M)
    gx, gy, gz = (float(v) for v in m.groups())
    print("%s, site frame: (%r, %r)" % (name, gx, -gz))
