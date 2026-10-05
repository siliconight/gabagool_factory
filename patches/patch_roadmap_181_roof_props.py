"""PIPELINE_ROADMAP.md: file item 181 -- Zoo's roof props cannot fire.

Found 2026-10-05 while giving the Empties TV antennas (Zoo 1.74.0, Patina
0.29.0, Deli Counter 0.185.0), which took the dressing path. Appends the item,
its status line directly above its heading, after item 180's last line; the
generated index is left to `tools/roadmap_status.py --write`.

    python patch_roadmap_181_roof_props.py
"""
import pathlib

ROADMAP = pathlib.Path(__file__).resolve().parent.parent / "PIPELINE_ROADMAP.md"

TAIL = '''*Earlier status, kept verbatim:* *STATUS: OPEN 2026-10-05 -- MEASURED on
cold run 9154's package: hiding every cover takes the worst view from 8,690
draws / 27.33 ms p95 to 5,571 / 17.74 ms, and the median view 850 draws /
2.06 ms lighter; control 0 draws / +0.05 ms. Nothing merges them.*
'''

ITEM = '''
*STATUS: OPEN 2026-10-05 -- FOUND, NOT STARTED. Zoo's roof scatter (`core/roofprops.py`, v0.25; `zoo_cli.py --roof-props`) has never run in a level: Level Factory's Zoo adapter passes `--roof-props` only for a job carrying `roof_props_slots`, and nothing in Level Factory writes that key.*

**181. Zoo's roof props cannot fire: the adapter reads a key no planner
writes.** Found while giving the Empties TV antennas and satellite dishes
(Zoo 1.74.0, Patina 0.29.0, Deli Counter 0.185.0), which took the dressing
path instead.

**WHAT EXISTS.** Zoo 0.25 plans and builds a rooftop scatter -- water tanks,
HVAC units, vent stacks, exhaust fans, skylights, satellite dishes --
deterministic per manifest and seed: `zoo_keeper/core/roofprops.py`
`scatter`, `bpylayer.build.build_roof_props`, `zoo_cli.py --roof-props`, with
its own tests (`tests/test_roofprops.py`). Level Factory's Zoo adapter
(`adapters/zoo/__init__.py:375`) adds `--roof-props` when a job spec carries
`roof_props_slots`.

**WHAT DOES NOT.** Nothing writes `roof_props_slots`. Grepped over Level
Factory's Python, tests excluded, on 2026-10-05: the key appears only where
the adapter reads it. No level has had a roof prop, and the adapter's branch
is a code path that cannot fire -- indistinguishable, from outside, from one
that ran and found nothing to do.

**WHY THE EMPTIES DID NOT USE IT.**
  * Its rules are a commercial roofscape -- a water tank on any roof of 50 m2
    or more, HVAC units by area -- most of it below a parapet from the
    street.
  * It writes a GLB per building with a mesh per part, where the Empties'
    covers merge one mesh per side per material (roadmap 180).
  * It has no TV antenna, which is the thing a rowhome's roofline shows.

**WHAT WOULD CLOSE IT.** Either a planner that writes the key -- for the
enterable buildings whose flat roofs a player sees from a higher roof or a
ladder -- with the result priced A/B/A2 like any look; or the branch and the
module removed. A path nothing reaches reads as a capability.
'''


def main():
    s = ROADMAP.read_text(encoding="utf-8")
    assert "\r" not in s
    assert s.count(TAIL) == 1 and s.endswith(TAIL), "item 180's last line is not the file's end"
    assert "**181." not in s
    ROADMAP.write_text(s + ITEM, encoding="utf-8", newline="\n")
    print("filed roadmap item 181")


if __name__ == "__main__":
    main()
