# How deep a level's files reach, against Windows' 260 (roadmap 227)

**Question.** The doctor prints, on every Windows machine:

    [WARN] windows_long_paths  verify LongPathsEnabled registry flag for deep asset paths

It is the only WARN left on a stranger's first `setup` (install tests 2 and
3). Does a level's file tree actually reach past 260 characters? If it does,
how far below its workspace does it reach, and so how deep can a workspace sit?

**Answer: yes.** A level writes 217 characters below its workspace. On this
machine's workspaces, 69 characters deep, that put 440 and 725 files past 260.

## What decides it

Windows refuses a path longer than 260 characters (`MAX_PATH`), unless both
of these hold:
- the program is long-path aware;
- `HKLM\SYSTEM\CurrentControlSet\Control\FileSystem\LongPathsEnabled` is 1.

On this machine the flag reads 1. So nothing here has ever failed on a long
path, and nothing here has run with the flag off. Setting it is a system
setting and was not touched. The failure itself is therefore not measured,
only the depth that would meet it.

## Measured

`depth.py` takes the deepest file of each kind, in characters below the
workspace root. Its output is `depth_9222_9223.txt`. Cold runs 9222 and 9223 were both restaurant_row_001, and
both workspaces sit at `C:\Projects\gabagool_studios\gabagool_factory\workspaces\cold-922N-ws`,
69 characters.

| kind | below the workspace | absolute | the file |
|---|---|---|---|
| Godot's `.godot/editor` (UI state) | 217 | 287 | `.level_factory\staging\<mission>.lux_apply\.godot\editor\<a Zoo prop's GLB name>-<md5>.scn-folding-<md5>` |
| everything else | 193 | 263 | a texture's `.png.provenance` in `jobs\<mission>.presentation_compose\1\out\presentation\lot\<building>\art\zoo\_tex\` |
| Godot's `.godot/imported` (what a level loads) | 174 | 244 | the same prop's `.glb-<md5>.md5` |
| Godot's other files | 117 | 187 | a candidate's `global_script_class_cache.cfg` |

**Files past 260, absolute:**

| run | files | past 260 |
|---|---|---|
| 9223 | 22,328 | 440 |
| 9222 | 26,925 | 725 |

**The budget, with the flag off:**
- **Every file under 260:** the workspace's own path can be at most
  260 - 217 - 1 = 42 characters.
- **Everything but Godot's editor state under 260:** at most 66 characters.

## Why a stranger meets it

- **`START_HERE.md` says "unzip the factory anywhere".** Its example,
  `C:\gabagool`, is short.
- **Explorer's Extract All goes deep by default.** It puts a package under
  `C:\Users\<name>\Downloads\gabagool_factory_package_<stamp>\`. With the
  page's `levels` folder below that, a workspace sits about as deep as this
  machine's, at around 70 characters.
- **The doctor cannot tell them.** It WARNs without reading the flag
  (`level_factory/packages/tools/doctor.py:202`). So it cannot PASS where
  the flag is on, and where it is off it does not say whether this
  workspace is deep enough to matter.

## What was not measured

- **What fails, and how, with the flag off.** It could be Python's `open`,
  Godot's import, or Blender's export. A Godot editor cache that cannot be
  written may be harmless; a provenance file or an import that cannot be
  written is not.
- **Linux.** Its limits are 4,096 for a path and 255 for one name. The
  longest name here is 151 characters, a Godot editor-state file
  (`depth_9222_9223.txt`). So Linux is not expected to meet this, but no
  Linux machine has run the factory.
- **Whether 217 is the deepest any level writes.** It is one mission's,
  measured twice. The names come from the library and from Godot's cache
  scheme, so a longer prop name moves it.
