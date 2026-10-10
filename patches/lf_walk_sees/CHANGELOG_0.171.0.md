## [0.171.0] - The walk preview starts at the player_start, its visual check can see, and its hints name what the person has

**Roadmap 202's install test, step 4.** The factory was packaged, unzipped
into `C:\stranger_202\gabagool`, and `START_HERE.md` followed in cmd.exe.
`make` built cold run 9222's level, matching it figure for figure. Then
`.\factory -C levels walk restaurant_row_001` exited 0, and three things in
what it printed were wrong. The same command on 9222's own workspace printed
the same three, so they are Level Factory's, not the unpack's.

### The player stood at the origin

**What it printed:** "player at default (no markers) (x=0.0, y=1.5, z=3.0)".
- **Why.** The preview spawns at a marker it finds by reading the level
  scene's text. An export's level scene is `mission.tscn`, an entry that loads
  its content at runtime, so its text holds no marker.
- **Where the player should have been.** The package says where a player
  begins: `gameplay_anchors.json`'s `player_start`, the anchor the factory's
  own `tools/walk_export.py` spawns at. On 9222 it is the getaway van, at
  (53.85, 0, 16.965).

**Now `_spawn_from_anchors` reads that anchor first.**
- **The lift:** it adds the 0.6 m a marker gets, because the anchor sits at
  grade and the player's origin is its feet.
- **When it is not used:** the markers decide when there is no
  `player_start`, and the default stands when there is neither.
- **Not applied:** the anchor's `rot_y_deg`, since the marker path does not
  turn the player either.

### The visual check passed five black frames

**What it printed:**
`shot bot [OK] exterior: jitter 0.0%, void 0.0%`, and the same for four ladder
stations.

**What the frames were.** Every pixel of all five was 0.

**Why they were black.** `mission.tscn` carries the shader warm-up
(`warmup.gd`, since 0.100.0). While it sweeps, it:
- covers the screen with a black `ColorRect`;
- draws at a tenth of the resolution.

**Why black passed.** The shot bot photographed inside that sweep. Its two
measurements cannot see a frame that shows nothing:
- void is the magenta background;
- jitter compares a frame with its twin 1 mm away.

Both are 0 for black.

**The bisection.**
- August's `lot_demo_001` preview still gives real frames today with the same
  `shot_bot.gd`, so the binary and the driver are fine.
- 9222's preview gives real frames with `site.tscn` and black ones with
  `mission.tscn`, the scene `walk` passes.

**Now `shot_bot.gd`:**
- **holds every warm-up before the content enters the tree.** It finds one by
  its `enabled` switch, `cover_screen` and `warmup_finished` signal, sets
  `enabled = false`, and reports how many it held. The warm-up pays a
  compile bill this pass does not measure.
- **fails a station whose frame is one colour.** All sampled pixels within
  `DIFF_TOL` of the first means a cover, a scene that did not load, or a
  camera inside a solid. Either way it cannot vouch for anything.

**Measured on 9222's preview with `mission.tscn`,** Godot 4.7, the window
open:
- **The control, the old script:** five frames, mean luma 0.0, all OK.
- **The new script:** it held 1 warm-up. The frames read mean luma 100.9
  (exterior), 181.7, 105.5, 175.4 and 191.3.
- **Two stations now FAIL on jitter:**
  - Ladder_ladder_0_base, 3.60%;
  - Ladder_ladder_1_top, 2.33%.

  Both are over the 2.0% gate. With `site.tscn`, the same base station read
  3.02% on the old script.
- **So a defect was hidden in every export since the warm-up shipped.** Its
  cause is not established: coplanar faces, or aliasing along the
  drop-ceiling grid the threshold was not calibrated on.

### Next steps it named that the person did not have

The walk printed `open:  & "<godot>" --path ... -e` and
`play:  & "<godot>" --path ...`:
- `&` is PowerShell's call operator, and an error in cmd;
- the person may not know where Godot is.

They are now `<command> -C <workspace> walk <mission> --open` and `--play`,
which launch Godot from `tools.local.json`. `<command>` is
`discovery.command_name()`, 0.170.0.

The export printed two hints a person with only Blender and Godot could not
run:
- `godot --headless --path <dir> --import`;
- `python tools/walk_export.py ...`, the factory checkout's tool, not this
  one.

What it prints now:
- the import step, in words, pointing at `HANDOFF.md`;
- `<command> -C <workspace> walk <mission> --play`.

`HANDOFF.md` in every package now tells its reader to walk with
`level-factory -C <workspace> walk <mission_id> --play`. In an unpacked
factory that is `.\factory` or `sh factory.sh`.

### Tests
`tests/unit/test_walk_preview_sees.py`, 11.

The spawn's tests build a preview from an export-shaped folder: an entry
scene with no markers, a `site.tscn` with a spawn marker, and an anchors
file:
- the player starts at the package's player_start, lifted 0.6;
- an entry scene alone left the player at the default. This is a control,
  and it passes on 0.170.0 too;
- without a player_start the markers decide. A control;
- an unreadable anchors file falls back to the markers;
- a player_start without a position is not a spawn.

The shot bot's tests read the script, because it needs a display and this
suite has none; the run above is what proved it:
- it holds the warm-up before the content enters the tree;
- what it holds is what `warmup.gd` declares. A control;
- a frame of one colour fails its station.

The hints' tests:
- the walk names its own `--open` and `--play`, not PowerShell;
- the export names no command the person lacks, reading code lines, not the
  comment that quotes them;
- `HANDOFF.md` sends its reader to `walk`.

On 0.170.0 the eight that are not controls fail.

Suite: 2,147 passed, 14 skipped, 1 xfailed, 0 failed (exit 0). 0.170.0 gave
2,135. The 11 tests here account for 11 of the 12. The twelfth is
`test_sibling_locator`'s guard, which runs once per `.py` in the repo: 315
cases on 0.170.0 and 316 here.
