"""Stations facing each walk-up of a cold run's urban street, for `tools/look_shots.py` (roadmaps 156 and 241).

    python docs/findings/fire_escape/walkup_stations.py <cold run N> <mission> <seed>

Reads the candidate's site spec (`workspaces/cold-N-ws/.level_factory/temp/<mission>/candidate_<seed>/site.json`):
its through road (`roads[0]`) and every blocker whose archetype Deli Counter (>= 0.220.0) stands a fire escape on --
a mid-rise of six storeys or fewer that is no corner block, read off the shell's own spec in `deli_counter/specs/`
(`fire_escape_stack`). A blocker on either side of the road is framed from the other side's sidewalk: the eye on
that sidewalk's centre line, 1.7 m up, straight across the street from the block's centre, looking at the block's
front line 6 m up -- the middle of a fire escape from the second storey to the fifth. Godot frame (x east, y up,
z = -plan y), metres. The frame's name is `walkup_<i>_<archetype>`, west to east.

Prints the arguments on stdout and what it read on stderr, and stops. A spec with no through road, or no walk-up
blocker, prints UNKNOWN SHAPE and exits 1.
"""
import json
import pathlib
import sys

F = pathlib.Path(__file__).resolve().parents[3]
EYE = 1.7
LOOK = 6.0


def _walkup(archetype):
    p = F / "deli_counter" / "specs" / (str(archetype) + ".json")
    if not p.is_file():
        return False
    return json.loads(p.read_text(encoding="utf-8")).get("fire_escape_stack") == "front"


def main():
    n, mission, seed = sys.argv[1], sys.argv[2], sys.argv[3]
    p = F / "workspaces" / f"cold-{n}-ws" / ".level_factory" / "temp" / mission / f"candidate_{seed}" / "site.json"
    spec = json.loads(p.read_text(encoding="utf-8"))
    roads, blockers = spec.get("roads") or [], spec.get("blockers") or []
    walkups = sorted((b for b in blockers if _walkup(b.get("archetype"))), key=lambda b: b["at"][0])
    if not roads or not walkups:
        sys.exit(f"UNKNOWN SHAPE: {len(roads)} road(s), {len(walkups)} walk-up blocker(s) in {p}")
    through = roads[0]
    y_road = (float(through["a"][1]) + float(through["b"][1])) / 2.0
    half = float(through["width"]) / 2.0 + float(through.get("sidewalk") or 0.0) / 2.0
    args = []
    for i, b in enumerate(walkups):
        x, y = float(b["at"][0]), float(b["at"][1])
        north = y > y_road
        eye = y_road - half if north else y_road + half
        front = y - float(b["size_y"]) / 2.0 if north else y + float(b["size_y"]) / 2.0
        name = f"walkup_{i}_{b['archetype']}"
        print(f"# {name}: block centre ({x:.2f}, {y:.2f}), {b['size_x']} x {b['size_y']} m, "
              f"{'north' if north else 'south'} of the road; eye at plan ({x:.2f}, {eye:.3f}), looking at its front "
              f"line y {front:.3f}", file=sys.stderr)
        args.append(f"--station {name}:{x:.3f},{EYE},{-eye:.3f},{x:.3f},{LOOK},{-front:.3f}")
    print(" ".join(args))


if __name__ == "__main__":
    main()
