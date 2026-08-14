r"""Roadmap item 16: CLOSED, and my own narrowing of it retracted.

    python patch_roadmap_item16_closed.py --check
    python patch_roadmap_item16_closed.py
    python patch_roadmap_item16_closed.py --selftest
    python patch_roadmap_item16_closed.py --revert

Run from the FACTORY ROOT. Run it AFTER patch_roadmap_navmesh_root.py, whose
section this rewrites.

WHAT HAPPENED. Earlier on 2026-08-14 I narrowed items 10, 12 and 16 to one
root cause -- `geometry_parsed_geometry_type = 2` with no
`geometry_collision_mask` -- and wrote a section saying so. The reasoning for
16 was: the stairs ship `-convcolonly`, a convex hull over a staircase is a
solid wedge at 39.2 degrees, so it bakes walkable over solid, and
`navmesh_solid_probe.gd` had swept a body through `stair0ramp_-1` at 39 of 41
samples.

Then the library sweep ran: **20 sites, 3,481 s, zero stuck walkers and zero
barrier resolutions on every one of them.** The three sites that defined item
16 -- central_vault, walkup_siege, ref_pvp -- all walk.

And `lot`'s own CHANGELOG had said why since 2026-08-02:

    ## [0.40.0] - the walker could not climb a legal stair

    ... walker bot_1 STUCK at (35.8, -2.3, -14.9) ... touching:
    stair0ramp_-1, slab_col_-1 ... 39.2 degrees ... A ramp that is legal by
    every number in agent_contract.json, and a physical capsule that cannot
    climb it. THAT IS THIS TOOL, NOT THE SITE.

    Two causes, both in `_drive`: gravity was applied every frame regardless
    of `is_on_floor()` ... the step-up probe was a single 0.5 m lift.

Same coordinate, same collider, same angle, same three sites. Item 16 was a
walker locomotion defect, fixed in Lot 0.40.0, and the sweep confirms it
empirically two weeks later.

WHY THE PROBE DID NOT CONTRADICT THAT. `navmesh_solid_probe.gd` swept the
walker's capsule from the walker's own stuck position and found the ramp
obstructing. That is what being pinned into the ramp-floor junction LOOKS
like. The probe measured the consequence of the locomotion bug and I read it
as an independent bake defect, because I came to it looking for one.

WHAT SURVIVES OF THE NARROWING. The facts about the bake are still facts:
`lot.py:1430,1643` write type 2, and `geometry_collision_mask` appears nowhere
in lot, level_factory or zoo. Prop colliders really do feed the bake unmasked,
which really is item 12's mechanism, and `nav_gate.gd` really does bake type 1
against scenes that ship at type 2, which really is item 10. Those two stay
NARROWED and stay joined. Item 16 is removed from that group and closed.

WHY THIS IS A SEPARATE PATCH RATHER THAN AN EDIT TO THE LAST ONE. The wrong
version is already committed and pushed. Rewriting it in place would leave no
trace that the roadmap spent an afternoon believing the stairs were a bake
problem, and the reason it believed that -- an instrument measuring a
consequence -- is worth more than the tidiness.

WHAT IS STILL OPEN ON THAT SWEEP. `ref_pvp` comes back BLOCKED, but its
walkers finished with 15/15 legs and 0 stuck. The finding is
`LOT_DESTINATION_ABOVE_FLOOR`: an objective marker 3.60 m above the site
ground plane, too tall to read as furniture, left where the marker put it.
That is item 9's residual gap -- Lot still cannot answer "is this anchor over
anything?" offline -- and not item 16.
"""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

TARGET = "PIPELINE_ROADMAP.md"
SIDECAR = ".pre_item16closed"

OLD_16 = ("*STATUS: NARROWED 2026-08-14 -- this item's own condition is met. "
          "`navmesh_solid_probe.gd` swept the walker's body and found "
          "`stair0ramp_-1` obstructing 39 of 41 samples, so the offenders DO "
          "name stair0ramp_*, and the bake is `geometry_parsed_geometry_type "
          "= 2` with no collision mask. Decisive test named in *One bake, "
          "three items* above; not yet run*")

