"""How far short of a run's end an urban wall with corners stops: Level Factory 0.206.0 against a fresh deal in
`_cornered`'s fill (roadmap 241, the corner shop; measured before the change is written).

    python patches/lf_corner_fill/measure_remainder.py

Cold run 9295's seed_9003 stopped its far wall 12.70 m short of the plate's working end, after its closing corner;
9294's three candidates stopped 3.70, 1.20 and 3.20 m short, and 9295's other two 1.20 and 4.70. `_cornered` stops
filling when nothing LEFT ON THE BAG fits before the room it keeps for the closing corner -- the condition
`infill` met on the near side and answered in 0.203.0 with a fresh deal behind the remainder.

This runs both on the same walls: the factory's thirteen designs at their built widths (read off cold run 9295's
blockers) and heights (storeys x 3.1 m plus the parapet, as `street_line.shell_top` reads them), the three
candidates' plates (171, 173 and 181 m) and the through road at y -21.665, no action and four actions (the three
candidates' centres and one east of them), seeds 1-40 -- 600 walls.
PREVIEW is `_cornered` with one change: where nothing on the bag fits before the closing corner's room and some
design does, a fresh deal goes behind the remainder (and, without heights, the next dealt that fits is taken,
as `infill` takes it, where 0.206.0 took the bag's next only). Prints, for each: the remainder after the run's closing block
(median, 90th percentile, max, count over 6.6 m -- the narrowest design), how many walls open and close on a corner,
and how many put a corner anywhere else. Prints what it measured and stops.
"""
import pathlib
import statistics
import sys

F = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(F / "level_factory"))
from packages.pipeline import empties, site_variation  # noqa: E402
from packages.pipeline.empties import (_blocked, _by_height, _corner_at, _deal, _far_side, _runs, _turned,  # noqa: E402
                                       _width, CLEARANCE)

#: built width (m), storeys, parapet (m) -- `deli_counter/presets.py`'s tables and cold run 9295's blockers
MIDRISES = {"gs_midrise_a": (15.3, 5, 1.0), "gs_midrise_b": (18.3, 6, 1.2), "gs_midrise_c": (21.3, 7, 1.0),
            "gs_midrise_d": (16.8, 8, 1.4), "gs_midrise_e": (24.3, 10, 1.5), "gs_midrise_f": (19.8, 12, 1.5),
            "gs_midrise_g": (12.3, 6, 1.0), "gs_midrise_h": (10.3, 5, 1.0), "gs_midrise_i": (6.6, 4, 0.8)}
CORNERS = {"gs_cornershop_a": (15.3, 6, 1.0), "gs_cornershop_b": (18.3, 8, 1.2), "gs_cornershop_c": (12.3, 5, 1.0),
           "gs_cornershop_d": (16.8, 7, 1.4)}
EXT = {k: (-w / 2.0, w / 2.0, -7.65, 7.65) for k, (w, _f, _c) in {**MIDRISES, **CORNERS}.items()}
TOP = {k: round(f * 3.1 + c, 3) for k, (_w, f, c) in {**MIDRISES, **CORNERS}.items()}
ROWS = [{"id": k, "family": "empty"} for k in MIDRISES] + [{"id": k, "family": "corner"} for k in CORNERS]
NARROWEST = min(w for w, _f, _c in MIDRISES.values())


def preview_no_repeat(*a, **k):
    """`preview`, but stopping rather than stand a block beside itself after the fresh deal."""
    return preview(*a, no_repeat=True, **k)


def preview_stuck(*a, **k):
    """`preview`, dealing afresh also where the only block on the bag that fits is the one just placed and
    another design fits: a block stands beside itself only where no other design fits."""
    return preview(*a, stuck=True, **k)


