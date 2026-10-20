---
name: trees-reference-roadmap-216
description: "Walker 2026-10-09: improve trees -- CC0 reference .blend (sculpted trunk + ~800 alpha-tested branch cards) filed; god rays as fake shafts only; roadmap 216, price an alpha-tested crown first"
metadata:
  node_type: memory
  type: project
  originSessionId: 27f14f8b-7ce5-44c0-a704-178a824035d7
  modified: 2026-10-09T13:04:36.106Z
---

The walker, 2026-10-09: "On the roadmap, improving Trees". They gave:
- **the reference** `one tree hill_gumroad.blend`, "The cc0 tree to use as a
  reference for how to make better looking trees";
- the transcript of the video it comes from;
- a god-rays note, with a photo of sun shafts through a canopy.

**Filed.**
- `docs/reference/TREE_REFERENCE.md` has the measured structure, the method
  in our words, and the god-ray constraints. It carries the sha256.
- `docs/findings/trees_reference/` holds `inspect_blend.py`, which reads a
  `.blend` with auto-exec off.
- The 75 MB binary is untracked in `_archive/reference/`. `docs/FILING.md`
  gained a row for reference assets too large to track.
- Roadmap 216 (OPEN).

**The reference vs Zoo.**
- **The reference:** a 7,030-triangle sculpted trunk, plus about 800 bent,
  alpha-tested, two-sided branch cards. About 21,000 triangles, 3 materials,
  2048 colour+alpha and normal maps.
- **Zoo today:** six species grown by `recipes/street_tree.py`, with faceted
  box leaf clusters (the retro read kept 2026-09-13). 2,220-3,564 triangles,
  4 primitives, and a Sway layer for wind. The cards mode from 0.69.2 was
  "not ready" on cold run 9032.

**Why price first:** cold run 9185 measured alpha-tested fence fabric at
+3.3 draws a view (a shadow pass) and up to +1.59 ms when it fills the view.
Blended fabric was cheaper but casts no shadow, and crown cards can't sort.

**How to apply:**
- **God rays.** Volumetric fog does not render on GL Compatibility (Lux
  measured it), and screen-space shafts are a deferred post-process. Use
  fake additive shafts in the style of Lux's `lux_light_cone.gdshader`, in
  the low-sun daylight slots only ([[levels-have-five-times-of-day]]).
- **The reference is a brief, not a part.** The deliverable is the
  generator ([[detail-lives-in-generator-logic]]).
- **The trunk** uses Zoo's skeleton under a Skin modifier, with bark as a
  baked normal map. That is trial 3 of [[modern-low-poly-standard]].
- **The crown** is a per-species baked card atlas, cards placed at the
  skeleton's tips, merged to 4 primitives a tree.
- **First species:** red_maple, unless the walker says otherwise. Whether
  the retro read goes is their call; [[realism-replaces-retro-look]] points
  that way.
