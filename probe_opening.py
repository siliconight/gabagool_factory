r"""Why does a map that satisfies `opening_engagement_is_fair` open with a shot?

    python probe_opening.py --selftest
    python probe_opening.py --gameplay <site.site.gameplay.json>
    python probe_opening.py --gameplay <...> --spawn X Z

Run from the FACTORY ROOT (the directory holding `lot/`).

## What is being asked

Laser Tag graded `lot_demo_001` at 45/100. Combat pacing lost 10 of 15 points
to one finding:

    WARN  INSTANT_CONTACT   The crew came under fire almost instantly (0.1s)

and traversal lost all 25 because the crew is dead before it finishes the route
(`route_completion_rate: 0.0`, `team_wipe_count: 25`). The report's own numbers:

    avg_time_to_first_enemy_shot   0.08 s     scenario wants >= 3.0
    enemy_sight_range              35.0 m     default_laser_tag_scenario.tres

`site_spawns.place_enemies` already refuses any enemy position that fails
`opening_engagement_is_fair`, and that function already says the right thing:

    if math.dist(candidate, spawn) >= opening_range + clearance:
        return True
    return not has_line_of_sight(candidate, spawn, occluders)

45 + 4.5 = 49.5 m, or a building in the way. The rule is not missing and it is
not unwired -- line 538 calls it on every candidate. So the interesting question
is not "why was the rule not applied" but **which of its two branches let each
enemy through**, because the two are not equally trustworthy:

  * The DISTANCE branch is a fact. 49.5 m is 49.5 m.
  * The OCCLUSION branch is a claim, and it is made in two dimensions against
    axis-aligned footprint RECTS. `has_line_of_sight` says so itself: "Buildings
    are the only occluders Lot can be sure of -- a shell is solid from the
    outside whatever is in it." A rect is not a shell. A shell with an open
    face, a courtyard, a covered walkthrough or a footprint larger than its
    massing is a rect that claims cover the geometry does not provide.

If every enemy passed on distance, the opening is fair by construction and the
0.08 s is coming from somewhere else entirely -- a different spawn marker, or
enemies moving before the clock, and this probe says so rather than guessing.

If enemies passed on occlusion, the site is trusting a 2D rect to stop a 3D
shot, and Laser Tag's own sampler already disagrees with it:

    WARN  OVEREXPOSED_ZONE  37% of walkable positions are visible to 3+ enemy
                            spawns. Worst at (-6.0, 0.4, 20.0), visible to 4.

That finding is measured from the enemy spawns by `LT_MapSampler` against real
collision. Lot says those spawns are occluded; Laser Tag says a third of the map
can see three or more of them. Both cannot be right, and this probe is the
cheapest way to find out which claim is doing the work.

## What it prints and stops at

Per enemy: distance to the crew spawn, which branch admitted it, and -- when it
was occlusion -- which building rect was credited and how much of the line that
rect actually covers. Then the counts. It changes nothing.

Read from the MERGED gameplay json rather than the candidate spec in temp/,
because the spec written at plan time carries no footprints: `_write_site_spec`
emits `archetype` and `glb`, and the extents are measured later, during assembly.
A probe run against the spec sees zero buildings and would report every line
open -- which is a fact about the spec, not about the site, and reporting it as
the second would be the failure mode this file exists to avoid.
"""
from __future__ import annotations

import argparse
import json
import math
import re
import sys
from pathlib import Path

#: `lot.write_walk_scene` emits every mission point as a Node3D hook with an
#: identity basis, so the origin is the last three numbers of the transform.
#: Godot is Y-up and the site plan is XY, so site y = -godot z -- the same
#: conversion `_v3` applies going the other way.
_HOOK = re.compile(
    r'^\[node name="([^"]+)" type="Node3D" parent="([^"]*)"\]\s*\n'
    r'transform = Transform3D\(\s*1,\s*0,\s*0,\s*0,\s*1,\s*0,\s*0,\s*0,\s*1,'
    r'([^)]*)\)', re.M)


#: A building instance in a built site scene. `write_godot_scene` emits one
#: StaticBody3D/Node3D per building at the top level; counting them is enough to
#: tell two builds of one mission apart, because the themed path selects from a
#: narrower pool than the greybox path and lands different shells.
_SCENE_BUILDING = re.compile(
    r'^\[node name="(b\d+)"[^\]]*parent="\."\]', re.M)


