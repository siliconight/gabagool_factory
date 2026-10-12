# Cold run 9257 -- the bake's editor given the scene groups

**What it tested:** Level Factory 0.191.0: the export writes the scene
groups cache the light bake's editor would otherwise build by loading every
scene before it opens one (`docs/findings/grader_speed/README.md`, "The
bake's editor: twenty seconds reading the scenes' groups"). Everything else
as in 9256; restaurant_row_001 on 9245's lot and seeds.

**Result: 0 interventions, 0 tool files changed.** seed_9104 picked on the
same route completions (0.96, 1.00, 0.48); findings 122 -> 122. The
export's own lines are 9256's but for the editor's time -- 1,370 occluders,
the Empties merged to 148 meshes, the greybox census 3 surfaces, the bake's
3,320 users, 415 of 415 shared pins and nothing re-pinned -- and the bake's
editor took 69.9 s against 88.1 s (`light_bake.json`: `scene_groups_cached`
3, one attempt). The walk copy's `.godot` carries the cache, byte for byte
what the package's scenes give (548 bytes), and the copy loads the same
level as before (`walk_copy_census.gd`: 3 scenes, 20,954 nodes, 3,380
meshes, none empty, 242 lights, 3,320 lightmap users).

## The time

    run    shell   art     export   walk   retire   the drive
    9256   74 s    153 s   204 s    11 s    3 s     7.5 min (452 s)
    9257   73 s    154 s   187 s     9 s    3 s     7.2 min (433 s)

From each run's step stamps; the drive from the journal's start to the
driver log's last write. The export is 17 s shorter; the bake's editor 18 s.

## The lightmap: packed differently, the same light

Texel by texel (`lightmap_compare.out.txt`), 9257's lightmap is far from
9256's: 38.82 % of texels the same and a mean difference of 0.0246, against
a lightmap whose mean is 0.031 and nearly the same in both (0.03104,
0.03110), where every earlier pair of runs read 0.0002 to 0.0008. Read user
by user (`lightmap_compare.py --layout`, `lightmap_layout.out.txt`; its
control, 9256 against itself, every user placed the same and nothing apart):

- **The atlas was packed differently.** Of 3,320 users, 3 changed size --
  the deli's dome glasses 001, 003 and 005, between charts of 14 x 6 and
  14 x 10 texels -- and 2,858 others moved; 459 stayed. 9254, 9255 and 9256
  were all packed alike, every user placed the same.
- **Where a user stayed,** its light differs from 9256's by 0.000224 on
  average, as 9255's did from 9254's (0.000182).
- **Where a user moved,** by 0.0032 on average, and falling either way: the
  signed mean is +0.000062 against their mean of 0.0388 (0.16 %). The users
  most apart, in this pair and in the two before it, are fluorescent
  housings and the payphones' glow, beside the brightest emitters.

So no surface is brighter or darker on average; where a chart moved, its
per-texel noise came out different. That last is read off the signed mean
and the stayed/moved split, not off the lightmapper.

The deli's fixtures are one of seven models that came out of Blender
different from 9256's -- two trash-bag props, the deli's fixtures and roof
props, a rowhome's dressing, the office's and the pharmacy's fixtures -- each
with its own `.unwrap_cache`: the open item roadmap 239 calls the Blender
builds' reproducibility. The domes' sizes swapped by name (001 and 005 grew,
003 shrank), which reads more like the order the domes are named in changing
between runs than like a shape changing; not measured.

0.191.0 is not in this: on fixed inputs -- 9256's workspace re-exported,
change against control -- the layout held and the two lightmaps were nearer
each other than two exports of 0.190.0 are
(`docs/findings/grader_speed/README.md`).

## What is evidence of what

- The time: the step stamps in `driver.log`; `light_bake.json`'s
  `editor_s`.
- The cache: `light_bake.json`'s `scene_groups_cached`; the walk copy's
  `.godot/scene_groups_cache.cfg` against `write_scene_groups_cache` run on
  the package's scenes.
- The lightmap: `lightmap_compare.out.txt` (texel by texel) and
  `lightmap_layout.out.txt` (user by user, with the two pairs of runs before
  it).
- The result: `cold_run.py --end` and the drive's findings step.
