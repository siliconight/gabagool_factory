# The scout window: Level Factory 0.235.0 (roadmap 295)

The walker: a window at runtime showing the level's buildings and their 3D schematics, "in the style of a 1990s palm
pilot...but with a little more backlight and color", the score and key props of interest shown -- "we will have the
asset for the palm pilot, so just make sure the window can be called by something on the gameplay layer (seam is
clear and visible)".

**The seam** is `scout/README.md` in every package (`assets/godot/scout/README.md` here): `LFScoutWindow` --
`open(as_overlay)`, `close()`, `is_open()`, `buildings()`, `select(id)`, `get_screen_texture()`,
`set_points(id, points)`, `turn(degrees)`, `set_spread(t)`; signals `opened`, `closed`, `building_selected(id)`.

**Driven through the seam alone** (`drive_window.gd`, a mock package of cold run 9379's `buildings.json` and Deli
Counter 0.260.0's models): every call and signal as stated, `close()` stopping it; `seam_pharmacy.png`;
`seam2_office_override.png` -- a gameplay-placed score with `"storey": 2` riding its floor when the floors spread (the
first draft placed it absolutely and it vanished into the stack).

**In game** (`ingame_probe.gd`, cold run 9381's walk copy `_runs/walk_9381_restaurant_row_001`, the walk scene
loaded, the warm-up's own `warmup_finished` awaited -- the first run photographed the warm-up's black screen four
times -- then F6 and the right arrow pressed as keys): `ingame_walk.png`, `ingame_f6.png`, `ingame_f6_next.png`. The
debug overlay's figures in those frames, one session, one camera:

| | draws | ms/frame (2 s) |
|---|---|---|
| walking | 319 | 4.59 |
| window open, deli_a03 | 348 | 5.03 |
| window open, pharmacy_a01 | 388 | 5.04 |

**Owed, seen in those frames:**
- the first open hitches -- one 239 ms frame (`low 4.2 fps`), the model loaded and the window's shaders compiled on
  first use; a warm-up pass for the window, or loading on `open` behind a frame, wants pricing;
- the arrow keys still move the walk player while the window is open (x -2.2 -> -1.6 between the two open frames):
  the player polls the keys, the window consumes the event -- the stand-in caller should hold the player, as a
  gameplay layer will;
- pixel type: the default font; a CC0 pixel font is a download and the walker's yes.
