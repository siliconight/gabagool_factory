---
name: lived-in-touches
description: "Walker 2026-10-23 -- rooms need order first, then small lived-in deviations with a readable cause (chair left out, toilet seat up, light left on, pencils out of the cup); \"we should see that\""
metadata:
  node_type: memory
  type: feedback
  originSessionId: 27f14f8b-7ce5-44c0-a704-178a824035d7
  modified: 2026-10-23T22:44:03.440Z
---

The walker, 2026-10-23, on roadmap 300 (furniture arrangement):
- "do the full correct fix, allowing us to have nuance and flavor, but not look like random assortment"
- then: "and little hand touches to make it look like people actually live in that world...like people forget to put the toilet seat down, push their chair in, turn off the lights, put the pencils back in the cup" -- "we should see that".

**Why:** a generated room reads fake two ways. It reads as scatter when nothing has a reason to be where it is. It reads as a showroom when everything is perfect. Real rooms are ordered, then lived in.

**How to apply:**
1. ORDER FIRST. Every piece needs a visible reason: wall, row/grid, seat at its host, a pile, centred. Measured by Deli Counter's arrangement census (`arrangement.py`, WIP in `_scratch/wip_dc_seed_lines`), with loose share as the number to lower.
2. THEN A LIVED-IN LAYER: a few deviations FROM that order, each with a cause.
   - Placement, in Deli Counter: chair pulled out and turned, door ajar.
   - Object states, as Zoo variants by the gap protocol: toilet seat up, drawer open, pencils beside the cup, mug on a desk.
   - Lights left on, through Lux.
3. Deterministic per room seed, sparse, never on routes or cover lines.
4. Show the walker frames.

Related: [[rooms-not-crowded-not-barren]], [[levels-feel-static-make-them-alive]], [[authorship-guide]].