NEW_16 = ("*STATUS: CLOSED 2026-08-14 -- not a bake defect. Lot 0.40.0 fixed "
          "it as walker locomotion on 2026-08-02 (gravity applied off-floor; "
          "single-lift step probe), and the library sweep on 2026-08-14 walked "
          "20 sites in 3,481 s with 0 stuck walkers and 0 barrier resolutions "
          "-- including all three sites that defined this item. The earlier "
          "same-day narrowing to a convex-hull bake was wrong; see *One bake, "
          "two items* above*")

OLD_10 = ("*STATUS: NARROWED 2026-08-14 -- quantified. `nav_gate.gd` bakes "
          "PARSED_GEOMETRY_MESH_INSTANCES; `lot.py:1430,1643` write "
          "`geometry_parsed_geometry_type = 2` for the scenes that ship. The "
          "two bakes voxelise different shapes, which is why the pass does not "
          "transfer. Same root as 12 and 16 -- see *One bake, three items* "
          "above*")

NEW_10 = ("*STATUS: NARROWED 2026-08-14 -- quantified. `nav_gate.gd` bakes "
          "PARSED_GEOMETRY_MESH_INSTANCES; `lot.py:1430,1643` write "
          "`geometry_parsed_geometry_type = 2` for the scenes that ship. The "
          "two bakes voxelise different shapes, which is why the pass does not "
          "transfer. Shares a root with 12 -- see *One bake, two items* above*")

OLD_12 = ("*STATUS: NARROWED 2026-08-14 -- the mechanism this item named is "
          "not misconfigured, it is ABSENT: `geometry_collision_mask` has no "
          "occurrence anywhere in lot, level_factory or zoo, and the bake is "
          "type 2, so every prop collider feeds it unmasked. Still the "
          "candidate cause of the 1,179 player_stuck_events in SESSION_0811*")

NEW_12 = ("*STATUS: NARROWED 2026-08-14 -- the mechanism this item named is "
          "not misconfigured, it is ABSENT: `geometry_collision_mask` has no "
          "occurrence anywhere in lot, level_factory or zoo, and the bake is "
          "type 2, so every prop collider feeds it unmasked. Still the "
          "candidate cause of the 1,179 player_stuck_events in SESSION_0811. "
          "NOTE: the 2026-08-14 sweep walked 20 sites with 0 stuck walkers, so "
          "whatever these dead polygons cost, it is not stopping walkers "
          "today*")

OLD_HEAD = "### One bake, three items — 2026-08-14"
NEW_HEAD = "### One bake, two items — and the third was already fixed — 2026-08-14"

#: The paragraph that has to go: it is the claim the sweep refuted.
OLD_STAIRS = """* **The stairs (item 16).** They ship `-convcolonly`. A convex hull over a
  staircase is a solid wedge, and its outer face measures 39.2° — under the
  55° the bake accepts. So it voxelises into walkable surface lying over
  geometry a body cannot occupy. `navmesh_solid_probe.gd` swept the walker's
  own capsule at the height the walker actually stands and found
  `stair0ramp_-1` obstructing **39 of 41 samples across 0.73 m, the first at
  the walker's own position**. That measurement was taken, recorded in the
  probe's docstring, and never reached this file — which is its own finding.
"""

