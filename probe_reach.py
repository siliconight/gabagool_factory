r"""What can the crew walk to, and what is in the way? The pre-flight's own model.

    python probe_reach.py <site_walk.tscn>
    python probe_reach.py <site_walk.tscn> --cell 4
    python probe_reach.py --selftest

## Why this exists

`spawn_placement.check_spawn_placement` refuses a build with

    "N of M mission destination(s) cannot be walked to from the player spawn:
     Route_2 is sealed off from the crew spawn"

and that is the last branch of `_placement`: the cell EXISTS, HAS floor, is on
the crew's STOREY, and is NOT inside solid geometry -- the flood fill simply
never arrives. So the finding says a wall exists without saying where, and the
reader is left to infer it from a scene file.

This prints the field the refusal was computed on. Same functions, same boxes,
same flood fill -- `heightfield` and `walk_distances` out of `spawn_placement`
itself, so this cannot disagree with the gate about geometry. It only says
where.

It is a PROBE. It prints what it measured and stops. It does not decide whether
a seal is a bug in the level or a bug in the model.

## Reading the map

    +   reachable on foot from the crew spawn
    o   standable, but the flood fill never got here   <-- the defect, in plan
    #   inside solid geometry
    ~   floored, but on a different storey than the spawn
    .   floored nowhere / outside the site's collision

    S   crew spawn      O   objective      E   an unreachable destination
    D   a reachable destination            e   enemy spawn

A wall reads as a line of `#`. A seal reads as a field of `o` with no `+`
touching it. The two together are the answer the finding does not print.

## The model's own bias, restated because it decides what a seal means

`spawn_placement`'s docstring: the field "is deliberately *optimistic* -- it
does not erode by agent radius, so a gap a 0.4 m agent cannot squeeze through
still reads as open ... this module under-reports rather than inventing a wall,
and everything it does report is something the bake will refuse too."

So an `o` region here is a seal the navmesh bake will also refuse. It is not a
false positive of the grid. What it MIGHT be is a seal caused by collision the
reader could not read -- which is why the opaque list is printed above the map
rather than left in a caveat.
"""
from __future__ import annotations

import sys
from pathlib import Path


def _lf_root(start: Path) -> Path | None:
    for base in (start, *start.parents):
        if (base / "level_factory" / "packages" / "validation").is_dir():
            return base / "level_factory"
        if (base / "packages" / "validation").is_dir():
            return base
    return None


ROOT = _lf_root(Path(__file__).resolve().parent)
if ROOT is None:
    raise SystemExit("cannot find level_factory/packages/validation -- run this "
                     "from the factory root")
sys.path.insert(0, str(ROOT))

from packages.validation import spawn_placement as sp          # noqa: E402
from packages.validation.ground_contact import (               # noqa: E402
    mission_points, read_scene_text, resolver, support_under)


# ------------------------------------------------------------------- reading
def survey(scene: Path):
    text = scene.read_text(encoding="utf-8", errors="replace")
    reading = read_scene_text(text, resolve=resolver(scene.parent),
                              _seen=frozenset({scene}))
    points = mission_points(text)
    player, enemies, destinations = sp.classify(points)
    return text, reading, points, player, enemies, destinations


def bounds(boxes):
    """World x/z extent of every box the reader could reduce."""
    xs, zs = [], []
    for b in boxes:
        cx, _cy, cz = b.centre
        sx, _sy, sz = b.size
        xs += [cx - sx / 2.0, cx + sx / 2.0]
        zs += [cz - sz / 2.0, cz + sz / 2.0]
    if not xs:
        return None
    return (min(xs), min(zs), max(xs), max(zs))


# ----------------------------------------------------------------- the plate
def classify_cell(field, reach, x: float, z: float) -> str:
    i = field.index(x, z)
    if i is None:
        return "."
    if field.floor[i] is None:
        return "."
    if abs(field.floor[i] - field.reference) > sp.FIELD_BAND:
        return "~"
    if field.blocked[i]:
        return "#"
    return "+" if i in reach else "o"


