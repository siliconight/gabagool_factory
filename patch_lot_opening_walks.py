r"""The fair-opening test stops assuming the crew stands still.

    python patch_lot_opening_walks.py --explain
    python patch_lot_opening_walks.py --check
    python patch_lot_opening_walks.py
    python patch_lot_opening_walks.py --verify <gameplay.json> <site_walk.tscn>
    python patch_lot_opening_walks.py --revert

Run from the FACTORY ROOT (the directory holding `lot/`).

## What was measured

`lot_demo_001` seed 5118, graded 45/100 by Laser Tag across 25 runs. Every
point lost, by category:

    traversal       0 / 25    route completed in 0% of runs
    npc_pathing    10 / 20    enemies stuck 34 times
    sightlines     10 / 20    37% of positions visible to 3+ enemy spawns
    cover          20 / 20    47% of shots blocked -- full marks
    combat_pacing   5 / 15    crew under fire at 0.08 s

`probe_opening.py` against the built scene and its own gameplay json:

    enemy 0    26.5 m   OCCLUSION  (building #0, covers 48% of the line)
    enemy 1    55.0 m   DISTANCE
    enemy 2    79.7 m   DISTANCE
    enemy 3    94.6 m   DISTANCE
    enemy 4   114.6 m   DISTANCE
    enemy 5   129.5 m   DISTANCE

Five enemies are fair by distance and nobody can argue with those. One is
inside the opening at 26.5 m, admitted because `b0` -- the SPAWN building --
has a footprint rect across 48% of the line.

## Why that one enemy is 35 of the 55 lost points

`OPENING_RANGE`'s own docstring, written before any of this was measured:

    #: The second half is worse than a mis-stamped clock. The bot's route only
    #: advances in the ``else`` of "can I see an enemy", and ``LT_EnemyBrain``
    #: has no range gate at all, so a crew that can see one enemy never walks
    #: again and the sightline never clears. One visible enemy is 0% route
    #: completion by construction, on every seed.

`route_completion_rate: 0.0`. Traversal is 0 of 25 not because the bot cannot
path but because it can see somebody. One enemy costs the whole category, plus
the 10 pacing points to `INSTANT_CONTACT`.

## The actual defect

Not the occlusion branch. That branch is right, and the module argues for it:

    #: The distance was never the mechanism though -- an enemy 20 m away around
    #: a corner is a fair fight and an enemy 30 m away down an open street is
    #: not -- so distance alone is not what the search below tests

An enemy around a corner IS a fair fight. The defect is narrower and it is
stated, as a deliberate choice, in `opening_engagement_is_fair` itself:

    Both are checked at the spawn point rather than along the route on purpose:
    the crew's first second is the only moment it has no cover, no information
    and no ability to react

**The crew does not spend its first second at the spawn point.** It walks at
`CREW_SPEED = 4.5` the moment the run starts, and the module already knows the
number -- `OPENING_CLEARANCE` is that speed times the reaction window, and it is
used to widen the DISTANCE branch while the OCCLUSION branch keeps testing a
single stationary point. A corner that hides an enemy from the spawn tile and
not from four metres down the street is credited as cover for a fight that
starts after the crew has walked those four metres.

Laser Tag's raycast says so at 0.08 s, and its sampler says 37% of walkable
positions see 3+ enemy spawns. Lot said `b0` was in the way. Both are describing
the same segment and only one of them is measured against real collision.

## The change

`opening_engagement_is_fair` takes the stretch of route the crew covers during
its reaction window instead of a single point, and an enemy admitted by
occlusion must stay occluded from ALL of it. The distance branch is untouched.

    def opening_engagement_is_fair(candidate, crew_path, occluders, ...):
        if all(dist(candidate, p) >= opening_range + clearance
               for p in crew_path):
            return True
        return not any(has_line_of_sight(candidate, p, occluders)
                       for p in crew_path)

`crew_path` is a required positional, not an optional one with a
stand-still default. A default here would leave every existing caller testing
the old thing while the new code sat unreached, which is the shape of half the
defects this tree has produced -- and an unused parameter is an unfinished
thought.

Both callers build it from what they already hold: `place_enemies` has the
route polyline, and `_opening_findings` gets it passed down. `crew_reaction_path`
walks `OPENING_CLEARANCE` metres from the spawn and samples every
`_PATH_STEP` metres, spawn included, so the single-point behaviour is the
first sample rather than a separate case.

## What this does NOT claim

It does not make Lot's occlusion model correct. `has_line_of_sight` is still a
2D segment-vs-rect test against footprints, and a rect is still not a shell --
`lot.py` reads real collider boxes into `solids` three lines before it calls
`place_enemies` and does not pass them. Handing those through, filtered by eye
height the way `site_cover` derives `MIN_COVER_HEIGHT`, is the real fix and it
is a change to what "occluder" means across the module. This patch makes the
existing model answer the right question; it does not replace the model.

It also may not move enemy 0. If `b0` occludes the whole reaction path, the
enemy stays where it is and the grade does not change -- and that is a result,
not a failure. `--verify` reports which enemies the new rule refuses on a real
built site before anything is re-run, so the answer arrives before the hour.
"""
from __future__ import annotations

