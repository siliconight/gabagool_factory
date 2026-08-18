# Re-posing Lot's cover planner on standable ground -- v3

Working design for roadmap 52's named remedy. Supersedes v1 and v2.
**No code has been written.** Everything below is measured on all three
`lot_demo_001` candidates under measured collision.

Probe: `_scratch/probe_standable_sweep.py` -- read-only, stages its own
geometry, ~35 s for all three seeds.

---

## 1. The problem, in one number

`mean_enemies = 4%`.

Six enemy points occupy about three of seventy-two bearings around a route
sample. Lot plans cover against that 4% sample of the directions a shooter
could actually come from. This is the quantitative form of "15 of 16 pieces
are placed against an `Enemy_*` point", and it is why the planner cannot
survive enemy placement moving to the gameplay layer.

## 2. Two metrics that do not work, and one that does

**Pairs** (today). `route_sightlines` returns (sample, shooter) pairs. Six
enemies give ~51 on seed_5219; a standable-ground sweep gives **3902**,
against a route budget of 11. Unusable.

**Boolean exposure** (v1's proposal). "Is this route sample exposed" is
already TRUE for every sample under six enemies -- 9/9, 8/8, 16/16 -- so it
is pinned at maximum before the sweep runs and carries no information.
Refuted by measurement, not by argument.

**Arc exposure** (this design). Bin each sample's threat bearings into 72
slices of 5 degrees; measure the fraction of 360 that holds a shooter with a
clear line.

```
seed  mean_enemies  mean_posts  at_full_360   spread (posts)
5017      4.0%        68.2%        0 / 9        43% .. 93%
5118      4.2%        65.8%        0 / 8        44% .. 90%
5219      4.3%        79.7%        0 / 16       51% .. 99%
```

Nothing saturates, the spread is wide, and cover reduces it monotonically.

## 3. The sampler

Already free. `site_spawns.outdoors(point, ground, rects)` is two
point-in-rect tests. Sweeping the route band -- `_route_point` for position
and tangent, perpendicular offsets out to `OPENING_RANGE`, deduped on a
declared grid -- yields 353-713 posts in **0.00 s**.

Declared parameters: along-route step 5 m, lateral step 5 m, dedup grid
2.5 m. `_candidates` is NOT reusable here: it orders `(fraction, offset)`
pairs by deviation from where enemy `i` was designed to stand, which is a
placement search for one enemy rather than an enumeration of the space.

## 4. The planner

Greedy. Score each candidate cover position by total arc removed across all
route samples, place the best, subtract, repeat until the budget is spent. A
(sample, bin) key closes only when EVERY open line in it is blocked -- that
is what makes this arc reduction rather than line breaking.

`_place_on`, the `Cover` record, `refused` bookkeeping and the budget
arithmetic all survive unchanged. What changes is the SCORING, and `breaks`
stops naming a pair and starts naming a sample plus an arc.

`route_sightlines` selects threats with `n.startswith(ENEMY_PREFIX)`
(site_cover.py:567). That prefix becomes a parameter. When Lot supplies posts
it passes `post@`; when a caller supplies enemies it passes `Enemy_` and
behaviour is identical, so Laser Tag and `level_factory/packages/validation/`
are untouched -- as in 0.44.0, `open_sightlines` itself is not modified.

`plan_cover` gains an optional `threats=` argument. Absent, behaviour is
exactly today's. No existing caller or test changes.

## 5. Prediction outcomes

| # | prediction | outcome |
|---|---|---|
| 1 | posts find >= the exposure six enemies find | HELD, but vacuously -- both saturate |
| 2 | today's placement is near-random against arc | **HELD STRONGLY** (see below) |
| 3 | scoring cost stays under ~1 s per candidate | **FAILED -- 31.1 s on seed_5219** |
| 4 | old and new metrics rank seeds differently | not yet tested |

Prediction 2, the kill switch:

```
seed  budget  placed  before   after today     after greedy    greedy cost
5017     7       8     68.2%   57.4%  (-10.8)  34.1%  (-34.1)     3.0 s
5118     6       9     65.8%   55.4%  (-10.4)  41.0%  (-24.8)     1.6 s
5219    11      14     79.7%   69.8%  ( -9.9)  46.4%  (-33.2)    31.1 s
```

Today's placement reduces arc by ~10% on EVERY seed regardless of geometry.
That flatness is what optimising a 4% sample looks like. Greedy reaches
2.4x-3.4x the reduction using FEWER pieces every time.

The greedy figure is an UPPER BOUND: capped 250-candidate set, no separation
or legality constraints beyond `_piece_rect`. A real planner lands below it.

## 6. Prediction 3 failed, so performance comes first

31.1 s of scoring against `assemble`'s own 0.18 s is not shippable. Candidate
restriction is now a PREREQUISITE, not a mitigation: restrict candidate
positions to the neighbourhood of high-exposure samples rather than lowering
the sweep density, and re-measure both cost AND whether the 2.4x-3.4x
advantage survives a realistic candidate set.

If the advantage collapses once candidates are restricted to legal,
well-separated positions near the route, this design is not worth building
and that should be said plainly rather than tuned around.

## 7. Metric transition

`route_open` counts open PAIRS and is only meaningful when enemies exist. Arc
exposure is a different quantity in different units. Emit
`route_exposure_mean` alongside `route_open` for one release, then retire
`route_open` deliberately. Silently redefining a number that appears in the
roadmap, two changelogs and a grader would repeat a mistake this project has
made more than once.

## 8. Still not established

* `LT_OPEN_SIGHTLINE` was never counted patched-versus-reverted per seed, so
  roadmap 52's claim about deleting cover the grader asks for remains
  unrefuted -- only overruled on precedence.
* The OPENING pass has not been analysed under arc at all. Only the route
  pass.
* Nothing has been tried on any mission other than `lot_demo_001`.

## 9. Order of work

1. **candidate restriction** -- fix prediction 3, re-measure cost and confirm
   the advantage survives. If it does not, stop here.
2. arc exposure behind `threats=`, prefix parameterised, both metrics emitted
3. suite, seed-matched re-measure, roadmap item, release
4. only then: the opening pass
