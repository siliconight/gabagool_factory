"""Which greybox base geometry has no owner: every built building's base, read node by node against the passes that
dress it (Level Factory's `zoo_worldskin.gd`) and the slots the composer fills (Deli Counter's `themed_tscn`).

A probe: prints what it measured and stops.

WHY. Level Factory 0.218.0 made the export's greybox census refuse ANY greybox surface in a themed package, on the
evidence that every class it had reported had an owner. Cold run 9342 (precinct_yard_001, seed 9708) was refused on
two surfaces of a kind nobody owned -- apartment_walkup_a01's legacy fire escape, `FIREESCAPE_*` -- and cold run
9172 had shipped the same two, reported and not refused, on 2026-10-06. A cold run finds such a kind only in the
buildings its lot happens to draw; this reads every building in the library at once.

WHAT IT READS. `deli_counter/build/<spec>.glb` (the greybox base Deli Counter bakes; node names as authored) and
`<spec>.slots.json`. For each node with a mesh, every primitive on a `gb_*` material is one surface, as the
engine's census counts mesh surfaces. Each such node is asked, in order:
  - a collider? (`colonly` in its name: Godot deletes the visual at import)
  - a slot's own node? (`themed_tscn.owns_node` with `longer_siblings`, the question the base strip and the
    composer both ask). The composer strips it when the slot resolves to a themed module. THIS PROBE ASSUMES EVERY
    SLOT DOES, so a kit gap -- a slot left on its greybox fallback -- is not measured here.
  - one of the worldskin passes' name tests, mirrored from `zoo_worldskin.gd`, whose prefixes are READ from that
    file (a prefix that is not there FAILS the probe rather than passing it): slab (`slab_`, no `col`); stair
    (`stair`, no `col`, no `ramp`; a `stair_guard_` node is counted and never assigned, so it is reported apart);
    ladder (`ladder`, no `col`, and `_rail_` or `_rung_` -- any other ladder mesh is seen and not skinned, so it
    is reported apart); vault ledge (`VAULTLEDGE_`, no `col`); a fire escape (`FIREESCAPE_`, no `col`) when the
    file defines `FIRE_ESCAPE_PREFIX`, and a vehicle ramp (`ramp` and an index, exactly) when it defines
    `RAMP_PREFIX` -- the two passes Level Factory 0.220.0 added in answer to this census.
  - otherwise UNOWNED, reported by name.
A roof slab the composer drops geometrically (`roof_covered_nodes`) is a `slab_` node, which the slab pass owns
either way, so it is not modelled.

    python docs/findings/base_greybox_owners/census.py [--spec NAME ...] [--json OUT]
"""
import argparse
import collections
import glob
import json
import os
import re
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
F = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(F, "deli_counter"))
import themed_tscn  # noqa: E402

BUILD = os.path.join(F, "deli_counter", "build")
WORLDSKIN = os.path.join(F, "level_factory", "assets", "godot", "zoo_worldskin.gd")


def _const(src, name, required=True):
    m = re.search(r'^const %s: String = "([^"]*)"' % name, src, re.M)
    if m is None and required:
        raise SystemExit("UNKNOWN SHAPE: zoo_worldskin.gd defines no %s" % name)
    return m.group(1) if m else None


SRC = open(WORLDSKIN, encoding="utf-8").read()
SLAB = _const(SRC, "SLAB_PREFIX")
STAIR = _const(SRC, "STAIR_PREFIX")
GUARD = _const(SRC, "STAIR_GUARD_PREFIX")
LADDER = _const(SRC, "LADDER_PREFIX")
RAIL, RUNG = _const(SRC, "LADDER_RAIL_MARK"), _const(SRC, "LADDER_RUNG_MARK")
LEDGE = _const(SRC, "VAULT_LEDGE_PREFIX")
FIRE = _const(SRC, "FIRE_ESCAPE_PREFIX", required=False)
RAMP = _const(SRC, "RAMP_PREFIX", required=False)


def _gltf(path):
    b = open(path, "rb").read()
    if b[:4] != b"glTF":
        raise SystemExit("UNKNOWN SHAPE: %s is not a binary glTF" % path)
    n, kind = struct.unpack_from("<II", b, 12)
    if kind != 0x4E4F534A:
        raise SystemExit("UNKNOWN SHAPE: %s's first chunk is not JSON" % path)
    return json.loads(b[20:20 + n])