import hashlib
import math
import sys
from pathlib import Path

SS = Path("lot") / "site_spawns.py"
SIDECAR = ".pre_openingwalk"


# --------------------------------------------------------------------------
# the edits
# --------------------------------------------------------------------------

FAIR_OLD = '''def opening_engagement_is_fair(candidate, spawn, occluders,
                               opening_range: float = OPENING_RANGE,
                               clearance: float = OPENING_CLEARANCE) -> bool:
    """True when an enemy here cannot shoot the crew before it has moved.

    Either it is further away than *either* side can open fire from with a
    second of daylight on top, or a building stands between the two. Both are
    checked at the spawn point rather than along the route on purpose: the
    crew's first second is the only moment it has no cover, no information and
    no ability to react, and that is the moment Laser Tag measures as
    ``time_to_first_contact``.

    The range defaults to `OPENING_RANGE`, which is the crew's reach and not the
    enemy's -- the crew sees ten metres further and shoots first, so the enemy's
    35 m answers the wrong question. `OPENING_CLEARANCE` is the part that was
    missing after that: a distance *equal* to the acquisition threshold is not
    a standoff, it is the threshold, and it starts the fight on frame one just
    as surely as standing next to the crew does.
    """
    if math.dist(candidate, spawn) >= opening_range + clearance:
        return True
    return not has_line_of_sight(candidate, spawn, occluders)'''

FAIR_NEW = '''#: How finely to sample the crew's opening walk. Half a metre is shorter than
#: any wall this site builds, so a corner cannot pass between two samples.
_PATH_STEP = 0.5


def crew_reaction_path(route, clearance: float = OPENING_CLEARANCE,
                       step: float = _PATH_STEP) -> list:
    """Where the crew is during the window the opening is judged over.

    Not a point. `CREW_SPEED` and `REACTION_SECONDS` are already multiplied
    together in `OPENING_CLEARANCE` to widen the distance branch; this walks the
    same metres along the actual route so the occlusion branch is asked about
    the same window. The spawn is the first sample, so a caller with nowhere to
    walk gets the old single-point behaviour without a second code path.
    """
    if not route:
        return []
    points = [tuple(route[0][:2])]
    walked = 0.0
    for a, b in zip(route, route[1:]):
        a, b = tuple(a[:2]), tuple(b[:2])
        leg = math.dist(a, b)
        if leg <= 1e-9:
            continue
        travelled = 0.0
        while travelled + step <= leg:
            travelled += step
            walked += step
            if walked > clearance:
                return points
            t = travelled / leg
            points.append((a[0] + (b[0] - a[0]) * t,
                           a[1] + (b[1] - a[1]) * t))
        walked += leg - travelled
        if walked >= clearance:
            return points
    return points


def opening_engagement_is_fair(candidate, crew_path, occluders,
                               opening_range: float = OPENING_RANGE,
                               clearance: float = OPENING_CLEARANCE) -> bool:
    """True when an enemy here cannot shoot the crew before it has moved.

    Either it is further away than *either* side can open fire from with a
    second of daylight on top, or a building stands between the two -- and
    both are now asked of the STRETCH OF ROUTE the crew covers in that second,
    not of the spawn tile alone.

    THE SPAWN TILE WAS THE DEFECT, and it was a deliberate choice with a
    reason that does not survive contact with the bot. The reason was: "the
    crew's first second is the only moment it has no cover, no information and
    no ability to react, and that is the moment Laser Tag measures as
    ``time_to_first_contact``." True, and the crew does not spend that second
    standing on the spawn. It walks at `CREW_SPEED` from frame one. A corner
    that hides an enemy from the spawn and not from four metres down the street
    was credited as cover for a fight that starts after the crew has walked
    those four metres.

    Measured, `lot_demo_001` seed 5118: Enemy_0 stood 26.5 m out, admitted
    because `b0` -- the crew's OWN spawn building -- covered 48% of the line
    from the spawn tile. Laser Tag's raycast disagreed at 0.08 s, its sampler
    reported 37% of walkable positions visible to 3+ enemy spawns, and the run
    graded 45/100 with `route_completion_rate: 0.0`. Per `OPENING_RANGE`'s own
    note, one visible enemy is 0% route completion by construction, so that one
    spawn cost the whole 25-point traversal category and the 10 pacing points
    on top.

    `crew_path` is required rather than defaulted to ``[spawn]``. A default
    would leave both existing callers testing the old thing while this code sat
    unreached, which is precisely the failure this patch exists to correct one
    instance of.

    The range still defaults to `OPENING_RANGE`, which is the crew's reach and
    not the enemy's -- the crew sees ten metres further and shoots first, so the
    enemy's 35 m answers the wrong question. `OPENING_CLEARANCE` is the part
    that was missing after that: a distance *equal* to the acquisition threshold
    is not a standoff, it is the threshold, and it starts the fight on frame one
    just as surely as standing next to the crew does.

    STILL NOT A COLLISION TEST. `has_line_of_sight` remains a 2D segment
    against footprint rects and a rect is not a shell. `lot.py` reads real
    collider boxes into `solids` three lines above its `place_enemies` call and
    does not pass them; doing so, filtered by eye height the way `site_cover`
    derives `MIN_COVER_HEIGHT`, is the fix this one does not attempt.
    """
    if not crew_path:
        return False
    reach = opening_range + clearance
    if all(math.dist(candidate, p) >= reach for p in crew_path):
        return True
    return not any(has_line_of_sight(candidate, p, occluders)
                   for p in crew_path)'''


