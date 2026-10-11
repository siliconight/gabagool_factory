## [1.99.1] - a hemisphere is the upper half it names, and every cap stands on its body

### What changed

**Roadmap 232, found by the dome.** `geometry.add_hemisphere` documents an
"upper hemisphere shell (open bottom)" and kept the LOWER half: its bisect
pointed the plane normal down, and `clear_inner` clears the side behind the
normal. Measured in Blender 5.1.1 at radii (0.5, 0.5, 0.3): z -0.3 .. 0 at
every ring count, the mean face normal z -0.74. Every caller lays it as a cap
on top, so every cap hung inside its own body. Built the way a kit build
builds them, at the genome's default corner:

- the **bollard** was flat-topped, its domed cap inside its pipe;
- the **exhaust fan**'s hood was a bowl hanging around its drum, and the fan
  stood 0.385 m in a 0.55 m slot, 70 % of its height;
- the **soda cup**'s lid dome hung inside the cup, under its lid;
- the **helmet**'s whole shell was a bowl below its rim.

And at an odd ring count -- `segments` 14 asks for 7 rings, and the helmet's
genome allows 12 to 32 -- no ring lies on the cut, the bisect makes the rim's
vertices new, and only the sphere's own vertices were transformed: 14
vertices left at radius 0.975 on a hemisphere asked for at 0.5, a spiked
disc around the helmet. A plan reaches it only when a prompt names the count.

- **The helper keeps the upper half** (the plane normal up), transforms the
  cut's vertices with the rest, and raises if the bisect leaves nothing
  rather than falling back to every vertex in the bmesh, which other parts
  share.
- **The bollard builds its cap inside its height**: the pipe stops short by
  the cap's rise (`CAP_RISE`, 0.42 of the foot's radius, the depth it always
  asked for), so the crown lands at h/2 and `fit_to` has nothing to scale;
  the bands keep their heights.
- The exhaust fan, the soda cup and the helmet change nothing of their own:
  each was written for the half the helper names.
- **The dome builds the same.** It lays its bowl by |z| since 1.98.1; built
  on 1.99.0 and on 1.99.1, its every vertex, face centre and face normal
  match to 0.01 mm.

Nothing in a level moves: no job asks Zoo for any of the four today (no
roof-props job is emitted, and no tool names a bollard, a soda cup or a
helmet). The fix is the library's: whoever asks for one gets what its genome
describes. The probes are `docs/findings/hemisphere_half/` in the factory.

**Census:** `blender -b --python tools/coplanar_census.py -- --species bollard exhaust_fan soda_cup helmet dome_fixture` on Blender 5.1.1, on an unpatched clone and on the patched one: the same triangles at every corner (bollard 550, exhaust_fan 224, soda_cup 420, helmet 480, dome_fixture 310) and 9 of 15 builds with coincident pairs in both. The unpatched clone reproduced `tests/test_coincident_faces.py`'s rows for the three species that have one, exactly -- the control that the census reads what the table recorded -- and two of them read differently after, and move with it: the soda cup's nearest cover from 0.21 mm to 2.0 mm (the 0.21 was its lid dome, hanging inside the cup 0.21 mm from the body and lip's pair; the nearest surface now is the lid's underside), and the exhaust fan's count from 3 to 4 -- its one buried coincidence at the default corner, the drum's foot on the curb, 1,725.46 cm2, counted as two pairs of 1,150.31 and 575.15 cm2 since: the same parts and the same area. The table's total goes from 2,995 to 2,996 with no coincidence new, and the helmet and the dome stay clean.

### Tests

11 in a new `tests/test_hemisphere.py`, 10 of them building in Blender (they skip without bpy): the helper keeps the upper half with every vertex inside the radii it was asked for, at 10, 12, 14 and 20 segments; each of the four caps crowns its body (a dome's top is its pole, a flat top or a bowl's rim reaches the full radius); the bollard and the exhaust fan stand their slots' full height. Run inside Blender 5.1.1 on the patched clone and again on the repo: 11 passed, with the three census rows above, 14 in all. On the unpatched clone: 10 failed and 1 passed, the bollard's height, which held before as well because its cap hid inside it.

**Suite:** 4,155 passed, 434 skipped (the builds that need bpy), 1 xfailed, exit 0 on the repo: 1.99.0's 4,154 and the new pure test, the 10 new bpy tests among the skips and run inside Blender as above.
