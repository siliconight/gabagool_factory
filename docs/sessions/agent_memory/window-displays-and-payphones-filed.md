---
name: window-displays-and-payphones-filed
description: "Walker 2026-10-08: shop window displays (music store first, roadmap 209, NOT started) and 90s payphones (roadmap 210: redrawn Zoo 1.88.0, lit Zoo 1.89.0 + Lux 0.70.0, indoor wall units DC 0.204.0; Lot themes open)"
metadata:
  node_type: memory
  type: project
  originSessionId: 27f14f8b-7ce5-44c0-a704-178a824035d7
  modified: 2026-10-09T17:26:15.725Z
---

Two design asks from the walker on 2026-10-08, each with photographs:

1. **Window displays, a music store first (roadmap 209). NOT started.** "For
   later, I want to add to the roadmap the ability to create certain
   buildings with a Window Display on the front, we can start with a
   Guitar/Music Store." Six photos: a riser of guitars on stands, guitars
   hung by the headstock behind, amps stacked, neon words hung in the
   glass, neon outline tube around the window, spots over the display, a
   two-storey store with a sign band. Comps:
   `docs/reference/MUSIC_STORE_WINDOW_COMPS.md`.
2. **Payphones (roadmap 210).** "for city/urban levels ... In the 90s you
   would pay with quarters, and the phone is not wireless, it's on a metal
   cord." Comps: `docs/reference/PAYPHONE_COMPS.md`.
   - **Redrawn: Zoo 1.88.0** (cold 9212). The walker had said the old one
     "doesn't have a phone or appropriate decals".
     - What it is: an instrument, a swept cord, and forms
       booth/pedestal/wall with `auto` = booth.
     - The company: YOUSETEL, invented.
     - The record: `docs/findings/payphone_redraw/`.
   - **Lit: Zoo 1.89.0 + Lux 0.70.0** (cold 9213, 0 interventions). The
     walker: "yes light it".
     - A backlit header and diffuser, `_Face`, one more draw a payphone.
     - The `LuxEmit_payphone_hood` marker carries `lux_drop`; Lux's
       `payphone_hood` row is `REFERENCE_POOL` x 0.75, set from frames of a
       live probe.
     - The record: `docs/findings/payphone_light/`.
   - **Indoors a wall unit: Deli Counter 0.204.0.** The walker: "do the
     indoor wall form".
     - The piece asks `form="wall"`; 39 payphones in 38 specs were
       refurnished and rebuilt.
     - The two AUTHORED payphones (`primos_pizza`, `strip_retail_a01`) stay
       booths.
   - **Still open:**
     - Lot's placement (wall units by store doors, pedestals at corners),
       waiting on the walker's call on which themes are city/urban;
     - the walker's eye on the lit booth. Frames were sent 2026-10-09.

**Why:** both are "the place reads as 1990s Delco" detail. The walker sends
comps and expects them built later, not now.

**How to apply:**
- Start from the roadmap item.
- Every mark in the photos is real: invent Delco names
  ([[fake-delco-brands-funny-and-crass]]).
- Which themes count as "city/urban" is the walker's call.
- Guitars in many colours are one mesh with vertex colour
  ([[performance-beats-graphics]]).
- **To light any Zoo prop, Lot needs no change.** The recipe returns a
  `LuxEmit_<type>` attachment plus `marker_props` (glTF extras: `lux_type`,
  `lux_drop`), and Lux adds a row. Ship both together: a marker with no row
  is skipped at spawn.
