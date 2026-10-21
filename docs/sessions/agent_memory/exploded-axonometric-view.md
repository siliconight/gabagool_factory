---
name: exploded-axonometric-view
description: "Roadmap 293: DC axonometric.py draws every building exploded with cutaways (0.254.0); offsets are the drawing's alone; stairs as treads next (0.255.0)"
metadata:
  type: project
---

The walker, 2026-10-21, filing `docs/reference/Floor_Plan_to_3D_Layout_and_Automap_Guide.md`: "make our floorplan
tool better and acheive that Exploded axonometric view, with architectural cutaways". Deli Counter 0.254.0's
`axonometric.py` draws it for every building from the spec, beside the plans (`validate.py` -> `build/floorplans/
<name>.axo.svg`, gitignored; the commit gate draws all of them). The walker then asked "draw the stairs as treads
next" (DC 0.255.0, from `stairwell.ascent_surfaces`).

**Why:** the plan drew one storey at a time; nothing showed how storeys stack (stairs, atriums, rooms over rooms).

**How to apply:**
- The display offset is the DRAWING's alone: never let it touch elevations, collision or navigation (each storey
  group carries `data-elevation` beside `data-offset`; a test pins it).
- One layout: walls come from `floorplan.storey_walls` / `wall_split`, stairs from `stairwell` -- never re-derive
  geometry in the drawing. Treads read `ascent_surfaces` (the headroom gate's copy of the builder).
- To look at one: `patches/dc_axonometric/svg_png.py <svg> <png> [scale]` (headless Edge, local file only); crop a
  detail with a viewBox (scratch `crop_svg.py`). Pass Windows paths to Python.
- LEFT on 293: ramps, platforms, fire escapes in either drawing; where a reviewer finds it beside a level (walker's
  call). Related: [[open-work-2026-10-09]], [[floor-holes-get-a-cause]].
