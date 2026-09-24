#!/usr/bin/env python3
"""Measure how much Lot's SITE PLANS actually vary.

WHY THIS EXISTS. Roadmap item 105 says "Lot builds one arrangement of buildings
and nothing varies it", and it says the first step is measurement rather than
more arrangements: "Until that number exists, 'more arrangements' is a
preference and not a target." `tools/repetition_census.py` answers the same
question one scale down, for the modules composing a facade. Nothing answered
it for the site.

Item 37 closed when a cold run shipped three DISTINCT BUILDINGS. That fixed the
buildings and left the plan alone -- how many, where they sit relative to one
another, what shape the space between them takes, which way they face. A site
of distinct buildings in the same footprint every time is one level shape
wearing different clothes, and interventions-per-level cannot see the
difference: every one of those runs scores zero.

WHAT IT MEASURES. It reads `site.site.gameplay.json` -- Lot's own output, the
plan as assembled rather than as briefed -- and reports, per plan: the
buildings' placements and rotations, the site rectangle, how much of it the
footprints cover, the gaps between neighbours, and how close the building
centres sit to a single straight line. Across plans it reports the rotation and
count vocabularies, and a pairwise distance between normalised plans.

WHAT IT DELIBERATELY DOES NOT DO, following `repetition_census.py`'s stance
exactly:

  * It does not decide whether a corpus is too repetitive. That threshold is a
    taste call and this tool has no taste. Pick the gate from the numbers.
  * It does not attribute variation to a cause. The same distance can come from
    a seed, a `site_shape`, a different building count or a different footprint
    library, and one reading cannot separate them.
  * It does not score a single plan. Variation is a property of a SET, so a
    corpus of one is refused rather than reported on.

THE ONE NUMBER, if you only read one: `plan_distance.median`. Two plans are
compared after each is translated so its site rectangle is centred on the
origin and scaled so its diagonal is 1, so the figure is a fraction of the site
diagonal and is comparable across missions of different size. A median near 0
means the corpus is one arrangement; there is no value at which it becomes
"enough", which is the point of the paragraph above.

WHAT THIS RULER CANNOT SEE, said up front. It measures WHERE THE BOXES SIT. It
says nothing about whether the space between them is fightable -- sightlines,
cover, how many approaches reach an objective. Item 105 names that risk
directly: "adding plan variety without a sightline or cover measurement is how
a site becomes traversable but unfightable". So a good number here is a
necessary condition and not a sufficient one, and anybody quoting it as
evidence the sites play well is quoting it wrongly.

Usage:
    python tools/site_plan_census.py                     # scan workspaces/
    python tools/site_plan_census.py <dir-or-file> ...
    python tools/site_plan_census.py --json out.json
"""
from __future__ import annotations

import argparse
import glob
import json
import math
import os
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PLAN_NAME = "site.site.gameplay.json"
#: Two normalised plans this close are the same arrangement for reporting
#: purposes. NOT a quality threshold -- it is the precision at which two
#: placements are indistinguishable after rounding through Lot's own 4-decimal
#: manifests, expressed as a fraction of the site diagonal.
SAME_PLAN_EPS = 0.005


# --------------------------------------------------------------- reading
def find_plans(targets) -> list:
    """Every site plan under the given files or directories.

    `os.walk`, NOT `glob`, and the reason is the whole corpus. Every plan lives
    under `<workspace>/.level_factory/jobs/...`, and neither `glob.glob` nor
    `Path.rglob` matches a path component beginning with a dot -- so the
    obvious `**/site.site.gameplay.json` returns ZERO against 93 files on disk
    and the census reports an empty corpus rather than an error. A finder that
    silently sees nothing is the worst shape a measurement can take.
    """
    out = []
    for t in targets:
        p = Path(t)
        if p.is_file():
            out.append(p)
        elif p.is_dir():
            for dirpath, _dirnames, filenames in os.walk(p):
                if PLAN_NAME in filenames:
                    out.append(Path(dirpath) / PLAN_NAME)
    return sorted(out)


