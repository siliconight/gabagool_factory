"""Census the roof fixtures a cold run's level carries, per Empty design.

    python roof_census.py <run> [<previous run>]

For every design the exported candidate's drawn site placed (`blockers[]`
marked `empty`, seed 9080's `site.site.drawn.json`), from the run's own
workspace:

* the `tv_antenna` / `sat_dish` orders Patina wrote for it
  (`jobs/gas_block_001.patina_dressing.<b>/out/<b>.patina.dressing.json`);
* the mesh nodes in the dressing GLB the package carries
  (`exports/LF_gas_block_001.portable-godot/lot/<b>/art/dressing/<b>_dressing.glb`),
  and the previous run's count for the same design beside it.

Every path was read off cold run 9160's workspace before this was written;
a design whose files are missing is reported as missing, never skipped.
Prints what it counted and stops.
"""
import collections
import json
import pathlib
import struct
import sys

F = pathlib.Path(r"C:\Projects\gabagool_studios\gabagool_factory")


def ws(run):
    return F / "workspaces" / f"cold-{run}-ws" / ".level_factory"


def nodes(glb):
    if not glb.exists():
        return None
    b = glb.read_bytes()
    clen = struct.unpack_from("<I", b, 12)[0]
    g = json.loads(b[20:20 + clen])
    return sorted(n.get("name") for n in g.get("nodes", []) if "mesh" in n)


run = sys.argv[1]
prev = sys.argv[2] if len(sys.argv) > 2 else None
site = (ws(run) / "jobs" / "gas_block_001.lot_assemble.candidate.seed_9080" / "out" / "site.site.drawn.json")
placed = [b["archetype"] for b in json.loads(site.read_text(encoding="utf-8"))["blockers"] if b.get("empty")]
designs = collections.Counter(placed)
tot = collections.Counter()
missing = 0
print(f"cold {run}: {len(placed)} Empties placed, {len(designs)} designs")
for bid in sorted(designs):
    man = ws(run) / "jobs" / f"gas_block_001.patina_dressing.{bid}" / "out" / f"{bid}.patina.dressing.json"
    glb = (ws(run) / "exports" / "LF_gas_block_001.portable-godot" / "lot" / bid / "art" / "dressing"
           / f"{bid}_dressing.glb")
    if not man.exists():
        print(f"  {bid}: MISSING manifest {man}")
        missing += 1
        continue
    orders = collections.Counter(o["cover"] for o in json.loads(man.read_text(encoding="utf-8"))["orders"]
                                 if o["cover"] in ("tv_antenna", "sat_dish"))
    now = nodes(glb)
    before = nodes(ws(prev) / "exports" / "LF_gas_block_001.portable-godot" / "lot" / bid / "art"
                   / "dressing" / f"{bid}_dressing.glb") if prev else None
    for k, v in orders.items():
        tot[k] += v * designs[bid]
    print(f"  {bid} x{designs[bid]}: antenna {orders.get('tv_antenna', 0)}, dish {orders.get('sat_dish', 0)}; "
          f"dressing meshes {len(now) if now is not None else 'MISSING'}"
          + (f" (cold {prev}: {len(before) if before is not None else 'not placed'})" if prev else "")
          + ("" if before is None or now is None or before == now else "  NODES DIFFER"))
print(f"in the level: {tot.get('tv_antenna', 0)} antennas, {tot.get('sat_dish', 0)} dishes; "
      f"{missing} design(s) missing a manifest")
sys.exit(1 if missing else 0)
