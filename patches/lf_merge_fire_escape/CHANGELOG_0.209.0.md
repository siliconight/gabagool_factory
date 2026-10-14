## [0.209.0] - A walk-up's fire escape merges with its front

**Factory roadmaps 156 and 241, found pricing cold run 9303** (Zoo 1.110.0's `fire_escape`, stood by Deli Counter
0.220.0, against 9302): +3.3 draws a heading on the mean and +26 at the worst. `merge_empties.gd` takes apart every
slot child of an Empty whose name gives a side and merges its surfaces one mesh a side per material. The fire
escape's slots, `fire_escape_<storey>` and `fire_escape_drop`, give none, so each stayed a module drawn on its own:
four to six a walk-up, 28 on 9303's picked candidate. The factory's proposal had counted one more draw a front
("the per-side merge carries it"). 0.196.0 met the same with the rowhome's stoop.

- **`_side`** gives a `fire_escape_*` slot the front's side, S. Deli Counter stands the stack on the S wall, and
  `fire_escape_stack.plan` refuses any other side. Every storey and the drop wear one material, Zoo's painted steel
  (`M_Skin_metal_painted_delco_1997_0f0f11` on all four of a walk-up's GLBs), so a stack joins the front's groups
  as one more mesh. No collider is copied: Deli Counter writes none.
- **`test_a_walk_up_s_fire_escape_merges_with_its_front`** pins the GDScript's rule, which 0.208.0's source has
  not got.
- **`test_deli_counter_stands_a_fire_escape_only_on_the_front`** reads Deli Counter's schema through
  `tests.siblings`. The rule is right only while `fire_escape_stack` names the front alone: a second side there
  fails it before a back stack is merged into the front's mesh. Skipped where Deli Counter cannot be found; a
  schema without the field fails.

**Merged:** on a mirror of cold run 9303's package -- its Empties merged by 0.208.0, each walk-up's fire escape left as four to six modules -- 0.208.0's `merge_empties.gd`, the control, takes nothing from the four walk-ups ("no side to merge" on each); 0.209.0's takes in each one's storeys and drop (5, 6, 5 and 4 meshes, a surface each) and makes one merged mesh of them, unwrapped, with no collider to copy; over the six other Empties it takes nothing ("no side to merge" on each) (the factory's `docs/findings/fire_escape/merge_fire_escape.sh` and `merge_fire_escape.out.txt`)

**Suite:** exit 0, 2,427 by the progress tally (2,412 passed, 14 skipped, 1 xfail): 0.208.0's 2,410 passed and the two new tests. Each new test fails where it should and passes on 0.209.0 (the factory's `patches/lf_merge_fire_escape/prove_tests.out.txt`): the rule test against 0.208.0's script, the schema test against a Deli Counter whose enum names a second side and one whose schema has no field