def owner(name, slot_ids, sibs):
    if "colonly" in name:
        return "collider"
    for sid in slot_ids:
        if themed_tscn.owns_node(sid, name, sibs[sid]):
            return "slot"
    if name.startswith(SLAB) and "col" not in name:
        return "slab pass"
    if name.startswith(STAIR) and "col" not in name and "ramp" not in name:
        return "stair guard (counted, never assigned)" if name.startswith(GUARD) else "stair pass"
    if name.startswith(LADDER) and "col" not in name:
        return "ladder pass" if (RAIL in name or RUNG in name) else "ladder, neither rail nor rung (left flat)"
    if name.startswith(LEDGE) and "col" not in name:
        return "vault ledge pass"
    if FIRE and name.startswith(FIRE) and "col" not in name:
        return "fire escape pass"
    if RAMP and name.startswith(RAMP) and re.fullmatch(r"[+-]?\d+", name[len(RAMP):]):
        return "ramp pass"
    return "UNOWNED"


def census(spec):
    g = _gltf(os.path.join(BUILD, spec + ".glb"))
    slots = json.load(open(os.path.join(BUILD, spec + ".slots.json"), encoding="utf-8"))
    if "slots" not in slots:
        raise SystemExit("UNKNOWN SHAPE: %s.slots.json has no slots (keys %s)" % (spec, sorted(slots)))
    ids = [s["slot_id"] for s in slots["slots"] if s.get("slot_id")]
    sibs = {sid: themed_tscn.longer_siblings(sid, ids) for sid in ids}
    mats = [m.get("name") or "" for m in g.get("materials", [])]
    by = collections.Counter()
    unowned = []
    for nd in g.get("nodes", []):
        if "mesh" not in nd:
            continue
        prims = g["meshes"][nd["mesh"]]["primitives"]
        gb = [mats[p["material"]] for p in prims if "material" in p and mats[p["material"]].startswith("gb_")]
        if not gb:
            continue
        who = owner(nd.get("name", ""), ids, sibs)
        by[who] += len(gb)
        if who == "UNOWNED" or who.startswith("ladder, neither") or who.startswith("stair guard"):
            unowned.append((who, nd.get("name", ""), ",".join(sorted(set(gb))), len(gb)))
    return by, unowned


ap = argparse.ArgumentParser()
ap.add_argument("--spec", nargs="*", default=None)
ap.add_argument("--json", default=None)
a = ap.parse_args()
specs = a.spec or sorted(os.path.basename(p)[:-len(".slots.json")]
                         for p in glob.glob(os.path.join(BUILD, "*.slots.json")))
print("[census] worldskin prefixes read: slab %r, stair %r (guard %r), ladder %r (%r / %r), vault ledge %r, "
      "fire escape %r, ramp %r" % (SLAB, STAIR, GUARD, LADDER, RAIL, RUNG, LEDGE, FIRE, RAMP))
total = collections.Counter()
rows = {}
families = collections.defaultdict(set)
for spec in specs:
    if not os.path.exists(os.path.join(BUILD, spec + ".glb")):
        print("%-34s NO GLB beside its slots.json" % spec)
        continue
    by, un = census(spec)
    total.update(by)
    rows[spec] = {"by_owner": dict(by), "flagged": un}
    for who, name, gb, n in un:
        families[(who, re.sub(r"\d+", "#", name))].add(spec)
    if un:
        print("%-34s %s" % (spec, "; ".join("%s %s (%s x%d)" % (who, name, gb, n) for who, name, gb, n in un)))
print("[census] %d spec(s); greybox surfaces by owner: %s" % (len(rows), dict(sorted(total.items()))))
for (who, fam), sp in sorted(families.items(), key=lambda t: (t[0][0], -len(t[1]))):
    print("    %-44s %-40s %d spec(s): %s" % (who, fam, len(sp), ", ".join(sorted(sp)[:8]) + (" ..." if len(sp) > 8 else "")))
if a.json:
    json.dump({"specs": rows, "total": dict(total)}, open(a.json, "w", encoding="utf-8"), indent=1, sort_keys=True)
