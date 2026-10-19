# Cold run 9325 -- urban_row_001 on Deli Counter 0.230.0 + Level Factory 0.218.2 (2026-10-19): every building's z-fight gate reads OK

Staged from 9324. The tool changes between them:

- Deli Counter 0.229.0 (54f5b5d4): the build freshness gate watches 20 more modules and the agent contract
  (roadmap 259). No geometry moved, and no rebuild was needed.
- Deli Counter 0.230.0 (c5e77e52): the z-fight gate reads a scene's `Transform3D` as Godot does, the basis's
  rows then the origin.
- Level Factory 0.218.2 (f1602ad): the ground-contact pre-flight reads rows too.

The two fixes are one defect class (`docs/findings/zfight_rows_177/`).

**Run:** 0 interventions (journal 0, unattributed files 0), drive exit 0, 11:30:19 to 11:39:56. The pick is seed
9104 again, PASS 100, route completion 1.00, 0 major -- as on 9317 to 9324. Findings 108 -> 107:
`PRESENTATION_ZFIGHT` 1 -> 0.

**The z-fight gate,** read off the compose job's log:

    17 buildings  [OK]
    (9324: 16 [OK], deli_a01 [WARN] on 2 coplanar pairs, ext_0_E_seg10 / int_0_1_seg18)

deli_a01 reads 0 pairs across 756 solids, 220 buried (`compose.summary.json`). That is what
`docs/findings/zfight_rows_177/rows_vs_columns.py` predicted from 9324's package with only the gate's matrix
swapped. The two pairs were the gate reading the east wall's end piece turned the other way; the engine never
placed it so (`pose_9324_junction.json` there).

**Everything else is 9324's:** the light bake lightmaps 352 models and keeps 8 dynamic, with 3,160 users. Laser
Tag on seed 9104 moves 0 of its 32 summary fields.

**The ground-contact fix** changes nothing here, as measured beforehand: every building in this level stands
unturned.

**The clean job** took one workspace, cold-9321-ws (1.4 GB), whose record is pushed and which is now beyond the
newest four.
