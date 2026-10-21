"""Prove 0.252.0's tests against Deli Counter 0.251.0: clone the factory's deli_counter at 0.251.0 (2ebc1359) into
<scratch dir>, copy in test_seated_hosts.py and the changed test_marker_room_routes.py, run both. Writes
prove_tests_on_0251.out.txt beside this file. Copied
from `patches/dc_marker_routes/prove_tests.py`, its version and files changed.

    python patches/dc_table_chairs/prove_tests.py <new scratch dir> <0.252.0 dir>
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
subprocess.run(["git", "-C", str(root), "checkout", "-q", "2ebc1359"], check=True)
for f in ("test_seated_hosts.py", "test_marker_room_routes.py"):
    shutil.copy2(new / f, root)
r = subprocess.run([sys.executable, "-B", "-m", "pytest", "-q", "-p", "no:cacheprovider", "-rA",
                    "test_seated_hosts.py", "test_marker_room_routes.py"], cwd=root, capture_output=True, text=True)
keep = [l for l in r.stdout.splitlines()
        if l.startswith(("PASSED", "FAILED", "E  ")) or " passed" in l or " failed" in l]
txt = "== 0.252.0's tests on 0.251.0 (2ebc1359) ==\n" + "\n".join(keep) + "\nexit %d\n" % r.returncode
(HERE / "prove_tests_on_0251.out.txt").write_text(txt, encoding="utf-8", newline="\n")
print(txt)
