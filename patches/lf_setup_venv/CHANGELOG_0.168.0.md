## [0.168.0] - setup --venv gives the tools a Python of their own

**Roadmap 202.** The walker's bar is that a consumer installs Blender and
Godot and nothing else. Blender ships an interpreter: 5.1.1's is 3.13.9, and
Level Factory runs under it unchanged (measured 2026-10-07). The tools do
not.
- **What is missing.** That Python carries numpy and lacks three packages
  the level-making path imports at the top of a module:
  - Pillow (Pixelcoat, Patina);
  - pygltflib (Patina; Deli Counter's gates and composer);
  - jsonschema (Patina).
- **What 0.167.0 already did.** Its `tools_python` check says so, but the
  only fix it could name was "pip install into it".
- **Why that fix does not work for a stranger.** For Blender installed under
  Program Files, it means writing into the Blender install, which needs admin
  rights. It also changes a program the user has for other reasons.

### What it is now

`level-factory setup --venv` takes these steps:
1. **It makes `<factory>/.venv`** from the interpreter running `setup`, with
   `--system-site-packages`. For somebody who installed nothing else, that
   interpreter is Blender's, so the environment keeps its numpy.
2. **It installs `interpreter.PINNED` into the environment:** Pillow 12.3.0,
   pygltflib 1.16.5 and jsonschema 4.26.0.
   - These are the versions every suite and cold run on this machine used.
   - A different Pillow is a different PNG encoder and resampler, so an
     unpinned one would make texture packs nobody here has looked at.
3. **It records the environment's interpreter** as `python_executable` in
   `factory.local.json`. Every later `init` writes it into the workspace.

**Its limits.**
- **Network.** It is the one step that needs the network: pip fetches from
  its index. It is asked for with a flag, never assumed, and pip's output
  goes to the terminal as it runs.
- **What it writes.** Nothing outside `<factory>/.venv`.
- **Re-running it** reuses the environment, and pip finds the pins already
  satisfied.
- **Refusals.** `--venv` with `--python` refuses. If the environment or the
  install fails, nothing is recorded.

The doctor's `tools_python` FAIL now names `level-factory setup --venv`
first, then the in-place install.

**What is not proven here: the install itself.**
- Downloads on this machine wait for the walker's yes, so no test runs pip.
- The environment is made for real once. The test proves it is rooted in its
  base and keeps the base's packages.
- The first real `pip install` into Blender's Python will be the install
  cold run's.

### Tests
`tests/unit/test_setup_venv.py`, 9:
- the environment is made from the base with `--system-site-packages`, and
  given exactly the pins;
- the pins are what the doctor asks for, less numpy, which the base must
  carry;
- a failed environment says so and installs nothing; a failed install says
  so;
- a real environment made from this interpreter has its prefix in `.venv`
  and its base prefix at this one;
- `setup` records the environment's interpreter;
- `setup` refuses `--venv` with `--python`;
- a failed environment records nothing;
- the doctor points at `setup --venv`.

On 0.167.0 all 9 fail. `make_venv` and `PINNED` do not exist, `setup` has
no `--venv`, and the doctor does not name it.

Suite: 2,113 passed, 14 skipped, 1 xfailed, 0 failed (exit 0). 0.167.0 gave
2,103. The 9 tests here account for 9 of the 10. The tenth is
`test_sibling_locator`'s guard, which runs once per `.py` in the repo: 311
cases on 0.167.0 and 312 here, one for the new test file.
