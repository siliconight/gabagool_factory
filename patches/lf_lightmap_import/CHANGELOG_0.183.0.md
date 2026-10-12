## [0.183.0] - The editor's import of the lightmap is kept, not done again

**Why now.** Roadmap 239: the export is the cold run's constraint, and
importing was 65 % of it. Measured on cold run 9248's export with the light
bake's imports logged (factory `docs/findings/grader_speed/bake_imports_probe.py`):
the bake's SECOND `--import`, after the editor's files are copied back,
imported one file and nothing else -- the lightmap `bake.exr`, a 1024 x 1024
texture array of 16 slices, VRAM-compressed (BPTC) as its sidecar says -- in
49.5 s. The editor that baked it had already imported those same bytes in
its work copy (its log: the bake itself 32.5 s of the editor's run).

**What changed.** `light_bake._copy_lightmap_import` copies the work copy's
cache entries for the lightmap (`.godot/imported/bake.exr-*`) into the
package's cache, beside the sidecar `BAKE_FILES` already copies, so the
import after finds them current: an entry is named for the file's `res://`
path and checked against its source's hash and its import parameters, all
three the same files in both projects. Without a cache on either side it
copies nothing and the import does the work as before. The bake's report
records what it copied (`lightmap_import_copied`).

**Measured:** cold run 9248's export re-run in its workspace (the run's package held aside and put back): the bake's second import 4.6 s against 50.3 s on 0.182.0 the same way, the two cache entries for bake.exr copied (light_bake.json: lightmap_import_copied), the bake ok, bake.exr.import the run's own but its uid, every shared texture shipped pinned, the closure verdict ok over 3,041 files; the export 281 s with the pin census's overhead against 339 s for 0.182.0 measured the same way (docs/findings/grader_speed/lightmap_import_ab.out.txt)

**Tests:** `tests/unit/test_lightmap_import_is_kept.py`, three (the
lightmap's entries are copied and nothing else; without a cache it copies
nothing and makes none; the bake keeps them after the copy back and before
its last import), all failing on 0.182.0. 2,263 passed, 16 skipped, 0 failed (JUnit, 2,279 tests); tests/unit/test_lightmap_import_is_kept.py, three, all failing on 0.182.0
