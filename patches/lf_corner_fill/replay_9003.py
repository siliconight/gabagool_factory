"""Cold run 9295's seed_9003 far wall, replayed with the inputs the compose stage had, and its fill traced where it
stopped (roadmap 241, the corner shop).

    python patches/lf_corner_fill/replay_9003.py

The inputs, each read where the run left it: the rows as `building_library.empties_for_brief` draws them for an
urban brief (Deli Counter's build dir, the mid-rises and the corner blocks); the extents and heights as the
compose stage reads them (`street_line.shell_extents(glb, skip=STOOP_COLLIDERS)`, `shell_top`); the roads and
the plate's width from the candidate's site spec (`workspaces/cold-9295-ws/.level_factory/temp/urban_row_001/
candidate_seed_9003/site.json`); the stream `site_variation.stream(9003 ^ 0x5E3A11)`; the action's centre as the
run's own log printed it (`docs/cold_runs/cold_9295/art.log`: x -28.5, to one decimal).

THE CONTROL: the replay must stand the run's far wall -- every block's archetype and `at` as the site spec's
blockers e0... -- or nothing it says about the fill is about this run. Then `_cornered`'s fill is run again, its
one call to `_by_height` wrapped to print, at the call that returns None, where the fill stood, the room it was
keeping for the closing corner, and what was left on the bag with its widths. Prints what it measured and stops.
"""
import json
import pathlib
import sys

F = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(F / "level_factory"))
from packages.pipeline import building_library as bl, empties, site_variation, street_line as sl  # noqa: E402

SEED, ACTION = 9003, -28.5


def main():
    lib = F / "deli_counter" / "build"
    rows = bl.empty_rows(lib, bl.MIDRISE_PREFIX) + bl.empty_rows(lib, bl.CORNER_PREFIX, family="corner")
    ext = {r["id"]: sl.shell_extents(r["glb"], skip=sl.STOOP_COLLIDERS) for r in rows}
    heights = {r["id"]: sl.shell_top(r["glb"]) for r in rows}
    spec = json.loads((F / "workspaces" / "cold-9295-ws" / ".level_factory" / "temp" / "urban_row_001" /
                       f"candidate_seed_{SEED}" / "site.json").read_text(encoding="utf-8"))
    roads, span = spec["roads"], spec["ground"]["size_x"]
    run = sorted(((b["archetype"], b["at"]) for b in spec["blockers"] if b["id"].startswith("e")),
                 key=lambda t: t[1][0])
    placed, _ = empties.terrace(rows, ext, site_variation.stream(SEED ^ 0x5E3A11), roads, span, continuous=True,
                                action=ACTION, heights=heights)
    replay = [(p["archetype"], p["at"]) for p in placed]
    print(f"rows {len(rows)}, span {span}, action {ACTION}: the run's far wall {len(run)} blocks, the replay's "
          f"{len(replay)}: {'SAME' if replay == run else 'DIFFERENT'}")
    if replay != run:
        for a, b in zip(run, replay):
            print("   run", a, "replay", b)
        sys.exit("the replay is not the run's wall: nothing below would be about this run")
    real = empties._by_height

    def watched(bag, extents, heights_, x, x_end, centre, reach, lo, hi, prev):
        i = real(bag, extents, heights_, x, x_end, centre, reach, lo, hi, prev)
        if i is None:
            left = [(r["id"], round(empties._width(extents, r["id"]), 2)) for r in bag]
            print(f"the fill stopped at x {x:.2f}, keeping the closing corner's room from x {x_end:.2f} "
                  f"({x_end - x:.2f} m left to fill); on the bag: {left}")
        return i

    empties._by_height = watched
    try:
        placed2, _ = empties.terrace(rows, ext, site_variation.stream(SEED ^ 0x5E3A11), roads, span, continuous=True,
                                     action=ACTION, heights=heights)
    finally:
        empties._by_height = real
    assert [(p["archetype"], p["at"]) for p in placed2] == replay
    last = placed2[-1]
    x1 = span / 2.0 - empties.CLEARANCE
    print(f"the closing block {last['archetype']}, {last['size_x']} m, ends at x "
          f"{last['at'][0] + last['size_x'] / 2.0:.2f}; the run ends at x {x1:.2f}")


if __name__ == "__main__":
    main()
