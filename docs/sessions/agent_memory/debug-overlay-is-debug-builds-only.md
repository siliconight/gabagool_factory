---
name: debug-overlay-is-debug-builds-only
description: "The coordinates debug overlay rides in walk/debug builds only, toggles with F3, and must never be baked into player exports."
metadata: 
  node_type: memory
  type: project
  originSessionId: 4bb794c9-c366-4613-95bd-3c61e9a0d0f9
  modified: 2026-09-13T21:23:32.677Z
---

The walker, 2026-09-13: the debug overlay (Level Factory
`assets/godot/debug_overlay.gd`: position, building under crosshair, surface
and distance) "should be toggleable with F3 on and off, and this is for debug
builds only, eventually we will have exports that dont have this baked in at
all (for the players)".

**Why:** walk copies are for finding and locating defects; player exports are
content and must carry no dev instrumentation.

**How to apply:** every walk tool (`tools/walk_export.py`, `tools/walk_themed.py`)
includes the overlay; the exported package never does. Guard the overlay with
`OS.is_debug_build()` so a release export of a walk project drops it as well.
Hand the walker walk copies with the overlay on, and ask for its readout when a
screenshot needs locating. Related: [[never-edit-tool-repos-during-a-cold-run]].
