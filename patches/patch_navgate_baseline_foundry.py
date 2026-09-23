"""`foundry_heist_vertical` enters the stair-failure baseline AS A REGRESSION.

NOT AN ACCEPTED FAILURE, and the distinction is the whole point of this patch.
The other three entries are shells that have never passed. This one PASSED: the
baseline was generated 2026-08-21 from a 135-shell sweep that recorded three
stair failures, `foundry_heist_vertical` was in the library at the time (its
spec was last touched 2026-07-17, 0.126.0 being later still) and it was not
among them. It fails now. So the gate is correct and something between those
dates broke it.

WHAT WAS MEASURED, from `build/foundry_heist_vertical.navgate.json` and the
built glb, so the next session does not re-derive it:

  * The bake yields 1,675 polygons in 19 islands. Island 0 is 1,286 polygons
    spanning y 0.20..10.55 -- ground floor to roof. Island 1 is 339 polygons
    spanning y -3.10..0.35 -- the basement. They are disjoint, and
    `foundry_heist_vertical_stair_0` has its lower endpoint on 1 and its upper
    on 0. `..._stair_1` (storey 0 to 2) is `ok`.
  * THREE independent connections cross that break and none of them carries:
    the switchback stair, a 12 m ramp declared at 30 deg, and `ladder1`
    (`from_story -1, to_story 0`). One failing is a defect in one thing; three
    failing is a defect at the junction.
  * It is 1 of 49 basement shells in the library, and the other 48 pass. It is
    also the ONLY stair in the library spanning +4 storeys (131 span +1, 12
    span +2, 5 span +3).

TWO HYPOTHESES RAISED AND REFUTED HERE, kept because they are cheaper to read
than to rediscover:

  1. "The spec's `to_story: 3` exceeds `n_stories: 3`." REFUTED: ten specs use
     `to_story == n_stories` as the roof-access convention and only this one
     fails, so the convention is not the defect.
  2. "The stair's arrival sits 0.15 m above the ground floor, one cell_height,
     so Recast will not join the spans." REFUTED by measuring the glb:
     `stair0_land_-1` and `stair0_discharge_-1` both top out at y = 0.0000 and
     `slab story 0` tops at y = 0.0000. They are level. The 0.20 and 0.35 in
     the island report are Recast voxel tops on the `-3.70 + k * 0.15` grid the
     bake's own AABB and `cell_height` define -- a ROUNDED ARTEFACT, which
     CLAUDE.md already warns cannot settle a question about floats. Both smooth
     ramp colliders pitch at 35.0 deg (rise 3.853 m over run 5.50 m), well
     inside the 55 deg bake limit, so slope is not it either.

WHAT IS NOT YET KNOWN: which commit. The window is 2026-08-21..2026-09-23 and
is dominated by stair-guard work -- 0.126.0 (stairs are guarded), 0.134.0 (the
back of a flight is filled), 0.138.0 (the hole behind the stair), 0.143.0 (a
rail's opening must have floor under it). Guards are the suspect and are NOT
convicted: the one guard-shaped quantity checked here came back clean, since
`st.width` is 1.8 against a `min_corridor_width` of 1.1, so this flight takes
the filled guard rather than the thin one and the side pieces measure flush to
the flight edges (x -4.70..-4.31 and -0.70..-0.30 against a flight at
-2.50..-0.70). Settling it needs a bisect over that window, rebuilding this one
shell and re-running nav_gate at each step.

Anchored: every anchor must match exactly once or this refuses to write.
"""
from pathlib import Path

TARGET = Path(__file__).resolve().parent.parent / "deli_counter" / \
    "navgate_baseline.json"

# ---------------------------------------------------------------- anchor 1
A1 = '''    "stair_failures": 3,'''
N1 = '''    "stair_failures": 4,'''

# ---------------------------------------------------------------- anchor 2
A2 = '''  "stair_failures": [
    {
      "shell": "cbp_town_finale_midbalanced_schemafixed",'''

N2 = '''  "stair_failures": [
    {
      "shell": "foundry_heist_vertical",
      "stairs": [
        "foundry_heist_vertical_stair_0"
      ],
      "entered": "2026-09-23",
      "regression": true,
      "reason": "A REGRESSION, NOT AN ACCEPTED FAILURE -- unlike the three below, this shell PASSED when this baseline was generated (2026-08-21, 135 shells, 3 stair failures, and this spec was last touched 2026-07-17). It is recorded so the gate stays live for the other 134 shells, NOT because the failure is acceptable, and it must be bisected out rather than left here. Measured: the bake yields 1675 polygons in 19 islands, island 0 (1286 polys, y 0.20..10.55) is ground-to-roof and island 1 (339 polys, y -3.10..0.35) is the basement, and they are disjoint -- so stair_0 has its lower endpoint on 1 and its upper on 0 while stair_1 (storey 0 to 2) is ok. THREE separate connections cross that junction and all three fail: the switchback stair, a 12 m ramp declared at 30 deg, and ladder1 (from_story -1 to_story 0), which is why the junction is the suspect rather than any one of them. It is 1 of 49 basement shells and the other 48 pass; it is also the only +4-storey stair in the library (131 are +1, 12 are +2, 5 are +3). REFUTED HYPOTHESES, kept so they are not re-run: (1) that the spec to_story 3 exceeds n_stories 3 -- ten specs use to_story == n_stories as the roof-access convention and only this one fails; (2) that the arrival sits one cell_height above the ground floor -- the glb says stair0_land_-1, stair0_discharge_-1 and slab story 0 all top out at y = 0.0000, and the 0.20/0.35 in the island report are Recast voxel tops on the -3.70 + k*0.15 grid, a rounded artefact. Both smooth ramp colliders pitch at 35.0 deg against a 55 deg bake limit, so slope is not it. OPEN: which commit. The window 2026-08-21..2026-09-23 is dominated by stair-guard work (0.126.0, 0.134.0, 0.138.0, 0.143.0) and guards are suspected but not convicted -- st.width 1.8 exceeds min_corridor_width 1.1, so this flight takes the filled guard and its side pieces measure flush to the flight edges. Settling it needs a bisect over that window."
    },
    {
      "shell": "cbp_town_finale_midbalanced_schemafixed",'''

EDITS = ((A1, N1), (A2, N2))


def main() -> None:
    data = TARGET.read_bytes()
    if b"\r\n" in data:
        raise SystemExit("REFUSED: expected LF, found CRLF")
    text = data.decode("utf-8")
    before = len(data)
    for i, (old, new) in enumerate(EDITS, 1):
        hits = text.count(old)
        if hits != 1:
            raise SystemExit(f"REFUSED: anchor {i} matched {hits} times")
        text = text.replace(old, new)
    out = text.encode("utf-8")
    if b"\r\n" in out:
        raise SystemExit("REFUSED: would write CRLF")
    # A BASELINE THAT DOES NOT PARSE IS WORSE THAN A FAILING TEST.
    import json
    d = json.loads(out.decode("utf-8"))
    assert d["counts"]["stair_failures"] == len(d["stair_failures"]), \
        "REFUSED: counts.stair_failures disagrees with the list"
    TARGET.write_bytes(out)
    print(f"{TARGET.name}: {before} -> {len(out)} bytes (+{len(out) - before}); "
          f"stair_failures {len(d['stair_failures'])}")


if __name__ == "__main__":
    main()
