r"""Roadmap 10, 12, 16: one bake setting, three items.

    python patch_roadmap_navmesh_root.py --check
    python patch_roadmap_navmesh_root.py
    python patch_roadmap_navmesh_root.py --selftest
    python patch_roadmap_navmesh_root.py --revert

Run from the FACTORY ROOT (the directory holding `factory.manifest.json`).

WHAT WAS FOUND, ON 2026-08-14, WITHOUT RUNNING ANYTHING.

Item 16 states its own next question conditionally: "If the offenders name
`stair0ramp_*`, the question moves to `geometry_parsed_geometry_type = 2`."

`navmesh_solid_probe.gd`'s header says the offenders DO name it -- swept with
the walker's own body at the height the walker actually stands,
`stair0ramp_-1` obstructs 39 of 41 samples across the 0.73 m, the first at the
walker's own position. That measurement was taken, written down in the probe's
docstring, and never reached this file.

So the condition is met, and the two facts it hands off to are on disk:

    lot/lot.py:1430, :1643      'geometry_parsed_geometry_type = 2',
    lot/dist/*/lot_site_walk.gd:35-37
        # geometry_parsed_geometry_type -- BOTH (default here) parses meshes
        #   AND PARSED_GEOMETRY_STATIC_COLLIDERS (the .glb ships -colonly
        #   bodies).
    geometry_collision_mask     no occurrence anywhere in lot, level_factory
                                or zoo

THE SYNTHESIS. The bake parses visual meshes AND every static collider, with
no mask. The stairs ship `-convcolonly`, and a CONVEX hull over a staircase is
a solid wedge whose outer face is 39.2 degrees -- under the 55 the bake
accepts. So it voxelises into walkable surface over geometry a body cannot
occupy, which is exactly what the probe swept.

The same sentence explains item 12: prop colliders feed the same unmasked
bake, so `cage_counter`, `vault_block` and `gaming_tables` bake walkable tops
by construction. Item 12 already named `NavigationMesh.geometry_collision_mask`
as the mechanism -- what is new is that the mask is not misconfigured, it is
ABSENT.

And item 10 from the other side: `nav_gate.gd` bakes
`PARSED_GEOMETRY_MESH_INSTANCES` while `lot` writes type 2 for the scenes that
ship. Two bakes, two different shapes. That is why its pass does not transfer.

WHY NARROWED AND NOT CLOSED. The structural facts are confirmed by reading:
type 2 is written, no mask exists, the hulls are convex, the probe swept a
body through solid. The CAUSAL step -- that the convex hull is what produced
that particular walkable polygon -- is inferred and has not been run. The
decisive experiment is named in each status line rather than assumed:

    rebake one failing site's navqa scene with
    geometry_parsed_geometry_type = 1, re-run its walktest, and see whether
    the walkers get through the stair.

AND TYPE 1 IS THE DIAGNOSTIC, NOT THE FIX, which the new section says out
loud. Dropping static colliders entirely loses real geometry: a wall shipping
as `-colonly` with no visual mesh disappears from the bake and you get navmesh
through walls, which is worse than navmesh through stairs. The fix is the mask
item 12 already specified, and it is a cross-repo change with a collision-layer
contract in the middle of it.

THIS PATCH ADDS PROSE AS WELL AS STAMPS. Three status lines carry the
narrowing, and a dated section above "What to do next" carries the argument,
because a finding that joins three items is longer than a status line should
be. The file already works this way -- "The scraps were the furniture" is the
same shape.
"""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

TARGET = "PIPELINE_ROADMAP.md"
SIDECAR = ".pre_navroot"

EDITS: list[tuple[str, str, str]] = [

    ("item 10",
     "*STATUS: OPEN 2026-08-12 -- unchanged*",
     "*STATUS: NARROWED 2026-08-14 -- quantified. `nav_gate.gd` bakes "
     "PARSED_GEOMETRY_MESH_INSTANCES; `lot.py:1430,1643` write "
     "`geometry_parsed_geometry_type = 2` for the scenes that ship. The two "
     "bakes voxelise different shapes, which is why the pass does not "
     "transfer. Same root as 12 and 16 -- see *One bake, three items* above*"),

    ("item 12",
     "*STATUS: OPEN 2026-08-12 -- candidate cause of the 1,179 "
     "player_stuck_events in SESSION_0811*",
     "*STATUS: NARROWED 2026-08-14 -- the mechanism this item named is not "
     "misconfigured, it is ABSENT: `geometry_collision_mask` has no "
     "occurrence anywhere in lot, level_factory or zoo, and the bake is type "
     "2, so every prop collider feeds it unmasked. Still the candidate cause "
     "of the 1,179 player_stuck_events in SESSION_0811*"),

    ("item 16",
     '*STATUS: OPEN 2026-08-12 -- unchanged; this file\'s own '
     '"biggest open question"*',
     "*STATUS: NARROWED 2026-08-14 -- this item's own condition is met. "
     "`navmesh_solid_probe.gd` swept the walker's body and found "
     "`stair0ramp_-1` obstructing 39 of 41 samples, so the offenders DO name "
     "stair0ramp_*, and the bake is `geometry_parsed_geometry_type = 2` with "
     "no collision mask. Decisive test named in *One bake, three items* "
     "above; not yet run*"),
]

