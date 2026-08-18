# Re-posing Lot's cover planner on standable ground -- v4

Working design for roadmap 52's named remedy. Supersedes v1, v2 and v3.
**No code has been written.** Everything below is measured on all three
`lot_demo_001` candidates under measured collision.

Probe: `tools/probe_standable_sweep.py` -- read-only, stages its own
geometry, ~2 s for all three seeds.

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
| 3 | scoring cost stays under ~1 s per candidate | FAILED at 31.1 s, then **FIXED -- 0.2 s** |
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

## 6. Prediction 3 was fixed, and the bound improved

31.1 s of scoring against `assemble`'s own 0.18 s was not shippable, so
candidate restriction was promoted from mitigation to prerequisite. Three
changes did it:

* a bounding-box reject before the real segment test
* per-candidate TOUCHED KEYS -- a candidate scores against the ~50 bearing
  bins it can affect rather than all ~900
* a candidate band restricted to `CANDIDATE_REACH = 12 m` of the route

`COVER_SEPARATION` (6 m) is also now enforced between chosen pieces, which
the first bound ignored.

```
seed  budget  today     greedy WIDE          greedy NEAR (12 m, 6 m sep)  kept
5017     7    -10.8%    -34.1%  (233 cand)   -40.3%  ( 99 cand)           118%
5118     6    -10.4%    -24.8%  (227 cand)   -38.2%  ( 79 cand)           154%
5219    11     -9.9%    -33.2%  (236 cand)   -51.0%  (242 cand)           153%
```

**31.1 s -> 0.2 s worst case, and the restricted band BEATS the unrestricted
one on every seed.** A `COVER_SIZE` piece at distance d subtends about
`2*atan(COVER_SIZE/2/d)` -- 33 degrees at 5 m, 11 at 15 m, 4 at 45 m -- so
sampling the whole post set evenly diluted the near candidates that carry the
arc. Restricting concentrated the budget where the geometry says it belongs.

So today's placement reduces arc by ~10% while a restricted, separated,
realistic greedy reaches 38-51%: **3.7x-5.2x**, not the 2.4x-3.4x the
unconstrained bound suggested. The design was expected to get worse under
realistic constraints and got better instead.

It remains an UPPER BOUND: candidates are standable posts rather than
verified legal piece positions, and nothing checks them against `_usable`.

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

1. ~~candidate restriction -- fix prediction 3~~ **DONE**: 0.2 s, and the
   advantage grew to 3.7x-5.2x
2. arc exposure behind `threats=`, prefix parameterised, both metrics emitted
3. suite, seed-matched re-measure, roadmap item, release
4. only then: the opening pass

Step 2 is the next code change. It touches `site_cover.py` and `lot.py` and
will change the cover output of every level, so it wants its own session and
its own release.
