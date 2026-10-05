## [1.71.0] - an Empty's stone lintels and sills

The walker's South Philly photograph (the factory root's
`docs/reference/EMPTIES_COMPS.md`, "Window comps"): "white stone lintels and
sills over and under every window". Patina (>= 0.27.0) orders a `lintel` at
every facade opening's head and a `window_sill` at every facade window's sill
line, and `dress_cover` builds them.

### Added
- **`lintel_parts`**: one block standing on the head.
  - 20 cm tall, bearing 10 cm into the brick past each jamb, 2.8 cm proud.
  - That keeps it behind the bars, whose uprights run up past the head
    3.1 cm off the wall.
- **`sill_parts`**: one block hung below the sill line, 7 cm deep and 6 cm
  proud so it reads as a ledge, 5 cm past each jamb.
  - The bars' feet and the air conditioner's brackets pass into it, as
    theirs are anchored in a real one.

Both stand 1 mm off the wall face.

- **In `plaster` (`STONE_TRIM_COVERS`).** Pixelcoat's `plaster_delco` is
  cream and matte, the nearest skin to the photograph's white stone that a
  cover already offers.
  - **Cost, to be priced:** one more material, so one more surface on each
    side of a building that has openings.
  - **The cheaper options:** the covers' own concrete (grey) or the gutters'
    painted white (semi-gloss) would merge at no draw.
