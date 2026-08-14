r"""A crew of four gets four places to stand instead of one.

    python patch_lot_crew_ring.py --explain
    python patch_lot_crew_ring.py --check
    python patch_lot_crew_ring.py
    python patch_lot_crew_ring.py --verify
    python patch_lot_crew_ring.py --revert

Run from the FACTORY ROOT (the directory holding `lot/` and `level_factory/`).

## What happened

`patch_lf_mission_scenario.py` gave `lot_demo_001` a `crew_size` of 4 and the
evaluation went from 45/FAIL to **10/BROKEN**:

    scenario_name          mission_scenario.tres     the scenario patch works
    player_count           4
    time_to_first_contact  -1.00                     nobody ever fired
    shots_fired            0
    player_deaths          0     enemy_deaths  0
    player_survival_time   180.07                    the full clock
    end_reason             TIMEOUT
    player_stuck_events    116

Zero shots by either side, in every run. Nobody dies. Every run burns the whole
180 seconds. With `shots_fired == 0` the scorer zeroes sightlines, cover AND
pacing outright -- `_score_cover` returns 0 on the first line, `_score_sightlines`
raises `NO_ENGAGEMENT`, `_score_pacing` raises `NO_CONTACT` -- so 45 collapses to
10 and the only category left standing is npc_pathing.

## Why

`LT_MapEvalHarness.spawn_players`:

    var spawn := player_spawns[i % player_spawns.size()] ...
    pill.global_position = spawn.global_position

and `lot.py` writes exactly one hook:

    body = _hook("LT_PlayerSpawn", ".", pos["spawn"], 1.0)

**Four capsules at one coordinate.** They interpenetrate, the physics solver
cannot separate them, and none of them can path. 116 stuck events and no
movement at all.

## Laser Tag has always supported a crew

`LT_MapEvalHarness._walk`:

    if node_name.begins_with(LT_Const.HOOK_PLAYER_SPAWN):
        player_spawns.append(node)

**`begins_with`.** `LT_PlayerSpawn_1`, `LT_PlayerSpawn_2` and so on are
discovered with no change to Laser Tag at all, `_sort_by_name` orders them, and
`spawn_players` already cycles the list. The capability was there; Lot has only
ever written one node. Fifth instance of the session's pattern -- a seam cut on
one side and nothing threaded through it.

## The change

`site_spawns.crew_spawns` returns `count` standing positions, the first being
the mission spawn exactly as before. The rest are found on the same
nearest-first rings `clear_crew_spawn` already walks, and each must be
`outdoors()` of the buildings and `CREW_SPACING` clear of every crew position
already placed.

`CREW_SPACING` is 2.0 m and derived rather than picked: `LT_PlayerPill` is a
capsule, the navmesh is baked at a 0.4 m agent radius, and two pills inside one
agent diameter is the state that produced the timeout. Two metres is a clear
diameter plus the wall margin `WALL_MARGIN` already keeps, so a crew member
standing on a ring point has the same room a spawn is required to have.

`crew_size` reaches Lot through the SITE SPEC, which is the contract between the
two. `_write_site_spec` writes it; `_lasertag_hook_nodes` reads it. No new
parameter on a function that already receives the spec.

A crew of 1 emits exactly the node it emitted before, at the same position, so
every mission that has not asked for a crew is byte-identical.

## What it does not do

**`enemy_count` still does not reach Lot.** `_lasertag_hook_nodes` takes
`enemy_count=6` as a parameter DEFAULT and nothing passes the brief's value, so
a brief asking for four enemies still gets six hooks and the harness spawns four
over a spread designed for six. Same defect, same shape, one function away --
and it is a separate patch because it changes what `place_enemies` is asked for
rather than how many places the crew has to stand.

**It does not predict the grade.** Four crew that can move may still wipe, and
the map still owes 34 enemy-stuck events and 37% overexposure to other causes.
What this buys is that the run can start at all.
"""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

SS = Path("lot") / "site_spawns.py"
LOT = Path("lot") / "lot.py"
CMDS = Path("level_factory") / "apps" / "cli" / "commands" / "__init__.py"
SIDECAR = ".pre_crewring"


CREW_OLD = '''def clear_crew_spawn(site_spec, positions, *, max_push: float = MAX_PUSH,'''

