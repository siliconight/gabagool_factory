## [0.191.0] - The light bake's editor is given the scene groups it would read first

**Why.** Factory roadmap 239, the cold-run speed loop. The light bake's
editor is the longest part of the export -- 88.1 s of cold run 9256's 204 s
-- and its plugin waits for the editor's file system to stop scanning before
it asks for the bake scene: it asked at 32.4 s, timed step by step with the
plugin swapped for a copy that prints the engine's clock at each step (the
factory's docs/findings/grader_speed/bake_phases_probe.py). Run again with
`--verbose`, the editor spent that wait loading each of the package's 482
models and their textures, its file system scanning all the while. A Godot
4.7 editor whose project's `.godot` holds no `scene_groups_cache.cfg` starts
by reading every scene's groups, and the export's headless imports never
write one. Put in the work copy, a cache an editor had written for the same
scenes stopped the scan by the first sample, took the ask from 32.4 s to
13.1 s and the editor from 88.0 s to 68.0 s; the scene's opening and the
bake took the same time.

**What changed.** `write_scene_groups_cache` writes that cache into the
package's `.godot` after the bake's import pass and before its work copy is
made: the groups of each scene that has any, read off the scenes' own
`[node ...]` headers (`scene_groups`). On cold run 9256's 22 scenes that is
the editor's own cache: the same three scenes, with the same groups. The
package still ships no `.godot` -- `occluders.keep_cache` moves it, the
cache with it, beside the package for the walk copy. `light_bake.json`
counts the scenes listed (`scene_groups_cached`).

**Measured:** cold run 9256's workspace re-exported four times, twice on 0.191.0 and twice with its write made a no-op as the control, in the order change, control, control, change (the factory's docs/findings/grader_speed/bake_phases_probe.py; bake_phases_probe.0191.out.txt and .0191b.out.txt): the editor asked for the scene at 13.6 and 13.1 s against 32.5 and 33.8 s, its file system not scanning at any sample where the control's scanned for its first 20 s; the editor 69.3 and 67.5 s against 87.6 and 92.6 s; the export 184.1 and 183.2 s against 202.5 and 212.5 s (the second control's first 25 s shared the disk with a stray `du`); the scene's opening 14.5 to 14.8 s, the bake 35.1 to 38.8 s and its two imports 5.1 and 4.2 to 4.5 s in every arm; light_bake.json the same in every count (3,320 users, 494 models baked, 215 room fills), the cache 3 scenes and 548 bytes, and the cache kept beside the package carrying the same bytes. Every package differs from 9256's own in the same 21 files the control's does, the files any two exports differ in; and the lightmap, read texel by texel (the factory's lightmap_compare.py, Godot reading each EXR), is closer to the control's than two exports of 0.190.0 are to each other: 93.44 % of texels bit for bit the same, the mean difference 0.000002 and the largest 0.0103, where the control against 9256's own differs by 0.000030 on average and up to 1.127

**Tests:** `tests/unit/test_scene_groups_cache.py`, six: the cache written
for the editor's own scenes is its file byte for byte (548 bytes, copied
from a bake's work copy); groups spread over many nodes are listed once each;
a scene with no group, and a scene under `.godot`, are left out; groups are
read off node headers only, in both of Godot's spellings; a package with no
group gets an empty cache; the bake writes it after its import and before its
work copy. All six fail on 0.190.0. 2,314 passed, 16 skipped, 0 failed (JUnit, 2,330 tests; the seventh new one is test_sibling_locator's check of the new file)
