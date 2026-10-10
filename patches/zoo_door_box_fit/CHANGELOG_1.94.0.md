## [1.94.0] - a door box wears its business's band as the pack asks, at the art's own shape

### What changed
Roadmap 223. Pixelcoat 0.62.0 letters a business's sign smooth, in Blue
Highway Condensed, the face this repo paints a name in over a door (1.90.0).
It draws the sign at the 6:1 of the street band Lot hangs it on, and the pack
asks to be sampled `linear`, with mips. Since 1.79.0 the door box has worn
the same pack, so one building's two signs carry one name. Two things here
undid that:
- **`skins.load_pack` dropped the pack's sampling hint,** and
  `make_emissive_textured_material` set every sign `Closest`, which steps
  each anti-aliased edge into stairs.
- **The face mapped the art 0..1 across itself.** Across the library's 95
  door signs, a face is 0.6 m tall and 3.33 to 8.33 times as wide, 4.67 at
  the median. A 6:1 band's letters would stand 28% too tall on the median
  door, and a 0.61.0 pack's 4:1 had stood 17% too wide.

### Now
- **`load_pack` returns the pack's `interpolation`** (`nearest` when it
  does not say) **and `art_aspect`,** the albedo's width over its height.
  `png_aspect` reads that from the PNG's header without decoding it.
- **The sign material samples as the pack asks:** `Linear` for a smooth
  pack, `Closest` for pixel lettering. Exported, a smooth face leaves with a
  LINEAR sampler, and Level Factory pins a texture every sampler filters to
  compressed with mips (`FILTERED_TEX_PINS`).
- **`skins.fit_uv` keeps the art's shape.**
  - A face of the art's shape, within 2%, takes it whole, as before.
  - A taller face shows the art across its width, centred.
  - A wider one shows it at full height, centred.
  - Past the art, the UV leaves 0..1 and the sign's `EXTEND` repeats the
    art's edge.
  - **What that costs:** on the median door, the art is 78% of the face's
    height, with 11% above and below. Where the pack has a border, those
    bands are the border's colour, so the frame reads thicker at top and
    bottom. A stretched name was the alternative.
- **The painted names (no pack)** are unchanged: they are drawn at the
  face's own shape (1.90.0).

### Tests
- **`tests/test_door_box_fits_its_art.py`:**
  - a PNG's shape, read from its header;
  - the pack says how to sample it and its shape, and a pack that does not
    say is sampled as pixels;
  - a face of the art's shape takes it whole;
  - the median door shows a 6:1 band's art at its own shape, and the widest
    door, 8.33:1, centres it across;
  - the material samples as the pack asks;
  - **built, inside Blender,** the door box's face texture leaves the GLB
    with a LINEAR sampler.
- **On 1.93.0 all eight fail, each on what it names:**
  - `fit_uv` or `png_aspect` missing, four;
  - no `interpolation`, two;
  - the material's line, one;
  - the GLB's sampler `9728`, NEAREST, one.
  The fixture writes its PNG with `zlib` and `struct`, because Blender's
  Python carries no PIL. On this release, inside Blender 5.1.1: 8 passed.

Suite: 4,101 passed, 422 skipped, 1 xfailed (1.93.0: 4,094, 421 and 1): the
7 new pure tests, and the Blender one skipped. Inside Blender 5.1.1 the new
file and `test_door_wears_the_band.py` run 11 passed.
