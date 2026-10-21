"""Prove 0.248.0's test against Deli Counter 0.247.0: clone the factory's deli_counter at 0.247.0 (e1cbd7e1) into
<scratch dir>, copy in test_office_floor_kind.py, run it. Writes prove_tests_on_0247.out.txt beside this file. Copied
from `patches/dc_corner_store_rows/prove_tests.py`, its version and files changed.

    python patches/dc_office_floor/prove_tests.py <new scratch dir> <0.248.0 tests dir>
"""
import pathlib
import shutil
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
DC = HERE.parents[1] / "deli_counter"
root, tests = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
assert not root.exists(), "the scratch dir must be new"
subprocess.run(["git", "clone", "-q", str(DC), str(root)], check=True)
subprocess.run(["git", "-C", str(root), "checkout", "-q", "e1cbd7e1"], check=True)
shutil.copy2(tests / "test_office_floor_kind.py", root)
r = subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", "-rA", "test_office_floor_kind.py"],
                   cwd=root, capture_output=True, text=True)
keep = [l for l in r.stdout.splitlines() if l.startswith(("PASSED", "FAILED", "E  ")) or " passed" in l or " failed" in l]
txt = "== 0.248.0's test on 0.247.0 (e1cbd7e1) ==\n" + "\n".join(keep) + "\nexit %d\n" % r.returncode
(HERE / "prove_tests_on_0247.out.txt").write_text(txt, encoding="utf-8", newline="\n")
print(txt)
