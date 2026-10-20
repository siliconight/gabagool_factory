---
name: consumers-need-only-blender-and-godot
description: "Walker's dependency bar (2026-10-07): a factory consumer installs Blender and Godot, nothing else; Blender's bundled Python 3.13.9 can run the tools; 5 pip packages are the gap"
metadata:
  node_type: memory
  type: project
  originSessionId: 27f14f8b-7ce5-44c0-a704-178a824035d7
  modified: 2026-10-07T16:16:10.741Z
---

The walker, 2026-10-07: "My goal is for consumers of Gabagool Factory to only
need Blender, Godot and then to be able to make great looking fun to play
levels" -- called out as dependency management and organization.

**Why:** the factory ships to people who have never seen the repo (first one:
[[collaborator-handoff-around-2026-10-21]]). Every extra install is an
intervention before their first level.

**How to apply:**
- Measured 2026-10-07: Blender 5.1.1's bundled interpreter
  (`C:\blender\5.1\python\bin\python.exe`) is Python 3.13.9 with numpy 2.3.4,
  pip 25.2, pytest 9.1.1, requests. Level Factory (>= 3.11, stdlib only) runs
  its CLI on it unchanged.
- The gap is five packages Blender lacks: Pillow, pygltflib, jsonschema,
  PyYAML, cairosvg. Prefer dropping or vendoring (the last four are pure
  Python or nearly) over asking for a separate Python; installing into
  Blender's own Python with its bundled pip at setup is the fallback.
- Any new tool dependency must clear this bar: stdlib, numpy, or vendored.
- Tracked in roadmap 202 ("THE BAR" paragraph).
