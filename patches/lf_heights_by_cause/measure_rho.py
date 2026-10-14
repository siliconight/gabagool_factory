"""Heights by cause, measured: the rank correlation of a block's distance from the action with its height, the deal
alone against heights by cause (Level Factory 0.204.0, factory roadmap 241).

    python patches/lf_heights_by_cause/measure_rho.py

Over 120 walls -- forty seeds, the action's centre at x 0, -40 and 55 on a 180 m plate, the six wide mid-rises as
`tests/unit/test_urban_heights_by_cause.py` holds them -- it runs `empties.terrace` twice: with ``heights=None``,
which 0.204.0 deals exactly as 0.203.0 did, and with the shells' tops. Prints each arm's Spearman rho (min, median,
max) and the walls' block counts. First run on `patch_lf_heights_by_cause.py --preview`'s copy of the code before
the patch was applied, and it read what this reads on the applied code: -0.69 / +0.03 / +0.77 dealt alone,
+0.58 / +0.82 / +0.92 by cause. Prints what it measured and stops.
"""
import pathlib
import statistics as st
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "level_factory"))
from packages.pipeline import empties, site_variation  # noqa: E402

EXT = {"a": (-7.5, 7.5, -7.5, 7.5), "b": (-9.0, 9.0, -7.5, 7.5), "c": (-10.5, 10.5, -7.5, 7.5),
       "d": (-8.25, 8.25, -7.5, 7.5), "e": (-12.0, 12.0, -7.5, 7.5), "f": (-9.75, 9.75, -7.5, 7.5)}
TOP = {"a": 16.5, "b": 19.8, "c": 22.7, "d": 26.2, "e": 32.5, "f": 38.7}
ROWS = [{"id": k} for k in EXT]
THROUGH = {"a": [-90.0, -27.65], "b": [90.0, -27.65], "width": 10.0, "sidewalk": 3.0}


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
    return cov / ((sum((a - mx) ** 2 for a in rx) * sum((b - my) ** 2 for b in ry)) ** 0.5)


def main():
    for label, heights in (("dealt alone", None), ("by cause", TOP)):
        rhos, counts = [], []
        for seed in range(1, 41):
            for action in (0.0, -40.0, 55.0):
                placed, _ = empties.terrace(ROWS, EXT, site_variation.stream(seed), [THROUGH], 180.0,
                                            continuous=True, action=action, heights=heights)
                rhos.append(_rho([abs(p["at"][0] - action) for p in placed], [TOP[p["archetype"]] for p in placed]))
                counts.append(len(placed))
        print(f"{label:11s}: rho min {min(rhos):+.2f}  median {st.median(rhos):+.2f}  max {max(rhos):+.2f}; "
              f"blocks a wall {min(counts)}-{max(counts)}")


if __name__ == "__main__":
    main()
