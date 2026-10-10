## [0.170.0] - Re-grounded to the tools of 2026-10-10; a hint names the command that was typed

**Roadmap 202's install test.** The factory was packaged, unzipped into a
fresh folder, `C:\stranger_202\gabagool`, and `START_HERE.md`'s commands
were typed into cmd.exe there. Two things a stranger would have had to ask
about came out of it before any level was built.

### Eight warnings nobody could act on

`setup` ends with the doctor. On the fresh unpack it printed, for every
tool, `drift vs certified <old> (grounded); re-certify`. The tools were
exactly the ones the package carries. The certified versions were
`contracts.GROUNDED`, last re-grounded on 2026-09-21 and three weeks behind
again on all eight rows:

| tool | was | now |
|---|---|---|
| deli_counter | 0.141.2 | 0.205.0 |
| lot | 0.74.0 | 0.105.0 |
| laser_tag | 0.23.1 | 0.25.0 |
| pixelcoat | 0.45.0 | 0.62.0 |
| zoo | 1.1.1 | 1.94.0 |
| lux | 0.40.0 | 0.72.0 |
| patina | 0.22.0 | 0.30.0 |
| dispatch | 0.3.0 | 0.5.2 |

Re-grounded the way 2026-09-21's was:
- **Measured.** Each tool was read through the probe and from its
  `VERSION` file.
- **Licensed.** `LF_TOOLS_DIR=<factory> pytest tests/real_tools` ran 10 of
  12. `test_real_dispatch` skipped, because its example's build inputs are
  absent, as before.
- **Before:** `test_grounded_table` failed, naming all eight drifts. **After:**
  it passes.

The stand-in tool repos follow the table, as
`test_the_stub_repos_declare_the_grounded_versions` asks: the suite failed
on all eight until they did. The stand-ins are `tests/fixtures/repos/<tool>`,
which the integration suites and `doctor` probe like real tools.
- Each one's `VERSION` now declares the grounded version.
- Deli Counter's and Dispatch's stub `contract` commands report it.
- Their contract shapes are unchanged, and their docstrings say so.

The 2026-09-21 table is kept below the new one. So are the rows' notes,
each marked as still true or as history:
- **Still true:**
  - Laser Tag's `plugin.cfg` still says 0.19.0 against `VERSION`'s 0.25.0.
  - Patina's `pyproject.toml` still says 0.1.1.
- **History:**
  - Dispatch's `__version__` now agrees with its `VERSION`.
  - Pixelcoat's `version.py` now derives from its `VERSION`.

### A hint that named a command they did not have

`init`, `make` and the doctor end with the next command to type, as
`level-factory ...`. That is the console script an installed copy has.
Somebody who unpacked the factory runs its launcher, `.\factory` or
`sh factory.sh`, and has no `level-factory`. The install test's `init`
printed `then run: level-factory -C C:\stranger_202\gabagool\levels doctor`.

`discovery.command_name()` is what the launcher says was typed:
- the launchers set `LEVEL_FACTORY_COMMAND`, `%~0` and `sh $0`;
- `level-factory` when the variable is unset.

These hints use it:
- `init`'s next step and its `setup` advice;
- the doctor's `setup --venv`;
- `make`'s closing walk command.

### Tests
`tests/unit/test_command_name.py`, 5:
- unset, it is `level-factory`, and blank counts as unset;
- set, it is the launcher's string, trimmed;
- `init`'s next step and `setup` advice name it, and `level-factory`
  appears nowhere in its output;
- the doctor names it for `setup --venv`;
- `make` names it for the walk.

On 0.169.0 all five fail: `discovery.command_name` does not exist.

The re-grounding is licensed by the real-tool smoke, as above, and not by a
unit test, which has no tools to read.

Suite: 2,135 passed, 14 skipped, 1 xfailed, 0 failed (exit 0). 0.169.0 gave
2,129. The 5 tests here account for 5 of the 6. The sixth is
`test_sibling_locator`'s guard, which runs once per `.py` in the repo: 314
cases on 0.169.0 and 315 here. The first run of this release failed
`test_the_stub_repos_declare_the_grounded_versions` on all eight stand-ins,
which is how they came to be in it. The real-tool smoke, with
LF_TOOLS_DIR set to the factory, ran 11 of 12 and exited 0.
