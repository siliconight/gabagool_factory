# Cold run 9296 -- the corner wall's fill deals afresh: Level Factory 0.206.1 proven

**What it tested:** urban_row_001 (9295's brief unchanged) on Level Factory 0.206.1 (c189baf). In it `_cornered`'s
fill deals afresh where nothing left on the bag fits before the closing corner's room and some design does. Cold
run 9295's seed_9003 had closed its wall 12.70 m short of the run's end (`patches/lf_corner_fill/`). The pick is
`auto`. Zoo 1.107.0, Deli Counter 0.218.0, Lot 0.123.0, Laser Tag 0.32.0. Staged from cold run 9295.

**Result: 0 interventions (journal 0, unattributed files 0). Every wall closes within the narrowest design of its
end, each as the replay said it would, and the picked package is 9295's.**

- **The walls** (each candidate's site spec), against 9295's and against `replay_candidates.py`'s prediction on
  0.206.1:

      seed     corners (west .. east)   blocks    short of the run's end
      9003     d .. c                   10 -> 11  12.70 -> 1.90 m   (predicted 1.90)
      9104     c .. d                   10        1.20 -> 1.20 m    (predicted unchanged)
      9205     b .. c                   10 -> 11   4.70 -> 2.60 m   (predicted 2.60)

- **The pick, `auto`: seed_9104 at PASS 100,** every grade as 9295's.

      seed 9003: 0 major (not counted: LOT_DESTINATION_ABOVE_FLOOR, LT_MAP_TRIVIAL_ENCOUNTER), route completion 1.00, grade PASS_WITH_TUNING 89
      seed 9104: 0 major, route completion 1.00, grade PASS 100
      seed 9205: 0 major (not counted: LOT_DESTINATION_ABOVE_FLOOR), route completion 1.00, grade PASS 90

- **The picked package is 9295's.** Of 3,676 files each, all on both sides, 24 differ.
  - Godot's per-save node `unique_id`s, import uids, the bake's timings and the workspace paths, in the
    manifests, the scenes and the reports.
  - One more is real bytes and unrelated (below).
  - So 9295's frames and price stand for 0.206.1's package: no A/B was shot.
- **Findings 109 -> 109.**
- **Found, not traced: the pharmacy's roof props are not byte-stable from run to run.**
  `lot/pharmacy_a01/art/roofprops/pharmacy_a01_roofprops.glb` reads f8fd372b in 9294 and 9296 and 290b98f0 in
  9295.
  - The same 67,908 bytes, its glTF JSON identical, 2,569 bytes of its binary buffer different from offset
    30,276.
  - Its Zoo job's command is the same in all three, `--seed` included, and the slots it reads are Deli
    Counter's build, unchanged between 9295 and 9296.
  - Roadmap 181 records the scatter as "deterministic per manifest and seed". Filed as roadmap 247.

## The time

    run    shell   art     export   walk   retire   the drive
    9295   112 s   219 s   215 s    13 s   20 s    10.0 min (597 s)
    9296   111 s   212 s   210 s    12 s   19 s     9.75 min (585 s)