CALL_OLD = '''            # The rule the standoff number was standing in for.
            if not opening_engagement_is_fair(candidate, spawn, occluders):
                continue'''

CALL_NEW = '''            # The rule the standoff number was standing in for, asked of
            # the ground the crew covers in its first second rather than of
            # the tile it starts on.
            if not opening_engagement_is_fair(candidate, crew_path, occluders):
                continue'''


PATH_OLD = '''    occluders = footprints(site_spec, margin=0.0)

    placed: list = []'''

PATH_NEW = '''    occluders = footprints(site_spec, margin=0.0)

    # The crew walks from frame one, so the opening is judged over the metres
    # it covers rather than the tile it starts on. Same window the distance
    # branch already allows for, applied to the same route the enemies are
    # spread along -- both halves of one contract now reading one number.
    crew_path = crew_reaction_path(route)

    placed: list = []'''


FINDINGS_CALL_OLD = '''    plan.findings.extend(_findings(plan, count, standoff, spawn, occluders))'''

FINDINGS_CALL_NEW = '''    plan.findings.extend(_findings(plan, count, standoff, spawn, occluders,
                                   crew_path=crew_path))'''


FINDINGS_SIG_OLD = '''def _findings(plan: Placement, requested: int, standoff: float,
              spawn=None, occluders=None) -> list:'''

FINDINGS_SIG_NEW = '''def _findings(plan: Placement, requested: int, standoff: float,
              spawn=None, occluders=None, *, crew_path=None) -> list:'''


READBACK_OLD = '''    out.extend(_opening_findings(plan, spawn, occluders, index, closest))'''

READBACK_NEW = '''    out.extend(_opening_findings(plan, spawn, occluders, index, closest,
                                 crew_path=crew_path))'''


OPENING_SIG_OLD = '''def _opening_findings(plan: Placement, spawn, occluders, index: int,
                      closest: float) -> list:'''

OPENING_SIG_NEW = '''def _opening_findings(plan: Placement, spawn, occluders, index: int,
                      closest: float, *, crew_path=None) -> list:'''


OPENING_BODY_OLD = '''    if occluders is not None:
        for i, point in enumerate(plan.positions):
            xy = point[:2]
            if not opening_engagement_is_fair(xy, spawn, occluders):
                exposed.append((i, math.dist(xy, spawn)))'''

