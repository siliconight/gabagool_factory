## [0.211.1] - a stoop is circulation, not a prop standing in it

**Found by cold run 9271** (0.211.0 in a real drive, 0 interventions): `PRESENTATION_CIRCULATION` 0 -> 12,
one a rowhome -- "stoop_landing 0.15 m into doorway:ext_0_S_open0". 0.211.0 drew the landing and treads
with the surface role `prop`, and this repo's circulation gate (`circulation.check_shell`, run on the
greybox shell by the compose) asks of every `prop` whether it stands in a doorway's walk-through volume.

**The 0.15 m is the gate's, not the stoop's.** `doorway_volume` starts a door's volume at its wall's
bottom plus its sill; `_opening_piece` opens the door at the slab's top (`floor_thick` / 2, 0.15 m on an
Empty) plus its sill; and a landing's top IS the threshold. At grade the offset never showed, because
the 0.15 m under every door is slab and a prop stands on top of it. It is recorded here and not changed:
moving every doorway volume moves every building's gate, and the fix is a slot field the gate can read
(an opening's own bottom), which is Zoo's input too.

- **`_stoop`** draws its landing and treads with the surface role `stair`: a stoop is the way to the
  door, as a flight's treads are, and the greybox paints it the climbable affordance's colour (`gb_stair`).
  The art pass still dresses each piece as a volume: its slot's `role` is the slot's own, `prop`.

**Built:** build.py --all, 146 shells; each rowhome's `surface_roles` names its `stoop_landing`, `stoop_tread_1` and `stoop_tread_2` `stair`, their slots still `prop` in concrete; `circulation.check_shell` on every built rowhome ok, no prop declared and none in a doorway

**Suite:** 1,432 passed; `test_stoop_circulation.py`, 25 checks, 24 of them failing on 0.211.0's built shells -- each the cold run's finding to the millimetre, `stoop_landing` 0.15 m into the front doorway, and the pieces `prop`