CREW_NEW = '''#: How far apart two crew members have to stand.
#:
#: Derived, not picked. `LT_PlayerPill` is a capsule and Godot bakes this site's
#: navmesh at a 0.4 m agent radius; two pills inside one agent diameter is the
#: state that produced `lot_demo_001`'s 10/BROKEN -- four crew written to one
#: coordinate, interpenetrating, 116 stuck events, zero shots fired by either
#: side and every run timing out at the full 180 s.
#:
#: Two metres is a clear pill diameter plus the `WALL_MARGIN` a spawn is already
#: required to have, so a crew member on a ring point stands in the same room
#: the mission spawn is held to.
CREW_SPACING = 2.0


def crew_spawns(site_spec, spawn, count: int, *,
                spacing: float = CREW_SPACING,
                max_push: float = MAX_PUSH,
                step: float = PUSH_STEP) -> list:
    """``count`` places for the crew to stand, the first being ``spawn``.

    THE FIRST IS ALWAYS THE SPAWN, unmoved. `clear_crew_spawn` has already
    decided where the mission starts and re-deciding it here would be two
    answers for one position, which is the defect that function was written to
    end. This only adds places for the people who arrive with them.

    The rest are found on the same nearest-first rings `clear_crew_spawn`
    walks, and each has to be `outdoors()` of every building and ``spacing``
    clear of every crew position already placed. Nearest-first for the reason
    `_offsets` gives: the crew should end up on the street it starts on, not
    strung out across whichever side of the block the search scanned first.

    A ``count`` of 1 returns ``[spawn]`` -- the exact node Lot has always
    written, at the exact position -- so a mission that has not asked for a crew
    is byte-identical.

    Laser Tag needs no change to read these. `LT_MapEvalHarness._walk` matches
    player spawns with ``begins_with(LT_Const.HOOK_PLAYER_SPAWN)`` and
    `spawn_players` cycles the list it finds, so `LT_PlayerSpawn_1` and up are
    discovered by a harness that has supported a crew all along.
    """
    base = tuple(spawn)
    placed = [base]
    count = max(1, int(count))
    if count == 1:
        return placed

    ground = ground_rect(site_spec)
    rects = footprints(site_spec)
    z = base[2] if len(base) > 2 else GROUND_Z
    for _ in range(count - 1):
        chosen = None
        for dx, dy in _rings(max_push, step):
            candidate = (base[0] + dx, base[1] + dy)
            if math.dist(candidate, base[:2]) < spacing:
                continue
            if ground is not None and not outdoors(candidate, ground, rects):
                continue
            if any(math.dist(candidate, p[:2]) < spacing for p in placed):
                continue
            chosen = candidate
            break
        if chosen is None:
            # Nowhere to put them. Stacking a crew member on someone else is
            # exactly the failure this exists to prevent, so the crew comes back
            # short and the caller can say so, rather than shipping a scene that
            # times out with no shots fired.
            break
        placed.append((chosen[0], chosen[1], z))
    return placed


def clear_crew_spawn(site_spec, positions, *, max_push: float = MAX_PUSH,'''


HOOK_OLD = '''    body = _hook("LT_PlayerSpawn", ".", pos["spawn"], 1.0)'''

HOOK_NEW = '''    # ONE NODE PER CREW MEMBER. This wrote a single `LT_PlayerSpawn` and
    # `LT_MapEvalHarness.spawn_players` puts every crew member on
    # `player_spawns[i % size()]` -- so a crew of four landed four capsules on
    # one coordinate, interpenetrating, and `lot_demo_001` graded 10/BROKEN with
    # 116 stuck events and not one shot fired in 25 runs.
    #
    # The harness matches these with `begins_with`, so the suffixed names are
    # found with no change to Laser Tag. Index 0 keeps the bare name and the
    # position `clear_crew_spawn` chose: `_sort_by_name` puts it first, and it
    # is still the mission's spawn.
    crew = site_spawns.crew_spawns(
        site_spec or {}, pos["spawn"],
        int((site_spec or {}).get("crew_size", 1) or 1))
    body = []
    for i, member in enumerate(crew):
        body += _hook("LT_PlayerSpawn" if i == 0 else f"LT_PlayerSpawn_{i}",
                      ".", member, 1.0)'''


SPEC_OLD = '''        # Building ids Lot resolves into the walkable scene's spawn_pos /
        # objective_pos / extraction_pos.'''

SPEC_NEW = '''        # HOW MANY PEOPLE ARRIVE. Lot writes one `LT_PlayerSpawn` per crew
        # member from this, because Laser Tag drops every one of them on
        # `player_spawns[i % size()]` -- one hook and a crew of four is four
        # capsules inside each other, which graded 10/BROKEN with zero shots
        # fired. The spec is the contract between the brief and Lot, so the
        # number travels here rather than as a new function parameter.
        "crew_size": int(getattr(model, "crew_size", 1) or 1),
        # Building ids Lot resolves into the walkable scene's spawn_pos /
        # objective_pos / extraction_pos.'''