def guard_same_build(scene_path: Path, data: dict) -> str | None:
    """Refuse a scene and a gameplay json that describe different sites.

    THE MISTAKE THIS EXISTS FOR, made on the first run of this probe: enemy
    hooks were read from `lot_assemble.candidate.seed_5118` and building
    footprints from `preview/<mission>_walk`, which is the THEMED build. Those
    are two different sites -- `_write_site_spec` runs again for the themed
    path and `require_themed_shells` narrows the pool, so the themed candidate
    stands different shells on a different plate. The probe happily reported an
    enemy from one build as unfair against the other build's buildings.

    Nothing about that output looked wrong. That is the point: a probe that
    cannot tell which site it is measuring will produce a confident number for
    a site that does not exist.
    """
    text = scene_path.read_text(encoding="utf-8", errors="replace")
    in_scene = len(set(_SCENE_BUILDING.findall(text)))
    in_json = len(data.get("buildings") or [])
    if in_scene and in_json and in_scene != in_json:
        return (f"{in_scene} building(s) in the scene, {in_json} in the "
                f"gameplay json")
    rect = (data.get("ground_extent") or {}).get("rect")
    if rect:
        span = (round(rect[2] - rect[0]), round(rect[3] - rect[1]))
        sizes = re.findall(r'^size = Vector3\(([\d.]+), [\d.]+, ([\d.]+)\)',
                           text, re.M)
        widest = max((float(a) for a, _b in sizes), default=0.0)
        if widest and widest > span[0] + 1.0:
            return (f"the scene has a {widest:.0f} m box on a plate the "
                    f"gameplay json says is {span[0]} m wide")
    return None


def hooks_from_scene(path: Path):
    """(spawn, [enemies]) read from a built ``site_walk.tscn``.

    THE SCENE, not a re-run of `place_enemies`. Re-running it here would be a
    second opinion computed from the same inputs, and the question is what
    Laser Tag was handed -- which is only answerable from what was written.
    """
    text = path.read_text(encoding="utf-8", errors="replace")
    spawn, enemies = None, []
    for name, parent, nums in _HOOK.findall(text):
        try:
            x, _y, z = [float(v) for v in nums.split(",")[:3]]
        except ValueError:
            continue
        xy = (x, -z)
        if name == "LT_PlayerSpawn":
            spawn = xy
        elif parent == "LT_EnemySpawnPoints" and name.startswith("Enemy_"):
            enemies.append((int(name.split("_")[1]), xy))
    enemies.sort()
    return spawn, [xy for _i, xy in enemies]


def _load_site_spawns():
    root = Path.cwd()
    lot_dir = root / "lot"
    if not lot_dir.is_dir():
        raise SystemExit(f"cannot find lot/ under {root} -- run from the "
                         f"factory root")
    sys.path.insert(0, str(lot_dir))
    import site_spawns
    return site_spawns


def _spec_from_gameplay(data: dict) -> dict:
    """A site spec `site_spawns` can read, rebuilt from what was assembled.

    Only the keys the placement functions touch. `footprint` is present here
    and absent from the plan-time spec, which is the whole reason this probe
    reads this file.
    """
    buildings = []
    for b in data.get("buildings", []) or []:
        rec = {"id": b.get("id"), "at": b.get("at"), "rot": b.get("rot", 0)}
        if b.get("footprint"):
            rec["footprint"] = b["footprint"]
        buildings.append(rec)
    rect = (data.get("ground_extent") or {}).get("rect")
    spec = {"name": "site", "buildings": buildings}
    if rect:
        x0, y0, x1, y1 = rect
        spec["ground"] = {"size_x": x1 - x0, "size_y": y1 - y0}
        spec["_ground_rect"] = rect
    return spec


def _markers(data: dict):
    """(spawn, objective, extraction) in site XY, or None where absent."""
    out = {}
    for entry in data.get("site_markers", []) or []:
        if not isinstance(entry, dict):
            continue
        groups = {str(g).lower() for g in (entry.get("groups") or [])}
        at = entry.get("at") or entry.get("position")
        if not at or len(at) < 2:
            continue
        xy = (float(at[0]), float(at[1]))
        for key, tag in (("spawn", "lt_playerspawn"),
                         ("objective", "lt_objectivepoint"),
                         ("extraction", "lt_extractionpoint")):
            if tag in groups or key in groups:
                out.setdefault(key, xy)
    return out


