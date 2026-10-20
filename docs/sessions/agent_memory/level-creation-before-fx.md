---
name: level-creation-before-fx
description: "walker 2026-10-11: prioritize level creation before FX; the factory owns FX emitters/hooks only (roadmap 235), effects are Calibria's (236), no scope creep"
metadata:
  node_type: memory
  type: feedback
  originSessionId: 27f14f8b-7ce5-44c0-a704-178a824035d7
  modified: 2026-10-11T13:18:02.075Z
---

The walker, 2026-10-11, after a run of FX questions (a building on fire, Calibria, flipbook fire, the Doom fire): "i dont want to scope creep, but ensure this factory has the fx emitters and hooks to allow for this type of stuff", then "i want to prioritize the level creation before fx though to be clear".

**Why:** the deliverable is levels made by the pipeline; effects are a consumer of levels, owned by the game-side Calibria (`gabagool_studio_tools/calibria`), and building them now would pull the factory off its metric.

**How to apply:** queue level-creation work (roof props 181, certification, level quality) ahead of FX. The factory's FX scope is roadmap 235 only -- `FxEmit_<kind>` markers in the art layer, their payload, a node group, the state binding, a Lux light hook, a gate, the shot bot's animated mask -- and it is BACKLOG behind level creation. The fire techniques (roadmap 236) are Calibria's, outside the factory. See [[floaters-zoo-core-concept]] for the other 2026-10-11 concept.
