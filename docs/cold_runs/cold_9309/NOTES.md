# Cold run 9309 -- the walk's findings 1-4, fresh for the walker's demo (gas_block_001)

**What it tested:** 9308's toolchain on gas_block_001, the second of the three levels the walker demos at 21:00
(`docs/findings/walk_2026-10-14/`; 9308's notes name the four changes). That is Zoo 1.111.0 and 1.112.0 and Level
Factory 0.211.0, with 0.210.0 dropping the modules the merge made redundant. gas_block_001's brief as cold run 9307
ran it, seed_9080 named as 9307 picked it. Staged from 9307.

**Result: 0 interventions (journal 0, unattributed files 0). Nothing the graders read moved, and the package
dropped the 218 modules no file names.**

- **The grades:** 0 of 32 summary fields moved on any candidate against 9307, and every enemy and crew spawn stands
  where it stood (`fight_fields_9307_9309.out.txt`). seed_9080 PASS 100, seed_9181 PASS_WITH_TUNING 89, seed_9282
  PASS 100.
- **Findings 105 -> 105.**
- **Merged modules:** 218 removed (3.4 MB), 2 named and kept.
  - The light bake's models went 547 -> 329; its users stayed 3,191.
  - The editor's bake took 61.5 s against 61.9 s.
- **Primitives 246 -> 247:** the backdrop's ground given a UV2, as in 9308. It is not a lightmap user.
- **Loaded headless** at 18:45 (`_runs/walk_export_gas_block_001`): exit 0, no engine error, no warning.
- **The gas station's door box** paints OPEN 24 HOURS, cream on green, where it wore the FLAPPAHS band's pack:
  the pack's two textures left the package and `lot/gas_station_a02/art/fixtures/_tex/SignBox_Face_656x216_*.png`
  joined it. Read off that texture, not seen in a frame.
- **Every other file that left or joined the package** is the modules' 654 (218 with their sidecars) and that
  door's four out and two in (`docs/findings/merged_modules/package_files_9307_9309.out.txt`). 3,233 files ->
  2,577, 166.9 MB -> 163.4 MB.
- **Not priced:** as 9308.

## The time

    run    shell   art     export   walk   retire   the drive
    9307   116 s   160 s   176 s    12 s    4 s     8.1 min (483 s)
    9309   154 s   221 s   210 s     8 s    4 s    10.2 min (613 s)

Frames for the fixes were shot in Godot during this run's shell and art legs (`_scratch/fix_after_9308`, written
18:21; `fix2_9305` and `fix2_9308`, 18:25 and 18:27). Neither leg is evidence about the tools' speed.
