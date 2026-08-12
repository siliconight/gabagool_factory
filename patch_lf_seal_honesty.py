r"""A seal this reader inferred is not a seal it may refuse a build on.

    python patch_lf_seal_honesty.py --check
    python patch_lf_seal_honesty.py
    python patch_lf_seal_honesty.py --revert

## The defect

`spawn_placement` states its own bias, and the statement is false:

    "it is deliberately *optimistic* -- it does not erode by agent radius, so a
     gap a 0.4 m agent cannot squeeze through still reads as open ... this
     module under-reports rather than inventing a wall, and everything it does
     report is something the bake will refuse too."

It invents a wall at every doorway on the site. `ground_contact._instanced`
builds its boxes from `glb_collision.collision_solids`, which gives each
collision MESH's bounding box -- and a mesh is exactly where a doorway lives.
An exterior wall with openings cut in it reduces to a solid box across every
one of them.

Measured 2026-08-09 on `lot_demo_001` candidate 5017. `cr_garage` declares
seventeen openings, seven of them ground-level entries, including two 5 m
garage doors. Rendered from this reader's own boxes at 0.5 m per cell it is an
unbroken ring: no gap on any wall. The extraction hook stands on clear floor
2.2 m inside it, `_placement` returns "sealed off from the crew spawn", and the
build is refused with `JOB_PREFLIGHT_REFUSED` for a level that is fine.

No mission point inside ANY building can be reachable under this model. Sites
pass only because Lot usually places markers outdoors.

## What this changes

Boxes learn whether they were measured or inferred, and a seal that depends on
inferred geometry stops being a refusal.

  * `ground_contact.Box` gains `approximate`. True for a box that is the
    bounding box of a collision mesh; False for a `BoxShape3D`, which is
    actually a box. Carried through sub-scene instancing.
  * `spawn_placement._optimistic_reach` floods a second time with the inferred
    WALLS set aside -- every measured box kept, and an inferred box kept only
    where its top is within a step of the mission's own storey, which is a
    floor or a kerb rather than a wall. A destination unreachable in BOTH
    fields is genuinely sealed and still gates. One reachable in the second is
    sealed only by geometry this reader had to infer, and becomes an ADVISORY
    under `LT_SEAL_UNVERIFIED`.

    The height rule is what the first draft of this patch got wrong, and the
    test caught it: setting a wall's BLOCKING aside while keeping its floor
    leaves a 3 m ledge that is standable and unclimbable, so the flood fill
    still cannot cross and the counterfactual answers the same as the original.
    A wall has to leave the field, not soften.

The other four `_placement` verdicts are untouched and still gate: outside the
collision, over a gap, on another storey, inside solid geometry. None of them
depends on being able to see a doorway.

## What it does NOT do

It does not make the model see doorways. That is occupancy from triangles
rather than bounding boxes -- correct, and a much larger change. This patch
makes the module honest about what it cannot see; it does not give it sight.

An advisory is not nothing: the finding still reaches `lf validate` with its
own code, so a genuinely sealed interior is still reported. It just no longer
stops the build on evidence the reader admits it does not have.
"""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

GC = Path("level_factory") / "packages" / "validation" / "ground_contact.py"
SP = Path("level_factory") / "packages" / "validation" / "spawn_placement.py"
SIDECAR = ".pre_sealhonesty"


# --------------------------------------------------------------- ground_contact
GC_BOX_OLD = '''@dataclass(frozen=True)
class Box:
    """An axis-aligned box collider, positioned in scene-root space."""

    name: str
    centre: Vec3
    size: Vec3
'''

GC_BOX_NEW = '''@dataclass(frozen=True)
class Box:
    """An axis-aligned box collider, positioned in scene-root space.

    ``approximate`` marks a box that is the BOUNDING BOX of a collision mesh
    rather than a shape that is genuinely a box. A wall mesh with doorways cut
    in it reduces to a solid box across every opening, so an approximate box
    can seal a building this reader has no way to see into.

    Measured 2026-08-09: `cr_garage` declares seven ground-level entries,
    including two 5 m garage doors, and its collision read as an unbroken ring
    at 0.5 m cells. Under this model no mission point inside any building can
    be reachable.

    Nothing in this module treats the two kinds differently. The flag exists so
    a caller deciding whether to REFUSE A BUILD can tell a wall it measured
    from a wall it inferred -- see `spawn_placement._optimistic_reach`.
    """

    name: str
    centre: Vec3
    size: Vec3
    approximate: bool = False
'''

