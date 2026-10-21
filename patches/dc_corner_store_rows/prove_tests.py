"""Prove 0.247.0's tests against Deli Counter 0.246.0: clone the factory's deli_counter at 0.246.0 (d94c6c0f) into
<scratch dir>, copy in test_corner_store_rows.py and 0.247.0's test_store_gondolas.py, run both. Writes
prove_tests_on_0246.out.txt beside this file.

    python patches/dc_corner_store_rows/prove_tests.py <new scratch dir> <0.247.0 tests dir>
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
subprocess.run(["git", "-C", str(root), "checkout", "-q", "d94c6c0f"], check=True)
shutil.copy2(tests / "test_corner_store_rows.py", root)
shutil.copy2(tests / "test_store_gondolas.py", root)
r = subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", "-rA", "test_corner_store_rows.py",
                    "test_store_gondolas.py"], cwd=root, capture_output=True, text=True)
keep = [l for l in r.stdout.splitlines() if l.startswith(("PASSED", "FAILED", "E  ")) or " passed" in l]
txt = "== 0.247.0's tests on 0.246.0 (d94c6c0f) ==\n" + "\n".join(keep) + "\nexit %d\n" % r.returncode
(HERE / "prove_tests_on_0246.out.txt").write_text(txt, encoding="utf-8", newline="\n")
print(txt)
