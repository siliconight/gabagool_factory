## [0.190.0] - Compressed everywhere: a package's textures import as an editor leaves them

**Why.** The walker's call of 2026-10-12. Found while timing the light
bake's editor (factory roadmap 239): its log says, texture by texture, that
it re-encodes what it finds in use -- 426 sidecars of cold run 9255's
package, the shared textures the export pinned LOSSLESS among them, the site
skins it never pinned, and the signs whose pack asked for nothing. Every
shipped sidecar kept Godot's 3D detection, and a headless import detects
nothing (its renderer draws nothing to detect with), so the pins held in the
export's own imports and in no editor: the bake's, the walk copy opened to
be walked, a recipient's. What anyone had looked at in an editor was
compressed all along. Offered lossless everywhere or VRAM everywhere, the
walker chose VRAM: "go with compressed everywhere".

**What the editor decides, read off its own sidecars** (the factory's
`docs/findings/grader_speed/editor_texture_probe.py`, the bake's work copy
kept and compared key by key with the shipped package): on every texture it
finds in use, `detect_3d/compress_to` 1 -> 0, `compress/mode` 0 -> 2 and a
mip chain; on each of the 22 normal maps -- exactly the 22 the models' glTF
names as `normalTexture` -- `compress/normal_map` 0 -> 1 and a roughness
limiter Godot 4.7 points at the map itself (`roughness/mode` 0 -> 1,
`roughness/src_normal` its own path). Nothing else, and nothing on the
runtime's and the validation overlays' own images.

**What changed.**

- `SHARED_TEX_PINS` is the editor's decision on a shared texture: VRAM
  compressed, a mip chain, the alpha border as pinned before, the detection
  off.
- `NORMAL_TEX_PINS`, with `roughness/src_normal` per file, on every shared
  texture a model's glTF names as a normal map
  (`_normal_map_shared_textures`, read off the GLBs before the sidecar step
  holds them, as 0.189.0 read the samplers).
- `SURFACE_TEX_PINS` on the site's skins (`_pin_skin_texture_imports`, new)
  and on every sign map whatever its pack asks (`_sign_pins` and its reading
  of `import_hints` replaced).
- The filtered split -- VRAM only where every sampler filtered, lossless for
  pixel art (0.128.0: `FILTERED_TEX_PINS`, `_filtered_shared_textures`,
  `GLTF_LINEAR`) -- removed: no sampler decides now.
- One write rule for every pin function (`_apply_pins`: a key a sidecar does
  not carry is not given one). The read-back after the last import pins the
  skins too, and its line counts them.

**Measured:** cold run 9255's package re-exported in its workspace on 0.190.0, the light bake's work copy kept and compared key by key with the package (the factory's docs/findings/grader_speed/editor_texture_probe.py): the bake's editor logged no texture detected as used in 3D, as a normal map or as a roughness map, where on 0.189.0 it logged 426, 22 and 22 (cold run 9255's own bake log) and changed 426 sidecars (editor_texture_probe.0189.out.txt); it left all 572 of the package's texture sidecars as they ship; it opened the scene in 14.7 s against 20.3 s; the export 200.3 s; 415 of 415 shared pins carried, and no shared, sign or skin sidecar re-pinned after the last import (editor_texture_probe.0190.out.txt)

**Tests:** `tests/unit/test_compressed_everywhere.py`, six: a shared albedo,
a normal map, a site skin and a sign -- a pixel pack's -- each pinned from
Godot's first-pass sidecar to exactly the `[params]` the bake's editor wrote
for one of its kind; a PNG outside the skins left alone; the skins pinned
where the signs are, in the sidecar step and in the read-back. All six fail
on 0.189.0. Changed with the decision:
`test_shared_texture_imports.py` (the pins' values; its 0.128.0 section on
filtered samplers replaced by the normal maps; a first-pass fixture with
every key Godot writes), `test_sign_texture_imports.py` (a pixel sign is
compressed and mipped too), `test_models_import_once.py` (the normal map
read before the models are held, where the filtered set was).
2,307 passed, 16 skipped, 0 failed (JUnit, 2,323 tests)
