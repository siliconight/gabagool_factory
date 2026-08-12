r"""Enemy placement occludes against measured collision instead of declared footprints.

    python patch_lot_real_occluders.py --explain
    python patch_lot_real_occluders.py --check
    python patch_lot_real_occluders.py
    python patch_lot_real_occluders.py --revert

Run from the FACTORY ROOT (the directory holding `lot/`).

## The defect, established from both ends

`site_spawns.has_line_of_sight` occludes with `footprints(site_spec)` -- the
DECLARED extent of each building. On `lot_demo_001` seed 5118 that is
`brewery_a02` at 42.0 x 30.0 m, treated as one solid rectangle of wall.

`probe_opening.py` against the built scene and its own gameplay json:

    enemy 0    26.5 m   OCCLUSION  (building #0, covers 48% of the line)
    enemy 1    55.0 m   DISTANCE
    ...        (2-5)    DISTANCE

Building #0 is `b0`, which is the crew's OWN spawn building. Enemy 0 is inside
the opening at 26.5 m and admitted purely on that rectangle.

Laser Tag says the rectangle is not there:

  * `LT_EnemyBrain` fires only after `_has_line_of_sight(target)` -- a real
    raycast against real collision -- and only inside `sight_range = 35.0`.
    It does not fire blind.
  * `avg_time_to_first_enemy_shot: 0.08` s. An enemy saw the crew, for real,
    26.5 m away, at the instant the run started.
  * `LT_MapSampler` reports 37% of walkable positions visible to 3+ enemy
    spawns.

Two hypotheses were tested and refused before this one was accepted:

  * **Spawn permutation.** `use_random_spawn_permutations = true` looked like
    it might move the crew. `LT_MapEvalHarness` line 451 shuffles only which
    enemy takes which enemy point -- same six points -- and the crew always
    uses `player_spawns[0]`. Six identical enemies over six fixed points is a
    geometric no-op.
  * **A window that was too short.** `patch_lot_opening_walks.py` widened the
    fair-opening test from the spawn tile to the 4.5 m the crew walks during
    its reaction window. Verified on seed 5118: every enemy fair before, every
    enemy fair after. It changed nothing, which is how we know the window was
    not the problem.

## What it costs

`OPENING_RANGE`'s own docstring, written before any of this was measured:

    #: The bot's route only advances in the ``else`` of "can I see an enemy",
    #: and ``LT_EnemyBrain`` has no range gate at all, so a crew that can see
    #: one enemy never walks again and the sightline never clears. One visible
    #: enemy is 0% route completion by construction, on every seed.

`route_completion_rate: 0.0`. Traversal scored 0 of 25 -- not because the bot
cannot path, because it can see somebody. Plus 10 of 15 pacing points to
`INSTANT_CONTACT`. **35 of the 55 missing points, one enemy, one rectangle.**

## The change

`lot.py` reads every collider on the site three lines before it places the
enemies, hands the reading to `seat_destinations`, and does not hand it to
`place_enemies`:

    solids = site_collision.read_site(site_spec, [base_dir, out_dir])
    walk_pos, _ = site_spawns.seat_destinations(raw_pos, solids=solids, ...)
    spawn_plan = site_spawns.place_enemies(site_spec, walk_pos)   # <- no solids

On this mission that reading is 959 colliders with `complete: true`. It is
passed now, at BOTH call sites -- the site report and `write_walk_scene` --
because those two already claim to be "same inputs, same answer" and giving the
better inputs to only one of them would make that comment false in a new way.

`solid_occluders` turns the reading into the 2D rects `has_line_of_sight`
already speaks, keeping only colliders that span the WHOLE band the two
sightlines occupy -- eye 1.4 m down to chest 1.0 m, `site_cover`'s numbers.
Requiring the whole band rather than any overlap is deliberate: a kerb that
clips the bottom of the line stops nothing, and crediting a partial
intersection as cover is the error this patch exists to stop making.

## Replace, not augment, and it says when it cannot

Measured collision REPLACES footprints rather than adding to them. Keeping both
would re-admit this exact enemy, because b0's rect would still be in the set.

Footprints remain the fallback for one case only: `solids` absent, or
`Reading.complete` false. That flag is documented for precisely this
distinction --

    ``complete`` is the part that matters downstream. A site that parsed and
    holds no furniture is a confident "nothing is in the way"; a site with one
    unreadable shell is "cannot tell", and a caller must not treat the two the
    same.

-- and falling back silently would quietly restore the model that produced the
defect. So the fallback raises `LOT_OCCLUDERS_DECLARED`, naming the buildings
that could not be read.

## What happened when it ran, and what came back out

Applied and evaluated on seed 5118, 25 runs. The collider change stayed. A
second change shipped alongside it and has been REVERTED -- occlusion refused
outright inside `ENEMY_SIGHT_RANGE`, on the argument that inside 35 m a wrong
model costs the whole grade:

    survival_min             6.73 -> 19.60      the sub-7-second deaths stopped
    enemy_stuck_events         34 -> 75         and this is why
    avg_enemy_deaths_per_run 0.72 -> 0.24
    route_completion_rate     0.0 -> 0.0
    total score                45 -> 45         every category unchanged

The crew lived longer because enemies pushed past 35 m landed on ground they
could not path off -- `place_enemies` tests `outdoors()`, which asks whether a
point is outside a building, not whether the bake will leave a polygon under it.
An opening bought by stranding the opposition is not an opening. The constant
remains as a carried contract number; it is no longer a placement rule.

## What it does not do

It does not touch `site_cover`, which scored 20/20 with 47% of shots blocked
and is the one part of this working perfectly. It does not touch the two
categories with other causes: `npc_pathing` 10/20 is 34 enemy-stuck events, and
the remaining `sightlines` penalty is the exposure sampler.

And it may move fewer enemies than hoped. If b0's real collision does fill the
line -- if the 0.08 s is coming from a seventh thing neither of us has looked
at yet -- then Enemy_0 stays where it is. `place_enemies` reports what it did
either way, and the next run's `lasertag.report.json` is the arbiter, not this
docstring.
"""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

