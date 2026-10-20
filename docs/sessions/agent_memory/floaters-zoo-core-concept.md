---
name: floaters-zoo-core-concept
description: "walker 2026-10-11 asked for \"Floaters\" as a Zoo core concept; roadmap 234; in Godot a floater RESTS (skirt past 2 mm) or HOVERS by >= 3 mm, never the Cycles shader trick"
metadata:
  node_type: memory
  type: project
  originSessionId: 27f14f8b-7ce5-44c0-a704-178a824035d7
  modified: 2026-10-11T12:23:32.108Z
---

The walker (2026-10-11) asked to add "Floaters" to Zoo as a core concept / roadmap item: small details (knobs, bezels, rings, grilles, labels) made as their own meshes and laid on a surface rather than cut into its topology; origin at the bottom, normals out, snapped aligned to the face; stackable; bakeable. Their reference: a short Blender tutorial (frames in the walker's Downloads zip, kept OUT of the repo -- someone else's video; node set-up credited to YouTube's Penfinity) and the polycount thread 86536 (the walker pasted it when the site's bot check refused a fetch).

**Why:** the tutorial's Cycles trick (backfaces transparent via Geometry + Light Path nodes) does not exist in Godot's GL Compatibility renderer, and hovering floaters z-fight from sqrt(gap x 838871) m and show gaps; buried ones waste lightmap texels and darken (the thread's warnings).

**How to apply:** roadmap 234 holds the plan. The rule: a SOLID floater rests, open-bottomed, with only a skirt past the coplanar probe's 2 mm window (Zoo's `flat_forms.JOIN`, 4 mm); a FLAT floater is one-sided and hovers >= 3 mm (`ART_PROUD` is 5 mm); flatter detail is texture. Zoo already does this ad hoc (JOIN, ART_PROUD, crt STAND_BURY, RING_PROUD, register PROUD). The README section is staged at `patches/zoo_floaters/README_floaters.md` + `patches/patch_zoo_floaters_readme.py`, to land AFTER factory 1.38.0's tags (docs-only commit, no version bump). Next: the helper `geometry.add_floater` + a first species (a CRT panel, or [[roadmap 181's roof props]]).
