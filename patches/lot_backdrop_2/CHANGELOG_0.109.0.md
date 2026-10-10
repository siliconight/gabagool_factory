## 0.109.0 - the yards, the parkland and the roadside

**Roadmap 228.** The walker asked for edges that differ by level; 0.108.0
named five recipes and laid one. Zoo 1.96.0 made the tree and the warehouse
the other three are made of, and this lays them:
- **`yards`:** runs of cargo containers along the near band, three to six
  long and most of them stacked two high (`z`, the upper one's foot at the
  lower one's height), warehouses with roof monitors facing the plate in
  the two bands behind, and the water tower.
- **`parkland`:** a belt of trees 2.5 to 38 m out, a tree every 1.2 to
  3.2 m from three sizes, and a sparser far belt 60 to 90 m out; no tower.
- **`roadside`:** a thin belt of trees and a few far warehouses; no tower.
- **`borough` takes one depth in every band** (4 to 16, 38 to 50 and 80 to
  92 m out). A module is a species at its dims, depth included, so 0.108.0's
  three depths were three times the six modules a level was said to draw
  from: cold run 9225 shipped 19 modules and 69 draws. `none` lays nothing,
  as before; `LOT_BACKDROP_RECIPE_PENDING` no longer fires, since every
  recipe has its kit.

**A piece's `z`.** A backdrop piece may say how high its foot stands above
the plate; `write_site_slots` lifts the slot by it and Level Factory's
composition does the same.

**Tests:** 7, `tests/test_site_backdrop_2.py`, all failing on 0.108.0.
**Suite:** 760 passed, exit 0 (753 as 0.108.0 and the 7 new); 0.108.0's own test moved with the change, the modules counting the tower and parkland laying its trees without a finding.