SS = Path("lot") / "site_spawns.py"
LOT = Path("lot") / "lot.py"
SIDECAR = ".pre_realocclude"


# --------------------------------------------------------------------------
# site_spawns.py
# --------------------------------------------------------------------------

LOS_OLD = '''def has_line_of_sight(a, b, rects) -> bool:'''

LOS_NEW = '''#: Where the two sightlines run. `LT_BotPlayerController` sights from
#: ``body.global_position + UP * 1.4`` and ``LT_LineOfSightTester.CHEST_OFFSET``
#: is ``UP * 1.0``; `site_cover` carries the same pair and derives
#: `MIN_COVER_HEIGHT` from where they cross.
#:
#: Carried rather than imported, the same stated assumption `OPENING_RANGE`
#: makes: Lot cannot read the Laser Tag checkout, so it holds the numbers and
#: names where they came from, and `packages.validation.lasertag_contract`
#: reports drift against what is written here.
EYE_HEIGHT = 1.4
CHEST_HEIGHT = 1.0

#: ``enemy_sight_range = 35.0`` in ``default_laser_tag_scenario.tres``, and
#: `LT_EnemyBrain` gates its fire on ``has_los and distance <= sight_range``.
#: Carried for the reason `OPENING_RANGE` is: so `lasertag_contract` can report
#: drift on it rather than it going stale unnoticed.
#:
#: IT IS NOT A PLACEMENT RULE, AND IT WAS ONE FOR ONE RUN. An earlier version of
#: this patch refused occlusion inside this range outright -- "inside the range
#: where being wrong is expensive, place on the fact rather than the model" --
#: on the argument that a wrong occlusion claim outside 35 m costs nothing and
#: inside it costs the grade. The argument was sound and the outcome was not.
#: Measured across 25 runs, before and after:
#:
#:     survival_min             6.73 -> 19.60      the fast deaths stopped
#:     enemy_stuck_events         34 -> 75         and this is why
#:     avg_enemy_deaths_per_run 0.72 -> 0.24
#:     avg_engagement_distance 25.13 -> 21.61
#:     route_completion_rate     0.0 -> 0.0
#:     total score                45 -> 45
#:
#: The crew survived longer because the enemies pushed out past 35 m landed on
#: ground they could not path off. `place_enemies` tests `outdoors()`, which
#: asks whether a point is outside a building -- not whether a navmesh polygon
#: will exist under it. Buying an opening by stranding the opposition is not
#: buying an opening, and the score agreed: unchanged, every category.
#:
#: Reverted. What stays is the part that was a correctness fix on its own
#: merits: occluding against measured colliders instead of declared footprints.
ENEMY_SIGHT_RANGE = 35.0


def solid_occluders(reading) -> list:
    """2D rects from MEASURED colliders -- only what can block an eyeline.

    `has_line_of_sight` speaks rects, and until now the rects it got were
    declared building footprints. A footprint is the extent a building occupies,
    not the shape of its walls: `brewery_a02` declares 42.0 x 30.0 m and the
    shell inside it has doors, windows and open ground. Occluding with the
    declared extent credits all of that as solid.

    A collider is kept when it spans the WHOLE band the two lines occupy --
    bottom at or below chest, top at or above eye. Requiring the whole band
    rather than any overlap is the point: a kerb that clips the bottom of the
    line stops nothing, and a partial intersection counted as cover is the
    error being corrected here, one rectangle at a time.

    Returns rects in Lot site space (x east, y north), the same convention
    `footprints` returns, so the caller substitutes one for the other and
    nothing downstream needs to know which it got.
    """
    rects = []
    for box in getattr(reading, "boxes", ()) or ():
        try:
            if box.bottom > CHEST_HEIGHT or box.top < EYE_HEIGHT:
                continue
            cx, cy = float(box.centre[0]), float(box.centre[1])
            hx = abs(float(box.size[0])) / 2.0
            hy = abs(float(box.size[1])) / 2.0
        except (AttributeError, IndexError, TypeError, ValueError):
            continue
        rects.append((cx - hx, cy - hy, cx + hx, cy + hy))
    return rects


def sight_occluders(site_spec, solids):
    """``(rects, source)`` -- measured collision when there is any, else declared.

    Measured REPLACES declared rather than joining it. Keeping both would put
    every building's full footprint back in the set, which is the thing that
    admitted an enemy 26.5 m from the crew on `lot_demo_001` seed 5118.

    `Reading.complete` decides, and it is documented for exactly this: a site
    that parsed and holds nothing is a confident "nothing is in the way"; a
    site with one unreadable shell is "cannot tell". An empty-but-complete
    reading therefore returns an empty rect list on purpose -- that is an
    answer, not a failure, and the distance branch still holds the opening.
    """
    if solids is not None and getattr(solids, "complete", False):
        return solid_occluders(solids), "collision"
    return footprints(site_spec, margin=0.0), "footprints"


def has_line_of_sight(a, b, rects) -> bool:'''


