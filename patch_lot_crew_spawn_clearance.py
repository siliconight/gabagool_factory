r"""The crew spawn gets the wall margin every enemy already gets.

    python patch_lot_crew_spawn_clearance.py --check
    python patch_lot_crew_spawn_clearance.py
    python patch_lot_crew_spawn_clearance.py --verify
    python patch_lot_crew_spawn_clearance.py --revert

Run from the FACTORY ROOT (the directory holding `lot/`).

## The defect

`site_spawns.WALL_MARGIN` exists for exactly this, and says so:

    #: navmesh with a 0.4 m agent radius, which erodes the walkable surface by
    #: that much from every solid; a spawn inside the eroded band has a floor
    #: and no navmesh polygon, which is UNREACHABLE_SPAWN again by a narrower
    #: route.
    WALL_MARGIN = 1.0

`footprints()` grows every building rect by it, and `place_enemies` refuses any
enemy sample that is not `outdoors()` of those grown rects. **The crew spawn is
never tested against them.** It is written wherever `_walk_positions` resolved
it, and nothing asks whether an agent standing there will have a navmesh
polygon under it.

Measured 2026-08-09, `lot_demo_001` candidate 5017. The crew spawn sits at
site (67, 0). `strip_retail_a01` stands at (59, 0) at rot 90, so its footprint
runs x 51.85 .. 66.15 -- the spawn is **0.85 m** from its east wall, inside the
1.0 m band. Laser Tag's own run:

    [LT] Baked navmesh on Nav (1041 polygons, 34356 source vertices)
    [LT] run 1/3 ended: TIMEOUT (180.1s)      ... 3/3, none completed
    - Bot rarely completed the route (0% of runs).   [FAIL]
    - Player got stuck 132 time(s).                  [WARN]

All 132 stuck events are at ONE point: x 65, z 0 -- two metres from the spawn,
inside the building it is standing against. The bot never leaves the start. No
run wipes and no run arrives; every one burns the full 180 s clock, so the job
also blows its 900 s timeout and the level is never graded at all.

## The change

One new function, `site_spawns.clear_crew_spawn`, and two call sites in
`lot.py` wired to it. It reuses the machinery enemies already go through --
`footprints()`, `ground_rect()`, `outdoors()` -- and adds no new model: no
flood fill, no collision reading, no second opinion about walkability.

  * outside the grown rects already -> returns the positions unchanged;
  * inside one -> pushed to the nearest point that is `outdoors`, searched
    nearest-first on a ring so the spawn ends up on the street it was already
    beside rather than wherever a scan happened to start, with
    `LOT_CREW_SPAWN_PUSHED`;
  * nowhere within `MAX_PUSH` -> left alone with `LOT_CREW_SPAWN_WALLED`,
    because moving it 80 m would be a different mission.

## Scope, deliberately

**The crew spawn only.** An objective or an extraction inside a building is a
heist, not a defect -- `cr_garage`'s extraction is inside `cr_garage` on
purpose. Whether the crew can REACH an interior destination is a different
question, unanswered here, and the one `LT_SEAL_UNVERIFIED` reports.

## What it does not do

The findings are produced and both wired call sites drop them, exactly as
`seat_destinations`' findings are dropped at the same two sites -- the comment
there explains why (`assemble` reports the same call's findings, and a finding
raised twice reads as two problems). Surfacing this one the same way is a
follow-up, and the geometry is fixed either way. Stated rather than quietly
left, because a push nobody is told about is the shape of defect this repo
keeps finding.
"""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

SS = Path("lot") / "site_spawns.py"
LOT = Path("lot") / "lot.py"
SIDECAR = ".pre_crewclear"


SS_OLD = '''def place_enemies(site_spec, positions, *, enemy_count: int = 6,'''