OPENING_BODY_NEW = '''    if occluders is not None:
        # The same window the search used. A read-back that asked an easier
        # question than the search would report a clean opening on exactly the
        # maps the search had just been too generous about, which is the
        # failure this function's docstring describes one version of.
        path = crew_path or [spawn]
        for i, point in enumerate(plan.positions):
            xy = point[:2]
            if not opening_engagement_is_fair(xy, path, occluders):
                exposed.append((i, math.dist(xy, spawn)))'''


EDITS = {
    SS: ((FAIR_OLD, FAIR_NEW),
         (PATH_OLD, PATH_NEW),
         (CALL_OLD, CALL_NEW),
         (FINDINGS_CALL_OLD, FINDINGS_CALL_NEW),
         (FINDINGS_SIG_OLD, FINDINGS_SIG_NEW),
         (READBACK_OLD, READBACK_NEW),
         (OPENING_SIG_OLD, OPENING_SIG_NEW),
         (OPENING_BODY_OLD, OPENING_BODY_NEW)),
}

_CRLF = "\r\n"


def _find(body: str, anchor: str):
    for candidate in (anchor, anchor.replace("\n", _CRLF)):
        count = body.count(candidate)
        if count:
            return candidate, count
    return anchor, 0


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _apply(path: Path, edits, *, check: bool) -> int:
    raw = path.read_bytes()
    body = raw.decode("utf-8")
    side = path.with_suffix(path.suffix + SIDECAR)

    done = sum(1 for _o, new in edits if _find(body, new)[1] == 1)
    if done == len(edits):
        print(f"  already applied  {path.name}")
        return 0
    if done:
        print(f"REFUSING: {path.name} has {done} of {len(edits)} edits already "
              f"present.")
        return 1

    out = body
    for old, new in edits:
        anchor, count = _find(out, old)
        if count != 1:
            print(f"REFUSING: {path.name} -- expected 1 occurrence of an "
                  f"anchor, found {count}.")
            print(f"  anchor starts: {old.splitlines()[0].strip()!r}")
            return 1
        out = out.replace(
            anchor, new.replace("\n", _CRLF) if _CRLF in anchor else new, 1)

    data = out.encode("utf-8")
    if check:
        print(f"  would patch  {path.name}  {len(raw):,} -> {len(data):,} "
              f"bytes ({len(data) - len(raw):+,})")
        return 0
    if not side.is_file():
        side.write_bytes(raw)
    path.write_bytes(data)
    print(f"  patched      {path.name}  {len(raw):,} -> {len(data):,} bytes "
          f"({len(data) - len(raw):+,})  sha256 {_sha(data)[:16]}")
    return 0


# --------------------------------------------------------------------------
# --explain / --verify
# --------------------------------------------------------------------------

def _explain() -> int:
    sys.path.insert(0, str(Path.cwd() / "lot"))
    import site_spawns as ss
    print(f"  OPENING_RANGE       {ss.OPENING_RANGE} m   the CREW's reach")
    print(f"  CREW_SPEED          {ss.CREW_SPEED} m/s")
    print(f"  REACTION_SECONDS    {ss.REACTION_SECONDS} s")
    print(f"  OPENING_CLEARANCE   {ss.OPENING_CLEARANCE} m   "
          f"the ground the crew covers while the opening is judged")
    print()
    if hasattr(ss, "crew_reaction_path"):
        route = [(-70.0, -69.0), (-6.0, -81.0), (76.0, 6.0)]
        path = ss.crew_reaction_path(route)
        print(f"  patched: the opening is judged over {len(path)} point(s) "
              f"spanning {math.dist(path[0], path[-1]):.1f} m of route")
        print(f"    first {path[0][0]:.1f}, {path[0][1]:.1f}"
              f"   last {path[-1][0]:.1f}, {path[-1][1]:.1f}")
    else:
        print("  unpatched: the opening is judged at ONE point, the spawn "
              "tile, while the crew walks 4.5 m during the same window")
    return 0