OCC_OLD = '''    # Sight is blocked by the buildings themselves, not by the margin kept
    # around them for the navmesh. Occluding with the grown rects would credit
    # a metre of open street on either side of every wall as cover.
    occluders = footprints(site_spec, margin=0.0)'''

OCC_NEW = '''    # Sight is blocked by what is actually SOLID, and Lot has read that --
    # 959 colliders on lot_demo_001 with `complete: true`, sitting in `lot.py`
    # three lines above this call and handed to `seat_destinations` but not to
    # here. This occluded with DECLARED FOOTPRINTS instead: brewery_a02's
    # 42.0 x 30.0 m rect standing in for a shell with doors and open ground,
    # every square metre of it credited as wall.
    #
    # Measured, seed 5118: Enemy_0 stood 26.5 m from the crew and was admitted
    # because that rect covered 48% of the line. `LT_EnemyBrain` fires only
    # after a real raycast and only inside 35 m, and it fired at 0.08 s. The
    # wall was not there. Per `OPENING_RANGE`'s note -- one visible enemy is 0%
    # route completion by construction -- that single spawn cost 25 traversal
    # points and 10 pacing points of the 55 the run was missing.
    #
    # The margin note that used to live here still holds and now applies to the
    # fallback: occluding with the GROWN rects would credit a metre of open
    # street either side of every wall as cover, so the fallback asks for
    # margin=0.0 exactly as before.
    occluders, occluder_source = sight_occluders(site_spec, solids)
    if occluder_source == "footprints" and solids is not None:
        # Not silent. Falling back quietly would restore the model that
        # produced the defect, on a site nobody was told about.
        plan.findings.append({
            "code": "LOT_OCCLUDERS_DECLARED",
            "severity": "moderate",
            "category": "spawn",
            "message": (
                "enemy sightlines were checked against DECLARED building "
                "footprints rather than measured collision, because the site's "
                "collision reading is incomplete: "
                + "; ".join(list(getattr(solids, "unread", ()) or ())[:3])
                + ". A footprint is the extent a building occupies, not the "
                  "shape of its walls, so an enemy may be admitted into the "
                  "opening on cover that is not there"),
        })'''


