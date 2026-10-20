---
name: walker-wants-retro-style-with-real-structure
description: "The user judges props by whether they read as a deliberate retro (Mario 64) style; a half-finished \"realistic\" technique (cutout foliage cards) reads worse than a clean low-poly volume; detail should come from real structure (trunk, branches, twigs, species)"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 4bb794c9-c366-4613-95bd-3c61e9a0d0f9
  modified: 2026-09-13T03:15:16.391Z
---

On 2026-09-13 the user compared the faceted low-poly tree crown ("mario64
trees which looked nice in their own retro way") with crossed alpha-cutout
cards and called the cards "not fully baked". Their advice for the detailed
path: trees have multiple branches from the trunk, twigs off the branches,
and the species decides how that looks (Pennsylvania street trees: red
maple, pin oak, honey locust, London plane, callery pear).

**Why:** A consistent low-poly style across cars, shelters and trees reads as
designed; a single asset in a more "realistic" but unfinished technique
reads as a defect. Detail the user values is structural and species-true,
not textural.

**How to apply:** When adding realism to a Zoo species, add STRUCTURE
(branches, parts, proportions from the real thing) in the same faceted
style before adding texture tricks. Keep experimental techniques (cards,
cutouts) behind a genome param, shipped only when they read as finished.
Show a frame before calling a look done.
