"""Prove test_room_count_storey.py against Deli Counter 0.245.0: clone the factory's deli_counter at 0.245.0 (147111ee)
into <scratch dir>, copy in the new test, run it; then copy in 0.246.0's level_design.py as well and run the library
test alone, which must fail on 0.245.0's unrefurnished specs. Writes prove_tests_on_0245.out.txt beside this file.

    python patches/dc_room_count/prove_tests.py <new scratch dir>
"""
import pathlib
import shutil
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
DC = HERE.parents[1] / "deli_counter"
root = pathlib.Path(sys.argv[1])
assert not root.exists(), "the scratch dir must be new"
subprocess.run(["git", "clone", "-q", str(DC), str(root)], check=True)
subprocess.run(["git", "-C", str(root), "checkout", "-q", "147111ee"], check=True)
shutil.copy2(DC / "test_room_count_storey.py", root)
out = []
r = subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", "test_room_count_storey.py"],
                   cwd=root, capture_output=True, text=True)
out.append("== test_room_count_storey.py on 0.245.0 (147111ee) ==\n" + r.stdout[-3000:] + "exit %d\n" % r.returncode)
shutil.copy2(DC / "level_design.py", root)
r = subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", "test_room_count_storey.py",
                    "-k", "fixed_point"], cwd=root, capture_output=True, text=True)
out.append("== the library test with 0.246.0's rule on 0.245.0's specs ==\n" + r.stdout[-2500:] + "exit %d\n" % r.returncode)
(HERE / "prove_tests_on_0245.out.txt").write_text("\n".join(out), encoding="utf-8", newline="\n")
print("\n".join(l for l in "\n".join(out).splitlines() if l.startswith(("==", "FAILED")) or " passed" in l or " failed" in l))
