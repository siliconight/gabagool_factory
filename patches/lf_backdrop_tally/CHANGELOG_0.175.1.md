## [0.175.1] - The backdrop's by-side count counts every piece

**Cold run 9226** (roadmap 228, the yards recipe) printed `[export]
backdrop: site_backdrop.tscn -- 121 instances of 5 module(s) on their
sides, 17 draw calls (N 0, S 0, E 0, W 0; 1 tower)`: `ship_backdrop`'s
`by_side` tallied `backdrop_rowhome` orders only, which the yards lay none
of. `backdrop_layer.pieces_by_side(orders)` now counts every order but the
tower a side, for any species; the borough's figures are what they were.

**Tests:** 1 pure test in `tests/unit/test_backdrop_layer.py` (a yard's
containers and warehouses counted, the tower not), failing on 0.175.0,
which has no `pieces_by_side`. **Suite:** RESULT_SUITE.