def _verify(gameplay: Path, scene: Path) -> int:
    """Which enemies the new rule refuses, on a real built site."""
    sys.path.insert(0, str(Path.cwd() / "lot"))
    import json
    import re
    import site_spawns as ss

    if not hasattr(ss, "crew_reaction_path"):
        print("[verify] site_spawns is unpatched -- apply first")
        return 1

    data = json.loads(gameplay.read_text(encoding="utf-8"))
    spec = {"name": "site", "buildings": [
        {"id": b.get("id"), "at": b.get("at"), "rot": b.get("rot", 0),
         **({"footprint": b["footprint"]} if b.get("footprint") else {})}
        for b in data.get("buildings", []) or []]}
    rect = (data.get("ground_extent") or {}).get("rect")
    if rect:
        spec["ground"] = {"size_x": rect[2] - rect[0],
                          "size_y": rect[3] - rect[1]}

    hook = re.compile(
        r'^\[node name="([^"]+)" type="Node3D" parent="([^"]*)"\]\s*\n'
        r'transform = Transform3D\(\s*1,\s*0,\s*0,\s*0,\s*1,\s*0,\s*0,\s*0,\s*1,'
        r'([^)]*)\)', re.M)
    text = scene.read_text(encoding="utf-8", errors="replace")
    spawn, objective, enemies = None, None, []
    for name, parent, nums in hook.findall(text):
        try:
            x, _y, z = [float(v) for v in nums.split(",")[:3]]
        except ValueError:
            continue
        xy = (x, -z)
        if name == "LT_PlayerSpawn":
            spawn = xy
        elif name == "LT_ObjectivePoint":
            objective = xy
        elif parent == "LT_EnemySpawnPoints" and name.startswith("Enemy_"):
            enemies.append((int(name.split("_")[1]), xy))
    enemies.sort()

    if spawn is None or not enemies:
        print("[verify] could not read the spawn and enemy hooks from "
              f"{scene}")
        return 1
    route = [spawn] + ([objective] if objective else [])
    path = ss.crew_reaction_path(route) if objective else [spawn]
    occ = ss.footprints(spec, margin=0.0)

    print(f"  {scene.name}: {len(enemies)} enemies, {len(occ)} buildings")
    print(f"  opening judged over {len(path)} point(s), "
          f"{math.dist(path[0], path[-1]):.1f} m of route")
    print()
    refused = 0
    for i, xy in enemies:
        d = math.dist(xy, spawn)
        was = (d >= ss.OPENING_RANGE + ss.OPENING_CLEARANCE
               or not ss.has_line_of_sight(xy, spawn, occ))
        now = ss.opening_engagement_is_fair(xy, path, occ)
        mark = ""
        if was and not now:
            mark = "   <-- REFUSED NOW: it will be moved"
            refused += 1
        elif not was:
            mark = "   (was already unfair)"
        print(f"  enemy {i}  {d:>7.1f} m   before {'fair' if was else 'UNFAIR'}"
              f"   after {'fair' if now else 'UNFAIR'}{mark}")
    print()
    if refused:
        print(f"  {refused} enemy spawn(s) the patched rule will not accept. "
              f"Re-run the mission and they move.")
    else:
        print("  the patched rule accepts every enemy this site already has, "
              "so re-running will not change the placement. That is a result: "
              "the occlusion these spawns rely on survives the crew's opening "
              "walk, and the 0.08 s first shot is coming from the model being "
              "2D rather than from the window being too short.")
    return 0


def main(argv: list[str]) -> int:
    if "--explain" in argv:
        return _explain()
    if "--verify" in argv:
        i = argv.index("--verify")
        if i + 2 >= len(argv):
            raise SystemExit("--verify needs <gameplay.json> <site_walk.tscn>")
        return _verify(Path(argv[i + 1]), Path(argv[i + 2]))

    root = Path.cwd()
    for rel in EDITS:
        if not (root / rel).is_file():
            raise SystemExit(f"cannot find {rel} under {root} -- run from the "
                             f"factory root (the directory holding lot/)")

    if "--revert" in argv:
        bad = 0
        for rel in EDITS:
            path = root / rel
            side = path.with_suffix(path.suffix + SIDECAR)
            if not side.is_file():
                print(f"  no sidecar for {path.name}")
                bad = 1
                continue
            path.write_bytes(side.read_bytes())
            print(f"  reverted     {path.name}")
        return bad

    check = "--check" in argv
    for rel, edits in EDITS.items():
        code = _apply(root / rel, edits, check=check)
        if code:
            return code
    if not check:
        print()
        print("  Before re-running anything, ask what it changes:")
        print("    python patch_lot_opening_walks.py --verify \\")
        print("      .\\gp_5118.json \\")
        print("      lot-demo-ws\\.level_factory\\jobs\\lot_demo_001."
              "lot_assemble.candidate.seed_5118\\out\\site_walk.tscn")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
