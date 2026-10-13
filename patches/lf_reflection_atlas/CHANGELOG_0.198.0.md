## [0.198.0] - The reflection atlas is sized to the package's probes

**Factory roadmap 238** (the walker, 2026-10-11: "texture memory and compression, worth measuring on a
package"). Measured by part on cold run 9273's package (the factory's `docs/findings/texture_memory/`),
257 of its 314.6 MiB of texture memory was the REFLECTION ATLAS:

- **Where it came from.** Godot's project default, 64 slots of 256 x 256 x 6 faces in half-float with
  mips, is 256 MiB. It is allocated the first time any ReflectionProbe renders -- the Warmup's sweep at
  load, or a player's camera.
- **What it held.** The level's 23 probes, each an interior room's ambient from Lux, in 64 slots.
- **The rest of the package.** The level's own textures are about 30 MiB and the lightmap 21.3.

The sky, which the first census blamed, is not resident.

- **`godot_project.py` writes the atlas from the package**, as it writes the light cap.
  - `count_package_probes` counts the ReflectionProbe nodes in its scenes. On 9273's package the text's
    23 is the running tree's 23.
  - The slots are that count rounded up to a power of two (`reflection_atlas_count`: 23 -> 32). Fewer
    slots than probes is not a lever: at 4 slots for 23 probes the engine raised `rpi->atlas_index < 0`
    113,494 times and the run stalled. More than the default's 64 probes now gets more slots, where the
    default would have overflowed.
  - The face size is `REFLECTION_ATLAS_SIZE`, 64.
  - A package with no probe writes no line: it never allocates the atlas.
- **The face size, priced** (`atlas_frames.sh`, `atlas_frames.png`). Against the 256 the package shipped
  with, at its derived stations and twelve interiors, a second 256 render was the control:
  - at 64, no pixel of any frame moved more than 32 codes, and at most 2.7 % moved more than 8, in one
    drywall room;
  - texture memory, all at 64 slots: 314.6 MiB at 256, 121.8 at 128, 73.5 at 64.

  **What 128 or 256 would buy back:** a sharper reflection on a glossy surface. The interiors measured
  are concrete, drywall and brick, so this is one number to raise if a level shows otherwise.
  `reflection_atlas_mib` pins the arithmetic to the measurement: 64 x 256 is 256 MiB, and 32 x 64, this
  package's atlas now, is 8.
- **Both writers pass the count:** the export and the walk preview each ask `count_package_probes` of
  their own folder.
- `rendering_block(light_count, occluders, probes)`: `probes` has no default, as `occluders` has none.
  The nine test calls that knew two numbers now say 0.
- `tests/unit/test_reflection_atlas.py`: the count, the slots, the block, the arithmetic, the export, and
  the export and the preview agreeing. It fails to import on 0.197.0.

**Suite:** exit 0, 2,368 by the progress tally (2,353 passed, 14 skipped, 1 xfail): 0.197.0's 2,360, the new file's seven, and one more case of `test_sibling_locator.py`, which runs once a `.py` file in the repository and so once for the new file. `test_reflection_atlas.py` fails to import on 0.197.0, run against an export of it; the nine test calls that now say 0 probes pass as they did
