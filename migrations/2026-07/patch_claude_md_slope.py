"""Record the SLOPE half of the contract tension, measured.

CLAUDE.md's "Known contract tensions" records one mismatch: agent_max_climb_m
versus unassisted_step_max_m, the STEP version. There is a second, identical in
shape and found tonight, that the section does not mention:

    nav_bake.agent_max_slope_deg = 55        what the navmesh routes a body up
    CharacterBody3D.floor_max_angle = 45     what a body stands on; never set,
                                             so it is Godot's default and was
                                             recorded nowhere at all

Anything between them is navigable on paper and a wall in play, exactly like the
step band. Measured off the shipped geometry: 20 of 38 buildings emit stair ramps
at 45.0-51.3 degrees, 18 below 45, none above 55.

AND THE REASON, which is the part worth keeping. Pitch is atan(story_height /
st.run) at deli_counter.py:1261, and st.run is pinned near 3 m regardless of how
tall the storey is. So a building's stairs are steep or not purely as a function
of its storey height, and that is why "the stairs used to work" was true:
walkup_siege's buildings are 35.8-40.4 degrees and walk fine, ballpark_block's are
45.0-50.0 and do not. Nothing regressed; a taller building had simply never been
walked.

Two further notes earned the same evening and cheap to keep:

  * The smooth collision ramp under the visual steps replaced per-step colliders
    on the reasoning that "a flush incline at the flight's pitch lets any
    controller walk straight up with no step logic". True only for pitch <=
    floor_max_angle. Per-step colliders were climbed by step-up at ANY pitch, so
    the change quietly made pitch load-bearing and nothing checked it.

  * Step-up cannot rescue a slope, and should not try. On a continuous incline
    the forward probe always finds a surface probe_distance * tan(pitch) higher,
    so the lift is set by the probe rather than the geometry and never converges.

Asserts its anchor, refuses on a miss, idempotent.
"""
import pathlib

ROOT = pathlib.Path(r"C:\Projects\gabagool_studios\gabagool_factory")
MD = ROOT / "CLAUDE.md"

ANCHOR = """and a wall in play — Lot's 0.16 kerb and the 0.492 riser measured at the foot of
walkup_siege's staircase both sit in that band. Before adding geometry with a
vertical rise, check which side of it the rise falls on.
"""

ADD = """and a wall in play — Lot's 0.16 kerb and the 0.492 riser measured at the foot of
walkup_siege's staircase both sit in that band. Before adding geometry with a
vertical rise, check which side of it the rise falls on.

**The same tension exists for SLOPE, and cost a whole evening before it was
named.** `nav_bake.agent_max_slope_deg` is 55; `CharacterBody3D.floor_max_angle`
is 45, is what a body actually stands on, was never set by any controller here,
and was recorded in no contract — so the mismatch had nothing to disagree with.
Measured off shipped geometry: 20 of 38 buildings emit stair ramps at 45.0–51.3°,
18 below 45°, none above 55°. The QA walkers follow the navmesh and climb them; a
person slides back down.

Why a building's stairs are steep is worth knowing, because it makes the failure
look intermittent when it is not. Pitch is `atan(story_height / st.run)`
(`deli_counter.py:1261`), and `st.run` is pinned near 3 m however tall the storey
is — so pitch is a pure function of storey height. `walkup_siege`'s buildings are
35.8–40.4° and walk fine; `ballpark_block`'s are 45.0–50.0° and do not. "The
stairs used to work" was true and not a regression: a tall-storey building had
simply never been walked.

Two corollaries:

- The smooth collision ramp replaced per-step colliders because "a flush incline
  at the flight's pitch lets any controller walk straight up with no step logic".
  That holds only for pitch ≤ `floor_max_angle`. Per-step colliders were climbed
  by step-up at *any* pitch, so the change quietly made pitch load-bearing and
  nothing checked that the geometry satisfied it.
- **Step-up cannot rescue a slope and must not try.** On a continuous incline the
  forward probe always finds a surface `probe_distance * tan(pitch)` higher, so
  the lift height comes from the probe rather than from the geometry: the body is
  thrown into the air, dropped, and thrown again. Gate step-up on the *top
  surface* being walkable, not merely on the obstruction being steep.
"""


def main() -> int:
    if not MD.exists():
        raise SystemExit(f"missing {MD}. Nothing written.")
    src = MD.read_text(encoding="utf-8")
    if "The same tension exists for SLOPE" in src:
        print("CLAUDE.md: already records the slope tension.")
        return 0
    if src.count(ANCHOR) != 1:
        raise SystemExit(f"CLAUDE.md: the contract-tensions anchor appears "
                         f"{src.count(ANCHOR)} time(s), expected exactly 1. "
                         f"NOTHING WRITTEN.")
    backup = MD.with_suffix(".md.pre_slope")
    if not backup.exists():
        backup.write_bytes(MD.read_bytes())
    out = src.replace(ANCHOR, ADD)
    MD.write_text(out, encoding="utf-8")
    print(f"CLAUDE.md: slope tension recorded "
          f"({len(src)} -> {len(out)} characters)")
    print(f"CLAUDE.md: previous file kept at {backup.name}")
    heads = [l for l in out.splitlines() if l.startswith("## ")]
    print(f"\n  sections ({len(heads)}), unchanged in number:")
    for h in heads:
        print(f"    {h[3:]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
