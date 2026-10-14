"""Cold run 9295's three far walls, replayed on the Level Factory at LF_ROOT (default the factory's), to see which
a change to the wall moves (roadmap 241, the corner shop).

    LF_ROOT=<a level_factory tree> python patches/lf_corner_fill/replay_candidates.py

Inputs as `replay_9003.py` reads them, for each candidate: its roads and plate from its site spec, the stream
`site_variation.stream(seed ^ 0x5E3A11)`, and the action's centre the run's log printed (`docs/cold_runs/cold_9295/
art.log`, in the order the candidates were composed: 9003, 9104, 9205). Prints, per candidate, whether the replay
stands the run's wall block for block, and if not, both walls' ends and how far short of the run's end each stops.
"""
import json
import os
import pathlib
import sys

F = pathlib.Path(__file__).resolve().parents[2]
LF = pathlib.Path(os.environ.get("LF_ROOT") or F / "level_factory")
sys.path.insert(0, str(LF))
from packages.pipeline import building_library as bl, empties, site_variation, street_line as sl  # noqa: E402

ACTIONS = {9003: -28.5, 9104: -2.5, 9205: -27.0}


def main():
    print("Level Factory at", LF, (LF / "VERSION").read_text(encoding="utf-8").strip())
    lib = F / "deli_counter" / "build"
    rows = bl.empty_rows(lib, bl.MIDRISE_PREFIX) + bl.empty_rows(lib, bl.CORNER_PREFIX, family="corner")
    ext = {r["id"]: sl.shell_extents(r["glb"], skip=sl.STOOP_COLLIDERS) for r in rows}
    heights = {r["id"]: sl.shell_top(r["glb"]) for r in rows}
    for seed, action in ACTIONS.items():
        spec = json.loads((F / "workspaces" / "cold-9295-ws" / ".level_factory" / "temp" / "urban_row_001" /
                           f"candidate_seed_{seed}" / "site.json").read_text(encoding="utf-8"))
        roads, span = spec["roads"], spec["ground"]["size_x"]
        run = sorted(((b["archetype"], b["at"]) for b in spec["blockers"] if b["id"].startswith("e")),
                     key=lambda t: t[1][0])
        placed, _ = empties.terrace(rows, ext, site_variation.stream(seed ^ 0x5E3A11), roads, span, continuous=True,
                                    action=action, heights=heights)
        replay = [(p["archetype"], p["at"]) for p in placed]
        x1 = span / 2.0 - empties.CLEARANCE

        def short(wall):
            a, at = wall[-1]
            return x1 - (at[0] + ext[a][1] - ext[a][0] - (ext[a][1] - ext[a][0]) / 2.0)

        if replay == run:
            print(f"seed_{seed}: SAME, {len(run)} blocks, {short(run):.2f} m short")
        else:
            print(f"seed_{seed}: MOVED, {len(run)} -> {len(replay)} blocks, {short(run):.2f} -> {short(replay):.2f} m "
                  f"short; ends {run[0][0]} .. {run[-1][0]} -> {replay[0][0]} .. {replay[-1][0]}")


if __name__ == "__main__":
    main()
