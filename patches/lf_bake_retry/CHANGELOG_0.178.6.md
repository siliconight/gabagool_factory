## [0.178.6] - A light bake that fails is tried once more on a fresh copy

**Cold run 9243.** 9242 again, on 0.178.5. The scene opened -- on the
plugin's second ask, at frame 300, the first one dropped -- and the bake ran
46 s; then the editor read its lightmap image back EMPTY
(`src_image_len == 0`, `res://bake.exr` "Error importing") and raised
"Failed creating lightmap images. Make sure the lightmap destination path
is writable." The package shipped unbaked again. 0.178.5 kept the editor's
log, which is how this one is known.

**The same package bakes on the next try.** A copy of 9243's package, baked
with Level Factory's own `bake()` on 0.178.5: ok, 38.2 s, 491 models and
the responders' car kept dynamic as in 9241's bake, 3,483 lightmap users --
9241's 3,518 less the 35 fixture meshes Zoo 1.100.0 merges away. So the
empty image is not the package's: something on the machine got between the
editor's write and its read. What, the logs do not say -- an antivirus scan
of the fresh file is one candidate and nothing more.

- **`BAKE_ATTEMPTS` = 2:** the editor's run is a loop, each try on a fresh
  work copy, stopping at the first that bakes.
- **Every try keeps its own editor log** (`<package>.lightbake.log`, then
  `.lightbake.2.log`), and `light_bake.json` carries `attempts` -- each
  try's editor seconds, log, whether it timed out and its result -- with
  `editor_s`, `editor_log` and `result` the last try's, as before.
- **The export says when it took two:** "light bake: baked on attempt 2 of
  2; the first failed: ...".

One more try costs one more editor minute, and only on a failure. Driving an
editor's GUI is not deterministic, and two bakes in three on this lot
failed for two different reasons before this release.

### Tests

Two in `tests/unit/test_light_bake.py`: a bake that fails once is tried on
a fresh copy and ships baked, the first try's error kept; a bake that works
is not tried again. 0.178.5's log test now reads both tries' logs.

**Suite:** 2,230 passed, 14 skipped, 1 xfailed, exit 0: 0.178.5's 2,228 and the two new tests; the new tests and 0.178.5's log test read both tries and fail on 0.178.5.