GC_GLB_OLD = '''        placed = []
        for solid in reading.solids:
            centre, size = _placed(at, solid.centre, solid.size)
            placed.append(Box(f"{label}:{solid.name}", centre, size))
        return Reading(tuple(placed), ())'''

GC_GLB_NEW = '''        placed = []
        for solid in reading.solids:
            centre, size = _placed(at, solid.centre, solid.size)
            # APPROXIMATE by construction: `collision_solids` reports each
            # collision MESH's bounding box, and a mesh is where the doorways
            # are. See `Box`.
            placed.append(Box(f"{label}:{solid.name}", centre, size,
                              approximate=True))
        return Reading(tuple(placed), ())'''

GC_TSCN_OLD = '''    moved = []
    for box in sub.boxes:
        centre, size = _placed(at, box.centre, box.size)
        moved.append(Box(f"{name}:{box.name}", centre, size))
    return Reading(tuple(moved), tuple(f"{name}:{o}" for o in sub.opaque))'''

GC_TSCN_NEW = '''    moved = []
    for box in sub.boxes:
        centre, size = _placed(at, box.centre, box.size)
        # The flag rides through the instance transform with the box: geometry
        # inferred inside the sub-scene is still inferred out here.
        moved.append(Box(f"{name}:{box.name}", centre, size,
                         approximate=box.approximate))
    return Reading(tuple(moved), tuple(f"{name}:{o}" for o in sub.opaque))'''


# -------------------------------------------------------------- spawn_placement
SP_CODES_OLD = '''CODE_STANDOFF = "LT_OPENING_STANDOFF"
CODE_FLOATING = "LT_MARKER_OFF_FLOOR"'''

SP_CODES_NEW = '''CODE_STANDOFF = "LT_OPENING_STANDOFF"
CODE_FLOATING = "LT_MARKER_OFF_FLOOR"

#: A seal that exists only in geometry this reader had to infer. Advisory for
#: the reason the others are: the claim cannot be stood behind, and a refusal
#: this module cannot defend is worse than a finding nobody acts on.
CODE_UNVERIFIED_SEAL = "LT_SEAL_UNVERIFIED"

#: `_placement`'s verdict for a cell the flood fill never reached. Named
#: because two functions now have to agree on it, and a sentence duplicated
#: across two call sites is a sentence that drifts.
_SEAL = "sealed off from the crew spawn"'''

SP_PLACE_OLD = '''    if i not in reach:
        return i, "sealed off from the crew spawn"'''

SP_PLACE_NEW = '''    if i not in reach:
        return i, _SEAL'''

SP_STRAND_OLD = '''def _strand(field: Field, reach: dict, points: dict) -> dict:
    stranded = {}
    for name, point in points.items():
        _, why = _placement(field, point, reach)
        if why:
            stranded[name] = why
    return stranded'''

