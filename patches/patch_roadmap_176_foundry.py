"""Roadmap item 176: a stair regression the baseline was about to absorb.

WHY THIS IS AN ITEM AND NOT A BASELINE LINE. `navgate_baseline.json` exists to
freeze a set that can otherwise grow silently -- its own docstring says so. It
now has a fourth entry, and the entry is different in kind from the other
three: those shells have never passed, this one PASSED on 2026-08-21 and fails
today. A baseline is the right place to record it so the gate stays live for
the other 134 shells; it is the wrong place to let it rest, because a
regression parked in a baseline reads identically to an accepted failure six
weeks later.

Appended at the end of the file, in the file's own [STATUS][HEADING][BODY]
order -- verified by reading item 175, whose status block sits directly above
its heading.

Anchored on the final two lines, which must match exactly once.
"""
from pathlib import Path

TARGET = Path(__file__).resolve().parent.parent / "PIPELINE_ROADMAP.md"

ANCHOR = """look before the rule is written as unconditional.
"""

BODY = """look before the rule is written as unconditional.

*STATUS: OPEN 2026-09-23 -- REGRESSION, WINDOW IDENTIFIED, COMMIT NOT YET
FOUND. `foundry_heist_vertical` passed the stair gate when
`navgate_baseline.json` was generated (2026-08-21, 135 shells, 3 stair
failures) and fails now. Its basement bakes as a disjoint island: 339 polygons
against 1,286 for ground-to-roof, with three separate connections crossing the
junction and none carrying. Two hypotheses refuted (below). Recorded in the
baseline as entry four, explicitly labelled a regression.*

**176. A stair regression hid behind a baseline that was doing its job.** One
shell in 135 stopped connecting its basement some time between 2026-08-21 and
2026-09-23, and nothing failed until the library was rebuilt for an unrelated
release.

**WHAT THE GATE SAYS.** `build/foundry_heist_vertical.navgate.json`:

    navmesh_polys  1675 in 19 islands
    island 0       1286 polys   y   0.20 .. 10.55   ground floor to roof
    island 1        339 polys   y  -3.10 ..  0.35   the basement
    stair_0        no_path -- "endpoints on disjoint islands
                   (lower on 1, upper on 0)"
    stair_1        ok      -- storey 0 to 2, entirely above ground

**THREE CONNECTIONS CROSS THAT JUNCTION AND NONE CARRIES**, which is what
moves the suspicion off any one of them and onto the junction itself: the
`switchback` stair (`from_story -1, to_story 3`), a 12 m ramp declared at
30 deg, and `ladder1` (`from_story -1, to_story 0`). One failing is a defect in
one thing. Three failing together is a defect in what they all land on.

**THE POPULATION, so the shape is not mistaken for a one-off spec.** It is 1 of
49 basement shells and the other 48 pass. It is also the only stair in the
library spanning +4 storeys -- 131 span +1, 12 span +2, 5 span +3 -- so if the
span is load-bearing, this is the only shell that could show it.

**TWO HYPOTHESES RAISED AND REFUTED**, kept here because they are cheaper to
read than to re-run:

1. *The spec's `to_story: 3` exceeds `n_stories: 3`.* REFUTED: ten specs use
   `to_story == n_stories` as the roof-access convention and only this one
   fails, so the convention is not the defect. (This was also stated as a
   finding earlier in the same session and retracted on checking the library --
   the retraction is the useful part.)
2. *The arrival sits one `cell_height` above the ground floor, so Recast will
   not join the spans.* REFUTED by measuring the glb rather than the report:
   `stair0_land_-1`, `stair0_discharge_-1` and `slab story 0` all top out at
   y = 0.0000. They are level. The 0.20 and 0.35 that suggested a 0.15 m step
   are Recast voxel tops on the `-3.70 + k * 0.15` grid the bake's own AABB and
   `cell_height` define -- a ROUNDED ARTEFACT, exactly the thing CLAUDE.md
   already records as unable to settle a question about floats. Both smooth
   ramp colliders pitch at 35.0 deg (rise 3.853 m over run 5.50 m) against a
   55 deg bake limit, so slope is not it either.

**WHAT IS OPEN: which commit.** The window is 2026-08-21..2026-09-23 and is
dominated by stair-guard work -- 0.126.0 (stairs are guarded), 0.134.0 (the
back of a flight is filled flush with its side walls), 0.138.0 (the hole behind
the stair), 0.143.0 (a rail's opening must have floor under it). Guards are the
suspect and are NOT convicted. The one guard-shaped quantity checked came back
clean: `st.width` is 1.8 against a `min_corridor_width` of 1.1, so this flight
takes the filled guard rather than the thin one, and its side pieces measure
flush to the flight edges (x -4.70..-4.31 and -0.70..-0.30 against a flight at
-2.50..-0.70) with no slot between.

**HOW TO SETTLE IT**, written down because the cost is the reason it has not
been done yet: bisect that window in a separate git worktree -- so the main
checkout stays clean and no cold run is disturbed -- rebuilding this one shell
and re-running `nav_gate` at each step. Roughly fifteen commits.

**THE SECOND-ORDER FINDING, and it may matter more than the first.** Nothing
caught this for a month. `test_navgate_population.py` compares against
`navgate_baseline.json` and reads `build/`, which is not committed -- so the
comparison only happens on a machine that has just rebuilt the library, and the
library is rebuilt when a release needs it rather than on a schedule. A gate
that runs when somebody happens to rebuild is a gate with an unknown duty
cycle, and the interval here was five weeks. Worth deciding whether the sweep
should run on its own cadence, and worth noting that the regression surfaced as
a side effect of an unrelated release rather than by being looked for.
"""


def main() -> None:
    data = TARGET.read_bytes()
    if b"\r\n" in data:
        raise SystemExit("REFUSED: expected LF, found CRLF")
    text = data.decode("utf-8")
    before = len(data)
    if "**176." in text:
        raise SystemExit("REFUSED: item 176 already present")
    hits = text.count(ANCHOR)
    if hits != 1:
        raise SystemExit(f"REFUSED: anchor matched {hits} times")
    text = text.replace(ANCHOR, BODY)
    out = text.encode("utf-8")
    if b"\r\n" in out:
        raise SystemExit("REFUSED: would write CRLF")
    TARGET.write_bytes(out)
    print(f"{TARGET.name}: {before} -> {len(out)} bytes (+{len(out) - before})")


if __name__ == "__main__":
    main()
