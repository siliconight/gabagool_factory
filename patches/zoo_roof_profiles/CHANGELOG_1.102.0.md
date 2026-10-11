## [1.102.0] - what a roof carries follows what the building is, and fewer

**The walker's call, 2026-10-11**, on cold run 9245's roofs (`roofs.png` in
its record): every enterable roof carried the same 17 props -- 4 HVAC units,
6 vent stacks, 3 exhaust fans, 2 skylights, 2 dishes -- because the area
formula saturated every species' cap on any roof over about 300 m2, the
antennas' uniformity again. Asked how a roof should be dressed, "by
building, fewer": a deli or shop gets a unit or two, a vent and a fan;
warehouses and markets more, and the skylights; seeded so no two roofs match.
The 12 m water-tank rule, also asked, was kept.

- **`ROOF_PROFILES` and `profile_of`**: the building's use, read off its
  id's words. The first row whose word is a TOKEN of the id wins (so
  `barber` is not `bar`), and a name no row claims is a shop. Checked
  against every id in Deli Counter's library: 12 kitchens (the delis, the
  pizza place, the clubs), 35 shops, 28 offices (banks, casinos,
  courthouses, clinics, funeral homes, museums), 43 big boxes (warehouses,
  markets, stations, stadiums, terminals, halls), 21 homes, and 6 with
  nothing (parking decks, construction sites).
- **`PROFILE_COUNTS`**: per profile, each species' count is drawn per roof
  in [lo, hi], seeded by the building, then placed as before. A kitchen:
  1-2 units, a vent, 1-2 hood fans, 0-1 dish; a shop: 1-2 units, a vent,
  0-1 fan, 0-1 dish; an office 2-3 units, 1-2 vents; a big box 2-4 units,
  2-4 vents, 1-2 fans, 2-4 skylights; a home 1-2 vents, 0-1 dish. A species
  the roof is too small for is still skipped, a `none` roof carries
  nothing, and the tank keeps its formula and its height rule. The plan
  records its `profile`.
- **Across the library** (the pure planner over every built roof, seed
  1999): 133 roofs, 756 props, 5.7 a roof, where 1.101.0's formula put 2,159 (16.2): kitchens 4 to 6 (10 roofs, mean 4.6), shops 2 to 5 (30, mean 3.3), offices 3 to 7 (26, mean 5.2), big boxes 7 to 13 (41, mean 10.6), homes 1 to 3 (20, mean 2.1), the six decks and sites none; 244 units, 222 vent stacks, 125 skylights, 104 fans, 59 dishes, and 2 water tanks -- the two roofs over 12 m

### Tests

`tests/test_roofprops.py`, now 18: the profile follows the building's words
(tokens, not substrings), a shop roof carries a unit or two and a vent, a
deli's a unit or two, a vent and its hood fan in every one of 30 seeds and
not one number for every roof, and a parking deck carries nothing (these
four fail on 1.101.0); a warehouse gets more and the skylights, and no two
roofs match (both already true of 1.101.0's formula, kept as the contract);
the geometry tests from 1.101.0 run on a big box, so there is enough on the
roof to test where it stands.

**Suite:** 4,168 passed, 438 skipped, 1 xfailed in 7 min 13 s, where 1.101.0 passed 4,163
