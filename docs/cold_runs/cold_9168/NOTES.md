# Cold run 9168 -- 0 interventions; bank_block_001 gains the Empties by default

Breadth sweep, run 3 of 10. bank_block_001's brief as last run cold (9054),
on Level Factory 0.144.0. The brief never mentions the Empties, the export
passed no flags, and the driver picked seed_9054.

**Every leg ran, `INTERVENTIONS: 0`, in 22 minutes** (22:00 to 22:22).

**From the defaults alone:**
- **The terrace:** all three candidates stood the 12 Empties beside their
  three real buildings:
  - seed_9054: bank_branch_a04, cr_garage, rail_station_a02;
  - seed_9155: bank_tower_a01, freight_terminal_a03, pharmacy_a01;
  - seed_9256: bank_branch_a04, mansion_a01, pawn_shop_a01.
- **The merge,** identical to 9165 to 9167:

      [export] Empties merged: 12 scene(s), 1061 mesh(es) of 1660 surface(s) -> 236 merged mesh(es), 962 collider(s) kept

- **The bake:** 409 models and 1,522 primitive meshes lightmapped, 4 kept
  dynamic; 90 steady rigs baked, 20 failing left live; 3,891 users, 87.8 s
  in the editor.

**Other figures.**
- **Shell:** 3 candidates, all distinct; 0 blockers of 45 findings.
- **Art:** 0 blockers of 63 findings.
- **Occluders:** 1,591 of 1,602 solid modules.

**Not checked yet:** frames and frame time, after the sweep.
