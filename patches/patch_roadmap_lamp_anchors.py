"""Roadmap item 19 -- the refutation of "nobody has to reconcile a lamp with
its light", and what fixed it.

Anchored, single-match, refuses on a miss. Touches only the item body: no
status block, no generated index (regenerate with tools/roadmap_status.py).
"""
from __future__ import annotations

import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
RM = ROOT / "PIPELINE_ROADMAP.md"

OLD = """So Zoo's fixture work is NOT authoring convenience and does not belong in the
same bucket as its importer dock. The dock, the Snap workflow and the exhibit
manifests are the convenience half; the baked kit, dressing and fixture geometry
are deliverable and must ship.
"""

NEW = """So Zoo's fixture work is NOT authoring convenience and does not belong in the
same bucket as its importer dock. The dock, the Snap workflow and the exhibit
manifests are the convenience half; the baked kit, dressing and fixture geometry
are deliverable and must ship.

**REFUTED FOR THE EXTERIOR HALF, 2026-09-26, and the sentence that was wrong is
"Nobody has to reconcile a lamp with its light because neither of them decided
where it goes."** That holds for a building: Deli Counter decides where a
fluorescent belongs, and Zoo's fixture pass and Lux's rig both read that one
anchor. It did not hold for the street, because the street's lamp and the
street's light were decided by two different functions and neither read the
other. `pole_vs_light.gd` on cold run 9087's walk copy:

    POLE/LIGHT: 54 streetlight light(s), 48 streetlight prop mesh(es)
       min 3.50 m   median 24.93 m   mean 30.62 m   max 93.68 m
       lights with a pole within 1.0 m: 0 of 54

`lot.site_furniture.plan_furniture` stood `streetlight` COVER pieces along the
kerb bands -- nudged clear of the dropped kerbs and the mission markers -- as
prop slots the site kit builds. `lot._streetlight_anchors` derived light ROWS
from the path graph and a ring 2 m inside the ground rect. Every exterior light
in the level was light from nowhere, and the walker found it from the inside
before any instrument did: standing at the map edge in two hard cone edges
washing the boundary wall, "a reminder that light should comes from light
sources, i don't know where this light is coming from".

**The first diagnosis was wrong in an expensive direction and is kept here for
that reason.** Reading the planner, this looked like a missing PIPELINE STAGE:
Zoo's fixture jobs are planned one per `art_buildings` entry
(`packages/pipeline/planner.py`, `_STAGE_ZOO_FIXTURES`) and there is no
site-level fixture job at all, so the site's manifest reaches Lux and never
reaches Zoo. That is true, and it is not why the lights were wrong. A grep for
who emits the anchors showed BOTH SIDES LIVE IN LOT -- `lot.py:455` and
`site_furniture.py:690`, one repo, and `merge_lights` already runs after
`plan_furniture` has extended `site_spec["cover"]`. The poles were sitting in
the same dict the anchors were being invented beside.

Lot 0.79.0: the poles are the anchors. One light per lamp, at the lamp's plan
point, at its yaw, at the height of its lens -- coincident by construction
rather than by two formulas agreeing. Measured end to end on `gs_heist`'s
emitted manifests: 8 poles, 8 lights, worst horizontal distance 0.0000 m, each
light exactly 0.175 m below its module's top, which is where the recipe puts
the emissive lens. The path rows and the perimeter ring are gone with it, so
the map edge is now lit by the moon alone; standing poles out there is a
placement decision for `site_furniture` and the right way to light a boundary,
and faking it from the light side was not.

The missing site-level fixture stage is still missing, and this makes it
SAFE rather than unnecessary. A site anchor now carries
`"hardware": "slot:cover_12"`, naming the slot whose pole already stands
there; Zoo 1.6.0's `plan` skips such an anchor with that reason recorded,
instead of building a second pole inside the first. What the stage would still
buy is hardware for the anchors that have none -- and after this change the
site manifest's only type is `streetlight`, so on today's sites it would buy
nothing. Reopen it when Lot starts emitting an exterior anchor that is not a
pole.
"""


def main():
    raw = RM.read_bytes()
    crlf, lf = raw.count(b"\r\n"), raw.count(b"\n")
    if crlf:
        raise SystemExit(f"REFUSED: roadmap is LF; found {crlf} CRLF of {lf}")
    text = raw.decode("utf-8")
    n = text.count(OLD)
    if n != 1:
        raise SystemExit(f"REFUSED: anchor matches {n} times, not 1")
    out = text.replace(OLD, NEW, 1).encode("utf-8")
    RM.write_bytes(out)
    print(f"[patch] PIPELINE_ROADMAP.md: {len(raw)} -> {len(out)} bytes, "
          f"CRLF {out.count(chr(13).encode() + chr(10).encode())}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
