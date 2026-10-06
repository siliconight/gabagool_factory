# Cold run 9113 -- a warm bulb over the register, a beer sign in the window

The walker, 2026-09-29: "add the warm counter accent and the window sign
next", from their 1990s lighting reference. Deli Counter 0.160.0, Zoo 1.27.0,
Lux 0.59.0. Zero interventions; the art leg read before export: 0 blockers, 64
findings, identical to 9112 code by code except the two the change owns --
ZOO_FIXTURES_MARKERLESS (21 -> 22 fixtures: the counter's pendant) and
PRESENTATION_TINT_MATERIALS (685 -> 691 entries, 222 -> 223 GLBs: the sign).
Same lot as 9112 (replayed: the window sign changes no shell's fitness).

## First, an instrument defect, which is the larger finding of this run

`tools/look_shots.gd` photographed the level DURING Level Factory's shader
warm-up (`warmup.gd`, LF >= 0.99.0, 2026-09-21), which sweeps at
`scaling_3d_scale` 0.1 with occlusion culling off for ~360 frames behind a
black cover -- and look_shots hides that cover as a HUD layer. It settled 10
frames and shot. So a look_shots frame of any package exported since
2026-09-21 was a 160 x 90 render stretched to 1600 x 900, until it was not.

How it was found, kept because four theories died first: the window sign
rendered as broken red dashes. REFUTED in turn, each by a probe that changed
one thing: occlusion by the store's glass or the sign's own sheet (hidden --
no change); Godot's automatic LOD (threshold 0 -- no change); the level's
post layers, glow and fog (off -- no change); every light (off -- no
change); Lux's emissive binder and stylized shader (read: neither touches
the mesh). The sign rendered WHOLE alone in the same project, and a second
copy spawned in the open broke the same way, so it was the level; a probe
reading the viewport 60 frames in printed `scaling_3d_scale=0.100`.

Fixed in `tools/look_shots.gd` (root repo, not one of the ten hashed tool
repos, so the run's zero stands): it waits for any node carrying
`warmup_finished` to stop running -- 358 frames here -- refuses to measure if
one is still running after 5,000, and stamps `scaling_3d_scale` and
`occlusion_culling` on every shot. Every shot in this file is at 1.0.

What it touched, measured rather than assumed: frame-wide statistics barely
move -- 9112's cooler wall at 8 m read 16.1 / 7.0 mean at 10% and 16.6 /
7.4 at full scale -- so the brightness and crushed-black figures of cold runs
9102-9112 hold to within a code or two. FINE DETAIL did not survive it:
strokes, lettering, small bright points. At full scale the price pylon's
FLAPPHAS reads at 30 m (`accent_and_sign_9112_vs_9113.png`, bottom row) --
and the case for making it 3.4 m (Zoo 1.26.0, cold runs 9109/9110) was
judged from 10% frames. That decision is the walker's to revisit.

`level_factory/tools/perf_stations.gd` is NOT affected, checked rather than
assumed: it warms every station itself (~560 frames after a 120-frame
settle) before timing, so the package's warm-up has restored full scale
first, and the package has no Camera3D for the warm-up to hand the view back
to. (The run journal's observation said otherwise; this corrects it.)

## The counter accent

It is applied, and it is subtle. The counter's face and top, full scale:
RGB 54.8 / 46.1 / 33.1 in 9112, 59.0 / 48.3 / 34.2 in 9113. At 10% scale a
probe scaling the lamp alone put 0x / 1x / 3x / 10x at red 53 / 58 / 63 /
71 -- it responds, so it is not lost to the per-mesh light cap, though the
counter's laminate top is the most crowded mesh in the store (11 lights
reach it, over the cap of 8, 10 of them before this). Energy is a free
lever: one light costs the same at any level.

## The window sign

At full scale it reads -- WOODER ICE, red on a blue border -- crisp at
1.5 m, legible at 4 m, where thin strokes begin to fray. Its door-side end
sits behind the store's lit sign box over the entrance (2.6 m wide, 0.68 m
outside the wall, 2.25-2.85 m up): `migrate_window_sign` measured clearance
from the door opening and never asked about the box. That is a placement
defect for Deli Counter.

## Cost, priced

Fresh package copies, `perf_stations_run.py` twice each, alternating, one
session. Same lot, so the stations are the same 14 and the headings the same
53:

    draws, heading by heading       44 of 53 identical; 60,638 -> 60,672
                                    total (+34); largest +15, one heading
                                    facing the store
    worst sightline                 2,620 both
    mean worst-heading p95          6.69 / 6.74 ms -> 7.89 / 6.95 ms
    positional lights               111 -> 112
    meshes over 8 lights            40 -> 43

The 7.89 is one run's spikes (player_start_26 20.1 ms in run c, 10.0 in run
d); the clean runs are within noise.

**Frame:** `counter_accent_0x_1x_2x_3x.png`, the four counter-accent strengths side by side (2026-09-29), filed with this record on 2026-10-06.
