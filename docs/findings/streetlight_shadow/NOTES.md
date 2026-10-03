# The dark poles: their shadow was their own shaft cap

The walker, 2026-10-03, walking `_runs/walk_export_moving` (cold run 9139's
gas station lot) at night: "we still have quite a few street lamps that
aren't putting their light down"; after the first fix attempt, "streetlights
still not showing light"; then, with a frame from (80.1, 5.6), "another data
point, this one far away is working but the one closer isn't".

The first cause written for this (`docs/findings/light_cap/NOTES.md`) was
indoor light leaking onto the lot tiles and pushing them over GL
Compatibility's 8-lights-a-mesh cap. That finding is real on the tiles it
named and was not why the poles were dark; it is kept there with its
retraction. This file is the measurement that replaced it.

## Finding which poles, then why (`patches/lux_streetlight_hang/probes/`, run on `_runs/walk_export_heat`)

Every probe below (copied into `patches/lux_streetlight_hang/probes/`; each
is copied beside the walk's `project.godot` and run `godot --path . --script
<probe>.gd`; `cap_sweep.gd` runs in the Lux project with
`--rendering-method gl_compatibility`): the walk's own scene, every other light switched off,
a camera 9 m from the pole's foot on the lot side looking at the foot, the
frame's centre band read as luminance.

**The survey** (`pole_survey_probe.gd`): each pole's own lamp, then the lamp
hidden and a fresh `SpotLight3D` on its exact transform with the same range,
angle, energy and colour:

    pole          at (x, z)       failing  own    copy   verdict
    site_lamp_1   (-60.5, 13.6)   cycling  0.001  0.325  DEAD
    site_lamp_3   (-35.5, 13.6)   -        0.001  0.306  DEAD
    site_lamp_5   ( -6.5, 13.6)   -        0.373  0.396  alive
    site_lamp_7   ( 14.5, 13.6)   cycling  0.237  0.254  alive
    site_lamp_9   ( 39.5, 13.6)   -        0.286  0.305  alive
    site_lamp_11  ( 64.5, 13.6)   -        0.001  0.319  DEAD
    site_lamp_15  (-85.5, 28.7)   cycling  0.001  0.126  DEAD
    site_lamp_17  (-60.5, 28.7)   -        0.001  0.305  DEAD
    site_lamp_19  (-35.5, 28.7)   -        0.001  0.303  DEAD
    site_lamp_21  (-10.5, 28.7)   -        0.001  0.305  DEAD
    site_lamp_23  ( 14.5, 28.7)   -        0.001  0.306  DEAD
    site_lamp_25  ( 39.5, 28.7)   cycling  0.001  0.252  DEAD
    site_lamp_27  ( 64.5, 28.7)   -        0.001  0.307  DEAD
    site_lamp_30  (-87.7, -8.9)   -        0.001  0.204  DEAD
    site_lamp_32  (-87.7,-33.8)   cycling  0.001  0.238  DEAD
    site_lamp_34  (-72.6, -8.9)   -        0.088  0.097  alive
    site_lamp_36  (-72.6,-33.8)   -        0.188  0.201  alive

Twelve dead, five alive; not the failing kind, not the energy, not the
order in the tree, and no spatial pattern -- which is the walker's "the far
one works and the near one doesn't".

**The one stored difference.** `presentation/lux.applied.tscn` carries
`shadow_enabled = true` on exactly the twelve dead poles' lamps and on no
other positional light. They are the lights `LuxLighting.apply_shadow_policy`
gave the High tier's 12 shadow maps: rank 0 ("street") for all 17, the
tie-break a string sort of node paths, so `site_lamp_1, 11, 15, 17, 19, 21,
23, 25, 27, 3, 30, 32` carry a shadow and `5, 7, 9, 34, 36` do not. (The
pool probe's property diff had reported no difference between the dead lamp
and its fresh copy; the shadow policy had already run on both by then and
the diff compared the wrong pair. Reading the packed scene found it.)

**Shadow on, nothing drawn** (`shadow_probe.gd`): the dead pole's lamp reads
0.001; `shadow_enabled = false` on it, 0.286; back to true, 0.001. A fresh
spot on its transform: shadow off 0.286, on 0.001, off again 0.286; born
with shadow on, 0.001. A fresh OMNI there with a shadow: 0.654. Atlas 4096,
16-bit, quadrants 2/2/3/4.

**The dials** (`shadow_dials.gd`, a fresh shadowed spot on the pole's
transform): tilt 15 degrees, cone 30, range 8 -- 0.000-0.002; shadow bias
0.5 / normal bias 5 -- 0.527; reverse cull -- 0.000; `shadow_caster_mask`
0 -- 0.532; 24-bit atlas -- 0.096; 8192 atlas -- 0.095; 3 m up instead of
5.9 -- 0.278; moved 4 m toward the camera -- 0.630; cull mask layer 1 --
0.096; over the camera aimed at the foot -- 0.483. Nothing casting, or a
bias large enough to swallow something very close, lights the ground: the
shadow map holds a caster a hair from the lamp.

**The caster** (`occluder_probe.gd`): the meshes around the lamp's origin
(-10.5, 5.922, 28.7) are `cover_21/Streetlight_Lens` (y 5.922-5.942, 24
verts) and `cover_21/Streetlight_metal_delco_1997` (the base, pole and head
merged by material; 77 of its 284 verts within 12 cm of the lamp). The pole
with its shadow: 0.001; the lens hidden, 0.001; the body hidden, 0.284; the
body's `cast_shadow` off, 0.279. The lamp lowered 0.02 -- 0.282; 0.05 --
0.239; 0.10 -- 0.282; raised 0.02 or 0.05 -- 0.000 (`pole_mat_probe.gd`,
which also tried the body's cull mode BACK / FRONT / DISABLED and
double-sided casting at the origin: 0.001 every time).

**Reproduced in the Lux project** (`cap_sweep.gd`, Zoo's shapes: a 0.06 m
shaft, a shoebox head, the lens on the cap, GL Compatibility): the lamp
5 mm over the cap, 0.002; at or under the cap, 0.742 whatever the cull
mode; the shaft hidden, 0.745; the head or the lens hidden, no change; no
shadow, 0.742.

So: a spot's shadow map is a perspective camera at the lamp. Zoo's recipe
puts the lens point -- Lot's anchor, 0.175 under the module's top -- 5 mm
above the shaft's top cap, and a 6 cm disc 5 mm in front of the camera
subtends 85 degrees, the whole 55-degree cone. Every ground pixel compares
as shadowed. At or below the cap the disc is behind the camera and casts
nothing.

A refutation kept: the first reading of the occluder was the shaft's
SIDES, from a camera on the cylinder's axis; a clean cylinder with the lamp
exactly on its cap lit the ground fully (0.742) and refuted it before it
reached a constant.

## RETRACTED IN PART (2026-10-03, later): the 0.64.0 placement put the lamp inside the pole

The diagnosis below stands: the shadowed poles were dark because the shaft's
cap filled their shadow frustum. The fix did not. Hanging the lamp 0.10 m
below the mount put it 9.5 cm inside the steel shaft, whose cap is only 5 mm
under the mount. A shadow map culls the shaft's inside faces, so the walk
showed every pool and the walker confirmed it. The light bake ray-traces,
and baked those poles to nothing (`docs/findings/light_bake/NOTES.md`). Lux
0.65.0 puts the lamp beside the pole: 0.2 m along the head, 1 cm under the
lens. What was missed: the hang was measured only as "does the pool come
back", never as "where is the lamp relative to the solid it hangs in".

## The fix (Lux 0.64.0, `patches/patch_lux_streetlight_hang.py`)

`LuxStreetlightRig.LAMP_HANG_M` (0.10): the lamp hangs that far below the
mount; the loader solves the pole's energy for the lamp's height. Wall
packs are the same rig and hang the same. The derivation and the table sit
on the constant. Why Lux and not Zoo or Lot: Lot says where the lens is,
Zoo builds it there, and the fluorescent rig already hangs its lamp
`FLUORESCENT_MOUNT` under its hardware for the same reason.

`lux/tools/streetlight_shadow_selftest.gd` (windowed, GL Compatibility)
holds it with two controls: a slab under the lamp blacks the pool (shadows
draw at all), the lamp at the lens point blacks the pool (the instrument
sees what the walk showed), and hung the pool keeps at least 0.8 of its
unshadowed self. Run with the hang set to 0 it fails on the last check:

    hung 0.444   unshadowed 0.444   at the lens point 0.001   under a slab 0.000

Rebuilt `workspaces/moving-ws` (`run --art --gameplay`, then `export`);
the export's `lux.applied.tscn` carries the lamp at local y -0.1 and the
same 12 shadows.

## After the fix, on the rebuilt lot (`_runs/walk_export_hang`, a walk copy of the export)

The same survey, the same 12 poles still carrying shadow maps:

    pole          own    copy          pole          own    copy
    site_lamp_1   0.296  0.318         site_lamp_21  0.275  0.297
    site_lamp_3   0.275  0.298         site_lamp_23  0.275  0.298
    site_lamp_5   0.364  0.387         site_lamp_25  0.229  0.249
    site_lamp_7   0.218  0.235         site_lamp_27  0.278  0.300
    site_lamp_9   0.279  0.298         site_lamp_30  0.168  0.200
    site_lamp_11  0.286  0.312         site_lamp_15  0.090  0.101
    site_lamp_17  0.275  0.298         site_lamp_32  0.218  0.236
    site_lamp_19  0.271  0.296         site_lamp_34  0.085  0.094
                                       site_lamp_36  0.183  0.196

17 of 17 alive; every pole's own shadowed lamp reads 0.85-0.94 of a fresh
unshadowed copy, the shadow now costing only what the pole's head and the
things on the lot actually block. (The energies read 18.48 against 19.20
before: the loader solves for the lamp's height, 0.10 m lower.)

## The general instrument (`lux/tools/self_shadow_census.gd`)

Every rig light in a walk copy, read with its shadow off and then on from a
camera beside the first collider its axis hits, every other light off; the
summary names the lights that lose more than half their light to their own
shadow map. On the lot BEFORE the fix (first cut, downlight targets below
the floor, so the poles and most indoor rows were unreadable from outside):
one wall pack read 0.50, and every readable sign, pendant, bulb,
fluorescent and spill read 0.89-1.09.

Rerun with ray-cast targets on the rebuilt lot (`census_after.txt`): 94 rig
lights, 20 unreadable (the camera beside the target saw under 0.01 with
the light on and no shadow -- indoors, behind a wall from where it stood),
the 17 poles at 0.97-1.00 but one, and two flagged: `Spawned_fluorescent_004`
(0.053 to 0.000) and `site_lamp_34` (0.051 to 0.007, a pole the survey's
lot-side camera reads at 0.90). Neither is chased here, and the tool cannot
yet tell the two readings apart: a light whose own hardware shadows it
reads near zero from every side, and a light whose pool the camera sees
THROUGH a wall reads near zero only when the shadow map starts stopping the
wall, which is the shadow doing its job. A camera placed in the light's own
room would separate them; the survey's lot-side camera is that for poles.
Lowest of the rest: a fluorescent at 0.53, a wall pack at 0.77, the two west
spills at 0.88-0.89, a sign at 0.91.

## Price (`hang_before.json`, `hang_after.json`, `hang_before2.json`, beside this file)

The fixed-station harness on fresh raw packages, idle machine, one
session; `before` is the old export reconstructed from its walk copy (the
nine underscore files removed, the main scene restored; the two then
differ in nothing but the Lux scripts, the applied Lux scene and the
manifests); `before2` the same package again as the control.
`patches/lux_streetlight_hang/perf_table.py` prints this from the three.

| package | mean median ms | mean p95 ms | mean GPU ms | mean draws | lights |
|---|---|---|---|---|---|
| before | 4.73 | 5.27 | 2.17 | 1079.7 | 94 |
| after | 4.60 | 5.07 | 2.14 | 1079.8 | 94 |
| before again | 4.64 | 5.10 | 2.14 | 1079.7 | 94 |

    median ms, after minus before:   mean -0.13, max |1.33|
    GPU ms,    after minus before:   mean -0.02, max |0.56|
    draws,     after minus before:   mean +0.02, max |1.00|
    control, before2 minus before:   median -0.09, GPU -0.03

Inside the control. Which is the expected shape: the twelve shadow maps
were being rendered before, for lights that then drew nothing; the same
twelve render now, for lights that draw. The cost of a shadowed pole was
already being paid; this buys the light it was for.

A first attempt at the control ran the harness on the walk copy itself
and the station probe never finished (CANNOT MEASURE after the watchdog,
twice, ten minutes each); the harness measures a raw export. Recorded in
`docs/COMMANDS.md`.

## Open

- The shadow policy's tie-break sorts paths as strings, so which 12 of 17
  poles carry a shadow is an accident of their ids. A natural sort, or
  distance from the site's centre, would make the shadowed set deliberate.
- (Not open, recorded so the next reader does not chase it: the art leg's
  `run --art --gameplay` returned exit 1 with "blockers open: 0, total
  findings: 51". That is `EXIT_FINDINGS` in `cmd_run` -- findings, none
  blocking -- and the export went through.)