SS_NEW = '''#: Directions tried at each radius when pushing the crew spawn clear. Sixteen
#: is fine enough that a 0.5 m ring never steps over a doorway-width gap, and
#: coarse enough that the whole search is a few hundred rect tests.
_RING_DIRECTIONS = 16


def _rings(max_push: float, step: float):
    """Offsets ordered by distance, nearest first, deterministic.

    Nearest-first for the reason `_offsets` gives: the crew should end up on
    the street it was already standing beside, not on whichever side of the
    block the search happened to scan first.
    """
    distance = step
    while distance <= max_push:
        for i in range(_RING_DIRECTIONS):
            angle = 2.0 * math.pi * i / _RING_DIRECTIONS
            yield (distance * math.cos(angle), distance * math.sin(angle))
        distance += step


def clear_crew_spawn(site_spec, positions, *, max_push: float = MAX_PUSH,
                     step: float = PUSH_STEP) -> tuple:
    """Move the crew spawn out of the band where a navmesh will not exist.

    `WALL_MARGIN` is documented for this and every enemy is already held to it:
    `footprints()` grows each building rect by it and `place_enemies` rejects
    any sample that is not `outdoors()` of the grown set. The crew spawn was
    never tested against the same rects -- it was written wherever
    `_walk_positions` resolved it.

    Measured 2026-08-09 on `lot_demo_001` candidate 5017: the crew spawn stood
    0.85 m from `strip_retail_a01`, inside the 1.0 m band. It had floor and no
    navmesh polygon, so Laser Tag's bot could not path off it -- 132 stuck
    events at one point across three runs, every run timing out at 180 s, 0%
    route completion, and the evaluation job blowing its own 900 s budget
    without ever producing a grade.

    THE CREW SPAWN ONLY. An objective or extraction inside a building is a
    heist. Whether the crew can reach one is a different question and is not
    answered here.

    Returns ``(positions, findings)``; ``positions`` is a new dict and the
    input is left alone.
    """
    spawn = positions.get("spawn")
    if spawn is None:
        return positions, []
    rects = footprints(site_spec)
    ground = ground_rect(site_spec)
    if ground is None and not rects:
        # Nothing known to place against. `place_enemies` says the same of the
        # same site in LOT_SPAWN_PLACEMENT_UNCHECKED; saying it twice for one
        # site description would read as two problems.
        return positions, []

    here = (float(spawn[0]), float(spawn[1]))
    if outdoors(here, ground, rects):
        return positions, []

    z = float(spawn[2]) if len(spawn) > 2 else GROUND_Z
    for dx, dy in _rings(max_push, step):
        candidate = (here[0] + dx, here[1] + dy)
        if not outdoors(candidate, ground, rects):
            continue
        moved = math.hypot(dx, dy)
        seated = dict(positions)
        seated["spawn"] = (candidate[0], candidate[1], z)
        return seated, [{
            "code": "LOT_CREW_SPAWN_PUSHED",
            "severity": "minor",
            "category": "spawn",
            "message": (
                f"the crew spawn stood within {WALL_MARGIN:g} m of a building "
                f"or the site edge, so it was moved {moved:.2f} m to the "
                f"nearest open ground. Godot erodes the navmesh by the agent "
                f"radius at every solid, so a spawn inside that band has a "
                f"floor and no polygon to path from: the bot wedges against "
                f"the wall it started beside and the run ends in TIMEOUT with "
                f"0% route completion rather than in a fight."),
        }]

    return positions, [{
        "code": "LOT_CREW_SPAWN_WALLED",
        "severity": "major",
        "category": "spawn",
        "message": (
            f"the crew spawn stands within {WALL_MARGIN:g} m of a building or "
            f"the site edge and no open ground exists within {max_push:g} m of "
            f"it, so Lot left it where it was. Moving it further would be a "
            f"different mission. Laser Tag's bot will have no navmesh polygon "
            f"under the crew and will report 0% route completion."),
    }]


def place_enemies(site_spec, positions, *, enemy_count: int = 6,'''


LOT_HOOKS_OLD = '''    pos = site_spawns.seat_destinations(
        pos, solids=solids, bounds=bounds)[0]
    route = [pos["spawn"], pos["objective"], pos["extraction"]]'''

LOT_HOOKS_NEW = '''    pos = site_spawns.seat_destinations(
        pos, solids=solids, bounds=bounds)[0]
    # And then off the wall it is standing against. Seating answers "is there
    # floor under this point"; this answers "will the bake leave a polygon on
    # it", which is a different question and the one the bot actually needs.
    pos = site_spawns.clear_crew_spawn(site_spec or {}, pos)[0]
    route = [pos["spawn"], pos["objective"], pos["extraction"]]'''