EDITS = {
    SS: ((CREW_OLD, CREW_NEW),),
    LOT: ((HOOK_OLD, HOOK_NEW),),
    CMDS: ((SPEC_OLD, SPEC_NEW),),
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


def _verify() -> int:
    """Real numbers: the seed 5118 plate, a crew of four, spacing checked."""
    import math
    sys.path.insert(0, str(Path.cwd() / "lot"))
    import site_spawns as ss

    if not hasattr(ss, "crew_spawns"):
        print("[verify] site_spawns has no crew_spawns -- apply first")
        return 1

    spec = {"name": "site", "ground": {"size_x": 260.0, "size_y": 268.0},
            "buildings": [
                {"id": "b0", "at": [-70, -86], "rot": 180, "footprint": [42, 30]},
                {"id": "b1", "at": [-6, -81], "rot": 180, "footprint": [44, 30]},
            ]}
    spawn = (-70.0, -69.0, 0.0)

    bad = 0
    one = ss.crew_spawns(spec, spawn, 1)
    if one != [tuple(spawn)]:
        print(f"[verify] FAIL a crew of one moved: {one}")
        bad = 1
    else:
        print("[verify] a crew of one is the same single position as before")

    crew = ss.crew_spawns(spec, spawn, 4)
    print(f"[verify] crew of 4 -> {len(crew)} position(s)")
    for i, m in enumerate(crew):
        print(f"    {'LT_PlayerSpawn' if i == 0 else f'LT_PlayerSpawn_{i}':<18}"
              f" ({m[0]:7.2f}, {m[1]:7.2f})"
              + ("   <- the mission spawn, unmoved" if i == 0 else
                 f"   {math.dist(m[:2], spawn[:2]):.2f} m out"))
    if len(crew) != 4:
        print(f"[verify] FAIL expected 4, got {len(crew)}")
        bad = 1
    if crew and tuple(crew[0]) != tuple(spawn):
        print("[verify] FAIL the mission spawn moved")
        bad = 1

    ground = ss.ground_rect(spec)
    rects = ss.footprints(spec)
    for i, a in enumerate(crew):
        if ground is not None and not ss.outdoors(a[:2], ground, rects):
            print(f"[verify] FAIL crew {i} is not outdoors")
            bad = 1
        for j, b in enumerate(crew):
            if j <= i:
                continue
            gap = math.dist(a[:2], b[:2])
            if gap < ss.CREW_SPACING - 1e-6:
                print(f"[verify] FAIL crew {i} and {j} are {gap:.2f} m apart, "
                      f"under CREW_SPACING {ss.CREW_SPACING}")
                bad = 1
    if not bad:
        print(f"[verify] every pair clears CREW_SPACING {ss.CREW_SPACING} m "
              f"and every member is on open ground")
    return bad


def _explain() -> int:
    sys.path.insert(0, str(Path.cwd() / "lot"))
    import site_spawns as ss
    if not hasattr(ss, "crew_spawns"):
        print("  unpatched: lot.py writes ONE LT_PlayerSpawn, and")
        print("  LT_MapEvalHarness.spawn_players puts every crew member on")
        print("  player_spawns[i % size()] -- so a crew of four is four")
        print("  capsules on one coordinate. Measured: 116 stuck events,")
        print("  0 shots fired in 25 runs, TIMEOUT, 10/BROKEN.")
        return 0
    print(f"  CREW_SPACING   {ss.CREW_SPACING} m")
    print(f"  WALL_MARGIN    {ss.WALL_MARGIN} m")
    print(f"  PUSH_STEP      {ss.PUSH_STEP} m   (ring resolution)")
    print()
    print("  Laser Tag discovers these with begins_with(HOOK_PLAYER_SPAWN),")
    print("  so LT_PlayerSpawn_1.. need no change on the Laser Tag side.")
    return 0


def main(argv: list[str]) -> int:
    if "--explain" in argv:
        return _explain()
    if "--verify" in argv:
        return _verify()

    root = Path.cwd()
    for rel in EDITS:
        if not (root / rel).is_file():
            raise SystemExit(f"cannot find {rel} under {root} -- run from the "
                             f"factory root")

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
        print("  python patch_lot_crew_ring.py --verify")
        print("  python $LF -C lot-demo-ws run lot_demo_001 --art")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
