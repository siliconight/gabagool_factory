## [0.166.0] - A dealt business's sign imports as its pack asks

**Roadmap 223.** Pixelcoat 0.62.0 letters a business's sign smooth, in Blue
Highway Condensed, at its band's 6:1, and its pack asks for `linear` sampling
and a mip chain. A pixel pack asks for `nearest` and neither. Lot copies a
dealt pack's maps to `signs/` beside its scene and, since Lot 0.105.0, the
pack's manifest with them.

**What was there.** The export left every sign map at Godot's first-pass
defaults. Read off `LF_gas_block_001`'s package (`signs/sign_delco_storage_
albedo.png.import`): `compress/mode=0`, `mipmaps/generate=false`.
- **The memory:** a smooth sign would have shipped uncompressed, 6.3 MB of
  maps where 1.6 MB would do.
- **The look:** it would have shimmered across a street for want of its
  mips.

### What it is now

`_pin_sign_texture_imports` runs where `_pin_shared_texture_imports` does,
after the first import pass:
- every `signs/*.pack.json` names its maps;
- `_sign_pins` turns the pack's `import_hints` into import pins:
  - `linear` takes `FILTERED_TEX_PINS`, `compress/mode=2`, as Zoo's
    filtered textures do since 0.128.0;
  - `generate_mipmaps` takes `mipmaps/generate=true`;
- each map's sidecar takes those keys and no others. A sidecar missing a key
  is not given one, a pixel pack's maps are left exactly as they were, and a
  manifest that cannot be read pins nothing;
- the second import pass then rebuilds what changed, as it does for the
  shared textures.

The door box that wears the same pack needs nothing here. Zoo 1.94.0 exports
its face with a LINEAR sampler, and `FILTERED_TEX_PINS` already reaches a
`_tex/` texture every sampler filters.

### Tests
`tests/unit/test_sign_texture_imports.py`, on the sidecar Godot 4.7 wrote
for a sign map:
- a smooth sign's two maps go to `compress/mode=2` and
  `mipmaps/generate=true`, and nothing else in them moves;
- a pixel sign is left byte for byte;
- a second run changes nothing;
- a sidecar missing a key is not given one;
- a manifest outside `signs/`, or one that cannot be read, pins nothing;
- the export pins signs beside the shared textures.

On 0.165.0 all eight fail: `_pin_sign_texture_imports` does not exist.

Suite: 2,076 passed, 14 skipped, 1 xfailed, 0 failed (exit 0). 0.165.0's
changelog gave 2,067; the 8 tests here account for 8 of the 9, and the
ninth was not traced.
