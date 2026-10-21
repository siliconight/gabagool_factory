"""Prove 0.255.0's tests against Deli Counter 0.254.0: clone the factory's deli_counter at 0.254.0 (00c50db9) into
<scratch dir>, copy in the changed test_axonometric.py, run it. Writes prove_tests_on_0254.out.txt beside this file.
Copied from `patches/dc_axonometric/prove_tests.py`, its version and file changed.

    python patches/dc_axo_treads/prove_tests.py <new scratch dir> <0.255.0 dir>
"""
import pathlib
import shutil
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
DC = HERE.parents[1] / "deli_counter"
root, new = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
assert not root.exists(), "the scratch dir must be new"
subprocess.run(["git", "clone", "-q", str(DC), str(root)], check=True)
subprocess.run(["git", "-C", str(root), "checkout", "-q", "00c50db9"], check=True)
assert (root / "test_axonometric.py").exists()
for f in ("test_axonometric.py",):
    shutil.copy2(new / f, root)
r = subprocess.run([sys.executable, "-B", "-m", "pytest", "-q", "-p", "no:cacheprovider", "-rA", "--continue-on-collection-errors",
                    "test_axonometric.py"], cwd=root, capture_output=True, text=True)
keep = [l for l in r.stdout.splitlines()
        if l.startswith(("PASSED", "FAILED", "ERROR", "E  ")) or " passed" in l or " failed" in l or " error" in l]
txt = "== 0.255.0's tests on 0.254.0 (00c50db9) ==\n" + "\n".join(keep) + "\nexit %d\n" % r.returncode
(HERE / "prove_tests_on_0254.out.txt").write_text(txt, encoding="utf-8", newline="\n")
print(txt)