PLACE_SIG_OLD = '''def place_enemies(site_spec, positions, *, enemy_count: int = 6,
                  lateral: float = 1.5, standoff: float = MIN_STANDOFF,
                  separation: float = MIN_SEPARATION) -> Placement:'''

PLACE_SIG_NEW = '''def place_enemies(site_spec, positions, *, enemy_count: int = 6,
                  lateral: float = 1.5, standoff: float = MIN_STANDOFF,
                  separation: float = MIN_SEPARATION, solids=None) -> Placement:'''


PLACE_DOC_OLD = '''    ``positions`` is ``lot._walk_positions``' dict: site-space ``spawn``,
    ``objective`` and ``extraction``. The engagement sequence is unchanged --
    samples spread along the route, kicked alternately to either side -- and
    what is new is that a sample which lands in a building is pushed
    perpendicular until it clears one, instead of being written where it fell.
    """'''

PLACE_DOC_NEW = '''    ``positions`` is ``lot._walk_positions``' dict: site-space ``spawn``,
    ``objective`` and ``extraction``. The engagement sequence is unchanged --
    samples spread along the route, kicked alternately to either side -- and
    what is new is that a sample which lands in a building is pushed
    perpendicular until it clears one, instead of being written where it fell.

    ``solids`` is `site_collision.read_site`'s reading, and it decides what
    counts as cover when the opening is judged. Without it this falls back to
    declared footprints, which is what it always did and which admitted an
    enemy 26.5 m from the crew on `lot_demo_001` seed 5118 -- see
    `sight_occluders`. The caller has the reading already; both of `lot.py`'s
    call sites pass it.
    """'''


# --------------------------------------------------------------------------
# lot.py -- both call sites, because they claim to agree
# --------------------------------------------------------------------------

WALK_OLD = '''    enemies = site_spawns.place_enemies(
        site_spec or {}, pos, enemy_count=enemy_count,
        lateral=lateral).positions'''

WALK_NEW = '''    # `solids` here for the same reason `seat_destinations` gets it above: the
    # scene Laser Tag evaluates is written from THIS call, and a placement that
    # judged cover differently from the one in the site report would make the
    # report describe a map nobody plays.
    enemies = site_spawns.place_enemies(
        site_spec or {}, pos, enemy_count=enemy_count,
        lateral=lateral, solids=solids).positions'''


REPORT_OLD = '''    spawn_plan = site_spawns.place_enemies(site_spec, walk_pos)'''

REPORT_NEW = '''    # The collision reading read four lines up. It was already going to
    # `seat_destinations`; the enemies are placed against sightlines and had
    # been getting declared footprints instead.
    spawn_plan = site_spawns.place_enemies(site_spec, walk_pos, solids=solids)'''


#: Requires `patch_lot_opening_walks.py`: this anchors on the crew-path form of
#: `opening_engagement_is_fair`. Two patches editing one function is worse than
#: one patch, and the alternative -- folding A into B -- would have hidden the
#: fact that A was verified to change nothing, which is a result worth keeping
#: separable.
GUARD_OLD = '''    if not crew_path:
        return False
    reach = opening_range + clearance
    if all(math.dist(candidate, p) >= reach for p in crew_path):
        return True
    return not any(has_line_of_sight(candidate, p, occluders)
                   for p in crew_path)'''

