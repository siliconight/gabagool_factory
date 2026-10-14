# Cold run 9310 -- the walk's findings 1-4, fresh for the walker's demo (restaurant_row_001)

**What it tested:** 9308's toolchain on restaurant_row_001, the strip with rowhomes, the third of the three levels
the walker demos at 21:00 (`docs/findings/walk_2026-10-14/`; 9308's notes name the four changes).
restaurant_row_001's brief as cold run 9306 ran it, seed_9003 named as 9306 picked it. Staged from 9306.

**Result: 0 interventions (journal 0, unattributed files 0). The three candidates grade as 9306's did, and the
package dropped the 218 modules no file names.**

- **The grades:** seed_9003, seed_9104 and seed_9205 each PASS 90 at route completion 1.00, as 9306's notes record
  them (`grades_9310.out.txt`, read off each candidate's `lasertag.report.json`).
  - Not compared field by field. This run's own retire step took 9306's workspace. The findings step read it at
    18:37:50 (112 -> 112); at 18:37:58 the retire removed `1 item(s), 1.0 GB`, and it is gone. Its notes are
    pushed, no record names it, and it stood fifth newest, beyond the four that `tools/factory_retire.py`'s
    pushed-runs rule keeps.
- **Findings 112 -> 112.**
- **Merged modules:** 218 removed (3.4 MB), 2 named and kept.
  - The light bake's models went 564 -> 346; its users stayed 3,490.
  - The editor's bake took 60.6 s against 59.8 s.
- **Primitives 236 -> 237:** the backdrop's ground given a UV2, as in 9308. It is not a lightmap user.
- **Loaded headless** at 18:45 (`_runs/walk_export_restaurant_row_001`): exit 0, no engine error, and the one
  warning this afternoon's copy also prints (`[cycle] no sky provider in this scene`).
- **Still standing, after the demo:** the office's stair core, the walk's findings 7-9. Nothing in this toolchain
  touches it.
- **Not priced:** as 9308.

## The time

    run    shell   art     export   walk   retire   the drive
    9306    97 s   172 s   178 s    12 s    4 s     8.0 min (478 s)
    9310   103 s   181 s   179 s     8 s   21 s     8.5 min (507 s)

The retire leg's 21 s is the 1.0 GB it removed.
