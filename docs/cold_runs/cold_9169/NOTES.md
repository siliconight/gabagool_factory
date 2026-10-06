# Cold run 9169 -- 0 interventions; video_block_001 gains the Empties by default

Breadth sweep, run 4 of 10. video_block_001's brief as last run cold (9133),
on Level Factory 0.144.0. The brief never mentions the Empties, the export
passed no flags, and the driver picked seed_9080.

**Every leg ran, `INTERVENTIONS: 0`, in 29 minutes** (22:23 to 22:52).

**From the defaults alone:**
- **The terrace:** all three candidates stood the 12 Empties beside the
  video store and two other real buildings:
  - seed_9080: bank_tower_a02, freight_terminal_a01, video_store_a01;
  - seed_9181: arena_a03, mansion_a02, video_store_a01;
  - seed_9282: airport_terminal_a02, funeral_home_a02, video_store_a01.
- **The merge,** identical to 9165 to 9168:

      [export] Empties merged: 12 scene(s), 1061 mesh(es) of 1660 surface(s) -> 236 merged mesh(es), 962 collider(s) kept

- **The bake:** 379 models and 1,694 primitive meshes lightmapped, 3 kept
  dynamic; 66 steady rigs baked, 16 failing left live; 3,271 users, 79.7 s
  in the editor.

**Other figures.**
- **Shell:** 3 candidates, all distinct; 0 blockers of 44 findings.
- **Art:** 0 blockers of 64 findings.
- **Occluders:** 1,364 of 1,370 solid modules.

**Not checked yet:** frames and frame time, after the sweep.