def render(field, reach, box, marks: dict, cell: float) -> list[str]:
    """Plan view, north (−z) at the top, west (−x) on the left."""
    x0, z0, x1, z1 = box
    rows = []
    z = z0
    while z <= z1:
        row = []
        x = x0
        while x <= x1:
            ch = classify_cell(field, reach, x, z)
            for (mx, mz), sym in marks.items():
                if abs(mx - x) <= cell / 2.0 and abs(mz - z) <= cell / 2.0:
                    ch = sym
                    break
            row.append(ch)
            x += cell
        rows.append("".join(row))
        z += cell
    return rows


# -------------------------------------------------------------------- report
def report(scene: Path, cell: float, around=None) -> int:
    text, reading, points, player, enemies, destinations = survey(scene)

    print(f"\n  scene       {scene}")
    print(f"  boxes read  {len(reading.boxes)}   readable={reading.readable}")
    if reading.opaque:
        print(f"  OPAQUE      {len(reading.opaque)} collider(s) the reader could "
              f"not reduce to an axis-aligned box:")
        for name in reading.opaque:
            print(f"                {name}")
        print("              (these are absent from the field below -- a seal "
              "that one of them\n               would have bridged is a fault "
              "in the MODEL, not in the level)")
    if player is None:
        print("  no LT_PlayerSpawn -- nothing to flood-fill from")
        return 2
    if not reading.readable:
        print("  the scene's collision could not be read")
        return 2

    support = support_under(player, reading.boxes)
    if support is None:
        print(f"  the crew spawn {player} stands over nothing -- "
              f"check_ground_contact owns this")
        return 1
    print(f"  crew spawn  {player}  standing on {support.name} "
          f"(top {support.top:.3f})")

    field = sp.heightfield(reading.boxes, support.top)
    if field is None:
        print("  no field could be built over that support")
        return 1
    start = field.index(player[0], player[2])
    if start is None or not field.standable(start):
        print("  the crew spawn is not standable in this scene's own collision")
        return 1
    reach = sp.walk_distances(field, start)
    print(f"  field       cell {field.cell:g} m"
          + ("  COARSENED" if field.coarsened else "")
          + f"   reachable cells {len(reach)}")

    print("\n  destinations")
    stranded = 0
    for name in sorted(destinations):
        pt = destinations[name]
        i, why = sp._placement(field, pt, reach)
        where = f"({pt[0]:7.1f}, {pt[2]:7.1f})"
        if why:
            stranded += 1
            print(f"    [STRANDED] {name:<20} {where}  {why}")
        else:
            print(f"    [ok]       {name:<20} {where}  "
                  f"{reach[i]:.1f} m on foot")
    for name in sorted(enemies):
        pt = enemies[name]
        i, why = sp._placement(field, pt, reach)
        if why:
            stranded += 1
            print(f"    [STRANDED] {name:<20} ({pt[0]:7.1f}, {pt[2]:7.1f})  {why}")

    box = bounds(reading.boxes)
    if around is not None:
        # A window, for looking at a doorway. The whole-site view at 4 m per
        # character cannot show a 1.1 m door, and "there is no gap here" is
        # exactly the claim a coarse render is least entitled to make.
        ax, az, half = around
        box = (ax - half, az - half, ax + half, az + half)
    if box is None:
        print("\n  no boxes to draw")
        return 1 if stranded else 0

    marks = {(player[0], player[2]): "S"}
    for name, pt in destinations.items():
        _i, why = sp._placement(field, pt, reach)
        marks[(pt[0], pt[2])] = ("E" if why else "D")
    for name, pt in destinations.items():
        if name.startswith("LT_ObjectivePoint") or name == "Objective":
            marks[(pt[0], pt[2])] = "O"
    for pt in enemies.values():
        marks.setdefault((pt[0], pt[2]), "e")

    x0, z0, x1, z1 = box
    print(f"\n  plan view   x {x0:.0f} .. {x1:.0f}   z {z0:.0f} .. {z1:.0f}   "
          f"at {cell:g} m per character")
    print("              + reachable   o standable but SEALED   # solid   "
          "~ other storey   . nothing")
    print("              S crew   O objective   D reachable dest   "
          "E stranded dest   e enemy\n")
    for row in render(field, reach, box, marks, cell):
        print("    " + row)

    print()
    if stranded:
        print(f"  {stranded} point(s) the crew cannot walk to. Every `o` region "
              f"with no `+` touching it is\n  a seal the navmesh bake will "
              f"refuse too -- this field does not erode by agent\n  radius, so "
              f"it reports fewer walls than the bake will find, not more.")
    else:
        print("  every mission point is reachable on foot from the crew spawn")
    return 1 if stranded else 0


