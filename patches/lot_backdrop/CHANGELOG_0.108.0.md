## 0.108.0 - the backdrop beyond the plate's edge, by recipe

**Roadmap 228, step D.** The walker picked E from the edge menu
(`docs/findings/edge_menu/` at the factory root) and asked for versions that
differ by level. The fence (0.107.0) and the glow (Lux 0.73.0) stand; Zoo
1.95.0 made the rowhome and the water tower. This lays them: `site_backdrop`
plans what stands beyond each edge from the spec's `surroundings`, a recipe
Level Factory will write from the brief, `borough` when unnamed.

**What `borough` lays,** in the mockup's figures: three bands of rowhomes
beyond each edge (4 to 14, 38 to 49 and 80 to 92 m out), the houses 5 to 7 m
wide and 8 to 11 m tall with the odd cross street and gap, facing the plate,
and one water tower 90 m past the north edge. On cold run 9223's 196 x 100 m
plate, about 300 houses.

**A few modules, many instances.** A level draws `MODULES_PER_LEVEL` (6)
width-and-height pairs from the fifteen and every house is one of them, so
Level Factory's composition (step E) is one MultiMesh a module a side, and
the draws scale with the modules, not the houses. Zoo lights each module's
windows by its stem, so the pairs are the patterns too.

**Backdrop is not cover.** The pieces go into their own list, `backdrop`:
nothing is a sightline blocker, nothing has collision, nothing is on the
navmesh, nothing stands inside the plate. `write_site_slots` gives each a
slot with `collision` none and `source` `site_backdrop`, so the same kit
build makes the modules; `LOT_BACKDROP_PLACED` says what was laid.

**The other recipes** (`yards`, `parkland`, `roadside`) are named so a
brief can ask for them and lay the borough with `LOT_BACKDROP_RECIPE_PENDING`
until their kits exist; `none` lays nothing; a recipe nobody knows lays the
borough and says `LOT_BACKDROP_RECIPE_UNKNOWN`.

**Nothing in a level changes yet:** the drawn scene writes no node for a
backdrop piece. Level Factory's step E composes them from the drawn spec and
the kit, and prices them.

**Tests:** 8, `tests/test_site_backdrop.py`, all failing on 0.107.0.
**Suite:** 753 passed, exit 0 (745 as 0.107.0 and the 8 new); the example compound's slot-manifest test now also counts the backdrop's slots apart from the cover.
