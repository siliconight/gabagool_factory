## [1.90.0] - the sign over a door in its owner's hand: Blue Highway for a shop, painted smooth

### What the walker asked for

- **2026-10-09, walking club_block_014 (cold run 9213, roadmap 219 note 10):**
  "need better looking fonts on these signs", at strip_club_a01's MOM THINKS
  I'M AT BINGO. Then: "use Blue Highway for the shop signs".
- **The mock-up** (`_scratch/2026-10-09_blue_highway/`) set three real shop
  names in Blue Highway's regular, bold and condensed weights, at three times
  the texel with smooth edges. It went to the walker recommending the
  condensed weight, "it fits the longest names on one line", as a single
  setting.

### Whose sign it was

The sign photographed is Zoo's. In 9213's package its material is
`M_SignBox_Face_SignBox_Face_256x52_25d84c02_Face`, `_card_atlas.build_art`'s.
No Pixelcoat sign pack is in that package at all. `storefront_names.paint`
set the name in `pixel_type`'s Pixel Operator (`monogram`) at a whole scale,
80 px a metre, and `sign_box` sampled it Closest: a CRT's letter on a lit
acrylic panel.

### What it is now

- **The name is `smooth_type` coverage at 240 px a metre** (`DENSITY` 3, the
  realism trial's rule, 1.46.0). It is outlined in the rule's colour by a
  disc of 3 px, the old one-texel `grow` at this density. The outline counts
  inside the box, as the mock-up's stroke did.
- **The face is the owner's,** `smooth_type.OWNERS`, the walker's font
  catalog ("Assign a typeface to an owner"):
  - **a shop's sign is the shop's own hand,** Blue Highway Condensed
    (`shop_small`), the weight the mock-up recommended. `VOICES["shop"]` is
    the one setting: `"shop"` is the bold, `"shop_copy"` the regular;
  - **a civic building's fascia is the institution's,** Aileron Bold
    (`maker`): POLICE, COURT HOUSE, MUSEUM, RAIL STATION, TERMINAL A, ARENA,
    STADIUM. This one is a call made from the catalog's rule, not asked for.
- **`voice_for(kind)`** names the voice. `sign_box` puts it on the face's
  tile and builds the art `smooth`: a bled 16 px gutter and a Linear
  sampler. A name sets on one line or on two, at the word break nearest
  even, and two only when that sets it bigger. Their baselines are
  `LINE_STEP` 1.32 caps apart, and the composed block, descenders and all,
  is what is fitted.
- **A name that does not set is listed in `unset` and left off,** never
  cropped (the 1.37.0 rule).

### What it changes

Measured on every library sign width: 95 signs across 131 manifests, all
0.6 m tall. Each version was asked through its own `layout`, for 64 names
(every kind's, every club's, and the widest street number):

| width (m) | 1.89.0 cap, cm (min / median / max) | 1.90.0 cap, cm | names on two lines |
|---|---|---|---|
| 2.0 | 8.8 / 17.5 / 35.0 | 16.7 / 23.1 / 37.9 | 45 -> 7 |
| 2.4 | 17.5 / 17.5 / 35.0 | 16.7 / 28.1 / 39.6 | 30 -> 2 |
| 2.8 | 17.5 / 17.5 / 35.0 | 18.8 / 33.1 / 39.6 | 18 -> 0 |
| 3.2 | 17.5 / 17.5 / 35.0 | 21.7 / 37.1 / 39.6 | 10 -> 0 |
| 5.0 | 17.5 / 35.0 / 35.0 | 34.6 / 37.9 / 39.6 | 0 -> 0 |

- **Every name sets** on all 768 width and name pairs, as before.
- **The sign photographed** (2.8 m) goes from two lines at 17.5 cm to one at
  24.2 cm.
- **Against 1.89.0,** the median letter is 1.44 times as tall.
- **35 of the 768 are smaller,** 0.85 at the least:
  - long names on 2.0 to 2.4 m signs, 16.7 cm where 1.89.0 crammed 17.5 cm
    pixel lines into the panel;
  - short civic names, whose Aileron Bold is wider than the pixel face (MUSEUM
    on 2.0 m: 35.0 to 29.6 cm).

### The price

- **Draws: none added.** The face is still one object and one `_Face`
  material.
- **Pixels: nine times as many.** A 2.8 m sign's atlas goes from 256 x 52 to
  704 x 216, and its PNG from 735 to 23,285 bytes.
- **Compression.** A texture every sampler filters ships VRAM-compressed
  (Level Factory 0.128.0), where 1.89.0's shipped lossless. Estimated from
  the formats, with mips: about 71 KB lossless RGBA8 against about 101 KB
  BC1, a sign. 9213's level letters 3 signs.
- **The proof run reads the imported sizes** and frame time; neither is
  measured here.
- **The suite:** `test_every_name_sets_on_every_sign_the_library_derives`
  takes 14 to 17 s where it took 8.2. The profile puts it in
  `smooth_type._weights`, which builds its resample matrices in Python
  loops. That module is every smooth painter's, so it is left alone here.

### What it does not cover

- **Pixelcoat's sign packs still letter in Pixel Operator**
  (`pixelcoat/core/signage.py`): the street band, and a door box that wears
  it (Level Factory 0.148.0). None is in club_block_014's package. A level
  that deals a band shows both faces until Pixelcoat's own change.
- **`neon_sign`'s tube lettering** is its own and unchanged.
- **The look is judged from painted tiles,** not from the street at night.
  The proof run's frames are owed.

### Tests

New:
- `test_a_sign_is_in_its_owner_s_hand`;
- `test_a_sign_is_painted_smooth_at_three_times_its_texel` (576 x 144 px, more
  than 12 colours; 1.89.0 paints 192 x 48 in 3);
- `test_a_name_too_long_for_its_sign_is_reported_not_cropped`;
- `test_a_long_name_takes_two_lines_when_that_sets_it_bigger`;
- `test_the_sign_box_builds_its_face_smooth_in_its_voice` (the recipe, read as
  source).

Changed:
- **The every-name test** paints each name in its own voice.
- **The built test** asks the face's sampler for `magFilter` 9729.

On 1.89.0 four of the five new tests fail, each for its reason:
- there is no `voice_for`;
- the face is 192 x 48 where 576 x 144 is asked;
- `layout`'s fourth argument is a pixel face (`no pixel face 'shop'`);
- the recipe calls `build_art` without `smooth=True`.

The fifth, a name too long reported and not cropped, passes there too. It
holds 1.37.0's rule, which 1.89.0 kept.

**The suites:**
- **Zoo:** 4,052 passed, 398 skipped, 1 xfailed in 353 s (`python -m pytest
  -q`). 1.89.0's figures were 4,047, 398 and 1; the difference is the five
  new pure tests.
- **Under Blender 5.1.1:** the sign's built test passed. With 1.89.0's
  `sign_box.py` in its place it fails, `assert 9728 == 9729`, so the
  sampler check can fail.
