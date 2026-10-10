# A traffic signal's lenses on one clock (Level Factory 0.165.0, roadmap 219 note 9)

**Question.** The walker, walking club_block_014 on 2026-10-09: "stop lights
are only bright for 1 color at a time, and if you have 2 here, they need to
be the same". Zoo's `traffic_signal` lights all three lenses at strength 1.6
on purpose, and leaves which is lit to whoever runs the level. Level
Factory 0.165.0's import gives each `M_TrafficSignal_Lens_<colour>` material
a lit shader on one 60 s clock:
- green from 0 to 33 s;
- amber from 33 to 37 s;
- red from 37 to 60 s.

Does Godot run it that way?

**Frame and units.**
- Times are seconds of the probe's own clock: the sum of `_process` deltas
  since its first frame. That is not the shader's `TIME`.
- Brightness is the mean, over a 5 x 5 box at a lens's centre, of each
  pixel's brightest channel, 0 to 1.

## Why every head can share one clock

Lot stands a signal only on a yielding leg's corner
(`site_furniture.plan_traffic_control`). Placed on Lot's own test
junctions:

| junction | pole | at | yaw | heads face (plan) |
|---|---|---|---|---|
| tee | `Signal_1L` | (-7.55, 8.4) | 270 | (-1, 0) |
| cross | `Signal_1R_0` | (6.55, -8.4) | 90 | (1, 0) |
| cross | `Signal_1L_1` | (-6.55, 8.4) | 270 | (-1, 0) |

- **The through road runs along x,** so every head faces along it: both
  directions of it at the crossroads, and no head faces the side street.
- **So every head at a junction serves the same traffic,** and shows the
  same lens.
- **The facing is computed** with `site_furniture.plate_facing(yaw)` for the
  model's -Y, where Zoo hangs the heads.

## The probe

`probe.gd` (`extends SceneTree`, windowed, quits itself) runs in a minimal
project. `project.godot` sets GL Compatibility, as packages ship.
- **The project holds cold run 9213's signal GLB,**
  `cover/prop_traffic_signal_delco_1997_01_w800_d62_h650.glb`, as
  `signal.glb`, with its steel's two textures.
- **It also holds the patched `zoo_worldskin.gd`,** from a Level Factory
  copy with the patch applied (`LF_ROOT=<copy> ... --draft`), byte-identical
  to the committed one.
- **`signal.glb.import` is the package's own,** with its paths pointed at
  the probe. It keeps `meshes/light_baking=2` and the import script.

`godot --headless --path <probe> --import` printed (`import.log`):

    [worldskin] signal.glb  3 signal lens surface(s) given the junction's clock

The probe printed each lens surface's material (`run2.log`):
- red: `ShaderMaterial`, window 37.0 to 60.0 s, energy 1.44;
- amber: `ShaderMaterial`, window 33.0 to 37.0 s, energy 1.57;
- green: `ShaderMaterial`, window 0.0 to 33.0 s, energy 1.31.

The energies differ by colour because Blender's exporter folds each colour's
peak into the strength: 0.90, 0.98 and 0.82 times 1.6. The emitted light,
colour times energy, is what Zoo asked for.

## Results

**Run 2** (`run2.log`) sampled every half second from 28 to 42 s, plus 8
and 47 s:

| probe time | near head | mast head |
|---|---|---|
| 8.0 to 33.0 s | green | green |
| 33.5 to 37.0 s | amber | amber |
| 37.5 to 42.0 s, and 47.0 | red | red |

- **The two heads agree in all 31 samples.**
- **A lit lens reads 1.00.** An unlit one reads 0.06 to 0.11.
- **The transitions fall between 33.0 and 33.5 s, and between 37.0 and
  37.5 s.** Those are the windows' 33 and 37.

**Run 1** (`run1.log`) is kept. It sampled 8, 35 and 47 s, and at 35 s both
heads were already red. In that run the probe's clock and the shader's
`TIME` were at least 2 s apart. This probe cannot say why: it reads its own
clock and not `TIME`. Its other two samples agree with run 2.

Run 1's readout was also the wrong instrument. It averaged the brightest
0.5 % of each half-frame, which took in sunlit steel, so 35 s and 47 s read
identically. Run 2 reads each lens at its own pixels.

`signal_states.png` is the three states, cropped from run 2's frames at 8,
35 and 47 s.

## What this does not show

- **A level:** the bake, Lux's grade, fog and a real night.
  - The lens keeps its lightmap only if a lit custom shader takes one,
    which is Godot's rule and is not measured here.
  - The proof run's frames are owed.
- **What the bake does with a lens's emission.** It bakes whichever lens is
  lit at the moment the editor bakes. Before, it baked all three at once.
- **Junctions out of step with each other.** One clock runs every signal in
  the level.
