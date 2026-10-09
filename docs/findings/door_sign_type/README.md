# The sign over a door: Pixel Operator against Blue Highway (Zoo 1.90.0, roadmap 219 note 10)

**Question.** The walker, walking club_block_014 on 2026-10-09 (cold run
9213): "need better looking fonts on these signs", then "use Blue Highway for
the shop signs". Two things needed measuring before and after the change:
- which tool lettered the sign they photographed;
- how big every name the library can show sets, on every sign width the
  library derives, in each version.

**Frame and units.**
- Letter sizes are CAP HEIGHTS in centimetres on the sign, from painted
  pixels over the version's pixels a metre: 80 for 1.89.0, 240 for 1.90.0.
- Pixel sizes are the tile's, before the atlas gutter.

## Whose sign

In cold run 9213's package, strip_club_a01's door box wears
`M_SignBox_Face_SignBox_Face_256x52_25d84c02_Face`.
- **That is `_card_atlas.build_art`'s material,** so the art is
  `storefront_names.paint`'s.
- **Its texture is `_tex/SignBox_Face_256x52_25d84c02_ed251bfd.png`,** 721
  bytes, sampler `magFilter` 9728 (Closest), imported lossless
  (`compress/mode=0`).
- **No Pixelcoat sign pack is anywhere in that package.** Its three lettered
  door signs are all Zoo's.

*First attributed to Pixelcoat's `core/signage.py`,* in roadmap 219's table
and the memory note of the walk. That module letters the street band, and a
door box that wears it (Level Factory 0.148.0). Neither is in this level.

## The instruments

**`sign_table.py <zoo_root> <out.json>`** asks one version's own `layout` for
every name on every width:
- the names are 64: every kind's, every club's, and the widest street
  number;
- the widths are the 12 Deli Counter derives, read off
  `deli_counter/build/*.lights.json` on 2026-10-09. That is 95 signs across
  131 manifests, all 0.6 m tall.

It also builds the atlas a 2.8 m sign makes, and prints:
- the version and the cell count;
- the cells that did not set;
- the atlas's size and its PNG's bytes.

**`sign_sheet.py <zoo_189_root> <zoo_190_root> <out.png>`** paints seven signs
through each version's own `paint`, each in a child process, since both are
the package `zoo_keeper`. It shows 1.89.0 nearest-magnified, as it was
sampled, above 1.90.0 smooth-scaled, as it will be. Each is 1120 px wide.

**Which job wrote which file.**
- **`table_189.json`** is the repo at 2a63e06 (Zoo 1.89.0), before the patch.
- **`table_190.json`** is the repo after `patch_zoo_sign_smooth.py`. A
  patched copy (`ZOO_ROOT=<copy> ... --draft`) gave a byte-identical file.
- **`sign_sheet.png`** is the 1.89.0 repo beside that copy.

To reproduce the 1.89.0 side now, export 2a63e06 into a scratch folder
(`git -C zoo archive 2a63e06 | tar -x -C <dir>`) and pass that folder.

## Results

`sign_table.py` printed:

    version 1.89.0 cells 768 unset 0 atlas (256, 52) png 735
    version 1.90.0 cells 768 unset 0 atlas (704, 216) png 23285

| width (m) | 1.89.0 cap, cm (min / median / max) | 1.90.0 cap, cm | names on two lines |
|---|---|---|---|
| 2.0 | 8.8 / 17.5 / 35.0 | 16.7 / 23.1 / 37.9 | 45 -> 7 |
| 2.05 | 8.8 / 17.5 / 35.0 | 16.7 / 23.5 / 38.3 | 42 -> 5 |
| 2.2 | 17.5 / 17.5 / 35.0 | 16.7 / 25.6 / 39.6 | 36 -> 4 |
| 2.3 | 17.5 / 17.5 / 35.0 | 16.7 / 26.9 / 39.6 | 36 -> 3 |
| 2.4 | 17.5 / 17.5 / 35.0 | 16.7 / 28.1 / 39.6 | 30 -> 2 |
| 2.6 | 17.5 / 17.5 / 35.0 | 17.5 / 30.6 / 39.6 | 26 -> 0 |
| 2.8 | 17.5 / 17.5 / 35.0 | 18.8 / 33.1 / 39.6 | 18 -> 0 |
| 3.0 | 17.5 / 17.5 / 35.0 | 20.4 / 35.6 / 39.6 | 15 -> 0 |
| 3.2 | 17.5 / 17.5 / 35.0 | 21.7 / 37.1 / 39.6 | 10 -> 0 |
| 3.4 | 17.5 / 17.5 / 35.0 | 22.9 / 37.3 / 39.6 | 6 -> 0 |
| 4.8 | 17.5 / 35.0 / 35.0 | 32.9 / 37.9 / 39.6 | 0 -> 0 |
| 5.0 | 17.5 / 35.0 / 35.0 | 34.6 / 37.9 / 39.6 | 0 -> 0 |

**Letter height, 1.90.0 over 1.89.0, per cell:** 0.85 at the least, 1.44 at
the median, 2.19 at the most.

**35 of the 768 cells are smaller.**
- **Long names on 2.0 to 2.4 m signs:**
  - the two funeral homes;
  - five of the clubs' names;
  - the country club, the brewery and the supermarket.
- **Short civic names in Aileron Bold:** MUSEUM, STADIUM, COURT HOUSE,
  TERMINAL A.

The worst is MUSEUM on a 2.0 m sign, 35.0 to 29.6 cm.

**The faces:** `highway_cond` in 684 cells, `aileron_bold` in 84, the civic
names.

### The look, and one correction made by looking at it

The first sheet fitted the name to the box and let the outline spill 3 px
past it. Short height-bound names then stood within about 3 cm of the rules:
POLICE at 40.0 cm, the street number likewise.

The mock-up the walker saw counted its stroke inside the box. 1.90.0 does
too, and POLICE is 37.9 cm. The width-bound names are mostly unchanged by it:
the cap is a whole pixel, and the 2.8 m sign's 58 px survives a box 6 px
narrower. The atlas's PNG is byte for byte the same size, and that is why.

## What this does not show

- **The street, at night, from the distances a player stands at.** The
  sheet magnifies tiles; the game minifies them through a mip chain.
- **The imported texture sizes and frame time,** owed by the proof run.
  1.90.0's CHANGELOG estimates the memory from the formats.
