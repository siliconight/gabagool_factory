# Cold run 9323 -- urban_row_001 on Deli Counter 0.227.0 + Level Factory 0.218.1 (2026-10-19): the office's z-fight is gone

Staged from 9322. The tool changes between them: Deli Counter 0.227.0 (709fee88), where a vault ledge at least half
inside a visible volume draws no box of its own; Level Factory 0.218.0 (3f7721f), where the greybox census refuses
any greybox surface in a themed package; and Level Factory 0.218.1 (4fb25fb), where the z-fight gate says WARN. The
root's walk export now puts the asset flags in every walk copy (f7e7a76).

**Run:** 0 interventions (journal 0, unattributed files 0), drive exit 0. The pick is seed 9104 again, PASS 100,
route completion 1.00, 0 major -- the same as 9317 to 9322. Findings 109 -> 108 against 9322: the office's
PRESENTATION_ZFIGHT is gone.

**The z-fight gate,** read off the compose job's log:

    16 buildings  [OK]
    deli_a01      [WARN]: 2 coplanar pair(s) across 755 solids -- ext_0_E_seg10 / int_0_1_seg18 (twice)
    (9322: deli_a01 2 and office 2, both printed [FAIL] and ERROR)

The office's `VAULTLEDGE_0 / reception_desk` pair is gone with the ledge's box. The ledge keeps its
`VAULTLEDGE_0-convcolonly` collider, and the drop-edge gate reads the same 54 rows. What stands is deli_a01's
partition 1, which runs the building's full 38 m into the east exterior wall, whose segment ends land on its
faces.

**The census** under Level Factory 0.218.0's stricter rule, its first export: `0 surface(s) on a greybox
material (none), 0 of them slabs; any one is refused (require_no_greybox)`. It passed.

**The walk copy** (`_runs/walk_export_urban_row_001/`) carries `_walk_asset_flags.gd` and its `WalkAssetFlags`
node: G marks what the crosshair rests on as looking good, P as needing love (roadmap 253).

**The clean job** took one workspace, cold-9319-ws (1.1 GB), whose record is pushed and which is now beyond the
newest four.
