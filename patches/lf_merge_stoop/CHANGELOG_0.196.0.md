## [0.196.0] - A rowhome's stoop merges with its front

**Factory roadmap 240, found pricing cold run 9271** (Deli Counter 0.211.0's stoops, against 9270): +22.7
draws a heading on the mean and +93 at the worst. `merge_empties.gd` takes apart every slot child of an
Empty whose name gives a side and merges its surfaces one mesh a side per material. The stoop's slots,
`stoop_landing` and `stoop_tread_<k>`, give none, so each stayed a module drawn on its own -- three an
Empty -- and 9271's merge report read exactly as 9270's (95 meshes in and 86 colliders on a rowhome).

- **`_side`** gives a `stoop_*` slot the front's side, S. Deli Counter stands the stoop at the front door,
  which it puts on the S wall (`stoop.front_door`). Its pieces join the front's groups and merge by
  material with the rest of that side. Its colliders are Deli Counter's own, in the greybox base, and
  unchanged.

**Merged:** on a mirror of cold run 9271's package -- its Empties merged by 0.195.0, each stoop left as three modules -- 0.196.0's `merge_empties.gd` takes in each rowhome's three stoop meshes (three surfaces) and makes one merged mesh of them, copying the modules' three box colliders out under `KitCollision` as it does every slot's; twelve scenes, no error (the factory's `docs/cold_runs/cold_9271/merge_stoop.sh`)

**Suite:** exit 0, 2,359 by the progress tally (2,344 passed, 14 skipped, 1 xfail); `test_a_rowhome_s_stoop_merges_with_its_front` pins the GDScript's rule, which 0.195.0's source has not got
