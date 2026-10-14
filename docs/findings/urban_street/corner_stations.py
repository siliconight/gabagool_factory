"""Stations facing each corner shop of a cold run's urban wall, for `tools/look_shots.py` (roadmap 241, the corner shop).

    python docs/findings/urban_street/corner_stations.py <cold run N> <mission> <seed>

Reads the candidate's site spec (`workspaces/cold-N-ws/.level_factory/temp/<mission>/candidate_<seed>/site.json`):
its through road (`roads[0]`) and every blocker whose archetype carries Level Factory's corner prefix
(`building_library.CORNER_PREFIX`). For each corner it prints one `--station` argument: the eye on the near
sidewalk's centre line, 1.7 m up, straight across the street from the block's centre, looking at the far side's
front line 2.5 m up -- the shop's glass. Godot frame (x east, y up, z = -plan y), metres. The frame's name is
`corner_<i>_<archetype>`, west to east.

Prints the arguments on stdout and what it read on stderr, and stops. A spec with no through road, or no corner
blocker, prints UNKNOWN SHAPE and exits 1.
"""
import json
import pathlib
import sys

F = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(F / "level_factory"))
from packages.pipeline import building_library, empties  # noqa: E402

EYE = 1.7
LOOK = 2.5


def main():
    n, mission, seed = sys.argv[1], sys.argv[2], sys.argv[3]
    p = F / "workspaces" / f"cold-{n}-ws" / ".level_factory" / "temp" / mission / f"candidate_{seed}" / "site.json"
    spec = json.loads(p.read_text(encoding="utf-8"))
    roads, blockers = spec.get("roads") or [], spec.get("blockers") or []
    corners = sorted((b for b in blockers if str(b.get("archetype", "")).startswith(building_library.CORNER_PREFIX)),
                     key=lambda b: b["at"][0])
    if not roads or not corners:
        sys.exit(f"UNKNOWN SHAPE: {len(roads)} road(s), {len(corners)} corner blocker(s) in {p}")
    through = roads[0]
    y_road = (float(through["a"][1]) + float(through["b"][1])) / 2.0
    near = y_road + float(through["width"]) / 2.0 + float(through.get("sidewalk") or 0.0) / 2.0
    _edge, front = empties._far_side(through)
    args = []
    for i, b in enumerate(corners):
        x = float(b["at"][0])
        name = f"corner_{i}_{b['archetype']}"
        print(f"# {name}: block centre x {x:.2f}, {b['size_x']} m wide; eye at plan ({x:.2f}, {near:.3f}), looking "
              f"at the far front line y {front:.3f}", file=sys.stderr)
        args.append(f"--station {name}:{x:.3f},{EYE},{-near:.3f},{x:.3f},{LOOK},{-front:.3f}")
    print(" ".join(args))


if __name__ == "__main__":
    main()
