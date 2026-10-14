"""The street's furniture, counted: by species, and the through road's trees by kerb (roadmap 241, street trees).

    python docs/findings/urban_street/street_counts.py <mission> <seed> <cold run N> [<cold run N> ...]

Reads each run's `lot_assemble` job for the candidate (`workspaces/cold-N-ws/.level_factory/jobs/<mission>.
lot_assemble.candidate.<seed>/1/out/site.site.gameplay.json`, its `furniture_plan.placed`) and prints, per run,
the count of every species Lot's street furniture stood, then the through road's trees (road 0) on each kerb with
the gaps between neighbours along it, in metres. Prints what it measured and stops.
"""
import collections
import json
import pathlib
import sys

F = pathlib.Path(__file__).resolve().parents[3]
TREES = ("street_tree", "red_maple", "pin_oak", "honey_locust", "london_plane", "callery_pear")


def main():
    mission, seed, runs = sys.argv[1], sys.argv[2], sys.argv[3:]
    for n in runs:
        g = F / "workspaces" / f"cold-{n}-ws" / ".level_factory" / "jobs" / \
            f"{mission}.lot_assemble.candidate.{seed}" / "1" / "out" / "site.site.gameplay.json"
        placed = json.loads(g.read_text(encoding="utf-8")).get("furniture_plan", {}).get("placed")
        if not isinstance(placed, list):
            print(f"{n}: UNKNOWN SHAPE, no furniture_plan.placed in {g}")
            continue
        by = collections.Counter("tree" if p.get("species") in TREES else p.get("species") for p in placed)
        print(f"{n} {seed}: " + ", ".join(f"{k} {v}" for k, v in sorted(by.items())))
        for kerb in ("L", "R"):
            ts = sorted(float(p["t"]) for p in placed
                        if p.get("species") in TREES and p.get("road") == 0 and p.get("kerb") == kerb)
            gaps = [round(b - a, 2) for a, b in zip(ts, ts[1:])]
            print(f"   through road, kerb {kerb}: {len(ts)} trees; gaps {gaps}")


if __name__ == "__main__":
    main()
