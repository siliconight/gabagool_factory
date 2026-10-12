## 0.119.1 - a far wire is a faint line, not a dotted one: drawn a pixel wide at least and faded by what it covers

**Factory roadmap 240, build 3, seen.** Cold run 9263's frames (`docs/cold_runs/cold_9263/wires.png`)
showed 0.119.0's wires as they should be within about 30 m and as dotted lines past it: a tube 2.4
to 4.4 cm across is under a pixel from about 15 to 30 m at the player's camera and 900 lines, and
the rasteriser keeps or drops such a line pixel by pixel -- a dash where a pixel centre falls inside
it, a gap where none does, and in motion a line that crawls. Drawing the tubes fatter would make the
near wires cables; the fix belongs where the pixel is known.

- **Each vertex carries its wire's drawn radius** as its UV's u (`vt`), so the vertex shader can
  find the wire's centre as `VERTEX - NORMAL * UV.x`.
- **`WIRE_SHADER`**, the wires' material, unshaded as before: at each vertex, half a pixel is the
  clip's w over the projection's y scale and the frame's height (w is the depth in a perspective
  view and 1 in an orthographic one, so the elevated shots hold too); a wire thinner than
  `WIRE_MIN_PX` (1) pixel is widened to it -- sqrt(2) wider than half a pixel, since a four-sided
  tube is that much narrower across a face than across its corners -- and its alpha is the share
  of the widened line the real wire covers. A far wire is a faint continuous line, as in a
  photograph; within the distance a wire covers a pixel it looks as 0.119.0's did (its alpha 1,
  though it is now drawn one side and in the transparent pass).
- **Wound outward, one side drawn.** `_tube`'s quads ran round the ring against their normals, and
  0.119.0 drew both sides (`cull_mode = 2`); with a fade, two layers would darken a far wire to
  nearly twice its coverage. The faces are now counter-clockwise about their outward normals,
  OBJ's front, and the material culls the back.

**Measured:** Spliced into a copy of cold run 9263's package (`docs/findings/pole_line/wire_pixel_splice.py`: the draft's wire files and material for the run's own cover) and shot at 9263's five wire stations, GL Compatibility: the shader compiled and drew; past about 60 m the wires 0.119.0 drew as dashes are faint continuous lines (`docs/findings/pole_line/wire_pixel.png`, the far end of `line` enlarged three times), and at all five stations the nearer wires read the same as 0.119.0's

**Tests:** three new in `tests/test_site_wires.py`: every vertex's u is the drawn radius of its
wire and a ring's four vertices give the shader one centre; every face is wound counter-clockwise
about its outward normal; the shader's contract (the radius from UV.x, the pixel from the clip's w,
the sqrt(2) clamp, the fade) and a code that a scene string can carry. The material test reads the
shader material. On 0.119.0 four of the nine fail, each on its own assertion: the material is a StandardMaterial3D, no vertex carries a radius (0 of 364 in the first cell), a face winds inward (-0.178), and there is no `WIRE_SHADER`

**Suite:** 818 passed, where 0.119.0 passed 815: the three new tests
