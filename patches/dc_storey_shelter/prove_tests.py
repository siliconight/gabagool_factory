"""Prove 0.249.0's tests against Deli Counter 0.248.0: clone the factory's deli_counter at 0.248.0 (88422d0b) into
<scratch dir>, copy in test_storey_shelter.py and migrate_shelter.py, run the tests. migrate_shelter.py goes in too so
the library test runs 0.248.0's own shelter pass over 0.248.0's library -- a failure there is behaviour, not a missing
import. Writes prove_tests_on_0248.out.txt beside this file. Copied from `patches/dc_office_floor/prove_tests.py`, its
version and files changed.

    python patches/dc_storey_shelter/prove_tests.py <new scratch dir> <0.249.0 dir>
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
subprocess.run(["git", "-C", str(root), "checkout", "-q", "88422d0b"], check=True)
for f in ("test_storey_shelter.py", "migrate_shelter.py"):
    shutil.copy2(new / f, root)
r = subprocess.run([sys.executable, "-B", "-m", "pytest", "-q", "-p", "no:cacheprovider", "-rA",
                    "test_storey_shelter.py"], cwd=root, capture_output=True, text=True)
keep = [l for l in r.stdout.splitlines()
        if l.startswith(("PASSED", "FAILED", "E  ")) or " passed" in l or " failed" in l]
txt = "== 0.249.0's tests on 0.248.0 (88422d0b) ==\n" + "\n".join(keep) + "\nexit %d\n" % r.returncode
(HERE / "prove_tests_on_0248.out.txt").write_text(txt, encoding="utf-8", newline="\n")
print(txt)
