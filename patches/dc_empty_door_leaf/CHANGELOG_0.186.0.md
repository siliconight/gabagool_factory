## [0.186.0] - an Empty's door is shut to a ray as well as a body

Roadmap 183. A door's aperture is a walkable void (`_opening_piece`), which
is right for a building you enter. On an Empty -- a sealed, hollow facade
shell -- it was a hole.
- The door module's jambs left 0.7 m, which stopped the 0.8 m walk capsule.
- It did not stop a shot: rays passed 10 m into `gs_empty_rowhome_f`
  through its front door, at 1.0 and 2.0 m (cold run 9162,
  `patches/lf_empties/door_collision_probe.gd`).

**A facade's door is now filled full-thickness**, as its window's pane is
(`ext_<storey>_<facing>_open<k>_leaf`, and its `-convcolonly` collider).
The art pass's door module still draws the leaf; this is its collision. A
building you enter keeps its doors open.

Every shell is rebuilt (`deli_counter.py` is a geometry source).