def by_producer(paths) -> dict:
    """Split the files by WHICH JOB WROTE THEM, before any of them is counted.

    348 files on disk are not 348 plans, and measuring variation over them
    would have been this tool's first wrong answer. Lot writes ONE plan per
    candidate, in its `lot_assemble` job; every other copy is that same plan
    staged somewhere else:

        jobs/<m>.lot_assemble.candidate.seed_N/1/out/   the plan      <- source
        jobs/<m>.lot_assemble.candidate.seed_N/out/     the same file
        staging/<m>.laser_tag_evaluate.candidate.seed_N/ staged for the evaluator
        staging/<m>.walktest_navqa.candidate.seed_N/     staged for the walktest
        jobs/<m>.themed_site_assemble/                   re-assembled, same plan

    So one plan appears up to five times, every copy is identical, and a
    distance distribution over that corpus is pulled toward zero by its own
    bookkeeping -- inventing exactly the "identical pairs" the tool exists to
    look for. CLAUDE.md's first rule, in the shape it actually arrives in:
    name what produced an artefact before concluding anything from it.
    """
    groups = {"lot_assemble": [], "staged_copy": [], "themed_reassembly": [],
              "other": []}
    for p in paths:
        parts = p.parts
        if any(".lot_assemble." in q for q in parts):
            groups["lot_assemble"].append(p)
        elif any(".themed_site_assemble" in q for q in parts):
            groups["themed_reassembly"].append(p)
        elif "staging" in parts:
            groups["staged_copy"].append(p)
        else:
            groups["other"].append(p)
    return groups


def dedupe_attempts(paths) -> list:
    """One file per job directory.

    A job keeps its numbered attempt (`1/out/...`) and a convenience copy at
    `out/...`. Keyed on the job directory rather than on a string substitution,
    because the obvious `replace("/out/", "/1/out/")` maps the two onto
    DIFFERENT keys and silently keeps both.
    """
    best = {}
    for p in paths:
        parts = list(p.parts)
        job = None
        for i, q in enumerate(parts):
            if ".lot_assemble." in q or ".themed_site_assemble" in q:
                job = os.sep.join(parts[:i + 1])
                break
        key = job or str(p.parent)
        # a numbered attempt is the record; `out/` is the convenience copy
        numbered = any(q.isdigit() for q in parts)
        if key not in best or (numbered and not best[key][0]):
            best[key] = (numbered, p)
    return [v[1] for v in best.values()]


def label(path: Path) -> tuple:
    """(mission, candidate) read from the job directory name.

    NAME WHAT PRODUCED THE ARTEFACT. A plan is only comparable to another from
    the same mission brief; grouping by a guessed key would compare a club
    block against a bank job and call the difference variation.
    """
    for part in path.parts:
        if ".lot_assemble." in part:
            mission, _, cand = part.partition(".lot_assemble.")
            return mission, cand
    return path.parent.name, path.stem


# --------------------------------------------------------------- geometry
def _centres(buildings) -> list:
    return [(float(b["at"][0]), float(b["at"][1])) for b in buildings]


def _footprint_area(buildings) -> float:
    tot = 0.0
    for b in buildings:
        fp = b.get("footprint") or [0, 0]
        tot += float(fp[0]) * float(fp[1])
    return tot


def _collinearity(centres, diag) -> float:
    """RMS distance of the centres from their best-fit line, over the site
    diagonal. Near 0 means the buildings sit in a row.

    Total-least-squares rather than a y-on-x fit, because a north-south street
    is exactly as much a row as an east-west one and an ordinary regression
    would report the first as scattered."""
    n = len(centres)
    if n < 3:
        return 0.0          # two points are always collinear; say so plainly
    mx = sum(c[0] for c in centres) / n
    my = sum(c[1] for c in centres) / n
    sxx = sum((c[0] - mx) ** 2 for c in centres)
    syy = sum((c[1] - my) ** 2 for c in centres)
    sxy = sum((c[0] - mx) * (c[1] - my) for c in centres)
    # principal axis of the covariance; the residual is the minor eigenvalue
    tr, det = sxx + syy, sxx * syy - sxy * sxy
    disc = max(tr * tr / 4.0 - det, 0.0)
    minor = tr / 2.0 - math.sqrt(disc)
    rms = math.sqrt(max(minor, 0.0) / n)
    return rms / diag if diag > 0 else 0.0


