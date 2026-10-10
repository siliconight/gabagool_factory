## [0.173.0] - The doctor reads the long-paths flag and weighs the workspace's depth

**Roadmap 227.** The doctor WARNed on every Windows machine:

    windows_long_paths  verify LongPathsEnabled registry flag for deep asset paths

It never read the flag. So it could not pass where long paths were on, and
where they were off it could not say whether a workspace sat deep enough to
matter. It was the last WARN on a stranger's first `setup` in install tests 2
and 3.

**What it meant was real.** Measured on cold runs 9222 and 9223
(`docs/findings/long_paths/` at the factory root):
- A level writes files 217 characters below its workspace: a Godot
  editor-state file in the lux_apply staging copy. The pipeline's own
  deepest output, a texture's provenance file, is 193 below.
- Those workspaces sit 69 characters deep. They held 725 and 440 files past
  Windows' 260, which Windows refuses unless `LongPathsEnabled` is 1.
- Explorer's Extract All, into a stranger's Downloads, puts a workspace
  about that deep.

**What the row says now:**
- **Long paths on:** PASS.
- **Off, or unreadable,** with the workspace's deepest file within 260:
  PASS, naming how far it reaches.
- **Off and past 260:** WARN, naming the reach, the budget (a workspace of
  at most 42 characters) and the two remedies, a shorter folder or an
  administrator turning long paths on.

It stays a WARN because what fails with the flag off has not been measured
here: this machine's flag is 1, and changing it is a system setting.

**Where it looks.**
- **`doctor`:** the workspace itself.
- **`setup`:** `<factory>\levels`, the workspace `START_HERE.md`'s first
  level makes.

`LEVEL_DEPTH` (217) is measured, not derived, and says what it was measured
against.

**Tests:** 9, all failing on 0.172.1 and passing on the draft. **Suite:** 2,163 passed, 14 skipped, 1 xfailed, exit 0 (2,153 as 0.172.1, the 9 new tests, and the sibling guard's case for the new file).
