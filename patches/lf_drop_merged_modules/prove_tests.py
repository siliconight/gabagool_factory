"""Level Factory 0.210.0's new test, run against 0.209.0's code and against 0.210.0's (factory roadmap 249).

    python patches/lf_drop_merged_modules/prove_tests.py > patches/lf_drop_merged_modules/prove_tests.out.txt

Swaps `merge_empties.py` and `export.py` for 0.209.0's (`git show 3ffe5c6:...`), runs
`tests/unit/test_merged_modules_dropped.py` with `-rA`, then restores both byte for byte and checks their hashes
before running it again on 0.210.0. Prints each run's per-test lines and stops.
"""
import hashlib
import pathlib
import subprocess
import sys

LF = pathlib.Path(__file__).resolve().parents[2] / "level_factory"
FILES = ("packages/exporting/merge_empties.py", "packages/exporting/export.py")
TEST = "tests/unit/test_merged_modules_dropped.py"
OLD = "3ffe5c6"                                   # Level Factory 0.209.0


def run(label):
    p = subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", "-rA", TEST], cwd=LF,
                       capture_output=True, text=True)
    lines = [l for l in (p.stdout + p.stderr).splitlines() if l.startswith(("PASSED", "FAILED", "ERROR"))]
    print("%s: exit %d" % (label, p.returncode))
    for l in lines:
        print("   " + l[:150])


new = {f: (LF / f).read_bytes() for f in FILES}
digest = {f: hashlib.sha256(b).hexdigest() for f, b in new.items()}
old = {f: subprocess.run(["git", "-C", str(LF), "show", "%s:%s" % (OLD, f)], capture_output=True,
                         check=True).stdout for f in FILES}
assert b"drop_merged_modules" not in old[FILES[0]] and b"drop_merged_modules" in new[FILES[0]]
try:
    for f in FILES:
        (LF / f).write_bytes(old[f])
    run("0.209.0's code")
finally:
    for f in FILES:
        (LF / f).write_bytes(new[f])
for f in FILES:
    assert hashlib.sha256((LF / f).read_bytes()).hexdigest() == digest[f], f + " was not restored"
run("0.210.0's code")
