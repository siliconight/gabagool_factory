"""Write patches/patch_dc_tidy.py (Deli Counter 0.265.0: the root is the builder), embedding the changelog entry and
the pins it is written against. The work itself is `tidy.py` and `tidy_hook.py` beside this, which the patch runs on
the repo; `build_clone.sh` builds the proven clone the same way. Refuses if the name is taken.

    python patches/dc_tidy/gen_dc_tidy.py
"""
import hashlib
import pathlib

F = pathlib.Path(r"C:\Projects\gabagool_studios\gabagool_factory")
SCRATCH = pathlib.Path(r"C:\Users\Brannen\AppData\Local\Temp\claude\C--Projects-gabagool-studios-gabagool-factory"
                       r"\27f14f8b-7ce5-44c0-a704-178a824035d7\scratchpad")
dest = F / "patches" / "patch_dc_tidy.py"
assert not dest.exists(), "name taken"
DC = F / "deli_counter"
CHANGELOG = (SCRATCH / "dc_changelog_0265.md").read_text(encoding="utf-8")
assert CHANGELOG.startswith("## [0.265.0]") and CHANGELOG.endswith("\n\n")
assert (DC / "VERSION").read_text(encoding="utf-8") == "Deli Counter 0.264.0"
PIN = hashlib.sha256((DC / "check.py").read_bytes().replace(b"\r\n", b"\n")).hexdigest()[:16]
N_TESTS = len(list(DC.glob("test_*.py")))
N_MIGRATE = len(list(DC.glob("migrate_*.py")))

PATCH = '''"""Deli Counter 0.265.0: the root is the builder -- the walker, 2026-10-23: "Deli Counter Repo needs a little clean
up/organization? (and a way so the home root doesn't just fill up with python files?)". The 181 tests move to tests/,
26 one-shot migrations to migrations/; root_modules.txt names the 81 builder modules left, and check.py refuses a root
.py not named there.

What this does, refused unless deli_counter is 0.264.0 with check.py the one it was written against, %d test_*.py and
%d migrate_*.py at its root and no tests/: runs `patches/dc_tidy/tidy.py` (the git moves and each moved file's
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
PIN = %r
N_TESTS, N_MIGRATE = %d, %d
CHANGELOG = %r
OLD_VERSION, NEW_VERSION = "Deli Counter 0.264.0", "Deli Counter 0.265.0"


def main():
    if (REPO / "VERSION").read_text(encoding="utf-8") != OLD_VERSION:
        raise SystemExit("REFUSED: deli_counter is not %%s; nothing written" %% OLD_VERSION)
    if (REPO / "tests").exists():
        raise SystemExit("REFUSED: deli_counter/tests/ exists already; nothing written")
    got = hashlib.sha256((REPO / "check.py").read_bytes().replace(b"\\r\\n", b"\\n")).hexdigest()[:16]
    if got != PIN:
        raise SystemExit("REFUSED: deli_counter/check.py is %%s, not the %%s this was written against; nothing "
                         "written" %% (got, PIN))
    n_t, n_m = len(list(REPO.glob("test_*.py"))), len(list(REPO.glob("migrate_*.py")))
    if (n_t, n_m) != (N_TESTS, N_MIGRATE):
        raise SystemExit("REFUSED: %%d tests and %%d migrations at the root, not %%d and %%d; nothing written"
                         %% (n_t, n_m, N_TESTS, N_MIGRATE))
    cl = REPO / "CHANGELOG.md"
    craw = cl.read_bytes()
    if b"\\r\\n" in craw or not craw.startswith(b"## [0.264.0]"):
        raise SystemExit("REFUSED: CHANGELOG.md is not LF opening on 0.264.0; nothing written")
    for script in ("tidy.py", "tidy_hook.py"):
        subprocess.run([sys.executable, str(HERE / script), str(REPO)], check=True)
    shutil.copy2(HERE / "test_root_is_the_builder.py", REPO / "tests" / "test_root_is_the_builder.py")
    (REPO / "VERSION").write_bytes(NEW_VERSION.encode("utf-8"))
    cl.write_bytes(CHANGELOG.encode("utf-8") + craw)
    print("%%s applied: the root is the builder. Now, in deli_counter/: the suite, check.py" %% NEW_VERSION)
    return 0


if __name__ == "__main__":
    sys.exit(main())
''' % (N_TESTS, N_MIGRATE, PIN, N_TESTS, N_MIGRATE, CHANGELOG)
compile(PATCH, str(dest), "exec")
dest.write_text(PATCH, encoding="utf-8", newline="\n")
print("wrote", dest, len(PATCH), "chars; pins check.py", PIN, "|", N_TESTS, "tests,", N_MIGRATE, "migrate_*")
