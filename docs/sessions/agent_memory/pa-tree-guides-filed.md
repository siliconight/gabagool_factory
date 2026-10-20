---
name: pa-tree-guides-filed
description: "Walker's two tree guides filed 2026-10-10 in docs/reference (PA_NATIVE_TREES_PHILLY_DELCO.md: species profiles, regional palettes with weights, context forms; BLENDER_SCRIPTING_PA_TREES.md: skeleton/tube/socket pipeline, species C/H and W/H rows, LOD and export checklist); backdrop uses the silhouette rows and palettes, street trees (216) the pipeline"
metadata:
  node_type: memory
  type: reference
  originSessionId: 27f14f8b-7ce5-44c0-a704-178a824035d7
  modified: 2026-10-10T19:58:13.072Z
---

The walker handed over two companion guides on 2026-10-10 ("do these docs
help with making trees look more realistic?"), filed verbatim with their
cross-links renamed:
- `docs/reference/PA_NATIVE_TREES_PHILLY_DELCO.md` (~45 KB): 35 species
  profiles with H/W ranges and asset instructions, habitat palettes for
  Philly and Delco, county palettes, seasonal and 1990s-era rules (no EAB
  dead ash before 2007), three weighted palettes (Delco upland woodland:
  tuliptree 25 / white oak 20 / red oak 20 / beech 15 / red maple 10 /
  pignut hickory 10; creek floodplain: sycamore 35 / silver maple 25 / red
  maple 15 / boxelder 15 / black willow 10; old field and residential edge:
  black cherry 30 / sassafras 25 / redcedar 20 / walnut 15 / red maple 10),
  ten placement rules, a 12-species minimum set.
- `docs/reference/BLENDER_SCRIPTING_PA_TREES.md` (~40 KB): skeleton graph
  before geometry, tapered tubes with transported frames, foliage sockets,
  space colonization inside overlapping crown lobes, species architecture
  rows (C/H = crown-start/height, W/H = width/height, scaffold counts, limb
  angles from vertical), bark/foliage material rules, LOD budgets (far stand
  a few hundred to 1.5k tris), Godot export checklist, a runnable
  architecture-study script.

**How to apply:**
- **Backdrop tree (roadmap 228 step G):** replace Zoo 1.97.0's invented
  form rows (oak/maple/elm by aspect) with the guide's species rows: white
  oak open (C/H 0.18-0.35, W/H 0.8-1.2, 5-9 limbs at 45-78 deg), red maple
  (0.30-0.50, 0.55-0.85, ascending, oval), tuliptree forest (0.55-0.75,
  0.30-0.55, a leader), American elm (vase: ascend then arch, drooping
  tips), pin oak (lower limbs 95-115 deg, middle 65-90, upper 25-55),
  sycamore (few big divisions, PALE upper wood = per-instance bark tint),
  redcedar (columnar). Forest forms far, open forms near. Lot's belt mix by
  recipe from the weighted palettes. Per-instance colour for season and
  the sycamore, never a material (the draw-call rule).
- **Street/hero trees (roadmap 216):** the whole pipeline; the 12-species
  set; price a card crown first.
- The numbers are "authored starting values, not measured": fills for
  blanks ([[references-fill-blanks-not-override]]).

See [[backdrop-trees-are-lollipops]], [[trees-reference-roadmap-216]].