SP_STRAND_NEW = '''def _strand(field: Field, reach: dict, points: dict) -> dict:
    stranded = {}
    for name, point in points.items():
        _, why = _placement(field, point, reach)
        if why:
            stranded[name] = why
    return stranded


def _optimistic_reach(field: Field, reading: Reading, player: Vec3):
    """The same flood fill, with the INFERRED walls set aside.

    `ground_contact` builds one box per collision MESH, taking its bounding
    box, and a doorway lives in a mesh -- so an exterior wall with openings cut
    in it arrives here as a solid box across every one of them. Measured
    2026-08-09, `cr_garage` declares seven ground-level entries and reads as an
    unbroken ring; under that model no point inside any building is reachable,
    ever.

    So this asks the counterfactual the module's docstring already promises:
    what would be reachable if the walls this reader had to INFER were not
    there? A point unreachable in both fields is sealed by geometry that was
    measured, and still gates. A point reachable only here is sealed by
    something this reader cannot see through, and refusing a build on that is
    refusing it on the reader's own blind spot.

    WHICH boxes leave is the whole care in this function. Every measured box
    stays. An inferred box stays only where its top is within a step of the
    mission's own storey -- an interior floor, a kerb, a threshold. An inferred
    box standing taller than that is the wall whose doorway could not be seen,
    and it leaves the field entirely.

    It has to LEAVE, not merely stop blocking. The first version of this kept
    each wall's floor contribution so the interior would not read as a hole,
    and a 3 m wall top is standable, unclimbable, and still uncrossable: the
    counterfactual answered exactly as the original did and the whole check was
    inert. The interior floor is a separate box and survives on its own.

    Returns ``(field, reach)`` or ``None`` when there is nothing to compare --
    no inferred walls, or no standable start once they are gone.
    """
    ceiling = field.reference + AGENT_CLIMB
    kept = [box for box in reading.boxes
            if not getattr(box, "approximate", False) or box.top <= ceiling]
    if len(kept) == len(reading.boxes):
        return None
    loose = heightfield(kept, field.reference, cell=field.cell)
    if loose is None:
        return None
    start = loose.index(player[0], player[2])
    if start is None or not loose.standable(start):
        return None
    return loose, walk_distances(loose, start)


def _split_seals(stranded: dict, points: dict, loose) -> tuple[dict, dict]:
    """``(verified, unverified)`` -- seals this reader can stand behind, and not.

    Only the seal verdict is ever moved. A point over a gap, on another storey
    or inside solid geometry is refused on evidence a doorway could not change,
    and those keep gating exactly as before.
    """
    if loose is None:
        return stranded, {}
    lfield, lreach = loose
    verified, unverified = {}, {}
    for name, why in stranded.items():
        if why == _SEAL:
            _i, still = _placement(lfield, points[name], lreach)
            if still is None:
                unverified[name] = why
                continue
        verified[name] = why
    return verified, unverified


def _unverified_findings(kind: str, stranded: dict, total: int) -> list[str]:
    if not stranded:
        return []
    return [
        f"{len(stranded)} of {total} {kind} sit(s) where this reader's own "
        f"collision has no route from the crew spawn ({_detail(stranded)}), "
        f"but every wall between is a collision MESH reduced to its bounding "
        f"box -- doorways included. With those walls set aside the point is "
        f"reachable, so the seal is this reader's blind spot rather than a "
        f"fact about the level, and it is reported instead of refused. If "
        f"Laser Tag comes back with TRAVERSAL at 0%, the seal was real"
    ]'''

SP_UNREACH_OLD = '''def _unreachable(field: Field, reach: dict, enemies: dict, destinations: dict,
                 reading: Reading) -> list[str]:'''

SP_UNREACH_NEW = '''def _unreachable(field: Field, reach: dict, enemies: dict, destinations: dict,
                 reading: Reading, loose=None) -> list[str]:'''

SP_UNREACH_BODY_OLD = '''    problems: list[str] = []
    caveat = _caveat(field, reading)

    stranded = _strand(field, reach, enemies)
    if stranded:
        problems.append(
            f"{len(stranded)} of {len(enemies)} enemy spawn(s) cannot be walked "
            f"to from the player spawn: {_detail(stranded)}{caveat}; Laser Tag "
            f"refuses the map with UNREACHABLE_SPAWN and completes zero runs")

    stranded = _strand(field, reach, destinations)
    if stranded:
        problems.append(
            f"{len(stranded)} of {len(destinations)} mission destination(s) "
            f"cannot be walked to from the player spawn: {_detail(stranded)}"
            f"{caveat}; the bot cannot finish the route, which Laser Tag "
            f"reports as TRAVERSAL with 0% completion")
    return problems'''

