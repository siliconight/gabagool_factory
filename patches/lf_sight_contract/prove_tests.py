"""Prove 0.230.0's tests against Level Factory 0.229.0: clone the factory's level_factory at 0.229.0 (1f6f047) into
<scratch dir>, copy in the new tests/unit/test_sight_follows_the_body.py, and run it there. Writes
prove_tests_on_0229.out.txt beside this file. Copied from `patches/lf_sight_crossing/prove_tests.py`, its version and
file changed.

    python patches/lf_sight_contract/prove_tests.py <new scratch dir> <0.230.0 dir>
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
subprocess.run(["git", "-C", str(root), "checkout", "-q", "1f6f047"], check=True)
assert not (root / "tests" / "unit" / "test_sight_follows_the_body.py").exists()
shutil.copy2(new / "tests" / "unit" / "test_sight_follows_the_body.py", root / "tests" / "unit")
env = dict(os.environ, LF_LASERTAG_ROOT=str(FACTORY / "lasertag"))
r = subprocess.run([sys.executable, "-B", "-m", "pytest", "-q", "-p", "no:cacheprovider", "-rA",
                    "tests/unit/test_sight_follows_the_body.py"], cwd=root, capture_output=True, text=True, env=env)
keep = [l for l in r.stdout.splitlines() if l.startswith(("PASSED", "FAILED", "SKIPPED", "E  "))]
txt = "== 0.230.0's tests on 0.229.0 (1f6f047) ==\n" + "\n".join(keep) + "\nexit %d\n" % r.returncode
(HERE / "prove_tests_on_0229.out.txt").write_text(txt, encoding="utf-8", newline="\n")
print(txt)
