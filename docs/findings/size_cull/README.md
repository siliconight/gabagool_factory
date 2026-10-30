# What a size-derived draw distance would drop

**Question (2026-10-30).** The walker: 60 FPS is the floor, and the level is not the whole frame -- guns, AI, sound,
running and networking need their share -- "so smart LOD, culling techniques now will go a long way". Nothing in a
package had a draw distance: every mesh reported `visibility_range_end = 0` (`zoo_worldskin.gd`'s note on roadmap
168), so a part's cost did not change with how far away it stood. Before writing one: at the price harness's own
views, how much of what is in view is too small to see?

**Instrument.** `size_cull_probe.gd`, headless, run on an imported walk copy:

    godot --headless --path <walk copy> --script res://size_cull_probe.gd -- --stations <perf report> --out <json>

It takes the stations and yaws from a `perf_stations.gd` report and points a camera as the harness does (eye 1.6 m
above the anchor, pitch 0, 75 degree vertical FOV, far 500; read from `perf_stations.gd` the same day). At each
heading it lists every visible mesh and MultiMesh instance whose world bounding sphere is in the frustum, and the
height in pixels that sphere projects to on a 1080-line screen. Frustum only: no occlusion, no shadow passes. Its
instance counts are a superset of what the renderer submits and its surface counts stand in for draws; they are not
a draw count.

**Measured** on slice 18's walk copy (`workspaces/slice-18-ws`, Level Factory 0.271.0) at slice 18's 53 headings
(`size_cull.s18.json`; the harness's report `docs/findings/slice_look/perf_s18_subject.json`):

| Heading | In frustum (inst / surf) | Harness draws | Surfaces under 2 / 3 / 4 px |
|---|---|---|---|
| longest_sightline yaw 90 | 3,000 / 3,024 | 2,443 | 342 / 502 / 720 |
| highest_vantage yaw 90 | 3,131 / 3,155 | -- | 381 / 563 / 789 |
| extraction_11 yaw 90 | 2,892 / 2,916 | -- | 312 / 469 / 643 |
| defender_spawn_20 yaw 270 | 2,601 / 2,625 | -- | 365 / 479 / 631 |
| camera_socket_0 yaw 270 | 2,395 / 2,419 | -- | 306 / 427 / 506 |
| a close view (camera_socket_0 yaw 0) | 147 / 147 | -- | 0 / 0 / 0 |

Nearly every instance is one surface (the merges already done). Under 3 px is about a sixth of what is in the
frustum at the long views and nothing at the close ones -- the shape wanted: the views over the draw budget shed,
the views a fight happens in do not change. The named parts under 3 px are small PARTS of props kept as their own
meshes: across every heading's top twelve, a parking meter's window 802 and body 109, cars' stickers 73, utility
poles' and wall packs' lenses 76 and 39 (lit, and so kept to every distance by what was built below), wall packs'
housings 23, newspaper boxes' windows 21; and merged Empty and building meshes (`MergedN_*`,
`MergedR_*`, made at export, not import). The top twelve account for about a fifth of a heading's under-3 px
surfaces; the rest is a long tail.

**What was built from it** (Level Factory 0.272.0, in a clone; slice 19 prices it against slice 18b): each part of
an object's GLB gets the distance at which its own bounding sphere spans 3 px -- about 235 x its radius -- so a
meter's window goes at about 35 m and its body at about 140 m. A part that lights keeps every distance. The merged
meshes made at export are not covered and are the next step if the price shows the import half working.

**Priced** (slice 19 against slice 18b, `docs/findings/slice_look/perf_s19_*`; the two builds differ in nothing but
this pass; a quiet price, the controls 0.93 ms apart): **no heading gains a draw; the long views lose 36-100**, the
close views nothing; 37,686 -> 37,041 draws over the 53 headings. The worst view, longest_sightline yaw 90, 2,443 ->
2,343 draws and p95 11.31 -> 10.92 ms -- under the 11 ms in-house line for the first time on the slice; extraction_11
yaw 90 2,380 -> 2,298. The import gave 1,386 parts of 302 object GLBs a range and kept 191 lit parts at any distance
(the package's import log). Frames against slice 18b under the inspection light: no visible change but the trees'
leaves, which move between any two shots.

**Prediction against result.** The table above predicted up to 502 surfaces under 3 px at the worst view; the price
saved 100 there. The difference is not attributed piece by piece, and three things are known to sit in it: what
occlusion was already removing (the probe is frustum-only), the merged building and Empty meshes made at export (not
covered by an import pass), and the lit parts kept on purpose.

**Not established.** Which of the under-3 px surfaces the renderer was already culling by occlusion: the probe cannot
see it, which is why the price, not this table, decides what the change saved. **Next:** the same rule on the meshes
`merge_buildings.gd` and `merge_empties.gd` make at export -- `MergedN_*` and `MergedR_*` were the probe's second and
third largest names -- priced the same way.