def _covered_fraction(a, b, rect, samples: int = 400) -> float:
    """How much of segment a->b lies inside ``rect``. The claim, quantified."""
    inside = 0
    for i in range(samples + 1):
        t = i / samples
        p = (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)
        if rect[0] <= p[0] <= rect[2] and rect[1] <= p[1] <= rect[3]:
            inside += 1
    return inside / (samples + 1)


def report(ss, spec: dict, spawn, enemies, *, opening_range=None,
           clearance=None) -> int:
    opening_range = ss.OPENING_RANGE if opening_range is None else opening_range
    clearance = ss.OPENING_CLEARANCE if clearance is None else clearance
    threshold = opening_range + clearance
    occluders = ss.footprints(spec, margin=0.0)

    print(f"  crew spawn            ({spawn[0]:.1f}, {spawn[1]:.1f})")
    print(f"  occluders (buildings) {len(occluders)}")
    print(f"  MIN_STANDOFF          {ss.MIN_STANDOFF} m   (a floor, not the rule)")
    print(f"  OPENING_RANGE         {opening_range} m")
    print(f"  OPENING_CLEARANCE     {clearance} m   "
          f"= CREW_SPEED {ss.CREW_SPEED} x REACTION_SECONDS {ss.REACTION_SECONDS}")
    print(f"  fair by distance at   {threshold} m")
    print()

    by_distance = by_occlusion = unfair = 0
    print(f"  {'enemy':<7} {'dist':>7}  admitted by")
    for i, e in enumerate(enemies):
        xy = (float(e[0]), float(e[1]))
        d = math.dist(xy, spawn)
        if d >= threshold:
            by_distance += 1
            print(f"  {i:<7} {d:>7.1f}  DISTANCE   (+{d - threshold:.1f} m clear)")
            continue
        if not ss.has_line_of_sight(xy, spawn, occluders):
            by_occlusion += 1
            best, best_frac = None, 0.0
            for j, rect in enumerate(occluders):
                if ss._inside(xy, rect) or ss._inside(spawn, rect):
                    continue
                if not ss._segment_crosses(xy, spawn, rect):
                    continue
                frac = _covered_fraction(xy, spawn, rect)
                if frac > best_frac:
                    best, best_frac = j, frac
            where = (f"building #{best}, covers {best_frac * 100:.0f}% of the "
                     f"line" if best is not None else "a rect, unattributed")
            print(f"  {i:<7} {d:>7.1f}  OCCLUSION  ({where})")
            continue
        unfair += 1
        print(f"  {i:<7} {d:>7.1f}  NEITHER    <-- this one should not be here")

    print()
    print(f"  by distance   {by_distance}")
    print(f"  by occlusion  {by_occlusion}"
          + ("   <-- these are 2D rect claims, not measured collision"
             if by_occlusion else ""))
    print(f"  neither       {unfair}"
          + ("   <-- place_enemies would have refused these; something else "
             "placed them" if unfair else ""))
    print()
    if by_occlusion and not unfair:
        print("  READ: every enemy inside the fair-opening distance is there on")
        print("  the strength of a footprint rect. `has_line_of_sight` is a 2D")
        print("  segment-vs-rect test and says so; Laser Tag's sampler measures")
        print("  real collision and reported 37% of the map visible to 3+ enemy")
        print("  spawns. That is the disagreement to settle next, and the two")
        print("  do not have to be reconciled by argument -- LT_MapSampler's")
        print("  numbers are in the report already.")
    elif by_distance == len(enemies):
        print("  READ: every enemy is beyond the fair-opening distance. The")
        print("  0.08 s first shot is NOT coming from enemy placement, and the")
        print("  next question is which spawn Laser Tag actually used.")
    return 0