LOT_WALK_OLD = '''    pos = site_spawns.seat_destinations(
        raw, solids=solids, bounds=_destination_bounds(merged, raw))[0]
    _p = "" if portable else "res://"'''

LOT_WALK_NEW = '''    pos = site_spawns.seat_destinations(
        raw, solids=solids, bounds=_destination_bounds(merged, raw))[0]
    # Same push the hook nodes get, on the same inputs, so the walk scene and
    # the evaluated scene put the crew in the same place. Two answers for one
    # spawn is the defect the comment above this one is about.
    pos = site_spawns.clear_crew_spawn(site_spec or {}, pos)[0]
    _p = "" if portable else "res://"'''


EDITS = {
    SS: ((SS_OLD, SS_NEW),),
    LOT: ((LOT_HOOKS_OLD, LOT_HOOKS_NEW),
          (LOT_WALK_OLD, LOT_WALK_NEW)),
}

_CRLF = "\r\n"


def _find(body: str, anchor: str) -> tuple[str, int]:
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


def _verify(root: Path) -> int:
    """The real numbers from candidate 5017, through the patched function."""
    sys.path.insert(0, str(root / "lot"))
    import site_spawns

    if not hasattr(site_spawns, "clear_crew_spawn"):
        print("[verify] FAIL: clear_crew_spawn is not there -- apply first")
        return 1

    # strip_retail_a01 at (59, 0) rot 90, footprint 20.3 x 14.3 -> x 51.85..66.15
    spec = {"ground": {"size_x": 300.0, "size_y": 120.0},
            "buildings": [{"id": "b3", "at": [59.0, 0.0], "rot": 90,
                           "footprint": [20.3, 14.3]}]}
    before = {"spawn": (67.0, 0.0, 0.0), "objective": (-10.0, -27.0, 0.0),
              "extraction": (-88.0, -4.0, 0.0)}

    after, findings = site_spawns.clear_crew_spawn(spec, before)
    codes = [f["code"] for f in findings]
    moved = round(((after["spawn"][0] - 67.0) ** 2
                   + (after["spawn"][1] - 0.0) ** 2) ** 0.5, 2)
    rects = site_spawns.footprints(spec)
    ground = site_spawns.ground_rect(spec)
    clear = site_spawns.outdoors(after["spawn"][:2], ground, rects)

    print(f"[verify] spawn {before['spawn'][:2]} -> "
          f"{tuple(round(v, 2) for v in after['spawn'][:2])}  "
          f"moved {moved} m  findings {codes}")
    print(f"[verify] outdoors after the push: {clear}")

    bad = 0
    if not codes:
        print("[verify] FAIL: a spawn 0.85 m from a wall was left alone. The "
              "band WALL_MARGIN documents is exactly what this is for.")
        bad = 1
    if not clear:
        print("[verify] FAIL: the pushed spawn is still not outdoors.")
        bad = 1
    if after["objective"] != before["objective"] or \
            after["extraction"] != before["extraction"]:
        print("[verify] FAIL: a destination moved. This is the crew spawn "
              "only -- an objective inside a building is a heist.")
        bad = 1

    # And the control: a spawn already clear must not be touched at all.
    open_spawn = dict(before, spawn=(120.0, 0.0, 0.0))
    same, none_ = site_spawns.clear_crew_spawn(spec, open_spawn)
    if same["spawn"] != open_spawn["spawn"] or none_:
        print(f"[verify] FAIL: a spawn already on open ground was moved "
              f"{same['spawn']} / {[f['code'] for f in none_]}. A push that "
              f"fires on a clear spawn would move every mission ever built.")
        bad = 1
    else:
        print("[verify] a spawn already on open ground is left untouched")

    if not bad:
        print("[verify] pushes what needs pushing and nothing else")
    return bad


def main(argv: list[str]) -> int:
    root = Path.cwd()
    for rel in EDITS:
        if not (root / rel).is_file():
            raise SystemExit(f"cannot find {rel} under {root} -- run from the "
                             f"factory root (the directory holding lot/)")

    if "--verify" in argv:
        return _verify(root)

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
        print("  Verify:  python patch_lot_crew_spawn_clearance.py --verify")
        print("  Then:    re-run the mission -- lot_assemble re-runs, the crew")
        print("           spawn moves, and Laser Tag gets a level its bot can")
        print("           walk off the start line of.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
