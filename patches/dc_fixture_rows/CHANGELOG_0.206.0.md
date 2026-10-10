## [0.206.0] - ceiling rows laid to the work, on the ceiling's grid

**The walker, 2026-10-10** (roadmap 229): indoor light fixtures should "not
always be in a perfect line, so it looks a little less robotic in the
line/lighting placement". Counted over the 131 shipped manifests
(`docs/findings/fixture_rows/` in the factory), 513 of 513 fluorescent rows
stood on their room's centreline along its longer axis, 303 of them at the
five-lamp cap, with lamps spread 3.0 to 11.6 m apart: one rule lit every
room from its bounds alone.

### What it is now

**Rows follow the room's work plane** (`lights._rows_for_room`; WOOD's shop
rule from the walker's references, `INDOOR_FIXTURE_PLACEMENT_GUIDE.md`):
with A the height from the work surface to the lamp, rows stand at most
1.5 x A apart and the outer row within half of that of its wall, so a room
takes ceil(width / 1.5 A) rows across its shorter axis, each along the
longer one as before, with lamps at 1.5 x A along it. The work surface is
the room's (`_WORK_PLANE`, matched on role and id with the furnish's own
words): 0.75 m where desks are seeded, 1.0 m where it sells or serves, the
floor in a hall, a stockroom, a bay. A 12 x 8 m sales floor is three rows of
four over its width where it was one row of three down its middle; a 12 x
4 m stockroom is still one row. Held to 3 rows and 12 lamps a room, the row
cap of 5 unchanged: the lamp count was a budget number before the bake, and
the price of more is roadmap 229's next measurement.

**Each row's line sits on the ceiling's grid** -- 0.6 m tiles over a desk
or a counter, 0.4 m joists elsewhere, from the building's origin -- so a row
is off its room's centre by up to half a pitch for a structural reason, the
same in every build of a spec. **A home's room is one fixture at its
centre** whatever its size. Below grade and in objective rooms the bulbs
are what 0.205.0 derived.

**Ids:** the first row keeps `<room>_ceiling` (split runs `_<i>` as
before), so every authored override binds as it did; further rows are
`<room>_ceiling_r<k>`, their split runs `_r<k>_<i>`. `_colinear_shift`
takes the row's own `line`; the report and the build line carry
`rows_laid`. `docs/LIGHT_MANIFEST.md` says so.

**Lux (>= 0.62.0) fails one tube AN ANCHOR**, so a three-row sales floor
would stutter three; the fix is Lux's, one a room by the anchor's base id,
and lands beside this.

**Tests:** `test_fixture_rows.py`, 10 pure tests: the narrow stockroom's one
row and unchanged id, the sales floor's three on the tiles, the office's two,
the room cap thinning every row alike, a room one spacing wide, the joist
snap by half a pitch at most, the home's one fixture, the bulbs as they
were, a second row's split runs named, a colinear partition moving only the
row it lies under. The void and partition suites keep their argument on
rooms narrowed to one row (the measured hospital lobby's lamps at x = +-8
reproduced on a 4.5 m slice of it), and the partition report gains
`rows_laid`. **Suite:** RESULT_SUITE. **The library rebuilt:** RESULT_CENSUS.