#: Matched WITHOUT line endings on purpose. The first version anchored on
#: "\n## What to do next\n" after verifying the count with `read_text`, which
#: normalises CRLF to LF -- while `_apply` uses `decode`, which does not. This
#: file is mixed-EOL and that heading is CRLF, so the check said 1 and the
#: apply found 0. The heading text alone is unambiguous, and the surrounding
#: endings are read from the file rather than assumed.
HEADING = "## What to do next"

SECTION = """
### One bake, three items — 2026-08-14

Items 10, 12 and 16 are three readings of one setting.

`lot.py` writes `geometry_parsed_geometry_type = 2` into every walk scene it
emits (lines 1430 and 1643, and the value is in the shipped `.tscn` files).
`lot_site_walk.gd` says what that means in its own comment: *BOTH (default
here) parses meshes AND `PARSED_GEOMETRY_STATIC_COLLIDERS` (the .glb ships
`-colonly` bodies)*. And `geometry_collision_mask` — the property item 12
named as the fix — **does not appear anywhere in `lot`, `level_factory` or
`zoo`**. Not set wrongly. Not set.

So the navmesh bake consumes the visual meshes *and every static collider in
the scene*, unfiltered.

That one sentence produces all three symptoms:

* **The stairs (item 16).** They ship `-convcolonly`. A convex hull over a
  staircase is a solid wedge, and its outer face measures 39.2° — under the
  55° the bake accepts. So it voxelises into walkable surface lying over
  geometry a body cannot occupy. `navmesh_solid_probe.gd` swept the walker's
  own capsule at the height the walker actually stands and found
  `stair0ramp_-1` obstructing **39 of 41 samples across 0.73 m, the first at
  the walker's own position**. That measurement was taken, recorded in the
  probe's docstring, and never reached this file — which is its own finding.
* **The props (item 12).** `cage_counter`, `vault_block`, `gaming_tables`
  are static colliders in the same unmasked bake. Their tops bake walkable by
  construction, exactly as the item describes. The item was right about the
  mechanism and wrong only in assuming it was configured.
* **The gate (item 10).** `nav_gate.gd` bakes
  `PARSED_GEOMETRY_MESH_INSTANCES` — type 1 — against scenes that ship at
  type 2. Two bakes, two shapes, and a pass that cannot transfer because it is
  not measuring the same solid.

**The decisive test, which has NOT been run.** Rebake one failing site's navqa
scene with `geometry_parsed_geometry_type = 1` and re-run its walktest. If the
walkers get through the stair, the convex hull is confirmed as the source. If
they still stop, this reading is wrong and the blockage is something the
capsule sweep cannot see — the same fork item 16 already set out.

**Type 1 is the diagnostic, not the fix.** Dropping static colliders loses
real geometry: a wall that ships as `-colonly` with no visual mesh vanishes
from the bake, and navmesh through walls is worse than navmesh through stairs.
The fix is the mask item 12 specified — prop and stair-hull colliders onto
their own physics layer in Deli Counter, masked out of the bake in Lot — and
it stays a cross-repo change wanting an `agent_contract.json` entry rather
than two magic numbers.

**What is asserted here and what is not.** Asserted, by reading: type 2 is
written, no mask exists, the hulls are convex, and the probe swept a body
through solid. Inferred, and not yet measured: that the convex hull is what
produced that particular walkable polygon. That is why all three items move to
NARROWED and none to CLOSED.

"""

