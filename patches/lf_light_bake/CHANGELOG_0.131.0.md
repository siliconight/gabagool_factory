## [0.131.0] - `export --bake-lights`: the steady lights baked into a lightmap

Roadmap item 31, from a probe to a pipeline step. The probe
(`docs/findings/light_bake/NOTES.md` at the factory root) baked the gas
station lot's steady lights with Godot 4.7's LightmapGI and priced it on the
fixed-station harness, quiet machine, GL Compatibility, baked and unbaked
alternated twice: -0.8 ms median frame (-16 %), -0.45 ms GPU, controls
0.04-0.10 ms, the heaviest views ~3 ms faster, no view slower by more than
0.3 ms. A static light stops adding a pass on the surfaces the lightmap
covers: draw calls fall 13 % on average.

`packages/exporting/light_bake.py`, run by the export after the occluder
bake (which leaves the import cache it needs) and before the cache is
dropped, when the profile asks (`--bake-lights`, `ExportProfile.
bake_lights`, off by default):

  * every model's sidecar set to Static Lightmaps, so Godot unwraps a second
    UV set on import -- except a model that already carries TEXCOORD_1,
    which is a moving or flickering prop whose second UV set its shader
    reads (7 on the walker's lot: two trees, two ATMs, the video poker, the
    roller grill, the slush machine); a sidecar with no light-baking line is
    reported, not guessed at;
  * every inline primitive mesh (ground, roads, walks) given `add_uv2`;
  * every Lux rig with no `failing_kind` marked `bake_mode = 1`; the failing
    fixtures stay live;
  * `bake.tscn` written (the presentation scene and one LightmapGI, quality
    Low, two bounces), the package copied to a Forward+ working copy with
    `assets/godot/light_bake_plugin.gd` enabled, and the editor run on it,
    bounded, killing its process tree on the bound. Godot 4.7 exposes no
    script call for a bake, so the plugin opens the scene, presses the
    editor's own Bake Lightmaps button, answers the save dialog, saves and
    quits;
  * `bake.tscn`, `bake.lmbake`, `bake.exr` and its sidecar copied back, the
    scene's uids stripped (the package ships paths), and `mission.tscn`
    pointed at `bake.tscn`.

Any failure -- no Godot, no presentation scene, the editor's bound, a bake
that did not complete -- restores the presentation scene and the entry,
removes the bake's files, and ships the package unbaked. `light_bake.json`
in the package says what was baked or why not.

Lux 0.66.0 binds the lightmap at load and switches it with the level's
state. Measured on the walker's lot exported with `--bake-lights` and walked
through Lux's own calls: baked at load, 2,614 draws overhead; switched to
real time, 3,302 and the never-baked picture; back, 2,615; the power cut
dark (0.119); power back, baked. The export took 214 s, 54 s of it in the
editor; the closure verdict was clean over the five new files. The unwrap
is deterministic: the lightmap UVs of 1,603 surfaces digested identically
as baked and after two fresh imports, so a recipient's import lands the
lightmap where it was baked.

`tests/unit/test_light_bake.py`, nine tests: static lightmaps on every
model but those whose second UV set is shader data; inline primitives
unwrap themselves once; steady rigs baked and failing ones live; a scene
without Lux rigs refused; no Godot bakes nothing and says so; a bake that
fails ships the package unbaked; one that works ships the lightmap and
points the entry at it; the bake scene; the profile does not bake unless
asked.

