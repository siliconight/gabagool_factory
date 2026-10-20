---
name: interiors-must-read-at-night
description: "Walker 2026-10-07: light night interiors enough to read the room; dens of sin are whole BUILDINGS kept a bit dark; the bake had lost the light (Lux 0.67.0 bulbs, 0.68.x room floor, LF 0.151.0)"
metadata:
  node_type: memory
  type: feedback
  originSessionId: 27f14f8b-7ce5-44c0-a704-178a824035d7
  modified: 2026-10-07T13:40:56.724Z
---

The walker, 2026-10-07: "i've noticed a lot of our interiors are quite dark
when the sun isn't up" ... "this can be intentional in dive bars, strip
clubs, and other 'dens of sin' but otherwise we should aim to give the humans
enough light to signify the surroundings". Later the same day: "the 'dens of
sin' BUILDINGS that we can keep a bit dark".

**Why:** a player must be able to read a room at night: its walls, its
pieces, its way through.

**How to apply:**
- **Dens of sin are whole buildings, not rooms.** A building with any tinted
  (club) room probe keeps every room unfilled, back rooms and cellar
  included (Lux 0.68.2). The first rule skipped only the tinted club floor,
  and the club's back rooms went 19.5 -> 52.3.
- **Keep pendants moodier than fluorescent rooms.** The walker said so on
  2026-09-28. Bulb-lit rooms get half the fill.
- **Measure** with `docs/findings/night_interiors/night_interior_census.py`:
  one station a room. Luminance and a look.
- **Price any light added**, by draws and frame time
  ([[performance-beats-graphics]]). Baked light that ships no node costs
  nothing per frame.

**What the bake had lost** (docs/findings/night_interiors/):
- **Bulbs:** every steady bare bulb sat inside its own glass. Fixed by Lux
  0.67.0 (`BULB_LAMP_DROP_M`).
- **The room floor:** room-probe ambient never reaches a lightmapped surface.
  Lux 0.68.0/0.68.1 lay bake-only fills; Level Factory 0.151.0 lays them,
  bakes them and frees them before the save.
- **On 9190's level:** fluorescent rooms 15.5 -> 39.0, bulb rooms 3.8 ->
  22.8 (scripted). Cold run 9193 is the end-to-end proof.

**Gotchas:**
- LightmapGI ignores unowned nodes.
- `editor_only` lights do not bake.
- Vendoring Lux into a package rewrites `res://addons/` to
  `res://runtime/`.

Related: [[levels-have-five-times-of-day]], [[strip-club-comp-lou-turks]].
