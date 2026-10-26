---
name: distant-vistas-variety
description: "Walker 2026-10-24: distant, non-interactive scenery -- trains, ocean with a marina, forest, malls, airports, etc.; variety that looks good AND is highly performant. Builds the never-built far band."
metadata:
  node_type: memory
  type: project
  originSessionId: 27f14f8b-7ce5-44c0-a704-178a824035d7
  modified: 2026-10-24T14:54:57.362Z
---

The walker, 2026-10-24: "Things I want in the distance that you can't interact with are trains, oceans (with
marina), forest, malls, airports, ect ect (want variety but that it looks goood) (but hihgly performant)".

**State when asked:** Lot's `site_backdrop.py` has five surroundings recipes (borough, yards, parkland, roadside,
none), all within ~100 m of the plate, MultiMesh'd per module (Level Factory step E). The FAR band (400 m+, a
panorama of our own kit baked into the sky, zero draws -- the 2026-10-04 three-band plan in
[[backdrop-guide-filed-for-later]]) was never built. Lux's skymint already ships panoramas (`*_land`, `*_ocean`).

**Why:** a backdrop identical everywhere reads as generated ([[edge-menu-walker-picked-e]]); and every frame is spent
on somebody else's machine ([[performance-beats-graphics]]).

**How to apply:**
- One vista a view, a landmark each (the PA guide's rule): far set pieces baked into the panorama (airport, mall,
  skyline, forest ridge, ocean horizon) cost nothing per frame; mid-band silhouettes MultiMesh'd per side; motion
  (a train, a plane, boat lights) as ONE mesh moved by a shader or one transform -- a constant cost, never per piece.
- The vista is chosen per level (brief or archetype), like the surroundings recipe; never one look everywhere.
- Price each piece the CLAUDE.md way: draws and frame time at fixed stations with controls; a look that costs real
  milliseconds ships cheap with its expensive version written down.
- Owners: Zoo species (silhouette kits), Lot (placement / recipe), Level Factory (MultiMesh, panorama bake), Lux
  (sky, lights at distance).

**2026-10-25, the sky too:** "random birds and commercial airplanes in the sky to add some live to the sky" -- filed as roadmap 307. Same rule: a flock is ONE mesh with the wing beat in the vertex shader, an airliner one far mesh on a slow track (contrail by day, nav and strobe lights by night); seeded per level; priced before shipping. They live in the sky above ~7 degrees, which street level does see.
