"""The near side's blocks, candidate by candidate, across cold runs (roadmap 241).

    python docs/findings/urban_street/near_blocks.py <mission> <cold run N> [<cold run N> ...]

Reads each candidate's site spec as Level Factory wrote it (`workspaces/cold-N-ws/.level_factory/temp/<mission>/
candidate_seed_<S>/site.json`, the `lot_assemble` job's input) and prints, per seed and run, every near-side Empty
(`blockers` whose id starts with `n`): its shell, and the span it stands on along the near line (x0 to x1, site
metres, from `at` and `size_x`; the near side's blocks all stand at rot 0). Then each run's count per seed.
Prints what it measured and stops.
"""
import json
import pathlib
import re
import sys

F = pathlib.Path(__file__).resolve().parents[3]


def _near(spec):
    out = []
    for bk in spec.get("blockers") or []:
        if str(bk.get("id", "")).startswith("n"):
            x, w = float(bk["at"][0]), float(bk["size_x"])
            out.append((x - w / 2.0, x + w / 2.0, bk["archetype"]))
    return sorted(out)


def main():
    mission, runs = sys.argv[1], sys.argv[2:]
    seen = {}
    for n in runs:
        temp = F / "workspaces" / f"cold-{n}-ws" / ".level_factory" / "temp" / mission
        for d in sorted(temp.glob("candidate_seed_*")):
            seed = int(re.search(r"(\d+)$", d.name).group(1))
            spec = d / "site.json"
            if spec.exists():
                seen.setdefault(seed, {})[n] = _near(json.loads(spec.read_text(encoding="utf-8")))
    for seed in sorted(seen):
        print(f"seed_{seed}")
        for n in runs:
            blocks = seen[seed].get(n)
            if blocks is None:
                print(f"   {n}: no site spec")
                continue
            print(f"   {n}: {len(blocks)} -- " + ", ".join(f"{a} {x0:.2f} to {x1:.2f} ({x1 - x0:.2f} m)"
                                                       for x0, x1, a in blocks))


if __name__ == "__main__":
    main()
