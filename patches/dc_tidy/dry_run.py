"""Dry-run patches/patch_dc_tidy.py on a fresh clone of deli_counter, twice, and compare every file to the proven clone.

    python patches/dc_tidy/dry_run.py <new scratch dir> <proven clone>

The scratch dir gets deli_counter (a fresh clone at the factory's HEAD) and patches/ (the patch and dc_tidy/); the patch
runs there, then every file git would carry in the dry clone is compared byte for byte with the proven clone's, both ways,
and the patch runs a second time, which must refuse. Writes dry_run_first.out.txt and dry_run_second.out.txt here.
"""
import pathlib
import shutil
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
F = HERE.parents[1]
D, proven = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
assert not D.exists(), "the scratch dir must be new"
(D / "patches").mkdir(parents=True)
subprocess.run(["git", "clone", "-q", str(F / "deli_counter"), str(D / "deli_counter")], check=True)
shutil.copy2(F / "patches" / "patch_dc_tidy.py", D / "patches")
shutil.copytree(HERE, D / "patches" / "dc_tidy")


def files(root):
    """Every file git would carry: tracked, and untracked but not ignored (a test's own outputs are ignored)."""
    out = subprocess.run(["git", "-C", str(root), "ls-files", "-co", "--exclude-standard"], capture_output=True,
                         text=True, check=True).stdout.splitlines()
    return {f for f in out if f and (root / f).is_file()}


for n, name in ((1, "first"), (2, "second")):
    r = subprocess.run([sys.executable, str(D / "patches" / "patch_dc_tidy.py")], capture_output=True, text=True)
    out = r.stdout + r.stderr + "%s exit %d\n" % (name, r.returncode)
    if n == 1:
        assert r.returncode == 0, out
        a, b = files(D / "deli_counter"), files(proven)
        assert a == b, (sorted(a - b)[:10], sorted(b - a)[:10])
        diff = [f for f in sorted(a) if (D / "deli_counter" / f).read_bytes() != (proven / f).read_bytes()]
        assert not diff, diff[:10]
        out += "the dry clone's %d files are the proven clone's, byte for byte\n" % len(a)
    else:
        assert r.returncode != 0 and "REFUSED" in out, out
    (HERE / ("dry_run_%s.out.txt" % name)).write_text(out, encoding="utf-8", newline="\n")
    print(out.strip().splitlines()[-2:])
