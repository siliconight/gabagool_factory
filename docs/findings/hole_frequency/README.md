# How often a level has a hole in a floor -- and the rule that makes it rare (2026-10-20, roadmap 269)

**The walker, 2026-10-20**, while the floor holes' causes were being proven (roadmap 265): "stairs and ladders should
be the primary way to get between floors in this game...with the holes in floors being somewhat rare...but still at
our disposal to use if needed/desired to add some more ways to navigate levels".

Rarity is a property of a LEVEL, not of a spec, so it is measured per level: `hole_frequency.py` replays Level
Factory's own lot draw (`building_library.lot_for_brief`, themed) over the latest staged brief of every mission,
twelve candidate seeds each (`seed_base + 101 k`, as a batch's are), and counts the holes a player would see in each
level's buildings -- a drop Deli Counter gave a `cause` (0.236.0), not one into a stair's own well. A
single-building mission builds its own building from Deli Counter's preset per candidate; its rows come from the
built transients `docs/findings/hole_causes_265/census_holes.json` recorded, and since Level Factory 0.221.0 the
line also says how many candidates the rate leaves the preset's holes. `--lf <dir>` replays with another checkout.

## Before (`hole_frequency.out.txt`; Level Factory 0.220.0, Deli Counter 0.236.1)

**54 of 300 lot levels** (18.0 %; 25 lot missions) carried a hole, and they bunched where a family that always carries
one anchors the mission:

| mission | levels with a hole | why |
|---|---|---|
| restaurant_row_001, urban_row_001 | **12 of 12** each | the deli anchors both, and both deli variants a themed lot can draw (a01, a03) carried the 2.2 m cut drop |
| warehouse_yard_001 | 7 of 12 | warehouse_a02's mezzanine hatch, the warehouse anchoring it |
| the other 22 lot missions | 0 to 3 of 12 | a deli, warehouse_a02 or apartment_walkup_a01 drawn now and then |
| deli_001 (one building) | **every level** | the corner_deli preset's cut drop and hatch |
| county_hospital_001 (one building) | **every level** | the hospital preset's elevator shafts, 1 or 2 a level, uncaused (bare) |

Four of the library's twelve hole-carrying specs are in the themed pool: deli_a01, deli_a03, warehouse_a02,
apartment_walkup_a01.

## The rule (Level Factory 0.221.0, Deli Counter 0.237.0)

- **Per level, at a rate:** `building_library.holes_wanted(candidate, rate)`, `FLOOR_HOLE_RATE = 0.25` -- a call made
  2026-10-20 and meant to be changed; a brief's `floor_holes` (0 to 1) overrides it.
- **A lot swaps a VARIANT, never a family** (`apply_hole_rule`): a level left without a hole takes a variant of each
  drawn family without one; a level that wants one and has none takes one with one -- one only. `pick_lot`'s draw
  stands, so a lot the rule does not touch is the lot it always was. `draw_lot` is the one place the draw and the
  rule meet, for the planner, the compose spec and the site spec alike.
- **The mission's own building** is built `--holes off` on a level left without (Deli Counter's
  `presets.make(holes=False)`, `hole_causes.without_holes`: the drop and the authored slab holes under it on every
  storey).
- **The deli family keeps a variant without the drop** (Deli Counter's `migrate_hole_free_variants.py`): deli_a01,
  a call; deli_a03 keeps the drop cold runs 9340 and 9341 proved.

**REFUTED, KEPT: the first coin was `zlib.crc32` of the candidate id.** Two missions' answers came out identical for
200 seeds of 200 at a rate of 0.5: CRC is affine over GF(2), so candidate ids differing only in the mission prefix
XOR to a constant for every seed. The coin is a SHA-256 now (0.248 of 4,000 candidates at 0.25; the two missions
agree on 101 of 200 at 0.5).

## After (`hole_frequency_after.out.txt`; Level Factory 0.221.0, Deli Counter 0.237.0)

**17 of 300 lot levels** (5.7 %) carry a hole:

| mission | before | after |
|---|---|---|
| restaurant_row_001 | 12 of 12 | 2 of 12 |
| urban_row_001 | 12 of 12 | 2 of 12 |
| warehouse_yard_001 | 7 of 12 | 4 of 12 |
| precinct_yard_001 | 2 of 12 | 3 of 12 |
| deli_001 (one building) | every level | 2 of 12 |
| county_hospital_001 (one building) | every level | 5 of 12 |

Twelve seeds is a small sample, which is why some read above 0.25; the rate itself is pinned by
`tests/unit/test_floor_holes.py`. restaurant_row_001's seed 9003 -- cold runs 9340 and 9341's -- still keeps its drop.

**A side effect, measured before the cold run (`predict_9345_9346.out.txt`):** a swap can make two candidates of one
mission place the same three buildings -- urban_row_001's 9003 and 9104 both place deli_a01, pharmacy_a01 and
office -- where the draw alone had given them different delis. Placement still differs by seed.

**REFUTED, KEPT: "54 of 288".** Deli Counter 0.237.0's and Level Factory 0.221.0's CHANGELOG entries and commit
messages, and the comment on `building_library.FLOOR_HOLE_RATE`, say 54 of 288 lot levels (and the Deli Counter entry
"24 staged lot missions"): a miscount of the missions made while reading the table by eye. The JSON says 25 lot
missions and 300 levels (`hole_frequency.json`, counted by script). The released texts are corrected by the next
change to each repo; the figures here are the counted ones.

## Not measured here

- Whether a level without its hole plays worse: the hole was an optional, one-way route, and stairs and ladders
  remain; the walk test and the firefight grade on the cold runs say whether anything else moved.
- The rate's taste: 0.25 is a call. The walker's "somewhat rare" is a word, and the dial is one number.
