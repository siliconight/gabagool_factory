"""The verdict on a price, and the action it prescribes -- the same rule every time.

    python tools/price_verdict.py <control_a.json> <control_b.json> <subject.json> [--json <out>]
    python tools/price_verdict.py --dir docs/findings/bank_interior --prefix perf_rows_

A PRICE is three runs of Level Factory's fixed-station harness (`level_factory/tools/perf_stations_run.py`) in one
session: a control, the subject, the same control again. The controls are the same bytes, so where they disagree is
the instrument's floor. This reads the three reports, compares the subject with the controls heading by heading, and
gives ONE verdict with ONE action (the walker, 2026-10-28: "clear actions should be taken from the pricing that
becomes standardized").

THE RULE. Every threshold is CHOSEN, not derived, and named here so it can be argued with:

  FAIL  -> do not release. Split the batch and price the halves until one change owns the cost; make that change
           cheaper (merge by material, MultiMesh, fewer materials, CLAUDE.md's order) or revert it.
     - a heading over budget (draws > --draws, p95 > --ms; the harness's own defaults) that no control was over;
     - the median heading's draws up more than DRAWS_MEDIAN_SHARE of the controls' median, and more than the
       controls' own largest draw disagreement: draw calls are the budget (CLAUDE.md);
     - the median heading's p95 up more than the controls' own LARGEST disagreement: the batch moves the typical
       view by more than the instrument's noise ever moved one.
  WATCH -> release, and look at the named headings' frames; record what moved there in the finding.
     - one heading's draws up more than HEADING_DRAWS_SHARE and more than HEADING_DRAWS_MIN;
     - one heading's p95 up more than the controls' largest disagreement;
     - a heading within NEAR_BUDGET of a budget;
     - the controls' own largest disagreement past FLOOR_MAX_MS: the floor every frame-time rule judges against is
       wide, so a real cost could pass under it -- re-price before trusting a PASS.
  PASS  -> release; record the price in the finding.

It never names a cause (CLAUDE.md: "a probe prints what it measured and stops"); it names the headings, the numbers
and the action. Refuses a report it does not recognise, three reports that do not hold the same headings, and an
incomplete run. Exit 0 PASS, 1 WATCH, 2 FAIL, 3 refused.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import statistics
import sys

DRAWS_MEDIAN_SHARE = 0.02
HEADING_DRAWS_SHARE = 0.05
HEADING_DRAWS_MIN = 20
NEAR_BUDGET = 0.10
#: just past the widest floor the bank's five prices of 2026-10-28 read (0.416-0.971 ms)
FLOOR_MAX_MS = 1.0
#: the harness's defaults (`perf_stations_run.DEFAULT_DRAWS`, `DEFAULT_MS`; docs/DRAW_CALL_BUDGET.md)
DEFAULT_DRAWS = 2000
DEFAULT_MS = 11.0
SCHEMA = "level_factory.perf_stations.v1"
ACTIONS = {
    "PASS": "Release. Record the price in the finding.",
    "WATCH": "Release, then look at the frames at the headings named above and record what moved there.",
    "FAIL": ("Do not release. Split the batch and price the halves until one change owns the cost; make it cheaper "
             "(merge by material, MultiMesh, fewer materials) or revert it."),
}


class Refused(Exception):
    pass


def load(path):
    d = json.loads(pathlib.Path(path).read_text(encoding="utf-8"))
    if d.get("schema") != SCHEMA or d.get("complete") is not True:
        raise Refused("%s is not a complete %s report" % (path, SCHEMA))
    out = {}
    for row in d.get("rows") or []:
        name = row.get("station") or row.get("name")
        if not name:
            raise Refused("%s has a row with no station" % path)
        for h in row.get("headings") or []:
            out[(name, h["yaw"])] = (int(h["draws"]), float(h["ms_p95"]))
    if not out:
        raise Refused("%s holds no headings" % path)
    return out


def verdict(a, b, s, draws_budget=DEFAULT_DRAWS, ms_budget=DEFAULT_MS):
    keys = sorted(set(a) & set(b) & set(s))
    if not keys or not (len(keys) == len(a) == len(b) == len(s)):
        raise Refused("the three reports hold different headings (%d, %d, %d; %d shared)"
                      % (len(a), len(b), len(s), len(keys)))
    mean = {k: ((a[k][0] + b[k][0]) / 2.0, (a[k][1] + b[k][1]) / 2.0) for k in keys}
    dd = {k: s[k][0] - mean[k][0] for k in keys}
    dp = {k: s[k][1] - mean[k][1] for k in keys}
    floor_draws = max(abs(a[k][0] - b[k][0]) for k in keys)
    floor_ms = max(abs(a[k][1] - b[k][1]) for k in keys)
    control_median_draws = statistics.median(m[0] for m in mean.values())
    fail, watch = [], []
    for k in keys:
        over = s[k][0] > draws_budget or s[k][1] > ms_budget
        was = any(c[k][0] > draws_budget or c[k][1] > ms_budget for c in (a, b))
        if over and not was:
            fail.append("%s yaw %s over budget: %d draws, %.2f ms p95" % (k[0], k[1], s[k][0], s[k][1]))
    med_dd, med_dp = statistics.median(dd.values()), statistics.median(dp.values())
    if med_dd > max(DRAWS_MEDIAN_SHARE * control_median_draws, floor_draws):
        fail.append("median heading draws %+.1f (over %.0f, %.0f%% of the controls' median %.0f)"
                    % (med_dd, DRAWS_MEDIAN_SHARE * control_median_draws, DRAWS_MEDIAN_SHARE * 100,
                       control_median_draws))
    if med_dp > floor_ms:
        fail.append("median heading p95 %+.3f ms, past the controls' largest disagreement %.3f" % (med_dp, floor_ms))
    for k in keys:
        if dd[k] > max(HEADING_DRAWS_SHARE * mean[k][0], HEADING_DRAWS_MIN):
            watch.append("%s yaw %s draws %+.0f (%d against %.0f)" % (k[0], k[1], dd[k], s[k][0], mean[k][0]))
        if dp[k] > floor_ms:
            watch.append("%s yaw %s p95 %+.3f ms, past the floor %.3f" % (k[0], k[1], dp[k], floor_ms))
        if s[k][0] > (1 - NEAR_BUDGET) * draws_budget or s[k][1] > (1 - NEAR_BUDGET) * ms_budget:
            watch.append("%s yaw %s near budget: %d draws, %.2f ms p95" % (k[0], k[1], s[k][0], s[k][1]))
    if floor_ms > FLOOR_MAX_MS:
        watch.insert(0, "the controls disagree by up to %.3f ms, past %.1f: the frame-time verdict is weak; re-price"
                     % (floor_ms, FLOOR_MAX_MS))
    name = "FAIL" if fail else ("WATCH" if watch else "PASS")
    return {"verdict": name, "action": ACTIONS[name], "headings": len(keys),
            "draws_median_delta": round(med_dd, 1), "draws_largest_delta": round(max(dd.values()), 1),
            "p95_median_delta_ms": round(med_dp, 3), "p95_largest_delta_ms": round(max(dp.values()), 3),
            "floor_draws": floor_draws, "floor_ms": round(floor_ms, 3),
            "budgets": {"draws": draws_budget, "ms_p95": ms_budget}, "fail": fail, "watch": watch}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("reports", nargs="*", help="control_a, control_b, subject")
    ap.add_argument("--dir")
    ap.add_argument("--prefix")
    ap.add_argument("--draws", type=int, default=DEFAULT_DRAWS)
    ap.add_argument("--ms", type=float, default=DEFAULT_MS)
    ap.add_argument("--json")
    args = ap.parse_args(argv)
    try:
        if args.dir and args.prefix:
            paths = [pathlib.Path(args.dir) / ("%s%s.json" % (args.prefix, t))
                     for t in ("control_a", "control_b", "subject")]
        elif len(args.reports) == 3:
            paths = [pathlib.Path(p) for p in args.reports]
        else:
            raise Refused("give three reports, or --dir and --prefix")
        v = verdict(*(load(p) for p in paths), draws_budget=args.draws, ms_budget=args.ms)
    except (Refused, OSError, ValueError, KeyError) as e:
        print("REFUSED: %s" % e)
        return 3
    print("%s over %d headings" % (v["verdict"], v["headings"]))
    print("  draws: median %+.1f, largest %+.1f (the controls' floor %d)"
          % (v["draws_median_delta"], v["draws_largest_delta"], v["floor_draws"]))
    print("  p95:   median %+.3f ms, largest %+.3f ms (the controls' floor %.3f ms)"
          % (v["p95_median_delta_ms"], v["p95_largest_delta_ms"], v["floor_ms"]))
    for line in v["fail"]:
        print("  FAIL  " + line)
    for line in v["watch"][:12]:
        print("  WATCH " + line)
    if len(v["watch"]) > 12:
        print("  ... %d more" % (len(v["watch"]) - 12))
    print("ACTION: " + v["action"])
    if args.json:
        pathlib.Path(args.json).write_text(json.dumps(v, indent=2) + "\n", encoding="utf-8")
    return {"PASS": 0, "WATCH": 1, "FAIL": 2}[v["verdict"]]


if __name__ == "__main__":
    sys.exit(main())
