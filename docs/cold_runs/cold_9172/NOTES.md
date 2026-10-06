# Cold run 9172 -- 0 interventions; precinct_yard_001, a September courtyard brief

Breadth sweep, run 7 of 10. precinct_yard_001's brief as last run cold
(9001, the first cold run there was), on Level Factory 0.144.1, with the seed
picked by the driver (seed_9001). The oldest brief in the sweep:
- `theme: "delco"`, a name the other nine dropped for `delco_1997`;
- no `crew_size`, so it ran at today's default of 4;
- a courtyard site with four buildings.

**Every leg ran, `INTERVENTIONS: 0`.**

**From the defaults alone:**
- **The terrace:** each candidate stood four real buildings and the 12
  Empties:
  - seed_9001: apartment_walkup_a01, bank_tower_a02, strip_retail_a02,
    train_yard_a02;
  - seed_9102: arena_a03, funeral_home_a03, office_stepped, warehouse_a01;
  - seed_9203: auto_shop_a01, deli_a01, depot_a01, warehouse_a02.
- **The merge,** identical to the street-block missions':

      [export] Empties merged: 12 scene(s), 1061 mesh(es) of 1660 surface(s) -> 236 merged mesh(es), 962 collider(s) kept

- **The bake:** 481 models and 1,900 primitive meshes lightmapped, 6 kept
  dynamic; 93 steady rigs baked, 24 failing left live; 4,247 users, 98.0 s
  in the editor. The biggest bake of the sweep so far.

**Other figures.**
- **Shell:** 3 candidates, all distinct; 0 blockers of 33 findings.
- **Art:** 0 blockers of 54 findings.
- **Surface dressing:** 4,714 instances of 4 meshes in 4 draw calls.
- **Occluders:** 1,379 of 1,392 solid modules.

**`delco` resolved.** It is Level Factory's own fallback theme word, and the
art tools took it.

**Not checked yet:** frames and frame time, after the sweep.
