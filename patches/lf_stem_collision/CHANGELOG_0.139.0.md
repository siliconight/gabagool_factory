## [0.139.0] - Two geometries under one module name block the run

Cold run 9148's Empties stood 2.8 m wall panels in 3.1 m slots: one Zoo
module name for two heights, so the module built last won. Zoo's planner
saw it and printed `STEM COLLISION ... one will overwrite the other` into
six kit logs, and the run passed. Deli Counter 0.176.0 removed the
collision; Zoo 1.62.0 writes `stem_collisions` into the kit index and exits
2.

This adapter has read Zoo's exit 2 as a usable kit since partial builds were
allowed: a failed module falls back to its base and becomes a non-blocking
`ZOO_PARTIAL_BUILD`. A collision has no fallback -- the wrong module stands
in every slot of one of the two geometries. So `normalize_validation` reads
the index's `stem_collisions` and raises `ZOO_STEM_COLLISION`, blocking. It
names each module and says where the fix lives. An index from before Zoo
1.62.0 carries no key, and absence stays silent.

`tests/unit/test_zoo_stem_collision.py`:
- a collision blocks and names the module (fails on 0.138.1);
- the controls: an empty list and a pre-1.62.0 index say nothing.
