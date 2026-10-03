## [0.130.0] - the wind: a street tree's crown sways

Step 3a of the wind design at the factory root
(`docs/proposals/WIND_DESIGN.md`). The walker, 2026-10-03: "start with the
crowns". Zoo 1.56.0 writes every corner of a crown with a sway weight (its
height over the crown's, squared) and a phase of its own leaf cluster in a
second UV set; this import moves it. The wood and the grate stay still,
which is what a tree does.

### Added
- **`_sway_crowns` in `zoo_worldskin.gd`, for every GLB.** The
  `StreetTree_Crown` node whose mesh carries a second UV set gets its skin
  REPLACED by a shader that reproduces exactly what Zoo's textured skins
  use -- the albedo texture at its UV1 scale with a nearest filter, the
  metallic-roughness texture by channel, the vertex colour where the
  surface is tinted, the two factors, alpha scissor where the skin is a
  cutout -- and leans the vertices with the wind: a lee lean of weight
  squared times 0.02 m per metre a second, capped at 0.4 m, under a gust
  that is a 7 s swell over a slower one, delayed by the distance downwind
  so the front walks across the lot, plus a 2 Hz flutter per cluster. The
  phase is per node from NODE_POSITION_WORLD. A skin carrying anything
  outside the shader's set (a normal map, an emission, a blend, triplanar)
  is REFUSED by name and left still; the wood has a normal map and does not
  move, so nothing in this level is refused.
- **`lf_wind`, one global shader uniform**, declared by the shipped
  project.godot from the brief's weather word
  (`godot_project.wind_for_weather`: clear 1.5, rain 4, storm 9, hurricane
  15 m/s, from the west) through `shader_globals_block`; `ExportProfile`
  carries `weather` and `cmd_export` reads it off the brief; the preview's
  project text declares the calm, and the agreement test compares the
  section.
- `tests/unit/test_worldskin_sway.py` holds the shape: the node name and
  the UV set, the one global, the lee lean and the gust front, the per-node
  phase, the support set and the refusal, replacement once with the skin's
  numbers, before the kit branch, the weather table and the preview's calm.

### Measured
On a rebuild of cold run 9139's lot with Zoo 1.56.0 (18 crowns, all wearing
the shader), walked as shipped:

    the crown at rest against the previous build, same camera, wind zero:
        15 pixels of 746,496 differ, none by more than 33 of 255
    the same camera, against the rest frame:
        the brief's breath (1.5 m/s)      431 pixels moved
        a storm (9 m/s)                 2,476 pixels moved
    frames half a second apart:
        breath 47 / 50   storm 116 / 155   wind zero 0 / 0
        (the previous build, no shader, reads 35 under the same test:
        the sky's own noise)

The replacement is invisible at rest, which was the gate. In a still a
breath moves the top of a crown a few pixels at nine metres: 3 cm over a
seven-second swell is the slow breathing the design asked for, and the
storm shows the lean plainly. The amplitudes are the design's starting
values; the walker's eye on the frames sets them.

Priced on the fixed-station harness, fresh copies, idle machine, the grill
build's package (Zoo 1.55.0, Level Factory 0.129.0) before and after as the
control, one session:

    package              mean median ms   mean p95 ms   mean draws
    grill build          4.80             5.53          1079.6
    this                 4.57             4.95          1079.6
    grill build again    4.92             6.03          1079.6

    draws: identical in all 53 views (the crown was one surface and is one)
    median ms, this minus the control's second pass:  mean -0.34, max |2.75|
    median ms, the control's first minus its second:  mean -0.11, max |3.61|

Within the instrument's spread, and faster than both control passes, which
is the machine and not the shader. The vertex stage runs on 1,891 vertices
a tree, 34,000 a frame for the eighteen.
