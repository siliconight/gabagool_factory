## [0.30.0] - a wall's anchors face out and stand on its face

### Fixed
Roadmap 221, found in cold run 9217's orders for strip_club_a01 and measured
on its shell (`docs/findings/patina_cover_normals/` at the factory root).

- **The anchor pass's wall normals pointed into the building.**
  - `_up_to_z` views a Y-up shell by swapping two axes. That is a
    reflection, so every triangle's winding reverses in the view, and
    `_exterior_wall_faces` took its normals from cross products there.
  - On strip_club_a01 all 10 wall segments' normals pointed at the
    building's centre.
  - Zoo takes the normal as given: it turns each cover's proud face along
    it, and `dressing.cover_side` files the cover with the side it leaves.
    So every base course and conduit faced the wall and joined the opposite
    side's merge, and the per-side merge (Zoo 1.68.0) could not cull a
    building's back.
  - `_exterior_wall_faces` now negates its product when the view is a
    reflection, and `generate` says when it is: both of `_up_to_z`'s
    permutations are. `_up_to_z`'s docstring, which said it kept "a
    right-handed frame", is corrected.
- **The inside of a wall made anchors.**
  - `surfaces.classify` calls a vertical face an exterior wall when it
    faces out within `_BOUNDARY_TOL` (0.25 m) of the bounds.
  - On the club, the floor slab stops under each wall and the roof slab
    over it, both on the 0.3 m wall's centre line, 0.15 m in. With the
    ends of the interior walls meeting the wall, they made a segment on
    every wall's centre line.
  - 28 of the club's 51 base courses and 52 of its 57 curbs were ordered
    there, inside the wall.
  - `_buried` now asks of each point the pass would place whether another
    segment of the same facing stands in front of it, within
    `BEHIND_DEPTH` (0.5 m), across its run position and its height. A
    buried point is skipped, and its jitter is still drawn, so every other
    anchor stays where it was.
  - **Asked per point, not per segment.** The first draft dropped a segment
    a face covered whole, and on the club none was covered: the slabs run
    0.3 m below each wall's face and 0.3 m above it. Per point, a base
    course at the foot is buried, and a roofline on the roof slab's exposed
    edge is not.
- **A conduit ran from the pack, 0.15 m off the wall.** Deli Counter stands
  a wall pack `_WALL_PACK_OUT` proud of the face, and the run stood out
  there with it. It now takes its wall segment's plane, and keeps the
  fixture's run along it.

### Measured on strip_club_a01
Patina's own dressing job, replayed on the shell, read through Zoo's
`plan_dressing` (`replay_dressing.py` in the findings):

| | 0.29.2 | 0.30.0 |
|---|---|---|
| base courses facing out | 0 of 51 | 45 of 45 |
| base courses on their own side | 0 | 45 |
| base courses inside the wall | 28 | 0 |
| curbs inside the wall | 52 of 57 | 0 of 57 |
| conduits facing out, on their side | 0 of 2 | 2 of 2 |
| `wall_base` anchors | 64, the clamp | 54 |

The clamp (`max_per_kind`, 64) had been spending anchors on the centre
lines. With those gone, the faces take 54.

### Tests
- **`tests/test_anchor_normals.py`,** on a 20 x 12 m Y-up shell built in
  memory, with a floor slab under its walls and a roof slab over them, both
  on the walls' centre line:
  - the slabs' edges are exterior walls to the classifier: the premise;
  - every `wall_base` faces out of the Y-up shell;
  - a Z-up shell still faces out;
  - no `wall_base` stands inside the wall;
  - a point behind a face is buried, and one above it, past its run, or on
    a wall facing the other way is not;
  - a conduit runs on its wall's plane, not at its pack.
  On 0.29.2, four of the six fail. The premise and the Z-up guard pass on
  both, as they should.
- **`tests/test_sign_conduit.py`:**
  - its south wall's normal is now outward. 0.29.2 wrote the inward
    normal the pass then derived;
  - its kept instrument for 9217's stub now finds the stub on the wall's
    plane, -12.0, where 0.29.1 put it on the sign's face, at -12.35.
- **`tests/test_anchors.py`:** the helper that stands in for
  `_wall_segments` accepts the new keyword.

Suite: 393 passed, 1 skipped in the working tree (0.29.2: 387 and 1). A copy with no
siblings beside it, where seven more skip, ran 386 and 8 against 380 and 8.
