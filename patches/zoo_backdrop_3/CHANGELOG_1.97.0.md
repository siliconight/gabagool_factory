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

**Built in Blender:** RESULT_BUILD

**The census:** RESULT_CENSUS

**Tests:** 6 pure in `tests/test_backdrop_3.py`: the form by proportion,
the foot on the ground and the top lobe at the top, every limb ending inside
a lobe and every lobe above the fork, the lobes' reach within a fifth of
the width before the fit, the seed turning the limbs alone, the estimate
within the budget. **Suite:** RESULT_SUITE.
