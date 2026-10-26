"""Dry-run patches/patch_lf_panel_polish.py on a fresh clone of Level Factory, twice, and compare it to the proven clone.

    python patches/lf_export/dry_run.py <scratch dir> <proven clone>

Clones the factory's level_factory at its HEAD into <scratch dir>/level_factory, runs a copy of the patch placed at
<scratch dir>/patches/ (the patch finds level_factory beside its own parent), then compares every tracked or new file
of the dry clone with the proven clone byte for byte, and runs the patch a second time, which must refuse. Writes
dry_run_first.out.txt and dry_run_second.out.txt beside this file and prints what it compared.
"""
import pathlib
import shutil
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
FACTORY = HERE.parents[1]
PATCH = FACTORY / "patches" / "patch_lf_panel_polish.py"

root, proven = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
assert not root.exists(), "the scratch dir must be new"
(root / "patches").mkdir(parents=True)
subprocess.run(["git", "clone", "-q", str(FACTORY / "level_factory"), str(root / "level_factory")], check=True)
shutil.copy2(PATCH, root / "patches" / PATCH.name)
for n, name in ((1, "first"), (2, "second")):
    r = subprocess.run([sys.executable, str(root / "patches" / PATCH.name)], capture_output=True, text=True)
    (HERE / ("dry_run_lf_%s.out.txt" % name)).write_text(r.stdout + r.stderr + "%s exit %d\n" % (name, r.returncode),
                                                      encoding="utf-8", newline="\n")
    print(name, "exit", r.returncode, (r.stdout + r.stderr).strip().splitlines()[-1:])
    if n == 1:
        assert r.returncode == 0
        dry = root / "level_factory"
        names = subprocess.run(["git", "-C", str(proven), "ls-files", "-mo", "--exclude-standard"],
                               capture_output=True, text=True, check=True).stdout.split()
        changed = subprocess.run(["git", "-C", str(dry), "ls-files", "-mo", "--exclude-standard"],
                                 capture_output=True, text=True, check=True).stdout.split()
        assert sorted(names) == sorted(changed), (sorted(names), sorted(changed))
        for f in names:
            assert (dry / f).read_bytes() == (proven / f).read_bytes(), f
        print("the dry clone's %d changed files are the proven clone's, byte for byte: %s" % (len(names),
                                                                                             ", ".join(sorted(names))))
    else:
        assert r.returncode != 0 and "REFUSED" in r.stdout + r.stderr
