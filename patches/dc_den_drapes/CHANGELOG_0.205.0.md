## [0.205.0] - a den's windows are drawn shut

**The walker, 2026-10-09,** walking club_block_014 (roadmap 219, note 2):
"the windows in any 'den of sin' building should have curtains or drapes or
blinds So people outside can't see in, and you keep the streetlight light out
of the club". strip_club_a01's one window was clear glass, with an area light
behind it standing for the street through the glass.

### What it is now

**Every window of a strip club hangs Zoo's `window_drape`** (>= 1.91.0): two
velvet panels drawn shut under a pelmet, on the room side of the glass. The
rule, `level_design.plan_den_drapes`, places each one off the window the
builder cuts:
- centred on the window's own snapped position. strip_club_a01's is at x
  12.0, where `pos * run` alone says 11.9;
- 0.15 m past each jamb, and 0.10 m under the sill;
- its pelmet 0.15 m over the head, where the ceiling allows;
- 0.03 m off the wall's inner face, as a window poster is taped;
- turned to face its room;
- with no collision, since the window's pane seals the opening;
- in `velvet`, declared with the club carpet's `Curtain` acoustics.

**`furnish` runs the rule beside `dress_club_rooms`,** so a generated den
hangs its own: the `strip_club` preset is windowless today. A new migration,
`migrate_den_drapes.py`, applies it to the authored specs, whose furnishing
is baked in. Both are idempotent:
- a drape already there is replaced by the rule's;
- one the rule no longer asks for is removed;
- the migration puts a new one before the pieces `furnish` wrote.

**The library's dens.** Two of the three strip clubs have windows:

| club | drape | at (m) | size (m) |
|---|---|---|---|
| strip_club_a01 | `window_drape_s0_1` | (12.0, -11.74, 2.475) | 1.5 x 0.16 x 1.55 |
| strip_club_a03 | `window_drape_s0_1` | (11.0, -11.74, 2.475) | 1.5 x 0.16 x 1.55 |
| strip_club_a03 | `window_drape_s1_1` | (-11.0, -11.74, 5.725) | 1.7 x 0.16 x 1.65 |
| strip_club_a03 | `window_drape_s1_2` | (11.0, -11.74, 5.725) | 1.7 x 0.16 x 1.65 |

strip_club_a02 has none.

**A draped window lets no light in.** `lights.derive_light_anchors` derives
no `window` area light behind a drape (`_drapes_window`). The window is still
counted first, so every other window on its wall keeps its light's id, and an
authored override keyed on that id still finds it. The report counts
`draped_windows`.

**Furnish never sees a drape.** The suite's first run failed four
fixed-point tests (`test_back_bar`, `test_club_fixtures`, `test_club_rooms`,
`test_wall_backing`). Re-furnished with its drape present:
- strip_club_a01's club room was re-drawn, fourteen pieces named differently
  and three fewer;
- strip_club_a03's upstairs room gained a chair.

A drape's foot is 1.3 to 1.7 m up, under `_HUNG_MIN` (1.8 m). So it was
counted as a piece the room held (`_room_volume_count`), and cleared as a
floor piece by `_seed_clear`'s 0.9 m. Now:
- **`_hung(v, floor)`** sits beside `_HUNG_MIN`. The five clearance checks
  that read `_HUNG_MIN` ask it (four `if`, `_seed_clear`'s `elif`), and it
  calls a drape hung. Every other volume answers as before.
- **`_room_volume_count` leaves a drape out:** the window sign's defect a
  fourth time (0.160.0, 0.170.0, 0.201.0). It is not a rule by foot height,
  and that was measured: over the library's 1,345 collision-free volumes, such
  a rule would move 683 of them. They are furnish's own posters, banners and
  hangers, which count toward a room's target today, so the rule would
  refurnish the library.
- **A drape is safe to ignore.** It spans its window and 0.15 m past each
  jamb, against the wall, where `_clear_of_openings` already keeps a wall
  piece 0.9 m clear.

The library is a fixed point of furnish again.

**The name reaches Zoo's species.** `prop_species` routes `window_drape`
after `window_sign`. Nothing earlier in the table claims the name (`draped`
is `dust_sheet`'s, and `window_drape_` does not contain it). Each drape's
dims fall inside the genome's ranges, so Zoo builds the species and not the
fallback box.

### The price

One draw a window: the species is one material. 944 to 1,064 triangles a
drape (Zoo 1.91.0), four in the library.

### Tests

`test_den_drapes.py`:
- every window of a strip club hangs one drape over the window the builder
  cut, measured against `build/<club>.gameplay.json`'s openings: centred,
  wider, from under the sill to over the head and under the ceiling, on the
  room side, turned to it;
- no other building is draped;
- the rule is idempotent, declares its velvet once, and removes a drape it
  no longer asks for;
- furnish never sees a drape: under the hung line, hung all the same, and
  out of every room's count;
- the name reaches Zoo's species, inside its genome;
- a draped window draws no light while the next keeps its id;
- the library's clubs carry their drapes (`migrate_den_drapes.py --check`);
- the built clubs draw no window light.

On 0.204.1 the file does not import: no `plan_den_drapes`, no
`lights.DRAPE_NAME`, no migration.

**The suite:** 1,368 passed, 2 skipped (`python -m pytest -q`). 0.204.1's
were 1,358 and 2; the difference is `test_den_drapes.py`'s 10.

**The library was rebuilt:** all 146 shells (`build.py --all`), after the
migration.
- **The two clubs changed in substance:** their slots carry the drapes,
  their lights lose the windows (a01's one, a03's three), and their
  gameplay files add the velvet and the drapes' roles.
- **Every other manifest changed only its `built_utc`.** No GLB changed.
