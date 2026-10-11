## 0.117.0 - the walk test's navigation updates on its own thread, so its clock need not wait

**Factory roadmap 239** (the walker: faster cold runs "without losing any
certainty"). Laser Tag's evaluations now take seconds (Laser Tag 0.27.0,
Level Factory 0.180.0), which leaves the walk tests as a shell leg's floor:
2.1 to 2.6 minutes each in cold run 9247. The director simulates at Godot's
default clock, which waits on real seconds -- its walkers' 475 to 480 m at
4 m/s are about 120 s of a 126 s job.

Run with Godot's `--fixed-fps 60` alone, the walk test failed on every one of
9247's three candidates: "navigation map is EMPTY at QA time". The setup
bakes synchronously and forces the map's commit, but Godot 4.7 iterates a
map and its regions on worker threads by default, so the region's update
landed when a worker finished -- wall time -- and the director's retry, "up
to 10 s" of physics frames, passed in milliseconds.

- **`lot_navqa_setup.gd`'s `_bake_nav` sets the world's map and the site's
  region to iterate synchronously before it bakes.** The setters are server
  commands applied in order at the next sync, which the existing
  `map_force_update` after the bake is.
- **`walktest.py` launches the scene with `--fixed-fps 60`** (`FIXED_FPS`;
  0 restores the waiting clock): each frame one physics step at the
  project's 60 ticks, computed as fast as the processor allows.

**Measured** (the factory's `docs/findings/grader_speed/walktest_ab.py`,
copies of cold run 9247's three staged walk tests, each the job's own
command and environment, each report compared with the job's field for
field):

    seed   the job's clock    --fixed-fps 60 alone             --fixed-fps 60, synchronous navigation
    9003   141.0 s, identical  2.1 s, ok=False, the map EMPTY   4.2 s, identical but map_iteration 2 -> 1
    9104   122.0 s, identical  2.0 s, ok=False, the map EMPTY   4.1 s, identical but map_iteration 2 -> 1
    9205   150.1 s, identical  2.3 s, ok=False, the map EMPTY   4.8 s, identical but map_iteration 2 -> 1

`map_iteration` is the director's own diagnostic (the navigation map's
iteration id when the walk began: one synchronous commit instead of two);
nothing reads it. This release's setters at run time against those
project-setting arms: on cold run 9247's three staged walk tests under --fixed-fps 60, this release's setters in the scene's own setup script, with nothing in project.godot, read identical to the project-setting arm in every field, twice each and three at once, in 4.2 to 5.3 s; against their jobs (122.0 to 150.1 s) only map_iteration differs, 2 -> 1 (docs/findings/grader_speed/walktest_setters_ab.py). REFUTED, KEPT: the first run patched the copy of the setup at the staged project's root, which the scene does not load, and so measured the unpatched setup failing (walktest_setters_ab.draft1.out.txt)

**Tests:** `tests/test_walktest_clock.py`, four (the scene runs on the fixed
clock, zero restores the waiting one, the map and the region are set
synchronous before the bake, the commit is still forced after it), three
failing on 0.116.0. 797 passed on the repo, 0.116.0's recorded 793 and these four; tests/test_walktest_clock.py, three of its four failing on 0.116.0
