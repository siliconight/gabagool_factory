## [0.208.0] - Every animated Lux rig at rest before the applied scene is packed

**Factory roadmap 247.** Two cold runs of one command shipped `presentation/lux.applied.tscn` with eleven lights'
`light_energy` apart: the same ten in every pair of runs 9295 to 9300, by about one part in 10,000, and a failing
tube at 2.618 or 3.7 (the factory's `docs/findings/roofprops_bytes/lux_energy_pairs.py`). They are already apart in
the `lux_apply` job's own output. `run_lux_apply.gd` awaits seven frames before it packs, and Lux's failing,
flickering and cycling rigs animate from their own clocks on each, by a wall-clock delta.

**What changes:**
- **Before `pack()`, every node in `lux_light_rig` that answers `rest()` is rested** (Lux 0.77.0): every lamp back
  at what its rebuild gave it, every clock at zero. The job log says how many:
  `[lux] N rig(s) at rest before the scene is packed`.
- **A Lux without `rest()` packs as before,** through `has_method`, and the log says 0.
- **`tests/unit/test_lux_rigs_rest_before_pack.py`:** fails on 0.207.0 on all three checks, finding no rest in `run_lux_apply.gd`; 3 of 3 pass on 0.208.0. The Godot proof beside it: cold run 9300's own `lux_apply` job replayed from a copy of its staging folder, twice as it ran and twice with Lux 0.77.0 and this script. The two first applied scenes are 10 lines apart once Godot's per-save ids are masked, the two second 0, each logging `[lux] 216 rig(s) at rest before the scene is packed`; against the first, the second moves 12 lines -- the 10 lights that wandered, and two poles whose failing cycle starts dark, saved at 0.0 in every run and now at the energy their rebuild gives (the factory's docs/findings/roofprops_bytes/lux_apply_replay.out.txt).
- **The suite:** `python -m pytest -q`: exit 0, 2,410 passed (0.207.0's 2,406, the new file's 3, and `test_sibling_locator`'s guard over the new file), 14 skipped (the real-tool smoke), 1 xfail, counted off the progress marks, in 8 min 25 s with a disk survey running beside it.
