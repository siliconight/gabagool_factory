---
name: props-must-contrast-with-floor-and-walls
description: "A prop a body can walk into must look visibly different from the floor and wall behind it, so its collision reads from a distance."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 4bb794c9-c366-4613-95bd-3c61e9a0d0f9
  modified: 2026-09-13T21:23:27.416Z
---

The walker, 2026-09-13, walking cold run 9048: chairs and tables wearing the
same texture as the floor and walls were nearly invisible, "which then makes
their collision hard to visually read as a human, making it easy to stumble
into things. The collision is correct, but it should look like a 3d object that
looks different from the ground and wall so I can see them from a distance."

**Why:** readability of collision is gameplay, not decoration. A solid that
blends into its surroundings is a trip hazard even when its collider is right.

**How to apply:** when any tool places a prop (Deli Counter `furnish` and cover
seeding, Lot street furniture, Zoo species defaults), give it a material that
contrasts with the building's floor and wall skins; never let a prop fall back
to the building's `default_material`. Treat contrast as measurable (luminance or
hue difference between the prop skin and adjacent surfaces). Related:
[[walker-taste-overrides-art-budget]], [[walker-wants-retro-style-with-real-structure]].
