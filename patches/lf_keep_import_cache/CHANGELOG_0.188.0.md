## [0.188.0] - The export keeps its import cache beside the package, for the walk copy

**Why now.** Roadmap 239. Cold run 9252's step stamps showed a cost no record
had timed: the drive's walk step, 91 s of 615 (88 of 580 in 9253). The
factory's `tools/walk_export.py` copies the package and imports it from
scratch -- a minute after the export imported the same files and deleted the
cache, which a package must not ship (machine-specific and large; it ships
sidecars).

**What changed.**

- `occluders.keep_cache(export_dir)` moves the import cache out of the
  package to sit beside it as `<package>.import_cache`, replacing any kept
  before it; `kept_cache_dir` names the place. The package leaves the export
  as cache-free as it did.
- `export_mission` keeps the cache where it dropped it -- after the census,
  before the pins are read back and the verdict walks the tree -- and removes
  the last package's kept cache before it builds, so an export that stops
  early leaves no walk copy a stranger's cache.
- `drop_cache` stays, for the occluder bake's and the merge's failures.
- The factory's `tools/walk_export.py` moves a kept cache into the copy as
  its `.godot` before its import pass. Moved, not copied: the copy is the
  cache's only reader, so it costs no disk, and a second walk copy imports
  from scratch as every one did before.
- `tests/unit/test_census_reads_the_bake_cache.py` (0.181.0) and
  `test_texture_pins_survive_the_bake.py` (0.182.0) pinned their order at
  the drop's line; they pin it at the keep's, the order unchanged.

**Is the copy the same?** Measured on cold run 9253's package re-exported
(the factory's `docs/findings/grader_speed/walk_cache_probe.py`): two walk
copies imported from scratch, the control, and one started from the kept
cache. Their imports differ in the same 482 scene files and their checksums
between the two from scratch as between either and the third -- an import
is not byte-deterministic -- and the third's lightmap texture is the
editor's encoding, which the export's cache has carried since 0.183.0. Every
model each imports loads the same: 501 of 501 by `import_digest.gd` (each
node, transform, mesh surface, vertex and index count, second UV set,
material and texture), a digest a positive control moves -- one model's
sidecar changed in the third copy and imported again moved that model's
digest and no other, and undoing it moved it back. The level each loads is
the same: 20,954 nodes, 3,380 meshes, none empty, 242 lights, 3,320
lightmap users. The census that said so first was blind and is kept, with
its fix, in the findings.

**Measured:** cold run 9253's package re-exported in its workspace with the cache kept beside it, the run's package held aside and put back (the factory's docs/findings/grader_speed/walk_cache_probe.py): the walk copy as the drive made it, imported from scratch, 86.4 and 88.2 s; started from the kept cache, 11.5 s (5.1 s assembling, 2.2 s copying the cache in, 4.2 s for the import pass that checks it); the probe's first run 85.6, 86.2 and 9.6 s. Every model the three copies import loads the same, 501 of 501 by import_digest.gd, a digest the positive control moved for its one model alone; the level the same in all three, 20,954 nodes, 3,380 meshes, none empty, 242 lights, 3,320 lightmap users

**Tests:** `tests/unit/test_kept_import_cache.py`, five (the cache goes
beside the package and the package ships without it; no cache, nothing
kept; a kept cache is replaced, never merged; an export removes the last
package's kept cache before it builds; the cache is kept where it was
dropped), all failing on 0.187.0. 2,297 passed, 16 skipped, 0 failed (JUnit, 2,313 tests: the five above and the sibling-locator check over the new file)
