## [1.62.0] - a kit that gives two geometries one name is refused

`plan_kit` has detected a stem collision -- two modules planned with
different geometry under one filename -- since it was written, and printed
`STEM COLLISION ... one will overwrite the other`.

Cold run 9148 printed it in all six rowhome Empties' kit logs: 2.8 m and
3.1 m walls and windows under one name each. `--build-kit` exited 0, the
2.8 m module stood in every 3.1 m slot, and the frames showed a strip at each
storey line. 1.60.0 and Deli Counter 0.176.0 removed that collision. This
release makes the next one stop the run instead of shipping:
- `stem_collisions` goes into `<building>_kit.built.json` beside `n_fail`,
  and into the result;
- `zoo_cli --build-kit` exits 2 on a collision, as it does on a failed
  module (`kit_exit_code`), with a `REFUSED` line per stem.

Measured beforehand: on 9148's library, only the six Empty kits had any
collision. With Deli Counter 0.176.0, none do.

`tests/test_kit_refuses_collision.py`:
- the plan still names the collision;
- a collision fails the build (fails on 1.61.0);
- the controls: a clean kit passes, and a failed module still fails.