def preview(usable, corners, extents, stream, roads, span_x, action=None, heights=None, no_repeat=False,
            stuck=False):
    """`empties._cornered` as 0.206.0 has it, but for the fresh deal marked below."""
    edge, line = _far_side(roads[0])
    x0 = -float(span_x) / 2.0 + CLEARANCE
    x1 = float(span_x) / 2.0 - CLEARANCE
    by_cause = bool(action is not None and heights
                    and all(heights.get(r["id"]) is not None for r in usable))
    if by_cause:
        lo = min(heights[r["id"]] for r in usable)
        hi = max(heights[r["id"]] for r in usable)
        reach = max(float(action) - x0, x1 - float(action))
    out, need, prev, bag, cbag = [], 0.0, None, [], []

    def place(pick, x):
        nonlocal need
        tx0, tx1, ty0, ty1 = _turned(extents[pick["id"]], 180)
        at_y = line - ty1
        out.append({"id": f"e{len(out)}", "archetype": pick["id"],
                    "at": [round(x - tx0, 3), round(at_y, 3)], "rot": 180,
                    "size_x": round(tx1 - tx0, 3), "size_y": round(ty1 - ty0, 3),
                    "front": round(at_y + ty1, 3)})
        need = max(need, -(at_y + ty0))
        return tx1 - tx0

    def fit(bag, x, end):
        if by_cause:
            return _by_height(bag, extents, heights, x, end, float(action), reach, lo, hi, prev)
        # THE CHANGE, without heights: the next dealt that fits, as `infill` takes it
        return next((i for i in range(len(bag) - 1, -1, -1) if x + _width(extents, bag[i]["id"]) <= end), None)

    for a, b in _runs(x0, x1, _blocked(roads, edge)):
        x, end, opened = a, b, None
        if not cbag:
            cbag = _deal(corners, stream)
        at = _corner_at(cbag, extents, b - a)
        if at is not None:
            pick = cbag.pop(at)
            opened = pick["id"]
            x += place(pick, x)
            others = [_width(extents, r["id"]) for r in corners if r["id"] != opened]
            end = b - min(others or [_width(extents, opened)])
        while True:
            if not bag:
                bag = _deal(usable, stream, prev)
            i = fit(bag, x, end)
            if stuck and i is not None and bag[i]["id"] == prev and any(
                    r["id"] != prev and x + _width(extents, r["id"]) <= end for r in usable):
                bag = _deal(usable, stream, prev) + bag          # only the last block fits on the bag
                i = fit(bag, x, end)
            if i is None and any(x + _width(extents, r["id"]) <= end for r in usable):
                bag = _deal(usable, stream, prev) + bag          # THE CHANGE: a fresh deal behind the remainder
                i = fit(bag, x, end)
                if no_repeat and i is not None and bag[i]["id"] == prev:
                    i = None
            if i is None:
                break
            pick = bag.pop(i)
            prev = pick["id"]
            x += place(pick, x)
        if opened is None:
            continue
        at = _corner_at(cbag, extents, b - x, widest=True, not_id=opened)
        if at is None or cbag[at]["id"] == opened:
            cbag = _deal(corners, stream, opened) + cbag
            at = _corner_at(cbag, extents, b - x, widest=True, not_id=opened)
        if at is not None:
            place(cbag.pop(at), x)
    return out, need


def _wall(fn, seed, span, action):
    through = {"a": [-span / 2.0, -21.665], "b": [span / 2.0, -21.665], "width": 10.0, "sidewalk": 3.0}
    usable = [r for r in ROWS if r["family"] == "empty"]
    corners = [r for r in ROWS if r["family"] == "corner"]
    return fn(usable, corners, EXT, site_variation.stream(seed), [through], float(span), action,
              TOP if action is not None else None)[0], span


def _report(name, fn):
    rems, closed, stray, alike = [], 0, 0, 0
    for span in (171, 173, 181):
        for action in (None, -2.5, -28.5, -27.0, 30.0):
            for seed in range(1, 41):
                placed, sp = _wall(fn, seed, span, action)
                x1 = sp / 2.0 - CLEARANCE
                rems.append(x1 - (placed[-1]["at"][0] + placed[-1]["size_x"] / 2.0))
                kinds = [p["archetype"] in CORNERS for p in placed]
                closed += kinds[0] and kinds[-1]
                stray += any(kinds[1:-1])
                alike += sum(a["archetype"] == b["archetype"] for a, b in zip(placed, placed[1:]))
    rems.sort()
    print(f"{name}: {len(rems)} walls; remainder after the closing block median {statistics.median(rems):.2f} m, "
          f"90th {rems[int(0.9 * len(rems))]:.2f}, max {rems[-1]:.2f}; over {NARROWEST} m: "
          f"{sum(r > NARROWEST for r in rems)}; opened and closed on a corner: {closed}; a corner mid-wall: {stray}; "
          f"neighbours alike: {alike}")


if __name__ == "__main__":
    _report("0.206.0", empties._cornered)
    _report("preview", preview)
    _report("preview, no repeat", preview_no_repeat)
    _report("preview, a stuck bag dealt afresh too", preview_stuck)