SP_UNREACH_BODY_NEW = '''    problems: list[str] = []
    caveat = _caveat(field, reading)

    stranded, _unverified = _split_seals(
        _strand(field, reach, enemies), enemies, loose)
    if stranded:
        problems.append(
            f"{len(stranded)} of {len(enemies)} enemy spawn(s) cannot be walked "
            f"to from the player spawn: {_detail(stranded)}{caveat}; Laser Tag "
            f"refuses the map with UNREACHABLE_SPAWN and completes zero runs")

    stranded, _unverified = _split_seals(
        _strand(field, reach, destinations), destinations, loose)
    if stranded:
        problems.append(
            f"{len(stranded)} of {len(destinations)} mission destination(s) "
            f"cannot be walked to from the player spawn: {_detail(stranded)}"
            f"{caveat}; the bot cannot finish the route, which Laser Tag "
            f"reports as TRAVERSAL with 0% completion")
    return problems'''

SP_CHECK_OLD = '''    return _unreachable(field, reach, enemies, destinations, reading)'''

SP_CHECK_NEW = '''    return _unreachable(field, reach, enemies, destinations, reading,
                        _optimistic_reach(field, reading, player))'''

SP_ADVISE_OLD = '''    return ([(CODE_STANDOFF, m)
             for m in _standoff(field, reach, enemies, opening_range)]
            + [(CODE_FLOATING, m)
               for m in _floating(field, player, enemies, destinations)])'''

SP_ADVISE_NEW = '''    loose = _optimistic_reach(field, reading, player)
    _v, unverified_enemies = _split_seals(
        _strand(field, reach, enemies), enemies, loose)
    _v, unverified_dests = _split_seals(
        _strand(field, reach, destinations), destinations, loose)
    return ([(CODE_STANDOFF, m)
             for m in _standoff(field, reach, enemies, opening_range)]
            + [(CODE_FLOATING, m)
               for m in _floating(field, player, enemies, destinations)]
            + [(CODE_UNVERIFIED_SEAL, m)
               for m in _unverified_findings("enemy spawn",
                                             unverified_enemies, len(enemies))]
            + [(CODE_UNVERIFIED_SEAL, m)
               for m in _unverified_findings("mission destination",
                                             unverified_dests,
                                             len(destinations))])'''


EDITS = {
    GC: ((GC_BOX_OLD, GC_BOX_NEW),
         (GC_GLB_OLD, GC_GLB_NEW),
         (GC_TSCN_OLD, GC_TSCN_NEW)),
    SP: ((SP_CODES_OLD, SP_CODES_NEW),
         (SP_PLACE_OLD, SP_PLACE_NEW),
         (SP_STRAND_OLD, SP_STRAND_NEW),
         (SP_UNREACH_OLD, SP_UNREACH_NEW),
         (SP_UNREACH_BODY_OLD, SP_UNREACH_BODY_NEW),
         (SP_CHECK_OLD, SP_CHECK_NEW),
         (SP_ADVISE_OLD, SP_ADVISE_NEW)),
}

_EPS = "\r\n"


def _find(body: str, anchor: str) -> tuple[str, int]:
    for candidate in (anchor, anchor.replace("\n", _EPS)):
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

    done = sum(1 for _old, new in edits if _find(body, new)[1] == 1)
    if done == len(edits):
        print(f"  already applied  {path.name}")
        return 0
    if done:
        print(f"REFUSING: {path.name} has {done} of {len(edits)} edits already "
              f"present. A half-applied file is not a state this patch can "
              f"reason about.")
        return 1

    out = body
    for old, new in edits:
        anchor, count = _find(out, old)
        if count != 1:
            print(f"REFUSING: {path.name} -- expected 1 occurrence of an "
                  f"anchor, found {count}.")
            print(f"  anchor starts: {old.splitlines()[0].strip()!r}")
            return 1
        out = out.replace(anchor,
                          new.replace("\n", _EPS) if _EPS in anchor else new, 1)

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


def main(argv: list[str]) -> int:
    root = Path.cwd()
    for rel in EDITS:
        if not (root / rel).is_file():
            raise SystemExit(f"cannot find {rel} under {root} -- run from the "
                             f"factory root")

    if "--revert" in argv:
        bad = 0
        for rel in EDITS:
            path, side = root / rel, (root / rel).with_suffix(
                (root / rel).suffix + SIDECAR)
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
        print("  Verify:  cd level_factory && python -m pytest tests\\unit")
        print("  Then:    python probe_reach.py <site_walk.tscn>")
        print("           the seal should now report as an advisory, and the "
              "run should plan")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
