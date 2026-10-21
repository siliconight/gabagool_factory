"""Dry-run Deli Counter 0.242.0's two patches, in order, on a fresh clone, and compare the result to the proven clone.

    python patches/dc_crowd_barrier/dry_run_both.py <new scratch dir> <proven clone>

Clones the factory's deli_counter at its HEAD into <scratch dir>/deli_counter, runs copies of
`patch_dc_crowd_barrier.py` and then `patch_dc_crowd_barrier_materials.py` placed at <scratch dir>/patches/, compares
every changed file of the dry clone with the proven clone byte for byte, and runs the second patch again, which must
refuse. Writes dry_run_both.out.txt beside this file and prints what it compared.
"""
import pathlib
import shutil
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
FACTORY = HERE.parents[1]
PATCHES = [FACTORY / "patches" / "patch_dc_crowd_barrier.py", FACTORY / "patches" / "patch_dc_crowd_barrier_materials.py"]

root, proven = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
assert not root.exists(), "the scratch dir must be new"
(root / "patches").mkdir(parents=True)
subprocess.run(["git", "clone", "-q", str(FACTORY / "deli_counter"), str(root / "deli_counter")], check=True)
lines = []
for p in PATCHES:
    shutil.copy2(p, root / "patches" / p.name)
for what, p in (("first", PATCHES[0]), ("second", PATCHES[1]), ("second again", PATCHES[1])):
    r = subprocess.run([sys.executable, str(root / "patches" / p.name)], capture_output=True, text=True)
    lines.append("%s (%s) exit %d: %s" % (what, p.name, r.returncode, (r.stdout + r.stderr).strip()))
    if what == "second again":
        assert r.returncode != 0 and "REFUSED" in r.stdout + r.stderr
    else:
        assert r.returncode == 0, lines[-1]
dry = root / "deli_counter"
names = subprocess.run(["git", "-C", str(proven), "ls-files", "-mo", "--exclude-standard"], capture_output=True,
                       text=True, check=True).stdout.split()
changed = subprocess.run(["git", "-C", str(dry), "ls-files", "-mo", "--exclude-standard"], capture_output=True,
                         text=True, check=True).stdout.split()
assert sorted(names) == sorted(changed), (sorted(names), sorted(changed))
for f in names:
    assert (dry / f).read_bytes() == (proven / f).read_bytes(), f
lines.append("the dry clone's %d changed files are the proven clone's, byte for byte: %s"
             % (len(names), ", ".join(sorted(names))))
text = "\n".join(lines) + "\n"
(HERE / "dry_run_both.out.txt").write_text(text, encoding="utf-8", newline="\n")
print(text)