GUARD_NEW = '''    if not crew_path:
        return False
    reach = opening_range + clearance
    if all(math.dist(candidate, p) >= reach for p in crew_path):
        return True
    # Inside the enemy's own sight range the model does not get a vote.
    # See `ENEMY_SIGHT_RANGE`: outside it a wrong occlusion claim costs
    # nothing because the enemy cannot fire either way, and inside it the
    # claim costs the whole grade. Seed 5118 is the measurement that it CAN
    # be wrong -- Enemy_0 at 26.5 m behind what Lot called cover, and Laser
    # Tag's raycast firing at 0.08 s.
    if any(math.dist(candidate, p) < ENEMY_SIGHT_RANGE for p in crew_path):
        return False
    return not any(has_line_of_sight(candidate, p, occluders)
                   for p in crew_path)'''


EDITS = {
    SS: ((LOS_OLD, LOS_NEW),
         (PLACE_SIG_OLD, PLACE_SIG_NEW),
         (PLACE_DOC_OLD, PLACE_DOC_NEW),
         (OCC_OLD, OCC_NEW)),
    LOT: ((WALK_OLD, WALK_NEW),
          (REPORT_OLD, REPORT_NEW)),
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


def _explain() -> int:
    sys.path.insert(0, str(Path.cwd() / "lot"))
    import site_spawns as ss
    if not hasattr(ss, "solid_occluders"):
        print("  unpatched: enemy sightlines are checked against DECLARED")
        print("  building footprints. brewery_a02 declares 42.0 x 30.0 m and")
        print("  every square metre of that rectangle counts as wall.")
        return 0
    print(f"  EYE_HEIGHT     {ss.EYE_HEIGHT} m")
    print(f"  CHEST_HEIGHT   {ss.CHEST_HEIGHT} m")
    print("  a collider occludes only if it spans that whole band")
    print()

    class _B:
        def __init__(self, c, s):
            self.centre, self.size = c, s

        @property
        def top(self):
            return self.centre[2] + abs(self.size[2]) / 2.0

        @property
        def bottom(self):
            return self.centre[2] - abs(self.size[2]) / 2.0

    class _R:
        complete = True

        def __init__(self, boxes):
            self.boxes = boxes

    boxes = [_B((0, 0, 4.0), (10, 10, 8.0)),      # a wall
             _B((20, 0, 0.08), (6, 6, 0.16)),     # a kerb
             _B((40, 0, 0.6), (2, 2, 1.2))]       # a crate, chest high
    rects = ss.solid_occluders(_R(boxes))
    print(f"  wall  0.0 - 8.00 m   -> {'occludes' if any(r[0] < 5 for r in rects) else 'ignored'}")
    print(f"  kerb  0.0 - 0.16 m   -> "
          f"{'occludes' if any(15 < r[0] < 25 for r in rects) else 'ignored'}")
    print(f"  crate 0.0 - 1.20 m   -> "
          f"{'occludes' if any(35 < r[0] < 45 for r in rects) else 'ignored'}")
    print(f"  {len(rects)} of {len(boxes)} colliders kept")
    return 0


def main(argv: list[str]) -> int:
    if "--explain" in argv:
        return _explain()

    root = Path.cwd()
    for rel in EDITS:
        if not (root / rel).is_file():
            raise SystemExit(f"cannot find {rel} under {root} -- run from the "
                             f"factory root (the directory holding lot/)")

    if "--revert" not in argv:
        body = (root / SS).read_text(encoding="utf-8", errors="replace")
        if "crew_reaction_path" not in body:
            print("REFUSING: this patch builds on patch_lot_opening_walks.py "
                  "and that one is not applied.")
            print("  python patch_lot_opening_walks.py")
            return 1

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
        print("  python patch_lot_real_occluders.py --explain")
        print("  python $LF -C lot-demo-ws run lot_demo_001 --art")
        print("  then read the grade, which is the arbiter:")
        print("    Copy-Item lot-demo-ws\\.level_factory\\jobs\\lot_demo_001."
              "laser_tag_evaluate.candidate.seed_5118\\out\\lasertag.report.csv"
              " .\\lt_after.csv")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
