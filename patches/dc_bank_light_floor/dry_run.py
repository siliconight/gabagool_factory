"""Dry-run patches/patch_dc_bank_light_floor.py on a fresh clone of deli_counter, twice, and compare it to the proven clone.

    python patches/dc_civic_rooms/dry_run.py <scratch dir> <proven clone>

Clones the factory's deli_counter at its HEAD into <scratch dir>/deli_counter, runs a copy of the patch placed at
<scratch dir>/patches/ (the patch finds deli_counter beside its own parent), then compares every tracked or new file
of the dry clone with the proven clone byte for byte, and runs the patch a second time, which must refuse. Writes
dry_run_first.out.txt and dry_run_second.out.txt beside this file and prints what it compared.
"""
import pathlib
import shutil
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
FACTORY = HERE.parents[1]
PATCH = FACTORY / "patches" / "patch_dc_bank_light_floor.py"

root, proven = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
assert not root.exists(), "the scratch dir must be new"
(root / "patches").mkdir(parents=True)
subprocess.run(["git", "clone", "-q", str(FACTORY / "deli_counter"), str(root / "deli_counter")], check=True)
shutil.copy2(PATCH, root / "patches" / PATCH.name)
for n, name in ((1, "first"), (2, "second")):
    r = subprocess.run([sys.executable, str(root / "patches" / PATCH.name)], capture_output=True, text=True)
    (HERE / ("dry_run_%s.out.txt" % name)).write_text(r.stdout + r.stderr + "%s exit %d\n" % (name, r.returncode),
                                                      encoding="utf-8", newline="\n")
    print(name, "exit", r.returncode, (r.stdout + r.stderr).strip().splitlines()[-1:])
    if n == 1:
        assert r.returncode == 0
        dry = root / "deli_counter"
        names = subprocess.run(["git", "-C", str(proven), "ls-files", "-mo", "--exclude-standard"],
                               capture_output=True, text=True, check=True).stdout.split()
        # the proven clone was built (`build.py --all`) for its proof and the patch writes no build output -- the
        # apply rebuilds -- so build/ is not compared
        names = [f for f in names if not f.startswith("build/")]
        changed = subprocess.run(["git", "-C", str(dry), "ls-files", "-mo", "--exclude-standard"],
                                 capture_output=True, text=True, check=True).stdout.split()
        assert sorted(names) == sorted(changed), (sorted(names), sorted(changed))
        for f in names:
            assert (dry / f).read_bytes() == (proven / f).read_bytes(), f
        print("the dry clone's %d changed files are the proven clone's, byte for byte: %s" % (len(names),
                                                                                             ", ".join(sorted(names))))
    else:
        assert r.returncode != 0 and "REFUSED" in r.stdout + r.stderr
