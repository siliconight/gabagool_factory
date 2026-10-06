# Cold run 9167 -- 0 interventions; club_block_014 gains the Empties by default

Breadth sweep, run 2 of 10. club_block_014's brief as last run cold (9134,
2 October), on Level Factory 0.144.0. The brief never mentions the Empties.
Its export passed no flags, and the driver picked the seed (`auto` chose
seed_9080 on the walktest and Laser Tag's route findings).

**Every leg ran, `INTERVENTIONS: 0`.**

**The Empties came from the default alone.**
- Every candidate stood the full terrace beside its three real buildings:

  | candidate | real buildings | Empties |
  |---|---|---|
  | seed_9080 | bank_tower_a02, freight_terminal_a01, strip_club_a02 | all 12, gs_empty_rowhome_a to _l |
  | seed_9181 | arena_a03, mansion_a02, strip_club_a01 | all 12 |
  | seed_9282 | airport_terminal_a02, funeral_home_a02, strip_club_a03 | all 12 |

- The export merged them exactly as on gas_block_001 (9165, 9166), which
  is expected with the same 12 designs dealt:

      [export] Empties merged: 12 scene(s), 1061 mesh(es) of 1660 surface(s) -> 236 merged mesh(es), 962 collider(s) kept

**The bake came from the default alone:** 422 models and 1,652 primitive
meshes lightmapped, 6 kept dynamic; 84 steady rigs baked, 16 failing left
live; 3,839 users, 86.4 s in the editor.

**Other figures.**
- **Shell:** 3 candidates, all distinct; 0 blockers of 42 findings.
- **Art:** 0 blockers of 62 findings, exiting 1 as the art leg has on every
  recent run.
- **Occluders:** 1,491 of 1,500 solid modules.
- **Time:** 21:28 to 22:00, 32 minutes.

**Not checked yet:** frames and frame time. They come after the sweep, so
that nothing draws on the GPU while a cold run is using it.
