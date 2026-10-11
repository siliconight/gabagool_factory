## [1.100.0] - a fixture's same-material parts are one mesh, inside it and never across two

### What changed

**Roadmap 233.** A building's fixtures ship as one GLB of many placements --
a layer, not a module -- and `build_fixtures` exported it unmerged on
purpose, because merging across fixtures would cost culling. So a fixture
whose parts share a material paid a submission for each part. Built from
1.99.0's genomes at their default corner: a streetlight is a pole, a base
and a head in one metal, three meshes where one carries them; a pendant a
cord and a socket; a wall pack an arm and a body; a sign box its arms and
its cabinet.

- **`merge.pack_by_material` takes `units`**, each part's placement. Given,
  a part merges only with parts of its own unit, a part with no unit is
  kept as itself, and a unit's parts must share one transform, which the
  merged mesh takes -- the identity rule a module keeps becomes "one
  transform" inside a placement, because `build_fixtures` moves a
  placement's parts with one matrix. A part whose transform differs from
  its unit's is refused and named, not baked.
- **`build_fixtures` records each visual part's placement** and exports
  merged by it: a streetlight sheds two meshes, a pendant, a wall pack and
  a sign box one each, and every other fixture species ships as it did
  (one part a material already). `merge_parts` False is the one-build
  control, as for a module, and `zoo_cli.py --no-merge-parts` reaches the
  fixtures now. The index carries the merge's stats under `merge`.
- **What it keeps:** every lens, diffuser and face is the only part in its
  material, so it ships as itself under its own name and material, which
  is what Lux's emissive binder and its failing-fixture lens finder read;
  the `LuxEmit_*` markers are empties and ride out untouched; triangles are
  asserted equal before and after, as for every merge.

**The layer:** the three fixture layers of cold run 9239's lot (restaurant_row_001: deli_a01, office, pharmacy_a01), built from Deli Counter's own lights manifests with each job's sign pack, theme delco_1997, once with the merge and once with `--no-merge-parts`, counted by `docs/findings/fixture_merge/layer_count.py` in the factory: the deli 257 submissions to 232, the office 128 to 122, the pharmacy 52 to 48 -- 437 to 402, 35 fewer, the counts the parts census predicts (a pendant, a sign box and a wall pack one each). In the deli the pendants' metal went from 46 meshes to 23, the sign box's and the wall pack's from 2 to 1; every lens, the domes, the troffers and the sign's face are the same counts both ways, and the LuxEmit markers 116, 61 and 24 in both.

### Tests

6 in a new `tests/test_fixture_merge.py`, 4 of them building in Blender (they skip without bpy): the layer is exported merged by placement and the exporter hands the units on; one layer built both ways from one manifest, a pendant, a streetlight and a wall pack shed their extra parts' meshes and never merge across two placements, each merged mesh stands where its parts stood, and every marker rides out beside its hardware; a unit whose parts disagree on their transform is refused, not baked. Run inside Blender 5.1.1 on a patched clone and again on the repo: 6 passed. On 1.99.1: 4 failed and 2 passed -- the positions and the markers, which hold unmerged as well and are there to hold after it.

**Suite:** 4,157 passed, 438 skipped (the builds that need bpy), 1 xfailed, exit 0 on the repo: 1.99.1's 4,155 and the two new pure tests, the four new bpy tests among the skips and run inside Blender as above, with 1.99.1's eleven: 17 passed.
