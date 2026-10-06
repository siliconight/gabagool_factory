"""Lot 0.97.3: VERSION and CHANGELOG for `patch_lot_spawns_keep_out_tests.py`
and `patch_lot_spawns_keep_out.py`.

    python patch_lot_0973_release.py
"""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
LOT = ROOT / "lot"

ENTRY = '''## 0.97.3 - no spawn inside an Empty, and no enemy behind an Empty row's front line

**Every refusal was the same defect.** Laser Tag refused four candidates in
cold runs 9164 to 9186 on `UNREACHABLE_SPAWN`: seed_9061 in 9170 and 9174,
and seed_9205 in 9179 and 9186. In each, Enemy_5 stood inside an Empty, e15
or e9 (`docs/findings/enemy_inside_an_empty/` at the factory root).
- **The control:** the other 17 enemies of 9186's candidates stand in the
  open, and so do all 18 of 9187's.
- An Empty is a house with its doors shut. Nothing inside one can reach the
  street.

**How.**
- `place_enemies` pushes a route sample sideways until `outdoors()` calls it
  open ground. `outdoors()` asked `footprints()`, which reads `buildings`,
  and an Empty is a blocker.
- 9186's Enemy_5 is 24.00 m off the route's last leg, the run's own
  `LOT_ENEMY_SPAWN_PUSHED` figure.
- With the collision reading `assemble` passes, 0.97.2 reproduces every
  shipped enemy on six candidates.
- `plan_fences` never strands a marker behind a row's front line, but it
  skips one inside a house. 9186's fence went up around an enemy already
  shut in.

**Why the band too.**
- On 9186's seed_9205, keeping the Empties out is enough. Enemy_5 goes to
  1.33 m clear of the row's front line.
- On 9174's seed_9061 it is not. Kept out of the Empties alone, Enemy_4 and
  Enemy_5 land behind the front line, on ground the row's fences shut off
  out to the plate's edge.
- With the band kept out as well, they stand in open ground on the far side
  of the route, pushed 50.0 and 45.0 m. The moves are large, and
  `LOT_ENEMY_SPAWN_PUSHED` reports them.
- On the runs in flight, the rule moves no enemy on any candidate of cold
  runs 9187 and 9178.

**Refuted, kept.** The first comparison measured on the declared-footprint
occluders without saying so. It quoted "Enemy_4 pushed through its house" as
Lot's placement for 9186. That is the fallback's placement; under the
collision reading, 9186's Enemy_4 never moves.

**What changed:**
- `site_extent.blocker_rect`: one reader for a blocker's plan rect (world
  extents, 12 m when unsaid). The ground, the fences and the spawns ask it;
  three copies of the rule existed.
- `site_fences.shut_band` / `shut_bands`: the band behind a row's front line,
  which `plan_fences` computed inline. The fences and the enemies now ask one
  function.
- `site_spawns.blocker_rects` and `solid_rects` (the footprints and the
  blockers): `crew_spawns`, `clear_crew_spawn` and `place_enemies` ask
  `outdoors()` of them. `place_enemies` also keeps out of
  `shut_band_rects`.
- **Not changed:** `plan_cover`'s sightline occluders and the pylons'
  keep-out read `footprints()` alone. Whether an Empty is cover to the cover
  planner is another question, with a visible effect.

**Tests:** `tests/test_spawns_keep_out_of_empties.py`, 5, on
`tests/fixtures/restaurant_row_001_seed_9205.site.json`. That is 9186's site
as drawn, byte for byte.
- It runs on the declared-footprint fallback, where 0.97.2 puts Enemy_4 in
  e13 and Enemy_5 in e9.
- What the tests hold:
  - the fixture is the refused site;
  - no enemy stands in a blocker;
  - none stands behind the row's front line;
  - the crew keeps out of a blocker;
  - the fences and the enemies ask one band.
- Blockers and the front line are read by the test's own arithmetic. Four
  fail on 0.97.2 on where the enemies stand; the fixture check passes on
  both.

**Suite:** 669 passed (0.97.2's 664 and these 5).

'''


def main():
    v = LOT / "VERSION"
    assert v.read_bytes() == b"Lot 0.97.2", v.read_bytes()
    cl = LOT / "CHANGELOG.md"
    data = cl.read_bytes()
    assert b"\r\n" not in data
    text = data.decode("utf-8")
    assert text.startswith("## 0.97.2 - the walk test decides ladder access"), text[:60]
    cl.write_bytes((ENTRY + text).encode("utf-8"))
    v.write_bytes(b"Lot 0.97.3")
    print("Lot 0.97.3: VERSION and CHANGELOG")


if __name__ == "__main__":
    main()
