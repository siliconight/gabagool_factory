# Cold run 9256 -- compressed everywhere

**What it tested:** Level Factory 0.190.0, the walker's call of 2026-10-12:
every texture the level draws in 3D -- the shared textures, the site skins,
the signs -- pinned as an editor leaves it (VRAM compressed, a mip chain, the
3D detection off; the normal maps red-green compressed with the roughness
limiter Godot gives them), where the lossless pins held only in a headless
import. Everything else as in 9255; restaurant_row_001 on 9245's lot and
seeds.

**Result: 0 interventions, 0 tool files changed.** seed_9104 picked on the
same route completions (0.96, 1.00, 0.48); findings 122 -> 122. The export's
own lines are 9255's -- 1,370 occluders, the Empties merged to 148 meshes,
the greybox census 3 surfaces, the bake's 3,320 users -- and its pins line
now counts the skins: 415 of 415 shared, and no shared, sign or skin sidecar
re-pinned. The light bake's editor logged no texture detected as used in 3D
(9255's logged 426, 22 normal maps and 22 roughness maps) and opened the
scene in 14.8 s (20.3 s in 9255's). The walk copy loads the same level as
before (`walk_copy_census.gd`: 20,954 nodes, 3,380 meshes, none empty, 242
lights, 3,320 lightmap users).

## The time

    run    shell   art     export   walk   retire   the drive
    9255   76 s    156 s   217 s    10 s    4 s     7.8 min (470 s)
    9256   74 s    153 s   204 s    11 s    3 s     7.5 min (452 s)

From each run's step stamps; the drive from the journal's start to the
driver log's last write. The export is 13 s shorter, of which the bake's
editor is 8 s (88.1 s against 96.1 s in the editor).

## What is evidence of what

- The textures: the bake editor's own log beside the package
  (`<package>.lightbake.log`), and `editor_texture_probe.py` on 9255's
  workspace for the key-by-key comparison (`editor_texture_probe.0190.out.txt`).
- The time: the step stamps in `driver.log`; `light_bake.json`'s `editor_s`.
- The result: `cold_run.py --end` and the drive's findings step.

## After the run

The bake's editor, the export's longest part, was timed step by step on
this workspace (`docs/findings/grader_speed/bake_phases_probe.py`; the
README's section on the editor's twenty seconds): its plugin waited 27.5 s
before it could ask for the bake scene, the editor loading every model to
read the scenes' groups, because the export leaves it no
`scene_groups_cache.cfg`. Level Factory 0.191.0 writes one. Re-exported
here four times, change and control alternated, the editor took 69.3 and
67.5 s against 87.6 and 92.6 s, and the lightmap stayed nearer the
control's than two exports are to each other. The same instrument found
that this run's release moved the baked light: 9256's lightmap against
9255's differs by 2 % of its mean on average, four times what two exports
differ by (`docs/findings/grader_speed/lightmap_compare.controls.out.txt`
and `lightmap_compare.0191.out.txt`). 0.190.0 changed nothing but
the textures' import settings.