def _selftest() -> int:
    ss = _load_site_spawns()
    spec = {"name": "site", "ground": {"size_x": 200, "size_y": 200},
            "buildings": [{"id": "b0", "at": [0, 0], "rot": 0,
                           "footprint": [20, 20]}]}
    occ = ss.footprints(spec, margin=0.0)
    assert len(occ) == 1, occ
    # Deliberately inside the fair-opening distance for the two "near" cases:
    # a first draft put them 80-108 m out, where they passed on DISTANCE and
    # the occlusion branch was never reached. A fixture that exercises the
    # wrong branch is a test that agrees with anything.
    spawn = (-30.0, 0.0)
    far = (30.0, 0.0)               # 60 m  -> distance
    near_hidden = (15.0, 0.0)       # 45 m, building between -> occlusion
    near_open = (-5.0, 25.0)        # 35 m, clear line -> neither
    assert ss.opening_engagement_is_fair(far, spawn, occ)
    assert ss.opening_engagement_is_fair(near_hidden, spawn, occ)
    assert not ss.opening_engagement_is_fair(near_open, spawn, occ)
    frac = _covered_fraction(near_hidden, spawn, occ[0])
    assert 0.3 < frac < 0.6, frac
    print("  selftest OK: far passes on distance, hidden passes on occlusion,")
    print(f"  open fails; the blocking rect covers {frac * 100:.0f}% of the line")
    return 0


def main(argv) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--gameplay", help="path to a built site.site.gameplay.json")
    ap.add_argument("--scene", help="path to the built site_walk.tscn, which "
                                    "carries the enemy hooks as shipped")
    ap.add_argument("--spawn", nargs=2, type=float, metavar=("X", "Z"),
                    help="crew spawn, when the markers cannot be read")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)

    if args.selftest:
        return _selftest()
    if not args.gameplay:
        ap.error("--gameplay is required (or --selftest)")

    ss = _load_site_spawns()
    data = json.loads(Path(args.gameplay).read_text(encoding="utf-8"))
    spec = _spec_from_gameplay(data)
    if not spec["buildings"]:
        print("  no buildings in this file -- is it a candidate spec rather "
              "than a merged gameplay json?")
        return 1
    if not any("footprint" in b for b in spec["buildings"]):
        print("  buildings carry no footprint -- this file predates assembly, "
              "and every line would read as open. Refusing to report that.")
        return 1

    scene_spawn, scene_enemies = (None, [])
    if args.scene:
        scene = Path(args.scene)
        mismatch = guard_same_build(scene, data)
        if mismatch:
            print("  REFUSING: the scene and the gameplay json are not the "
                  "same build --")
            print(f"    {mismatch}")
            print("  A mission has a greybox build and a themed build and they "
                  "stand DIFFERENT shells. Pass both files from the SAME job:")
            print("    <ws>\\.level_factory\\jobs\\<mission>.lot_assemble."
                  "candidate.seed_NNNN\\out\\site.site.gameplay.json")
            print("    <ws>\\.level_factory\\jobs\\<mission>.lot_assemble."
                  "candidate.seed_NNNN\\out\\site_walk.tscn")
            return 1
        scene_spawn, scene_enemies = hooks_from_scene(scene)

    marks = _markers(data)
    spawn = (tuple(args.spawn) if args.spawn
             else scene_spawn or marks.get("spawn"))
    if spawn is None:
        print("  could not find the crew spawn in this file; pass --spawn X Z")
        print(f"  markers found: {sorted(marks)}")
        return 1

    enemies = list(scene_enemies)
    for entry in ([] if enemies else (data.get("site_markers") or [])):
        if not isinstance(entry, dict):
            continue
        groups = {str(g).lower() for g in (entry.get("groups") or [])}
        name = str(entry.get("name", "")).lower()
        at = entry.get("at") or entry.get("position")
        if not at or len(at) < 2:
            continue
        if "lt_enemyspawn" in groups or name.startswith("enemy"):
            enemies.append((float(at[0]), float(at[1])))
    if not enemies:
        print("  no enemy spawn hooks found. `site_markers` is empty in this "
              "file, so pass the built scene as well:")
        print("    --scene <...>/lot_demo_001.lot_assemble.candidate.seed_NNNN"
              "/out/site_walk.tscn")
        print("  Rebuilding the placement here instead would be a second "
              "opinion computed from the same inputs, not a reading of what "
              "Laser Tag was handed.")
        return 1

    print(f"  {args.gameplay}")
    return report(ss, spec, spawn, enemies)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