NEW_STAIRS = """* **The stairs (item 16) — NOT this, and the correction is the point.**
  This section first claimed them: the stairs ship `-convcolonly`, a convex
  hull over a staircase is a solid wedge at 39.2°, under the 55° the bake
  accepts, so it must bake walkable over solid — and `navmesh_solid_probe.gd`
  had swept the walker's capsule through `stair0ramp_-1` at 39 of 41 samples.
  It was wrong. The library sweep the same day walked **20 sites in 3,481 s
  with 0 stuck walkers and 0 barrier resolutions**, including all three sites
  that defined item 16. `lot`'s own CHANGELOG had said why since 2026-08-02:
  **0.40.0, "the walker could not climb a legal stair"** — gravity applied
  every frame regardless of `is_on_floor()`, pinning the capsule into the
  ramp-floor junction, and a step-up probe that was a single 0.5 m lift with
  no fallback. Its words: *a ramp that is legal by every number in
  agent_contract.json, and a physical capsule that cannot climb it. That is
  this tool, not the site.* The probe was sweeping from the walker's own
  pinned position, so it measured the consequence of the locomotion bug and
  read as a bake defect to someone arriving in search of one. Item 16 is
  closed.
"""

#: The header sentence and the decisive-test block both name three items.
OLD_LEAD = "Items 10, 12 and 16 are three readings of one setting."
NEW_LEAD = ("Items 10 and 12 are two readings of one setting. Item 16 looked "
            "like a third and was not; that correction is below, and it is "
            "the most useful thing in this section.")

OLD_TEST = """**The decisive test, which has NOT been run.** Rebake one failing site's navqa
scene with `geometry_parsed_geometry_type = 1` and re-run its walktest. If the
walkers get through the stair, the convex hull is confirmed as the source. If
they still stop, this reading is wrong and the blockage is something the
capsule sweep cannot see — the same fork item 16 already set out.
"""

NEW_TEST = """**The test that settled it was the sweep, not a rebake.**
`library_walk.py` on 2026-08-14: 20 sites, 3,481 s, **19 pass and 1 blocked**,
with `stranded`, `no_floor`, `barrier` and `stuck` all zero on every row. The
one blocked site is `ref_pvp`, and its walkers finished — 15/15 legs, 0 stuck.
Its finding is `LOT_DESTINATION_ABOVE_FLOOR`: an objective marker 3.60 m above
the site ground plane, too tall to read as furniture, so Lot left it where the
marker put it. That is item 9's residual gap — *Lot still cannot answer "is
this anchor over anything?" offline* — not a navmesh defect.

So for items 10 and 12 there is still no measurement, only the reading above.
The rebake at `geometry_parsed_geometry_type = 1` would still say whether the
unmasked colliders change the baked surface; what it can no longer be expected
to change is stuck walkers, because there are none.
"""

OLD_TAIL = """**What is asserted here and what is not.** Asserted, by reading: type 2 is
written, no mask exists, the hulls are convex, and the probe swept a body
through solid. Inferred, and not yet measured: that the convex hull is what
produced that particular walkable polygon. That is why all three items move to
NARROWED and none to CLOSED.
"""

NEW_TAIL = """**What is asserted here and what is not.** Asserted, by reading: `lot.py`
writes type 2, `geometry_collision_mask` exists nowhere, and `nav_gate.gd`
bakes type 1 against scenes that ship at type 2. Inferred, and still not
measured: that the unmasked colliders are what put walkable polygons on prop
tops. So items 10 and 12 are NARROWED, not CLOSED.

**And the lesson this section is now mostly about.** Its first version joined
item 16 to these two on a hypothesis that `lot` 0.40.0 had already refuted and
fixed, in a CHANGELOG entry nobody was reading — because `lot`'s VERSION said
0.33.0 while its CHANGELOG documented through 0.41.0. The version drift
repaired earlier that same day had been hiding the answer to this file's
self-declared biggest open question. An instrument that measures a consequence
looks exactly like an instrument that measures a cause, and the only defence is
the record: the answer was written down, dated 2026-08-02, in the repo that
fixed it.
"""

_CRLF = "\r\n"


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


