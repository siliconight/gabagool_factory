"""Prove 0.229.0's tests against Level Factory 0.228.0: clone the factory's level_factory at 0.228.0 (e71ea71) into
<scratch dir>, copy in the changed tests/unit/test_sightlines.py, run it with the factory's Laser Tag named
(LF_LASERTAG_ROOT), so the new test asks 0.228.0's heights of the shipped evaluator. Writes prove_tests_on_0228.out.txt
beside this file. Copied from `patches/dc_reserved_routes/prove_tests.py`, its repository, version and files changed.

    python patches/lf_sight_crossing/prove_tests.py <new scratch dir> <0.229.0 dir>
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
subprocess.run(["git", "-C", str(root), "checkout", "-q", "e71ea71"], check=True)
shutil.copy2(new / "tests" / "unit" / "test_sightlines.py", root / "tests" / "unit")
env = dict(os.environ, LF_LASERTAG_ROOT=str(FACTORY / "lasertag"))
r = subprocess.run([sys.executable, "-B", "-m", "pytest", "-q", "-p", "no:cacheprovider", "-rA",
                    "tests/unit/test_sightlines.py"], cwd=root, capture_output=True, text=True, env=env)
keep = [l for l in r.stdout.splitlines() if l.startswith(("PASSED", "FAILED", "SKIPPED", "E  "))]
txt = "== 0.229.0's tests on 0.228.0 (e71ea71) ==\n" + "\n".join(keep) + "\nexit %d\n" % r.returncode
(HERE / "prove_tests_on_0228.out.txt").write_text(txt, encoding="utf-8", newline="\n")
print(txt)