# ------------------------------------------------------------------ selftest
def _selftest() -> int:
    """A yard split by a wall, with and without a doorway.

    Proves the probe distinguishes a seal from a walk BEFORE it is trusted on a
    real site -- a probe that can only report `sealed` cannot tell you it would
    not also report it for open ground.
    """
    from packages.validation.ground_contact import Box
    floor = Box("floor", (0.0, -0.25, 0.0), (120.0, 0.5, 60.0))
    wall = Box("wall", (0.0, 1.5, 0.0), (1.0, 3.0, 60.0))
    gap = Box("wall_n", (0.0, 1.5, -18.0), (1.0, 3.0, 24.0))
    gap_s = Box("wall_s", (0.0, 1.5, 18.0), (1.0, 3.0, 24.0))
    spawn = (-40.0, 0.0, 0.0)
    far = (40.0, 0.0, 0.0)

    def reachable(boxes) -> bool:
        support = support_under(spawn, boxes)
        field = sp.heightfield(boxes, support.top)
        start = field.index(spawn[0], spawn[2])
        reach = sp.walk_distances(field, start)
        _i, why = sp._placement(field, far, reach)
        return why is None

    sealed = reachable([floor, wall])
    open_ = reachable([floor, gap, gap_s])
    print(f"[selftest] solid wall across the yard -> "
          f"{'REACHABLE' if sealed else 'sealed'}")
    print(f"[selftest] same wall with a 12 m doorway -> "
          f"{'reachable' if open_ else 'SEALED'}")
    bad = 0
    if sealed:
        print("[selftest] FAIL: a wall spanning the whole yard did not seal it. "
              "The flood fill is not seeing the wall, so nothing this probe "
              "reports about walls means anything.")
        bad = 1
    if not open_:
        print("[selftest] FAIL: a 12 m doorway read as sealed. The probe "
              "invents walls, which is the expensive direction -- it would "
              "blame the level for the model.")
        bad = 1
    if not bad:
        print("[selftest] seals what is sealed and walks what is open")
    return bad


def main(argv: list[str]) -> int:
    cell = float(argv[argv.index("--cell") + 1]) if "--cell" in argv else 4.0
    around = None
    if "--around" in argv:
        i = argv.index("--around")
        around = (float(argv[i + 1]), float(argv[i + 2]), float(argv[i + 3]))
    if "--selftest" in argv:
        return _selftest()
    args, skip = [], 0
    for i, a in enumerate(argv):
        if skip:
            skip -= 1
            continue
        if a == "--around":
            skip = 3
        elif a == "--cell":
            skip = 1
        elif not a.startswith("--"):
            args.append(a)
    if not args:
        print(__doc__.splitlines()[2].strip())
        print(__doc__.splitlines()[3].strip())
        print("    python probe_reach.py <scene> --around <x> <z> <half> "
              "--cell 0.5")
        return 2
    scene = Path(args[0])
    if not scene.is_file():
        print(f"not a file: {scene}")
        return 2
    return report(scene, cell, around)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
