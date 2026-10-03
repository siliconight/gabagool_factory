# The light-bake probe (roadmap item 31)

The walker, 2026-10-03: "baked lights now?" -- the second item of the order
agreed after the crowns (`memory: work-order-after-crowns`). Item 31 asked
for a probe before any fix is quoted: set static lightmaps on one package's
import, open it, see whether a second UV set appears.

## Step 1: can the geometry get a second UV set? Yes.

`patches/lightbake_probe/prepare.py` on a copy of `_runs/walk_export_dumpsters`
(gas_block_001, seed 9080, Lot 0.90.0 / Zoo 1.58.0), then a headless
`--import`, then `uv2_census.gd` over the instanced site:

    models set to static lightmaps (meshes/light_baking 1 -> 2)   193
    models kept dynamic (already carry TEXCOORD_1)                  7
    inline primitive meshes given add_uv2 (ground, roads, walks)  1384
    import                                                 29 s, 0 errors
    mesh instances                                              3328
      with a second UV set                                      3279
      without                                                     49
    lightmap size hints on the imported meshes, summed      4.3 Mtexels

The 49 without are exactly the seven kept-dynamic models' remaining meshes:
the London plane and the red maple (crown sway), both ATMs and the video
poker machine (screen shutter schedules), the roller grill (turn pivots)
and the slush machine (churn). Their TEXCOORD_1 is data a shader reads;
static lightmaps on their import would overwrite it, so a bake must leave
them dynamic, which their motion asks for anyway.

Item 31's other worry, the unwrapper failing across ~183 meshes a shell,
did not happen: zero import errors.

## Step 2: can a bake run unattended? Yes, through the editor's own button.

Godot 4.7 exposes no bake call to a script: `LightmapGI` has its settings
and no `bake()`. The proposal to expose it (godot-proposals #8656) is open
with an unmerged pull request, and the forum has no workaround. So
`patches/lightbake_probe/bake_plugin.gd` is an editor plugin in a Forward+
copy of the package (only a RenderingDevice can bake) that opens
`bake.tscn`, selects its LightmapGI, presses the Bake Lightmaps button,
answers the one dialog that follows, saves, and quits. `run_bake.py` bounds
it and kills only its own process tree.

Three things this cost, each worth knowing before it is a job:

- **A LightmapGI with no data file makes the editor ASK where to save**, in
  a modal file dialog ("Select lightmap bake file:"). The first site run
  waited 25 minutes for light data behind it, on the walker's screen. The
  plugin now reads every visible dialog, answers that one with
  `res://bake.lmbake`, and stops on any other within seconds.
- **A bake and a save each pump the editor's main loop**, which calls the
  plugin's `_process` again from inside them; the first control run's save
  recursed until the stack overflowed. The plugin holds a busy flag across
  both.
- **The editor rewrites project.godot on save and drops a setting at its
  default.** Forward+ is the default, so the renderer line vanished;
  `prepare_compat.py` writes Compatibility explicitly.

Measured (control: a plane and a box, one static omni; site: the walker's
lot, 77 steady rigs marked static, 17 failing fixtures left live):

    control    bake 5.1 s    2 users      one 128 x 128 layer
    site       bake 22 s     3270 users   512 x 512 x 36 layers, 28 MB EXR,
                                          9.4 MB imported (BPTC)

## Step 3: in GL Compatibility, the steady streetlights' pools were gone

The baked package back on GL Compatibility (`prepare_compat.py`), shot at
six stations with the level's own lights only (`lit_shots.gd`) against the
same package unbaked:

    station        draws unbaked  draws baked   luminance unbaked  baked
    lot north         1,562          1,215          0.0669        0.0671
    bank west         1,490          1,401          0.1530        0.0978
    station front     1,440          1,354          0.1663        0.1627
    bank front        1,546          1,437          0.1467        0.1552
    street            1,944          1,567          0.0927        0.0905
    above             3,249          2,619          0.1601        0.1360

Draws fell 6-22 % everywhere. But from above, every steady streetlight's
pool was missing; only the failing poles, left live, still lit the ground.
The lightmap itself (`lightmap_layers.png`) held indoor pools, windows and
spills, and no outdoor ground pools.

**The cause was Lux 0.64.0's own fix.** It hung a pole's lamp 0.10 m below
the mount; the mount is 5 mm above the shaft's cap, so the lamp sat inside
the steel. A shadow map culls the shaft's inside faces and drew the pool;
the lightmapper ray-traces. The pole control (`make_pole_control.py`, one
closed 6 m pole and one static spot):

    lamp inside the shaft (0.64.0)             0 lit texels   max 0.005
    on the axis at the lens point (to 0.63.0)  2,815          max 0.039
    0.2 m along the head, 1 cm under the lens  5,581          max 20.9
    no pole at all                             5,605          max 3.0

Lux 0.65.0 puts the pole's lamp 0.2 m along the head, 1 cm under the lens,
beside the pole (`patches/patch_lux_pole_lamp.py`). The run after it is
`v2/` below.

## Step 4: priced on a quiet machine (`price/`, 2026-10-03)

The v2 pair (Lux 0.65.0's pole lamps, the same lot baked and unbaked, raw
GL Compatibility packages), on the fixed-station harness with no other
Godot running, alternated unbaked, baked, unbaked, baked:

| package | mean median ms | mean p95 ms | mean GPU ms | mean draws |
|---|---|---|---|---|
| unbaked, run a | 5.14 | 5.73 | 2.24 | 1078.2 |
| baked, run a | 4.29 | 4.95 | 1.75 | 933.1 |
| unbaked, run b | 5.18 | 5.82 | 2.23 | 1078.2 |
| baked, run b | 4.39 | 4.98 | 1.80 | 933.1 |

    median ms, baked minus unbaked:   -0.85 (pair a), -0.79 (pair b)
    GPU ms,    baked minus unbaked:   -0.49, -0.43
    controls (same package twice):    unbaked +0.04 ms, baked +0.10 ms

About 16 % off the median frame and 20 % off GPU time, eight to twenty
times the controls. No view of 53 got slower by more than 0.3 ms. The
heaviest views gain most: the extraction and attacker-spawn views looking
across the lot drop ~3 ms each (extraction_14 at yaw 90: 13.5 to 10.5 ms,
2,730 to 2,115 draws). The earlier run's 1.1 ms control was the walker's
Godot window competing for the GPU; with it closed the controls are
0.04-0.10 ms.

Not yet measured: the light leak and per-mesh light cap claims (expected
from how a static light treats lightmapped surfaces), and bake quality
above Low. Not yet decided: which lights may bake (the power-cut beat and
the Lux presets cannot change a baked light's effect on the level).
