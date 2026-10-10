## [0.167.0] - init finds the tools, and the doctor asks the interpreter they run under

**Roadmap 202.** The walker's bar for the factory's first outside user: they
install Blender and Godot, unpack the factory and get levels out. Before any
level is built, two things stood in the way. One was a question. The other
was a check that said yes when the answer was no.

**What was there.**
- **`init` wrote `tools.local.json` with all eleven paths blank.** It then
  printed "edit tools.local.json to point at your tool repositories". So the
  first thing a stranger with a fresh unpack had to do was ask what those
  were.
  - The cold driver never relied on `init` for them. It copied the previous
    run's file.
  - Cold run 9194 stopped exactly there, because that run's workspace had
    been retired.
- **A blank `python_executable` meant two different interpreters:**
  - jobs ran under `python3`, the scheduler's fallback;
  - the Deli Counter and Dispatch probes ran under `python`, their own.

  On a fresh Windows machine both names are the Microsoft Store's
  app-execution alias, which runs no Python.
- **`doctor` read a third interpreter.** Its "python" check read
  `sys.version_info`, the interpreter running Level Factory, which needs no
  third-party package. It never asked the tools' interpreter anything, so a
  machine where no tool could start read PASS.

### What it is now

**One interpreter for the tools** (`packages/tools/interpreter.py`).
- `tools_python` is `python_executable` when it is set, and the interpreter
  running Level Factory when it is blank. The scheduler and both probes call
  it.
- On the machine this was written on, `python3`, `python` and that
  interpreter are one 3.14.4, so no cold run there changes.

**The doctor asks that interpreter** (`tools_python` check).
- It asks for its version, which must be at least 3.11.
- It asks whether it can import what the tools import at the top of a module
  on the level-making path:
  - numpy and Pillow (Pixelcoat, Patina);
  - pygltflib (Patina; Deli Counter's gates and composer);
  - jsonschema (Patina).
- It imports `PIL.Image`, not `PIL`, because the package imports without its
  compiled half and the module does not.
- A missing module FAILs, naming the `pip install` that fixes it, against
  that interpreter.
- An interpreter that does not run, or answers in any other shape, also
  FAILs. It is never read as a pass.
- Measured 2026-10-10: Blender 5.1.1's own Python carries numpy and lacks the
  other three (the factory's `docs/findings/stranger_install/`).

**`init` fills `tools.local.json`** (`packages/tools/discovery.py`). Each
value is printed with where it came from.
- **The factory** is the nearest directory at or above this checkout that
  holds `factory.manifest.json`, the marker `roadmap_status.py` walks up for.
  Outside any factory, every repository is named as not found.
  - **The first draft counted parents instead:** `parents[3]`.
  - `test_sibling_locator`'s guard failed it in the first full suite. The
    guard is right: from a git worktree that count lands in `scratchpad`
    (0.91.0, 0.94.0).
- **The tool repositories** are the checkouts the manifest names: an entry's
  `path`, else its key, each holding a `VERSION`.
- **Blender, Godot and the tools' Python** are looked for in this order:
  1. a flag (`--blender`, `--godot`, `--python`);
  2. this machine's `factory.local.json`;
  3. the environment: `$BLENDER`; `$GODOT`, `$LOT_GODOT`, `$DC_GODOT`;
  4. PATH;
  5. for Blender only, where its installers and archives put it. Newest
     first, 5.x included: Deli Counter's own search stops at 4.5.
- **Godot has no installer,** so after PATH it is not searched for.
- **What is not found stays blank** and is named, with the flag that
  supplies it.
- **A `tools.local.json` already in the workspace is kept.**

**`setup` records them once.** `level-factory setup [--blender] [--godot]
[--python]`:
- writes `factory.local.json` beside the manifest, which every later `init`
  reads first;
- runs the doctor over what it found;
- exits 3 while anything is missing or failing.

Run it again with a flag to fill in a gap: what it found before is read back
from the file. A `factory.local.json` in any other shape refuses rather than
reading as empty.

### Tests
`tests/unit/test_tools_python.py`, 9:
- a blank `python_executable` is this interpreter; a set one is used as
  given;
- the interpreter answers its version and names a module it cannot import,
  with its distribution;
- one that does not run, or answers in another shape, is an error;
- the doctor FAILs a tools' interpreter that does not exist, while its own
  `python` check passes;
- the doctor names what cannot be imported, with the `pip install`;
- a job with a blank `python_executable` runs under this interpreter (it was
  `python3`);
- the Deli Counter and Dispatch probes use the same one.

`tests/unit/test_discovery.py`, 14, on a factory built in a temporary
directory:
- the repositories are the checkouts the manifest names, `path` before key;
- a checkout without a `VERSION` is a gap;
- the flag, then the record, then the environment, then PATH;
- Blender falls back to an install and Godot does not;
- Godot is read from the walk test's variables;
- a recorded path that is not a file is named;
- a blank Python is not a gap;
- a record in another shape refuses;
- with no manifest, every repository is blank and says why;
- the factory is searched for, at any depth, and is None when there is
  none above;
- outside any factory, every repository says so;
- installs are newest first;
- `init` writes what was found;
- `setup` records it and the next `init` reads it.

On 0.166.0 both files fail to collect, because `interpreter` and
`discovery` do not exist. That proves little, so each was also run on 0.166.0
with only its new module added:
- **`test_tools_python.py`:** the four that hold the scheduler, the probes
  and the doctor fail, and the five on the module itself pass:
  - no `tools_python` check, twice;
  - a job ran under `python3`;
  - a probe ran under `python`.
- **`test_discovery.py`:** the two that hold `init` and `setup` fail, and the
  twelve on the module itself pass:
  - `init` wrote the blanks;
  - `setup` does not exist.

Suite: 2,103 passed, 14 skipped, 1 xfailed, 0 failed (exit 0). 0.166.0's
changelog gave 2,076. The 23 tests here account for 23 of the 27. The other 4
are `test_sibling_locator`'s guard, which runs once per `.py` in the repo: it
collects 307 cases on 0.166.0 and 311 here, one for each new file.
