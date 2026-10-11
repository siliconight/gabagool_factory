"""Roadmap 181: roof props reach a level -- Deli Counter 0.209.0, Zoo 1.101.0, Level Factory 0.179.0,
priced and seen in cold run 9245. Replaces 181's status block (asserted whole by its first and last
text and asserted to adjoin its heading) and appends one body paragraph. The index is NOT touched
here: run `python tools/roadmap_status.py --write` then `--check` after it.

    python patches/patch_roadmap_181_roof_props.py && python tools/roadmap_status.py --write && python tools/roadmap_status.py --check
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
RM = ROOT / "PIPELINE_ROADMAP.md"
HEAD_181 = "\n\n**181. Zoo's roof props cannot fire: the adapter reads a key no planner\nwrites.**"
S181_START = "*STATUS: OPEN 2026-10-05 -- FOUND, NOT STARTED. Zoo's roof scatter (`core/roofprops.py`, v0.25"
S181_END = "only for a job carrying `roof_props_slots`, and nothing in Level Factory writes that key.*"
S181_NEW = (
    "*STATUS: CLOSED 2026-10-11 -- roof props reach a level, priced and seen. Zoo 1.101.0 "
    "(`patches/patch_zoo_roof_props.py`: the scatter keeps off the roof's holes and the landings Deli "
    "Counter 0.209.0 writes on the roof slot, tests a yawed prop as the box it occupies, plans a tank "
    "only from 12 m up, and merges a roof to about one mesh a species -- deli_a01's 59 parts to 6), "
    "Deli Counter 0.209.0 (`patch_dc_roof_keepout.py`: `fit.keep_out`, the `roofprops` layer, the "
    "gate's third arm; 52 of 133 library roofs carry a landing) and Level Factory 0.179.0 "
    "(`patch_lf_roof_props.py`: `zoo_roof_props_build` per enterable building, the third compose "
    "layer, the brief's `roof_props`; the dead `roof_props_slots` read gone -- it could never have "
    "fired, `zoo_cli` answering `--roof-props` before `--build-kit`). Cold run 9245 "
    "(restaurant_row_001, 0 interventions, baked on its first attempt): three roofs of 17 props each, "
    "3,501 lightmap users = 9244's 3,483 + the 18 merged meshes; against 9244's package +13 draws a "
    "heading at the median, +33 at most, never fewer, p95 -0.46 ms inside a 1.11 ms control spread, "
    "0 of 53 headings outside it; seen from the deli's hatch (units, stacks and a dish throwing long "
    "evening shadows) and barely from the street (behind the parapet). The gate's two new moderates "
    "were its own stair column reaching the roof -- Deli Counter 0.209.1 bounds it to the floors the "
    "stair serves, re-gated 8 -> 0 on the run's buildings. The walk bots on the package: "
    "`Ladder_ladder_0` climbed to 6.6 m and stood up on that roof among its 17 props, the landing "
    "kept off being where it stood; all five stations passed, the hatch-top one at 0.04 % fighting. "
    "Left to the walker's eye, not "
    "to this item: the species' look, the 12 m tank gate, and the mix -- density 1.0 saturates every "
    "cap on any roof over about 300 m2, so all three roofs carry the same 17, the antennas' "
    "uniformity again.*")
TAIL_181 = ("ladder -- with the result priced A/B/A2 like any look; or the branch and the\n"
            "module removed. A path nothing reaches reads as a capability.")
ADD_181 = """

**LANDED AND PRICED, 2026-10-11** (`docs/cold_runs/cold_9245/`, `docs/findings/roof_props/`). What closing it took, in the order it shipped: the roof slot learned where a body steps off a ladder (Deli Counter 0.209.0's `keep_out`, written in the frame the slab's holes use -- a stepped building's holes and landings would be off by its inset together, and two of 133 roofs stand off-centre, both hole-less: noted, not fixed); the scatter learned to read holes and landings, to clamp and overlap-test a yawed prop by the box it occupies (0.25 read the unrotated box, and a 90-degree HVAC at a 4 m roof's long edge reached inside a parapet), to withhold a water tank below 12 m, and to merge a roof's props across the roof (the merge groups by part family and material: about one mesh a species); the planner got a stage of its own, since the kit-branch read could never have run both commands; the composer a third layer the gate asks its question of. The price is cheap because the unit is right: a roof's props enter and leave view together, so eighteen meshes cost thirty-three draws at the worst heading and nothing the harness can see. **What the gate taught:** its stair column ran +/-1e6 in z, which no dressing prop had ever met because none stands over a stairwell on a floor the stair does not serve; the roof does, on both buildings with a stair under it. Attributed before patching -- eight conflicts, seven HVAC parts and a dish, all stair columns, no doorway or ladder -- and the fix shown to own exactly those by running the patched gate against the run's own compose output (`regate_9245.py`, 8 -> 0, the other arms unmoved). **What is open is taste, and it is queued:** the mix (17 a roof, every cap saturated), the species' look, the tank gate."""


def main():
    raw = RM.read_bytes()
    assert b"\r\n" not in raw, "the roadmap is LF"
    text = raw.decode("utf-8")
    assert "RESULT_" not in S181_NEW + ADD_181 and "WALK_PENDING" not in S181_NEW, "the walk's line is not filled in"
    assert text.count(HEAD_181) == 1, "181's heading not found once"
    h = text.index(HEAD_181)
    s = text.rfind("\n\n*STATUS:", 0, h) + 2
    status = text[s:h]
    assert status.startswith(S181_START) and status.endswith(S181_END), ("181's status", status[:80], status[-80:])
    nxt = text.find("\n\n*STATUS:", h + 10)
    body = text[h:nxt]
    assert body.endswith(TAIL_181), ("181's body tail", body[-160:])
    assert "LANDED AND PRICED" not in body, "already applied"
    text = text[:nxt] + ADD_181 + text[nxt:]
    text = text[:s] + S181_NEW + text[h:]
    assert text.endswith("\n")
    RM.write_bytes(text.encode("utf-8"))
    print("roadmap: 181's status replaced and its paragraph appended; now roadmap_status.py --write / --check")


if __name__ == "__main__":
    sys.exit(main())