REPLACEMENTS = [
    ("item 16 status", OLD_16, NEW_16),
    ("item 10 status", OLD_10, NEW_10),
    ("item 12 status", OLD_12, NEW_12),
    ("section heading", OLD_HEAD, NEW_HEAD),
    ("section lead", OLD_LEAD, NEW_LEAD),
    ("the stairs bullet", OLD_STAIRS, NEW_STAIRS),
    ("the decisive-test block", OLD_TEST, NEW_TEST),
    ("the asserted/inferred tail", OLD_TAIL, NEW_TAIL),
]


def _apply(root: Path, *, check: bool) -> int:
    p = root / TARGET
    if not p.is_file():
        print(f"REFUSING: {TARGET} is not here")
        return 1
    raw = p.read_bytes()
    body = raw.decode("utf-8")

    if NEW_HEAD in body:
        print("  already applied")
        return 0
    if OLD_HEAD not in body:
        print("REFUSING: the 'One bake, three items' section is not here -- "
              "run patch_roadmap_navmesh_root.py first")
        return 1

    out = body
    crlf_delta = 0
    for label, old, new in REPLACEMENTS:
        # Multi-line blocks carry whatever ending the file used there.
        eol = _CRLF if (_CRLF + old.split("\n")[0]) in out else "\n"
        o = old.replace("\n", eol) if eol == _CRLF else old
        n = new.replace("\n", eol) if eol == _CRLF else new
        if out.count(o) != 1:
            print(f"REFUSING: {label} occurs {out.count(o)} time(s), "
                  f"expected 1")
            return 1
        crlf_delta += n.count(_CRLF) - o.count(_CRLF)
        out = out.replace(o, n, 1)

    data = out.encode("utf-8")
    got = data.count(_CRLF.encode())
    want = raw.count(_CRLF.encode()) + crlf_delta
    if got != want:
        print(f"REFUSING: CRLF count is {got:,}, expected {want:,}")
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

    check("item 16 reads CLOSED", NEW_16 in t)
    check("its NARROWED stamp is gone", OLD_16 not in t)
    check("items 10 and 12 stay NARROWED", NEW_10 in t and NEW_12 in t)
    check("neither still claims item 16", "Same root as 12 and 16" not in t)
    check("the section is retitled", NEW_HEAD in t and OLD_HEAD not in t)

    check("the sweep's numbers are recorded",
          "20 sites in 3,481 s" in flat and "0 barrier resolutions" in flat)
    check("lot 0.40.0 is named as the actual fix",
          '0.40.0, "the walker could not climb a legal stair"' in flat)
    check("it quotes lot's own verdict",
          "That is this tool, not the site" in flat)
    check("it explains why the probe misled",
          "measured the consequence of the locomotion bug" in flat)
    check("it says the earlier narrowing was wrong, in the item too",
          "The earlier same-day narrowing to a convex-hull bake was wrong"
          in t)
    check("ref_pvp's real finding is recorded",
          "LOT_DESTINATION_ABOVE_FLOOR" in t and "3.60 m above" in flat)
    check("it routes ref_pvp to item 9, not 16",
          "item 9's residual gap" in flat)
    check("it names the drift that hid the answer",
          "VERSION said 0.33.0 while its CHANGELOG documented through 0.41.0"
          in flat)

    # Everything the correction does NOT touch.
    check("the type-2 facts survive",
          "does not appear anywhere in `lot`, `level_factory` or" in flat)
    check("item 8 stays closed",
          "STATUS: CLOSED 2026-08-14 -- shipped as Lot 0.28.0" in t)
    check("item 16's own argument is untouched",
          "The bake and the colliders disagree about the same staircase"
          in flat)

    if "| 16 | **NARROWED**" in t or "| 16 | **OPEN**" in t:
        print("  note  the generated table is stale -- run "
              "`python tools\\roadmap_status.py --write`")

    print()
    print("  item 16 closed, and the wrong reading kept where it can be read"
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
        print("  python patches\\patch_roadmap_item16_closed.py --selftest")
        print("  python tools\\roadmap_status.py --write")
        print("  python tools\\roadmap_status.py --check")
    return rc


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
