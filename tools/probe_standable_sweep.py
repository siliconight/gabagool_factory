#!/usr/bin/env python3
"""Step 1 of the standable-ground re-posing: MEASURE, change nothing.

Drives a real `lot.assemble` per seed with `site_cover.plan_cover` spied, so
the ground / rects / route / points the sweep uses are the ones the pipeline
actually passes -- not reconstructed, not guessed.

Then answers, per seed:

  * how many standable posts exist within OPENING_RANGE of the crew's route
  * how many route samples are exposed under the SIX ENEMY POINTS  (today)
  * how many route samples are exposed under the POSTS             (proposed)
  * how many raw PAIRS each produces, which is the number that would explode
  * wall clock for the sweep

READ-ONLY. Writes only into a temp directory it makes for assemble's output.

A NOTE ON HOW THE POSTS ARE NAMED
`site_cover.route_sightlines` selects threats with
`n.startswith(ENEMY_PREFIX)` (site_cover.py:567). To measure the proposed
mode WITHOUT editing shipped code, the posts are named `Enemy_post<N>` so the
existing function picks them up unchanged. The real change would parameterise
that prefix; this probe deliberately does not.

USAGE
    python _scratch\\probe_standable_sweep.py
"""
from __future__ import annotations

import math
import os
import shutil
import sys
import tempfile
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOT = os.path.join(ROOT, "lot")
if LOT not in sys.path:
    sys.path.insert(0, LOT)

TEMP = os.path.join(ROOT, "workspaces", "lot-demo-ws", ".level_factory",
                    "temp", "lot_demo_001")
SEEDS = (5017, 5118, 5219)

#: Sweep density, DECLARED rather than emergent. Along-route step and lateral
#: step in metres. 5 m x 5 m out to OPENING_RANGE either side.
ALONG_STEP = 5.0
LATERAL_STEP = 5.0
#: Posts are deduped onto this grid so density is a parameter, not an accident.
GRID = 2.5
#: Bearing bins for ARC EXPOSURE. 72 bins = 5 degrees each.
BEARING_BINS = 72
#: Candidate cover positions considered by the greedy upper bound. Capped and
#: DECLARED: the full post set would be 713 on seed_5219 and the scoring is
#: O(candidates x pairs). Sampled evenly across the post list.
GREEDY_CANDIDATES = 250
#: RESTRICTED candidate band. A COVER_SIZE piece at distance d from a route
#: sample subtends about 2*atan(COVER_SIZE/2/d): ~33 deg at 5 m, ~11 deg at
#: 15 m, ~4 deg at 45 m. Distant candidates cannot compete for arc, so
#: restricting to a band near the route should cost little and remove most of
#: the work. That "should" is what this run tests.
CANDIDATE_REACH = 12.0


DC_BUILD = os.path.join(ROOT, "deli_counter", "build")