_CRLF = "\r\n"


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _apply(root: Path, *, check: bool) -> int:
    p = root / TARGET
    if not p.is_file():
        print(f"REFUSING: {TARGET} is not here")
        return 1
    raw = p.read_bytes()
    body = raw.decode("utf-8")

    if "### One bake, three items" in body:
        print("  already applied")
        return 0

    out = body
    for label, old, new in EDITS:
        if out.count(old) != 1:
            print(f"REFUSING: {label}'s status line occurs {out.count(old)} "
                  f"time(s), expected 1")
            return 1
        out = out.replace(old, new, 1)

    if out.count(HEADING) != 1:
        print(f"REFUSING: the 'What to do next' heading occurs "
              f"{out.count(HEADING)} time(s), expected 1")
        return 1
    idx = out.index(HEADING)
    eol = _CRLF if out[:idx].endswith(_CRLF) else "\n"
    section = SECTION.replace("\n", eol) if eol == _CRLF else SECTION
    section = section[len(eol):] if section.startswith(eol) else section
    out = out[:idx] + section + out[idx:]
    #: The status-line swaps are EOL-neutral; this insert is not, and should
    #: not be. It adds exactly the endings it brings, in the ending the
    #: surrounding text already uses. Asserting "unchanged" here would have
    #: been a guard that only permits the edit it was written for.
    added_crlf = section.count(_CRLF)

    before_crlf = raw.count(_CRLF.encode())
    data = out.encode("utf-8")
    got, want = data.count(_CRLF.encode()), before_crlf + added_crlf
    if got != want:
        print(f"REFUSING: CRLF count is {got:,}, expected {want:,} "
              f"({before_crlf:,} before + {added_crlf} inserted) -- the edit "
              f"changed line endings it should not have touched")
        return 1

    if check:
        print(f"  would patch  {TARGET}  {len(raw):,} -> {len(data):,} bytes "
              f"({len(data) - len(raw):+,})")
        return 0
    side = p.with_suffix(p.suffix + SIDECAR)
    if not side.is_file():
        side.write_bytes(raw)
    p.write_bytes(data)
    print(f"  patched      {TARGET}  {len(raw):,} -> {len(data):,} bytes "
          f"({len(data) - len(raw):+,})  sha256 {_sha(data)[:16]}")
    return 0


def selftest(root: Path) -> int:
    bad = 0

    def check(label: str, ok: bool) -> None:
        nonlocal bad
        bad += 0 if ok else 1
        print(f"  {'ok  ' if ok else 'FAIL'} {label}")

    t = (root / TARGET).read_text(encoding="utf-8")
    flat = " ".join(t.split())

    for label, old, new in EDITS:
        check(f"{label} reads NARROWED", new in t)
        check(f"{label}'s old OPEN stamp is gone", old not in t)

    check("the section exists, dated", "### One bake, three items — 2026-08-14"
          in t)
    check("it sits above 'What to do next'",
          t.index("### One bake, three items") < t.index("## What to do next"))
    check("it names the two lot.py lines", "1430 and 1643" in flat)
    check("it records the probe's measurement",
          "39 of 41 samples" in flat)
    check("it states the mask is absent, not wrong",
          "Not set wrongly. Not set." in flat)
    check("it names the decisive test and says it has not been run",
          "which has NOT been run" in flat
          and "geometry_parsed_geometry_type = 1" in flat)
    check("it separates type 1 the diagnostic from the mask the fix",
          "Type 1 is the diagnostic, not the fix" in flat)
    check("it separates asserted from inferred",
          "Asserted, by reading" in flat and "Inferred, and not yet measured"
          in flat)

    # The arguments of all three items must be untouched.
    check("item 16's argument survives",
          "The bake and the colliders disagree about the same staircase"
          in flat)
    check("item 12's argument survives",
          "NavigationMesh.geometry_collision_mask" in flat
          and "some props *should* be mountable" in flat)
    check("item 10's argument survives",
          "the importer never runs" in flat)
    check("item 8 stays closed",
          "STATUS: CLOSED 2026-08-14 -- shipped as Lot 0.28.0" in t)

    if "| 16 | **OPEN**" in t:
        print("  note  the generated table is stale -- run "
              "`python tools\\roadmap_status.py --write`")

    print()
    print("  three items, one root, and the untested step is labelled"
          if not bad else f"  {bad} FAILURE(S)")
    return 1 if bad else 0


def main(argv: list[str]) -> int:
    root = Path.cwd()
    if not (root / "factory.manifest.json").is_file():
        raise SystemExit("run this from the factory root")

    if "--selftest" in argv:
        return selftest(root)

    if "--revert" in argv:
        p = root / TARGET
        side = p.with_suffix(p.suffix + SIDECAR)
        if not side.is_file():
            print(f"  no sidecar for {TARGET}")
            return 1
        p.write_bytes(side.read_bytes())
        print(f"  reverted     {TARGET}")
        return 0

    check = "--check" in argv
    rc = _apply(root, check=check)
    if not rc and not check:
        print()
        print("  python patches\\patch_roadmap_navmesh_root.py --selftest")
        print("  python tools\\roadmap_status.py --write")
        print("  python tools\\roadmap_status.py --check")
        print()
        print("  then the experiment the section names -- rebake one failing")
        print("  site at geometry_parsed_geometry_type = 1 and re-walk it.")
    return rc


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
