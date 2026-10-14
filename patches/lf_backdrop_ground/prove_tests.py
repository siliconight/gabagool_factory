"""Level Factory 0.211.0's new test, run against 0.210.0's `backdrop_layer.py` and against 0.211.0's.

    python patches/lf_backdrop_ground/prove_tests.py > patches/lf_backdrop_ground/prove_tests.out.txt

Swaps the module for 0.210.0's (`git show 4a63d38:...`), runs `tests/unit/test_backdrop_ground.py` with `-rA`,
restores the module byte for byte and checks its hash, then runs it again. Prints each run's lines and stops.
"""
import hashlib
import pathlib
import subprocess
import sys

LF = pathlib.Path(__file__).resolve().parents[2] / "level_factory"
FILE = "packages/exporting/backdrop_layer.py"
TEST = "tests/unit/test_backdrop_ground.py"
OLD = "4a63d38"                                   # Level Factory 0.210.0


def run(label):
    p = subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", "-rA", TEST], cwd=LF,
                       capture_output=True, text=True)
    print("%s: exit %d" % (label, p.returncode))
    for line in (p.stdout + p.stderr).splitlines():
        if line.startswith(("PASSED", "FAILED", "ERROR")):
            print("   " + line[:150])


new = (LF / FILE).read_bytes()
digest = hashlib.sha256(new).hexdigest()
old = subprocess.run(["git", "-C", str(LF), "show", "%s:%s" % (OLD, FILE)], capture_output=True, check=True).stdout
assert b"def with_ground" not in old and b"def with_ground" in new
try:
    (LF / FILE).write_bytes(old)
    run("0.210.0's backdrop_layer")
finally:
    (LF / FILE).write_bytes(new)
assert hashlib.sha256((LF / FILE).read_bytes()).hexdigest() == digest, "the module was not restored"
run("0.211.0's backdrop_layer")
