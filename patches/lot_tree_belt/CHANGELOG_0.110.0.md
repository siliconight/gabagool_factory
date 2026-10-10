## 0.110.0 - the tree belt in clusters, in three forms

**Roadmap 228, step F.** The walker, on cold run 9227's parkland: "those
trees in the distance are a little lazy imo (giant lolipops vs. trees)".
Zoo 1.97.0 redraws the tree with a silhouette and takes its form from the
slot's proportions: a squat slot is a broad oak, a tall one a vase-shaped
elm, between them a round maple. This lays the belt to suit it.

- **Six dims, two a form** (`TREES`): oaks at 8 x 8 x 8 and 11 x 11 x 12 m,
  maples at 5 x 5 x 7 and 7 x 7 x 10, elms at 4 x 4 x 9 and 6 x 6 x 13,
  drawn at random a tree, so a belt mixes crowns instead of standing three
  maples. Six modules a belt where there were three: about twelve more
  MultiMeshes a level, which the parkland's 14 draws a heading (9227) has
  room for; 9229 and the next parkland run price it.
- **Clusters, not ranks** (`_trees`): the near belt stands in groups of
  `TREE_CLUSTER` (4 to 9) trees at `TREE_STEP` (1.5 to 3.0 m) apart, with
  `TREE_CLUSTER_GAP` (5 to 18 m) of daylight between the groups, the way a
  wood's edge breaks; the far belt keeps its one sparse run. The roadside's
  thin belt clusters the same way.
- **The near edge stands 6 m off the fence** (`TREE_BELT`, 2.5 before;
  the roadside's 4 m): on 9227's 87 m plate a 9 m crown 2.5 m past the
  fence filled an elevated view's foreground larger than the building.

**Tests:** `test_the_parkland_is_a_belt_of_trees_and_no_tower` keeps its
argument with the belt's floor at 150 trees on the 196 x 100 m test plate
(300 before: the clusters' gaps are the point). **Suite:** RESULT_SUITE.
