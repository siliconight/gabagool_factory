## [0.181.0] - What hangs in an Empty's window: bars, an air conditioner

The walker's window photographs (the factory root's
`docs/reference/EMPTIES_COMPS.md`, "Window comps"):

- "window air conditioners in nearly every photograph": a white or beige box
  in the lower sash, standing out of the wall, so geometry;
- bars proud of the frame on bolted straps.

Bars were painted into the pane (`lit_bars`, `dark_bars`), and nothing made
an air conditioner. Here each Empty window also gets what hangs in it, as
slot fields beside its pane (`empty_panes.fixtures`):

- **`bars: true`** on a barred pane: about a third of the street-level
  windows, as before.
- **`ac: true`** on a window drawn for a unit:
  - 30 in 100 eligible windows upstairs (the bedrooms), 10 at the street;
  - never behind flat bars (they stand 3.5 cm off the wall, a unit 30 cm
    out; the bellied grille that takes one is not built), in a boarded
    window, or in the box fan's.

The unit is drawn on its own key, so which windows glow does not move.

Patina (>= 0.26.0) orders the bars and units from these fields, and Zoo
(>= 1.69.0) builds them -- merged per side of the building with the rest of
its covers, so their cost does not grow with the number of windows. Zoo
1.69.0 also stops painting bars into the pane; the bars are the geometry now.

Per building, as the pane is: every placement of one archetype hangs the
same units.
