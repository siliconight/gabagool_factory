## [1.97.0] - the backdrop tree with a silhouette

### What changed

**Roadmap 228, step F.** The walker, on cold run 9227's parkland, of
1.96.0's `backdrop_tree`, a trunk box under one twelve-by-six faceted
sphere: "those trees in the distance are a little lazy imo (giant lolipops
vs. trees)". A sphere on a stick is not a tree's outline at twenty to
ninety metres.

- **The tree is a trunk that flares at the foot and forks into three limbs,
  under a crown of seven overlapping lobes** at different heights: one on
  each limb's tip, a top lobe on the axis whose top is the slot's top, and
  three fillers between the limbs, lower, so the outline has no gaps and
  daylight shows under the crown (`backdrop_forms.tree_plan`). Each lobe is
  an eight-by-five ellipsoid displaced by three broad lobes of its own
  (`geometry.displace_lobes`, a tenth of its radius), so no two read as the
  same ball.
- **The form follows the slot's proportions,** so Lot's dims choose it
  (`tree_form`): a squat slot (h / w under 1.25) is a broad oak-like crown on
  wide limbs, a tall one (over 1.6) a vase-shaped elm with steep limbs and a
  high crown, between them a round maple. 1.96.0's three sizes are all
  maples; the belt's variety is Lot's next call.
- **The sum is fitted to the slot** (`geometry.fit_to`), so the extents are
  exact whatever the lobes do; the seed turns the limbs and nothing else.
- Bark and the style's vegetation, two materials and two objects as before;
  the budget rises from 180 to 800 triangles (the estimate is 672), which a
  MultiMesh a module a side does not notice: the parkland cost 14 draws a
  heading and no frame time in cold run 9227.

**Built in Blender:** the second kit (`docs/findings/backdrop_kit/backdrop_slots_2.json`, two trees at 4 x 4 x 6 and 7 x 7 x 10 m and the warehouse) rebuilt in Blender 5.1.1 on a draft of 1.97.0, theme delco: all three PASS, the trees at 548 triangles of 800 (the estimate said 672; the lobes' uv-spheres share their poles), bark and vegetation two materials, two objects. The renders (`docs/findings/backdrop_kit/tree_forms_1_97_0.png`): the first draft's four balls on sticks read as balloons, and the second's ten overlapping lobes with a lower ring read as a crown over a forking trunk -- a low oak, a round maple, a narrow elm

**The census:** `tools/coplanar_census.py --species backdrop_tree` on the draft: "3 builds, 0 with coincident pairs, 0 that did not build", 548 triangles at the default and the maximum dims; the limbs end inside their lobes and the lobes overlap as ellipsoids, so no face lies in another's plane

**Tests:** 6 pure in `tests/test_backdrop_3.py`: the form by proportion,
the foot on the ground and the top lobe at the top, every limb ending inside
a lobe and every lobe above the fork, the lobes' reach within a fifth of
the width before the fit, the seed turning the limbs alone, the estimate
within the budget. **Suite:** 4,147 passed, 424 skipped (the builds that need bpy), 1 xfailed, exit 0 on the repo (4,141 as 1.96.0 and the 6 new cases).
