"""Two proofs for Deli Counter 0.258.0 (argv: <0.257.0 checkout> <0.258.0 clone>), each run in its own Python:
1. every spec in the 0.257.0 checkout (its ignored lf_* included) renders its full axonometric to the same bytes on both (the scout view is a mode, the default untouched);
2. the new and changed tests, copied onto 0.257.0, fail there -- and say how (a missing name or behaviour)."""
import pathlib
import shutil
import subprocess
import sys
import tempfile

base, new = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
DUMP = r'''
import glob, hashlib, json, os, sys
sys.path.insert(0, sys.argv[1])
import axonometric, spec_loader
out = {}
for p in sorted(glob.glob(os.path.join(sys.argv[2], "*.json"))):
    out[os.path.basename(p)] = hashlib.sha256(axonometric.render_axonometric(spec_loader.load_spec(p)).encode()).hexdigest()
print(json.dumps(out))
'''
h = {}
for tag, repo in (("0.257.0", base), ("0.258.0", new)):
    # both read the SAME specs, the 0.257.0 checkout's -- its ignored lf_* per-candidate specs included
    r = subprocess.run([sys.executable, "-B", "-c", DUMP, str(repo), str(base / "specs")], capture_output=True,
                       text=True, check=True, cwd=str(repo))
    h[tag] = __import__("json").loads(r.stdout)
assert h["0.257.0"].keys() == h["0.258.0"].keys()
moved = [k for k in h["0.257.0"] if h["0.257.0"][k] != h["0.258.0"][k]]
print("1. full axonometric, %d specs: %d render differently %s" % (len(h["0.257.0"]), len(moved), moved[:5]))

tmp = pathlib.Path(tempfile.mkdtemp(prefix="dc_prove_"))
try:
    work = tmp / "dc"
    shutil.copytree(base, work, ignore=shutil.ignore_patterns(".git", "build", "__pycache__"))
    for f in ("test_scout_view.py", "test_package_drawings.py"):
        shutil.copy2(new / f, work / f)
    r = subprocess.run([sys.executable, "-B", "-m", "pytest", "-q", "-p", "no:cacheprovider", "-rf",
                        "test_scout_view.py", "test_package_drawings.py"], cwd=work, capture_output=True, text=True)
    print("2. the new tests on 0.257.0:")
    for line in r.stdout.splitlines():
        if line.startswith(("FAILED", "PASSED")) or " passed" in line or " failed" in line:
            print("   " + line[:200])
finally:
    shutil.rmtree(tmp, ignore_errors=True)
