# Cold run 9114 -- a 1990s cooler on every store's sales floor

The walker, 2026-09-29: "fridges of cold sodas, beer, milk, etc, with glowing
lights too", then "bottled water wasn't really a thing in the 1990s in USA ...
prioritize soda, gatorade (sports drink), milk, beer"; and "2x" for the
counter, "fix the sign". Lux 0.60.0, Zoo 1.29.0, Deli Counter 0.161.0 and
0.162.0. Zero interventions; the art leg read before export: 0 blockers, 64
findings, identical to 9113 code by code but PRESENTATION_TINT_MATERIALS (+3
material entries, +1 name, +1 GLB: the new cooler module). Same lot as 9113
(replayed before --begin).

The run's exit status was 1 on both legs. Read, not assumed: it is
`EXIT_FINDINGS` -- findings present and no job blocked
(level_factory/apps/cli/commands, the end of `cmd_run`); a blocked job prints
"blocked at" and returns EXIT_BLOCKED or EXIT_TOOL.

## What the frames show (full scale; `store_9113_vs_9114.png`, 9113 left)

Rows: the cooler wall from 5 m (the camera stands half behind a shelf end),
from inside the entrance, the counter down the aisle, the window sign at 4 m.

- gas_station_a02's sales floor has its 8 m cooler on the back wall: COLD
  SODA, SPORTS DRINKS, DAIRY, COLD BEER, ICE COLD DRINKS over lit doors,
  visible down the aisles from the entrance and through the storefront glass.
- The window sign clears the lit sign box and reads through the glass; the
  box is centred on its door (Deli Counter 0.162.0).
- The counter carries its warm pool at 2x.

    frame mean, 9113 -> 9114
    cooler wall 5 m      44.4 -> 46.0
    from the entrance    31.7 -> 32.1
    counter              37.8 -> 38.0
    window sign 4 m      21.1 -> 21.6
    storefront 8 m       24.8 -> 24.9
    street 30 m          10.5 -> 10.4

## Cost

Fresh package copies, `perf_stations_run.py` twice each, alternating:

    draws, heading by heading    60,733 -> 60,732 over 53 headings; 46
                                 identical, largest +5
    worst sightline              2,620 both
    positional lights            112 both
    meshes over 8 lights         43 both

The cooler costs what the shelf run it displaced cost: the glow is emission,
three submissions a run, no light.
