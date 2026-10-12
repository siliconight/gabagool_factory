# Cold run 9263 -- the pole line's wires in a real drive

**What it tested:** roadmap 240's third build in a real drive of restaurant_row_001: Lot 0.119.0's
wires (the walker's full set without house drops -- three primaries, the neutral, the secondary and
two cables -- along every pole line and tied across each junction, unshaded, casting no shadow,
drawn in the themed site only) and Level Factory 0.194.0 keeping their OBJs out of the lightmap.
Lot 0.118.1's corner pole is in its first drive too. Everything else as in 9262.

**Result: 0 interventions, 0 tool files changed.** seed_9104 picked, as in 9241 to 9262.

## The wires, as built

`wire_spans.py` on the run's own themed drawn spec, through Lot's own functions
(`wire_spans.out.txt`): 12 poles -- six on the main road's south kerb, three on each side street's
-- and 11 spans: 9 along the lines, 12.7 to 33.2 m, and 2 ties, each side street's corner pole to
the main line (Pole_25 to Pole_47, 12.7 m; Pole_28 to Pole_22, 16.4 m, across the main road). 7
cells, 7 nodes, 7,392 triangles; the lowest cable 5.43 m over the road, mid-span on the main line.
The west street's tie is new with 0.118.1: in 9262 its first pole stood at plan y 6.89, 34.6 m from
the main line, past the 30 m reach.

- **The themed scene** (`themed_site_assemble/1/out/site.tscn`): 7 `site_wires_c*` nodes, each
  `cast_shadow = 0`, `gi_mode = 0`, the shared unshaded material; the job wrote the 7 OBJs.
- **The graded lots** (`lot_assemble.candidate.seed_{9003,9104,9205}`): no wire node in any scene
  and no wire OBJ, 3 of 3. Laser Tag and the walk test grade those.
- **The export** (`light_bake.json`): `imports.unlit` names the 7 OBJs and `imports.baked` none of
  them; every wire sidecar keeps `generate_lightmap_uv2=false`; 497 models baked, as in 9262. The
  bake took 30.5 s (9262: 31.6) and its log has no UV warning.
- **Lightmap users 3,333 -> 3,338, not the wires.** Read out of `bake.lmbake` by name: the only
  user names in 9263 and not 9262 are `cover_151` -- the 152nd cover piece, the west street's new
  corner pole, four meshes -- and `hung_14`, one more piece hung on a pole. No user names a wire.
  Live rigs 26 -> 27: that pole's lamp.

## The findings: 120 -> 119, not the wires

`LT_MAP_TRAVERSAL` on seed_9104, 1 -> 0 (the validation report, candidate by code). Laser Tag read
the candidate at route completion 0.72 and 72 player-stuck events, where 9262 read 0.64 and 29
(9261: 1.00 and 9). Its graded lot carries no wires; against 9262's it differs only in its poles
(the drawn specs' cover: the west street's corner pole added, the east street's two restepped to
match). 64 of the 72 events stand at one place, plan (-68, -4) at the road's height -- the kerb face
roadmap 242 names, where 9261's bot stuck 6 times and 9262's 18. The furniture 40 m away rolls how
often the bot walks into it; the snag is the defect (roadmap 242).

**CORRECTED, the same day** (`docs/findings/route_snag/`): not a kerb face. The 64 stand at one point
to fifteen digits, plan (-66.35, -4.94), INSIDE the deli on its ground floor at the front register
counter's south-west corner, where the bot -- cutting the corner by its arrival radius -- touches the
counter and Godot Physics' `move_and_slide` takes the floor as every slide's collision and never turns
along it. Under Jolt the same three lots read 1, 7 and 7 player-stuck events where Godot Physics read
9, 29 and 72, and none at the counter.

## The price

`wires_price.sh`: the run's own package against a copy with every wire node hidden
(`wires_off.py`: `visible = false` under each of the 7 nodes in both scenes that carry them -- the
content `site.tscn` and Lux's `presentation/lux.applied.tscn`, which `bake.tscn` instances and
`mission.tscn` loads), Level Factory's fixed stations, GL Compatibility, control / subject / control
(`price/price.txt`; the harness names the subject `glow`):

    controls' spread, median over 53 headings: p95 0.09 ms, draws 0.0 (the noise floor)
    run        draws +mean   draws +min   draws +max   p95 +median ms  p95 +max ms
    control_1          0.0            0            0             0.01         0.38
    subject            2.2            0            6             0.05         0.63
    control_2          0.0            0            0            -0.01         0.56

The instrument sees them: a wire cell is one draw, and the subject reads +0 to +6 where the
controls read exactly the same as each other. The frame does not: p95 +0.05 ms at the median,
inside the controls' own 0.09 ms, and the subject's worst heading (+0.63) beside the controls'
worst (+0.38, +0.56). Seven cells cost seven submissions at most and nothing the harness can tell
from the noise.

**Found on the way, not the wires:** the level's worst heading reads 5,735 draws at p95 16.72 ms
(`player_start_19` facing 90), and five more read 4,700 to 5,500. That has been this level's shape
since 9241 (worst 5,257; 9245: 5,219), 2.6 to 2.9 times the provisional 2,000-draw budget. The pole
line itself -- 9262 against 9261 -- is priced in `docs/findings/pole_line/` (`poles_price.sh`).

## The frames

`wires.png`: the same copies shot at five stations, wires hidden left, as built right (eye 1.8 m over
the sidewalk, the mission's own evening light): `line`, `across` and `corner` are 9262's stations;
`west` looks at the new tie across the main road; `up` stands under the main line west of Pole_22
and looks up at its crossarm. The wires read as dark lines against the sky, sag between the poles,
leave each pole at its crossarm, spools and bolts, and cross both junctions. **For the walker's eye:**
past about 60 m a wire thins to under a pixel and draws as a dotted line (the far end of `line`) --
the shimmer the doubled radius was chosen to soften; whether it reads as wire or as noise in motion
is a look call, and the cheaper fix (a fade with distance) and the dearer one (a screen-space minimum
width in the vertex shader) are both unpriced.

## The time

    run    shell   art     export   walk   retire   the drive
    9262   77 s    160 s   175 s    10 s    4 s     7.4 min (444 s)
    9263   79 s    168 s   172 s    11 s   17 s     7.8 min (467 s)

The retire step removed cold-9259-ws (0.9 GB) this time.

## What is evidence of what

- The wires: `wire_spans.out.txt`; the themed job's `site.tscn` and OBJs; the candidates' outputs.
- The export and the bake: the package's `light_bake.json`, its sidecars, `bake.lmbake` and the
  bake's log.
- The findings and the route: the validation reports and Laser Tag's reports of 9261 to 9263.
- The price: `price/` (three reports and `price.txt`), `price/wires_off.txt`.
- The frames: `wires.png`; the PNGs and look_shots' json under `_scratch/frames_9263/`.
- The result: `cold_run.py --end`.
