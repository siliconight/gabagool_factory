"""The urban wall's heights, west to east, against the action (roadmap 241, heights by cause).

    python docs/findings/urban_street/wall_heights.py <mission> <cold run N> [<cold run N> ...]

Reads each candidate's site spec as Level Factory wrote it (`workspaces/cold-N-ws/.level_factory/temp/<mission>/
candidate_seed_<S>/site.json`) and the shells its `lot_assemble` job staged (`jobs/<mission>.lot_assemble.
candidate.seed_<S>/1/out/buildings/`). For each far-side Empty (`blockers` whose id starts with `e`), west to east:
its shell and its top (`street_line.shell_top`, metres above its floor). The action's centre is rebuilt as the
compose stage builds it (Level Factory 0.204.0): the middle of the span the spawn, objective and extraction
buildings cover, each building's rect from its `at`, `rot` and `site_variation.shell_footprint` of its staged
shell. Then the rank correlation (Spearman) of each block's distance from that centre with its top. Prints what
it measured and stops.
"""
import json
import pathlib
import re
import statistics as st
import sys

F = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(F / "level_factory"))
from packages.pipeline import empties, site_variation, street_line  # noqa: E402


def _ranks(v):
    order = sorted(range(len(v)), key=lambda i: v[i])
    r, i = [0.0] * len(v), 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and v[order[j + 1]] == v[order[i]]:
            j += 1
        for k in range(i, j + 1):
            r[order[k]] = (i + j) / 2.0
        i = j + 1
    return r


def _rho(x, y):
    rx, ry = _ranks(x), _ranks(y)
    mx, my = st.mean(rx), st.mean(ry)
    cov = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    den = (sum((a - mx) ** 2 for a in rx) * sum((b - my) ** 2 for b in ry)) ** 0.5
    return cov / den if den else float("nan")


def _one(ws, mission, seed):
    spec = json.loads((ws / "temp" / mission / f"candidate_seed_{seed}" / "site.json").read_text(encoding="utf-8"))
    out = ws / "jobs" / f"{mission}.lot_assemble.candidate.seed_{seed}" / "1" / "out"
    tops = {}
    wall = []
    for bk in spec.get("blockers") or []:
        if not str(bk.get("id", "")).startswith("e"):
            continue
        a = bk["archetype"]
        if a not in tops:
            tops[a] = street_line.shell_top(out / bk["glb"])
        wall.append((float(bk["at"][0]), a, tops[a]))
    wall.sort()
    ids = {spec.get(k) for k in ("spawn", "objective", "extraction")} - {None}
    rects = [empties.building_rect(b["at"], b["rot"], site_variation.shell_footprint(out / b["glb"]))
             for b in spec["buildings"] if b.get("id") in ids]
    centre = (min(r[0] for r in rects) + max(r[1] for r in rects)) / 2.0 if rects else None
    return wall, centre


def main():
    mission, runs = sys.argv[1], sys.argv[2:]
    for n in runs:
        ws = F / "workspaces" / f"cold-{n}-ws" / ".level_factory"
        for d in sorted((ws / "temp" / mission).glob("candidate_seed_*")):
            seed = int(re.search(r"(\d+)$", d.name).group(1))
            if not (ws / "jobs" / f"{mission}.lot_assemble.candidate.seed_{seed}").exists():
                continue
            wall, centre = _one(ws, mission, seed)
            if any(t is None for _x, _a, t in wall) or centre is None:
                print(f"{n} seed_{seed}: a top or the action's centre could not be read")
                continue
            rho = _rho([abs(x - centre) for x, _a, _t in wall], [t for _x, _a, t in wall])
            print(f"{n} seed_{seed}: action's centre x {centre:.1f}; rho {rho:+.2f}; west to east: "
                  + ", ".join(f"{a.replace('gs_midrise_', '')} {t:.1f} m @{x:.0f}" for x, a, t in wall))


if __name__ == "__main__":
    main()