def _gaps(buildings) -> list:
    """Edge-to-edge gap to the nearest other building, per building.

    Axis-aligned rectangles from `at` and `footprint`. Lot rotates buildings in
    90-degree steps, so a rotation swaps the footprint's two extents rather
    than producing an oriented box -- handled here rather than assumed away.
    """
    rects = []
    for b in buildings:
        cx, cy = float(b["at"][0]), float(b["at"][1])
        fp = b.get("footprint") or [0, 0]
        w, d = float(fp[0]), float(fp[1])
        if int(round(float(b.get("rot", 0)) / 90.0)) % 2 == 1:
            w, d = d, w
        rects.append((cx - w / 2, cy - d / 2, cx + w / 2, cy + d / 2))
    out = []
    for i, a in enumerate(rects):
        best = None
        for j, c in enumerate(rects):
            if i == j:
                continue
            dx = max(c[0] - a[2], a[0] - c[2], 0.0)
            dy = max(c[1] - a[3], a[1] - c[3], 0.0)
            g = math.hypot(dx, dy)
            best = g if best is None else min(best, g)
        if best is not None:
            out.append(best)
    return out


def read_plan(path: Path) -> dict:
    """One plan's measurements, or a row saying why it could not be measured.

    An unreadable plan is REPORTED, not skipped. A census that quietly drops
    what it cannot parse reports on a corpus it chose, which is the defect
    CLAUDE.md records under "a number that silently describes four fifths of a
    table is worse than no number".
    """
    mission, cand = label(path)
    row = {"path": str(path), "mission": mission, "candidate": cand,
           "ok": False, "error": ""}
    try:
        d = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        row["error"] = f"unreadable: {exc}"
        return row
    buildings = [b for b in (d.get("buildings") or [])
                 if isinstance(b.get("at"), (list, tuple))
                 and len(b["at"]) >= 2]
    if not buildings:
        row["error"] = "no buildings carrying an `at`"
        return row
    rect = ((d.get("ground_extent") or {}).get("rect")
            or (d.get("ground_extent") or {}).get("declared"))
    if not (isinstance(rect, (list, tuple)) and len(rect) == 4):
        row["error"] = "no ground_extent rect"
        return row
    x0, y0, x1, y1 = (float(v) for v in rect)
    w, h = abs(x1 - x0), abs(y1 - y0)
    diag = math.hypot(w, h)
    centres = _centres(buildings)
    gaps = _gaps(buildings)
    fa = _footprint_area(buildings)
    row.update({
        "ok": True,
        "buildings": len(buildings),
        "rotations": sorted({int(round(float(b.get("rot", 0)))) % 360
                             for b in buildings}),
        "site_w": round(w, 2), "site_h": round(h, 2),
        "site_aspect": round(max(w, h) / min(w, h), 3) if min(w, h) > 0 else 0.0,
        "site_area": round(w * h, 1),
        "footprint_area": round(fa, 1),
        "coverage": round(fa / (w * h), 4) if w * h > 0 else 0.0,
        "gap_min": round(min(gaps), 2) if gaps else None,
        "gap_median": round(statistics.median(gaps), 2) if gaps else None,
        "gap_max": round(max(gaps), 2) if gaps else None,
        "collinearity": round(_collinearity(centres, diag), 4),
        # normalised for cross-plan comparison: site rect centred, diagonal 1
        "_norm": [(((c[0] - (x0 + x1) / 2) / diag),
                   ((c[1] - (y0 + y1) / 2) / diag)) for c in centres],
    })
    return row


