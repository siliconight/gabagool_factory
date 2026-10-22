"""Prove 0.232.0's tests against Level Factory 0.231.0: clone the factory's level_factory at 0.231.0 (d3cf8d5) into
<scratch dir>, copy in the new tests/unit/test_buildings_index.py and tests/unit/test_compose_draws_its_buildings.py,
and run both there -- with --continue-on-collection-errors, because the first imports a module 0.231.0 does not have
and would otherwise stop the run before the second is asked anything. Writes prove_tests_on_0231.out.txt beside this
file. Copied from `patches/lf_enemy_eye/prove_tests.py`, its version and files changed.

    python patches/lf_drawings/prove_tests.py <new scratch dir> <0.232.0 dir>
"""
import os
import pathlib
import shutil
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
FACTORY = HERE.parents[1]
root, new = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
assert not root.exists(), "the scratch dir must be new"
subprocess.run(["git", "clone", "-q", str(FACTORY / "level_factory"), str(root)], check=True)
subprocess.run(["git", "-C", str(root), "checkout", "-q", "d3cf8d5"], check=True)
TESTS = ("test_buildings_index.py", "test_compose_draws_its_buildings.py")
for f in TESTS:
    assert not (root / "tests" / "unit" / f).exists(), f
    shutil.copy2(new / "tests" / "unit" / f, root / "tests" / "unit")
env = dict(os.environ, LF_LASERTAG_ROOT=str(FACTORY / "lasertag"), LF_DC_ROOT=str(FACTORY / "deli_counter"))
r = subprocess.run([sys.executable, "-B", "-m", "pytest", "-q", "-p", "no:cacheprovider", "-rA",
                    "--continue-on-collection-errors"] + ["tests/unit/" + f for f in TESTS],
                   cwd=root, capture_output=True, text=True, env=env, encoding="utf-8", errors="replace")
keep = [l for l in r.stdout.splitlines() if l.startswith(("PASSED", "FAILED", "SKIPPED", "ERROR", "E  "))]
txt = "== 0.232.0's tests on 0.231.0 (d3cf8d5) ==\n" + "\n".join(keep) + "\nexit %d\n" % r.returncode
(HERE / "prove_tests_on_0231.out.txt").write_text(txt, encoding="utf-8", newline="\n")
print(txt)
