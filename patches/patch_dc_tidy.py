"""Deli Counter 0.265.0: the root is the builder -- the walker, 2026-10-23: "Deli Counter Repo needs a little clean
up/organization? (and a way so the home root doesn't just fill up with python files?)". The 181 tests move to tests/,
26 one-shot migrations to migrations/; root_modules.txt names the 81 builder modules left, and check.py refuses a root
.py not named there.

What this does, refused unless deli_counter is 0.264.0 with check.py the one it was written against, 181 test_*.py and
32 migrate_*.py at its root and no tests/: runs `patches/dc_tidy/tidy.py` (the git moves and each moved file's
repo-relative paths) and `patches/dc_tidy/tidy_hook.py` (tests/conftest.py, root_modules.txt, check.py, the test that
names a moved file), copies `test_root_is_the_builder.py` into tests/, writes VERSION and prepends the CHANGELOG entry.
Dry-run on a fresh clone against the proven clone's every file (`patches/dc_tidy/dry_run_*.out.txt`).

    python patches/patch_dc_tidy.py
    cd deli_counter && python -m pytest -q && python check.py
"""
import hashlib
import pathlib
import shutil
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
REPO = ROOT / "deli_counter"
HERE = ROOT / "patches" / "dc_tidy"
PIN = '25eb48e3b381977f'
N_TESTS, N_MIGRATE = 181, 32
CHANGELOG = '## [0.265.0] - the root is the builder: tests in tests/, one-shots in migrations/, and a hook that keeps it so\n\n**The walker, 2026-10-23**: "Deli Counter Repo needs a little clean up/organization? (and a way so the home root\ndoesn\'t just fill up with python files?)". 300 files stood at the root, 288 of them Python: 181 tests, 32\n`migrate_*`, 75 builder modules. 0.193.0 moved the 23 one-shots nothing imported into `migrations/` and left the rest,\nbecause the tests imported them by standing beside them.\n\n### Changed\n- **The 181 tests live in `tests/`**, with a `conftest.py` that puts the root and `migrations/` on the import path as\n  the root\'s own directory once was. In each, the name for the repo -- `HERE`, `here`, a `__file__`-relative path --\n  is the root, one level up, and a usage line that named a test or a migration names it where it now stands.\n- **26 `migrate_*` one-shots live in `migrations/`.** Six stay at the root, because they are builder code under an\n  old name: `presets.py` imports `migrate_roller_grill`, `migrate_slush_machine`, `migrate_wall_crossing`,\n  `migrate_window_poster` and `migrate_window_sign`, and a build reaches `migrate_furnish_recipes`\n  (`build_freshness.GEOMETRY_SOURCES`, which Level Factory parses by file name). Run one as `python\n  migrations/migrate_<name>.py`.\n- **The root holds the builder, 81 modules, and 92 files in all.** Nothing a consumer imports moved: Level Factory,\n  the factory\'s `tools/` and its findings import builder modules by name from the root, as before.\n\n### Added\n- **`root_modules.txt`** names every `.py` at the root. **`check.py`** -- the commit hook -- runs a first step, "the\n  root is the builder": a root `.py` not named there fails, with where it belongs (a test in `tests/`, a one-shot in\n  `migrations/`, an instrument in the factory\'s `tools/`), and so does a name with no file. A new builder module is\n  added to the list on purpose, in the change that adds it.\n- `check.py`\'s held-back and Blender-only tests are named under `tests/`.\n\n### Tests\n- `tests/test_root_is_the_builder.py` (new): the root holds what `root_modules.txt` names and nothing else; a stray\n  script at the root and a name with no file are both refused.\n- `tests/test_check_order.py`: the population test named where it stands.\n\n'
OLD_VERSION, NEW_VERSION = "Deli Counter 0.264.0", "Deli Counter 0.265.0"


def main():
    if (REPO / "VERSION").read_text(encoding="utf-8") != OLD_VERSION:
        raise SystemExit("REFUSED: deli_counter is not %s; nothing written" % OLD_VERSION)
    if (REPO / "tests").exists():
        raise SystemExit("REFUSED: deli_counter/tests/ exists already; nothing written")
    got = hashlib.sha256((REPO / "check.py").read_bytes().replace(b"\r\n", b"\n")).hexdigest()[:16]
    if got != PIN:
        raise SystemExit("REFUSED: deli_counter/check.py is %s, not the %s this was written against; nothing "
                         "written" % (got, PIN))
    n_t, n_m = len(list(REPO.glob("test_*.py"))), len(list(REPO.glob("migrate_*.py")))
    if (n_t, n_m) != (N_TESTS, N_MIGRATE):
        raise SystemExit("REFUSED: %d tests and %d migrations at the root, not %d and %d; nothing written"
                         % (n_t, n_m, N_TESTS, N_MIGRATE))
    cl = REPO / "CHANGELOG.md"
    craw = cl.read_bytes()
    if b"\r\n" in craw or not craw.startswith(b"## [0.264.0]"):
        raise SystemExit("REFUSED: CHANGELOG.md is not LF opening on 0.264.0; nothing written")
    for script in ("tidy.py", "tidy_hook.py"):
        subprocess.run([sys.executable, str(HERE / script), str(REPO)], check=True)
    shutil.copy2(HERE / "test_root_is_the_builder.py", REPO / "tests" / "test_root_is_the_builder.py")
    (REPO / "VERSION").write_bytes(NEW_VERSION.encode("utf-8"))
    cl.write_bytes(CHANGELOG.encode("utf-8") + craw)
    print("%s applied: the root is the builder. Now, in deli_counter/: the suite, check.py" % NEW_VERSION)
    return 0


if __name__ == "__main__":
    sys.exit(main())
