## [0.29.2] - no conduit to a sign's face

### Fixed
- **A sign is no longer a conduit target** (`anchors.conduit_targets`,
  whose default kinds are now `("wall_pack",)`). Roadmap 220.
  - **Deli Counter stands a sign's light anchor on the sign's face,**
    `_SIGN_OUT` (0.2 m) proud of the wall, and hangs every sign it derives
    over a door.
  - **So the run stood 0.2 m out in the air.** `openings.apply` started it
    above the door head, as it should. That left a 0.27 m stub from the
    head to the middle of the lit face, standing through it.
  - **Walked** as a light vertical bar on strip_club_a01's door sign in cold
    runs 9213 and 9217. All three signed buildings of club_block_014 ordered
    one.
  - **Found by hiding things and looking:** of the 19 meshes within 2 m of
    the bar, hiding `Dressing/CoverN_concrete` alone took it from luma 243
    to 90, against the face's 122. That merged mesh holds a 0.05 x 0.04 x
    0.27 m box on the face plane (`docs/findings/sign_bar/` at the factory
    root).
  - A cabinet sign is fed through the wall behind it. Nothing runs up the
    outside of the wall to its face. Wall packs keep their conduits.
- **The CLI's note when no conduit is ordered** now tells a missing
  `<name>.lights.json` from a manifest with no wall pack. Without the sign,
  a lights manifest whose only exterior fixture is a sign orders none, and
  is not missing.

### Tests
- `tests/test_sign_conduit.py`, 4 tests:
  - a sign is not a target;
  - a wall pack still is;
  - the signed door orders no stub. This one fails on 0.29.1;
  - the 0.29.1 order, through the opening pass, is the 0.27 m stub on the
    face plane that 9217 shipped. It is the instrument for the claim, and
    it is kept.
- `test_anchors.py`'s target list loses the sign.
- Suite: 387 passed, 1 skipped in the working tree. On a `git archive` of
  HEAD, where seven tests skip, 380 passed and 8 skipped, against 376 and 8
  on 0.29.1's.