# ----------------------------------------------------------- across plans
def plan_distance(a: dict, b: dict) -> float:
    """Symmetric mean nearest-centre distance between two normalised plans,
    as a fraction of the site diagonal.

    Symmetrised deliberately: a plan of two buildings sitting on top of two of
    another plan's five would otherwise read as identical from one side."""
    pa, pb = a["_norm"], b["_norm"]
    if not pa or not pb:
        return float("nan")

    def one_way(p, q):
        return sum(min(math.dist(u, v) for v in q) for u in p) / len(p)
    return (one_way(pa, pb) + one_way(pb, pa)) / 2.0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("targets", nargs="*",
                    default=[str(ROOT / "workspaces")],
                    help="site plan files or directories to scan")
    ap.add_argument("--json", type=Path, help="write the full report here")
    ap.add_argument("--by-mission", action="store_true",
                    help="report each mission separately as well")
    args = ap.parse_args(argv)

    found = find_plans(args.targets)
    groups = by_producer(found)
    chosen = dedupe_attempts(groups["lot_assemble"])

    print(f"site plan census: {len(found)} file(s) named {PLAN_NAME} on disk")
    print(f"  lot_assemble (the producer)  {len(groups['lot_assemble']):4d}"
          f"  -> {len(chosen)} after collapsing each job's duplicate copy")
    for k, why in (("staged_copy", "staged for another job, same plan"),
                   ("themed_reassembly", "re-assembled, same plan"),
                   ("other", "unattributed")):
        if groups[k]:
            print(f"  {k:<28} {len(groups[k]):4d}  EXCLUDED: {why}")

    rows = [read_plan(p) for p in chosen]
    ok = [r for r in rows if r["ok"]]
    bad = [r for r in rows if not r["ok"]]

    print(f"\n  measured {len(ok)}, refused {len(bad)}")
    for r in bad[:10]:
        print(f"  REFUSED {r['candidate']}: {r['error']}")
    if len(ok) < 2:
        print("\nREFUSED: variation is a property of a SET. Fewer than two "
              "plans measured, so there is nothing to compare and no number "
              "below would mean anything.")
        return 2

    missions = sorted({r["mission"] for r in ok})
    counts = sorted({r["buildings"] for r in ok})
    rots = sorted({v for r in ok for v in r["rotations"]})
    print(f"\n  missions            {len(missions)}: "
          f"{', '.join(missions[:4])}{' ...' if len(missions) > 4 else ''}")
    print(f"  building counts     {counts}")
    print(f"  ROTATION VOCABULARY {rots}   <- every orientation Lot ever used")

    def dist(vals, unit=""):
        return (f"min {min(vals):.3f}{unit}  median "
                f"{statistics.median(vals):.3f}{unit}  max {max(vals):.3f}{unit}")

    print(f"\n  coverage            {dist([r['coverage'] for r in ok])}"
          "   (footprint area / site area)")
    print(f"  collinearity        {dist([r['collinearity'] for r in ok])}"
          "   (0 = the centres sit in a straight line)")
    g = [r["gap_median"] for r in ok if r["gap_median"] is not None]
    if g:
        print(f"  neighbour gap       {dist(g, ' m')}   (median per plan)")
    asp = [r["site_aspect"] for r in ok]
    print(f"  site aspect         {dist(asp)}")

    # pairwise distances WITHIN a mission: two plans of different briefs are
    # not supposed to look alike, so pooling them would flatter the number
    report_groups = {}
    for m in missions:
        grp = [r for r in ok if r["mission"] == m]
        if len(grp) < 2:
            continue
        ds = [plan_distance(grp[i], grp[j])
              for i in range(len(grp)) for j in range(i + 1, len(grp))]
        same = sum(1 for d in ds if d < SAME_PLAN_EPS)
        report_groups[m] = {"plans": len(grp), "pairs": len(ds),
                            "min": min(ds), "median": statistics.median(ds),
                            "max": max(ds), "identical_pairs": same}

    if report_groups:
        print("\n  PLAN DISTANCE, within one mission brief "
              "(fraction of the site diagonal)")
        print("  %-28s %5s %6s %7s %7s %7s %s"
              % ("mission", "plans", "pairs", "min", "median", "max",
                 "identical"))
        for m, v in sorted(report_groups.items()):
            print("  %-28s %5d %6d %7.4f %7.4f %7.4f %d"
                  % (m, v["plans"], v["pairs"], v["min"], v["median"],
                     v["max"], v["identical_pairs"]))

    if args.by_mission:
        print("\n  per plan")
        print("  %-30s %4s %-12s %8s %8s %8s"
              % ("candidate", "bld", "rotations", "coverage", "collin", "gap"))
        for r in ok:
            print("  %-30s %4d %-12s %8.4f %8.4f %8s"
                  % (r["candidate"][:30], r["buildings"],
                     ",".join(str(x) for x in r["rotations"]),
                     r["coverage"], r["collinearity"],
                     "-" if r["gap_median"] is None else f"{r['gap_median']:.2f}"))

    print("\n  This tool reports numbers and picks no threshold. It measures "
          "where the boxes sit, not whether the space between them is "
          "fightable -- see roadmap item 105.")

    if args.json:
        for r in rows:
            r.pop("_norm", None)
        args.json.write_text(json.dumps(
            {"schema": "lf.site_plan_census.v1", "measured": len(ok),
             "refused": len(bad), "rotation_vocabulary": rots,
             "building_counts": counts, "by_mission": report_groups,
             "plans": rows}, indent=1), encoding="utf-8")
        print(f"  wrote {args.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