def arc_bins(lines):
    """route@N -> set of occupied 5-degree bearing bins.

    THE MAGNITUDE MEASURE. Boolean exposure saturated at 100% on every
    candidate, so "is this sample exposed" carries no information. This asks
    HOW MUCH: of the 360 degrees around a route sample, what fraction holds a
    shooter with a clear line. Continuous, enemy-independent, and cover
    reduces it monotonically.

    Reuses the pairs route_sightlines already returns -- no extra raycasting.
    """
    width = 360.0 / BEARING_BINS
    per = {}
    for name, _other_name, sample, other, _length in lines:
        ang = math.degrees(math.atan2(other[1] - sample[1],
                                      other[0] - sample[0])) % 360.0
        per.setdefault(name, set()).add(int(ang // width))
    return per


def arc_stats(lines, samples):
    """(mean, min, max, per-sample list) over EVERY sample, zeros included."""
    per = arc_bins(lines)
    vals = []
    for i in range(len(samples)):
        vals.append(len(per.get(f"route@{i}", ())) / BEARING_BINS)
    if not vals:
        return 0.0, 0.0, 0.0, []
    return sum(vals) / len(vals), min(vals), max(vals), vals


def _greedy_arc(site_cover, site_spawns, lines, samples, candidates, budget,
                separation=None):
    """Place `budget` pieces to close the most bearing bins.

    A (sample, bin) key CLOSES only when every open line in it is blocked --
    arc reduction, not line breaking.

    Three things make this tractable where the first version took 31.1 s:

      * a bounding-box reject before the real segment test
      * per-candidate TOUCHED KEYS, so scoring a candidate iterates the ~50
        keys it can affect rather than all ~900
      * the caller restricts the candidate band (see CANDIDATE_REACH)

    `separation` enforces COVER_SEPARATION between chosen pieces, which the
    real planner does. Without it the bound flatters itself.

    Returns (mean arc after, pieces used, candidates considered, precompute s,
    greedy s).
    """
    width = 360.0 / BEARING_BINS
    keys = {}
    seg_box = []
    for idx, (sname, _pn, sample, other, _l) in enumerate(lines):
        ang = math.degrees(math.atan2(other[1] - sample[1],
                                      other[0] - sample[0])) % 360.0
        keys.setdefault((sname, int(ang // width)), set()).add(idx)
        seg_box.append((min(sample[0], other[0]), min(sample[1], other[1]),
                        max(sample[0], other[0]), max(sample[1], other[1])))
    if not keys:
        return 0.0, 0, len(candidates), 0.0, 0.0

    size = getattr(site_cover, "COVER_SIZE", 3.0)
    half = size / 2.0

    t0 = time.perf_counter()
    blocks = []
    for c in candidates:
        try:
            rect = site_cover._piece_rect(c, size)
        except Exception:
            continue
        cx0, cy0 = c[0] - half, c[1] - half
        cx1, cy1 = c[0] + half, c[1] + half
        hit = set()
        for idx, (_sn, _pn, sample, other, _l) in enumerate(lines):
            bx0, by0, bx1, by1 = seg_box[idx]
            if bx1 < cx0 or bx0 > cx1 or by1 < cy0 or by0 > cy1:
                continue
            if site_spawns._segment_crosses(sample, other, rect):
                hit.add(idx)
        if hit:
            touched = frozenset(k for k, v in keys.items() if v & hit)
            blocks.append((c, hit, touched))
    t_pre = time.perf_counter() - t0

    t1 = time.perf_counter()
    remaining = {k: set(v) for k, v in keys.items()}
    chosen, used = [], 0
    for _ in range(budget):
        best, best_gain = None, 0
        for c, hit, touched in blocks:
            if separation and any(math.dist(c, q) < separation for q in chosen):
                continue
            gain = 0
            for k in touched:
                r = remaining[k]
                if r and r <= hit:
                    gain += 1
            if gain > best_gain:
                best, best_gain = (c, hit, touched), gain
        if not best:
            break
        c, hit, touched = best
        for k in touched:
            remaining[k] -= hit
        chosen.append(c)
        used += 1
    t_loop = time.perf_counter() - t1

    per_sample = {}
    for (sname, b), r in remaining.items():
        if r:
            per_sample.setdefault(sname, set()).add(b)
    vals = [len(per_sample.get(f"route@{i}", ())) / BEARING_BINS
            for i in range(len(samples))]
    return ((sum(vals) / len(vals) if vals else 0.0), used, len(blocks),
            t_pre, t_loop)


def _near_route(posts, samples, reach):
    """Posts within `reach` of any route sample."""
    out = []
    for pt in posts:
        for s in samples:
            if math.dist(pt, s) <= reach:
                out.append(pt)
                break
    return out


def _spec_for(seed: int) -> str:
    return os.path.join(TEMP, f"candidate_seed_{seed}", "site.json")


def _stage(seed: int, tmp: str):
    """Rebuild the layout `_find_asset` needs: the spec, plus buildings/.

    `package._find_asset` looks for a .glb NEXT TO THE SITE SPEC first, then
    in <dc>/build/<name>. The spec names `buildings/<stem>.glb`, the library
    stores `<stem>.glb` at build/ root, and the pipeline's temp dir has been
    cleaned of the staged copies. So neither path resolves any more and a
    direct `assemble` silently falls back to DECLARED footprints.

    This copies the candidate dir and stages the .glb files the spec names,
    from the same library the pipeline used.
    """
    import json as _json
    src_dir = os.path.join(TEMP, f"candidate_seed_{seed}")
    work = os.path.join(tmp, "spec")
    shutil.copytree(src_dir, work)
    spec = _json.loads(open(os.path.join(work, "site.json"),
                            encoding="utf-8").read())
    staged, missing = 0, []
    for key in ("buildings", "blockers"):
        for b in spec.get(key, []) or []:
            rel = b.get("glb") or b.get("scene")
            if not rel:
                continue
            stem = os.path.basename(rel)
            src = os.path.join(DC_BUILD, stem)
            dst = os.path.join(work, rel.replace("/", os.sep))
            if not os.path.exists(src):
                missing.append(stem)
                continue
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copy2(src, dst)
            staged += 1
    return os.path.join(work, "site.json"), staged, missing


def _route_lengths(route):
    lengths = [math.dist(a, b) for a, b in zip(route, route[1:])]
    return lengths, sum(lengths)


def _point_and_dir(route, lengths, total, fraction):
    target = total * fraction
    walked = 0.0
    for (a, b), length in zip(zip(route, route[1:]), lengths):
        if walked + length >= target and length > 0:
            t = (target - walked) / length
            pt = (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)
            return pt, (b[0] - a[0], b[1] - a[1])
        walked += length
    a, b = route[-2], route[-1]
    return (b[0], b[1]), (b[0] - a[0], b[1] - a[1])


def sweep_posts(route, ground, rects, reach, site_spawns):
    """Standable points within `reach` of the route, on a declared grid."""
    lengths, total = _route_lengths(route)
    if total <= 0:
        return {}
    seen = {}
    steps = max(1, int(math.ceil(total / ALONG_STEP)))
    laterals = [0.0]
    d = LATERAL_STEP
    while d <= reach + 1e-9:
        laterals.extend((d, -d))
        d += LATERAL_STEP
    for s in range(steps + 1):
        fraction = min(1.0, s * ALONG_STEP / total)
        pt, direction = _point_and_dir(route, lengths, total, fraction)
        norm = math.hypot(direction[0], direction[1])
        if norm <= 0:
            continue
        px, py = -direction[1] / norm, direction[0] / norm
        for off in laterals:
            cand = (pt[0] + px * off, pt[1] + py * off)
            if not site_spawns.outdoors(cand, ground, rects):
                continue
            key = (round(cand[0] / GRID), round(cand[1] / GRID))
            seen.setdefault(key, cand)
    return {f"Enemy_post{i}": p for i, p in enumerate(seen.values())}


def main() -> int:
    import site_cover
    import site_spawns
    import lot

    real_plan = site_cover.plan_cover
    real_place = site_spawns.place_enemies
    captured = {}
    finding_codes = []

    def spy_place(site_spec, positions, **kw):
        plan = real_place(site_spec, positions, **kw)
        for f in getattr(plan, "findings", []) or []:
            code = f.get("code") if isinstance(f, dict) else None
            if code:
                finding_codes.append(code)
        return plan

    def spy_plan(points, rects, ground, **kw):
        res = real_plan(points, rects, ground, **kw)
        if not captured:
            captured.update(points=dict(points), rects=list(rects),
                            ground=ground, kw=dict(kw), plan=res)
        return res

    print("=" * 78)
    print("STANDABLE-GROUND SWEEP -- MEASUREMENT ONLY, NOTHING CHANGED")
    print("along-step %.1f m   lateral-step %.1f m   dedup grid %.1f m"
          % (ALONG_STEP, LATERAL_STEP, GRID))
    print("=" * 78)

    rows = []
    for seed in SEEDS:
        spec = _spec_for(seed)
        if not os.path.exists(spec):
            print(f"seed {seed}: NO SPEC at {spec}")
            continue
        captured.clear()
        del finding_codes[:]
        tmp = tempfile.mkdtemp(prefix=f"sweep_{seed}_")
        site_cover.plan_cover = spy_plan
        site_spawns.place_enemies = spy_place
        try:
            staged_spec, staged, missing = _stage(seed, tmp)
            t0 = time.perf_counter()
            lot.assemble(staged_spec, os.path.join(tmp, "out"), walkable=True)
            t_assemble = time.perf_counter() - t0
        finally:
            site_cover.plan_cover = real_plan
            site_spawns.place_enemies = real_place
            shutil.rmtree(tmp, ignore_errors=True)

        declared = "LOT_OCCLUDERS_DECLARED" in finding_codes
        unknown = "LOT_SHELL_COLLISION_UNKNOWN" in finding_codes

        if not captured:
            print(f"seed {seed}: plan_cover was never called")
            continue

        points = captured["points"]
        rects = captured["rects"]
        ground = captured["ground"]
        kw = captured["kw"]
        route = kw.get("route") or []
        envelope = kw.get("opening_range", site_spawns.OPENING_RANGE)

        samples = site_cover.route_samples(
            route, spacing=site_cover.ROUTE_SAMPLE_SPACING)
        lengths, total = _route_lengths(route)

        enemies = {k: v for k, v in points.items()
                   if k.startswith(site_cover.ENEMY_PREFIX)}

        lines_now = site_cover.route_sightlines(
            samples, points, rects, envelope=envelope)
        exposed_now = {ln[0] for ln in lines_now}

        t1 = time.perf_counter()
        posts = sweep_posts(route, ground, rects, envelope, site_spawns)
        t_sweep = time.perf_counter() - t1

        merged = {k: v for k, v in points.items()
                  if not k.startswith(site_cover.ENEMY_PREFIX)}
        merged.update(posts)
        lines_posts = site_cover.route_sightlines(
            samples, merged, rects, envelope=envelope)
        exposed_posts = {ln[0] for ln in lines_posts}

        budget = max(1, int(math.ceil(
            total / site_cover.ROUTE_METRES_PER_PIECE)))

        print("-" * 78)
        print(f"seed {seed}")
        print(f"  staged {staged} .glb   missing {missing if missing else 'none'}")
        print(f"  COLLISION: {'DECLARED FALLBACK' if declared else 'measured'}"
              f"   shell-unknown: {unknown}")
        if declared or missing:
            print("  !! numbers below are NOT pipeline-faithful -- Lot fell back")
            print("     to declared footprints. Fix the staging before reading "
                  "them.")
        print(f"  route {len(route)} pts, {total:.1f} m   "
              f"samples {len(samples)}   route budget {budget}")
        print(f"  ground {ground}   rects {len(rects)}")
        print(f"  assemble {t_assemble:.2f}s   sweep {t_sweep:.2f}s")
        print(f"  ENEMIES  {len(enemies):>4}   pairs {len(lines_now):>5}   "
              f"exposed samples {len(exposed_now):>3} / {len(samples)}")
        print(f"  POSTS    {len(posts):>4}   pairs {len(lines_posts):>5}   "
              f"exposed samples {len(exposed_posts):>3} / {len(samples)}")
        e_mean, e_min, e_max, e_vals = arc_stats(lines_now, samples)
        p_mean, p_min, p_max, p_vals = arc_stats(lines_posts, samples)
        print(f"  ARC EXPOSURE ({BEARING_BINS} bins of "
              f"{360.0 / BEARING_BINS:.0f} deg)")
        print(f"    enemies  mean {e_mean:6.1%}  min {e_min:6.1%}  "
              f"max {e_max:6.1%}")
        print(f"    posts    mean {p_mean:6.1%}  min {p_min:6.1%}  "
              f"max {p_max:6.1%}")
        sat = sum(1 for v in p_vals if v >= 0.999)
        print(f"    posts at FULL 360 exposure: {sat} / {len(p_vals)} samples"
              f"   [if this is all of them, magnitude saturates too]")
        print("    per sample  " + " ".join(
            f"{i}:{e:.0%}/{q:.0%}" for i, (e, q)
            in enumerate(zip(e_vals, p_vals))))

        # ---- PREDICTION 2: is today's placement already good on arc? -----
        plan = captured.get("plan")
        piece_rects = [pc.rect for pc in (getattr(plan, "cover", []) or [])
                       if getattr(pc, "rect", None) is not None]
        lines_after_today = site_cover.route_sightlines(
            samples, merged, rects + piece_rects, envelope=envelope)
        a_mean, _a_min, _a_max, _a_vals = arc_stats(lines_after_today, samples)

        all_posts = list(posts.values())
        wide = all_posts[::max(1, len(all_posts) // GREEDY_CANDIDATES)]
        wide = wide[:GREEDY_CANDIDATES]
        near = _near_route(all_posts, samples, CANDIDATE_REACH)
        sep = getattr(site_cover, "COVER_SEPARATION", 6.0)

        g_mean, g_used, g_n, g_pre, g_loop = _greedy_arc(
            site_cover, site_spawns, lines_posts, samples, wide, budget)
        r_mean, r_used, r_n, r_pre, r_loop = _greedy_arc(
            site_cover, site_spawns, lines_posts, samples, near, budget,
            separation=sep)

        print(f"  PLACEMENT vs ARC  (budget {budget} route pieces; "
              f"today placed {len(piece_rects)} total)")
        print(f"    before any cover          mean arc {p_mean:6.1%}")
        print(f"    after TODAY's pieces      mean arc {a_mean:6.1%}   "
              f"reduction {p_mean - a_mean:+6.1%}")
        print(f"    GREEDY wide  {g_used:>2}/{g_n:<4} cand  "
              f"mean arc {g_mean:6.1%}   reduction {p_mean - g_mean:+6.1%}   "
              f"pre {g_pre:5.1f}s loop {g_loop:5.1f}s")
        print(f"    GREEDY near  {r_used:>2}/{r_n:<4} cand  "
              f"mean arc {r_mean:6.1%}   reduction {p_mean - r_mean:+6.1%}   "
              f"pre {r_pre:5.1f}s loop {r_loop:5.1f}s"
              f"   [within {CANDIDATE_REACH:.0f} m, separation {sep:.0f} m]")
        print(f"    quality kept by restricting: "
              f"{(p_mean - r_mean) / (p_mean - g_mean):.0%} of wide's reduction"
              if (p_mean - g_mean) > 0 else "")
        t_greedy = g_pre + g_loop + r_pre + r_loop

        gained = sorted(exposed_posts - exposed_now,
                        key=lambda s: int(s.split("@")[1]))
        print(f"  samples exposed by posts but NOT by the six enemies: "
              f"{len(gained)}  {gained[:12]}")
        missed = sorted(exposed_now - exposed_posts)
        print(f"  samples exposed by enemies but NOT by posts: "
              f"{len(missed)}  {missed[:12]}   [expect 0]")
        rows.append((seed, len(posts), len(lines_now), len(lines_posts),
                     len(exposed_now), len(exposed_posts), len(samples),
                     budget, t_sweep, e_mean, p_mean, sat, len(p_vals)))

    print("=" * 78)
    print("SUMMARY   (prediction 1: exposed_posts >= exposed_enemies on every "
          "seed)")
    print("%-7s %6s %8s %8s %9s %9s %8s %7s %7s" % (
        "seed", "posts", "pairs_e", "pairs_p", "exposed_e", "exposed_p",
        "samples", "budget", "sweep_s"))
    for r in rows:
        print("%-7d %6d %8d %8d %9d %9d %8d %7d %7.2f" % r[:9])
    print()
    print("ARC EXPOSURE -- the magnitude measure that boolean exposure could "
          "not give")
    print("%-7s %12s %12s %18s" % ("seed", "mean_enemies", "mean_posts",
                                   "posts_at_full_360"))
    for r in rows:
        print("%-7d %11.1f%% %11.1f%% %13d / %d" % (
            r[0], r[9] * 100, r[10] * 100, r[11], r[12]))
    if rows:
        all_sat = all(r[11] == r[12] for r in rows)
        print()
        print("MAGNITUDE %s" % (
            "SATURATES TOO -- every sample fully surrounded; standable ground "
            "is the wrong frame" if all_sat else
            "DISCRIMINATES -- it varies across samples, so cover has something "
            "to reduce"))
    if rows:
        held = all(r[5] >= r[4] for r in rows)
        print()
        print("PREDICTION 1 %s" % ("HOLDS" if held else "FAILED -- the sweep "
                                   "finds LESS exposure than six points did"))
        blow = max(r[3] for r in rows)
        print("PAIR EXPLOSION: worst pair count under posts is %d against a "
              "route budget of %d" % (blow, max(r[7] for r in rows)))
        print("  -- this is why the unit of account has to change from pairs")
        print("     to exposed samples; see the proposal, section 2.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
