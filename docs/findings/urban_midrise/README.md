# Roadmap 241: mid-rise Empties, the first cut (Deli Counter 0.213.0)

The walker, 2026-10-11, chose a new urban level type. Mid-rise Empties of five to twelve storeys form
continuous street walls at the sidewalk line, the enterable buildings stand among them, and the Delco strip
levels stay as they are (`docs/reference/URBAN_MIDRISE_COMPS.md`). The build order is five steps. This is
step 1, Deli Counter's mid-rise Empty family, in its first cut.

## The family (`presets.empty_midrise`, `presets.EMPTY_MIDRISES`)

A brick block with windows in regular bays front and back. It has a lobby door at grade and a service door
behind it. Its sides are party walls, sealed by `auto_exterior`, and it carries a parapet. The block is 15 m
deep with a 3.1 m storey, and it is an Empty in every respect Deli Counter keys on `facade`: shut doors,
painted windows, only its roof slab.

    block          storeys   width   wall           height to the parapet's top   slots
    gs_midrise_a      5      15.0 m  brick_brown    16.5 m                         223
    gs_midrise_b      6      18.0 m  brick          19.8 m                         291
    gs_midrise_c      7      21.0 m  brick_orange   22.7 m                         367
    gs_midrise_d      8      16.5 m  stone_ext      26.2 m                         383
    gs_midrise_e     10      24.0 m  brick_brown    32.5 m                         557
    gs_midrise_f     12      19.5 m  brick          38.7 m                         615

The heights are the built shells' bounds, read by `midrise_frame.gd`. Each built in 2 to 3 s under
Blender 5.1.1, and every validation manifest passed.

**The bay is chosen, not read.** The comps give no dimension. `MIDRISE_BAY` is 3.2 m, one window
1.1 x 1.6 m a bay, and the bays are rounded to the width, so the spacing lands at 3.0 to 3.3 m.

**Kept out of today's streets, twice.** Level Factory hands every `gs_empty_*` in the library to any brief
that stands a terrace (`building_library.empty_rows`), so the family is named `gs_midrise_*`. As facades the
blocks are already outside the enterable draw (`building_library.non_source`). They wait for the urban
brief that asks for them (241, step 3).

**Not built:**

- the rooftop penthouse;
- the corner variant with a lit shop at grade;
- the bay-window variant.

Each needs a capability Deli Counter does not have yet: a structure on a roof, a storefront on an Empty, a
projecting bay.

## The frames (`midrise_frame.gd`, `midrise_street.png`, `midrise_high.png`)

The six blocks stand in a row as a street wall, a rowhome Empty (`gs_empty_rowhome_a`) at its end for
scale. They are greybox, before any theme. Their materials are near-white, which hid the windows, so each
piece is tinted by its node name: a window's `_pane` dark, a door's `_leaf` wood, every other exterior
piece in a colour for its block's wall kind. The frames show massing, height and the window rhythm, not the
look a level gives the blocks.

**First attempts, kept as what they taught.**

- Tinting by MATERIAL left every surface white: the greybox names (`gb_wall`, `gb_window`, `gb_ceiling`,
  `gb_threshold`) carry no wall kind.
- Tinting `gb_window` then drew floor-to-roof stripes. Each opening's `_sill` and `_lintel` wear the
  window's material too, so whole columns went dark. The node names are what tell a pane from the wall
  around it.

## What the walker is asked

- **The windows:** one 1.1 x 1.6 m window a bay, about 3 m apart. Do they read as apartments, or should they
  be larger, paired, or set in a rhythm?
- **The ground floor:** the same windows as above, and one lobby door. The comps' corners carry a lit shop;
  that is the corner variant, not built.
- **The top:** a plain parapet band, with no cornice detail.
- **The heights:** 5 to 12 storeys. The comps' far blocks stand 12 to 15.
