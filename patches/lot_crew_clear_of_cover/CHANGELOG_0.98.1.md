## 0.98.1 - no crew member stands in the getaway van

**Cold run 9198** (bank_block_001, the first run with the van) built three
candidates, and Laser Tag played two of them. On seed_9256 it refused the map
before a single run -- `SPAWN_IN_COLLISION: LT_PlayerSpawn_1 is inside world
collision` -- and graded it BROKEN on 0 runs (`LT_NOT_EVALUATED`).

**The cause.** `site_spawns.crew_spawns` puts the crew's other members on the
first ring points `CREW_SPACING` (2.0 m) clear of the spawn. The rings start
along +X, and each point was tested against `solid_rects` only: the buildings
and the blockers.
- No cover had stood near a spawn until 0.98.0 parked the van at one.
- On seed_9256 the van stood on the +X side, its slot 1.25 m off the spawn,
  x 20.062 to 22.662.
- `LT_PlayerSpawn_1` went to (20.812, -1.8), inside the van.

### `cover_rects`, asked by `crew_spawns`

`cover_rects(site_spec, margin=WALL_MARGIN)` is every cover piece's plan rect,
grown by `margin`, and `crew_spawns` asks it beside `solid_rects`.
- **The margin** is `WALL_MARGIN` (1.0 m), for the reason a wall gets it: the
  bake erodes the navmesh round every solid, and a body inside that band has
  nothing to path from.
- **`size` is [plan x, height, plan y]**, the frame `lot.py` stands each
  piece's box in (`lot.py:2123`); `_lasertag_hook_nodes` says the same at its
  cover points. The middle number is the HEIGHT.
- **The spawn itself is never moved here**, as before.
- **Where the crew stands now.** On seed_9256 the other three stand at
  (18.812, 0.2), (16.812, -1.8) and (17.855, -4.110), 2.0, 2.0 and 2.5 m
  from the spawn, all on the sidewalk side of the kerb. 9198 had them at
  +X, +Y and -X; +X was the van.
- **`place_enemies` does not ask it.** It runs before most of the cover exists:
  `assemble` plans the furniture, the parked cars, the fences and
  `site_cover`'s pieces after it.

### Filed, not fixed: the audit's cover rects

`site_audit._cover_rects` reads the middle number of `size` as plan y, so
every cover rect the audit measures has its height for a depth. That is
3.05 m for the van's 6.8 m, and 1.73 m for a 4.7 m car.
- It feeds two coarse checks: an anchor's backstop distance, and a leg's
  cover count.
- It has done so since v0.17.1.
- It changes no geometry, so it is left for its own release, and this one
  moves only where the crew stands.

### Seen, not changed: a ring point exactly `CREW_SPACING` out

The rings' first eligible radius is the spacing itself, and the test is
`math.dist(candidate, base) < spacing` on a point built as `base + (r cos,
r sin)`. Three of sixteen directions there come back a few bits short:
1.9999999999999998 at 270 deg, 1.9999999999999993 at 247.5 deg and
1.999999999999999 at 157.5 deg. They are refused, so on seed_9256 the third
member stands on the next ring, 2.5 m out. It costs half a metre of spread.
Fixing it would move crew members on every level, so it is not done here.

### Kept, with its claim corrected: the enemies' one-leg spread

0.98.0 said the crew "passes them going in and coming out". 9198 measured
otherwise.
- **The enemies do not wait on their leg.** `LT_EnemyBrain` walks every enemy
  that cannot see the crew toward it from the first frame, so a spread along
  the route sets arrival bearings and times, not a sequence. On seed_9054 and
  seed_9155, in 9197 and 9198 alike, every enemy's median time of death was
  3.5 to 10.7 s, whichever leg it stood on.
- **On one leg, they arrive single file.** Six enemies come one at a time
  from one side. The crew's losses over 25 runs fell from 48 to 1 on
  seed_9054, and from 19 to 0 on seed_9155, which Laser Tag flagged as
  `LT_MAP_TRIVIAL_ENCOUNTER`.
- **9197's danger was an accident of geography.** Its two-leg routes ended at
  another building, which put two enemies behind the crew on seed_9054 and
  two pairs at one distance each on seed_9155. That came from where the
  building happened to stand, not from design.

The behaviour stays. Enemy placement is provisional until a gameplay layer
owns it, and what the fight in a there-and-back heist should be is the
walker's call (roadmap 206). The comment in `place_enemies` now says so.

### Tests

`tests/test_crew_keeps_out_of_the_van.py` runs against
`tests/fixtures/bank_block_001_seed_9256.site.json`, that candidate's
`site.site.drawn.json` byte for byte.
- **Its instruments are its own.** A piece's slot is read from the fixture,
  not through `cover_rects`, so on 0.98.0 the tests fail on where the crew
  stands rather than on a missing name.
- **On 0.98.0, 4 of 6 fail.** Three fail on where the crew stands: in the
  van, in any cover, and in the scene's own `LT_PlayerSpawn` nodes, read
  back from `_lasertag_hook_nodes`. The fourth is the direct test of
  `cover_rects`, which fails on the missing name.
- **Two pass either way, by design.** One checks that the fixture is the
  refused site; the other checks that the crew still stands within one ring
  of the spawn.

**Suite:** 684 passed (678 + 6), `python -m pytest -q`.
